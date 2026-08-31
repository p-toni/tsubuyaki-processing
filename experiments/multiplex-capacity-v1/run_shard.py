#!/usr/bin/env python3
"""Run one challenge shard of a frozen multiplex-capacity-v1 master-seed block.

Transport adapter only. Scientific primitives are imported from run.py unchanged.
Four shards reconstruct the exact twelve-challenge seed block before aggregation.
"""
from __future__ import annotations

import argparse
import json
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


def run_block_shard(seed: int, shard: int) -> dict:
    if seed not in run.ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    if shard not in range(len(SHARDS)):
        raise ValueError(f"shard {shard} outside 0..{len(SHARDS)-1}")
    if run.DESCRIPTOR_VERSION != "structural-v1":
        raise AssertionError(f"descriptor version drift: {run.DESCRIPTOR_VERSION}")
    if len(run.CHALLENGES) != 12 or len(run.FAMILIES) != 4:
        raise AssertionError("challenge contract drift")

    starts_by_rep = {}
    start_attempts = {}
    for route in run.CURRENT_ROUTES:
        starts_by_rep[route], start_attempts[route] = run._current_starts(seed, route)
    experimental, experimental_attempts, shared_hashes = run._experimental_starts(seed)
    starts_by_rep.update(experimental)
    for rep in run.VARIANTS:
        start_attempts[rep] = experimental_attempts

    niche_records = {rep: run._start_niche_records(rep, starts_by_rep[rep]) for rep in run.REPRESENTATIONS}
    challenge_rows = []
    for challenge in SHARDS[shard]:
        target = run._target_images(seed, challenge)
        row = {
            "id": challenge.id,
            "family": challenge.family,
            "smoothPlausible": challenge.smooth_plausible,
            "targetFingerprint": run._target_fingerprint(target),
            "representations": {},
        }
        for rep in run.REPRESENTATIONS:
            result = run._search(rep, seed, challenge, starts_by_rep[rep], target)
            niche_records[rep].extend(result.pop("nicheRecords"))
            row["representations"][rep] = result
        challenge_rows.append(row)

    for row in challenge_rows:
        if tuple(row["representations"]) != run.REPRESENTATIONS:
            raise AssertionError("representation rectangle drift")
        for rep, result in row["representations"].items():
            if result["totalCandidates"] != run.TOTAL_CANDIDATES_PER_SEARCH:
                raise AssertionError(f"budget drift for {rep}/{row['id']}")

    hard_invariants = {
        "completeShardChallengeRectangle": len(challenge_rows) == len(SHARDS[shard]),
        "completeRepresentationRectangle": all(
            len(row["representations"]) == len(run.REPRESENTATIONS) for row in challenge_rows
        ),
        "equalCandidateBudget": all(
            result["totalCandidates"] == run.TOTAL_CANDIDATES_PER_SEARCH
            for row in challenge_rows
            for result in row["representations"].values()
        ),
        "sharedExperimentalStarts": all(
            [run._genome_key(c.genome) for c in starts_by_rep[rep]]
            == [run._genome_key(c.genome) for c in starts_by_rep[run.FULL]]
            for rep in run.VARIANTS
        ),
    }
    if not all(hard_invariants.values()):
        raise AssertionError(f"shard hard invariant failure: {hard_invariants}")

    return {
        "version": 1,
        "experiment": "multiplex-capacity-v1",
        "transport": "challenge-shard-v1",
        "population": "smoke-excluded" if seed == run.SMOKE_SEED else "consumed",
        "seed": seed,
        "shard": shard,
        "metric": "sparse-geometry-v1",
        "descriptor": run.DESCRIPTOR_VERSION,
        "settings": {
            "starts": run.STARTS,
            "cycles": run.CYCLES,
            "scales": list(run.SCALES),
            "candidateEvaluationsPerRepresentationChallenge": run.TOTAL_CANDIDATES_PER_SEARCH,
            "targetAlpha": run.TARGET_ALPHA,
        },
        "representations": list(run.REPRESENTATIONS),
        "currentRoutes": list(run.CURRENT_ROUTES),
        "fullMultiplex": run.FULL,
        "ablations": list(run.ABLATIONS),
        "challengeIds": [challenge.id for challenge in SHARDS[shard]],
        "families": list(run.FAMILIES),
        "startAttempts": start_attempts,
        "sharedExperimentalStartGenomeHashes": shared_hashes,
        "challenges": challenge_rows,
        "nicheRecords": niche_records,
        "hardInvariants": hard_invariants,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, choices=run.ALL_SEEDS, required=True)
    parser.add_argument("--shard", type=int, choices=range(len(SHARDS)), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = json.dumps(run_block_shard(args.seed, args.shard), indent=2, sort_keys=True)
    Path(args.output).write_text(payload + "\n")


if __name__ == "__main__":
    main()
