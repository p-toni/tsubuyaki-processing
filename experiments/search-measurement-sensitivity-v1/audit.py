#!/usr/bin/env python3
"""Consumed-seed sensitivity audit for sparse structural target metrics."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import statistics
from pathlib import Path

from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1_AUDIT_PATH = ROOT / "experiments" / "search-measurement-audit-v1" / "objective_audit.py"

spec = importlib.util.spec_from_file_location("search_measurement_audit_v1", V1_AUDIT_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

ROUTES = tuple(base.ROUTES)
SEEDS = tuple(base.SEEDS)
REGIMES = tuple(base.REGIMES)
BG = base.BG
SUPPORT_THRESHOLD = base.SUPPORT_THRESHOLD
SHAPE_WEIGHT = base.SHAPE_WEIGHT
MASS_WEIGHT = base.MASS_WEIGHT
EPSILON = base.EPSILON
RADII = (0, 1, 2, 3)
TRANSLATIONS = (1, 2, 3, 6, 12)


def _mask(im: Image.Image) -> Image.Image:
    return im.point(lambda v: 255 if v > SUPPORT_THRESHOLD else 0)


def _dilate(mask: Image.Image, radius: int) -> Image.Image:
    if radius <= 0:
        return mask
    return mask.filter(ImageFilter.MaxFilter(size=2 * radius + 1))


def _tolerant_f1(a: Image.Image, b: Image.Image, radius: int) -> float:
    am = _mask(a)
    bm = _mask(b)
    ad = _dilate(am, radius)
    bd = _dilate(bm, radius)
    ab = am.tobytes()
    bb = bm.tobytes()
    adb = ad.tobytes()
    bdb = bd.tobytes()
    ac = sum(1 for x in ab if x)
    bc = sum(1 for x in bb if x)
    if ac == 0 or bc == 0:
        return 0.0
    precision = sum(1 for x, y in zip(ab, bdb) if x and y) / ac
    recall = sum(1 for x, y in zip(bb, adb) if x and y) / bc
    if precision + recall <= EPSILON:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def sparse_shape_v2_frame_distance(a: Image.Image, b: Image.Image) -> float:
    multiscale_f1 = statistics.fmean(_tolerant_f1(a, b, radius) for radius in RADII)
    shape_distance = 1.0 - multiscale_f1
    mass_error = base._relative_mass_error(a, b)
    return SHAPE_WEIGHT * shape_distance + MASS_WEIGHT * mass_error


def sparse_shape_v2_distance(frames: tuple[Image.Image, ...], target: tuple[Image.Image, ...]) -> float:
    return statistics.fmean(sparse_shape_v2_frame_distance(a, b) for a, b in zip(frames, target))


def _shift(im: Image.Image, dx: int) -> Image.Image:
    out = base._blank_like(im)
    out.paste(im, (dx, 0))
    return out


def _foreground_points(im: Image.Image) -> list[tuple[int, int, int]]:
    width, _height = im.size
    return [
        (index % width, index // width, value)
        for index, value in enumerate(im.tobytes())
        if value > SUPPORT_THRESHOLD
    ]


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


def _support_fraction(candidate: Image.Image, target: Image.Image) -> float:
    c = sum(1 for value in candidate.tobytes() if value > SUPPORT_THRESHOLD)
    t = sum(1 for value in target.tobytes() if value > SUPPORT_THRESHOLD)
    return c / t if t else 0.0


def _distance_record(frames: tuple[Image.Image, ...], target_frames: tuple[Image.Image, ...]) -> dict:
    return {
        "sparseShapeV1": base.sparse_shape_distance(frames, target_frames),
        "sparseShapeV2": sparse_shape_v2_distance(frames, target_frames),
        "meanInkMass": statistics.fmean(base._ink_mass(im) for im in frames),
        "meanSupportFraction": statistics.fmean(_support_fraction(a, b) for a, b in zip(frames, target_frames)),
    }


def _contracts(distances: dict[str, dict], metric: str) -> dict[str, bool]:
    d = lambda name: float(distances[name][metric])
    return {
        "exactZero": abs(d("exact")) <= EPSILON,
        "blankAtLeast099": d("blank") >= 0.99,
        "shift3Positive": d("shift3") > EPSILON,
        "shortTranslationNondecreasing": d("shift1") <= d("shift2") + EPSILON and d("shift2") <= d("shift3") + EPSILON,
        "longTranslationStrict": d("shift3") + EPSILON < d("shift6") and d("shift6") + EPSILON < d("shift12"),
        "fadeBelowDelete": d("fade50") + EPSILON < d("deleteRightThird"),
        "deleteBelowBlank": d("deleteRightThird") + EPSILON < d("blank"),
        "denseAboveNeighbor": d("denseBBox") > d("validNeighbor") + EPSILON,
        "unrelatedAboveNeighbor": d("unrelatedValid") > d("validNeighbor") + EPSILON,
        "duplicateAboveFade": d("duplicateShift6") > d("fade50") + EPSILON,
    }


def _target_case(route: str, seed: int, regime: str, target, starts, brief) -> dict:
    target_frames = base._frames(target)
    alpha = base._alpha_variant(target, brief)
    neighbor = base._valid_neighbor(target, brief, seed, f"sensitivity-{regime}")
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
    distances = {name: _distance_record(frames, target_frames) for name, frames in variants.items()}
    return {
        "route": route,
        "seed": seed,
        "regime": regime,
        "targetFingerprint": base.v1.phenotype_fingerprint(target),
        "distances": distances,
        "contracts": {
            "sparseShapeV1": _contracts(distances, "sparseShapeV1"),
            "sparseShapeV2": _contracts(distances, "sparseShapeV2"),
        },
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
        "route": route,
        "seed": seed,
        "metrics": {
            "sparseShapeV1": "0.8*(1-F1 radius3)+0.2*relativeInkMassError",
            "sparseShapeV2": "0.8*(1-mean(F1 radii 0,1,2,3))+0.2*relativeInkMassError",
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
