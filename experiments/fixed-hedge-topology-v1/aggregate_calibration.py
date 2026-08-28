#!/usr/bin/env python3
"""Calibrate one fixed depth/breadth hedge share on already-consumed seeds."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "policy.py"
spec = importlib.util.spec_from_file_location("fixed_hedge_policy", POLICY_PATH)
policy = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(policy)


def _load(results_dir: Path) -> dict[tuple[str, int], dict]:
    blocks = {}
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        route, seed = doc.get("route"), doc.get("seed")
        if route not in policy.ROUTE_ORDER or seed not in policy.CALIBRATION_SEEDS:
            continue
        key = (str(route), int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate calibration block {key}")
        if tuple(float(x) for x in doc.get("shares", ())) != tuple(policy.HEDGE_SHARES):
            raise AssertionError(f"hedge-share grid drift for {route}/{seed}")
        blocks[key] = doc

    expected = {(route, seed) for route in policy.ROUTE_ORDER for seed in policy.CALIBRATION_SEEDS}
    if set(blocks) != expected:
        raise AssertionError(f"calibration block mismatch missing={sorted(expected-set(blocks))} extra={sorted(set(blocks)-expected)}")
    return blocks


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    scores = {s: [] for s in policy.HEDGE_SHARES}
    strict = {s: 0 for s in policy.HEDGE_SHARES}
    nonworse = {s: 0 for s in policy.HEDGE_SHARES}
    route_scores = {route: {s: [] for s in policy.HEDGE_SHARES} for route in policy.ROUTE_ORDER}
    local_scores = {s: [] for s in policy.HEDGE_SHARES}
    global_scores = {s: [] for s in policy.HEDGE_SHARES}
    oracle_scores = []

    for (route, _seed), block in blocks.items():
        oracle_scores.append(statistics.fmean(float(block["regimes"][r]["fixedShareOracleImprovement"]) for r in policy.REGIMES))
        for share in policy.HEDGE_SHARES:
            key = str(share)
            combined = block["combined"][key]
            value = float(combined["hedgeImprovement"])
            adaptive = float(combined["adaptiveImprovement"])
            scores[share].append(value)
            route_scores[route][share].append(value)
            strict[share] += int(value > adaptive + policy.EPSILON)
            nonworse[share] += int(value + policy.EPSILON >= adaptive)
            local_scores[share].append(float(block["regimes"]["local"]["shares"][key]["normalizedImprovement"]))
            global_scores[share].append(float(block["regimes"]["global"]["shares"][key]["normalizedImprovement"]))

    means = {s: statistics.fmean(values) for s, values in scores.items()}
    best = max(means.values())
    selected = max(s for s, value in means.items() if abs(value - best) <= policy.EPSILON)

    return {
        "version": 1,
        "complete": True,
        "blocks": len(blocks),
        "regimeCases": len(blocks) * len(policy.REGIMES),
        "calibrationSeeds": list(policy.CALIBRATION_SEEDS),
        "holdoutSeedsReserved": list(policy.HOLDOUT_SEEDS),
        "shareGrid": list(policy.HEDGE_SHARES),
        "policy": "paid explore prefix followed by a fixed split of remaining budget between causal adaptive continuation and independent breadth",
        "selectionRule": "highest mean combined normalized improvement across all calibration blocks; exact tie chooses larger adaptive share",
        "shares": {
            str(s): {
                "meanCombinedImprovement": means[s],
                "meanLocalImprovement": statistics.fmean(local_scores[s]),
                "meanGlobalImprovement": statistics.fmean(global_scores[s]),
                "rawStrictWinsVsAdaptive": strict[s],
                "rawNonWorseVsAdaptive": nonworse[s],
                "routeMeans": {route: statistics.fmean(route_scores[route][s]) for route in policy.ROUTE_ORDER},
            }
            for s in policy.HEDGE_SHARES
        },
        "selectedShare": selected,
        "meanFixedShareOracleImprovement": statistics.fmean(oracle_scores),
        "boundary": "hyperparameter calibration only; no untouched-holdout or artistic-quality claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
