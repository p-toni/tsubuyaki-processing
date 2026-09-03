#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

MASTER_SEEDS = (
    762003, 762019, 762037, 762053, 762071,
    762089, 762107, 762127, 762149, 762167,
    762181, 762199, 762223, 762239, 762257,
    762277, 762293, 762311, 762331, 762349,
)
BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 762555001
MEANINGFUL_BAR = 0.005
VALIDITY_FLOOR = 0.95
LEVERAGE_RETENTION = 0.90
MAX_LAW_FAILURE_FRACTION = 0.25
MAX_TARGET_FAMILY_SHARE = 0.50
LAW_FAILURE = "shared family law loses sibling-scale coherence"


def _mean(xs):
    return statistics.fmean(xs) if xs else 0.0


def _bootstrap_lower(seed_values: list[float], rng: random.Random) -> float:
    n = len(seed_values)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        draws.append(_mean([seed_values[rng.randrange(n)] for _ in range(n)]))
    draws.sort()
    return draws[int(0.05 * (len(draws) - 1))]


def _family_share(cells: list[dict], key: str) -> tuple[dict[str, float], float]:
    positive = defaultdict(float)
    for cell in cells:
        delta = float(cell[key])
        if delta > 0:
            positive[cell["targetFamily"]] += delta
    total = sum(positive.values())
    shares = {
        family: value / total if total > 0 else 0.0
        for family, value in sorted(positive.items())
    }
    return shares, max(shares.values(), default=0.0)


