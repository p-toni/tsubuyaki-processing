#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image

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
from spectral_control import velocity_rms, warp_geometry
import fast_grayscale_metric as fast

REFERENCE_PATH = ROOT / "experiments" / "search-measurement-geometry-v1" / "audit.py"
spec = importlib.util.spec_from_file_location("spectral_material_control_reference_metric", REFERENCE_PATH)
reference = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(reference)

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
TIMES = (30.0, 90.0, 150.0)
MASTER_SEED = 98997
TOL = 1e-12


def compare(a, b, path="root") -> float:
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            raise AssertionError(f"key mismatch at {path}: {a.keys()} != {b.keys()}")
        return max((compare(a[k], b[k], f"{path}.{k}") for k in a), default=0.0)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        delta = abs(float(a) - float(b))
        if delta > TOL:
            raise AssertionError(f"numeric mismatch at {path}: {a} != {b} (delta={delta})")
        return delta
    if a != b:
        raise AssertionError(f"value mismatch at {path}: {a!r} != {b!r}")
    return 0.0


def synthetic_image(seed: int) -> Image.Image:
    rng = random.Random(seed)
    data = np.full((400, 400), 9, dtype=np.uint8)
    # Mix sub-threshold haze, sparse strokes, overlap-like bright points, and clipped edges.
    for _ in range(700):
        x = rng.randrange(400)
        y = rng.randrange(400)
        data[y, x] = rng.randrange(10, 256)
    for _ in range(6):
        x0 = rng.randrange(-20, 380)
        y0 = rng.randrange(-20, 380)
        w = rng.randrange(2, 45)
        h = rng.randrange(2, 45)
        value = rng.randrange(10, 256)
        xa, xb = max(0, x0), min(400, x0 + w)
        ya, yb = max(0, y0), min(400, y0 + h)
        if xa < xb and ya < yb:
            data[ya:yb, xa:xb] = np.maximum(data[ya:yb, xa:xb], value)
    return Image.fromarray(data, mode="L")


def shifted(image: Image.Image, dx: int, dy: int) -> Image.Image:
    out = Image.new("L", image.size, 9)
    out.paste(image, (dx, dy))
    return out


def valid_base(route: str) -> dict:
    version = str(core.ROUTES[route]["version"])
    rng = representation_rng(MASTER_SEED, route, version, "spectral-material-control-metric-equivalence")
    for _ in range(128):
        genome = core.ROUTES[route]["seed"](rng)
        checks = core.check_candidate(route, genome, TIMES, core.ROUTES[route]["geometry"], core.W, core.H)
        if checks.get("valid", False):
            return genome
    raise AssertionError(f"could not establish metric-equivalence base for {route}")


def main() -> None:
    maximum = 0.0
    cases = 0

    blank = Image.new("L", (400, 400), 9)
    synthetic = [blank] + [synthetic_image(7000 + i) for i in range(12)]
    pairs = []
    for index, image in enumerate(synthetic):
        pairs.append((image, image.copy()))
        pairs.append((shifted(image, 3, 0), image))
        pairs.append((shifted(image, -5, 4), image))
        if index + 1 < len(synthetic):
            pairs.append((image, synthetic[index + 1]))
    for candidate, target in pairs:
        expected = reference.sparse_geometry_distance((candidate,), (target,))
        observed = fast.sparse_geometry_distance((candidate,), (target,))
        maximum = max(maximum, compare(expected, observed))
        cases += 1

    for route in ROUTES:
        genome = valid_base(route)
        field_seed = derived_seed(MASTER_SEED, "spectral-material-control-metric-equivalence", route)
        field = frozen_field.random_field(2, field_seed)
        rms = velocity_rms(field)
        native = core.ROUTES[route]["geometry"](genome, 90.0)
        base_image = core.draw_points(native["all"], int(genome.get("alpha", 48)))
        for amplitude in (4.0, 12.0, 24.0):
            warped = warp_geometry(field, native, amplitude, core.W, core.H, rms=rms)
            candidate = core.draw_points(warped["all"], int(genome.get("alpha", 48)))
            expected = reference.sparse_geometry_distance((candidate,), (base_image,))
            observed = fast.sparse_geometry_distance((candidate,), (base_image,))
            maximum = max(maximum, compare(expected, observed))
            cases += 1

    print({"decision": "FAST_GRAYSCALE_METRIC_EQUIVALENT", "cases": cases, "maxAbsoluteDifference": maximum, "tolerance": TOL})


if __name__ == "__main__":
    main()
