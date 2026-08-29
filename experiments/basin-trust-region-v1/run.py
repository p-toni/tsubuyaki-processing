#!/usr/bin/env python3
"""Run one route×seed block of the consumed-seed basin trust-region pilot."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1_PATH = ROOT / "experiments" / "search-leverage-v1" / "reproduce.py"
METRIC_PATH = ROOT / "experiments" / "search-history-geometry-replay-v1" / "metric.py"

from policy import (
    PARTITIONS,
    changed_frozen_keys,
    changed_identity_keys,
    frozen_signature,
    identity_mutate,
    partition_for,
    trust_region_mutate,
    validate_partition,
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v1 = _load("basin_trust_search_leverage_v1", V1_PATH)
metric = _load("basin_trust_geometry_metric", METRIC_PATH)
metric.install_sparse_geometry_metric(v1)

PROTO = ROOT / "prototypes" / "autonomous-discovery"
if str(PROTO) not in sys.path:
    sys.path.insert(0, str(PROTO))
from rng_streams import derived_seed, representation_rng

ROUTE_ORDER = tuple(v1.ROUTE_ORDER)
PILOT_SEEDS = (
    1009, 1013, 1019, 1021,
    1031, 1033, 1039, 1049,
    1051, 1061, 1063, 1069,
)
SMOKE_SEED = 9001
ALL_SEEDS = PILOT_SEEDS + (SMOKE_SEED,)
TARGET_REGIMES = ("same-basin", "identity-jump")
DISCOVERY_PER_BASIN = 4
EXPLOIT_BUDGET = 20
LOCAL_TARGET_SCALE = 0.65
SAME_BASIN_STEPS = 6
JUMP_LOCAL_STEPS = 5
IDENTITY_JUMP_SCALE = 1.2
EPSILON = v1.EPSILON


def _candidate(cid: str, route: str, basin: str, genome: dict, parent_id: str | None, stage: str, brief: dict):
    cand = v1.Candidate(cid, route, basin, genome, parent_id, stage)
    v1.evaluate_candidate(cand, brief)
    return cand


def _accepted_local_step(route: str, brief: dict, rng, current, step: int, prefix: str):
    for attempt in range(1, 61):
        genome = trust_region_mutate(route, current.genome, rng, LOCAL_TARGET_SCALE)
        trial = _candidate(
            f"{prefix}-L{step}-A{attempt}", route, "TARGET", genome, current.id, "target-local", brief
        )
        if trial.checks.get("valid", False):
            return trial
    raise RuntimeError(f"could not generate accepted local target step {step} for {route}")


def _target(route: str, brief: dict, seed: int, ancestor, regime: str):
    version = v1.ROUTES[route].get("version", "1")
    current = copy.deepcopy(ancestor)

    if regime == "identity-jump":
        rng = representation_rng(seed, route, version, "basin-trust-v1-target-identity-jump")
        accepted = None
        for attempt in range(1, 101):
            genome = identity_mutate(route, current.genome, rng, IDENTITY_JUMP_SCALE)
            if not changed_identity_keys(route, ancestor.genome, genome):
                continue
            trial = _candidate(
                f"TARGET-JUMP-I-A{attempt}", route, "TARGET", genome, current.id, "target-identity", brief
            )
            if trial.checks.get("valid", False):
                accepted = trial
                break
        if accepted is None:
            raise RuntimeError(f"could not generate accepted identity jump for {route}")
        current = accepted
        local_steps = JUMP_LOCAL_STEPS
        local_stream = "basin-trust-v1-target-jump-local"
        prefix = "TARGET-JUMP"
    elif regime == "same-basin":
        local_steps = SAME_BASIN_STEPS
        local_stream = "basin-trust-v1-target-same-local"
        prefix = "TARGET-SAME"
    else:
        raise ValueError(regime)

    rng = representation_rng(seed, route, version, local_stream)
    for step in range(1, local_steps + 1):
        current = _accepted_local_step(route, brief, rng, current, step, prefix)

    current.id = "TARGET-SAME" if regime == "same-basin" else "TARGET-JUMP"
    current.basin = "TARGET"
    frozen_delta = changed_frozen_keys(route, ancestor.genome, current.genome)
    identity_delta = changed_identity_keys(route, ancestor.genome, current.genome)
    if regime == "same-basin" and frozen_delta:
        raise AssertionError(f"same-basin target drifted frozen keys: {frozen_delta}")
    if regime == "identity-jump" and not identity_delta:
        raise AssertionError("identity-jump target did not cross an identity key")
    return current


def _discovery_pool(route: str, brief: dict, seed: int, starts: list):
    pools = {}
    all_candidates = []
    for start in starts:
        pool = [start]
        for j in range(1, DISCOVERY_PER_BASIN + 1):
            rng = random.Random(derived_seed(seed, "basin-trust-v1", "discovery", route, start.id, j))
            genome = v1.ROUTES[route]["mutate"](start.genome, rng, 1.0)
            cand = _candidate(
                f"{start.id}-D{j}", route, start.basin, genome, start.id, "basin-discovery", brief
            )
            pool.append(cand)
        pools[start.basin] = pool
        all_candidates.extend(pool)
    expected = len(starts) * (DISCOVERY_PER_BASIN + 1)
    if len(all_candidates) != expected:
        raise AssertionError("discovery candidate count drift")
    return pools


def _select_discovered(target, pools: dict):
    selector = v1.TargetDistanceSelector(target)
    representatives = []
    per_basin = {}
    for basin, pool in pools.items():
        valid = [cand for cand in pool if cand.checks.get("valid", False)]
        if not valid:
            raise AssertionError(f"discovery basin {basin} lost all valid candidates")
        ranked = sorted((selector.distance(cand), cand.id, cand) for cand in valid)
        distance, _, representative = ranked[0]
        representatives.append((distance, representative.id, representative))
        per_basin[basin] = {
            "representative": representative.id,
            "distance": distance,
            "validCandidates": len(valid),
            "totalCandidates": len(pool),
        }
    selected_distance, _, selected = sorted(representatives)[0]
    return selected, selected_distance, per_basin


def _exploit(route: str, brief: dict, seed: int, regime: str, target, selected, policy: str):
    selector = v1.TargetDistanceSelector(target)
    initial_distance = selector.distance(selected)
    champion = selected
    champion_distance = initial_distance
    generated = []
    base = selected

    for j in range(1, EXPLOIT_BUDGET + 1):
        use_champion = j <= 14
        parent = champion if use_champion else base
        scale = 0.55 if use_champion else 1.20
        # Same event label for both policies. The policy changes key eligibility,
        # not the future event stream.
        rng = random.Random(derived_seed(seed, "basin-trust-v1", "exploit", route, regime, j))
        if policy == "generic":
            genome = v1.ROUTES[route]["mutate"](parent.genome, rng, scale)
        elif policy == "trust-region":
            genome = trust_region_mutate(route, parent.genome, rng, scale)
        else:
            raise ValueError(policy)

        tag = "G" if policy == "generic" else "T"
        cand = _candidate(
            f"{base.basin}-{tag}-{regime}-{j}", route, base.basin, genome, parent.id, "basin-exploit", brief
        )
        generated.append(cand)
        if cand.checks.get("valid", False):
            distance = selector.distance(cand)
            if distance < champion_distance - EPSILON:
                champion = cand
                champion_distance = distance

    if len(generated) != EXPLOIT_BUDGET:
        raise AssertionError("exploitation candidate count drift")
    valid = [cand for cand in generated if cand.checks.get("valid", False)]
    frozen_drift_generated = sum(bool(changed_frozen_keys(route, base.genome, cand.genome)) for cand in generated)
    frozen_drift_champion = changed_frozen_keys(route, base.genome, champion.genome)
    identity_drift_champion = changed_identity_keys(route, base.genome, champion.genome)
    normalized = (initial_distance - champion_distance) / max(initial_distance, EPSILON)

    return {
        "policy": policy,
        "initialCandidate": base.id,
        "initialDistance": initial_distance,
        "finalCandidate": champion.id,
        "finalDistance": champion_distance,
        "normalizedImprovement": normalized,
        "candidateCount": len(generated),
        "validCandidates": len(valid),
        "validYield": len(valid) / len(generated),
        "generatedCandidatesWithFrozenDrift": frozen_drift_generated,
        "championFrozenDriftKeys": frozen_drift_champion,
        "championIdentityDriftKeys": identity_drift_champion,
    }


def run_block(route: str, seed: int) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} not in {ROUTE_ORDER}")
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")

    brief = v1._brief(route)
    starts = v1._generate_common_starts(brief, seed, route)
    for start in starts:
        validate_partition(route, start.genome)
    ancestor = starts[0]
    ancestor_frozen = frozen_signature(route, ancestor.genome)
    pools = _discovery_pool(route, brief, seed, starts)

    regimes = {}
    for regime in TARGET_REGIMES:
        target = _target(route, brief, seed, ancestor, regime)
        selected, selected_distance, per_basin = _select_discovered(target, pools)
        generic = _exploit(route, brief, seed, regime, target, selected, "generic")
        trust = _exploit(route, brief, seed, regime, target, selected, "trust-region")
        if generic["candidateCount"] != trust["candidateCount"]:
            raise AssertionError("policy budget mismatch")
        if generic["initialCandidate"] != trust["initialCandidate"]:
            raise AssertionError("policies did not fork from the same discovered representative")
        if trust["championFrozenDriftKeys"]:
            raise AssertionError(
                f"trust-region champion crossed frozen basin keys: {trust['championFrozenDriftKeys']}"
            )

        target_frozen_delta = changed_frozen_keys(route, ancestor.genome, target.genome)
        target_identity_delta = changed_identity_keys(route, ancestor.genome, target.genome)
        regimes[regime] = {
            "target": {
                "id": target.id,
                "ancestor": ancestor.id,
                "bestDiscoveryDistance": selected_distance,
                "frozenDeltaKeysFromAncestor": target_frozen_delta,
                "identityDeltaKeysFromAncestor": target_identity_delta,
            },
            "discovery": {
                "selectedBasin": selected.basin,
                "selectedRepresentative": selected.id,
                "selectedAncestorBasin": selected.basin == ancestor.basin,
                "perBasin": per_basin,
            },
            "policies": {
                "generic": generic,
                "trust-region": trust,
            },
            "deltaTrustMinusGeneric": trust["normalizedImprovement"] - generic["normalizedImprovement"],
        }

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "analysisSeed": seed in PILOT_SEEDS,
        "metric": "sparse-geometry-v1",
        "pilotSeeds": list(PILOT_SEEDS),
        "targetRegimes": list(TARGET_REGIMES),
        "discoveryPerBasin": DISCOVERY_PER_BASIN,
        "exploitBudget": EXPLOIT_BUDGET,
        "partition": {
            "sampling": list(partition_for(route).sampling),
            "identity": list(partition_for(route).identity),
            "local": list(partition_for(route).local),
        },
        "commonStartFingerprints": {cand.id: v1.phenotype_fingerprint(cand) for cand in starts},
        "ancestor": {
            "id": ancestor.id,
            "basin": ancestor.basin,
            "frozenSignature": list(ancestor_frozen),
        },
        "rng": "event-keyed derived_seed(master_seed, labels); shared event labels across exploitation policies",
        "intervention": "shared broad discovery; exploitation differs only in whole-genome vs route-local key eligibility",
        "regimes": regimes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2))


if __name__ == "__main__":
    main()
