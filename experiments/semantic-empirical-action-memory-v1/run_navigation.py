from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
LOCAL_DIR = ROOT / 'experiments' / 'semantic-local-dynamics-v1'
PERCEPTUAL = ROOT / 'experiments' / 'semantic-perceptual-steering-v1'
WM_DIR = ROOT / 'experiments' / 'semantic-world-model-navigation-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(LOCAL_DIR))
sys.path.insert(0, str(PERCEPTUAL))
sys.path.insert(0, str(WM_DIR))
sys.path.insert(0, str(HERE))

from orbit_representation import register_orbit
register_orbit()

import core
from material_control import with_spectral_control
from rng_streams import derived_seed
import empirical_memory as em
import generate_pairs
import local_dynamics as ld
import perceptual_metric as pm
import unseen_targets
import world_model as wm

RENDER_BUDGET = 60
BEAM_SIZE = 6
ROUNDS = 3
RENDERS_PER_ROUND = 18
PROPOSALS_PER_PARENT = 64
MODES = ('mean', 'memory')


def _genome_fingerprint(route: str, genome: dict) -> str:
    payload = json.dumps({'route': route, 'genome': genome}, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode()).hexdigest()


def _render_state(route: str, genome: dict, cid: str):
    cand = ld.quick_candidate(route, genome, cid)
    image = pm.binary_candidate_image(cand)
    visual = wm.visual_vector(image)
    return {
        'route': route,
        'genome': genome,
        'cand': cand,
        'image': image,
        'visual': visual,
        'fingerprint': _genome_fingerprint(route, genome),
    }


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
        rng = random.Random(derived_seed(seed, em.STREAM, 'breadth-bases', route))
        for i in range(10):
            base = core.ROUTES[route]['seed'](rng)
            spectral = with_spectral_control(base, derived_seed(seed, em.STREAM, 'breadth-field', route, i))
            states.append(_render_state(route, base, f'B-{route}-{i}-native'))
            states.append(_render_state(route, spectral, f'B-{route}-{i}-spectral'))
    if len(states) != RENDER_BUDGET:
        raise AssertionError('breadth budget drifted')
    fp = hashlib.sha256(''.join(s['fingerprint'] for s in states).encode()).hexdigest()
    return states, fp


def _valid_start_pair(seed: int, route: str):
    rng = random.Random(derived_seed(seed, em.STREAM, 'starts', route))
    return generate_pairs._valid_parent_pair(
        derived_seed(seed, em.STREAM, 'start-parent-seed', route), route, 0, rng
    )[:2]


def _initial_states(seed: int):
    states = []
    for route in ld.ROUTES:
        native, spectral = _valid_start_pair(seed, route)
        states.append(_render_state(route, native[0], f'G-{route}-start-native'))
        states.append(_render_state(route, spectral[0], f'G-{route}-start-spectral'))
    if len(states) != BEAM_SIZE or not all(s['cand'].checks.get('valid', False) for s in states):
        raise AssertionError('invalid empirical-navigation start rectangle')
    return states


def _proposal_pool(seed: int, round_index: int, beam, memory, mode: str):
    proposals = []
    for parent_index, parent in enumerate(beam):
        action_seed = derived_seed(seed, em.STREAM, 'mpc-actions', round_index, parent_index, parent['fingerprint'])
        actions = ld.action_set(parent['route'], parent['genome'], action_seed, PROPOSALS_PER_PARENT)
        predicted, diags = em.predict_children(memory, parent['visual'], parent['route'], parent['genome'], actions, mode=mode)
        for j, (((child, family), pv), diag) in enumerate(zip(zip(actions, predicted), diags)):
            proposals.append({
                'parentIndex': parent_index,
                'route': parent['route'],
                'genome': child,
                'family': int(family),
                'predictedVisual': pv,
                'fingerprint': _genome_fingerprint(parent['route'], child),
                'proposalIndex': j,
                'neighbor': diag,
            })
    return proposals


