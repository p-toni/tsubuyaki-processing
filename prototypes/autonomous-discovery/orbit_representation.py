"""Experimental closed-recurrence representation for aperture-bearing forms.

This module deliberately registers the new arm at experiment time instead of
changing the baseline four-route registry. That keeps the intervention isolated
until its capacity generalizes beyond the recurrence↔sheet boundary study.
"""
from __future__ import annotations

import math
import statistics
from typing import Dict

from representations import RepresentationSpec, mutate_numeric


def orbit_geometry(g: Dict[str, float], t: float, W: int, H: int):
    """Closed 1-D recurrent manifold with a persistent central aperture."""
    spine = []
    sides = []
    n = int(g["samples"])
    cx, cy = W / 2, H / 2

    for i in range(n):
        q = 2 * math.pi * i / n
        radial = (
            1
            + g["lobe"] * math.sin(g["f1"] * q + t / g["time"])
            + g["ripple"] * math.sin(g["f2"] * q - t / g["time2"] + g["phase"])
            + g["asym"] * math.cos(q - g["asym_phase"])
            - g["dent"] * math.exp(g["dent_k"] * (math.cos(q - g["dent_phase"]) - 1))
        )
        ang = q + g["warp"] * math.sin(g["f3"] * q + t / g["time3"])
        r = g["radius"] * radial
        x = cx + g["sx"] * r * math.cos(ang)
        y = cy + g["sy"] * r * math.sin(ang)
        x += g["fold"] * math.sin(2 * q + t / g["time4"]) * (0.35 + 0.65 * math.sin(q) ** 2)
        y += g["fold2"] * math.sin(3 * q - t / g["time5"]) * (0.35 + 0.65 * math.cos(q) ** 2)
        spine.append((x, y))

    for i, (x, y) in enumerate(spine):
        if i % 2:
            continue
        x0, y0 = spine[(i - 1) % n]
        x1, y1 = spine[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        mag = max(1e-6, math.hypot(dx, dy))
        nx, ny = -dy / mag, dx / mag
        q = 2 * math.pi * i / n
        width = g["side"] * (0.7 + 0.3 * math.sin(q + g["width_phase"]) ** 2)
        sides.extend(((x + width * nx, y + width * ny), (x - width * nx, y - width * ny)))

    return {"spine": spine, "sides": sides, "all": spine + sides}


def orbit_seed(rng):
    # Integer angular frequencies are intentional: non-integer winding creates a
    # visible seam at q=0/2π and violates the closed-manifold contract.
    return {
        "samples": rng.choice([2200, 2600, 3000]),
        "radius": rng.uniform(72, 112),
        "sx": rng.uniform(0.82, 1.22),
        "sy": rng.uniform(0.68, 1.12),
        "lobe": rng.uniform(0.07, 0.22),
        "ripple": rng.uniform(0.02, 0.085),
        "asym": rng.uniform(0.03, 0.13),
        "dent": rng.uniform(0.08, 0.24),
        "dent_k": rng.uniform(2.0, 4.5),
        "f1": rng.choice([2, 3, 4]),
        "f2": rng.choice([5, 6, 7, 8, 9, 10]),
        "f3": rng.choice([2, 3, 4, 5]),
        "phase": rng.uniform(0, 2 * math.pi),
        "asym_phase": rng.uniform(0, 2 * math.pi),
        "dent_phase": rng.uniform(0, 2 * math.pi),
        "warp": rng.uniform(0.025, 0.12),
        "fold": rng.uniform(3, 15),
        "fold2": rng.uniform(2, 11),
        "side": rng.uniform(4, 13),
        "width_phase": rng.uniform(0, 2 * math.pi),
        "time": rng.uniform(18, 38),
        "time2": rng.uniform(20, 46),
        "time3": rng.uniform(22, 50),
        "time4": rng.uniform(18, 44),
        "time5": rng.uniform(20, 48),
        "alpha": rng.randint(28, 48),
    }


ORBIT_SPEC = RepresentationSpec(
    "orbit", "O", "1", 1, (0.012, 0.06), orbit_seed, mutate_numeric, orbit_geometry
)


def _bbox(points, width, height):
    if not points:
        return {"width": 0.0, "height": 0.0, "dominant": 0.0}
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bw = (max(xs) - min(xs)) / width
    bh = (max(ys) - min(ys)) / height
    return {"width": bw, "height": bh, "dominant": max(bw, bh)}


def _step_stats(points):
    if len(points) < 3:
        return {"median": 0.0, "p95_over_median": float("inf")}
    ds = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])]
    ordered = sorted(ds)
    med = statistics.median(ordered)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    return {"median": med, "p95_over_median": p95 / med if med > 1e-9 else float("inf")}


