#!/usr/bin/env python3
"""Apply the preregistered untouched-holdout gate for online topology probe v1."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE_PATH = HERE / "probe.py"
CALIBRATION_PATH = HERE / "calibration.json"
spec = importlib.util.spec_from_file_location("online_probe", PROBE_PATH)
probe = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(probe)


def _selected_pilot_size() -> int:
    doc = json.loads(CALIBRATION_PATH.read_text())
    if not doc.get("complete"):
        raise AssertionError("calibration is not frozen complete")
    if tuple(doc.get("holdoutSeedsReserved", ())) != tuple(probe.HOLDOUT_SEEDS):
        raise AssertionError("reserved holdout seeds drifted from calibration record")
    selected = int(doc["selectedPilotSize"])
    if selected not in probe.PILOT_SIZES:
        raise AssertionError("frozen selected pilot size is outside preregistered grid")
    return selected


def _load(results_dir: Path, selected_p: int) -> dict[tuple[str, int], dict]:
    blocks: dict[tuple[str, int], dict] = {}
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        route, seed = doc.get("route"), doc.get("seed")
        if route not in probe.ROUTE_ORDER or seed not in probe.HOLDOUT_SEEDS:
            continue
        key = (str(route), int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate holdout block {key}")
        if tuple(doc.get("pilotSizes", ())) != (selected_p,):
            raise AssertionError(f"pilot-size drift for {route}/{seed}: {doc.get('pilotSizes')}")
        if tuple(doc.get("times", ())) != tuple(probe.v1.TIMES):
            raise AssertionError(f"time drift for {route}/{seed}")
        blocks[key] = doc

    expected = {
        (route, seed)
        for route in probe.ROUTE_ORDER
        for seed in probe.HOLDOUT_SEEDS
    }
    if set(blocks) != expected:
        raise AssertionError(
            f"holdout block mismatch missing={sorted(expected-set(blocks))} extra={sorted(set(blocks)-expected)}"
        )
    return blocks


def aggregate(results_dir: Path) -> dict:
    selected_p = _selected_pilot_size()
    blocks = _load(results_dir, selected_p)

    route_rows = {}
    raw_nonworse = 0
    raw_strict = 0
    probe_scores = []
    adaptive_scores = []
    breadth_scores = []
    fixed_scores = []
    best_three_scores = []
    simple_oracle_scores = []
    local_probe = []
    local_adaptive = []
    global_probe = []
    global_adaptive = []
    arm_correct = []
    arm_choices = Counter()
    simple_oracle_regret = []
    best_three_regret = []

    for route in probe.ROUTE_ORDER:
        route_nonworse = 0
        route_strict = 0
        seed_rows = []
        for seed in probe.HOLDOUT_SEEDS:
            block = blocks[(route, seed)]
            combined = block["combinedNormalizedImprovement"]
            adaptive = float(combined["adaptive"])
            breadth = float(combined["breadth"])
            fixed = float(combined["fixed"])
            probe_score = float(combined["probes"][str(selected_p)])
            nonworse = probe_score + probe.EPSILON >= adaptive
            strict = probe_score > adaptive + probe.EPSILON
            route_nonworse += int(nonworse)
            route_strict += int(strict)
            raw_nonworse += int(nonworse)
            raw_strict += int(strict)

            probe_scores.append(probe_score)
            adaptive_scores.append(adaptive)
            breadth_scores.append(breadth)
            fixed_scores.append(fixed)
            simple_oracle_scores.append(max(breadth, fixed))
            best_three_scores.append(max(adaptive, breadth, fixed))

            regime_rows = {}
            for regime in probe.REGIMES:
                rd = block["regimes"][regime]
                probe_metrics = rd["probes"][str(selected_p)]
                adaptive_metrics = rd["adaptive"]
                breadth_metrics = rd["breadth"]
                fixed_metrics = rd["fixed"]
                p_imp = float(probe_metrics["normalizedImprovement"])
                a_imp = float(adaptive_metrics["normalizedImprovement"])
                b_imp = float(breadth_metrics["normalizedImprovement"])
                f_imp = float(fixed_metrics["normalizedImprovement"])
                simple_imp = max(b_imp, f_imp)
                best_three_imp = max(a_imp, b_imp, f_imp)
                chosen = str(probe_metrics["chosenArm"])
                oracle_arm = str(rd["simpleOracleArm"])
                correct = chosen == oracle_arm
                arm_correct.append(correct)
                arm_choices[chosen] += 1
                simple_oracle_regret.append(simple_imp - p_imp)
                best_three_regret.append(best_three_imp - p_imp)
                if regime == "local":
                    local_probe.append(p_imp)
                    local_adaptive.append(a_imp)
                else:
                    global_probe.append(p_imp)
                    global_adaptive.append(a_imp)
                regime_rows[regime] = {
                    "probeImprovement": p_imp,
                    "adaptiveImprovement": a_imp,
                    "breadthImprovement": b_imp,
                    "fixedImprovement": f_imp,
                    "chosenArm": chosen,
                    "simpleOracleArm": oracle_arm,
                    "armChoiceCorrect": correct,
                }

            seed_rows.append({
                "seed": seed,
                "probeCombinedImprovement": probe_score,
                "adaptiveCombinedImprovement": adaptive,
                "breadthCombinedImprovement": breadth,
                "fixedCombinedImprovement": fixed,
                "nonWorseVsAdaptive": nonworse,
                "strictWinVsAdaptive": strict,
                "regimes": regime_rows,
            })

        route_support = route_nonworse >= 2
        strict_support = route_strict >= 2
        route_rows[route] = {
            "nonWorseSeeds": route_nonworse,
            "strictWinSeeds": route_strict,
            "replacementSupport": route_support,
            "strictAdvantageSupport": strict_support,
            "seeds": seed_rows,
        }

    supporting_routes = sum(int(row["replacementSupport"]) for row in route_rows.values())
    strict_routes = sum(int(row["strictAdvantageSupport"]) for row in route_rows.values())
    if supporting_routes >= 4:
        classification = "general online-simple replacement supported"
        next_step = "eligible for an opt-in research implementation experiment with real phenotype evidence"
    elif supporting_routes == 3:
        classification = "mixed / representation-dependent online leverage"
        next_step = "do not implement as a general default; investigate representation or observable-state interactions"
    else:
        classification = "general online-simple replacement not supported"
        next_step = "investigate richer observable search-state signals; do not add more stages to current adaptive topology"

    return {
        "version": 1,
        "complete": True,
        "selectedPilotSize": selected_p,
        "holdoutSeeds": list(probe.HOLDOUT_SEEDS),
        "blocks": len(blocks),
        "primaryGate": "route supports when probe is non-worse than adaptive on >=2/3 seeds; general support requires >=4/5 routes",
        "routes": route_rows,
        "supportingRoutes": supporting_routes,
        "strictAdvantageRoutes": strict_routes,
        "rawNonWorseBlocks": raw_nonworse,
        "rawStrictWinBlocks": raw_strict,
        "classification": classification,
        "nextStep": next_step,
        "means": {
            "probeCombinedImprovement": statistics.fmean(probe_scores),
            "adaptiveCombinedImprovement": statistics.fmean(adaptive_scores),
            "breadthCombinedImprovement": statistics.fmean(breadth_scores),
            "fixedCombinedImprovement": statistics.fmean(fixed_scores),
            "simpleOracleCombinedImprovement": statistics.fmean(simple_oracle_scores),
            "bestThreeCombinedImprovement": statistics.fmean(best_three_scores),
            "localProbeImprovement": statistics.fmean(local_probe),
            "localAdaptiveImprovement": statistics.fmean(local_adaptive),
            "globalProbeImprovement": statistics.fmean(global_probe),
            "globalAdaptiveImprovement": statistics.fmean(global_adaptive),
            "pilotArmChoiceAccuracy": statistics.fmean(arm_correct),
            "simpleOracleRegret": statistics.fmean(simple_oracle_regret),
            "bestThreeRegret": statistics.fmean(best_three_regret),
        },
        "armChoiceCounts": dict(sorted(arm_choices.items())),
        "boundary": "objective search-mechanics holdout only; no artistic promotion, representation pruning, portfolio sufficiency, or production SKILL.md authority",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
