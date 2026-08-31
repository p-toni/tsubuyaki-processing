#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OP_DIR = ROOT / "experiments" / "operator-novelty-allocation-v1"
sys.path.insert(0, str(OP_DIR))

import run_allocation as op

base = op.base
core = op.core
search_engine = op.search_engine
derived_seed = op.derived_seed

ROUTES = ("recurrence", "orbit", "filament")
MARGINAL_ATTEMPTS = 4
LOCAL_SCHEDULE = ("native", "spectral", "native", "spectral")
LOCAL_SCALE = 0.55
DELIVERY_MARGIN = 0.003255297955511336

SMOKE_SEED = 746999
MASTER_SEEDS = (
    746003, 746019, 746037, 746053, 746071,
    746089, 746107, 746127, 746149, 746167,
    746181, 746199, 746223, 746239, 746257,
    746277, 746293, 746311, 746331, 746349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str) -> dict:
    return {
        "name": "independent-starts-marginal-v1",
        "artistic_intent": "mechanical marginal-search screen only; no artistic authority",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.MIXED_1D_V1,
    }


def _baseline_fingerprint(run: dict) -> list[dict]:
    state = run["state"]
    attempts = op._operator_attempts(state)
    return [
        {
            "candidateId": c.id,
            "operator": c.checks.get("generationOperator"),
            "valid": bool(c.checks.get("valid", False)),
            "phenotypeHash": base._phenotype_hash(c),
        }
        for c in attempts
    ]


def _spawn_local(
    route: str,
    search_seed: int,
    parent: core.Candidate,
    index: int,
    operator: str,
) -> core.Candidate:
    brief = _brief(route)
    rng = random.Random(
        derived_seed(search_seed, "independent-starts-marginal-v1", "deep-local", index)
    )
    cid = f"{parent.basin}-ML{index + 1}"
    if operator == "native":
        genome = search_engine.mutate_native(
            core.ROUTES[route], parent.genome, rng, LOCAL_SCALE
        )
    elif operator == "spectral":
        field_seed = derived_seed(
            search_seed,
            "independent-starts-marginal-v1",
            "deep-local-spectral",
            index,
            parent.id,
        )
        genome = search_engine.with_spectral_control(parent.genome, field_seed)
    else:
        raise ValueError(operator)
    cand = core.Candidate(
        cid,
        route,
        parent.basin,
        genome,
        parent.id,
        "marginal-local",
    )
    core.evaluate_candidate(cand, brief)
    cand.checks["generationOperator"] = operator
    cand.checks["marginalArm"] = "deepLocal24"
    return cand


def _deep_local(route: str, search_seed: int, baseline: dict) -> dict:
    state = baseline["state"]
    champion = state.candidates[baseline["record"]["provisionalChampion"]]
    selector = search_engine.DeterministicTemporalSelector()
    extras = []
    decisions = []

    for i, operator in enumerate(LOCAL_SCHEDULE):
        cand = _spawn_local(route, search_seed, champion, i, operator)
        extras.append(cand)
        next_champion, decision = search_engine.incumbent_challenge(
            selector, champion, cand, _brief(route)
        )
        decisions.append(decision.to_json())
        champion = next_champion

    valid_extras = [c for c in extras if bool(c.checks.get("valid", False))]
    archive = list(baseline["generatedValid"]) + valid_extras
    shortlist = base._select_shortlists(archive)
    return {
        "extras": extras,
        "validExtras": valid_extras,
        "archive": archive,
        "deliveryCandidates": shortlist["dispersionCandidates"],
        "record": {
            "attemptCount": len(extras),
            "validExtraCount": len(valid_extras),
            "schedule": list(LOCAL_SCHEDULE),
            "scale": LOCAL_SCALE,
            "finalChampionId": champion.id,
            "decisions": decisions,
            "delivery": shortlist["dispersion"],
        },
    }


