from __future__ import annotations

import argparse
import json
from pathlib import Path

import run_capacity

capacity = run_capacity.capacity

CONFIRMATION_SEEDS = (
    61001,
    61007,
    61027,
    61031,
    61043,
    61051,
    61057,
    61091,
    61099,
    61121,
    61129,
    61141,
    61151,
    61153,
    61169,
    61211,
    61223,
    61231,
    61253,
    61261,
    61283,
    61291,
    61297,
    61331,
)


def run_seed(seed: int) -> dict:
    if seed not in CONFIRMATION_SEEDS:
        raise ValueError(f"seed {seed} is not in the frozen confirmation population")

    # The frozen Stage-B runner uses HOLDOUT_SEEDS only as an authorization
    # rectangle. Temporarily substitute the fresh population without changing
    # any candidate-generation, target, render, metric, or scoring semantics.
    original = capacity.HOLDOUT_SEEDS
    capacity.HOLDOUT_SEEDS = CONFIRMATION_SEEDS
    try:
        result = capacity.run_seed(seed, "holdout")
    finally:
        capacity.HOLDOUT_SEEDS = original

    result["confirmation"] = {
        "experiment": "sampling-invariance-capacity-confirmation-v1",
        "population": "fresh-confirmation",
        "sourceExperiment": "sampling-invariance-capacity-v1",
        "seed": seed,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, choices=CONFIRMATION_SEEDS, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run_seed(args.seed)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "seed": args.seed,
                "confirmation": True,
                "hardInvariants": result["hardInvariants"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
