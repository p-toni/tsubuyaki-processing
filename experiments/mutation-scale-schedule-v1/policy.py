#!/usr/bin/env python3
"""Coarse-to-fine mutation-scale schedule experiment on existing adaptive search."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import statistics
from contextlib import contextmanager
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
CALIBRATION_SEEDS = (
    101, 103, 107, 109, 113, 127, 131, 137, 139,
    149, 151, 157, 163, 167, 173, 179, 181, 191,
)
HOLDOUT_SEEDS = (193, 197, 199)
ALL_SEEDS = CALIBRATION_SEEDS + HOLDOUT_SEEDS
CONTRASTS = (2.0 / 3.0, 0.8, 1.0, 1.25, 1.5)
REGIMES = ("local", "global")
EPSILON = v1.EPSILON

BASE_SCALES = {
    1.0: "explore",
    0.7: "roundA",
    0.55: "refine-local",
    1.2: "refine-jump",
}


def _scheduled_scale(scale: float, q: float) -> float:
    if abs(scale - 1.0) <= EPSILON:
        return 1.0 * q
    if abs(scale - 0.7) <= EPSILON:
        return 0.7
    if abs(scale - 0.55) <= EPSILON:
        return 0.55 / q
    if abs(scale - 1.2) <= EPSILON:
        return 1.2
    raise AssertionError(f"unexpected adaptive-search mutation scale {scale!r}")


@contextmanager
def _scheduled_mutator(route: str, q: float):
    original = v1.ROUTES[route]["mutate"]

    def wrapped(genome, rng, scale=1.0):
        return original(genome, rng, _scheduled_scale(float(scale), q))

    v1.ROUTES[route]["mutate"] = wrapped
    try:
        yield
    finally:
        v1.ROUTES[route]["mutate"] = original


def _metrics(state, report, starts, target, q: float | None) -> dict:
    selector = v1.TargetDistanceSelector(target)
    candidates = list(state.candidates.values())
    metrics = v1._candidate_metrics(candidates, target, {c.id for c in starts})
    winner_id = report.get("provisionalChampion")
    if not winner_id:
        raise AssertionError("target search has no provisional champion")
    winner_distance = selector.distance(state.candidates[winner_id])
    if abs(winner_distance - metrics["bestDistance"]) > EPSILON:
        raise AssertionError("final champion is not objective best")
    metrics.update(
        policy="baseline-adaptive" if q is None else "scheduled-adaptive",
        scheduleContrast=q,
        winner=winner_id,
        winnerDistance=winner_distance,
        lineageDepth=v1._lineage_depth(winner_id, state.candidates),
        selectionStatus=report.get("selectionStatus"),
        invalidCandidates=sum(not c.checks.get("valid", False) for c in candidates),
    )
    return metrics


def _canonical_signature(state, report) -> str:
    candidates = []
    for cid in sorted(state.candidates):
        c = state.candidates[cid]
        candidates.append({
            "id": c.id,
            "route": c.route,
            "basin": c.basin,
            "parentId": c.parent_id,
            "stage": c.stage,
            "genome": c.genome,
            "valid": bool(c.checks.get("valid", False)),
            "phenotypeFingerprint": v1.phenotype_fingerprint(c),
        })
    canonical = {
        "candidates": candidates,
        "stageDecisions": state.stage_decisions,
        "report": {
            "provisionalChampion": report.get("provisionalChampion"),
            "selectionStatus": report.get("selectionStatus"),
            "artisticFrontier": report.get("artisticFrontier"),
            "allocations": report.get("allocations"),
        },
    }
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def _run_plain(brief: dict, seed: int, starts: list, target):
    selector = v1.TargetDistanceSelector(target)
    with TemporaryDirectory() as td:
        state, report = v1.run_search_from_starts(
            brief, seed, Path(td), copy.deepcopy(starts), selector
        )
    return state, report, _metrics(state, report, starts, target, None)


def _run_schedule(brief: dict, seed: int, route: str, starts: list, target, q: float):
    selector = v1.TargetDistanceSelector(target)
    with _scheduled_mutator(route, q):
        with TemporaryDirectory() as td:
            state, report = v1.run_search_from_starts(
                brief, seed, Path(td), copy.deepcopy(starts), selector
            )
    return state, report, _metrics(state, report, starts, target, q)


def run_block(route: str, seed: int, contrasts: tuple[float, ...]) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} is not predeclared")
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    if not contrasts or any(all(abs(q-c) > EPSILON for c in CONTRASTS) for q in contrasts):
        raise ValueError(f"schedule contrasts must be drawn from {CONTRASTS}")
    if len({round(q, 12) for q in contrasts}) != len(contrasts):
        raise ValueError("duplicate schedule contrast")

    brief = v1._brief(route)
    starts = v1._generate_common_starts(brief, seed, route)
    targets = {
        "local": v1._local_target(brief, seed, route, starts[0]),
        "global": v1._global_target(brief, seed, route),
    }

    regimes = {}
    for kind, target in targets.items():
        baseline_state, baseline_report, baseline = _run_plain(brief, seed, starts, target)
        baseline_signature = _canonical_signature(baseline_state, baseline_report)
        rows = {}
        for q in contrasts:
            state, report, metrics = _run_schedule(brief, seed, route, starts, target, q)
            if metrics["totalCandidates"] != baseline["totalCandidates"]:
                raise AssertionError(
                    f"candidate-count drift at q={q}: "
                    f"{metrics['totalCandidates']} != {baseline['totalCandidates']}"
                )
            signature = _canonical_signature(state, report)
            exact_replay = signature == baseline_signature
            if abs(q - 1.0) <= EPSILON and not exact_replay:
                raise AssertionError("q=1.0 failed exact ordinary-baseline replay")
            metrics.update(
                trajectorySignature=signature,
                exactBaselineReplay=exact_replay,
                strictWinVsBaseline=(
                    float(metrics["normalizedImprovement"])
                    > float(baseline["normalizedImprovement"]) + EPSILON
                ),
                nonWorseVsBaseline=(
                    float(metrics["normalizedImprovement"]) + EPSILON
                    >= float(baseline["normalizedImprovement"])
                ),
                effectiveScales={
                    "explore": _scheduled_scale(1.0, q),
                    "roundA": _scheduled_scale(0.7, q),
                    "refineLocal": _scheduled_scale(0.55, q),
                    "refineJump": _scheduled_scale(1.2, q),
                },
            )
            rows[str(q)] = metrics

        regimes[kind] = {
            "target": v1._target_record(target, starts),
            "baseline": baseline,
            "baselineTrajectorySignature": baseline_signature,
            "schedules": rows,
        }

    combined = {}
    baseline_combined = statistics.fmean(
        float(regimes[k]["baseline"]["normalizedImprovement"])
        for k in REGIMES
    )
    for q in contrasts:
        key = str(q)
        value = statistics.fmean(
            float(regimes[k]["schedules"][key]["normalizedImprovement"])
            for k in REGIMES
        )
        combined[key] = {
            "combinedImprovement": value,
            "baselineCombinedImprovement": baseline_combined,
            "strictWinVsBaseline": value > baseline_combined + EPSILON,
            "nonWorseVsBaseline": value + EPSILON >= baseline_combined,
            "meanValidYield": statistics.fmean(
                float(regimes[k]["schedules"][key]["validYield"])
                for k in REGIMES
            ),
            "meanUniquePhenotypeRate": statistics.fmean(
                float(regimes[k]["schedules"][key]["uniquePhenotypeRate"])
                for k in REGIMES
            ),
            "meanWinnerLineageDepth": statistics.fmean(
                float(regimes[k]["schedules"][key]["lineageDepth"])
                for k in REGIMES
            ),
        }

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "contrasts": list(contrasts),
        "times": list(v1.TIMES),
        "commonStartFingerprints": {
            c.id: v1.phenotype_fingerprint(c) for c in starts
        },
        "schedule": "explore=1*q; roundA=.7; refine-local=.55/q; refine-jump=1.2",
        "regimes": regimes,
        "combined": combined,
    }


def _parse_contrasts(raw: str) -> tuple[float, ...]:
    return tuple(float(part.strip()) for part in raw.split(",") if part.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    parser.add_argument("--contrasts", default=",".join(str(x) for x in CONTRASTS))
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed, _parse_contrasts(args.contrasts)), indent=2))


if __name__ == "__main__":
    main()