def _spawn_restart(route: str, search_seed: int, index: int) -> core.Candidate:
    brief = _brief(route)
    rng = random.Random(
        derived_seed(search_seed, "independent-starts-marginal-v1", "restart", index)
    )
    prefix = core.ROUTES[route].get("prefix", route[:1].upper())
    cid = f"{prefix}MR{index + 1}"
    genome = core.ROUTES[route]["seed"](rng)
    cand = core.Candidate(
        cid,
        route,
        cid,
        genome,
        None,
        "marginal-restart",
    )
    core.evaluate_candidate(cand, brief)
    cand.checks["generationOperator"] = "restart"
    cand.checks["marginalArm"] = "independentStarts24"
    return cand


def _independent_starts(route: str, search_seed: int, baseline: dict) -> dict:
    extras = [_spawn_restart(route, search_seed, i) for i in range(MARGINAL_ATTEMPTS)]
    valid_extras = [c for c in extras if bool(c.checks.get("valid", False))]
    archive = list(baseline["generatedValid"]) + valid_extras
    shortlist = base._select_shortlists(archive)
    return {
        "extras": extras,
        "validExtras": valid_extras,
        "archive": archive,
        "deliveryCandidates": shortlist["dispersionCandidates"],
        "record": {
            "attemptCount": len(extras),
            "validExtraCount": len(valid_extras),
            "oneShotNoRetry": True,
            "delivery": shortlist["dispersion"],
        },
    }


def _images(cands: list[core.Candidate]):
    return [core.render_candidate_frame(c, base.CANONICAL_TIME) for c in cands]


