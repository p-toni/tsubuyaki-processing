from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPACITY_DIR = ROOT / "experiments" / "sampling-invariance-v1"
SEARCH_V1_DIR = ROOT / "experiments" / "sampling-invariance-search-v1"
sys.path.insert(0, str(CAPACITY_DIR))
sys.path.insert(0, str(SEARCH_V1_DIR))

import run_capacity
import fast_binary_metric as metric
from spectral_operator import geodesic_mutate

from targets_v2 import build_targets_v2, target_contract_v2

capacity = run_capacity.capacity

STREAM = "sampling-invariance-search-v2"
SMOKE_SEED = 95999
PILOT_SEEDS = (
    96001,
    96013,
    96017,
    96043,
    96053,
    96059,
    96079,
    96097,
    96137,
    96149,
    96157,
    96167,
    96179,
    96181,
    96199,
    96211,
    96221,
    96223,
    96233,
    96259,
)
COMMON_STARTS = 4
DISCOVERY_DRAWS = 8
TAIL_EVALUATIONS = 8
TOTAL_EVALUATIONS = COMMON_STARTS + DISCOVERY_DRAWS + TAIL_EVALUATIONS
ANGLES = (0.04, 0.08, 0.16, 0.32)
MEANINGFUL_MARGIN = 0.005
EPSILON = 1e-12


@dataclass
class FieldCandidate:
    id: str
    coefficients: np.ndarray
    image: object
    valid: bool
    origin: str


def _rng(*parts: object) -> np.random.Generator:
    payload = "|".join(str(part) for part in (STREAM,) + parts)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big", signed=False))


def _event_seed(seed: int, target_id: str, event_index: int) -> int:
    payload = f"{STREAM}|{seed}|{target_id}|exploit-event|{event_index}"
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _render(coefficients: np.ndarray, rasterizer, candidate_id: str, origin: str) -> FieldCandidate:
    image = rasterizer.image(coefficients)
    valid, _geometry = capacity._field_valid(image)
    return FieldCandidate(candidate_id, coefficients, image, bool(valid), origin)


def _common_starts(seed: int, rasterizer) -> tuple[list[FieldCandidate], int]:
    rng = _rng(seed, "common-starts")
    starts = []
    attempts = 0
    while len(starts) < COMMON_STARTS and attempts < COMMON_STARTS * 20:
        attempts += 1
        candidate = _render(
            capacity._draw_field_coefficients(rng),
            rasterizer,
            f"S{len(starts)+1}",
            "shared-start",
        )
        if candidate.valid:
            starts.append(candidate)
    if len(starts) != COMMON_STARTS:
        raise RuntimeError(f"seed {seed}: only {len(starts)} valid shared starts")
    return starts, attempts


def _independent_draws(seed: int, rasterizer, label: str, count: int, prefix: str) -> list[FieldCandidate]:
    rng = _rng(seed, label)
    out = []
    for index in range(count):
        out.append(
            _render(
                capacity._draw_field_coefficients(rng),
                rasterizer,
                f"{prefix}{index+1}",
                label,
            )
        )
    return out


def _recovery(candidate: FieldCandidate, target_image) -> float:
    if not candidate.valid:
        return float("-inf")
    distance = float(metric.sparse_geometry_distance((candidate.image,), (target_image,))["distance"])
    return 1.0 - distance


def _rank_valid(candidates: list[FieldCandidate], target_image) -> list[tuple[float, FieldCandidate]]:
    scored = [(_recovery(candidate, target_image), candidate) for candidate in candidates if candidate.valid]
    scored.sort(key=lambda item: (-item[0], item[1].id))
    return scored


def _best(candidates: list[FieldCandidate], target_image) -> tuple[FieldCandidate, float]:
    ranked = _rank_valid(candidates, target_image)
    if not ranked:
        raise AssertionError("candidate pool has no valid candidate")
    recovery, candidate = ranked[0]
    return candidate, recovery


