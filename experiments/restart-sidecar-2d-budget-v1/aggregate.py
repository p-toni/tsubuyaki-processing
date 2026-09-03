#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

BUDGETS = (1, 2, 4, 8)
ROUTES = ("family", "sheet")
MASTER_SEEDS = (
    761003, 761019, 761037, 761053, 761071,
    761089, 761107, 761127, 761149, 761167,
    761181, 761199, 761223, 761239, 761257,
    761277, 761293, 761311, 761331, 761349,
)
BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 761555001
MEANINGFUL_EFFECT_BAR = 0.003255297955511336
SUFFICIENCY_RATIO = 0.90
EPS = 1e-12


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
    records = [json.loads(p.read_text()) for p in sorted(input_dir.glob("seed-*.json"))]
    seeds = sorted(int(x["masterSeed"]) for x in records)
    if seeds != sorted(MASTER_SEEDS):
        raise AssertionError(f"incomplete or unexpected seed rectangle: {seeds}")
    if not all(x["smoke"] is False and all(x["hardInvariants"].values()) for x in records):
        raise AssertionError("authoritative record failed hard invariant")

    seed_metrics = {k: [] for k in BUDGETS}
    route_archive = {k: defaultdict(list) for k in BUDGETS}
    route_delivery = {k: defaultdict(list) for k in BUDGETS}
    route_dispersion = {k: defaultdict(list) for k in BUDGETS}
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
            rr = record["routes"][route]
            for k in BUDGETS:
                route_dispersion[k][route].append(
                    float(rr["budgets"][str(k)]["dispersion"]["minimumPairwiseDistance"])
                    - float(rr["baselineDispersion"]["minimumPairwiseDistance"])
                )

        for k in BUDGETS:
            cells = cells_by_budget[k]
            if len(cells) != len(ROUTES) * 15:
                raise AssertionError(
                    f"seed {record['masterSeed']} budget {k} cell count {len(cells)}"
                )
            seed_metrics[k].append({
                "seed": int(record["masterSeed"]),
                "archiveDelta": _mean([float(c["archiveDelta"]) for c in cells]),
                "deliveryDelta": _mean([float(c["deliveryDelta"]) for c in cells]),
                "minimumDispersionDelta": _mean([
                    float(record["routes"][r]["budgets"][str(k)]["dispersion"]["minimumPairwiseDistance"])
                    - float(record["routes"][r]["baselineDispersion"]["minimumPairwiseDistance"])
                    for r in ROUTES
                ]),
                "distinctPhenotypesAdded": _mean([
                    float(record["routes"][r]["budgets"][str(k)]["distinctValidPhenotypesAddedVsBaseline"])
                    for r in ROUTES
                ]),
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
            "distinctPhenotypesAddedMeanPerRoute": _mean([
                x["distinctPhenotypesAdded"] for x in sm
            ]),
            "routeArchiveDeltaMeans": {r: _mean(route_archive[k][r]) for r in ROUTES},
            "routeDeliveryDeltaMeans": {r: _mean(route_delivery[k][r]) for r in ROUTES},
            "routeMinimumDispersionDeltaMeans": {
                r: _mean(route_dispersion[k][r]) for r in ROUTES
            },
        }

    maxb = budgets["8"]
    validity_rate = validity_valid / validity_attempts
    prerequisite = {
        "maxBudgetValidityAtLeast95Pct": validity_rate >= 0.95,
        "maxBudgetArchiveAboveMeaningfulEffectBar": maxb["archiveDeltaMean"] > MEANINGFUL_EFFECT_BAR,
        "maxBudgetArchiveLowerPositive": maxb["archiveDeltaOneSided95BootstrapLower"] > 0,
        "maxBudgetDeliveryAboveMeaningfulEffectBar": maxb["deliveryDeltaMean"] > MEANINGFUL_EFFECT_BAR,
        "maxBudgetDeliveryLowerPositive": maxb["deliveryDeltaOneSided95BootstrapLower"] > 0,
        "maxBudgetMinimumDispersionMeanPositive": maxb["minimumDispersionDeltaMean"] > 0,
        "maxBudgetEveryRouteArchivePositive": all(v > 0 for v in maxb["routeArchiveDeltaMeans"].values()),
        "maxBudgetEveryRouteDeliveryPositive": all(v > 0 for v in maxb["routeDeliveryDeltaMeans"].values()),
    }

    pooled_denominators = {
        "archive": maxb["archiveDeltaMean"],
        "delivery": maxb["deliveryDeltaMean"],
        "dispersion": maxb["minimumDispersionDeltaMean"],
    }
    route_denominators = {
        r: {
            "archive": maxb["routeArchiveDeltaMeans"][r],
            "delivery": maxb["routeDeliveryDeltaMeans"][r],
        }
        for r in ROUTES
    }
    denominator_ok = all(v > EPS for v in pooled_denominators.values()) and all(
        v > EPS for r in ROUTES for v in route_denominators[r].values()
    )

    ratios = {}
    sufficient = {}
    for k in BUDGETS:
        b = budgets[str(k)]
        if denominator_ok:
            pooled = {
                "archive": b["archiveDeltaMean"] / pooled_denominators["archive"],
                "delivery": b["deliveryDeltaMean"] / pooled_denominators["delivery"],
                "dispersion": b["minimumDispersionDeltaMean"] / pooled_denominators["dispersion"],
            }
            by_route = {
                r: {
                    "archive": b["routeArchiveDeltaMeans"][r] / route_denominators[r]["archive"],
                    "delivery": b["routeDeliveryDeltaMeans"][r] / route_denominators[r]["delivery"],
                }
                for r in ROUTES
            }
        else:
            pooled = {"archive": None, "delivery": None, "dispersion": None}
            by_route = {r: {"archive": None, "delivery": None} for r in ROUTES}
        ratios[str(k)] = {"pooled": pooled, "byRoute": by_route}
        sufficient[str(k)] = bool(
            denominator_ok
            and all(v is not None and v >= SUFFICIENCY_RATIO for v in pooled.values())
            and all(
                v is not None and v >= SUFFICIENCY_RATIO
                for r in ROUTES for v in by_route[r].values()
            )
            and all(v >= -1e-15 for v in b["routeArchiveDeltaMeans"].values())
            and all(v >= -1e-15 for v in b["routeDeliveryDeltaMeans"].values())
            and all(v >= -1e-15 for v in b["routeMinimumDispersionDeltaMeans"].values())
        )

    if not all(prerequisite.values()) or not denominator_ok:
        selected = None
        decision = "SIDECAR_2D_BUDGET_EFFECT_NOT_REPLICATED"
    else:
        selected = next(k for k in BUDGETS if sufficient[str(k)])
        if selected in (1, 2):
            decision = "SIDECAR_2D_SMALLER_BUDGET_SUFFICIENT"
        elif selected == 4:
            decision = "SIDECAR_2D_FOUR_MECHANICALLY_EFFICIENT"
        else:
            decision = "SIDECAR_2D_EIGHT_REQUIRED_FOR_COVERAGE"

    return {
        "version": 1,
        "experiment": "restart-sidecar-2d-budget-v1",
        "artisticEvidence": False,
        "authority": "mechanical-compute-coverage-only",
        "seedCount": len(records),
        "routeSeedCount": len(records) * len(ROUTES),
        "budgetsPerRoute": list(BUDGETS),
        "historicalMeaningfulEffectBar": MEANINGFUL_EFFECT_BAR,
        "coverageSufficiencyRatio": SUFFICIENCY_RATIO,
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed equal-route mean",
        },
        "maxBudgetSidecarValidCount": validity_valid,
        "maxBudgetSidecarAttemptCount": validity_attempts,
        "maxBudgetSidecarValidRate": validity_rate,
        "budgets": budgets,
        "gainRatiosVsEight": ratios,
        "coverageSufficient": sufficient,
        "prerequisiteGates": prerequisite,
        "selectedAttemptsPer2DRoute": selected,
        "decision": decision,
        "interpretation": (
            "Select the smallest nested 2-D sidecar prefix that retains at least 90% of the k=8 pooled archive, pooled delivery, pooled dispersion, and each route's own archive/delivery gain while keeping route-level archive, delivery, and dispersion non-negative. This is mechanical compute evidence only."
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
