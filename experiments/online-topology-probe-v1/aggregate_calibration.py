#!/usr/bin/env python3
"""Select the global probe pilot size from already-used calibration seeds."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE_PATH = HERE / "probe.py"
spec = importlib.util.spec_from_file_location("online_probe", PROBE_PATH)
probe = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(probe)


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
        if route not in probe.ROUTE_ORDER or seed not in probe.CALIBRATION_SEEDS:
            continue
        key = (str(route), int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate calibration block {key}")
        blocks[key] = doc
    expected = {
        (route, seed)
        for route in probe.ROUTE_ORDER
        for seed in probe.CALIBRATION_SEEDS
    }
    if set(blocks) != expected:
        raise AssertionError(
            f"calibration block mismatch missing={sorted(expected-set(blocks))} extra={sorted(set(blocks)-expected)}"
        )
    return blocks


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    scores = {p: [] for p in probe.PILOT_SIZES}
    route_scores = {
        route: {p: [] for p in probe.PILOT_SIZES}
        for route in probe.ROUTE_ORDER
    }
    nonworse = {p: 0 for p in probe.PILOT_SIZES}
    strict = {p: 0 for p in probe.PILOT_SIZES}
    arm_accuracy = {p: [] for p in probe.PILOT_SIZES}

    for (route, seed), block in blocks.items():
        if tuple(block.get("pilotSizes", ())) != tuple(probe.PILOT_SIZES):
            raise AssertionError(f"pilot-size drift for {route}/{seed}")
        if tuple(block.get("times", ())) != tuple(probe.v1.TIMES):
            raise AssertionError(f"time drift for {route}/{seed}")
        combined = block.get("combinedNormalizedImprovement") or {}
        adaptive = float(combined["adaptive"])
        probe_scores = combined.get("probes") or {}
        if set(probe_scores) != {str(p) for p in probe.PILOT_SIZES}:
            raise AssertionError(f"probe score set drift for {route}/{seed}")

        for p in probe.PILOT_SIZES:
            value = float(probe_scores[str(p)])
            scores[p].append(value)
            route_scores[route][p].append(value)
            nonworse[p] += int(value + probe.EPSILON >= adaptive)
            strict[p] += int(value > adaptive + probe.EPSILON)

            for regime in probe.REGIMES:
                rd = block["regimes"][regime]
                chosen = rd["probes"][str(p)]["chosenArm"]
                arm_accuracy[p].append(chosen == rd["simpleOracleArm"])

    mean_scores = {p: statistics.fmean(values) for p, values in scores.items()}
    best_mean = max(mean_scores.values())
    selected = min(
        p for p, value in mean_scores.items()
        if abs(value - best_mean) <= probe.EPSILON
    )

    return {
        "version": 1,
        "complete": True,
        "blocks": len(blocks),
        "calibrationSeeds": list(probe.CALIBRATION_SEEDS),
        "holdoutSeedsReserved": list(probe.HOLDOUT_SEEDS),
        "candidatePilotSizes": list(probe.PILOT_SIZES),
        "selectionRule": "highest mean combined normalized improvement across all 30 calibration blocks; exact tie chooses smaller p",
        "pilotSizes": {
            str(p): {
                "meanCombinedImprovement": mean_scores[p],
                "rawNonWorseVsAdaptive": nonworse[p],
                "rawStrictWinsVsAdaptive": strict[p],
                "pilotArmChoiceAccuracy": statistics.fmean(arm_accuracy[p]),
                "routeMeans": {
                    route: statistics.fmean(route_scores[route][p])
                    for route in probe.ROUTE_ORDER
                },
            }
            for p in probe.PILOT_SIZES
        },
        "selectedPilotSize": selected,
        "boundary": "hyperparameter calibration only; no holdout or artistic-quality claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
