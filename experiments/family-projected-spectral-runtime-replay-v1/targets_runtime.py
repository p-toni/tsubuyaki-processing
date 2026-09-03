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


def build_targets_family_runtime():
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
        "family-runtime-components-1",
        "disconnected-loops",
        (
            capacity._ellipse_points(132, 142, 38, 46, rotation=-0.24),
            capacity._ellipse_points(276, 260, 41, 36, rotation=0.31),
        ),
    )
    lines(
        "family-runtime-components-2",
        "disconnected-loops",
        (
            capacity._ellipse_points(111, 158, 30, 32, rotation=0.28),
            capacity._ellipse_points(287, 139, 34, 39, rotation=-0.22),
            capacity._ellipse_points(208, 286, 39, 33, rotation=0.16),
        ),
    )
    lines(
        "family-runtime-components-3",
        "disconnected-loops",
        (
            capacity._ellipse_points(105, 116, 30, 27, rotation=-0.18),
            capacity._ellipse_points(297, 101, 31, 32, rotation=0.27),
            capacity._ellipse_points(124, 284, 31, 28, rotation=0.20),
            capacity._ellipse_points(289, 294, 29, 34, rotation=-0.24),
        ),
    )

    lines(
        "family-runtime-nested-1",
        "nested-loops",
        (
            capacity._ellipse_points(204, 201, 111, 101, rotation=0.23),
            capacity._ellipse_points(226, 191, 34, 27, rotation=-0.29),
        ),
    )
    outer = capacity._catmull_closed(
        ((91, 166), (143, 88), (249, 91), (318, 175), (294, 279), (196, 316), (86, 278))
    )
    lines(
        "family-runtime-nested-2",
        "nested-loops",
        (
            outer,
            capacity._ellipse_points(154, 211, 29, 25, rotation=0.24),
            capacity._ellipse_points(248, 190, 26, 32, rotation=-0.21),
        ),
    )
    lines(
        "family-runtime-nested-3",
        "nested-loops",
        (
            capacity._ellipse_points(197, 198, 107, 116, rotation=-0.16),
            capacity._ellipse_points(164, 163, 25, 23, rotation=0.19),
            capacity._ellipse_points(249, 184, 27, 23, rotation=-0.26),
            capacity._ellipse_points(205, 256, 25, 29, rotation=0.22),
        ),
    )

    controls = (
        ((77, 204), (128, 107), (224, 78), (319, 151), (253, 215), (311, 289), (207, 326), (92, 270), (151, 218)),
        ((88, 226), (126, 126), (203, 91), (298, 121), (323, 211), (238, 191), (272, 316), (164, 309), (82, 251), (158, 235)),
        ((91, 151), (165, 86), (271, 121), (315, 208), (224, 216), (293, 298), (188, 314), (97, 242), (159, 184)),
    )
    for i, control in enumerate(controls, 1):
        lines(
            f"family-runtime-concave-{i}",
            "concave-loops",
            (capacity._catmull_closed(control),),
        )

    lines(
        "family-runtime-network-1",
        "open-networks",
        (
            capacity._bezier((63, 104), (142, 317), (270, 78), (339, 297)),
            capacity._bezier((77, 319), (151, 74), (256, 328), (325, 88)),
            capacity._bezier((103, 180), (176, 232), (236, 145), (306, 207)),
        ),
    )
    lines(
        "family-runtime-network-2",
        "open-networks",
        (
            capacity._bezier((193, 191), (144, 140), (104, 97), (64, 61)),
            capacity._bezier((193, 191), (257, 153), (303, 126), (342, 126)),
            capacity._bezier((193, 191), (153, 249), (115, 302), (82, 340)),
            capacity._bezier((193, 191), (251, 252), (297, 292), (330, 335)),
        ),
    )
    lines(
        "family-runtime-network-3",
        "open-networks",
        (
            capacity._bezier((67, 137), (145, 78), (249, 166), (338, 111)),
            capacity._bezier((72, 207), (154, 310), (257, 110), (333, 226)),
            capacity._bezier((76, 297), (159, 232), (249, 329), (335, 289)),
            capacity._bezier((119, 72), (170, 174), (236, 235), (279, 334)),
        ),
    )

    targets.append(
        capacity.Target(
            "family-runtime-dense-1",
            "dense-regions",
            capacity._filled_target(
                lambda d: d.ellipse((111, 88, 296, 316), fill=capacity.FG)
            ),
        )
    )

    def annulus(drawer) -> None:
        drawer.ellipse((82, 91, 319, 313), fill=capacity.FG)
        drawer.ellipse((154, 145, 246, 256), fill=capacity.BG)

    targets.append(
        capacity.Target(
            "family-runtime-dense-2",
            "dense-regions",
            capacity._filled_target(annulus),
        )
    )

    def lobes(drawer) -> None:
        drawer.ellipse((78, 128, 207, 287), fill=capacity.FG)
        drawer.ellipse((196, 104, 331, 270), fill=capacity.FG)
        drawer.ellipse((151, 201, 250, 314), fill=capacity.FG)

    targets.append(
        capacity.Target(
            "family-runtime-dense-3",
            "dense-regions",
            capacity._filled_target(lobes),
        )
    )

    if len(targets) != 15:
        raise AssertionError(f"family runtime target count drifted: {len(targets)}")
    return tuple(targets)


