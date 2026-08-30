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
import fresh_targets
import perceptual_metric as pm

ROUTES = ('recurrence', 'orbit', 'filament')
STREAM = 'semantic-breadth-budget-v1'
BUDGETS = (60, 120, 240, 480)
PER_ROUTE_PREFIX = {60: 20, 120: 40, 240: 80, 480: 160}
TOTAL_PER_ROUTE = 160
PROMPTS = tuple(fresh_targets.PROMPTS)
SMOKE_SEED = 732499999


def _brief(route: str) -> dict:
    return {
        'name': STREAM,
        'artistic_intent': 'Target-blind semantic breadth budget audit.',
        'routes': [route],
        'bbox_target': [0.55, 0.82],
    }


def _valid_start(master_seed: int, route: str):
    rng = random.Random(derived_seed(master_seed, STREAM, route, 'start'))
    spec = core.ROUTES[route]
    prefix = spec.get('prefix', route[:1].upper())
    brief = _brief(route)
    for attempt in range(1, 257):
        genome = spec['seed'](rng)
        cand = core.Candidate(f'{prefix}S1', route, f'{prefix}S1', genome, None, 'start')
        core.evaluate_candidate(cand, brief)
        if cand.checks.get('valid', False):
            return cand, attempt
    raise RuntimeError(f'could not draw valid start for {route}')


