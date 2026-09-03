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
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_targets_family_projection():
    targets = []

    def lines(target_id: str, family: str, groups: Sequence[Sequence[tuple[float, float]]]) -> None:
        targets.append(
            capacity.Target(
                target_id,
                family,
                capacity._binary_points([p for group in groups for p in group]),
            )
        )

    lines(
        "family-projection-components-1",
        "disconnected-loops",
        (
            capacity._ellipse_points(128, 145, 39, 46, rotation=-0.27),
            capacity._ellipse_points(276, 254, 51, 35, rotation=0.31),
        ),
    )
    lines(
        "family-projection-components-2",
        "disconnected-loops",
        (
            capacity._ellipse_points(104, 153, 29, 39, rotation=0.16),
            capacity._ellipse_points(289, 139, 42, 28, rotation=-0.24),
            capacity._ellipse_points(205, 284, 39, 34, rotation=0.11),
        ),
    )
    lines(
        "family-projection-components-3",
        "disconnected-loops",
        (
            capacity._ellipse_points(106, 110, 25, 31, rotation=-0.20),
            capacity._ellipse_points(292, 117, 31, 27, rotation=0.28),
            capacity._ellipse_points(123, 286, 34, 25, rotation=0.23),
            capacity._ellipse_points(287, 289, 27, 34, rotation=-0.25),
        ),
    )

    lines(
        "family-projection-nested-1",
        "nested-loops",
        (
            capacity._ellipse_points(197, 201, 121, 87, rotation=0.19),
            capacity._ellipse_points(224, 192, 34, 27, rotation=-0.28),
        ),
    )
    outer = capacity._catmull_closed(
        ((76, 179), (120, 101), (222, 78), (325, 149), (317, 250), (235, 323), (111, 304))
    )
    lines(
        "family-projection-nested-2",
        "nested-loops",
        (
            outer,
            capacity._ellipse_points(151, 204, 23, 34, rotation=0.16),
            capacity._ellipse_points(251, 198, 34, 22, rotation=-0.23),
        ),
    )
    lines(
        "family-projection-nested-3",
        "nested-loops",
        (
            capacity._ellipse_points(202, 202, 117, 103, rotation=-0.22),
            capacity._ellipse_points(160, 164, 21, 24, rotation=0.25),
            capacity._ellipse_points(243, 178, 29, 18, rotation=-0.15),
            capacity._ellipse_points(210, 251, 24, 31, rotation=0.18),
        ),
    )

    controls = (
        ((79, 173), (122, 93), (221, 84), (324, 145), (246, 209), (314, 286), (211, 326), (91, 276), (151, 217)),
        ((88, 231), (101, 125), (169, 84), (277, 98), (327, 181), (241, 173), (296, 303), (185, 324), (83, 282), (154, 241)),
        ((83, 151), (145, 84), (263, 99), (327, 184), (236, 203), (311, 281), (204, 326), (94, 263), (151, 194)),
    )
    for i, control in enumerate(controls, 1):
        lines(
            f"family-projection-concave-{i}",
            "concave-loops",
            (capacity._catmull_closed(control),),
        )

    lines(
        "family-projection-network-1",
        "open-networks",
        (
            capacity._bezier((62, 102), (137, 318), (270, 82), (338, 296)),
            capacity._bezier((61, 295), (158, 86), (245, 322), (341, 109)),
            capacity._bezier((93, 182), (157, 145), (246, 242), (315, 205)),
        ),
    )
    lines(
        "family-projection-network-2",
        "open-networks",
        (
            capacity._bezier((194, 197), (138, 151), (99, 109), (62, 70)),
            capacity._bezier((194, 197), (256, 151), (301, 118), (340, 101)),
            capacity._bezier((194, 197), (158, 258), (112, 301), (78, 337)),
            capacity._bezier((194, 197), (252, 247), (290, 292), (319, 337)),
        ),
    )
    lines(
        "family-projection-network-3",
        "open-networks",
        (
            capacity._bezier((61, 113), (143, 64), (263, 174), (341, 111)),
            capacity._bezier((61, 212), (155, 310), (244, 101), (342, 226)),
            capacity._bezier((65, 300), (161, 220), (258, 339), (339, 294)),
            capacity._bezier((101, 67), (168, 151), (232, 260), (300, 340)),
        ),
    )

    targets.append(
        capacity.Target(
            "family-projection-dense-1",
            "dense-regions",
            capacity._filled_target(
                lambda d: d.ellipse((91, 101, 313, 300), fill=capacity.FG)
            ),
        )
    )

    def annulus(drawer) -> None:
        drawer.ellipse((76, 85, 325, 316), fill=capacity.FG)
        drawer.ellipse((154, 145, 248, 253), fill=capacity.BG)

    targets.append(
        capacity.Target(
            "family-projection-dense-2",
            "dense-regions",
            capacity._filled_target(annulus),
        )
    )

    def lobes(drawer) -> None:
        drawer.ellipse((73, 113, 208, 289), fill=capacity.FG)
        drawer.ellipse((202, 105, 331, 273), fill=capacity.FG)
        drawer.ellipse((151, 204, 250, 307), fill=capacity.FG)

    targets.append(
        capacity.Target(
            "family-projection-dense-3",
            "dense-regions",
            capacity._filled_target(lobes),
        )
    )

    if len(targets) != 15:
        raise AssertionError(f"family projection target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract_family_projection() -> dict:
    targets = build_targets_family_projection()
    contract = capacity.target_contract(targets)

    modules = [
        _load("fp_targets_v2", ROOT / "experiments" / "sampling-invariance-search-v2" / "targets_v2.py"),
        _load("fp_targets_top1", ROOT / "experiments" / "sampling-invariance-search-top1-confirmation-v1" / "targets_top1.py"),
        _load("fp_targets_operator", ROOT / "experiments" / "spectral-material-control-operator-v1" / "targets_operator.py"),
        _load("fp_targets_1d", ROOT / "experiments" / "spectral-material-control-1d-confirmation-v1" / "targets_1d.py"),
        _load("fp_targets_portfolio", ROOT / "experiments" / "spectral-material-control-1d-portfolio-v1" / "targets_portfolio.py"),
        _load("fp_targets_runtime", ROOT / "experiments" / "spectral-material-control-runtime-replay-v1" / "targets_runtime.py"),
    ]

    prior = {_fingerprint(t.image) for t in capacity.build_targets()}
    prior.update(_fingerprint(t.image) for t in modules[0].build_targets_v2())
    prior.update(_fingerprint(t.image) for t in modules[1].build_targets_top1())
    prior.update(_fingerprint(t.image) for t in modules[2].build_targets_operator())
    prior.update(_fingerprint(t.image) for t in modules[3].build_targets_1d())
    prior.update(_fingerprint(t.image) for t in modules[4].build_targets_portfolio())
    prior.update(_fingerprint(t.image) for t in modules[5].build_targets_runtime())

    fingerprints = [_fingerprint(t.image) for t in targets]
    overlap = sorted(set(fingerprints) & prior)
    contract["disjointFromAllPriorSamplingMaterialTargets"] = not overlap
    contract["priorOverlap"] = overlap
    contract["fingerprints"] = fingerprints
    contract["valid"] = bool(contract["valid"] and not overlap)
    return contract


if __name__ == "__main__":
    import json

    print(json.dumps(target_contract_family_projection(), indent=2, sort_keys=True))
