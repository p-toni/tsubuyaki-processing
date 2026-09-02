#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import statistics
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
SHORTLIST_DIR = ROOT / "experiments" / "delivery-dispersion-shortlist-v1"
METRIC_DIR = ROOT / "experiments" / "spectral-material-control-v1"
RUNTIME_DIR = ROOT / "experiments" / "spectral-material-control-runtime-replay-v1"
for p in (PROTO, SHORTLIST_DIR, METRIC_DIR, RUNTIME_DIR):
    sys.path.insert(0, str(p))

from orbit_representation import register_orbit
register_orbit()

import core
import restart_sidecar
import search_engine
from rng_streams import derived_seed
from targets_runtime import build_targets_runtime
import run_shortlist as shortlist

ROUTES = ("recurrence", "orbit", "filament")
BUDGETS = (1, 2, 4, 8)
MAX_BUDGET = 8
TIMES = (30, 90, 150)
CANONICAL_TIME = 90
SMOKE_SEED = 759999
MASTER_SEEDS = (
    759003, 759019, 759037, 759053, 759071,
    759089, 759107, 759127, 759149, 759167,
    759181, 759199, 759223, 759239, 759257,
    759277, 759293, 759311, 759331, 759349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str) -> dict:
    return {
        "name": "restart-sidecar-budget-v1",
        "artistic_intent": "mechanical sidecar budget experiment only; no artistic authority",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.MIXED_1D_V1,
    }


def _generated(state: core.SearchState) -> list[core.Candidate]:
    return [
        c for c in state.candidates.values()
        if c.stage != "start" and c.checks.get("generationOperator") in {"native", "spectral"}
    ]


def _generated_valid(state: core.SearchState) -> list[core.Candidate]:
    return [c for c in _generated(state) if bool(c.checks.get("valid", False))]


def _operator_diag(state: core.SearchState) -> dict:
    generated = _generated(state)
    native = [c for c in generated if c.checks.get("generationOperator") == "native"]
    spectral = [c for c in generated if c.checks.get("generationOperator") == "spectral"]
    return {
        "total": len(generated),
        "native": len(native),
        "spectral": len(spectral),
        "valid": sum(bool(c.checks.get("valid", False)) for c in generated),
        "nativeValid": sum(bool(c.checks.get("valid", False)) for c in native),
        "spectralValid": sum(bool(c.checks.get("valid", False)) for c in spectral),
    }


