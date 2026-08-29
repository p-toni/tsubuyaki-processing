from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
sys.path.insert(0, str(PROTO))

from orbit_representation import register_orbit

register_orbit()

from core import BG, FG, H, W, Candidate, ROUTES, default_brief, draw_points, evaluate_candidate
from rng_streams import representation_rng

FIELD_PATH = HERE / "field.py"
field_spec = importlib.util.spec_from_file_location("sampling_invariance_field", FIELD_PATH)
field = importlib.util.module_from_spec(field_spec)
assert field_spec.loader is not None
field_spec.loader.exec_module(field)

METRIC_PATH = ROOT / "experiments" / "search-measurement-geometry-v1" / "audit.py"
metric_spec = importlib.util.spec_from_file_location("sampling_invariance_sparse_geometry", METRIC_PATH)
metric = importlib.util.module_from_spec(metric_spec)
assert metric_spec.loader is not None
metric_spec.loader.exec_module(metric)

CURRENT_ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
FIELD_ROUTE = "bandlimited-k2"
REPRESENTATIONS = CURRENT_ROUTES + (FIELD_ROUTE,)
STREAM = "sampling-invariance-capacity-v1"
ARCHIVE_SIZE = 48
MAX_ATTEMPT_MULTIPLIER = 20
CANONICAL_TIME = 90.0
FIELD_BANDWIDTH = 2
FIELD_GRID = 201
FIELD_MARGIN = 50
FIELD_MIN_SUPPORT = 80
FIELD_MAX_SUPPORT = 8000
FIELD_MIN_DOMINANT_SPAN = 0.35
DESIGN_SEEDS = (93001, 93007, 93019, 93037)
HOLDOUT_SEEDS = (
    51001,
    51031,
    51043,
    51047,
    51059,
    51061,
    51071,
    51109,
    51131,
    51133,
    51137,
    51151,
    51157,
    51169,
    51193,
    51197,
    51199,
    51203,
    51217,
    51229,
)
MEANINGFUL_MARGIN = 0.005


@dataclass(frozen=True)
class Target:
    id: str
    family: str
    image: Image.Image


@dataclass(frozen=True)
class RenderedCandidate:
    id: str
    representation: str
    image: Image.Image


def _binary_points(points: Iterable[tuple[float, float]]) -> Image.Image:
    return draw_points(list(points), alpha=255)