def _mean_displacement(a, b, diagonal):
    n = min(len(a), len(b))
    if not n:
        return float("inf")
    step = max(1, n // 512)
    ds = [math.hypot(a[i][0] - b[i][0], a[i][1] - b[i][1]) for i in range(0, n, step)]
    return statistics.fmean(ds) / diagonal if ds else 0.0


def check_orbit(genome, times, geometry_fn, width, height):
    geoms = [geometry_fn(genome, t) for t in times]
    spines = [g["spine"] for g in geoms]
    frames = [g["all"] for g in geoms]
    failures = []
    warnings = []

    finite = [bool(p) and all(math.isfinite(x) and math.isfinite(y) for x, y in p) for p in frames]
    in_frame = [sum(0 <= x < width and 0 <= y < height for x, y in p) / len(p) if p else 0 for p in frames]
    frame_boxes = [_bbox(p, width, height) for p in frames]
    closure = []
    aperture = []
    angular = []
    spine_boxes = []
    continuity = []

    for spine in spines:
        spine_boxes.append(_bbox(spine, width, height))
        continuity.append(_step_stats(spine))
        if len(spine) < 4:
            closure.append(float("inf")); aperture.append(0.0); angular.append(0.0)
            continue
        ds = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(spine, spine[1:])]
        med = statistics.median(ds) if ds else 0.0
        seam = math.hypot(spine[0][0] - spine[-1][0], spine[0][1] - spine[-1][1])
        closure.append(seam / max(1e-9, med))
        cx = statistics.fmean(p[0] for p in spine)
        cy = statistics.fmean(p[1] for p in spine)
        radii = [math.hypot(x - cx, y - cy) for x, y in spine]
        aperture.append(min(radii) / min(width, height))
        bins = {int(((math.atan2(y - cy, x - cx) + math.pi) / (2 * math.pi)) * 36) % 36 for x, y in spine}
        angular.append(len(bins) / 36)

    temporal = [_mean_displacement(a, b, math.hypot(width, height)) for a, b in zip(spines, spines[1:])]
    diagnostics = {
        "finiteByFrame": finite,
        "inFrameFractionByFrame": in_frame,
        "bboxByFrame": frame_boxes,
        "closureStepRatioByFrame": closure,
        "apertureRadiusFractionByFrame": aperture,
        "angularCoverageByFrame": angular,
        "spineBBoxByFrame": spine_boxes,
        "spineContinuityByFrame": continuity,
        "temporalSpineDisplacement": temporal,
        "intrinsicDimension": 1,
        "occupancyUsedAsGate": False,
    }

    if not all(finite): failures.append("non-finite or empty geometry")
    if min(in_frame, default=0.0) < 0.78: failures.append("too much geometry leaves the canvas")
    if max(closure, default=float("inf")) > 4.0: failures.append("closed recurrence develops a visible seam")
    if min(aperture, default=0.0) < 0.055: failures.append("closed recurrence loses its central aperture")
    if min(angular, default=0.0) < 0.88: failures.append("closed recurrence does not wrap coherently around its aperture")
    if min((b["width"] for b in spine_boxes), default=0.0) < 0.28 or min((b["height"] for b in spine_boxes), default=0.0) < 0.24:
        failures.append("closed recurrence loses meaningful two-axis span")
    if max((c["p95_over_median"] for c in continuity), default=float("inf")) > 8.0:
        failures.append("closed recurrence sampling develops large discontinuities")
    if temporal:
        if max(temporal) > 0.24: failures.append("closed recurrence motion is too discontinuous")
        elif max(temporal) < 0.001: warnings.append("closed recurrence is nearly static")

    return {"route": "orbit", "valid": not failures, "failures": failures, "warnings": warnings, "diagnostics": diagnostics}


def register_orbit():
    """Register the experimental arm in the autonomous prototype for this process."""
    import core
    import representations

    representations.REPRESENTATIONS["orbit"] = ORBIT_SPEC
    core.ROUTES["orbit"] = {
        "render": lambda g, t: ORBIT_SPEC.points(g, t, core.W, core.H),
        "geometry": lambda g, t: ORBIT_SPEC.geometry(g, t, core.W, core.H),
        "target_occupancy": ORBIT_SPEC.target_occupancy,
        "seed": ORBIT_SPEC.seed,
        "mutate": ORBIT_SPEC.mutate,
        "prefix": ORBIT_SPEC.prefix,
        "version": ORBIT_SPEC.version,
        "intrinsic_dimension": ORBIT_SPEC.intrinsic_dimension,
    }
    if not getattr(core, "_orbit_checker_registered", False):
        base_check = core.check_candidate

        def extended_check(route, genome, times, geometry_fn, width, height):
            if route == "orbit":
                return check_orbit(genome, times, geometry_fn, width, height)
            return base_check(route, genome, times, geometry_fn, width, height)

        core.check_candidate = extended_check
        core._orbit_checker_registered = True
    return ORBIT_SPEC
