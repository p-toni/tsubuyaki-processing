#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

MASTER_SEEDS = (
    746003, 746019, 746037, 746053, 746071,
    746089, 746107, 746127, 746149, 746167,
    746181, 746199, 746223, 746239, 746257,
    746277, 746293, 746311, 746331, 746349,
)
ROUTES = ("recurrence", "orbit", "filament")
EXPECTED_CELLS_PER_SEED = 45
BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 746555001
DELIVERY_MARGIN = 0.003255297955511336


def _mean(values) -> float:
    values = list(values)
    if not values:
        raise AssertionError("empty mean")
    return statistics.fmean(values)


def _seed_effects(cells: list[dict], field: str) -> list[float]:
    by_seed = defaultdict(list)
    for c in cells:
        by_seed[int(c["masterSeed"])].append(float(c[field]))
    if set(by_seed) != set(MASTER_SEEDS):
        raise AssertionError("seed set drift in aggregate")
    return [_mean(by_seed[s]) for s in MASTER_SEEDS]


def _bootstrap_lower(seed_effects: list[float]) -> float:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(seed_effects)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        draws.append(_mean(seed_effects[rng.randrange(n)] for _ in range(n)))
    draws.sort()
    return float(draws[int(0.05 * BOOTSTRAP_DRAWS)])


def _route_means(cells: list[dict], field: str) -> dict:
    out = {}
    for route in ROUTES:
        vals = [float(c[field]) for c in cells if c["route"] == route]
        if len(vals) != len(MASTER_SEEDS) * 15:
            raise AssertionError(f"route cell count drift for {route}: {len(vals)}")
        out[route] = _mean(vals)
    return out


