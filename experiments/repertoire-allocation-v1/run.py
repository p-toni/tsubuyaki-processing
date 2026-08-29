#!/usr/bin/env python3
"""Run one route×seed block of repertoire-allocation-v1."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1_PATH = ROOT / "experiments" / "search-leverage-v1" / "reproduce.py"
METRIC_PATH = ROOT / "experiments" / "search-history-geometry-replay-v1" / "metric.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v1 = _load("repertoire_allocation_search_leverage_v1", V1_PATH)
metric = _load("repertoire_allocation_sparse_geometry_v1", METRIC_PATH)
metric.install_sparse_geometry_metric(v1)

PROTO = ROOT / "prototypes" / "autonomous-discovery"
if str(PROTO) not in sys.path:
    sys.path.insert(0, str(PROTO))

from phenotype_descriptors import DESCRIPTOR_VERSION, describe_genome, niche_key
from rng_streams import derived_seed

ROUTE_ORDER = tuple(v1.ROUTE_ORDER)
PILOT_SEEDS = (
    1009, 1013, 1019, 1021,
    1031, 1033, 1039, 1049,
    1051, 1061, 1063, 1069,
    1087, 1091, 1093, 1097,
)
SMOKE_SEED = 9001
ALL_SEEDS = PILOT_SEEDS + (SMOKE_SEED,)
STARTS_PER_ROUTE = 6
EVENTS_PER_BASIN = 6
MUTATION_SCALES = (1.0, 0.7, 0.55, 1.2, 0.7, 1.0)
GENERATED_PER_ARM = STARTS_PER_ROUTE * EVENTS_PER_BASIN
LOCAL_TARGET_STEPS = 3
LOCAL_TARGET_SCALE = 0.8
GLOBAL_TARGETS = 2
TARGET_COUNT = STARTS_PER_ROUTE + GLOBAL_TARGETS
EPSILON = 1e-12


def _brief(route: str) -> dict:
    brief = v1._brief(route)
    brief.update(
        name=f"repertoire-allocation-v1-{route}",
        routes=[route],
        starts_per_route=STARTS_PER_ROUTE,
    )
    return brief


def _candidate(cid: str, route: str, basin: str, genome: dict, parent_id: str | None, stage: str, brief: dict):
    cand = v1.Candidate(cid, route, basin, genome, parent_id, stage)
    v1.evaluate_candidate(cand, brief)
    return cand


def _niche_tuple(candidate) -> tuple[int, int, int, str]:
    if not candidate.checks.get("valid", False):
        raise ValueError("cannot describe invalid candidate as a repertoire parent")
    descriptor = describe_genome(candidate.route, candidate.genome)
    key = niche_key(descriptor)
    return (
        int(key.anisotropy_bin),
        int(key.central_void_bin),
        int(key.motion_bin),
        str(key.version),
    )


def _niche_label(niche: tuple[int, int, int, str]) -> str:
    a, v, m, version = niche
    return f"{version}:a{a}-v{v}-m{m}"


def _generate_starts(brief: dict, seed: int, route: str):
    starts, attempts = v1._generate_route_archive(brief, seed, route, STARTS_PER_ROUTE)
    if len(starts) != STARTS_PER_ROUTE:
        raise AssertionError("shared start count drift")
    if any(not c.checks.get("valid", False) for c in starts):
        raise AssertionError("shared starts must all be hard-valid")
    if len({c.basin for c in starts}) != STARTS_PER_ROUTE:
        raise AssertionError("each independent start must define a distinct basin lineage")
    return starts, attempts


def _accepted_local_target_step(route: str, brief: dict, seed: int, start, current, step: int):
    event_seed = derived_seed(
        seed,
        "repertoire-allocation-v1",
        "target-local",
        route,
        start.basin,
        step,
    )
    rng = random.Random(event_seed)
    for attempt in range(1, 81):
        genome = v1.ROUTES[route]["mutate"](current.genome, rng, LOCAL_TARGET_SCALE)
        trial = _candidate(
            f"TARGET-{start.basin}-L{step}-A{attempt}",
            route,
            f"TARGET-{start.basin}",
            genome,
            current.id,
            "target-local",
            brief,
        )
        if trial.checks.get("valid", False):
            return trial
    raise RuntimeError(f"could not produce accepted local target step {step} for {route}/{start.basin}")


def _local_target(route: str, brief: dict, seed: int, start):
    current = copy.deepcopy(start)
    for step in range(1, LOCAL_TARGET_STEPS + 1):
        current = _accepted_local_target_step(route, brief, seed, start, current, step)
    current.id = f"TARGET-LOCAL-{start.basin}"
    current.basin = f"TARGET-LOCAL-{start.basin}"
    return current


def _global_target(route: str, brief: dict, seed: int, index: int):
    event_seed = derived_seed(seed, "repertoire-allocation-v1", "target-global", route, index)
    rng = random.Random(event_seed)
    for attempt in range(1, 121):
        trial = _candidate(
            f"TARGET-GLOBAL-{index}-A{attempt}",
            route,
            f"TARGET-GLOBAL-{index}",
            v1.ROUTES[route]["seed"](rng),
            None,
            "target-global",
            brief,
        )
        if trial.checks.get("valid", False):
            trial.id = f"TARGET-GLOBAL-{index}"
            return trial
    raise RuntimeError(f"could not generate independent valid global target {index} for {route}")


def _targets(route: str, brief: dict, seed: int, starts: list):
    local = [_local_target(route, brief, seed, start) for start in starts]
    global_targets = [_global_target(route, brief, seed, index) for index in range(1, GLOBAL_TARGETS + 1)]
    targets = local + global_targets
    if len(targets) != TARGET_COUNT or any(not t.checks.get("valid", False) for t in targets):
        raise AssertionError("target portfolio contract drift")
    return targets


def _latest(candidates: list):
    if not candidates:
        raise AssertionError("basin has no valid candidate")
    return candidates[-1]


def _select_parent(policy: str, basin: str, valid_by_basin: dict, niche_exposure: dict):
    candidates = valid_by_basin[basin]
    if policy == "lineage-depth":
        return _latest(candidates), None
    if policy != "repertoire-preserving":
        raise ValueError(policy)

    by_niche: dict[tuple, list] = defaultdict(list)
    for cand in candidates:
        by_niche[_niche_tuple(cand)].append(cand)
    exposure = niche_exposure[basin]
    chosen_niche = min(by_niche, key=lambda n: (int(exposure.get(n, 0)), n))
    parent = _latest(by_niche[chosen_niche])
    exposure[chosen_niche] += 1
    return parent, chosen_niche


def _run_policy(route: str, brief: dict, seed: int, starts: list, policy: str):
    copied_starts = copy.deepcopy(starts)
    start_by_basin = {c.basin: c for c in copied_starts}
    basin_order = tuple(sorted(start_by_basin))
    if len(basin_order) != STARTS_PER_ROUTE:
        raise AssertionError("basin order contract drift")

    valid_by_basin = {basin: [start_by_basin[basin]] for basin in basin_order}
    known_niches = {basin: {_niche_tuple(start_by_basin[basin])} for basin in basin_order}
    niche_exposure: dict[str, Counter] = {basin: Counter() for basin in basin_order}
    generated = []
    events = []
    new_niche_children = 0

    for cycle in range(1, EVENTS_PER_BASIN + 1):
        scale = MUTATION_SCALES[cycle - 1]
        for basin in basin_order:
            parent, selected_niche = _select_parent(policy, basin, valid_by_basin, niche_exposure)
            if parent.basin != basin:
                raise AssertionError("parent escaped scheduled basin")
            event_seed = derived_seed(
                seed,
                "repertoire-allocation-v1",
                "mutation",
                route,
                basin,
                cycle,
            )
            rng = random.Random(event_seed)
            genome = v1.ROUTES[route]["mutate"](parent.genome, rng, scale)
            tag = "D" if policy == "lineage-depth" else "Q"
            child = _candidate(
                f"{basin}-{tag}{cycle}",
                route,
                basin,
                genome,
                parent.id,
                policy,
                brief,
            )
            generated.append(child)

            child_niche = None
            discovered_new_niche = False
            if child.checks.get("valid", False):
                child_niche = _niche_tuple(child)
                discovered_new_niche = child_niche not in known_niches[basin]
                if discovered_new_niche:
                    new_niche_children += 1
                    known_niches[basin].add(child_niche)
                valid_by_basin[basin].append(child)

            parent_niche = _niche_tuple(parent)
            events.append(
                {
                    "cycle": cycle,
                    "basin": basin,
                    "eventSeed": event_seed,
                    "scale": scale,
                    "parent": parent.id,
                    "parentNiche": _niche_label(parent_niche),
                    "selectedLeastExposedNiche": _niche_label(selected_niche) if selected_niche else None,
                    "child": child.id,
                    "childValid": bool(child.checks.get("valid", False)),
                    "childNiche": _niche_label(child_niche) if child_niche else None,
                    "discoveredNewNicheInBasin": discovered_new_niche,
                }
            )

    if len(generated) != GENERATED_PER_ARM:
        raise AssertionError("generated candidate budget drift")
    event_counts = Counter(event["basin"] for event in events)
    if any(event_counts.get(basin, 0) != EVENTS_PER_BASIN for basin in basin_order):
        raise AssertionError("per-basin mutation budget drift")

    valid_generated = [c for c in generated if c.checks.get("valid", False)]
    valid_pool = copied_starts + valid_generated
    final_niches = {_niche_tuple(c) for c in valid_pool}
    basin_niche_slots = {(c.basin, _niche_tuple(c)) for c in valid_pool}
    fingerprints = {v1.phenotype_fingerprint(c) for c in valid_pool}
    total_parent_selections = len(events)
    basin_shares = {basin: event_counts[basin] / total_parent_selections for basin in basin_order}

    return {
        "policy": policy,
        "starts": copied_starts,
        "generated": generated,
        "validPool": valid_pool,
        "events": events,
        "diagnostics": {
            "generatedCandidates": len(generated),
            "validGeneratedCandidates": len(valid_generated),
            "validYield": len(valid_generated) / len(generated),
            "occupiedNiches": len(final_niches),
            "basinNicheSlots": len(basin_niche_slots),
            "newNicheChildren": new_niche_children,
            "uniqueRenderedPhenotypes": len(fingerprints),
            "uniquePhenotypeRate": len(fingerprints) / len(valid_pool),
            "eventsPerBasin": dict(sorted(event_counts.items())),
            "basinBudgetShare": dict(sorted(basin_shares.items())),
            "maxBasinBudgetShare": max(basin_shares.values()),
            "nicheParentSelectionsByBasin": {
                basin: {
                    _niche_label(niche): count
                    for niche, count in sorted(niche_exposure[basin].items())
                }
                for basin in basin_order
            },
        },
    }


def _target_gain(starts: list, pool: list, target) -> dict:
    frames = v1._frame_bytes(target)
    initial = min(v1.phenotype_distance(c, frames) for c in starts)
    final = min(v1.phenotype_distance(c, frames) for c in pool if c.checks.get("valid", False))
    gain = (initial - final) / max(initial, EPSILON)
    if gain < -1e-10:
        raise AssertionError(f"target gain became negative despite retaining starts: {gain}")
    return {
        "target": target.id,
        "fingerprint": v1.phenotype_fingerprint(target),
        "initialBestDistance": initial,
        "finalBestDistance": final,
        "normalizedGain": max(0.0, gain),
    }


def _portfolio(starts: list, policy_result: dict, targets: list) -> dict:
    target_results = [_target_gain(starts, policy_result["validPool"], target) for target in targets]
    gains = [item["normalizedGain"] for item in target_results]
    ordered = sorted(gains)
    return {
        "meanGain": statistics.fmean(gains),
        "lowerHalfMeanGain": statistics.fmean(ordered[: len(ordered) // 2]),
        "targetGains": target_results,
    }


def _event_signature(policy_result: dict):
    return [
        (event["cycle"], event["basin"], event["eventSeed"], event["scale"])
        for event in policy_result["events"]
    ]


def run_block(route: str, seed: int) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} not in {ROUTE_ORDER}")
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    if DESCRIPTOR_VERSION != "structural-v1":
        raise AssertionError(f"descriptor version drift: {DESCRIPTOR_VERSION}")

    brief = _brief(route)
    starts, start_attempts = _generate_starts(brief, seed, route)
    targets = _targets(route, brief, seed, starts)

    baseline = _run_policy(route, brief, seed, starts, "lineage-depth")
    repertoire = _run_policy(route, brief, seed, starts, "repertoire-preserving")

    start_fingerprints = {c.id: v1.phenotype_fingerprint(c) for c in starts}
    if {c.id: v1.phenotype_fingerprint(c) for c in baseline["starts"]} != start_fingerprints:
        raise AssertionError("baseline start phenotype drift")
    if {c.id: v1.phenotype_fingerprint(c) for c in repertoire["starts"]} != start_fingerprints:
        raise AssertionError("repertoire start phenotype drift")
    if _event_signature(baseline) != _event_signature(repertoire):
        raise AssertionError("matched mutation event stream drift")
    if baseline["diagnostics"]["generatedCandidates"] != GENERATED_PER_ARM:
        raise AssertionError("baseline budget mismatch")
    if repertoire["diagnostics"]["generatedCandidates"] != GENERATED_PER_ARM:
        raise AssertionError("repertoire budget mismatch")
    expected_share = 1.0 / STARTS_PER_ROUTE
    if abs(baseline["diagnostics"]["maxBasinBudgetShare"] - expected_share) > EPSILON:
        raise AssertionError("baseline basin budget concentration drift")
    if abs(repertoire["diagnostics"]["maxBasinBudgetShare"] - expected_share) > EPSILON:
        raise AssertionError("repertoire basin budget concentration drift")

    baseline_portfolio = _portfolio(starts, baseline, targets)
    repertoire_portfolio = _portfolio(starts, repertoire, targets)
    primary_delta = repertoire_portfolio["meanGain"] - baseline_portfolio["meanGain"]
    robustness_delta = repertoire_portfolio["lowerHalfMeanGain"] - baseline_portfolio["lowerHalfMeanGain"]

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "analysisSeed": seed in PILOT_SEEDS,
        "freshSearchEvidence": False,
        "metric": "sparse-geometry-v1",
        "descriptorVersion": DESCRIPTOR_VERSION,
        "settings": {
            "startsPerRoute": STARTS_PER_ROUTE,
            "eventsPerBasin": EVENTS_PER_BASIN,
            "generatedPerArm": GENERATED_PER_ARM,
            "mutationScales": list(MUTATION_SCALES),
            "localTargetSteps": LOCAL_TARGET_STEPS,
            "localTargetScale": LOCAL_TARGET_SCALE,
            "globalTargets": GLOBAL_TARGETS,
            "targetCount": TARGET_COUNT,
        },
        "startGenerationAttempts": start_attempts,
        "commonStartFingerprints": start_fingerprints,
        "targetFingerprints": {target.id: v1.phenotype_fingerprint(target) for target in targets},
        "rng": "event-keyed derived_seed(master_seed, labels); corresponding policy events share basin/cycle/event seed/scale",
        "intervention": "same route and basin budgets, generic mutator, scales, targets, and RNG events; parent selection is latest-valid lineage depth vs least-exposed structural-v1 niche within the same basin",
        "policies": {
            "lineage-depth": {
                "portfolio": baseline_portfolio,
                "diagnostics": baseline["diagnostics"],
            },
            "repertoire-preserving": {
                "portfolio": repertoire_portfolio,
                "diagnostics": repertoire["diagnostics"],
            },
        },
        "primaryDelta": primary_delta,
        "robustnessDelta": robustness_delta,
        "hardInvariants": {
            "identicalSharedStarts": True,
            "targetsGeneratedBeforePolicyFork": True,
            "equalThirtySixCandidateBudgets": True,
            "equalSixEventsPerStartingBasin": True,
            "matchedEventRngAndScales": True,
            "sameGenericMutator": True,
            "targetBlindParentSelection": True,
            "parentStaysInsideScheduledBasin": True,
            "structuralV1Unchanged": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