def _guided_search(seed: int, prompt: str, memory, targets, bank, mode: str):
    if mode not in MODES:
        raise KeyError(mode)
    target_visual = wm.visual_vector(next(t.image for t in targets if t.id == prompt))
    rendered = _initial_states(seed)
    start_fingerprint = hashlib.sha256(''.join(s['fingerprint'] for s in rendered).encode()).hexdigest()
    seen = {s['fingerprint'] for s in rendered}
    beam = sorted(rendered, key=lambda s: _exact_key(s, prompt, bank))[:BEAM_SIZE]
    rounds = []

    for round_index in range(ROUNDS):
        proposals = _proposal_pool(seed, round_index, beam, memory, mode)
        scored = []
        for p in proposals:
            if p['fingerprint'] in seen:
                continue
            distance = wm.model_distance(p['predictedVisual'], target_visual)
            if not math.isfinite(distance):
                raise AssertionError('non-finite predicted target distance')
            scored.append(((float(distance), p['fingerprint']), p))
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
            raise AssertionError(f'{mode} only {len(selected)} unique proposals in round {round_index}')

        new_states = []
        for rank, p in enumerate(selected):
            state = _render_state(p['route'], p['genome'], f'{mode}-{prompt}-r{round_index}-k{rank}')
            new_states.append(state)
            seen.add(state['fingerprint'])
        rendered.extend(new_states)
        valid_pool = [s for s in beam + new_states if s['cand'].checks.get('valid', False)]
        if len(valid_pool) < BEAM_SIZE:
            raise AssertionError(f'{mode}: too few valid rendered states for beam')
        beam = sorted(valid_pool, key=lambda s: _exact_key(s, prompt, bank))[:BEAM_SIZE]
        finite_neighbor = [p['neighbor']['nearestDistance'] for p in selected if math.isfinite(float(p['neighbor']['nearestDistance']))]
        rounds.append({
            'round': round_index,
            'proposalCount': len(proposals),
            'eligibleUniqueProposalCount': len(scored),
            'renderedCount': len(new_states),
            'renderedValidCount': sum(bool(s['cand'].checks.get('valid', False)) for s in new_states),
            'beamRoutes': [s['route'] for s in beam],
            'selectedMeanNearestDistance': float(sum(finite_neighbor) / len(finite_neighbor)) if finite_neighbor else None,
        })

    if len(rendered) != RENDER_BUDGET:
        raise AssertionError(f'{mode} logical renders {len(rendered)} != {RENDER_BUDGET}')
    final = sorted([s for s in rendered if s['cand'].checks.get('valid', False)], key=lambda s: _exact_key(s, prompt, bank))[0]
    return {
        'final': final,
        'logicalRenderedCount': len(rendered),
        'actualValidRenderedCount': sum(bool(s['cand'].checks.get('valid', False)) for s in rendered),
        'rounds': rounds,
        'uniqueRenderedFingerprints': len({s['fingerprint'] for s in rendered}),
        'startFingerprint': start_fingerprint,
    }


def _arm_record(state, prompt: str, targets, bank, logical_count: int, valid_count: int):
    return {
        'route': state['route'],
        'valid': bool(state['cand'].checks.get('valid', False)),
        'selection': _exact_record(state, prompt, bank),
        'heldout': _heldout(state, prompt, targets),
        'logicalRenderedCount': int(logical_count),
        'validRenderedCount': int(valid_count),
        'fingerprint': state['fingerprint'],
        'genome': state['genome'],
    }


