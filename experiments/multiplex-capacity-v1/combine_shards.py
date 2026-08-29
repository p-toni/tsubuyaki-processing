#!/usr/bin/env python3
"""Reconstruct one frozen multiplex-capacity-v1 seed block from four challenge shards."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run
from run_shard import SHARDS


def _load(root: Path, seed: int) -> list[dict]:
    shards = []
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text())
        if data.get("experiment") == "multiplex-capacity-v1" and int(data.get("seed", -1)) == seed and "shard" in data:
            shards.append(data)
    if len(shards) != len(SHARDS):
        raise AssertionError(f"expected {len(SHARDS)} shards for seed {seed}, found {len(shards)}")
    shards.sort(key=lambda item: int(item["shard"]))
    if [int(item["shard"]) for item in shards] != list(range(len(SHARDS))):
        raise AssertionError(f"shard rectangle drift for seed {seed}")
    return shards


def combine(root: Path, seed: int) -> dict:
    if seed not in run.ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    shards = _load(root, seed)
    first = shards[0]

    equal_fields = (
        "version", "experiment", "population", "seed", "metric", "descriptor",
        "settings", "representations", "currentRoutes", "fullMultiplex", "ablations",
        "families", "startAttempts", "sharedExperimentalStartGenomeHashes",
    )
    for field in equal_fields:
        if any(shard[field] != first[field] for shard in shards[1:]):
            raise AssertionError(f"shard metadata drift for seed {seed}: {field}")
    if first.get("transport") != "challenge-shard-v1" or any(
        shard.get("transport") != "challenge-shard-v1" for shard in shards
    ):
        raise AssertionError("challenge-shard transport marker drift")
    if any(not all(bool(v) for v in shard["hardInvariants"].values()) for shard in shards):
        raise AssertionError(f"one or more shard hard invariants failed for seed {seed}")

    challenges = []
    for shard_index, shard in enumerate(shards):
        expected_ids = tuple(challenge.id for challenge in SHARDS[shard_index])
        actual_ids = tuple(str(row["id"]) for row in shard["challenges"])
        if actual_ids != expected_ids or tuple(shard["challengeIds"]) != expected_ids:
            raise AssertionError(f"challenge shard order drift for seed {seed}/shard {shard_index}")
        challenges.extend(shard["challenges"])
    if tuple(str(row["id"]) for row in challenges) != run.CHALLENGE_IDS:
        raise AssertionError(f"full challenge order drift for seed {seed}")

    niche_records = {}
    for rep in run.REPRESENTATIONS:
        start_sets = [
            [record for record in shard["nicheRecords"][rep] if record["challenge"] == "__starts__"]
            for shard in shards
        ]
        if any(records != start_sets[0] for records in start_sets[1:]):
            raise AssertionError(f"start niche record drift for seed {seed}/{rep}")
        combined = list(start_sets[0])
        for shard in shards:
            combined.extend(
                record for record in shard["nicheRecords"][rep]
                if record["challenge"] != "__starts__"
            )
        niche_records[rep] = combined

    hard_invariants = {
        "completeChallengeRectangle": len(challenges) == len(run.CHALLENGES),
        "completeRepresentationRectangle": all(
            tuple(row["representations"]) == run.REPRESENTATIONS for row in challenges
        ),
        "equalCandidateBudget": all(
            int(result["totalCandidates"]) == run.TOTAL_CANDIDATES_PER_SEARCH
            for row in challenges
            for result in row["representations"].values()
        ),
        "sharedExperimentalStarts": all(
            bool(shard["hardInvariants"]["sharedExperimentalStarts"]) for shard in shards
        ),
    }
    if not all(hard_invariants.values()):
        raise AssertionError(f"reconstructed hard invariant failure for seed {seed}: {hard_invariants}")

    return {
        "version": first["version"],
        "experiment": first["experiment"],
        "population": first["population"],
        "seed": seed,
        "metric": first["metric"],
        "descriptor": first["descriptor"],
        "settings": first["settings"],
        "representations": first["representations"],
        "currentRoutes": first["currentRoutes"],
        "fullMultiplex": first["fullMultiplex"],
        "ablations": first["ablations"],
        "challengeIds": list(run.CHALLENGE_IDS),
        "families": first["families"],
        "startAttempts": first["startAttempts"],
        "sharedExperimentalStartGenomeHashes": first["sharedExperimentalStartGenomeHashes"],
        "challenges": challenges,
        "nicheRecords": niche_records,
        "hardInvariants": hard_invariants,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--seed", type=int, choices=run.ALL_SEEDS, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = json.dumps(combine(Path(args.results_dir), args.seed), indent=2, sort_keys=True)
    Path(args.output).write_text(payload + "\n")


if __name__ == "__main__":
    main()
