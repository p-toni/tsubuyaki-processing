#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
PARENT = ROOT / 'experiments' / 'semantic-perceptual-steering-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(PARENT))

from orbit_representation import register_orbit
register_orbit()

import core
from material_control import with_spectral_control
from rng_streams import derived_seed
from search_engine import MIXED_1D_V1, run_search_from_starts
import fresh_targets
import perceptual_metric as pm

ROUTES = ('recurrence', 'orbit', 'filament')
STREAM = 'semantic-breadth-rerank-v1'
SMOKE_SEED = 732299999
BREADTH_PER_ROUTE = 20


def _brief(route: str) -> dict:
    return {
        'name': STREAM,
        'artistic_intent': 'Semantic search-policy comparison; artistic quality is not evaluated here.',
        'routes': [route],
        'bbox_target': [0.55, 0.82],
        'explore_per_basin': 4,
        'roundA_per_survivor': 4,
        'total_extra_budget': 12,
        'mutation_portfolio': MIXED_1D_V1,
    }


def _phenotype_fingerprint(cand) -> str:
    h = hashlib.sha256()
    for t in core.TIMES:
        h.update(core.render_candidate_frame(cand, t).tobytes())
        h.update(b'\0')
    return h.hexdigest()


def _valid_start(master_seed: int, route: str):
    # Deliberately target-blind. The exact same start is shared across all concepts
    # and both arms for a master seed.
    rng = random.Random(derived_seed(master_seed, STREAM, route, 'start'))
    brief = _brief(route)
    prefix = core.ROUTES[route].get('prefix', route[:1].upper())
    for attempt in range(1, 257):
        genome = core.ROUTES[route]['seed'](rng)
        cand = core.Candidate(f'{prefix}S1', route, f'{prefix}S1', genome, None, 'start')
        core.evaluate_candidate(cand, brief)
        if cand.checks.get('valid', False):
            return cand, attempt
    raise RuntimeError(f'could not draw valid start for {route}')


def _operator_contract(report: dict) -> dict:
    counts = report['generationOperatorCounts']; valid = report['generationOperatorValidCounts']
    return {
        'totalChallengers': int(counts.get('native', 0)) + int(counts.get('spectral', 0)),
        'nativeChallengers': int(counts.get('native', 0)),
        'spectralChallengers': int(counts.get('spectral', 0)),
        'nativeValid': int(valid.get('native', 0)),
        'spectralValid': int(valid.get('spectral', 0)),
    }


def _run_adaptive(master_seed: int, prompt: str, route: str, start, selector, out_dir: Path):
    search_seed = derived_seed(master_seed, STREAM, prompt, route, 'adaptive-search')
    state, report = run_search_from_starts(
        _brief(route), search_seed, out_dir, [copy.deepcopy(start)], selector=selector,
    )
    champ = state.candidates[report['provisionalChampion']]
    if not champ.checks.get('valid', False):
        raise AssertionError('adaptive final route champion is invalid')
    return state, report, champ


def _semantic_record(cand, prompt: str, bank: pm.PrototypeBank, targets) -> dict:
    image = pm.binary_candidate_image(cand)
    return {
        'selection': bank.image_record(image, prompt),
        'heldout': pm.heldout_prototype_record(image, prompt, targets),
    }


