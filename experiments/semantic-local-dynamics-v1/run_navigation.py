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
WM_DIR = ROOT / 'experiments' / 'semantic-world-model-navigation-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(PERCEPTUAL))
sys.path.insert(0, str(WM_DIR))
sys.path.insert(0, str(HERE))

from orbit_representation import register_orbit
register_orbit()

import core
from material_control import with_spectral_control
from rng_streams import derived_seed
import perceptual_metric as pm
import unseen_targets
import world_model as wm
import generate_pairs
import local_dynamics as ld

STREAM = 'semantic-local-dynamics-v1'
RENDER_BUDGET = 60
BEAM_SIZE = 6
ROUNDS = 3
RENDERS_PER_ROUND = 18
PROPOSALS_PER_PARENT = 64


def _genome_fingerprint(route: str, genome: dict) -> str:
    payload = json.dumps({'route': route, 'genome': genome}, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode()).hexdigest()


def _render_state(route: str, genome: dict, cid: str):
    cand = ld.quick_candidate(route, genome, cid)
    image = pm.binary_candidate_image(cand)
    visual = wm.visual_vector(image)
    return {'route': route, 'genome': genome, 'cand': cand, 'image': image, 'visual': visual, 'fingerprint': _genome_fingerprint(route, genome)}


def _exact_record(state, prompt: str, bank):
    if not state['cand'].checks.get('valid', False):
        return {'top1': False, 'targetDistance': float('inf'), 'margin': float('-inf')}
    return bank.image_record(state['image'], prompt)


def _exact_key(state, prompt: str, bank):
    if not state['cand'].checks.get('valid', False):
        return (2, float('inf'), float('inf'), state['fingerprint'])
    rec = _exact_record(state, prompt, bank)
    return (*pm.rank_key(rec), state['fingerprint'])


def _heldout(state, prompt: str, targets):
    if not state['cand'].checks.get('valid', False):
        return {'requested': prompt, 'top1': False, 'top1Id': None, 'targetF1': 0.0, 'bestOtherF1': 1.0, 'margin': -1.0}
    return pm.heldout_prototype_record(state['image'], prompt, targets)


def _breadth_pool(seed: int):
    states = []
    for route in ld.ROUTES:
        rng = random.Random(derived_seed(seed, STREAM, 'breadth-bases', route))
        for i in range(10):
            base = core.ROUTES[route]['seed'](rng)
            spectral = with_spectral_control(base, derived_seed(seed, STREAM, 'breadth-field', route, i))
            states.append(_render_state(route, base, f'B-{route}-{i}-native'))
            states.append(_render_state(route, spectral, f'B-{route}-{i}-spectral'))
    if len(states) != RENDER_BUDGET:
        raise AssertionError('breadth budget drifted')
    fp = hashlib.sha256(''.join(s['fingerprint'] for s in states).encode()).hexdigest()
    return states, fp


def _valid_start_pair(seed: int, route: str):
    rng = random.Random(derived_seed(seed, STREAM, 'starts', route))
    return generate_pairs._valid_parent_pair(
        derived_seed(seed, STREAM, 'start-parent-seed', route), route, 0, rng
    )[:2]


def _initial_states(seed: int):
    states = []
    for route in ld.ROUTES:
        native, spectral = _valid_start_pair(seed, route)
        states.append(_render_state(route, native[0], f'M-{route}-start-native'))
        states.append(_render_state(route, spectral[0], f'M-{route}-start-spectral'))
    if len(states) != BEAM_SIZE or not all(s['cand'].checks.get('valid', False) for s in states):
        raise AssertionError('invalid local-dynamics start rectangle')
    return states


def _proposal_pool(seed: int, round_index: int, beam):
    proposals = []
    for parent_index, parent in enumerate(beam):
        action_seed = derived_seed(seed, STREAM, 'mpc-actions', round_index, parent_index, parent['fingerprint'])
        actions = ld.action_set(parent['route'], parent['genome'], action_seed, PROPOSALS_PER_PARENT)
        children = [g for g, _ in actions]
        predicted, predicted_valid = ld.predict_children(
            _proposal_pool.model,
            parent['visual'], parent['route'], parent['genome'], children,
        )
        for j, ((child, family), pv, pvalid) in enumerate(zip(actions, predicted, predicted_valid)):
            proposals.append({
                'parentIndex': parent_index,
                'route': parent['route'],
                'genome': child,
                'family': int(family),
                'predictedVisual': pv,
                'predictedValid': float(pvalid),
                'fingerprint': _genome_fingerprint(parent['route'], child),
                'proposalIndex': j,
            })
    return proposals


_proposal_pool.model = None


