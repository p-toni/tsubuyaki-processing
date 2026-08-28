#!/usr/bin/env python3
"""Calibrate stage-1 response threshold on already-consumed seeds."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "policy.py"
spec = importlib.util.spec_from_file_location("stage1_response_policy", POLICY_PATH)
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
        if tuple(float(x) for x in doc.get("thresholds", ())) != tuple(policy.THRESHOLDS):
            raise AssertionError(f"threshold grid drift for {route}/{seed}")
        blocks[key] = doc

    expected = {
        (route, seed)
        for route in policy.ROUTE_ORDER
        for seed in policy.CALIBRATION_SEEDS
    }
    if set(blocks) != expected:
        raise AssertionError(
            f"calibration block mismatch missing={sorted(expected-set(blocks))} extra={sorted(set(blocks)-expected)}"
        )
    return blocks


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    scores = {t: [] for t in policy.THRESHOLDS}
    strict = {t: 0 for t in policy.THRESHOLDS}
    nonworse = {t: 0 for t in policy.THRESHOLDS}
    accuracy = {t: [] for t in policy.THRESHOLDS}
    breadth_rate = {t: [] for t in policy.THRESHOLDS}
    route_scores = {
        route: {t: [] for t in policy.THRESHOLDS}
        for route in policy.ROUTE_ORDER
    }
    local_gains = []
    global_gains = []

    for (route, _seed), block in blocks.items():
        local_gains.append(float(block["regimes"]["local"]["prefixResponse"]["normalizedBestGain"]))
        global_gains.append(float(block["regimes"]["global"]["prefixResponse"]["normalizedBestGain"]))
        for threshold in policy.THRESHOLDS:
            key = str(threshold)
            combined = block["combined"][key]
            value = float(combined["selectedImprovement"])
            adaptive = float(combined["adaptiveImprovement"])
            scores[threshold].append(value)
            route_scores[route][threshold].append(value)
            strict[threshold] += int(value > adaptive + policy.EPSILON)
            nonworse[threshold] += int(value + policy.EPSILON >= adaptive)
            for regime in policy.REGIMES:
                row = block["regimes"][regime]["thresholds"][key]
                accuracy[threshold].append(bool(row["choiceCorrect"]))
                breadth_rate[threshold].append(row["chosenPolicy"] == "stage1-then-breadth")

    means = {t: statistics.fmean(values) for t, values in scores.items()}
    best = max(means.values())
    selected = min(t for t, value in means.items() if abs(value - best) <= policy.EPSILON)

    return {
        "version": 1,
        "complete": True,
        "blocks": len(blocks),
        "regimeCases": len(blocks) * len(policy.REGIMES),
        "calibrationSeeds": list(policy.CALIBRATION_SEEDS),
        "holdoutSeedsReserved": list(policy.HOLDOUT_SEEDS),
        "thresholdGrid": list(policy.THRESHOLDS),
        "signal": "normalized objective gain from common starts through exact adaptive explore stage",
        "decision": "continue adaptive when prefix gain >= threshold; otherwise spend remaining equal budget on independent breadth",
        "selectionRule": "highest mean combined normalized improvement across all 60 calibration blocks; exact tie chooses smaller threshold",
        "thresholds": {
            str(t): {
                "meanCombinedImprovement": means[t],
                "rawStrictWinsVsAdaptive": strict[t],
                "rawNonWorseVsAdaptive": nonworse[t],
                "regimeChoiceAccuracyVsAdaptiveBreadthOracle": statistics.fmean(accuracy[t]),
                "breadthSwitchSelectionRate": statistics.fmean(breadth_rate[t]),
                "routeMeans": {
                    route: statistics.fmean(route_scores[route][t])
                    for route in policy.ROUTE_ORDER
                },
            }
            for t in policy.THRESHOLDS
        },
        "selectedThreshold": selected,
        "prefixResponseMeans": {
            "local": statistics.fmean(local_gains),
            "global": statistics.fmean(global_gains),
        },
        "boundary": "hyperparameter calibration only; no untouched-holdout or artistic-quality claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
