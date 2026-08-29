#!/usr/bin/env python3
"""Aggregate the complete #56-#63 geometry replay without new inferential gates."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
EPSILON = 1e-12

TOPOLOGY_AGG_PATH = ROOT / "experiments" / "topology-structural-replay-v1" / "aggregate.py"
_spec = importlib.util.spec_from_file_location("historical_topology_aggregate", TOPOLOGY_AGG_PATH)
topo = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(topo)

SEEDS = {
    "search-leverage": (101, 103, 107),
    "route-conditional": (109, 113, 127),
    "online-probe": (101, 103, 107, 109, 113, 127, 131, 137, 139),
    "start-state": (101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157),
    "stage1-response": (101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173),
    "fixed-hedge": (101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191),
    "mutation-scale": (101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199),
    "mutation-schedule": (101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199),
}
CALIBRATION_18 = SEEDS["mutation-scale"][:18]
RETROSPECTIVE_HOLDOUT = (193, 197, 199)
MULTIPLIERS = (0.5, 0.75, 1.0, 1.25, 1.5)
CONTRASTS = (2.0 / 3.0, 0.8, 1.0, 1.25, 1.5)

HISTORICAL = {
    "mutationScale": {
        "selected": 1.0,
        "holdoutOpenedAtExperimentTime": False,
        "historicalConclusion": "retain current global mutation scale",
    },
    "mutationSchedule": {
        "selected": 1.25,
        "holdoutOpenedAtExperimentTime": True,
        "historicalHoldoutMeanDelta": 0.003172,
        "historicalHoldoutMedianDelta": -0.001338,
        "historicalConclusion": "reject a general stage-schedule change; retain current schedule",
    },
}


def _load(results_dir: Path) -> dict[str, dict[tuple[str, int], dict]]:
    blocks = {name: {} for name in SEEDS}
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        meta = doc.get("structuralReplay")
        if not isinstance(meta, dict) or meta.get("metric") != "sparse-geometry-v1":
            continue
        experiment = meta.get("experiment")
        if experiment not in blocks:
            continue
        route = str(doc.get("route"))
        seed = int(doc.get("seed"))
        key = (route, seed)
        if key in blocks[experiment]:
            raise AssertionError(f"duplicate {experiment} block {key}")
        blocks[experiment][key] = doc

    for experiment, seeds in SEEDS.items():
        expected = {(route, seed) for route in ROUTES for seed in seeds}
        actual = set(blocks[experiment])
        if actual != expected:
            raise AssertionError(
                f"{experiment} block mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
            )
    return blocks


def _key_for(mapping: dict, value: float) -> str:
    for key in mapping:
        try:
            if abs(float(key) - value) <= EPSILON:
                return str(key)
        except (TypeError, ValueError):
            pass
    raise KeyError(f"numeric key {value} absent from {sorted(mapping)}")


def _balanced_mean(rows: list[dict]) -> float:
    by_seed: dict[int, list[float]] = {}
    for row in rows:
        by_seed.setdefault(int(row["seed"]), []).append(float(row["delta"]))
    return statistics.fmean(statistics.fmean(values) for values in by_seed.values())


def _effect_summary(rows: list[dict]) -> dict:
    if not rows:
        return {"blocks": 0, "seeds": 0}

    seed_ids = sorted({int(row["seed"]) for row in rows})
    route_ids = tuple(route for route in ROUTES if any(row["route"] == route for row in rows))
    expected = {(route, seed) for route in route_ids for seed in seed_ids}
    actual = {(str(row["route"]), int(row["seed"])) for row in rows}
    complete = actual == expected and len(rows) == len(expected)

    route_summary = {}
    for route in route_ids:
        values = [float(row["delta"]) for row in rows if row["route"] == route]
        route_summary[route] = {
            "mean": statistics.fmean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
        }

    seed_summary = {}
    seed_effects = []
    for seed in seed_ids:
        values = [float(row["delta"]) for row in rows if int(row["seed"]) == seed]
        effect = statistics.fmean(values)
        seed_effects.append(effect)
        seed_summary[str(seed)] = {
            "equalRouteMean": effect,
            "medianRouteDelta": statistics.median(values),
            "minRouteDelta": min(values),
            "maxRouteDelta": max(values),
        }

    mean_effect = statistics.fmean(seed_effects)
    sd = statistics.stdev(seed_effects) if len(seed_effects) >= 2 else None
    se = sd / math.sqrt(len(seed_effects)) if sd is not None else None

    leave_seed = []
    if len(seed_ids) > 1:
        for seed in seed_ids:
            kept = [row for row in rows if int(row["seed"]) != seed]
            leave_seed.append({"omittedSeed": seed, "mean": _balanced_mean(kept)})
    leave_route = []
    if len(route_ids) > 1:
        for route in route_ids:
            kept = [row for row in rows if row["route"] != route]
            leave_route.append({"omittedRoute": route, "mean": _balanced_mean(kept)})

    largest = max(rows, key=lambda row: abs(float(row["delta"])))
    local = [float(row["localDelta"]) for row in rows if row.get("localDelta") is not None]
    global_ = [float(row["globalDelta"]) for row in rows if row.get("globalDelta") is not None]

    return {
        "blocks": len(rows),
        "seeds": len(seed_ids),
        "routes": len(route_ids),
        "completeRouteSeedRectangle": complete,
        "primaryEstimand": "mean over complete master-seed equal-route mean effects",
        "meanSeedEffect": mean_effect,
        "medianSeedEffect": statistics.median(seed_effects),
        "seedEffectSD": sd,
        "seedEffectSE": se,
        "routeEffects": route_summary,
        "seedEffects": seed_summary,
        "meanLocalDelta": statistics.fmean(local) if local else None,
        "meanGlobalDelta": statistics.fmean(global_) if global_ else None,
        "strictPositiveCells": sum(float(row["delta"]) > EPSILON for row in rows),
        "nonNegativeCells": sum(float(row["delta"]) >= -EPSILON for row in rows),
        "leaveOneSeedOut": leave_seed,
        "leaveOneSeedOutMeanRange": [
            min(item["mean"] for item in leave_seed),
            max(item["mean"] for item in leave_seed),
        ] if leave_seed else None,
        "leaveOneRouteOut": leave_route,
        "leaveOneRouteOutMeanRange": [
            min(item["mean"] for item in leave_route),
            max(item["mean"] for item in leave_route),
        ] if leave_route else None,
        "largestAbsoluteCell": largest,
        "rows": sorted(rows, key=lambda row: (ROUTES.index(row["route"]), int(row["seed"]))),
    }


def _topology_summary(blocks: dict[str, dict[tuple[str, int], dict]]) -> dict:
    root = topo._root_summary(blocks["search-leverage"])
    route_cond = topo._route_conditional_summary(
        blocks["search-leverage"], blocks["route-conditional"]
    )
    online = topo._online_summary(blocks["online-probe"])
    start = topo._threshold_summary(
        "start-state",
        blocks["start-state"],
        (0.0, 0.025, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0),
    )
    stage1 = topo._threshold_summary(
        "stage1-response",
        blocks["stage1-response"],
        (0.0, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0),
    )
    hedge = topo._hedge_summary(blocks["fixed-hedge"])

    return {
        "searchLeverage": {
            **root,
            "effectFramework": {
                "localAdaptiveMinusFixed": _effect_summary(root["localAdaptiveMinusFixed"]["rows"]),
                "globalBreadthMinusAdaptive": _effect_summary(root["globalBreadthMinusAdaptive"]["rows"]),
            },
        },
        "routeConditional": {
            **route_cond,
            "effectFramework": _effect_summary(route_cond["selectedVsAdaptive"].get("rows", [])),
        },
        "onlineProbe": {
            **online,
            "effectFramework": _effect_summary(online["holdoutVsAdaptive"].get("rows", [])),
        },
        "startState": {
            **start,
            "effectFramework": _effect_summary(start["holdoutVsAdaptive"].get("rows", [])),
        },
        "stage1Response": {
            **stage1,
            "effectFramework": _effect_summary(stage1["holdoutVsAdaptive"].get("rows", [])),
        },
        "fixedHedge": {
            **hedge,
            "effectFramework": _effect_summary(hedge["holdoutVsAdaptive"].get("rows", [])),
        },
    }


def _select_grid(
    blocks: dict[tuple[str, int], dict],
    seeds: tuple[int, ...],
    values: tuple[float, ...],
    combined_field: str,
) -> tuple[float, dict[str, dict]]:
    means = {}
    details = {}
    for value in values:
        scores = []
        baseline_scores = []
        local = []
        global_ = []
        by_route = {route: [] for route in ROUTES}
        for (route, seed), block in blocks.items():
            if seed not in seeds:
                continue
            key = _key_for(block["combined"], value)
            row = block["combined"][key]
            score = float(row[combined_field])
            baseline = float(row["baselineCombinedImprovement"])
            scores.append(score)
            baseline_scores.append(baseline)
            by_route[route].append(score)
            regime_container = "multipliers" if combined_field == "combinedImprovement" and "multipliers" in block["regimes"]["local"] else "schedules"
            local_key = _key_for(block["regimes"]["local"][regime_container], value)
            global_key = _key_for(block["regimes"]["global"][regime_container], value)
            local.append(float(block["regimes"]["local"][regime_container][local_key]["normalizedImprovement"]))
            global_.append(float(block["regimes"]["global"][regime_container][global_key]["normalizedImprovement"]))
        means[value] = statistics.fmean(scores)
        details[str(value)] = {
            "meanCombinedImprovement": means[value],
            "meanDeltaVsBaseline": means[value] - statistics.fmean(baseline_scores),
            "meanLocalImprovement": statistics.fmean(local),
            "meanGlobalImprovement": statistics.fmean(global_),
            "routeMeans": {route: statistics.fmean(by_route[route]) for route in ROUTES},
        }

    best = max(means.values())
    tied = [value for value, mean in means.items() if abs(mean - best) <= EPSILON]
    selected = min(tied, key=lambda value: (abs(value - 1.0), value))
    return selected, details


def _selected_rows(
    blocks: dict[tuple[str, int], dict],
    seeds: tuple[int, ...],
    selected: float,
    regime_container: str,
) -> list[dict]:
    rows = []
    for (route, seed), block in sorted(blocks.items()):
        if seed not in seeds:
            continue
        selected_key = _key_for(block["combined"], selected)
        baseline_key = _key_for(block["combined"], 1.0)
        selected_combined = float(block["combined"][selected_key]["combinedImprovement"])
        baseline_combined = float(block["combined"][baseline_key]["combinedImprovement"])
        local_selected_key = _key_for(block["regimes"]["local"][regime_container], selected)
        local_base_key = _key_for(block["regimes"]["local"][regime_container], 1.0)
        global_selected_key = _key_for(block["regimes"]["global"][regime_container], selected)
        global_base_key = _key_for(block["regimes"]["global"][regime_container], 1.0)
        rows.append({
            "route": route,
            "seed": seed,
            "delta": selected_combined - baseline_combined,
            "localDelta": (
                float(block["regimes"]["local"][regime_container][local_selected_key]["normalizedImprovement"])
                - float(block["regimes"]["local"][regime_container][local_base_key]["normalizedImprovement"])
            ),
            "globalDelta": (
                float(block["regimes"]["global"][regime_container][global_selected_key]["normalizedImprovement"])
                - float(block["regimes"]["global"][regime_container][global_base_key]["normalizedImprovement"])
            ),
            "selected": selected_combined,
            "baseline": baseline_combined,
        })
    return rows


def _mutation_scale_summary(blocks: dict[tuple[str, int], dict]) -> dict:
    selected, grid = _select_grid(
        blocks, CALIBRATION_18, MULTIPLIERS, "combinedImprovement"
    )
    calibration_rows = _selected_rows(blocks, CALIBRATION_18, selected, "multipliers")
    holdout_rows = (
        [] if abs(selected - 1.0) <= EPSILON
        else _selected_rows(blocks, RETROSPECTIVE_HOLDOUT, selected, "multipliers")
    )
    return {
        "historical": HISTORICAL["mutationScale"],
        "geometrySelectedMultiplier": selected,
        "selectionChanged": abs(selected - HISTORICAL["mutationScale"]["selected"]) > EPSILON,
        "calibrationGrid": grid,
        "calibrationSelectedVsBaseline": _effect_summary(calibration_rows),
        "retrospectiveHoldoutUsedForInterpretation": abs(selected - 1.0) > EPSILON,
        "retrospectiveHoldoutSelectedVsBaseline": _effect_summary(holdout_rows),
        "note": "193/197/199 are no longer fresh because #63 later opened them; any #62 holdout here is retrospective diagnostic evidence only",
    }


def _mutation_schedule_summary(blocks: dict[tuple[str, int], dict]) -> dict:
    selected, grid = _select_grid(
        blocks, CALIBRATION_18, CONTRASTS, "combinedImprovement"
    )
    calibration_rows = _selected_rows(blocks, CALIBRATION_18, selected, "schedules")
    holdout_rows = _selected_rows(blocks, RETROSPECTIVE_HOLDOUT, selected, "schedules")
    return {
        "historical": HISTORICAL["mutationSchedule"],
        "geometrySelectedContrast": selected,
        "selectionChanged": abs(selected - HISTORICAL["mutationSchedule"]["selected"]) > EPSILON,
        "calibrationGrid": grid,
        "calibrationSelectedVsBaseline": _effect_summary(calibration_rows),
        "holdoutSelectedVsBaseline": _effect_summary(holdout_rows),
        "note": "holdout is consumed historical evidence; continuous effect framework replaces the retired route-vote gate for reinterpretation",
    }


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    topology = _topology_summary(blocks)
    scale = _mutation_scale_summary(blocks["mutation-scale"])
    schedule = _mutation_schedule_summary(blocks["mutation-schedule"])

    return {
        "version": 1,
        "metric": "sparse-geometry-v1",
        "metricQualification": "#69 preregistered out-of-design holdout pass",
        "freshSearchSeedsConsumed": False,
        "historicalArc": "#56-#63",
        "topology": topology,
        "mutationScale": scale,
        "mutationSchedule": schedule,
        "classificationRule": {
            "SURVIVES": "same practical research conclusion under corrected metric without contradictory robust continuous mechanism",
            "REVERSES": "corrected metric yields a materially different coherent mechanism that makes the historical conclusion indefensible even diagnostically",
            "UNRESOLVED / HETEROGENEOUS": "choice/effects conflict, are fragile to seed/route influence, or are too unstable for either conclusion",
        },
        "classification": "intentionally not automated; reducer exposes preregistered evidence without inventing a new numeric gate after results",
        "boundary": "consumed-seed methodological reinterpretation only; no fresh confirmation, artistic authority, representation pruning, production/default change, or benchmark adoption",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
