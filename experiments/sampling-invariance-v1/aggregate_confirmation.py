from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
from pathlib import Path

import run_capacity

capacity = run_capacity.capacity
import aggregate_capacity
import validate_fast_metric
from confirmation_capacity import CONFIRMATION_SEEDS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
T_CRIT_95_ONE_SIDED_DF23 = 1.7138715277470473

FROZEN_BLOBS = {
    "experiments/sampling-invariance-v1/field.py": "66f59d92ab39379d3a2016d18adbd271827997dd",
    "experiments/sampling-invariance-v1/capacity.py": "fa5aa481ddab9babff17abdf1e4342d7ed74d2a2",
    "experiments/sampling-invariance-v1/aggregate_capacity.py": "bf163da46b3b7728beaa13013d42eadf93d98fae",
    "experiments/sampling-invariance-v1/fast_binary_metric.py": "7e1c875350050312971d9397091e8708752c0bcd",
    "experiments/sampling-invariance-v1/run_capacity.py": "4fd07ccd9b548b2537fe86ee3e64914a30fc88bd",
    "experiments/sampling-invariance-v1/validate_fast_metric.py": "ece688dbd8f489c3f6ed03bb55b11dd236eb4f8e",
    "experiments/sampling-invariance-v1/STAGE-B.md": "f9cef9e3c66a0f4161c444d6340d32cd7b32abbb",
}


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def _lower_bound(values: list[float]) -> float:
    if len(values) != len(CONFIRMATION_SEEDS):
        raise AssertionError("confirmation inference requires the complete 24-seed sample")
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    return mean - T_CRIT_95_ONE_SIDED_DF23 * sd / math.sqrt(len(values))


def _verify_frozen_blobs() -> dict:
    observed = {}
    for relative_path, expected in FROZEN_BLOBS.items():
        actual = subprocess.check_output(
            ["git", "hash-object", relative_path],
            cwd=ROOT,
            text=True,
        ).strip()
        observed[relative_path] = {
            "expected": expected,
            "actual": actual,
            "pass": actual == expected,
        }
    return {
        "pass": all(item["pass"] for item in observed.values()),
        "files": observed,
    }


def _verify_metric_equivalence() -> dict:
    targets = capacity.build_targets()
    cases = []
    for target in targets:
        candidates = (
            ("exact", target.image),
            ("shift+1", validate_fast_metric.shift(target.image, 1, 0)),
            ("shift-3+2", validate_fast_metric.shift(target.image, -3, 2)),
            ("blank", validate_fast_metric.Image.new("L", target.image.size, capacity.BG)),
            ("random-sparse", validate_fast_metric.random_binary(7000 + len(cases), 900)),
            ("random-dense", validate_fast_metric.random_binary(9000 + len(cases), 18000)),
        )
        for label, candidate in candidates:
            diff = validate_fast_metric.compare(candidate, target.image)
            cases.append({"target": target.id, "candidate": label, "maxAbsoluteDifference": diff})
    max_diff = max(case["maxAbsoluteDifference"] for case in cases)
    return {
        "cases": len(cases),
        "maxAbsoluteDifference": max_diff,
        "tolerance": 1e-12,
        "pass": max_diff <= 1e-12,
    }


