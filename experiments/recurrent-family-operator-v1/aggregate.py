#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

MASTER_SEEDS = (
    767003, 767019, 767037, 767053, 767071,
    767089, 767107, 767127, 767149, 767167,
    767181, 767199, 767223, 767239, 767257,
    767277, 767293, 767311, 767331, 767349,
)
MODEL_NAMES = (
    "tied-burnin",
    "tied-shallow",
    "untied-equal-param",
    "untied-equal-compute",
)
HORIZONS = (0, 1, 2, 4, 8, 16, 32, 64, 128, 256)
BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 767555001
MEANINGFUL_BAR = 0.005
BURNIN_DIAGNOSTIC_BAR = 0.003


def _mean(xs):
    return statistics.fmean(xs) if xs else 0.0


def _bootstrap_lower(values, rng: random.Random):
    n = len(values)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        draws.append(_mean([values[rng.randrange(n)] for _ in range(n)]))
    draws.sort()
    return draws[int(0.05 * (len(draws) - 1))]


def _h(record, model: str, horizon: int):
    return record["models"][model]["horizons"][str(horizon)]


def aggregate(input_dir: Path) -> dict:
    records = [json.loads(p.read_text()) for p in sorted(input_dir.glob("seed-*.json"))]
    seeds = sorted(int(x["masterSeed"]) for x in records)
    if seeds != sorted(MASTER_SEEDS):
        raise AssertionError(f"incomplete/unexpected seed rectangle: {seeds}")
    if not all(x["smoke"] is False and all(x["hardInvariants"].values()) for x in records):
        raise AssertionError("authoritative record failed hard invariant")

    model_digests = {x["training"]["modelArtifactSha256"] for x in records}
    corpus_digests = {x["training"]["corpusSha256"] for x in records}
    if len(model_digests) != 1 or len(corpus_digests) != 1:
        raise AssertionError("authoritative evaluations did not consume one frozen training artifact/corpus")

    trajectory_means = {}
    validity_rates = {}
    law_failures = {}
    parameter_mse_means = {}
    dynamics_means = {}
    for model in MODEL_NAMES:
        trajectory_means[model] = {}
        validity_rates[model] = {}
        law_failures[model] = {}
        parameter_mse_means[model] = {}
        for h in HORIZONS:
            cells = [_h(r, model, h) for r in records]
            trajectory_means[model][str(h)] = _mean([float(x["recovery"]) for x in cells])
            validity_rates[model][str(h)] = _mean([1.0 if x["valid"] else 0.0 for x in cells])
            law_failures[model][str(h)] = sum(int(x["lawFailures"]) for x in cells)
            parameter_mse_means[model][str(h)] = _mean([float(x["parameterMSE"]) for x in cells])
        dynamics_means[model] = {
            "tailStepNormMean": _mean([
                float(r["models"][model]["dynamics"]["tailStepNormMean"]) for r in records
            ]),
            "tailBoundSaturationMean": _mean([
                float(r["models"][model]["dynamics"]["tailBoundSaturationMean"]) for r in records
            ]),
            "fixedPointTailCount": sum(
                bool(r["models"][model]["dynamics"]["fixedPointTail"]) for r in records
            ),
            "twoCycleTailCount": sum(
                bool(r["models"][model]["dynamics"]["twoCycleTail"]) for r in records
            ),
        }

    rng = random.Random(BOOTSTRAP_SEED)
    tied_128_16 = [
        float(_h(r, "tied-burnin", 128)["recovery"]) - float(_h(r, "tied-burnin", 16)["recovery"])
        for r in records
    ]
    tied_256_16 = [
        float(_h(r, "tied-burnin", 256)["recovery"]) - float(_h(r, "tied-burnin", 16)["recovery"])
        for r in records
    ]
    tied_vs_equal_param_128 = [
        float(_h(r, "tied-burnin", 128)["recovery"]) - float(_h(r, "untied-equal-param", 128)["recovery"])
        for r in records
    ]
    burnin_vs_shallow_256 = [
        float(_h(r, "tied-burnin", 256)["recovery"]) - float(_h(r, "tied-shallow", 256)["recovery"])
        for r in records
    ]

    comparisons = {
        "tiedRecoveryGain128Minus16": {
            "mean": _mean(tied_128_16),
            "oneSided95BootstrapLower": _bootstrap_lower(tied_128_16, rng),
        },
        "tiedRecoveryGain256Minus16": {
            "mean": _mean(tied_256_16),
            "oneSided95BootstrapLower": _bootstrap_lower(tied_256_16, rng),
        },
        "tiedMinusUntiedEqualParamAt128": {
            "mean": _mean(tied_vs_equal_param_128),
            "oneSided95BootstrapLower": _bootstrap_lower(tied_vs_equal_param_128, rng),
        },
        "tiedMinusUntiedEqualComputeAt128": {
            "mean": trajectory_means["tied-burnin"]["128"] - trajectory_means["untied-equal-compute"]["128"],
        },
        "tiedMinusUntiedEqualComputeAt256": {
            "mean": trajectory_means["tied-burnin"]["256"] - trajectory_means["untied-equal-compute"]["256"],
        },
        "tied256MinusTied128": {
            "mean": trajectory_means["tied-burnin"]["256"] - trajectory_means["tied-burnin"]["128"],
        },
        "burninMinusShallowAt256": {
            "mean": _mean(burnin_vs_shallow_256),
            "oneSided95BootstrapLower": _bootstrap_lower(burnin_vs_shallow_256, rng),
        },
    }

    viability = {
        "completeHardInvariantRectangle": True,
        "postHorizonValidityAtLeast95Pct": all(
            validity_rates["tied-burnin"][str(h)] >= 0.95 for h in (32, 64, 128, 256)
        ),
        "postHorizonSiblingLawFailuresZero": all(
            law_failures["tied-burnin"][str(h)] == 0 for h in (16, 32, 64, 128, 256)
        ),
        "gain128Minus16AtLeast005": comparisons["tiedRecoveryGain128Minus16"]["mean"] >= MEANINGFUL_BAR,
        "gain128Minus16BootstrapLowerPositive": comparisons["tiedRecoveryGain128Minus16"]["oneSided95BootstrapLower"] > 0,
        "gain256Minus16AtLeast005": comparisons["tiedRecoveryGain256Minus16"]["mean"] >= MEANINGFUL_BAR,
        "gain256Minus16BootstrapLowerPositive": comparisons["tiedRecoveryGain256Minus16"]["oneSided95BootstrapLower"] > 0,
        "noMaterialLateCollapse": comparisons["tied256MinusTied128"]["mean"] >= -MEANINGFUL_BAR,
    }

    efficiency = {
        "beatsEqualParameterUntiedAt128By005": comparisons["tiedMinusUntiedEqualParamAt128"]["mean"] >= MEANINGFUL_BAR,
        "equalParameterPairedBootstrapLowerPositive": comparisons["tiedMinusUntiedEqualParamAt128"]["oneSided95BootstrapLower"] > 0,
        "nonInferiorToEqualComputeWideAt128Within005": comparisons["tiedMinusUntiedEqualComputeAt128"]["mean"] >= -MEANINGFUL_BAR,
        "nonInferiorToEqualComputeWideAt256Within005": comparisons["tiedMinusUntiedEqualComputeAt256"]["mean"] >= -MEANINGFUL_BAR,
    }

    burnin_diagnostic = bool(
        comparisons["burninMinusShallowAt256"]["mean"] >= BURNIN_DIAGNOSTIC_BAR
        and comparisons["burninMinusShallowAt256"]["oneSided95BootstrapLower"] > 0
    )

    viability_pass = all(viability.values())
    efficiency_pass = all(efficiency.values())
    if viability_pass and efficiency_pass:
        decision = "RECURRENT_FAMILY_OPERATOR_PROMISING"
    elif viability_pass:
        decision = "RECURRENT_FAMILY_ITERATION_PRESENT_TYING_EFFICIENCY_NOT_DEMONSTRATED"
    else:
        decision = "RECURRENT_FAMILY_OPERATOR_NOT_PROMISING"

    references = {
        "nativeOnly20MeanBestArchiveRecovery": _mean([
            float(r["searchReferences"]["nativeOnly20"]["bestArchiveRecovery"]) for r in records
        ]),
        "familyProjected20MeanBestArchiveRecovery": _mean([
            float(r["searchReferences"]["familyProjected20"]["bestArchiveRecovery"]) for r in records
        ]),
        "meanStartRecovery": _mean([float(r["start"]["recovery"]) for r in records]),
    }

    return {
        "version": 1,
        "experiment": "recurrent-family-operator-v1",
        "artisticEvidence": False,
        "authority": "mechanical-recurrent-family-only",
        "seedCount": len(records),
        "trainingModelArtifactSha256": next(iter(model_digests)),
        "trainingCorpusSha256": next(iter(corpus_digests)),
        "meaningfulRecoveryBar": MEANINGFUL_BAR,
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed paired trajectory",
        },
        "trajectoryRecoveryMeans": trajectory_means,
        "validityRates": validity_rates,
        "siblingLawFailures": law_failures,
        "parameterMSEMeans": parameter_mse_means,
        "dynamicsMeans": dynamics_means,
        "comparisons": comparisons,
        "recurrentViabilityGates": viability,
        "weightSharingEfficiencyGates": efficiency,
        "recurrentViabilityPassed": viability_pass,
        "weightSharingEfficiencyPassed": efficiency_pass,
        "lateStateTrainingAddsTailStability": burnin_diagnostic,
        "searchReferences": references,
        "decision": decision,
        "interpretation": (
            "The primary decision asks whether the shared transition improves materially beyond its 16-step training horizon while preserving family validity, then whether that tied model is parameter-efficient relative to untied controls. The burn-in comparison is diagnostic and does not veto recurrent viability."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = aggregate(Path(args.input_dir))
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