def _recovery(images, target_image) -> float:
    return max(base._recovery(im, target_image) for im in images)


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    routes = {}
    frozen = {}
    smoke_equivalence = {}

    with tempfile.TemporaryDirectory(prefix=f"independent-starts-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            search_seed = derived_seed(master_seed, "independent-starts-marginal-v1", route)

            baseline = op._run_arm(route, search_seed, "baseline10x10")
            baseline_diag = baseline["record"]["operatorDiagnostics"]
            if not (
                baseline_diag["total"] == 20
                and baseline_diag["native"] == 10
                and baseline_diag["spectral"] == 10
            ):
                raise AssertionError(f"baseline operator budget drift: {baseline_diag}")

            local = _deep_local(route, search_seed, baseline)
            restarts = _independent_starts(route, search_seed, baseline)

            if len(local["extras"]) != MARGINAL_ATTEMPTS:
                raise AssertionError("local marginal attempt drift")
            if len(restarts["extras"]) != MARGINAL_ATTEMPTS:
                raise AssertionError("restart marginal attempt drift")
            if [c.checks.get("generationOperator") for c in local["extras"]] != list(LOCAL_SCHEDULE):
                raise AssertionError("local marginal operator schedule drift")
            if any(c.parent_id is not None for c in restarts["extras"]):
                raise AssertionError("restart parenting drift")

            reference_exact = None
            if smoke:
                ref = op._reference_baseline(route, search_seed, root / f"reference-{route}")
                reference_exact = (
                    _baseline_fingerprint(baseline) == ref["attempts"]
                    and baseline["record"]["provisionalChampion"] == ref["provisionalChampion"]
                    and baseline_diag == ref["operatorDiagnostics"]
                )
                if not reference_exact:
                    raise AssertionError(f"baseline runtime replay mismatch for {route}")
                smoke_equivalence[route] = True

            baseline_archive = list(baseline["generatedValid"])
            if len(baseline_archive) < base.MIN_VALID_GENERATED:
                raise AssertionError("baseline valid archive below promoted shortlist minimum")

            routes[route] = {
                "searchSeed": search_seed,
                "baseline": {
                    "operatorDiagnostics": baseline_diag,
                    "validGeneratedCount": len(baseline_archive),
                    "provisionalChampion": baseline["record"]["provisionalChampion"],
                    "fingerprint": _baseline_fingerprint(baseline),
                    "delivery": baseline["record"]["delivery"],
                },
                "deepLocal24": local["record"],
                "independentStarts24": restarts["record"],
                "smokeBaselineRuntimeReplayExact": reference_exact,
            }
            frozen[route] = {
                "baselineArchive": _images(baseline_archive),
                "localArchive": _images(local["archive"]),
                "restartArchive": _images(restarts["archive"]),
                "baselineDelivery": _images(baseline["deliveryCandidates"]),
                "localDelivery": _images(local["deliveryCandidates"]),
                "restartDelivery": _images(restarts["deliveryCandidates"]),
            }

        targets = base.build_targets_runtime()
        cells = []
        for route in ROUTES:
            ims = frozen[route]
            for target in targets:
                baseline_archive = _recovery(ims["baselineArchive"], target.image)
                local_archive = _recovery(ims["localArchive"], target.image)
                restart_archive = _recovery(ims["restartArchive"], target.image)
                baseline_delivery = _recovery(ims["baselineDelivery"], target.image)
                local_delivery = _recovery(ims["localDelivery"], target.image)
                restart_delivery = _recovery(ims["restartDelivery"], target.image)
                cells.append({
                    "masterSeed": master_seed,
                    "route": route,
                    "targetId": target.id,
                    "targetFamily": target.family,
                    "baselineArchiveRecovery": baseline_archive,
                    "deepLocalArchiveRecovery": local_archive,
                    "independentStartsArchiveRecovery": restart_archive,
                    "localMarginalArchiveGain": local_archive - baseline_archive,
                    "restartMarginalArchiveGain": restart_archive - baseline_archive,
                    "restartMinusLocalArchive": restart_archive - local_archive,
                    "baselineDeliveryRecovery": baseline_delivery,
                    "deepLocalDeliveryRecovery": local_delivery,
                    "independentStartsDeliveryRecovery": restart_delivery,
                    "restartMinusLocalDelivery": restart_delivery - local_delivery,
                    "restartMinusBaselineDelivery": restart_delivery - baseline_delivery,
                })

    hard = {
        "routeSetExact": tuple(routes) == ROUTES,
        "baselineBudgetExact": all(
            routes[r]["baseline"]["operatorDiagnostics"]["total"] == 20
            and routes[r]["baseline"]["operatorDiagnostics"]["native"] == 10
            and routes[r]["baseline"]["operatorDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "fourLocalEvaluationsExact": all(
            routes[r]["deepLocal24"]["attemptCount"] == 4 for r in ROUTES
        ),
        "fourRestartEvaluationsExact": all(
            routes[r]["independentStarts24"]["attemptCount"] == 4 for r in ROUTES
        ),
        "localScheduleExact": all(
            routes[r]["deepLocal24"]["schedule"] == list(LOCAL_SCHEDULE) for r in ROUTES
        ),
        "localScaleExact": all(
            routes[r]["deepLocal24"]["scale"] == LOCAL_SCALE for r in ROUTES
        ),
        "restartOneShotNoRetry": all(
            routes[r]["independentStarts24"]["oneShotNoRetry"] is True for r in ROUTES
        ),
        "cellCountExact": len(cells) == 45,
        "smokeBaselineRuntimeReplayExact": (
            all(smoke_equivalence.get(r, False) for r in ROUTES) if smoke else True
        ),
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
            "sharedBaselineAttempts": 20,
            "sharedBaselineNative": 10,
            "sharedBaselineSpectral": 10,
            "marginalEvaluationsPerArm": MARGINAL_ATTEMPTS,
            "deepLocalSchedule": list(LOCAL_SCHEDULE),
            "deepLocalScale": LOCAL_SCALE,
            "restartDefinition": "four independent one-shot route-prior draws; invalid consumes evaluation; no retry",
            "deliveryRule": "target-blind three-item max-dispersion over hard-valid generated archive",
            "deliveryNonInferiorityMargin": DELIVERY_MARGIN,
            "canonicalStructuralTime": base.CANONICAL_TIME,
            "structuralMetric": "sparse-geometry-v1-exact-fast-grayscale",
        },
        "hardInvariants": hard,
        "smokeBaselineEquivalence": smoke_equivalence,
        "routes": routes,
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
