#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
FIELD_DIR = ROOT / "experiments" / "sampling-invariance-v1"
CONTROL_DIR = ROOT / "experiments" / "spectral-material-control-v1"
for path in (PROTO, FIELD_DIR, CONTROL_DIR):
    sys.path.insert(0, str(path))

import field as frozen_field
from orbit_representation import register_orbit
register_orbit()

import core
from rng_streams import derived_seed, representation_rng
from spectral_control import velocity_rms, warp_geometry
import fast_grayscale_metric as metric
from targets_portfolio import build_targets_portfolio

ROUTES = ("recurrence", "orbit", "filament")
EXCLUDED_ROUTES = ("family", "sheet")
TIMES = (30.0, 90.0, 150.0)
CANONICAL_TIME = 90.0
STARTS_PER_ROUTE = 2
BASELINE_NATIVE_PER_START = 6
MIXED_NATIVE_PER_START = 3
MIXED_SPECTRAL_PER_START = 3
TOTAL_CHALLENGERS_PER_ARM = 12
SPECTRAL_AMPLITUDE = 16.0
FIELD_BANDWIDTH = 2
MAX_START_ATTEMPTS = 128
SMOKE_SEED = 121999
MASTER_SEEDS = (
    122011, 122021, 122027, 122029, 122033, 122039,
    122041, 122051, 122053, 122069, 122081, 122099,
    122117, 122131, 122147, 122149, 122167, 122173,
    122201, 122203, 122207, 122209, 122219, 122231,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _topology_contract() -> bool:
    return (
        all(int(core.ROUTES[r]["intrinsic_dimension"]) == 1 for r in ROUTES)
        and all(int(core.ROUTES[r]["intrinsic_dimension"]) == 2 for r in EXCLUDED_ROUTES)
    )


def _native_valid(route: str, genome: dict) -> bool:
    return bool(core.check_candidate(route, genome, TIMES, core.ROUTES[route]["geometry"], core.W, core.H).get("valid", False))


def _render_native(route: str, genome: dict):
    geometry = core.ROUTES[route]["geometry"](genome, CANONICAL_TIME)
    return core.draw_points(geometry["all"], int(genome.get("alpha", 48)))


def _valid_starts(master_seed: int, route: str) -> tuple[list[dict], int]:
    version = str(core.ROUTES[route]["version"])
    rng = representation_rng(master_seed, route, version, "spectral-material-control-1d-portfolio-v1-starts")
    starts = []
    attempts = 0
    while len(starts) < STARTS_PER_ROUTE and attempts < MAX_START_ATTEMPTS:
        attempts += 1
        genome = core.ROUTES[route]["seed"](rng)
        if _native_valid(route, genome):
            starts.append(genome)
    if len(starts) != STARTS_PER_ROUTE:
        raise AssertionError(f"failed to establish starts for {master_seed}/{route}: {len(starts)} in {attempts}")
    return starts, attempts


def _baseline_native(master_seed: int, route: str, starts: list[dict]) -> list[dict]:
    version = str(core.ROUTES[route]["version"])
    records = []
    for start_index, base in enumerate(starts):
        rng = representation_rng(master_seed, route, version, f"spectral-material-control-1d-portfolio-v1-native-{start_index}")
        for challenger_index in range(BASELINE_NATIVE_PER_START):
            genome = core.ROUTES[route]["mutate"](base, rng, 1.0)
            valid = _native_valid(route, genome)
            records.append({
                "startIndex": start_index,
                "challengerIndex": challenger_index,
                "valid": valid,
                "image": _render_native(route, genome) if valid else None,
            })
    if len(records) != TOTAL_CHALLENGERS_PER_ARM:
        raise AssertionError("baseline native budget drift")
    return records


def _mixed_native_prefix(baseline_native: list[dict]) -> list[dict]:
    records = [r for r in baseline_native if int(r["challengerIndex"]) < MIXED_NATIVE_PER_START]
    if len(records) != STARTS_PER_ROUTE * MIXED_NATIVE_PER_START:
        raise AssertionError("mixed native prefix budget drift")
    return records


def _mixed_spectral(master_seed: int, route: str, starts: list[dict]) -> list[dict]:
    records = []
    for start_index, base in enumerate(starts):
        for challenger_index in range(MIXED_SPECTRAL_PER_START):
            field_seed = derived_seed(
                master_seed,
                "spectral-material-control-1d-portfolio-v1",
                "spectral",
                route,
                start_index,
                challenger_index,
            )
            field = frozen_field.random_field(FIELD_BANDWIDTH, field_seed)
            rms = velocity_rms(field)

            def geometry_fn(g, t, *, _route=route, _field=field, _rms=rms):
                native = core.ROUTES[_route]["geometry"](g, t)
                return warp_geometry(_field, native, SPECTRAL_AMPLITUDE, core.W, core.H, rms=_rms)

            checks = core.check_candidate(route, base, TIMES, geometry_fn, core.W, core.H)
            valid = bool(checks.get("valid", False))
            if valid:
                geometry = geometry_fn(base, CANONICAL_TIME)
                image = core.draw_points(geometry["all"], int(base.get("alpha", 48)))
            else:
                image = None
            records.append({
                "startIndex": start_index,
                "challengerIndex": challenger_index,
                "fieldSeed": field_seed,
                "valid": valid,
                "failures": list(checks.get("failures", [])),
                "image": image,
            })
    if len(records) != STARTS_PER_ROUTE * MIXED_SPECTRAL_PER_START:
        raise AssertionError("mixed spectral budget drift")
    return records


def _recovery(image, target_image) -> float:
    return 1.0 - float(metric.sparse_geometry_distance((image,), (target_image,))["distance"])


def run_seed(master_seed: int) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} is not frozen for this experiment")
    if not _topology_contract():
        raise AssertionError("intrinsic-dimension route class drift")

    # Build all operator archives before target construction/scoring.
    archives = {}
    for route in ROUTES:
        starts, start_attempts = _valid_starts(master_seed, route)
        base_images = [_render_native(route, genome) for genome in starts]
        baseline_native = _baseline_native(master_seed, route, starts)
        mixed_native = _mixed_native_prefix(baseline_native)
        mixed_spectral = _mixed_spectral(master_seed, route, starts)
        archives[route] = {
            "startAttempts": start_attempts,
            "starts": starts,
            "baseImages": base_images,
            "baselineNative": baseline_native,
            "mixedNative": mixed_native,
            "mixedSpectral": mixed_spectral,
        }

    targets = build_targets_portfolio()
    cells = []
    route_diagnostics = {}
    for route in ROUTES:
        archive = archives[route]
        base_images = archive["baseImages"]
        baseline_images = [r["image"] for r in archive["baselineNative"] if r["valid"]]
        mixed_native_images = [r["image"] for r in archive["mixedNative"] if r["valid"]]
        mixed_spectral_images = [r["image"] for r in archive["mixedSpectral"] if r["valid"]]
        route_diagnostics[route] = {
            "startAttempts": archive["startAttempts"],
            "sharedValidStarts": len(base_images),
            "baselineNativeAttempts": len(archive["baselineNative"]),
            "baselineNativeValid": len(baseline_images),
            "mixedNativeAttempts": len(archive["mixedNative"]),
            "mixedNativeValid": len(mixed_native_images),
            "mixedSpectralAttempts": len(archive["mixedSpectral"]),
            "mixedSpectralValid": len(mixed_spectral_images),
            "mixedSpectralFailureModes": sorted(
                failure
                for record in archive["mixedSpectral"]
                if not record["valid"]
                for failure in record.get("failures", [])
            ),
        }
        for target in targets:
            base_recovery = max(_recovery(image, target.image) for image in base_images)
            baseline_recovery = max([base_recovery] + [_recovery(image, target.image) for image in baseline_images])
            mixed_recovery = max(
                [base_recovery]
                + [_recovery(image, target.image) for image in mixed_native_images]
                + [_recovery(image, target.image) for image in mixed_spectral_images]
            )
            cells.append({
                "masterSeed": master_seed,
                "route": route,
                "targetId": target.id,
                "targetFamily": target.family,
                "baseRecovery": base_recovery,
                "baselineRecovery": baseline_recovery,
                "mixedRecovery": mixed_recovery,
                "baselineAdded": baseline_recovery - base_recovery,
                "mixedAdded": mixed_recovery - base_recovery,
                "delta": mixed_recovery - baseline_recovery,
            })

    hard = {
        "topologyClassExact": _topology_contract(),
        "routeSetExact": tuple(archives) == ROUTES,
        "cellCountExact": len(cells) == len(ROUTES) * len(targets),
        "twoSharedStartsEveryRoute": all(route_diagnostics[r]["sharedValidStarts"] == STARTS_PER_ROUTE for r in ROUTES),
        "baselineBudgetExact": all(route_diagnostics[r]["baselineNativeAttempts"] == TOTAL_CHALLENGERS_PER_ARM for r in ROUTES),
        "mixedBudgetExact": all(
            route_diagnostics[r]["mixedNativeAttempts"] + route_diagnostics[r]["mixedSpectralAttempts"] == TOTAL_CHALLENGERS_PER_ARM
            for r in ROUTES
        ),
        "commonNativePrefixExact": all(
            archive["mixedNative"] == [x for x in archive["baselineNative"] if int(x["challengerIndex"]) < MIXED_NATIVE_PER_START]
            for archive in archives.values()
        ),
        "targetSetExact": len(targets) == 15,
    }
    if not all(hard.values()):
        raise AssertionError(f"hard invariant failure: {hard}")

    return {
        "version": 1,
        "masterSeed": master_seed,
        "artisticEvidence": False,
        "settings": {
            "routes": list(ROUTES),
            "excludedRoutesByFrozenIntrinsicDimension": list(EXCLUDED_ROUTES),
            "times": list(TIMES),
            "canonicalTime": CANONICAL_TIME,
            "startsPerRoute": STARTS_PER_ROUTE,
            "totalChallengersPerArm": TOTAL_CHALLENGERS_PER_ARM,
            "baselineNativePerStart": BASELINE_NATIVE_PER_START,
            "mixedNativePerStart": MIXED_NATIVE_PER_START,
            "mixedSpectralPerStart": MIXED_SPECTRAL_PER_START,
            "nativeMutationScale": 1.0,
            "spectralAmplitude": SPECTRAL_AMPLITUDE,
            "fieldBandwidth": FIELD_BANDWIDTH,
            "metric": "sparse-geometry-v1-exact-fast-grayscale",
        },
        "hardInvariants": hard,
        "routeDiagnostics": route_diagnostics,
        "cells": cells,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run_seed(args.seed)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
