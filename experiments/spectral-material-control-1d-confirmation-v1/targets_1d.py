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


V2 = _load("spectral_1d_v2_targets", ROOT / "experiments" / "sampling-invariance-search-v2" / "targets_v2.py")
TOP1 = _load("spectral_1d_top1_targets", ROOT / "experiments" / "sampling-invariance-search-top1-confirmation-v1" / "targets_top1.py")
OPERATOR = _load("spectral_1d_operator_targets", ROOT / "experiments" / "spectral-material-control-operator-v1" / "targets_operator.py")


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_targets_1d():
    targets = []

    def lines(target_id: str, family: str, groups: Sequence[Sequence[tuple[float, float]]]) -> None:
        points = [point for group in groups for point in group]
        targets.append(capacity.Target(target_id, family, capacity._binary_points(points)))

    # Disconnected loops.
    lines(
        "one-d-components-1",
        "disconnected-loops",
        (
            capacity._ellipse_points(137, 158, 47, 52, rotation=0.16),
            capacity._ellipse_points(263, 247, 49, 45, rotation=-0.23),
        ),
    )
    lines(
        "one-d-components-2",
        "disconnected-loops",
        (
            capacity._ellipse_points(121, 147, 35, 39, rotation=-0.21),
            capacity._ellipse_points(278, 143, 40, 31, rotation=0.17),
            capacity._ellipse_points(211, 272, 43, 38, rotation=0.12),
        ),
    )
    lines(
        "one-d-components-3",
        "disconnected-loops",
        (
            capacity._ellipse_points(129, 127, 31, 35, rotation=0.19),
            capacity._ellipse_points(275, 137, 35, 28, rotation=-0.15),
            capacity._ellipse_points(116, 267, 37, 29, rotation=-0.19),
            capacity._ellipse_points(278, 278, 29, 38, rotation=0.18),
        ),
    )

    # Nested / cavity forms.
    lines(
        "one-d-nested-1",
        "nested-loops",
        (
            capacity._ellipse_points(201, 196, 113, 102, rotation=-0.10),
            capacity._ellipse_points(218, 201, 41, 30, rotation=0.20),
        ),
    )
    outer = capacity._catmull_closed(
        ((94, 177), (146, 94), (248, 101), (311, 178), (286, 276), (198, 310), (103, 271))
    )
    lines(
        "one-d-nested-2",
        "nested-loops",
        (
            outer,
            capacity._ellipse_points(155, 198, 28, 34, rotation=-0.14),
            capacity._ellipse_points(239, 204, 34, 26, rotation=0.18),
        ),
    )
    lines(
        "one-d-nested-3",
        "nested-loops",
        (
            capacity._ellipse_points(199, 204, 120, 91, rotation=0.14),
            capacity._ellipse_points(159, 178, 25, 22, rotation=-0.15),
            capacity._ellipse_points(229, 174, 28, 22, rotation=0.14),
            capacity._ellipse_points(224, 239, 25, 28, rotation=-0.20),
        ),
    )

    # Concave single loops.
    controls = (
        ((92, 188), (141, 96), (241, 101), (307, 165), (238, 220), (286, 303), (188, 309), (98, 251), (174, 211)),
        ((103, 211), (116, 116), (191, 99), (286, 119), (309, 207), (242, 187), (272, 296), (173, 307), (101, 268), (170, 229)),
        ((101, 176), (163, 102), (267, 117), (306, 204), (237, 205), (289, 288), (195, 309), (111, 257), (174, 202)),
    )
    for index, control in enumerate(controls, start=1):
        lines(f"one-d-concave-{index}", "concave-loops", (capacity._catmull_closed(control),))

    # Open networks.
    lines(
        "one-d-network-1",
        "open-networks",
        (
            capacity._bezier((81, 96), (158, 298), (242, 109), (321, 305)),
            capacity._bezier((82, 306), (157, 105), (248, 292), (318, 103)),
            capacity._bezier((110, 201), (161, 177), (239, 218), (294, 194)),
        ),
    )
    lines(
        "one-d-network-2",
        "open-networks",
        (
            capacity._bezier((196, 202), (146, 158), (111, 126), (82, 91)),
            capacity._bezier((196, 202), (247, 149), (284, 119), (322, 106)),
            capacity._bezier((196, 202), (161, 248), (120, 282), (88, 316)),
            capacity._bezier((196, 202), (238, 246), (268, 284), (295, 318)),
        ),
    )
    lines(
        "one-d-network-3",
        "open-networks",
        (
            capacity._bezier((79, 119), (149, 91), (244, 162), (321, 116)),
            capacity._bezier((78, 194), (157, 281), (243, 124), (322, 201)),
            capacity._bezier((81, 279), (154, 239), (252, 308), (320, 276)),
            capacity._bezier((128, 91), (177, 166), (224, 237), (274, 314)),
        ),
    )

    # Dense controls stay under the unchanged 40k support ceiling.
    targets.append(
        capacity.Target(
            "one-d-dense-1",
            "dense-regions",
            capacity._filled_target(lambda d: d.ellipse((106, 104, 294, 296), fill=capacity.FG)),
        )
    )

    def draw_annulus(drawer) -> None:
        drawer.ellipse((92, 90, 308, 308), fill=capacity.FG)
        drawer.ellipse((148, 152, 252, 248), fill=capacity.BG)

    targets.append(capacity.Target("one-d-dense-2", "dense-regions", capacity._filled_target(draw_annulus)))

    def draw_lobes(drawer) -> None:
        drawer.ellipse((88, 118, 214, 286), fill=capacity.FG)
        drawer.ellipse((190, 116, 316, 282), fill=capacity.FG)
        drawer.ellipse((164, 192, 238, 300), fill=capacity.FG)

    targets.append(capacity.Target("one-d-dense-3", "dense-regions", capacity._filled_target(draw_lobes)))

    if len(targets) != 15:
        raise AssertionError(f"1d target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract_1d() -> dict:
    targets = build_targets_1d()
    contract = capacity.target_contract(targets)
    prior = {_fingerprint(target.image) for target in capacity.build_targets()}
    prior.update(_fingerprint(target.image) for target in V2.build_targets_v2())
    prior.update(_fingerprint(target.image) for target in TOP1.build_targets_top1())
    prior.update(_fingerprint(target.image) for target in OPERATOR.build_targets_operator())
    fingerprints = [_fingerprint(target.image) for target in targets]
    overlap = sorted(set(fingerprints) & prior)
    contract["disjointFromAllPriorSamplingTargets"] = not overlap
    contract["priorOverlap"] = overlap
    contract["fingerprints"] = fingerprints
    contract["valid"] = bool(contract["valid"] and not overlap)
    return contract


if __name__ == "__main__":
    import json
    print(json.dumps(target_contract_1d(), indent=2, sort_keys=True))
