#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHORTLIST_DIR = ROOT / "experiments" / "delivery-dispersion-shortlist-v1"
sys.path.insert(0, str(SHORTLIST_DIR))

import run_shortlist as base

core = base.core
search_engine = base.search_engine
derived_seed = base.derived_seed

ROUTES = ("recurrence", "orbit", "filament")
FULL_ATTEMPTS = 20
MIN_VALID_FOR_SIGNAL = 12
STABLE_ADDITIONS = 3
NONINFERIORITY_MARGIN = 0.003255297955511336
SMOKE_SEED = 744999
MASTER_SEEDS = (
    744003, 744019, 744037, 744053, 744071,
    744089, 744107, 744127, 744149, 744167,
    744181, 744199, 744223, 744239, 744257,
    744277, 744293, 744311, 744331, 744349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str) -> dict:
    return {
        "name": "delivery-saturation-stop-v1",
        "artistic_intent": "target-blind stopping-signal experiment only; no artistic authority",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.MIXED_1D_V1,
    }


def _all_generated(state: core.SearchState) -> list[core.Candidate]:
    return [
        c for c in state.candidates.values()
        if c.stage != "start"
        and c.checks.get("generationOperator") in {"native", "spectral"}
    ]


def _valid_generated(cands: list[core.Candidate]) -> list[core.Candidate]:
    return [c for c in cands if bool(c.checks.get("valid", False))]


def _dispersion_trio(cands: list[core.Candidate]) -> dict:
    if len(cands) < 3:
        raise AssertionError("need at least three candidates for a dispersion trio")
    hashes = [base._phenotype_hash(c) for c in cands]
    if len(set(hashes)) < 3:
        raise AssertionError("candidate prefix has fewer than three distinct phenotype hashes")
    distances = base._distance_matrix(cands)
    best_combo = None
    best_score = None
    eps = 1e-15
    for combo in itertools.combinations(range(len(cands)), 3):
        score = base._combo_dispersion(combo, distances)
        if best_score is None:
            best_combo, best_score = combo, score
            continue
        if score[0] > best_score[0] + eps or (
            abs(score[0] - best_score[0]) <= eps and score[1] > best_score[1] + eps
        ):
            best_combo, best_score = combo, score
    assert best_combo is not None and best_score is not None
    selected = [cands[i] for i in best_combo]
    selected_hashes = [base._phenotype_hash(c) for c in selected]
    if len(set(selected_hashes)) != 3:
        raise AssertionError("dispersion trio does not contain three distinct phenotypes")
    return {
        "indices": list(best_combo),
        "candidateIds": [c.id for c in selected],
        "phenotypeHashes": selected_hashes,
        "minimumPairwiseDistance": float(best_score[0]),
        "meanPairwiseDistance": float(best_score[1]),
        "candidates": selected,
    }


def _derive_stop(generated: list[core.Candidate]) -> dict:
    if len(generated) != FULL_ATTEMPTS:
        raise AssertionError(f"expected {FULL_ATTEMPTS} generated attempts; found {len(generated)}")

    valid_prefix: list[core.Candidate] = []
    previous_ids: tuple[str, ...] | None = None
    stable_count = 0
    stop_attempt = FULL_ATTEMPTS
    stop_reason = "full-budget"
    checkpoints = []

    for attempt, cand in enumerate(generated, start=1):
        if not bool(cand.checks.get("valid", False)):
            continue
        valid_prefix.append(cand)
        if len(valid_prefix) < MIN_VALID_FOR_SIGNAL:
            continue

        trio = _dispersion_trio(valid_prefix)
        ids = tuple(str(x) for x in trio["candidateIds"])
        changed = previous_ids is None or ids != previous_ids
        if previous_ids is None:
            stable_count = 0
        elif ids == previous_ids:
            stable_count += 1
        else:
            stable_count = 0
        checkpoints.append({
            "attempt": attempt,
            "validCount": len(valid_prefix),
            "candidateIds": list(ids),
            "minimumPairwiseDistance": trio["minimumPairwiseDistance"],
            "meanPairwiseDistance": trio["meanPairwiseDistance"],
            "changed": changed,
            "stableAdditionCount": stable_count,
        })
        previous_ids = ids

        if stable_count >= STABLE_ADDITIONS:
            stop_attempt = attempt
            stop_reason = "stable-dispersion-trio"
            break

    prefix_generated = generated[:stop_attempt]
    stopped_valid = _valid_generated(prefix_generated)
    full_valid = _valid_generated(generated)
    if len(full_valid) < MIN_VALID_FOR_SIGNAL:
        raise AssertionError(
            f"need >={MIN_VALID_FOR_SIGNAL} hard-valid challengers in full trajectory; found {len(full_valid)}"
        )
    if len(stopped_valid) < MIN_VALID_FOR_SIGNAL:
        raise AssertionError("derived stop prefix has fewer than minimum valid challengers")

    stopped_trio = _dispersion_trio(stopped_valid)
    full_trio = _dispersion_trio(full_valid)

    return {
        "stopAttempt": stop_attempt,
        "attemptsSaved": FULL_ATTEMPTS - stop_attempt,
        "stopReason": stop_reason,
        "stoppedValidCount": len(stopped_valid),
        "fullValidCount": len(full_valid),
        "stoppedTrio": stopped_trio,
        "fullTrio": full_trio,
        "stoppedValidCandidates": stopped_valid,
        "fullValidCandidates": full_valid,
        "signalCheckpoints": checkpoints,
    }