def _local_search(seed: int, prompt: str, model, targets, bank):
    _proposal_pool.model = model
    target_visual = wm.visual_vector(next(t.image for t in targets if t.id == prompt))
    rendered = _initial_states(seed)
    seen = {s['fingerprint'] for s in rendered}
    beam = sorted(rendered, key=lambda s: _exact_key(s, prompt, bank))[:BEAM_SIZE]
    round_diagnostics = []

    for round_index in range(ROUNDS):
        proposals = _proposal_pool(seed, round_index, beam)
        scored = []
        for p in proposals:
            if p['fingerprint'] in seen:
                continue
            distance = wm.model_distance(p['predictedVisual'], target_visual)
            if not math.isfinite(distance):
                raise AssertionError('non-finite predicted target distance')
            scored.append((
                (0 if p['predictedValid'] >= 0.5 else 1, float(distance), -p['predictedValid'], p['fingerprint']),
                p,
            ))
        scored.sort(key=lambda x: x[0])
        selected = []
        selected_fp = set()
        for _, p in scored:
            if p['fingerprint'] in selected_fp:
                continue
            selected.append(p); selected_fp.add(p['fingerprint'])
            if len(selected) == RENDERS_PER_ROUND:
                break
        if len(selected) != RENDERS_PER_ROUND:
            raise AssertionError(f'only {len(selected)} unique proposals available in round {round_index}')

        new_states = []
        for rank, p in enumerate(selected):
            state = _render_state(p['route'], p['genome'], f'M-{prompt}-r{round_index}-k{rank}')
            new_states.append(state)
            seen.add(state['fingerprint'])
        rendered.extend(new_states)
        valid_pool = [s for s in beam + new_states if s['cand'].checks.get('valid', False)]
        if len(valid_pool) < BEAM_SIZE:
            raise AssertionError('too few valid rendered states for beam')
        beam = sorted(valid_pool, key=lambda s: _exact_key(s, prompt, bank))[:BEAM_SIZE]
        round_diagnostics.append({
            'round': round_index,
            'proposalCount': len(proposals),
            'eligibleUniqueProposalCount': len(scored),
            'renderedCount': len(new_states),
            'renderedValidCount': sum(bool(s['cand'].checks.get('valid', False)) for s in new_states),
            'beamRoutes': [s['route'] for s in beam],
        })

    if len(rendered) != RENDER_BUDGET:
        raise AssertionError(f'local dynamics logical renders {len(rendered)} != {RENDER_BUDGET}')
    final = sorted([s for s in rendered if s['cand'].checks.get('valid', False)], key=lambda s: _exact_key(s, prompt, bank))[0]
    return {
        'final': final,
        'logicalRenderedCount': len(rendered),
        'actualValidRenderedCount': sum(bool(s['cand'].checks.get('valid', False)) for s in rendered),
        'rounds': round_diagnostics,
        'uniqueRenderedFingerprints': len({s['fingerprint'] for s in rendered}),
    }


def _arm_record(state, prompt: str, targets, bank, logical_count: int, valid_count: int):
    selection = _exact_record(state, prompt, bank)
    heldout = _heldout(state, prompt, targets)
    return {
        'route': state['route'],
        'valid': bool(state['cand'].checks.get('valid', False)),
        'selection': selection,
        'heldout': heldout,
        'logicalRenderedCount': int(logical_count),
        'validRenderedCount': int(valid_count),
        'fingerprint': state['fingerprint'],
    }


def run(seed: int, model_path: Path, smoke: bool = False) -> dict:
    model = ld.load_model(model_path)
    model_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
    targets = unseen_targets.build_targets()
    bank = pm.PrototypeBank(targets)
    breadth_states, breadth_fp = _breadth_pool(seed)
    if smoke:
        _, breadth_fp2 = _breadth_pool(seed)
        if breadth_fp2 != breadth_fp:
            raise AssertionError('breadth replay drifted')

    concepts = {}
    hard = {
        'exactPromptRectangle': tuple(t.id for t in targets) == unseen_targets.PROMPTS,
        'exactRenderedBudgets': True,
        'breadthPromptIndependent': True,
        'finalsValid': True,
        'scoresFinite': True,
        'localUniqueRenderBudgets': True,
    }
    breadth_valid = sum(bool(s['cand'].checks.get('valid', False)) for s in breadth_states)

    for prompt in unseen_targets.PROMPTS:
        valid_breadth = [s for s in breadth_states if s['cand'].checks.get('valid', False)]
        if not valid_breadth:
            raise AssertionError('breadth pool has no valid candidates')
        breadth_final = sorted(valid_breadth, key=lambda s: _exact_key(s, prompt, bank))[0]
        local = _local_search(seed, prompt, model, targets, bank)

        breadth = _arm_record(breadth_final, prompt, targets, bank, RENDER_BUDGET, breadth_valid)
        learned = _arm_record(
            local['final'], prompt, targets, bank,
            local['logicalRenderedCount'], local['actualValidRenderedCount'],
        )
        if breadth['logicalRenderedCount'] != RENDER_BUDGET or learned['logicalRenderedCount'] != RENDER_BUDGET:
            hard['exactRenderedBudgets'] = False
        if local['uniqueRenderedFingerprints'] != RENDER_BUDGET:
            hard['localUniqueRenderBudgets'] = False
        if not breadth['valid'] or not learned['valid']:
            hard['finalsValid'] = False
        for arm in (breadth, learned):
            for section in ('selection', 'heldout'):
                for value in arm[section].values():
                    if isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isfinite(float(value)):
                        hard['scoresFinite'] = False
        concepts[prompt] = {
            'breadth60': breadth,
            'localDynamics60': learned,
            'deltaHeldoutTargetF1': float(learned['heldout']['targetF1']) - float(breadth['heldout']['targetF1']),
            'breadthHeldoutTop1': bool(breadth['heldout']['top1']),
            'localDynamicsHeldoutTop1': bool(learned['heldout']['top1']),
            'localDiagnostics': local['rounds'],
        }

    return {
        'version': 1,
        'seed': int(seed),
        'smoke': bool(smoke),
        'modelSha256': model_sha,
        'semanticTargetsUsedOnlyAtControllerEvaluation': True,
        'poolFingerprint': breadth_fp,
        'prompts': list(unseen_targets.PROMPTS),
        'renderBudgetPerArmConcept': RENDER_BUDGET,
        'hardInvariants': hard,
        'concepts': concepts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(args.seed, args.model, smoke=args.smoke), indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
