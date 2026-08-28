#!/usr/bin/env python3
"""Apply the preregistered untouched-holdout gate for paid stage-1 response topology v1."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "policy.py"
CALIBRATION_PATH = HERE / "calibration.json"
spec = importlib.util.spec_from_file_location("stage1_response_policy", POLICY_PATH)
policy = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(policy)


def _calibration() -> tuple[dict, float]:
    doc = json.loads(CALIBRATION_PATH.read_text())
    if not doc.get("complete"):
        raise AssertionError("calibration is not frozen complete")
    if tuple(doc.get("calibrationSeeds", ())) != tuple(policy.CALIBRATION_SEEDS):
        raise AssertionError("calibration seeds drifted")
    if tuple(doc.get("holdoutSeedsReserved", ())) != tuple(policy.HOLDOUT_SEEDS):
        raise AssertionError("reserved holdout seeds drifted")
    if tuple(float(x) for x in doc.get("thresholdGrid", ())) != tuple(policy.THRESHOLDS):
        raise AssertionError("threshold grid drifted")
    threshold = float(doc["selectedThreshold"])
    if threshold not in policy.THRESHOLDS:
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
        if route not in policy.ROUTE_ORDER or seed not in policy.HOLDOUT_SEEDS:
            continue
        key = (str(route), int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate holdout block {key}")
        if tuple(float(x) for x in doc.get("thresholds", ())) != (threshold,):
            raise AssertionError(f"threshold drift for {route}/{seed}: {doc.get('thresholds')}")
        if tuple(doc.get("times", ())) != tuple(policy.v1.TIMES):
            raise AssertionError(f"time drift for {route}/{seed}")
        if len(doc.get("commonStartFingerprints", {})) != policy.v1.COMMON_STARTS:
            raise AssertionError(f"common-start count drift for {route}/{seed}")
        expected_prefix = policy.v1.COMMON_STARTS * (1 + policy.v1.EXPLORE_PER_BASIN)
        if len(doc.get("paidPrefixFingerprints", {})) != expected_prefix:
            raise AssertionError(f"paid-prefix count drift for {route}/{seed}")
        for regime in policy.REGIMES:
            row = doc["regimes"][regime]
            if int(row["adaptive"]["totalCandidates"]) != int(row["breadthSwitch"]["totalCandidates"]):
                raise AssertionError(f"equal-budget drift for {route}/{seed}/{regime}")
        blocks[key] = doc

    expected = {
        (route, seed)
        for route in policy.ROUTE_ORDER
        for seed in policy.HOLDOUT_SEEDS
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
    selected_scores = []
    adaptive_scores = []
    breadth_scores = []
    oracle_scores = []
    choice_accuracy = []
    oracle_regret = []
    choices = Counter()
    local_choices = Counter()
    global_choices = Counter()
    local_selected = []
    local_adaptive = []
    local_breadth = []
    global_selected = []
    global_adaptive = []
    global_breadth = []
    local_prefix_gains = []
    global_prefix_gains = []

    for route in policy.ROUTE_ORDER:
        strict_wins = 0
        nonworse = 0
        seeds = []
        for seed in policy.HOLDOUT_SEEDS:
            block = blocks[(route, seed)]
            combined = block["combined"][tkey]
            selected = float(combined["selectedImprovement"])
            adaptive = float(combined["adaptiveImprovement"])
            breadth = float(combined["breadthSwitchImprovement"])
            oracle = float(combined["adaptiveVsBreadthOracleImprovement"])
            strict = selected > adaptive + policy.EPSILON
            nw = selected + policy.EPSILON >= adaptive
            strict_wins += int(strict)
            nonworse += int(nw)
            raw_strict += int(strict)
            raw_nonworse += int(nw)
            selected_scores.append(selected)
            adaptive_scores.append(adaptive)
            breadth_scores.append(breadth)
            oracle_scores.append(oracle)

            regime_rows = {}
            for regime in policy.REGIMES:
                rd = block["regimes"][regime]
                row = rd["thresholds"][tkey]
                chosen = str(row["chosenPolicy"])
                oracle_policy = str(row["oraclePolicy"])
                selected_imp = float(row["selectedImprovement"])
                adaptive_imp = float(rd["adaptive"]["normalizedImprovement"])
                breadth_imp = float(rd["breadthSwitch"]["normalizedImprovement"])
                oracle_imp = float(row["oracleImprovement"])
                prefix_gain = float(rd["prefixResponse"]["normalizedBestGain"])
                correct = chosen == oracle_policy

                choice_accuracy.append(correct)
                oracle_regret.append(oracle_imp - selected_imp)
                choices[chosen] += 1
                if regime == "local":
                    local_choices[chosen] += 1
                    local_selected.append(selected_imp)
                    local_adaptive.append(adaptive_imp)
                    local_breadth.append(breadth_imp)
                    local_prefix_gains.append(prefix_gain)
                else:
                    global_choices[chosen] += 1
                    global_selected.append(selected_imp)
                    global_adaptive.append(adaptive_imp)
                    global_breadth.append(breadth_imp)
                    global_prefix_gains.append(prefix_gain)

                regime_rows[regime] = {
                    "prefixGain": prefix_gain,
                    "chosenPolicy": chosen,
                    "oraclePolicy": oracle_policy,
                    "choiceCorrect": correct,
                    "selectedImprovement": selected_imp,
                    "adaptiveImprovement": adaptive_imp,
                    "breadthSwitchImprovement": breadth_imp,
                    "oracleImprovement": oracle_imp,
                }

            seeds.append({
                "seed": seed,
                "selectorCombinedImprovement": selected,
                "adaptiveCombinedImprovement": adaptive,
                "breadthSwitchCombinedImprovement": breadth,
                "oracleCombinedImprovement": oracle,
                "strictWinVsAdaptive": strict,
                "nonWorseVsAdaptive": nw,
                "regimes": regime_rows,
            })

        support = strict_wins >= 2
        route_rows[route] = {
            "strictWinSeeds": strict_wins,
            "nonWorseSeeds": nonworse,
            "paidResponseTopologySupport": support,
            "seeds": seeds,
        }

    supporting_routes = sum(int(row["paidResponseTopologySupport"]) for row in route_rows.values())
    if supporting_routes >= 4:
        classification = "general paid stage1 response topology leverage supported"
        next_step = "eligible for a later opt-in runtime integration experiment; no default change yet"
    elif supporting_routes == 3:
        classification = "mixed / representation-dependent paid stage1 response topology signal"
        next_step = "do not implement generally; inspect representation interactions"
    else:
        classification = "general paid stage1 response topology leverage not supported"
        next_step = "do not add more topology stages; prefer simpler fixed policies or a different search-mechanics hypothesis"

    return {
        "version": 1,
        "complete": True,
        "calibrationSourceWorkflowRun": calibration.get("sourceWorkflowRun"),
        "selectedThreshold": threshold,
        "holdoutSeeds": list(policy.HOLDOUT_SEEDS),
        "blocks": len(blocks),
        "primaryGate": "strict dynamic-policy win over adaptive on >=2/3 seeds supports a route; general support requires >=4/5 routes",
        "routes": route_rows,
        "supportingRoutes": supporting_routes,
        "rawStrictWinBlocks": raw_strict,
        "rawNonWorseBlocks": raw_nonworse,
        "classification": classification,
        "nextStep": next_step,
        "means": {
            "selectorCombinedImprovement": statistics.fmean(selected_scores),
            "adaptiveCombinedImprovement": statistics.fmean(adaptive_scores),
            "breadthSwitchCombinedImprovement": statistics.fmean(breadth_scores),
            "adaptiveVsBreadthOracleCombinedImprovement": statistics.fmean(oracle_scores),
            "regimeChoiceAccuracy": statistics.fmean(choice_accuracy),
            "regimeOracleRegret": statistics.fmean(oracle_regret),
            "localSelectorImprovement": statistics.fmean(local_selected),
            "localAdaptiveImprovement": statistics.fmean(local_adaptive),
            "localBreadthSwitchImprovement": statistics.fmean(local_breadth),
            "globalSelectorImprovement": statistics.fmean(global_selected),
            "globalAdaptiveImprovement": statistics.fmean(global_adaptive),
            "globalBreadthSwitchImprovement": statistics.fmean(global_breadth),
            "localPrefixGain": statistics.fmean(local_prefix_gains),
            "globalPrefixGain": statistics.fmean(global_prefix_gains),
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
