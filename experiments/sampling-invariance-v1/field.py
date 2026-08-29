from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


Point = tuple[float, float]


def positive_half_support(bandwidth: int) -> tuple[tuple[int, int], ...]:
    if bandwidth < 1:
        raise ValueError("bandwidth must be >= 1")
    out: list[tuple[int, int]] = []
    for ky in range(-bandwidth, bandwidth + 1):
        for kx in range(-bandwidth, bandwidth + 1):
            if kx == 0 and ky == 0:
                continue
            if ky > 0 or (ky == 0 and kx > 0):
                out.append((kx, ky))
    expected = (2 * bandwidth + 1) ** 2
    if 1 + 2 * len(out) != expected:
        raise AssertionError("real half-support accounting drifted")
    return tuple(out)


def coefficient_dimension(bandwidth: int) -> int:
    return (2 * bandwidth + 1) ** 2


@dataclass(frozen=True)
class BandlimitedField:
    bandwidth: int
    coefficients: np.ndarray

    def __post_init__(self) -> None:
        coeff = np.asarray(self.coefficients, dtype=float)
        expected = coefficient_dimension(self.bandwidth)
        if coeff.shape != (expected,):
            raise ValueError(f"expected {expected} coefficients, got {coeff.shape}")
        if not np.all(np.isfinite(coeff)):
            raise ValueError("coefficients must be finite")
        if np.linalg.norm(coeff) <= 1e-15:
            raise ValueError("zero coefficient vector has no defined projective geometry")
        object.__setattr__(self, "coefficients", coeff)

    @property
    def support(self) -> tuple[tuple[int, int], ...]:
        return positive_half_support(self.bandwidth)

    @property
    def coefficient_dof(self) -> int:
        return len(self.coefficients)

    @property
    def geometry_dof(self) -> int:
        return self.coefficient_dof - 1

    def basis_row(self, x: float, y: float) -> np.ndarray:
        values = [1.0]
        for kx, ky in self.support:
            theta = 2.0 * math.pi * (kx * x + ky * y)
            values.extend((math.cos(theta), math.sin(theta)))
        return np.asarray(values, dtype=float)

    def value(self, x: float, y: float) -> float:
        return float(self.basis_row(x, y) @ self.coefficients)

    def normalized(self) -> "BandlimitedField":
        norm = float(np.linalg.norm(self.coefficients))
        return BandlimitedField(self.bandwidth, self.coefficients / norm)

    def scaled(self, factor: float) -> "BandlimitedField":
        if abs(factor) <= 1e-15:
            raise ValueError("scale must be nonzero")
        return BandlimitedField(self.bandwidth, self.coefficients * factor)


@dataclass(frozen=True)
class Reconstruction:
    field: BandlimitedField
    rank: int
    nullity: int
    singular_values: tuple[float, ...]


def random_field(bandwidth: int, seed: int) -> BandlimitedField:
    rng = np.random.default_rng(seed)
    dimension = coefficient_dimension(bandwidth)
    for _ in range(128):
        coefficients = rng.normal(size=dimension)
        coefficients[0] *= 0.25
        coefficients /= np.linalg.norm(coefficients)
        field = BandlimitedField(bandwidth, coefficients)
        probe = [field.value(i / 24.0, j / 24.0) for i in range(24) for j in range(24)]
        if min(probe) < -0.05 and max(probe) > 0.05:
            return field
    raise RuntimeError("failed to draw a nondegenerate zero-crossing field")


def coefficient_similarity(a: BandlimitedField, b: BandlimitedField) -> float:
    if a.bandwidth != b.bandwidth:
        raise ValueError("bandwidth mismatch")
    denom = float(np.linalg.norm(a.coefficients) * np.linalg.norm(b.coefficients))
    return abs(float(a.coefficients @ b.coefficients) / denom)


def reconstruct_from_zero_points(bandwidth: int, points: Sequence[Point]) -> Reconstruction:
    if not points:
        raise ValueError("at least one point is required")
    template = BandlimitedField(
        bandwidth,
        np.r_[1.0, np.zeros(coefficient_dimension(bandwidth) - 1)],
    )
    matrix = np.stack([template.basis_row(x, y) for x, y in points])
    _, singular_values, vh = np.linalg.svd(matrix, full_matrices=True)
    rank = int(np.linalg.matrix_rank(matrix))
    nullity = coefficient_dimension(bandwidth) - rank
    estimate = vh[-1]
    estimate /= np.linalg.norm(estimate)
    return Reconstruction(
        field=BandlimitedField(bandwidth, estimate),
        rank=rank,
        nullity=nullity,
        singular_values=tuple(float(v) for v in singular_values),
    )


