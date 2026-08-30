#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
OLD_DIR = ROOT / 'experiments' / 'semantic-shape-steering-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(OLD_DIR))

from orbit_representation import register_orbit
register_orbit()

import core
from rng_streams import derived_seed
from search_engine import MIXED_1D_V1, run_search_from_starts

import fresh_targets
import perceptual_metric as pm


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OLD_STEERING = _load('semantic_shape_v1_steering_baseline', OLD_DIR / 'steering.py')

ROUTES = ('recurrence', 'orbit', 'filament')
STREAM = 'semantic-perceptual-steering-v1'
SMOKE_SEED = 731899999


def _brief(route: str) -> dict:
    return {
        'name': STREAM,
        'artistic_intent': 'Semantic-shape objective comparison; artistic quality is not evaluated here.',
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
    counts = report['generationOperatorCounts']; valid = report['generationOperatorValidCounts']
    return {
        'totalChallengers': int(counts.get('native', 0)) + int(counts.get('spectral', 0)),
        'nativeChallengers': int(counts.get('native', 0)),
        'spectralChallengers': int(counts.get('spectral', 0)),
        'nativeValid': int(valid.get('native', 0)),
        'spectralValid': int(valid.get('spectral', 0)),
    }


def _run_arm(master_seed: int, prompt: str, route: str, start, selector, out_dir: Path):
    search_seed = derived_seed(master_seed, STREAM, prompt, route, 'search')
    state, report = run_search_from_starts(
        _brief(route), search_seed, out_dir, [copy.deepcopy(start)], selector=selector,
    )
    champ = state.candidates[report['provisionalChampion']]
    if not champ.checks.get('valid', False):
        raise AssertionError('final route champion is invalid')
    return state, report, champ


def _semantic_record(cand, prompt: str, bank: pm.PrototypeBank, targets) -> dict:
    image = pm.binary_candidate_image(cand)
    selection = bank.image_record(image, prompt)
    heldout = pm.heldout_prototype_record(image, prompt, targets)
    return {
        'selection': selection,
        'heldout': heldout,
        'sparseTargetDistance': OLD_STEERING.target_distance(cand, {t.id: t for t in targets}[prompt].image),
    }


def run_block(master_seed: int, prompt: str, out_root: Path, smoke: bool = False) -> dict:
    if prompt not in fresh_targets.PROMPTS:
        raise ValueError(f'prompt must be one of {fresh_targets.PROMPTS}')
    targets = fresh_targets.build_targets()
    target_by_id = {t.id: t for t in targets}
    target = target_by_id[prompt]
    bank = pm.PrototypeBank(targets)

    starts = {}; start_attempts = {}; start_fingerprints = {}
    for route in ROUTES:
        start, attempts = _valid_start(master_seed, prompt, route)
        starts[route] = start
        start_attempts[route] = attempts
        start_fingerprints[route] = _phenotype_fingerprint(start)

    hard = {
        'identicalStartsAcrossArms': True,
        'exactBudgets': True,
        'exactMixedAllocation': True,
        'finalsValid': True,
        'scoresFinite': True,
        'perceptualReplayDeterministic': True,
        'perceptualSelectorValiditySafe': True,
    }
    route_records = {}
    baseline_champs = []
    perceptual_champs = []

    for route in ROUTES:
        baseline_selector = OLD_STEERING.TargetGeometrySelector(target.image)
        perceptual_selector = pm.PrototypePerceptualSelector(prompt, bank)
        bs, br, bc = _run_arm(master_seed, prompt, route, starts[route], baseline_selector, out_root / f'{route}-baseline')
        ps, pr, pc = _run_arm(master_seed, prompt, route, starts[route], perceptual_selector, out_root / f'{route}-perceptual')
        baseline_champs.append(bc); perceptual_champs.append(pc)

        bcontract = _operator_contract(br); pcontract = _operator_contract(pr)
        for contract in (bcontract, pcontract):
            if contract['totalChallengers'] != 20:
                hard['exactBudgets'] = False
            if contract['nativeChallengers'] != 10 or contract['spectralChallengers'] != 10:
                hard['exactMixedAllocation'] = False

        bstart = bs.candidates[starts[route].id]; pstart = ps.candidates[starts[route].id]
        if bstart.genome != pstart.genome or _phenotype_fingerprint(bstart) != _phenotype_fingerprint(pstart):
            hard['identicalStartsAcrossArms'] = False
        if not bc.checks.get('valid', False) or not pc.checks.get('valid', False):
            hard['finalsValid'] = False

        for d in ps.stage_decisions:
            a = ps.candidates.get(d.get('aId')); b = ps.candidates.get(d.get('bId'))
            if a is None or b is None:
                continue
            av = bool(a.checks.get('valid', False)); bv = bool(b.checks.get('valid', False))
            if av != bv:
                expected = 'a' if av else 'b'
                if d.get('verdict') != expected:
                    hard['perceptualSelectorValiditySafe'] = False

        route_records[route] = {
            'startAttempts': start_attempts[route],
            'startFingerprint': start_fingerprints[route],
            'baseline': {
                'championId': bc.id,
                'fingerprint': _phenotype_fingerprint(bc),
                'operatorContract': bcontract,
                'trajectorySignature': _trajectory_signature(bs),
                **_semantic_record(bc, prompt, bank, targets),
            },
            'perceptual': {
                'championId': pc.id,
                'fingerprint': _phenotype_fingerprint(pc),
                'operatorContract': pcontract,
                'trajectorySignature': _trajectory_signature(ps),
                **_semantic_record(pc, prompt, bank, targets),
            },
        }

        if smoke:
            replay_selector = pm.PrototypePerceptualSelector(prompt, bank)
            rs, rr, rc = _run_arm(master_seed, prompt, route, starts[route], replay_selector, out_root / f'{route}-perceptual-replay')
            if _trajectory_signature(rs) != route_records[route]['perceptual']['trajectorySignature']:
                hard['perceptualReplayDeterministic'] = False
            if _phenotype_fingerprint(rc) != route_records[route]['perceptual']['fingerprint']:
                hard['perceptualReplayDeterministic'] = False
            if _operator_contract(rr) != pcontract:
                hard['perceptualReplayDeterministic'] = False

    baseline_final = min(baseline_champs, key=lambda c: OLD_STEERING.target_distance(c, target.image))
    perceptual_final = min(perceptual_champs, key=lambda c: pm.rank_key(pm.candidate_record(c, prompt, bank)))
    baseline_record = _semantic_record(baseline_final, prompt, bank, targets)
    perceptual_record = _semantic_record(perceptual_final, prompt, bank, targets)

    for record in (baseline_record, perceptual_record):
        for section in ('selection', 'heldout'):
            for key, value in record[section].items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if not math.isfinite(float(value)):
                        hard['scoresFinite'] = False

    for arm in ('baseline', 'perceptual'):
        total = sum(route_records[r][arm]['operatorContract']['totalChallengers'] for r in ROUTES)
        native = sum(route_records[r][arm]['operatorContract']['nativeChallengers'] for r in ROUTES)
        spectral = sum(route_records[r][arm]['operatorContract']['spectralChallengers'] for r in ROUTES)
        if total != 60:
            hard['exactBudgets'] = False
        if native != 30 or spectral != 30:
            hard['exactMixedAllocation'] = False

    return {
        'version': 1,
        'masterSeed': int(master_seed),
        'prompt': prompt,
        'smoke': bool(smoke),
        'targetFingerprint': hashlib.sha256(target.image.tobytes()).hexdigest(),
        'hardInvariants': hard,
        'routes': route_records,
        'baselineFinal': {
            'route': baseline_final.route,
            'id': baseline_final.id,
            'fingerprint': _phenotype_fingerprint(baseline_final),
            **baseline_record,
        },
        'perceptualFinal': {
            'route': perceptual_final.route,
            'id': perceptual_final.id,
            'fingerprint': _phenotype_fingerprint(perceptual_final),
            **perceptual_record,
        },
        'deltaHeldoutTargetF1': perceptual_record['heldout']['targetF1'] - baseline_record['heldout']['targetF1'],
        'deltaHeldoutMargin': perceptual_record['heldout']['margin'] - baseline_record['heldout']['margin'],
        'baselineHeldoutTop1': bool(baseline_record['heldout']['top1']),
        'perceptualHeldoutTop1': bool(perceptual_record['heldout']['top1']),
        'baselineSelectionTop1': bool(baseline_record['selection']['top1']),
        'perceptualSelectionTop1': bool(perceptual_record['selection']['top1']),
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
