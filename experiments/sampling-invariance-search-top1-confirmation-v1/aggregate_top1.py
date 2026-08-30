from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from run_top1 import CONFIRMATION_SEEDS, MEANINGFUL_MARGIN

EXPECTED_SEEDS = tuple(CONFIRMATION_SEEDS)
EXPECTED_FAMILIES = (
    "concave-loops",
    "dense-regions",
    "disconnected-loops",
    "nested-loops",
    "open-networks",
)
T_CRITICAL_ONE_SIDED_95_DF23 = 1.713871527747048


def _stats(values: list[float]) -> dict:
    if not values:
        raise ValueError("empty statistic")
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def _load(results_dir: Path) -> list[dict]:
    records = []
    for path in sorted(results_dir.glob("seed-*.json")):
        records.append(json.loads(path.read_text()))
    return records


def reduce(records: list[dict]) -> dict:
    seeds = sorted(record["seed"] for record in records)
    settings_serialized = {json.dumps(record["settings"], sort_keys=True) for record in records}
    target_suites = {json.dumps(record["targetSuite"], sort_keys=True) for record in records}

    hard = {
        "completeSeedRectangle": tuple(seeds) == EXPECTED_SEEDS,
        "allBlockHardInvariants": len(records) == len(EXPECTED_SEEDS)
        and all(all(record["hardInvariants"].values()) for record in records),
        "identicalSettings": len(settings_serialized) == 1,
        "identicalTargetSuite": len(target_suites) == 1,
    }

    rows = []
    for record in records:
        for target in record["targets"]:
            rows.append(
                {
                    "seed": record["seed"],
                    "target": target["target"],
                    "family": target["family"],
                    "effect": float(target["effects"]["top1VsBreadth"]),
                    "meaningful": bool(target["effects"]["top1MeaningfulVsBreadth"]),
                    "exploitValidYield": float(target["policies"]["hybrid-top1"]["exploitValidYield"]),
                    "top1UniquePhenotypeRate": float(target["policies"]["hybrid-top1"]["uniquePhenotypeRate"]),
                    "breadthTailValidYield": float(target["policies"]["breadth-20"]["tailValidYield"]),
                    "acceptedImprovements": float(target["policies"]["hybrid-top1"]["acceptedImprovements"]),
                }
            )

    hard["completeCellRectangle"] = len(rows) == len(EXPECTED_SEEDS) * 15
    families = sorted({row["family"] for row in rows})
    hard["exactFamilyRectangle"] = tuple(families) == EXPECTED_FAMILIES and all(
        sum(1 for row in rows if row["family"] == family) == len(EXPECTED_SEEDS) * 3
        for family in EXPECTED_FAMILIES
    )

    effects = [row["effect"] for row in rows]
    seed_means = {
        seed: statistics.fmean(row["effect"] for row in rows if row["seed"] == seed)
        for seed in EXPECTED_SEEDS
    }
    seed_values = [seed_means[seed] for seed in EXPECTED_SEEDS]
    seed_stats = _stats(seed_values)
    seed_lcb = seed_stats["mean"] - T_CRITICAL_ONE_SIDED_95_DF23 * seed_stats["sd"] / math.sqrt(len(seed_values))

    family_diagnostics = {}
    positive_total = sum(max(0.0, value) for value in effects)
    for family in EXPECTED_FAMILIES:
        subset = [row for row in rows if row["family"] == family]
        vals = [row["effect"] for row in subset]
        positive = sum(max(0.0, value) for value in vals)
        family_diagnostics[family] = {
            "effect": _stats(vals),
            "meaningfulFraction": statistics.fmean(1.0 if row["meaningful"] else 0.0 for row in subset),
            "positiveContributionShare": positive / positive_total if positive_total > 0.0 else 0.0,
        }

    loo = {}
    for omitted in EXPECTED_FAMILIES:
        vals = [row["effect"] for row in rows if row["family"] != omitted]
        loo[omitted] = statistics.fmean(vals)

    meaningful_fraction = statistics.fmean(1.0 if row["meaningful"] else 0.0 for row in rows)
    exploit_valid_yield = statistics.fmean(row["exploitValidYield"] for row in rows)
    top1_unique_rate = statistics.fmean(row["top1UniquePhenotypeRate"] for row in rows)
    breadth_valid_yield = statistics.fmean(row["breadthTailValidYield"] for row in rows)
    largest_share = max(info["positiveContributionShare"] for info in family_diagnostics.values())

    gates = {
        "completeHardInvariantRectangle": all(hard.values()),
        "overallMeanPositive": statistics.fmean(effects) > 0.0,
        "masterSeedOneSided95LowerBoundPositive": seed_lcb > 0.0,
        "everyFamilyMeanPositive": all(info["effect"]["mean"] > 0.0 for info in family_diagnostics.values()),
        "everyLeaveOneFamilyOutMeanPositive": all(value > 0.0 for value in loo.values()),
        "meaningfulFractionAtLeast0p30": meaningful_fraction >= 0.30,
        "exploitValidYieldAtLeast0p95": exploit_valid_yield >= 0.95,
        "noFamilyAbove60PercentPositiveContribution": largest_share <= 0.60,
    }

    decision = "SPECTRAL_TOP1_SEARCH_CONFIRMED" if all(gates.values()) else "SPECTRAL_TOP1_SEARCH_NOT_CONFIRMED"

    target_diagnostics = {}
    for target_id in sorted({row["target"] for row in rows}):
        subset = [row for row in rows if row["target"] == target_id]
        target_diagnostics[target_id] = {
            "family": subset[0]["family"],
            "effect": _stats([row["effect"] for row in subset]),
            "meaningfulFraction": statistics.fmean(1.0 if row["meaningful"] else 0.0 for row in subset),
        }

    return {
        "version": 1,
        "experiment": "sampling-invariance-search-top1-confirmation-v1",
        "population": "confirmation",
        "decision": decision,
        "meaningfulMargin": MEANINGFUL_MARGIN,
        "seeds": list(EXPECTED_SEEDS),
        "hardInvariants": hard,
        "gates": gates,
        "primary": {
            "cellEffect": _stats(effects),
            "masterSeedMeanEffect": seed_stats,
            "masterSeedOneSided95LowerBound": seed_lcb,
            "tCriticalOneSided95Df23": T_CRITICAL_ONE_SIDED_95_DF23,
            "meaningfulFraction": meaningful_fraction,
            "exploitValidYield": exploit_valid_yield,
            "top1UniquePhenotypeRate": top1_unique_rate,
            "breadthTailValidYield": breadth_valid_yield,
            "largestFamilyPositiveContributionShare": largest_share,
            "leaveOneFamilyOutMean": loo,
            "acceptedImprovements": _stats([row["acceptedImprovements"] for row in rows]),
        },
        "familyDiagnostics": family_diagnostics,
        "seedDiagnostics": {str(seed): {"meanEffect": seed_means[seed]} for seed in EXPECTED_SEEDS},
        "targetDiagnostics": target_diagnostics,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = reduce(_load(Path(args.results_dir)))
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"decision": result["decision"], "gates": result["gates"], "primary": result["primary"]}, indent=2))


if __name__ == "__main__":
    main()
