#!/usr/bin/env python3
"""Run one complete master-seed block of multiplex-capacity-v1."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
if str(PROTO) not in sys.path:
    sys.path.insert(0, str(PROTO))

V1_PATH = ROOT / "experiments" / "search-leverage-v1" / "reproduce.py"
GEOMETRY_PATH = ROOT / "experiments" / "search-measurement-geometry-v1" / "audit.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v1 = _load("multiplex_capacity_search_v1", V1_PATH)
geometry = _load("multiplex_capacity_sparse_geometry_v1", GEOMETRY_PATH)

import core
from phenotype_descriptors import DESCRIPTOR_VERSION, describe_images, niche_key
from rng_streams import derived_seed
from challenges import CHALLENGES, CHALLENGE_IDS, FAMILIES, points as challenge_points
from multiplex_representation import VARIANTS, hard_valid, mutate_genome, points as multiplex_points, seed_genome

CURRENT_ROUTES = tuple(v1.ROUTE_ORDER)
REPRESENTATIONS = CURRENT_ROUTES + VARIANTS
FULL = "multiplex-full"
ABLATIONS = tuple(v for v in VARIANTS if v != FULL)

CONSUMED_SEEDS = (
    1087, 1091, 1093, 1097, 1103,
    1109, 1117, 1123, 1129, 1151,
    1153, 1163, 1171, 1181, 1187,
    1193, 1201, 1213, 1217, 1223,
)
SMOKE_SEED = 9001
ALL_SEEDS = CONSUMED_SEEDS + (SMOKE_SEED,)
STARTS = 4
CYCLES = 4
SCALES = (1.0, 0.7, 0.55, 1.2)
MUTATIONS = STARTS * CYCLES
TOTAL_CANDIDATES_PER_SEARCH = STARTS + MUTATIONS
TARGET_ALPHA = 44
EPSILON = 1e-12

_RENDER_CACHE: dict[tuple[str, str], tuple[Image.Image, ...]] = {}
_NICHE_CACHE: dict[tuple[str, str], str] = {}


def _register_experimental_routes() -> None:
    for variant in VARIANTS:
        intrinsic = 2 if variant == "multiplex-regular-grid" else 1
        core.ROUTES[variant] = {
            "render": lambda genome, t, v=variant: multiplex_points(genome, t, v, core.W, core.H),
            "geometry": lambda genome, t, v=variant: {"all": multiplex_points(genome, t, v, core.W, core.H)},
            "target_occupancy": (0.008, 0.20),
            "seed": seed_genome,
            "mutate": mutate_genome,
            "prefix": "M",
            "version": "1",
            "intrinsic_dimension": intrinsic,
        }


_register_experimental_routes()


def _genome_key(genome: dict) -> str:
    return json.dumps(genome, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _images(candidate) -> tuple[Image.Image, ...]:
    key = (candidate.route, _genome_key(candidate.genome))
    cached = _RENDER_CACHE.get(key)
    if cached is None:
        cached = tuple(v1.render_candidate_frame(candidate, t).convert("L") for t in core.TIMES)
        _RENDER_CACHE[key] = cached
    return cached


def _fingerprint(candidate) -> str:
    return hashlib.sha256(b"\0".join(im.tobytes() for im in _images(candidate))).hexdigest()


def _niche(candidate) -> str:
    key = (candidate.route, _genome_key(candidate.genome))
    cached = _NICHE_CACHE.get(key)
    if cached is not None:
        return cached
    descriptor = describe_images(_images(candidate), int(core.ROUTES[candidate.route]["intrinsic_dimension"]))
    niche = niche_key(descriptor)
    label = f"{niche.version}:a{niche.anisotropy_bin}-v{niche.central_void_bin}-m{niche.motion_bin}"
    _NICHE_CACHE[key] = label
    return label


def _evaluate(candidate, brief: dict | None = None):
    if candidate.route in CURRENT_ROUTES:
        return v1.evaluate_candidate(candidate, brief if brief is not None else v1._brief(candidate.route))
    candidate.checks = hard_valid(candidate.genome, candidate.route, core.TIMES, core.draw_points, core.W, core.H)
    candidate.features = {}
    candidate.score = 0.0 if candidate.checks["valid"] else -1e9
    return candidate


def _candidate(cid: str, rep: str, basin: str, genome: dict, parent_id: str | None, stage: str, brief=None):
    candidate = v1.Candidate(cid, rep, basin, dict(genome), parent_id, stage)
    return _evaluate(candidate, brief)


def _target_images(seed: int, challenge) -> tuple[Image.Image, ...]:
    images = tuple(
        core.draw_points(challenge_points(seed, challenge, t, core.W, core.H), TARGET_ALPHA)
        for t in core.TIMES
    )
    for im in images:
        support = sum(1 for value in im.tobytes() if value > 20)
        if support < 140:
            raise AssertionError(f"challenge {challenge.id} has insufficient support: {support}")
    return images


def _target_fingerprint(images: tuple[Image.Image, ...]) -> str:
    return hashlib.sha256(b"\0".join(im.tobytes() for im in images)).hexdigest()


def _distance(candidate, target_images: tuple[Image.Image, ...]) -> float:
    if not candidate.checks.get("valid", False):
        return float("inf")
    return float(geometry.sparse_geometry_distance(_images(candidate), target_images)["distance"])


def _current_starts(seed: int, route: str):
    brief = v1._brief(route)
    rng = random.Random(derived_seed(seed, "multiplex-capacity-v1", "starts", route))
    starts = []
    attempts = 0
    while len(starts) < STARTS and attempts < 600:
        attempts += 1
        candidate = _candidate(
            f"{route}-S{len(starts)+1}-A{attempts}",
            route,
            f"{route}-B{len(starts)+1}",
            v1.ROUTES[route]["seed"](rng),
            None,
            "start",
            brief,
        )
        if candidate.checks.get("valid", False):
            candidate.id = f"{route}-S{len(starts)+1}"
            starts.append(candidate)
    if len(starts) != STARTS:
        raise RuntimeError(f"could not generate {STARTS} valid starts for {route}")
    return starts, attempts


def _experimental_starts(seed: int):
    """Generate genomes that are hard-valid under all five multiplex variants."""
    rng = random.Random(derived_seed(seed, "multiplex-capacity-v1", "starts", "multiplex-shared"))
    by_rep = {rep: [] for rep in VARIANTS}
    attempts = 0
    accepted_genome_hashes = []
    while len(accepted_genome_hashes) < STARTS and attempts < 1000:
        attempts += 1
        genome = seed_genome(rng)
        candidates = {
            rep: _candidate(
                f"{rep}-S{len(accepted_genome_hashes)+1}-A{attempts}",
                rep,
                f"M-B{len(accepted_genome_hashes)+1}",
                genome,
                None,
                "start",
            )
            for rep in VARIANTS
        }
        if all(candidate.checks.get("valid", False) for candidate in candidates.values()):
            digest = hashlib.sha256(_genome_key(genome).encode("utf-8")).hexdigest()
            accepted_genome_hashes.append(digest)
            for rep, candidate in candidates.items():
                candidate.id = f"{rep}-S{len(accepted_genome_hashes)}"
                by_rep[rep].append(candidate)
    if len(accepted_genome_hashes) != STARTS:
        raise RuntimeError("could not generate shared hard-valid multiplex starts")
    for rep in VARIANTS:
        if [_genome_key(c.genome) for c in by_rep[rep]] != [_genome_key(c.genome) for c in by_rep[FULL]]:
            raise AssertionError("experimental start genome matching drift")
    return by_rep, attempts, accepted_genome_hashes


def _mutate(rep: str, parent, rng, scale: float):
    if rep in CURRENT_ROUTES:
        return v1.ROUTES[rep]["mutate"](parent.genome, rng, scale)
    return mutate_genome(parent.genome, rng, scale)


def _search(rep: str, seed: int, challenge, starts: list, target_images: tuple[Image.Image, ...]):
    brief = v1._brief(rep) if rep in CURRENT_ROUTES else None
    copied = copy.deepcopy(starts)
    current = {candidate.basin: candidate for candidate in copied}
    basin_order = tuple(sorted(current))
    if len(basin_order) != STARTS:
        raise AssertionError("start basin count drift")

    all_candidates = list(copied)
    events = []
    initial_best = min(_distance(candidate, target_images) for candidate in copied)

    for cycle, scale in enumerate(SCALES, start=1):
        for basin in basin_order:
            parent = current[basin]
            stream_rep = "multiplex-shared" if rep in VARIANTS else rep
            event_seed = derived_seed(
                seed,
                "multiplex-capacity-v1",
                "mutation",
                stream_rep,
                challenge.id,
                basin,
                cycle,
            )
            rng = random.Random(event_seed)
            child = _candidate(
                f"{rep}-{challenge.id}-{basin}-C{cycle}",
                rep,
                basin,
                _mutate(rep, parent, rng, scale),
                parent.id,
                "target-search",
                brief,
            )
            all_candidates.append(child)
            accepted = False
            parent_distance = _distance(parent, target_images)
            child_distance = _distance(child, target_images)
            if child.checks.get("valid", False) and child_distance <= parent_distance + EPSILON:
                current[basin] = child
                accepted = True
            events.append(
                {
                    "cycle": cycle,
                    "basin": basin,
                    "eventSeed": event_seed,
                    "scale": scale,
                    "childValid": bool(child.checks.get("valid", False)),
                    "accepted": accepted,
                }
            )

    if len(all_candidates) != TOTAL_CANDIDATES_PER_SEARCH:
        raise AssertionError("candidate evaluation budget drift")
    valid = [candidate for candidate in all_candidates if candidate.checks.get("valid", False)]
    if len(valid) < STARTS:
        raise AssertionError("valid pool lost valid starts")
    final_best = min(_distance(candidate, target_images) for candidate in valid)
    if final_best > initial_best + EPSILON:
        raise AssertionError("search lost retained-start best distance")
    fingerprints = {_fingerprint(candidate) for candidate in valid}

    child_records = []
    for candidate in all_candidates[STARTS:]:
        if candidate.checks.get("valid", False):
            child_records.append(
                {
                    "challenge": challenge.id,
                    "candidateId": candidate.id,
                    "fingerprint": _fingerprint(candidate),
                    "niche": _niche(candidate),
                }
            )

    return {
        "initialBestDistance": initial_best,
        "finalBestDistance": final_best,
        "recovery": 1.0 - final_best,
        "normalizedImprovement": (initial_best - final_best) / max(initial_best, EPSILON),
        "totalCandidates": len(all_candidates),
        "hardValidCandidates": len(valid),
        "hardValidYield": len(valid) / len(all_candidates),
        "uniqueRenderedPhenotypes": len(fingerprints),
        "uniquePhenotypeRate": len(fingerprints) / len(valid),
        "acceptedMutations": sum(1 for event in events if event["accepted"]),
        "events": events,
        "nicheRecords": child_records,
    }


def _start_niche_records(rep: str, starts: list):
    return [
        {
            "challenge": "__starts__",
            "candidateId": candidate.id,
            "fingerprint": _fingerprint(candidate),
            "niche": _niche(candidate),
        }
        for candidate in starts
    ]


def run_block(seed: int) -> dict:
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is not predeclared")
    if DESCRIPTOR_VERSION != "structural-v1":
        raise AssertionError(f"descriptor version drift: {DESCRIPTOR_VERSION}")
    if len(CHALLENGES) != 12 or len(FAMILIES) != 4:
        raise AssertionError("challenge contract drift")
    if sum(1 for c in CHALLENGES if c.smooth_plausible) < 4:
        raise AssertionError("smooth-plausible challenge floor drift")

    starts_by_rep = {}
    start_attempts = {}
    for route in CURRENT_ROUTES:
        starts_by_rep[route], start_attempts[route] = _current_starts(seed, route)
    experimental, experimental_attempts, shared_hashes = _experimental_starts(seed)
    starts_by_rep.update(experimental)
    for rep in VARIANTS:
        start_attempts[rep] = experimental_attempts

    niche_records = {rep: _start_niche_records(rep, starts_by_rep[rep]) for rep in REPRESENTATIONS}
    challenge_rows = []

    for challenge in CHALLENGES:
        target = _target_images(seed, challenge)
        row = {
            "id": challenge.id,
            "family": challenge.family,
            "smoothPlausible": challenge.smooth_plausible,
            "targetFingerprint": _target_fingerprint(target),
            "representations": {},
        }
        for rep in REPRESENTATIONS:
            result = _search(rep, seed, challenge, starts_by_rep[rep], target)
            niche_records[rep].extend(result.pop("nicheRecords"))
            row["representations"][rep] = result
        challenge_rows.append(row)

    for row in challenge_rows:
        if tuple(row["representations"]) != REPRESENTATIONS:
            raise AssertionError("representation rectangle drift")
        for rep, result in row["representations"].items():
            if result["totalCandidates"] != TOTAL_CANDIDATES_PER_SEARCH:
                raise AssertionError(f"budget drift for {rep}/{row['id']}")

    return {
        "version": 1,
        "experiment": "multiplex-capacity-v1",
        "population": "smoke-excluded" if seed == SMOKE_SEED else "consumed",
        "seed": seed,
        "metric": "sparse-geometry-v1",
        "descriptor": DESCRIPTOR_VERSION,
        "settings": {
            "starts": STARTS,
            "cycles": CYCLES,
            "scales": list(SCALES),
            "candidateEvaluationsPerRepresentationChallenge": TOTAL_CANDIDATES_PER_SEARCH,
            "targetAlpha": TARGET_ALPHA,
        },
        "representations": list(REPRESENTATIONS),
        "currentRoutes": list(CURRENT_ROUTES),
        "fullMultiplex": FULL,
        "ablations": list(ABLATIONS),
        "challengeIds": list(CHALLENGE_IDS),
        "families": list(FAMILIES),
        "startAttempts": start_attempts,
        "sharedExperimentalStartGenomeHashes": shared_hashes,
        "challenges": challenge_rows,
        "nicheRecords": niche_records,
        "hardInvariants": {
            "completeChallengeRectangle": len(challenge_rows) == len(CHALLENGES),
            "completeRepresentationRectangle": all(len(row["representations"]) == len(REPRESENTATIONS) for row in challenge_rows),
            "equalCandidateBudget": all(
                result["totalCandidates"] == TOTAL_CANDIDATES_PER_SEARCH
                for row in challenge_rows
                for result in row["representations"].values()
            ),
            "sharedExperimentalStarts": all(
                [_genome_key(c.genome) for c in starts_by_rep[rep]] == [_genome_key(c.genome) for c in starts_by_rep[FULL]]
                for rep in VARIANTS
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, choices=ALL_SEEDS, required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run_block(args.seed)
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload + "\n")
    else:
        print(payload)


if __name__ == "__main__":
    main()
