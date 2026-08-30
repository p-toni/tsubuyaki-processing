from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPACITY_DIR = ROOT / "experiments" / "sampling-invariance-v1"
V2_TARGETS_PATH = ROOT / "experiments" / "sampling-invariance-search-v2" / "targets_v2.py"
TOP1_TARGETS_PATH = ROOT / "experiments" / "sampling-invariance-search-top1-confirmation-v1" / "targets_top1.py"
sys.path.insert(0, str(CAPACITY_DIR))

import run_capacity

capacity = run_capacity.capacity


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v2 = _load("spectral_control_operator_v2_targets", V2_TARGETS_PATH)
top1 = _load("spectral_control_operator_top1_targets", TOP1_TARGETS_PATH)


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_targets_operator():
    targets = []

    def lines(target_id: str, family: str, groups: Sequence[Sequence[tuple[float, float]]]) -> None:
        points = [point for group in groups for point in group]
        targets.append(capacity.Target(target_id, family, capacity._binary_points(points)))

    lines(
        "operator-components-1",
        "disconnected-loops",
        (
            capacity._ellipse_points(126, 163, 43, 56, rotation=-0.17),
            capacity._ellipse_points(275, 239, 54, 42, rotation=0.21),
        ),
    )
    lines(
        "operator-components-2",
        "disconnected-loops",
        (
            capacity._ellipse_points(112, 139, 33, 41, rotation=0.24),
            capacity._ellipse_points(286, 151, 38, 32, rotation=-0.13),
            capacity._ellipse_points(201, 279, 45, 36, rotation=-0.09),
        ),
    )
    lines(
        "operator-components-3",
        "disconnected-loops",
        (
            capacity._ellipse_points(117, 119, 30, 34, rotation=-0.12),
            capacity._ellipse_points(283, 131, 34, 29, rotation=0.22),
            capacity._ellipse_points(126, 279, 36, 30, rotation=0.18),
            capacity._ellipse_points(288, 272, 30, 37, rotation=-0.20),
        ),
    )

    lines(
        "operator-nested-1",
        "nested-loops",
        (
            capacity._ellipse_points(198, 203, 119, 96, rotation=0.09),
            capacity._ellipse_points(219, 207, 39, 29, rotation=-0.21),
        ),
    )
    outer2 = capacity._catmull_closed(
        ((88, 174), (137, 96), (236, 88), (314, 164), (304, 260), (219, 315), (112, 286))
    )
    lines(
        "operator-nested-2",
        "nested-loops",
        (
            outer2,
            capacity._ellipse_points(164, 204, 25, 33, rotation=0.18),
            capacity._ellipse_points(244, 201, 33, 25, rotation=-0.19),
        ),
    )
    lines(
        "operator-nested-3",
        "nested-loops",
        (
            capacity._ellipse_points(204, 197, 116, 101, rotation=-0.16),
            capacity._ellipse_points(166, 171, 24, 22, rotation=0.13),
            capacity._ellipse_points(232, 179, 27, 20, rotation=-0.18),
            capacity._ellipse_points(219, 242, 23, 29, rotation=0.21),
        ),
    )

    concave_controls = (
        ((86, 184), (132, 99), (229, 91), (315, 151), (251, 215), (301, 291), (205, 316), (105, 265), (161, 207)),
        ((94, 224), (108, 128), (178, 91), (276, 103), (316, 188), (247, 178), (287, 285), (190, 315), (91, 278), (160, 235)),
        ((91, 161), (151, 92), (256, 105), (317, 188), (247, 198), (304, 276), (207, 317), (102, 268), (162, 199)),
    )
    for index, controls in enumerate(concave_controls, start=1):
        lines(f"operator-concave-{index}", "concave-loops", (capacity._catmull_closed(controls),))

    lines(
        "operator-network-1",
        "open-networks",
        (
            capacity._bezier((69, 108), (143, 306), (258, 96), (331, 292)),
            capacity._bezier((72, 291), (154, 89), (247, 309), (329, 115)),
            capacity._bezier((101, 186), (164, 159), (241, 232), (305, 209)),
        ),
    )
    lines(
        "operator-network-2",
        "open-networks",
        (
            capacity._bezier((203, 201), (151, 154), (111, 119), (74, 82)),
            capacity._bezier((203, 201), (254, 158), (293, 129), (332, 116)),
            capacity._bezier((203, 201), (169, 251), (129, 289), (91, 326)),
            capacity._bezier((203, 201), (246, 249), (279, 289), (307, 326)),
        ),
    )
    lines(
        "operator-network-3",
        "open-networks",
        (
            capacity._bezier((70, 132), (145, 78), (253, 177), (333, 128)),
            capacity._bezier((68, 205), (148, 296), (254, 110), (333, 215)),
            capacity._bezier((72, 291), (162, 224), (247, 325), (331, 289)),
            capacity._bezier((114, 79), (178, 159), (224, 252), (287, 329)),
        ),
    )

    targets.append(
        capacity.Target(
            "operator-dense-1",
            "dense-regions",
            capacity._filled_target(lambda d: d.ellipse((100, 110, 300, 292), fill=capacity.FG)),
        )
    )

    def draw_annulus(drawer) -> None:
        drawer.ellipse((90, 88, 310, 310), fill=capacity.FG)
        drawer.ellipse((145, 150, 255, 250), fill=capacity.BG)

    targets.append(capacity.Target("operator-dense-2", "dense-regions", capacity._filled_target(draw_annulus)))

    def draw_lobes(drawer) -> None:
        drawer.ellipse((83, 125, 207, 282), fill=capacity.FG)
        drawer.ellipse((198, 114, 322, 270), fill=capacity.FG)
        drawer.ellipse((157, 190, 239, 296), fill=capacity.FG)

    targets.append(capacity.Target("operator-dense-3", "dense-regions", capacity._filled_target(draw_lobes)))

    if len(targets) != 15:
        raise AssertionError(f"operator target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract_operator() -> dict:
    targets = build_targets_operator()
    contract = capacity.target_contract(targets)
    prior = {_fingerprint(target.image) for target in capacity.build_targets()}
    prior.update(_fingerprint(target.image) for target in v2.build_targets_v2())
    prior.update(_fingerprint(target.image) for target in top1.build_targets_top1())
    fingerprints = [_fingerprint(target.image) for target in targets]
    overlap = sorted(set(fingerprints) & prior)
    contract["disjointFromV1V2Top1"] = not overlap
    contract["priorOverlap"] = overlap
    contract["fingerprints"] = fingerprints
    contract["valid"] = bool(contract["valid"] and not overlap)
    return contract


if __name__ == "__main__":
    import json

    print(json.dumps(target_contract_operator(), indent=2, sort_keys=True))
