#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

MASTER_SEEDS = (
    120011, 120017, 120041, 120047, 120049,
    120067, 120071, 120079, 120097, 120103,
    120121, 120133, 120157, 120163, 120181,
    120193, 120199, 120223, 120233, 120247,
)
ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
FAMILIES = (
    "disconnected-loops",
    "nested-loops",
    "concave-loops",
    "open-networks",
    "dense-regions",
)
CELLS_PER_SEED = 75
MEAN_MARGIN = 0.002
MEANINGFUL_MARGIN = 0.005
T95_DF19_ONE_SIDED = 1.7291328115213682
EPS = 1e-12


def _load_inputs(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or "masterSeed" not in data:
            continue
        rows.append(data)
    return rows


def _summary(values: list[float]) -> dict:
    return {
        "n": len(values),
        "mean": statistics.fmean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def aggregate(blocks: list[dict]) -> dict:
    seeds = [int(block["masterSeed"]) for block in blocks]
    if len(seeds) != len(set(seeds)):
        raise AssertionError("duplicate master-seed blocks")
    if tuple(sorted(seeds)) != tuple(sorted(MASTER_SEEDS)):
        raise AssertionError(f"consumed seed set mismatch: {sorted(seeds)}")

    settings = blocks[0]["settings"]
    if any(block["settings"] != settings for block in blocks[1:]):
        raise AssertionError("settings drift across master seeds")
    if settings["routes"] != list(ROUTES):
        raise AssertionError("route order drift")
    if settings["startsPerRoute"] != 2 or settings["challengersPerArm"] != 12:
        raise AssertionError("budget drift")
    if float(settings["spectralAmplitude"]) != 16.0:
        raise AssertionError("calibrated amplitude drift")

    all_cells = []
    target_signature = None
    for block in blocks:
        if not all(block.get("hardInvariants", {}).values()):
            raise AssertionError(f"hard invariant failure in seed {block['masterSeed']}")
        cells = block["cells"]
        if len(cells) != CELLS_PER_SEED:
            raise AssertionError(f"cell count drift in seed {block['masterSeed']}")
        signature = tuple(sorted((c["route"], c["targetId"], c["targetFamily"]) for c in cells))
        if len(signature) != len(set(signature)):
            raise AssertionError(f"duplicate route/target cell in seed {block['masterSeed']}")
        if target_signature is None:
            target_signature = signature
        elif signature != target_signature:
            raise AssertionError("target/route rectangle drift across seeds")
        all_cells.extend(cells)

    if len(all_cells) != len(MASTER_SEEDS) * CELLS_PER_SEED:
        raise AssertionError("aggregate rectangle incomplete")
    family_counts = Counter(c["targetFamily"] for c in blocks[0]["cells"])
    if family_counts != Counter({family: 15 for family in FAMILIES}):
        # 5 routes × 3 targets per family = 15 cells per family in each seed.
        raise AssertionError(f"target family rectangle drift: {family_counts}")

    deltas = [float(c["delta"]) for c in all_cells]
    native_added = [float(c["nativeAdded"]) for c in all_cells]
    spectral_added = [float(c["spectralAdded"]) for c in all_cells]

    by_seed = defaultdict(list)
    by_route = defaultdict(list)
    by_family = defaultdict(list)
    for cell in all_cells:
        delta = float(cell["delta"])
        by_seed[int(cell["masterSeed"])].append(delta)
        by_route[cell["route"]].append(delta)
        by_family[cell["targetFamily"]].append(delta)

    master_means = {str(seed): statistics.fmean(by_seed[seed]) for seed in MASTER_SEEDS}
    seed_values = [master_means[str(seed)] for seed in MASTER_SEEDS]
    seed_mean = statistics.fmean(seed_values)
    seed_sd = statistics.stdev(seed_values)
    lower95 = seed_mean - T95_DF19_ONE_SIDED * seed_sd / math.sqrt(len(seed_values))

    route_means = {route: statistics.fmean(by_route[route]) for route in ROUTES}
    family_means = {family: statistics.fmean(by_family[family]) for family in FAMILIES}
    leave_one_family_out = {
        family: statistics.fmean(
            float(c["delta"]) for c in all_cells if c["targetFamily"] != family
        )
        for family in FAMILIES
    }

    meaningful_win_fraction = sum(d > MEANINGFUL_MARGIN for d in deltas) / len(deltas)
    meaningful_loss_fraction = sum(d < -MEANINGFUL_MARGIN for d in deltas) / len(deltas)

    spectral_valid = 0
    spectral_attempts = 0
    native_valid = 0
    native_attempts = 0
    spectral_by_route = {route: [0, 0] for route in ROUTES}
    native_by_route = {route: [0, 0] for route in ROUTES}
    spectral_failures = Counter()
    for block in blocks:
        for route in ROUTES:
            diag = block["routeDiagnostics"][route]
            sa = int(diag["spectralAttempts"])
            sv = int(diag["spectralValid"])
            na = int(diag["nativeAttempts"])
            nv = int(diag["nativeValid"])
            spectral_attempts += sa
            spectral_valid += sv
            native_attempts += na
            native_valid += nv
            spectral_by_route[route][0] += sv
            spectral_by_route[route][1] += sa
            native_by_route[route][0] += nv
            native_by_route[route][1] += na
            spectral_failures.update(diag.get("spectralFailureModes", []))

    spectral_valid_fraction = spectral_valid / spectral_attempts
    native_valid_fraction = native_valid / native_attempts
    spectral_route_valid = {
        route: valid / attempts for route, (valid, attempts) in spectral_by_route.items()
    }
    native_route_valid = {
        route: valid / attempts for route, (valid, attempts) in native_by_route.items()
    }

    positive_by_family = {
        family: sum(max(0.0, float(c["delta"])) for c in all_cells if c["targetFamily"] == family)
        for family in FAMILIES
    }
    total_positive = sum(positive_by_family.values())
    positive_share = {
        family: (value / total_positive if total_positive > EPS else 0.0)
        for family, value in positive_by_family.items()
    }
    max_positive_share = max(positive_share.values(), default=1.0)

    gates = {
        "completeHardInvariantRectangle": True,
        "meanDeltaAtLeast002": seed_mean >= MEAN_MARGIN,
        "masterSeedLower95Positive": lower95 > 0.0,
        "allFiveRouteMeansPositive": all(route_means[route] > 0.0 for route in ROUTES),
        "allLeaveOneFamilyOutPositive": all(
            leave_one_family_out[family] > 0.0 for family in FAMILIES
        ),
        "meaningfulWinsExceedLosses": meaningful_win_fraction > meaningful_loss_fraction,
        "spectralValidityRetained": (
            spectral_valid_fraction >= 0.95
            and min(spectral_route_valid.values()) >= 0.90
        ),
        "positiveAdvantageNotFamilyConcentrated": (
            total_positive > EPS and max_positive_share <= 0.50
        ),
    }
    decision = (
        "SPECTRAL_MATERIAL_CONTROL_OPERATOR_PROMISING"
        if all(gates.values())
        else "SPECTRAL_MATERIAL_CONTROL_OPERATOR_NOT_PROMISING"
    )

    return {
        "version": 1,
        "decision": decision,
        "population": {
            "masterSeeds": list(MASTER_SEEDS),
            "routes": list(ROUTES),
            "targetFamilies": list(FAMILIES),
            "cells": len(all_cells),
            "settings": settings,
        },
        "gates": gates,
        "delta": _summary(deltas),
        "masterSeedDelta": {
            **_summary(seed_values),
            "oneSided95Lower": lower95,
            "tCritical": T95_DF19_ONE_SIDED,
            "perSeed": master_means,
        },
        "routeMeanDelta": route_means,
        "familyMeanDelta": family_means,
        "leaveOneFamilyOutMeanDelta": leave_one_family_out,
        "meaningful": {
            "margin": MEANINGFUL_MARGIN,
            "winFraction": meaningful_win_fraction,
            "lossFraction": meaningful_loss_fraction,
        },
        "addedRecovery": {
            "native": _summary(native_added),
            "spectral": _summary(spectral_added),
        },
        "validity": {
            "spectralPooled": spectral_valid_fraction,
            "spectralByRoute": spectral_route_valid,
            "nativePooled": native_valid_fraction,
            "nativeByRoute": native_route_valid,
            "spectralFailureModes": dict(spectral_failures),
        },
        "positiveAdvantageConcentration": {
            "byFamily": positive_by_family,
            "shareByFamily": positive_share,
            "maxFamilyShare": max_positive_share,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(args.input_root)
    blocks = _load_inputs(sorted(root.rglob("*.json")))
    result = aggregate(blocks)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
