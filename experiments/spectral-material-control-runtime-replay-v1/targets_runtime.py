from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Sequence

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


V2 = _load('runtime_targets_v2', ROOT / 'experiments' / 'sampling-invariance-search-v2' / 'targets_v2.py')
TOP1 = _load('runtime_targets_top1', ROOT / 'experiments' / 'sampling-invariance-search-top1-confirmation-v1' / 'targets_top1.py')
OPERATOR = _load('runtime_targets_operator', ROOT / 'experiments' / 'spectral-material-control-operator-v1' / 'targets_operator.py')
ONE_D = _load('runtime_targets_1d', ROOT / 'experiments' / 'spectral-material-control-1d-confirmation-v1' / 'targets_1d.py')
PORTFOLIO = _load('runtime_targets_portfolio', ROOT / 'experiments' / 'spectral-material-control-1d-portfolio-v1' / 'targets_portfolio.py')


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_targets_runtime():
    targets = []

    def lines(target_id: str, family: str, groups: Sequence[Sequence[tuple[float, float]]]) -> None:
        targets.append(capacity.Target(target_id, family, capacity._binary_points([p for g in groups for p in g])))

    lines('runtime-components-1', 'disconnected-loops', (
        capacity._ellipse_points(118, 162, 37, 49, rotation=0.17),
        capacity._ellipse_points(276, 239, 47, 39, rotation=-0.21),
    ))
    lines('runtime-components-2', 'disconnected-loops', (
        capacity._ellipse_points(105, 132, 31, 38, rotation=-0.22),
        capacity._ellipse_points(284, 128, 36, 30, rotation=0.14),
        capacity._ellipse_points(211, 279, 43, 32, rotation=-0.11),
    ))
    lines('runtime-components-3', 'disconnected-loops', (
        capacity._ellipse_points(112, 112, 27, 33, rotation=0.19),
        capacity._ellipse_points(286, 126, 35, 25, rotation=-0.18),
        capacity._ellipse_points(108, 281, 31, 29, rotation=-0.12),
        capacity._ellipse_points(291, 276, 29, 36, rotation=0.16),
    ))

    lines('runtime-nested-1', 'nested-loops', (
        capacity._ellipse_points(198, 204, 113, 91, rotation=-0.16),
        capacity._ellipse_points(214, 190, 37, 28, rotation=0.21),
    ))
    outer = capacity._catmull_closed(((82, 187), (132, 105), (230, 83), (319, 164), (303, 259), (220, 318), (104, 289)))
    lines('runtime-nested-2', 'nested-loops', (
        outer,
        capacity._ellipse_points(154, 206, 24, 31, rotation=-0.13),
        capacity._ellipse_points(248, 193, 31, 24, rotation=0.20),
    ))
    lines('runtime-nested-3', 'nested-loops', (
        capacity._ellipse_points(201, 198, 115, 101, rotation=0.15),
        capacity._ellipse_points(158, 169, 22, 25, rotation=-0.18),
        capacity._ellipse_points(236, 184, 27, 20, rotation=0.12),
        capacity._ellipse_points(218, 246, 22, 27, rotation=-0.21),
    ))

    controls = (
        ((83, 181), (126, 104), (224, 88), (318, 149), (250, 211), (306, 291), (205, 319), (97, 270), (157, 217)),
        ((91, 224), (107, 129), (178, 91), (276, 103), (319, 188), (239, 177), (288, 299), (190, 321), (91, 279), (158, 238)),
        ((90, 158), (149, 89), (255, 104), (321, 188), (237, 198), (305, 274), (209, 319), (99, 270), (160, 198)),
    )
    for i, control in enumerate(controls, 1):
        lines(f'runtime-concave-{i}', 'concave-loops', (capacity._catmull_closed(control),))

    lines('runtime-network-1', 'open-networks', (
        capacity._bezier((66, 96), (146, 309), (258, 96), (333, 304)),
        capacity._bezier((67, 303), (164, 90), (239, 311), (334, 103)),
        capacity._bezier((99, 192), (164, 160), (241, 230), (306, 198)),
    ))
    lines('runtime-network-2', 'open-networks', (
        capacity._bezier((198, 191), (141, 151), (104, 115), (67, 78)),
        capacity._bezier((198, 191), (254, 148), (296, 122), (335, 107)),
        capacity._bezier((198, 191), (160, 252), (116, 292), (85, 329)),
        capacity._bezier((198, 191), (248, 238), (282, 291), (311, 329)),
    ))
    lines('runtime-network-3', 'open-networks', (
        capacity._bezier((66, 119), (149, 74), (254, 166), (335, 116)),
        capacity._bezier((65, 207), (151, 299), (251, 112), (337, 217)),
        capacity._bezier((69, 292), (160, 233), (255, 327), (335, 291)),
        capacity._bezier((110, 75), (174, 159), (231, 250), (291, 334)),
    ))

    targets.append(capacity.Target('runtime-dense-1', 'dense-regions', capacity._filled_target(lambda d: d.ellipse((96, 105, 307, 294), fill=capacity.FG))))

    def annulus(drawer):
        drawer.ellipse((82, 91, 318, 309), fill=capacity.FG)
        drawer.ellipse((151, 151, 252, 250), fill=capacity.BG)
    targets.append(capacity.Target('runtime-dense-2', 'dense-regions', capacity._filled_target(annulus)))

    def lobes(drawer):
        drawer.ellipse((78, 121, 211, 286), fill=capacity.FG)
        drawer.ellipse((195, 112, 326, 278), fill=capacity.FG)
        drawer.ellipse((163, 199, 239, 296), fill=capacity.FG)
    targets.append(capacity.Target('runtime-dense-3', 'dense-regions', capacity._filled_target(lobes)))

    if len(targets) != 15:
        raise AssertionError(f'runtime target count drifted: {len(targets)}')
    return tuple(targets)


def target_contract_runtime() -> dict:
    targets = build_targets_runtime()
    contract = capacity.target_contract(targets)
    prior = {_fingerprint(t.image) for t in capacity.build_targets()}
    prior.update(_fingerprint(t.image) for t in V2.build_targets_v2())
    prior.update(_fingerprint(t.image) for t in TOP1.build_targets_top1())
    prior.update(_fingerprint(t.image) for t in OPERATOR.build_targets_operator())
    prior.update(_fingerprint(t.image) for t in ONE_D.build_targets_1d())
    prior.update(_fingerprint(t.image) for t in PORTFOLIO.build_targets_portfolio())
    fingerprints = [_fingerprint(t.image) for t in targets]
    overlap = sorted(set(fingerprints) & prior)
    contract['disjointFromAllPriorSamplingTargets'] = not overlap
    contract['priorOverlap'] = overlap
    contract['fingerprints'] = fingerprints
    contract['valid'] = bool(contract['valid'] and not overlap)
    return contract


if __name__ == '__main__':
    import json
    print(json.dumps(target_contract_runtime(), indent=2, sort_keys=True))
