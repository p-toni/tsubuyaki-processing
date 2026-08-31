#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from run_allocation import (
    ARMS,
    MASTER_SEEDS,
    MEANINGFUL_MARGIN,
    ROUTES,
)

BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 745555001


def _mean(xs):
    return statistics.fmean(xs) if xs else 0.0


def _percentile(xs, q):
    ys = sorted(xs)
    if not ys:
        raise ValueError("empty percentile")
    pos = (len(ys) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ys) - 1)
    frac = pos - lo
    return ys[lo] * (1.0 - frac) + ys[hi] * frac


def _bootstrap_lower(seed_effects):
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(seed_effects)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        draws.append(_mean([seed_effects[rng.randrange(n)] for _ in range(n)]))
    return _percentile(draws, 0.05)


def aggregate(input_dir: Path) -> dict:
    files = sorted(input_dir.glob("seed-*.json"))
    rows = [json.loads(p.read_text()) for p in files]
    got = tuple(sorted(int(x["masterSeed"]) for x in rows))
    expected = tuple(sorted(MASTER_SEEDS))
    if got != expected:
        raise AssertionError(f"seed set mismatch: got {got}, expected {expected}")
    if any(bool(x.get("smoke")) for x in rows):
        raise AssertionError("smoke result present in authoritative aggregate")
    if not all(all(x["hardInvariants"].values()) for x in rows):
        raise AssertionError("one or more hard invariants failed")

    seed_ab_archive = []
    seed_ax_archive = []
    seed_ab_delivery = []
    seed_ax_delivery = []
    route_ab_archive = defaultdict(list)
    route_ax_archive = defaultdict(list)
    route_ab_delivery = defaultdict(list)
    route_ax_delivery = defaultdict(list)
    winner_counts = {"native": 0, "spectral": 0}
    valid_totals = {arm: 0 for arm in ARMS}
    attempt_totals = {arm: 0 for arm in ARMS}
    cells = []

    seed_rows = []
    for x in rows:
        if len(x["cells"]) != 45:
            raise AssertionError(f"seed {x['masterSeed']} has wrong cell count")
        cells.extend(x["cells"])
        ab_archive = [float(c["adaptiveMinusBaselineArchive"]) for c in x["cells"]]
        ax_archive = [float(c["adaptiveMinusAntiArchive"]) for c in x["cells"]]
        ab_delivery = [float(c["adaptiveMinusBaselineDelivery"]) for c in x["cells"]]
        ax_delivery = [float(c["adaptiveMinusAntiDelivery"]) for c in x["cells"]]
        seed_ab_archive.append(_mean(ab_archive))
        seed_ax_archive.append(_mean(ax_archive))
        seed_ab_delivery.append(_mean(ab_delivery))
        seed_ax_delivery.append(_mean(ax_delivery))
        seed_rows.append(
            {
                "masterSeed": int(x["masterSeed"]),
                "adaptiveMinusBaselineArchive": _mean(ab_archive),
                "adaptiveMinusAntiArchive": _mean(ax_archive),
                "adaptiveMinusBaselineDelivery": _mean(ab_delivery),
                "adaptiveMinusAntiDelivery": _mean(ax_delivery),
            }
        )

        for c in x["cells"]:
            route = str(c["route"])
            route_ab_archive[route].append(float(c["adaptiveMinusBaselineArchive"]))
            route_ax_archive[route].append(float(c["adaptiveMinusAntiArchive"]))
            route_ab_delivery[route].append(float(c["adaptiveMinusBaselineDelivery"]))
            route_ax_delivery[route].append(float(c["adaptiveMinusAntiDelivery"]))

        for route in ROUTES:
            winner = str(x["routes"][route]["noveltyDecision"]["winner"])
            if winner not in winner_counts:
                raise AssertionError(f"unexpected novelty winner {winner!r}")
            winner_counts[winner] += 1
            for arm in ARMS:
                diag = x["routes"][route]["arms"][arm]["operatorDiagnostics"]
                valid_totals[arm] += int(diag["valid"])
                attempt_totals[arm] += int(diag["total"])

    mean_ab_archive = _mean(seed_ab_archive)
    mean_ax_archive = _mean(seed_ax_archive)
    mean_ab_delivery = _mean(seed_ab_delivery)
    mean_ax_delivery = _mean(seed_ax_delivery)

    lower_ab_archive = _bootstrap_lower(seed_ab_archive)
    lower_ax_archive = _bootstrap_lower(seed_ax_archive)
    lower_ab_delivery = _bootstrap_lower(seed_ab_delivery)
    lower_ax_delivery = _bootstrap_lower(seed_ax_delivery)

    route_means = {
        "adaptiveMinusBaselineArchive": {
            route: _mean(route_ab_archive[route]) for route in ROUTES
        },
        "adaptiveMinusAntiArchive": {
            route: _mean(route_ax_archive[route]) for route in ROUTES
        },
        "adaptiveMinusBaselineDelivery": {
            route: _mean(route_ab_delivery[route]) for route in ROUTES
        },
        "adaptiveMinusAntiDelivery": {
            route: _mean(route_ax_delivery[route]) for route in ROUTES
        },
    }

    valid_rates = {
        arm: valid_totals[arm] / attempt_totals[arm] for arm in ARMS
    }
    adaptive_minus_baseline_valid = (
        valid_rates["adaptive12x8"] - valid_rates["baseline10x10"]
    )
    route_seed_count = len(rows) * len(ROUTES)
    minority_winner_rate = min(winner_counts.values()) / route_seed_count
    dominant_operator = max(winner_counts, key=winner_counts.get)
    dominant_rate = winner_counts[dominant_operator] / route_seed_count

    gates = {
        "archiveMeanVsBaselineAboveMeaningfulMargin": (
            mean_ab_archive > MEANINGFUL_MARGIN
        ),
        "archive95LowerVsBaselinePositive": lower_ab_archive > 0.0,
        "archiveMeanVsAntiPositive": mean_ax_archive > 0.0,
        "archive95LowerVsAntiPositive": lower_ax_archive > 0.0,
        "everyRouteArchiveVsBaselinePositive": all(
            v > 0.0
            for v in route_means["adaptiveMinusBaselineArchive"].values()
        ),
        "everyRouteArchiveVsAntiPositive": all(
            v > 0.0 for v in route_means["adaptiveMinusAntiArchive"].values()
        ),
        "deliveryMeanVsBaselinePositive": mean_ab_delivery > 0.0,
        "delivery95LowerVsBaselineAboveNegativeMargin": (
            lower_ab_delivery > -MEANINGFUL_MARGIN
        ),
        "everyRouteDeliveryVsBaselineAboveNegativeMargin": all(
            v > -MEANINGFUL_MARGIN
            for v in route_means["adaptiveMinusBaselineDelivery"].values()
        ),
        "adaptiveValidityNoMoreThanFivePointsLower": (
            adaptive_minus_baseline_valid >= -0.05
        ),
        "bothOperatorsWinAtLeastTwentyPercent": minority_winner_rate >= 0.20,
    }

    core_gate_names = (
        "archiveMeanVsBaselineAboveMeaningfulMargin",
        "archive95LowerVsBaselinePositive",
        "archiveMeanVsAntiPositive",
        "archive95LowerVsAntiPositive",
        "everyRouteArchiveVsBaselinePositive",
        "everyRouteArchiveVsAntiPositive",
        "deliveryMeanVsBaselinePositive",
        "delivery95LowerVsBaselineAboveNegativeMargin",
        "everyRouteDeliveryVsBaselineAboveNegativeMargin",
        "adaptiveValidityNoMoreThanFivePointsLower",
    )
    core_pass = all(gates[name] for name in core_gate_names)
    diversity_pass = gates["bothOperatorsWinAtLeastTwentyPercent"]

    if core_pass and diversity_pass:
        decision = "NOVELTY_OPERATOR_ALLOCATION_PROMISING"
        research_status = "FRESH_BLINDED_ARTISTIC_COMPARISON_AUTHORIZED"
    elif core_pass and not diversity_pass:
        decision = "GLOBAL_OPERATOR_BIAS_INDICATED"
        research_status = "FRESH_FIXED_DOMINANT_OPERATOR_RATIO_REPLICATION_AUTHORIZED"
    else:
        decision = "NOVELTY_OPERATOR_ALLOCATION_NOT_PROMISING"
        research_status = "EXACT_PREFIX_NOVELTY_12X8_POLICY_STOPPED"

    return {
        "version": 1,
        "decision": decision,
        "artisticEvidence": False,
        "authority": "mechanical-structural-benchmark-only",
        "seedCount": len(rows),
        "routeSeedCount": route_seed_count,
        "cellCount": len(cells),
        "meaningfulEffectMargin": MEANINGFUL_MARGIN,
        "meanAdaptiveMinusBaselineArchive": mean_ab_archive,
        "oneSided95BootstrapLowerAdaptiveMinusBaselineArchive": lower_ab_archive,
        "meanAdaptiveMinusAntiArchive": mean_ax_archive,
        "oneSided95BootstrapLowerAdaptiveMinusAntiArchive": lower_ax_archive,
        "meanAdaptiveMinusBaselineDelivery": mean_ab_delivery,
        "oneSided95BootstrapLowerAdaptiveMinusBaselineDelivery": lower_ab_delivery,
        "meanAdaptiveMinusAntiDelivery": mean_ax_delivery,
        "oneSided95BootstrapLowerAdaptiveMinusAntiDelivery": lower_ax_delivery,
        "routeMeanEffects": route_means,
        "noveltyWinnerCounts": winner_counts,
        "minorityWinnerRate": minority_winner_rate,
        "dominantOperator": dominant_operator,
        "dominantOperatorRate": dominant_rate,
        "validRates": valid_rates,
        "adaptiveMinusBaselineValidRate": adaptive_minus_baseline_valid,
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 45 paired route-target cells",
        },
        "gates": gates,
        "corePerformancePassed": core_pass,
        "trajectorySpecificityPassed": diversity_pass,
        "seedEffects": sorted(seed_rows, key=lambda x: x["masterSeed"]),
        "researchLineStatus": research_status,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = aggregate(Path(args.input_dir))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    Path(args.output).write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
