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
MEMORY_DIR = ROOT / 'experiments' / 'semantic-empirical-action-memory-v1'
for p in (PROTO, LOCAL_DIR, PERCEPTUAL, WM_DIR, MEMORY_DIR, HERE):
    sys.path.insert(0, str(p))

from orbit_representation import register_orbit
register_orbit()

import core
from material_control import with_spectral_control
from rng_streams import derived_seed
import empirical_memory as em
import local_dynamics as ld
import perceptual_metric as pm
import world_model as wm
import targets

STREAM = 'semantic-memory-hybrid-replication-v1'
RENDER_BUDGET = 60
PREFIX_BUDGET = 48
REFINEMENT_BUDGET = 12
PARENT_COUNT = 6
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
    return (*pm.rank_key(_exact_record(state, prompt, bank)), state['fingerprint'])


def _heldout(state, prompt: str, all_targets):
    if not state['cand'].checks.get('valid', False):
        return {
            'requested': prompt,
            'top1': False,
            'top1Id': None,
            'targetF1': 0.0,
            'bestOtherF1': 1.0,
            'margin': -1.0,
        }
    return pm.heldout_prototype_record(state['image'], prompt, all_targets)


def _breadth_pool(seed: int):
    rngs = {
        route: random.Random(derived_seed(seed, STREAM, 'breadth-bases', route))
        for route in ld.ROUTES
    }
    states = []
    for i in range(10):
        for route in ld.ROUTES:
            base = core.ROUTES[route]['seed'](rngs[route])
            spectral = with_spectral_control(
                base,
                derived_seed(seed, STREAM, 'breadth-field', route, i),
            )
            states.append(_render_state(route, base, f'B-{i}-{route}-native'))
            states.append(_render_state(route, spectral, f'B-{i}-{route}-spectral'))
    if len(states) != RENDER_BUDGET:
        raise AssertionError(f'breadth budget drifted: {len(states)}')
    if len({s['fingerprint'] for s in states}) != RENDER_BUDGET:
        raise AssertionError('breadth pool contains duplicate genomes')
    fp = hashlib.sha256(''.join(s['fingerprint'] for s in states).encode()).hexdigest()
    return states, fp


def _proposal_pool(seed: int, prompt: str, parents, memory, mode: str, target_visual):
    if mode not in MODES:
        raise KeyError(mode)
    proposals = []
    proposal_fps = []
    for parent_index, parent in enumerate(parents):
        action_seed = derived_seed(
            seed,
            STREAM,
            'hybrid-actions',
            prompt,
            parent_index,
            parent['fingerprint'],
        )
        actions = ld.action_set(
            parent['route'],
            parent['genome'],
            action_seed,
            PROPOSALS_PER_PARENT,
        )
        predicted, diags = em.predict_children(
            memory,
            parent['visual'],
            parent['route'],
            parent['genome'],
            actions,
            mode=mode,
        )
        for proposal_index, (((child, family), predicted_visual), diag) in enumerate(
            zip(zip(actions, predicted), diags)
        ):
            fp = _genome_fingerprint(parent['route'], child)
            distance = wm.model_distance(predicted_visual, target_visual)
            if not math.isfinite(distance):
                raise AssertionError('non-finite predicted target distance')
            proposals.append({
                'parentIndex': parent_index,
                'route': parent['route'],
                'genome': child,
                'family': int(family),
                'fingerprint': fp,
                'proposalIndex': proposal_index,
                'predictedTargetDistance': float(distance),
                'neighbor': diag,
            })
            proposal_fps.append(fp)
    expected = PARENT_COUNT * PROPOSALS_PER_PARENT
    if len(proposals) != expected:
        raise AssertionError(f'proposal rectangle drifted: {len(proposals)} != {expected}')
    pool_fp = hashlib.sha256(''.join(proposal_fps).encode()).hexdigest()
    return proposals, pool_fp


