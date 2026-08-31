#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
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
ARMS = ("baseline10x10", "adaptive12x8", "antiAdaptive8x12")
FULL_ATTEMPTS = 20
PREFIX_ATTEMPTS = 8
REFINE_ATTEMPTS = 12
MIN_VALID_GENERATED = 12
MEANINGFUL_MARGIN = 0.003255297955511336

SMOKE_SEED = 745999
MASTER_SEEDS = (
    745003, 745019, 745037, 745053, 745071,
    745089, 745107, 745127, 745149, 745167,
    745181, 745199, 745223, 745239, 745257,
    745277, 745293, 745311, 745331, 745349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str) -> dict:
    return {
        "name": "operator-novelty-allocation-v1",
        "artistic_intent": "target-blind operator-allocation experiment only; no artistic authority",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.MIXED_1D_V1,
    }


def _record(state: core.SearchState, stage: str, decisions) -> None:
    for d in decisions:
        x = d.to_json()
        x["stage"] = stage
        state.stage_decisions.append(x)


def _select_local(selector, incumbent, challengers, brief, state, stage):
    champion = incumbent
    for c in challengers:
        champion, d = search_engine.incumbent_challenge(selector, champion, c, brief)
        _record(state, stage, [d])
    return champion


def _spawn_explicit(
    brief: dict,
    seed: int,
    parent: core.Candidate,
    cid: str,
    stage: str,
    index: int,
    rng: random.Random,
    scale: float,
    operator: str,
) -> core.Candidate:
    if operator == "native":
        genome = search_engine.mutate_native(
            core.ROUTES[parent.route], parent.genome, rng, scale
        )
    elif operator == "spectral":
        field_seed = derived_seed(
            seed,
            "runtime-spectral-material-control-v1",
            parent.route,
            parent.basin,
            stage,
            index,
            parent.id,
        )
        genome = search_engine.with_spectral_control(parent.genome, field_seed)
    else:
        raise ValueError(f"unsupported operator {operator!r}")
    cand = core.Candidate(cid, parent.route, parent.basin, genome, parent.id, stage)
    core.evaluate_candidate(cand, brief)
    cand.checks["generationOperator"] = operator
    return cand


def _seed_start(route: str, brief: dict, rng: random.Random, state: core.SearchState):
    prefix = core.ROUTES[route].get("prefix", route[:1].upper())
    cid = f"{prefix}S1"
    for attempt in range(1, 21):
        trial = core.Candidate(
            cid,
            route,
            cid,
            core.ROUTES[route]["seed"](rng),
            None,
            "start",
        )
        core.evaluate_candidate(trial, brief)
        if trial.checks["valid"]:
            state.candidates[cid] = trial
            return trial
        trial.id = f"{cid}-invalid{attempt}"
        state.candidates[trial.id] = trial
    raise RuntimeError(f"could not seed valid {route}")


def _operator_attempts(state: core.SearchState) -> list[core.Candidate]:
    return [
        c
        for c in state.candidates.values()
        if c.stage != "start"
        and c.checks.get("generationOperator") in {"native", "spectral"}
    ]


def _generated_valid(state: core.SearchState) -> list[core.Candidate]:
    return [c for c in _operator_attempts(state) if bool(c.checks.get("valid", False))]


def _operator_diag(state: core.SearchState) -> dict:
    attempts = _operator_attempts(state)
    native = [c for c in attempts if c.checks.get("generationOperator") == "native"]
    spectral = [c for c in attempts if c.checks.get("generationOperator") == "spectral"]
    return {
        "total": len(attempts),
        "native": len(native),
        "spectral": len(spectral),
        "valid": sum(bool(c.checks.get("valid", False)) for c in attempts),
        "nativeValid": sum(bool(c.checks.get("valid", False)) for c in native),
        "spectralValid": sum(bool(c.checks.get("valid", False)) for c in spectral),
    }


