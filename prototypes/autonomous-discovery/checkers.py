"""Route-specific hard-validity checkers for the autonomous discovery prototype.

These checks are deliberately *not* aesthetic fitness functions. They answer whether a
candidate still satisfies the representation contract strongly enough to be worth
artistic comparison.

The checker receives route geometry from the exact same generator used by the renderer,
so no route equation is duplicated here.
"""
from __future__ import annotations

import math
import statistics
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Point = Tuple[float, float]


def _finite_points(points: Sequence[Point]) -> bool:
    return bool(points) and all(math.isfinite(x) and math.isfinite(y) for x, y in points)


def _in_frame_fraction(points: Sequence[Point], width: int, height: int) -> float:
    if not points:
        return 0.0
    return sum(0 <= x < width and 0 <= y < height for x, y in points) / len(points)


def _bbox(points: Sequence[Point], width: int, height: int) -> Dict[str, float]:
    if not points:
        return {"width": 0.0, "height": 0.0, "dominant": 0.0}
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bw = (max(xs) - min(xs)) / width
    bh = (max(ys) - min(ys)) / height
    return {"width": bw, "height": bh, "dominant": max(bw, bh)}


def _step_stats(points: Sequence[Point]) -> Dict[str, float]:
    if len(points) < 3:
        return {"median": 0.0, "p95": float("inf"), "max": float("inf"), "p95_over_median": float("inf")}
    ds = [math.hypot(b[0]-a[0], b[1]-a[1]) for a,b in zip(points, points[1:])]
    ordered = sorted(ds)
    med = statistics.median(ordered)
    p95 = ordered[min(len(ordered)-1, int(len(ordered)*.95))]
    mx = ordered[-1]
    return {
        "median": med,
        "p95": p95,
        "max": mx,
        "p95_over_median": p95 / med if med > 1e-9 else float("inf"),
    }


