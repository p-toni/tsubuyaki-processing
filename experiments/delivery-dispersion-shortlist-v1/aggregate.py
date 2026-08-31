#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from run_shortlist import MASTER_SEEDS, ROUTES

BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 742555001


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

    seed_effects = []
    route_cells = defaultdict(list)
    distance_lifts = []
    quantile_regrets = []
    dispersion_regrets = []
    cells = []

    for x in rows:
        if len(x["cells"]) != 45:
            raise AssertionError(f"seed {x['masterSeed']} has wrong cell count")
        deltas = [float(c["delta"]) for c in x["cells"]]
        seed_effects.append(_mean(deltas))
        cells.extend(x["cells"])
        for c in x["cells"]:
            route_cells[str(c["route"])].append(float(c["delta"]))
            quantile_regrets.append(float(c["quantileRegret"]))
            dispersion_regrets.append(float(c["dispersionRegret"]))
        for route in ROUTES:
            distance_lifts.append(float(x["routes"][route]["minimumPairwiseDistanceLift"]))

    mean_effect = _mean(seed_effects)
    lower = _bootstrap_lower(seed_effects)
    route_means = {route: _mean(route_cells[route]) for route in ROUTES}

    gates = {
        "meanSeedEffectPositive": mean_effect > 0.0,
        "oneSided95BootstrapLowerPositive": lower > 0.0,
        "everyRouteMeanPositive": all(v > 0.0 for v in route_means.values()),
    }
    passed = all(gates.values())

    return {
        "version": 1,
        "decision": "DISPERSION_SHORTLIST_PROMISING" if passed else "DISPERSION_SHORTLIST_NOT_PROMISING",
        "artisticEvidence": False,
        "seedCount": len(rows),
        "cellCount": len(cells),
        "meanSeedEffect": mean_effect,
        "oneSided95BootstrapLower": lower,
        "routeMeanEffects": route_means,
        "meanQuantileFullArchiveRegret": _mean(quantile_regrets),
        "meanDispersionFullArchiveRegret": _mean(dispersion_regrets),
        "dispersionMinusQuantileMeanRegret": _mean(dispersion_regrets) - _mean(quantile_regrets),
        "medianMinimumPairwiseDistanceLift": statistics.median(distance_lifts),
        "minimumPairwiseDistanceLiftMin": min(distance_lifts),
        "routeSeedCountWithStrictDistanceLift": sum(v > 1e-15 for v in distance_lifts),
        "routeSeedCount": len(distance_lifts),
        "seedEffects": [
            {"masterSeed": seed, "meanDelta": effect}
            for seed, effect in zip(sorted(MASTER_SEEDS), seed_effects)
        ],
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 45 paired route-target cells",
        },
        "gates": gates,
        "dispersionShortlistPassed": passed,
        "authority": "mechanical-structural-benchmark-only",
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
