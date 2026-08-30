#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

MASTER_SEEDS = (
    122011, 122021, 122027, 122029, 122033, 122039,
    122041, 122051, 122053, 122069, 122081, 122099,
    122117, 122131, 122147, 122149, 122167, 122173,
    122201, 122203, 122207, 122209, 122219, 122231,
)
ROUTES = ("recurrence", "orbit", "filament")
FAMILIES = ("disconnected-loops", "nested-loops", "concave-loops", "open-networks", "dense-regions")
CELLS_PER_SEED = 45
MEAN_MARGIN = 0.005
MEANINGFUL_MARGIN = 0.005
T95_DF23_ONE_SIDED = 1.713871527747048
EPS = 1e-12


def _load_inputs(paths: list[Path]) -> list[dict]:
    out = []
    for path in paths:
        data = json.loads(path.read_text())
        if isinstance(data, dict) and "masterSeed" in data:
            out.append(data)
    return out


def _summary(values: list[float]) -> dict:
    return {
        "n": len(values),
        "mean": statistics.fmean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def _lower95(values: list[float]) -> float:
    if len(values) != len(MASTER_SEEDS):
        raise AssertionError("seed-mean count drift")
    return statistics.fmean(values) - T95_DF23_ONE_SIDED * statistics.stdev(values) / math.sqrt(len(values))


def aggregate(blocks: list[dict]) -> dict:
    seeds = [int(b["masterSeed"]) for b in blocks]
    if len(seeds) != len(set(seeds)):
        raise AssertionError("duplicate master-seed blocks")
    if tuple(sorted(seeds)) != tuple(sorted(MASTER_SEEDS)):
        raise AssertionError(f"consumed seed set mismatch: {sorted(seeds)}")

    settings = blocks[0]["settings"]
    if any(b["settings"] != settings for b in blocks[1:]):
        raise AssertionError("settings drift")
    if settings["routes"] != list(ROUTES):
        raise AssertionError("route drift")
    if settings["excludedRoutesByFrozenIntrinsicDimension"] != ["family", "sheet"]:
        raise AssertionError("topology exclusion drift")
    if settings["totalChallengersPerArm"] != 12:
        raise AssertionError("total budget drift")
    if settings["baselineNativePerStart"] != 6 or settings["mixedNativePerStart"] != 3 or settings["mixedSpectralPerStart"] != 3:
        raise AssertionError("portfolio split drift")
    if float(settings["spectralAmplitude"]) != 16.0:
        raise AssertionError("spectral amplitude drift")

    all_cells = []
    signature0 = None
    for block in blocks:
        if not all(block.get("hardInvariants", {}).values()):
            raise AssertionError(f"hard invariant failure in seed {block['masterSeed']}")
        cells = block["cells"]
        if len(cells) != CELLS_PER_SEED:
            raise AssertionError(f"cell count drift in seed {block['masterSeed']}")
        sig = tuple(sorted((c["route"], c["targetId"], c["targetFamily"]) for c in cells))
        if len(sig) != len(set(sig)):
            raise AssertionError("duplicate route/target cell")
        if signature0 is None:
            signature0 = sig
        elif sig != signature0:
            raise AssertionError("target rectangle drift")
        all_cells.extend(cells)

    if len(all_cells) != len(MASTER_SEEDS) * CELLS_PER_SEED:
        raise AssertionError("aggregate rectangle incomplete")
    if Counter(c["targetFamily"] for c in blocks[0]["cells"]) != Counter({f: 9 for f in FAMILIES}):
        raise AssertionError("target family rectangle drift")

    deltas = [float(c["delta"]) for c in all_cells]
    baseline_added = [float(c["baselineAdded"]) for c in all_cells]
    mixed_added = [float(c["mixedAdded"]) for c in all_cells]
    by_seed = defaultdict(list)
    by_route = defaultdict(list)
    by_route_seed = defaultdict(list)
    by_family = defaultdict(list)
    for c in all_cells:
        d = float(c["delta"])
        seed = int(c["masterSeed"])
        route = c["route"]
        by_seed[seed].append(d)
        by_route[route].append(d)
        by_route_seed[(route, seed)].append(d)
        by_family[c["targetFamily"]].append(d)

    seed_means = {str(s): statistics.fmean(by_seed[s]) for s in MASTER_SEEDS}
    seed_values = [seed_means[str(s)] for s in MASTER_SEEDS]
    global_lower = _lower95(seed_values)
    route_means = {r: statistics.fmean(by_route[r]) for r in ROUTES}
    route_seed_stats = {}
    for route in ROUTES:
        per_seed = {str(s): statistics.fmean(by_route_seed[(route, s)]) for s in MASTER_SEEDS}
        values = [per_seed[str(s)] for s in MASTER_SEEDS]
        route_seed_stats[route] = {**_summary(values), "oneSided95Lower": _lower95(values), "perSeed": per_seed}

    family_means = {f: statistics.fmean(by_family[f]) for f in FAMILIES}
    leave_one_family_out = {
        f: statistics.fmean(float(c["delta"]) for c in all_cells if c["targetFamily"] != f)
        for f in FAMILIES
    }
    win_fraction = sum(d > MEANINGFUL_MARGIN for d in deltas) / len(deltas)
    loss_fraction = sum(d < -MEANINGFUL_MARGIN for d in deltas) / len(deltas)

    baseline_native_valid = baseline_native_attempts = 0
    mixed_native_valid = mixed_native_attempts = 0
    spectral_valid = spectral_attempts = 0
    spectral_by_route = {r: [0, 0] for r in ROUTES}
    failures = Counter()
    for block in blocks:
        for route in ROUTES:
            diag = block["routeDiagnostics"][route]
            baseline_native_attempts += int(diag["baselineNativeAttempts"])
            baseline_native_valid += int(diag["baselineNativeValid"])
            mixed_native_attempts += int(diag["mixedNativeAttempts"])
            mixed_native_valid += int(diag["mixedNativeValid"])
            sa, sv = int(diag["mixedSpectralAttempts"]), int(diag["mixedSpectralValid"])
            spectral_attempts += sa
            spectral_valid += sv
            spectral_by_route[route][0] += sv
            spectral_by_route[route][1] += sa
            failures.update(diag.get("mixedSpectralFailureModes", []))
    spectral_pooled = spectral_valid / spectral_attempts
    spectral_route_valid = {r: v / a for r, (v, a) in spectral_by_route.items()}

    positive_by_family = {
        f: sum(max(0.0, float(c["delta"])) for c in all_cells if c["targetFamily"] == f)
        for f in FAMILIES
    }
    total_positive = sum(positive_by_family.values())
    shares = {f: (v / total_positive if total_positive > EPS else 0.0) for f, v in positive_by_family.items()}
    max_share = max(shares.values(), default=1.0)

    gates = {
        "completeHardInvariantRectangle": True,
        "meanDeltaAtLeast005": statistics.fmean(seed_values) >= MEAN_MARGIN,
        "globalMasterSeedLower95Positive": global_lower > 0.0,
        "allThreeRouteMeansPositive": all(route_means[r] > 0.0 for r in ROUTES),
        "allThreeRouteSeedLower95Positive": all(route_seed_stats[r]["oneSided95Lower"] > 0.0 for r in ROUTES),
        "allLeaveOneFamilyOutPositive": all(leave_one_family_out[f] > 0.0 for f in FAMILIES),
        "meaningfulWinsExceedLosses": win_fraction > loss_fraction,
        "spectralValidityRetained": spectral_pooled >= 0.95 and min(spectral_route_valid.values()) >= 0.90,
        "positiveAdvantageNotFamilyConcentrated": total_positive > EPS and max_share <= 0.50,
    }
    decision = "SPECTRAL_MATERIAL_CONTROL_1D_PORTFOLIO_PROMISING" if all(gates.values()) else "SPECTRAL_MATERIAL_CONTROL_1D_PORTFOLIO_NOT_PROMISING"

    return {
        "version": 1,
        "decision": decision,
        "population": {"masterSeeds": list(MASTER_SEEDS), "routes": list(ROUTES), "targetFamilies": list(FAMILIES), "cells": len(all_cells), "settings": settings},
        "gates": gates,
        "delta": _summary(deltas),
        "masterSeedDelta": {**_summary(seed_values), "oneSided95Lower": global_lower, "tCritical": T95_DF23_ONE_SIDED, "perSeed": seed_means},
        "routeMeanDelta": route_means,
        "routeMasterSeedDelta": route_seed_stats,
        "familyMeanDelta": family_means,
        "leaveOneFamilyOutMeanDelta": leave_one_family_out,
        "meaningful": {"margin": MEANINGFUL_MARGIN, "winFraction": win_fraction, "lossFraction": loss_fraction},
        "addedRecovery": {"nativeOnly": _summary(baseline_added), "mixed": _summary(mixed_added)},
        "validity": {
            "baselineNativePooled": baseline_native_valid / baseline_native_attempts,
            "mixedNativePooled": mixed_native_valid / mixed_native_attempts,
            "mixedSpectralPooled": spectral_pooled,
            "mixedSpectralByRoute": spectral_route_valid,
            "mixedSpectralFailureModes": dict(failures),
        },
        "positiveAdvantageConcentration": {"byFamily": positive_by_family, "shareByFamily": shares, "maxFamilyShare": max_share},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = aggregate(_load_inputs(sorted(Path(args.input_root).rglob("*.json"))))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
