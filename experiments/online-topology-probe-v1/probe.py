#!/usr/bin/env python3
"""Objective online topology probe simulator for calibration and holdout."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1_PATH = ROOT / "experiments" / "search-leverage-v1" / "reproduce.py"

spec = importlib.util.spec_from_file_location("search_leverage_v1", V1_PATH)
v1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(v1)

ROUTE_ORDER = tuple(v1.ROUTE_ORDER)
CALIBRATION_SEEDS = (101, 103, 107, 109, 113, 127)
HOLDOUT_SEEDS = (131, 137, 139)
ALL_SEEDS = CALIBRATION_SEEDS + HOLDOUT_SEEDS
PILOT_SIZES = (1, 2, 3, 4)
REGIMES = ("local", "global")
EPSILON = v1.EPSILON


def _arm_sequences(
    brief: dict,
    seed: int,
    route: str,
    target_kind: str,
    starts: list,
    target,
    budget: int,
) -> tuple[list, list, str]:
    version = v1.ROUTES[route].get("version", "1")

    breadth_rng = v1.representation_rng(
        seed, route, version, "search-leverage-independent-breadth-v1"
    )
    breadth = []
    for index in range(1, budget + 1):
        cand = v1.Candidate(
            f"B{index}",
            route,
            f"B{index}",
            v1.ROUTES[route]["seed"](breadth_rng),
            None,
            "independent-breadth",
        )
        v1.evaluate_candidate(cand, brief)
        breadth.append(cand)

    target_frames = v1._frame_bytes(target)
    fixed_parent = min(
        starts,
        key=lambda c: (v1.phenotype_distance(c, target_frames), c.id),
    )
    fixed_rng = v1.representation_rng(
        seed, route, version, f"search-leverage-fixed-parent-{target_kind}-v1"
    )
    scales = (1.0, 0.7, 0.55, 1.2)
    fixed = []
    for index in range(1, budget + 1):
        scale = scales[(index - 1) % len(scales)]
        cand = v1.Candidate(
            f"F{index}",
            route,
            fixed_parent.id,
            v1.ROUTES[route]["mutate"](fixed_parent.genome, fixed_rng, scale),
            fixed_parent.id,
            "fixed-parent-local",
        )
        v1.evaluate_candidate(cand, brief)
        fixed.append(cand)

    return breadth, fixed, fixed_parent.id


def _metrics(starts: list, additions: list, target, policy: str, **extra) -> dict:
    candidates = copy.deepcopy(starts) + additions
    metrics = v1._candidate_metrics(candidates, target, {c.id for c in starts})
    metrics.update(policy=policy, **extra)
    return metrics


def _probe_metrics(
    starts: list,
    target,
    breadth: list,
    fixed: list,
    budget: int,
    pilot_size: int,
) -> dict:
    if pilot_size < 1 or 2 * pilot_size > budget:
        raise ValueError(f"invalid pilot size {pilot_size} for budget {budget}")

    breadth_pilot = _metrics(
        starts,
        breadth[:pilot_size],
        target,
        "pilot-breadth",
    )
    fixed_pilot = _metrics(
        starts,
        fixed[:pilot_size],
        target,
        "pilot-fixed",
    )

    if breadth_pilot["bestDistance"] + EPSILON < fixed_pilot["bestDistance"]:
        chosen = "independent-breadth"
    else:
        chosen = "fixed-parent-local"

    continuation = budget - 2 * pilot_size
    if chosen == "independent-breadth":
        additions = breadth[: pilot_size + continuation] + fixed[:pilot_size]
    else:
        additions = breadth[:pilot_size] + fixed[: pilot_size + continuation]

    metrics = _metrics(
        starts,
        additions,
        target,
        f"probe-commit-p{pilot_size}",
        pilotSize=pilot_size,
        chosenArm=chosen,
        pilotBreadthBestDistance=breadth_pilot["bestDistance"],
        pilotFixedBestDistance=fixed_pilot["bestDistance"],
        continuationEvaluations=continuation,
        tieDefaultsTo="fixed-parent-local",
    )
    if metrics["totalCandidates"] != len(starts) + budget:
        raise AssertionError("probe policy violated total candidate-evaluation budget")
    return metrics


def _combined(regimes: dict, key: str) -> float:
    return statistics.fmean(float(regimes[kind][key]) for kind in REGIMES)


def run_block(route: str, seed: int, pilot_sizes: tuple[int, ...]) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} is not predeclared")
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    if not pilot_sizes or any(p not in PILOT_SIZES for p in pilot_sizes):
        raise ValueError(f"pilot sizes must be drawn from {PILOT_SIZES}")

    brief = v1._brief(route)
    starts = v1._generate_common_starts(brief, seed, route)
    targets = {
        "local": v1._local_target(brief, seed, route, starts[0]),
        "global": v1._global_target(brief, seed, route),
    }

    regimes = {}
    for kind, target in targets.items():
        adaptive, budget = v1._run_adaptive(brief, seed, starts, target)
        if any(2 * p > budget for p in pilot_sizes):
            raise AssertionError(f"adaptive budget {budget} too small for frozen pilots {pilot_sizes}")

        breadth_seq, fixed_seq, fixed_parent_id = _arm_sequences(
            brief, seed, route, kind, starts, target, budget
        )
        breadth = _metrics(
            starts,
            breadth_seq,
            target,
            "independent-breadth",
            lineageDepth=0,
        )
        fixed = _metrics(
            starts,
            fixed_seq,
            target,
            "fixed-parent-local",
            fixedParent=fixed_parent_id,
            lineageDepth=1,
        )
        probes = {
            str(p): _probe_metrics(starts, target, breadth_seq, fixed_seq, budget, p)
            for p in pilot_sizes
        }

        for item in (adaptive, breadth, fixed, *probes.values()):
            if item["totalCandidates"] != len(starts) + budget:
                raise AssertionError("equal candidate-evaluation budget invariant failed")

        simple_oracle_distance = min(breadth["bestDistance"], fixed["bestDistance"])
        simple_oracle_arm = (
            "independent-breadth"
            if breadth["bestDistance"] + EPSILON < fixed["bestDistance"]
            else "fixed-parent-local"
        )
        best_three_distance = min(
            adaptive["bestDistance"], breadth["bestDistance"], fixed["bestDistance"]
        )

        regimes[kind] = {
            "target": v1._target_record(target, starts),
            "incrementalEvaluationBudget": budget,
            "adaptive": adaptive,
            "breadth": breadth,
            "fixed": fixed,
            "probes": probes,
            "simpleOracleArm": simple_oracle_arm,
            "simpleOracleBestDistance": simple_oracle_distance,
            "bestThreeDistance": best_three_distance,
        }

    combined = {
        "adaptive": statistics.fmean(
            float(regimes[k]["adaptive"]["normalizedImprovement"]) for k in REGIMES
        ),
        "breadth": statistics.fmean(
            float(regimes[k]["breadth"]["normalizedImprovement"]) for k in REGIMES
        ),
        "fixed": statistics.fmean(
            float(regimes[k]["fixed"]["normalizedImprovement"]) for k in REGIMES
        ),
        "probes": {
            str(p): statistics.fmean(
                float(regimes[k]["probes"][str(p)]["normalizedImprovement"])
                for k in REGIMES
            )
            for p in pilot_sizes
        },
    }

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "pilotSizes": list(pilot_sizes),
        "times": list(v1.TIMES),
        "commonStartFingerprints": {c.id: v1.phenotype_fingerprint(c) for c in starts},
        "settings": {
            "commonStarts": v1.COMMON_STARTS,
            "localTargetAcceptedSteps": v1.LOCAL_TARGET_ACCEPTED_STEPS,
            "localTargetScale": v1.LOCAL_TARGET_SCALE,
            "explorePerBasin": v1.EXPLORE_PER_BASIN,
            "roundAPerSurvivor": v1.ROUND_A_PER_SURVIVOR,
            "totalExtraBudget": v1.TOTAL_EXTRA_BUDGET,
            "tieDefaultArm": "fixed-parent-local",
        },
        "regimes": regimes,
        "combinedNormalizedImprovement": combined,
    }


def _parse_pilot_sizes(raw: str) -> tuple[int, ...]:
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if len(set(values)) != len(values):
        raise ValueError("duplicate pilot size")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    parser.add_argument("--pilot-sizes", default=",".join(map(str, PILOT_SIZES)))
    args = parser.parse_args()
    pilot_sizes = _parse_pilot_sizes(args.pilot_sizes)
    print(json.dumps(run_block(args.route, args.seed, pilot_sizes), indent=2))


if __name__ == "__main__":
    main()