def aggregate(results_dir: Path) -> dict:
    paths = sorted(Path(results_dir).glob("seed-*.json"))
    blocks = [json.loads(path.read_text()) for path in paths]
    by_seed = {int(block["seed"]): block for block in blocks}

    confirmation_markers_valid = (
        sorted(by_seed) == sorted(CONFIRMATION_SEEDS)
        and len(by_seed) == len(CONFIRMATION_SEEDS)
        and all(
            block.get("confirmation", {}).get("experiment")
            == "sampling-invariance-capacity-confirmation-v1"
            and block.get("confirmation", {}).get("population") == "fresh-confirmation"
            and int(block.get("confirmation", {}).get("seed")) == seed
            for seed, block in by_seed.items()
        )
    )

    original_holdout_seeds = capacity.HOLDOUT_SEEDS
    capacity.HOLDOUT_SEEDS = CONFIRMATION_SEEDS
    try:
        fresh_stage_b = aggregate_capacity.aggregate(Path(results_dir), "holdout")
    finally:
        capacity.HOLDOUT_SEEDS = original_holdout_seeds

    field_means = []
    paired_added_margins = []
    field_meaningful_fractions = []
    paired_meaningful_margins = []
    per_seed = {}

    for seed in CONFIRMATION_SEEDS:
        block = by_seed[seed]
        targets = block["targets"]
        field_mean = statistics.fmean(float(target["fieldAddedRecovery"]) for target in targets)
        route_means = {
            route: statistics.fmean(float(target["currentRouteAddedRecovery"][route]) for target in targets)
            for route in capacity.CURRENT_ROUTES
        }
        route_median = statistics.median(route_means.values())
        field_fraction = statistics.fmean(
            1.0 if target["fieldMeaningfulUniqueContribution"] else 0.0 for target in targets
        )
        route_fractions = {
            route: statistics.fmean(
                1.0 if target["currentRouteMeaningfulUniqueContribution"][route] else 0.0
                for target in targets
            )
            for route in capacity.CURRENT_ROUTES
        }
        route_fraction_median = statistics.median(route_fractions.values())

        added_margin = field_mean - route_median
        meaningful_margin = field_fraction - route_fraction_median

        field_means.append(field_mean)
        paired_added_margins.append(added_margin)
        field_meaningful_fractions.append(field_fraction)
        paired_meaningful_margins.append(meaningful_margin)
        per_seed[str(seed)] = {
            "fieldMeanAddedRecovery": field_mean,
            "currentRouteMeanAddedRecovery": route_means,
            "currentRouteMedianMeanAddedRecovery": route_median,
            "pairedAddedMargin": added_margin,
            "fieldMeaningfulFraction": field_fraction,
            "currentRouteMeaningfulFraction": route_fractions,
            "currentRouteMedianMeaningfulFraction": route_fraction_median,
            "pairedMeaningfulMargin": meaningful_margin,
        }

    frozen_source = _verify_frozen_blobs()
    metric_equivalence = _verify_metric_equivalence()

    inference = {
        "fieldMeanAddedRecovery": {
            **_summary(field_means),
            "oneSided95LowerBound": _lower_bound(field_means),
            "nullThreshold": 0.002,
        },
        "pairedAddedMarginVsCurrentRouteMedian": {
            **_summary(paired_added_margins),
            "oneSided95LowerBound": _lower_bound(paired_added_margins),
            "nullThreshold": 0.0,
        },
        "fieldMeaningfulFraction": _summary(field_meaningful_fractions),
        "pairedMeaningfulMarginVsCurrentRouteMedian": {
            **_summary(paired_meaningful_margins),
            "oneSided95LowerBound": _lower_bound(paired_meaningful_margins),
            "nullThreshold": 0.0,
        },
        "studentT": {
            "df": 23,
            "oneSided95Critical": T_CRIT_95_ONE_SIDED_DF23,
            "clusterUnit": "master-seed",
        },
    }

    gates = {
        "completeConfirmationRectangle": confirmation_markers_valid,
        "allOriginalStageBGatesPass": all(fresh_stage_b.get("gates", {}).values()),
        "fieldMeanLowerBoundAbove0p002": inference["fieldMeanAddedRecovery"]["oneSided95LowerBound"] > 0.002,
        "pairedAddedMarginLowerBoundAboveZero": inference["pairedAddedMarginVsCurrentRouteMedian"]["oneSided95LowerBound"] > 0.0,
        "pairedMeaningfulMarginLowerBoundAboveZero": inference["pairedMeaningfulMarginVsCurrentRouteMedian"]["oneSided95LowerBound"] > 0.0,
        "frozenSourceBlobsExact": frozen_source["pass"],
        "metricEquivalenceExact": metric_equivalence["pass"],
    }

    return {
        "version": 1,
        "experiment": "sampling-invariance-capacity-confirmation-v1",
        "population": "fresh-confirmation",
        "seeds": list(CONFIRMATION_SEEDS),
        "frozenPilot": {
            "workflowRun": 33280597919,
            "artifact": 9722902487,
            "artifactDigest": "sha256:cb0e55e87861f235093341f0afaa73395dba710ee703c63d2adf5552432d6d47",
            "decision": "SAMPLING_INVARIANCE_CAPACITY_PROMISING",
        },
        "frozenSource": frozen_source,
        "metricEquivalence": metric_equivalence,
        "masterSeedInference": inference,
        "seedDiagnostics": per_seed,
        "freshStageBAggregate": fresh_stage_b,
        "gates": gates,
        "decision": (
            "SAMPLING_INVARIANCE_CAPACITY_CONFIRMED"
            if all(gates.values())
            else "SAMPLING_INVARIANCE_CAPACITY_NOT_CONFIRMED"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = aggregate(Path(args.results_dir))
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "gates": result["gates"],
                "masterSeedInference": result["masterSeedInference"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
