"""Install the #69 sparse-geometry-v1 target metric into historical simulators."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Callable

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY_PATH = ROOT / "experiments" / "search-measurement-geometry-v1" / "audit.py"

_spec = importlib.util.spec_from_file_location("search_measurement_geometry_v1", GEOMETRY_PATH)
geometry = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(geometry)


def _image_from_bytes(raw: bytes) -> Image.Image:
    side = math.isqrt(len(raw))
    if side * side != len(raw):
        raise ValueError(f"expected square grayscale frame, got {len(raw)} bytes")
    return Image.frombytes("L", (side, side), raw)


def install_sparse_geometry_metric(v1) -> Callable:
    """Replace only ``v1.phenotype_distance`` with the qualified #69 metric.

    Historical selector classes resolve that global function at runtime, so
    target construction, candidate generation, RNG consumption, topology and
    budgets remain historical. The #69 implementation itself is imported rather
    than copied so replay cannot drift from the metric that passed holdout.
    """

    target_cache: dict[bytes, tuple[Image.Image, ...]] = {}
    distance_cache: dict[tuple[str, str, bytes], float] = {}

    def distance(cand, target_frames: tuple[bytes, ...]) -> float:
        if not cand.checks.get("valid", False):
            return float("inf")

        target_digest = hashlib.sha256(b"\0".join(target_frames)).digest()
        target_images = target_cache.get(target_digest)
        if target_images is None:
            target_images = tuple(_image_from_bytes(raw) for raw in target_frames)
            target_cache[target_digest] = target_images

        genome_key = json.dumps(
            cand.genome,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        cache_key = (str(cand.route), genome_key, target_digest)
        cached = distance_cache.get(cache_key)
        if cached is not None:
            return cached

        candidate_raw = v1._frame_bytes(cand)
        if len(candidate_raw) != len(target_frames):
            raise ValueError("candidate/target frame count mismatch")
        candidate_images = tuple(_image_from_bytes(raw) for raw in candidate_raw)
        value = float(geometry.sparse_geometry_distance(candidate_images, target_images)["distance"])
        distance_cache[cache_key] = value
        return value

    v1.phenotype_distance = distance
    return distance
