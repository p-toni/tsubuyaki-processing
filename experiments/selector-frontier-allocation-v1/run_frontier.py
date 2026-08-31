#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
METRIC_DIR = ROOT / "experiments" / "spectral-material-control-v1"
RUNTIME_DIR = ROOT / "experiments" / "spectral-material-control-runtime-replay-v1"
for p in (PROTO, METRIC_DIR, RUNTIME_DIR):
    sys.path.insert(0, str(p))

from orbit_representation import register_orbit
register_orbit()

import core
import search_engine
import fast_grayscale_metric as metric
from pairwise_selector import DeterministicTemporalSelector, clear_loss_frontier
from rng_streams import derived_seed
from targets_runtime import build_targets_runtime

ROUTES = ("recurrence", "orbit", "filament")
CANONICAL_TIME = 90
FRONTIER_CAP = 4
SMOKE_SEED = 731999
MASTER_SEEDS = (
    731003, 731019, 731037, 731051,
    731069, 731087, 731101, 731123,
    731141, 731159, 731177, 731191,
    731207, 731219, 731233, 731251,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str) -> dict:
    return {
        "name": "selector-frontier-allocation-v1",
        "artistic_intent": "mechanical selector-policy experiment only; no artistic authority",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.MIXED_1D_V1,
    }


def _phenotype_hash(cand: core.Candidate) -> str:
    h = hashlib.sha256()
    for t in core.TIMES:
        h.update(core.render_candidate_frame(cand, t).tobytes())
        h.update(b"\0")
    return h.hexdigest()


def _clone_candidate(c: core.Candidate) -> core.Candidate:
    return core.Candidate(
        c.id,
        c.route,
        c.basin,
        copy.deepcopy(c.genome),
        c.parent_id,
        c.stage,
    )


def _make_start(master_seed: int, route: str) -> core.Candidate:
    rng = random.Random(derived_seed(master_seed, "selector-frontier-start-v1", route))
    prefix = core.ROUTES[route].get("prefix", route[:1].upper())
    cid = f"{prefix}S1"
    brief = _brief(route)
    for attempt in range(1, 41):
        c = core.Candidate(cid, route, cid, core.ROUTES[route]["seed"](rng), None, "start")
        core.evaluate_candidate(c, brief)
        if c.checks.get("valid", False):
            return c
    raise RuntimeError(f"could not generate hard-valid start for {route} seed {master_seed}")


def _record(state: core.SearchState, stage: str, decisions) -> None:
    for d in decisions:
        x = d.to_json()
        x["stage"] = stage
        state.stage_decisions.append(x)


def _bounded_frontier(selector, candidates, brief, state, stage):
    champion, survivors, decisions = clear_loss_frontier(selector, candidates, brief)
    _record(state, stage, decisions)
    survivors = [c for c in survivors if c.checks.get("valid", False)]
    if not survivors:
        raise AssertionError(f"{stage}: frontier lost every hard-valid candidate")
    return champion, survivors[:FRONTIER_CAP]


def _run_frontier(route: str, master_seed: int, start: core.Candidate):
    brief = _brief(route)
    search_seed = derived_seed(master_seed, "selector-frontier-search-v1", route)
    rng = random.Random(search_seed)
    selector = DeterministicTemporalSelector()
    state = core.SearchState(brief, search_seed)
    start = _clone_candidate(start)
    core.evaluate_candidate(start, brief)
    if not start.checks.get("valid", False):
        raise AssertionError("frontier arm start is not hard-valid")
    state.candidates[start.id] = start

    # Stage 1: identical generation to the incumbent-only baseline.
    explore = []
    n = 4
    for j in range(n):
        cid = f"{start.basin}-E{j+1}"
        c = search_engine._spawn(brief, search_seed, start, cid, "explore", j, n, rng, 1.0)
        state.candidates[cid] = c
        explore.append(c)
    _, frontier = _bounded_frontier(
        selector, [start] + explore, brief, state, "explore-frontier"
    )

    # Stage 2: fixed budget distributed round-robin across the bounded plural frontier.
    round_a = []
    parents = tuple(frontier)
    n = 4
    for j in range(n):
        parent = parents[j % len(parents)]
        cid = f"{start.basin}-A{j+1}"
        c = search_engine._spawn(brief, search_seed, parent, cid, "roundA", j, n, rng, 0.7)
        state.candidates[cid] = c
        round_a.append(c)
    _, frontier = _bounded_frontier(
        selector, list(frontier) + round_a, brief, state, "roundA-frontier"
    )

    # Stage 3: preserve the current runtime's 9 local / 3 wide attempt split,
    # but distribute those attempts over the frozen roundA frontier.
    refine = []
    parents = tuple(frontier)
    n = 12
    for j in range(n):
        parent = parents[j % len(parents)]
        scale = 0.55 if j < 9 else 1.2
        cid = f"{start.basin}-R{j+1}"
        c = search_engine._spawn(brief, search_seed, parent, cid, "refine", j, n, rng, scale)
        state.candidates[cid] = c
        refine.append(c)
    champion, frontier = _bounded_frontier(
        selector, list(frontier) + refine, brief, state, "final-frontier"
    )
    state.winner_id = champion.id if len(frontier) == 1 else None
    return state, champion, frontier


