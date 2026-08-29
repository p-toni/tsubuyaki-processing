#!/usr/bin/env python3
"""Geometric structural target-metric audit with an out-of-design consumed-seed holdout."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import statistics
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_PATH = ROOT / "experiments" / "search-measurement-audit-v1" / "objective_audit.py"

spec = importlib.util.spec_from_file_location("search_measurement_audit_v1", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

ROUTES = tuple(base.ROUTES)
DESIGN_SEEDS = (101, 103, 107)
HOLDOUT_SEEDS = (109, 113, 127)
SEEDS = DESIGN_SEEDS + HOLDOUT_SEEDS
REGIMES = ("local", "global")
BG = base.BG
SUPPORT_THRESHOLD = base.SUPPORT_THRESHOLD
ALIGN_RADIUS = 3
PLACEMENT_FRACTION = 0.10
EPSILON = base.EPSILON


def _foreground_points(im: Image.Image) -> list[tuple[int, int, int]]:
    width, _height = im.size
    return [
        (index % width, index // width, value)
        for index, value in enumerate(im.tobytes())
        if value > SUPPORT_THRESHOLD
    ]


def _support_geometry(im: Image.Image) -> dict | None:
    points = _foreground_points(im)
    if not points:
        return None
    xs = [x for x, _y, _v in points]
    ys = [y for _x, y, _v in points]
    return {
        "count": len(points),
        "cx": statistics.fmean(xs),
        "cy": statistics.fmean(ys),
        "width": max(xs) - min(xs) + 1,
        "height": max(ys) - min(ys) + 1,
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
    }


def _shift(im: Image.Image, dx: int, dy: int = 0) -> Image.Image:
    out = base._blank_like(im)
    out.paste(im, (dx, dy))
    return out


def _align_candidate(candidate: Image.Image, target: Image.Image) -> Image.Image:
    cg = _support_geometry(candidate)
    tg = _support_geometry(target)
    if cg is None or tg is None:
        return candidate.copy()
    dx = int(round(float(tg["cx"]) - float(cg["cx"])))
    dy = int(round(float(tg["cy"]) - float(cg["cy"])))
    return _shift(candidate, dx, dy)


def _placement_component(candidate: Image.Image, target: Image.Image) -> float:
    cg = _support_geometry(candidate)
    tg = _support_geometry(target)
    if cg is None or tg is None:
        return 1.0
    scale = max(1.0, PLACEMENT_FRACTION * min(candidate.size))
    distance = math.hypot(float(cg["cx"]) - float(tg["cx"]), float(cg["cy"]) - float(tg["cy"]))
    return min(1.0, distance / scale)


def _shape_component(candidate: Image.Image, target: Image.Image) -> float:
    if _support_geometry(candidate) is None or _support_geometry(target) is None:
        return 1.0
    aligned = _align_candidate(candidate, target)
    return 1.0 - base._tolerant_f1(aligned, target)


def _extent_component(candidate: Image.Image, target: Image.Image) -> float:
    cg = _support_geometry(candidate)
    tg = _support_geometry(target)
    if cg is None or tg is None:
        return 1.0
    width_error = min(1.0, abs(float(cg["width"]) - float(tg["width"])) / max(float(tg["width"]), 1.0))
    height_error = min(1.0, abs(float(cg["height"]) - float(tg["height"])) / max(float(tg["height"]), 1.0))
    return (width_error + height_error) / 2.0


def _mass_component(candidate: Image.Image, target: Image.Image) -> float:
    return base._relative_mass_error(candidate, target)


def frame_components(candidate: Image.Image, target: Image.Image) -> dict[str, float]:
    if _support_geometry(candidate) is None:
        return {"placement": 1.0, "shape": 1.0, "extent": 1.0, "mass": 1.0}
    components = {
        "placement": _placement_component(candidate, target),
        "shape": _shape_component(candidate, target),
        "extent": _extent_component(candidate, target),
        "mass": _mass_component(candidate, target),
    }
    for name, value in components.items():
        if value < -EPSILON or value > 1.0 + EPSILON:
            raise AssertionError(f"component {name} outside [0,1]: {value}")
    return components


def sparse_geometry_distance(frames: tuple[Image.Image, ...], target_frames: tuple[Image.Image, ...]) -> dict:
    per_frame = [frame_components(candidate, target) for candidate, target in zip(frames, target_frames)]
    mean_components = {
        name: statistics.fmean(frame[name] for frame in per_frame)
        for name in ("placement", "shape", "extent", "mass")
    }
    return {
        "distance": statistics.fmean(mean_components.values()),
        "components": mean_components,
        "meanInkMass": statistics.fmean(base._ink_mass(im) for im in frames),
        "meanSupport": statistics.fmean(sum(1 for value in im.tobytes() if value > SUPPORT_THRESHOLD) for im in frames),
    }


def _delete_right_third(im: Image.Image) -> Image.Image:
    points = _foreground_points(im)
    if not points:
        return im.copy()
    xs = sorted(x for x, _y, _v in points)
    cutoff = xs[max(0, min(len(xs) - 1, (2 * len(xs)) // 3))]
    out = im.copy()
    pixels = out.load()
    for x, y, _value in points:
        if x >= cutoff:
            pixels[x, y] = BG
    return out


def _dense_bbox(im: Image.Image) -> Image.Image:
    points = _foreground_points(im)
    if not points:
        return im.copy()
    xs = [x for x, _y, _v in points]
    ys = [y for _x, y, _v in points]
    ink = max(SUPPORT_THRESHOLD + 1, int(round(statistics.fmean(v for _x, _y, v in points))))
    out = base._blank_like(im)
    pixels = out.load()
    for y in range(min(ys), max(ys) + 1):
        for x in range(min(xs), max(xs) + 1):
            pixels[x, y] = ink
    return out


def _duplicate_shift(im: Image.Image, dx: int = 6) -> Image.Image:
    shifted = _shift(im, dx)
    return Image.frombytes("L", im.size, bytes(max(a, b) for a, b in zip(im.tobytes(), shifted.tobytes())))


def _contracts(distances: dict[str, dict]) -> dict[str, bool]:
    d = lambda name: float(distances[name]["distance"])
    return {
        "exactZero": abs(d("exact")) <= EPSILON,
        "blankOne": abs(d("blank") - 1.0) <= EPSILON,
        "translationsStrict": (
            d("shift1") + EPSILON < d("shift2")
            and d("shift2") + EPSILON < d("shift3")
            and d("shift3") + EPSILON < d("shift6")
            and d("shift6") + EPSILON < d("shift12")
        ),
        "shift3BelowFade": d("shift3") + EPSILON < d("fade50"),
        "shift12BelowDelete": d("shift12") + EPSILON < d("deleteRightThird"),
        "alphaBelowDelete": d("validAlpha") + EPSILON < d("deleteRightThird"),
        "deleteBelowBlank": d("deleteRightThird") + EPSILON < d("blank"),
        "neighborBelowUnrelated": d("validNeighbor") + EPSILON < d("unrelatedValid"),
        "neighborBelowDense": d("validNeighbor") + EPSILON < d("denseBBox"),
        "duplicateAboveFade": d("duplicateShift6") > d("fade50") + EPSILON,
        "duplicateAboveShift12": d("duplicateShift6") > d("shift12") + EPSILON,
    }


def _target_case(route: str, seed: int, regime: str, target, starts, brief) -> dict:
    target_frames = base._frames(target)
    alpha = base._alpha_variant(target, brief)
    neighbor = base._valid_neighbor(target, brief, seed, f"geometry-{regime}")
    unrelated = copy.deepcopy(starts[-1])
    base.v1.evaluate_candidate(unrelated, brief)
    if not unrelated.checks.get("valid", False):
        raise AssertionError("common-start unrelated control became invalid")

    variants: dict[str, tuple[Image.Image, ...]] = {
        "exact": target_frames,
        "shift1": tuple(_shift(im, 1) for im in target_frames),
        "shift2": tuple(_shift(im, 2) for im in target_frames),
        "shift3": tuple(_shift(im, 3) for im in target_frames),
        "shift6": tuple(_shift(im, 6) for im in target_frames),
        "shift12": tuple(_shift(im, 12) for im in target_frames),
        "fade50": tuple(base._fade(im, 0.5) for im in target_frames),
        "blank": tuple(base._blank_like(im) for im in target_frames),
        "validAlpha": base._frames(alpha),
        "validNeighbor": base._frames(neighbor),
        "unrelatedValid": base._frames(unrelated),
        "deleteRightThird": tuple(_delete_right_third(im) for im in target_frames),
        "denseBBox": tuple(_dense_bbox(im) for im in target_frames),
        "duplicateShift6": tuple(_duplicate_shift(im, 6) for im in target_frames),
    }
    distances = {name: sparse_geometry_distance(frames, target_frames) for name, frames in variants.items()}
    return {
        "route": route,
        "seed": seed,
        "population": "design" if seed in DESIGN_SEEDS else "holdout",
        "regime": regime,
        "targetFingerprint": base.v1.phenotype_fingerprint(target),
        "distances": distances,
        "contracts": _contracts(distances),
    }


def run_block(route: str, seed: int) -> dict:
    if route not in ROUTES or seed not in SEEDS:
        raise ValueError("route/seed outside preregistered population")
    brief = base.v1._brief(route)
    starts = base.v1._generate_common_starts(brief, seed, route)
    targets = {
        "local": base.v1._local_target(brief, seed, route, starts[0]),
        "global": base.v1._global_target(brief, seed, route),
    }
    return {
        "version": 1,
        "metric": "sparse-geometry-v1",
        "route": route,
        "seed": seed,
        "population": "design" if seed in DESIGN_SEEDS else "holdout",
        "settings": {
            "supportThreshold": SUPPORT_THRESHOLD,
            "alignmentRadius": ALIGN_RADIUS,
            "placementFractionOfCanvas": PLACEMENT_FRACTION,
            "componentWeights": {"placement": 0.25, "shape": 0.25, "extent": 0.25, "mass": 0.25},
        },
        "cases": [_target_case(route, seed, regime, target, starts, brief) for regime, target in targets.items()],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTES, required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2))


if __name__ == "__main__":
    main()
