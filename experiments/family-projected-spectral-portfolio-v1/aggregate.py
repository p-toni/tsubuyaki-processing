#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

MASTER_SEEDS = (
    763003, 763019, 763037, 763053, 763071,
    763089, 763107, 763127, 763149, 763167,
    763181, 763199, 763223, 763239, 763257,
    763277, 763293, 763311, 763331, 763349,
)
FAMILIES = (
    "disconnected-loops",
    "nested-loops",
    "concave-loops",
    "open-networks",
    "dense-regions",
)
BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 763555001
MEANINGFUL_BAR = 0.005
VALIDITY_FLOOR = 0.95
VALIDITY_NONINFERIORITY_MARGIN = 0.05
MAX_TARGET_FAMILY_SHARE = 0.50
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
    seeds = sorted(int(r["masterSeed"]) for r in records)
    if seeds != sorted(MASTER_SEEDS):
        raise AssertionError(f"incomplete or unexpected seed rectangle: {seeds}")
    if not all(r["smoke"] is False and all(r["hardInvariants"].values()) for r in records):
        raise AssertionError("authoritative record failed hard invariant")
    if not all(len(r["cells"]) == 15 for r in records):
        raise AssertionError("authoritative target cell count drift")

    settings = records[0]["settings"]
    if any(r["settings"] != settings for r in records[1:]):
        raise AssertionError("settings drift")
    if settings["route"] != "family":
        raise AssertionError("route drift")
    if settings["totalChallengersPerArm"] != 12:
        raise AssertionError("total budget drift")
    if settings["baselineNativePerStart"] != 6:
        raise AssertionError("baseline native budget drift")
    if settings["mixedNativePerStart"] != 3 or settings["mixedProjectedSpectralPerStart"] != 3:
        raise AssertionError("mixed portfolio split drift")
    if float(settings["spectralAmplitude"]) != 16.0 or int(settings["fieldBandwidth"]) != 2:
        raise AssertionError("projected spectral operator drift")

    cells = [c for record in records for c in record["cells"]]
    if len(cells) != len(MASTER_SEEDS) * 15:
        raise AssertionError("aggregate rectangle incomplete")
    if Counter(c["targetFamily"] for c in records[0]["cells"]) != Counter({f: 3 for f in FAMILIES}):
        raise AssertionError("target-family rectangle drift")

    by_seed = defaultdict(list)
    by_family = defaultdict(list)
    deltas = []
    baseline_added = []
    mixed_added = []
    for c in cells:
        d = float(c["delta"])
        deltas.append(d)
        baseline_added.append(float(c["baselineAdded"]))
        mixed_added.append(float(c["mixedAdded"]))
        by_seed[int(c["masterSeed"])].append(d)
        by_family[c["targetFamily"]].append(d)

    seed_means = {str(s): _mean(by_seed[s]) for s in MASTER_SEEDS}
    seed_values = [seed_means[str(s)] for s in MASTER_SEEDS]
    rng = random.Random(BOOTSTRAP_SEED)
    lower = _bootstrap_lower(seed_values, rng)
    mean_delta = _mean(seed_values)

    family_means = {f: _mean(by_family[f]) for f in FAMILIES}
    leave_one_family_out = {
        f: _mean([float(c["delta"]) for c in cells if c["targetFamily"] != f])
        for f in FAMILIES
    }
    wins = sum(d > MEANINGFUL_BAR for d in deltas)
    losses = sum(d < -MEANINGFUL_BAR for d in deltas)

    baseline_attempts = baseline_valid = 0
    mixed_native_attempts = mixed_native_valid = 0
    projected_attempts = projected_valid = 0
    projected_law_failures = 0
    failures = Counter()
    for record in records:
        diag = record["diagnostics"]
        baseline_attempts += int(diag["baselineNativeAttempts"])
        baseline_valid += int(diag["baselineNativeValid"])
        mixed_native_attempts += int(diag["mixedNativeAttempts"])
        mixed_native_valid += int(diag["mixedNativeValid"])
        projected_attempts += int(diag["mixedProjectedAttempts"])
        projected_valid += int(diag["mixedProjectedValid"])
        projected_law_failures += int(diag["mixedProjectedLawFailures"])
        failures.update(diag.get("mixedProjectedFailureModes", []))

    baseline_valid_rate = baseline_valid / baseline_attempts
    projected_valid_rate = projected_valid / projected_attempts
    mixed_attempts = mixed_native_attempts + projected_attempts
    mixed_valid = mixed_native_valid + projected_valid
    mixed_valid_rate = mixed_valid / mixed_attempts

    positive_by_family = {
        f: sum(max(0.0, float(c["delta"])) for c in cells if c["targetFamily"] == f)
        for f in FAMILIES
    }
    total_positive = sum(positive_by_family.values())
    shares = {
        f: (v / total_positive if total_positive > EPS else 0.0)
        for f, v in positive_by_family.items()
    }
    max_share = max(shares.values(), default=1.0)

    gates = {
        "completeHardInvariantRectangle": True,
        "meanDeltaAtLeast005": mean_delta >= MEANINGFUL_BAR,
        "masterSeedBootstrapLower95Positive": lower > 0.0,
        "everyTargetFamilyMeanPositive": all(v > 0 for v in family_means.values()),
        "everyLeaveOneTargetFamilyOutMeanPositive": all(v > 0 for v in leave_one_family_out.values()),
        "meaningfulWinsExceedLosses": wins > losses,
        "projectedSpectralValidityAtLeast95Pct": projected_valid_rate >= VALIDITY_FLOOR,
        "projectedSiblingScaleLawFailuresZero": projected_law_failures == 0,
        "mixedValidityWithin5ppOfBaseline": mixed_valid_rate >= baseline_valid_rate - VALIDITY_NONINFERIORITY_MARGIN,
        "positiveAdvantageNotFamilyConcentrated": total_positive > EPS and max_share <= MAX_TARGET_FAMILY_SHARE,
    }
    decision = (
        "FAMILY_PROJECTED_SPECTRAL_PORTFOLIO_PROMISING"
        if all(gates.values())
        else "FAMILY_PROJECTED_SPECTRAL_PORTFOLIO_NOT_PROMISING"
    )

    return {
        "version": 1,
        "experiment": "family-projected-spectral-portfolio-v1",
        "artisticEvidence": False,
        "authority": "mechanical-family-portfolio-only",
        "decision": decision,
        "seedCount": len(records),
        "cellCount": len(cells),
        "meaningfulRecoveryBar": MEANINGFUL_BAR,
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "unit": "master-seed mean across 15 target cells",
        },
        "gates": gates,
        "deltaMean": mean_delta,
        "deltaOneSided95BootstrapLower": lower,
        "masterSeedDelta": seed_means,
        "targetFamilyDeltaMeans": family_means,
        "leaveOneTargetFamilyOutDeltaMeans": leave_one_family_out,
        "meaningfulWins": wins,
        "meaningfulLosses": losses,
        "addedRecovery": {
            "nativeOnlyMean": _mean(baseline_added),
            "mixedMean": _mean(mixed_added),
        },
        "validity": {
            "baselineNativeValid": baseline_valid,
            "baselineNativeAttempts": baseline_attempts,
            "baselineNativeRate": baseline_valid_rate,
            "mixedNativeValid": mixed_native_valid,
            "mixedNativeAttempts": mixed_native_attempts,
            "projectedSpectralValid": projected_valid,
            "projectedSpectralAttempts": projected_attempts,
            "projectedSpectralRate": projected_valid_rate,
            "mixedTotalValid": mixed_valid,
            "mixedTotalAttempts": mixed_attempts,
            "mixedTotalRate": mixed_valid_rate,
            "projectedSiblingScaleLawFailures": projected_law_failures,
            "projectedFailureModes": dict(failures),
        },
        "positiveAdvantageConcentration": {
            "byFamily": positive_by_family,
            "shareByFamily": shares,
            "maxFamilyShare": max_share,
        },
        "settings": settings,
        "interpretation": (
            "Equal-budget family-only portfolio test: 12 native attempts versus an exact six-native-prefix plus six family-law projected spectral attempts. Mechanical support only authorizes an opt-in runtime implementation plus fresh replay; it does not confer artistic authority."
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
