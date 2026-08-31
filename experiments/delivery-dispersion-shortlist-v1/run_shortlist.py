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

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
METRIC_DIR = ROOT / "experiments" / "spectral-material-control-v1"
RUNTIME_DIR = ROOT / "experiments" / "spectral-material-control-runtime-replay-v1"
for p in (PROTO, METRIC_DIR, RUNTIME_DIR):
    sys.path.insert(0, str(p))

from orbit_representation import register_orbit
register_orbit()

import core
import search_engine
import fast_grayscale_metric as metric
from rng_streams import derived_seed
from targets_runtime import build_targets_runtime

ROUTES = ("recurrence", "orbit", "filament")
TIMES = (30, 90, 150)
CANONICAL_TIME = 90
DISTANCE_SIZE = 100
QUANTILES = (0.20, 0.50, 0.80)
MIN_VALID_GENERATED = 12
SMOKE_SEED = 742999
MASTER_SEEDS = (
    742003, 742021, 742039, 742057,
    742073, 742091, 742109, 742127,
    742147, 742163, 742181, 742199,
    742217, 742237, 742253, 742271,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str) -> dict:
    return {
        "name": "delivery-dispersion-shortlist-v1",
        "artistic_intent": "mechanical delivery-shortlist experiment only; no artistic authority",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.MIXED_1D_V1,
    }


def _generated_valid(state: core.SearchState) -> list[core.Candidate]:
    return [
        c for c in state.candidates.values()
        if c.stage != "start"
        and c.checks.get("generationOperator") in {"native", "spectral"}
        and c.checks.get("valid", False)
    ]


def _operator_diag(state: core.SearchState) -> dict:
    generated = [
        c for c in state.candidates.values()
        if c.stage != "start"
        and c.checks.get("generationOperator") in {"native", "spectral"}
    ]
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


def _phenotype_hash(cand: core.Candidate) -> str:
    h = hashlib.sha256()
    for t in TIMES:
        h.update(core.render_candidate_frame(cand, t).tobytes())
        h.update(b"\0")
    return h.hexdigest()


def _distance_vector(cand: core.Candidate) -> np.ndarray:
    frames = []
    for t in TIMES:
        im = core.render_candidate_frame(cand, t).convert("L")
        im = im.resize((DISTANCE_SIZE, DISTANCE_SIZE), resample=Image.Resampling.NEAREST)
        frames.append(np.frombuffer(im.tobytes(), dtype=np.uint8).astype(np.int16))
    return np.concatenate(frames)


def _distance_matrix(cands: list[core.Candidate]) -> np.ndarray:
    vectors = [_distance_vector(c) for c in cands]
    n = len(vectors)
    out = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            d = float(np.abs(vectors[i] - vectors[j]).mean()) / 255.0
            out[i, j] = d
            out[j, i] = d
    return out


def _combo_dispersion(combo: tuple[int, int, int], distances: np.ndarray) -> tuple[float, float]:
    i, j, k = combo
    ds = (float(distances[i, j]), float(distances[i, k]), float(distances[j, k]))
    return min(ds), statistics.fmean(ds)


def _select_shortlists(generated: list[core.Candidate]) -> dict:
    n = len(generated)
    if n < MIN_VALID_GENERATED:
        raise AssertionError(f"need >={MIN_VALID_GENERATED} hard-valid generated challengers; found {n}")

    hashes = [_phenotype_hash(c) for c in generated]
    if len(set(hashes)) < 3:
        raise AssertionError("archive has fewer than three distinct generated phenotype hashes")

    quantile_indices = tuple(int((n - 1) * q) for q in QUANTILES)
    if len(set(quantile_indices)) != 3:
        raise AssertionError(f"quantile indices collapsed: {quantile_indices}")

    distances = _distance_matrix(generated)
    quantile_score = _combo_dispersion(quantile_indices, distances)

    best_combo = None
    best_score = None
    eps = 1e-15
    for combo in itertools.combinations(range(n), 3):
        score = _combo_dispersion(combo, distances)
        if best_score is None:
            best_combo, best_score = combo, score
            continue
        if score[0] > best_score[0] + eps or (
            abs(score[0] - best_score[0]) <= eps and score[1] > best_score[1] + eps
        ):
            best_combo, best_score = combo, score

    assert best_combo is not None and best_score is not None
    quantile = [generated[i] for i in quantile_indices]
    dispersion = [generated[i] for i in best_combo]

    dispersion_hashes = [_phenotype_hash(c) for c in dispersion]
    quantile_hashes = [_phenotype_hash(c) for c in quantile]
    if len(set(dispersion_hashes)) != 3:
        raise AssertionError("max-dispersion shortlist does not contain three distinct phenotypes")
    if len(set(quantile_hashes)) != 3:
        raise AssertionError("quantile shortlist does not contain three distinct phenotypes")
    if best_score[0] + eps < quantile_score[0]:
        raise AssertionError("max-dispersion shortlist underperformed feasible quantile minimum distance")

    return {
        "quantileCandidates": quantile,
        "dispersionCandidates": dispersion,
        "quantile": {
            "indices": list(quantile_indices),
            "candidateIds": [c.id for c in quantile],
            "phenotypeHashes": quantile_hashes,
            "minimumPairwiseDistance": quantile_score[0],
            "meanPairwiseDistance": quantile_score[1],
        },
        "dispersion": {
            "indices": list(best_combo),
            "candidateIds": [c.id for c in dispersion],
            "phenotypeHashes": dispersion_hashes,
            "minimumPairwiseDistance": best_score[0],
            "meanPairwiseDistance": best_score[1],
        },
    }


