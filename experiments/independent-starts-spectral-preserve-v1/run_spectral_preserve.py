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
MEANINGFUL_MARGIN = 0.003255297955511336
SMOKE_SEED = 751999
MASTER_SEEDS = (
    751003, 751019, 751037, 751053, 751071,
    751089, 751107, 751127, 751149, 751167,
    751181, 751199, 751223, 751239, 751257,
    751277, 751293, 751311, 751331, 751349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _fingerprint(cands: list[core.Candidate]) -> list[dict]:
    return [
        {
            "candidateId": c.id,
            "operator": c.checks.get("generationOperator"),
            "valid": bool(c.checks.get("valid", False)),
            "phenotypeHash": base._phenotype_hash(c),
        }
        for c in cands
    ]


def _spawn_restart(route: str, search_seed: int, index: int) -> core.Candidate:
    rng = random.Random(
        derived_seed(search_seed, "independent-starts-spectral-preserve-v1", "restart", index)
    )
    prefix = core.ROUTES[route].get("prefix", route[:1].upper())
    cid = f"{prefix}SPR{index + 1}"
    genome = core.ROUTES[route]["seed"](rng)
    cand = core.Candidate(cid, route, cid, genome, None, "restart-native-swap")
    core.evaluate_candidate(cand, op._brief(route))
    cand.checks["generationOperator"] = "restart"
    cand.checks["spectralPreserveArm"] = "spectralPreserve20"
    return cand


def _run_spectral_preserve(route: str, search_seed: int) -> dict:
    brief = op._brief(route)
    rng = random.Random(search_seed)
    selector = search_engine.DeterministicTemporalSelector()
    state = core.SearchState(brief, search_seed)

    start = op._seed_start(route, brief, rng, state)
    basin_id = start.id
    incumbent = start

    explore = []
    for j, operator in enumerate(("native", "native", "spectral", "spectral")):
        cid = f"{basin_id}-E{j+1}"
        cand = op._spawn_explicit(
            brief, search_seed, incumbent, cid, "explore", j, rng, 1.0, operator
        )
        state.candidates[cid] = cand
        explore.append(cand)
    incumbent = op._select_local(selector, incumbent, explore, brief, state, "explore")

    _, survivors, ds = search_engine.route_aware_frontier(selector, [incumbent], brief)
    op._record(state, "frontier", ds)
    if len(survivors) != 1:
        raise AssertionError("single-route frontier drift after explore")
    incumbent = survivors[0]

    round_a = []
    for j, operator in enumerate(("native", "native", "spectral", "spectral")):
        cid = f"{basin_id}-A{j+1}"
        cand = op._spawn_explicit(
            brief, search_seed, incumbent, cid, "roundA", j, rng, 0.7, operator
        )
        state.candidates[cid] = cand
        round_a.append(cand)
    incumbent = op._select_local(selector, incumbent, round_a, brief, state, "roundA")

    _, survivors, ds = search_engine.route_aware_frontier(selector, [incumbent], brief)
    op._record(state, "allocate-frontier", ds)
    if len(survivors) != 1:
        raise AssertionError("single-route frontier drift after roundA")
    incumbent = survivors[0]

    refine_incumbent = incumbent
    champion = refine_incumbent
    shared_refine = []

    for j in range(2):
        parent = champion
        cid = f"{basin_id}-R{j+1}"
        cand = op._spawn_explicit(
            brief, search_seed, parent, cid, "refine", j, rng, 0.55, "native"
        )
        state.candidates[cid] = cand
        shared_refine.append(cand)
        champion, decision = search_engine.incumbent_challenge(
            selector, champion, cand, brief
        )
        op._record(state, "refine", [decision])

    shared_attempts = explore + round_a + shared_refine
    if len(shared_attempts) != 10:
        raise AssertionError(f"shared prefix attempt drift: {len(shared_attempts)}")

    restarts = []
    for i in range(4):
        cand = _spawn_restart(route, search_seed, i)
        state.candidates[cand.id] = cand
        restarts.append(cand)

    spectral_tail = []
    for j in range(6, 12):
        parent = champion if j < 12 * 0.7 else refine_incumbent
        scale = 0.55 if j < 12 * 0.7 else 1.2
        cid = f"{basin_id}-R{j+1}"
        cand = op._spawn_explicit(
            brief, search_seed, parent, cid, "refine", j, rng, scale, "spectral"
        )
        state.candidates[cid] = cand
        spectral_tail.append(cand)
        champion, decision = search_engine.incumbent_challenge(
            selector, champion, cand, brief
        )
        op._record(state, "refine", [decision])

    generated = [
        c for c in state.candidates.values()
        if c.stage != "start"
        and c.checks.get("generationOperator") in {"native", "spectral", "restart"}
    ]
    valid_generated = [c for c in generated if bool(c.checks.get("valid", False))]
    if len(generated) != 20:
        raise AssertionError(f"treatment total budget drift: {len(generated)}")
    if len(valid_generated) < base.MIN_VALID_GENERATED:
        raise AssertionError("treatment valid archive below delivery minimum")

    shortlist = base._select_shortlists(valid_generated)
    return {
        "state": state,
        "start": start,
        "sharedAttempts": shared_attempts,
        "restarts": restarts,
        "spectralTail": spectral_tail,
        "generatedValid": valid_generated,
        "deliveryCandidates": shortlist["dispersionCandidates"],
        "record": {
            "totalGenerated": len(generated),
            "native": sum(c.checks.get("generationOperator") == "native" for c in generated),
            "spectral": sum(c.checks.get("generationOperator") == "spectral" for c in generated),
            "restart": sum(c.checks.get("generationOperator") == "restart" for c in generated),
            "validGenerated": len(valid_generated),
            "validRestarts": sum(bool(c.checks.get("valid", False)) for c in restarts),
            "sharedPrefixFingerprint": _fingerprint(shared_attempts),
            "spectralTailFingerprint": _fingerprint(spectral_tail),
            "startPhenotypeHash": base._phenotype_hash(start),
            "delivery": shortlist["dispersion"],
        },
    }


def _images(cands: list[core.Candidate]):
    return [core.render_candidate_frame(c, base.CANONICAL_TIME) for c in cands]


def _recovery(images, target_image) -> float:
    return max(base._recovery(im, target_image) for im in images)


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    routes = {}
    frozen = {}
    smoke_equivalence = {}
    smoke_r10_r12_exact = {}

    with tempfile.TemporaryDirectory(prefix=f"spectral-preserve-restart-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            search_seed = derived_seed(
                master_seed, "independent-starts-spectral-preserve-v1", route
            )
            baseline = op._run_arm(route, search_seed, "baseline10x10")
            treatment = _run_spectral_preserve(route, search_seed)

            baseline_attempts = op._operator_attempts(baseline["state"])
            if len(baseline_attempts) != 20:
                raise AssertionError("baseline total attempt drift")

            shared_exact = (
                _fingerprint(baseline_attempts[:10])
                == treatment["record"]["sharedPrefixFingerprint"]
            )
            start_exact = (
                baseline["record"]["startPhenotypeHash"]
                == treatment["record"]["startPhenotypeHash"]
            )
            if not shared_exact or not start_exact:
                raise AssertionError(f"shared prefix/start drift for {route}")

            r10_r12_exact = (
                _fingerprint(baseline_attempts[17:20])
                == _fingerprint(treatment["spectralTail"][3:6])
            )
            if not r10_r12_exact:
                raise AssertionError(f"baseline R10-R12 spectral replay drift for {route}")

            bdiag = baseline["record"]["operatorDiagnostics"]
            if not (
                bdiag["total"] == 20
                and bdiag["native"] == 10
                and bdiag["spectral"] == 10
            ):
                raise AssertionError(f"baseline budget drift: {bdiag}")
            tdiag = treatment["record"]
            if not (
                tdiag["totalGenerated"] == 20
                and tdiag["native"] == 6
                and tdiag["spectral"] == 10
                and tdiag["restart"] == 4
            ):
                raise AssertionError(f"treatment budget drift: {tdiag}")

            reference_exact = None
            if smoke:
                ref = op._reference_baseline(route, search_seed, root / f"ref-{route}")
                reference_exact = (
                    _fingerprint(baseline_attempts) == ref["attempts"]
                    and baseline["record"]["provisionalChampion"] == ref["provisionalChampion"]
                    and bdiag == ref["operatorDiagnostics"]
                )
                if not reference_exact:
                    raise AssertionError(f"baseline runtime replay mismatch for {route}")
                smoke_equivalence[route] = True
                smoke_r10_r12_exact[route] = r10_r12_exact

            routes[route] = {
                "searchSeed": search_seed,
                "baseline20": {
                    "operatorDiagnostics": bdiag,
                    "validGeneratedCount": len(baseline["generatedValid"]),
                    "delivery": baseline["record"]["delivery"],
                },
                "spectralPreserve20": treatment["record"],
                "sharedFirst10Exact": shared_exact,
                "sharedStartExact": start_exact,
                "baselineR10R12SpectralExact": r10_r12_exact,
                "smokeBaselineRuntimeReplayExact": reference_exact,
            }
            frozen[route] = {
                "baselineArchive": _images(baseline["generatedValid"]),
                "treatmentArchive": _images(treatment["generatedValid"]),
                "baselineDelivery": _images(baseline["deliveryCandidates"]),
                "treatmentDelivery": _images(treatment["deliveryCandidates"]),
            }

        targets = base.build_targets_runtime()
        cells = []
        for route in ROUTES:
            ims = frozen[route]
            for target in targets:
                ba = _recovery(ims["baselineArchive"], target.image)
                ta = _recovery(ims["treatmentArchive"], target.image)
                bd = _recovery(ims["baselineDelivery"], target.image)
                td = _recovery(ims["treatmentDelivery"], target.image)
                cells.append({
                    "masterSeed": master_seed,
                    "route": route,
                    "targetId": target.id,
                    "targetFamily": target.family,
                    "baselineArchiveRecovery": ba,
                    "treatmentArchiveRecovery": ta,
                    "archiveDelta": ta - ba,
                    "baselineDeliveryRecovery": bd,
                    "treatmentDeliveryRecovery": td,
                    "deliveryDelta": td - bd,
                })

    hard = {
        "routeSetExact": tuple(routes) == ROUTES,
        "baselineBudgetExact": all(
            routes[r]["baseline20"]["operatorDiagnostics"]["total"] == 20
            and routes[r]["baseline20"]["operatorDiagnostics"]["native"] == 10
            and routes[r]["baseline20"]["operatorDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "treatmentBudgetExact": all(
            routes[r]["spectralPreserve20"]["totalGenerated"] == 20
            and routes[r]["spectralPreserve20"]["native"] == 6
            and routes[r]["spectralPreserve20"]["spectral"] == 10
            and routes[r]["spectralPreserve20"]["restart"] == 4
            for r in ROUTES
        ),
        "sharedFirst10Exact": all(routes[r]["sharedFirst10Exact"] for r in ROUTES),
        "sharedStartExact": all(routes[r]["sharedStartExact"] for r in ROUTES),
        "baselineR10R12SpectralExact": all(routes[r]["baselineR10R12SpectralExact"] for r in ROUTES),
        "cellCountExact": len(cells) == 45,
        "smokeBaselineRuntimeReplayExact": (
            all(smoke_equivalence.get(r, False) for r in ROUTES) if smoke else True
        ),
        "smokeR10R12SpectralReplayExact": (
            all(smoke_r10_r12_exact.get(r, False) for r in ROUTES) if smoke else True
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
            "budgetPerArm": 20,
            "sharedPrefixAttempts": 10,
            "baselinePortfolio": {"native": 10, "spectral": 10, "restart": 0},
            "treatmentPortfolio": {"native": 6, "spectral": 10, "restart": 4},
            "replacedBaselineAttempts": ["R3", "R4", "R5", "R6"],
            "preservedSpectralAttemptCount": 10,
            "exactlyReplayedBaselineSpectralAttempts": ["R10", "R11", "R12"],
            "restartDefinition": "independent one-shot route-prior draw; invalid consumes budget; no retry; never parent",
            "meaningfulEffectMargin": MEANINGFUL_MARGIN,
            "deliveryRule": "target-blind three-item max-dispersion",
            "structuralMetric": "sparse-geometry-v1-exact-fast-grayscale",
        },
        "hardInvariants": hard,
        "smokeBaselineEquivalence": smoke_equivalence,
        "smokeR10R12SpectralReplayExact": smoke_r10_r12_exact,
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
