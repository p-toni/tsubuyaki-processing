#!/usr/bin/env python3
"""Apply preregistered coarse-to-fine scale-schedule calibration rule."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "policy.py"
spec = importlib.util.spec_from_file_location("mutation_scale_schedule_policy", POLICY_PATH)
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
        actual = tuple(float(x) for x in doc.get("contrasts", ()))
        if len(actual) != len(policy.CONTRASTS) or any(
            abs(a-b) > policy.EPSILON for a, b in zip(actual, policy.CONTRASTS)
        ):
            raise AssertionError(f"contrast grid drift for {route}/{seed}: {actual}")
        for regime in policy.REGIMES:
            row = doc["regimes"][regime]["schedules"]["1.0"]
            if not row.get("exactBaselineReplay"):
                raise AssertionError(f"q=1 exact replay missing for {route}/{seed}/{regime}")
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


def _tie_key(q: float) -> tuple[float, float]:
    return (abs(q - 1.0), q)


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    scores = {q: [] for q in policy.CONTRASTS}
    strict = {q: 0 for q in policy.CONTRASTS}
    nonworse = {q: 0 for q in policy.CONTRASTS}
    local = {q: [] for q in policy.CONTRASTS}
    global_ = {q: [] for q in policy.CONTRASTS}
    yields = {q: [] for q in policy.CONTRASTS}
    unique = {q: [] for q in policy.CONTRASTS}
    depth = {q: [] for q in policy.CONTRASTS}
    route_scores = {
        route: {q: [] for q in policy.CONTRASTS}
        for route in policy.ROUTE_ORDER
    }
    baseline_scores = []

    for (route, _seed), block in blocks.items():
        first = next(iter(block["combined"].values()))
        baseline_scores.append(float(first["baselineCombinedImprovement"]))
        for q in policy.CONTRASTS:
            key = str(q)
            combined = block["combined"][key]
            value = float(combined["combinedImprovement"])
            baseline = float(combined["baselineCombinedImprovement"])
            scores[q].append(value)
            route_scores[route][q].append(value)
            strict[q] += int(value > baseline + policy.EPSILON)
            nonworse[q] += int(value + policy.EPSILON >= baseline)
            yields[q].append(float(combined["meanValidYield"]))
            unique[q].append(float(combined["meanUniquePhenotypeRate"]))
            depth[q].append(float(combined["meanWinnerLineageDepth"]))
            local[q].append(float(block["regimes"]["local"]["schedules"][key]["normalizedImprovement"]))
            global_[q].append(float(block["regimes"]["global"]["schedules"][key]["normalizedImprovement"]))

    baseline_mean = statistics.fmean(baseline_scores)
    means = {q: statistics.fmean(values) for q, values in scores.items()}
    best = max(means.values())
    tied = [q for q, value in means.items() if abs(value - best) <= policy.EPSILON]
    selected = min(tied, key=_tie_key)

    return {
        "version": 1,
        "complete": True,
        "blocks": len(blocks),
        "regimeCases": len(blocks) * len(policy.REGIMES),
        "exactBaselineReplayCases": len(blocks) * len(policy.REGIMES),
        "calibrationSeeds": list(policy.CALIBRATION_SEEDS),
        "holdoutSeedsReserved": list(policy.HOLDOUT_SEEDS),
        "contrastGrid": list(policy.CONTRASTS),
        "schedule": "explore=1*q; roundA=.7; refine-local=.55/q; refine-jump=1.2",
        "selectionRule": "highest mean combined normalized improvement across all 90 calibration blocks; exact ties choose q closest to 1.0, then smaller q",
        "baselineMeanCombinedImprovement": baseline_mean,
        "contrasts": {
            str(q): {
                "meanCombinedImprovement": means[q],
                "meanDeltaVsBaseline": means[q] - baseline_mean,
                "rawStrictWinsVsBaseline": strict[q],
                "rawNonWorseVsBaseline": nonworse[q],
                "meanLocalImprovement": statistics.fmean(local[q]),
                "meanGlobalImprovement": statistics.fmean(global_[q]),
                "meanValidYield": statistics.fmean(yields[q]),
                "meanUniquePhenotypeRate": statistics.fmean(unique[q]),
                "meanWinnerLineageDepth": statistics.fmean(depth[q]),
                "effectiveScales": {
                    "explore": policy._scheduled_scale(1.0, q),
                    "roundA": policy._scheduled_scale(0.7, q),
                    "refineLocal": policy._scheduled_scale(0.55, q),
                    "refineJump": policy._scheduled_scale(1.2, q),
                },
                "routeMeans": {
                    route: statistics.fmean(route_scores[route][q])
                    for route in policy.ROUTE_ORDER
                },
            }
            for q in policy.CONTRASTS
        },
        "selectedContrast": selected,
        "boundary": "hyperparameter calibration only; untouched holdout remains sealed; no artistic-quality or production-default claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
