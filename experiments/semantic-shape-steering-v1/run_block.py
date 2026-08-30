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
sys.path.insert(0, str(PROTO))

from orbit_representation import register_orbit
register_orbit()

import core
from pairwise_selector import DeterministicTemporalSelector
from rng_streams import derived_seed
from search_engine import MIXED_1D_V1, run_search_from_starts

from semantic_targets import PROMPTS, resolve_prompt
from steering import TargetGeometrySelector, binary_candidate_image, heldout_scores, target_distance

ROUTES = ('recurrence', 'orbit', 'filament')
STREAM = 'semantic-shape-steering-v1'
SMOKE_SEED = 124999


def _brief(route: str) -> dict:
    return {
        'name': STREAM,
        'artistic_intent': 'Target-directed structural steering experiment; artistic quality is not evaluated here.',
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


def _valid_start(master_seed: int, prompt: str, route: str):
    seed = derived_seed(master_seed, STREAM, prompt, route, 'start')
    rng = random.Random(seed)
    brief = _brief(route)
    prefix = core.ROUTES[route].get('prefix', route[:1].upper())
    for attempt in range(1, 257):
        genome = core.ROUTES[route]['seed'](rng)
        cand = core.Candidate(f'{prefix}S1', route, f'{prefix}S1', genome, None, 'start')
        core.evaluate_candidate(cand, brief)
        if cand.checks.get('valid', False):
            return cand, attempt
    raise RuntimeError(f'could not draw valid start for {prompt}/{route}')


def _trajectory_signature(state) -> str:
    payload = {
        'candidates': {
            cid: {
                'route': c.route,
                'basin': c.basin,
                'genome': c.genome,
                'parent': c.parent_id,
                'stage': c.stage,
                'valid': bool(c.checks.get('valid', False)),
                'operator': c.checks.get('generationOperator'),
                'phenotype': _phenotype_fingerprint(c),
            }
            for cid, c in sorted(state.candidates.items())
        },
        'stageDecisions': state.stage_decisions,
        'winnerId': state.winner_id,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _operator_contract(report: dict) -> dict:
    counts = report['generationOperatorCounts']
    valid = report['generationOperatorValidCounts']
    return {
        'totalChallengers': int(counts.get('native', 0)) + int(counts.get('spectral', 0)),
        'nativeChallengers': int(counts.get('native', 0)),
        'spectralChallengers': int(counts.get('spectral', 0)),
        'nativeValid': int(valid.get('native', 0)),
        'spectralValid': int(valid.get('spectral', 0)),
    }


def _run_arm(master_seed: int, prompt: str, route: str, start, target, guided: bool, out_dir: Path):
    search_seed = derived_seed(master_seed, STREAM, prompt, route, 'search')
    selector = TargetGeometrySelector(target.image) if guided else DeterministicTemporalSelector()
    state, report = run_search_from_starts(
        _brief(route),
        search_seed,
        out_dir,
        [copy.deepcopy(start)],
        selector=selector,
    )
    champ_id = report['provisionalChampion']
    champion = state.candidates[champ_id]
    if not champion.checks.get('valid', False):
        raise AssertionError('final route champion is invalid')
    return state, report, champion


def run_block(master_seed: int, prompt: str, out_root: Path, smoke: bool = False) -> dict:
    if prompt not in PROMPTS:
        raise ValueError(f'prompt must be one of {PROMPTS}')
    target = resolve_prompt(prompt)
    target_fp = hashlib.sha256(target.image.tobytes()).hexdigest()
    starts = {}
    start_attempts = {}
    start_fingerprints = {}
    for route in ROUTES:
        start, attempts = _valid_start(master_seed, prompt, route)
        starts[route] = start
        start_attempts[route] = attempts
        start_fingerprints[route] = _phenotype_fingerprint(start)

    route_records = {}
    blind_champions = []
    guided_champions = []
    hard = {
        'identicalStartsAcrossArms': True,
        'exactBudgets': True,
        'exactMixedAllocation': True,
        'finalsValid': True,
        'scoresFiniteAndBounded': True,
        'guidedReplayDeterministic': True,
        'targetSelectorValiditySafe': True,
    }

    for route in ROUTES:
        blind_state, blind_report, blind_champ = _run_arm(
            master_seed, prompt, route, starts[route], target, False,
            out_root / f'{route}-blind',
        )
        guided_state, guided_report, guided_champ = _run_arm(
            master_seed, prompt, route, starts[route], target, True,
            out_root / f'{route}-guided',
        )
        blind_champions.append(blind_champ)
        guided_champions.append(guided_champ)

        blind_contract = _operator_contract(blind_report)
        guided_contract = _operator_contract(guided_report)
        expected = {'totalChallengers': 20, 'nativeChallengers': 10, 'spectralChallengers': 10}
        for contract in (blind_contract, guided_contract):
            if contract['totalChallengers'] != expected['totalChallengers']:
                hard['exactBudgets'] = False
            if contract['nativeChallengers'] != 10 or contract['spectralChallengers'] != 10:
                hard['exactMixedAllocation'] = False

        blind_start = blind_state.candidates[starts[route].id]
        guided_start = guided_state.candidates[starts[route].id]
        if blind_start.genome != guided_start.genome or _phenotype_fingerprint(blind_start) != _phenotype_fingerprint(guided_start):
            hard['identicalStartsAcrossArms'] = False
        if not blind_champ.checks.get('valid', False) or not guided_champ.checks.get('valid', False):
            hard['finalsValid'] = False

        # Verify every target-selector decision involving one valid and one invalid candidate
        # chose the valid side. Search stores ids relative to the current state.
        for d in guided_state.stage_decisions:
            a = guided_state.candidates.get(d.get('aId'))
            b = guided_state.candidates.get(d.get('bId'))
            if a is None or b is None:
                continue
            av = bool(a.checks.get('valid', False)); bv = bool(b.checks.get('valid', False))
            if av != bv:
                expected_verdict = 'a' if av else 'b'
                if d.get('verdict') != expected_verdict:
                    hard['targetSelectorValiditySafe'] = False

        record = {
            'startAttempts': start_attempts[route],
            'startFingerprint': start_fingerprints[route],
            'startTargetDistance': target_distance(starts[route], target.image),
            'blind': {
                'championId': blind_champ.id,
                'championFingerprint': _phenotype_fingerprint(blind_champ),
                'operatorContract': blind_contract,
                'targetDistance': target_distance(blind_champ, target.image),
                'trajectorySignature': _trajectory_signature(blind_state),
            },
            'guided': {
                'championId': guided_champ.id,
                'championFingerprint': _phenotype_fingerprint(guided_champ),
                'operatorContract': guided_contract,
                'targetDistance': target_distance(guided_champ, target.image),
                'trajectorySignature': _trajectory_signature(guided_state),
            },
        }

        if smoke:
            replay_state, replay_report, replay_champ = _run_arm(
                master_seed, prompt, route, starts[route], target, True,
                out_root / f'{route}-guided-replay',
            )
            replay_sig = _trajectory_signature(replay_state)
            record['guidedReplaySignature'] = replay_sig
            if replay_sig != record['guided']['trajectorySignature']:
                hard['guidedReplayDeterministic'] = False
            if replay_champ.genome != guided_champ.genome or _phenotype_fingerprint(replay_champ) != _phenotype_fingerprint(guided_champ):
                hard['guidedReplayDeterministic'] = False
            if _operator_contract(replay_report) != guided_contract:
                hard['guidedReplayDeterministic'] = False

        route_records[route] = record

    blind_final = min(blind_champions, key=lambda c: target_distance(c, target.image))
    guided_final = min(guided_champions, key=lambda c: target_distance(c, target.image))
    blind_scores = heldout_scores(blind_final, target.image)
    guided_scores = heldout_scores(guided_final, target.image)
    best_start_distance = min(target_distance(c, target.image) for c in starts.values())

    for value in [*blind_scores.values(), *guided_scores.values(), best_start_distance]:
        if not math.isfinite(float(value)):
            hard['scoresFiniteAndBounded'] = False
    for name in ('coarseSoftIoU', 'multiscaleF1', 'targetDistance'):
        for scores in (blind_scores, guided_scores):
            if not (0.0 <= float(scores[name]) <= 1.0):
                hard['scoresFiniteAndBounded'] = False

    if sum(route_records[r]['blind']['operatorContract']['totalChallengers'] for r in ROUTES) != 60:
        hard['exactBudgets'] = False
    if sum(route_records[r]['guided']['operatorContract']['totalChallengers'] for r in ROUTES) != 60:
        hard['exactBudgets'] = False
    if sum(route_records[r]['blind']['operatorContract']['nativeChallengers'] for r in ROUTES) != 30 or sum(route_records[r]['blind']['operatorContract']['spectralChallengers'] for r in ROUTES) != 30:
        hard['exactMixedAllocation'] = False
    if sum(route_records[r]['guided']['operatorContract']['nativeChallengers'] for r in ROUTES) != 30 or sum(route_records[r]['guided']['operatorContract']['spectralChallengers'] for r in ROUTES) != 30:
        hard['exactMixedAllocation'] = False

    return {
        'version': 1,
        'masterSeed': int(master_seed),
        'prompt': prompt,
        'targetFingerprint': target_fp,
        'smoke': bool(smoke),
        'hardInvariants': hard,
        'routes': route_records,
        'blindFinal': {
            'route': blind_final.route,
            'id': blind_final.id,
            'fingerprint': _phenotype_fingerprint(blind_final),
            **blind_scores,
        },
        'guidedFinal': {
            'route': guided_final.route,
            'id': guided_final.id,
            'fingerprint': _phenotype_fingerprint(guided_final),
            **guided_scores,
        },
        'bestSharedStartDistance': best_start_distance,
        'deltaCoarse': guided_scores['coarseSoftIoU'] - blind_scores['coarseSoftIoU'],
        'deltaMultiscale': guided_scores['multiscaleF1'] - blind_scores['multiscaleF1'],
        'guidedObjectiveGain': best_start_distance - guided_scores['targetDistance'],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--prompt', choices=PROMPTS, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    out_root = args.output.parent / f'work-{args.seed}-{args.prompt}'
    result = run_block(args.seed, args.prompt, out_root, smoke=args.smoke)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
