#!/usr/bin/env python3
"""Zero-extra-cost start-state topology selector calibration/holdout simulator."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1_PATH = ROOT / "experiments" / "search-leverage-v1" / "reproduce.py"
PROBE_PATH = ROOT / "experiments" / "online-topology-probe-v1" / "probe.py"

v1_spec = importlib.util.spec_from_file_location("search_leverage_v1", V1_PATH)
v1 = importlib.util.module_from_spec(v1_spec)
assert v1_spec.loader is not None
v1_spec.loader.exec_module(v1)

probe_spec = importlib.util.spec_from_file_location("online_probe_v1", PROBE_PATH)
online_probe = importlib.util.module_from_spec(probe_spec)
assert probe_spec.loader is not None
probe_spec.loader.exec_module(online_probe)

ROUTE_ORDER = tuple(v1.ROUTE_ORDER)
CALIBRATION_SEEDS = (101, 103, 107, 109, 113, 127, 131, 137, 139)
HOLDOUT_SEEDS = (149, 151, 157)
ALL_SEEDS = CALIBRATION_SEEDS + HOLDOUT_SEEDS
THRESHOLDS = (0.0, 0.025, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0)
PILOT_SIZE = 4
REGIMES = ("local", "global")
EPSILON = v1.EPSILON


def start_concentration(starts: list, target) -> tuple[float, list[float]]:
    frames = v1._frame_bytes(target)
    distances = sorted(float(v1.phenotype_distance(c, frames)) for c in starts)
    if len(distances) < 2:
        raise AssertionError("start-state selector requires at least two common starts")
    mean_distance = statistics.fmean(distances)
    concentration = (distances[1] - distances[0]) / max(mean_distance, EPSILON)
    return concentration, distances


def choose_policy(concentration: float, threshold: float) -> str:
    return "adaptive" if concentration + EPSILON >= threshold else "simple-probe"


def run_block(route: str, seed: int, thresholds: tuple[float, ...]) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"route {route!r} is not predeclared")
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    if not thresholds or any(t not in THRESHOLDS for t in thresholds):
        raise ValueError(f"thresholds must be drawn from {THRESHOLDS}")

    brief = v1._brief(route)
    starts = v1._generate_common_starts(brief, seed, route)
    targets = {
        "local": v1._local_target(brief, seed, route, starts[0]),
        "global": v1._global_target(brief, seed, route),
    }

    regimes = {}
    for kind, target in targets.items():
        concentration, start_distances = start_concentration(starts, target)
        adaptive, budget = v1._run_adaptive(brief, seed, starts, target)
        breadth_seq, fixed_seq, _ = online_probe._arm_sequences(
            brief, seed, route, kind, starts, target, budget
        )
        simple_probe = online_probe._probe_metrics(
            starts, target, breadth_seq, fixed_seq, budget, PILOT_SIZE
        )
        if adaptive["totalCandidates"] != simple_probe["totalCandidates"]:
            raise AssertionError("adaptive/simple equal-budget invariant failed")

        a_imp = float(adaptive["normalizedImprovement"])
        s_imp = float(simple_probe["normalizedImprovement"])
        oracle_policy = "adaptive" if a_imp + EPSILON >= s_imp else "simple-probe"
        oracle_imp = max(a_imp, s_imp)

        threshold_rows = {}
        for threshold in thresholds:
            chosen = choose_policy(concentration, threshold)
            selected_imp = a_imp if chosen == "adaptive" else s_imp
            threshold_rows[str(threshold)] = {
                "chosenPolicy": chosen,
                "selectedImprovement": selected_imp,
                "oraclePolicy": oracle_policy,
                "oracleImprovement": oracle_imp,
                "choiceCorrect": chosen == oracle_policy,
                "strictWinVsAdaptive": selected_imp > a_imp + EPSILON,
                "nonWorseVsAdaptive": selected_imp + EPSILON >= a_imp,
            }

        regimes[kind] = {
            "target": v1._target_record(target, starts),
            "incrementalEvaluationBudget": budget,
            "startDistances": start_distances,
            "startConcentration": concentration,
            "adaptive": adaptive,
            "simpleProbe": simple_probe,
            "thresholds": threshold_rows,
        }

    combined = {}
    for threshold in thresholds:
        key = str(threshold)
        selected = statistics.fmean(
            float(regimes[k]["thresholds"][key]["selectedImprovement"])
            for k in REGIMES
        )
        adaptive = statistics.fmean(
            float(regimes[k]["adaptive"]["normalizedImprovement"])
            for k in REGIMES
        )
        simple = statistics.fmean(
            float(regimes[k]["simpleProbe"]["normalizedImprovement"])
            for k in REGIMES
        )
        oracle = statistics.fmean(
            float(regimes[k]["thresholds"][key]["oracleImprovement"])
            for k in REGIMES
        )
        combined[key] = {
            "selectedImprovement": selected,
            "adaptiveImprovement": adaptive,
            "simpleProbeImprovement": simple,
            "adaptiveVsSimpleOracleImprovement": oracle,
            "strictWinVsAdaptive": selected > adaptive + EPSILON,
            "nonWorseVsAdaptive": selected + EPSILON >= adaptive,
        }

    return {
        "version": 1,
        "route": route,
        "seed": seed,
        "thresholds": list(thresholds),
        "pilotSize": PILOT_SIZE,
        "times": list(v1.TIMES),
        "commonStartFingerprints": {c.id: v1.phenotype_fingerprint(c) for c in starts},
        "signal": "(second_best_start_distance - best_start_distance) / mean_start_distance",
        "decision": "adaptive when concentration >= threshold; otherwise simple-probe",
        "regimes": regimes,
        "combined": combined,
    }


def _parse_thresholds(raw: str) -> tuple[float, ...]:
    values = tuple(float(part.strip()) for part in raw.split(",") if part.strip())
    if len(set(values)) != len(values):
        raise ValueError("duplicate threshold")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTE_ORDER, required=True)
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    parser.add_argument("--thresholds", default=",".join(str(x) for x in THRESHOLDS))
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed, _parse_thresholds(args.thresholds)), indent=2))


if __name__ == "__main__":
    main()
