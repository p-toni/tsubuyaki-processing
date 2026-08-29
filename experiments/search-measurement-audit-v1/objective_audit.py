#!/usr/bin/env python3
"""Adversarial sanity audit for sparse-image target-recovery objectives."""
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
V1_PATH = ROOT / "experiments" / "search-leverage-v1" / "reproduce.py"

spec = importlib.util.spec_from_file_location("search_leverage_v1", V1_PATH)
v1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(v1)

ROUTES = tuple(v1.ROUTE_ORDER)
SEEDS = (101, 103, 107)
REGIMES = ("local", "global")
BG = 9
SUPPORT_THRESHOLD = 20
SHIFT_PX = 3
DILATION_RADIUS = 3
SHAPE_WEIGHT = 0.8
MASS_WEIGHT = 0.2
EPSILON = 1e-12


def _frames(candidate) -> tuple[Image.Image, ...]:
    return tuple(v1.render_candidate_frame(candidate, t).convert("L") for t in v1.TIMES)


def _pixel_mae(a: Image.Image, b: Image.Image) -> float:
    ap = a.tobytes(); bp = b.tobytes()
    if len(ap) != len(bp):
        raise ValueError("image-size mismatch")
    return sum(abs(x-y) for x, y in zip(ap, bp)) / (255.0 * len(ap))


def current_mae(frames: tuple[Image.Image, ...], target: tuple[Image.Image, ...]) -> float:
    return statistics.fmean(_pixel_mae(a, b) for a, b in zip(frames, target))


def _blank_like(im: Image.Image) -> Image.Image:
    return Image.new("L", im.size, BG)


def _shift(im: Image.Image, dx: int = SHIFT_PX, dy: int = 0) -> Image.Image:
    out = _blank_like(im)
    out.paste(im, (dx, dy))
    return out


def _fade(im: Image.Image, fraction: float = 0.5) -> Image.Image:
    return im.point(lambda v: int(round(BG + (v-BG) * fraction)))


def _mask(im: Image.Image) -> Image.Image:
    return im.point(lambda v: 255 if v > SUPPORT_THRESHOLD else 0)


def _ink_mass(im: Image.Image) -> float:
    return float(sum(max(0, v-BG) for v in im.tobytes()))


def _tolerant_f1(a: Image.Image, b: Image.Image) -> float:
    am = _mask(a); bm = _mask(b)
    size = 2 * DILATION_RADIUS + 1
    ad = am.filter(ImageFilter.MaxFilter(size=size))
    bd = bm.filter(ImageFilter.MaxFilter(size=size))
    ab = am.tobytes(); bb = bm.tobytes(); adb = ad.tobytes(); bdb = bd.tobytes()
    ac = sum(1 for x in ab if x)
    bc = sum(1 for x in bb if x)
    if ac == 0 or bc == 0:
        return 0.0
    precision = sum(1 for x, y in zip(ab, bdb) if x and y) / ac
    recall = sum(1 for x, y in zip(bb, adb) if x and y) / bc
    if precision + recall <= EPSILON:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _relative_mass_error(a: Image.Image, b: Image.Image) -> float:
    am = _ink_mass(a); bm = _ink_mass(b)
    denom = max(am, bm, EPSILON)
    return abs(am-bm) / denom


def sparse_shape_frame_distance(a: Image.Image, b: Image.Image) -> float:
    shape_distance = 1.0 - _tolerant_f1(a, b)
    mass_error = _relative_mass_error(a, b)
    return SHAPE_WEIGHT * shape_distance + MASS_WEIGHT * mass_error


def sparse_shape_distance(frames: tuple[Image.Image, ...], target: tuple[Image.Image, ...]) -> float:
    return statistics.fmean(sparse_shape_frame_distance(a, b) for a, b in zip(frames, target))


def _alpha_variant(target, brief):
    genome = dict(target.genome)
    original = int(genome.get("alpha", 48))
    genome["alpha"] = max(22, int(round(original * 0.55)))
    cand = v1.Candidate("VALID-ALPHA", target.route, target.basin, genome, target.id, "audit-alpha")
    v1.evaluate_candidate(cand, brief)
    if not cand.checks.get("valid", False):
        raise AssertionError(f"alpha-only variant unexpectedly invalid for {target.route}")
    return cand


