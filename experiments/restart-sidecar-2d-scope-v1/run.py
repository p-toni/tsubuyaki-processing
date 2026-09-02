#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
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
MAX_BUDGET = 8
SMOKE_SEED = 760999
MASTER_SEEDS = (
    760003, 760019, 760037, 760053, 760071,
    760089, 760107, 760127, 760149, 760167,
    760181, 760199, 760223, 760239, 760257,
    760277, 760293, 760311, 760331, 760349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str) -> dict:
    return {
        "name": "restart-sidecar-2d-scope-v1",
        "artistic_intent": "mechanical 2d sidecar scope test only; no artistic authority",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.NATIVE_ONLY,
    }


def _spawn_experimental_restart(brief: dict, master_seed: int, route: str, index: int) -> core.Candidate:
    """Reproduce sidecar mechanics without expanding production route authority."""
    rng = random.Random(derived_seed(master_seed, restart_sidecar.SIDECAR_NAMESPACE, route, index))
    prefix = str(core.ROUTES[route].get("prefix", route[:1].upper()))
    cid = f"SC-{prefix}{index + 1}"
    cand = core.Candidate(
        cid,
        route,
        cid,
        core.ROUTES[route]["seed"](rng),
        None,
        "restart-sidecar",
    )
    core.evaluate_candidate(cand, brief)
    cand.checks["generationOperator"] = "restart-sidecar"
    cand.checks["sidecarVersion"] = restart_sidecar.SIDECAR_VERSION
    cand.checks["mayEnterBaselineSearch"] = False
    cand.checks["mayParentBaselineSearch"] = False
    cand.checks["mayReplaceBaselineDelivery"] = False
    return cand


def _sidecar_record(c: core.Candidate) -> dict:
    return {
        "id": c.id,
        "valid": bool(c.checks.get("valid", False)),
        "phenotypeHash": budget_base.shortlist._phenotype_hash(c),
        "mayEnterBaselineSearch": bool(c.checks.get("mayEnterBaselineSearch", True)),
        "mayParentBaselineSearch": bool(c.checks.get("mayParentBaselineSearch", True)),
        "mayReplaceBaselineDelivery": bool(c.checks.get("mayReplaceBaselineDelivery", True)),
        "generationOperator": c.checks.get("generationOperator"),
        "sidecarVersion": c.checks.get("sidecarVersion"),
    }


