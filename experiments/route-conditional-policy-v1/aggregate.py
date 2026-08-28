#!/usr/bin/env python3
"""Aggregate the route-only simple-policy holdout without failing on hypothesis outcomes."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPRO_PATH = HERE / "reproduce.py"
spec = importlib.util.spec_from_file_location("route_policy_reproduce", REPRO_PATH)
repro = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(repro)

EXPECTED_MAPPING = {
    "recurrence": "fixed-parent-local",
    "orbit": "fixed-parent-local",
    "family": "independent-breadth",
    "sheet": "fixed-parent-local",
    "filament": "fixed-parent-local",
}
EXPECTED_UNIVERSAL = "fixed-parent-local"


def _load_blocks(results_dir: Path) -> dict[tuple[str, int], dict]:
    blocks: dict[tuple[str, int], dict] = {}
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        route = doc.get("route")
        seed = doc.get("seed")
        if route not in repro.ROUTE_ORDER or seed not in repro.HOLDOUT_SEEDS:
            continue
        key = (str(route), int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate holdout block for {key}: {path}")
        blocks[key] = doc

    expected = {(route, seed) for route in repro.ROUTE_ORDER for seed in repro.HOLDOUT_SEEDS}
    if set(blocks) != expected:
        raise AssertionError(
            f"block set mismatch missing={sorted(expected - set(blocks))} extra={sorted(set(blocks) - expected)}"
        )
    return blocks


def _policy(regime: dict, name: str) -> dict:
    matches = [item for item in regime["policies"] if item.get("policy") == name]
    if len(matches) != 1:
        raise AssertionError(f"expected one {name!r} policy, got {len(matches)}")
    return matches[0]


def _classification(count: int, *, supported: str, mixed: str, unsupported: str) -> str:
    if count >= 4:
        return supported
    if count == 3:
        return mixed
    return unsupported


def aggregate(results_dir: Path) -> dict:
    if repro.ROUTE_POLICY != EXPECTED_MAPPING:
        raise AssertionError(f"frozen route mapping drift: {repro.ROUTE_POLICY}")
    if repro.UNIVERSAL_SIMPLE_POLICY != EXPECTED_UNIVERSAL:
        raise AssertionError("universal simple policy drift")

    blocks = _load_blocks(results_dir)
    route_results = {}
    selected_raw_strict = 0
    selected_raw_nonworse = 0
    universal_raw_strict = 0
    universal_raw_nonworse = 0
    family_exception_strict = 0
    means = {
        "combined": {name: [] for name in ("route-selected", "adaptive", "universal-simple", "oracle-best-of-three")},
        "local": {name: [] for name in ("route-selected", "adaptive", "universal-simple")},
        "global": {name: [] for name in ("route-selected", "adaptive", "universal-simple")},
        "oracleGap": [],
    }

    for route in repro.ROUTE_ORDER:
        strict_wins = 0
        nonworse = 0
        universal_strict = 0
        universal_nonworse = 0
        seed_results = []

        for seed in repro.HOLDOUT_SEEDS:
            block = blocks[(route, seed)]
            if tuple(block.get("times", ())) != tuple(repro.v1.TIMES):
                raise AssertionError(f"time horizon drift for {route}/{seed}")
            if block.get("routeSelectedPolicy") != EXPECTED_MAPPING[route]:
                raise AssertionError(f"route-selected policy drift for {route}/{seed}")
            if block.get("universalSimplePolicy") != EXPECTED_UNIVERSAL:
                raise AssertionError(f"universal policy drift for {route}/{seed}")
            regimes = block.get("regimes") or {}
            if set(regimes) != set(repro.REGIMES):
                raise AssertionError(f"regime set drift for {route}/{seed}")

            combined = block.get("combined") or {}
            scores = combined.get("normalizedImprovement") or {}
            if set(scores) != set(repro.POLICIES):
                raise AssertionError(f"combined policy set drift for {route}/{seed}")

            selected_name = EXPECTED_MAPPING[route]
            selected_score = float(scores[selected_name])
            adaptive_score = float(scores["adaptive"])
            universal_score = float(scores[EXPECTED_UNIVERSAL])
            oracle_score = max(float(value) for value in scores.values())

            selected_strict = selected_score > adaptive_score + repro.EPSILON
            selected_nonworse = selected_score + repro.EPSILON >= adaptive_score
            fixed_strict = universal_score > adaptive_score + repro.EPSILON
            fixed_nonworse = universal_score + repro.EPSILON >= adaptive_score

            if selected_strict != bool(combined.get("routeSelectedStrictlyBeatsAdaptive")):
                raise AssertionError(f"selected strict flag drift for {route}/{seed}")
            if selected_nonworse != bool(combined.get("routeSelectedNonWorseThanAdaptive")):
                raise AssertionError(f"selected non-worse flag drift for {route}/{seed}")
            if abs(float(combined.get("oracleBestOfThreeScore")) - oracle_score) > repro.EPSILON:
                raise AssertionError(f"oracle score drift for {route}/{seed}")

            strict_wins += int(selected_strict)
            nonworse += int(selected_nonworse)
            universal_strict += int(fixed_strict)
            universal_nonworse += int(fixed_nonworse)
            selected_raw_strict += int(selected_strict)
            selected_raw_nonworse += int(selected_nonworse)
            universal_raw_strict += int(fixed_strict)
            universal_raw_nonworse += int(fixed_nonworse)

            family_exception = False
            if route == "family":
                family_exception = selected_score > universal_score + repro.EPSILON
                family_exception_strict += int(family_exception)

            means["combined"]["route-selected"].append(selected_score)
            means["combined"]["adaptive"].append(adaptive_score)
            means["combined"]["universal-simple"].append(universal_score)
            means["combined"]["oracle-best-of-three"].append(oracle_score)
            means["oracleGap"].append(oracle_score - selected_score)

            for regime_name in repro.REGIMES:
                regime = regimes[regime_name]
                selected_item = _policy(regime, selected_name)
                adaptive_item = _policy(regime, "adaptive")
                universal_item = _policy(regime, EXPECTED_UNIVERSAL)
                means[regime_name]["route-selected"].append(float(selected_item["normalizedImprovement"]))
                means[regime_name]["adaptive"].append(float(adaptive_item["normalizedImprovement"]))
                means[regime_name]["universal-simple"].append(float(universal_item["normalizedImprovement"]))

            seed_results.append({
                "seed": seed,
                "selectedPolicy": selected_name,
                "selectedCombinedScore": selected_score,
                "adaptiveCombinedScore": adaptive_score,
                "universalSimpleCombinedScore": universal_score,
                "selectedStrictlyBeatsAdaptive": selected_strict,
                "selectedNonWorseThanAdaptive": selected_nonworse,
                "universalStrictlyBeatsAdaptive": fixed_strict,
                "universalNonWorseThanAdaptive": fixed_nonworse,
                "familyBreadthStrictlyBeatsFixed": family_exception if route == "family" else None,
                "oracleGapFromSelected": oracle_score - selected_score,
            })

        route_results[route] = {
            "selectedPolicy": EXPECTED_MAPPING[route],
            "selectedStrictWins": strict_wins,
            "selectedNonWorse": nonworse,
            "supportsSimpleReplacement": nonworse >= 2,
            "supportsStrictSimpleAdvantage": strict_wins >= 2,
            "universalStrictWins": universal_strict,
            "universalNonWorse": universal_nonworse,
            "supportsUniversalSimpleReplacement": universal_nonworse >= 2,
            "seeds": seed_results,
        }

    selected_support_routes = sum(item["supportsSimpleReplacement"] for item in route_results.values())
    selected_strict_routes = sum(item["supportsStrictSimpleAdvantage"] for item in route_results.values())
    universal_support_routes = sum(item["supportsUniversalSimpleReplacement"] for item in route_results.values())

    selected_class = _classification(
        selected_support_routes,
        supported="general-route-only-simple-replacement-supported",
        mixed="mixed-representation-dependent-simple-replacement",
        unsupported="general-route-only-simple-replacement-not-supported",
    )
    strict_class = _classification(
        selected_strict_routes,
        supported="general-strict-simple-performance-advantage-supported",
        mixed="mixed-strict-simple-performance-advantage",
        unsupported="general-strict-simple-performance-advantage-not-supported",
    )
    universal_class = _classification(
        universal_support_routes,
        supported="general-universal-fixed-parent-replacement-supported",
        mixed="mixed-universal-fixed-parent-replacement",
        unsupported="general-universal-fixed-parent-replacement-not-supported",
    )
    family_exception_supported = family_exception_strict >= 2

    if selected_support_routes >= 4 and family_exception_supported:
        decision = "route-conditional-simple-policy-supported"
    elif universal_support_routes >= 4 and not family_exception_supported:
        decision = "universal-fixed-parent-simplification-supported"
    elif selected_support_routes >= 4:
        decision = "simple-simplification-supported-route-rule-needs-revision"
    else:
        decision = "simple-route-policy-simplification-not-supported"

    summary_means = {
        group: {name: statistics.fmean(values) for name, values in group_values.items()}
        for group, group_values in means.items()
        if group != "oracleGap"
    }
    summary_means["oracleGap"] = statistics.fmean(means["oracleGap"])

    return {
        "version": 1,
        "complete": True,
        "blocks": len(blocks),
        "trainSeeds": [101, 103, 107],
        "holdoutSeeds": list(repro.HOLDOUT_SEEDS),
        "frozenRoutePolicy": EXPECTED_MAPPING,
        "universalSimplePolicy": EXPECTED_UNIVERSAL,
        "decisionRule": {
            "blockScore": "mean local/global normalizedImprovement",
            "routeReplacementSupport": "selected simple non-worse than adaptive on >=2/3 fresh seeds",
            "generalReplacementSupport": ">=4/5 supporting routes",
            "familyRouteConditioningSupport": "family breadth strictly beats fixed-parent on >=2/3 fresh seeds",
            "nonWorseTieRule": "exact numerical ties count as non-worse; any loss > epsilon fails",
        },
        "routeResults": route_results,
        "primary": {
            "selectedSupportingRoutes": selected_support_routes,
            "selectedStrictAdvantageRoutes": selected_strict_routes,
            "selectedRawStrictWins": selected_raw_strict,
            "selectedRawNonWorse": selected_raw_nonworse,
            "selectedClassification": selected_class,
            "strictClassification": strict_class,
            "universalSupportingRoutes": universal_support_routes,
            "universalRawStrictWins": universal_raw_strict,
            "universalRawNonWorse": universal_raw_nonworse,
            "universalClassification": universal_class,
            "familyBreadthStrictWinsOverFixed": family_exception_strict,
            "familyRouteConditioningSupported": family_exception_supported,
            "decision": decision,
        },
        "secondaryMeans": summary_means,
        "boundary": "objective fresh-seed search-mechanics evidence only; no artistic-quality claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
