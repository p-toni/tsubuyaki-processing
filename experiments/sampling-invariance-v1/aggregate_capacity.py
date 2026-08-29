from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import capacity


def _summary(values: list[float]) -> dict[str, float]:
    if not values:
        return {"n": 0, "mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "sd": 0.0}
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "sd": statistics.pstdev(values) if len(values) > 1 else 0.0,
    }


def aggregate(results_dir: Path, population: str) -> dict:
    expected_seeds = capacity.DESIGN_SEEDS if population == "design" else capacity.HOLDOUT_SEEDS
    paths = sorted(Path(results_dir).glob("seed-*.json"))
    blocks = [json.loads(path.read_text()) for path in paths]
    failures = []

    seeds = [int(block.get("seed")) for block in blocks]
    if sorted(seeds) != sorted(expected_seeds):
        failures.append(f"seed rectangle mismatch: got={sorted(seeds)} expected={sorted(expected_seeds)}")
    if len(set(seeds)) != len(seeds):
        failures.append("duplicate seed blocks")

    if not blocks:
        raise AssertionError("no capacity blocks found")

    first = blocks[0]
    canonical_settings = first["settings"]
    canonical_representations = first["representations"]
    canonical_targets = [
        (target["id"], target["family"], target["targetFingerprint"])
        for target in first["targets"]
    ]

    cells = []
    archive_diagnostics = {representation: [] for representation in canonical_representations}
    for block in blocks:
        if block.get("experiment") != "sampling-invariance-capacity-v1":
            failures.append(f"seed {block.get('seed')}: experiment id mismatch")
        if block.get("population") != population:
            failures.append(f"seed {block.get('seed')}: population mismatch")
        if block.get("settings") != canonical_settings:
            failures.append(f"seed {block.get('seed')}: settings mismatch")
        if block.get("representations") != canonical_representations:
            failures.append(f"seed {block.get('seed')}: representation list mismatch")
        if not all(block.get("hardInvariants", {}).values()):
            failures.append(f"seed {block.get('seed')}: hard invariant failure {block.get('hardInvariants')}")
        target_identity = [
            (target["id"], target["family"], target["targetFingerprint"])
            for target in block["targets"]
        ]
        if target_identity != canonical_targets:
            failures.append(f"seed {block.get('seed')}: target identity/order mismatch")
        for representation in canonical_representations:
            archive_diagnostics[representation].append(block["archiveDiagnostics"][representation])
        for target in block["targets"]:
            cells.append(
                {
                    "seed": int(block["seed"]),
                    "target": target["id"],
                    "family": target["family"],
                    "fieldSignedDelta": float(target["fieldSignedDelta"]),
                    "fieldAddedRecovery": float(target["fieldAddedRecovery"]),
                    "fieldMeaningful": bool(target["fieldMeaningfulUniqueContribution"]),
                    "fieldRecovery": float(target["fieldRecovery"]),
                    "bestCurrentRecovery": float(target["bestCurrentRecovery"]),
                    "bestCurrentRoute": target["bestCurrentRoute"],
                    "currentAdded": {
                        route: float(target["currentRouteAddedRecovery"][route]) for route in capacity.CURRENT_ROUTES
                    },
                    "currentMeaningful": {
                        route: bool(target["currentRouteMeaningfulUniqueContribution"][route])
                        for route in capacity.CURRENT_ROUTES
                    },
                }
            )

    expected_cells = len(expected_seeds) * 15
    if len(cells) != expected_cells:
        failures.append(f"cell rectangle mismatch: got={len(cells)} expected={expected_cells}")

    field_added = [cell["fieldAddedRecovery"] for cell in cells]
    field_signed = [cell["fieldSignedDelta"] for cell in cells]
    field_meaningful_fraction = statistics.fmean(1.0 if cell["fieldMeaningful"] else 0.0 for cell in cells)

    current_route_contribution = {}
    for route in capacity.CURRENT_ROUTES:
        added = [cell["currentAdded"][route] for cell in cells]
        meaningful_fraction = statistics.fmean(1.0 if cell["currentMeaningful"][route] else 0.0 for cell in cells)
        current_route_contribution[route] = {
            "addedRecovery": _summary(added),
            "meaningfulUniqueContributionFraction": meaningful_fraction,
        }

    route_mean_baseline = statistics.median(
        [current_route_contribution[route]["addedRecovery"]["mean"] for route in capacity.CURRENT_ROUTES]
    )
    route_meaningful_baseline = statistics.median(
        [current_route_contribution[route]["meaningfulUniqueContributionFraction"] for route in capacity.CURRENT_ROUTES]
    )

    families = sorted({cell["family"] for cell in cells})
    family_records = {}
    meaningful_families = []
    for family in families:
        family_cells = [cell for cell in cells if cell["family"] == family]
        added = [cell["fieldAddedRecovery"] for cell in family_cells]
        signed = [cell["fieldSignedDelta"] for cell in family_cells]
        meaningful_count = sum(cell["fieldMeaningful"] for cell in family_cells)
        if meaningful_count:
            meaningful_families.append(family)
        family_records[family] = {
            "addedRecovery": _summary(added),
            "signedDelta": _summary(signed),
            "meaningfulUniqueContributions": meaningful_count,
            "meaningfulFraction": meaningful_count / len(family_cells),
        }

    target_ids = [identity[0] for identity in canonical_targets]
    target_records = {}
    target_positive_sums = {}
    for target_id in target_ids:
        target_cells = [cell for cell in cells if cell["target"] == target_id]
        added = [cell["fieldAddedRecovery"] for cell in target_cells]
        signed = [cell["fieldSignedDelta"] for cell in target_cells]
        positive_sum = sum(added)
        target_positive_sums[target_id] = positive_sum
        target_records[target_id] = {
            "family": target_cells[0]["family"],
            "addedRecovery": _summary(added),
            "signedDelta": _summary(signed),
            "meaningfulUniqueContributions": sum(cell["fieldMeaningful"] for cell in target_cells),
        }

    total_positive = sum(target_positive_sums.values())
    if total_positive > 0.0:
        contribution_share = {target: value / total_positive for target, value in target_positive_sums.items()}
        largest_target = max(contribution_share, key=lambda target: (contribution_share[target], target))
        largest_target_share = contribution_share[largest_target]
    else:
        contribution_share = {target: 0.0 for target in target_ids}
        largest_target = None
        largest_target_share = 1.0

    seed_records = {}
    for seed in expected_seeds:
        seed_cells = [cell for cell in cells if cell["seed"] == seed]
        seed_records[str(seed)] = {
            "meanAddedRecovery": statistics.fmean(cell["fieldAddedRecovery"] for cell in seed_cells),
            "meanSignedDelta": statistics.fmean(cell["fieldSignedDelta"] for cell in seed_cells),
            "meaningfulUniqueContributions": sum(cell["fieldMeaningful"] for cell in seed_cells),
        }

    best_current_counts = {route: 0 for route in capacity.CURRENT_ROUTES}
    for cell in cells:
        best_current_counts[cell["bestCurrentRoute"]] += 1

    archive_summary = {}
    for representation, records in archive_diagnostics.items():
        archive_summary[representation] = {
            "meanAttemptsPerAccepted": statistics.fmean(float(record["attemptsPerAccepted"]) for record in records),
            "minUniquePhenotypeRate": min(float(record["uniquePhenotypeRate"]) for record in records),
            "meanUniquePhenotypeRate": statistics.fmean(float(record["uniquePhenotypeRate"]) for record in records),
        }

    hard_invariants = {
        "completeSeedRectangle": sorted(seeds) == sorted(expected_seeds) and len(set(seeds)) == len(seeds),
        "completeCellRectangle": len(cells) == expected_cells,
        "allBlockHardInvariants": not any("hard invariant failure" in failure for failure in failures),
        "identicalSettings": not any("settings mismatch" in failure for failure in failures),
        "identicalRepresentationList": not any("representation list mismatch" in failure for failure in failures),
        "identicalTargetSuite": not any("target identity/order mismatch" in failure for failure in failures),
    }

    primary = {
        "fieldPortfolioAddedRecovery": _summary(field_added),
        "fieldSignedCompetitiveDelta": _summary(field_signed),
        "fieldMeaningfulUniqueContributionFraction": field_meaningful_fraction,
        "currentRouteMedianMeanAddedRecovery": route_mean_baseline,
        "currentRouteMedianMeaningfulFraction": route_meaningful_baseline,
        "meaningfulFamilies": meaningful_families,
        "largestSingleTargetContribution": {
            "target": largest_target,
            "share": largest_target_share,
        },
    }

    result = {
        "version": 1,
        "experiment": "sampling-invariance-capacity-v1",
        "population": population,
        "settings": canonical_settings,
        "seeds": list(expected_seeds),
        "targets": [
            {"id": target_id, "family": family, "fingerprint": fingerprint}
            for target_id, family, fingerprint in canonical_targets
        ],
        "hardInvariants": hard_invariants,
        "failures": failures,
        "primary": primary,
        "currentRouteContribution": current_route_contribution,
        "familyDiagnostics": family_records,
        "targetDiagnostics": target_records,
        "targetPositiveContributionShare": contribution_share,
        "seedDiagnostics": seed_records,
        "bestCurrentRouteCounts": best_current_counts,
        "archiveDiagnostics": archive_summary,
    }

    if population == "holdout":
        gates = {
            "completeHardInvariantRectangle": all(hard_invariants.values()) and not failures,
            "meanFieldAddedRecoveryAtLeast0p002": primary["fieldPortfolioAddedRecovery"]["mean"] >= 0.002,
            "fieldMeanAddedAboveCurrentRouteMedian": primary["fieldPortfolioAddedRecovery"]["mean"] > route_mean_baseline,
            "fieldMeaningfulFractionAtLeastCurrentRouteMedian": field_meaningful_fraction >= route_meaningful_baseline,
            "meaningfulContributionInAtLeastTwoFamilies": len(meaningful_families) >= 2,
            "noSingleTargetAbove35PercentPositiveContribution": largest_target_share <= 0.35,
        }
        result["gates"] = gates
        result["decision"] = (
            "SAMPLING_INVARIANCE_CAPACITY_PROMISING"
            if all(gates.values())
            else "SAMPLING_INVARIANCE_CAPACITY_NOT_PROMISING"
        )
    else:
        result["decision"] = "DESIGN_INFRA_VALID" if all(hard_invariants.values()) and not failures else "DESIGN_INFRA_INVALID"

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", choices=("design", "holdout"), required=True)
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = aggregate(Path(args.results_dir), args.population)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"population": args.population, "decision": result["decision"], "hardInvariants": result["hardInvariants"]}, indent=2))
    if args.population == "design" and result["decision"] != "DESIGN_INFRA_VALID":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