def _prefix_novelty(start: core.Candidate, prefix_attempts: list[core.Candidate]) -> dict:
    if len(prefix_attempts) != PREFIX_ATTEMPTS:
        raise AssertionError(f"expected {PREFIX_ATTEMPTS} prefix attempts")
    op_counts = {
        op: sum(c.checks.get("generationOperator") == op for c in prefix_attempts)
        for op in ("native", "spectral")
    }
    if op_counts != {"native": 4, "spectral": 4}:
        raise AssertionError(f"prefix allocation drift: {op_counts}")

    valid = [c for c in prefix_attempts if bool(c.checks.get("valid", False))]
    pool = [start] + valid
    distances = base._distance_matrix(pool)
    novelty_by_id = {}
    for i, cand in enumerate(pool[1:], start=1):
        ds = [float(distances[i, j]) for j in range(len(pool)) if j != i]
        novelty_by_id[cand.id] = min(ds) if ds else 0.0

    contributions = {"native": [], "spectral": []}
    attempt_rows = []
    for cand in prefix_attempts:
        op = str(cand.checks["generationOperator"])
        value = novelty_by_id.get(cand.id, 0.0) if cand.checks.get("valid", False) else 0.0
        contributions[op].append(float(value))
        attempt_rows.append(
            {
                "candidateId": cand.id,
                "operator": op,
                "valid": bool(cand.checks.get("valid", False)),
                "leaveOneOutNearestNeighborDistance": float(value),
            }
        )

    means = {op: statistics.fmean(values) for op, values in contributions.items()}
    eps = 1e-15
    if means["native"] > means["spectral"] + eps:
        winner = "native"
        tie = False
    elif means["spectral"] > means["native"] + eps:
        winner = "spectral"
        tie = False
    else:
        winner = "native"
        tie = True

    return {
        "winner": winner,
        "exactTie": tie,
        "meanNovelty": means,
        "nativeMinusSpectral": means["native"] - means["spectral"],
        "attempts": attempt_rows,
    }


def _refine_schedule(arm: str, winner: str) -> list[str]:
    if arm == "baseline10x10":
        native_n = 6
    elif arm == "adaptive12x8":
        native_n = 8 if winner == "native" else 4
    elif arm == "antiAdaptive8x12":
        native_n = 4 if winner == "native" else 8
    else:
        raise ValueError(f"unsupported arm {arm!r}")
    return ["native"] * native_n + ["spectral"] * (REFINE_ATTEMPTS - native_n)


