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
sys.path.insert(0, str(OLD_DIR))
sys.path.insert(0, str(PREV_DIR))
sys.path.insert(0, str(UNSEEN_DIR))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OLD = _load('semantic_hybrid_old_targets', OLD_DIR / 'semantic_targets.py')
PREV = _load('semantic_hybrid_prev_targets', PREV_DIR / 'fresh_targets.py')
UNSEEN = _load('semantic_hybrid_unseen_targets', UNSEEN_DIR / 'unseen_targets.py')
capacity = OLD.capacity
PROMPTS = ('glasses', 'cup', 'ladder', 'house', 'envelope', 'snowman', 'scissors', 'rocket')


def _line_target(prompt: str, groups):
    pts = [p for group in groups for p in group]
    return capacity.Target(prompt, 'semantic-breadth-memory-hybrid-v1', capacity._binary_points(pts))


def _circle(cx: float, cy: float, radius: float, samples: int = 1600):
    return [
        (cx + radius * math.cos(2 * math.pi * i / samples), cy + radius * math.sin(2 * math.pi * i / samples))
        for i in range(samples)
    ]


def build_targets() -> tuple:
    out = []

    left_lens = capacity._ellipse_points(132, 194, 66, 54, samples=1900)
    right_lens = capacity._ellipse_points(268, 194, 66, 54, samples=1900)
    bridge = capacity._bezier((198, 188), (190, 170), (210, 170), (202, 188), samples=450)
    left_arm = OLD._sample_polyline(((67, 183), (42, 160)), 450)
    right_arm = OLD._sample_polyline(((333, 183), (358, 160)), 450)
    out.append(_line_target('glasses', (left_lens, right_lens, bridge, left_arm, right_arm)))

    cup_body = capacity._bezier((112, 120), (110, 235), (130, 300), (200, 310), samples=1350)
    cup_body += capacity._bezier((200, 310), (270, 300), (290, 235), (288, 120), samples=1350)
    rim = OLD._sample_polyline(((112, 120), (288, 120)), 900)
    handle_outer = capacity._bezier((286, 160), (355, 145), (360, 260), (284, 258), samples=1000)
    handle_inner = capacity._bezier((286, 185), (330, 175), (332, 230), (286, 232), samples=700)
    out.append(_line_target('cup', (cup_body, rim, handle_outer, handle_inner)))

    rail_l = OLD._sample_polyline(((128, 68), (128, 332)), 1500)
    rail_r = OLD._sample_polyline(((272, 68), (272, 332)), 1500)
    rungs = tuple(OLD._sample_polyline(((128, y), (272, y)), 650) for y in (105, 153, 201, 249, 297))
    out.append(_line_target('ladder', (rail_l, rail_r, *rungs)))

    body = OLD._closed_polygon(((95, 188), (305, 188), (305, 330), (95, 330)), 500)
    roof = OLD._closed_polygon(((72, 188), (200, 72), (328, 188)), 500)
    door = OLD._closed_polygon(((169, 244), (231, 244), (231, 330), (169, 330)), 380)
    out.append(_line_target('house', (body, roof, door)))

    box = OLD._closed_polygon(((75, 105), (325, 105), (325, 295), (75, 295)), 520)
    flap_l = OLD._sample_polyline(((75, 105), (200, 218), (325, 105)), 750)
    fold_l = OLD._sample_polyline(((75, 295), (168, 207)), 650)
    fold_r = OLD._sample_polyline(((325, 295), (232, 207)), 650)
    out.append(_line_target('envelope', (box, flap_l, fold_l, fold_r)))

    bottom = _circle(200, 265, 82, samples=2100)
    middle = _circle(200, 165, 61, samples=1800)
    head = _circle(200, 78, 43, samples=1500)
    arm_l = OLD._sample_polyline(((143, 167), (84, 126), (61, 94)), 700)
    arm_r = OLD._sample_polyline(((257, 167), (316, 126), (339, 94)), 700)
    out.append(_line_target('snowman', (bottom, middle, head, arm_l, arm_r)))

    handle_l = _circle(128, 276, 45, samples=1500)
    handle_r = _circle(272, 276, 45, samples=1500)
    blade_l = OLD._sample_polyline(((158, 244), (301, 88)), 1500)
    blade_r = OLD._sample_polyline(((242, 244), (99, 88)), 1500)
    pivot = _circle(200, 200, 14, samples=700)
    out.append(_line_target('scissors', (handle_l, handle_r, blade_l, blade_r, pivot)))

    rocket_body = capacity._catmull_closed(
        ((200, 52), (246, 105), (262, 220), (234, 290), (200, 328), (166, 290), (138, 220), (154, 105)),
        samples_per_segment=310,
    )
    fin_l = OLD._closed_polygon(((156, 220), (92, 292), (163, 276)), 420)
    fin_r = OLD._closed_polygon(((244, 220), (308, 292), (237, 276)), 420)
    window = _circle(200, 152, 31, samples=1200)
    exhaust_l = OLD._sample_polyline(((182, 317), (165, 354)), 400)
    exhaust_r = OLD._sample_polyline(((218, 317), (235, 354)), 400)
    out.append(_line_target('rocket', (rocket_body, fin_l, fin_r, window, exhaust_l, exhaust_r)))

    if tuple(t.id for t in out) != PROMPTS:
        raise AssertionError('hybrid semantic target ordering drifted')
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
    overlap = sorted(set(fingerprints) & prior)
    if len(set(fingerprints)) != len(fingerprints):
        failures.append('hybrid semantic target fingerprints are not distinct')
    if overlap:
        failures.append(f'hybrid semantic target overlaps prior target fingerprints: {overlap}')
    if tuple(t.id for t in targets) != PROMPTS:
        failures.append('hybrid semantic prompt rectangle/order drifted')
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
