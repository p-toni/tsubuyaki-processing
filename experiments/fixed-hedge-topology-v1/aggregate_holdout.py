#!/usr/bin/env python3
"""Apply the preregistered untouched-holdout gate for fixed hedge topology v1."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "policy.py"
CALIBRATION_PATH = HERE / "calibration.json"
spec = importlib.util.spec_from_file_location("fixed_hedge_policy", POLICY_PATH)
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
    if tuple(float(x) for x in doc.get("shareGrid", ())) != tuple(policy.HEDGE_SHARES):
        raise AssertionError("hedge share grid drifted")
    share = float(doc["selectedShare"])
    if share not in policy.HEDGE_SHARES:
        raise AssertionError("selected share outside preregistered grid")
    return doc, share


def _load(results_dir: Path, share: float) -> dict[tuple[str, int], dict]:
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
        if tuple(float(x) for x in doc.get("shares", ())) != (share,):
            raise AssertionError(f"hedge share drift for {route}/{seed}: {doc.get('shares')}")
        if tuple(doc.get("times", ())) != tuple(policy.v1.TIMES):
            raise AssertionError(f"time drift for {route}/{seed}")
        if len(doc.get("commonStartFingerprints", {})) != policy.v1.COMMON_STARTS:
            raise AssertionError(f"common-start count drift for {route}/{seed}")
        expected_prefix = policy.v1.COMMON_STARTS * (1 + policy.v1.EXPLORE_PER_BASIN)
        if len(doc.get("paidPrefixFingerprints", {})) != expected_prefix:
            raise AssertionError(f"paid-prefix count drift for {route}/{seed}")
        skey = str(share)
        for regime in policy.REGIMES:
            rd = doc["regimes"][regime]
            hedge = rd["shares"][skey]
            if int(hedge["totalCandidates"]) != int(rd["adaptive"]["totalCandidates"]):
                raise AssertionError(f"equal-budget drift for {route}/{seed}/{regime}")
        blocks[key] = doc

    expected = {(route, seed) for route in policy.ROUTE_ORDER for seed in policy.HOLDOUT_SEEDS}
    if set(blocks) != expected:
        raise AssertionError(
            f"holdout block mismatch missing={sorted(expected-set(blocks))} extra={sorted(set(blocks)-expected)}"
        )
    return blocks


def aggregate(results_dir: Path) -> dict:
    calibration, share = _calibration()
    blocks = _load(results_dir, share)
    skey = str(share)

    route_rows = {}
    hedge_scores = []
    adaptive_scores = []
    local_hedge = []
    local_adaptive = []
    global_hedge = []
    global_adaptive = []
    raw_strict = 0
    raw_nonworse = 0

    for route in policy.ROUTE_ORDER:
        strict_wins = 0
        nonworse = 0
        seeds = []
        for seed in policy.HOLDOUT_SEEDS:
            block = blocks[(route, seed)]
            combined = block["combined"][skey]
            hedge = float(combined["hedgeImprovement"])
            adaptive = float(combined["adaptiveImprovement"])
            strict = hedge > adaptive + policy.EPSILON
            nw = hedge + policy.EPSILON >= adaptive
            strict_wins += int(strict)
            nonworse += int(nw)
            raw_strict += int(strict)
            raw_nonworse += int(nw)
            hedge_scores.append(hedge)
            adaptive_scores.append(adaptive)

            regimes = {}
            for regime in policy.REGIMES:
                rd = block["regimes"][regime]
                hv = float(rd["shares"][skey]["normalizedImprovement"])
                av = float(rd["adaptive"]["normalizedImprovement"])
                if regime == "local":
                    local_hedge.append(hv)
                    local_adaptive.append(av)
                else:
                    global_hedge.append(hv)
                    global_adaptive.append(av)
                regimes[regime] = {
                    "hedgeImprovement": hv,
                    "adaptiveImprovement": av,
                    "deltaVsAdaptive": hv - av,
                    "adaptiveContinuationEvaluations": int(rd["shares"][skey]["adaptiveContinuationEvaluations"]),
                    "breadthContinuationEvaluations": int(rd["shares"][skey]["breadthContinuationEvaluations"]),
                }

            seeds.append({
                "seed": seed,
                "hedgeCombinedImprovement": hedge,
                "adaptiveCombinedImprovement": adaptive,
                "deltaVsAdaptive": hedge - adaptive,
                "strictWinVsAdaptive": strict,
                "nonWorseVsAdaptive": nw,
                "regimes": regimes,
            })

        support = strict_wins >= 2
        route_rows[route] = {
            "strictWinSeeds": strict_wins,
            "nonWorseSeeds": nonworse,
            "fixedHedgeSupport": support,
            "seeds": seeds,
        }

    supporting_routes = sum(int(row["fixedHedgeSupport"]) for row in route_rows.values())
    if supporting_routes >= 4:
        classification = "general fixed-hedge leverage supported"
        next_step = "eligible for a later opt-in runtime integration experiment; no default change yet"
    elif supporting_routes == 3:
        classification = "mixed / representation-dependent fixed-hedge leverage"
        next_step = "do not implement generally; inspect representation interactions"
    else:
        classification = "general fixed-hedge leverage not supported"
        next_step = "stop the depth-vs-breadth topology line and shift to a different search-mechanics axis"

    hedge_mean = statistics.fmean(hedge_scores)
    adaptive_mean = statistics.fmean(adaptive_scores)
    return {
        "version": 1,
        "complete": True,
        "calibrationSourceWorkflowRun": calibration.get("sourceWorkflowRun"),
        "selectedShare": share,
        "holdoutSeeds": list(policy.HOLDOUT_SEEDS),
        "blocks": len(blocks),
        "primaryGate": "strict fixed-hedge win over adaptive on >=2/3 seeds supports a route; general support requires >=4/5 routes",
        "routes": route_rows,
        "supportingRoutes": supporting_routes,
        "rawStrictWinBlocks": raw_strict,
        "rawNonWorseBlocks": raw_nonworse,
        "classification": classification,
        "nextStep": next_step,
        "means": {
            "hedgeCombinedImprovement": hedge_mean,
            "adaptiveCombinedImprovement": adaptive_mean,
            "deltaVsAdaptive": hedge_mean - adaptive_mean,
            "relativeDeltaVsAdaptive": (hedge_mean - adaptive_mean) / adaptive_mean if abs(adaptive_mean) > policy.EPSILON else None,
            "localHedgeImprovement": statistics.fmean(local_hedge),
            "localAdaptiveImprovement": statistics.fmean(local_adaptive),
            "globalHedgeImprovement": statistics.fmean(global_hedge),
            "globalAdaptiveImprovement": statistics.fmean(global_adaptive),
        },
        "boundary": "objective search-mechanics holdout only; no artistic promotion, representation pruning, portfolio sufficiency, production default change, or SKILL.md authority",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