def _production_authority_rejects(route: str, brief: dict) -> bool:
    if restart_sidecar._eligible_routes(brief):
        return False
    try:
        with restart_sidecar.restart_route_registry((route,)):
            pass
    except ValueError:
        return True
    return False


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    route_records = {}
    frozen = {}

    with tempfile.TemporaryDirectory(prefix=f"restart-sidecar-2d-scope-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            brief = _brief(route)
            if int(core.ROUTES[route].get("intrinsic_dimension", -1)) != 2:
                raise AssertionError(f"route intrinsic-dimension drift: {route}")

            search_seed = derived_seed(master_seed, "restart-sidecar-2d-scope-v1", route)
            state, report = search_engine.run_search(brief, search_seed, root / f"baseline-{route}")
            diag = budget_base._operator_diag(state)
            if diag["total"] != 20 or diag["native"] != 20 or diag["spectral"] != 0:
                raise AssertionError(f"baseline native budget drift for {route}: {diag}")

            baseline_all = budget_base._generated(state)
            baseline_valid = budget_base._generated_valid(state)
            before_digest = budget_base._archive_digest(baseline_all)
            sidecars = [
                _spawn_experimental_restart(brief, master_seed, route, i)
                for i in range(MAX_BUDGET)
            ]
            after_digest = budget_base._archive_digest(baseline_all)

            union_valid = baseline_valid + [c for c in sidecars if bool(c.checks.get("valid", False))]
            baseline_selection = budget_base._select_dispersion(baseline_valid)
            union_selection = budget_base._select_dispersion(union_valid)
            baseline_hashes = {budget_base.shortlist._phenotype_hash(c) for c in baseline_valid}
            sidecar_valid = [c for c in sidecars if bool(c.checks.get("valid", False))]
            sidecar_valid_hashes = {budget_base.shortlist._phenotype_hash(c) for c in sidecar_valid}

            route_records[route] = {
                "searchSeed": search_seed,
                "selectionStatus": report["selectionStatus"],
                "provisionalChampion": report["provisionalChampion"],
                "baselineOperatorDiagnostics": diag,
                "baselineValidCount": len(baseline_valid),
                "baselineArchiveDigestBeforeSidecar": before_digest,
                "baselineArchiveDigestAfterSidecar": after_digest,
                "productionAuthorityStillRejectsRoute": _production_authority_rejects(route, brief),
                "baselineDispersion": {
                    k: v for k, v in baseline_selection.items() if k != "candidates"
                },
                "unionDispersion": {
                    k: v for k, v in union_selection.items() if k != "candidates"
                },
                "sidecar": [_sidecar_record(c) for c in sidecars],
                "sidecarAttempted": len(sidecars),
                "sidecarValid": len(sidecar_valid),
                "sidecarValidRate": len(sidecar_valid) / len(sidecars),
                "distinctValidPhenotypesAddedVsBaseline": len(sidecar_valid_hashes - baseline_hashes),
            }
            frozen[route] = {
                "baselineArchive": baseline_valid,
                "unionArchive": union_valid,
                "baselineDelivery": baseline_selection["candidates"],
                "unionDelivery": union_selection["candidates"],
            }

        targets = budget_base.build_targets_runtime()
        if len(targets) != 15:
            raise AssertionError(f"target-suite drift: {len(targets)}")

        cells = []
        for route in ROUTES:
            rr = frozen[route]
            baseline_archive_images = budget_base._images(rr["baselineArchive"])
            union_archive_images = budget_base._images(rr["unionArchive"])
            baseline_delivery_images = budget_base._images(rr["baselineDelivery"])
            union_delivery_images = budget_base._images(rr["unionDelivery"])
            for target in targets:
                base_archive = max(budget_base._recovery(im, target.image) for im in baseline_archive_images)
                union_archive = max(budget_base._recovery(im, target.image) for im in union_archive_images)
                base_delivery = max(budget_base._recovery(im, target.image) for im in baseline_delivery_images)
                union_delivery = max(budget_base._recovery(im, target.image) for im in union_delivery_images)
                cells.append({
                    "masterSeed": master_seed,
                    "route": route,
                    "targetId": target.id,
                    "targetFamily": target.family,
                    "baselineArchiveRecovery": base_archive,
                    "unionArchiveRecovery": union_archive,
                    "archiveDelta": union_archive - base_archive,
                    "baselineDeliveryRecovery": base_delivery,
                    "unionDeliveryRecovery": union_delivery,
                    "deliveryDelta": union_delivery - base_delivery,
                })

    hard = {
        "routeSetExact": tuple(route_records) == ROUTES,
        "routeClassExact": all(int(core.ROUTES[r].get("intrinsic_dimension", -1)) == 2 for r in ROUTES),
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
        "sidecarBudgetExact": all(len(route_records[r]["sidecar"]) == MAX_BUDGET for r in ROUTES),
        "sidecarAuthorityFlagsExact": all(
            not c["mayEnterBaselineSearch"]
            and not c["mayParentBaselineSearch"]
            and not c["mayReplaceBaselineDelivery"]
            and c["generationOperator"] == "restart-sidecar"
            for r in ROUTES for c in route_records[r]["sidecar"]
        ),
        "productionAuthorityUnchanged": all(
            route_records[r]["productionAuthorityStillRejectsRoute"] for r in ROUTES
        ),
        "cellCountExact": len(cells) == len(ROUTES) * 15,
    }
    if not all(hard.values()):
        raise AssertionError(f"hard invariant failure: {hard}")

    return {
        "version": 1,
        "experiment": "restart-sidecar-2d-scope-v1",
        "masterSeed": master_seed,
        "smoke": smoke,
        "artisticEvidence": False,
        "authority": "mechanical-route-scope-only",
        "settings": {
            "routes": list(ROUTES),
            "sidecarAttemptsPerRoute": MAX_BUDGET,
            "baselineGeneratedAttemptsPerRoute": 20,
            "baselineNativePerRoute": 20,
            "baselineSpectralPerRoute": 0,
            "sidecarNamespace": restart_sidecar.SIDECAR_NAMESPACE,
            "structuralMetric": "sparse-geometry-v1-exact-fast-grayscale",
            "delivery": "target-blind raw-pixel max-dispersion trio",
        },
        "hardInvariants": hard,
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