def _refine(seed: int, prompt: str, prefix, memory, all_targets, bank, mode: str):
    prefix_valid = [s for s in prefix if s['cand'].checks.get('valid', False)]
    if len(prefix_valid) < PARENT_COUNT:
        raise AssertionError(f'{mode}: too few valid prefix states')
    parents = sorted(prefix_valid, key=lambda s: _exact_key(s, prompt, bank))[:PARENT_COUNT]
    parent_fp = hashlib.sha256(''.join(s['fingerprint'] for s in parents).encode()).hexdigest()
    target_image = next(t.image for t in all_targets if t.id == prompt)
    target_visual = wm.visual_vector(target_image)
    proposals, proposal_pool_fp = _proposal_pool(
        seed, prompt, parents, memory, mode, target_visual
    )

    seen = {s['fingerprint'] for s in prefix}
    ranked = sorted(
        proposals,
        key=lambda p: (p['predictedTargetDistance'], p['fingerprint']),
    )
    selected = []
    selected_fp = set()
    for p in ranked:
        if p['fingerprint'] in seen or p['fingerprint'] in selected_fp:
            continue
        selected.append(p)
        selected_fp.add(p['fingerprint'])
        if len(selected) == REFINEMENT_BUDGET:
            break
    if len(selected) != REFINEMENT_BUDGET:
        raise AssertionError(f'{mode}: only {len(selected)} unique refinement proposals')

    refinement = []
    for rank, p in enumerate(selected):
        refinement.append(
            _render_state(p['route'], p['genome'], f'{mode}-{prompt}-refine-{rank}')
        )

    archive = list(prefix) + refinement
    if len(archive) != RENDER_BUDGET:
        raise AssertionError(f'{mode}: logical archive budget drifted')
    if len({s['fingerprint'] for s in archive}) != RENDER_BUDGET:
        raise AssertionError(f'{mode}: duplicate rendered state')
    valid_archive = [s for s in archive if s['cand'].checks.get('valid', False)]
    if not valid_archive:
        raise AssertionError(f'{mode}: no valid final archive states')
    final = sorted(valid_archive, key=lambda s: _exact_key(s, prompt, bank))[0]

    finite_neighbor = [
        float(p['neighbor']['nearestDistance'])
        for p in selected
        if math.isfinite(float(p['neighbor']['nearestDistance']))
    ]
    return {
        'final': final,
        'logicalRenderedCount': len(archive),
        'validRenderedCount': len(valid_archive),
        'uniqueRenderedFingerprints': len({s['fingerprint'] for s in archive}),
        'parentFingerprint': parent_fp,
        'proposalPoolFingerprint': proposal_pool_fp,
        'selectedProposalFingerprints': [p['fingerprint'] for p in selected],
        'selectedRoutes': [p['route'] for p in selected],
        'selectedMeanNearestDistance': (
            float(sum(finite_neighbor) / len(finite_neighbor)) if finite_neighbor else None
        ),
    }


def _arm_record(state, prompt: str, all_targets, bank, logical_count: int, valid_count: int):
    return {
        'route': state['route'],
        'valid': bool(state['cand'].checks.get('valid', False)),
        'selection': _exact_record(state, prompt, bank),
        'heldout': _heldout(state, prompt, all_targets),
        'logicalRenderedCount': int(logical_count),
        'validRenderedCount': int(valid_count),
        'fingerprint': state['fingerprint'],
        'genome': state['genome'],
    }