def target_contract_family_runtime() -> dict:
    targets = build_targets_family_runtime()
    contract = capacity.target_contract(targets)

    modules = [
        _load("frt_targets_v2", ROOT / "experiments" / "sampling-invariance-search-v2" / "targets_v2.py"),
        _load("frt_targets_top1", ROOT / "experiments" / "sampling-invariance-search-top1-confirmation-v1" / "targets_top1.py"),
        _load("frt_targets_operator", ROOT / "experiments" / "spectral-material-control-operator-v1" / "targets_operator.py"),
        _load("frt_targets_1d", ROOT / "experiments" / "spectral-material-control-1d-confirmation-v1" / "targets_1d.py"),
        _load("frt_targets_portfolio", ROOT / "experiments" / "spectral-material-control-1d-portfolio-v1" / "targets_portfolio.py"),
        _load("frt_targets_runtime", ROOT / "experiments" / "spectral-material-control-runtime-replay-v1" / "targets_runtime.py"),
        _load("frt_targets_family_projection", ROOT / "experiments" / "family-spectral-projection-v1" / "targets.py"),
        _load("frt_targets_family_portfolio", ROOT / "experiments" / "family-projected-spectral-portfolio-v1" / "targets.py"),
    ]

    prior = {_fingerprint(t.image) for t in capacity.build_targets()}
    prior.update(_fingerprint(t.image) for t in modules[0].build_targets_v2())
    prior.update(_fingerprint(t.image) for t in modules[1].build_targets_top1())
    prior.update(_fingerprint(t.image) for t in modules[2].build_targets_operator())
    prior.update(_fingerprint(t.image) for t in modules[3].build_targets_1d())
    prior.update(_fingerprint(t.image) for t in modules[4].build_targets_portfolio())
    prior.update(_fingerprint(t.image) for t in modules[5].build_targets_runtime())
    prior.update(_fingerprint(t.image) for t in modules[6].build_targets_family_projection())
    prior.update(_fingerprint(t.image) for t in modules[7].build_targets_family_portfolio())

    fingerprints = [_fingerprint(t.image) for t in targets]
    overlap = sorted(set(fingerprints) & prior)
    contract["disjointFromAllPriorSamplingMaterialTargetsThroughFamilyPortfolio"] = not overlap
    contract["priorOverlap"] = overlap
    contract["fingerprints"] = fingerprints
    contract["valid"] = bool(contract["valid"] and not overlap)
    return contract


if __name__ == "__main__":
    import json
    print(json.dumps(target_contract_family_runtime(), indent=2, sort_keys=True))
