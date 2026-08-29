#!/usr/bin/env python3
"""Run one fresh route×seed block of the frozen basin trust-region mechanism."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PILOT_RUN = ROOT / "experiments" / "basin-trust-region-v1" / "run.py"

FRESH_SEEDS = (
    2003, 2011, 2017, 2027,
    2029, 2039, 2053, 2063,
    2069, 2081, 2083, 2087,
    2089, 2099, 2111, 2113,
    2129, 2131, 2137, 2141,
    2143, 2153, 2161, 2179,
    2203, 2207, 2213, 2221,
    2237, 2239, 2243, 2251,
)
SMOKE_SEED = 9001
ALL_SEEDS = FRESH_SEEDS + (SMOKE_SEED,)


def _load_pilot():
    spec = importlib.util.spec_from_file_location("basin_trust_confirmation_frozen_pilot", PILOT_RUN)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_block(route: str, seed: int) -> dict:
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    pilot = _load_pilot()
    # The mechanism is imported unchanged. Only the allowed analysis population
    # is replaced before execution so the pilot implementation's own fail-closed
    # seed checks and analysisSeed marker remain active.
    pilot.PILOT_SEEDS = FRESH_SEEDS
    pilot.ALL_SEEDS = ALL_SEEDS
    result = pilot.run_block(route, seed)
    out = dict(result)
    out.pop("pilotSeeds", None)
    out.update(
        confirmationVersion=1,
        confirmationSeed=seed in FRESH_SEEDS,
        freshSeeds=list(FRESH_SEEDS),
        sourceMechanism="experiments/basin-trust-region-v1/run.py",
        sourcePartition="experiments/basin-trust-region-v1/policy.py",
        mechanismFrozen=True,
        freshSearchEvidence=seed in FRESH_SEEDS,
    )
    if bool(out.get("analysisSeed")) != bool(out["confirmationSeed"]):
        raise AssertionError("frozen pilot seed marker drift")
    return out


def main() -> None:
    pilot = _load_pilot()
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=tuple(pilot.ROUTE_ORDER), required=True)
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2))


if __name__ == "__main__":
    main()
