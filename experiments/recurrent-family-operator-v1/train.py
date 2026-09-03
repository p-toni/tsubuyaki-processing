#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from family_problem import build_training_corpus
from recurrent_model import (
    MODEL_SPECS,
    model_parameter_count,
    save_models,
    train_model,
)

AUTHORITATIVE_CORPUS_SEED = 766001
AUTHORITATIVE_SCHEDULE_SEED = 766089
AUTHORITATIVE_TARGETS = 256
AUTHORITATIVE_MAX_DRAWS = 512
AUTHORITATIVE_UPDATES = 1600
BATCH_SIZE = 64

SMOKE_CORPUS_SEED = 766999
SMOKE_SCHEDULE_SEED = 766998
SMOKE_TARGETS = 16
SMOKE_MAX_DRAWS = 64
SMOKE_UPDATES = 8

EXPECTED_PARAMETER_COUNTS = {
    "tied-burnin": 3946,
    "tied-shallow": 3946,
    "untied-equal-param": 4000,
    "untied-equal-compute": 63136,
}


def _array_sha256(*arrays: np.ndarray) -> str:
    h = hashlib.sha256()
    for array in arrays:
        x = np.ascontiguousarray(array, dtype=np.float64)
        h.update(str(x.shape).encode("utf-8"))
        h.update(b"\0")
        h.update(x.tobytes())
        h.update(b"\0")
    return h.hexdigest()


def train(output_model: Path, output_summary: Path, smoke: bool) -> dict:
    corpus_seed = SMOKE_CORPUS_SEED if smoke else AUTHORITATIVE_CORPUS_SEED
    schedule_seed = SMOKE_SCHEDULE_SEED if smoke else AUTHORITATIVE_SCHEDULE_SEED
    target_count = SMOKE_TARGETS if smoke else AUTHORITATIVE_TARGETS
    max_draws = SMOKE_MAX_DRAWS if smoke else AUTHORITATIVE_MAX_DRAWS
    updates = SMOKE_UPDATES if smoke else AUTHORITATIVE_UPDATES

    states, descriptors, accepted_draws = build_training_corpus(
        corpus_seed,
        count=target_count,
        max_draws=max_draws,
    )
    corpus_digest = _array_sha256(states, descriptors)

    observed_counts = {
        name: model_parameter_count(spec) for name, spec in MODEL_SPECS.items()
    }
    if observed_counts != EXPECTED_PARAMETER_COUNTS:
        raise AssertionError(f"parameter-count drift: {observed_counts}")

    models = {}
    model_summaries = {}
    for name in (
        "tied-burnin",
        "tied-shallow",
        "untied-equal-param",
        "untied-equal-compute",
    ):
        model, summary = train_model(
            name,
            states,
            descriptors,
            updates=updates,
            schedule_seed=schedule_seed,
            batch_size=BATCH_SIZE,
        )
        models[name] = model
        model_summaries[name] = summary

    metadata = {
        "version": 1,
        "experiment": "recurrent-family-operator-v1",
        "smoke": bool(smoke),
        "corpusSeed": corpus_seed,
        "scheduleSeed": schedule_seed,
        "targetCount": target_count,
        "maxDraws": max_draws,
        "acceptedDrawCount": len(accepted_draws),
        "lastAcceptedDrawIndex": int(accepted_draws[-1]),
        "corpusSha256": corpus_digest,
        "updatesPerModel": updates,
        "batchSize": BATCH_SIZE,
        "checkpointSelection": "final-update-only",
        "parameterCounts": observed_counts,
    }
    save_models(output_model, models, metadata)

    model_digest = hashlib.sha256(Path(output_model).read_bytes()).hexdigest()
    result = {
        **metadata,
        "modelArtifactSha256": model_digest,
        "models": model_summaries,
        "hardInvariants": {
            "targetCountExact": states.shape == (target_count, 19),
            "descriptorShapeExact": descriptors.shape == (target_count, 192),
            "parameterCountsExact": observed_counts == EXPECTED_PARAMETER_COUNTS,
            "finalCheckpointOnly": True,
            "allModelsTrainedExactUpdates": all(
                int(x["updates"]) == updates for x in model_summaries.values()
            ),
            "equalParameterControlWithin2Pct": abs(
                observed_counts["untied-equal-param"] / observed_counts["tied-burnin"] - 1.0
            ) <= 0.02,
            "equalComputeWidePerStepWidthExact": (
                MODEL_SPECS["untied-equal-compute"]["hidden"]
                == MODEL_SPECS["tied-burnin"]["hidden"]
            ),
        },
    }
    if not all(result["hardInvariants"].values()):
        raise AssertionError(f"training invariant failure: {result['hardInvariants']}")
    Path(output_summary).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model-out", required=True)
    p.add_argument("--summary-out", required=True)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    result = train(Path(args.model_out), Path(args.summary_out), args.smoke)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
