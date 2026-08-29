"""Fitness-independent phenotype descriptors for repertoire niches.

Cell-defining descriptors are computed from visible rendered support after removing
translation and global scale. They must not reuse route/representation metadata or
diagnostic-score inputs such as raw occupancy, canvas span, or centering.

The public `describe_frames` helper accepts point clouds for synthetic tests. The
production `describe_genome` path rasterizes through the exact prototype renderer
and then describes binary foreground support, so generator point density, alpha
intensity above the support threshold, and curve parameterization do not become
accidental diversity axes.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import statistics
from typing import Iterable, Sequence

from PIL import Image

Point = tuple[float, float]
Frame = Sequence[Point]
DESCRIPTOR_VERSION = "structural-v1"
ANGULAR_BINS = 36
NICHE_BINS = 4
SUPPORT_THRESHOLD = 20
MOTION_GRID = 32
MOTION_RADIUS_RMS = 3.0


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


def _shape_signature(points: Frame) -> frozenset[tuple[int, int]]:
    """Translation/scale-normalized occupied-cell signature.

    Using occupied cells rather than corresponding point indices makes temporal
    shape motion insensitive to point count, repeated samples, and parameterization
    speed along a curve. Rotation is intentionally *not* normalized away: coherent
    rotation is visible temporal behavior and may define a motion niche.
    """
    standardized, _ = _standardize(points)
    if not standardized:
        return frozenset()

    radius = MOTION_RADIUS_RMS
    cells: set[tuple[int, int]] = set()
    for x, y in standardized:
        x = max(-radius, min(radius, x))
        y = max(-radius, min(radius, y))
        gx = min(MOTION_GRID - 1, int(((x + radius) / (2.0 * radius)) * MOTION_GRID))
        gy = min(MOTION_GRID - 1, int(((y + radius) / (2.0 * radius)) * MOTION_GRID))
        cells.add((gx, gy))
    return frozenset(cells)


def _shape_motion(a: Frame, b: Frame) -> float:
    sa = _shape_signature(a)
    sb = _shape_signature(b)
    if not sa and not sb:
        return 0.0
    if not sa or not sb:
        return 1.0
    overlap = len(sa & sb)
    f1 = (2.0 * overlap) / (len(sa) + len(sb))
    return _clamp01(1.0 - f1)


def _support_points(image: Image.Image, threshold: int = SUPPORT_THRESHOLD) -> list[Point]:
    gray = image.convert("L")
    width, _height = gray.size
    return [
        (float(index % width), float(index // width))
        for index, value in enumerate(gray.tobytes())
        if value > threshold
    ]


@dataclass(frozen=True)
class PhenotypeDescriptor:
    # Mathematical intrinsic dimension is retained as a diagnostic, but is NOT a
    # niche axis because it comes from the representation spec rather than pixels.
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


def describe_images(images: Sequence[Image.Image], intrinsic_dimension: int) -> PhenotypeDescriptor:
    """Describe visible binary support; pixel intensity above threshold is ignored."""
    frames = [_support_points(image) for image in images]
    if any(not frame for frame in frames):
        raise ValueError("phenotype descriptor requires foreground support in every frame")
    return describe_frames(frames, intrinsic_dimension)


def describe_genome(route: str, genome: dict[str, object], times: Iterable[float] | None = None) -> PhenotypeDescriptor:
    # Local import avoids creating a module cycle with core.py.
    from core import ROUTES, TIMES, draw_points

    if route not in ROUTES:
        raise KeyError(f"route {route!r} is not registered")
    active_times = tuple(TIMES if times is None else times)
    alpha = int(genome["alpha"])
    images = [draw_points(ROUTES[route]["render"](genome, t), alpha) for t in active_times]
    return describe_images(images, int(ROUTES[route]["intrinsic_dimension"]))


def _bin01(value: float, bins: int = NICHE_BINS) -> int:
    if bins < 2:
        raise ValueError("niche bins must be >= 2")
    bounded = min(1.0 - 1e-12, max(0.0, value))
    return min(bins - 1, int(bounded * bins))


def niche_key(descriptor: PhenotypeDescriptor, bins: int = NICHE_BINS) -> NicheKey:
    """Map rendered structure to a deliberately small fixed phenotype grid.

    Only bounded geometry/temporal axes define cells in v1. Mathematical
    intrinsic dimension, `radial_cv`, and `angular_coverage` remain diagnostics.
    Route/representation identity is preserved separately by the archive stratum.
    """
    return NicheKey(
        anisotropy_bin=_bin01(descriptor.anisotropy, bins),
        central_void_bin=_bin01(descriptor.central_void, bins),
        motion_bin=_bin01(descriptor.shape_motion, bins),
    )
