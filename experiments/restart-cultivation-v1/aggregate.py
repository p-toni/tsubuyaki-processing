#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

MASTER_SEEDS = (
    753003, 753019, 753037, 753053, 753071,
    753089, 753107, 753127, 753149, 753167,
    753181, 753199, 753223, 753239, 753257,
    753277, 753293, 753311, 753331, 753349,
)
ROUTES = ("recurrence", "orbit", "filament")
DRAWS = 50000
BOOTSTRAP_SEED = 753555001
MEANINGFUL_MARGIN = 0.003255297955511336


def _mean(values):
    vals = list(values)
    if not vals:
        raise AssertionError("empty mean")
    return statistics.fmean(vals)


def _seed_effects(cells, field):
    by_seed = defaultdict(list)
    for c in cells:
        by_seed[int(c["masterSeed"])].append(float(c[field]))
    if set(by_seed) != set(MASTER_SEEDS):
        raise AssertionError("seed set drift")
    return [_mean(by_seed[s]) for s in MASTER_SEEDS]


def _bootstrap_lower(values, salt: int):
    rng = random.Random(BOOTSTRAP_SEED + salt)
    n = len(values)
    draws = []
    for _ in range(DRAWS):
        draws.append(_mean(values[rng.randrange(n)] for _ in range(n)))
    draws.sort()
    return float(draws[int(0.05 * DRAWS)])


def _route_means(cells, field):
    out = {}
    for route in ROUTES:
        vals = [float(c[field]) for c in cells if c["route"] == route]
        if len(vals) != len(MASTER_SEEDS) * 15:
            raise AssertionError(f"route count drift {route}: {len(vals)}")
        out[route] = _mean(vals)
    return out


def _effect(cells, field, salt):
    seed = _seed_effects(cells, field)
    return {
        "mean": _mean(seed),
        "oneSided95BootstrapLower": _bootstrap_lower(seed, salt),
        "routeMeans": _route_means(cells, field),
    }