def _genome_digest(cand) -> str:
    payload = {
        'route': cand.route,
        'id': cand.id,
        'genome': cand.genome,
        'valid': bool(cand.checks.get('valid', False)),
        'operator': cand.checks.get('generationOperator', 'start'),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _selection_records_for_descriptor(desc, bank: pm.PrototypeBank) -> dict[str, dict]:
    distances = {
        target_id: pm.descriptor_distance(desc, target_desc)[0]
        for target_id, target_desc in bank.descriptors.items()
    }
    ordered = sorted(distances.items(), key=lambda kv: (kv[1], kv[0]))
    ranking = [k for k, _ in ordered]
    out = {}
    for requested in PROMPTS:
        target_distance = float(distances[requested])
        best_other = min(float(v) for k, v in distances.items() if k != requested)
        out[requested] = {
            'requested': requested,
            'top1': ranking[0] == requested,
            'top1Id': ranking[0],
            'targetDistance': target_distance,
            'bestOtherDistance': best_other,
            'margin': best_other - target_distance,
            'ranking': ranking,
        }
    return out


def _verify_selection_equivalence(image, records: dict[str, dict], bank: pm.PrototypeBank) -> float:
    max_delta = 0.0
    for prompt in PROMPTS:
        ref = bank.image_record(image, prompt)
        got = records[prompt]
        if ref['top1'] != got['top1'] or ref['top1Id'] != got['top1Id'] or ref['ranking'] != got['ranking']:
            return float('inf')
        for key in ('targetDistance', 'bestOtherDistance', 'margin'):
            max_delta = max(max_delta, abs(float(ref[key]) - float(got[key])))
    return max_delta


def _generate_archive(master_seed: int, bank: pm.PrototypeBank):
    starts = {}; start_attempts = {}
    for route in ROUTES:
        starts[route], start_attempts[route] = _valid_start(master_seed, route)

    challengers = {r: [] for r in ROUTES}
    attempted = {'native': 0, 'spectral': 0}
    valid = {'native': 0, 'spectral': 0}
    route_valid_prefix = {r: [] for r in ROUTES}
    signature_items = [('start', r, _genome_digest(starts[r])) for r in ROUTES]
    selection_records = {}
    candidates = {}
    equivalence_deltas = []

    # Shared starts are available at every budget.
    for route in ROUTES:
        key = f'{route}:{starts[route].id}'
        image = pm.binary_candidate_image(starts[route])
        records = _selection_records_for_descriptor(pm.descriptor(image), bank)
        selection_records[key] = records
        candidates[key] = starts[route]
        equivalence_deltas.append(_verify_selection_equivalence(image, records, bank))

    for route in ROUTES:
        spec = core.ROUTES[route]
        prefix = spec.get('prefix', route[:1].upper())
        rng = random.Random(derived_seed(master_seed, STREAM, route, 'breadth-draws'))
        brief = _brief(route)
        valid_so_far = 0
        for pair_index in range(TOTAL_PER_ROUTE // 2):
            for operator in ('native', 'spectral'):
                i = len(challengers[route])
                base = spec['seed'](rng)
                if operator == 'native':
                    genome = base
                else:
                    genome = with_spectral_control(
                        base, derived_seed(master_seed, STREAM, route, pair_index, 'field')
                    )
                cand = core.Candidate(
                    f'{prefix}B{i+1:03d}', route, f'{prefix}B{i+1:03d}', genome, None, 'breadth'
                )
                core.evaluate_candidate(cand, brief)
                cand.checks['generationOperator'] = operator
                challengers[route].append(cand)
                attempted[operator] += 1
                if cand.checks.get('valid', False):
                    valid[operator] += 1
                    valid_so_far += 1
                    key = f'{route}:{cand.id}'
                    image = pm.binary_candidate_image(cand)
                    records = _selection_records_for_descriptor(pm.descriptor(image), bank)
                    selection_records[key] = records
                    candidates[key] = cand
                    if len(equivalence_deltas) < 9:
                        equivalence_deltas.append(_verify_selection_equivalence(image, records, bank))
                route_valid_prefix[route].append(valid_so_far)
                signature_items.append((route, i, operator, _genome_digest(cand)))

    signature = hashlib.sha256(
        json.dumps(signature_items, separators=(',', ':'), sort_keys=False).encode()
    ).hexdigest()
    max_equivalence_delta = max(equivalence_deltas) if equivalence_deltas else float('inf')
    return {
        'starts': starts,
        'startAttempts': start_attempts,
        'challengers': challengers,
        'selectionRecords': selection_records,
        'candidates': candidates,
        'attempted': attempted,
        'valid': valid,
        'routeValidPrefix': route_valid_prefix,
        'archiveSignature': signature,
        'maxSelectionEquivalenceDelta': max_equivalence_delta,
    }


def _budget_contract(archive, budget: int) -> dict:
    n = PER_ROUTE_PREFIX[budget]
    route_stats = {}
    total_valid = 0
    for route in ROUTES:
        prefix = archive['challengers'][route][:n]
        rv = sum(1 for c in prefix if c.checks.get('valid', False))
        total_valid += rv
        native = sum(1 for c in prefix if c.checks.get('generationOperator') == 'native')
        spectral = sum(1 for c in prefix if c.checks.get('generationOperator') == 'spectral')
        route_stats[route] = {
            'attempted': n,
            'valid': rv,
            'validFraction': rv / n,
            'nativeAttempted': native,
            'spectralAttempted': spectral,
        }
    return {
        'budget': budget,
        'perRouteAttempts': n,
        'totalAttempts': budget,
        'totalValid': total_valid,
        'pooledValidFraction': total_valid / budget,
        'nativeAttempted': sum(v['nativeAttempted'] for v in route_stats.values()),
        'spectralAttempted': sum(v['spectralAttempted'] for v in route_stats.values()),
        'routes': route_stats,
    }


def _pool_keys(archive, budget: int) -> list[str]:
    n = PER_ROUTE_PREFIX[budget]
    keys = []
    for route in ROUTES:
        start = archive['starts'][route]
        keys.append(f'{route}:{start.id}')
        for cand in archive['challengers'][route][:n]:
            if cand.checks.get('valid', False):
                keys.append(f'{route}:{cand.id}')
    return keys


def run_archive(master_seed: int, smoke: bool = False) -> dict:
    targets = fresh_targets.build_targets()
    target_by_id = {t.id: t for t in targets}
    bank = pm.PrototypeBank(targets)
    archive = _generate_archive(master_seed, bank)

    hard = {
        'exactTotalArchiveAttempts': sum(archive['attempted'].values()) == 480,
        'exactFullOperatorSplit': archive['attempted'] == {'native': 240, 'spectral': 240},
        'exactNestedBudgets': True,
        'nestedPools': True,
        'targetBlindReplayDeterministic': True,
        'selectionMetricExactlyEquivalent': archive['maxSelectionEquivalenceDelta'] <= 1e-12,
        'scoresFinite': True,
    }

    budget_results = {}
    previous_keys = set()
    for budget in BUDGETS:
        contract = _budget_contract(archive, budget)
        expected_half = budget // 2
        if contract['totalAttempts'] != budget or contract['nativeAttempted'] != expected_half or contract['spectralAttempted'] != expected_half:
            hard['exactNestedBudgets'] = False
        for route in ROUTES:
            expected_route_half = PER_ROUTE_PREFIX[budget] // 2
            rc = contract['routes'][route]
            if rc['nativeAttempted'] != expected_route_half or rc['spectralAttempted'] != expected_route_half:
                hard['exactNestedBudgets'] = False

        keys = _pool_keys(archive, budget)
        key_set = set(keys)
        if previous_keys and not previous_keys.issubset(key_set):
            hard['nestedPools'] = False
        previous_keys = key_set

        concepts = {}
        for prompt in PROMPTS:
            best_key = min(
                keys,
                key=lambda k: pm.rank_key(archive['selectionRecords'][k][prompt]),
            )
            cand = archive['candidates'][best_key]
            selection = archive['selectionRecords'][best_key][prompt]
            image = pm.binary_candidate_image(cand)
            heldout = pm.heldout_prototype_record(image, prompt, targets)
            for section in (selection, heldout):
                for value in section.values():
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        if not math.isfinite(float(value)):
                            hard['scoresFinite'] = False
            concepts[prompt] = {
                'selectedRoute': cand.route,
                'selectedId': cand.id,
                'selectedOperator': cand.checks.get('generationOperator', 'start'),
                'selectionTop1': bool(selection['top1']),
                'selectionTargetDistance': float(selection['targetDistance']),
                'selectionMargin': float(selection['margin']),
                'heldoutTop1': bool(heldout['top1']),
                'heldoutTop1Id': heldout['top1Id'],
                'heldoutTargetF1': float(heldout['targetF1']),
                'heldoutMargin': float(heldout['margin']),
            }
        budget_results[str(budget)] = {
            'contract': contract,
            'concepts': concepts,
        }

    if smoke:
        replay = _generate_archive(master_seed, bank)
        if replay['archiveSignature'] != archive['archiveSignature']:
            hard['targetBlindReplayDeterministic'] = False
        if replay['attempted'] != archive['attempted'] or replay['valid'] != archive['valid']:
            hard['targetBlindReplayDeterministic'] = False

    return {
        'version': 1,
        'masterSeed': int(master_seed),
        'smoke': bool(smoke),
        'targetBlindGeneration': True,
        'archiveSignature': archive['archiveSignature'],
        'startAttempts': archive['startAttempts'],
        'maxSelectionEquivalenceDelta': archive['maxSelectionEquivalenceDelta'],
        'hardInvariants': hard,
        'budgets': budget_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    result = run_archive(args.seed, smoke=args.smoke)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
