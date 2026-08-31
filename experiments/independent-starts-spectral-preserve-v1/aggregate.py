#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

MASTER_SEEDS = (
    751003, 751019, 751037, 751053, 751071,
    751089, 751107, 751127, 751149, 751167,
    751181, 751199, 751223, 751239, 751257,
    751277, 751293, 751311, 751331, 751349,
)
ROUTES = ("recurrence", "orbit", "filament")
DRAWS = 50000
BOOTSTRAP_SEED = 751555001
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


def _bootstrap_lower(values):
    rng = random.Random(BOOTSTRAP_SEED)
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

    archive_seed = _seed_effects(cells, "archiveDelta")
    delivery_seed = _seed_effects(cells, "deliveryDelta")
    archive_mean = _mean(archive_seed)
    archive_lower = _bootstrap_lower(archive_seed)
    delivery_mean = _mean(delivery_seed)
    delivery_lower = _bootstrap_lower(delivery_seed)
    route_archive = _route_means(cells, "archiveDelta")
    route_delivery = _route_means(cells, "deliveryDelta")

    baseline_valid = sum(
        int(x["routes"][r]["baseline20"]["operatorDiagnostics"]["valid"])
        for x in records for r in ROUTES
    )
    treatment_valid = sum(
        int(x["routes"][r]["spectralPreserve20"]["validGenerated"])
        for x in records for r in ROUTES
    )
    attempts = len(MASTER_SEEDS) * len(ROUTES) * 20
    baseline_rate = baseline_valid / attempts
    treatment_rate = treatment_valid / attempts
    valid_restarts = sum(
        int(x["routes"][r]["spectralPreserve20"]["validRestarts"])
        for x in records for r in ROUTES
    )

    gates = {
        "archiveMeanAboveMeaningfulMargin": archive_mean > MEANINGFUL_MARGIN,
        "archive95LowerPositive": archive_lower > 0.0,
        "everyRouteArchivePositive": all(v > 0.0 for v in route_archive.values()),
        "deliveryMeanAboveMeaningfulMargin": delivery_mean > MEANINGFUL_MARGIN,
        "delivery95LowerPositive": delivery_lower > 0.0,
        "everyRouteDeliveryPositive": all(v > 0.0 for v in route_delivery.values()),
        "treatmentValidityNoMoreThanFivePointsLower": treatment_rate >= baseline_rate - 0.05,
    }
    passed = all(gates.values())

    return {
        "version": 1,
        "decision": (
            "SPECTRAL_PRESERVE_RESTART_PROMISING"
            if passed else
            "SPECTRAL_PRESERVE_RESTART_NOT_PROMISING"
        ),
        "artisticEvidence": False,
        "authority": "mechanical-structural-equal-budget-only",
        "seedCount": len(MASTER_SEEDS),
        "routeSeedCount": len(MASTER_SEEDS) * len(ROUTES),
        "cellCount": len(cells),
        "budgetPerArm": 20,
        "baselinePortfolio": {"native": 10, "spectral": 10, "restart": 0},
        "treatmentPortfolio": {"native": 6, "spectral": 10, "restart": 4},
        "replacedBaselineAttempts": ["R3", "R4", "R5", "R6"],
        "exactlyReplayedBaselineSpectralAttempts": ["R10", "R11", "R12"],
        "meaningfulEffectMargin": MEANINGFUL_MARGIN,
        "meanArchiveDelta": archive_mean,
        "oneSided95BootstrapLowerArchiveDelta": archive_lower,
        "meanDeliveryDelta": delivery_mean,
        "oneSided95BootstrapLowerDeliveryDelta": delivery_lower,
        "routeMeanEffects": {
            "archiveDelta": route_archive,
            "deliveryDelta": route_delivery,
        },
        "validity": {
            "baselineValidCount": baseline_valid,
            "treatmentValidCount": treatment_valid,
            "attemptsPerArm": attempts,
            "baselineValidRate": baseline_rate,
            "treatmentValidRate": treatment_rate,
            "treatmentMinusBaselineValidRate": treatment_rate - baseline_rate,
            "validRestartCount": valid_restarts,
            "restartAttemptCount": len(MASTER_SEEDS) * len(ROUTES) * 4,
        },
        "gates": gates,
        "mechanicalPassed": passed,
        "bootstrap": {
            "draws": DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 45 paired route-target cells",
        },
        "researchLineStatus": (
            "FRESH_BLINDED_ARTISTIC_COMPARISON_AUTHORIZED"
            if passed else
            "SPECTRAL_PRESERVE_NATIVE_SWAP_STOPPED"
        ),
        "interpretation": (
            "Preserving all ten spectral evaluations while replacing four native refine attempts with independent one-shot starts clears the fresh equal-budget mechanical gate. This closes the strongest #112 operator-deletion confound and authorizes one fresh blinded artistic comparison only; production remains unchanged until that boundary passes."
            if passed else
            "Preserving the full spectral budget does not rescue the independent-start substitution under the frozen archive, delivery, and validity gates. Stop this exact native-swap integration and move to the separately preregistered restart-cultivation loophole rather than tuning positions or ratios on 751xxx."
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
