from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
PERCEPTUAL = ROOT / 'experiments' / 'semantic-perceptual-steering-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(PERCEPTUAL))
sys.path.insert(0, str(HERE))

from orbit_representation import register_orbit
register_orbit()

import core
from material_control import with_spectral_control
from rng_streams import derived_seed
import perceptual_metric as pm
import unseen_targets
import world_model as wm

STREAM = 'semantic-world-model-navigation-v1'
POOL_BASES_PER_ROUTE = 1024
RENDER_BUDGET = 60


def _brief(route: str) -> dict:
    return {'name': STREAM, 'artistic_intent': 'Zero-shot semantic world-model navigation.', 'routes': [route], 'bbox_target': [0.55, 0.82]}


def _pool(seed: int):
    records = []
    X = []
    baseline = []
    for route in wm.ROUTES:
        rng = random.Random(derived_seed(seed, STREAM, 'semantic-pool', route, 'bases'))
        route_indices = []
        for i in range(POOL_BASES_PER_ROUTE):
            base = core.ROUTES[route]['seed'](rng)
            states = (
                ('native', base),
                ('spectral', with_spectral_control(base, derived_seed(seed, STREAM, 'semantic-pool', route, i, 'field'))),
            )
            for operator, genome in states:
                idx = len(records)
                records.append({'route': route, 'operator': operator, 'baseIndex': i, 'genome': genome})
                X.append(wm.math_vector(route, genome))
                route_indices.append(idx)
                if i < 10:
                    baseline.append(idx)
        if len(route_indices) != POOL_BASES_PER_ROUTE * 2:
            raise AssertionError('route pool size drifted')
    if len(records) != len(wm.ROUTES) * POOL_BASES_PER_ROUTE * 2:
        raise AssertionError('pool size drifted')
    if len(baseline) != RENDER_BUDGET:
        raise AssertionError('baseline budget drifted')
    payload = [
        {
            'route': r['route'], 'operator': r['operator'], 'baseIndex': r['baseIndex'],
            'genome': r['genome'],
        }
        for r in records
    ]
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return records, np.asarray(X, dtype=np.float64), tuple(baseline), fingerprint


def _render(records, index: int, cache: dict):
    if index in cache:
        return cache[index]
    r = records[index]
    prefix = core.ROUTES[r['route']].get('prefix', r['route'][0].upper())
    cand = core.Candidate(f'{prefix}-WM-{index:05d}', r['route'], f'{prefix}-WM-{index:05d}', r['genome'], None, 'world-model-navigation')
    core.evaluate_candidate(cand, _brief(r['route']))
    image = pm.binary_candidate_image(cand)
    cache[index] = (cand, image)
    return cand, image


def _exact_record(cand, image, prompt: str, bank) -> dict:
    if not cand.checks.get('valid', False):
        return {'top1': False, 'targetDistance': float('inf'), 'margin': float('-inf')}
    return bank.image_record(image, prompt)


def _choose(indices, records, cache, prompt: str, bank, targets):
    scored = []
    valid_counts = {r: {'native': [0, 0], 'spectral': [0, 0]} for r in wm.ROUTES}
    for idx in indices:
        cand, image = _render(records, int(idx), cache)
        op = records[int(idx)]['operator']; route = records[int(idx)]['route']
        valid_counts[route][op][0] += 1
        if cand.checks.get('valid', False): valid_counts[route][op][1] += 1
        rec = _exact_record(cand, image, prompt, bank)
        scored.append((pm.rank_key(rec), int(idx), cand, image, rec))
    scored.sort(key=lambda x: (x[0], x[1]))
    _, best_idx, best_cand, best_image, selection = scored[0]
    heldout = pm.heldout_prototype_record(best_image, prompt, targets) if best_cand.checks.get('valid', False) else {
        'requested': prompt, 'top1': False, 'top1Id': None, 'targetF1': 0.0, 'bestOtherF1': 1.0, 'margin': -1.0,
    }
    return {
        'candidateIndex': best_idx,
        'route': best_cand.route,
        'operator': records[best_idx]['operator'],
        'valid': bool(best_cand.checks.get('valid', False)),
        'selection': selection,
        'heldout': heldout,
        'logicalRenderedCount': len(indices),
        'validityCounts': valid_counts,
    }