def _adaptive_cycle(
    seed: int,
    target,
    start_parent: FieldCandidate,
    event_offset: int,
    rasterizer,
    prefix: str,
) -> tuple[list[FieldCandidate], FieldCandidate, float, int, list[dict]]:
    parent = start_parent
    parent_recovery = _recovery(parent, target.image)
    children = []
    accepted = 0
    events = []
    for local_index, angle in enumerate(ANGLES):
        event_index = event_offset + local_index
        event_seed = _event_seed(seed, target.id, event_index)
        rng = np.random.default_rng(event_seed)
        child = _render(
            geodesic_mutate(parent.coefficients, rng, angle),
            rasterizer,
            f"{prefix}{local_index+1}",
            prefix,
        )
        child_recovery = _recovery(child, target.image)
        if child.valid and child_recovery > parent_recovery + EPSILON:
            parent = child
            parent_recovery = child_recovery
            accepted += 1
        children.append(child)
        events.append({"eventIndex": event_index, "angle": angle, "seed": event_seed})
    return children, parent, parent_recovery, accepted, events


def _pool_unique_rate(candidates: list[FieldCandidate]) -> float:
    return len({_fingerprint(candidate.image) for candidate in candidates}) / len(candidates)


def _target_run(
    seed: int,
    target,
    discovery_pool: list[FieldCandidate],
    breadth_tail: list[FieldCandidate],
    rasterizer,
) -> dict:
    ranked = _rank_valid(discovery_pool, target.image)
    if len(ranked) < 2:
        raise AssertionError("shared discovery pool has fewer than two valid anchors")
    top1_recovery, top1 = ranked[0]
    top2_recovery, top2 = ranked[1]

    # Common first exploitation cycle: exactly identical for H1/H2.
    common_children, common_parent, common_parent_recovery, common_accepted, first_events = _adaptive_cycle(
        seed, target, top1, 0, rasterizer, "X1-"
    )

    # Same second-cycle event seeds/angles; only basin allocation differs.
    top1_second, _h1_parent, _h1_parent_recovery, h1_second_accepted, second_events_h1 = _adaptive_cycle(
        seed, target, common_parent, 4, rasterizer, "H1-"
    )
    top2_second, _h2_parent, _h2_parent_recovery, h2_second_accepted, second_events_h2 = _adaptive_cycle(
        seed, target, top2, 4, rasterizer, "H2-"
    )

    breadth_pool = discovery_pool + breadth_tail
    h1_pool = discovery_pool + common_children + top1_second
    h2_pool = discovery_pool + common_children + top2_second

    breadth_winner, breadth_best = _best(breadth_pool, target.image)
    h1_winner, h1_best = _best(h1_pool, target.image)
    h2_winner, h2_best = _best(h2_pool, target.image)

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
    first_event_hash = hashlib.sha256(
        json.dumps(first_events, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    second_h1_hash = hashlib.sha256(
        json.dumps(second_events_h1, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    second_h2_hash = hashlib.sha256(
        json.dumps(second_events_h2, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    first_cycle_fps = [_fingerprint(candidate.image) for candidate in common_children]
    h2_basin2_ids = {candidate.id for candidate in top2_second}

    policies = {
        "breadth-20": {
            "bestRecovery": breadth_best,
            "winner": breadth_winner.id,
            "evaluations": len(breadth_pool),
            "tailValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in breadth_tail),
            "uniquePhenotypeRate": _pool_unique_rate(breadth_pool),
        },
        "hybrid-top1": {
            "bestRecovery": h1_best,
            "winner": h1_winner.id,
            "evaluations": len(h1_pool),
            "exploitValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in common_children + top1_second),
            "uniquePhenotypeRate": _pool_unique_rate(h1_pool),
            "acceptedImprovements": common_accepted + h1_second_accepted,
        },
        "hybrid-top2": {
            "bestRecovery": h2_best,
            "winner": h2_winner.id,
            "evaluations": len(h2_pool),
            "exploitValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in common_children + top2_second),
            "uniquePhenotypeRate": _pool_unique_rate(h2_pool),
            "acceptedImprovementsTop1": common_accepted,
            "acceptedImprovementsTop2": h2_second_accepted,
            "winnerFromSecondBasin": h2_winner.id in h2_basin2_ids,
        },
    }

    hard = {
        "sharedDiscoveryHas12Evaluations": len(discovery_pool) == COMMON_STARTS + DISCOVERY_DRAWS,
        "twoDistinctValidAnchors": top1.id != top2.id and top1.valid and top2.valid,
        "equalTwentyEvaluationBudget": all(policy["evaluations"] == TOTAL_EVALUATIONS for policy in policies.values()),
        "firstCycleExactlyShared": len(first_cycle_fps) == 4,
        "firstCycleEventScheduleLength4": len(first_events) == 4,
        "secondCycleEventSchedulesMatch": second_h1_hash == second_h2_hash and len(second_events_h1) == 4,
        "firstAndSecondAnglesFrozen": [row["angle"] for row in first_events] == list(ANGLES)
        and [row["angle"] for row in second_events_h1] == list(ANGLES),
        "discoveryHashPresent": bool(discovery_hash),
        "firstEventHashPresent": bool(first_event_hash),
    }

    return {
        "target": target.id,
        "family": target.family,
        "targetFingerprint": _fingerprint(target.image),
        "discoveryHash": discovery_hash,
        "anchor1": {"id": top1.id, "recovery": top1_recovery, "fingerprint": _fingerprint(top1.image)},
        "anchor2": {"id": top2.id, "recovery": top2_recovery, "fingerprint": _fingerprint(top2.image)},
        "anchorRecoveryGap": top1_recovery - top2_recovery,
        "firstCycleEventHash": first_event_hash,
        "secondCycleEventHash": second_h1_hash,
        "policies": policies,
        "effects": {
            "top2VsBreadth": h2_best - breadth_best,
            "top2VsTop1": h2_best - h1_best,
            "top1VsBreadth": h1_best - breadth_best,
            "top2MeaningfulVsBreadth": h2_best - breadth_best > MEANINGFUL_MARGIN,
        },
        "hardInvariants": hard,
    }


def run_seed(seed: int, population: str) -> dict:
    allowed = (SMOKE_SEED,) if population == "smoke" else PILOT_SEEDS if population == "pilot" else ()
    if seed not in allowed:
        raise ValueError(f"seed {seed} not declared for population {population}")

    target_contract = target_contract_v2()
    if not target_contract["valid"]:
        raise AssertionError(target_contract)
    targets = build_targets_v2()

    rasterizer = capacity.FieldRasterizer()
    starts, start_attempts = _common_starts(seed, rasterizer)
    discovery_draws = _independent_draws(seed, rasterizer, "shared-discovery", DISCOVERY_DRAWS, "D")
    breadth_tail = _independent_draws(seed, rasterizer, "breadth-tail", TAIL_EVALUATIONS, "B")
    discovery_pool = starts + discovery_draws

    target_records = [
        _target_run(seed, target, discovery_pool, breadth_tail, rasterizer)
        for target in targets
    ]

    target_fps = [record["targetFingerprint"] for record in target_records]
    discovery_hashes = {record["discoveryHash"] for record in target_records}
    hard = {
        "exactTargetRectangle": len(target_records) == 15,
        "targetSuiteContractValid": bool(target_contract["valid"]),
        "targetSuiteDisjointFromV1": bool(target_contract["disjointFromV1"]),
        "allTargetHardInvariants": all(all(record["hardInvariants"].values()) for record in target_records),
        "commonStartsValid": all(candidate.valid for candidate in starts),
        "commonStartsDistinct": len({_fingerprint(candidate.image) for candidate in starts}) == COMMON_STARTS,
        "sharedDiscoveryPoolIdenticalAcrossTargets": len(discovery_hashes) == 1,
        "targetFingerprintsDistinct": len(set(target_fps)) == 15,
    }

    return {
        "version": 2,
        "experiment": "sampling-invariance-search-v2",
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
            "fieldBandwidth": capacity.FIELD_BANDWIDTH,
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
    parser.add_argument("--population", choices=("smoke", "pilot"), required=True)
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
