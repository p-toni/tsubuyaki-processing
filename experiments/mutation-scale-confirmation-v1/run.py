#!/usr/bin/env python3
"""Run one fresh mutation-scale confirmation block under sparse-geometry-v1."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
POLICY_PATH = ROOT / "experiments" / "mutation-scale-v1" / "policy.py"
METRIC_PATH = ROOT / "experiments" / "search-history-geometry-replay-v1" / "metric.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


policy = _load("mutation_scale_confirmation_policy", POLICY_PATH)
metric = _load("mutation_scale_confirmation_metric", METRIC_PATH)
metric.install_sparse_geometry_metric(policy.v1)

ROUTES = tuple(policy.ROUTE_ORDER)
FRESH_SEEDS = (
    1009, 1013, 1019, 1021,
    1031, 1033, 1039, 1049,
    1051, 1061, 1063, 1069,
    1087, 1091, 1093, 1097,
    1103, 1109, 1117, 1123,
    1129, 1151, 1153, 1163,
    1171, 1181, 1187, 1193,
    1201, 1213, 1217, 1223,
)
SMOKE_SEED = 9001
ALLOWED_SEEDS = FRESH_SEEDS + (SMOKE_SEED,)
BASELINE = 1.0
CANDIDATE = 1.25

# The historical #62 runner validates against its original seed registry. Extend
# only that registry; target construction and all RNG behavior accept arbitrary
# integer master seeds and remain otherwise unchanged.
policy.ALL_SEEDS = tuple(dict.fromkeys(tuple(policy.ALL_SEEDS) + ALLOWED_SEEDS))


def run_block(route: str, seed: int) -> dict:
    if route not in ROUTES:
        raise ValueError(f"route {route!r} is not predeclared")
    if seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {seed} is not in the preregistered fresh/smoke population")

    raw = policy.run_block(route, seed, (BASELINE, CANDIDATE))
    regimes = {}
    exact = True
    for regime in policy.REGIMES:
        record = raw["regimes"][regime]
        baseline = record["multipliers"][str(BASELINE)]
        candidate = record["multipliers"][str(CANDIDATE)]
        if not baseline.get("exactBaselineReplay", False):
            raise AssertionError(f"m=1.0 failed exact ordinary-baseline replay for {route}/{seed}/{regime}")
        exact = exact and bool(baseline["exactBaselineReplay"])
        regimes[regime] = {
            "baselineImprovement": float(baseline["normalizedImprovement"]),
            "candidateImprovement": float(candidate["normalizedImprovement"]),
            "delta": float(candidate["normalizedImprovement"]) - float(baseline["normalizedImprovement"]),
            "baselineTrajectorySignature": baseline["trajectorySignature"],
            "candidateTrajectorySignature": candidate["trajectorySignature"],
            "baselineExactOrdinaryReplay": bool(baseline["exactBaselineReplay"]),
            "baselineWinner": baseline["winner"],
            "candidateWinner": candidate["winner"],
            "baselineLineageDepth": baseline["lineageDepth"],
            "candidateLineageDepth": candidate["lineageDepth"],
            "baselineValidYield": baseline["validYield"],
            "candidateValidYield": candidate["validYield"],
            "baselineUniquePhenotypeRate": baseline["uniquePhenotypeRate"],
            "candidateUniquePhenotypeRate": candidate["uniquePhenotypeRate"],
        }

    baseline_combined = float(raw["combined"][str(BASELINE)]["combinedImprovement"])
    candidate_combined = float(raw["combined"][str(CANDIDATE)]["combinedImprovement"])
    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "analysisSeed": seed in FRESH_SEEDS,
        "metric": "sparse-geometry-v1",
        "metricSource": "experiments/search-measurement-geometry-v1/audit.py",
        "baselineMultiplier": BASELINE,
        "candidateMultiplier": CANDIDATE,
        "intervention": "multiply only the existing numeric mutator scale argument by 1.25; alpha jitter unchanged",
        "eventAligned": True,
        "baselineExactOrdinaryReplay": exact,
        "baselineCombinedImprovement": baseline_combined,
        "candidateCombinedImprovement": candidate_combined,
        "combinedDelta": candidate_combined - baseline_combined,
        "localDelta": regimes["local"]["delta"],
        "globalDelta": regimes["global"]["delta"],
        "regimes": regimes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTES, required=True)
    parser.add_argument("--seed", type=int, choices=ALLOWED_SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
