#!/usr/bin/env python3
"""Aggregate objective search-leverage blocks without turning hypothesis outcomes into CI failures."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPRO_PATH = HERE / "reproduce.py"
spec = importlib.util.spec_from_file_location("search_leverage_reproduce", REPRO_PATH)
repro = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(repro)

POLICIES = ("adaptive", "independent-breadth", "fixed-parent-local")
REGIMES = ("local", "global")


def _load_blocks(results_dir: Path) -> dict[tuple[str, int], dict]:
    blocks: dict[tuple[str, int], dict] = {}
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict) or doc.get("route") not in repro.ROUTE_ORDER or doc.get("seed") not in repro.SEEDS:
            continue
        key = (str(doc["route"]), int(doc["seed"]))
        if key in blocks:
            raise AssertionError(f"duplicate search-leverage block for {key}: {path}")
        blocks[key] = doc
    expected = {(route, seed) for route in repro.ROUTE_ORDER for seed in repro.SEEDS}
    missing = expected - set(blocks)
    extra = set(blocks) - expected
    if missing or extra:
        raise AssertionError(f"block set mismatch missing={sorted(missing)} extra={sorted(extra)}")
    return blocks


def _policy(regime: dict, name: str) -> dict:
    matches = [item for item in regime["policies"] if item.get("policy") == name]
    if len(matches) != 1:
        raise AssertionError(f"expected one {name!r} policy, got {len(matches)}")
    return matches[0]


def _strict_lt(a: float, b: float) -> bool:
    return a + repro.EPSILON < b


def _classification(supporting_routes: int, *, positive: str, mixed: str, negative: str) -> str:
    if supporting_routes >= 4:
        return positive
    if supporting_routes == 3:
        return mixed
    return negative


def aggregate(results_dir: Path) -> dict:
    blocks = _load_blocks(results_dir)
    route_results = {}
    local_raw_wins = 0
    global_raw_wins = 0
    secondary = {
        regime: {policy: {"normalizedImprovement": [], "validYield": [], "uniquePhenotypeRate": []} for policy in POLICIES}
        for regime in REGIMES
    }
    adaptive_depths = {regime: [] for regime in REGIMES}

    for route in repro.ROUTE_ORDER:
        local_wins = 0
        global_wins = 0
        seed_results = []
        for seed in repro.SEEDS:
            block = blocks[(route, seed)]
            if tuple(block.get("times", ())) != tuple(repro.TIMES):
                raise AssertionError(f"time horizon drift for {route}/{seed}")
            regimes = block.get("regimes") or {}
            if set(regimes) != set(REGIMES):
                raise AssertionError(f"regime set drift for {route}/{seed}: {sorted(regimes)}")

            local = regimes["local"]
            global_regime = regimes["global"]
            local_adaptive = _policy(local, "adaptive")
            local_fixed = _policy(local, "fixed-parent-local")
            global_adaptive = _policy(global_regime, "adaptive")
            global_breadth = _policy(global_regime, "independent-breadth")

            local_win = _strict_lt(local_adaptive["bestDistance"], local_fixed["bestDistance"])
            global_win = _strict_lt(global_breadth["bestDistance"], global_adaptive["bestDistance"])
            if local_win != bool(local.get("adaptiveBeatsFixedParent")):
                raise AssertionError(f"local comparison flag drift for {route}/{seed}")
            if global_win != bool(global_regime.get("breadthBeatsAdaptive")):
                raise AssertionError(f"global comparison flag drift for {route}/{seed}")

            local_wins += int(local_win)
            global_wins += int(global_win)
            local_raw_wins += int(local_win)
            global_raw_wins += int(global_win)

            for regime_name, regime in regimes.items():
                for policy_name in POLICIES:
                    item = _policy(regime, policy_name)
                    for metric in ("normalizedImprovement", "validYield", "uniquePhenotypeRate"):
                        secondary[regime_name][policy_name][metric].append(float(item[metric]))
                adaptive_depths[regime_name].append(int(_policy(regime, "adaptive")["lineageDepth"]))

            seed_results.append({
                "seed": seed,
                "localAdaptiveBeatsFixedParent": local_win,
                "globalBreadthBeatsAdaptive": global_win,
                "localWinnerPolicies": local["winnerPolicies"],
                "globalWinnerPolicies": global_regime["winnerPolicies"],
            })

        route_results[route] = {
            "localAdaptiveWins": local_wins,
            "localSupportsSequentialPromotion": local_wins >= 2,
            "globalBreadthWins": global_wins,
            "globalSupportsBasinDiscovery": global_wins >= 2,
            "seeds": seed_results,
        }

    local_support_routes = sum(item["localSupportsSequentialPromotion"] for item in route_results.values())
    global_support_routes = sum(item["globalSupportsBasinDiscovery"] for item in route_results.values())

    local_class = _classification(
        local_support_routes,
        positive="general-exploitation-leverage-supported",
        mixed="mixed-representation-dependent-exploitation-leverage",
        negative="general-exploitation-leverage-not-supported",
    )
    global_class = _classification(
        global_support_routes,
        positive="general-basin-discovery-requirement-supported",
        mixed="mixed-representation-dependent-basin-discovery-requirement",
        negative="general-breadth-advantage-not-supported",
    )
    if local_support_routes >= 4 and global_support_routes >= 4:
        architecture = "broad-to-deep-objectively-supported"
    elif local_support_routes >= 4:
        architecture = "selective-depth-supported-breadth-not-general"
    elif global_support_routes >= 4:
        architecture = "breadth-supported-chained-exploitation-not-general"
    else:
        architecture = "current-staged-topology-not-generally-supported"

    secondary_summary = {}
    for regime_name in REGIMES:
        secondary_summary[regime_name] = {}
        for policy_name in POLICIES:
            secondary_summary[regime_name][policy_name] = {
                metric: statistics.fmean(values)
                for metric, values in secondary[regime_name][policy_name].items()
            }
        depths = adaptive_depths[regime_name]
        secondary_summary[regime_name]["adaptiveLineageDepth"] = {
            "mean": statistics.fmean(depths),
            "min": min(depths),
            "max": max(depths),
        }

    return {
        "version": 1,
        "complete": True,
        "blocks": len(blocks),
        "decisionRule": {
            "routeSupport": "strict win in >=2/3 frozen seeds",
            "generalSupport": ">=4/5 supporting routes",
            "tiesCountAsWins": False,
        },
        "routeResults": route_results,
        "primary": {
            "localSupportingRoutes": local_support_routes,
            "localRawWins": local_raw_wins,
            "localClassification": local_class,
            "globalSupportingRoutes": global_support_routes,
            "globalRawWins": global_raw_wins,
            "globalClassification": global_class,
            "architectureClassification": architecture,
        },
        "secondary": secondary_summary,
        "boundary": "objective search-mechanics evidence only; no artistic-quality claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
