from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
CAPACITY_DIR = ROOT / 'experiments' / 'sampling-invariance-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(CAPACITY_DIR))

import core
import fast_binary_metric
from material_control import candidate_points
from pairwise_selector import DimensionVote, PairwiseDecision, PairwiseSelector

CANONICAL_TIME = 90.0
TIE_EPSILON = 1e-9
COARSE_SIZE = 40
EVAL_RADII = (6, 12)


def binary_candidate_image(cand) -> Image.Image:
    points = candidate_points(core.ROUTES[cand.route], cand.genome, CANONICAL_TIME, core.W, core.H)
    return core.draw_points(points, alpha=255)


def target_distance(cand, target_image: Image.Image) -> float:
    if not cand.checks.get('valid', False):
        return float('inf')
    result = fast_binary_metric.sparse_geometry_distance(
        (binary_candidate_image(cand),),
        (target_image,),
    )
    value = float(result['distance'])
    if not math.isfinite(value) or value < 0.0 or value > 1.0:
        raise AssertionError(f'target distance outside [0,1]: {value}')
    return value


class TargetGeometrySelector(PairwiseSelector):
    name = 'target-geometry-steering-v1'

    def __init__(self, target_image: Image.Image):
        self.target_image = target_image.copy()
        self._cache: dict[str, float] = {}

    def score(self, cand) -> float:
        if cand.id not in self._cache:
            self._cache[cand.id] = target_distance(cand, self.target_image)
        return self._cache[cand.id]

    def compare(self, a, b, brief):
        av = bool(a.checks.get('valid', False))
        bv = bool(b.checks.get('valid', False))
        if av != bv:
            verdict = 'a' if av else 'b'
            return PairwiseDecision(
                a.id, b.id, verdict, 'clear',
                (DimensionVote('route-validity', verdict, 'invalid challenger cannot displace a valid target-search incumbent', av, bv),),
                self.name,
            )
        if not av and not bv:
            return PairwiseDecision(
                a.id, b.id, 'tie', 'defer',
                (DimensionVote('route-validity', 'tie', 'both candidates are invalid', av, bv),),
                self.name,
            )
        ad = self.score(a)
        bd = self.score(b)
        delta = ad - bd
        if abs(delta) <= TIE_EPSILON:
            verdict = 'tie'; confidence = 'defer'
        else:
            verdict = 'a' if ad < bd else 'b'; confidence = 'clear'
        return PairwiseDecision(
            a.id, b.id, verdict, confidence,
            (DimensionVote('target-distance', verdict, 'lower frozen sparse-geometry target distance', ad, bd),),
            self.name,
        )


def _support(image: Image.Image) -> np.ndarray:
    array = np.frombuffer(image.tobytes(), dtype=np.uint8).reshape((image.height, image.width))
    return array > fast_binary_metric.SUPPORT_THRESHOLD


def coarse_soft_iou(candidate: Image.Image, target: Image.Image) -> float:
    def field(image: Image.Image) -> np.ndarray:
        resized = image.resize((COARSE_SIZE, COARSE_SIZE), Image.Resampling.BOX)
        arr = np.asarray(resized, dtype=float)
        arr = np.clip((arr - core.BG) / max(1.0, float(core.FG - core.BG)), 0.0, 1.0)
        return arr
    a = field(candidate)
    b = field(target)
    intersection = float(np.minimum(a, b).sum())
    union = float(np.maximum(a, b).sum())
    score = intersection / union if union > 1e-12 else 0.0
    if score < -1e-12 or score > 1.0 + 1e-12:
        raise AssertionError(f'coarse soft IoU outside [0,1]: {score}')
    return max(0.0, min(1.0, score))


def _centroid(mask: np.ndarray) -> tuple[float, float]:
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return 0.0, 0.0
    return float(xs.mean()), float(ys.mean())


def _shift(mask: np.ndarray, dx: int, dy: int) -> np.ndarray:
    h, w = mask.shape
    out = np.zeros_like(mask, dtype=bool)
    src_x0 = max(0, -dx); src_x1 = min(w, w - dx)
    src_y0 = max(0, -dy); src_y1 = min(h, h - dy)
    if src_x1 <= src_x0 or src_y1 <= src_y0:
        return out
    dst_x0 = src_x0 + dx; dst_x1 = src_x1 + dx
    dst_y0 = src_y0 + dy; dst_y1 = src_y1 + dy
    out[dst_y0:dst_y1, dst_x0:dst_x1] = mask[src_y0:src_y1, src_x0:src_x1]
    return out


def _dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    h, w = mask.shape
    out = np.zeros_like(mask, dtype=bool)
    rr = int(radius)
    for dy in range(-rr, rr + 1):
        src_y0 = max(0, -dy); src_y1 = min(h, h - dy)
        dst_y0 = src_y0 + dy; dst_y1 = src_y1 + dy
        for dx in range(-rr, rr + 1):
            if dx*dx + dy*dy > rr*rr:
                continue
            src_x0 = max(0, -dx); src_x1 = min(w, w - dx)
            dst_x0 = src_x0 + dx; dst_x1 = src_x1 + dx
            out[dst_y0:dst_y1, dst_x0:dst_x1] |= mask[src_y0:src_y1, src_x0:src_x1]
    return out


def multiscale_f1(candidate: Image.Image, target: Image.Image) -> float:
    a = _support(candidate)
    b = _support(target)
    if not a.any() or not b.any():
        return 0.0
    acx, acy = _centroid(a); bcx, bcy = _centroid(b)
    aligned = _shift(a, int(round(bcx-acx)), int(round(bcy-acy)))
    scores = []
    for radius in EVAL_RADII:
        bd = _dilate(b, radius)
        ad = _dilate(aligned, radius)
        acount = int(aligned.sum()); bcount = int(b.sum())
        precision = float(np.count_nonzero(aligned & bd)) / max(1, acount)
        recall = float(np.count_nonzero(b & ad)) / max(1, bcount)
        f1 = 2.0 * precision * recall / max(1e-12, precision + recall)
        scores.append(f1)
    score = float(sum(scores) / len(scores))
    if score < -1e-12 or score > 1.0 + 1e-12:
        raise AssertionError(f'multiscale F1 outside [0,1]: {score}')
    return max(0.0, min(1.0, score))


def heldout_scores(cand, target_image: Image.Image) -> dict[str, float]:
    image = binary_candidate_image(cand)
    return {
        'coarseSoftIoU': coarse_soft_iou(image, target_image),
        'multiscaleF1': multiscale_f1(image, target_image),
        'targetDistance': target_distance(cand, target_image),
    }