def aggregate(input_dir: Path) -> dict:
    records = [json.loads(p.read_text()) for p in sorted(input_dir.glob("seed-*.json"))]
    seeds = sorted(int(r["masterSeed"]) for r in records)
    if seeds != sorted(MASTER_SEEDS):
        raise AssertionError(f"incomplete/unexpected seed rectangle: {seeds}")
    if not all(r["smoke"] is False and all(r["hardInvariants"].values()) for r in records):
        raise AssertionError("authoritative record failed hard invariant")
    if not all(len(r["cells"]) == 15 for r in records):
        raise AssertionError("authoritative target cell count drift")

    cells = [cell for record in records for cell in record["cells"]]
    generic_valid = sum(int(r["diagnostics"]["genericValid"]) for r in records)
    projected_valid = sum(int(r["diagnostics"]["projectedValid"]) for r in records)
    attempts = len(records) * 12
    generic_law_failures = sum(int(r["diagnostics"]["genericLawFailures"]) for r in records)
    projected_law_failures = sum(int(r["diagnostics"]["projectedLawFailures"]) for r in records)

    generic_seed_delta = []
    projected_seed_delta = []
    for record in records:
        generic_seed_delta.append(_mean([
            float(c["genericDeltaVsNative"]) for c in record["cells"]
        ]))
        projected_seed_delta.append(_mean([
            float(c["projectedDeltaVsNative"]) for c in record["cells"]
        ]))

    rng = random.Random(BOOTSTRAP_SEED)
    generic_delta = _mean([float(c["genericDeltaVsNative"]) for c in cells])
    projected_delta = _mean([float(c["projectedDeltaVsNative"]) for c in cells])
    generic_lower = _bootstrap_lower(generic_seed_delta, rng)
    projected_lower = _bootstrap_lower(projected_seed_delta, rng)

    families = sorted({c["targetFamily"] for c in cells})
    generic_family_means = {
        family: _mean([
            float(c["genericDeltaVsNative"])
            for c in cells if c["targetFamily"] == family
        ])
        for family in families
    }
    projected_family_means = {
        family: _mean([
            float(c["projectedDeltaVsNative"])
            for c in cells if c["targetFamily"] == family
        ])
        for family in families
    }

    generic_wins = sum(float(c["genericDeltaVsNative"]) > MEANINGFUL_BAR for c in cells)
    generic_losses = sum(float(c["genericDeltaVsNative"]) < -MEANINGFUL_BAR for c in cells)
    projected_wins = sum(float(c["projectedDeltaVsNative"]) > MEANINGFUL_BAR for c in cells)
    projected_losses = sum(float(c["projectedDeltaVsNative"]) < -MEANINGFUL_BAR for c in cells)

    generic_added = _mean([float(c["genericAdded"]) for c in cells])
    projected_added = _mean([float(c["projectedAdded"]) for c in cells])
    native_added = _mean([float(c["nativeAdded"]) for c in cells])
    leverage_ratio = (
        projected_added / generic_added if generic_added > 1e-12 else None
    )

    generic_shares, generic_max_share = _family_share(cells, "genericDeltaVsNative")
    projected_shares, projected_max_share = _family_share(cells, "projectedDeltaVsNative")

    if generic_law_failures > 0:
        law_repair = projected_law_failures <= MAX_LAW_FAILURE_FRACTION * generic_law_failures
    else:
        law_repair = projected_law_failures == 0

    generic_gates = {
        "validityAtLeast95Pct": generic_valid / attempts >= VALIDITY_FLOOR,
        "deltaAtLeastMeaningfulBar": generic_delta >= MEANINGFUL_BAR,
        "oneSided95BootstrapLowerPositive": generic_lower > 0,
        "everyTargetFamilyMeanPositive": all(v > 0 for v in generic_family_means.values()),
        "meaningfulWinsExceedLosses": generic_wins > generic_losses,
    }
    projected_gates = {
        "validityAtLeast95Pct": projected_valid / attempts >= VALIDITY_FLOOR,
        "familyLawFailureReducedToQuarterOrZero": law_repair,
        "deltaAtLeastMeaningfulBar": projected_delta >= MEANINGFUL_BAR,
        "oneSided95BootstrapLowerPositive": projected_lower > 0,
        "everyTargetFamilyMeanPositive": all(v > 0 for v in projected_family_means.values()),
        "meaningfulWinsExceedLosses": projected_wins > projected_losses,
        "retainsAtLeast90PctGenericAddedRecovery": (
            leverage_ratio is None or leverage_ratio >= LEVERAGE_RETENTION
        ),
        "noTargetFamilyOverHalfPositiveAdvantage": projected_max_share <= MAX_TARGET_FAMILY_SHARE,
    }

    generic_supported = all(generic_gates.values())
    projected_supported = all(projected_gates.values())
    if generic_supported and projected_supported:
        decision = "FAMILY_SPECTRAL_GENERIC_AND_PROJECTED_MECHANICALLY_SUPPORTED"
    elif projected_supported:
        decision = "FAMILY_SPECTRAL_PROJECTION_MECHANICALLY_SUPPORTED"
    elif generic_supported:
        decision = "FAMILY_SPECTRAL_GENERIC_MECHANICALLY_SUPPORTED"
    else:
        decision = "FAMILY_SPECTRAL_NOT_SUPPORTED"

    return {
        "version": 1,
        "experiment": "family-spectral-projection-v1",
        "artisticEvidence": False,
        "authority": "mechanical-family-operator-only",
        "seedCount": len(records),
        "cellCount": len(cells),
        "challengerAttemptsPerArmPerSeed": 12,
        "meaningfulRecoveryBar": MEANINGFUL_BAR,
        "validityFloor": VALIDITY_FLOOR,
        "leverageRetentionFloor": LEVERAGE_RETENTION,
        "maxLawFailureFraction": MAX_LAW_FAILURE_FRACTION,
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 15 fresh target cells",
        },
        "nativeAddedRecoveryMean": native_added,
        "generic": {
            "valid": generic_valid,
            "attempts": attempts,
            "validRate": generic_valid / attempts,
            "familyLawFailures": generic_law_failures,
            "addedRecoveryMean": generic_added,
            "deltaVsNativeMean": generic_delta,
            "oneSided95BootstrapLower": generic_lower,
            "targetFamilyDeltaMeans": generic_family_means,
            "meaningfulWins": generic_wins,
            "meaningfulLosses": generic_losses,
            "positiveAdvantageShares": generic_shares,
            "maxPositiveAdvantageShare": generic_max_share,
            "gates": generic_gates,
            "supported": generic_supported,
        },
        "projected": {
            "valid": projected_valid,
            "attempts": attempts,
            "validRate": projected_valid / attempts,
            "familyLawFailures": projected_law_failures,
            "addedRecoveryMean": projected_added,
            "addedRecoveryRatioVsGeneric": leverage_ratio,
            "deltaVsNativeMean": projected_delta,
            "oneSided95BootstrapLower": projected_lower,
            "targetFamilyDeltaMeans": projected_family_means,
            "meaningfulWins": projected_wins,
            "meaningfulLosses": projected_losses,
            "positiveAdvantageShares": projected_shares,
            "maxPositiveAdvantageShare": projected_max_share,
            "gates": projected_gates,
            "supported": projected_supported,
        },
        "decision": decision,
        "interpretation": (
            "Fresh family-only causal test of the fixed K=2/amplitude-16 spectral operator. "
            "The projected treatment retains the generic pointwise warp but normalizes each "
            "warped sibling around its warped anchor to preserve its native terminal length. "
            "Mechanical support does not confer artistic or runtime-default authority."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    Path(args.output).write_text(
        json.dumps(aggregate(Path(args.input_dir)), indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
