#!/usr/bin/env python3
"""Objective search-leverage benchmark using held-out rendered phenotype targets.

This experiment does not evaluate artistic quality. It compares search topologies
under equal candidate-evaluation budgets using matched-frame image distance.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
sys.path.insert(0, str(PROTO))

from orbit_representation import register_orbit
register_orbit()

from core import Candidate, ROUTES, TIMES, default_brief, evaluate_candidate, render_candidate_frame
from pairwise_selector import DimensionVote, PairwiseDecision, PairwiseSelector
from representation_capacity import _generate_route_archive
from rng_streams import representation_rng
from search_engine import run_search_from_starts

ROUTE_ORDER = ("recurrence", "orbit", "family", "sheet", "filament")
SEEDS = (101, 103, 107)
COMMON_STARTS = 3
LOCAL_TARGET_ACCEPTED_STEPS = 6
LOCAL_TARGET_SCALE = 0.65
EXPLORE_PER_BASIN = 4
ROUND_A_PER_SURVIVOR = 3
TOTAL_EXTRA_BUDGET = 8
EPSILON = 1e-12


def _brief(route: str) -> dict:
    brief = default_brief()
    brief.update(
        name=f"search-leverage-{route}",
        routes=[route],
        starts_per_route=COMMON_STARTS,
        explore_per_basin=EXPLORE_PER_BASIN,
        roundA_per_survivor=ROUND_A_PER_SURVIVOR,
        total_extra_budget=TOTAL_EXTRA_BUDGET,
    )
    return brief


def _frame_bytes(cand: Candidate) -> tuple[bytes, ...]:
    return tuple(render_candidate_frame(cand, t).convert("L").tobytes() for t in TIMES)


def _distance_from_bytes(candidate_frames: tuple[bytes, ...], target_frames: tuple[bytes, ...]) -> float:
    if len(candidate_frames) != len(target_frames):
        raise ValueError("candidate/target frame count mismatch")
    total = 0
    count = 0
    for a, b in zip(candidate_frames, target_frames):
        if len(a) != len(b):
            raise ValueError("candidate/target image size mismatch")
        total += sum(abs(x - y) for x, y in zip(a, b))
        count += len(a)
    return total / (255.0 * count) if count else float("inf")


def phenotype_distance(cand: Candidate, target_frames: tuple[bytes, ...]) -> float:
    if not cand.checks.get("valid", False):
        return float("inf")
    return _distance_from_bytes(_frame_bytes(cand), target_frames)


def phenotype_fingerprint(cand: Candidate) -> str:
    return hashlib.sha256(b"\0".join(_frame_bytes(cand))).hexdigest()


class TargetDistanceSelector(PairwiseSelector):
    """Strict non-artistic selector: lower matched-frame target distance wins."""

    name = "target-phenotype-distance-v1"

    def __init__(self, target: Candidate):
        if not target.checks.get("valid", False):
            raise ValueError("target must be valid")
        self.target_frames = _frame_bytes(target)
        self._cache: dict[str, float] = {}

    def distance(self, cand: Candidate) -> float:
        if cand.id not in self._cache:
            self._cache[cand.id] = phenotype_distance(cand, self.target_frames)
        return self._cache[cand.id]

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        av = bool(a.checks.get("valid", False))
        bv = bool(b.checks.get("valid", False))
        if av != bv:
            winner = "a" if av else "b"
            return PairwiseDecision(
                a.id,
                b.id,
                winner,
                "clear",
                (DimensionVote("route-validity", winner, "invalid candidates cannot win target recovery", av, bv),),
                self.name,
            )
        if not av and not bv:
            return PairwiseDecision(
                a.id,
                b.id,
                "tie",
                "defer",
                (DimensionVote("route-validity", "tie", "both candidates are invalid", av, bv),),
                self.name,
            )

        ad = self.distance(a)
        bd = self.distance(b)
        if abs(ad - bd) <= EPSILON:
            verdict = "tie"
            confidence = "defer"
        else:
            verdict = "a" if ad < bd else "b"
            confidence = "clear"
        return PairwiseDecision(
            a.id,
            b.id,
            verdict,
            confidence,
            (
                DimensionVote(
                    "matched-frame-target-distance",
                    verdict,
                    "lower normalized mean absolute pixel distance to the held-out target wins",
                    ad,
                    bd,
                ),
            ),
            self.name,
        )


def _generate_common_starts(brief: dict, seed: int, route: str) -> list[Candidate]:
    starts, _ = _generate_route_archive(brief, seed, route, COMMON_STARTS)
    if len(starts) != COMMON_STARTS or any(not c.checks.get("valid", False) for c in starts):
        raise AssertionError("common start archive must contain exactly three valid candidates")
    return starts


def _local_target(brief: dict, seed: int, route: str, ancestor: Candidate) -> Candidate:
    version = ROUTES[route].get("version", "1")
    rng = representation_rng(seed, route, version, "search-leverage-local-target-v1")
    current = copy.deepcopy(ancestor)
    for step in range(1, LOCAL_TARGET_ACCEPTED_STEPS + 1):
        accepted = None
        for attempt in range(1, 61):
            genome = ROUTES[route]["mutate"](current.genome, rng, LOCAL_TARGET_SCALE)
            trial = Candidate(
                f"TARGET-L{step}-A{attempt}",
                route,
                "TARGET-LOCAL",
                genome,
                current.id,
                "target-local",
            )
            evaluate_candidate(trial, brief)
            if trial.checks.get("valid", False):
                accepted = trial
                break
        if accepted is None:
            raise RuntimeError(f"could not produce accepted local target step {step} for {route}")
        current = accepted
    current.id = "TARGET-LOCAL"
    current.basin = "TARGET-LOCAL"
    return current


def _global_target(brief: dict, seed: int, route: str) -> Candidate:
    version = ROUTES[route].get("version", "1")
    rng = representation_rng(seed, route, version, "search-leverage-global-target-v1")
    for attempt in range(1, 101):
        trial = Candidate(
            f"TARGET-GLOBAL-A{attempt}",
            route,
            "TARGET-GLOBAL",
            ROUTES[route]["seed"](rng),
            None,
            "target-global",
        )
        evaluate_candidate(trial, brief)
        if trial.checks.get("valid", False):
            trial.id = "TARGET-GLOBAL"
            trial.basin = "TARGET-GLOBAL"
            return trial
    raise RuntimeError(f"could not generate independent valid target for {route}")


def _candidate_metrics(candidates: list[Candidate], target: Candidate, initial_ids: set[str]) -> dict:
    target_frames = _frame_bytes(target)
    valid = [c for c in candidates if c.checks.get("valid", False)]
    if not valid:
        raise AssertionError("policy produced no valid candidates")
    distances = [(phenotype_distance(c, target_frames), c) for c in valid]
    best_distance, best = min(distances, key=lambda item: (item[0], item[1].id))
    initial_distances = [d for d, c in distances if c.id in initial_ids]
    if len(initial_distances) != len(initial_ids):
        raise AssertionError("common initial candidates missing from policy pool")
    initial_best = min(initial_distances)
    improvement = (initial_best - best_distance) / max(initial_best, EPSILON)
    fingerprints = {phenotype_fingerprint(c) for c in valid}
    return {
        "bestCandidate": best.id,
        "bestDistance": best_distance,
        "initialBestDistance": initial_best,
        "normalizedImprovement": improvement,
        "validCandidates": len(valid),
        "totalCandidates": len(candidates),
        "validYield": len(valid) / len(candidates),
        "uniqueRenderedPhenotypes": len(fingerprints),
        "uniquePhenotypeRate": len(fingerprints) / len(valid),
    }


def _lineage_depth(candidate_id: str, candidates: dict[str, Candidate]) -> int:
    depth = 0
    seen = set()
    current = candidates.get(candidate_id)
    while current is not None and current.parent_id is not None and current.parent_id in candidates:
        if current.id in seen:
            raise AssertionError("candidate lineage cycle")
        seen.add(current.id)
        depth += 1
        current = candidates[current.parent_id]
    return depth


def _run_adaptive(brief: dict, seed: int, starts: list[Candidate], target: Candidate) -> tuple[dict, int]:
    selector = TargetDistanceSelector(target)
    with TemporaryDirectory() as td:
        state, report = run_search_from_starts(
            brief,
            seed,
            Path(td),
            copy.deepcopy(starts),
            selector,
        )
    candidates = list(state.candidates.values())
    initial_ids = {c.id for c in starts}
    metrics = _candidate_metrics(candidates, target, initial_ids)
    winner_id = report.get("provisionalChampion")
    if not winner_id:
        raise AssertionError("adaptive target search has no provisional champion")
    winner_distance = selector.distance(state.candidates[winner_id])
    if abs(winner_distance - metrics["bestDistance"]) > EPSILON:
        raise AssertionError(
            f"adaptive final champion is not the objective best: {winner_distance} != {metrics['bestDistance']}"
        )
    metrics.update(
        policy="adaptive",
        winner=winner_id,
        winnerDistance=winner_distance,
        lineageDepth=_lineage_depth(winner_id, state.candidates),
        selectionStatus=report.get("selectionStatus"),
    )
    additional_evaluations = len(candidates) - len(starts)
    if additional_evaluations < 1:
        raise AssertionError("adaptive run generated no incremental candidates")
    return metrics, additional_evaluations


def _run_independent_breadth(
    brief: dict,
    seed: int,
    route: str,
    starts: list[Candidate],
    target: Candidate,
    budget: int,
) -> dict:
    version = ROUTES[route].get("version", "1")
    rng = representation_rng(seed, route, version, "search-leverage-independent-breadth-v1")
    candidates = copy.deepcopy(starts)
    for index in range(1, budget + 1):
        cand = Candidate(
            f"B{index}",
            route,
            f"B{index}",
            ROUTES[route]["seed"](rng),
            None,
            "independent-breadth",
        )
        evaluate_candidate(cand, brief)
        candidates.append(cand)
    metrics = _candidate_metrics(candidates, target, {c.id for c in starts})
    metrics.update(policy="independent-breadth", lineageDepth=0)
    return metrics


def _run_fixed_parent(
    brief: dict,
    seed: int,
    route: str,
    target_kind: str,
    starts: list[Candidate],
    target: Candidate,
    budget: int,
) -> dict:
    target_frames = _frame_bytes(target)
    fixed_parent = min(
        starts,
        key=lambda c: (phenotype_distance(c, target_frames), c.id),
    )
    version = ROUTES[route].get("version", "1")
    rng = representation_rng(seed, route, version, f"search-leverage-fixed-parent-{target_kind}-v1")
    scales = (1.0, 0.7, 0.55, 1.2)
    candidates = copy.deepcopy(starts)
    for index in range(1, budget + 1):
        scale = scales[(index - 1) % len(scales)]
        cand = Candidate(
            f"F{index}",
            route,
            fixed_parent.id,
            ROUTES[route]["mutate"](fixed_parent.genome, rng, scale),
            fixed_parent.id,
            "fixed-parent-local",
        )
        evaluate_candidate(cand, brief)
        candidates.append(cand)
    metrics = _candidate_metrics(candidates, target, {c.id for c in starts})
    metrics.update(policy="fixed-parent-local", fixedParent=fixed_parent.id, lineageDepth=1)
    return metrics


def _winner_labels(policies: list[dict]) -> list[str]:
    best = min(p["bestDistance"] for p in policies)
    return [p["policy"] for p in policies if abs(p["bestDistance"] - best) <= EPSILON]


def _target_record(target: Candidate, starts: list[Candidate]) -> dict:
    frames = _frame_bytes(target)
    start_distances = {c.id: phenotype_distance(c, frames) for c in starts}
    return {
        "id": target.id,
        "phenotypeFingerprint": phenotype_fingerprint(target),
        "distanceFromEachStart": start_distances,
        "bestInitialDistance": min(start_distances.values()),
        "valid": bool(target.checks.get("valid", False)),
    }


def run_block(route: str, seed: int) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} is not predeclared")
    if seed not in SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    brief = _brief(route)
    starts = _generate_common_starts(brief, seed, route)
    targets = {
        "local": _local_target(brief, seed, route, starts[0]),
        "global": _global_target(brief, seed, route),
    }
    regimes = {}
    for kind, target in targets.items():
        adaptive, budget = _run_adaptive(brief, seed, starts, target)
        breadth = _run_independent_breadth(brief, seed, route, starts, target, budget)
        fixed = _run_fixed_parent(brief, seed, route, kind, starts, target, budget)
        policies = [adaptive, breadth, fixed]
        if any(p["totalCandidates"] != len(starts) + budget for p in policies):
            raise AssertionError("equal candidate-evaluation budget invariant failed")
        regimes[kind] = {
            "target": _target_record(target, starts),
            "incrementalEvaluationBudget": budget,
            "policies": policies,
            "winnerPolicies": _winner_labels(policies),
            "adaptiveBeatsFixedParent": adaptive["bestDistance"] + EPSILON < fixed["bestDistance"],
            "breadthBeatsAdaptive": breadth["bestDistance"] + EPSILON < adaptive["bestDistance"],
        }

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "times": list(TIMES),
        "commonStartFingerprints": {c.id: phenotype_fingerprint(c) for c in starts},
        "settings": {
            "commonStarts": COMMON_STARTS,
            "localTargetAcceptedSteps": LOCAL_TARGET_ACCEPTED_STEPS,
            "localTargetScale": LOCAL_TARGET_SCALE,
            "explorePerBasin": EXPLORE_PER_BASIN,
            "roundAPerSurvivor": ROUND_A_PER_SURVIVOR,
            "totalExtraBudget": TOTAL_EXTRA_BUDGET,
        },
        "regimes": regimes,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2))


if __name__ == "__main__":
    main()
