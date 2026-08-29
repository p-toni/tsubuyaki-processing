"""Fitness-independent phenotype descriptors for repertoire niches.

These descriptors intentionally remove translation and global scale before
measuring structure. They must not reuse diagnostic-score inputs such as raw
occupancy, canvas span, or centering; those belong to viability/composition,
not diversity identity.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import statistics
from typing import Iterable, Sequence

Point = tuple[float, float]
Frame = Sequence[Point]
DESCRIPTOR_VERSION = "structural-v1"
ANGULAR_BINS = 36
NICHE_BINS = 4


def _clamp01(value: float) -> float:
    return 0.0 if value < 0.0 else 1.0 if value > 1.0 else value


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * fraction))))
    return ordered[index]


def _standardize(points: Frame) -> tuple[list[Point], list[float]]:
    if not points:
        return [], []
    cx = statistics.fmean(p[0] for p in points)
    cy = statistics.fmean(p[1] for p in points)
    centered = [(x - cx, y - cy) for x, y in points]
    radii = [math.hypot(x, y) for x, y in centered]
    rms = math.sqrt(statistics.fmean(r * r for r in radii)) if radii else 0.0
    if rms <= 1e-12:
        return [(0.0, 0.0) for _ in centered], [0.0 for _ in radii]
    return [(x / rms, y / rms) for x, y in centered], [r / rms for r in radii]


def _frame_structure(points: Frame) -> dict[str, float]:
    standardized, radii = _standardize(points)
    if len(standardized) < 2:
        return {"anisotropy": 0.0, "central_void": 0.0, "radial_cv": 0.0, "angular_coverage": 0.0}

    vx = statistics.fmean(x * x for x, _ in standardized)
    vy = statistics.fmean(y * y for _, y in standardized)
    cov = statistics.fmean(x * y for x, y in standardized)
    trace = vx + vy
    disc = math.sqrt(max(0.0, (vx - vy) ** 2 + 4.0 * cov * cov))
    l1 = max(0.0, (trace + disc) / 2.0)
    l2 = max(0.0, (trace - disc) / 2.0)
    anisotropy = (l1 - l2) / max(1e-12, l1 + l2)

    median_radius = statistics.median(radii) if radii else 0.0
    central_void = _percentile(radii, 0.10) / median_radius if median_radius > 1e-12 else 0.0
    mean_radius = statistics.fmean(radii) if radii else 0.0
    radial_cv = statistics.pstdev(radii) / mean_radius if len(radii) > 1 and mean_radius > 1e-12 else 0.0

    occupied = set()
    for x, y in standardized:
        if abs(x) + abs(y) <= 1e-12:
            continue
        angle = (math.atan2(y, x) + math.pi) / (2.0 * math.pi)
        occupied.add(min(ANGULAR_BINS - 1, int(angle * ANGULAR_BINS)))
    angular_coverage = len(occupied) / ANGULAR_BINS

    return {
        "anisotropy": _clamp01(anisotropy),
        "central_void": _clamp01(central_void),
        "radial_cv": max(0.0, radial_cv),
        "angular_coverage": _clamp01(angular_coverage),
    }


def _shape_motion(a: Frame, b: Frame) -> float:
    sa, _ = _standardize(a)
    sb, _ = _standardize(b)
    n = min(len(sa), len(sb))
    if n == 0:
        return 0.0
    step = max(1, n // 512)
    displacement = statistics.fmean(
        math.hypot(sa[i][0] - sb[i][0], sa[i][1] - sb[i][1])
        for i in range(0, n, step)
    )
    # Monotone bounded transform: 0 is static after translation/scale removal;
    # increasingly large structural motion asymptotes toward 1.
    return _clamp01(1.0 - math.exp(-max(0.0, displacement)))


@dataclass(frozen=True)
class PhenotypeDescriptor:
    intrinsic_dimension: int
    anisotropy: float
    central_void: float
    radial_cv: float
    angular_coverage: float
    shape_motion: float
    version: str = DESCRIPTOR_VERSION

    def to_json(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, order=True)
class NicheKey:
    intrinsic_dimension: int
    anisotropy_bin: int
    central_void_bin: int
    motion_bin: int
    version: str = DESCRIPTOR_VERSION

    def to_json(self) -> dict[str, object]:
        return asdict(self)


def describe_frames(frames: Sequence[Frame], intrinsic_dimension: int) -> PhenotypeDescriptor:
    if intrinsic_dimension not in (1, 2):
        raise ValueError("intrinsic_dimension must be 1 or 2")
    if not frames or any(not frame for frame in frames):
        raise ValueError("phenotype descriptor requires non-empty frames")

    stats = [_frame_structure(frame) for frame in frames]
    motions = [_shape_motion(a, b) for a, b in zip(frames, frames[1:])]
    return PhenotypeDescriptor(
        intrinsic_dimension=intrinsic_dimension,
        anisotropy=statistics.fmean(s["anisotropy"] for s in stats),
        central_void=statistics.fmean(s["central_void"] for s in stats),
        radial_cv=statistics.fmean(s["radial_cv"] for s in stats),
        angular_coverage=statistics.fmean(s["angular_coverage"] for s in stats),
        shape_motion=statistics.fmean(motions) if motions else 0.0,
    )


def describe_genome(route: str, genome: dict[str, object], times: Iterable[float] | None = None) -> PhenotypeDescriptor:
    # Local import avoids creating a module cycle with core.py.
    from core import ROUTES, TIMES

    if route not in ROUTES:
        raise KeyError(f"route {route!r} is not registered")
    active_times = tuple(TIMES if times is None else times)
    frames = [ROUTES[route]["geometry"](genome, t)["all"] for t in active_times]
    return describe_frames(frames, int(ROUTES[route]["intrinsic_dimension"]))


def _bin01(value: float, bins: int = NICHE_BINS) -> int:
    if bins < 2:
        raise ValueError("niche bins must be >= 2")
    bounded = min(1.0 - 1e-12, max(0.0, value))
    return min(bins - 1, int(bounded * bins))


def niche_key(descriptor: PhenotypeDescriptor, bins: int = NICHE_BINS) -> NicheKey:
    """Map structure to a deliberately small fixed phenotype niche grid.

    Only three bounded structure axes define cells in v1. `radial_cv` and
    `angular_coverage` remain diagnostics so the first archive does not explode
    into a mostly empty high-dimensional grid.
    """
    return NicheKey(
        intrinsic_dimension=descriptor.intrinsic_dimension,
        anisotropy_bin=_bin01(descriptor.anisotropy, bins),
        central_void_bin=_bin01(descriptor.central_void, bins),
        motion_bin=_bin01(descriptor.shape_motion, bins),
    )
