#!/usr/bin/env python3
"""Fail-closed reducer for multiplex-capacity-v1."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from run import (
    ABLATIONS,
    CHALLENGE_IDS,
    CONSUMED_SEEDS,
    CURRENT_ROUTES,
    FAMILIES,
    FULL,
    REPRESENTATIONS,
    TOTAL_CANDIDATES_PER_SEARCH,
)

EXPECTED_BLOCKS = len(CONSUMED_SEEDS)
REPRESENTATION_SET = set(REPRESENTATIONS)


def _load_blocks(root: Path) -> list[dict]:
    blocks = []
    for path in sorted(root.rglob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception as exc:
            raise AssertionError(f"invalid JSON artifact {path}: {exc}") from exc
        if isinstance(data, dict) and data.get("experiment") == "multiplex-capacity-v1" and data.get("population") == "consumed":
            blocks.append(data)
    return blocks


def _summary(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("cannot summarize empty values")
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def _challenge_rows(block: dict) -> dict[str, dict]:
    rows = {str(row["id"]): row for row in block["challenges"]}
    if tuple(rows) != CHALLENGE_IDS:
        raise AssertionError(f"challenge order/rectangle drift for seed {block['seed']}")
    return rows


def _validate(blocks: list[dict]) -> dict[int, dict]:
    if len(blocks) != EXPECTED_BLOCKS:
        raise AssertionError(f"expected {EXPECTED_BLOCKS} consumed seed blocks, found {len(blocks)}")
    by_seed = {}
    for block in blocks:
        seed = int(block["seed"])
        if seed in by_seed:
            raise AssertionError(f"duplicate seed block {seed}")
        if seed not in CONSUMED_SEEDS:
            raise AssertionError(f"out-of-contract seed {seed}")
        if block.get("metric") != "sparse-geometry-v1" or block.get("descriptor") != "structural-v1":
            raise AssertionError(f"measurement contract drift for seed {seed}")
        if tuple(block.get("representations", ())) != REPRESENTATIONS:
            raise AssertionError(f"representation contract drift for seed {seed}")
        invariants = block.get("hardInvariants") or {}
        if not invariants or not all(bool(value) for value in invariants.values()):
            raise AssertionError(f"hard invariant failure for seed {seed}: {invariants}")
        rows = _challenge_rows(block)
        for challenge_id, row in rows.items():
            # Combined seed blocks are serialized with sort_keys=True, so mapping
            # insertion order is not a valid post-serialization invariant. The
            # canonical order remains protected by block['representations'] above;
            # here we require the exact representation key rectangle instead.
            if (
                len(row["representations"]) != len(REPRESENTATIONS)
                or set(row["representations"]) != REPRESENTATION_SET
            ):
                raise AssertionError(f"representation rectangle drift for {seed}/{challenge_id}")
            for rep, result in row["representations"].items():
                if int(result["totalCandidates"]) != TOTAL_CANDIDATES_PER_SEARCH:
                    raise AssertionError(f"budget drift for {seed}/{challenge_id}/{rep}")
                if int(result["hardValidCandidates"]) < 4:
                    raise AssertionError(f"valid start retention drift for {seed}/{challenge_id}/{rep}")
        by_seed[seed] = block
    if set(by_seed) != set(CONSUMED_SEEDS):
        raise AssertionError("consumed master-seed rectangle incomplete")
    return by_seed


def _primary_cells(by_seed: dict[int, dict]):
    cells = []
    for seed in CONSUMED_SEEDS:
        for row in by_seed[seed]["challenges"]:
            reps = row["representations"]
            full_recovery = float(reps[FULL]["recovery"])
            current = {route: float(reps[route]["recovery"]) for route in CURRENT_ROUTES}
            best_route, best_current = max(current.items(), key=lambda item: (item[1], item[0]))
            cells.append(
                {
                    "seed": seed,
                    "challenge": row["id"],
                    "family": row["family"],
                    "smoothPlausible": bool(row["smoothPlausible"]),
                    "fullRecovery": full_recovery,
                    "bestCurrentRoute": best_route,
                    "bestCurrentRecovery": best_current,
                    "advantage": full_recovery - best_current,
                    "ablationAdvantages": {
                        ablation: full_recovery - float(reps[ablation]["recovery"])
                        for ablation in ABLATIONS
                    },
                }
            )
    return cells


def _rarefied_niche_diagnostics(by_seed: dict[int, dict]):
    records_by_rep = {rep: [] for rep in (FULL,) + ABLATIONS}
    for seed in CONSUMED_SEEDS:
        block = by_seed[seed]
        for rep in records_by_rep:
            seen = set()
            for record in block["nicheRecords"][rep]:
                # A rendering may appear more than once through a no-op mutation;
                # count it once so niche density is not inflated by duplicates.
                key = (record["fingerprint"], record["challenge"], record["candidateId"])
                if key in seen:
                    continue
                seen.add(key)
                records_by_rep[rep].append(
                    {
                        "seed": seed,
                        "challenge": str(record["challenge"]),
                        "candidateId": str(record["candidateId"]),
                        "fingerprint": str(record["fingerprint"]),
                        "niche": str(record["niche"]),
                    }
                )

    valid_counts = {rep: len(records) for rep, records in records_by_rep.items()}
    rarefaction_count = min(valid_counts.values())
    if rarefaction_count < 1:
        raise AssertionError("empty multiplex niche population")

    summaries = {}
    for rep, records in records_by_rep.items():
        ordered = sorted(records, key=lambda r: (r["seed"], r["challenge"], r["candidateId"], r["fingerprint"]))
        rare = ordered[:rarefaction_count]
        niches = {record["niche"] for record in rare}
        fingerprints = {record["fingerprint"] for record in records}
        summaries[rep] = {
            "hardValidRecords": len(records),
            "uniqueRenderedPhenotypes": len(fingerprints),
            "rarefactionCount": rarefaction_count,
            "distinctNichesAtRarefaction": len(niches),
            "rarefiedNicheDensity": len(niches) / rarefaction_count,
            "niches": sorted(niches),
        }
    strongest_ablation = max(ABLATIONS, key=lambda rep: (summaries[rep]["rarefiedNicheDensity"], rep))
    ratio = summaries[FULL]["rarefiedNicheDensity"] / max(1e-12, summaries[strongest_ablation]["rarefiedNicheDensity"])
    return {
        "rarefactionCount": rarefaction_count,
        "representations": summaries,
        "strongestAblation": strongest_ablation,
        "fullToStrongestAblationDensityRatio": ratio,
    }


def aggregate(results_dir: Path) -> dict:
    blocks = _load_blocks(results_dir)
    by_seed = _validate(blocks)
    cells = _primary_cells(by_seed)

    seed_effects = {
        seed: statistics.fmean(cell["advantage"] for cell in cells if cell["seed"] == seed)
        for seed in CONSUMED_SEEDS
    }
    primary_values = [seed_effects[seed] for seed in CONSUMED_SEEDS]

    leave_one_family_out = []
    for omitted in FAMILIES:
        retained = [cell["advantage"] for cell in cells if cell["family"] != omitted]
        leave_one_family_out.append({"omittedFamily": omitted, "meanAdvantage": statistics.fmean(retained)})

    ablation_means = {
        ablation: statistics.fmean(cell["ablationAdvantages"][ablation] for cell in cells)
        for ablation in ABLATIONS
    }

    positive_by_family = {
        family: sum(max(0.0, cell["advantage"]) for cell in cells if cell["family"] == family)
        for family in FAMILIES
    }
    positive_total = sum(positive_by_family.values())
    family_positive_share = {
        family: (positive_by_family[family] / positive_total if positive_total > 0 else 0.0)
        for family in FAMILIES
    }
    max_family_share = max(family_positive_share.values()) if family_positive_share else 1.0

    niche = _rarefied_niche_diagnostics(by_seed)
    niche_ratio = float(niche["fullToStrongestAblationDensityRatio"])

    gates = {
        "completeHardInvariantRectangle": True,
        "fullMeanAdvantageOverBestCurrentPositive": statistics.fmean(primary_values) > 0.0,
        "everyLeaveOneChallengeFamilyOutPositive": all(item["meanAdvantage"] > 0.0 for item in leave_one_family_out),
        "fullMeanAdvantageOverEveryAblationPositive": all(value > 0.0 for value in ablation_means.values()),
        "rarefiedNicheDensityAtLeast1p25xStrongestAblation": niche_ratio >= 1.25,
        "noChallengeFamilyAbove60PercentPositiveContribution": positive_total > 0.0 and max_family_share <= 0.60,
    }
    promising = all(gates.values())

    family_means = {
        family: statistics.fmean(cell["advantage"] for cell in cells if cell["family"] == family)
        for family in FAMILIES
    }
    challenge_means = {
        challenge: statistics.fmean(cell["advantage"] for cell in cells if cell["challenge"] == challenge)
        for challenge in CHALLENGE_IDS
    }
    best_current_counts = Counter(cell["bestCurrentRoute"] for cell in cells)
    smooth_cells = [cell["advantage"] for cell in cells if cell["smoothPlausible"]]
    non_smooth_cells = [cell["advantage"] for cell in cells if not cell["smoothPlausible"]]
    largest = max(cells, key=lambda cell: abs(float(cell["advantage"])))

    hard_valid_yield = {}
    unique_rate = {}
    for rep in REPRESENTATIONS:
        hard_valid_yield[rep] = statistics.fmean(
            float(row["representations"][rep]["hardValidYield"])
            for block in blocks
            for row in block["challenges"]
        )
        unique_rate[rep] = statistics.fmean(
            float(row["representations"][rep]["uniquePhenotypeRate"])
            for block in blocks
            for row in block["challenges"]
        )

    return {
        "version": 1,
        "experiment": "multiplex-capacity-v1",
        "decision": "MULTIPLEX_CAPACITY_PROMISING" if promising else "MULTIPLEX_CAPACITY_NOT_PROMISING",
        "freshSearchEvidence": False,
        "population": {
            "masterSeeds": len(CONSUMED_SEEDS),
            "challenges": len(CHALLENGE_IDS),
            "representations": len(REPRESENTATIONS),
            "seedChallengeCells": len(cells),
            "candidateEvaluationsPerRepresentationChallenge": TOTAL_CANDIDATES_PER_SEARCH,
        },
        "gates": gates,
        "primary": {
            "completeMasterSeedEffects": _summary(primary_values),
            "seedEffects": {str(seed): seed_effects[seed] for seed in CONSUMED_SEEDS},
            "leaveOneChallengeFamilyOut": leave_one_family_out,
            "familyMeans": family_means,
            "challengeMeans": challenge_means,
            "smoothPlausibleChallenges": _summary(smooth_cells),
            "otherChallenges": _summary(non_smooth_cells),
            "bestCurrentRouteCounts": dict(sorted(best_current_counts.items())),
            "largestAbsoluteSeedChallengeCell": largest,
        },
        "ablationAdvantages": ablation_means,
        "positiveContribution": {
            "byFamily": positive_by_family,
            "shareByFamily": family_positive_share,
            "maximumFamilyShare": max_family_share,
        },
        "nicheCoverage": niche,
        "diagnostics": {
            "meanHardValidYieldByRepresentation": hard_valid_yield,
            "meanUniquePhenotypeRateByRepresentation": unique_rate,
        },
        "interpretationBoundary": "consumed-seed mechanism-capacity pilot only; passing does not admit a sixth route and failing cannot be repaired by tuning on these seeds",
        "ifPromising": "freeze exact grammar, ablations, challenges, search topology and reducer; power-plan one fresh fixed-sample confirmation before any representation admission",
        "ifNotPromising": "do not retune this mechanism family on these 20 seeds; classify the failed assumption and either close the line or define a materially new hypothesis on a different consumed holdout",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = aggregate(Path(args.results_dir))
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
