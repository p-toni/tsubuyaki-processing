from __future__ import annotations

import hashlib
import importlib.util
import math
import sys
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPACITY_DIR = ROOT / 'experiments' / 'sampling-invariance-v1'
sys.path.insert(0, str(CAPACITY_DIR))

import run_capacity
capacity = run_capacity.capacity


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V2 = _load('semantic_targets_v2', ROOT / 'experiments' / 'sampling-invariance-search-v2' / 'targets_v2.py')
TOP1 = _load('semantic_targets_top1', ROOT / 'experiments' / 'sampling-invariance-search-top1-confirmation-v1' / 'targets_top1.py')
OPERATOR = _load('semantic_targets_operator', ROOT / 'experiments' / 'spectral-material-control-operator-v1' / 'targets_operator.py')
ONE_D = _load('semantic_targets_1d', ROOT / 'experiments' / 'spectral-material-control-1d-confirmation-v1' / 'targets_1d.py')
PORTFOLIO = _load('semantic_targets_portfolio', ROOT / 'experiments' / 'spectral-material-control-1d-portfolio-v1' / 'targets_portfolio.py')
RUNTIME = _load('semantic_targets_runtime', ROOT / 'experiments' / 'spectral-material-control-runtime-replay-v1' / 'targets_runtime.py')

PROMPTS = ('heart', 'star', 'crescent', 'fish', 'butterfly', 'tree', 'letter-a', 'flower')


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _sample_polyline(points: Sequence[tuple[float, float]], samples_per_segment: int = 420) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for a, b in zip(points, points[1:]):
        for i in range(samples_per_segment):
            t = i / max(1, samples_per_segment - 1)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def _closed_polygon(points: Sequence[tuple[float, float]], samples_per_segment: int = 420) -> list[tuple[float, float]]:
    return _sample_polyline(tuple(points) + (points[0],), samples_per_segment)


def _parametric(fn, samples: int = 3200) -> list[tuple[float, float]]:
    return [fn(2.0 * math.pi * i / samples) for i in range(samples)]


def _line_target(prompt: str, groups: Iterable[Sequence[tuple[float, float]]]):
    pts = [p for group in groups for p in group]
    return capacity.Target(prompt, 'semantic-shape', capacity._binary_points(pts))


def build_semantic_targets() -> tuple:
    targets = []

    # Classic analytic heart outline, centered and vertically balanced.
    heart = _parametric(
        lambda q: (
            200.0 + 7.0 * 16.0 * math.sin(q) ** 3,
            198.0 - 7.0 * (13.0 * math.cos(q) - 5.0 * math.cos(2*q) - 2.0 * math.cos(3*q) - math.cos(4*q)),
        )
    )
    targets.append(_line_target('heart', (heart,)))

    # Five-point star outline.
    star_vertices = []
    for i in range(10):
        q = -math.pi / 2 + i * math.pi / 5
        r = 118.0 if i % 2 == 0 else 48.0
        star_vertices.append((200.0 + r * math.cos(q), 202.0 + r * math.sin(q)))
    targets.append(_line_target('star', (_closed_polygon(star_vertices),)))

    # Single strongly concave loop reading as a crescent facing right.
    crescent = capacity._catmull_closed(
        ((219, 75), (143, 92), (91, 158), (88, 232), (139, 306), (219, 326),
         (178, 278), (160, 235), (158, 190), (174, 130)),
        samples_per_segment=360,
    )
    targets.append(_line_target('crescent', (crescent,)))

    # Fish: body, tail, and eye. Components intentionally touch/overlap at the tail root.
    fish_body = capacity._ellipse_points(178, 203, 88, 58, rotation=-0.04, samples=2400)
    fish_tail = _closed_polygon(((257, 201), (330, 143), (310, 202), (331, 261), (257, 201)), 360)
    fish_eye = capacity._ellipse_points(135, 188, 7, 7, samples=700)
    targets.append(_line_target('fish', (fish_body, fish_tail, fish_eye)))

    # Butterfly: four wings plus central body/antennae.
    wing_lu = capacity._catmull_closed(((193, 190), (145, 96), (72, 91), (82, 174), (153, 208)), samples_per_segment=300)
    wing_ll = capacity._catmull_closed(((192, 211), (148, 217), (91, 269), (130, 319), (188, 236)), samples_per_segment=300)
    wing_ru = [(400-x, y) for x, y in wing_lu]
    wing_rl = [(400-x, y) for x, y in wing_ll]
    body = _sample_polyline(((200, 132), (200, 272)), 1200)
    antenna_l = capacity._bezier((199, 145), (179, 111), (164, 96), (151, 82), samples=700)
    antenna_r = capacity._bezier((201, 145), (221, 111), (236, 96), (249, 82), samples=700)
    targets.append(_line_target('butterfly', (wing_lu, wing_ll, wing_ru, wing_rl, body, antenna_l, antenna_r)))

    # Tree skeleton: trunk with asymmetric recursive-looking branches.
    trunk = capacity._bezier((201, 325), (199, 274), (203, 216), (201, 163), samples=1600)
    branches = (
        capacity._bezier((201, 246), (174, 222), (142, 201), (102, 185), samples=950),
        capacity._bezier((201, 232), (231, 212), (264, 184), (305, 166), samples=950),
        capacity._bezier((201, 201), (176, 176), (151, 142), (127, 109), samples=850),
        capacity._bezier((202, 194), (225, 168), (250, 139), (271, 105), samples=850),
        capacity._bezier((145, 203), (127, 176), (111, 150), (94, 126), samples=700),
        capacity._bezier((259, 188), (278, 164), (293, 143), (314, 124), samples=700),
    )
    targets.append(_line_target('tree', (trunk, *branches)))

    # Uppercase A as an explicit open network.
    a_left = _sample_polyline(((104, 311), (198, 83)), 1800)
    a_right = _sample_polyline(((198, 83), (303, 311)), 1800)
    a_bar = _sample_polyline(((145, 213), (258, 213)), 1000)
    targets.append(_line_target('letter-a', (a_left, a_right, a_bar)))

    # Five-petal flower outline + center + stem/leaves.
    flower = _parametric(
        lambda q: (
            200.0 + (74.0 + 33.0 * math.cos(5*q)) * math.cos(q),
            171.0 + (74.0 + 33.0 * math.cos(5*q)) * math.sin(q),
        ),
        samples=3600,
    )
    flower_center = capacity._ellipse_points(200, 171, 24, 24, samples=1000)
    stem = capacity._bezier((200, 238), (201, 267), (199, 298), (201, 329), samples=1100)
    leaf_l = capacity._catmull_closed(((199, 282), (170, 262), (145, 279), (171, 299)), samples_per_segment=240)
    leaf_r = [(400-x, y+11) for x, y in leaf_l]
    targets.append(_line_target('flower', (flower, flower_center, stem, leaf_l, leaf_r)))

    if tuple(t.id for t in targets) != PROMPTS:
        raise AssertionError('semantic prompt ordering drifted')
    return tuple(targets)