def _run_arm(route: str, search_seed: int, arm: str) -> dict:
    brief = _brief(route)
    rng = random.Random(search_seed)
    selector = search_engine.DeterministicTemporalSelector()
    state = core.SearchState(brief, search_seed)

    start = _seed_start(route, brief, rng, state)
    basin_id = start.id
    incumbent = start

    # Exact current explore prefix: N,N,S,S.
    explore = []
    for j, op in enumerate(("native", "native", "spectral", "spectral")):
        cid = f"{basin_id}-E{j+1}"
        cand = _spawn_explicit(
            brief, search_seed, incumbent, cid, "explore", j, rng, 1.0, op
        )
        state.candidates[cid] = cand
        explore.append(cand)
    incumbent = _select_local(selector, incumbent, explore, brief, state, "explore")

    _, survivors, ds = search_engine.route_aware_frontier(
        selector, [incumbent], brief
    )
    _record(state, "frontier", ds)
    if len(survivors) != 1:
        raise AssertionError("single-route/single-basin frontier drift after explore")
    incumbent = survivors[0]

    # Exact current roundA prefix: N,N,S,S.
    round_a = []
    for j, op in enumerate(("native", "native", "spectral", "spectral")):
        cid = f"{basin_id}-A{j+1}"
        cand = _spawn_explicit(
            brief, search_seed, incumbent, cid, "roundA", j, rng, 0.7, op
        )
        state.candidates[cid] = cand
        round_a.append(cand)
    incumbent = _select_local(selector, incumbent, round_a, brief, state, "roundA")

    _, survivors, ds = search_engine.route_aware_frontier(
        selector, [incumbent], brief
    )
    _record(state, "allocate-frontier", ds)
    if len(survivors) != 1:
        raise AssertionError("single-route/single-basin frontier drift after roundA")
    incumbent = survivors[0]

    prefix_attempts = explore + round_a
    novelty = _prefix_novelty(start, prefix_attempts)
    refine_schedule = _refine_schedule(arm, novelty["winner"])

    refine_incumbent = incumbent
    champion = refine_incumbent
    for j, op in enumerate(refine_schedule):
        parent = champion if j < REFINE_ATTEMPTS * 0.7 else refine_incumbent
        scale = 0.55 if j < REFINE_ATTEMPTS * 0.7 else 1.2
        cid = f"{basin_id}-R{j+1}"
        cand = _spawn_explicit(
            brief, search_seed, parent, cid, "refine", j, rng, scale, op
        )
        state.candidates[cid] = cand
        champion, d = search_engine.incumbent_challenge(
            selector, champion, cand, brief
        )
        _record(state, "refine", [d])

    winner, frontier, ds = search_engine.route_aware_frontier(
        selector, [champion], brief
    )
    _record(state, "final", ds)
    selection_status = "clear" if len(frontier) == 1 else "tie-defer"
    state.winner_id = winner.id if selection_status == "clear" else None

    attempts = _operator_attempts(state)
    if len(attempts) != FULL_ATTEMPTS:
        raise AssertionError(f"attempt count drift: {len(attempts)}")
    generated_valid = _generated_valid(state)
    if len(generated_valid) < MIN_VALID_GENERATED:
        raise AssertionError(
            f"need >={MIN_VALID_GENERATED} hard-valid generated challengers; "
            f"found {len(generated_valid)}"
        )
    shortlist = base._select_shortlists(generated_valid)

    prefix_fingerprint = [
        {
            "candidateId": c.id,
            "operator": c.checks.get("generationOperator"),
            "valid": bool(c.checks.get("valid", False)),
            "phenotypeHash": base._phenotype_hash(c),
        }
        for c in prefix_attempts
    ]

    return {
        "state": state,
        "start": start,
        "generatedValid": generated_valid,
        "deliveryCandidates": shortlist["dispersionCandidates"],
        "record": {
            "arm": arm,
            "operatorDiagnostics": _operator_diag(state),
            "validGeneratedCount": len(generated_valid),
            "selectionStatus": selection_status,
            "provisionalChampion": winner.id,
            "noveltyDecision": novelty,
            "refineSchedule": refine_schedule,
            "prefixFingerprint": prefix_fingerprint,
            "startPhenotypeHash": base._phenotype_hash(start),
            "delivery": shortlist["dispersion"],
        },
    }


def _reference_baseline(route: str, search_seed: int, out_dir: Path) -> dict:
    state, report = search_engine.run_search(
        _brief(route), search_seed, out_dir, selector=search_engine.DeterministicTemporalSelector()
    )
    attempts = _operator_attempts(state)
    return {
        "attempts": [
            {
                "candidateId": c.id,
                "operator": c.checks.get("generationOperator"),
                "valid": bool(c.checks.get("valid", False)),
                "phenotypeHash": base._phenotype_hash(c),
            }
            for c in attempts
        ],
        "provisionalChampion": report["provisionalChampion"],
        "operatorDiagnostics": _operator_diag(state),
    }


