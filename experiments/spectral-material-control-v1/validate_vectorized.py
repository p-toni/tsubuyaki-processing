#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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
    max_point_delta,
    point_leaf_count,
    velocity_rms,
    velocity_rms_scalar,
    warp_geometry,
    warp_geometry_scalar,
)

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
TIMES = (30.0, 90.0, 150.0)
AMPLITUDES = (4.0, 12.0, 24.0)
MASTER_SEED = 98999
TOL = 2e-10


def valid_base(route: str) -> dict:
    version = str(core.ROUTES[route]["version"])
    rng = representation_rng(MASTER_SEED, route, version, "spectral-material-control-vector-equivalence")
    for _ in range(128):
        genome = core.ROUTES[route]["seed"](rng)
        checks = core.check_candidate(route, genome, TIMES, core.ROUTES[route]["geometry"], core.W, core.H)
        if checks.get("valid", False):
            return genome
    raise AssertionError(f"could not establish equivalence base for {route}")


def main() -> None:
    max_delta = 0.0
    max_rms_relative = 0.0
    rendered_exact = 0
    validity_exact = 0
    cases = 0

    for route in ROUTES:
        genome = valid_base(route)
        field_seed = derived_seed(MASTER_SEED, "spectral-material-control-vector-equivalence", route)
        field = frozen_field.random_field(2, field_seed)
        scalar_rms = velocity_rms_scalar(field)
        vector_rms = velocity_rms(field)
        rms_relative = abs(vector_rms - scalar_rms) / scalar_rms
        max_rms_relative = max(max_rms_relative, rms_relative)
        if rms_relative > 2e-14:
            raise AssertionError(f"RMS equivalence failed for {route}: {rms_relative}")

        for amplitude in AMPLITUDES:
            for t in TIMES:
                native = core.ROUTES[route]["geometry"](genome, t)
                reference = warp_geometry_scalar(field, native, amplitude, core.W, core.H, rms=scalar_rms)
                vectorized = warp_geometry(field, native, amplitude, core.W, core.H, rms=vector_rms)
                if point_leaf_count(reference) != point_leaf_count(vectorized):
                    raise AssertionError(f"topology drift for {route}/{amplitude}/{t}")
                delta = max_point_delta(reference, vectorized)
                max_delta = max(max_delta, delta)
                if delta > TOL:
                    raise AssertionError(f"point equivalence failed for {route}/{amplitude}/{t}: {delta}")
                alpha = int(genome.get("alpha", 48))
                ref_image = core.draw_points(reference["all"], alpha)
                vec_image = core.draw_points(vectorized["all"], alpha)
                if ref_image.tobytes() != vec_image.tobytes():
                    raise AssertionError(f"render equivalence failed for {route}/{amplitude}/{t}")
                rendered_exact += 1
                cases += 1

            def scalar_geometry_fn(g, t, *, _route=route, _field=field, _amp=amplitude, _rms=scalar_rms):
                native = core.ROUTES[_route]["geometry"](g, t)
                return warp_geometry_scalar(_field, native, _amp, core.W, core.H, rms=_rms)

            def vector_geometry_fn(g, t, *, _route=route, _field=field, _amp=amplitude, _rms=vector_rms):
                native = core.ROUTES[_route]["geometry"](g, t)
                return warp_geometry(_field, native, _amp, core.W, core.H, rms=_rms)

            scalar_checks = core.check_candidate(route, genome, TIMES, scalar_geometry_fn, core.W, core.H)
            vector_checks = core.check_candidate(route, genome, TIMES, vector_geometry_fn, core.W, core.H)
            if bool(scalar_checks.get("valid")) != bool(vector_checks.get("valid")):
                raise AssertionError(f"validity equivalence failed for {route}/{amplitude}")
            if list(scalar_checks.get("failures", [])) != list(vector_checks.get("failures", [])):
                raise AssertionError(f"failure-set equivalence failed for {route}/{amplitude}")
            validity_exact += 1

    print(
        {
            "decision": "VECTOR_WARP_EQUIVALENT",
            "cases": cases,
            "renderedExact": rendered_exact,
            "validityExact": validity_exact,
            "maxPointDelta": max_delta,
            "maxRmsRelativeDifference": max_rms_relative,
            "tolerance": TOL,
        }
    )


if __name__ == "__main__":
    main()
