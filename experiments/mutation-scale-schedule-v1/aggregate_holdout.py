#!/usr/bin/env python3
"""Aggregate the predeclared fresh-seed holdout for mutation-scale schedule v1.

The historical route-vote gate is preserved exactly as preregistered. Continuous
paired effects are also retained as diagnostics so the holdout does not discard
magnitude information before the later methodology audit.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
SEEDS = (193, 197, 199)
BASELINE = "1.0"
SELECTED = "1.25"
EPSILON = 1e-12


def _load_blocks(results_dir: Path) -> list[dict]:
    blocks = []
    for path in sorted(results_dir.rglob("*.json")):
        data = json.loads(path.read_text())
        if isinstance(data, dict) and data.get("route") in ROUTES and data.get("seed") in SEEDS:
            blocks.append(data)
    expected = {(route, seed) for route in ROUTES for seed in SEEDS}
    seen = {(b["route"], int(b["seed"])) for b in blocks}
    if seen != expected or len(blocks) != len(expected):
        raise AssertionError(f"holdout block mismatch: expected={sorted(expected)} seen={sorted(seen)} count={len(blocks)}")
    return blocks


def aggregate(blocks: list[dict]) -> dict:
    rows = []
    route_rows = {route: [] for route in ROUTES}
    for block in blocks:
        route = block["route"]
        seed = int(block["seed"])
        combined = block["combined"]
        if set(combined) != {BASELINE, SELECTED}:
            raise AssertionError(f"unexpected holdout contrasts for {route}/{seed}: {sorted(combined)}")
        baseline = float(combined[BASELINE]["combinedImprovement"])
        selected = float(combined[SELECTED]["combinedImprovement"])
        delta = selected - baseline
        local_base = float(block["regimes"]["local"]["schedules"][BASELINE]["normalizedImprovement"])
        local_sel = float(block["regimes"]["local"]["schedules"][SELECTED]["normalizedImprovement"])
        global_base = float(block["regimes"]["global"]["schedules"][BASELINE]["normalizedImprovement"])
        global_sel = float(block["regimes"]["global"]["schedules"][SELECTED]["normalizedImprovement"])
        row = {
            "route": route,
            "seed": seed,
            "baselineCombined": baseline,
            "selectedCombined": selected,
            "delta": delta,
            "strictWin": delta > EPSILON,
            "nonWorse": delta >= -EPSILON,
            "localDelta": local_sel - local_base,
            "globalDelta": global_sel - global_base,
        }
        rows.append(row)
        route_rows[route].append(row)

    routes = {}
    supporting = 0
    for route in ROUTES:
        rs = sorted(route_rows[route], key=lambda x: x["seed"])
        wins = sum(r["strictWin"] for r in rs)
        supports = wins >= 2
        supporting += int(supports)
        routes[route] = {
            "strictWins": wins,
            "supportsLegacyGate": supports,
            "meanDelta": statistics.fmean(r["delta"] for r in rs),
            "medianDelta": statistics.median(r["delta"] for r in rs),
            "meanLocalDelta": statistics.fmean(r["localDelta"] for r in rs),
            "meanGlobalDelta": statistics.fmean(r["globalDelta"] for r in rs),
            "seeds": rs,
        }

    deltas = [r["delta"] for r in rows]
    result = {
        "version": 1,
        "complete": True,
        "selectedContrast": 1.25,
        "baselineContrast": 1.0,
        "holdoutSeeds": list(SEEDS),
        "blocks": len(rows),
        "legacyPreregisteredGate": {
            "routeRule": ">=2/3 strict-win seeds",
            "generalRule": ">=4/5 supporting routes",
            "supportingRoutes": supporting,
            "generalSupport": supporting >= 4,
            "classification": (
                "general global stage-schedule leverage supported" if supporting >= 4
                else "mixed / representation-dependent stage-schedule signal" if supporting == 3
                else "general global stage-schedule leverage not supported"
            ),
        },
        "continuousPairedDiagnosticsPredeclaredBeforeHoldoutResults": {
            "meanDelta": statistics.fmean(deltas),
            "medianDelta": statistics.median(deltas),
            "strictWins": sum(r["strictWin"] for r in rows),
            "nonWorse": sum(r["nonWorse"] for r in rows),
            "meanLocalDelta": statistics.fmean(r["localDelta"] for r in rows),
            "meanGlobalDelta": statistics.fmean(r["globalDelta"] for r in rows),
            "routeMeanDelta": {route: routes[route]["meanDelta"] for route in ROUTES},
        },
        "routes": routes,
        "boundary": "objective target-recovery evidence only; legacy gate retained for protocol fidelity; continuous diagnostics retained for subsequent methodology audit",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(_load_blocks(args.results_dir)), indent=2))


if __name__ == "__main__":
    main()
