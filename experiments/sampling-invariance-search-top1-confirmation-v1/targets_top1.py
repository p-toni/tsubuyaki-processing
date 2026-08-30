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
sys.path.insert(0, str(CAPACITY_DIR))

import run_capacity

capacity = run_capacity.capacity

_v2_spec = importlib.util.spec_from_file_location("sampling_invariance_targets_v2_frozen", V2_TARGETS_PATH)
_v2 = importlib.util.module_from_spec(_v2_spec)
assert _v2_spec.loader is not None
_v2_spec.loader.exec_module(_v2)


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_targets_top1():
    targets = []

    def lines(target_id: str, family: str, groups: Sequence[Sequence[tuple[float, float]]]) -> None:
        points = [point for group in groups for point in group]
        targets.append(capacity.Target(target_id, family, capacity._binary_points(points)))

    # Disconnected closed components; coordinates differ from v1/v2.
    lines(
        "top1-components-1",
        "disconnected-loops",
        (
            capacity._ellipse_points(132, 151, 45, 61, rotation=0.11),
            capacity._ellipse_points(267, 249, 52, 46, rotation=-0.19),
        ),
    )
    lines(
        "top1-components-2",
        "disconnected-loops",
        (
            capacity._ellipse_points(118, 141, 36, 43, rotation=-0.27),
            capacity._ellipse_points(280, 132, 42, 34, rotation=0.19),
            capacity._ellipse_points(208, 274, 49, 39, rotation=0.07),
        ),
    )
    lines(
        "top1-components-3",
        "disconnected-loops",
        (
            capacity._ellipse_points(124, 124, 32, 36, rotation=0.13),
            capacity._ellipse_points(282, 142, 36, 30, rotation=-0.18),
            capacity._ellipse_points(119, 275, 39, 31, rotation=-0.22),
            capacity._ellipse_points(284, 263, 31, 40, rotation=0.24),
        ),
    )

    # Nested/cavity targets.
    lines(
        "top1-nested-1",
        "nested-loops",
        (
            capacity._ellipse_points(203, 198, 116, 104, rotation=-0.13),
            capacity._ellipse_points(226, 194, 43, 31, rotation=0.23),
        ),
    )
    outer2 = capacity._catmull_closed(
        ((91, 181), (143, 101), (244, 96), (313, 172), (292, 270), (208, 314), (109, 279))
    )
    lines(
        "top1-nested-2",
        "nested-loops",
        (
            outer2,
            capacity._ellipse_points(158, 205, 27, 35, rotation=-0.16),
            capacity._ellipse_points(238, 196, 35, 27, rotation=0.21),
        ),
    )
    lines(
        "top1-nested-3",
        "nested-loops",
        (
            capacity._ellipse_points(201, 201, 122, 93, rotation=0.18),
            capacity._ellipse_points(157, 176, 26, 23, rotation=-0.11),
            capacity._ellipse_points(224, 177, 29, 21, rotation=0.16),
            capacity._ellipse_points(231, 238, 24, 30, rotation=-0.23),
        ),
    )

    # Concave single loops.
    concave_controls = (
        ((90, 190), (139, 101), (238, 96), (311, 158), (246, 217), (291, 296), (194, 313), (101, 257), (169, 210)),
        ((99, 217), (111, 122), (184, 94), (281, 111), (314, 198), (248, 181), (280, 291), (181, 311), (97, 274), (166, 232)),
        ((95, 169), (159, 98), (261, 112), (312, 196), (243, 202), (296, 283), (201, 314), (107, 262), (169, 205)),
    )
    for index, controls in enumerate(concave_controls, start=1):
        lines(f"top1-concave-{index}", "concave-loops", (capacity._catmull_closed(controls),))

    # Open networks.
    lines(
        "top1-network-1",
        "open-networks",
        (
            capacity._bezier((75, 101), (151, 304), (251, 102), (327, 299)),
            capacity._bezier((77, 298), (163, 94), (244, 301), (325, 108)),
            capacity._bezier((105, 193), (161, 169), (247, 226), (301, 202)),
        ),
    )
    lines(
        "top1-network-2",
        "open-networks",
        (
            capacity._bezier((199, 198), (145, 163), (107, 122), (79, 88)),
            capacity._bezier((199, 198), (250, 151), (288, 123), (326, 111)),
            capacity._bezier((199, 198), (166, 247), (126, 285), (96, 321)),
            capacity._bezier((199, 198), (243, 242), (272, 287), (298, 323)),
        ),
    )
    lines(
        "top1-network-3",
        "open-networks",
        (
            capacity._bezier((74, 124), (147, 84), (250, 169), (329, 121)),
            capacity._bezier((72, 198), (151, 289), (249, 114), (328, 209)),
            capacity._bezier((76, 286), (158, 232), (246, 321), (326, 282)),
            capacity._bezier((121, 84), (174, 162), (229, 242), (282, 326)),
        ),
    )

    # Dense controls deliberately stay below the unchanged 40k support ceiling.
    targets.append(
        capacity.Target(
            "top1-dense-1",
            "dense-regions",
            capacity._filled_target(lambda d: d.ellipse((104, 96, 304, 300), fill=capacity.FG)),
        )
    )

    def draw_annulus(drawer) -> None:
        drawer.ellipse((85, 94, 315, 306), fill=capacity.FG)
        drawer.ellipse((141, 155, 261, 247), fill=capacity.BG)

    targets.append(capacity.Target("top1-dense-2", "dense-regions", capacity._filled_target(draw_annulus)))

    def draw_lobes(drawer) -> None:
        drawer.ellipse((78, 116, 218, 290), fill=capacity.FG)
        drawer.ellipse((186, 109, 326, 276), fill=capacity.FG)
        drawer.ellipse((161, 185, 242, 302), fill=capacity.FG)

    targets.append(capacity.Target("top1-dense-3", "dense-regions", capacity._filled_target(draw_lobes)))

    if len(targets) != 15:
        raise AssertionError(f"top1 target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract_top1() -> dict:
    targets = build_targets_top1()
    contract = capacity.target_contract(targets)
    old_fingerprints = {_fingerprint(target.image) for target in capacity.build_targets()}
    old_fingerprints.update(_fingerprint(target.image) for target in _v2.build_targets_v2())
    new_fingerprints = [_fingerprint(target.image) for target in targets]
    overlap = sorted(set(new_fingerprints) & old_fingerprints)
    contract["disjointFromV1V2"] = not overlap
    contract["priorOverlap"] = overlap
    contract["valid"] = bool(contract["valid"] and not overlap)
    return contract


if __name__ == "__main__":
    import json

    print(json.dumps(target_contract_top1(), indent=2, sort_keys=True))
