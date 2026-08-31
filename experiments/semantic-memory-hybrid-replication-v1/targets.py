from __future__ import annotations

import hashlib
import importlib.util
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD_DIR = ROOT / 'experiments' / 'semantic-shape-steering-v1'
PREV_DIR = ROOT / 'experiments' / 'semantic-perceptual-steering-v1'
UNSEEN_DIR = ROOT / 'experiments' / 'semantic-world-model-navigation-v1'
HYBRID_DIR = ROOT / 'experiments' / 'semantic-breadth-memory-hybrid-v1'
for p in (OLD_DIR, PREV_DIR, UNSEEN_DIR, HYBRID_DIR):
    sys.path.insert(0, str(p))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OLD = _load('semantic_replication_old_targets', OLD_DIR / 'semantic_targets.py')
PREV = _load('semantic_replication_prev_targets', PREV_DIR / 'fresh_targets.py')
UNSEEN = _load('semantic_replication_unseen_targets', UNSEEN_DIR / 'unseen_targets.py')
HYBRID = _load('semantic_replication_hybrid_targets', HYBRID_DIR / 'targets.py')
capacity = OLD.capacity
PROMPTS = ('star', 'tree', 'fish', 'chair', 'anchor', 'guitar', 'butterfly', 'bicycle')


def _line_target(prompt: str, groups):
    pts = [p for group in groups for p in group]
    return capacity.Target(prompt, 'semantic-memory-hybrid-replication-v1', capacity._binary_points(pts))


def _circle(cx: float, cy: float, radius: float, samples: int = 1500):
    return [
        (cx + radius * math.cos(2 * math.pi * i / samples), cy + radius * math.sin(2 * math.pi * i / samples))
        for i in range(samples)
    ]


