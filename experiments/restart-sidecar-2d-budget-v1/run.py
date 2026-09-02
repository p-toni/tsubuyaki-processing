#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
BUDGET_V1 = ROOT / "experiments" / "restart-sidecar-budget-v1"
for p in (PROTO, BUDGET_V1):
    sys.path.insert(0, str(p))

import core
import restart_sidecar
import search_engine
from rng_streams import derived_seed
import run_budget as budget_base

ROUTES = ("family", "sheet")
BUDGETS = (1, 2, 4, 8)
MAX_BUDGET = 8
SMOKE_SEED = 761999
MASTER_SEEDS = (
    761003, 761019, 761037, 761053, 761071,
    761089, 761107, 761127, 761149, 761167,
    761181, 761199, 761223, 761239, 761257,
    761277, 761293, 761311, 761331, 761349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str) -> dict:
    return {
        "name": "restart-sidecar-2d-budget-v1",
        "artistic_intent": "mechanical 2d sidecar budget experiment only; no artistic authority",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.NATIVE_ONLY,
    }


def _spawn_sidecars(brief: dict, master_seed: int, route: str) -> list[core.Candidate]:
    with restart_sidecar.restart_route_registry((route,)):
        return [
            restart_sidecar._spawn_restart(brief, master_seed, route, i)
            for i in range(MAX_BUDGET)
        ]


