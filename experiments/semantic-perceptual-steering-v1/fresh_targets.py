from __future__ import annotations

import hashlib
import importlib.util
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD_DIR = ROOT / 'experiments' / 'semantic-shape-steering-v1'
sys.path.insert(0, str(OLD_DIR))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OLD = _load('semantic_shape_v1_targets_for_perceptual_followup', OLD_DIR / 'semantic_targets.py')
capacity = OLD.capacity
PROMPTS = ('diamond', 'spiral', 'lightning', 'leaf', 'umbrella', 'crown', 'letter-s', 'sailboat')


def _line_target(prompt: str, groups):
    pts = [p for group in groups for p in group]
    return capacity.Target(prompt, 'semantic-perceptual-v1', capacity._binary_points(pts))


def build_targets() -> tuple:
    out = []

    out.append(_line_target('diamond', (
        OLD._closed_polygon(((200, 62), (335, 200), (200, 338), (65, 200)), 500),
    )))

    spiral = []
    turns = 2.15
    samples = 3500
    for i in range(samples):
        t = i / (samples - 1)
        q = -math.pi / 2 + turns * 2 * math.pi * t
        r = 18 + 112 * t
        spiral.append((200 + r * math.cos(q), 200 + r * math.sin(q)))
    out.append(_line_target('spiral', (spiral,)))

    out.append(_line_target('lightning', (
        OLD._closed_polygon(((224, 54), (113, 211), (183, 211), (145, 346), (292, 164), (218, 164)), 450),
    )))

    leaf_outline = capacity._catmull_closed(
        ((200, 65), (275, 105), (320, 193), (270, 286), (200, 335), (130, 286), (80, 193), (125, 105)),
        samples_per_segment=360,
    )
    leaf_vein = capacity._bezier((200, 320), (196, 250), (202, 165), (200, 82), samples=1200)
    out.append(_line_target('leaf', (leaf_outline, leaf_vein)))

    canopy = []
    canopy += capacity._bezier((72, 195), (95, 90), (305, 90), (328, 195), samples=1800)
    canopy += capacity._bezier((328, 195), (300, 175), (274, 175), (250, 195), samples=500)
    canopy += capacity._bezier((250, 195), (226, 175), (202, 175), (178, 195), samples=500)
    canopy += capacity._bezier((178, 195), (154, 175), (128, 175), (104, 195), samples=500)
    canopy += capacity._bezier((104, 195), (92, 190), (82, 190), (72, 195), samples=300)
    shaft = OLD._sample_polyline(((200, 135), (200, 305)), 1200)
    hook = capacity._bezier((200, 305), (202, 350), (150, 350), (150, 315), samples=700)
    rib_l = capacity._bezier((200, 135), (185, 160), (170, 178), (178, 195), samples=500)
    rib_r = capacity._bezier((200, 135), (220, 160), (238, 178), (250, 195), samples=500)
    out.append(_line_target('umbrella', (canopy, shaft, hook, rib_l, rib_r)))

    crown = OLD._closed_polygon(((78, 288), (72, 128), (142, 205), (200, 88), (258, 205), (328, 128), (322, 288)), 450)
    crown_base = OLD._sample_polyline(((78, 288), (322, 288)), 900)
    out.append(_line_target('crown', (crown, crown_base)))

    s_top = capacity._bezier((282, 93), (215, 50), (112, 75), (112, 155), samples=1500)
    s_mid = capacity._bezier((112, 155), (112, 225), (288, 175), (288, 255), samples=1500)
    s_bottom = capacity._bezier((288, 255), (288, 332), (180, 350), (112, 307), samples=1500)
    out.append(_line_target('letter-s', (s_top, s_mid, s_bottom)))

    hull = OLD._closed_polygon(((88, 260), (312, 260), (267, 312), (133, 312)), 450)
    mast = OLD._sample_polyline(((200, 90), (200, 260)), 1000)
    sail_l = OLD._closed_polygon(((194, 105), (194, 245), (105, 245)), 450)
    sail_r = OLD._closed_polygon(((207, 118), (207, 245), (292, 245)), 450)
    water_l = capacity._bezier((75, 333), (125, 318), (165, 348), (205, 333), samples=500)
    water_r = capacity._bezier((205, 333), (245, 318), (285, 348), (330, 333), samples=500)
    out.append(_line_target('sailboat', (hull, mast, sail_l, sail_r, water_l, water_r)))

    if tuple(t.id for t in out) != PROMPTS:
        raise AssertionError('fresh semantic prompt ordering drifted')
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
    overlap = sorted(set(fingerprints) & prior)
    if len(set(fingerprints)) != len(fingerprints):
        failures.append('fresh semantic target fingerprints are not distinct')
    if overlap:
        failures.append(f'fresh semantic target overlaps prior target fingerprints: {overlap}')
    if tuple(t.id for t in targets) != PROMPTS:
        failures.append('fresh prompt rectangle/order drifted')
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


def resolve_prompt(prompt: str):
    normalized = str(prompt).strip().lower().replace('_', '-')
    aliases = {'s': 'letter-s', 'letter s': 'letter-s', 'bolt': 'lightning', 'boat': 'sailboat'}
    normalized = aliases.get(normalized, normalized)
    by_id = {t.id: t for t in build_targets()}
    if normalized not in by_id:
        raise KeyError(f'unsupported semantic-perceptual-v1 prompt {prompt!r}')
    return by_id[normalized]


if __name__ == '__main__':
    import json
    print(json.dumps(target_contract(), indent=2, sort_keys=True))
