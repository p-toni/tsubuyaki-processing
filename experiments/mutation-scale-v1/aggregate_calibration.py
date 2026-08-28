#!/usr/bin/env python3
"""Apply the preregistered global mutation-scale calibration rule."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "policy.py"
spec = importlib.util.spec_from_file_location("mutation_scale_policy", POLICY_PATH)
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
        if tuple(float(x) for x in doc.get("multipliers", ())) != tuple(policy.MULTIPLIERS):
            raise AssertionError(f"multiplier grid drift for {route}/{seed}")
        for regime in policy.REGIMES:
            row = doc["regimes"][regime]["multipliers"]["1.0"]
            if not row.get("exactBaselineReplay"):
                raise AssertionError(f"m=1 exact replay missing for {route}/{seed}/{regime}")
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


def _tie_key(multiplier: float) -> tuple[float, float]:
    return (abs(multiplier - 1.0), multiplier)


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    scores = {m: [] for m in policy.MULTIPLIERS}
    strict = {m: 0 for m in policy.MULTIPLIERS}
    nonworse = {m: 0 for m in policy.MULTIPLIERS}
    local = {m: [] for m in policy.MULTIPLIERS}
    global_ = {m: [] for m in policy.MULTIPLIERS}
    yields = {m: [] for m in policy.MULTIPLIERS}
    unique = {m: [] for m in policy.MULTIPLIERS}
    depth = {m: [] for m in policy.MULTIPLIERS}
    route_scores = {
        route: {m: [] for m in policy.MULTIPLIERS}
        for route in policy.ROUTE_ORDER
    }
    baseline_scores = []

    for (route, _seed), block in blocks.items():
        first = next(iter(block["combined"].values()))
        baseline_scores.append(float(first["baselineCombinedImprovement"]))
        for m in policy.MULTIPLIERS:
            key = str(m)
            combined = block["combined"][key]
            value = float(combined["combinedImprovement"])
            baseline = float(combined["baselineCombinedImprovement"])
            scores[m].append(value)
            route_scores[route][m].append(value)
            strict[m] += int(value > baseline + policy.EPSILON)
            nonworse[m] += int(value + policy.EPSILON >= baseline)
            yields[m].append(float(combined["meanValidYield"]))
            unique[m].append(float(combined["meanUniquePhenotypeRate"]))
            depth[m].append(float(combined["meanWinnerLineageDepth"]))
            local[m].append(float(block["regimes"]["local"]["multipliers"][key]["normalizedImprovement"]))
            global_[m].append(float(block["regimes"]["global"]["multipliers"][key]["normalizedImprovement"]))

    means = {m: statistics.fmean(values) for m, values in scores.items()}
    best = max(means.values())
    tied = [m for m, value in means.items() if abs(value - best) <= policy.EPSILON]
    selected = min(tied, key=_tie_key)

    return {
        "version": 1,
        "complete": True,
        "blocks": len(blocks),
        "regimeCases": len(blocks) * len(policy.REGIMES),
        "exactBaselineReplayCases": len(blocks) * len(policy.REGIMES),
        "calibrationSeeds": list(policy.CALIBRATION_SEEDS),
        "holdoutSeedsReserved": list(policy.HOLDOUT_SEEDS),
        "multiplierGrid": list(policy.MULTIPLIERS),
        "selectionRule": "highest mean combined normalized improvement across all 90 calibration blocks; exact ties choose multiplier closest to 1.0, then smaller multiplier",
        "baselineMeanCombinedImprovement": statistics.fmean(baseline_scores),
        "multipliers": {
            str(m): {
                "meanCombinedImprovement": means[m],
                "meanDeltaVsBaseline": means[m] - statistics.fmean(baseline_scores),
                "rawStrictWinsVsBaseline": strict[m],
                "rawNonWorseVsBaseline": nonworse[m],
                "meanLocalImprovement": statistics.fmean(local[m]),
                "meanGlobalImprovement": statistics.fmean(global_[m]),
                "meanValidYield": statistics.fmean(yields[m]),
                "meanUniquePhenotypeRate": statistics.fmean(unique[m]),
                "meanWinnerLineageDepth": statistics.fmean(depth[m]),
                "routeMeans": {
                    route: statistics.fmean(route_scores[route][m])
                    for route in policy.ROUTE_ORDER
                },
            }
            for m in policy.MULTIPLIERS
        },
        "selectedMultiplier": selected,
        "boundary": "hyperparameter calibration only; untouched holdout remains sealed; no artistic-quality or production-default claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