def _support_geometry(image: Image.Image) -> dict[str, float]:
    values = image.tobytes()
    indices = [index for index, value in enumerate(values) if value > metric.SUPPORT_THRESHOLD]
    if not indices:
        return {"support": 0.0, "bboxWidth": 0.0, "bboxHeight": 0.0, "dominantSpan": 0.0}
    xs = [index % W for index in indices]
    ys = [index // W for index in indices]
    bw = (max(xs) - min(xs) + 1) / W
    bh = (max(ys) - min(ys) + 1) / H
    return {
        "support": float(len(indices)),
        "bboxWidth": bw,
        "bboxHeight": bh,
        "dominantSpan": max(bw, bh),
    }


def _fingerprint(image: Image.Image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _ellipse_points(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    rotation: float = 0.0,
    samples: int = 1800,
) -> list[tuple[float, float]]:
    cr = math.cos(rotation)
    sr = math.sin(rotation)
    points = []
    for index in range(samples):
        q = 2.0 * math.pi * index / samples
        ex = rx * math.cos(q)
        ey = ry * math.sin(q)
        points.append((cx + cr * ex - sr * ey, cy + sr * ex + cr * ey))
    return points


def _catmull_closed(
    controls: Sequence[tuple[float, float]],
    samples_per_segment: int = 240,
) -> list[tuple[float, float]]:
    n = len(controls)
    if n < 4:
        raise ValueError("closed Catmull-Rom curve requires >=4 controls")
    out: list[tuple[float, float]] = []
    for i in range(n):
        p0 = controls[(i - 1) % n]
        p1 = controls[i]
        p2 = controls[(i + 1) % n]
        p3 = controls[(i + 2) % n]
        for j in range(samples_per_segment):
            t = j / samples_per_segment
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                2 * p1[0]
                + (-p0[0] + p2[0]) * t
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                2 * p1[1]
                + (-p0[1] + p2[1]) * t
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            out.append((x, y))
    return out


def _bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    samples: int = 1400,
) -> list[tuple[float, float]]:
    out = []
    for index in range(samples):
        t = index / max(1, samples - 1)
        u = 1.0 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        out.append((x, y))
    return out


def _filled_target(draw_fn: Callable[[ImageDraw.ImageDraw], None]) -> Image.Image:
    image = Image.new("L", (W, H), BG)
    drawer = ImageDraw.Draw(image)
    draw_fn(drawer)
    return image


def build_targets() -> tuple[Target, ...]:
    targets: list[Target] = []

    def lines(target_id: str, family_name: str, groups: Sequence[Sequence[tuple[float, float]]]) -> None:
        points = [point for group in groups for point in group]
        targets.append(Target(target_id, family_name, _binary_points(points)))

    # Multiple disconnected closed components.
    lines(
        "components-1",
        "disconnected-loops",
        (
            _ellipse_points(135, 200, 50, 82, rotation=-0.18),
            _ellipse_points(270, 195, 43, 70, rotation=0.31),
        ),
    )
    lines(
        "components-2",
        "disconnected-loops",
        (
            _ellipse_points(132, 145, 42, 50, rotation=0.15),
            _ellipse_points(268, 148, 50, 39, rotation=-0.22),
            _ellipse_points(205, 270, 47, 43, rotation=0.08),
        ),
    )
    lines(
        "components-3",
        "disconnected-loops",
        (
            _ellipse_points(137, 145, 35, 42, rotation=-0.2),
            _ellipse_points(264, 148, 43, 34, rotation=0.3),
            _ellipse_points(145, 262, 39, 33, rotation=0.18),
            _ellipse_points(258, 260, 34, 44, rotation=-0.28),
        ),
    )

    # Nested contours / cavities.
    lines(
        "nested-1",
        "nested-loops",
        (
            _ellipse_points(200, 200, 124, 105, rotation=0.08),
            _ellipse_points(216, 193, 54, 43, rotation=-0.16),
        ),
    )
    lines(
        "nested-2",
        "nested-loops",
        (
            _ellipse_points(200, 200, 124, 100, rotation=0.24),
            _ellipse_points(165, 200, 31, 39, rotation=-0.1),
            _ellipse_points(238, 198, 34, 29, rotation=0.27),
        ),
    )
    irregular_outer = _catmull_closed(
        ((92, 212), (118, 120), (208, 88), (302, 132), (314, 225), (260, 309), (155, 304))
    )
    lines(
        "nested-3",
        "nested-loops",
        (
            irregular_outer,
            _ellipse_points(207, 205, 53, 39, rotation=0.32),
        ),
    )

    # Smooth but strongly concave single loops.
    concave_controls = (
        ((94, 203), (122, 113), (217, 89), (309, 139), (252, 198), (312, 275), (214, 313), (113, 282), (158, 224)),
        ((92, 188), (138, 102), (240, 95), (312, 172), (245, 180), (289, 270), (207, 317), (108, 268), (158, 210)),
        ((104, 220), (106, 131), (183, 88), (285, 116), (315, 207), (245, 192), (279, 296), (177, 313), (101, 269), (163, 230)),
    )
    for index, controls in enumerate(concave_controls, start=1):
        lines(f"concave-{index}", "concave-loops", (_catmull_closed(controls),))

    # Open network controls.
    lines(
        "network-1",
        "open-networks",
        (
            _bezier((82, 108), (158, 308), (247, 85), (320, 292)),
            _bezier((84, 292), (159, 88), (246, 315), (318, 112)),
        ),
    )
    lines(
        "network-2",
        "open-networks",
        (
            _bezier((200, 205), (155, 170), (125, 112), (104, 76)),
            _bezier((200, 205), (245, 166), (283, 121), (320, 92)),
            _bezier((200, 205), (196, 248), (214, 302), (206, 334)),
        ),
    )
    lines(
        "network-3",
        "open-networks",
        (
            _bezier((72, 128), (145, 82), (248, 188), (331, 126)),
            _bezier((72, 205), (152, 276), (242, 122), (329, 210)),
            _bezier((73, 286), (153, 231), (250, 328), (330, 278)),
        ),
    )

    # Dense support controls constructed directly as masks.
    targets.append(
        Target(
            "dense-1",
            "dense-regions",
            _filled_target(lambda d: d.ellipse((92, 112, 308, 288), fill=FG)),
        )
    )

    def draw_annulus(d: ImageDraw.ImageDraw) -> None:
        d.ellipse((75, 95, 325, 305), fill=FG)
        d.ellipse((148, 145, 260, 254), fill=BG)

    targets.append(Target("dense-2", "dense-regions", _filled_target(draw_annulus)))

    def draw_lobes(d: ImageDraw.ImageDraw) -> None:
        d.ellipse((78, 120, 230, 290), fill=FG)
        d.ellipse((178, 105, 326, 277), fill=FG)

    targets.append(Target("dense-3", "dense-regions", _filled_target(draw_lobes)))

    if len(targets) != 15:
        raise AssertionError(f"target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract(targets: Sequence[Target]) -> dict:
    records = []
    failures = []
    fingerprints = []
    for target in targets:
        geometry = _support_geometry(target.image)
        fingerprint = _fingerprint(target.image)
        fingerprints.append(fingerprint)
        valid = (
            geometry["support"] >= 250
            and geometry["support"] <= 40000
            and geometry["dominantSpan"] >= 0.45
            and geometry["dominantSpan"] <= 0.85
        )
        if not valid:
            failures.append(f"{target.id}: target support/span contract failed: {geometry}")
        records.append(
            {
                "id": target.id,
                "family": target.family,
                "fingerprint": fingerprint,
                "geometry": geometry,
                "valid": valid,
            }
        )
    distinct = len(set(fingerprints)) == len(fingerprints)
    if not distinct:
        failures.append("target fingerprints are not all distinct")
    families = sorted({target.family for target in targets})
    if len(families) != 5 or any(sum(t.family == family for t in targets) != 3 for family in families):
        failures.append(f"target family rectangle invalid: {families}")
    return {
        "valid": not failures,
        "failures": failures,
        "targets": records,
        "families": families,
        "distinctFingerprints": distinct,
    }


class FieldRasterizer:
    def __init__(self) -> None:
        grid = np.linspace(0.0, 1.0, FIELD_GRID, dtype=float)
        xx, yy = np.meshgrid(grid, grid)
        flat_x = xx.ravel()
        flat_y = yy.ravel()
        columns = [np.ones_like(flat_x)]
        for kx, ky in field.positive_half_support(FIELD_BANDWIDTH):
            theta = 2.0 * math.pi * (kx * flat_x + ky * flat_y)
            columns.extend((np.cos(theta), np.sin(theta)))
        self.basis = np.stack(columns, axis=1)
        expected = field.coefficient_dimension(FIELD_BANDWIDTH)
        if self.basis.shape[1] != expected:
            raise AssertionError("field raster basis dimension drifted")
        self.span = W - 2 * FIELD_MARGIN

    def image(self, coefficients: np.ndarray) -> Image.Image:
        values = (self.basis @ coefficients).reshape((FIELD_GRID, FIELD_GRID))
        a = values[:-1, :-1]
        b = values[:-1, 1:]
        c = values[1:, :-1]
        d = values[1:, 1:]
        minimum = np.minimum(np.minimum(a, b), np.minimum(c, d))
        maximum = np.maximum(np.maximum(a, b), np.maximum(c, d))
        mask = (minimum <= 0.0) & (maximum >= 0.0)
        rows, cols = np.nonzero(mask)
        scale = self.span / (FIELD_GRID - 1)
        points = [
            (FIELD_MARGIN + (int(col) + 0.5) * scale, FIELD_MARGIN + (int(row) + 0.5) * scale)
            for row, col in zip(rows, cols)
        ]
        return _binary_points(points)


def _field_rng(seed: int) -> np.random.Generator:
    digest = hashlib.sha256(f"{STREAM}|{seed}|{FIELD_ROUTE}".encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big", signed=False)
    return np.random.default_rng(value)


def _draw_field_coefficients(rng: np.random.Generator) -> np.ndarray:
    coefficients = rng.normal(size=field.coefficient_dimension(FIELD_BANDWIDTH))
    coefficients[0] *= 0.25
    norm = float(np.linalg.norm(coefficients))
    if norm <= 1e-15:
        raise AssertionError("random coefficient norm vanished")
    return coefficients / norm


def _field_valid(image: Image.Image) -> tuple[bool, dict[str, float]]:
    geometry = _support_geometry(image)
    valid = (
        geometry["support"] >= FIELD_MIN_SUPPORT
        and geometry["support"] <= FIELD_MAX_SUPPORT
        and geometry["dominantSpan"] >= FIELD_MIN_DOMINANT_SPAN
    )
    return valid, geometry


def _route_brief(route: str) -> dict:
    brief = default_brief()
    brief.update(name=f"sampling-invariance-capacity-{route}", routes=[route])
    return brief


def _generate_current_archive(route: str, seed: int) -> tuple[list[RenderedCandidate], dict]:
    brief = _route_brief(route)
    version = ROUTES[route].get("version", "1")
    rng = representation_rng(seed, route, version, STREAM)
    prefix = ROUTES[route].get("prefix", route[0].upper())
    accepted: list[RenderedCandidate] = []
    attempts = 0
    max_attempts = ARCHIVE_SIZE * MAX_ATTEMPT_MULTIPLIER
    native_valid = 0
    while len(accepted) < ARCHIVE_SIZE and attempts < max_attempts:
        attempts += 1
        candidate = Candidate(
            f"{prefix}{attempts}",
            route,
            f"{prefix}{attempts}",
            ROUTES[route]["seed"](rng),
            None,
            "sampling-invariance-capacity",
        )
        evaluate_candidate(candidate, brief)
        if not candidate.checks.get("valid", False):
            continue
        native_valid += 1
        points = ROUTES[route]["geometry"](candidate.genome, CANONICAL_TIME)["all"]
        image = _binary_points(points)
        accepted.append(RenderedCandidate(candidate.id, route, image))
    if len(accepted) != ARCHIVE_SIZE:
        raise RuntimeError(f"{route}/{seed}: only {len(accepted)}/{ARCHIVE_SIZE} viable candidates in {attempts} attempts")
    fingerprints = {_fingerprint(candidate.image) for candidate in accepted}
    return accepted, {
        "attempts": attempts,
        "accepted": len(accepted),
        "nativeValid": native_valid,
        "attemptsPerAccepted": attempts / len(accepted),
        "uniqueRenderedPhenotypes": len(fingerprints),
        "uniquePhenotypeRate": len(fingerprints) / len(accepted),
    }


def _generate_field_archive(seed: int, rasterizer: FieldRasterizer) -> tuple[list[RenderedCandidate], dict]:
    rng = _field_rng(seed)
    accepted: list[RenderedCandidate] = []
    attempts = 0
    max_attempts = ARCHIVE_SIZE * MAX_ATTEMPT_MULTIPLIER
    support_counts = []
    while len(accepted) < ARCHIVE_SIZE and attempts < max_attempts:
        attempts += 1
        coefficients = _draw_field_coefficients(rng)
        image = rasterizer.image(coefficients)
        valid, geometry = _field_valid(image)
        if not valid:
            continue
        support_counts.append(geometry["support"])
        accepted.append(RenderedCandidate(f"B{attempts}", FIELD_ROUTE, image))
    if len(accepted) != ARCHIVE_SIZE:
        raise RuntimeError(f"{FIELD_ROUTE}/{seed}: only {len(accepted)}/{ARCHIVE_SIZE} viable candidates in {attempts} attempts")
    fingerprints = {_fingerprint(candidate.image) for candidate in accepted}
    return accepted, {
        "attempts": attempts,
        "accepted": len(accepted),
        "attemptsPerAccepted": attempts / len(accepted),
        "uniqueRenderedPhenotypes": len(fingerprints),
        "uniquePhenotypeRate": len(fingerprints) / len(accepted),
        "meanSupport": statistics.fmean(support_counts),
    }


def _recovery(candidate: Image.Image, target: Image.Image) -> tuple[float, dict]:
    record = metric.sparse_geometry_distance((candidate,), (target,))
    return 1.0 - float(record["distance"]), record


def run_seed(seed: int, population: str) -> dict:
    allowed = DESIGN_SEEDS if population == "design" else HOLDOUT_SEEDS if population == "holdout" else ()
    if seed not in allowed:
        raise ValueError(f"seed {seed} is not in declared {population} population")

    targets = build_targets()
    target_check = target_contract(targets)
    if not target_check["valid"]:
        raise AssertionError(target_check["failures"])

    rasterizer = FieldRasterizer()
    archives: dict[str, list[RenderedCandidate]] = {}
    diagnostics: dict[str, dict] = {}
    for route in CURRENT_ROUTES:
        archives[route], diagnostics[route] = _generate_current_archive(route, seed)
    archives[FIELD_ROUTE], diagnostics[FIELD_ROUTE] = _generate_field_archive(seed, rasterizer)

    if any(len(archives[representation]) != ARCHIVE_SIZE for representation in REPRESENTATIONS):
        raise AssertionError("archive rectangle incomplete")

    target_records = []
    for target in targets:
        by_representation = {}
        for representation in REPRESENTATIONS:
            scored = []
            for candidate in archives[representation]:
                recovery, distance_record = _recovery(candidate.image, target.image)
                scored.append((recovery, candidate.id, distance_record))
            best_recovery, best_id, best_distance = max(scored, key=lambda item: (item[0], item[1]))
            by_representation[representation] = {
                "bestRecovery": best_recovery,
                "bestCandidate": best_id,
                "distance": best_distance,
            }

        current_recoveries = {route: by_representation[route]["bestRecovery"] for route in CURRENT_ROUTES}
        best_current_route = max(CURRENT_ROUTES, key=lambda route: (current_recoveries[route], route))
        best_current = current_recoveries[best_current_route]
        field_recovery = by_representation[FIELD_ROUTE]["bestRecovery"]
        signed_delta = field_recovery - best_current
        current_added = {}
        for route in CURRENT_ROUTES:
            other_best = max(current_recoveries[other] for other in CURRENT_ROUTES if other != route)
            current_added[route] = max(0.0, current_recoveries[route] - other_best)

        target_records.append(
            {
                "id": target.id,
                "family": target.family,
                "targetFingerprint": _fingerprint(target.image),
                "representations": by_representation,
                "bestCurrentRoute": best_current_route,
                "bestCurrentRecovery": best_current,
                "fieldRecovery": field_recovery,
                "fieldSignedDelta": signed_delta,
                "fieldAddedRecovery": max(0.0, signed_delta),
                "fieldMeaningfulUniqueContribution": signed_delta > MEANINGFUL_MARGIN,
                "currentRouteAddedRecovery": current_added,
                "currentRouteMeaningfulUniqueContribution": {
                    route: current_added[route] > MEANINGFUL_MARGIN for route in CURRENT_ROUTES
                },
            }
        )

    return {
        "version": 1,
        "experiment": "sampling-invariance-capacity-v1",
        "population": population,
        "seed": seed,
        "settings": {
            "archiveSize": ARCHIVE_SIZE,
            "canonicalTime": CANONICAL_TIME,
            "metric": "sparse-geometry-v1",
            "commonBinarySupport": True,
            "fieldBandwidth": FIELD_BANDWIDTH,
            "fieldGrid": FIELD_GRID,
            "fieldMargin": FIELD_MARGIN,
            "meaningfulMargin": MEANINGFUL_MARGIN,
        },
        "representations": list(REPRESENTATIONS),
        "targetContract": target_check,
        "archiveDiagnostics": diagnostics,
        "targets": target_records,
        "hardInvariants": {
            "targetContract": target_check["valid"],
            "completeArchiveRectangle": all(len(archives[r]) == ARCHIVE_SIZE for r in REPRESENTATIONS),
            "completeTargetRectangle": len(target_records) == 15,
            "uniqueCandidatePhenotypes": all(diagnostics[r]["uniquePhenotypeRate"] > 0.95 for r in REPRESENTATIONS),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", choices=("design", "holdout"), required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run_seed(args.seed, args.population)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"seed": args.seed, "population": args.population, "hardInvariants": result["hardInvariants"]}, indent=2))


if __name__ == "__main__":
    main()
