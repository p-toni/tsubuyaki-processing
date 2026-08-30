#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
FIELD_DIR = ROOT / "experiments" / "sampling-invariance-v1"
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(FIELD_DIR))

import field as frozen_field
from orbit_representation import register_orbit

register_orbit()

import core
from rng_streams import derived_seed, representation_rng

from spectral_control import (
    all_points_finite,
    max_point_delta,
    point_leaf_count,
    velocity_rms,
    warp_geometry,
)

METRIC_PATH = ROOT / "experiments" / "search-measurement-geometry-v1" / "audit.py"
metric_spec = importlib.util.spec_from_file_location("spectral_material_control_metric", METRIC_PATH)
metric = importlib.util.module_from_spec(metric_spec)
assert metric_spec.loader is not None
metric_spec.loader.exec_module(metric)

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
MASTER_SEEDS = (99001, 99007, 99019, 99037)
AMPLITUDES = (4.0, 8.0, 12.0, 16.0, 24.0)
PAIRS_PER_ROUTE_SEED = 6
TIMES = (30.0, 90.0, 150.0)
CANONICAL_TIME = 90.0
MAX_BASE_ATTEMPTS = 128
INVARIANT_TOLERANCE = 1e-9


def _base_valid(route: str, genome: dict) -> bool:
    checks = core.check_candidate(
        route,
        genome,
        TIMES,
        core.ROUTES[route]["geometry"],
        core.W,
        core.H,
    )
    return bool(checks.get("valid", False))


def _valid_bases(master_seed: int, route: str) -> list[dict]:
    version = str(core.ROUTES[route]["version"])
    rng = representation_rng(
        master_seed,
        route,
        version,
        stream="spectral-material-control-v1-calibration",
    )
    out: list[dict] = []
    attempts = 0
    while len(out) < PAIRS_PER_ROUTE_SEED and attempts < MAX_BASE_ATTEMPTS:
        attempts += 1
        genome = core.ROUTES[route]["seed"](rng)
        if _base_valid(route, genome):
            out.append(genome)
    if len(out) != PAIRS_PER_ROUTE_SEED:
        raise AssertionError(
            f"failed to establish {PAIRS_PER_ROUTE_SEED} valid bases for {master_seed}/{route}: {len(out)} in {attempts} attempts"
        )
    return out


def _render(points, alpha: int):
    return core.draw_points(points, alpha)


def _invariants(field, geometry) -> dict[str, object]:
    rms = velocity_rms(field)
    zero = warp_geometry(field, geometry, 0.0, core.W, core.H, rms=rms)
    reference = warp_geometry(field, geometry, 24.0, core.W, core.H, rms=rms)
    variants = [
        field.scaled(-1.0),
        field.scaled(7.0),
        field.scaled(-3.0),
    ]
    variant_deltas = []
    for variant in variants:
        warped = warp_geometry(variant, geometry, 24.0, core.W, core.H)
        variant_deltas.append(max_point_delta(reference, warped))
    return {
        "zeroAmplitudeExact": max_point_delta(geometry, zero) == 0.0,
        "signScaleInvariant": max(variant_deltas, default=0.0) <= INVARIANT_TOLERANCE,
        "maxSignScaleDelta": max(variant_deltas, default=0.0),
        "pointLeafCountPreserved": point_leaf_count(reference) == point_leaf_count(geometry),
        "allFinite": all_points_finite(reference),
        "velocityRmsFinite": math.isfinite(rms) and rms > 1e-12,
    }


