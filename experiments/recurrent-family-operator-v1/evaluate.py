#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path

import numpy as np

import search_engine
from family_problem import (
    DISCRETE_KEYS,
    LAW_FAILURE,
    candidate_summary,
    first_hard_valid_target,
    genome_from_state,
    normalize_genome,
    phenotype_descriptor,
    search_reference,
    target_frames,
    valid_perturbed_start,
)
from recurrent_model import load_models, trajectory
from rng_streams import derived_seed

HORIZONS = (0, 1, 2, 4, 8, 16, 32, 64, 128, 256)
MODEL_NAMES = (
    "tied-burnin",
    "tied-shallow",
    "untied-equal-param",
    "untied-equal-compute",
)
EXPECTED_PARAMETER_COUNTS = {
    "tied-burnin": 3946,
    "tied-shallow": 3946,
    "untied-equal-param": 4000,
    "untied-equal-compute": 63136,
}

SMOKE_SEED = 767999
MASTER_SEEDS = (
    767003, 767019, 767037, 767053, 767071,
    767089, 767107, 767127, 767149, 767167,
    767181, 767199, 767223, 767239, 767257,
    767277, 767293, 767311, 767331, 767349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _dynamics(states: np.ndarray, step_norms: np.ndarray) -> dict:
    tail_steps = step_norms[-min(32, len(step_norms)):]
    tail_states = states[-min(33, len(states)):]
    if len(states) >= 34:
        two_cycle = [
            float(np.linalg.norm(states[i] - states[i - 2]))
            for i in range(len(states) - 32, len(states))
            if i >= 2
        ]
    else:
        two_cycle = []
    saturation = np.mean(np.abs(tail_states) >= 0.999, axis=1)
    return {
        "tailStepNormMean": float(np.mean(tail_steps)) if len(tail_steps) else 0.0,
        "tailStepNormMax": float(np.max(tail_steps)) if len(tail_steps) else 0.0,
        "tailTwoCycleDistanceMean": float(np.mean(two_cycle)) if two_cycle else None,
        "tailBoundSaturationMean": float(np.mean(saturation)),
        "fixedPointTail": bool(len(tail_steps) and float(np.mean(tail_steps)) <= 1e-4),
        "twoCycleTail": bool(
            two_cycle
            and float(np.mean(two_cycle)) <= 1e-4
            and float(np.mean(tail_steps)) > 1e-4
        ),
    }


def evaluate(model_path: Path, seed: int, smoke: bool) -> dict:
    if seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {seed} outside frozen evaluation population")
    if smoke != (seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    models, training_meta = load_models(model_path)
    if tuple(models) != MODEL_NAMES:
        raise AssertionError(f"model set/order drift: {tuple(models)}")
    if bool(training_meta.get("smoke")) != bool(smoke):
        raise AssertionError("smoke evaluation must consume smoke weights; authoritative evaluation must consume authoritative weights")
    if training_meta.get("parameterCounts") != EXPECTED_PARAMETER_COUNTS:
        raise AssertionError(f"training parameter-count metadata drift: {training_meta.get('parameterCounts')}")

    target_genome, target_draw = first_hard_valid_target(
        seed,
        "recurrent-family-eval-target-v1",
        max_draws=32,
    )
    target_state = normalize_genome(target_genome)
    descriptor = phenotype_descriptor(target_genome)
    images = target_frames(target_genome)
    start_state, start_genome, start_retry, start_scale = valid_perturbed_start(target_genome, seed)
    start_record = candidate_summary(start_genome, images)
    if not start_record["valid"]:
        raise AssertionError("fixed evaluation start is not hard-valid")

    model_records = {}
    all_discrete_exact = True
    initial_recoveries = []
    for name in MODEL_NAMES:
        model = models[name]
        states, step_norms = trajectory(model, start_state, descriptor, 256)
        horizons = {}
        for h in HORIZONS:
            state = states[h]
            genome = genome_from_state(state, target_genome)
            discrete_exact = all(genome[k] == target_genome[k] for k in DISCRETE_KEYS)
            all_discrete_exact = all_discrete_exact and discrete_exact
            summary = candidate_summary(genome, images)
            summary.update({
                "horizon": h,
                "parameterMSE": float(np.mean((state - target_state) ** 2)),
                "boundSaturation": float(np.mean(np.abs(state) >= 0.999)),
                "discreteFieldsExact": discrete_exact,
            })
            horizons[str(h)] = summary
        initial_recoveries.append(horizons["0"]["recovery"])
        model_records[name] = {
            "parameterCount": int(model["parameterCount"]),
            "horizons": horizons,
            "dynamics": _dynamics(states, step_norms),
        }

    with tempfile.TemporaryDirectory(prefix=f"recurrent-family-reference-{seed}-") as td:
        root = Path(td)
        native_ref = search_reference(
            start_genome,
            images,
            derived_seed(seed, "recurrent-family-native-reference-v1"),
            search_engine.NATIVE_ONLY,
            root / "native",
        )
        projected_ref = search_reference(
            start_genome,
            images,
            derived_seed(seed, "recurrent-family-projected-reference-v1"),
            search_engine.FAMILY_PROJECTED_V1,
            root / "projected",
        )

    hard = {
        "trainingModelSetExact": tuple(models) == MODEL_NAMES,
        "parameterCountsExact": {
            name: int(models[name]["parameterCount"]) for name in MODEL_NAMES
        } == EXPECTED_PARAMETER_COUNTS,
        "targetDrawBounded": 1 <= int(target_draw) <= 32,
        "validStartFoundByFrozenBackoff": bool(start_record["valid"]) and 0 <= int(start_retry) <= 7,
        "targetDescriptorShapeExact": descriptor.shape == (192,),
        "allModelsShareExactStartRecovery": max(initial_recoveries) - min(initial_recoveries) <= 1e-15,
        "allDecodedDiscreteFieldsExact": all_discrete_exact,
        "allStateHorizonsPresent": all(
            tuple(int(x) for x in model_records[name]["horizons"]) == HORIZONS
            for name in MODEL_NAMES
        ),
        "nativeReferenceBudgetExact": (
            int(native_ref["generationOperatorCounts"].get("native", -1)) == 20
            and int(native_ref["generationOperatorCounts"].get("spectral", -1)) == 0
        ),
        "projectedReferenceBudgetExact": (
            int(projected_ref["generationOperatorCounts"].get("native", -1)) == 10
            and int(projected_ref["generationOperatorCounts"].get("projected-spectral", -1)) == 10
            and int(projected_ref["generationOperatorCounts"].get("spectral", -1)) == 0
        ),
    }
    if not all(hard.values()):
        raise AssertionError(f"evaluation hard invariant failure: {hard}")

    return {
        "version": 1,
        "experiment": "recurrent-family-operator-v1",
        "masterSeed": int(seed),
        "smoke": bool(smoke),
        "artisticEvidence": False,
        "authority": "mechanical-recurrent-family-only",
        "training": training_meta,
        "target": {
            "draw": int(target_draw),
            "descriptorDim": int(descriptor.shape[0]),
        },
        "start": {
            "retryIndex": int(start_retry),
            "perturbationScale": float(start_scale),
            "recovery": float(start_record["recovery"]),
            "valid": bool(start_record["valid"]),
            "maxSiblingLengthCV": start_record["maxSiblingLengthCV"],
        },
        "models": model_records,
        "searchReferences": {
            "nativeOnly20": native_ref,
            "familyProjected20": projected_ref,
        },
        "hardInvariants": hard,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--models", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    result = evaluate(Path(args.models), args.seed, args.smoke)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