def _mean_corresponding_displacement(a: Sequence[Point], b: Sequence[Point], diagonal: float) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return float("inf")
    # Sample at most 512 correspondences to keep the checker cheap.
    step = max(1, n // 512)
    ds = [math.hypot(a[i][0]-b[i][0], a[i][1]-b[i][1]) for i in range(0, n, step)]
    return statistics.fmean(ds) / diagonal if ds else 0.0


def _shared_frame_checks(frames: List[Sequence[Point]], width: int, height: int) -> Tuple[List[str], Dict[str, object]]:
    failures: List[str] = []
    diagnostics: Dict[str, object] = {}
    finite = [_finite_points(p) for p in frames]
    in_frame = [_in_frame_fraction(p, width, height) for p in frames]
    boxes = [_bbox(p, width, height) for p in frames]
    diagnostics.update({
        "finiteByFrame": finite,
        "inFrameFractionByFrame": in_frame,
        "bboxByFrame": boxes,
    })
    if not all(finite):
        failures.append("non-finite or empty geometry")
    if min(in_frame, default=0.0) < 0.78:
        failures.append("too much geometry leaves the canvas")
    if min((b["dominant"] for b in boxes), default=0.0) < 0.28:
        failures.append("representation collapses to a very small form")
    return failures, diagnostics


def check_recurrence(
    genome: Dict[str, float],
    times: Sequence[float],
    geometry_fn: Callable[[Dict[str, float], float], Dict[str, object]],
    width: int,
    height: int,
) -> Dict[str, object]:
    """Validate a continuous filament/ribbon representation.

    Occupancy is intentionally absent from pass/fail. A healthy filament may be sparse.
    """
    geoms = [geometry_fn(genome, t) for t in times]
    frames = [g["all"] for g in geoms]
    spines = [g["spine"] for g in geoms]
    failures, diagnostics = _shared_frame_checks(frames, width, height)
    warnings: List[str] = []

    spine_in_frame = [_in_frame_fraction(s, width, height) for s in spines]
    continuity = [_step_stats(s) for s in spines]
    spine_boxes = [_bbox(s, width, height) for s in spines]
    diagonal = math.hypot(width, height)
    temporal_motion = [
        _mean_corresponding_displacement(a, b, diagonal)
        for a,b in zip(spines, spines[1:])
    ]

    diagnostics.update({
        "spineInFrameFractionByFrame": spine_in_frame,
        "spineContinuityByFrame": continuity,
        "spineBBoxByFrame": spine_boxes,
        "temporalSpineDisplacement": temporal_motion,
        "sideAmplitude": float(genome.get("side", 0.0)),
        "occupancyUsedAsGate": False,
    })

    if min(spine_in_frame, default=0.0) < 0.90:
        failures.append("axial spine leaves the canvas")
    if max((c["p95_over_median"] for c in continuity), default=float("inf")) > 8.0:
        failures.append("axial sampling develops large discontinuities")
    if max((c["max"] for c in continuity), default=float("inf")) > 18.0:
        failures.append("axial spine contains a large geometric jump")
    if min((b["dominant"] for b in spine_boxes), default=0.0) < 0.35:
        failures.append("axial spine loses meaningful canvas coverage")
    if float(genome.get("side", 0.0)) < 3.0:
        warnings.append("side structure is extremely subtle; inspect filament identity")
    if temporal_motion:
        if max(temporal_motion) > 0.28:
            failures.append("temporal motion is too discontinuous across the review horizon")
        elif max(temporal_motion) < 0.001:
            warnings.append("motion is nearly static across the review horizon")

    return {
        "route": "recurrence",
        "valid": not failures,
        "failures": failures,
        "warnings": warnings,
        "diagnostics": diagnostics,
    }


def check_family(
    genome: Dict[str, float],
    times: Sequence[float],
    geometry_fn: Callable[[Dict[str, float], float], Dict[str, object]],
    width: int,
    height: int,
) -> Dict[str, object]:
    """Validate root + attached repeated-family semantics.

    The checker relies on the generator's explicit part views rather than inferring
    anatomy from pixels.
    """
    geoms = [geometry_fn(genome, t) for t in times]
    frames = [g["all"] for g in geoms]
    failures, diagnostics = _shared_frame_checks(frames, width, height)
    warnings: List[str] = []

    expected = int(genome.get("organs", 0))
    counts = [len(g["organs"]) for g in geoms]
    root_boxes = [_bbox(g["root"], width, height) for g in geoms]
    anchor_in_frame = []
    tip_in_frame = []
    length_cv = []
    anchor_gap_ratio = []

    for g in geoms:
        anchors = g["anchors"]
        organs = g["organs"]
        anchor_in_frame.append(_in_frame_fraction(anchors, width, height))
        tips = [o[-1] for o in organs if o]
        tip_in_frame.append(_in_frame_fraction(tips, width, height))
        lengths = []
        for anchor, organ in zip(anchors, organs):
            if not organ:
                continue
            lengths.append(math.hypot(organ[-1][0]-anchor[0], organ[-1][1]-anchor[1]))
        if lengths and statistics.fmean(lengths) > 1e-9:
            length_cv.append(statistics.pstdev(lengths) / statistics.fmean(lengths))
        else:
            length_cv.append(float("inf"))
        gaps = [math.hypot(b[0]-a[0], b[1]-a[1]) for a,b in zip(anchors, anchors[1:])]
        if gaps:
            root_scale = max(1.0, float(genome.get("root_w", 1.0))*2)
            anchor_gap_ratio.append(min(gaps) / root_scale)
        else:
            anchor_gap_ratio.append(0.0)

    diagnostics.update({
        "expectedOrganCount": expected,
        "organCountByFrame": counts,
        "rootBBoxByFrame": root_boxes,
        "anchorInFrameFractionByFrame": anchor_in_frame,
        "tipInFrameFractionByFrame": tip_in_frame,
        "siblingLengthCVByFrame": length_cv,
        "minimumAnchorGapRatioByFrame": anchor_gap_ratio,
    })

    if expected < 3:
        failures.append("repeated family has fewer than three siblings")
    if any(c != expected for c in counts):
        failures.append("repeated-family count is not preserved")
    if min((b["width"] for b in root_boxes), default=0.0) < 0.22 or min((b["height"] for b in root_boxes), default=0.0) < 0.18:
        failures.append("root mass collapses")
    if min(anchor_in_frame, default=0.0) < 1.0:
        failures.append("one or more family anchors leave the canvas")
    if min(tip_in_frame, default=0.0) < 0.80:
        failures.append("too many organ tips leave the canvas")
    if max(length_cv, default=float("inf")) > 0.32:
        failures.append("shared family law loses sibling-scale coherence")
    if min(anchor_gap_ratio, default=0.0) < 0.045:
        warnings.append("family anchors are tightly packed; inspect merged-organ drift")

    return {
        "route": "family",
        "valid": not failures,
        "failures": failures,
        "warnings": warnings,
        "diagnostics": diagnostics,
    }


def check_candidate(
    route: str,
    genome: Dict[str, float],
    times: Sequence[float],
    geometry_fn: Callable[[Dict[str, float], float], Dict[str, object]],
    width: int,
    height: int,
) -> Dict[str, object]:
    if route == "recurrence":
        return check_recurrence(genome, times, geometry_fn, width, height)
    if route == "family":
        return check_family(genome, times, geometry_fn, width, height)
    return {
        "route": route,
        "valid": False,
        "failures": [f"no checker registered for route {route!r}"],
        "warnings": [],
        "diagnostics": {},
    }
