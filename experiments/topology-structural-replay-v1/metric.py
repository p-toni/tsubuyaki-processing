"""Install the #64 sparse-shape-v1 target metric into historical simulators."""
from __future__ import annotations

import hashlib
import json
import math
from typing import Callable

from PIL import Image, ImageFilter

BG = 9
SUPPORT_THRESHOLD = 20
DILATION_RADIUS = 3
SHAPE_WEIGHT = 0.8
MASS_WEIGHT = 0.2
EPSILON = 1e-12


def _image_from_bytes(raw: bytes) -> Image.Image:
    side = math.isqrt(len(raw))
    if side * side != len(raw):
        raise ValueError(f"expected square grayscale frame, got {len(raw)} bytes")
    return Image.frombytes("L", (side, side), raw)


def _mask(im: Image.Image) -> Image.Image:
    return im.point(lambda v: 255 if v > SUPPORT_THRESHOLD else 0)


def _ink_mass(im: Image.Image) -> float:
    return float(sum(max(0, v - BG) for v in im.tobytes()))


def _prepare(raw: bytes) -> tuple[bytes, bytes, int, float]:
    im = _image_from_bytes(raw)
    mask = _mask(im)
    size = 2 * DILATION_RADIUS + 1
    dilated = mask.filter(ImageFilter.MaxFilter(size=size))
    mask_bytes = mask.tobytes()
    return mask_bytes, dilated.tobytes(), sum(1 for x in mask_bytes if x), _ink_mass(im)


def _frame_distance(
    candidate_raw: bytes,
    target_raw: bytes,
    target_prepared: tuple[bytes, bytes, int, float],
) -> float:
    candidate_mask, candidate_dilated, candidate_count, candidate_mass = _prepare(candidate_raw)
    target_mask, target_dilated, target_count, target_mass = target_prepared

    if candidate_count == 0 or target_count == 0:
        tolerant_f1 = 0.0
    else:
        precision = sum(
            1 for x, y in zip(candidate_mask, target_dilated) if x and y
        ) / candidate_count
        recall = sum(
            1 for x, y in zip(target_mask, candidate_dilated) if x and y
        ) / target_count
        tolerant_f1 = (
            0.0
            if precision + recall <= EPSILON
            else 2.0 * precision * recall / (precision + recall)
        )

    shape_distance = 1.0 - tolerant_f1
    mass_error = abs(candidate_mass - target_mass) / max(candidate_mass, target_mass, EPSILON)
    return SHAPE_WEIGHT * shape_distance + MASS_WEIGHT * mass_error


def install_sparse_shape_metric(v1) -> Callable:
    """Replace only ``v1.phenotype_distance`` and return the installed function.

    Historical selectors resolve that global function at runtime, so candidate
    generation, RNG streams, IDs, search topology and budgets remain untouched.
    Caches are local to this imported simulator instance and keyed by genome plus
    exact target-frame digest; no score can bleed across targets.
    """

    target_cache: dict[bytes, tuple[tuple[bytes, bytes, int, float], ...]] = {}
    distance_cache: dict[tuple[str, str, bytes], float] = {}

    def distance(cand, target_frames: tuple[bytes, ...]) -> float:
        if not cand.checks.get("valid", False):
            return float("inf")
        target_digest = hashlib.sha256(b"\0".join(target_frames)).digest()
        target_prepared = target_cache.get(target_digest)
        if target_prepared is None:
            target_prepared = tuple(_prepare(raw) for raw in target_frames)
            target_cache[target_digest] = target_prepared

        genome_key = json.dumps(cand.genome, sort_keys=True, separators=(",", ":"), allow_nan=False)
        cache_key = (str(cand.route), genome_key, target_digest)
        cached = distance_cache.get(cache_key)
        if cached is not None:
            return cached

        candidate_frames = v1._frame_bytes(cand)
        if len(candidate_frames) != len(target_frames):
            raise ValueError("candidate/target frame count mismatch")
        value = sum(
            _frame_distance(a, b, prepared)
            for a, b, prepared in zip(candidate_frames, target_frames, target_prepared)
        ) / len(target_frames)
        distance_cache[cache_key] = value
        return value

    v1.phenotype_distance = distance
    return distance
