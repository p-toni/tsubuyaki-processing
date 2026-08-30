#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

PROMPTS = ('diamond', 'spiral', 'lightning', 'leaf', 'umbrella', 'crown', 'letter-s', 'sailboat')
SEEDS = (
    732300011, 732300029, 732300041, 732300067,
    732300079, 732300101, 732300113, 732300137,
    732300151, 732300173, 732300197, 732300211,
    732300233, 732300257, 732300271, 732300293,
)
TCRIT_95_ONE_SIDED_DF15 = 1.7530503556925547


def _load_blocks(root: Path) -> list[dict]:
    blocks = []
    for path in sorted(root.rglob('*.json')):
        try:
            d = json.loads(path.read_text())
        except Exception:
            continue
        if isinstance(d, dict) and 'masterSeed' in d and 'prompt' in d and 'breadthFinal' in d:
            blocks.append(d)
    return blocks


def _mean(xs):
    return statistics.fmean(xs) if xs else float('nan')


def aggregate(blocks: list[dict]) -> dict:
    expected = {(s, p) for s in SEEDS for p in PROMPTS}
    observed = {(int(b['masterSeed']), str(b['prompt'])) for b in blocks}
    duplicates = len(observed) != len(blocks)
    complete = observed == expected and not duplicates and len(blocks) == 128

    hard_all = complete and all(all(bool(v) for v in b['hardInvariants'].values()) for b in blocks)
    exact_budgets = hard_all and all(
        b['breadthContract']['totalChallengers'] == 60
        and b['breadthContract']['nativeChallengers'] == 30
        and b['breadthContract']['spectralChallengers'] == 30
        and sum(b['adaptiveRoutes'][r]['operatorContract']['totalChallengers'] for r in ('recurrence','orbit','filament')) == 60
        and sum(b['adaptiveRoutes'][r]['operatorContract']['nativeChallengers'] for r in ('recurrence','orbit','filament')) == 30
        and sum(b['adaptiveRoutes'][r]['operatorContract']['spectralChallengers'] for r in ('recurrence','orbit','filament')) == 30
        for b in blocks
    )

    deltas = [float(b['deltaHeldoutTargetF1']) for b in blocks]
    mean_delta = _mean(deltas)
    seed_mean_delta = []
    for seed in SEEDS:
        vals = [float(b['deltaHeldoutTargetF1']) for b in blocks if int(b['masterSeed']) == seed]
        seed_mean_delta.append(_mean(vals))
    seed_sd = statistics.stdev(seed_mean_delta) if len(seed_mean_delta) > 1 else 0.0
    lb = _mean(seed_mean_delta) - TCRIT_95_ONE_SIDED_DF15 * seed_sd / math.sqrt(len(seed_mean_delta))

    adaptive_top1 = _mean([1.0 if b['adaptiveHeldoutTop1'] else 0.0 for b in blocks])
    breadth_top1 = _mean([1.0 if b['breadthHeldoutTop1'] else 0.0 for b in blocks])
    top1_delta = breadth_top1 - adaptive_top1

    concept_stats = {}
    positive_mass_total = sum(max(0.0, float(b['deltaHeldoutTargetF1'])) for b in blocks)
    max_positive_share = 0.0
    for prompt in PROMPTS:
        pb = [b for b in blocks if b['prompt'] == prompt]
        pdelta = [float(b['deltaHeldoutTargetF1']) for b in pb]
        ppos = sum(max(0.0, x) for x in pdelta)
        share = ppos / positive_mass_total if positive_mass_total > 0 else 0.0
        max_positive_share = max(max_positive_share, share)
        concept_stats[prompt] = {
            'meanDeltaHeldoutTargetF1': _mean(pdelta),
            'adaptiveTop1Fraction': _mean([1.0 if b['adaptiveHeldoutTop1'] else 0.0 for b in pb]),
            'breadthTop1Fraction': _mean([1.0 if b['breadthHeldoutTop1'] else 0.0 for b in pb]),
            'positiveDeltaContributionShare': share,
        }

    loo = {}
    for omitted in PROMPTS:
        vals = [float(b['deltaHeldoutTargetF1']) for b in blocks if b['prompt'] != omitted]
        loo[omitted] = _mean(vals)

    breadth_attempts = sum(int(b['breadthContract']['totalChallengers']) for b in blocks)
    breadth_valid = sum(int(b['breadthContract']['totalValidChallengers']) for b in blocks)
    pooled_validity = breadth_valid / breadth_attempts if breadth_attempts else 0.0
    route_validity = {}
    for route in ('recurrence','orbit','filament'):
        attempted = sum(int(b['breadthContract']['routes'][route]['attempted']) for b in blocks)
        valid = sum(int(b['breadthContract']['routes'][route]['valid']) for b in blocks)
        route_validity[route] = valid / attempted if attempted else 0.0

    gates = {
        'completePairedRectangle': complete,
        'hardInvariants': hard_all,
        'exactAttemptBudgets': exact_budgets,
        'meanF1DeltaAtLeastPoint03': mean_delta >= 0.03,
        'seedMeanOneSided95LowerBoundPositive': lb > 0.0,
        'top1ImprovementAtLeastPoint10': top1_delta >= 0.10,
        'breadthTop1AtLeastPoint60': breadth_top1 >= 0.60,
        'everyConceptBreadthTop1AtLeastPoint40': all(v['breadthTop1Fraction'] >= 0.40 for v in concept_stats.values()),
        'everyLeaveOneConceptOutMeanDeltaPositive': all(v > 0.0 for v in loo.values()),
        'breadthPooledValidityAtLeastPoint90': pooled_validity >= 0.90,
        'everyBreadthRouteValidityAtLeastPoint85': all(v >= 0.85 for v in route_validity.values()),
        'noConceptDominatesPositiveDelta': max_positive_share <= 0.30,
    }
    decision = 'SEMANTIC_BREADTH_RERANK_PROMISING' if all(gates.values()) else 'SEMANTIC_BREADTH_RERANK_NOT_PROMISING'

    return {
        'decision': decision,
        'seedCount': len(SEEDS),
        'conceptCount': len(PROMPTS),
        'blockCount': len(blocks),
        'overall': {
            'meanDeltaHeldoutTargetF1': mean_delta,
            'seedMeanDeltaStdDev': seed_sd,
            'seedMeanDeltaOneSided95LowerBound': lb,
            'adaptiveHeldoutTop1Fraction': adaptive_top1,
            'breadthHeldoutTop1Fraction': breadth_top1,
            'top1FractionDelta': top1_delta,
            'breadthPooledValidFraction': pooled_validity,
            'breadthRouteValidFraction': route_validity,
            'maxPositiveDeltaContributionShare': max_positive_share,
        },
        'concepts': concept_stats,
        'leaveOneConceptOutMeanDelta': loo,
        'seedMeanDelta': {str(s): v for s, v in zip(SEEDS, seed_mean_delta)},
        'gates': gates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    blocks = _load_blocks(args.input_root)
    result = aggregate(blocks)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
