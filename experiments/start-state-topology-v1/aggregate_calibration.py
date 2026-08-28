#!/usr/bin/env python3
"""Calibrate the frozen start-concentration threshold on already-consumed seeds."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELECTOR_PATH = HERE / "selector.py"
spec = importlib.util.spec_from_file_location("start_state_selector", SELECTOR_PATH)
selector = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(selector)


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
        if route not in selector.ROUTE_ORDER or seed not in selector.CALIBRATION_SEEDS:
            continue
        key = (str(route), int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate calibration block {key}")
        if tuple(doc.get("thresholds", ())) != tuple(selector.THRESHOLDS):
            raise AssertionError(f"threshold grid drift for {route}/{seed}")
        if int(doc.get("pilotSize")) != selector.PILOT_SIZE:
            raise AssertionError(f"simple-probe pilot drift for {route}/{seed}")
        blocks[key] = doc

    expected = {
        (route, seed)
        for route in selector.ROUTE_ORDER
        for seed in selector.CALIBRATION_SEEDS
    }
    if set(blocks) != expected:
        raise AssertionError(
            f"calibration block mismatch missing={sorted(expected-set(blocks))} extra={sorted(set(blocks)-expected)}"
        )
    return blocks


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    scores = {t: [] for t in selector.THRESHOLDS}
    route_scores = {
        route: {t: [] for t in selector.THRESHOLDS}
        for route in selector.ROUTE_ORDER
    }
    strict = {t: 0 for t in selector.THRESHOLDS}
    nonworse = {t: 0 for t in selector.THRESHOLDS}
    accuracy = {t: [] for t in selector.THRESHOLDS}
    simple_rate = {t: [] for t in selector.THRESHOLDS}

    for (route, _seed), block in blocks.items():
        for threshold in selector.THRESHOLDS:
            key = str(threshold)
            combined = block["combined"][key]
            value = float(combined["selectedImprovement"])
            adaptive = float(combined["adaptiveImprovement"])
            scores[threshold].append(value)
            route_scores[route][threshold].append(value)
            strict[threshold] += int(value > adaptive + selector.EPSILON)
            nonworse[threshold] += int(value + selector.EPSILON >= adaptive)
            for regime in selector.REGIMES:
                row = block["regimes"][regime]["thresholds"][key]
                accuracy[threshold].append(bool(row["choiceCorrect"]))
                simple_rate[threshold].append(row["chosenPolicy"] == "simple-probe")

    mean_scores = {t: statistics.fmean(v) for t, v in scores.items()}
    best_mean = max(mean_scores.values())
    selected = min(
        t for t, value in mean_scores.items()
        if abs(value - best_mean) <= selector.EPSILON
    )

    return {
        "version": 1,
        "complete": True,
        "blocks": len(blocks),
        "regimeCases": len(blocks) * len(selector.REGIMES),
        "calibrationSeeds": list(selector.CALIBRATION_SEEDS),
        "holdoutSeedsReserved": list(selector.HOLDOUT_SEEDS),
        "thresholdGrid": list(selector.THRESHOLDS),
        "pilotSize": selector.PILOT_SIZE,
        "signal": "(second_best_start_distance - best_start_distance) / mean_start_distance",
        "decision": "adaptive when concentration >= threshold; otherwise simple-probe",
        "selectionRule": "highest mean combined normalized improvement across all 45 calibration blocks; exact tie chooses smaller threshold",
        "thresholds": {
            str(t): {
                "meanCombinedImprovement": mean_scores[t],
                "rawStrictWinsVsAdaptive": strict[t],
                "rawNonWorseVsAdaptive": nonworse[t],
                "regimeChoiceAccuracyVsAdaptiveSimpleOracle": statistics.fmean(accuracy[t]),
                "simpleProbeSelectionRate": statistics.fmean(simple_rate[t]),
                "routeMeans": {
                    route: statistics.fmean(route_scores[route][t])
                    for route in selector.ROUTE_ORDER
                },
            }
            for t in selector.THRESHOLDS
        },
        "selectedThreshold": selected,
        "boundary": "hyperparameter calibration only; no untouched-holdout or artistic-quality claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