def _production_replay_check(
    brief: dict,
    master_seed: int,
    route: str,
    expected: list[core.Candidate],
    root: Path,
) -> bool:
    out = root / f"production-{route}"
    restart_sidecar.generate_restart_sidecar(
        brief, master_seed, out, attempts_per_route=4
    )
    records = json.loads((out / "candidates.json").read_text())
    got = [r["phenotypeHash"] for r in records]
    want = [budget_base.shortlist._phenotype_hash(c) for c in expected[:4]]
    return got == want


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    route_records = {}
    frozen = {}
    production_replay = {}

    with tempfile.TemporaryDirectory(prefix=f"restart-sidecar-2d-budget-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            brief = _brief(route)
            if int(core.ROUTES[route].get("intrinsic_dimension", -1)) != 2:
                raise AssertionError(f"route intrinsic-dimension drift: {route}")
            if restart_sidecar._eligible_routes(brief) != [route]:
                raise AssertionError(f"production sidecar authority missing for {route}")

            search_seed = derived_seed(master_seed, "restart-sidecar-2d-budget-v1", route)
            state, report = search_engine.run_search(brief, search_seed, root / f"baseline-{route}")
            diag = budget_base._operator_diag(state)
            if diag["total"] != 20 or diag["native"] != 20 or diag["spectral"] != 0:
                raise AssertionError(f"baseline native budget drift for {route}: {diag}")

            baseline_all = budget_base._generated(state)
            baseline_valid = budget_base._generated_valid(state)
            before_digest = budget_base._archive_digest(baseline_all)
            sidecars = _spawn_sidecars(brief, master_seed, route)
            after_digest = budget_base._archive_digest(baseline_all)

            if smoke:
                production_replay[route] = _production_replay_check(
                    brief, master_seed, route, sidecars, root
                )

            arms = {0: baseline_valid}
            for k in BUDGETS:
                arms[k] = baseline_valid + [
                    c for c in sidecars[:k] if bool(c.checks.get("valid", False))
                ]
            selections = {k: budget_base._select_dispersion(arms[k]) for k in (0,) + BUDGETS}

            baseline_hashes = {
                budget_base.shortlist._phenotype_hash(c) for c in baseline_valid
            }
            budget_records = {}
            for k in BUDGETS:
                prefix = sidecars[:k]
                valid_prefix = [c for c in prefix if bool(c.checks.get("valid", False))]
                prefix_hashes = [budget_base.shortlist._phenotype_hash(c) for c in prefix]
                valid_hashes = {
                    budget_base.shortlist._phenotype_hash(c) for c in valid_prefix
                }
                budget_records[str(k)] = {
                    "attempted": k,
                    "valid": len(valid_prefix),
                    "validRate": len(valid_prefix) / k,
                    "prefixPhenotypeHashes": prefix_hashes,
                    "distinctValidPhenotypesAddedVsBaseline": len(valid_hashes - baseline_hashes),
                    "unionValidCount": len(arms[k]),
                    "unionDistinctPhenotypes": len({
                        budget_base.shortlist._phenotype_hash(c) for c in arms[k]
                    }),
                    "dispersion": {
                        key: value for key, value in selections[k].items()
                        if key != "candidates"
                    },
                }

            route_records[route] = {
                "searchSeed": search_seed,
                "selectionStatus": report["selectionStatus"],
                "provisionalChampion": report["provisionalChampion"],
                "baselineOperatorDiagnostics": diag,
                "baselineValidCount": len(baseline_valid),
                "baselineArchiveDigestBeforeSidecar": before_digest,
                "baselineArchiveDigestAfterSidecar": after_digest,
                "baselineDispersion": {
                    key: value for key, value in selections[0].items()
                    if key != "candidates"
                },
                "sidecar": [budget_base._sidecar_record(c) for c in sidecars],
                "budgets": budget_records,
            }
            frozen[route] = {"arms": arms, "selections": selections}

        targets = budget_base.build_targets_runtime()
        if len(targets) != 15:
            raise AssertionError(f"target-suite drift: {len(targets)}")

        cells = []
        for route in ROUTES:
            for target in targets:
                base_archive = frozen[route]["arms"][0]
                base_delivery = frozen[route]["selections"][0]["candidates"]
                base_archive_recovery = max(
                    budget_base._recovery(im, target.image)
                    for im in budget_base._images(base_archive)
                )
                base_delivery_recovery = max(
                    budget_base._recovery(im, target.image)
                    for im in budget_base._images(base_delivery)
                )
                for k in BUDGETS:
                    archive = frozen[route]["arms"][k]
                    delivery = frozen[route]["selections"][k]["candidates"]
                    archive_recovery = max(
                        budget_base._recovery(im, target.image)
                        for im in budget_base._images(archive)
                    )
                    delivery_recovery = max(
                        budget_base._recovery(im, target.image)
                        for im in budget_base._images(delivery)
                    )
                    cells.append({
                        "masterSeed": master_seed,
                        "route": route,
                        "targetId": target.id,
                        "targetFamily": target.family,
                        "budget": k,
                        "baselineArchiveRecovery": base_archive_recovery,
                        "unionArchiveRecovery": archive_recovery,
                        "archiveDelta": archive_recovery - base_archive_recovery,
                        "baselineDeliveryRecovery": base_delivery_recovery,
                        "unionDeliveryRecovery": delivery_recovery,
                        "deliveryDelta": delivery_recovery - base_delivery_recovery,
                    })

    hard = {
        "routeSetExact": tuple(route_records) == ROUTES,
        "routeClassExact": all(
            int(core.ROUTES[r].get("intrinsic_dimension", -1)) == 2 for r in ROUTES
        ),
        "productionSidecarAuthorityExact": all(
            restart_sidecar._eligible_routes(_brief(r)) == [r] for r in ROUTES
        ),
        "baselineBudgetExact": all(
            route_records[r]["baselineOperatorDiagnostics"]["total"] == 20
            and route_records[r]["baselineOperatorDiagnostics"]["native"] == 20
            and route_records[r]["baselineOperatorDiagnostics"]["spectral"] == 0
            for r in ROUTES
        ),
        "baselineUnchangedBySidecar": all(
            route_records[r]["baselineArchiveDigestBeforeSidecar"]
            == route_records[r]["baselineArchiveDigestAfterSidecar"]
            for r in ROUTES
        ),
        "sidecarMaxBudgetExact": all(
            len(route_records[r]["sidecar"]) == MAX_BUDGET for r in ROUTES
        ),
        "sidecarAuthorityFlagsExact": all(
            not c["mayEnterBaselineSearch"]
            and not c["mayParentBaselineSearch"]
            and not c["mayReplaceBaselineDelivery"]
            and c["generationOperator"] == "restart-sidecar"
            for r in ROUTES for c in route_records[r]["sidecar"]
        ),
        "nestedPrefixesExact": all(
            route_records[r]["budgets"]["1"]["prefixPhenotypeHashes"]
            == route_records[r]["budgets"]["8"]["prefixPhenotypeHashes"][:1]
            and route_records[r]["budgets"]["2"]["prefixPhenotypeHashes"]
            == route_records[r]["budgets"]["8"]["prefixPhenotypeHashes"][:2]
            and route_records[r]["budgets"]["4"]["prefixPhenotypeHashes"]
            == route_records[r]["budgets"]["8"]["prefixPhenotypeHashes"][:4]
            for r in ROUTES
        ),
        "cellCountExact": len(cells) == len(ROUTES) * 15 * len(BUDGETS),
    }
    if smoke:
        hard["productionApiFirstFourReplayExact"] = all(production_replay.values())
    if not all(hard.values()):
        raise AssertionError(f"hard invariant failure: {hard}")

    return {
        "version": 1,
        "experiment": "restart-sidecar-2d-budget-v1",
        "masterSeed": master_seed,
        "smoke": smoke,
        "artisticEvidence": False,
        "authority": "mechanical-compute-coverage-only",
        "settings": {
            "routes": list(ROUTES),
            "budgetsPerRoute": list(BUDGETS),
            "maxSidecarBudgetPerRoute": MAX_BUDGET,
            "baselineGeneratedAttemptsPerRoute": 20,
            "baselineNativePerRoute": 20,
            "baselineSpectralPerRoute": 0,
            "sidecarNamespace": restart_sidecar.SIDECAR_NAMESPACE,
            "structuralMetric": "sparse-geometry-v1-exact-fast-grayscale",
            "delivery": "target-blind raw-pixel max-dispersion trio",
        },
        "hardInvariants": hard,
        "productionReplay": production_replay,
        "routes": route_records,
        "cells": cells,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--output")
    args = p.parse_args()
    result = run_seed(args.seed, smoke=args.smoke)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