def aggregate(input_dir: Path) -> dict:
    records = []
    for seed in MASTER_SEEDS:
        path = input_dir / f"seed-{seed}.json"
        if not path.exists():
            raise AssertionError(f"missing {path}")
        x = json.loads(path.read_text())
        if x["masterSeed"] != seed or x["smoke"] is not False:
            raise AssertionError(f"seed identity drift {seed}")
        if not all(x["hardInvariants"].values()):
            raise AssertionError(f"hard invariant failure {seed}")
        if len(x["cells"]) != 45:
            raise AssertionError(f"cell count drift {seed}")
        records.append(x)

    cells = [c for x in records for c in x["cells"]]
    if len(cells) != 900:
        raise AssertionError(f"rectangle drift: {len(cells)}")
    keys = {(int(c["masterSeed"]), c["route"], c["targetId"]) for c in cells}
    if len(keys) != 900:
        raise AssertionError("duplicate/missing cells")

    effects = {
        "oneShotVsBaselineArchive": _effect(cells, "oneShotVsBaselineArchiveDelta", 1),
        "oneShotVsBaselineDelivery": _effect(cells, "oneShotVsBaselineDeliveryDelta", 2),
        "cultivatedVsBaselineArchive": _effect(cells, "cultivatedVsBaselineArchiveDelta", 3),
        "cultivatedVsBaselineDelivery": _effect(cells, "cultivatedVsBaselineDeliveryDelta", 4),
        "cultivatedVsOneShotArchive": _effect(cells, "cultivatedVsOneShotArchiveDelta", 5),
        "cultivatedVsOneShotDelivery": _effect(cells, "cultivatedVsOneShotDeliveryDelta", 6),
    }

    baseline_valid = sum(
        int(x["routes"][r]["baseline20"]["operatorDiagnostics"]["valid"])
        for x in records for r in ROUTES
    )
    one_shot_valid = sum(
        int(x["routes"][r]["oneShot20"]["validGenerated"])
        for x in records for r in ROUTES
    )
    cultivated_valid = sum(
        int(x["routes"][r]["cultivated20"]["validGenerated"])
        for x in records for r in ROUTES
    )
    valid_restart_parents = sum(
        int(x["routes"][r]["cultivated20"]["validRestarts"])
        for x in records for r in ROUTES
    )
    valid_children = sum(
        int(x["routes"][r]["cultivated20"]["validCultivationChildren"])
        for x in records for r in ROUTES
    )

    attempts = len(MASTER_SEEDS) * len(ROUTES) * 20
    restart_attempts = len(MASTER_SEEDS) * len(ROUTES) * 2
    child_attempts = restart_attempts
    baseline_rate = baseline_valid / attempts
    one_shot_rate = one_shot_valid / attempts
    cultivated_rate = cultivated_valid / attempts
    restart_parent_rate = valid_restart_parents / restart_attempts
    child_rate = valid_children / child_attempts

    os_a = effects["oneShotVsBaselineArchive"]
    os_d = effects["oneShotVsBaselineDelivery"]
    cv_a = effects["cultivatedVsBaselineArchive"]
    cv_d = effects["cultivatedVsBaselineDelivery"]
    co_a = effects["cultivatedVsOneShotArchive"]
    co_d = effects["cultivatedVsOneShotDelivery"]

    gates = {
        "oneShotArchiveMeanAboveMargin": os_a["mean"] > MEANINGFUL_MARGIN,
        "oneShotArchiveLowerPositive": os_a["oneSided95BootstrapLower"] > 0.0,
        "oneShotEveryRouteArchivePositive": all(v > 0.0 for v in os_a["routeMeans"].values()),
        "oneShotDeliveryMeanAboveMargin": os_d["mean"] > MEANINGFUL_MARGIN,
        "oneShotDeliveryLowerPositive": os_d["oneSided95BootstrapLower"] > 0.0,
        "oneShotEveryRouteDeliveryPositive": all(v > 0.0 for v in os_d["routeMeans"].values()),

        "cultivatedArchiveMeanAboveMargin": cv_a["mean"] > MEANINGFUL_MARGIN,
        "cultivatedArchiveLowerPositive": cv_a["oneSided95BootstrapLower"] > 0.0,
        "cultivatedEveryRouteArchivePositive": all(v > 0.0 for v in cv_a["routeMeans"].values()),
        "cultivatedDeliveryMeanAboveMargin": cv_d["mean"] > MEANINGFUL_MARGIN,
        "cultivatedDeliveryLowerPositive": cv_d["oneSided95BootstrapLower"] > 0.0,
        "cultivatedEveryRouteDeliveryPositive": all(v > 0.0 for v in cv_d["routeMeans"].values()),

        "cultivatedArchiveNonInferiorToOneShot": co_a["oneSided95BootstrapLower"] > -MEANINGFUL_MARGIN,
        "cultivatedEveryRouteArchiveWithinMarginOfOneShot": all(
            v > -MEANINGFUL_MARGIN for v in co_a["routeMeans"].values()
        ),
        "cultivatedDeliveryNonInferiorToOneShot": co_d["oneSided95BootstrapLower"] > -MEANINGFUL_MARGIN,
        "cultivatedEveryRouteDeliveryWithinMarginOfOneShot": all(
            v > -MEANINGFUL_MARGIN for v in co_d["routeMeans"].values()
        ),

        "cultivatedValidityWithinOnePointOfBaseline": cultivated_rate >= baseline_rate - 0.01,
        "restartParentValidRateAtLeast95Pct": restart_parent_rate >= 0.95,
        "cultivationChildValidRateAtLeast95Pct": child_rate >= 0.95,
    }
    passed = all(gates.values())

    return {
        "version": 1,
        "decision": "RESTART_CULTIVATION_PROMISING" if passed else "RESTART_CULTIVATION_NOT_PROMISING",
        "artisticEvidence": False,
        "authority": "mechanical-structural-equal-budget-only",
        "seedCount": len(MASTER_SEEDS),
        "routeSeedCount": len(MASTER_SEEDS) * len(ROUTES),
        "cellCount": len(cells),
        "budgetPerArm": 20,
        "meaningfulEffectMargin": MEANINGFUL_MARGIN,
        "effects": effects,
        "validity": {
            "attemptsPerArm": attempts,
            "baselineValidCount": baseline_valid,
            "oneShotValidCount": one_shot_valid,
            "cultivatedValidCount": cultivated_valid,
            "baselineValidRate": baseline_rate,
            "oneShotValidRate": one_shot_rate,
            "cultivatedValidRate": cultivated_rate,
            "cultivatedMinusBaselineValidRate": cultivated_rate - baseline_rate,
            "validRestartParentCount": valid_restart_parents,
            "restartParentAttemptCount": restart_attempts,
            "restartParentValidRate": restart_parent_rate,
            "validCultivationChildCount": valid_children,
            "cultivationChildAttemptCount": child_attempts,
            "cultivationChildValidRate": child_rate,
        },
        "gates": gates,
        "mechanicalPassed": passed,
        "bootstrap": {
            "draws": DRAWS,
            "seedBase": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 45 paired route-target cells",
        },
        "researchLineStatus": "FRESH_STRICT_ARTISTIC_REVIEW_AUTHORIZED" if passed else "AUTOMATIC_RESTART_SUBSTITUTION_STOPPED",
        "interpretation": (
            "Two restart basins plus one local child per basin preserve the fresh one-shot structural advantage within the frozen non-inferiority margin while remaining strongly above baseline. This supports the maturity loophole mechanically and authorizes one fresh stricter blinded artistic review only; production remains unchanged."
            if passed else
            "Cultivating restart basins does not satisfy the frozen replication, baseline-improvement, non-inferiority, and validity gates. Stop automatic restart substitution rather than tuning cultivation on consumed 753xxx evidence; use a baseline-preserving optional restart sidecar as the evidence-conservative fallback."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output")
    args = p.parse_args()
    result = aggregate(Path(args.input_dir))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
