#!/usr/bin/env python3
"""Fixed post-prefix hedge between adaptive continuation and independent breadth."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAGE1_PATH = ROOT / "experiments" / "stage1-response-topology-v1" / "policy.py"

spec = importlib.util.spec_from_file_location("stage1_response_policy", STAGE1_PATH)
stage1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(stage1)

v1 = stage1.v1
ROUTE_ORDER = tuple(stage1.ROUTE_ORDER)
CALIBRATION_SEEDS = tuple(stage1.ALL_SEEDS)
HOLDOUT_SEEDS = (179, 181, 191)
ALL_SEEDS = CALIBRATION_SEEDS + HOLDOUT_SEEDS
HEDGE_SHARES = (0.0, 0.25, 0.5, 0.75, 1.0)
REGIMES = tuple(stage1.REGIMES)
EPSILON = stage1.EPSILON


def _adaptive_count(remaining: int, share: float) -> int:
    if remaining < 0:
        raise ValueError("remaining must be non-negative")
    if share not in HEDGE_SHARES:
        raise ValueError(f"share must be drawn from {HEDGE_SHARES}")
    return min(remaining, max(0, int(math.floor(share * remaining + 0.5))))


def _hedge_metrics(brief: dict, seed: int, route: str, starts: list, target, adaptive_state, share: float) -> dict:
    start_ids = {c.id for c in starts}
    prefix = stage1._prefix_candidates(adaptive_state, start_ids)
    prefix_ids = {c.id for c in prefix}
    continuation = [c for c in adaptive_state.candidates.values() if c.id not in prefix_ids]
    remaining = len(continuation)
    keep_adaptive = _adaptive_count(remaining, share)
    breadth_count = remaining - keep_adaptive

    candidates = [copy.deepcopy(c) for c in prefix]
    candidates.extend(copy.deepcopy(c) for c in continuation[:keep_adaptive])

    version = v1.ROUTES[route].get("version", "1")
    rng = v1.representation_rng(seed, route, version, "stage1-response-breadth-v1")
    for index in range(1, breadth_count + 1):
        cand = v1.Candidate(
            f"HG-B{index}",
            route,
            f"HG-B{index}",
            v1.ROUTES[route]["seed"](rng),
            None,
            "fixed-hedge-breadth",
        )
        v1.evaluate_candidate(cand, brief)
        candidates.append(cand)

    if len(candidates) != len(adaptive_state.candidates):
        raise AssertionError("fixed hedge equal-evaluation budget invariant failed")

    metrics = v1._candidate_metrics(candidates, target, start_ids)
    metrics.update(
        policy="fixed-hedge",
        adaptiveShare=share,
        prefixCandidates=len(prefix),
        continuationEvaluations=remaining,
        adaptiveContinuationEvaluations=keep_adaptive,
        breadthContinuationEvaluations=breadth_count,
    )
    return metrics


def run_block(route: str, seed: int, shares: tuple[float, ...]) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} is not predeclared")
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    if not shares or any(s not in HEDGE_SHARES for s in shares):
        raise ValueError(f"shares must be drawn from {HEDGE_SHARES}")

    brief = v1._brief(route)
    starts = v1._generate_common_starts(brief, seed, route)
    start_ids = {c.id for c in starts}
    targets = {
        "local": v1._local_target(brief, seed, route, starts[0]),
        "global": v1._global_target(brief, seed, route),
    }

    regimes = {}
    prefix_fingerprints = None
    for kind, target in targets.items():
        state, adaptive = stage1._adaptive_state(brief, seed, starts, target)
        prefix = stage1._prefix_candidates(state, start_ids)
        current_prefix_fps = {c.id: v1.phenotype_fingerprint(c) for c in prefix}
        if prefix_fingerprints is None:
            prefix_fingerprints = current_prefix_fps
        elif prefix_fingerprints != current_prefix_fps:
            raise AssertionError("paid prefix changed across target regimes")

        share_rows = {}
        for share in shares:
            hedge = _hedge_metrics(brief, seed, route, starts, target, state, share)
            if int(hedge["totalCandidates"]) != int(adaptive["totalCandidates"]):
                raise AssertionError("adaptive/hedge equal candidate budget failed")
            if share == 1.0 and abs(float(hedge["normalizedImprovement"]) - float(adaptive["normalizedImprovement"])) > EPSILON:
                raise AssertionError("100% adaptive hedge must reproduce adaptive objective result")
            share_rows[str(share)] = hedge

        oracle_imp = max(float(row["normalizedImprovement"]) for row in share_rows.values())
        regimes[kind] = {
            "target": v1._target_record(target, starts),
            "adaptive": adaptive,
            "shares": share_rows,
            "fixedShareOracleImprovement": oracle_imp,
        }

    combined = {}
    for share in shares:
        key = str(share)
        selected = statistics.fmean(float(regimes[k]["shares"][key]["normalizedImprovement"]) for k in REGIMES)
        adaptive = statistics.fmean(float(regimes[k]["adaptive"]["normalizedImprovement"]) for k in REGIMES)
        oracle = statistics.fmean(float(regimes[k]["fixedShareOracleImprovement"]) for k in REGIMES)
        combined[key] = {
            "hedgeImprovement": selected,
            "adaptiveImprovement": adaptive,
            "fixedShareOracleImprovement": oracle,
            "strictWinVsAdaptive": selected > adaptive + EPSILON,
            "nonWorseVsAdaptive": selected + EPSILON >= adaptive,
        }

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "shares": list(shares),
        "times": list(v1.TIMES),
        "commonStartFingerprints": {c.id: v1.phenotype_fingerprint(c) for c in starts},
        "paidPrefixFingerprints": prefix_fingerprints,
        "policy": "exact paid explore prefix, then fixed fraction of remaining budget keeps causal adaptive continuation and the rest becomes independent breadth",
        "rounding": "adaptive continuation count = floor(share * remaining + 0.5)",
        "regimes": regimes,
        "combined": combined,
    }


def _parse_shares(raw: str) -> tuple[float, ...]:
    values = tuple(float(part.strip()) for part in raw.split(",") if part.strip())
    if len(set(values)) != len(values):
        raise ValueError("duplicate share")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    parser.add_argument("--shares", default=",".join(str(x) for x in HEDGE_SHARES))
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed, _parse_shares(args.shares)), indent=2))


if __name__ == "__main__":
    main()
