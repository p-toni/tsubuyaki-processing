from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from run_search import MEANINGFUL_MARGIN, PILOT_SEEDS

FAMILIES = (
    "concave-loops",
    "dense-regions",
    "disconnected-loops",
    "nested-loops",
    "open-networks",
)


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def aggregate(results_dir: Path) -> dict:
    paths = sorted(Path(results_dir).glob("seed-*.json"))
    blocks = [json.loads(path.read_text()) for path in paths]
    by_seed = {int(block["seed"]): block for block in blocks}

    complete_seeds = sorted(by_seed) == sorted(PILOT_SEEDS) and len(by_seed) == len(PILOT_SEEDS)
    first = by_seed[PILOT_SEEDS[0]] if complete_seeds else None
    identical_settings = bool(first) and all(block["settings"] == first["settings"] for block in by_seed.values())
    identical_targets = bool(first) and all(block["targetSuite"] == first["targetSuite"] for block in by_seed.values())
    all_block_hard = complete_seeds and all(all(block["hardInvariants"].values()) for block in by_seed.values())

    cells = []
    for seed in PILOT_SEEDS:
        block = by_seed.get(seed)
        if block is None:
            continue
        for target in block["targets"]:
            cells.append(
                {
                    "seed": seed,
                    "target": target["target"],
                    "family": target["family"],
                    "adaptiveVsBreadth": float(target["effects"]["adaptiveVsBreadth"]),
                    "adaptiveVsFixed": float(target["effects"]["adaptiveVsFixed"]),
                    "adaptiveGainFromInitial": float(target["effects"]["adaptiveGainFromInitial"]),
                    "meaningful": bool(target["effects"]["adaptiveMeaningfulVsBreadth"]),
                    "adaptiveValidYield": float(target["policies"]["adaptive-geodesic"]["incrementalValidYield"]),
                    "fixedValidYield": float(target["policies"]["fixed-parent-geodesic"]["incrementalValidYield"]),
                    "breadthValidYield": float(target["policies"]["independent-breadth"]["incrementalValidYield"]),
                    "adaptiveUniqueRate": float(target["policies"]["adaptive-geodesic"]["uniquePhenotypeRate"]),
                    "acceptedImprovements": int(target["policies"]["adaptive-geodesic"]["acceptedImprovements"]),
                }
            )

    expected_cells = len(PILOT_SEEDS) * 15
    complete_cells = len(cells) == expected_cells
    adaptive_breadth = [cell["adaptiveVsBreadth"] for cell in cells]
    adaptive_fixed = [cell["adaptiveVsFixed"] for cell in cells]
    adaptive_initial = [cell["adaptiveGainFromInitial"] for cell in cells]

    loo = {}
    for omitted in FAMILIES:
        values = [cell["adaptiveVsBreadth"] for cell in cells if cell["family"] != omitted]
        loo[omitted] = statistics.fmean(values) if values else float("nan")

    positive_by_family = {
        family: sum(max(0.0, cell["adaptiveVsBreadth"]) for cell in cells if cell["family"] == family)
        for family in FAMILIES
    }
    total_positive = sum(positive_by_family.values())
    family_share = {
        family: (value / total_positive if total_positive > 0.0 else 0.0)
        for family, value in positive_by_family.items()
    }

    family_diagnostics = {}
    for family in FAMILIES:
        subset = [cell for cell in cells if cell["family"] == family]
        family_diagnostics[family] = {
            "adaptiveVsBreadth": _summary([cell["adaptiveVsBreadth"] for cell in subset]),
            "adaptiveVsFixed": _summary([cell["adaptiveVsFixed"] for cell in subset]),
            "meaningfulFraction": statistics.fmean(1.0 if cell["meaningful"] else 0.0 for cell in subset),
            "positiveContributionShare": family_share[family],
        }

    target_ids = sorted({cell["target"] for cell in cells})
    target_diagnostics = {}
    for target_id in target_ids:
        subset = [cell for cell in cells if cell["target"] == target_id]
        target_diagnostics[target_id] = {
            "family": subset[0]["family"],
            "adaptiveVsBreadth": _summary([cell["adaptiveVsBreadth"] for cell in subset]),
            "adaptiveVsFixed": _summary([cell["adaptiveVsFixed"] for cell in subset]),
            "meaningfulFraction": statistics.fmean(1.0 if cell["meaningful"] else 0.0 for cell in subset),
        }

    seed_diagnostics = {}
    for seed in PILOT_SEEDS:
        subset = [cell for cell in cells if cell["seed"] == seed]
        if not subset:
            continue
        seed_diagnostics[str(seed)] = {
            "meanAdaptiveVsBreadth": statistics.fmean(cell["adaptiveVsBreadth"] for cell in subset),
            "meanAdaptiveVsFixed": statistics.fmean(cell["adaptiveVsFixed"] for cell in subset),
            "meaningfulCells": sum(1 for cell in subset if cell["meaningful"]),
            "meanAcceptedImprovements": statistics.fmean(cell["acceptedImprovements"] for cell in subset),
        }

    hard = {
        "completeSeedRectangle": complete_seeds,
        "completeCellRectangle": complete_cells,
        "identicalSettings": identical_settings,
        "identicalTargetSuite": identical_targets,
        "allBlockHardInvariants": all_block_hard,
    }

    primary = {
        "adaptiveVsBreadth": _summary(adaptive_breadth),
        "adaptiveVsFixed": _summary(adaptive_fixed),
        "adaptiveGainFromInitial": _summary(adaptive_initial),
        "meaningfulAdaptiveVsBreadthFraction": statistics.fmean(1.0 if cell["meaningful"] else 0.0 for cell in cells),
        "adaptiveIncrementalValidYield": statistics.fmean(cell["adaptiveValidYield"] for cell in cells),
        "fixedIncrementalValidYield": statistics.fmean(cell["fixedValidYield"] for cell in cells),
        "breadthIncrementalValidYield": statistics.fmean(cell["breadthValidYield"] for cell in cells),
        "adaptiveUniquePhenotypeRate": statistics.fmean(cell["adaptiveUniqueRate"] for cell in cells),
        "leaveOneFamilyOutAdaptiveVsBreadthMean": loo,
        "positiveContributionShareByFamily": family_share,
        "largestFamilyPositiveContributionShare": max(family_share.values()) if family_share else 0.0,
    }

    gates = {
        "completeHardInvariantRectangle": all(hard.values()),
        "meanAdaptiveVsBreadthPositive": primary["adaptiveVsBreadth"]["mean"] > 0.0,
        "everyLeaveOneFamilyOutAdaptiveVsBreadthPositive": all(value > 0.0 for value in loo.values()),
        "meanAdaptiveVsFixedPositive": primary["adaptiveVsFixed"]["mean"] > 0.0,
        "meaningfulAdaptiveVsBreadthFractionAtLeast0p30": primary["meaningfulAdaptiveVsBreadthFraction"] >= 0.30,
        "adaptiveValidYieldAtLeast0p95": primary["adaptiveIncrementalValidYield"] >= 0.95,
        "noFamilyAbove60PercentPositiveContribution": primary["largestFamilyPositiveContributionShare"] <= 0.60,
    }

    return {
        "version": 1,
        "experiment": "sampling-invariance-search-v1",
        "population": "pilot",
        "meaningfulMargin": MEANINGFUL_MARGIN,
        "seeds": list(PILOT_SEEDS),
        "hardInvariants": hard,
        "primary": primary,
        "familyDiagnostics": family_diagnostics,
        "targetDiagnostics": target_diagnostics,
        "seedDiagnostics": seed_diagnostics,
        "gates": gates,
        "decision": "SPECTRAL_SEARCH_PROMISING" if all(gates.values()) else "SPECTRAL_SEARCH_NOT_PROMISING",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = aggregate(Path(args.results_dir))
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"decision": result["decision"], "gates": result["gates"], "primary": result["primary"]}, indent=2, sort_keys=True))
    if not result["gates"]["completeHardInvariantRectangle"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