def _all_prior_fingerprints() -> set[str]:
    prior = {_fingerprint(t.image) for t in capacity.build_targets()}
    prior.update(_fingerprint(t.image) for t in V2.build_targets_v2())
    prior.update(_fingerprint(t.image) for t in TOP1.build_targets_top1())
    prior.update(_fingerprint(t.image) for t in OPERATOR.build_targets_operator())
    prior.update(_fingerprint(t.image) for t in ONE_D.build_targets_1d())
    prior.update(_fingerprint(t.image) for t in PORTFOLIO.build_targets_portfolio())
    prior.update(_fingerprint(t.image) for t in RUNTIME.build_targets_runtime())
    return prior


def semantic_target_contract() -> dict:
    targets = build_semantic_targets()
    base = capacity.target_contract(targets)
    # target_contract expects five structural families; semantic v1 intentionally has one
    # semantic family, so preserve its per-target support/span checks while replacing only
    # the old 5x3 rectangle assertion with the frozen eight-concept rectangle.
    structural_failures = [f for f in base['failures'] if not f.startswith('target family rectangle invalid:')]
    fingerprints = [_fingerprint(t.image) for t in targets]
    overlap = sorted(set(fingerprints) & _all_prior_fingerprints())
    distinct = len(set(fingerprints)) == len(fingerprints)
    failures = list(structural_failures)
    if tuple(t.id for t in targets) != PROMPTS:
        failures.append('prompt rectangle/order drifted')
    if not distinct:
        failures.append('semantic target fingerprints are not distinct')
    if overlap:
        failures.append(f'semantic target overlaps prior target fingerprints: {overlap}')
    return {
        'valid': not failures,
        'failures': failures,
        'prompts': list(PROMPTS),
        'targets': base['targets'],
        'fingerprints': fingerprints,
        'distinctFingerprints': distinct,
        'priorOverlap': overlap,
        'disjointFromPriorTargets': not overlap,
    }


def resolve_prompt(prompt: str):
    normalized = str(prompt).strip().lower().replace('_', '-')
    aliases = {'a': 'letter-a', 'letter a': 'letter-a'}
    normalized = aliases.get(normalized, normalized)
    targets = {t.id: t for t in build_semantic_targets()}
    if normalized not in targets:
        raise KeyError(f'unsupported semantic-shape-v1 prompt {prompt!r}')
    return targets[normalized]


if __name__ == '__main__':
    import json
    print(json.dumps(semantic_target_contract(), indent=2, sort_keys=True))
