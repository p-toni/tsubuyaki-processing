#!/usr/bin/env python3
"""Apply the preregistered untouched-holdout gate for start-state topology v1."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELECTOR_PATH = HERE / "selector.py"
CALIBRATION_PATH = HERE / "calibration.json"
spec = importlib.util.spec_from_file_location("start_state_selector", SELECTOR_PATH)
selector = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(selector)


def _calibration() -> tuple[dict, float]:
    doc = json.loads(CALIBRATION_PATH.read_text())
    if not doc.get("complete"):
        raise AssertionError("calibration is not frozen complete")
    if tuple(doc.get("holdoutSeedsReserved", ())) != tuple(selector.HOLDOUT_SEEDS):
        raise AssertionError("reserved holdout seeds drifted")
    if tuple(float(x) for x in doc.get("thresholdGrid", ())) != tuple(selector.THRESHOLDS):
        raise AssertionError("threshold grid drifted")
    if int(doc.get("pilotSize")) != selector.PILOT_SIZE:
        raise AssertionError("simple-probe pilot size drifted")
    threshold = float(doc["selectedThreshold"])
    if threshold not in selector.THRESHOLDS:
        raise AssertionError("selected threshold outside preregistered grid")
    return doc, threshold


def _load(results_dir: Path, threshold: float) -> dict[tuple[str, int], dict]:
    blocks = {}
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        route, seed = doc.get("route"), doc.get("seed")
        if route not in selector.ROUTE_ORDER or seed not in selector.HOLDOUT_SEEDS:
            continue
        key = (str(route), int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate holdout block {key}")
        if tuple(float(x) for x in doc.get("thresholds", ())) != (threshold,):
            raise AssertionError(f"threshold drift for {route}/{seed}: {doc.get('thresholds')}")
        if int(doc.get("pilotSize")) != selector.PILOT_SIZE:
            raise AssertionError(f"pilot-size drift for {route}/{seed}")
        if tuple(doc.get("times", ())) != tuple(selector.v1.TIMES):
            raise AssertionError(f"time drift for {route}/{seed}")
        blocks[key] = doc

    expected = {
        (route, seed)
        for route in selector.ROUTE_ORDER
        for seed in selector.HOLDOUT_SEEDS
    }
    if set(blocks) != expected:
        raise AssertionError(
            f"holdout block mismatch missing={sorted(expected-set(blocks))} extra={sorted(set(blocks)-expected)}"
        )
    return blocks


def aggregate(results_dir: Path) -> dict:
    calibration, threshold = _calibration()
    blocks = _load(results_dir, threshold)
    tkey = str(threshold)

    route_rows = {}
    raw_strict = 0
    raw_nonworse = 0
    selector_scores = []
    adaptive_scores = []
    simple_scores = []
    oracle_scores = []
    regime_accuracy = []
    oracle_regret = []
    choices = Counter()
    local_choices = Counter()
    global_choices = Counter()
    local_selector = []
    local_adaptive = []
    global_selector = []
    global_adaptive = []
    concentrations = []
    local_concentrations = []
    global_concentrations = []
    route_concentrations = {route: [] for route in selector.ROUTE_ORDER}

    for route in selector.ROUTE_ORDER:
        strict_wins = 0
        nonworse = 0
        seeds = []
        for seed in selector.HOLDOUT_SEEDS:
            block = blocks[(route, seed)]
            combined = block["combined"][tkey]
            selected = float(combined["selectedImprovement"])
            adaptive = float(combined["adaptiveImprovement"])
            simple = float(combined["simpleProbeImprovement"])
            oracle = float(combined["adaptiveVsSimpleOracleImprovement"])
            strict = selected > adaptive + selector.EPSILON
            nw = selected + selector.EPSILON >= adaptive
            strict_wins += int(strict)
            nonworse += int(nw)
            raw_strict += int(strict)
            raw_nonworse += int(nw)
            selector_scores.append(selected)
            adaptive_scores.append(adaptive)
            simple_scores.append(simple)
            oracle_scores.append(oracle)

            regime_rows = {}
            for regime in selector.REGIMES:
                rd = block["regimes"][regime]
                row = rd["thresholds"][tkey]
                chosen = str(row["chosenPolicy"])
                oracle_policy = str(row["oraclePolicy"])
                selected_imp = float(row["selectedImprovement"])
                oracle_imp = float(row["oracleImprovement"])
                adaptive_imp = float(rd["adaptive"]["normalizedImprovement"])
                simple_imp = float(rd["simpleProbe"]["normalizedImprovement"])
                concentration = float(rd["startConcentration"])
                correct = chosen == oracle_policy

                regime_accuracy.append(correct)
                oracle_regret.append(oracle_imp - selected_imp)
                choices[chosen] += 1
                concentrations.append(concentration)
                route_concentrations[route].append(concentration)
                if regime == "local":
                    local_choices[chosen] += 1
                    local_selector.append(selected_imp)
                    local_adaptive.append(adaptive_imp)
                    local_concentrations.append(concentration)
                else:
                    global_choices[chosen] += 1
                    global_selector.append(selected_imp)
                    global_adaptive.append(adaptive_imp)
                    global_concentrations.append(concentration)

                regime_rows[regime] = {
                    "startConcentration": concentration,
                    "chosenPolicy": chosen,
                    "oraclePolicy": oracle_policy,
                    "choiceCorrect": correct,
                    "selectedImprovement": selected_imp,
                    "adaptiveImprovement": adaptive_imp,
                    "simpleProbeImprovement": simple_imp,
                    "oracleImprovement": oracle_imp,
                }

            seeds.append({
                "seed": seed,
                "selectorCombinedImprovement": selected,
                "adaptiveCombinedImprovement": adaptive,
                "simpleProbeCombinedImprovement": simple,
                "oracleCombinedImprovement": oracle,
                "strictWinVsAdaptive": strict,
                "nonWorseVsAdaptive": nw,
                "regimes": regime_rows,
            })

        support = strict_wins >= 2
        route_rows[route] = {
            "strictWinSeeds": strict_wins,
            "nonWorseSeeds": nonworse,
            "topologySignalSupport": support,
            "meanStartConcentration": statistics.fmean(route_concentrations[route]),
            "seeds": seeds,
        }

    supporting_routes = sum(int(row["topologySignalSupport"]) for row in route_rows.values())
    if supporting_routes >= 4:
        classification = "general start-state topology leverage supported"
        next_step = "eligible for a later opt-in implementation experiment with real phenotype evidence"
    elif supporting_routes == 3:
        classification = "mixed / representation-dependent start-state topology signal"
        next_step = "do not implement generally; investigate representation interactions"
    else:
        classification = "general start-state topology leverage not supported"
        next_step = "investigate richer early-search progress signals rather than adding search stages"

    return {
        "version": 1,
        "complete": True,
        "calibrationSourceWorkflowRun": calibration.get("sourceWorkflowRun"),
        "selectedThreshold": threshold,
        "pilotSize": selector.PILOT_SIZE,
        "holdoutSeeds": list(selector.HOLDOUT_SEEDS),
        "blocks": len(blocks),
        "primaryGate": "strict selector win over adaptive on >=2/3 seeds supports a route; general support requires >=4/5 routes",
        "routes": route_rows,
        "supportingRoutes": supporting_routes,
        "rawStrictWinBlocks": raw_strict,
        "rawNonWorseBlocks": raw_nonworse,
        "classification": classification,
        "nextStep": next_step,
        "means": {
            "selectorCombinedImprovement": statistics.fmean(selector_scores),
            "adaptiveCombinedImprovement": statistics.fmean(adaptive_scores),
            "simpleProbeCombinedImprovement": statistics.fmean(simple_scores),
            "adaptiveVsSimpleOracleCombinedImprovement": statistics.fmean(oracle_scores),
            "regimeChoiceAccuracy": statistics.fmean(regime_accuracy),
            "regimeOracleRegret": statistics.fmean(oracle_regret),
            "localSelectorImprovement": statistics.fmean(local_selector),
            "localAdaptiveImprovement": statistics.fmean(local_adaptive),
            "globalSelectorImprovement": statistics.fmean(global_selector),
            "globalAdaptiveImprovement": statistics.fmean(global_adaptive),
            "startConcentration": statistics.fmean(concentrations),
            "localStartConcentration": statistics.fmean(local_concentrations),
            "globalStartConcentration": statistics.fmean(global_concentrations),
        },
        "policyChoiceCounts": dict(sorted(choices.items())),
        "localPolicyChoiceCounts": dict(sorted(local_choices.items())),
        "globalPolicyChoiceCounts": dict(sorted(global_choices.items())),
        "boundary": "objective search-mechanics holdout only; no artistic promotion, representation pruning, portfolio sufficiency, production default change, or SKILL.md authority",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
