from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V2_DIR = ROOT / "experiments" / "sampling-invariance-search-v2"
sys.path.insert(0, str(V2_DIR))

import run_search_v2 as v2

from targets_top1 import build_targets_top1, target_contract_top1

STREAM = "sampling-invariance-search-top1-confirmation-v1"
SMOKE_SEED = 96999
CONFIRMATION_SEEDS = (
    97001, 97003, 97007, 97021, 97039, 97073,
    97081, 97103, 97117, 97127, 97151, 97157,
    97159, 97169, 97171, 97177, 97187, 97213,
    97231, 97241, 97259, 97283, 97301, 97303,
)
COMMON_STARTS = 4
DISCOVERY_DRAWS = 8
TAIL_EVALUATIONS = 8
TOTAL_EVALUATIONS = 20
ANGLES = (0.04, 0.08, 0.16, 0.32)
MEANINGFUL_MARGIN = 0.005

# Reuse the exact v2 search primitive with only a fresh RNG namespace.
v2.STREAM = STREAM
if tuple(v2.ANGLES) != ANGLES:
    raise AssertionError(f"frozen angle drift: {v2.ANGLES}")
if v2.COMMON_STARTS != COMMON_STARTS or v2.DISCOVERY_DRAWS != DISCOVERY_DRAWS or v2.TAIL_EVALUATIONS != TAIL_EVALUATIONS:
    raise AssertionError("frozen 12/8 allocation drifted")


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _target_run(seed: int, target, discovery_pool, breadth_tail, rasterizer) -> dict:
    ranked = v2._rank_valid(discovery_pool, target.image)
    if not ranked:
        raise AssertionError("shared discovery pool has no valid anchor")
    anchor_recovery, anchor = ranked[0]

    first_children, first_parent, _first_recovery, first_accepted, first_events = v2._adaptive_cycle(
        seed, target, anchor, 0, rasterizer, "X1-"
    )
    second_children, _final_parent, _final_recovery, second_accepted, second_events = v2._adaptive_cycle(
        seed, target, first_parent, 4, rasterizer, "H1-"
    )

    breadth_pool = discovery_pool + breadth_tail
    top1_pool = discovery_pool + first_children + second_children
    breadth_winner, breadth_best = v2._best(breadth_pool, target.image)
    top1_winner, top1_best = v2._best(top1_pool, target.image)

    discovery_hash = hashlib.sha256(
        json.dumps(
            [
                {"id": candidate.id, "fp": _fingerprint(candidate.image), "valid": candidate.valid}
                for candidate in discovery_pool
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    event_schedule = first_events + second_events

    hard = {
        "sharedDiscoveryHas12Evaluations": len(discovery_pool) == COMMON_STARTS + DISCOVERY_DRAWS,
        "anchorFromSharedDiscovery": anchor in discovery_pool and anchor.valid,
        "equalTwentyEvaluationBudget": len(breadth_pool) == TOTAL_EVALUATIONS and len(top1_pool) == TOTAL_EVALUATIONS,
        "exactEightExploitEvents": len(event_schedule) == TAIL_EVALUATIONS,
        "frozenAngleSchedule": [row["angle"] for row in event_schedule] == list(ANGLES) * 2,
        "uniqueExploitEventIndices": [row["eventIndex"] for row in event_schedule] == list(range(8)),
        "discoveryHashPresent": bool(discovery_hash),
    }

    effect = top1_best - breadth_best
    return {
        "target": target.id,
        "family": target.family,
        "targetFingerprint": _fingerprint(target.image),
        "discoveryHash": discovery_hash,
        "anchor": {"id": anchor.id, "recovery": anchor_recovery, "fingerprint": _fingerprint(anchor.image)},
        "policies": {
            "breadth-20": {
                "bestRecovery": breadth_best,
                "winner": breadth_winner.id,
                "evaluations": len(breadth_pool),
                "tailValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in breadth_tail),
                "uniquePhenotypeRate": v2._pool_unique_rate(breadth_pool),
            },
            "hybrid-top1": {
                "bestRecovery": top1_best,
                "winner": top1_winner.id,
                "evaluations": len(top1_pool),
                "exploitValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in first_children + second_children),
                "uniquePhenotypeRate": v2._pool_unique_rate(top1_pool),
                "acceptedImprovements": first_accepted + second_accepted,
            },
        },
        "effects": {
            "top1VsBreadth": effect,
            "top1MeaningfulVsBreadth": effect > MEANINGFUL_MARGIN,
        },
        "eventSchedule": event_schedule,
        "hardInvariants": hard,
    }


def run_seed(seed: int, population: str) -> dict:
    allowed = (SMOKE_SEED,) if population == "smoke" else CONFIRMATION_SEEDS if population == "confirmation" else ()
    if seed not in allowed:
        raise ValueError(f"seed {seed} not declared for population {population}")

    contract = target_contract_top1()
    if not contract["valid"]:
        raise AssertionError(contract)
    targets = build_targets_top1()

    rasterizer = v2.capacity.FieldRasterizer()
    starts, start_attempts = v2._common_starts(seed, rasterizer)
    discovery_draws = v2._independent_draws(seed, rasterizer, "shared-discovery", DISCOVERY_DRAWS, "D")
    breadth_tail = v2._independent_draws(seed, rasterizer, "breadth-tail", TAIL_EVALUATIONS, "B")
    discovery_pool = starts + discovery_draws

    target_records = [_target_run(seed, target, discovery_pool, breadth_tail, rasterizer) for target in targets]
    discovery_hashes = {record["discoveryHash"] for record in target_records}
    target_fps = [record["targetFingerprint"] for record in target_records]

    hard = {
        "exactTargetRectangle": len(target_records) == 15,
        "targetSuiteContractValid": bool(contract["valid"]),
        "targetSuiteDisjointFromV1V2": bool(contract["disjointFromV1V2"]),
        "allTargetHardInvariants": all(all(record["hardInvariants"].values()) for record in target_records),
        "commonStartsValid": all(candidate.valid for candidate in starts),
        "commonStartsDistinct": len({_fingerprint(candidate.image) for candidate in starts}) == COMMON_STARTS,
        "sharedDiscoveryPoolIdenticalAcrossTargets": len(discovery_hashes) == 1,
        "targetFingerprintsDistinct": len(set(target_fps)) == 15,
    }

    return {
        "version": 1,
        "experiment": "sampling-invariance-search-top1-confirmation-v1",
        "population": population,
        "seed": seed,
        "settings": {
            "commonStarts": COMMON_STARTS,
            "discoveryDraws": DISCOVERY_DRAWS,
            "tailEvaluations": TAIL_EVALUATIONS,
            "totalEvaluationsPerPolicyTarget": TOTAL_EVALUATIONS,
            "angles": list(ANGLES),
            "meaningfulMargin": MEANINGFUL_MARGIN,
            "metric": "sparse-geometry-v1-exact-binary-equivalent",
            "fieldBandwidth": v2.capacity.FIELD_BANDWIDTH,
            "policy": "12-discovery-then-8-top1-geodesic-v1",
        },
        "startDiagnostics": {
            "attemptsForFourValidStarts": start_attempts,
            "sharedDiscoveryValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in discovery_draws),
            "startFingerprints": [_fingerprint(candidate.image) for candidate in starts],
        },
        "targetSuite": [
            {"id": target.id, "family": target.family, "fingerprint": _fingerprint(target.image)}
            for target in targets
        ],
        "targets": target_records,
        "hardInvariants": hard,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", choices=("smoke", "confirmation"), required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run_seed(args.seed, args.population)
    if not all(result["hardInvariants"].values()):
        raise AssertionError(result["hardInvariants"])
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"seed": args.seed, "population": args.population, "hardInvariants": result["hardInvariants"]}, indent=2))


if __name__ == "__main__":
    main()
