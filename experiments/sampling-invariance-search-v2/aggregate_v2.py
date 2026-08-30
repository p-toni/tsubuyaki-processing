from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from run_search_v2 import MEANINGFUL_MARGIN, PILOT_SEEDS

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


def _loo(cells: list[dict], key: str) -> dict[str, float]:
    return {
        omitted: statistics.fmean(cell[key] for cell in cells if cell["family"] != omitted)
        for omitted in FAMILIES
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
                    "top2VsBreadth": float(target["effects"]["top2VsBreadth"]),
                    "top2VsTop1": float(target["effects"]["top2VsTop1"]),
                    "top1VsBreadth": float(target["effects"]["top1VsBreadth"]),
                    "meaningful": bool(target["effects"]["top2MeaningfulVsBreadth"]),
                    "top2ValidYield": float(target["policies"]["hybrid-top2"]["exploitValidYield"]),
                    "top1ValidYield": float(target["policies"]["hybrid-top1"]["exploitValidYield"]),
                    "breadthValidYield": float(target["policies"]["breadth-20"]["tailValidYield"]),
                    "top2UniqueRate": float(target["policies"]["hybrid-top2"]["uniquePhenotypeRate"]),
                    "winnerFromSecondBasin": bool(target["policies"]["hybrid-top2"]["winnerFromSecondBasin"]),
                    "anchorGap": float(target["anchorRecoveryGap"]),
                    "acceptedTop1": int(target["policies"]["hybrid-top2"]["acceptedImprovementsTop1"]),
                    "acceptedTop2": int(target["policies"]["hybrid-top2"]["acceptedImprovementsTop2"]),
                }
            )

    complete_cells = len(cells) == len(PILOT_SEEDS) * 15
    top2_breadth = [cell["top2VsBreadth"] for cell in cells]
    top2_top1 = [cell["top2VsTop1"] for cell in cells]
    top1_breadth = [cell["top1VsBreadth"] for cell in cells]
    loo_breadth = _loo(cells, "top2VsBreadth")
    loo_top1 = _loo(cells, "top2VsTop1")

    positive_by_family = {
        family: sum(max(0.0, cell["top2VsBreadth"]) for cell in cells if cell["family"] == family)
        for family in FAMILIES
    }
    total_positive = sum(positive_by_family.values())
    contribution_share = {
        family: value / total_positive if total_positive > 0.0 else 0.0
        for family, value in positive_by_family.items()
    }

    family_diagnostics = {}
    for family in FAMILIES:
        subset = [cell for cell in cells if cell["family"] == family]
        family_diagnostics[family] = {
            "top2VsBreadth": _summary([cell["top2VsBreadth"] for cell in subset]),
            "top2VsTop1": _summary([cell["top2VsTop1"] for cell in subset]),
            "top1VsBreadth": _summary([cell["top1VsBreadth"] for cell in subset]),
            "meaningfulFraction": statistics.fmean(1.0 if cell["meaningful"] else 0.0 for cell in subset),
            "secondBasinWinnerFraction": statistics.fmean(1.0 if cell["winnerFromSecondBasin"] else 0.0 for cell in subset),
            "positiveContributionShare": contribution_share[family],
        }

    target_diagnostics = {}
    for target_id in sorted({cell["target"] for cell in cells}):
        subset = [cell for cell in cells if cell["target"] == target_id]
        target_diagnostics[target_id] = {
            "family": subset[0]["family"],
            "top2VsBreadth": _summary([cell["top2VsBreadth"] for cell in subset]),
            "top2VsTop1": _summary([cell["top2VsTop1"] for cell in subset]),
            "meaningfulFraction": statistics.fmean(1.0 if cell["meaningful"] else 0.0 for cell in subset),
            "secondBasinWinnerFraction": statistics.fmean(1.0 if cell["winnerFromSecondBasin"] else 0.0 for cell in subset),
        }

    seed_diagnostics = {}
    for seed in PILOT_SEEDS:
        subset = [cell for cell in cells if cell["seed"] == seed]
        if subset:
            seed_diagnostics[str(seed)] = {
                "meanTop2VsBreadth": statistics.fmean(cell["top2VsBreadth"] for cell in subset),
                "meanTop2VsTop1": statistics.fmean(cell["top2VsTop1"] for cell in subset),
                "meaningfulCells": sum(1 for cell in subset if cell["meaningful"]),
                "secondBasinWinnerCells": sum(1 for cell in subset if cell["winnerFromSecondBasin"]),
            }

    hard = {
        "completeSeedRectangle": complete_seeds,
        "completeCellRectangle": complete_cells,
        "identicalSettings": identical_settings,
        "identicalTargetSuite": identical_targets,
        "allBlockHardInvariants": all_block_hard,
    }

    primary = {
        "top2VsBreadth": _summary(top2_breadth),
        "top2VsTop1": _summary(top2_top1),
        "top1VsBreadth": _summary(top1_breadth),
        "meaningfulTop2VsBreadthFraction": statistics.fmean(1.0 if cell["meaningful"] else 0.0 for cell in cells),
        "top2ExploitValidYield": statistics.fmean(cell["top2ValidYield"] for cell in cells),
        "top1ExploitValidYield": statistics.fmean(cell["top1ValidYield"] for cell in cells),
        "breadthTailValidYield": statistics.fmean(cell["breadthValidYield"] for cell in cells),
        "top2UniquePhenotypeRate": statistics.fmean(cell["top2UniqueRate"] for cell in cells),
        "secondBasinWinnerFraction": statistics.fmean(1.0 if cell["winnerFromSecondBasin"] else 0.0 for cell in cells),
        "anchorRecoveryGap": _summary([cell["anchorGap"] for cell in cells]),
        "acceptedImprovementsTop1": _summary([float(cell["acceptedTop1"]) for cell in cells]),
        "acceptedImprovementsTop2": _summary([float(cell["acceptedTop2"]) for cell in cells]),
        "leaveOneFamilyOutTop2VsBreadthMean": loo_breadth,
        "leaveOneFamilyOutTop2VsTop1Mean": loo_top1,
        "positiveContributionShareByFamily": contribution_share,
        "largestFamilyPositiveContributionShare": max(contribution_share.values()) if contribution_share else 0.0,
    }

    gates = {
        "completeHardInvariantRectangle": all(hard.values()),
        "meanTop2VsBreadthPositive": primary["top2VsBreadth"]["mean"] > 0.0,
        "everyLeaveOneFamilyOutTop2VsBreadthPositive": all(value > 0.0 for value in loo_breadth.values()),
        "meanTop2VsTop1Positive": primary["top2VsTop1"]["mean"] > 0.0,
        "everyLeaveOneFamilyOutTop2VsTop1Positive": all(value > 0.0 for value in loo_top1.values()),
        "meaningfulTop2VsBreadthFractionAtLeast0p30": primary["meaningfulTop2VsBreadthFraction"] >= 0.30,
        "top2ValidYieldAtLeast0p95": primary["top2ExploitValidYield"] >= 0.95,
        "noFamilyAbove60PercentPositiveContribution": primary["largestFamilyPositiveContributionShare"] <= 0.60,
    }

    return {
        "version": 2,
        "experiment": "sampling-invariance-search-v2",
        "population": "pilot",
        "seeds": list(PILOT_SEEDS),
        "meaningfulMargin": MEANINGFUL_MARGIN,
        "hardInvariants": hard,
        "primary": primary,
        "familyDiagnostics": family_diagnostics,
        "targetDiagnostics": target_diagnostics,
        "seedDiagnostics": seed_diagnostics,
        "gates": gates,
        "decision": "SPECTRAL_HEDGE_SEARCH_PROMISING" if all(gates.values()) else "SPECTRAL_HEDGE_SEARCH_NOT_PROMISING",
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
