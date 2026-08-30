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
sys.path.insert(0, str(OLD_DIR))
sys.path.insert(0, str(PREV_DIR))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OLD = _load('semantic_world_model_old_targets', OLD_DIR / 'semantic_targets.py')
PREV = _load('semantic_world_model_prev_targets', PREV_DIR / 'fresh_targets.py')
capacity = OLD.capacity
PROMPTS = ('arrow', 'key', 'mushroom', 'cloud', 'number-3', 'hourglass', 'bird', 'cactus')


def _line_target(prompt: str, groups):
    pts = [p for group in groups for p in group]
    return capacity.Target(prompt, 'semantic-world-model-v1', capacity._binary_points(pts))


def _circle(cx, cy, radius, samples=1800):
    return [
        (cx + radius * math.cos(2 * math.pi * i / samples), cy + radius * math.sin(2 * math.pi * i / samples))
        for i in range(samples)
    ]


def build_targets() -> tuple:
    out = []

    arrow = OLD._closed_polygon(((65, 168), (220, 168), (220, 92), (340, 200), (220, 308), (220, 232), (65, 232)), 500)
    out.append(_line_target('arrow', (arrow,)))

    key_head = _circle(122, 170, 62)
    key_shaft = OLD._sample_polyline(((178, 170), (326, 170)), 1300)
    key_tooth1 = OLD._sample_polyline(((275, 170), (275, 215), (300, 215), (300, 170)), 650)
    key_tooth2 = OLD._sample_polyline(((315, 170), (315, 200), (338, 200)), 450)
    out.append(_line_target('key', (key_head, key_shaft, key_tooth1, key_tooth2)))

    cap = capacity._bezier((72, 190), (105, 70), (295, 70), (328, 190), samples=2200)
    cap_base = capacity._bezier((328, 190), (285, 225), (115, 225), (72, 190), samples=1400)
    stem = OLD._closed_polygon(((166, 190), (234, 190), (246, 322), (154, 322)), 650)
    out.append(_line_target('mushroom', (cap, cap_base, stem)))

    cloud = capacity._catmull_closed(
        ((70, 235), (76, 178), (125, 158), (145, 103), (205, 105), (238, 135), (290, 128), (329, 173), (323, 231), (280, 265), (210, 272), (135, 268)),
        samples_per_segment=300,
    )
    out.append(_line_target('cloud', (cloud,)))

    three_top = capacity._bezier((120, 92), (285, 35), (330, 128), (205, 193), samples=1900)
    three_bottom = capacity._bezier((205, 193), (345, 238), (288, 357), (116, 307), samples=1900)
    out.append(_line_target('number-3', (three_top, three_bottom)))

    hourglass = OLD._closed_polygon(((105, 72), (295, 72), (235, 188), (295, 328), (105, 328), (165, 188)), 650)
    out.append(_line_target('hourglass', (hourglass,)))

    left_wing = capacity._bezier((65, 215), (125, 115), (178, 128), (200, 205), samples=1600)
    right_wing = capacity._bezier((200, 205), (222, 128), (278, 115), (338, 215), samples=1600)
    body = capacity._bezier((200, 205), (200, 230), (202, 255), (205, 286), samples=700)
    out.append(_line_target('bird', (left_wing, right_wing, body)))

    cactus = OLD._closed_polygon(((165, 330), (165, 235), (112, 235), (112, 170), (145, 170), (145, 205), (165, 205), (165, 85), (235, 85), (235, 190), (258, 190), (258, 145), (292, 145), (292, 225), (235, 225), (235, 330)), 700)
    out.append(_line_target('cactus', (cactus,)))

    if tuple(t.id for t in out) != PROMPTS:
        raise AssertionError('unseen target ordering drifted')
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
    overlap = sorted(set(fingerprints) & prior)
    if len(set(fingerprints)) != len(fingerprints):
        failures.append('unseen target fingerprints are not distinct')
    if overlap:
        failures.append(f'unseen semantic target overlaps prior target fingerprints: {overlap}')
    if tuple(t.id for t in targets) != PROMPTS:
        failures.append('unseen prompt rectangle/order drifted')
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
    print(__import__('json').dumps(target_contract(), indent=2, sort_keys=True))
