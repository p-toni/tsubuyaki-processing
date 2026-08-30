#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

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
import perceptual_metric

ROUTES = ('recurrence', 'orbit', 'filament')
STREAM = 'semantic-accessible-capacity-v1'
DRAWS_PER_ROUTE = 256
PROMPTS = tuple(fresh_targets.PROMPTS)


def _brief(route: str) -> dict:
    return {
        'name': STREAM,
        'artistic_intent': 'Target-blind accessible semantic capacity audit.',
        'routes': [route],
        'bbox_target': [0.55, 0.82],
    }


def _target_cache(targets) -> dict[str, dict]:
    cache = {}
    for target in targets:
        field = perceptual_metric.normalize_soft(target.image)
        mask = field > 0.08
        cache[target.id] = {
            'mask': mask,
            'count': max(1, int(mask.sum())),
            'dilated': [perceptual_metric._dilate(mask, r) for r in perceptual_metric.HELDOUT_RADII],
        }
    return cache


def _score_image(image, target_cache: dict[str, dict]) -> tuple[str, dict[str, float]]:
    field = perceptual_metric.normalize_soft(image)
    mask = field > 0.08
    count = max(1, int(mask.sum()))
    dilated = [perceptual_metric._dilate(mask, r) for r in perceptual_metric.HELDOUT_RADII]
    scores = {}
    if not mask.any():
        scores = {prompt: 0.0 for prompt in target_cache}
    else:
        for prompt, target in target_cache.items():
            f1s = []
            for candidate_dilated, target_dilated in zip(dilated, target['dilated']):
                precision = float(np.count_nonzero(mask & target_dilated)) / count
                recall = float(np.count_nonzero(target['mask'] & candidate_dilated)) / target['count']
                f1s.append(2.0 * precision * recall / max(1e-12, precision + recall))
            scores[prompt] = float(sum(f1s) / len(f1s))
    top1 = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return top1, scores


def _verify_equivalence(image, targets, scores: dict[str, float]) -> float:
    max_delta = 0.0
    for target in targets:
        reference = perceptual_metric.heldout_prototype_record(image, target.id, targets)
        delta = abs(float(reference['targetF1']) - float(scores[target.id]))
        max_delta = max(max_delta, delta)
    return max_delta


def run_archive(master_seed: int) -> dict:
    targets = fresh_targets.build_targets()
    target_cache = _target_cache(targets)
    if tuple(target_cache) != PROMPTS:
        raise AssertionError('prompt ordering drifted')

    stats = {
        p: {
            'top1Found': False,
            'bestTop1TargetF1': 0.0,
            'bestAnyTargetF1': 0.0,
            'bestTop1Route': None,
            'bestTop1Operator': None,
        }
        for p in PROMPTS
    }
    attempted = {'native': 0, 'spectral': 0}
    valid = {'native': 0, 'spectral': 0}
    route_attempted = {r: {'native': 0, 'spectral': 0} for r in ROUTES}
    route_valid = {r: {'native': 0, 'spectral': 0} for r in ROUTES}
    top1_counts = {p: 0 for p in PROMPTS}
    equivalence_deltas = []

    for route in ROUTES:
        rng = random.Random(derived_seed(master_seed, STREAM, route, 'native-draws'))
        spec = core.ROUTES[route]
        prefix = spec.get('prefix', route[:1].upper())
        brief = _brief(route)
        verified_for_route = 0
        for i in range(DRAWS_PER_ROUTE):
            base_genome = spec['seed'](rng)
            candidates = [
                ('native', base_genome),
                ('spectral', with_spectral_control(base_genome, derived_seed(master_seed, STREAM, route, i, 'field'))),
            ]
            for operator, genome in candidates:
                attempted[operator] += 1
                route_attempted[route][operator] += 1
                cand = core.Candidate(
                    f'{prefix}-{i:03d}-{operator}', route, f'{prefix}-{i:03d}', genome, None, 'capacity-audit'
                )
                core.evaluate_candidate(cand, brief)
                if not cand.checks.get('valid', False):
                    continue
                valid[operator] += 1
                route_valid[route][operator] += 1
                image = perceptual_metric.binary_candidate_image(cand)
                top1, scores = _score_image(image, target_cache)
                if verified_for_route < 2:
                    equivalence_deltas.append(_verify_equivalence(image, targets, scores))
                    verified_for_route += 1
                top1_counts[top1] += 1
                for prompt, score in scores.items():
                    if score > stats[prompt]['bestAnyTargetF1']:
                        stats[prompt]['bestAnyTargetF1'] = score
                    if top1 == prompt and score > stats[prompt]['bestTop1TargetF1']:
                        stats[prompt]['top1Found'] = True
                        stats[prompt]['bestTop1TargetF1'] = score
                        stats[prompt]['bestTop1Route'] = route
                        stats[prompt]['bestTop1Operator'] = operator

    total_attempts = sum(attempted.values())
    total_valid = sum(valid.values())
    route_summaries = {}
    for route in ROUTES:
        ra = sum(route_attempted[route].values())
        rv = sum(route_valid[route].values())
        route_summaries[route] = {
            'attempted': ra,
            'valid': rv,
            'validFraction': rv / ra,
            'nativeAttempted': route_attempted[route]['native'],
            'spectralAttempted': route_attempted[route]['spectral'],
            'nativeValid': route_valid[route]['native'],
            'spectralValid': route_valid[route]['spectral'],
        }

    max_equivalence_delta = max(equivalence_deltas) if equivalence_deltas else float('inf')
    hard = {
        'exactTotalAttempts': total_attempts == 1536,
        'exactOperatorSplit': attempted == {'native': 768, 'spectral': 768},
        'exactRouteAttempts': all(x['attempted'] == 512 for x in route_summaries.values()),
        'finiteScores': all(
            0.0 <= float(v[k]) <= 1.0
            for v in stats.values()
            for k in ('bestTop1TargetF1', 'bestAnyTargetF1')
        ),
        'fastHeldoutExactlyEquivalent': max_equivalence_delta <= 1e-12,
    }

    return {
        'version': 1,
        'masterSeed': int(master_seed),
        'targetBlindGeneration': True,
        'drawsPerRoute': DRAWS_PER_ROUTE,
        'attempted': attempted,
        'valid': valid,
        'totalAttempts': total_attempts,
        'totalValid': total_valid,
        'pooledValidFraction': total_valid / total_attempts,
        'routes': route_summaries,
        'top1Counts': top1_counts,
        'concepts': stats,
        'maxHeldoutEquivalenceDelta': max_equivalence_delta,
        'hardInvariants': hard,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run_archive(args.seed)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