def _images(cands: list[core.Candidate]):
    return [core.render_candidate_frame(c, base.CANONICAL_TIME) for c in cands]


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    route_records = {}
    archives = {}

    with tempfile.TemporaryDirectory(prefix=f"delivery-saturation-stop-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            search_seed = derived_seed(master_seed, "delivery-saturation-stop-v1", route)
            state, report = search_engine.run_search(_brief(route), search_seed, root / route)
            diag = base._operator_diag(state)
            if diag["total"] != FULL_ATTEMPTS or diag["native"] != 10 or diag["spectral"] != 10:
                raise AssertionError(f"mixed budget drift for {route}: {diag}")

            generated = _all_generated(state)
            if len(generated) != FULL_ATTEMPTS:
                raise AssertionError(f"generated attempt count drift for {route}: {len(generated)}")
            stop = _derive_stop(generated)

            stopped_trio = stop["stoppedTrio"]
            full_trio = stop["fullTrio"]
            route_records[route] = {
                "searchSeed": search_seed,
                "operatorDiagnostics": diag,
                "selectionStatus": report["selectionStatus"],
                "provisionalChampion": report["provisionalChampion"],
                "stopAttempt": stop["stopAttempt"],
                "attemptsSaved": stop["attemptsSaved"],
                "stopReason": stop["stopReason"],
                "stoppedValidCount": stop["stoppedValidCount"],
                "fullValidCount": stop["fullValidCount"],
                "stoppedTrio": {
                    k: v for k, v in stopped_trio.items() if k != "candidates"
                },
                "fullTrio": {
                    k: v for k, v in full_trio.items() if k != "candidates"
                },
                "signalCheckpoints": stop["signalCheckpoints"],
            }
            archives[route] = {
                "stoppedDelivery": _images(stopped_trio["candidates"]),
                "fullDelivery": _images(full_trio["candidates"]),
                "stoppedArchive": _images(stop["stoppedValidCandidates"]),
                "fullArchive": _images(stop["fullValidCandidates"]),
            }

        # Targets are deliberately constructed only after all route stop points and
        # all stopped/full delivery identities have been frozen target-blind.
        targets = base.build_targets_runtime()
        cells = []
        for route in ROUTES:
            for target in targets:
                stopped_delivery = max(base._recovery(im, target.image) for im in archives[route]["stoppedDelivery"])
                full_delivery = max(base._recovery(im, target.image) for im in archives[route]["fullDelivery"])
                stopped_archive = max(base._recovery(im, target.image) for im in archives[route]["stoppedArchive"])
                full_archive = max(base._recovery(im, target.image) for im in archives[route]["fullArchive"])
                cells.append({
                    "masterSeed": master_seed,
                    "route": route,
                    "targetId": target.id,
                    "targetFamily": target.family,
                    "stoppedDeliveryRecovery": stopped_delivery,
                    "fullDeliveryRecovery": full_delivery,
                    "deliveryLoss": full_delivery - stopped_delivery,
                    "stoppedArchiveRecovery": stopped_archive,
                    "fullArchiveRecovery": full_archive,
                    "archiveLoss": full_archive - stopped_archive,
                })

    hard = {
        "routeSetExact": tuple(route_records) == ROUTES,
        "mixedBudgetExact": all(
            route_records[r]["operatorDiagnostics"]["total"] == FULL_ATTEMPTS
            and route_records[r]["operatorDiagnostics"]["native"] == 10
            and route_records[r]["operatorDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "minimumFullValidMet": all(
            route_records[r]["fullValidCount"] >= MIN_VALID_FOR_SIGNAL for r in ROUTES
        ),
        "minimumStoppedValidMet": all(
            route_records[r]["stoppedValidCount"] >= MIN_VALID_FOR_SIGNAL for r in ROUTES
        ),
        "stopAttemptInRange": all(
            MIN_VALID_FOR_SIGNAL <= route_records[r]["stopAttempt"] <= FULL_ATTEMPTS for r in ROUTES
        ),
        "threeDistinctStoppedPhenotypes": all(
            len(set(route_records[r]["stoppedTrio"]["phenotypeHashes"])) == 3 for r in ROUTES
        ),
        "threeDistinctFullPhenotypes": all(
            len(set(route_records[r]["fullTrio"]["phenotypeHashes"])) == 3 for r in ROUTES
        ),
        "cellCountExact": len(cells) == 45,
    }
    if not all(hard.values()):
        raise AssertionError(f"hard invariant failure: {hard}")

    return {
        "version": 1,
        "masterSeed": master_seed,
        "smoke": smoke,
        "artisticEvidence": False,
        "settings": {
            "routes": list(ROUTES),
            "fullAttempts": FULL_ATTEMPTS,
            "mixedNativeAttempts": 10,
            "mixedSpectralAttempts": 10,
            "minimumValidForSignal": MIN_VALID_FOR_SIGNAL,
            "stableAdditionsRequired": STABLE_ADDITIONS,
            "noninferiorityMargin": NONINFERIORITY_MARGIN,
            "signal": "three consecutive hard-valid additions leave exact max-dispersion trio ids unchanged",
            "canonicalStructuralTime": base.CANONICAL_TIME,
            "structuralMetric": "sparse-geometry-v1-exact-fast-grayscale",
        },
        "hardInvariants": hard,
        "routes": route_records,
        "cells": cells,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--output")
    args = p.parse_args()
    result = run_seed(args.seed, smoke=args.smoke)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
