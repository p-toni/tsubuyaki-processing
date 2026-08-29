#!/usr/bin/env python3
"""Fail-closed reducer for repertoire-allocation-v1."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

from run import PILOT_SEEDS, ROUTE_ORDER, GENERATED_PER_ARM, EVENTS_PER_BASIN, STARTS_PER_ROUTE

EXPECTED_BLOCKS = len(PILOT_SEEDS) * len(ROUTE_ORDER)


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
    if not values:
        raise ValueError("cannot summarize empty values")
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def _policy_diag_mean(blocks: list[dict], policy: str, key: str) -> float:
    return statistics.fmean(float(block["policies"][policy]["diagnostics"][key]) for block in blocks)


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
        if route not in ROUTE_ORDER or seed not in PILOT_SEEDS:
            raise AssertionError(f"out-of-contract block {key}")
        if block.get("analysisSeed") is not True or block.get("freshSearchEvidence") is not False:
            raise AssertionError(f"block {key} evidence boundary drift")
        if block.get("descriptorVersion") != "structural-v1":
            raise AssertionError(f"block {key} descriptor version drift")
        if block.get("metric") != "sparse-geometry-v1":
            raise AssertionError(f"block {key} metric drift")
        invariants = block.get("hardInvariants") or {}
        if not invariants or not all(bool(value) for value in invariants.values()):
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

    expected = {(route, seed) for route in ROUTE_ORDER for seed in PILOT_SEEDS}
    if seen != expected:
        raise AssertionError("route×seed rectangle incomplete")
    if any(len(by_seed[seed]) != len(ROUTE_ORDER) for seed in PILOT_SEEDS):
        raise AssertionError("one or more master seeds are incomplete")
    if any(len(by_route[route]) != len(PILOT_SEEDS) for route in ROUTE_ORDER):
        raise AssertionError("one or more route strata are incomplete")

    seed_primary = {
        seed: statistics.fmean(float(block["primaryDelta"]) for block in by_seed[seed])
        for seed in PILOT_SEEDS
    }
    seed_robustness = {
        seed: statistics.fmean(float(block["robustnessDelta"]) for block in by_seed[seed])
        for seed in PILOT_SEEDS
    }
    primary_values = [seed_primary[seed] for seed in PILOT_SEEDS]
    robustness_values = [seed_robustness[seed] for seed in PILOT_SEEDS]

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
        effects = [
            statistics.fmean(
                float(next(block for block in by_seed[seed] if block["route"] == route)["primaryDelta"])
                for route in retained
            )
            for seed in PILOT_SEEDS
        ]
        leave_one_route_out.append({"omittedRoute": omitted, "primaryMean": statistics.fmean(effects)})

    target_deltas = {"local": [], "global": []}
    for block in blocks:
        baseline = {
            item["target"]: float(item["normalizedGain"])
            for item in block["policies"]["lineage-depth"]["portfolio"]["targetGains"]
        }
        repertoire = {
            item["target"]: float(item["normalizedGain"])
            for item in block["policies"]["repertoire-preserving"]["portfolio"]["targetGains"]
        }
        if set(baseline) != set(repertoire):
            raise AssertionError("policy target portfolios differ")
        for target in baseline:
            kind = "global" if target.startswith("TARGET-GLOBAL") else "local"
            target_deltas[kind].append(repertoire[target] - baseline[target])

    mechanism = {}
    for key in (
        "occupiedNiches",
        "basinNicheSlots",
        "newNicheChildren",
        "uniqueRenderedPhenotypes",
        "uniquePhenotypeRate",
        "validYield",
    ):
        baseline_mean = _policy_diag_mean(blocks, "lineage-depth", key)
        repertoire_mean = _policy_diag_mean(blocks, "repertoire-preserving", key)
        mechanism[key] = {
            "lineageDepthMean": baseline_mean,
            "repertoireMean": repertoire_mean,
            "delta": repertoire_mean - baseline_mean,
        }

    primary_mean = statistics.fmean(primary_values)
    robustness_mean = statistics.fmean(robustness_values)
    loro_all_positive = all(item["primaryMean"] > 0 for item in leave_one_route_out)
    gates = {
        "completeHardInvariantRectangle": True,
        "completeSeedMeanPrimaryPositive": primary_mean > 0,
        "everyLeaveOneRouteOutPrimaryPositive": loro_all_positive,
        "completeSeedMeanRobustnessPositive": robustness_mean > 0,
    }
    promising = all(gates.values())

    largest_cell = max(
        blocks,
        key=lambda block: abs(float(block["primaryDelta"])),
    )

    return {
        "version": 1,
        "decision": "PILOT_PROMISING" if promising else "PILOT_NOT_PROMISING",
        "freshSearchEvidence": False,
        "population": {
            "masterSeeds": len(PILOT_SEEDS),
            "routes": len(ROUTE_ORDER),
            "routeSeedBlocks": len(blocks),
            "generatedCandidatesPerArmPerBlock": GENERATED_PER_ARM,
        },
        "gates": gates,
        "primary": {
            "completeMasterSeedEffects": _summary(primary_values),
            "seedEffects": {str(seed): seed_primary[seed] for seed in PILOT_SEEDS},
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
            "seedEffects": {str(seed): seed_robustness[seed] for seed in PILOT_SEEDS},
            "routeMeans": route_robustness,
        },
        "targetPortfolioDiagnostics": {
            "localTargetDelta": _summary(target_deltas["local"]),
            "globalTargetDelta": _summary(target_deltas["global"]),
        },
        "mechanismDiagnostics": mechanism,
        "interpretationBoundary": "consumed-seed mechanical pilot only; route signs and repertoire coverage diagnostics cannot override the preregistered capability gate",
        "ifPromising": "use complete-master-seed variance to preregister a fresh fixed-sample confirmation without tuning this allocator",
        "ifNotPromising": "do not tune structural-v1 or this allocator on the pilot outcomes; move up a level or formulate a new allocation hypothesis",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(Path(args.results_dir)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
