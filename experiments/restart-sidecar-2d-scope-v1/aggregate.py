#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROUTES = ("family", "sheet")
MASTER_SEEDS = (
    760003, 760019, 760037, 760053, 760071,
    760089, 760107, 760127, 760149, 760167,
    760181, 760199, 760223, 760239, 760257,
    760277, 760293, 760311, 760331, 760349,
)
BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 760555001
MEANINGFUL_EFFECT_BAR = 0.003255297955511336


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

    seed_archive = []
    seed_delivery = []
    seed_dispersion = []
    route_archive = defaultdict(list)
    route_delivery = defaultdict(list)
    route_dispersion = defaultdict(list)
    validity_attempts = 0
    validity_valid = 0
    distinct_added = []

    for record in records:
        if tuple(record["settings"]["routes"]) != ROUTES:
            raise AssertionError("route settings drift")
        if len(record["cells"]) != 30:
            raise AssertionError(f"seed {record['masterSeed']} cell count drift")

        archive_vals = []
        delivery_vals = []
        for cell in record["cells"]:
            route = cell["route"]
            a = float(cell["archiveDelta"])
            d = float(cell["deliveryDelta"])
            archive_vals.append(a)
            delivery_vals.append(d)
            route_archive[route].append(a)
            route_delivery[route].append(d)

        dispersion_vals = []
        for route in ROUTES:
            rr = record["routes"][route]
            validity_attempts += int(rr["sidecarAttempted"])
            validity_valid += int(rr["sidecarValid"])
            distinct_added.append(float(rr["distinctValidPhenotypesAddedVsBaseline"]))
            delta = (
                float(rr["unionDispersion"]["minimumPairwiseDistance"])
                - float(rr["baselineDispersion"]["minimumPairwiseDistance"])
            )
            dispersion_vals.append(delta)
            route_dispersion[route].append(delta)

        seed_archive.append(_mean(archive_vals))
        seed_delivery.append(_mean(delivery_vals))
        seed_dispersion.append(_mean(dispersion_vals))

    rng = random.Random(BOOTSTRAP_SEED)
    archive_mean = _mean(seed_archive)
    archive_lower = _bootstrap_lower(seed_archive, rng)
    delivery_mean = _mean(seed_delivery)
    delivery_lower = _bootstrap_lower(seed_delivery, rng)
    dispersion_mean = _mean(seed_dispersion)
    validity_rate = validity_valid / validity_attempts

    route_archive_means = {r: _mean(route_archive[r]) for r in ROUTES}
    route_delivery_means = {r: _mean(route_delivery[r]) for r in ROUTES}
    route_dispersion_means = {r: _mean(route_dispersion[r]) for r in ROUTES}

    gates = {
        "sidecarValidityAtLeast95Pct": validity_rate >= 0.95,
        "archiveMeanAboveHistoricalMeaningfulEffectBar": archive_mean > MEANINGFUL_EFFECT_BAR,
        "archiveOneSided95BootstrapLowerPositive": archive_lower > 0,
        "deliveryMeanAboveHistoricalMeaningfulEffectBar": delivery_mean > MEANINGFUL_EFFECT_BAR,
        "deliveryOneSided95BootstrapLowerPositive": delivery_lower > 0,
        "minimumPairwiseDispersionMeanPositive": dispersion_mean > 0,
        "everyRouteArchiveMeanPositive": all(v > 0 for v in route_archive_means.values()),
        "everyRouteDeliveryMeanPositive": all(v > 0 for v in route_delivery_means.values()),
    }
    decision = (
        "SIDECAR_2D_SCOPE_MECHANICALLY_SUPPORTED"
        if all(gates.values())
        else "SIDECAR_2D_SCOPE_NOT_SUPPORTED"
    )

    return {
        "version": 1,
        "experiment": "restart-sidecar-2d-scope-v1",
        "artisticEvidence": False,
        "authority": "mechanical-route-scope-only",
        "seedCount": len(records),
        "routeSeedCount": len(records) * len(ROUTES),
        "sidecarAttemptsPerRoute": 8,
        "historicalMeaningfulEffectBar": MEANINGFUL_EFFECT_BAR,
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed equal-route mean",
        },
        "sidecarValidCount": validity_valid,
        "sidecarAttemptCount": validity_attempts,
        "sidecarValidRate": validity_rate,
        "archiveDeltaMean": archive_mean,
        "archiveDeltaOneSided95BootstrapLower": archive_lower,
        "deliveryDeltaMean": delivery_mean,
        "deliveryDeltaOneSided95BootstrapLower": delivery_lower,
        "minimumPairwiseDispersionDeltaMean": dispersion_mean,
        "distinctValidPhenotypesAddedMeanPerRouteSeed": _mean(distinct_added),
        "routeArchiveDeltaMeans": route_archive_means,
        "routeDeliveryDeltaMeans": route_delivery_means,
        "routeMinimumPairwiseDispersionDeltaMeans": route_dispersion_means,
        "gates": gates,
        "decision": decision,
        "interpretation": (
            "A positive decision supports expanding only the opt-in exploratory restart-sidecar route authority to family and sheet. It does not provide artistic authority, enable the sidecar by default, permit baseline parenting, or permit automatic delivery replacement. A negative decision leaves the existing route authority unchanged and stops this exact scope hypothesis."
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
