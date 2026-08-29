#!/usr/bin/env python3
"""Thin fresh-evidence adapter for the frozen repertoire-allocation-v1 mechanism."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PILOT_RUN = ROOT / "experiments" / "repertoire-allocation-v1" / "run.py"

FRESH_SEEDS = (
    31013, 31019, 31033, 31039,
    31051, 31063, 31069, 31079,
    31081, 31091, 31121, 31123,
    31139, 31147, 31151, 31153,
    31159, 31177, 31181, 31183,
    31189, 31193, 31219, 31223,
)
SMOKE_SEED = 9001
ALL_SEEDS = FRESH_SEEDS + (SMOKE_SEED,)


def _load_pilot():
    spec = importlib.util.spec_from_file_location("repertoire_allocation_v1_frozen", PILOT_RUN)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


pilot = _load_pilot()
ROUTE_ORDER = tuple(pilot.ROUTE_ORDER)
GENERATED_PER_ARM = int(pilot.GENERATED_PER_ARM)
EVENTS_PER_BASIN = int(pilot.EVENTS_PER_BASIN)
STARTS_PER_ROUTE = int(pilot.STARTS_PER_ROUTE)

# Only the admitted seed population changes. All scientific mechanics and RNG labels remain frozen in #77.
pilot.PILOT_SEEDS = FRESH_SEEDS
pilot.ALL_SEEDS = ALL_SEEDS
pilot.SMOKE_SEED = SMOKE_SEED


def run_block(route: str, seed: int) -> dict:
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    result = pilot.run_block(route, seed)
    is_fresh = seed in FRESH_SEEDS
    result["analysisSeed"] = is_fresh
    result["freshSearchEvidence"] = is_fresh
    result["confirmation"] = {
        "version": 1,
        "mechanism": "repertoire-allocation-v1-frozen",
        "freshPopulation": len(FRESH_SEEDS),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=True, choices=ROUTE_ORDER)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
