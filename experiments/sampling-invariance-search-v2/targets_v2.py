from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPACITY_DIR = ROOT / "experiments" / "sampling-invariance-v1"
sys.path.insert(0, str(CAPACITY_DIR))

import run_capacity

capacity = run_capacity.capacity


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_targets_v2():
    targets = []

    def lines(target_id: str, family: str, groups: Sequence[Sequence[tuple[float, float]]]) -> None:
        points = [point for group in groups for point in group]
        targets.append(capacity.Target(target_id, family, capacity._binary_points(points)))

    # New disconnected closed-component geometries.
    lines(
        "v2-components-1",
        "disconnected-loops",
        (
            capacity._ellipse_points(126, 158, 48, 67, rotation=0.24),
            capacity._ellipse_points(273, 241, 56, 43, rotation=-0.31),
        ),
    )
    lines(
        "v2-components-2",
        "disconnected-loops",
        (
            capacity._ellipse_points(119, 132, 39, 45, rotation=-0.16),
            capacity._ellipse_points(279, 137, 47, 36, rotation=0.28),
            capacity._ellipse_points(207, 273, 52, 41, rotation=-0.09),
        ),
    )
    lines(
        "v2-components-3",
        "disconnected-loops",
        (
            capacity._ellipse_points(128, 132, 34, 38, rotation=0.21),
            capacity._ellipse_points(277, 139, 38, 32, rotation=-0.25),
            capacity._ellipse_points(122, 274, 42, 33, rotation=-0.12),
            capacity._ellipse_points(279, 267, 33, 43, rotation=0.30),
        ),
    )

    # New nested/cavity geometries.
    lines(
        "v2-nested-1",
        "nested-loops",
        (
            capacity._ellipse_points(201, 202, 119, 108, rotation=0.17),
            capacity._ellipse_points(174, 211, 46, 33, rotation=-0.29),
        ),
    )
    outer2 = capacity._catmull_closed(
        ((88, 188), (134, 103), (235, 91), (315, 163), (301, 260), (219, 318), (116, 287))
    )
    lines(
        "v2-nested-2",
        "nested-loops",
        (
            outer2,
            capacity._ellipse_points(164, 195, 29, 37, rotation=0.18),
            capacity._ellipse_points(241, 213, 37, 28, rotation=-0.24),
        ),
    )
    lines(
        "v2-nested-3",
        "nested-loops",
        (
            capacity._ellipse_points(198, 199, 126, 96, rotation=-0.21),
            capacity._ellipse_points(151, 190, 27, 25, rotation=0.12),
            capacity._ellipse_points(218, 165, 30, 23, rotation=-0.10),
            capacity._ellipse_points(242, 231, 25, 31, rotation=0.26),
        ),
    )

    # New strongly concave single loops.
    concave_controls = (
        ((86, 195), (132, 103), (233, 92), (315, 151), (248, 210), (298, 292), (198, 316), (99, 264), (164, 216)),
        ((102, 224), (104, 127), (177, 91), (276, 104), (318, 190), (250, 177), (286, 286), (187, 315), (101, 281), (168, 236)),
        ((91, 174), (152, 94), (257, 107), (318, 190), (246, 199), (304, 278), (205, 319), (104, 269), (164, 211)),
    )
    for index, controls in enumerate(concave_controls, start=1):
        lines(f"v2-concave-{index}", "concave-loops", (capacity._catmull_closed(controls),))

    # New open-network geometries.
    lines(
        "v2-network-1",
        "open-networks",
        (
            capacity._bezier((72, 96), (156, 312), (244, 96), (330, 304)),
            capacity._bezier((73, 303), (158, 87), (249, 310), (329, 101)),
            capacity._bezier((102, 199), (154, 177), (251, 221), (304, 197)),
        ),
    )
    lines(
        "v2-network-2",
        "open-networks",
        (
            capacity._bezier((194, 203), (138, 171), (104, 121), (76, 82)),
            capacity._bezier((194, 203), (247, 156), (291, 119), (330, 105)),
            capacity._bezier((194, 203), (159, 249), (124, 289), (92, 326)),
            capacity._bezier((194, 203), (239, 248), (268, 293), (301, 327)),
        ),
    )
    lines(
        "v2-network-3",
        "open-networks",
        (
            capacity._bezier((70, 119), (144, 80), (247, 174), (333, 116)),
            capacity._bezier((68, 203), (152, 294), (244, 109), (332, 204)),
            capacity._bezier((71, 292), (155, 237), (248, 326), (331, 287)),
            capacity._bezier((118, 78), (177, 159), (225, 246), (286, 331)),
        ),
    )

    # New dense controls.
    targets.append(
        capacity.Target(
            "v2-dense-1",
            "dense-regions",
            capacity._filled_target(lambda d: d.ellipse((101, 92, 307, 304), fill=capacity.FG)),
        )
    )

    def draw_annulus(drawer) -> None:
        drawer.ellipse((82, 91, 318, 309), fill=capacity.FG)
        drawer.ellipse((137, 153, 264, 250), fill=capacity.BG)

    targets.append(capacity.Target("v2-dense-2", "dense-regions", capacity._filled_target(draw_annulus)))

    def draw_lobes(drawer) -> None:
        drawer.ellipse((74, 113, 221, 293), fill=capacity.FG)
        drawer.ellipse((183, 105, 329, 279), fill=capacity.FG)
        drawer.ellipse((143, 167, 260, 321), fill=capacity.FG)

    targets.append(capacity.Target("v2-dense-3", "dense-regions", capacity._filled_target(draw_lobes)))

    if len(targets) != 15:
        raise AssertionError(f"v2 target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract_v2() -> dict:
    targets = build_targets_v2()
    contract = capacity.target_contract(targets)
    old_fingerprints = {_fingerprint(target.image) for target in capacity.build_targets()}
    new_fingerprints = [_fingerprint(target.image) for target in targets]
    overlap = sorted(set(new_fingerprints) & old_fingerprints)
    contract["disjointFromV1"] = not overlap
    contract["v1Overlap"] = overlap
    contract["valid"] = bool(contract["valid"] and not overlap)
    return contract


if __name__ == "__main__":
    import json

    print(json.dumps(target_contract_v2(), indent=2, sort_keys=True))
