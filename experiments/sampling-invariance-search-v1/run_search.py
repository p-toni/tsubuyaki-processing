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
sys.path.insert(0, str(CAPACITY_DIR))

import run_capacity
import fast_binary_metric as metric

capacity = run_capacity.capacity

from spectral_operator import geodesic_mutate

STREAM = "sampling-invariance-search-v1"
SMOKE_SEED = 94999
PILOT_SEEDS = (
    95003,
    95009,
    95021,
    95027,
    95063,
    95071,
    95083,
    95087,
    95089,
    95093,
    95101,
    95107,
    95111,
    95131,
    95143,
    95153,
    95177,
    95189,
    95191,
    95203,
)
COMMON_STARTS = 4
EXTRA_EVALUATIONS = 16
TOTAL_EVALUATIONS = COMMON_STARTS + EXTRA_EVALUATIONS
ANGLES = (0.04, 0.08, 0.16, 0.32) * 4
MEANINGFUL_MARGIN = 0.005
EPSILON = 1e-12


@dataclass
class FieldCandidate:
    id: str
    coefficients: np.ndarray
    image: object
    valid: bool


def _rng(*parts: object) -> np.random.Generator:
    payload = "|".join(str(part) for part in (STREAM,) + parts)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big", signed=False))


def _event_seed(seed: int, target_id: str, event_index: int) -> int:
    payload = f"{STREAM}|{seed}|{target_id}|event|{event_index}"
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _render(coefficients: np.ndarray, rasterizer) -> FieldCandidate:
    image = rasterizer.image(coefficients)
    valid, _geometry = capacity._field_valid(image)
    return FieldCandidate("", coefficients, image, bool(valid))


def _common_starts(seed: int, rasterizer) -> tuple[list[FieldCandidate], int]:
    rng = _rng(seed, "common-starts")
    starts = []
    attempts = 0
    while len(starts) < COMMON_STARTS and attempts < COMMON_STARTS * 20:
        attempts += 1
        coefficients = capacity._draw_field_coefficients(rng)
        candidate = _render(coefficients, rasterizer)
        if not candidate.valid:
            continue
        candidate.id = f"S{len(starts) + 1}"
        starts.append(candidate)
    if len(starts) != COMMON_STARTS:
        raise RuntimeError(f"seed {seed}: only {len(starts)} valid common starts")
    return starts, attempts


def _breadth(seed: int, rasterizer) -> list[FieldCandidate]:
    rng = _rng(seed, "independent-breadth")
    out = []
    for index in range(EXTRA_EVALUATIONS):
        coefficients = capacity._draw_field_coefficients(rng)
        candidate = _render(coefficients, rasterizer)
        candidate.id = f"B{index + 1}"
        out.append(candidate)
    return out


def _recovery(candidate: FieldCandidate, target_image) -> float:
    if not candidate.valid:
        return float("-inf")
    distance = float(metric.sparse_geometry_distance((candidate.image,), (target_image,))["distance"])
    return 1.0 - distance


def _best(candidates: list[FieldCandidate], target_image) -> tuple[FieldCandidate, float]:
    scored = [(_recovery(candidate, target_image), candidate.id, candidate) for candidate in candidates]
    recovery, _id, candidate = max(scored, key=lambda item: (item[0], item[1]))
    if not np.isfinite(recovery):
        raise AssertionError("candidate pool has no valid member")
    return candidate, recovery


def _unique_rate(candidates: list[FieldCandidate]) -> float:
    return len({_fingerprint(candidate.image) for candidate in candidates}) / len(candidates)


