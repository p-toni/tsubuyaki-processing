#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from run_stop import MASTER_SEEDS, NONINFERIORITY_MARGIN, ROUTES

BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 744555001


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


def _bootstrap_upper(seed_effects):
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(seed_effects)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        draws.append(_mean([seed_effects[rng.randrange(n)] for _ in range(n)]))
    return _percentile(draws, 0.95)


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

    seed_delivery_loss = []
    seed_archive_loss = []
    route_delivery = defaultdict(list)
    route_archive = defaultdict(list)
    attempts_saved = []
    stop_attempts = []
    valid_at_stop = []
    early_stops = 0
    route_early = defaultdict(int)
    cells = []

    for x in rows:
        if len(x["cells"]) != 45:
            raise AssertionError(f"seed {x['masterSeed']} has wrong cell count")
        dloss = [float(c["deliveryLoss"]) for c in x["cells"]]
        aloss = [float(c["archiveLoss"]) for c in x["cells"]]
        seed_delivery_loss.append(_mean(dloss))
        seed_archive_loss.append(_mean(aloss))
        cells.extend(x["cells"])
        for c in x["cells"]:
            route_delivery[str(c["route"])].append(float(c["deliveryLoss"]))
            route_archive[str(c["route"])].append(float(c["archiveLoss"]))
        for route in ROUTES:
            rec = x["routes"][route]
            saved = int(rec["attemptsSaved"])
            attempts_saved.append(saved)
            stop_attempts.append(int(rec["stopAttempt"]))
            valid_at_stop.append(int(rec["stoppedValidCount"]))
            if saved > 0:
                early_stops += 1
                route_early[route] += 1

    mean_delivery_loss = _mean(seed_delivery_loss)
    mean_archive_loss = _mean(seed_archive_loss)
    delivery_upper = _bootstrap_upper(seed_delivery_loss)
    archive_upper = _bootstrap_upper(seed_archive_loss)
    route_delivery_means = {route: _mean(route_delivery[route]) for route in ROUTES}
    route_archive_means = {route: _mean(route_archive[route]) for route in ROUTES}
    route_count = len(attempts_saved)
    early_rate = early_stops / route_count
    median_saved = statistics.median(attempts_saved)

    gates = {
        "earlyStopRateAtLeastHalf": early_rate >= 0.5,
        "medianAttemptsSavedAtLeast3": median_saved >= 3,
        "meanDeliveryLossBelowMargin": mean_delivery_loss < NONINFERIORITY_MARGIN,
        "delivery95UpperBelowMargin": delivery_upper < NONINFERIORITY_MARGIN,
        "meanArchiveLossBelowMargin": mean_archive_loss < NONINFERIORITY_MARGIN,
        "archive95UpperBelowMargin": archive_upper < NONINFERIORITY_MARGIN,
        "everyRouteMeanDeliveryLossBelowMargin": all(v < NONINFERIORITY_MARGIN for v in route_delivery_means.values()),
        "everyRouteMeanArchiveLossBelowMargin": all(v < NONINFERIORITY_MARGIN for v in route_archive_means.values()),
    }
    passed = all(gates.values())

    return {
        "version": 1,
        "decision": "SATURATION_STOP_PROMISING" if passed else "SATURATION_STOP_NOT_PROMISING",
        "artisticEvidence": False,
        "seedCount": len(rows),
        "routeSeedCount": route_count,
        "cellCount": len(cells),
        "noninferiorityMargin": NONINFERIORITY_MARGIN,
        "earlyStopCount": early_stops,
        "earlyStopRate": early_rate,
        "medianAttemptsSaved": median_saved,
        "meanAttemptsSaved": _mean(attempts_saved),
        "medianStopAttempt": statistics.median(stop_attempts),
        "meanStopAttempt": _mean(stop_attempts),
        "medianValidAtStop": statistics.median(valid_at_stop),
        "meanDeliveryLoss": mean_delivery_loss,
        "oneSided95BootstrapUpperDeliveryLoss": delivery_upper,
        "meanArchiveLoss": mean_archive_loss,
        "oneSided95BootstrapUpperArchiveLoss": archive_upper,
        "routeMeanDeliveryLoss": route_delivery_means,
        "routeMeanArchiveLoss": route_archive_means,
        "routeEarlyStopCount": {route: route_early[route] for route in ROUTES},
        "attemptSavingsDistribution": {
            str(v): attempts_saved.count(v) for v in sorted(set(attempts_saved))
        },
        "seedEffects": [
            {
                "masterSeed": seed,
                "meanDeliveryLoss": dloss,
                "meanArchiveLoss": aloss,
            }
            for seed, dloss, aloss in zip(sorted(MASTER_SEEDS), seed_delivery_loss, seed_archive_loss)
        ],
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 45 paired route-target cells",
        },
        "gates": gates,
        "saturationStopPassed": passed,
        "authority": "mechanical-structural-noninferiority-only",
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
