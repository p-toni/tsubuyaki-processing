#!/usr/bin/env python3
"""Fresh-seed holdout for a frozen route-only simple search-policy mapping."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1_PATH = ROOT / "experiments" / "search-leverage-v1" / "reproduce.py"
MAPPING_PATH = HERE / "training-mapping.json"

spec = importlib.util.spec_from_file_location("search_leverage_v1", V1_PATH)
v1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(v1)

ROUTE_ORDER = tuple(v1.ROUTE_ORDER)
HOLDOUT_SEEDS = (109, 113, 127)
REGIMES = ("local", "global")
SIMPLE_POLICIES = ("independent-breadth", "fixed-parent-local")
POLICIES = ("adaptive",) + SIMPLE_POLICIES
EPSILON = v1.EPSILON


def _load_mapping() -> tuple[dict[str, str], str]:
    doc = json.loads(MAPPING_PATH.read_text())
    if tuple(doc.get("trainSeeds", ())) != (101, 103, 107):
        raise AssertionError("training seed drift")
    routes = doc.get("routes") or {}
    if set(routes) != set(ROUTE_ORDER):
        raise AssertionError("route mapping set drift")
    mapping = {route: str(routes[route]["selectedPolicy"]) for route in ROUTE_ORDER}
    if any(policy not in SIMPLE_POLICIES for policy in mapping.values()):
        raise AssertionError("route mapping contains a non-simple policy")
    universal = str(doc.get("universalSimplePolicy"))
    if universal not in SIMPLE_POLICIES:
        raise AssertionError("invalid universal simple policy")
    return mapping, universal


ROUTE_POLICY, UNIVERSAL_SIMPLE_POLICY = _load_mapping()


def _policy(regime: dict, name: str) -> dict:
    matches = [item for item in regime["policies"] if item.get("policy") == name]
    if len(matches) != 1:
        raise AssertionError(f"expected one {name!r} policy, got {len(matches)}")
    return matches[0]


def _combined_score(regimes: dict, policy_name: str) -> float:
    return statistics.fmean(
        float(_policy(regimes[regime], policy_name)["normalizedImprovement"])
        for regime in REGIMES
    )


def run_block(route: str, seed: int) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} is not predeclared")
    if seed not in HOLDOUT_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")

    brief = v1._brief(route)
    starts = v1._generate_common_starts(brief, seed, route)
    targets = {
        "local": v1._local_target(brief, seed, route, starts[0]),
        "global": v1._global_target(brief, seed, route),
    }

    regimes = {}
    for kind, target in targets.items():
        adaptive, budget = v1._run_adaptive(brief, seed, starts, target)
        breadth = v1._run_independent_breadth(brief, seed, route, starts, target, budget)
        fixed = v1._run_fixed_parent(brief, seed, route, kind, starts, target, budget)
        policies = [adaptive, breadth, fixed]
        if any(item["totalCandidates"] != len(starts) + budget for item in policies):
            raise AssertionError("equal candidate-evaluation budget invariant failed")

        selected_name = ROUTE_POLICY[route]
        selected = next(item for item in policies if item["policy"] == selected_name)
        regimes[kind] = {
            "target": v1._target_record(target, starts),
            "incrementalEvaluationBudget": budget,
            "policies": policies,
            "winnerPolicies": v1._winner_labels(policies),
            "routeSelectedPolicy": selected_name,
            "routeSelectedBestDistance": selected["bestDistance"],
            "routeSelectedBeatsAdaptive": selected["bestDistance"] + EPSILON < adaptive["bestDistance"],
            "routeSelectedNonWorseThanAdaptive": selected["bestDistance"] <= adaptive["bestDistance"] + EPSILON,
        }

    combined = {policy: _combined_score(regimes, policy) for policy in POLICIES}
    selected_name = ROUTE_POLICY[route]
    selected_score = combined[selected_name]
    adaptive_score = combined["adaptive"]
    universal_score = combined[UNIVERSAL_SIMPLE_POLICY]
    oracle_score = max(combined.values())

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "times": list(v1.TIMES),
        "routeSelectedPolicy": selected_name,
        "universalSimplePolicy": UNIVERSAL_SIMPLE_POLICY,
        "commonStartFingerprints": {c.id: v1.phenotype_fingerprint(c) for c in starts},
        "settings": {
            "commonStarts": v1.COMMON_STARTS,
            "localTargetAcceptedSteps": v1.LOCAL_TARGET_ACCEPTED_STEPS,
            "localTargetScale": v1.LOCAL_TARGET_SCALE,
            "explorePerBasin": v1.EXPLORE_PER_BASIN,
            "roundAPerSurvivor": v1.ROUND_A_PER_SURVIVOR,
            "totalExtraBudget": v1.TOTAL_EXTRA_BUDGET,
        },
        "regimes": regimes,
        "combined": {
            "normalizedImprovement": combined,
            "routeSelectedScore": selected_score,
            "adaptiveScore": adaptive_score,
            "universalSimpleScore": universal_score,
            "oracleBestOfThreeScore": oracle_score,
            "routeSelectedStrictlyBeatsAdaptive": selected_score > adaptive_score + EPSILON,
            "routeSelectedNonWorseThanAdaptive": selected_score + EPSILON >= adaptive_score,
            "routeSelectedStrictlyBeatsUniversalSimple": selected_score > universal_score + EPSILON,
            "routeSelectedNonWorseThanUniversalSimple": selected_score + EPSILON >= universal_score,
            "oracleGapFromRouteSelected": oracle_score - selected_score,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=HOLDOUT_SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2))


if __name__ == "__main__":
    main()