def aggregate(input_dir: Path) -> dict:
    records = []
    for seed in MASTER_SEEDS:
        path = input_dir / f"seed-{seed}.json"
        if not path.exists():
            raise AssertionError(f"missing seed artifact {path}")
        x = json.loads(path.read_text())
        if x["masterSeed"] != seed or x["smoke"] is not False:
            raise AssertionError(f"seed identity drift for {seed}")
        if not all(x["hardInvariants"].values()):
            raise AssertionError(f"hard invariant failure for {seed}")
        if len(x["cells"]) != EXPECTED_CELLS_PER_SEED:
            raise AssertionError(f"cell count drift for {seed}")
        records.append(x)

    cells = [c for x in records for c in x["cells"]]
    if len(cells) != len(MASTER_SEEDS) * EXPECTED_CELLS_PER_SEED:
        raise AssertionError("complete rectangle missing")

    route_seed_count = len(MASTER_SEEDS) * len(ROUTES)
    actual_keys = {(int(c["masterSeed"]), c["route"], c["targetId"]) for c in cells}
    if len(actual_keys) != len(cells):
        raise AssertionError("duplicate seed-route-target cells")
    if len(actual_keys) != 900:
        raise AssertionError(f"unexpected unique cell count: {len(actual_keys)}")

    archive_seed = _seed_effects(cells, "restartMinusLocalArchive")
    delivery_seed = _seed_effects(cells, "restartMinusLocalDelivery")
    restart_baseline_delivery_seed = _seed_effects(cells, "restartMinusBaselineDelivery")

    mean_archive = _mean(archive_seed)
    lower_archive = _bootstrap_lower(archive_seed)
    mean_delivery = _mean(delivery_seed)
    lower_delivery = _bootstrap_lower(delivery_seed)
    lower_restart_baseline_delivery = _bootstrap_lower(restart_baseline_delivery_seed)

    local_marginal = _mean(float(c["localMarginalArchiveGain"]) for c in cells)
    restart_marginal = _mean(float(c["restartMarginalArchiveGain"]) for c in cells)

    route_archive = _route_means(cells, "restartMinusLocalArchive")
    route_delivery = _route_means(cells, "restartMinusLocalDelivery")
    route_restart_baseline_delivery = _route_means(cells, "restartMinusBaselineDelivery")

    local_valid = sum(
        int(x["routes"][r]["deepLocal24"]["validExtraCount"])
        for x in records for r in ROUTES
    )
    restart_valid = sum(
        int(x["routes"][r]["independentStarts24"]["validExtraCount"])
        for x in records for r in ROUTES
    )
    marginal_attempts = route_seed_count * 4

    gates = {
        "archiveMeanRestartMinusLocalPositive": mean_archive > 0.0,
        "archive95LowerRestartMinusLocalPositive": lower_archive > 0.0,
        "everyRouteArchiveRestartMinusLocalPositive": all(v > 0.0 for v in route_archive.values()),
        "restartMarginalArchiveGainAboveLocal": restart_marginal > local_marginal,
        "deliveryMeanRestartMinusLocalAboveNegativeMargin": mean_delivery > -DELIVERY_MARGIN,
        "delivery95LowerRestartMinusLocalAboveNegativeMargin": lower_delivery > -DELIVERY_MARGIN,
        "everyRouteDeliveryRestartMinusLocalAboveNegativeMargin": all(
            v > -DELIVERY_MARGIN for v in route_delivery.values()
        ),
        "delivery95LowerRestartMinusBaselineAboveNegativeMargin": (
            lower_restart_baseline_delivery > -DELIVERY_MARGIN
        ),
        "everyRouteDeliveryRestartMinusBaselineAboveNegativeMargin": all(
            v > -DELIVERY_MARGIN for v in route_restart_baseline_delivery.values()
        ),
    }
    passed = all(gates.values())

    return {
        "version": 1,
        "decision": (
            "INDEPENDENT_STARTS_SCREEN_PROMISING"
            if passed else "INDEPENDENT_STARTS_SCREEN_NOT_PROMISING"
        ),
        "artisticEvidence": False,
        "authority": "mechanical-structural-marginal-screen-only",
        "seedCount": len(MASTER_SEEDS),
        "routeSeedCount": route_seed_count,
        "cellCount": len(cells),
        "marginalEvaluationsPerArm": 4,
        "deliveryNonInferiorityMargin": DELIVERY_MARGIN,
        "meanRestartMinusLocalArchive": mean_archive,
        "oneSided95BootstrapLowerRestartMinusLocalArchive": lower_archive,
        "meanLocalMarginalArchiveGain": local_marginal,
        "meanRestartMarginalArchiveGain": restart_marginal,
        "meanRestartMinusLocalDelivery": mean_delivery,
        "oneSided95BootstrapLowerRestartMinusLocalDelivery": lower_delivery,
        "meanRestartMinusBaselineDelivery": _mean(restart_baseline_delivery_seed),
        "oneSided95BootstrapLowerRestartMinusBaselineDelivery": lower_restart_baseline_delivery,
        "routeMeanEffects": {
            "restartMinusLocalArchive": route_archive,
            "restartMinusLocalDelivery": route_delivery,
            "restartMinusBaselineDelivery": route_restart_baseline_delivery,
        },
        "marginalValidity": {
            "deepLocalValidCount": local_valid,
            "independentRestartValidCount": restart_valid,
            "attemptsPerArm": marginal_attempts,
            "deepLocalValidRate": local_valid / marginal_attempts,
            "independentRestartValidRate": restart_valid / marginal_attempts,
        },
        "gates": gates,
        "screenPassed": passed,
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 45 paired route-target cells",
        },
        "interpretation": (
            "Independent one-shot route-prior starts beat four additional local mutations "
            "robustly enough at the marginal 24-candidate screen, while the promoted delivery "
            "surface remains inside the frozen non-inferiority margin. Authorize one fresh "
            "equal-20-budget substitution experiment; do not choose replaced attempts from "
            "consumed 746xxx evidence."
            if passed else
            "Independent one-shot route-prior starts did not satisfy the preregistered "
            "marginal archive-and-delivery screen against four additional local mutations. "
            "Stop this exact four-vs-four marginal policy and do not tune it on consumed "
            "746xxx evidence."
        ),
    }


def main() -> None:
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