def _valid_neighbor(target, brief, seed: int, kind: str):
    route = target.route
    version = v1.ROUTES[route].get("version", "1")
    rng = v1.representation_rng(seed, route, version, f"search-measurement-audit-neighbor-{kind}-v1")
    target_fp = v1.phenotype_fingerprint(target)
    for attempt in range(1, 101):
        genome = v1.ROUTES[route]["mutate"](target.genome, rng, 0.55)
        cand = v1.Candidate(
            f"VALID-NEIGHBOR-A{attempt}", route, target.basin, genome, target.id, "audit-neighbor"
        )
        v1.evaluate_candidate(cand, brief)
        if cand.checks.get("valid", False) and v1.phenotype_fingerprint(cand) != target_fp:
            return cand
    raise RuntimeError(f"could not generate distinct valid neighbor for {route}/{seed}/{kind}")


def _distance_record(candidate_frames, target_frames) -> dict:
    return {
        "currentMAE": current_mae(candidate_frames, target_frames),
        "sparseShapeV1": sparse_shape_distance(candidate_frames, target_frames),
        "meanInkMass": statistics.fmean(_ink_mass(im) for im in candidate_frames),
    }


def _target_case(route: str, seed: int, kind: str, target, starts, brief) -> dict:
    target_frames = _frames(target)
    exact = target_frames
    shift3 = tuple(_shift(im) for im in target_frames)
    fade50 = tuple(_fade(im, 0.5) for im in target_frames)
    blank = tuple(_blank_like(im) for im in target_frames)
    alpha = _alpha_variant(target, brief)
    neighbor = _valid_neighbor(target, brief, seed, kind)
    unrelated = copy.deepcopy(starts[-1])
    v1.evaluate_candidate(unrelated, brief)
    if not unrelated.checks.get("valid", False):
        raise AssertionError("common-start unrelated control became invalid")

    variants = {
        "exact": exact,
        "shift3": shift3,
        "fade50": fade50,
        "blank": blank,
        "validAlpha": _frames(alpha),
        "validNeighbor": _frames(neighbor),
        "unrelatedValid": _frames(unrelated),
    }
    distances = {name: _distance_record(frames, target_frames) for name, frames in variants.items()}

    current_falsified = distances["blank"]["currentMAE"] + EPSILON < distances["shift3"]["currentMAE"]
    candidate_contracts = {
        "exactZero": abs(distances["exact"]["sparseShapeV1"]) <= EPSILON,
        "shiftBeatsBlank": distances["shift3"]["sparseShapeV1"] + EPSILON < distances["blank"]["sparseShapeV1"],
        "fadeBeatsBlank": distances["fade50"]["sparseShapeV1"] + EPSILON < distances["blank"]["sparseShapeV1"],
        "validAlphaBeatsBlank": distances["validAlpha"]["sparseShapeV1"] + EPSILON < distances["blank"]["sparseShapeV1"],
        "blankAtLeast099": distances["blank"]["sparseShapeV1"] >= 0.99,
        "shiftAtMost025": distances["shift3"]["sparseShapeV1"] <= 0.25,
    }
    return {
        "route": route,
        "seed": seed,
        "regime": kind,
        "targetFingerprint": v1.phenotype_fingerprint(target),
        "targetValid": bool(target.checks.get("valid", False)),
        "validAlphaFingerprint": v1.phenotype_fingerprint(alpha),
        "validNeighborFingerprint": v1.phenotype_fingerprint(neighbor),
        "unrelatedValidFingerprint": v1.phenotype_fingerprint(unrelated),
        "distances": distances,
        "currentMAEBlankBeatsShift3": current_falsified,
        "currentMAEBlankBeatsValidNeighbor": distances["blank"]["currentMAE"] + EPSILON < distances["validNeighbor"]["currentMAE"],
        "currentMAEBlankBeatsUnrelatedValid": distances["blank"]["currentMAE"] + EPSILON < distances["unrelatedValid"]["currentMAE"],
        "sparseShapeV1Contracts": candidate_contracts,
        "sparseShapeV1AllContractsPass": all(candidate_contracts.values()),
    }


def run_block(route: str, seed: int) -> dict:
    if route not in ROUTES:
        raise ValueError(f"unknown route {route!r}")
    if seed not in SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    brief = v1._brief(route)
    starts = v1._generate_common_starts(brief, seed, route)
    targets = {
        "local": v1._local_target(brief, seed, route, starts[0]),
        "global": v1._global_target(brief, seed, route),
    }
    cases = [_target_case(route, seed, kind, target, starts, brief) for kind, target in targets.items()]
    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "times": list(v1.TIMES),
        "settings": {
            "background": BG,
            "supportThreshold": SUPPORT_THRESHOLD,
            "shiftPixels": SHIFT_PX,
            "dilationRadius": DILATION_RADIUS,
            "shapeWeight": SHAPE_WEIGHT,
            "massWeight": MASS_WEIGHT,
        },
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTES, required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2))


if __name__ == "__main__":
    main()
