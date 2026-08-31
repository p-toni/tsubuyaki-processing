#!/usr/bin/env python3
"""Parallel excluded-seed mechanics smoke for multiplex-capacity-v1.

This is transport-only validation. It imports the frozen scientific implementation
from run.py and exercises disjoint challenge shards on seed 9001; consumed-seed
execution continues to call run.py directly.
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run

SHARDS = (
    tuple(run.CHALLENGES[0:3]),
    tuple(run.CHALLENGES[3:6]),
    tuple(run.CHALLENGES[6:9]),
    tuple(run.CHALLENGES[9:12]),
)


def validate_shard(shard: int) -> dict[str, object]:
    if shard not in range(len(SHARDS)):
        raise ValueError(f"smoke shard {shard} outside 0..{len(SHARDS)-1}")
    seed = run.SMOKE_SEED
    challenges = SHARDS[shard]

    starts_by_rep = {}
    for route in run.CURRENT_ROUTES:
        starts_by_rep[route], _attempts = run._current_starts(seed, route)
    experimental, _experimental_attempts, shared_hashes = run._experimental_starts(seed)
    starts_by_rep.update(experimental)

    if len(shared_hashes) != run.STARTS:
        raise AssertionError("shared experimental start count drift")
    if tuple(starts_by_rep) != run.REPRESENTATIONS:
        raise AssertionError("smoke representation rectangle drift")

    searches = 0
    for challenge in challenges:
        target = run._target_images(seed, challenge)
        if not run._target_fingerprint(target):
            raise AssertionError(f"missing target fingerprint for {challenge.id}")
        for rep in run.REPRESENTATIONS:
            result = run._search(rep, seed, challenge, copy.deepcopy(starts_by_rep[rep]), target)
            searches += 1
            if result["totalCandidates"] != run.TOTAL_CANDIDATES_PER_SEARCH:
                raise AssertionError(f"budget drift for {rep}/{challenge.id}")
            if result["hardValidCandidates"] < run.STARTS:
                raise AssertionError(f"valid-start loss for {rep}/{challenge.id}")
            if not (0.0 <= result["hardValidYield"] <= 1.0):
                raise AssertionError(f"valid-yield range drift for {rep}/{challenge.id}")

    expected = len(challenges) * len(run.REPRESENTATIONS)
    if searches != expected:
        raise AssertionError(f"expected {expected} smoke searches, got {searches}")
    return {
        "population": "smoke-excluded",
        "seed": seed,
        "shard": shard,
        "challengeIds": [challenge.id for challenge in challenges],
        "representations": list(run.REPRESENTATIONS),
        "searches": searches,
        "candidateEvaluationsPerRepresentationChallenge": run.TOTAL_CANDIDATES_PER_SEARCH,
        "passed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, choices=range(len(SHARDS)), required=True)
    args = parser.parse_args()
    result = validate_shard(args.shard)
    print(
        "excluded smoke shard passed:",
        result["shard"],
        ",".join(result["challengeIds"]),
        result["searches"],
        "searches",
    )


if __name__ == "__main__":
    main()
