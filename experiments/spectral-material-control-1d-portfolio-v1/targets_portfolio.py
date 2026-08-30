from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPACITY_DIR = ROOT / "experiments" / "sampling-invariance-v1"
sys.path.insert(0, str(CAPACITY_DIR))

import run_capacity
capacity = run_capacity.capacity


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


V2 = _load("spectral_portfolio_v2_targets", ROOT / "experiments" / "sampling-invariance-search-v2" / "targets_v2.py")
TOP1 = _load("spectral_portfolio_top1_targets", ROOT / "experiments" / "sampling-invariance-search-top1-confirmation-v1" / "targets_top1.py")
OPERATOR = _load("spectral_portfolio_operator_targets", ROOT / "experiments" / "spectral-material-control-operator-v1" / "targets_operator.py")
ONE_D = _load("spectral_portfolio_1d_targets", ROOT / "experiments" / "spectral-material-control-1d-confirmation-v1" / "targets_1d.py")


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_targets_portfolio():
    targets = []

    def lines(target_id: str, family: str, groups: Sequence[Sequence[tuple[float, float]]]) -> None:
        targets.append(capacity.Target(target_id, family, capacity._binary_points([p for g in groups for p in g])))

    lines("portfolio-components-1", "disconnected-loops", (
        capacity._ellipse_points(130, 155, 41, 53, rotation=-0.14),
        capacity._ellipse_points(270, 252, 51, 43, rotation=0.18),
    ))
    lines("portfolio-components-2", "disconnected-loops", (
        capacity._ellipse_points(116, 145, 34, 42, rotation=0.20),
        capacity._ellipse_points(282, 148, 39, 33, rotation=-0.16),
        capacity._ellipse_points(205, 276, 46, 35, rotation=0.10),
    ))
    lines("portfolio-components-3", "disconnected-loops", (
        capacity._ellipse_points(123, 121, 29, 36, rotation=-0.18),
        capacity._ellipse_points(280, 136, 37, 27, rotation=0.20),
        capacity._ellipse_points(122, 273, 35, 32, rotation=0.14),
        capacity._ellipse_points(282, 268, 32, 39, rotation=-0.17),
    ))

    lines("portfolio-nested-1", "nested-loops", (
        capacity._ellipse_points(202, 201, 117, 98, rotation=0.12),
        capacity._ellipse_points(221, 198, 40, 30, rotation=-0.17),
    ))
    outer = capacity._catmull_closed(((90, 179), (140, 99), (241, 92), (312, 170), (296, 269), (211, 312), (106, 282)))
    lines("portfolio-nested-2", "nested-loops", (
        outer,
        capacity._ellipse_points(161, 201, 26, 34, rotation=0.16),
        capacity._ellipse_points(241, 198, 34, 26, rotation=-0.18),
    ))
    lines("portfolio-nested-3", "nested-loops", (
        capacity._ellipse_points(203, 199, 119, 95, rotation=-0.13),
        capacity._ellipse_points(162, 174, 24, 23, rotation=0.16),
        capacity._ellipse_points(230, 180, 29, 21, rotation=-0.15),
        capacity._ellipse_points(226, 241, 24, 29, rotation=0.19),
    ))

    controls = (
        ((88, 192), (136, 103), (235, 94), (312, 158), (244, 218), (295, 298), (198, 314), (102, 260), (166, 213)),
        ((97, 219), (113, 124), (185, 96), (282, 108), (313, 195), (245, 181), (281, 292), (184, 313), (95, 274), (164, 233)),
        ((96, 165), (156, 96), (260, 109), (314, 193), (242, 203), (299, 281), (202, 312), (105, 264), (168, 203)),
    )
    for i, control in enumerate(controls, 1):
        lines(f"portfolio-concave-{i}", "concave-loops", (capacity._catmull_closed(control),))

    lines("portfolio-network-1", "open-networks", (
        capacity._bezier((73, 104), (149, 301), (253, 104), (326, 297)),
        capacity._bezier((75, 296), (158, 97), (243, 304), (326, 111)),
        capacity._bezier((106, 196), (160, 168), (246, 225), (299, 203)),
    ))
    lines("portfolio-network-2", "open-networks", (
        capacity._bezier((201, 196), (147, 157), (110, 121), (78, 87)),
        capacity._bezier((201, 196), (251, 153), (290, 126), (328, 113)),
        capacity._bezier((201, 196), (166, 247), (124, 286), (94, 322)),
        capacity._bezier((201, 196), (244, 241), (275, 286), (302, 322)),
    ))
    lines("portfolio-network-3", "open-networks", (
        capacity._bezier((75, 127), (151, 82), (248, 172), (328, 124)),
        capacity._bezier((74, 201), (153, 291), (247, 118), (329, 211)),
        capacity._bezier((78, 283), (159, 229), (249, 318), (327, 284)),
        capacity._bezier((119, 82), (176, 163), (228, 245), (281, 327)),
    ))

    targets.append(capacity.Target(
        "portfolio-dense-1", "dense-regions",
        capacity._filled_target(lambda d: d.ellipse((102, 101, 302, 299), fill=capacity.FG)),
    ))

    def annulus(drawer):
        drawer.ellipse((88, 96, 312, 304), fill=capacity.FG)
        drawer.ellipse((143, 157, 259, 245), fill=capacity.BG)
    targets.append(capacity.Target("portfolio-dense-2", "dense-regions", capacity._filled_target(annulus)))

    def lobes(drawer):
        drawer.ellipse((80, 120, 216, 288), fill=capacity.FG)
        drawer.ellipse((188, 111, 324, 279), fill=capacity.FG)
        drawer.ellipse((160, 187, 241, 300), fill=capacity.FG)
    targets.append(capacity.Target("portfolio-dense-3", "dense-regions", capacity._filled_target(lobes)))

    if len(targets) != 15:
        raise AssertionError(f"portfolio target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract_portfolio() -> dict:
    targets = build_targets_portfolio()
    contract = capacity.target_contract(targets)
    prior = {_fingerprint(t.image) for t in capacity.build_targets()}
    prior.update(_fingerprint(t.image) for t in V2.build_targets_v2())
    prior.update(_fingerprint(t.image) for t in TOP1.build_targets_top1())
    prior.update(_fingerprint(t.image) for t in OPERATOR.build_targets_operator())
    prior.update(_fingerprint(t.image) for t in ONE_D.build_targets_1d())
    fingerprints = [_fingerprint(t.image) for t in targets]
    overlap = sorted(set(fingerprints) & prior)
    contract["disjointFromAllPriorSamplingTargets"] = not overlap
    contract["priorOverlap"] = overlap
    contract["fingerprints"] = fingerprints
    contract["valid"] = bool(contract["valid"] and not overlap)
    return contract


if __name__ == "__main__":
    import json
    print(json.dumps(target_contract_portfolio(), indent=2, sort_keys=True))
