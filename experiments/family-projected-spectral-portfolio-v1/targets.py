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


def build_targets_family_portfolio():
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
        "family-portfolio-components-1",
        "disconnected-loops",
        (
            capacity._ellipse_points(122, 151, 35, 51, rotation=0.29),
            capacity._ellipse_points(282, 246, 44, 41, rotation=-0.33),
        ),
    )
    lines(
        "family-portfolio-components-2",
        "disconnected-loops",
        (
            capacity._ellipse_points(99, 145, 27, 36, rotation=-0.19),
            capacity._ellipse_points(294, 151, 38, 31, rotation=0.26),
            capacity._ellipse_points(196, 291, 45, 29, rotation=-0.14),
        ),
    )
    lines(
        "family-portfolio-components-3",
        "disconnected-loops",
        (
            capacity._ellipse_points(115, 105, 29, 25, rotation=0.22),
            capacity._ellipse_points(291, 109, 28, 35, rotation=-0.30),
            capacity._ellipse_points(112, 292, 27, 33, rotation=-0.17),
            capacity._ellipse_points(300, 281, 33, 29, rotation=0.21),
        ),
    )

    lines(
        "family-portfolio-nested-1",
        "nested-loops",
        (
            capacity._ellipse_points(201, 197, 118, 94, rotation=-0.20),
            capacity._ellipse_points(181, 208, 35, 25, rotation=0.27),
        ),
    )
    outer = capacity._catmull_closed(
        ((84, 175), (129, 96), (238, 82), (323, 157), (307, 266), (214, 322), (94, 293))
    )
    lines(
        "family-portfolio-nested-2",
        "nested-loops",
        (
            outer,
            capacity._ellipse_points(158, 196, 26, 31, rotation=-0.20),
            capacity._ellipse_points(253, 207, 29, 26, rotation=0.25),
        ),
    )
    lines(
        "family-portfolio-nested-3",
        "nested-loops",
        (
            capacity._ellipse_points(199, 203, 113, 108, rotation=0.18),
            capacity._ellipse_points(153, 181, 24, 21, rotation=-0.23),
            capacity._ellipse_points(241, 166, 24, 28, rotation=0.16),
            capacity._ellipse_points(223, 252, 29, 22, rotation=-0.19),
        ),
    )

    controls = (
        ((81, 190), (136, 99), (237, 90), (321, 164), (247, 221), (299, 302), (194, 320), (88, 258), (157, 207)),
        ((94, 218), (119, 118), (188, 84), (286, 111), (322, 198), (245, 183), (280, 309), (174, 318), (86, 268), (166, 231)),
        ((93, 163), (156, 91), (264, 111), (319, 197), (232, 211), (301, 288), (205, 315), (103, 254), (164, 190)),
    )
    for i, control in enumerate(controls, 1):
        lines(
            f"family-portfolio-concave-{i}",
            "concave-loops",
            (capacity._catmull_closed(control),),
        )

    lines(
        "family-portfolio-network-1",
        "open-networks",
        (
            capacity._bezier((69, 91), (151, 322), (263, 89), (332, 310)),
            capacity._bezier((72, 307), (155, 83), (251, 317), (330, 94)),
            capacity._bezier((104, 197), (166, 151), (237, 226), (303, 187)),
        ),
    )
    lines(
        "family-portfolio-network-2",
        "open-networks",
        (
            capacity._bezier((207, 184), (151, 148), (104, 108), (70, 72)),
            capacity._bezier((207, 184), (263, 143), (303, 117), (337, 112)),
            capacity._bezier((207, 184), (165, 247), (128, 296), (92, 332)),
            capacity._bezier((207, 184), (253, 240), (294, 283), (324, 324)),
        ),
    )
    lines(
        "family-portfolio-network-3",
        "open-networks",
        (
            capacity._bezier((72, 126), (150, 71), (253, 156), (331, 124)),
            capacity._bezier((68, 215), (148, 299), (263, 121), (336, 212)),
            capacity._bezier((70, 286), (154, 242), (260, 318), (329, 301)),
            capacity._bezier((112, 79), (179, 163), (228, 249), (287, 326)),
        ),
    )

    targets.append(
        capacity.Target(
            "family-portfolio-dense-1",
            "dense-regions",
            capacity._filled_target(
                lambda d: d.ellipse((102, 96, 305, 307), fill=capacity.FG)
            ),
        )
    )

    def annulus(drawer) -> None:
        drawer.ellipse((88, 79, 313, 320), fill=capacity.FG)
        drawer.ellipse((146, 159, 257, 244), fill=capacity.BG)

    targets.append(
        capacity.Target(
            "family-portfolio-dense-2",
            "dense-regions",
            capacity._filled_target(annulus),
        )
    )

    def lobes(drawer) -> None:
        drawer.ellipse((85, 116, 214, 278), fill=capacity.FG)
        drawer.ellipse((190, 120, 324, 289), fill=capacity.FG)
        drawer.ellipse((158, 188, 243, 303), fill=capacity.FG)

    targets.append(
        capacity.Target(
            "family-portfolio-dense-3",
            "dense-regions",
            capacity._filled_target(lobes),
        )
    )

    if len(targets) != 15:
        raise AssertionError(f"family portfolio target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract_family_portfolio() -> dict:
    targets = build_targets_family_portfolio()
    contract = capacity.target_contract(targets)

    modules = [
        _load("fpp_targets_v2", ROOT / "experiments" / "sampling-invariance-search-v2" / "targets_v2.py"),
        _load("fpp_targets_top1", ROOT / "experiments" / "sampling-invariance-search-top1-confirmation-v1" / "targets_top1.py"),
        _load("fpp_targets_operator", ROOT / "experiments" / "spectral-material-control-operator-v1" / "targets_operator.py"),
        _load("fpp_targets_1d", ROOT / "experiments" / "spectral-material-control-1d-confirmation-v1" / "targets_1d.py"),
        _load("fpp_targets_portfolio", ROOT / "experiments" / "spectral-material-control-1d-portfolio-v1" / "targets_portfolio.py"),
        _load("fpp_targets_runtime", ROOT / "experiments" / "spectral-material-control-runtime-replay-v1" / "targets_runtime.py"),
        _load("fpp_targets_family_projection", ROOT / "experiments" / "family-spectral-projection-v1" / "targets.py"),
    ]

    prior = {_fingerprint(t.image) for t in capacity.build_targets()}
    prior.update(_fingerprint(t.image) for t in modules[0].build_targets_v2())
    prior.update(_fingerprint(t.image) for t in modules[1].build_targets_top1())
    prior.update(_fingerprint(t.image) for t in modules[2].build_targets_operator())
    prior.update(_fingerprint(t.image) for t in modules[3].build_targets_1d())
    prior.update(_fingerprint(t.image) for t in modules[4].build_targets_portfolio())
    prior.update(_fingerprint(t.image) for t in modules[5].build_targets_runtime())
    prior.update(_fingerprint(t.image) for t in modules[6].build_targets_family_projection())

    fingerprints = [_fingerprint(t.image) for t in targets]
    overlap = sorted(set(fingerprints) & prior)
    contract["disjointFromAllPriorSamplingMaterialTargetsIncludingFamilyProjection"] = not overlap
    contract["priorOverlap"] = overlap
    contract["fingerprints"] = fingerprints
    contract["valid"] = bool(contract["valid"] and not overlap)
    return contract


if __name__ == "__main__":
    import json

    print(json.dumps(target_contract_family_portfolio(), indent=2, sort_keys=True))