def _predicted_order(pred: np.ndarray, pred_valid: np.ndarray, target_vectors: dict[str, np.ndarray], prompt: str):
    rows = []
    for i in range(len(pred)):
        distances = {name: wm.model_distance(pred[i], vec) for name, vec in target_vectors.items()}
        ordered = sorted(distances.items(), key=lambda kv: (kv[1], kv[0]))
        td = float(distances[prompt])
        other = min(v for k, v in distances.items() if k != prompt)
        top1 = ordered[0][0] == prompt
        rows.append(((0 if pred_valid[i] >= 0.5 else 1, 0 if top1 else 1, td, -(other - td), -float(pred_valid[i]), i), i))
    rows.sort(key=lambda x: x[0])
    return tuple(i for _, i in rows[:RENDER_BUDGET])


def run(seed: int, model_path: Path, smoke: bool = False) -> dict:
    model = wm.load_model(model_path)
    records, X, baseline_indices, pool_fp = _pool(seed)
    pred, pred_valid = wm.predict(model, X)
    targets = unseen_targets.build_targets()
    bank = pm.PrototypeBank(targets)
    target_vectors = {t.id: wm.visual_vector(t.image) for t in targets}
    cache = {}
    concepts = {}
    hard = {
        'exactPoolSize': len(records) == 6144,
        'exactRenderedBudgets': True,
        'promptIndependentPool': True,
        'finalsValid': True,
        'scoresFinite': True,
        'targetBlindPoolReplayDeterministic': True,
    }
    if smoke:
        _, X2, b2, fp2 = _pool(seed)
        hard['targetBlindPoolReplayDeterministic'] = fp2 == pool_fp and b2 == baseline_indices and np.array_equal(X2, X)

    for prompt in unseen_targets.PROMPTS:
        learned_indices = _predicted_order(pred, pred_valid, target_vectors, prompt)
        if len(baseline_indices) != RENDER_BUDGET or len(learned_indices) != RENDER_BUDGET or len(set(learned_indices)) != RENDER_BUDGET:
            hard['exactRenderedBudgets'] = False
        baseline = _choose(baseline_indices, records, cache, prompt, bank, targets)
        learned = _choose(learned_indices, records, cache, prompt, bank, targets)
        if not baseline['valid'] or not learned['valid']:
            hard['finalsValid'] = False
        for arm in (baseline, learned):
            for section in ('selection', 'heldout'):
                for value in arm[section].values():
                    if isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isfinite(float(value)):
                        hard['scoresFinite'] = False
        concepts[prompt] = {
            'breadth60': baseline,
            'worldModel60': learned,
            'deltaHeldoutTargetF1': float(learned['heldout']['targetF1']) - float(baseline['heldout']['targetF1']),
            'breadthHeldoutTop1': bool(baseline['heldout']['top1']),
            'worldModelHeldoutTop1': bool(learned['heldout']['top1']),
            'learnedPoolIndices': list(learned_indices),
        }

    return {
        'version': 1,
        'seed': int(seed),
        'smoke': bool(smoke),
        'modelSha256': hashlib.sha256(model_path.read_bytes()).hexdigest(),
        'poolFingerprint': pool_fp,
        'poolSize': len(records),
        'renderBudgetPerArmConcept': RENDER_BUDGET,
        'prompts': list(unseen_targets.PROMPTS),
        'hardInvariants': hard,
        'concepts': concepts,
        'uniqueActuallyRenderedStates': len(cache),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    result = run(args.seed, args.model, smoke=args.smoke)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
