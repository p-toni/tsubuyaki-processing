from __future__ import annotations

import math
from numbers import Real
from typing import Any

import numpy as np


def value_and_gradient(field, x: float, y: float) -> tuple[float, float, float]:
    """Evaluate F, dF/dx, dF/dy for the frozen real trigonometric basis."""
    coefficients = np.asarray(field.coefficients, dtype=float)
    value = float(coefficients[0])
    dx = 0.0
    dy = 0.0
    offset = 1
    for kx, ky in field.support:
        a = float(coefficients[offset])
        b = float(coefficients[offset + 1])
        offset += 2
        theta = 2.0 * math.pi * (kx * x + ky * y)
        c = math.cos(theta)
        s = math.sin(theta)
        value += a * c + b * s
        common = -a * s + b * c
        dx += 2.0 * math.pi * kx * common
        dy += 2.0 * math.pi * ky * common
    return value, dx, dy


def hamiltonian_velocity(field, x: float, y: float) -> tuple[float, float]:
    """J grad(F^2): sign-invariant and divergence-free in the analytic field."""
    value, dx, dy = value_and_gradient(field, x, y)
    return 2.0 * value * dy, -2.0 * value * dx


def velocity_rms(field, grid: int = 65) -> float:
    if grid < 3:
        raise ValueError("grid must be >= 3")
    energy = 0.0
    count = 0
    for j in range(grid):
        y = (j + 0.5) / grid
        for i in range(grid):
            x = (i + 0.5) / grid
            vx, vy = hamiltonian_velocity(field, x, y)
            energy += vx * vx + vy * vy
            count += 1
    rms = math.sqrt(energy / max(1, count))
    if not math.isfinite(rms) or rms <= 1e-12:
        raise ValueError("degenerate spectral-control velocity field")
    return rms


def warp_point(
    field,
    point: tuple[float, float],
    amplitude: float,
    width: int = 400,
    height: int = 400,
    *,
    rms: float | None = None,
) -> tuple[float, float]:
    x, y = float(point[0]), float(point[1])
    if amplitude == 0:
        return x, y
    scale = velocity_rms(field) if rms is None else float(rms)
    vx, vy = hamiltonian_velocity(field, x / width, y / height)
    return x + amplitude * vx / scale, y + amplitude * vy / scale


def _is_point(value: Any) -> bool:
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and all(isinstance(v, Real) for v in value)
    )


def warp_geometry(
    field,
    geometry: Any,
    amplitude: float,
    width: int = 400,
    height: int = 400,
    *,
    rms: float | None = None,
):
    """Recursively preserve geometry structure while warping every point leaf."""
    scale = velocity_rms(field) if rms is None else float(rms)

    def visit(value):
        if _is_point(value):
            return warp_point(field, value, amplitude, width, height, rms=scale)
        if isinstance(value, list):
            return [visit(v) for v in value]
        if isinstance(value, tuple):
            return tuple(visit(v) for v in value)
        if isinstance(value, dict):
            return {k: visit(v) for k, v in value.items()}
        return value

    return visit(geometry)


def point_leaf_count(value: Any) -> int:
    if _is_point(value):
        return 1
    if isinstance(value, dict):
        return sum(point_leaf_count(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return sum(point_leaf_count(v) for v in value)
    return 0


def max_point_delta(a: Any, b: Any) -> float:
    """Maximum Euclidean point delta across identically structured geometry."""
    if _is_point(a) and _is_point(b):
        return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))
    if isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys():
        return max((max_point_delta(a[k], b[k]) for k in a), default=0.0)
    if isinstance(a, (list, tuple)) and isinstance(b, type(a)) and len(a) == len(b):
        return max((max_point_delta(x, y) for x, y in zip(a, b)), default=0.0)
    if a == b:
        return 0.0
    raise AssertionError("geometry topology mismatch")


def all_points_finite(value: Any) -> bool:
    if _is_point(value):
        return all(math.isfinite(float(v)) for v in value)
    if isinstance(value, dict):
        return all(all_points_finite(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(all_points_finite(v) for v in value)
    return True