def build_targets() -> tuple:
    out = []

    star_pts = []
    for i in range(10):
        q = -math.pi / 2 + i * math.pi / 5
        r = 135 if i % 2 == 0 else 58
        star_pts.append((200 + r * math.cos(q), 200 + r * math.sin(q)))
    out.append(_line_target('star', (OLD._closed_polygon(tuple(star_pts), 700),)))

    crown_l = OLD._closed_polygon(((200, 55), (92, 210), (145, 210), (72, 302), (328, 302), (255, 210), (308, 210)), 650)
    trunk = OLD._closed_polygon(((172, 302), (228, 302), (228, 352), (172, 352)), 350)
    out.append(_line_target('tree', (crown_l, trunk)))

    fish_body = capacity._catmull_closed(
        ((85, 200), (125, 132), (220, 118), (292, 165), (315, 200), (292, 235), (220, 282), (125, 268)),
        samples_per_segment=300,
    )
    fish_tail = OLD._closed_polygon(((88, 200), (42, 128), (50, 200), (42, 272)), 500)
    eye = _circle(255, 181, 10, 600)
    out.append(_line_target('fish', (fish_body, fish_tail, eye)))

    chair_back = OLD._closed_polygon(((115, 68), (265, 68), (265, 205), (115, 205)), 500)
    seat = OLD._closed_polygon(((105, 205), (286, 205), (286, 245), (105, 245)), 450)
    leg_l = OLD._sample_polyline(((128, 245), (105, 340)), 650)
    leg_r = OLD._sample_polyline(((262, 245), (286, 340)), 650)
    out.append(_line_target('chair', (chair_back, seat, leg_l, leg_r)))

    ring = _circle(200, 72, 31, 1000)
    shaft = OLD._sample_polyline(((200, 103), (200, 286)), 1150)
    crossbar = OLD._sample_polyline(((125, 155), (275, 155)), 850)
    left_curve = capacity._bezier((200, 286), (165, 338), (92, 329), (72, 258), samples=1000)
    right_curve = capacity._bezier((200, 286), (235, 338), (308, 329), (328, 258), samples=1000)
    fluke_l = OLD._sample_polyline(((72, 258), (58, 290), (96, 280)), 500)
    fluke_r = OLD._sample_polyline(((328, 258), (342, 290), (304, 280)), 500)
    out.append(_line_target('anchor', (ring, shaft, crossbar, left_curve, right_curve, fluke_l, fluke_r)))

    guitar_body = capacity._catmull_closed(
        ((188, 352), (118, 332), (102, 275), (135, 231), (119, 187), (151, 147), (200, 154), (249, 147), (281, 187), (265, 231), (298, 275), (282, 332)),
        samples_per_segment=250,
    )
    neck = OLD._closed_polygon(((184, 155), (216, 155), (222, 62), (178, 62)), 450)
    head = OLD._closed_polygon(((176, 62), (224, 62), (230, 35), (170, 35)), 350)
    sound = _circle(200, 235, 28, 1000)
    out.append(_line_target('guitar', (guitar_body, neck, head, sound)))

    wing_ul = capacity._catmull_closed(((192, 184), (135, 75), (58, 82), (72, 178), (145, 205)), samples_per_segment=280)
    wing_ll = capacity._catmull_closed(((151, 210), (72, 206), (82, 316), (166, 274), (193, 223)), samples_per_segment=280)
    wing_ur = capacity._catmull_closed(((208, 184), (265, 75), (342, 82), (328, 178), (255, 205)), samples_per_segment=280)
    wing_lr = capacity._catmull_closed(((249, 210), (328, 206), (318, 316), (234, 274), (207, 223)), samples_per_segment=280)
    body = capacity._ellipse_points(200, 215, 17, 105, samples=1600)
    antenna_l = capacity._bezier((193, 112), (168, 75), (153, 53), (137, 44), samples=500)
    antenna_r = capacity._bezier((207, 112), (232, 75), (247, 53), (263, 44), samples=500)
    out.append(_line_target('butterfly', (wing_ul, wing_ll, wing_ur, wing_lr, body, antenna_l, antenna_r)))

    wheel_l = _circle(112, 276, 69, 1900)
    wheel_r = _circle(291, 276, 69, 1900)
    frame = OLD._sample_polyline(((112, 276), (178, 182), (235, 276), (112, 276), (203, 276), (178, 182)), 1200)
    fork = OLD._sample_polyline(((235, 276), (260, 153), (291, 276)), 900)
    handle = OLD._sample_polyline(((250, 153), (285, 143), (298, 153)), 500)
    seat_post = OLD._sample_polyline(((178, 182), (165, 145)), 450)
    seat = OLD._sample_polyline(((143, 145), (181, 145)), 400)
    out.append(_line_target('bicycle', (wheel_l, wheel_r, frame, fork, handle, seat_post, seat)))

    if tuple(t.id for t in out) != PROMPTS:
        raise AssertionError('replication semantic target ordering drifted')
    return tuple(out)


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def target_contract() -> dict:
    targets = build_targets()
    base = capacity.target_contract(targets)
    failures = [f for f in base['failures'] if not f.startswith('target family rectangle invalid:')]
    fingerprints = [_fingerprint(t.image) for t in targets]
    prior = set(OLD._all_prior_fingerprints())
    prior.update(_fingerprint(t.image) for t in OLD.build_semantic_targets())
    prior.update(_fingerprint(t.image) for t in PREV.build_targets())
    prior.update(_fingerprint(t.image) for t in UNSEEN.build_targets())
    prior.update(_fingerprint(t.image) for t in HYBRID.build_targets())
    overlap = sorted(set(fingerprints) & prior)
    if len(set(fingerprints)) != len(fingerprints):
        failures.append('replication semantic target fingerprints are not distinct')
    if overlap:
        failures.append(f'replication semantic target overlaps prior target fingerprints: {overlap}')
    if tuple(t.id for t in targets) != PROMPTS:
        failures.append('replication semantic prompt rectangle/order drifted')
    return {
        'valid': not failures,
        'failures': failures,
        'prompts': list(PROMPTS),
        'targets': base['targets'],
        'fingerprints': fingerprints,
        'distinctFingerprints': len(set(fingerprints)) == len(fingerprints),
        'priorOverlap': overlap,
        'disjointFromPriorTargets': not overlap,
    }


if __name__ == '__main__':
    import json
    print(json.dumps(target_contract(), indent=2, sort_keys=True))