def _images(cands: list[core.Candidate]) -> list[Image.Image]:
    return [core.render_candidate_frame(c, CANONICAL_TIME) for c in cands]


def _recovery(image: Image.Image, target_image: Image.Image) -> float:
    return 1.0 - float(metric.sparse_geometry_distance((image,), (target_image,))["distance"])


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    route_records = {}
    archives = {}

    with tempfile.TemporaryDirectory(prefix=f"delivery-shortlist-{master_seed}-") as td:
        root = Path(td)
        for route in ROUTES:
            search_seed = derived_seed(master_seed, "delivery-dispersion-shortlist-v1", route)
            state, report = search_engine.run_search(
                _brief(route), search_seed, root / route
            )
            diag = _operator_diag(state)
            if diag["total"] != 20 or diag["native"] != 10 or diag["spectral"] != 10:
                raise AssertionError(f"mixed budget drift for {route}: {diag}")

            generated = _generated_valid(state)
            shortlist = _select_shortlists(generated)
            q = shortlist["quantileCandidates"]
            d = shortlist["dispersionCandidates"]

            route_records[route] = {
                "searchSeed": search_seed,
                "operatorDiagnostics": diag,
                "validGeneratedCount": len(generated),
                "selectionStatus": report["selectionStatus"],
                "provisionalChampion": report["provisionalChampion"],
                "quantile": shortlist["quantile"],
                "dispersion": shortlist["dispersion"],
                "minimumPairwiseDistanceLift": (
                    shortlist["dispersion"]["minimumPairwiseDistance"]
                    - shortlist["quantile"]["minimumPairwiseDistance"]
                ),
            }
            archives[route] = {
                "quantile": _images(q),
                "dispersion": _images(d),
                "full": _images(generated),
            }

        # Structural targets are constructed/scored only after both target-blind
        # shortlist policies have been frozen for every route.
        targets = build_targets_runtime()
        cells = []
        for route in ROUTES:
            for target in targets:
                quantile_recovery = max(_recovery(im, target.image) for im in archives[route]["quantile"])
                dispersion_recovery = max(_recovery(im, target.image) for im in archives[route]["dispersion"])
                full_recovery = max(_recovery(im, target.image) for im in archives[route]["full"])
                cells.append({
                    "masterSeed": master_seed,
                    "route": route,
                    "targetId": target.id,
                    "targetFamily": target.family,
                    "quantileRecovery": quantile_recovery,
                    "dispersionRecovery": dispersion_recovery,
                    "fullArchiveRecovery": full_recovery,
                    "quantileRegret": full_recovery - quantile_recovery,
                    "dispersionRegret": full_recovery - dispersion_recovery,
                    "delta": dispersion_recovery - quantile_recovery,
                })

    hard = {
        "routeSetExact": tuple(route_records) == ROUTES,
        "mixedBudgetExact": all(
            route_records[r]["operatorDiagnostics"]["total"] == 20
            and route_records[r]["operatorDiagnostics"]["native"] == 10
            and route_records[r]["operatorDiagnostics"]["spectral"] == 10
            for r in ROUTES
        ),
        "minimumValidGeneratedMet": all(
            route_records[r]["validGeneratedCount"] >= MIN_VALID_GENERATED for r in ROUTES
        ),
        "threeDistinctPerShortlist": all(
            len(set(route_records[r]["quantile"]["phenotypeHashes"])) == 3
            and len(set(route_records[r]["dispersion"]["phenotypeHashes"])) == 3
            for r in ROUTES
        ),
        "dispersionMinimumNeverBelowQuantile": all(
            route_records[r]["minimumPairwiseDistanceLift"] >= -1e-15 for r in ROUTES
        ),
        "cellCountExact": len(cells) == 45,
    }
    if not all(hard.values()):
        raise AssertionError(f"hard invariant failure: {hard}")

    return {
        "version": 1,
        "masterSeed": master_seed,
        "smoke": smoke,
        "artisticEvidence": False,
        "settings": {
            "routes": list(ROUTES),
            "challengersPerRoute": 20,
            "mixedNativePerRoute": 10,
            "mixedSpectralPerRoute": 10,
            "minimumValidGenerated": MIN_VALID_GENERATED,
            "shortlistSize": 3,
            "quantiles": list(QUANTILES),
            "distanceFrames": list(TIMES),
            "distanceResize": DISTANCE_SIZE,
            "distance": "mean-absolute-grayscale-pixel-difference-nearest-resize",
            "canonicalStructuralTime": CANONICAL_TIME,
            "structuralMetric": "sparse-geometry-v1-exact-fast-grayscale",
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