def _target_run(
    seed: int,
    target,
    starts: list[FieldCandidate],
    breadth_extra: list[FieldCandidate],
    rasterizer,
) -> dict:
    initial_parent, initial_best = _best(starts, target.image)

    breadth_pool = starts + breadth_extra
    _breadth_winner, breadth_best = _best(breadth_pool, target.image)

    fixed_parent = initial_parent
    fixed_children: list[FieldCandidate] = []
    adaptive_parent = initial_parent
    adaptive_parent_recovery = initial_best
    adaptive_children: list[FieldCandidate] = []
    accepted_improvements = 0
    event_labels = []

    for event_index, angle in enumerate(ANGLES):
        event_seed = _event_seed(seed, target.id, event_index)
        event_labels.append({"index": event_index, "angle": angle, "seed": event_seed})

        fixed_rng = np.random.default_rng(event_seed)
        fixed_coefficients = geodesic_mutate(fixed_parent.coefficients, fixed_rng, angle)
        fixed_child = _render(fixed_coefficients, rasterizer)
        fixed_child.id = f"F{event_index + 1}"
        fixed_children.append(fixed_child)

        adaptive_rng = np.random.default_rng(event_seed)
        adaptive_coefficients = geodesic_mutate(adaptive_parent.coefficients, adaptive_rng, angle)
        adaptive_child = _render(adaptive_coefficients, rasterizer)
        adaptive_child.id = f"A{event_index + 1}"
        adaptive_children.append(adaptive_child)
        adaptive_recovery = _recovery(adaptive_child, target.image)
        if adaptive_child.valid and adaptive_recovery > adaptive_parent_recovery + EPSILON:
            adaptive_parent = adaptive_child
            adaptive_parent_recovery = adaptive_recovery
            accepted_improvements += 1

    fixed_pool = starts + fixed_children
    adaptive_pool = starts + adaptive_children
    _fixed_winner, fixed_best = _best(fixed_pool, target.image)
    _adaptive_winner, adaptive_best = _best(adaptive_pool, target.image)

    event_hash = hashlib.sha256(
        json.dumps(event_labels, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    start_fingerprints = [_fingerprint(candidate.image) for candidate in starts]

    policy_records = {
        "independent-breadth": {
            "bestRecovery": breadth_best,
            "incrementalValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in breadth_extra),
            "uniquePhenotypeRate": _unique_rate(breadth_pool),
            "evaluations": len(breadth_pool),
        },
        "fixed-parent-geodesic": {
            "bestRecovery": fixed_best,
            "incrementalValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in fixed_children),
            "uniquePhenotypeRate": _unique_rate(fixed_pool),
            "evaluations": len(fixed_pool),
            "initialParent": fixed_parent.id,
            "eventHash": event_hash,
        },
        "adaptive-geodesic": {
            "bestRecovery": adaptive_best,
            "incrementalValidYield": statistics.fmean(1.0 if candidate.valid else 0.0 for candidate in adaptive_children),
            "uniquePhenotypeRate": _unique_rate(adaptive_pool),
            "evaluations": len(adaptive_pool),
            "initialParent": initial_parent.id,
            "eventHash": event_hash,
            "acceptedImprovements": accepted_improvements,
        },
    }

    hard = {
        "sharedFourStarts": len(start_fingerprints) == COMMON_STARTS and len(set(start_fingerprints)) == COMMON_STARTS,
        "equalTwentyEvaluationBudget": all(record["evaluations"] == TOTAL_EVALUATIONS for record in policy_records.values()),
        "sameFixedAdaptiveInitialParent": policy_records["fixed-parent-geodesic"]["initialParent"] == policy_records["adaptive-geodesic"]["initialParent"],
        "sameFixedAdaptiveEventHash": policy_records["fixed-parent-geodesic"]["eventHash"] == policy_records["adaptive-geodesic"]["eventHash"],
        "eventScheduleLength16": len(event_labels) == EXTRA_EVALUATIONS,
    }

    return {
        "target": target.id,
        "family": target.family,
        "targetFingerprint": _fingerprint(target.image),
        "startFingerprints": start_fingerprints,
        "initialBestRecovery": initial_best,
        "policies": policy_records,
        "effects": {
            "adaptiveVsBreadth": adaptive_best - breadth_best,
            "adaptiveVsFixed": adaptive_best - fixed_best,
            "adaptiveGainFromInitial": adaptive_best - initial_best,
            "adaptiveMeaningfulVsBreadth": adaptive_best - breadth_best > MEANINGFUL_MARGIN,
        },
        "hardInvariants": hard,
    }


def run_seed(seed: int, population: str) -> dict:
    if population == "smoke":
        allowed = (SMOKE_SEED,)
    elif population == "pilot":
        allowed = PILOT_SEEDS
    else:
        allowed = ()
    if seed not in allowed:
        raise ValueError(f"seed {seed} not declared for population {population}")

    targets = capacity.build_targets()
    target_check = capacity.target_contract(targets)
    if not target_check["valid"]:
        raise AssertionError(target_check["failures"])

    rasterizer = capacity.FieldRasterizer()
    starts, start_attempts = _common_starts(seed, rasterizer)
    breadth_extra = _breadth(seed, rasterizer)
    target_records = [
        _target_run(seed, target, starts, breadth_extra, rasterizer)
        for target in targets
    ]

    target_fingerprints = [record["targetFingerprint"] for record in target_records]
    hard = {
        "exactTargetRectangle": len(target_records) == 15,
        "allTargetHardInvariants": all(all(record["hardInvariants"].values()) for record in target_records),
        "commonStartsValid": all(candidate.valid for candidate in starts),
        "commonStartsDistinct": len({_fingerprint(candidate.image) for candidate in starts}) == COMMON_STARTS,
        "targetFingerprintsDistinct": len(set(target_fingerprints)) == len(target_fingerprints),
    }

    return {
        "version": 1,
        "experiment": "sampling-invariance-search-v1",
        "population": population,
        "seed": seed,
        "settings": {
            "commonStarts": COMMON_STARTS,
            "extraEvaluations": EXTRA_EVALUATIONS,
            "totalEvaluationsPerPolicyTarget": TOTAL_EVALUATIONS,
            "angles": list(ANGLES),
            "meaningfulMargin": MEANINGFUL_MARGIN,
            "metric": "sparse-geometry-v1-exact-binary-equivalent",
            "fieldBandwidth": capacity.FIELD_BANDWIDTH,
        },
        "startDiagnostics": {
            "attemptsForFourValidStarts": start_attempts,
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
