#!/usr/bin/env python3
"""Aggregate preregistered sparse-shape sensitivity audit."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
SEEDS = (101, 103, 107)
METRICS = ("sparseShapeV1", "sparseShapeV2")
VARIANTS = (
    "exact", "shift1", "shift2", "shift3", "shift6", "shift12", "fade50", "blank",
    "validAlpha", "validNeighbor", "unrelatedValid", "deleteRightThird", "denseBBox", "duplicateShift6",
)
CONTRACTS = (
    "exactZero", "blankAtLeast099", "shift3Positive", "shortTranslationNondecreasing",
    "longTranslationStrict", "fadeBelowDelete", "deleteBelowBlank", "denseAboveNeighbor",
    "unrelatedAboveNeighbor", "duplicateAboveFade",
)
REQUIRED = {
    "exactZero": 30,
    "blankAtLeast099": 30,
    "shift3Positive": 30,
    "shortTranslationNondecreasing": 27,
    "longTranslationStrict": 27,
    "fadeBelowDelete": 27,
    "deleteBelowBlank": 30,
    "denseAboveNeighbor": 27,
    "unrelatedAboveNeighbor": 27,
    "duplicateAboveFade": 27,
}


def _load(results_dir: Path) -> list[dict]:
    blocks = []
    for path in sorted(results_dir.rglob("*.json")):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(data, dict) and data.get("route") in ROUTES and data.get("seed") in SEEDS and "cases" in data:
            blocks.append(data)
    expected = {(route, seed) for route in ROUTES for seed in SEEDS}
    seen = {(str(block["route"]), int(block["seed"])) for block in blocks}
    if seen != expected or len(blocks) != len(expected):
        raise AssertionError(f"sensitivity block mismatch missing={sorted(expected-seen)} extra={sorted(seen-expected)} count={len(blocks)}")
    return blocks


def _metric_summary(cases: list[dict], metric: str) -> dict:
    passes = {
        contract: sum(bool(case["contracts"][metric][contract]) for case in cases)
        for contract in CONTRACTS
    }
    means = {
        variant: statistics.fmean(float(case["distances"][variant][metric]) for case in cases)
        for variant in VARIANTS
    }
    by_route = {}
    for route in ROUTES:
        rows = [case for case in cases if case["route"] == route]
        by_route[route] = {
            "cases": len(rows),
            "contractPasses": {
                contract: sum(bool(case["contracts"][metric][contract]) for case in rows)
                for contract in CONTRACTS
            },
            "meanDistances": {
                variant: statistics.fmean(float(case["distances"][variant][metric]) for case in rows)
                for variant in VARIANTS
            },
        }
    qualification = {contract: passes[contract] >= REQUIRED[contract] for contract in CONTRACTS}
    return {
        "contractPasses": passes,
        "requiredPasses": REQUIRED,
        "qualificationChecks": qualification,
        "qualifies": all(qualification.values()),
        "meanDistances": means,
        "byRoute": by_route,
    }


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    cases = [case for block in blocks for case in block["cases"]]
    if len(cases) != 30:
        raise AssertionError(f"expected 30 target cases, got {len(cases)}")
    metrics = {metric: _metric_summary(cases, metric) for metric in METRICS}
    return {
        "version": 1,
        "blocks": len(blocks),
        "targetCases": len(cases),
        "consumedSeedsOnly": True,
        "metrics": metrics,
        "comparison": {
            "v1QualifiesUnderSensitivityContract": metrics["sparseShapeV1"]["qualifies"],
            "v2QualifiesUnderSensitivityContract": metrics["sparseShapeV2"]["qualifies"],
            "shift3MeanDistance": {
                metric: metrics[metric]["meanDistances"]["shift3"] for metric in METRICS
            },
        },
        "boundary": "instrument sensitivity audit only; a passing candidate is eligible for a separately preregistered fresh-seed search confirmation, not automatic benchmark adoption or artistic authority",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