def run(seed: int, memory_path: Path, smoke: bool = False) -> dict:
    memory = em.load_memory(memory_path)
    all_targets = targets.build_targets()
    bank = pm.PrototypeBank(all_targets)
    breadth_states, breadth_fp = _breadth_pool(seed)
    if smoke:
        _, replay_fp = _breadth_pool(seed)
        if replay_fp != breadth_fp:
            raise AssertionError('breadth replay drifted')

    prefix = breadth_states[:PREFIX_BUDGET]
    prefix_fp = hashlib.sha256(''.join(s['fingerprint'] for s in prefix).encode()).hexdigest()
    route_counts = {
        route: sum(1 for s in prefix if s['route'] == route)
        for route in ld.ROUTES
    }
    breadth_valid = [s for s in breadth_states if s['cand'].checks.get('valid', False)]
    if not breadth_valid:
        raise AssertionError('breadth pool has no valid candidates')

    hard = {
        'exactPromptRectangle': tuple(t.id for t in all_targets) == targets.PROMPTS,
        'exactRenderedBudgets': True,
        'breadthPromptIndependent': True,
        'prefixExactFirst48OfBreadth60': len(prefix) == PREFIX_BUDGET,
        'prefixRouteBalanced': set(route_counts.values()) == {PREFIX_BUDGET // len(ld.ROUTES)},
        'finalsValid': True,
        'scoresFinite': True,
        'hybridUniqueRenderBudgets': True,
        'meanMemoryParentsIdentical': True,
        'meanMemoryProposalPoolsIdentical': True,
    }

    concepts = {}
    for prompt in targets.PROMPTS:
        breadth_final = sorted(breadth_valid, key=lambda s: _exact_key(s, prompt, bank))[0]
        mean_search = _refine(seed, prompt, prefix, memory, all_targets, bank, mode='mean')
        memory_search = _refine(seed, prompt, prefix, memory, all_targets, bank, mode='memory')

        if mean_search['parentFingerprint'] != memory_search['parentFingerprint']:
            hard['meanMemoryParentsIdentical'] = False
        if mean_search['proposalPoolFingerprint'] != memory_search['proposalPoolFingerprint']:
            hard['meanMemoryProposalPoolsIdentical'] = False

        breadth = _arm_record(
            breadth_final,
            prompt,
            all_targets,
            bank,
            RENDER_BUDGET,
            len(breadth_valid),
        )
        mean_arm = _arm_record(
            mean_search['final'],
            prompt,
            all_targets,
            bank,
            mean_search['logicalRenderedCount'],
            mean_search['validRenderedCount'],
        )
        memory_arm = _arm_record(
            memory_search['final'],
            prompt,
            all_targets,
            bank,
            memory_search['logicalRenderedCount'],
            memory_search['validRenderedCount'],
        )

        for arm in (breadth, mean_arm, memory_arm):
            if arm['logicalRenderedCount'] != RENDER_BUDGET:
                hard['exactRenderedBudgets'] = False
            if not arm['valid']:
                hard['finalsValid'] = False
            for section in ('selection', 'heldout'):
                for value in arm[section].values():
                    if (
                        isinstance(value, (int, float))
                        and not isinstance(value, bool)
                        and not math.isfinite(float(value))
                    ):
                        hard['scoresFinite'] = False
        if (
            mean_search['uniqueRenderedFingerprints'] != RENDER_BUDGET
            or memory_search['uniqueRenderedFingerprints'] != RENDER_BUDGET
        ):
            hard['hybridUniqueRenderBudgets'] = False

        overlap = len(
            set(mean_search['selectedProposalFingerprints'])
            & set(memory_search['selectedProposalFingerprints'])
        )
        concepts[prompt] = {
            'breadth60': breadth,
            'meanHybrid60': mean_arm,
            'memoryHybrid60': memory_arm,
            'deltaHeldoutTargetF1MemoryVsBreadth': (
                float(memory_arm['heldout']['targetF1'])
                - float(breadth['heldout']['targetF1'])
            ),
            'deltaHeldoutTargetF1MemoryVsMean': (
                float(memory_arm['heldout']['targetF1'])
                - float(mean_arm['heldout']['targetF1'])
            ),
            'deltaHeldoutTargetF1MeanVsBreadth': (
                float(mean_arm['heldout']['targetF1'])
                - float(breadth['heldout']['targetF1'])
            ),
            'breadthHeldoutTop1': bool(breadth['heldout']['top1']),
            'meanHeldoutTop1': bool(mean_arm['heldout']['top1']),
            'memoryHeldoutTop1': bool(memory_arm['heldout']['top1']),
            'refinementParentFingerprint': mean_search['parentFingerprint'],
            'proposalPoolFingerprint': mean_search['proposalPoolFingerprint'],
            'selectedProposalOverlapCount': overlap,
            'meanSelectedRoutes': mean_search['selectedRoutes'],
            'memorySelectedRoutes': memory_search['selectedRoutes'],
            'memorySelectedMeanNearestDistance': memory_search['selectedMeanNearestDistance'],
        }

    k, weight, shrinkage = em.selected_config(memory)
    return {
        'version': 1,
        'seed': int(seed),
        'smoke': bool(smoke),
        'trainingContainsSemanticTargets': False,
        'semanticTargetsUsedOnlyAfterBreadthPrefix': True,
        'selectedMemoryConfig': {
            'k': k,
            'actionWeight': weight,
            'shrinkage': shrinkage,
        },
        'breadthPoolFingerprint': breadth_fp,
        'prefixFingerprint': prefix_fp,
        'prefixRouteCounts': route_counts,
        'prompts': list(targets.PROMPTS),
        'renderBudgetPerArmConcept': RENDER_BUDGET,
        'breadthPrefixBudget': PREFIX_BUDGET,
        'refinementBudget': REFINEMENT_BUDGET,
        'refinementParentCount': PARENT_COUNT,
        'proposalsPerParent': PROPOSALS_PER_PARENT,
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
    args.output.write_text(
        json.dumps(run(args.seed, args.memory, smoke=args.smoke), indent=2, sort_keys=True) + '\n'
    )


if __name__ == '__main__':
    main()