def run(seed: int, memory_path: Path, smoke: bool = False) -> dict:
    memory = em.load_memory(memory_path)
    targets = unseen_targets.build_targets()
    bank = pm.PrototypeBank(targets)
    breadth_states, breadth_fp = _breadth_pool(seed)
    if smoke:
        _, breadth_fp2 = _breadth_pool(seed)
        if breadth_fp2 != breadth_fp:
            raise AssertionError('breadth replay drifted')
    breadth_valid = [s for s in breadth_states if s['cand'].checks.get('valid', False)]
    if not breadth_valid:
        raise AssertionError('breadth pool has no valid candidates')

    concepts = {}
    hard = {
        'exactPromptRectangle': tuple(t.id for t in targets) == unseen_targets.PROMPTS,
        'exactRenderedBudgets': True,
        'breadthPromptIndependent': True,
        'finalsValid': True,
        'scoresFinite': True,
        'guidedUniqueRenderBudgets': True,
        'meanMemoryStartsIdentical': True,
    }

    for prompt in unseen_targets.PROMPTS:
        breadth_final = sorted(breadth_valid, key=lambda s: _exact_key(s, prompt, bank))[0]
        mean_search = _guided_search(seed, prompt, memory, targets, bank, mode='mean')
        memory_search = _guided_search(seed, prompt, memory, targets, bank, mode='memory')
        if mean_search['startFingerprint'] != memory_search['startFingerprint']:
            hard['meanMemoryStartsIdentical'] = False

        breadth = _arm_record(breadth_final, prompt, targets, bank, RENDER_BUDGET, len(breadth_valid))
        mean_arm = _arm_record(mean_search['final'], prompt, targets, bank, mean_search['logicalRenderedCount'], mean_search['actualValidRenderedCount'])
        memory_arm = _arm_record(memory_search['final'], prompt, targets, bank, memory_search['logicalRenderedCount'], memory_search['actualValidRenderedCount'])
        for arm in (breadth, mean_arm, memory_arm):
            if arm['logicalRenderedCount'] != RENDER_BUDGET:
                hard['exactRenderedBudgets'] = False
            if not arm['valid']:
                hard['finalsValid'] = False
            for section in ('selection', 'heldout'):
                for value in arm[section].values():
                    if isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isfinite(float(value)):
                        hard['scoresFinite'] = False
        if mean_search['uniqueRenderedFingerprints'] != RENDER_BUDGET or memory_search['uniqueRenderedFingerprints'] != RENDER_BUDGET:
            hard['guidedUniqueRenderBudgets'] = False

        concepts[prompt] = {
            'breadth60': breadth,
            'meanDynamics60': mean_arm,
            'empiricalMemory60': memory_arm,
            'deltaHeldoutTargetF1MemoryVsBreadth': float(memory_arm['heldout']['targetF1']) - float(breadth['heldout']['targetF1']),
            'deltaHeldoutTargetF1MemoryVsMean': float(memory_arm['heldout']['targetF1']) - float(mean_arm['heldout']['targetF1']),
            'deltaHeldoutTargetF1MeanVsBreadth': float(mean_arm['heldout']['targetF1']) - float(breadth['heldout']['targetF1']),
            'breadthHeldoutTop1': bool(breadth['heldout']['top1']),
            'meanHeldoutTop1': bool(mean_arm['heldout']['top1']),
            'memoryHeldoutTop1': bool(memory_arm['heldout']['top1']),
            'meanDiagnostics': mean_search['rounds'],
            'memoryDiagnostics': memory_search['rounds'],
        }

    k, weight, shrinkage = em.selected_config(memory)
    return {
        'version': 1,
        'seed': int(seed),
        'smoke': bool(smoke),
        'semanticTargetsUsedOnlyAtControllerEvaluation': True,
        'trainingContainsSemanticTargets': False,
        'selectedMemoryConfig': {'k': k, 'actionWeight': weight, 'shrinkage': shrinkage},
        'poolFingerprint': breadth_fp,
        'prompts': list(unseen_targets.PROMPTS),
        'renderBudgetPerArmConcept': RENDER_BUDGET,
        'hardInvariants': hard,
        'concepts': concepts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--memory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(args.seed, args.memory, smoke=args.smoke), indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
