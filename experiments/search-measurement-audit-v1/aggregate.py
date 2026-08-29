#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
SEEDS = (101, 103, 107)
VARIANTS = ("exact", "shift3", "fade50", "blank", "validAlpha", "validNeighbor", "unrelatedValid")
METRICS = ("currentMAE", "sparseShapeV1")


def _load(results_dir: Path) -> list[dict]:
    blocks = []
    for path in sorted(results_dir.rglob("*.json")):
        data = json.loads(path.read_text())
        if isinstance(data, dict) and data.get("route") in ROUTES and data.get("seed") in SEEDS and "cases" in data:
            blocks.append(data)
    expected = {(r, s) for r in ROUTES for s in SEEDS}
    seen = {(b["route"], int(b["seed"])) for b in blocks}
    if seen != expected or len(blocks) != len(expected):
        raise AssertionError(f"measurement audit block mismatch expected={sorted(expected)} seen={sorted(seen)} count={len(blocks)}")
    return blocks


def aggregate(blocks: list[dict]) -> dict:
    cases = [case for block in blocks for case in block["cases"]]
    if len(cases) != 30:
        raise AssertionError(f"expected 30 target cases, got {len(cases)}")

    current_blank_shift = sum(bool(c["currentMAEBlankBeatsShift3"]) for c in cases)
    current_blank_neighbor = sum(bool(c["currentMAEBlankBeatsValidNeighbor"]) for c in cases)
    current_blank_unrelated = sum(bool(c["currentMAEBlankBeatsUnrelatedValid"]) for c in cases)
    candidate_passes = sum(bool(c["sparseShapeV1AllContractsPass"]) for c in cases)

    means = {}
    for metric in METRICS:
        means[metric] = {
            variant: statistics.fmean(float(c["distances"][variant][metric]) for c in cases)
            for variant in VARIANTS
        }

    by_route = {}
    for route in ROUTES:
        rs = [c for c in cases if c["route"] == route]
        by_route[route] = {
            "cases": len(rs),
            "currentMAEBlankBeatsShift3": sum(bool(c["currentMAEBlankBeatsShift3"]) for c in rs),
            "currentMAEBlankBeatsValidNeighbor": sum(bool(c["currentMAEBlankBeatsValidNeighbor"]) for c in rs),
            "currentMAEBlankBeatsUnrelatedValid": sum(bool(c["currentMAEBlankBeatsUnrelatedValid"]) for c in rs),
            "sparseShapeV1ContractPasses": sum(bool(c["sparseShapeV1AllContractsPass"]) for c in rs),
            "meanCurrentBlankDistance": statistics.fmean(float(c["distances"]["blank"]["currentMAE"]) for c in rs),
            "meanCurrentShift3Distance": statistics.fmean(float(c["distances"]["shift3"]["currentMAE"]) for c in rs),
            "meanSparseBlankDistance": statistics.fmean(float(c["distances"]["blank"]["sparseShapeV1"]) for c in rs),
            "meanSparseShift3Distance": statistics.fmean(float(c["distances"]["shift3"]["sparseShapeV1"]) for c in rs),
        }

    mass_diagnostics = []
    for c in cases:
        target_mass = float(c["distances"]["exact"]["meanInkMass"])
        for variant in ("validAlpha", "validNeighbor", "unrelatedValid"):
            row = c["distances"][variant]
            mass_diagnostics.append({
                "route": c["route"],
                "seed": c["seed"],
                "regime": c["regime"],
                "variant": variant,
                "massRatioToTarget": float(row["meanInkMass"]) / target_mass if target_mass else 0.0,
                "currentMAE": float(row["currentMAE"]),
                "sparseShapeV1": float(row["sparseShapeV1"]),
            })

    return {
        "version": 1,
        "blocks": len(blocks),
        "targetCases": len(cases),
        "currentMAE": {
            "falsificationContract": "falsified if any target has blank distance < exact 3px-shift distance",
            "blankBeatsShift3Cases": current_blank_shift,
            "falsifiedAsStructuralRecoveryObjective": current_blank_shift > 0,
            "blankBeatsValidNeighborCases": current_blank_neighbor,
            "blankBeatsUnrelatedValidCases": current_blank_unrelated,
        },
        "sparseShapeV1": {
            "qualificationContract": "all 30 targets pass exactZero, shiftBeatsBlank, fadeBeatsBlank, validAlphaBeatsBlank, blankAtLeast099, shiftAtMost025",
            "contractPassCases": candidate_passes,
            "qualifiesForLaterBenchmarkReplay": candidate_passes == len(cases),
        },
        "meanDistances": means,
        "byRoute": by_route,
        "candidateMassDiagnostics": mass_diagnostics,
        "boundary": "instrument audit only; candidate metric qualification authorizes benchmark replay research, not automatic replacement or artistic authority",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(_load(args.results_dir)), indent=2))


if __name__ == "__main__":
    main()
