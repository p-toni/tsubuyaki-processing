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
SPR_DIR = ROOT / "experiments" / "independent-starts-spectral-preserve-v1"
sys.path.insert(0, str(SPR_DIR))

import run_spectral_preserve as spr

op = spr.op
base = spr.base
core = spr.core
search_engine = spr.search_engine
derived_seed = spr.derived_seed

ROUTES = ("recurrence", "orbit", "filament")
MEANINGFUL_MARGIN = 0.003255297955511336
SMOKE_SEED = 753999
MASTER_SEEDS = (
    753003, 753019, 753037, 753053, 753071,
    753089, 753107, 753127, 753149, 753167,
    753181, 753199, 753223, 753239, 753257,
    753277, 753293, 753311, 753331, 753349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _fingerprint(cands: list[core.Candidate]) -> list[dict]:
    return spr._fingerprint(cands)


def _spawn_cultivation_child(
    route: str,
    search_seed: int,
    parent: core.Candidate,
    index: int,
) -> core.Candidate:
    rng = random.Random(
        derived_seed(search_seed, "restart-cultivation-v1", "cultivation-child", index)
    )
    prefix = core.ROUTES[route].get("prefix", route[:1].upper())
    cid = f"{prefix}CUL{index + 1}"
    cand = op._spawn_explicit(
        op._brief(route),
        search_seed,
        parent,
        cid,
        "cultivate",
        index,
        rng,
        0.55,
        "native",
    )
    cand.checks["cultivationChild"] = True
    cand.checks["cultivationParentRestartId"] = parent.id
    cand.checks["restartCultivationArm"] = "cultivated20"
    return cand


def _run_cultivated(route: str, search_seed: int) -> dict:
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
    cultivation_children = []
    for i in range(2):
        restart = spr._spawn_restart(route, search_seed, i)
        state.candidates[restart.id] = restart
        restarts.append(restart)

        child = _spawn_cultivation_child(route, search_seed, restart, i)
        state.candidates[child.id] = child
        cultivation_children.append(child)

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
        and (
            c.checks.get("generationOperator") in {"native", "spectral", "restart"}
            or c.checks.get("cultivationChild") is True
        )
    ]
    valid_generated = [c for c in generated if bool(c.checks.get("valid", False))]
    if len(generated) != 20:
        raise AssertionError(f"cultivated total budget drift: {len(generated)}")
    if len(valid_generated) < base.MIN_VALID_GENERATED:
        raise AssertionError("cultivated valid archive below delivery minimum")

    shortlist = base._select_shortlists(valid_generated)
    native_count = sum(c.checks.get("generationOperator") == "native" for c in generated)
    spectral_count = sum(c.checks.get("generationOperator") == "spectral" for c in generated)
    restart_count = sum(c.checks.get("generationOperator") == "restart" for c in generated)
    cultivation_count = sum(c.checks.get("cultivationChild") is True for c in generated)

    return {
        "state": state,
        "start": start,
        "sharedAttempts": shared_attempts,
        "restarts": restarts,
        "cultivationChildren": cultivation_children,
        "spectralTail": spectral_tail,
        "generatedValid": valid_generated,
        "deliveryCandidates": shortlist["dispersionCandidates"],
        "record": {
            "totalGenerated": len(generated),
            "native": native_count,
            "spectral": spectral_count,
            "restart": restart_count,
            "cultivationChildren": cultivation_count,
            "validGenerated": len(valid_generated),
            "validRestarts": sum(bool(c.checks.get("valid", False)) for c in restarts),
            "validCultivationChildren": sum(
                bool(c.checks.get("valid", False)) for c in cultivation_children
            ),
            "sharedPrefixFingerprint": _fingerprint(shared_attempts),
            "restartFingerprint": _fingerprint(restarts),
            "cultivationChildFingerprint": _fingerprint(cultivation_children),
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

    with tempfile.TemporaryDirectory(prefix=f"restart-cultivation-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            search_seed = derived_seed(master_seed, "restart-cultivation-v1", route)
            baseline = op._run_arm(route, search_seed, "baseline10x10")
            one_shot = spr._run_spectral_preserve(route, search_seed)
            cultivated = _run_cultivated(route, search_seed)

            baseline_attempts = op._operator_attempts(baseline["state"])
            if len(baseline_attempts) != 20:
                raise AssertionError("baseline total attempt drift")

            shared_start_exact = (
                baseline["record"]["startPhenotypeHash"]
                == one_shot["record"]["startPhenotypeHash"]
                == cultivated["record"]["startPhenotypeHash"]
            )
            shared_first10_exact = (
                _fingerprint(baseline_attempts[:10])
                == one_shot["record"]["sharedPrefixFingerprint"]
                == cultivated["record"]["sharedPrefixFingerprint"]
            )
            shared_first_two_restarts_exact = (
                _fingerprint(one_shot["restarts"][:2])
                == cultivated["record"]["restartFingerprint"]
            )
            shared_spectral_tail_exact = (
                _fingerprint(one_shot["spectralTail"])
                == cultivated["record"]["spectralTailFingerprint"]
            )
            if not all((
                shared_start_exact,
                shared_first10_exact,
                shared_first_two_restarts_exact,
                shared_spectral_tail_exact,
            )):
                raise AssertionError(f"cross-arm causal isolation drift for {route}")

            bdiag = baseline["record"]["operatorDiagnostics"]
            odiag = one_shot["record"]
            cdiag = cultivated["record"]
            if not (
                bdiag["total"] == 20 and bdiag["native"] == 10 and bdiag["spectral"] == 10
            ):
                raise AssertionError(f"baseline budget drift: {bdiag}")
            if not (
                odiag["totalGenerated"] == 20
                and odiag["native"] == 6
                and odiag["spectral"] == 10
                and odiag["restart"] == 4
            ):
                raise AssertionError(f"one-shot budget drift: {odiag}")
            if not (
                cdiag["totalGenerated"] == 20
                and cdiag["native"] == 8
                and cdiag["spectral"] == 10
                and cdiag["restart"] == 2
                and cdiag["cultivationChildren"] == 2
            ):
                raise AssertionError(f"cultivated budget drift: {cdiag}")

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

            routes[route] = {
                "searchSeed": search_seed,
                "baseline20": {
                    "operatorDiagnostics": bdiag,
                    "validGeneratedCount": len(baseline["generatedValid"]),
                },
                "oneShot20": odiag,
                "cultivated20": cdiag,
                "sharedStartExact": shared_start_exact,
                "sharedFirst10Exact": shared_first10_exact,
                "sharedFirstTwoRestartsExact": shared_first_two_restarts_exact,
                "sharedSpectralTailExact": shared_spectral_tail_exact,
                "smokeBaselineRuntimeReplayExact": reference_exact,
            }
            frozen[route] = {
                "baselineArchive": _images(baseline["generatedValid"]),
                "oneShotArchive": _images(one_shot["generatedValid"]),
                "cultivatedArchive": _images(cultivated["generatedValid"]),
                "baselineDelivery": _images(baseline["deliveryCandidates"]),
                "oneShotDelivery": _images(one_shot["deliveryCandidates"]),
                "cultivatedDelivery": _images(cultivated["deliveryCandidates"]),
            }

        targets = base.build_targets_runtime()
        cells = []
        for route in ROUTES:
            ims = frozen[route]
            for target in targets:
                ba = _recovery(ims["baselineArchive"], target.image)
                oa = _recovery(ims["oneShotArchive"], target.image)
                ca = _recovery(ims["cultivatedArchive"], target.image)
                bd = _recovery(ims["baselineDelivery"], target.image)
                od = _recovery(ims["oneShotDelivery"], target.image)
                cd = _recovery(ims["cultivatedDelivery"], target.image)
                cells.append({
                    "masterSeed": master_seed,
                    "route": route,
                    "targetId": target.id,
                    "targetFamily": target.family,
                    "baselineArchiveRecovery": ba,
                    "oneShotArchiveRecovery": oa,
                    "cultivatedArchiveRecovery": ca,
                    "oneShotVsBaselineArchiveDelta": oa - ba,
                    "cultivatedVsBaselineArchiveDelta": ca - ba,
                    "cultivatedVsOneShotArchiveDelta": ca - oa,
                    "baselineDeliveryRecovery": bd,
                    "oneShotDeliveryRecovery": od,
                    "cultivatedDeliveryRecovery": cd,
                    "oneShotVsBaselineDeliveryDelta": od - bd,
                    "cultivatedVsBaselineDeliveryDelta": cd - bd,
                    "cultivatedVsOneShotDeliveryDelta": cd - od,
                })

    hard = {
        "routeSetExact": tuple(routes) == ROUTES,
        "baselineBudgetExact": all(
            routes[r]["baseline20"]["operatorDiagnostics"]["total"] == 20
            and routes[r]["baseline20"]["operatorDiagnostics"]["native"] == 10
            and routes[r]["baseline20"]["operatorDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "oneShotBudgetExact": all(
            routes[r]["oneShot20"]["totalGenerated"] == 20
            and routes[r]["oneShot20"]["native"] == 6
            and routes[r]["oneShot20"]["spectral"] == 10
            and routes[r]["oneShot20"]["restart"] == 4
            for r in ROUTES
        ),
        "cultivatedBudgetExact": all(
            routes[r]["cultivated20"]["totalGenerated"] == 20
            and routes[r]["cultivated20"]["native"] == 8
            and routes[r]["cultivated20"]["spectral"] == 10
            and routes[r]["cultivated20"]["restart"] == 2
            and routes[r]["cultivated20"]["cultivationChildren"] == 2
            for r in ROUTES
        ),
        "sharedStartExact": all(routes[r]["sharedStartExact"] for r in ROUTES),
        "sharedFirst10Exact": all(routes[r]["sharedFirst10Exact"] for r in ROUTES),
        "sharedFirstTwoRestartsExact": all(
            routes[r]["sharedFirstTwoRestartsExact"] for r in ROUTES
        ),
        "sharedSpectralTailExact": all(
            routes[r]["sharedSpectralTailExact"] for r in ROUTES
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
            "budgetPerArm": 20,
            "sharedPrefixAttempts": 10,
            "baselinePortfolio": {"native": 10, "spectral": 10, "restart": 0},
            "oneShotPortfolio": {"native": 6, "spectral": 10, "restart": 4},
            "cultivatedPortfolio": {
                "native": 8,
                "spectral": 10,
                "restart": 2,
                "cultivationChildren": 2,
            },
            "cultivationDefinition": (
                "two shared independent route-prior starts; one isolated native "
                "scale-0.55 child per restart; no retries; parent and child both archived"
            ),
            "meaningfulEffectMargin": MEANINGFUL_MARGIN,
            "deliveryRule": "target-blind three-item max-dispersion",
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