def _bisect_root(
    fn,
    left: float,
    right: float,
    f_left: float,
    f_right: float,
    iterations: int = 52,
) -> float | None:
    if f_left == 0.0:
        return left
    if f_right == 0.0:
        return right
    if f_left * f_right > 0.0:
        return None
    for _ in range(iterations):
        mid = 0.5 * (left + right)
        f_mid = fn(mid)
        if f_mid == 0.0:
            return mid
        if f_left * f_mid <= 0.0:
            right, f_right = mid, f_mid
        else:
            left, f_left = mid, f_mid
    return 0.5 * (left + right)


def _horizontal_roots(
    field: BandlimitedField,
    y: float,
    scan_steps: int,
    phase: float,
) -> list[Point]:
    xs = [(i + phase) / scan_steps for i in range(scan_steps + 1)]
    values = [field.value(x, y) for x in xs]
    out: list[Point] = []
    for i in range(scan_steps):
        left, right = xs[i], xs[i + 1]
        f_left, f_right = values[i], values[i + 1]
        if f_left == 0.0 or f_right == 0.0 or f_left * f_right < 0.0:
            root = _bisect_root(lambda x: field.value(x, y), left, right, f_left, f_right)
            if root is not None:
                out.append((root % 1.0, y % 1.0))
    return out


def _vertical_roots(
    field: BandlimitedField,
    x: float,
    scan_steps: int,
    phase: float,
) -> list[Point]:
    ys = [(i + phase) / scan_steps for i in range(scan_steps + 1)]
    values = [field.value(x, y) for y in ys]
    out: list[Point] = []
    for i in range(scan_steps):
        left, right = ys[i], ys[i + 1]
        f_left, f_right = values[i], values[i + 1]
        if f_left == 0.0 or f_right == 0.0 or f_left * f_right < 0.0:
            root = _bisect_root(lambda y: field.value(x, y), left, right, f_left, f_right)
            if root is not None:
                out.append((x % 1.0, root % 1.0))
    return out


def _dedupe(points: Iterable[Point], digits: int = 12) -> list[Point]:
    unique: dict[tuple[float, float], Point] = {}
    for x, y in points:
        unique[(round(x, digits), round(y, digits))] = (float(x), float(y))
    return list(unique.values())


def regular_line_zero_samples(
    field: BandlimitedField,
    line_count: int = 32,
    scan_steps: int = 128,
    line_shift: float = 0.37,
) -> list[Point]:
    points: list[Point] = []
    for index in range(line_count):
        y = ((index + line_shift) / line_count) % 1.0
        points.extend(_horizontal_roots(field, y, scan_steps, phase=0.23))
    for index in range(line_count):
        x = ((index + line_shift) / line_count) % 1.0
        points.extend(_vertical_roots(field, x, scan_steps, phase=0.41))
    return _dedupe(points)


def irregular_line_zero_samples(
    field: BandlimitedField,
    seed: int,
    line_count: int = 32,
    scan_steps: int = 128,
) -> list[Point]:
    rng = np.random.default_rng(seed)
    points: list[Point] = []
    for y in rng.random(line_count):
        points.extend(_horizontal_roots(field, float(y), scan_steps, phase=float(rng.random())))
    for x in rng.random(line_count):
        points.extend(_vertical_roots(field, float(x), scan_steps, phase=float(rng.random())))
    return _dedupe(points)


def deterministic_subset(points: Sequence[Point], count: int, seed: int) -> list[Point]:
    if len(points) < count:
        raise ValueError(f"need {count} points, only have {len(points)}")
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(points), size=count, replace=False)
    return [points[int(i)] for i in indices]


def perturb_points(points: Sequence[Point], sigma: float, seed: int) -> list[Point]:
    rng = np.random.default_rng(seed)
    return [
        (
            (x + float(rng.normal(0.0, sigma))) % 1.0,
            (y + float(rng.normal(0.0, sigma))) % 1.0,
        )
        for x, y in points
    ]


def symmetric_chamfer(
    a: Sequence[Point],
    b: Sequence[Point],
    max_points: int = 512,
) -> float:
    if not a or not b:
        return float("inf")

    def thin(points: Sequence[Point]) -> np.ndarray:
        if len(points) <= max_points:
            return np.asarray(points, dtype=float)
        indices = np.linspace(0, len(points) - 1, max_points, dtype=int)
        return np.asarray([points[int(i)] for i in indices], dtype=float)

    aa = thin(a)
    bb = thin(b)
    distances = np.sqrt(np.sum((aa[:, None, :] - bb[None, :, :]) ** 2, axis=2))
    return float(0.5 * (distances.min(axis=1).mean() + distances.min(axis=0).mean()))


def reference_zero_cloud(field: BandlimitedField) -> list[Point]:
    return regular_line_zero_samples(
        field,
        line_count=64,
        scan_steps=192,
        line_shift=0.11,
    )