def _breadth_archive(master_seed: int, starts: dict[str, object]) -> tuple[list, dict, str]:
    # Prompt never enters any RNG stream in this function.
    pool = [copy.deepcopy(starts[r]) for r in ROUTES]
    attempted = {'native': 0, 'spectral': 0}
    valid = {'native': 0, 'spectral': 0}
    route_attempted = {r: {'native': 0, 'spectral': 0} for r in ROUTES}
    route_valid = {r: {'native': 0, 'spectral': 0} for r in ROUTES}
    challenger_fingerprints = []

    for route in ROUTES:
        spec = core.ROUTES[route]
        prefix = spec.get('prefix', route[:1].upper())
        rng = random.Random(derived_seed(master_seed, STREAM, route, 'breadth-draws'))
        brief = _brief(route)
        for i in range(BREADTH_PER_ROUTE):
            operator = 'native' if i < BREADTH_PER_ROUTE // 2 else 'spectral'
            base = spec['seed'](rng)
            if operator == 'native':
                genome = base
            else:
                genome = with_spectral_control(
                    base, derived_seed(master_seed, STREAM, route, i, 'breadth-field')
                )
            cand = core.Candidate(
                f'{prefix}B{i+1:02d}', route, f'{prefix}B{i+1:02d}', genome, None, 'breadth'
            )
            core.evaluate_candidate(cand, brief)
            cand.checks['generationOperator'] = operator
            attempted[operator] += 1
            route_attempted[route][operator] += 1
            challenger_fingerprints.append((cand.id, route, operator, _phenotype_fingerprint(cand)))
            if cand.checks.get('valid', False):
                valid[operator] += 1
                route_valid[route][operator] += 1
                pool.append(cand)

    signature = hashlib.sha256(
        json.dumps(challenger_fingerprints, separators=(',', ':'), sort_keys=False).encode()
    ).hexdigest()
    route_stats = {}
    for route in ROUTES:
        ra = sum(route_attempted[route].values()); rv = sum(route_valid[route].values())
        route_stats[route] = {
            'attempted': ra,
            'valid': rv,
            'validFraction': rv / ra,
            'nativeAttempted': route_attempted[route]['native'],
            'spectralAttempted': route_attempted[route]['spectral'],
            'nativeValid': route_valid[route]['native'],
            'spectralValid': route_valid[route]['spectral'],
        }
    contract = {
        'attempted': attempted,
        'valid': valid,
        'totalChallengers': sum(attempted.values()),
        'nativeChallengers': attempted['native'],
        'spectralChallengers': attempted['spectral'],
        'totalValidChallengers': sum(valid.values()),
        'pooledValidFraction': sum(valid.values()) / sum(attempted.values()),
        'routes': route_stats,
    }
    return pool, contract, signature


