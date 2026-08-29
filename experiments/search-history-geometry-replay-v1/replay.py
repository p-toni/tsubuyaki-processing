#!/usr/bin/env python3
"""Replay one historical search-mechanics block under sparse-geometry-v1."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

from metric import install_sparse_geometry_metric

EXPERIMENT_PATHS = {
    "search-leverage": ROOT / "experiments" / "search-leverage-v1" / "reproduce.py",
    "route-conditional": ROOT / "experiments" / "route-conditional-policy-v1" / "reproduce.py",
    "online-probe": ROOT / "experiments" / "online-topology-probe-v1" / "probe.py",
    "start-state": ROOT / "experiments" / "start-state-topology-v1" / "selector.py",
    "stage1-response": ROOT / "experiments" / "stage1-response-topology-v1" / "policy.py",
    "fixed-hedge": ROOT / "experiments" / "fixed-hedge-topology-v1" / "policy.py",
    "mutation-scale": ROOT / "experiments" / "mutation-scale-v1" / "policy.py",
    "mutation-schedule": ROOT / "experiments" / "mutation-scale-schedule-v1" / "policy.py",
}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(
        f"geometry_history_replay_{name.replace('-', '_')}", path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _install(module) -> None:
    seen = set()

    def install(v1) -> None:
        if id(v1) in seen:
            return
        install_sparse_geometry_metric(v1)
        seen.add(id(v1))

    if hasattr(module, "v1"):
        install(module.v1)
    if hasattr(module, "online_probe") and hasattr(module.online_probe, "v1"):
        install(module.online_probe.v1)
    if hasattr(module, "stage1") and hasattr(module.stage1, "v1"):
        install(module.stage1.v1)


def run(experiment: str, route: str, seed: int) -> dict:
    if experiment not in EXPERIMENT_PATHS:
        raise ValueError(f"unknown experiment {experiment!r}")

    module = _load(experiment, EXPERIMENT_PATHS[experiment])
    _install(module)

    if experiment == "search-leverage":
        if seed not in module.SEEDS:
            raise ValueError(f"seed {seed} not in root seeds {module.SEEDS}")
        result = module.run_block(route, seed)
    elif experiment == "route-conditional":
        if seed not in module.HOLDOUT_SEEDS:
            raise ValueError(f"seed {seed} not in route-conditional holdout")
        result = module.run_block(route, seed)
    elif experiment == "online-probe":
        if seed not in module.ALL_SEEDS:
            raise ValueError(f"seed {seed} not in online-probe population")
        result = module.run_block(route, seed, tuple(module.PILOT_SIZES))
    elif experiment == "start-state":
        if seed not in module.ALL_SEEDS:
            raise ValueError(f"seed {seed} not in start-state population")
        result = module.run_block(route, seed, tuple(module.THRESHOLDS))
    elif experiment == "stage1-response":
        if seed not in module.ALL_SEEDS:
            raise ValueError(f"seed {seed} not in stage1-response population")
        result = module.run_block(route, seed, tuple(module.THRESHOLDS))
    elif experiment == "fixed-hedge":
        if seed not in module.ALL_SEEDS:
            raise ValueError(f"seed {seed} not in fixed-hedge population")
        result = module.run_block(route, seed, tuple(module.HEDGE_SHARES))
    elif experiment == "mutation-scale":
        if seed not in module.ALL_SEEDS:
            raise ValueError(f"seed {seed} not in mutation-scale population")
        # All contrasts are computed even on the already-consumed retrospective
        # holdout; the reducer is allowed to inspect only the calibration-selected
        # contrast versus 1.0 there.
        result = module.run_block(route, seed, tuple(module.MULTIPLIERS))
    elif experiment == "mutation-schedule":
        if seed not in module.ALL_SEEDS:
            raise ValueError(f"seed {seed} not in mutation-schedule population")
        # Same rule: holdout grid is generated for transport simplicity, but only
        # the geometry-calibration-selected contrast may enter interpretation.
        result = module.run_block(route, seed, tuple(module.CONTRASTS))
    else:  # pragma: no cover
        raise AssertionError(experiment)

    out = dict(result)
    out["structuralReplay"] = {
        "experiment": experiment,
        "metric": "sparse-geometry-v1",
        "metricSource": "experiments/search-measurement-geometry-v1/audit.py",
        "intervention": "runtime replacement of historical phenotype_distance only",
        "freshSearchEvidence": False,
    }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", choices=tuple(EXPERIMENT_PATHS), required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.experiment, args.route, args.seed), indent=2))


if __name__ == "__main__":
    main()
