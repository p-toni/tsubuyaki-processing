from __future__ import annotations

import math
from numbers import Real
from typing import Any, Iterable

import numpy as np


_TWO_PI = 2.0 * math.pi


def value_and_gradient(field, x: float, y: float) -> tuple[float, float, float]:
    """Scalar reference evaluation of F, dF/dx, dF/dy for the frozen basis."""
    coefficients = np.asarray(field.coefficients, dtype=float)
    value = float(coefficients[0])
    dx = 0.0
    dy = 0.0
    offset = 1
    for kx, ky in field.support:
        a = float(coefficients[offset])
        b = float(coefficients[offset + 1])
        offset += 2
        theta = _TWO_PI * (kx * x + ky * y)
        c = math.cos(theta)
        s = math.sin(theta)
        value += a * c + b * s
        common = -a * s + b * c
        dx += _TWO_PI * kx * common
        dy += _TWO_PI * ky * common
    return value, dx, dy


def value_and_gradient_many(field, xy: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized equivalent of value_and_gradient for an N×2 coordinate matrix."""
    coords = np.asarray(xy, dtype=float)
    if coords.ndim != 2 or coords.shape[1] != 2:
        raise ValueError("xy must have shape (N,2)")
    if len(coords) == 0:
        empty = np.empty(0, dtype=float)
        return empty, empty, empty

    coefficients = np.asarray(field.coefficients, dtype=float)
    support = np.asarray(field.support, dtype=float)
    kx = support[:, 0]
    ky = support[:, 1]
    a = coefficients[1::2]
    b = coefficients[2::2]
    if not (len(kx) == len(a) == len(b)):
        raise AssertionError("spectral coefficient/support accounting drift")

    theta = _TWO_PI * (
        coords[:, 0, None] * kx[None, :] + coords[:, 1, None] * ky[None, :]
    )
    c = np.cos(theta)
    s = np.sin(theta)
    value = coefficients[0] + c @ a + s @ b
    common = -s * a[None, :] + c * b[None, :]
    dx = _TWO_PI * (common @ kx)
    dy = _TWO_PI * (common @ ky)
    return value, dx, dy


def hamiltonian_velocity(field, x: float, y: float) -> tuple[float, float]:
    """J grad(F^2): sign-invariant and divergence-free in the analytic field."""
    value, dx, dy = value_and_gradient(field, x, y)
    return 2.0 * value * dy, -2.0 * value * dx


def hamiltonian_velocity_many(field, xy: np.ndarray) -> np.ndarray:
    value, dx, dy = value_and_gradient_many(field, xy)
    return np.column_stack((2.0 * value * dy, -2.0 * value * dx))


def velocity_rms_scalar(field, grid: int = 65) -> float:
    """Frozen scalar reference used only for equivalence validation."""
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


def velocity_rms(field, grid: int = 65) -> float:
    if grid < 3:
        raise ValueError("grid must be >= 3")
    axis = (np.arange(grid, dtype=float) + 0.5) / grid
    xx, yy = np.meshgrid(axis, axis)
    coords = np.column_stack((xx.ravel(), yy.ravel()))
    velocity = hamiltonian_velocity_many(field, coords)
    rms = float(np.sqrt(np.mean(np.sum(velocity * velocity, axis=1))))
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
    """Scalar reference warp for one point."""
    x, y = float(point[0]), float(point[1])
    if amplitude == 0:
        return x, y
    scale = velocity_rms(field) if rms is None else float(rms)
    vx, vy = hamiltonian_velocity(field, x / width, y / height)
    return x + amplitude * vx / scale, y + amplitude * vy / scale


def warp_points(
    field,
    points: Iterable[tuple[float, float]],
    amplitude: float,
    width: int = 400,
    height: int = 400,
    *,
    rms: float | None = None,
) -> list[tuple[float, float]]:
    points_list = [(float(x), float(y)) for x, y in points]
    if not points_list:
        return []
    if amplitude == 0:
        return points_list
    scale = velocity_rms(field) if rms is None else float(rms)
    xy = np.asarray(points_list, dtype=float)
    normalized = np.column_stack((xy[:, 0] / width, xy[:, 1] / height))
    velocity = hamiltonian_velocity_many(field, normalized)
    warped = xy + (float(amplitude) / scale) * velocity
    return [(float(x), float(y)) for x, y in warped]


def _is_point(value: Any) -> bool:
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and all(isinstance(v, Real) for v in value)
    )


def _point_leaves(value: Any, out: list[tuple[float, float]]) -> None:
    if _is_point(value):
        out.append((float(value[0]), float(value[1])))
        return
    if isinstance(value, dict):
        for child in value.values():
            _point_leaves(child, out)
        return
    if isinstance(value, (list, tuple)):
        for child in value:
            _point_leaves(child, out)


def _replace_point_leaves(value: Any, points_iter):
    if _is_point(value):
        return next(points_iter)
    if isinstance(value, list):
        return [_replace_point_leaves(v, points_iter) for v in value]
    if isinstance(value, tuple):
        return tuple(_replace_point_leaves(v, points_iter) for v in value)
    if isinstance(value, dict):
        return {k: _replace_point_leaves(v, points_iter) for k, v in value.items()}
    return value


def warp_geometry_scalar(
    field,
    geometry: Any,
    amplitude: float,
    width: int = 400,
    height: int = 400,
    *,
    rms: float | None = None,
):
    """Original point-by-point implementation retained as an equivalence oracle."""
    scale = velocity_rms_scalar(field) if rms is None else float(rms)

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


def warp_geometry(
    field,
    geometry: Any,
    amplitude: float,
    width: int = 400,
    height: int = 400,
    *,
    rms: float | None = None,
):
    """Preserve geometry topology while vectorizing all point-leaf field evaluations."""
    leaves: list[tuple[float, float]] = []
    _point_leaves(geometry, leaves)
    scale = velocity_rms(field) if rms is None else float(rms)
    warped = warp_points(field, leaves, amplitude, width, height, rms=scale)
    iterator = iter(warped)
    result = _replace_point_leaves(geometry, iterator)
    try:
        next(iterator)
    except StopIteration:
        return result
    raise AssertionError("unused warped points after geometry reconstruction")


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
