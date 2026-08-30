"""Opt-in spectral material control for intrinsic-1D discovery routes.

The runtime representation remains the incumbent route/genome. A material-control
record is stored under a reserved genome key so spectral phenotypes are replayable
without inventing a new route. Native genomes remain byte-for-byte structurally
unchanged when the feature is not used.
"""
from __future__ import annotations

import copy
import math
from numbers import Real
from typing import Any

import numpy as np

CONTROL_KEY = "_material_control"
CONTROL_TYPE = "spectral-hamiltonian-k2-v1"
BANDWIDTH = 2
AMPLITUDE = 16.0
_TWO_PI = 2.0 * math.pi


def _support(bandwidth: int = BANDWIDTH) -> tuple[tuple[int, int], ...]:
    out = []
    for ky in range(-bandwidth, bandwidth + 1):
        for kx in range(-bandwidth, bandwidth + 1):
            if kx == 0 and ky == 0:
                continue
            if ky > 0 or (ky == 0 and kx > 0):
                out.append((kx, ky))
    return tuple(out)


def _native_genome(genome: dict) -> dict:
    if CONTROL_KEY not in genome:
        return genome
    out = dict(genome)
    out.pop(CONTROL_KEY, None)
    return out


def has_control(genome: dict) -> bool:
    return CONTROL_KEY in genome


def control_record(genome: dict) -> dict | None:
    value = genome.get(CONTROL_KEY)
    return dict(value) if isinstance(value, dict) else None


def _field_values(coefficients: np.ndarray, xy: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    support = np.asarray(_support(), dtype=float)
    kx = support[:, 0]; ky = support[:, 1]
    a = coefficients[1::2]; b = coefficients[2::2]
    theta = _TWO_PI * (xy[:, 0, None] * kx[None, :] + xy[:, 1, None] * ky[None, :])
    c = np.cos(theta); s = np.sin(theta)
    value = coefficients[0] + c @ a + s @ b
    common = -s * a[None, :] + c * b[None, :]
    dx = _TWO_PI * (common @ kx)
    dy = _TWO_PI * (common @ ky)
    return value, dx, dy


def _velocity_rms(coefficients: np.ndarray, grid: int = 65) -> float:
    axis = (np.arange(grid, dtype=float) + 0.5) / grid
    xx, yy = np.meshgrid(axis, axis)
    xy = np.column_stack((xx.ravel(), yy.ravel()))
    value, dx, dy = _field_values(coefficients, xy)
    vx = 2.0 * value * dy; vy = -2.0 * value * dx
    rms = float(np.sqrt(np.mean(vx * vx + vy * vy)))
    if not math.isfinite(rms) or rms <= 1e-12:
        raise ValueError("degenerate spectral-control velocity field")
    return rms


def _draw_control(seed: int) -> dict:
    rng = np.random.default_rng(int(seed))
    dimension = (2 * BANDWIDTH + 1) ** 2
    probe_axis = np.arange(24, dtype=float) / 24.0
    px, py = np.meshgrid(probe_axis, probe_axis)
    probe_xy = np.column_stack((px.ravel(), py.ravel()))
    for _ in range(128):
        coefficients = rng.normal(size=dimension)
        coefficients[0] *= 0.25
        coefficients /= np.linalg.norm(coefficients)
        values, _, _ = _field_values(coefficients, probe_xy)
        if float(values.min()) < -0.05 and float(values.max()) > 0.05:
            return {
                "type": CONTROL_TYPE,
                "bandwidth": BANDWIDTH,
                "amplitude": AMPLITUDE,
                "fieldSeed": int(seed),
                "coefficients": [float(v) for v in coefficients],
                "velocityRms": _velocity_rms(coefficients),
            }
    raise RuntimeError("failed to draw nondegenerate runtime spectral field")


def with_spectral_control(genome: dict, seed: int) -> dict:
    out = copy.deepcopy(_native_genome(genome))
    out[CONTROL_KEY] = _draw_control(seed)
    return out


def mutate_native(route_spec: dict, genome: dict, rng, scale: float) -> dict:
    """Mutate grammar parameters while preserving an already-selected material field."""
    existing = control_record(genome)
    child = route_spec["mutate"](_native_genome(genome), rng, scale)
    if existing is not None:
        child[CONTROL_KEY] = existing
    return child


def _is_point(value: Any) -> bool:
    return isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, Real) for v in value)


def _leaves(value: Any, out: list[tuple[float, float]]) -> None:
    if _is_point(value):
        out.append((float(value[0]), float(value[1]))); return
    if isinstance(value, dict):
        for child in value.values(): _leaves(child, out)
    elif isinstance(value, (list, tuple)):
        for child in value: _leaves(child, out)


def _replace(value: Any, it):
    if _is_point(value): return next(it)
    if isinstance(value, list): return [_replace(v, it) for v in value]
    if isinstance(value, tuple): return tuple(_replace(v, it) for v in value)
    if isinstance(value, dict): return {k: _replace(v, it) for k, v in value.items()}
    return value


def _warp_geometry(geometry: Any, record: dict, width: int, height: int):
    if record.get("type") != CONTROL_TYPE or int(record.get("bandwidth", -1)) != BANDWIDTH:
        raise ValueError("unsupported material-control record")
    coefficients = np.asarray(record["coefficients"], dtype=float)
    if coefficients.shape != ((2 * BANDWIDTH + 1) ** 2,):
        raise ValueError("spectral coefficient dimension drift")
    points: list[tuple[float, float]] = []
    _leaves(geometry, points)
    if not points: return geometry
    xy = np.asarray(points, dtype=float)
    normalized = np.column_stack((xy[:, 0] / width, xy[:, 1] / height))
    value, dx, dy = _field_values(coefficients, normalized)
    velocity = np.column_stack((2.0 * value * dy, -2.0 * value * dx))
    rms = float(record["velocityRms"])
    warped = xy + (float(record["amplitude"]) / rms) * velocity
    it = iter((float(x), float(y)) for x, y in warped)
    result = _replace(geometry, it)
    try: next(it)
    except StopIteration: return result
    raise AssertionError("unused warped points")


def candidate_geometry(route_spec: dict, genome: dict, t: float, width: int, height: int):
    base = _native_genome(genome)
    geometry = route_spec["geometry"](base, t)
    record = control_record(genome)
    if record is None:
        return geometry
    if int(route_spec.get("intrinsic_dimension", -1)) != 1:
        raise ValueError("spectral material control is restricted to intrinsic-1D routes")
    return _warp_geometry(geometry, record, width, height)


def candidate_points(route_spec: dict, genome: dict, t: float, width: int, height: int):
    if not has_control(genome):
        return route_spec["render"](genome, t)
    return candidate_geometry(route_spec, genome, t, width, height)["all"]
