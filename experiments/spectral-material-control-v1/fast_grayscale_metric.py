from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

import numpy as np
from PIL import Image

BG = 9
SUPPORT_THRESHOLD = 20
RADIUS = 3
PLACEMENT_FRACTION = 0.10
EPSILON = 1e-12


@dataclass(frozen=True)
class GraySupport:
    image: Image.Image
    mask: np.ndarray
    count: int
    cx: float
    cy: float
    width: int
    height: int
    ink_mass: float


_ANALYSIS_CACHE: dict[int, GraySupport] = {}
_DILATION_CACHE: dict[int, np.ndarray] = {}


def _analyze(image: Image.Image) -> GraySupport:
    key = id(image)
    cached = _ANALYSIS_CACHE.get(key)
    if cached is not None and cached.image is image:
        return cached
    array = np.frombuffer(image.tobytes(), dtype=np.uint8).reshape((image.height, image.width))
    mask = array > SUPPORT_THRESHOLD
    ys, xs = np.nonzero(mask)
    count = int(len(xs))
    if count:
        cx = float(int(xs.sum())) / count
        cy = float(int(ys.sum())) / count
        width = int(xs.max() - xs.min() + 1)
        height = int(ys.max() - ys.min() + 1)
    else:
        cx = cy = 0.0
        width = height = 0
    ink_mass = float(np.maximum(array.astype(np.int16) - BG, 0).sum(dtype=np.int64))
    record = GraySupport(
        image=image,
        mask=mask,
        count=count,
        cx=cx,
        cy=cy,
        width=width,
        height=height,
        ink_mass=ink_mass,
    )
    _ANALYSIS_CACHE[key] = record
    return record


def _dilate(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    out = np.zeros_like(mask, dtype=bool)
    for dy in range(-RADIUS, RADIUS + 1):
        src_y0 = max(0, -dy)
        src_y1 = min(h, h - dy)
        dst_y0 = src_y0 + dy
        dst_y1 = src_y1 + dy
        for dx in range(-RADIUS, RADIUS + 1):
            src_x0 = max(0, -dx)
            src_x1 = min(w, w - dx)
            dst_x0 = src_x0 + dx
            dst_x1 = src_x1 + dx
            out[dst_y0:dst_y1, dst_x0:dst_x1] |= mask[src_y0:src_y1, src_x0:src_x1]
    return out


def _cached_dilation(record: GraySupport) -> np.ndarray:
    key = id(record.image)
    cached = _DILATION_CACHE.get(key)
    if cached is not None:
        return cached
    dilated = _dilate(record.mask)
    _DILATION_CACHE[key] = dilated
    return dilated


def _shift_mask(mask: np.ndarray, dx: int, dy: int) -> np.ndarray:
    h, w = mask.shape
    out = np.zeros_like(mask, dtype=bool)
    src_x0 = max(0, -dx)
    src_x1 = min(w, w - dx)
    src_y0 = max(0, -dy)
    src_y1 = min(h, h - dy)
    if src_x1 <= src_x0 or src_y1 <= src_y0:
        return out
    dst_x0 = src_x0 + dx
    dst_x1 = src_x1 + dx
    dst_y0 = src_y0 + dy
    dst_y1 = src_y1 + dy
    out[dst_y0:dst_y1, dst_x0:dst_x1] = mask[src_y0:src_y1, src_x0:src_x1]
    return out


def _placement(candidate: GraySupport, target: GraySupport) -> float:
    if candidate.count == 0 or target.count == 0:
        return 1.0
    scale = max(1.0, PLACEMENT_FRACTION * min(candidate.image.size))
    distance = math.hypot(target.cx - candidate.cx, target.cy - candidate.cy)
    return min(1.0, distance / scale)


def _shape(candidate: GraySupport, target: GraySupport) -> float:
    if candidate.count == 0 or target.count == 0:
        return 1.0
    dx = int(round(target.cx - candidate.cx))
    dy = int(round(target.cy - candidate.cy))
    aligned = _shift_mask(candidate.mask, dx, dy)
    aligned_count = int(aligned.sum())
    if aligned_count == 0:
        return 1.0
    target_dilated = _cached_dilation(target)
    precision = float(np.count_nonzero(aligned & target_dilated)) / aligned_count
    aligned_dilated = _dilate(aligned)
    recall = float(np.count_nonzero(target.mask & aligned_dilated)) / target.count
    if precision + recall <= EPSILON:
        return 1.0
    return 1.0 - 2.0 * precision * recall / (precision + recall)


def _extent(candidate: GraySupport, target: GraySupport) -> float:
    if candidate.count == 0 or target.count == 0:
        return 1.0
    width_error = min(1.0, abs(candidate.width - target.width) / max(float(target.width), 1.0))
    height_error = min(1.0, abs(candidate.height - target.height) / max(float(target.height), 1.0))
    return (width_error + height_error) / 2.0


def _mass(candidate: GraySupport, target: GraySupport) -> float:
    denom = max(candidate.ink_mass, target.ink_mass, EPSILON)
    return abs(candidate.ink_mass - target.ink_mass) / denom


def frame_components(candidate: Image.Image, target: Image.Image) -> dict[str, float]:
    c = _analyze(candidate)
    t = _analyze(target)
    if c.count == 0:
        return {"placement": 1.0, "shape": 1.0, "extent": 1.0, "mass": 1.0}
    components = {
        "placement": _placement(c, t),
        "shape": _shape(c, t),
        "extent": _extent(c, t),
        "mass": _mass(c, t),
    }
    for name, value in components.items():
        if value < -EPSILON or value > 1.0 + EPSILON:
            raise AssertionError(f"component {name} outside [0,1]: {value}")
    return components


def sparse_geometry_distance(frames: tuple[Image.Image, ...], target_frames: tuple[Image.Image, ...]) -> dict:
    if len(frames) != len(target_frames):
        raise ValueError("candidate/target frame count mismatch")
    per_frame = [frame_components(candidate, target) for candidate, target in zip(frames, target_frames)]
    mean_components = {
        name: statistics.fmean(frame[name] for frame in per_frame)
        for name in ("placement", "shape", "extent", "mass")
    }
    analyses = [_analyze(image) for image in frames]
    return {
        "distance": statistics.fmean(mean_components.values()),
        "components": mean_components,
        "meanInkMass": statistics.fmean(record.ink_mass for record in analyses),
        "meanSupport": statistics.fmean(record.count for record in analyses),
    }


def clear_caches() -> None:
    _ANALYSIS_CACHE.clear()
    _DILATION_CACHE.clear()