def _archive_digest(cands: list[core.Candidate]) -> str:
    payload = [
        {
            "id": c.id,
            "route": c.route,
            "stage": c.stage,
            "operator": c.checks.get("generationOperator"),
            "valid": bool(c.checks.get("valid", False)),
            "phenotype": shortlist._phenotype_hash(c),
        }
        for c in cands
    ]
    return hashlib.sha256(
        (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()


def _select_dispersion(cands: list[core.Candidate]) -> dict:
    if len(cands) < 3:
        raise AssertionError(f"need at least 3 hard-valid candidates, found {len(cands)}")
    hashes = [shortlist._phenotype_hash(c) for c in cands]
    if len(set(hashes)) < 3:
        raise AssertionError("archive has fewer than three distinct temporal phenotypes")
    distances = shortlist._distance_matrix(cands)
    best_combo = None
    best_score = None
    eps = 1e-15
    for combo in itertools.combinations(range(len(cands)), 3):
        score = shortlist._combo_dispersion(combo, distances)
        if best_score is None or score[0] > best_score[0] + eps or (
            abs(score[0] - best_score[0]) <= eps and score[1] > best_score[1] + eps
        ):
            best_combo, best_score = combo, score
    assert best_combo is not None and best_score is not None
    selected = [cands[i] for i in best_combo]
    return {
        "candidates": selected,
        "indices": list(best_combo),
        "candidateIds": [c.id for c in selected],
        "phenotypeHashes": [shortlist._phenotype_hash(c) for c in selected],
        "minimumPairwiseDistance": float(best_score[0]),
        "meanPairwiseDistance": float(best_score[1]),
    }


def _images(cands: list[core.Candidate]) -> list[Image.Image]:
    return [core.render_candidate_frame(c, CANONICAL_TIME) for c in cands]


def _recovery(image: Image.Image, target_image: Image.Image) -> float:
    return shortlist._recovery(image, target_image)


def _spawn_sidecars(brief: dict, master_seed: int, route: str) -> list[core.Candidate]:
    with restart_sidecar.restart_route_registry((route,)):
        return [
            restart_sidecar._spawn_restart(brief, master_seed, route, i)
            for i in range(MAX_BUDGET)
        ]


def _sidecar_record(c: core.Candidate) -> dict:
    return {
        "id": c.id,
        "valid": bool(c.checks.get("valid", False)),
        "phenotypeHash": shortlist._phenotype_hash(c),
        "mayEnterBaselineSearch": bool(c.checks.get("mayEnterBaselineSearch", True)),
        "mayParentBaselineSearch": bool(c.checks.get("mayParentBaselineSearch", True)),
        "mayReplaceBaselineDelivery": bool(c.checks.get("mayReplaceBaselineDelivery", True)),
        "generationOperator": c.checks.get("generationOperator"),
        "sidecarVersion": c.checks.get("sidecarVersion"),
    }


def _production_replay_check(brief: dict, master_seed: int, route: str, expected: list[core.Candidate], root: Path) -> bool:
    out = root / f"production-{route}"
    restart_sidecar.generate_restart_sidecar(
        brief, master_seed, out, attempts_per_route=4
    )
    records = json.loads((out / "candidates.json").read_text())
    got = [r["phenotypeHash"] for r in records]
    want = [shortlist._phenotype_hash(c) for c in expected[:4]]
    return got == want


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    route_records = {}
    frozen = {}
    production_replay = {}

    with tempfile.TemporaryDirectory(prefix=f"restart-sidecar-budget-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            brief = _brief(route)
            search_seed = derived_seed(master_seed, "restart-sidecar-budget-v1", route)
            state, report = search_engine.run_search(brief, search_seed, root / f"baseline-{route}")
            diag = _operator_diag(state)
            if diag["total"] != 20 or diag["native"] != 10 or diag["spectral"] != 10:
                raise AssertionError(f"baseline mixed budget drift for {route}: {diag}")

            baseline_all = _generated(state)
            baseline_valid = _generated_valid(state)
            before_digest = _archive_digest(baseline_all)
            sidecars = _spawn_sidecars(brief, master_seed, route)
            after_digest = _archive_digest(baseline_all)
            sidecar_records = [_sidecar_record(c) for c in sidecars]

            if smoke:
                production_replay[route] = _production_replay_check(
                    brief, master_seed, route, sidecars, root
                )

            arms = {0: baseline_valid}
            for k in BUDGETS:
                arms[k] = baseline_valid + [c for c in sidecars[:k] if bool(c.checks.get("valid", False))]

            selections = {k: _select_dispersion(arms[k]) for k in (0,) + BUDGETS}
            baseline_hashes = {shortlist._phenotype_hash(c) for c in baseline_valid}
            budget_records = {}
            for k in BUDGETS:
                prefix = sidecars[:k]
                prefix_hashes = [shortlist._phenotype_hash(c) for c in prefix]
                valid_prefix = [c for c in prefix if bool(c.checks.get("valid", False))]
                valid_hashes = {shortlist._phenotype_hash(c) for c in valid_prefix}
                budget_records[str(k)] = {
                    "attempted": k,
                    "valid": len(valid_prefix),
                    "validRate": len(valid_prefix) / k,
                    "prefixPhenotypeHashes": prefix_hashes,
                    "distinctValidPhenotypesAddedVsBaseline": len(valid_hashes - baseline_hashes),
                    "unionValidCount": len(arms[k]),
                    "unionDistinctPhenotypes": len({shortlist._phenotype_hash(c) for c in arms[k]}),
                    "dispersion": {
                        key: value for key, value in selections[k].items() if key != "candidates"
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
                    key: value for key, value in selections[0].items() if key != "candidates"
                },
                "sidecar": sidecar_records,
                "budgets": budget_records,
            }
            frozen[route] = {
                "arms": arms,
                "selections": selections,
            }

        targets = build_targets_runtime()
        cells = []
        for route in ROUTES:
            for target in targets:
                base_archive = frozen[route]["arms"][0]
                base_delivery = frozen[route]["selections"][0]["candidates"]
                base_archive_recovery = max(_recovery(im, target.image) for im in _images(base_archive))
                base_delivery_recovery = max(_recovery(im, target.image) for im in _images(base_delivery))
                for k in BUDGETS:
                    archive = frozen[route]["arms"][k]
                    delivery = frozen[route]["selections"][k]["candidates"]
                    archive_recovery = max(_recovery(im, target.image) for im in _images(archive))
                    delivery_recovery = max(_recovery(im, target.image) for im in _images(delivery))
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
        "baselineBudgetExact": all(
            route_records[r]["baselineOperatorDiagnostics"]["total"] == 20
            and route_records[r]["baselineOperatorDiagnostics"]["native"] == 10
            and route_records[r]["baselineOperatorDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "baselineUnchangedBySidecar": all(
            route_records[r]["baselineArchiveDigestBeforeSidecar"]
            == route_records[r]["baselineArchiveDigestAfterSidecar"]
            for r in ROUTES
        ),
        "sidecarMaxBudgetExact": all(len(route_records[r]["sidecar"]) == MAX_BUDGET for r in ROUTES),
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
        "cellCountExact": len(cells) == 3 * 15 * len(BUDGETS),
    }
    if smoke:
        hard["productionApiFirstFourReplayExact"] = all(production_replay.values())
    if not all(hard.values()):
        raise AssertionError(f"hard invariant failure: {hard}")

    return {
        "version": 1,
        "experiment": "restart-sidecar-budget-v1",
        "masterSeed": master_seed,
        "smoke": smoke,
        "artisticEvidence": False,
        "authority": "mechanical-compute-coverage-only",
        "settings": {
            "routes": list(ROUTES),
            "budgetsPerRoute": list(BUDGETS),
            "maxSidecarBudgetPerRoute": MAX_BUDGET,
            "baselineGeneratedAttemptsPerRoute": 20,
            "baselineNativePerRoute": 10,
            "baselineSpectralPerRoute": 10,
            "sidecarNamespace": restart_sidecar.SIDECAR_NAMESPACE,
            "canonicalStructuralTime": CANONICAL_TIME,
            "distanceFrames": list(TIMES),
            "distanceResize": shortlist.DISTANCE_SIZE,
            "distance": "mean-absolute-grayscale-pixel-difference-nearest-resize",
            "structuralMetric": "sparse-geometry-v1-exact-fast-grayscale",
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
