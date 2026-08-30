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
from targets_1d import build_targets_1d

ROUTES = ("recurrence", "orbit", "filament")
EXCLUDED_ROUTES = ("family", "sheet")
TIMES = (30.0, 90.0, 150.0)
CANONICAL_TIME = 90.0
STARTS_PER_ROUTE = 2
CHALLENGERS_PER_START = 6
CHALLENGERS_PER_ARM = STARTS_PER_ROUTE * CHALLENGERS_PER_START
SPECTRAL_AMPLITUDE = 16.0
FIELD_BANDWIDTH = 2
MAX_START_ATTEMPTS = 128
SMOKE_SEED = 120999
MASTER_SEEDS = (
    121001, 121007, 121013, 121019, 121021, 121039,
    121061, 121063, 121067, 121081, 121123, 121139,
    121151, 121157, 121169, 121171, 121181, 121189,
    121229, 121259, 121267, 121271, 121283, 121291,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _topology_contract() -> bool:
    return (
        all(int(core.ROUTES[r]["intrinsic_dimension"]) == 1 for r in ROUTES)
        and all(int(core.ROUTES[r]["intrinsic_dimension"]) == 2 for r in EXCLUDED_ROUTES)
    )


def _native_valid(route: str, genome: dict) -> bool:
    checks = core.check_candidate(route, genome, TIMES, core.ROUTES[route]["geometry"], core.W, core.H)
    return bool(checks.get("valid", False))


def _render_native(route: str, genome: dict):
    geometry = core.ROUTES[route]["geometry"](genome, CANONICAL_TIME)
    return core.draw_points(geometry["all"], int(genome.get("alpha", 48)))


def _valid_starts(master_seed: int, route: str) -> tuple[list[dict], int]:
    version = str(core.ROUTES[route]["version"])
    rng = representation_rng(master_seed, route, version, "spectral-material-control-1d-confirmation-v1-starts")
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


def _native_challengers(master_seed: int, route: str, starts: list[dict]) -> list[dict]:
    version = str(core.ROUTES[route]["version"])
    records = []
    for start_index, base in enumerate(starts):
        rng = representation_rng(master_seed, route, version, f"spectral-material-control-1d-confirmation-v1-native-{start_index}")
        for challenger_index in range(CHALLENGERS_PER_START):
            genome = core.ROUTES[route]["mutate"](base, rng, 1.0)
            valid = _native_valid(route, genome)
            records.append({
                "startIndex": start_index,
                "challengerIndex": challenger_index,
                "valid": valid,
                "image": _render_native(route, genome) if valid else None,
            })
    if len(records) != CHALLENGERS_PER_ARM:
        raise AssertionError("native challenger budget drift")
    return records


def _spectral_challengers(master_seed: int, route: str, starts: list[dict]) -> list[dict]:
    records = []
    for start_index, base in enumerate(starts):
        for challenger_index in range(CHALLENGERS_PER_START):
            field_seed = derived_seed(
                master_seed,
                "spectral-material-control-1d-confirmation-v1",
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
    if len(records) != CHALLENGERS_PER_ARM:
        raise AssertionError("spectral challenger budget drift")
    return records


def _recovery(image, target_image) -> float:
    return 1.0 - float(metric.sparse_geometry_distance((image,), (target_image,))["distance"])


def run_seed(master_seed: int) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} is not frozen for this experiment")
    if not _topology_contract():
        raise AssertionError("intrinsic-dimension route class drift")

    # Generate every archive before target construction/scoring.
    archives = {}
    for route in ROUTES:
        starts, start_attempts = _valid_starts(master_seed, route)
        base_images = [_render_native(route, genome) for genome in starts]
        native = _native_challengers(master_seed, route, starts)
        spectral = _spectral_challengers(master_seed, route, starts)
        archives[route] = {
            "startAttempts": start_attempts,
            "starts": starts,
            "baseImages": base_images,
            "native": native,
            "spectral": spectral,
        }

    targets = build_targets_1d()
    cells = []
    route_diagnostics = {}
    for route in ROUTES:
        archive = archives[route]
        native_images = [r["image"] for r in archive["native"] if r["valid"]]
        spectral_images = [r["image"] for r in archive["spectral"] if r["valid"]]
        base_images = archive["baseImages"]
        route_diagnostics[route] = {
            "startAttempts": archive["startAttempts"],
            "sharedValidStarts": len(base_images),
            "nativeAttempts": len(archive["native"]),
            "nativeValid": len(native_images),
            "spectralAttempts": len(archive["spectral"]),
            "spectralValid": len(spectral_images),
            "spectralFailureModes": sorted(
                failure
                for record in archive["spectral"]
                if not record["valid"]
                for failure in record.get("failures", [])
            ),
        }
        for target in targets:
            base_recovery = max(_recovery(image, target.image) for image in base_images)
            native_recovery = max([base_recovery] + [_recovery(image, target.image) for image in native_images])
            spectral_recovery = max([base_recovery] + [_recovery(image, target.image) for image in spectral_images])
            cells.append({
                "masterSeed": master_seed,
                "route": route,
                "targetId": target.id,
                "targetFamily": target.family,
                "baseRecovery": base_recovery,
                "nativeRecovery": native_recovery,
                "spectralRecovery": spectral_recovery,
                "nativeAdded": native_recovery - base_recovery,
                "spectralAdded": spectral_recovery - base_recovery,
                "delta": spectral_recovery - native_recovery,
            })

    hard = {
        "topologyClassExact": _topology_contract(),
        "routeSetExact": tuple(archives) == ROUTES,
        "cellCountExact": len(cells) == len(ROUTES) * len(targets),
        "twoSharedStartsEveryRoute": all(route_diagnostics[r]["sharedValidStarts"] == STARTS_PER_ROUTE for r in ROUTES),
        "nativeBudgetExact": all(route_diagnostics[r]["nativeAttempts"] == CHALLENGERS_PER_ARM for r in ROUTES),
        "spectralBudgetExact": all(route_diagnostics[r]["spectralAttempts"] == CHALLENGERS_PER_ARM for r in ROUTES),
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
            "challengersPerStart": CHALLENGERS_PER_START,
            "challengersPerArm": CHALLENGERS_PER_ARM,
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