def run() -> dict:
    rows: list[dict] = []
    invariant_rows: list[dict] = []

    for master_seed in MASTER_SEEDS:
        for route in ROUTES:
            bases = _valid_bases(master_seed, route)
            for pair_index, genome in enumerate(bases):
                field_seed = derived_seed(
                    master_seed,
                    "spectral-material-control-v1",
                    route,
                    pair_index,
                )
                field = frozen_field.random_field(2, field_seed)
                base_geometry = core.ROUTES[route]["geometry"](genome, CANONICAL_TIME)
                invariants = _invariants(field, base_geometry)
                invariant_rows.append(
                    {
                        "masterSeed": master_seed,
                        "route": route,
                        "pairIndex": pair_index,
                        "fieldSeed": field_seed,
                        **invariants,
                    }
                )
                rms = velocity_rms(field)
                base_image = _render(base_geometry["all"], int(genome.get("alpha", 48)))

                for amplitude in AMPLITUDES:
                    def warped_geometry_fn(g, t, *, _field=field, _amplitude=amplitude, _rms=rms, _route=route):
                        native = core.ROUTES[_route]["geometry"](g, t)
                        return warp_geometry(_field, native, _amplitude, core.W, core.H, rms=_rms)

                    checks = core.check_candidate(
                        route,
                        genome,
                        TIMES,
                        warped_geometry_fn,
                        core.W,
                        core.H,
                    )
                    warped_geometry = warped_geometry_fn(genome, CANONICAL_TIME)
                    warped_image = _render(warped_geometry["all"], int(genome.get("alpha", 48)))
                    distance = metric.sparse_geometry_distance((warped_image,), (base_image,))["distance"]
                    diagnostics = checks.get("diagnostics", {})
                    in_frame = diagnostics.get("inFrameFractionByFrame")
                    if not isinstance(in_frame, list):
                        in_frame = diagnostics.get("inFrameByFrame")
                    rows.append(
                        {
                            "masterSeed": master_seed,
                            "route": route,
                            "pairIndex": pair_index,
                            "fieldSeed": field_seed,
                            "amplitude": amplitude,
                            "valid": bool(checks.get("valid", False)),
                            "failures": list(checks.get("failures", [])),
                            "distanceFromBase": float(distance),
                            "inFrameDiagnostic": in_frame,
                        }
                    )

    invariant_gate = all(
        row["zeroAmplitudeExact"]
        and row["signScaleInvariant"]
        and row["pointLeafCountPreserved"]
        and row["allFinite"]
        and row["velocityRmsFinite"]
        for row in invariant_rows
    )

    summaries: dict[str, dict] = {}
    for amplitude in AMPLITUDES:
        group = [row for row in rows if row["amplitude"] == amplitude]
        route_valid = {}
        for route in ROUTES:
            route_rows = [row for row in group if row["route"] == route]
            route_valid[route] = sum(row["valid"] for row in route_rows) / len(route_rows)
        summaries[str(int(amplitude))] = {
            "amplitude": amplitude,
            "n": len(group),
            "pooledValidFraction": sum(row["valid"] for row in group) / len(group),
            "routeValidFraction": route_valid,
            "minRouteValidFraction": min(route_valid.values()),
            "medianDistanceFromBase": statistics.median(row["distanceFromBase"] for row in group),
            "meanDistanceFromBase": statistics.fmean(row["distanceFromBase"] for row in group),
        }

    eligible = [
        summary
        for summary in summaries.values()
        if invariant_gate
        and summary["pooledValidFraction"] >= 0.95
        and summary["minRouteValidFraction"] >= 0.90
        and 0.01 <= summary["medianDistanceFromBase"] <= 0.12
    ]
    selected = max((summary["amplitude"] for summary in eligible), default=None)
    if not invariant_gate:
        decision = "SPECTRAL_MATERIAL_CONTROL_INVALID"
    elif selected is None:
        decision = "SPECTRAL_MATERIAL_CONTROL_NOT_READY"
    else:
        decision = "SPECTRAL_MATERIAL_CONTROL_CALIBRATED"

    return {
        "version": 1,
        "decision": decision,
        "selectedAmplitude": selected,
        "population": {
            "masterSeeds": list(MASTER_SEEDS),
            "routes": list(ROUTES),
            "pairsPerRouteSeed": PAIRS_PER_ROUTE_SEED,
            "amplitudes": list(AMPLITUDES),
            "times": list(TIMES),
        },
        "invariantGate": invariant_gate,
        "maxSignScaleDelta": max((row["maxSignScaleDelta"] for row in invariant_rows), default=0.0),
        "amplitudeSummaries": summaries,
        "invariants": invariant_rows,
        "rows": rows,
    }


def main() -> None:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
