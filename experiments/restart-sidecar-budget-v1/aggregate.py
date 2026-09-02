#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

BUDGETS = (1, 2, 4, 8)
ROUTES = ("recurrence", "orbit", "filament")
MASTER_SEEDS = (
    759003, 759019, 759037, 759053, 759071,
    759089, 759107, 759127, 759149, 759167,
    759181, 759199, 759223, 759239, 759257,
    759277, 759293, 759311, 759331, 759349,
)
BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 759555001
EPS = 1e-12
SUFFICIENCY_RATIO = 0.90


def _mean(xs):
    return statistics.fmean(xs) if xs else 0.0


def _bootstrap_lower(seed_values: list[float], rng: random.Random) -> float:
    n = len(seed_values)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        draws.append(_mean([seed_values[rng.randrange(n)] for _ in range(n)]))
    draws.sort()
    return draws[int(0.05 * (len(draws) - 1))]


def aggregate(input_dir: Path) -> dict:
    records = []
    for path in sorted(input_dir.glob("seed-*.json")):
        records.append(json.loads(path.read_text()))
    seeds = sorted(int(x["masterSeed"]) for x in records)
    if seeds != sorted(MASTER_SEEDS):
        raise AssertionError(f"incomplete or unexpected seed rectangle: {seeds}")
    if not all(x["smoke"] is False and all(x["hardInvariants"].values()) for x in records):
        raise AssertionError("authoritative record failed hard invariant")

    seed_metrics = {k: [] for k in BUDGETS}
    route_archive = {k: defaultdict(list) for k in BUDGETS}
    route_delivery = {k: defaultdict(list) for k in BUDGETS}
    validity_attempts = 0
    validity_valid = 0

    for record in records:
        cells_by_budget = {k: [] for k in BUDGETS}
        for cell in record["cells"]:
            k = int(cell["budget"])
            cells_by_budget[k].append(cell)
            route_archive[k][cell["route"]].append(float(cell["archiveDelta"]))
            route_delivery[k][cell["route"]].append(float(cell["deliveryDelta"]))

        for route in ROUTES:
            sidecars = record["routes"][route]["sidecar"]
            validity_attempts += len(sidecars)
            validity_valid += sum(bool(c["valid"]) for c in sidecars)

        for k in BUDGETS:
            cells = cells_by_budget[k]
            if len(cells) != 45:
                raise AssertionError(f"seed {record['masterSeed']} budget {k} cell count {len(cells)}")
            archive_mean = _mean([float(c["archiveDelta"]) for c in cells])
            delivery_mean = _mean([float(c["deliveryDelta"]) for c in cells])
            dispersion_deltas = []
            distinct_added = []
            valid_rates = []
            for route in ROUTES:
                rr = record["routes"][route]
                b = rr["budgets"][str(k)]
                dispersion_deltas.append(
                    float(b["dispersion"]["minimumPairwiseDistance"])
                    - float(rr["baselineDispersion"]["minimumPairwiseDistance"])
                )
                distinct_added.append(float(b["distinctValidPhenotypesAddedVsBaseline"]))
                valid_rates.append(float(b["validRate"]))
            seed_metrics[k].append({
                "seed": int(record["masterSeed"]),
                "archiveDelta": archive_mean,
                "deliveryDelta": delivery_mean,
                "minimumDispersionDelta": _mean(dispersion_deltas),
                "distinctPhenotypesAdded": _mean(distinct_added),
                "sidecarValidRate": _mean(valid_rates),
            })

    rng = random.Random(BOOTSTRAP_SEED)
    budgets = {}
    for k in BUDGETS:
        sm = seed_metrics[k]
        archive_values = [x["archiveDelta"] for x in sm]
        delivery_values = [x["deliveryDelta"] for x in sm]
        dispersion_values = [x["minimumDispersionDelta"] for x in sm]
        budgets[str(k)] = {
            "archiveDeltaMean": _mean(archive_values),
            "archiveDeltaOneSided95BootstrapLower": _bootstrap_lower(archive_values, rng),
            "deliveryDeltaMean": _mean(delivery_values),
            "deliveryDeltaOneSided95BootstrapLower": _bootstrap_lower(delivery_values, rng),
            "minimumDispersionDeltaMean": _mean(dispersion_values),
            "distinctPhenotypesAddedMeanPerRoute": _mean([x["distinctPhenotypesAdded"] for x in sm]),
            "sidecarValidRateMeanAcrossRouteSeeds": _mean([x["sidecarValidRate"] for x in sm]),
            "routeArchiveDeltaMeans": {r: _mean(route_archive[k][r]) for r in ROUTES},
            "routeDeliveryDeltaMeans": {r: _mean(route_delivery[k][r]) for r in ROUTES},
        }

    maxb = budgets["8"]
    prerequisite = {
        "maxBudgetValidityAtLeast95Pct": validity_valid / validity_attempts >= 0.95,
        "maxBudgetArchiveMeanPositive": maxb["archiveDeltaMean"] > 0,
        "maxBudgetArchiveLowerPositive": maxb["archiveDeltaOneSided95BootstrapLower"] > 0,
        "maxBudgetDeliveryMeanPositive": maxb["deliveryDeltaMean"] > 0,
        "maxBudgetDeliveryLowerPositive": maxb["deliveryDeltaOneSided95BootstrapLower"] > 0,
        "maxBudgetMinimumDispersionMeanPositive": maxb["minimumDispersionDeltaMean"] > 0,
        "maxBudgetEveryRouteArchiveNonNegative": all(v >= -1e-15 for v in maxb["routeArchiveDeltaMeans"].values()),
        "maxBudgetEveryRouteDeliveryNonNegative": all(v >= -1e-15 for v in maxb["routeDeliveryDeltaMeans"].values()),
    }

    ratios = {}
    sufficient = {}
    max_gains = {
        "archive": maxb["archiveDeltaMean"],
        "delivery": maxb["deliveryDeltaMean"],
        "dispersion": maxb["minimumDispersionDeltaMean"],
    }
    denominator_ok = all(v > EPS for v in max_gains.values())
    for k in BUDGETS:
        b = budgets[str(k)]
        if denominator_ok:
            ratio = {
                "archive": b["archiveDeltaMean"] / max_gains["archive"],
                "delivery": b["deliveryDeltaMean"] / max_gains["delivery"],
                "dispersion": b["minimumDispersionDeltaMean"] / max_gains["dispersion"],
            }
        else:
            ratio = {"archive": None, "delivery": None, "dispersion": None}
        ratios[str(k)] = ratio
        sufficient[str(k)] = bool(
            denominator_ok
            and all(v is not None and v >= SUFFICIENCY_RATIO for v in ratio.values())
            and all(v >= -1e-15 for v in b["routeArchiveDeltaMeans"].values())
            and all(v >= -1e-15 for v in b["routeDeliveryDeltaMeans"].values())
        )

    if not all(prerequisite.values()) or not denominator_ok:
        decision = "SIDECAR_BUDGET_EFFECT_NOT_DEMONSTRATED"
        selected = 4
    else:
        selected = next(k for k in BUDGETS if sufficient[str(k)])
        if selected == 4:
            decision = "SIDECAR_DEFAULT_FOUR_MECHANICALLY_EFFICIENT"
        elif selected in (1, 2):
            decision = "SIDECAR_SMALLER_BUDGET_SUFFICIENT"
        else:
            decision = "SIDECAR_EIGHT_REQUIRED_FOR_COVERAGE"

    return {
        "version": 1,
        "experiment": "restart-sidecar-budget-v1",
        "artisticEvidence": False,
        "authority": "mechanical-compute-coverage-only",
        "seedCount": len(records),
        "routeSeedCount": len(records) * len(ROUTES),
        "budgetsPerRoute": list(BUDGETS),
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 45 route-target cells; dispersion mean across three routes",
        },
        "coverageSufficiencyRatio": SUFFICIENCY_RATIO,
        "maxBudgetSidecarValidCount": validity_valid,
        "maxBudgetSidecarAttemptCount": validity_attempts,
        "maxBudgetSidecarValidRate": validity_valid / validity_attempts,
        "budgets": budgets,
        "gainRatiosVsEight": ratios,
        "coverageSufficient": sufficient,
        "prerequisiteGates": prerequisite,
        "selectedAttemptsPerRoute": selected,
        "decision": decision,
        "interpretation": (
            "Select the smallest sidecar budget that captures at least 90% of the k=8 pooled gain on archive structural recovery, max-dispersion delivery recovery, and minimum pairwise dispersion, after the maximum budget first demonstrates a positive valid mechanical coverage effect. This does not confer artistic authority or change baseline search."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = aggregate(Path(args.input_dir))
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
