#!/usr/bin/env python3
"""Fail-closed reducer for the preregistered fresh mutation-scale confirmation."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
SEEDS = (
    1009, 1013, 1019, 1021,
    1031, 1033, 1039, 1049,
    1051, 1061, 1063, 1069,
    1087, 1091, 1093, 1097,
    1103, 1109, 1117, 1123,
    1129, 1151, 1153, 1163,
    1171, 1181, 1187, 1193,
    1201, 1213, 1217, 1223,
)
EXPECTED = {(route, seed) for route in ROUTES for seed in SEEDS}
# One-sided 95% Student-t critical value for df=31, frozen before outcomes.
T_CRIT_DF31_ONE_SIDED_95 = 1.695519
EPS = 1e-12


def _mean(xs):
    return statistics.fmean(xs) if xs else float("nan")


def _load(results_dir: Path):
    rows = {}
    ignored_smoke = []
    for path in sorted(results_dir.rglob("*.json")):
        record = json.loads(path.read_text())
        if not record.get("analysisSeed", False):
            ignored_smoke.append(str(path))
            continue
        key = (str(record["route"]), int(record["seed"]))
        if key in rows:
            raise AssertionError(f"duplicate route/seed block {key}: {path}")
        rows[key] = record

    got = set(rows)
    missing = sorted(EXPECTED - got)
    extra = sorted(got - EXPECTED)
    if missing or extra:
        raise AssertionError(f"incomplete confirmation rectangle missing={missing} extra={extra}")
    if len(rows) != len(EXPECTED):
        raise AssertionError(f"expected {len(EXPECTED)} blocks, got {len(rows)}")

    for key, row in rows.items():
        if row.get("metric") != "sparse-geometry-v1":
            raise AssertionError(f"metric drift for {key}")
        if float(row.get("baselineMultiplier")) != 1.0 or float(row.get("candidateMultiplier")) != 1.25:
            raise AssertionError(f"contrast drift for {key}")
        if not row.get("baselineExactOrdinaryReplay", False):
            raise AssertionError(f"baseline exact-replay gate failed for {key}")
        expected_combined = (float(row["localDelta"]) + float(row["globalDelta"])) / 2
        if abs(expected_combined - float(row["combinedDelta"])) > EPS:
            raise AssertionError(f"combined delta mismatch for {key}")
    return rows, ignored_smoke


def _effect_summary(rows):
    seed_effects = {}
    for seed in SEEDS:
        vals = [float(rows[(route, seed)]["combinedDelta"]) for route in ROUTES]
        seed_effects[seed] = _mean(vals)

    effects = list(seed_effects.values())
    mean = _mean(effects)
    median = statistics.median(effects)
    sd = statistics.stdev(effects)
    se = sd / math.sqrt(len(effects))
    lower = mean - T_CRIT_DF31_ONE_SIDED_95 * se

    route_effects = {}
    for route in ROUTES:
        vals = [float(rows[(route, seed)]["combinedDelta"]) for seed in SEEDS]
        route_effects[route] = {
            "mean": _mean(vals),
            "median": statistics.median(vals),
            "min": min(vals),
            "max": max(vals),
        }

    leave_seed = []
    for omitted in SEEDS:
        vals = [effect for seed, effect in seed_effects.items() if seed != omitted]
        leave_seed.append({"omittedSeed": omitted, "mean": _mean(vals)})

    leave_route = []
    for omitted in ROUTES:
        vals = [
            float(rows[(route, seed)]["combinedDelta"])
            for seed in SEEDS
            for route in ROUTES
            if route != omitted
        ]
        # Equal cells is equal-route/equal-seed here because the complete rectangle
        # contains exactly one cell per route×seed.
        leave_route.append({"omittedRoute": omitted, "mean": _mean(vals)})

    cells = []
    for route in ROUTES:
        for seed in SEEDS:
            row = rows[(route, seed)]
            cells.append({
                "route": route,
                "seed": seed,
                "delta": float(row["combinedDelta"]),
                "localDelta": float(row["localDelta"]),
                "globalDelta": float(row["globalDelta"]),
                "baseline": float(row["baselineCombinedImprovement"]),
                "candidate": float(row["candidateCombinedImprovement"]),
            })
    largest = max(cells, key=lambda row: abs(row["delta"]))

    local = [float(row["localDelta"]) for row in rows.values()]
    global_ = [float(row["globalDelta"]) for row in rows.values()]
    positive_cells = sum(float(row["combinedDelta"]) > 0 for row in rows.values())
    nonnegative_cells = sum(float(row["combinedDelta"]) >= 0 for row in rows.values())

    lower_positive = lower > 0
    leave_route_positive = min(row["mean"] for row in leave_route) > 0
    confirmed = lower_positive and leave_route_positive

    return {
        "primaryEstimand": "mean over complete master-seed equal-route mean effects",
        "completeMasterSeeds": len(SEEDS),
        "routes": len(ROUTES),
        "cells": len(cells),
        "meanSeedEffect": mean,
        "medianSeedEffect": median,
        "seedEffectSD": sd,
        "seedEffectSE": se,
        "studentTCriticalOneSided95Df31": T_CRIT_DF31_ONE_SIDED_95,
        "oneSided95LowerBound": lower,
        "routeEffects": route_effects,
        "seedEffects": {str(seed): effect for seed, effect in seed_effects.items()},
        "meanLocalDelta": _mean(local),
        "meanGlobalDelta": _mean(global_),
        "strictPositiveCells": positive_cells,
        "nonNegativeCells": nonnegative_cells,
        "leaveOneSeedOut": leave_seed,
        "leaveOneSeedOutMeanRange": [min(x["mean"] for x in leave_seed), max(x["mean"] for x in leave_seed)],
        "leaveOneRouteOut": leave_route,
        "leaveOneRouteOutMeanRange": [min(x["mean"] for x in leave_route), max(x["mean"] for x in leave_route)],
        "largestAbsoluteCell": largest,
        "preregisteredChecks": {
            "oneSided95LowerBoundAboveZero": lower_positive,
            "everyLeaveOneRouteOutMeanAboveZero": leave_route_positive,
        },
        "decision": "CONFIRMED" if confirmed else "NOT_CONFIRMED",
        "rows": cells,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    rows, ignored_smoke = _load(args.results_dir)
    summary = {
        "version": 1,
        "experiment": "mutation-scale-confirmation-v1",
        "metric": "sparse-geometry-v1",
        "freshSearchSeedsConsumed": True,
        "freshSeeds": list(SEEDS),
        "baselineMultiplier": 1.0,
        "candidateMultiplier": 1.25,
        "sequentialStopping": False,
        "reselectionAllowed": False,
        "ignoredSmokeArtifacts": ignored_smoke,
        "effect": _effect_summary(rows),
        "boundary": "mechanistic confirmation only; artistic authority and representation promotion remain out of scope",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
