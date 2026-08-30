from __future__ import annotations

import math
import sys
from collections import deque
from pathlib import Path
from typing import Iterable

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
NORMALIZED_SIZE = 96
NORMALIZED_PAD = 8
TIE_EPSILON = 1e-6
HELDOUT_RADII = (2, 4, 7)


def binary_candidate_image(cand) -> Image.Image:
    points = candidate_points(core.ROUTES[cand.route], cand.genome, CANONICAL_TIME, core.W, core.H)
    return core.draw_points(points, alpha=255)


def _ink_field(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.convert('L'), dtype=float)
    denom = max(1.0, float(core.FG - core.BG))
    return np.clip((arr - float(core.BG)) / denom, 0.0, 1.0)


def normalize_soft(image: Image.Image, size: int = NORMALIZED_SIZE, pad: int = NORMALIZED_PAD) -> np.ndarray:
    raw = np.asarray(image.convert('L'), dtype=np.uint8)
    support = raw > fast_binary_metric.SUPPORT_THRESHOLD
    ys, xs = np.nonzero(support)
    if len(xs) == 0:
        return np.zeros((size, size), dtype=float)
    field = _ink_field(image)
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    crop = (np.clip(field[y0:y1 + 1, x0:x1 + 1], 0.0, 1.0) * 255.0).round().astype(np.uint8)
    crop_image = Image.fromarray(crop, mode='L')
    inner = size - 2 * pad
    scale = min(inner / crop_image.width, inner / crop_image.height)
    new_w = max(1, int(round(crop_image.width * scale)))
    new_h = max(1, int(round(crop_image.height * scale)))
    resized = crop_image.resize((new_w, new_h), Image.Resampling.BOX)
    canvas = Image.new('L', (size, size), 0)
    canvas.paste(resized, ((size - new_w) // 2, (size - new_h) // 2))
    return np.asarray(canvas, dtype=float) / 255.0


def _resize_field(field: np.ndarray, size: int) -> np.ndarray:
    image = Image.fromarray((np.clip(field, 0.0, 1.0) * 255.0).round().astype(np.uint8), mode='L')
    return np.asarray(image.resize((size, size), Image.Resampling.BOX), dtype=float) / 255.0


def _mass_normalize(values: np.ndarray) -> np.ndarray:
    total = float(values.sum())
    if total <= 1e-12:
        return np.zeros_like(values, dtype=float)
    return values.astype(float) / total


def _dilate(mask: np.ndarray, radius: int = 1) -> np.ndarray:
    h, w = mask.shape
    out = np.zeros_like(mask, dtype=bool)
    rr = int(radius)
    for dy in range(-rr, rr + 1):
        for dx in range(-rr, rr + 1):
            if dx * dx + dy * dy > rr * rr:
                continue
            src_y0 = max(0, -dy); src_y1 = min(h, h - dy)
            src_x0 = max(0, -dx); src_x1 = min(w, w - dx)
            if src_y1 <= src_y0 or src_x1 <= src_x0:
                continue
            dst_y0 = src_y0 + dy; dst_y1 = src_y1 + dy
            dst_x0 = src_x0 + dx; dst_x1 = src_x1 + dx
            out[dst_y0:dst_y1, dst_x0:dst_x1] |= mask[src_y0:src_y1, src_x0:src_x1]
    return out


def _components(mask: np.ndarray) -> list[tuple[int, bool]]:
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out: list[tuple[int, bool]] = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or seen[y, x]:
                continue
            q = deque([(y, x)])
            seen[y, x] = True
            count = 0
            touches_border = False
            while q:
                yy, xx = q.popleft()
                count += 1
                if yy == 0 or xx == 0 or yy == h - 1 or xx == w - 1:
                    touches_border = True
                for ddy in (-1, 0, 1):
                    for ddx in (-1, 0, 1):
                        if ddy == 0 and ddx == 0:
                            continue
                        ny, nx = yy + ddy, xx + ddx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((ny, nx))
            out.append((count, touches_border))
    return out


def descriptor(image: Image.Image) -> dict[str, np.ndarray]:
    field = normalize_soft(image)

    grids = []
    for size in (32, 16, 8):
        grid = _resize_field(field, size).reshape(-1)
        grids.append(_mass_normalize(grid))

    grid32 = _resize_field(field, 32)
    projection_x = _mass_normalize(grid32.sum(axis=0))
    projection_y = _mass_normalize(grid32.sum(axis=1))

    yy, xx = np.mgrid[0:NORMALIZED_SIZE, 0:NORMALIZED_SIZE]
    center = (NORMALIZED_SIZE - 1) / 2.0
    dx = xx - center
    dy = yy - center
    radius = np.sqrt(dx * dx + dy * dy) / (NORMALIZED_SIZE / 2.0)
    angle = (np.arctan2(dy, dx) + 2.0 * math.pi) % (2.0 * math.pi)

    polar = []
    for r0, r1 in ((0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.2)):
        for j in range(16):
            t0 = 2.0 * math.pi * j / 16.0
            t1 = 2.0 * math.pi * (j + 1) / 16.0
            selected = (radius >= r0) & (radius < r1) & (angle >= t0) & (angle < t1)
            polar.append(float(field[selected].sum()))
    polar = _mass_normalize(np.asarray(polar, dtype=float))

    grad_y, grad_x = np.gradient(field)
    magnitude = np.sqrt(grad_x * grad_x + grad_y * grad_y)
    orientation = (np.arctan2(grad_y, grad_x) + math.pi) % math.pi
    orientation_hist = []
    for j in range(12):
        t0 = math.pi * j / 12.0
        t1 = math.pi * (j + 1) / 12.0
        orientation_hist.append(float(magnitude[(orientation >= t0) & (orientation < t1)].sum()))
    orientation_hist = _mass_normalize(np.asarray(orientation_hist, dtype=float))

    support = field > 0.08
    radial_profile = np.zeros(24, dtype=float)
    for j in range(24):
        t0 = 2.0 * math.pi * j / 24.0
        t1 = 2.0 * math.pi * (j + 1) / 24.0
        selected = support & (angle >= t0) & (angle < t1)
        if selected.any():
            radial_profile[j] = float(radius[selected].max())

    symmetry = np.asarray([
        float(np.mean(np.abs(field - field[:, ::-1]))),
        float(np.mean(np.abs(field - field[::-1, :]))),
        float(np.mean(np.abs(field - field[::-1, ::-1]))),
    ], dtype=float)

    topo_mask = _dilate(_resize_field(field, 64) > 0.08, 1)
    foreground_components = [item for item in _components(topo_mask) if item[0] >= 5]
    background_components = _components(~topo_mask)
    holes = sum(1 for size, touches in background_components if not touches and size >= 9)
    ys, xs = np.nonzero(topo_mask)
    aspect = 1.0 if len(xs) == 0 else float((np.ptp(xs) + 1) / (np.ptp(ys) + 1))
    topology = np.asarray([
        math.log1p(min(len(foreground_components), 12)) / math.log(13.0),
        math.log1p(min(holes, 12)) / math.log(13.0),
        min(1.0, abs(math.log(max(aspect, 1e-4))) / math.log(4.0)),
    ], dtype=float)

    return {
        'grid32': grids[0],
        'grid16': grids[1],
        'grid8': grids[2],
        'projectionX': projection_x,
        'projectionY': projection_y,
        'polar': polar,
        'orientation': orientation_hist,
        'radial': radial_profile,
        'symmetry': symmetry,
        'topology': topology,
    }


def descriptor_distance(a: dict[str, np.ndarray], b: dict[str, np.ndarray]) -> tuple[float, dict[str, float]]:
    grid = float(np.mean([
        0.5 * np.abs(a['grid32'] - b['grid32']).sum(),
        0.5 * np.abs(a['grid16'] - b['grid16']).sum(),
        0.5 * np.abs(a['grid8'] - b['grid8']).sum(),
    ]))
    projection = float(0.25 * (
        np.abs(a['projectionX'] - b['projectionX']).sum() +
        np.abs(a['projectionY'] - b['projectionY']).sum()
    ))
    polar = float(0.5 * np.abs(a['polar'] - b['polar']).sum())
    orientation = float(0.5 * np.abs(a['orientation'] - b['orientation']).sum())
    radial = float(np.mean(np.abs(a['radial'] - b['radial'])))
    symmetry = float(np.mean(np.abs(a['symmetry'] - b['symmetry'])))
    topology = float(np.mean(np.abs(a['topology'] - b['topology'])))
    blocks = {
        'grid': grid,
        'projection': projection,
        'polar': polar,
        'orientation': orientation,
        'radial': radial,
        'symmetry': symmetry,
        'topology': topology,
    }
    value = float(sum(blocks.values()) / len(blocks))
    if not math.isfinite(value) or value < -1e-12:
        raise AssertionError(f'invalid perceptual descriptor distance {value}')
    return max(0.0, value), blocks


class PrototypeBank:
    def __init__(self, targets: Iterable):
        self.targets = tuple(targets)
        self.by_id = {t.id: t for t in self.targets}
        if len(self.by_id) != len(self.targets):
            raise ValueError('prototype ids must be unique')
        self.descriptors = {t.id: descriptor(t.image) for t in self.targets}

    def image_record(self, image: Image.Image, requested: str) -> dict:
        cand_desc = descriptor(image)
        distances = {
            target_id: descriptor_distance(cand_desc, target_desc)[0]
            for target_id, target_desc in self.descriptors.items()
        }
        ordered = sorted(distances.items(), key=lambda kv: (kv[1], kv[0]))
        target_distance = float(distances[requested])
        best_other = min(float(v) for k, v in distances.items() if k != requested)
        return {
            'requested': requested,
            'top1': ordered[0][0] == requested,
            'top1Id': ordered[0][0],
            'targetDistance': target_distance,
            'bestOtherDistance': best_other,
            'margin': best_other - target_distance,
            'ranking': [k for k, _ in ordered],
        }


def candidate_record(cand, requested: str, bank: PrototypeBank) -> dict:
    if not cand.checks.get('valid', False):
        return {
            'requested': requested,
            'top1': False,
            'top1Id': None,
            'targetDistance': float('inf'),
            'bestOtherDistance': float('inf'),
            'margin': float('-inf'),
            'ranking': [],
        }
    return bank.image_record(binary_candidate_image(cand), requested)


def rank_key(record: dict) -> tuple[int, float, float]:
    return (
        0 if record['top1'] else 1,
        float(record['targetDistance']),
        -float(record['margin']),
    )


class PrototypePerceptualSelector(PairwiseSelector):
    name = 'prototype-perceptual-steering-v1'

    def __init__(self, requested: str, bank: PrototypeBank):
        if requested not in bank.by_id:
            raise KeyError(requested)
        self.requested = requested
        self.bank = bank
        self._cache: dict[str, dict] = {}

    def record(self, cand) -> dict:
        if cand.id not in self._cache:
            self._cache[cand.id] = candidate_record(cand, self.requested, self.bank)
        return self._cache[cand.id]

    def compare(self, a, b, brief):
        av = bool(a.checks.get('valid', False)); bv = bool(b.checks.get('valid', False))
        if av != bv:
            verdict = 'a' if av else 'b'
            return PairwiseDecision(
                a.id, b.id, verdict, 'clear',
                (DimensionVote('route-validity', verdict, 'invalid candidate cannot displace a valid semantic-search incumbent', av, bv),),
                self.name,
            )
        if not av and not bv:
            return PairwiseDecision(
                a.id, b.id, 'tie', 'defer',
                (DimensionVote('route-validity', 'tie', 'both candidates are invalid', av, bv),),
                self.name,
            )
        ar = self.record(a); br = self.record(b)
        ak = rank_key(ar); bk = rank_key(br)
        if ak == bk:
            verdict = 'tie'; confidence = 'defer'
        else:
            verdict = 'a' if ak < bk else 'b'; confidence = 'clear'
        return PairwiseDecision(
            a.id, b.id, verdict, confidence,
            (
                DimensionVote('prototype-top1', verdict, 'prefer candidates whose nearest frozen prototype is the requested concept', ar['top1'], br['top1']),
                DimensionVote('prototype-distance', verdict, 'then reduce global perceptual distance to the requested prototype', ar['targetDistance'], br['targetDistance']),
                DimensionVote('prototype-margin', verdict, 'use discriminative prototype margin only as a tie-breaker', ar['margin'], br['margin']),
            ),
            self.name,
        )


def _heldout_f1_from_fields(a: np.ndarray, b: np.ndarray) -> float:
    am = a > 0.08; bm = b > 0.08
    if not am.any() or not bm.any():
        return 0.0
    scores = []
    for radius in HELDOUT_RADII:
        ad = _dilate(am, radius); bd = _dilate(bm, radius)
        precision = float(np.count_nonzero(am & bd)) / max(1, int(am.sum()))
        recall = float(np.count_nonzero(bm & ad)) / max(1, int(bm.sum()))
        scores.append(2.0 * precision * recall / max(1e-12, precision + recall))
    return float(sum(scores) / len(scores))


def heldout_prototype_record(image: Image.Image, requested: str, targets: Iterable) -> dict:
    normalized = normalize_soft(image)
    scores = {}
    for target in targets:
        scores[target.id] = _heldout_f1_from_fields(normalized, normalize_soft(target.image))
    ordered = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    requested_score = float(scores[requested])
    best_other = max(float(v) for k, v in scores.items() if k != requested)
    return {
        'requested': requested,
        'top1': ordered[0][0] == requested,
        'top1Id': ordered[0][0],
        'targetF1': requested_score,
        'bestOtherF1': best_other,
        'margin': requested_score - best_other,
        'ranking': [k for k, _ in ordered],
    }
