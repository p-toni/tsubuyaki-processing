#!/usr/bin/env python3
"""Aggregate the six historical topology experiments under sparse-shape-v1."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
REGIMES = ("local", "global")
EPSILON = 1e-12

SEEDS = {
    "search-leverage": ((101, 103, 107), ()),
    "route-conditional": ((101, 103, 107), (109, 113, 127)),
    "online-probe": ((101, 103, 107, 109, 113, 127), (131, 137, 139)),
    "start-state": ((101, 103, 107, 109, 113, 127, 131, 137, 139), (149, 151, 157)),
    "stage1-response": ((101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157), (163, 167, 173)),
    "fixed-hedge": ((101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173), (179, 181, 191)),
}

EXPECTED_RUN_SEEDS = {
    "search-leverage": SEEDS["search-leverage"][0],
    "route-conditional": SEEDS["route-conditional"][1],
    "online-probe": SEEDS["online-probe"][0] + SEEDS["online-probe"][1],
    "start-state": SEEDS["start-state"][0] + SEEDS["start-state"][1],
    "stage1-response": SEEDS["stage1-response"][0] + SEEDS["stage1-response"][1],
    "fixed-hedge": SEEDS["fixed-hedge"][0] + SEEDS["fixed-hedge"][1],
}

HISTORICAL = {
    "route-conditional": {
        "selected": {
            "recurrence": "fixed-parent-local",
            "orbit": "fixed-parent-local",
            "family": "independent-breadth",
            "sheet": "fixed-parent-local",
            "filament": "fixed-parent-local",
        },
        "universalSimple": "fixed-parent-local",
        "holdoutMeanDeltaVsAdaptive": 0.06489416147236944 - 0.0769023132386739,
    },
    "online-probe": {
        "selected": 4,
        "holdoutMeanDeltaVsAdaptive": 0.07303751855754112 - 0.08975346812953156,
    },
    "start-state": {
        "selected": 0.5,
        "holdoutMeanDeltaVsAdaptive": 0.06917016392081915 - 0.06393698452949619,
    },
    "stage1-response": {
        "selected": 0.025,
        "holdoutMeanDeltaVsAdaptive": 0.08459048123383908 - 0.09281059828134507,
    },
    "fixed-hedge": {
        "selected": 0.5,
        "holdoutMeanDeltaVsAdaptive": 0.007438865838951411,
    },
}


def _load(results_dir: Path) -> dict[str, dict[tuple[str, int], dict]]:
    blocks: dict[str, dict[tuple[str, int], dict]] = {name: {} for name in EXPECTED_RUN_SEEDS}
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        meta = doc.get("structuralReplay") if isinstance(doc, dict) else None
        if not isinstance(meta, dict):
            continue
        experiment = meta.get("experiment")
        if experiment not in blocks or meta.get("metric") != "sparse-shape-v1":
            continue
        route = str(doc.get("route"))
        seed = int(doc.get("seed"))
        key = (route, seed)
        if key in blocks[experiment]:
            raise AssertionError(f"duplicate {experiment} block {key}")
        blocks[experiment][key] = doc

    for experiment, seeds in EXPECTED_RUN_SEEDS.items():
        expected = {(route, seed) for route in ROUTES for seed in seeds}
        actual = set(blocks[experiment])
        if actual != expected:
            raise AssertionError(
                f"{experiment} block mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
            )
    return blocks


def _policy(regime: dict, name: str) -> dict:
    rows = [row for row in regime["policies"] if row.get("policy") == name]
    if len(rows) != 1:
        raise AssertionError(f"expected one policy {name!r}, got {len(rows)}")
    return rows[0]


def _simple_combined(block: dict, name: str) -> float:
    return statistics.fmean(float(_policy(block["regimes"][kind], name)["normalizedImprovement"]) for kind in REGIMES)


def _sign(value: float) -> str:
    if value > EPSILON:
        return "positive"
    if value < -EPSILON:
        return "negative"
    return "zero"


def _paired_summary(rows: list[dict]) -> dict:
    if not rows:
        return {"blocks": 0}
    deltas = [float(row["delta"]) for row in rows]
    local = [float(row["localDelta"]) for row in rows if row.get("localDelta") is not None]
    global_ = [float(row["globalDelta"]) for row in rows if row.get("globalDelta") is not None]
    return {
        "blocks": len(rows),
        "meanDelta": statistics.fmean(deltas),
        "medianDelta": statistics.median(deltas),
        "meanSign": _sign(statistics.fmean(deltas)),
        "strictWins": sum(delta > EPSILON for delta in deltas),
        "nonWorse": sum(delta >= -EPSILON for delta in deltas),
        "routeMeanDelta": {
            route: statistics.fmean(float(row["delta"]) for row in rows if row["route"] == route)
            for route in ROUTES
            if any(row["route"] == route for row in rows)
        },
        "seedMeanDelta": {
            str(seed): statistics.fmean(float(row["delta"]) for row in rows if int(row["seed"]) == seed)
            for seed in sorted({int(row["seed"]) for row in rows})
        },
        "meanLocalDelta": statistics.fmean(local) if local else None,
        "meanGlobalDelta": statistics.fmean(global_) if global_ else None,
        "rows": sorted(rows, key=lambda row: (ROUTES.index(row["route"]), int(row["seed"]))),
    }


def _root_summary(blocks: dict[tuple[str, int], dict]) -> dict:
    local_rows = []
    global_rows = []
    policy_scores = {kind: {name: [] for name in ("adaptive", "independent-breadth", "fixed-parent-local")} for kind in REGIMES}
    for (route, seed), block in blocks.items():
        local = block["regimes"]["local"]
        global_ = block["regimes"]["global"]
        a_local = float(_policy(local, "adaptive")["normalizedImprovement"])
        f_local = float(_policy(local, "fixed-parent-local")["normalizedImprovement"])
        b_global = float(_policy(global_, "independent-breadth")["normalizedImprovement"])
        a_global = float(_policy(global_, "adaptive")["normalizedImprovement"])
        local_rows.append({"route": route, "seed": seed, "delta": a_local - f_local})
        global_rows.append({"route": route, "seed": seed, "delta": b_global - a_global})
        for kind in REGIMES:
            for name in policy_scores[kind]:
                policy_scores[kind][name].append(float(_policy(block["regimes"][kind], name)["normalizedImprovement"]))
    return {
        "historicalQuestion": "adaptive sequential promotion vs fixed-parent on local targets; independent breadth vs adaptive on global targets",
        "localAdaptiveMinusFixed": _paired_summary(local_rows),
        "globalBreadthMinusAdaptive": _paired_summary(global_rows),
        "meanNormalizedImprovement": {
            kind: {name: statistics.fmean(values) for name, values in policy_scores[kind].items()}
            for kind in REGIMES
        },
    }


def _derive_route_mapping(root_blocks: dict[tuple[str, int], dict]) -> dict:
    mapping = {}
    details = {}
    total = {"independent-breadth": 0, "fixed-parent-local": 0}
    for route in ROUTES:
        wins = {"independent-breadth": 0, "fixed-parent-local": 0}
        ties = 0
        seed_rows = []
        for seed in SEEDS["route-conditional"][0]:
            block = root_blocks[(route, seed)]
            breadth = _simple_combined(block, "independent-breadth")
            fixed = _simple_combined(block, "fixed-parent-local")
            if breadth > fixed + EPSILON:
                winner = "independent-breadth"
                wins[winner] += 1
                total[winner] += 1
            elif fixed > breadth + EPSILON:
                winner = "fixed-parent-local"
                wins[winner] += 1
                total[winner] += 1
            else:
                winner = "tie"
                ties += 1
            seed_rows.append({"seed": seed, "breadth": breadth, "fixed": fixed, "winner": winner})
        selected = next((name for name, count in wins.items() if count >= 2), None)
        mapping[route] = selected
        details[route] = {"wins": wins, "ties": ties, "selectedPolicy": selected, "seeds": seed_rows}
    if total["independent-breadth"] > total["fixed-parent-local"]:
        universal = "independent-breadth"
    elif total["fixed-parent-local"] > total["independent-breadth"]:
        universal = "fixed-parent-local"
    else:
        universal = None
    return {"mapping": mapping, "routes": details, "universalSimplePolicy": universal, "totalStrictWins": total}


def _route_conditional_summary(root_blocks, holdout_blocks) -> dict:
    training = _derive_route_mapping(root_blocks)
    mapping = training["mapping"]
    mapping_complete = all(mapping[route] is not None for route in ROUTES)
    selected_rows = []
    universal_rows = []
    family_rows = []
    for (route, seed), block in holdout_blocks.items():
        adaptive_local = float(_policy(block["regimes"]["local"], "adaptive")["normalizedImprovement"])
        adaptive_global = float(_policy(block["regimes"]["global"], "adaptive")["normalizedImprovement"])
        adaptive = (adaptive_local + adaptive_global) / 2
        selected_name = mapping[route]
        if selected_name is not None:
            selected_local = float(_policy(block["regimes"]["local"], selected_name)["normalizedImprovement"])
            selected_global = float(_policy(block["regimes"]["global"], selected_name)["normalizedImprovement"])
            selected_rows.append({
                "route": route, "seed": seed,
                "delta": (selected_local + selected_global) / 2 - adaptive,
                "localDelta": selected_local - adaptive_local,
                "globalDelta": selected_global - adaptive_global,
                "selectedPolicy": selected_name,
            })
        universal_name = training["universalSimplePolicy"]
        if universal_name is not None:
            u_local = float(_policy(block["regimes"]["local"], universal_name)["normalizedImprovement"])
            u_global = float(_policy(block["regimes"]["global"], universal_name)["normalizedImprovement"])
            universal_rows.append({"route": route, "seed": seed, "delta": (u_local+u_global)/2-adaptive, "localDelta": u_local-adaptive_local, "globalDelta": u_global-adaptive_global})
        if route == "family":
            breadth = _simple_combined(block, "independent-breadth")
            fixed = _simple_combined(block, "fixed-parent-local")
            family_rows.append({"route": route, "seed": seed, "delta": breadth-fixed})
    return {
        "training": training,
        "historicalRouteMapping": HISTORICAL["route-conditional"]["selected"],
        "mappingChanged": mapping != HISTORICAL["route-conditional"]["selected"],
        "mappingComplete": mapping_complete,
        "selectedVsAdaptive": _paired_summary(selected_rows),
        "universalSimpleVsAdaptive": _paired_summary(universal_rows),
        "familyBreadthMinusFixed": _paired_summary(family_rows),
        "historicalHoldoutMeanDeltaVsAdaptive": HISTORICAL["route-conditional"]["holdoutMeanDeltaVsAdaptive"],
        "historicalMeanSign": _sign(HISTORICAL["route-conditional"]["holdoutMeanDeltaVsAdaptive"]),
        "structuralMeanSign": _sign(statistics.fmean(row["delta"] for row in selected_rows)) if selected_rows else "unresolved",
    }


def _select_max_mean(blocks: list[dict], values: tuple, score_fn, tie: str) -> tuple[object, dict[str, float]]:
    means = {value: statistics.fmean(score_fn(block, value) for block in blocks) for value in values}
    best = max(means.values())
    tied = [value for value in values if abs(means[value] - best) <= EPSILON]
    selected = min(tied) if tie == "smaller" else max(tied)
    return selected, {str(k): v for k, v in means.items()}


def _online_summary(blocks: dict[tuple[str, int], dict]) -> dict:
    cal = [b for (r,s),b in blocks.items() if s in SEEDS["online-probe"][0]]
    selected, means = _select_max_mean(cal, (1,2,3,4), lambda b,p: float(b["combinedNormalizedImprovement"]["probes"][str(p)]), "smaller")
    rows = []
    for (route, seed), block in blocks.items():
        if seed not in SEEDS["online-probe"][1]: continue
        combined = block["combinedNormalizedImprovement"]
        delta = float(combined["probes"][str(selected)]) - float(combined["adaptive"])
        local = float(block["regimes"]["local"]["probes"][str(selected)]["normalizedImprovement"]) - float(block["regimes"]["local"]["adaptive"]["normalizedImprovement"])
        global_ = float(block["regimes"]["global"]["probes"][str(selected)]["normalizedImprovement"]) - float(block["regimes"]["global"]["adaptive"]["normalizedImprovement"])
        rows.append({"route":route,"seed":seed,"delta":delta,"localDelta":local,"globalDelta":global_})
    hist = HISTORICAL["online-probe"]
    summary = _paired_summary(rows)
    return {"selectedPilotSize":selected,"historicalSelectedPilotSize":hist["selected"],"calibrationChanged":selected!=hist["selected"],"calibrationMeans":means,"holdoutVsAdaptive":summary,"historicalHoldoutMeanDeltaVsAdaptive":hist["holdoutMeanDeltaVsAdaptive"],"historicalMeanSign":_sign(hist["holdoutMeanDeltaVsAdaptive"]),"structuralMeanSign":summary["meanSign"]}


def _threshold_summary(name: str, blocks: dict[tuple[str,int],dict], thresholds: tuple[float,...]) -> dict:
    cal_seeds, holdout_seeds = SEEDS[name]
    cal = [b for (r,s),b in blocks.items() if s in cal_seeds]
    selected, means = _select_max_mean(cal, thresholds, lambda b,t: float(b["combined"][str(t)]["selectedImprovement"]), "smaller")
    rows=[]
    for (route,seed),block in blocks.items():
        if seed not in holdout_seeds: continue
        row=block["combined"][str(selected)]
        selected_imp=float(row["selectedImprovement"]); adaptive=float(row["adaptiveImprovement"])
        local_row=block["regimes"]["local"]["thresholds"][str(selected)]
        global_row=block["regimes"]["global"]["thresholds"][str(selected)]
        local_delta=float(local_row["selectedImprovement"])-float(block["regimes"]["local"]["adaptive"]["normalizedImprovement"])
        global_delta=float(global_row["selectedImprovement"])-float(block["regimes"]["global"]["adaptive"]["normalizedImprovement"])
        rows.append({"route":route,"seed":seed,"delta":selected_imp-adaptive,"localDelta":local_delta,"globalDelta":global_delta,"chosenLocal":local_row["chosenPolicy"],"chosenGlobal":global_row["chosenPolicy"]})
    hist=HISTORICAL[name]; summary=_paired_summary(rows)
    return {"selected":selected,"historicalSelected":hist["selected"],"calibrationChanged":selected!=hist["selected"],"calibrationMeans":means,"holdoutVsAdaptive":summary,"historicalHoldoutMeanDeltaVsAdaptive":hist["holdoutMeanDeltaVsAdaptive"],"historicalMeanSign":_sign(hist["holdoutMeanDeltaVsAdaptive"]),"structuralMeanSign":summary["meanSign"]}


def _hedge_summary(blocks: dict[tuple[str,int],dict]) -> dict:
    cal = [b for (r,s),b in blocks.items() if s in SEEDS["fixed-hedge"][0]]
    shares=(0.0,0.25,0.5,0.75,1.0)
    selected, means = _select_max_mean(cal, shares, lambda b,s: float(b["combined"][str(s)]["hedgeImprovement"]), "larger")
    rows=[]
    for (route,seed),block in blocks.items():
        if seed not in SEEDS["fixed-hedge"][1]: continue
        combined=block["combined"][str(selected)]
        local=block["regimes"]["local"]
        global_=block["regimes"]["global"]
        rows.append({
            "route":route,"seed":seed,
            "delta":float(combined["hedgeImprovement"])-float(combined["adaptiveImprovement"]),
            "localDelta":float(local["shares"][str(selected)]["normalizedImprovement"])-float(local["adaptive"]["normalizedImprovement"]),
            "globalDelta":float(global_["shares"][str(selected)]["normalizedImprovement"])-float(global_["adaptive"]["normalizedImprovement"]),
        })
    hist=HISTORICAL["fixed-hedge"]; summary=_paired_summary(rows)
    return {"selectedShare":selected,"historicalSelectedShare":hist["selected"],"calibrationChanged":selected!=hist["selected"],"calibrationMeans":means,"holdoutVsAdaptive":summary,"historicalHoldoutMeanDeltaVsAdaptive":hist["holdoutMeanDeltaVsAdaptive"],"historicalMeanSign":_sign(hist["holdoutMeanDeltaVsAdaptive"]),"structuralMeanSign":summary["meanSign"]}


def aggregate(results_dir: Path) -> dict:
    blocks=_load(results_dir)
    result={
        "version":1,
        "metric":"sparse-shape-v1",
        "freshSeedsConsumed":False,
        "historicalGateReusedForInference":False,
        "searchLeverage":_root_summary(blocks["search-leverage"]),
        "routeConditional":_route_conditional_summary(blocks["search-leverage"],blocks["route-conditional"]),
        "onlineProbe":_online_summary(blocks["online-probe"]),
        "startState":_threshold_summary("start-state",blocks["start-state"],(0.0,0.025,0.05,0.1,0.15,0.2,0.3,0.5,0.75,1.0)),
        "stage1Response":_threshold_summary("stage1-response",blocks["stage1-response"],(0.0,0.01,0.025,0.05,0.075,0.1,0.15,0.2,0.3,0.5,1.0)),
        "fixedHedge":_hedge_summary(blocks["fixed-hedge"]),
        "boundary":"consumed-seed diagnostic remeasurement; no fresh confirmation, artistic authority, representation pruning, production/default change, or benchmark adoption",
    }
    result["comparison"]={
        "calibrationChoicesChanged": {
            "routeConditional": result["routeConditional"]["mappingChanged"],
            "onlineProbe": result["onlineProbe"]["calibrationChanged"],
            "startState": result["startState"]["calibrationChanged"],
            "stage1Response": result["stage1Response"]["calibrationChanged"],
            "fixedHedge": result["fixedHedge"]["calibrationChanged"],
        },
        "holdoutMeanSignChanged": {
            name: result[key]["historicalMeanSign"] != result[key]["structuralMeanSign"]
            for name,key in (
                ("routeConditional","routeConditional"),
                ("onlineProbe","onlineProbe"),
                ("startState","startState"),
                ("stage1Response","stage1Response"),
                ("fixedHedge","fixedHedge"),
            )
        },
    }
    return result


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--results-dir",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(aggregate(args.results_dir),indent=2))


if __name__=="__main__":
    main()