def _run_baseline(route: str, master_seed: int, start: core.Candidate, out: Path):
    search_seed = derived_seed(master_seed, "selector-frontier-search-v1", route)
    return search_engine.run_search_from_starts(
        _brief(route),
        search_seed,
        out,
        [_clone_candidate(start)],
        selector=DeterministicTemporalSelector(),
    )


def _generated(state: core.SearchState):
    return [
        c for c in state.candidates.values()
        if c.stage != "start" and c.checks.get("generationOperator") in {"native", "spectral"}
    ]


def _diag(state: core.SearchState) -> dict:
    generated = _generated(state)
    native = [c for c in generated if c.checks.get("generationOperator") == "native"]
    spectral = [c for c in generated if c.checks.get("generationOperator") == "spectral"]
    return {
        "generated": len(generated),
        "valid": sum(bool(c.checks.get("valid", False)) for c in generated),
        "native": len(native),
        "nativeValid": sum(bool(c.checks.get("valid", False)) for c in native),
        "spectral": len(spectral),
        "spectralValid": sum(bool(c.checks.get("valid", False)) for c in spectral),
    }


def _valid_images(state: core.SearchState):
    return [
        core.render_candidate_frame(c, CANONICAL_TIME)
        for c in state.candidates.values()
        if c.checks.get("valid", False)
    ]


def _recovery(image, target_image) -> float:
    return 1.0 - float(metric.sparse_geometry_distance((image,), (target_image,))["distance"])


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} is outside frozen experiment namespace")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    archives = {}
    routes = {}
    with tempfile.TemporaryDirectory(prefix=f"selector-frontier-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            start = _make_start(master_seed, route)
            baseline_state, baseline_report = _run_baseline(
                route, master_seed, start, root / f"{route}-baseline"
            )
            frontier_state, frontier_champion, frontier_final = _run_frontier(
                route, master_seed, start
            )

            baseline_start = next(
                c for c in baseline_state.candidates.values()
                if c.stage == "start" and c.checks.get("valid", False)
            )
            frontier_start = next(
                c for c in frontier_state.candidates.values()
                if c.stage == "start" and c.checks.get("valid", False)
            )
            same_start = (
                baseline_start.genome == frontier_start.genome
                and _phenotype_hash(baseline_start) == _phenotype_hash(frontier_start)
            )
            bd = _diag(baseline_state)
            fd = _diag(frontier_state)
            if bd["generated"] != 20 or bd["native"] != 10 or bd["spectral"] != 10:
                raise AssertionError(f"baseline budget drift {route}: {bd}")
            if fd["generated"] != 20 or fd["native"] != 10 or fd["spectral"] != 10:
                raise AssertionError(f"frontier budget drift {route}: {fd}")
            if not same_start:
                raise AssertionError(f"start mismatch for {route}")

            final_non_start = [c for c in frontier_final if c.stage != "start"]
            routes[route] = {
                "sharedStartExact": same_start,
                "baselineDiagnostics": bd,
                "frontierDiagnostics": fd,
                "baselineSelectionStatus": baseline_report["selectionStatus"],
                "baselineProvisionalChampion": baseline_report["provisionalChampion"],
                "baselineChampionIsSharedStart": baseline_report["provisionalChampion"] == baseline_start.id,
                "frontierChampion": frontier_champion.id,
                "frontierSize": len(frontier_final),
                "frontierNonStartCount": len(final_non_start),
                "frontierIds": [c.id for c in frontier_final],
            }
            archives[route] = {
                "baselineImages": _valid_images(baseline_state),
                "frontierImages": _valid_images(frontier_state),
            }

        # Outcome scoring occurs only after both treatment trajectories for every route exist.
        targets = build_targets_runtime()
        cells = []
        for route in ROUTES:
            for target in targets:
                baseline = max(_recovery(im, target.image) for im in archives[route]["baselineImages"])
                frontier = max(_recovery(im, target.image) for im in archives[route]["frontierImages"])
                cells.append({
                    "masterSeed": master_seed,
                    "route": route,
                    "targetId": target.id,
                    "targetFamily": target.family,
                    "baselineRecovery": baseline,
                    "frontierRecovery": frontier,
                    "delta": frontier - baseline,
                })

    hard = {
        "routeSetExact": tuple(routes) == ROUTES,
        "sharedStartsExact": all(routes[r]["sharedStartExact"] for r in ROUTES),
        "baselineBudgetExact": all(
            routes[r]["baselineDiagnostics"]["generated"] == 20
            and routes[r]["baselineDiagnostics"]["native"] == 10
            and routes[r]["baselineDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "frontierBudgetExact": all(
            routes[r]["frontierDiagnostics"]["generated"] == 20
            and routes[r]["frontierDiagnostics"]["native"] == 10
            and routes[r]["frontierDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "cellCountExact": len(cells) == 45,
        "frontierCapRespected": all(routes[r]["frontierSize"] <= FRONTIER_CAP for r in ROUTES),
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
            "challengersPerRouteArm": 20,
            "mixedNativePerRoute": 10,
            "mixedSpectralPerRoute": 10,
            "frontierCap": FRONTIER_CAP,
            "canonicalTime": CANONICAL_TIME,
            "metric": "sparse-geometry-v1-exact-fast-grayscale",
            "selector": "deterministic-temporal-proxy-v1",
        },
        "hardInvariants": hard,
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