def run_block(master_seed: int, prompt: str, out_root: Path, smoke: bool = False) -> dict:
    if prompt not in fresh_targets.PROMPTS:
        raise ValueError(f'prompt must be one of {fresh_targets.PROMPTS}')
    targets = fresh_targets.build_targets()
    bank = pm.PrototypeBank(targets)

    starts = {}; start_attempts = {}; start_fingerprints = {}
    for route in ROUTES:
        start, attempts = _valid_start(master_seed, route)
        starts[route] = start
        start_attempts[route] = attempts
        start_fingerprints[route] = _phenotype_fingerprint(start)

    hard = {
        'identicalStartsAcrossArms': True,
        'exactBudgets': True,
        'exactMixedAllocation': True,
        'finalsValid': True,
        'scoresFinite': True,
        'adaptiveReplayDeterministic': True,
        'breadthTargetBlindReplay': True,
    }

    adaptive_champs = []
    adaptive_routes = {}
    for route in ROUTES:
        selector = pm.PrototypePerceptualSelector(prompt, bank)
        state, report, champ = _run_adaptive(
            master_seed, prompt, route, starts[route], selector, out_root / f'{route}-adaptive'
        )
        contract = _operator_contract(report)
        if contract['totalChallengers'] != 20:
            hard['exactBudgets'] = False
        if contract['nativeChallengers'] != 10 or contract['spectralChallengers'] != 10:
            hard['exactMixedAllocation'] = False
        if not champ.checks.get('valid', False):
            hard['finalsValid'] = False
        adaptive_champs.append(champ)
        adaptive_routes[route] = {
            'startAttempts': start_attempts[route],
            'startFingerprint': start_fingerprints[route],
            'championId': champ.id,
            'championFingerprint': _phenotype_fingerprint(champ),
            'operatorContract': contract,
        }
        if smoke:
            replay_selector = pm.PrototypePerceptualSelector(prompt, bank)
            _, replay_report, replay_champ = _run_adaptive(
                master_seed, prompt, route, starts[route], replay_selector,
                out_root / f'{route}-adaptive-replay'
            )
            if _operator_contract(replay_report) != contract:
                hard['adaptiveReplayDeterministic'] = False
            if _phenotype_fingerprint(replay_champ) != adaptive_routes[route]['championFingerprint']:
                hard['adaptiveReplayDeterministic'] = False

    adaptive_final = min(
        adaptive_champs, key=lambda c: pm.rank_key(pm.candidate_record(c, prompt, bank))
    )
    adaptive_record = _semantic_record(adaptive_final, prompt, bank, targets)

    breadth_pool, breadth_contract, breadth_signature = _breadth_archive(master_seed, starts)
    if breadth_contract['totalChallengers'] != 60:
        hard['exactBudgets'] = False
    if breadth_contract['nativeChallengers'] != 30 or breadth_contract['spectralChallengers'] != 30:
        hard['exactMixedAllocation'] = False
    valid_pool = [c for c in breadth_pool if c.checks.get('valid', False)]
    if not valid_pool:
        raise AssertionError('breadth archive contains no valid candidate')
    breadth_final = min(
        valid_pool, key=lambda c: pm.rank_key(pm.candidate_record(c, prompt, bank))
    )
    breadth_record = _semantic_record(breadth_final, prompt, bank, targets)
    if not breadth_final.checks.get('valid', False):
        hard['finalsValid'] = False

    if smoke:
        _, replay_contract, replay_signature = _breadth_archive(master_seed, starts)
        if replay_contract != breadth_contract or replay_signature != breadth_signature:
            hard['breadthTargetBlindReplay'] = False

    for record in (adaptive_record, breadth_record):
        for section in ('selection', 'heldout'):
            for value in record[section].values():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if not math.isfinite(float(value)):
                        hard['scoresFinite'] = False

    adaptive_total = sum(adaptive_routes[r]['operatorContract']['totalChallengers'] for r in ROUTES)
    adaptive_native = sum(adaptive_routes[r]['operatorContract']['nativeChallengers'] for r in ROUTES)
    adaptive_spectral = sum(adaptive_routes[r]['operatorContract']['spectralChallengers'] for r in ROUTES)
    if adaptive_total != 60:
        hard['exactBudgets'] = False
    if adaptive_native != 30 or adaptive_spectral != 30:
        hard['exactMixedAllocation'] = False

    return {
        'version': 1,
        'masterSeed': int(master_seed),
        'prompt': prompt,
        'smoke': bool(smoke),
        'hardInvariants': hard,
        'startFingerprints': start_fingerprints,
        'adaptiveRoutes': adaptive_routes,
        'adaptiveFinal': {
            'route': adaptive_final.route,
            'id': adaptive_final.id,
            'fingerprint': _phenotype_fingerprint(adaptive_final),
            **adaptive_record,
        },
        'breadthContract': breadth_contract,
        'breadthArchiveSignature': breadth_signature,
        'breadthFinal': {
            'route': breadth_final.route,
            'id': breadth_final.id,
            'fingerprint': _phenotype_fingerprint(breadth_final),
            'operator': breadth_final.checks.get('generationOperator', 'start'),
            **breadth_record,
        },
        'deltaHeldoutTargetF1': breadth_record['heldout']['targetF1'] - adaptive_record['heldout']['targetF1'],
        'adaptiveHeldoutTop1': bool(adaptive_record['heldout']['top1']),
        'breadthHeldoutTop1': bool(breadth_record['heldout']['top1']),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--prompt', choices=fresh_targets.PROMPTS, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    work = args.output.parent / f'work-{args.seed}-{args.prompt}'
    result = run_block(args.seed, args.prompt, work, smoke=args.smoke)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
