#!/usr/bin/env python3
"""Paid stage-1 response selector between adaptive depth and breadth switching."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import statistics
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1_PATH = ROOT / "experiments" / "search-leverage-v1" / "reproduce.py"

spec = importlib.util.spec_from_file_location("search_leverage_v1", V1_PATH)
v1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(v1)

ROUTE_ORDER = tuple(v1.ROUTE_ORDER)
CALIBRATION_SEEDS = (101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157)
HOLDOUT_SEEDS = (163, 167, 173)
ALL_SEEDS = CALIBRATION_SEEDS + HOLDOUT_SEEDS
THRESHOLDS = (0.0, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0)
REGIMES = ("local", "global")
EPSILON = v1.EPSILON


def _adaptive_state(brief: dict, seed: int, starts: list, target):
    selector = v1.TargetDistanceSelector(target)
    with TemporaryDirectory() as td:
        state, report = v1.run_search_from_starts(
            brief,
            seed,
            Path(td),
            copy.deepcopy(starts),
            selector,
        )
    candidates = list(state.candidates.values())
    metrics = v1._candidate_metrics(candidates, target, {c.id for c in starts})
    winner_id = report.get("provisionalChampion")
    if not winner_id:
        raise AssertionError("adaptive target search has no provisional champion")
    winner_distance = selector.distance(state.candidates[winner_id])
    if abs(winner_distance - metrics["bestDistance"]) > EPSILON:
        raise AssertionError("adaptive final champion is not objective best")
    metrics.update(
        policy="adaptive",
        winner=winner_id,
        winnerDistance=winner_distance,
        lineageDepth=v1._lineage_depth(winner_id, state.candidates),
        selectionStatus=report.get("selectionStatus"),
    )
    return state, metrics


def _prefix_candidates(state, start_ids: set[str]) -> list:
    starts = [c for c in state.candidates.values() if c.id in start_ids]
    explores = [c for c in state.candidates.values() if c.stage == "explore"]
    if {c.id for c in starts} != start_ids or len(starts) != v1.COMMON_STARTS:
        raise AssertionError(
            f"unexpected prefix start identities {sorted(c.id for c in starts)} != {sorted(start_ids)}"
        )
    expected_explores = v1.COMMON_STARTS * v1.EXPLORE_PER_BASIN
    if len(explores) != expected_explores:
        raise AssertionError(f"unexpected explore prefix count {len(explores)} != {expected_explores}")
    if any(c.basin not in start_ids for c in explores):
        raise AssertionError("explore prefix contains candidate outside common-start basins")
    return starts + explores


def _prefix_response(prefix: list, target, start_ids: set[str]) -> dict:
    target_frames = v1._frame_bytes(target)
    starts = [c for c in prefix if c.id in start_ids]
    explores = [c for c in prefix if c.stage == "explore"]
    initial_best = min(v1.phenotype_distance(c, target_frames) for c in starts)
    prefix_best = min(v1.phenotype_distance(c, target_frames) for c in prefix if c.checks.get("valid", False))
    gain = (initial_best - prefix_best) / max(initial_best, EPSILON)

    basin_gains = []
    improved_basins = 0
    for start in starts:
        parent_distance = v1.phenotype_distance(start, target_frames)
        basin_children = [c for c in explores if c.basin == start.id and c.checks.get("valid", False)]
        child_best = min(
            [parent_distance] + [v1.phenotype_distance(c, target_frames) for c in basin_children]
        )
        basin_gain = (parent_distance - child_best) / max(parent_distance, EPSILON)
        basin_gains.append(basin_gain)
        improved_basins += int(basin_gain > EPSILON)

    return {
        "initialBestDistance": initial_best,
        "prefixBestDistance": prefix_best,
        "normalizedBestGain": gain,
        "meanBasinGain": statistics.fmean(basin_gains),
        "maxBasinGain": max(basin_gains),
        "improvedBasins": improved_basins,
        "basinGains": basin_gains,
    }


def _breadth_switch(
    brief: dict,
    seed: int,
    route: str,
    starts: list,
    target,
    adaptive_state,
) -> dict:
    start_ids = {c.id for c in starts}
    prefix = _prefix_candidates(adaptive_state, start_ids)
    total_incremental = len(adaptive_state.candidates) - len(starts)
    prefix_incremental = len(prefix) - len(starts)
    remaining = total_incremental - prefix_incremental
    if remaining < 1:
        raise AssertionError("adaptive search leaves no budget after stage-1 prefix")

    version = v1.ROUTES[route].get("version", "1")
    rng = v1.representation_rng(seed, route, version, "stage1-response-breadth-v1")
    candidates = [copy.deepcopy(c) for c in prefix]
    existing_ids = {c.id for c in candidates}
    for index in range(1, remaining + 1):
        cid = f"SW-B{index}"
        if cid in existing_ids:
            raise AssertionError(f"breadth-switch id collision {cid}")
        cand = v1.Candidate(
            cid,
            route,
            cid,
            v1.ROUTES[route]["seed"](rng),
            None,
            "breadth-switch",
        )
        v1.evaluate_candidate(cand, brief)
        candidates.append(cand)

    if len(candidates) != len(adaptive_state.candidates):
        raise AssertionError("breadth-switch equal-evaluation budget invariant failed")
    metrics = v1._candidate_metrics(candidates, target, start_ids)
    metrics.update(
        policy="stage1-then-breadth",
        prefixIncrementalEvaluations=prefix_incremental,
        continuationEvaluations=remaining,
        lineageDepth=1,
    )
    return metrics


def choose_policy(response_gain: float, threshold: float) -> str:
    return "adaptive" if response_gain + EPSILON >= threshold else "stage1-then-breadth"


def run_block(route: str, seed: int, thresholds: tuple[float, ...]) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} is not predeclared")
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    if not thresholds or any(t not in THRESHOLDS for t in thresholds):
        raise ValueError(f"thresholds must be drawn from {THRESHOLDS}")

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
        state, adaptive = _adaptive_state(brief, seed, starts, target)
        prefix = _prefix_candidates(state, start_ids)
        current_prefix_fps = {c.id: v1.phenotype_fingerprint(c) for c in prefix}
        if prefix_fingerprints is None:
            prefix_fingerprints = current_prefix_fps
        elif prefix_fingerprints != current_prefix_fps:
            raise AssertionError("paid stage-1 prefix changed across target regimes")

        response = _prefix_response(prefix, target, start_ids)
        breadth = _breadth_switch(brief, seed, route, starts, target, state)
        if adaptive["totalCandidates"] != breadth["totalCandidates"]:
            raise AssertionError("adaptive/breadth-switch equal candidate budget failed")

        a_imp = float(adaptive["normalizedImprovement"])
        b_imp = float(breadth["normalizedImprovement"])
        oracle_policy = "adaptive" if a_imp + EPSILON >= b_imp else "stage1-then-breadth"
        oracle_imp = max(a_imp, b_imp)

        threshold_rows = {}
        for threshold in thresholds:
            chosen = choose_policy(float(response["normalizedBestGain"]), threshold)
            selected_imp = a_imp if chosen == "adaptive" else b_imp
            threshold_rows[str(threshold)] = {
                "chosenPolicy": chosen,
                "selectedImprovement": selected_imp,
                "oraclePolicy": oracle_policy,
                "oracleImprovement": oracle_imp,
                "choiceCorrect": chosen == oracle_policy,
                "strictWinVsAdaptive": selected_imp > a_imp + EPSILON,
                "nonWorseVsAdaptive": selected_imp + EPSILON >= a_imp,
            }

        regimes[kind] = {
            "target": v1._target_record(target, starts),
            "incrementalEvaluationBudget": adaptive["totalCandidates"] - len(starts),
            "prefixResponse": response,
            "adaptive": adaptive,
            "breadthSwitch": breadth,
            "thresholds": threshold_rows,
        }

    combined = {}
    for threshold in thresholds:
        key = str(threshold)
        selected = statistics.fmean(
            float(regimes[k]["thresholds"][key]["selectedImprovement"])
            for k in REGIMES
        )
        adaptive = statistics.fmean(
            float(regimes[k]["adaptive"]["normalizedImprovement"])
            for k in REGIMES
        )
        breadth = statistics.fmean(
            float(regimes[k]["breadthSwitch"]["normalizedImprovement"])
            for k in REGIMES
        )
        oracle = statistics.fmean(
            float(regimes[k]["thresholds"][key]["oracleImprovement"])
            for k in REGIMES
        )
        combined[key] = {
            "selectedImprovement": selected,
            "adaptiveImprovement": adaptive,
            "breadthSwitchImprovement": breadth,
            "adaptiveVsBreadthOracleImprovement": oracle,
            "strictWinVsAdaptive": selected > adaptive + EPSILON,
            "nonWorseVsAdaptive": selected + EPSILON >= adaptive,
        }

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "thresholds": list(thresholds),
        "times": list(v1.TIMES),
        "commonStartFingerprints": {c.id: v1.phenotype_fingerprint(c) for c in starts},
        "paidPrefixFingerprints": prefix_fingerprints,
        "signal": "normalized objective gain from common starts through exact adaptive explore stage",
        "decision": "continue adaptive when prefix gain >= threshold; otherwise spend remaining equal budget on independent breadth",
        "regimes": regimes,
        "combined": combined,
    }


def _parse_thresholds(raw: str) -> tuple[float, ...]:
    values = tuple(float(part.strip()) for part in raw.split(",") if part.strip())
    if len(set(values)) != len(values):
        raise ValueError("duplicate threshold")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    parser.add_argument("--thresholds", default=",".join(str(x) for x in THRESHOLDS))
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed, _parse_thresholds(args.thresholds)), indent=2))


if __name__ == "__main__":
    main()
