#!/usr/bin/env python3
"""Fail-closed reducer for fresh repertoire-allocation confirmation."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from run import FRESH_SEEDS, ROUTE_ORDER, GENERATED_PER_ARM, EVENTS_PER_BASIN, STARTS_PER_ROUTE

EXPECTED_BLOCKS = len(FRESH_SEEDS) * len(ROUTE_ORDER)
T_CRIT_ONE_SIDED_95_DF23 = 1.713871527747048


def _load_blocks(root: Path) -> list[dict]:
    blocks = []
    for path in sorted(root.rglob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception as exc:
            raise AssertionError(f"invalid JSON artifact {path}: {exc}") from exc
        if isinstance(data, dict) and "primaryDelta" in data and "route" in data and "seed" in data:
            blocks.append(data)
    return blocks


def _summary(values: list[float]) -> dict[str, float | int]:
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def _lower_bound(values: list[float]) -> float:
    if len(values) != len(FRESH_SEEDS):
        raise AssertionError("lower bound requires the complete frozen master-seed population")
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    return mean - T_CRIT_ONE_SIDED_95_DF23 * sd / math.sqrt(len(values))


def aggregate(results_dir: Path) -> dict:
    blocks = _load_blocks(results_dir)
    if len(blocks) != EXPECTED_BLOCKS:
        raise AssertionError(f"expected {EXPECTED_BLOCKS} route×seed blocks, found {len(blocks)}")

    seen = set()
    by_seed: dict[int, list[dict]] = defaultdict(list)
    by_route: dict[str, list[dict]] = defaultdict(list)
    for block in blocks:
        route = str(block["route"])
        seed = int(block["seed"])
        key = (route, seed)
        if key in seen:
            raise AssertionError(f"duplicate block {key}")
        seen.add(key)
        if route not in ROUTE_ORDER or seed not in FRESH_SEEDS:
            raise AssertionError(f"out-of-contract block {key}")
        if block.get("analysisSeed") is not True or block.get("freshSearchEvidence") is not True:
            raise AssertionError(f"block {key} fresh-evidence boundary drift")
        if block.get("descriptorVersion") != "structural-v1":
            raise AssertionError(f"block {key} descriptor version drift")
        if block.get("metric") != "sparse-geometry-v1":
            raise AssertionError(f"block {key} metric drift")
        confirmation = block.get("confirmation") or {}
        if confirmation.get("mechanism") != "repertoire-allocation-v1-frozen":
            raise AssertionError(f"block {key} mechanism marker drift")
        invariants = block.get("hardInvariants") or {}
        if not invariants or not all(bool(v) for v in invariants.values()):
            raise AssertionError(f"block {key} hard invariant failure: {invariants}")
        for policy in ("lineage-depth", "repertoire-preserving"):
            diag = block["policies"][policy]["diagnostics"]
            if int(diag["generatedCandidates"]) != GENERATED_PER_ARM:
                raise AssertionError(f"block {key}/{policy} generated budget drift")
            events = diag["eventsPerBasin"]
            if len(events) != STARTS_PER_ROUTE or any(int(v) != EVENTS_PER_BASIN for v in events.values()):
                raise AssertionError(f"block {key}/{policy} basin budget drift")
        by_seed[seed].append(block)
        by_route[route].append(block)

    expected = {(route, seed) for route in ROUTE_ORDER for seed in FRESH_SEEDS}
    if seen != expected:
        raise AssertionError("route×seed rectangle incomplete")
    if any(len(by_seed[seed]) != len(ROUTE_ORDER) for seed in FRESH_SEEDS):
        raise AssertionError("one or more master seeds are incomplete")
    if any(len(by_route[route]) != len(FRESH_SEEDS) for route in ROUTE_ORDER):
        raise AssertionError("one or more route strata are incomplete")

    seed_primary = {
        seed: statistics.fmean(float(block["primaryDelta"]) for block in by_seed[seed])
        for seed in FRESH_SEEDS
    }
    seed_robustness = {
        seed: statistics.fmean(float(block["robustnessDelta"]) for block in by_seed[seed])
        for seed in FRESH_SEEDS
    }
    primary_values = [seed_primary[seed] for seed in FRESH_SEEDS]
    robustness_values = [seed_robustness[seed] for seed in FRESH_SEEDS]

    route_primary = {
        route: statistics.fmean(float(block["primaryDelta"]) for block in by_route[route])
        for route in ROUTE_ORDER
    }
    route_robustness = {
        route: statistics.fmean(float(block["robustnessDelta"]) for block in by_route[route])
        for route in ROUTE_ORDER
    }

    leave_one_route_out = []
    for omitted in ROUTE_ORDER:
        retained = [route for route in ROUTE_ORDER if route != omitted]
        effects = []
        for seed in FRESH_SEEDS:
            route_map = {str(block["route"]): block for block in by_seed[seed]}
            effects.append(statistics.fmean(float(route_map[route]["primaryDelta"]) for route in retained))
        leave_one_route_out.append({"omittedRoute": omitted, "primaryMean": statistics.fmean(effects)})

    primary_lb = _lower_bound(primary_values)
    robustness_lb = _lower_bound(robustness_values)
    loro_all_positive = all(item["primaryMean"] > 0 for item in leave_one_route_out)
    gates = {
        "completeHardInvariantRectangle": True,
        "primaryOneSided95LowerBoundPositive": primary_lb > 0,
        "everyLeaveOneRouteOutPrimaryPositive": loro_all_positive,
        "robustnessOneSided95LowerBoundPositive": robustness_lb > 0,
    }
    confirmed = all(gates.values())

    largest_cell = max(blocks, key=lambda block: abs(float(block["primaryDelta"])))

    return {
        "version": 1,
        "decision": "CONFIRMED" if confirmed else "NOT_CONFIRMED",
        "freshSearchEvidence": True,
        "population": {
            "masterSeeds": len(FRESH_SEEDS),
            "routes": len(ROUTE_ORDER),
            "routeSeedBlocks": len(blocks),
            "generatedCandidatesPerArmPerBlock": GENERATED_PER_ARM,
            "seeds": list(FRESH_SEEDS),
        },
        "preregisteredInference": {
            "test": "Student-t one-sided 95% lower bound over complete master-seed effects",
            "df": len(FRESH_SEEDS) - 1,
            "criticalValue": T_CRIT_ONE_SIDED_95_DF23,
            "noEarlyStopping": True,
            "noSeedReplacement": True,
        },
        "gates": gates,
        "primary": {
            "completeMasterSeedEffects": _summary(primary_values),
            "oneSided95LowerBound": primary_lb,
            "seedEffects": {str(seed): seed_primary[seed] for seed in FRESH_SEEDS},
            "routeMeans": route_primary,
            "leaveOneRouteOut": leave_one_route_out,
            "leaveOneRouteOutRange": [
                min(item["primaryMean"] for item in leave_one_route_out),
                max(item["primaryMean"] for item in leave_one_route_out),
            ],
            "largestAbsoluteRouteSeedCell": {
                "route": largest_cell["route"],
                "seed": largest_cell["seed"],
                "primaryDelta": largest_cell["primaryDelta"],
            },
        },
        "robustness": {
            "completeMasterSeedEffects": _summary(robustness_values),
            "oneSided95LowerBound": robustness_lb,
            "seedEffects": {str(seed): seed_robustness[seed] for seed in FRESH_SEEDS},
            "routeMeans": route_robustness,
        },
        "interpretationBoundary": "fresh mechanical confirmation of the exact #77 allocator only; route signs and diagnostics cannot override the preregistered gates",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(Path(args.results_dir)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