def _images(cands: list[core.Candidate]):
    return [core.render_candidate_frame(c, base.CANONICAL_TIME) for c in cands]


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    route_records = {}
    frozen_images = {}
    smoke_equivalence = {}

    with tempfile.TemporaryDirectory(prefix=f"operator-novelty-allocation-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            search_seed = derived_seed(master_seed, "operator-novelty-allocation-v1", route)
            arm_runs = {arm: _run_arm(route, search_seed, arm) for arm in ARMS}

            baseline = arm_runs["baseline10x10"]["record"]
            adaptive = arm_runs["adaptive12x8"]["record"]
            anti = arm_runs["antiAdaptive8x12"]["record"]

            if not (
                baseline["prefixFingerprint"]
                == adaptive["prefixFingerprint"]
                == anti["prefixFingerprint"]
            ):
                raise AssertionError(f"shared prefix drift for {route}")
            if not (
                baseline["startPhenotypeHash"]
                == adaptive["startPhenotypeHash"]
                == anti["startPhenotypeHash"]
            ):
                raise AssertionError(f"shared start drift for {route}")
            if not (
                baseline["noveltyDecision"]["winner"]
                == adaptive["noveltyDecision"]["winner"]
                == anti["noveltyDecision"]["winner"]
            ):
                raise AssertionError(f"novelty decision drift across arms for {route}")

            bdiag = baseline["operatorDiagnostics"]
            adiag = adaptive["operatorDiagnostics"]
            xdiag = anti["operatorDiagnostics"]
            if (bdiag["native"], bdiag["spectral"]) != (10, 10):
                raise AssertionError(f"baseline budget drift for {route}: {bdiag}")
            if sorted((adiag["native"], adiag["spectral"])) != [8, 12]:
                raise AssertionError(f"adaptive budget drift for {route}: {adiag}")
            if sorted((xdiag["native"], xdiag["spectral"])) != [8, 12]:
                raise AssertionError(f"anti-adaptive budget drift for {route}: {xdiag}")
            if (
                adiag["native"] + xdiag["native"] != 20
                or adiag["spectral"] + xdiag["spectral"] != 20
            ):
                raise AssertionError(f"adaptive/complement budget mismatch for {route}")

            if smoke:
                reference = _reference_baseline(route, search_seed, root / f"{route}-reference")
                custom_attempts = [
                    {
                        "candidateId": c.id,
                        "operator": c.checks.get("generationOperator"),
                        "valid": bool(c.checks.get("valid", False)),
                        "phenotypeHash": base._phenotype_hash(c),
                    }
                    for c in _operator_attempts(arm_runs["baseline10x10"]["state"])
                ]
                exact = (
                    custom_attempts == reference["attempts"]
                    and baseline["provisionalChampion"] == reference["provisionalChampion"]
                    and baseline["operatorDiagnostics"] == reference["operatorDiagnostics"]
                )
                smoke_equivalence[route] = exact
                if not exact:
                    raise AssertionError(f"custom baseline differs from current runtime for {route}")

            route_records[route] = {
                "searchSeed": search_seed,
                "noveltyDecision": adaptive["noveltyDecision"],
                "sharedPrefixFingerprint": adaptive["prefixFingerprint"],
                "sharedStartPhenotypeHash": adaptive["startPhenotypeHash"],
                "arms": {arm: arm_runs[arm]["record"] for arm in ARMS},
            }
            frozen_images[route] = {
                arm: {
                    "archive": _images(arm_runs[arm]["generatedValid"]),
                    "delivery": _images(arm_runs[arm]["deliveryCandidates"]),
                }
                for arm in ARMS
            }

        # Targets are deliberately constructed only after every route's three
        # target-blind search archives and delivery trios have been frozen.
        targets = base.build_targets_runtime()
        cells = []
        for route in ROUTES:
            for target in targets:
                values = {}
                for arm in ARMS:
                    archive_recovery = max(
                        base._recovery(im, target.image)
                        for im in frozen_images[route][arm]["archive"]
                    )
                    delivery_recovery = max(
                        base._recovery(im, target.image)
                        for im in frozen_images[route][arm]["delivery"]
                    )
                    values[arm] = {
                        "archiveRecovery": archive_recovery,
                        "deliveryRecovery": delivery_recovery,
                    }
                cells.append(
                    {
                        "masterSeed": master_seed,
                        "route": route,
                        "targetId": target.id,
                        "targetFamily": target.family,
                        "baselineArchiveRecovery": values["baseline10x10"]["archiveRecovery"],
                        "adaptiveArchiveRecovery": values["adaptive12x8"]["archiveRecovery"],
                        "antiAdaptiveArchiveRecovery": values["antiAdaptive8x12"]["archiveRecovery"],
                        "adaptiveMinusBaselineArchive": (
                            values["adaptive12x8"]["archiveRecovery"]
                            - values["baseline10x10"]["archiveRecovery"]
                        ),
                        "adaptiveMinusAntiArchive": (
                            values["adaptive12x8"]["archiveRecovery"]
                            - values["antiAdaptive8x12"]["archiveRecovery"]
                        ),
                        "baselineDeliveryRecovery": values["baseline10x10"]["deliveryRecovery"],
                        "adaptiveDeliveryRecovery": values["adaptive12x8"]["deliveryRecovery"],
                        "antiAdaptiveDeliveryRecovery": values["antiAdaptive8x12"]["deliveryRecovery"],
                        "adaptiveMinusBaselineDelivery": (
                            values["adaptive12x8"]["deliveryRecovery"]
                            - values["baseline10x10"]["deliveryRecovery"]
                        ),
                        "adaptiveMinusAntiDelivery": (
                            values["adaptive12x8"]["deliveryRecovery"]
                            - values["antiAdaptive8x12"]["deliveryRecovery"]
                        ),
                    }
                )

    hard = {
        "routeSetExact": tuple(route_records) == ROUTES,
        "cellCountExact": len(cells) == 45,
        "sharedPrefixExact": all(
            route_records[r]["arms"]["baseline10x10"]["prefixFingerprint"]
            == route_records[r]["arms"]["adaptive12x8"]["prefixFingerprint"]
            == route_records[r]["arms"]["antiAdaptive8x12"]["prefixFingerprint"]
            for r in ROUTES
        ),
        "sharedStartExact": all(
            route_records[r]["arms"]["baseline10x10"]["startPhenotypeHash"]
            == route_records[r]["arms"]["adaptive12x8"]["startPhenotypeHash"]
            == route_records[r]["arms"]["antiAdaptive8x12"]["startPhenotypeHash"]
            for r in ROUTES
        ),
        "baselineBudgetExact": all(
            route_records[r]["arms"]["baseline10x10"]["operatorDiagnostics"]["total"] == 20
            and route_records[r]["arms"]["baseline10x10"]["operatorDiagnostics"]["native"] == 10
            and route_records[r]["arms"]["baseline10x10"]["operatorDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "adaptiveBudgetExact": all(
            route_records[r]["arms"]["adaptive12x8"]["operatorDiagnostics"]["total"] == 20
            and sorted(
                (
                    route_records[r]["arms"]["adaptive12x8"]["operatorDiagnostics"]["native"],
                    route_records[r]["arms"]["adaptive12x8"]["operatorDiagnostics"]["spectral"],
                )
            )
            == [8, 12]
            for r in ROUTES
        ),
        "antiAdaptiveBudgetExact": all(
            route_records[r]["arms"]["antiAdaptive8x12"]["operatorDiagnostics"]["total"] == 20
            and sorted(
                (
                    route_records[r]["arms"]["antiAdaptive8x12"]["operatorDiagnostics"]["native"],
                    route_records[r]["arms"]["antiAdaptive8x12"]["operatorDiagnostics"]["spectral"],
                )
            )
            == [8, 12]
            for r in ROUTES
        ),
        "minimumValidGeneratedMet": all(
            route_records[r]["arms"][arm]["validGeneratedCount"] >= MIN_VALID_GENERATED
            for r in ROUTES
            for arm in ARMS
        ),
        "threeDistinctDeliveryPhenotypes": all(
            len(set(route_records[r]["arms"][arm]["delivery"]["phenotypeHashes"])) == 3
            for r in ROUTES
            for arm in ARMS
        ),
        "smokeBaselineRuntimeReplayExact": (
            all(smoke_equivalence.values()) if smoke else True
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
            "arms": list(ARMS),
            "fullAttemptsPerRouteArm": FULL_ATTEMPTS,
            "sharedPrefixAttempts": PREFIX_ATTEMPTS,
            "sharedPrefixNative": 4,
            "sharedPrefixSpectral": 4,
            "refineAttempts": REFINE_ATTEMPTS,
            "baselineFinalSplit": "10 native / 10 spectral",
            "adaptiveFinalSplit": "12/8 in favor of prefix novelty winner",
            "antiAdaptiveFinalSplit": "8/12 against prefix novelty winner",
            "novelty": "mean leave-one-out nearest-neighbor raw multi-time phenotype distance per exact four operator prefix attempts; invalid contribution zero",
            "noveltyFrames": list(base.TIMES),
            "noveltyResize": base.DISTANCE_SIZE,
            "tieRule": "exact floating-point tie -> native",
            "meaningfulEffectMargin": MEANINGFUL_MARGIN,
            "canonicalStructuralTime": base.CANONICAL_TIME,
            "structuralMetric": "sparse-geometry-v1-exact-fast-grayscale",
            "deliveryPolicy": "exact #106 max-dispersion three-item shortlist",
        },
        "hardInvariants": hard,
        "smokeBaselineEquivalence": smoke_equivalence,
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
