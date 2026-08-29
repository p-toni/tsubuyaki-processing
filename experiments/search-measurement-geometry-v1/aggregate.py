#!/usr/bin/env python3
"""Aggregate sparse-geometry-v1 design and metric-holdout evidence."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
DESIGN_SEEDS = (101, 103, 107)
HOLDOUT_SEEDS = (109, 113, 127)
SEEDS = DESIGN_SEEDS + HOLDOUT_SEEDS
VARIANTS = (
    "exact", "shift1", "shift2", "shift3", "shift6", "shift12", "fade50", "blank",
    "validAlpha", "validNeighbor", "unrelatedValid", "deleteRightThird", "denseBBox", "duplicateShift6",
)
COMPONENTS = ("placement", "shape", "extent", "mass")
CONTRACTS = (
    "exactZero", "blankOne", "translationsStrict", "shift3BelowFade", "shift12BelowDelete",
    "alphaBelowDelete", "deleteBelowBlank", "neighborBelowUnrelated", "neighborBelowDense",
    "duplicateAboveFade", "duplicateAboveShift12",
)
HOLDOUT_REQUIRED = {
    "exactZero": 30,
    "blankOne": 30,
    "translationsStrict": 30,
    "shift3BelowFade": 30,
    "shift12BelowDelete": 27,
    "alphaBelowDelete": 27,
    "deleteBelowBlank": 30,
    "neighborBelowUnrelated": 27,
    "neighborBelowDense": 27,
    "duplicateAboveFade": 27,
    "duplicateAboveShift12": 27,
}


def _load(results_dir: Path) -> list[dict]:
    blocks = []
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict) or doc.get("metric") != "sparse-geometry-v1":
            continue
        route = doc.get("route")
        seed = doc.get("seed")
        if route in ROUTES and seed in SEEDS and "cases" in doc:
            blocks.append(doc)
    expected = {(route, seed) for route in ROUTES for seed in SEEDS}
    seen = {(str(block["route"]), int(block["seed"])) for block in blocks}
    if seen != expected or len(blocks) != len(expected):
        raise AssertionError(f"geometry block mismatch missing={sorted(expected-seen)} extra={sorted(seen-expected)} count={len(blocks)}")
    return blocks


def _population_summary(cases: list[dict], required: dict[str, int] | None) -> dict:
    if len(cases) != 30:
        raise AssertionError(f"expected 30 cases in population, got {len(cases)}")
    contract_passes = {
        contract: sum(bool(case["contracts"][contract]) for case in cases)
        for contract in CONTRACTS
    }
    means = {
        variant: statistics.fmean(float(case["distances"][variant]["distance"]) for case in cases)
        for variant in VARIANTS
    }
    component_means = {
        variant: {
            component: statistics.fmean(float(case["distances"][variant]["components"][component]) for case in cases)
            for component in COMPONENTS
        }
        for variant in VARIANTS
    }
    by_route = {}
    for route in ROUTES:
        rows = [case for case in cases if case["route"] == route]
        by_route[route] = {
            "cases": len(rows),
            "contractPasses": {
                contract: sum(bool(case["contracts"][contract]) for case in rows)
                for contract in CONTRACTS
            },
            "meanDistances": {
                variant: statistics.fmean(float(case["distances"][variant]["distance"]) for case in rows)
                for variant in VARIANTS
            },
        }
    violations = [
        {
            "route": case["route"],
            "seed": case["seed"],
            "regime": case["regime"],
            "failed": [contract for contract in CONTRACTS if not case["contracts"][contract]],
        }
        for case in cases
        if any(not case["contracts"][contract] for contract in CONTRACTS)
    ]
    out = {
        "targetCases": len(cases),
        "contractPasses": contract_passes,
        "meanDistances": means,
        "componentMeans": component_means,
        "byRoute": by_route,
        "violations": violations,
    }
    if required is not None:
        checks = {contract: contract_passes[contract] >= threshold for contract, threshold in required.items()}
        out["requiredPasses"] = required
        out["qualificationChecks"] = checks
        out["qualifies"] = all(checks.values())
    return out


def aggregate(results_dir: Path) -> dict:
    blocks = _load(results_dir)
    cases = [case for block in blocks for case in block["cases"]]
    if len(cases) != 60:
        raise AssertionError(f"expected 60 total target cases, got {len(cases)}")
    design = [case for case in cases if int(case["seed"]) in DESIGN_SEEDS]
    holdout = [case for case in cases if int(case["seed"]) in HOLDOUT_SEEDS]
    return {
        "version": 1,
        "metric": "sparse-geometry-v1",
        "blocks": len(blocks),
        "freshSearchSeedsConsumed": False,
        "designSeeds": list(DESIGN_SEEDS),
        "metricHoldoutSeeds": list(HOLDOUT_SEEDS),
        "design": _population_summary(design, None),
        "holdout": _population_summary(holdout, HOLDOUT_REQUIRED),
        "boundary": "instrument validation only; holdout qualification authorizes complete consumed-seed search replay research, not benchmark adoption or artistic authority",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
