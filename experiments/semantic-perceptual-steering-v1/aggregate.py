#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

import fresh_targets

SEEDS = (
    731900011, 731900027, 731900039, 731900057,
    731900081, 731900103, 731900119, 731900143,
    731900157, 731900181, 731900207, 731900229,
)
PROMPTS = fresh_targets.PROMPTS
T_CRIT_ONE_SIDED_DF11 = 1.795884819


def _lower_bound(values: list[float]) -> float:
    if len(values) != len(SEEDS):
        raise AssertionError('master seed is the inference unit')
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    return mean - T_CRIT_ONE_SIDED_DF11 * sd / math.sqrt(len(values))


def _load(input_root: Path) -> list[dict]:
    rows = []
    for path in input_root.rglob('seed-*.json'):
        data = json.loads(path.read_text())
        if data.get('smoke'):
            continue
        rows.append(data)
    expected = {(seed, prompt) for seed in SEEDS for prompt in PROMPTS}
    found = {(int(r['masterSeed']), str(r['prompt'])) for r in rows}
    if found != expected:
        missing = sorted(expected - found)
        extra = sorted(found - expected)
        raise AssertionError(f'incomplete rectangle missing={missing} extra={extra}')
    if len(rows) != len(expected):
        raise AssertionError(f'duplicate blocks: {len(rows)} rows for {len(expected)} cells')
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = _load(args.input_root)

    hard = all(all(bool(v) for v in row['hardInvariants'].values()) for row in rows)
    exact_budget = True
    for row in rows:
        for arm in ('baseline', 'perceptual'):
            total = sum(row['routes'][r][arm]['operatorContract']['totalChallengers'] for r in ('recurrence','orbit','filament'))
            native = sum(row['routes'][r][arm]['operatorContract']['nativeChallengers'] for r in ('recurrence','orbit','filament'))
            spectral = sum(row['routes'][r][arm]['operatorContract']['spectralChallengers'] for r in ('recurrence','orbit','filament'))
            exact_budget &= total == 60 and native == 30 and spectral == 30

    seed_means = {}
    for seed in SEEDS:
        subset = [r for r in rows if int(r['masterSeed']) == seed]
        seed_means[str(seed)] = {
            'deltaHeldoutTargetF1': statistics.fmean(float(r['deltaHeldoutTargetF1']) for r in subset),
            'deltaHeldoutMargin': statistics.fmean(float(r['deltaHeldoutMargin']) for r in subset),
        }

    f1_seed_values = [seed_means[str(s)]['deltaHeldoutTargetF1'] for s in SEEDS]
    margin_seed_values = [seed_means[str(s)]['deltaHeldoutMargin'] for s in SEEDS]
    mean_delta_f1 = statistics.fmean(float(r['deltaHeldoutTargetF1']) for r in rows)
    mean_delta_margin = statistics.fmean(float(r['deltaHeldoutMargin']) for r in rows)
    f1_lb = _lower_bound(f1_seed_values)
    margin_lb = _lower_bound(margin_seed_values)

    baseline_top1 = statistics.fmean(1.0 if r['baselineHeldoutTop1'] else 0.0 for r in rows)
    perceptual_top1 = statistics.fmean(1.0 if r['perceptualHeldoutTop1'] else 0.0 for r in rows)
    baseline_selection_top1 = statistics.fmean(1.0 if r['baselineSelectionTop1'] else 0.0 for r in rows)
    perceptual_selection_top1 = statistics.fmean(1.0 if r['perceptualSelectionTop1'] else 0.0 for r in rows)

    concept_means = {}
    positive_total = sum(max(0.0, float(r['deltaHeldoutTargetF1'])) for r in rows)
    for prompt in PROMPTS:
        subset = [r for r in rows if r['prompt'] == prompt]
        pos = sum(max(0.0, float(r['deltaHeldoutTargetF1'])) for r in subset)
        concept_means[prompt] = {
            'deltaHeldoutTargetF1': statistics.fmean(float(r['deltaHeldoutTargetF1']) for r in subset),
            'deltaHeldoutMargin': statistics.fmean(float(r['deltaHeldoutMargin']) for r in subset),
            'baselineHeldoutTop1Fraction': statistics.fmean(1.0 if r['baselineHeldoutTop1'] else 0.0 for r in subset),
            'perceptualHeldoutTop1Fraction': statistics.fmean(1.0 if r['perceptualHeldoutTop1'] else 0.0 for r in subset),
            'perceptualSelectionTop1Fraction': statistics.fmean(1.0 if r['perceptualSelectionTop1'] else 0.0 for r in subset),
            'positiveF1ContributionShare': pos / positive_total if positive_total > 1e-12 else 0.0,
        }

    positive_concepts = [p for p, x in concept_means.items() if x['deltaHeldoutTargetF1'] > 0.0]
    strong_top1_concepts = [p for p, x in concept_means.items() if x['perceptualHeldoutTop1Fraction'] >= 0.5]
    max_contribution = max(x['positiveF1ContributionShare'] for x in concept_means.values())

    gates = {
        'completeHardInvariantRectangle': hard,
        'exactEqualBudget': exact_budget,
        'meanHeldoutF1GainAtLeastPoint025': mean_delta_f1 >= 0.025,
        'heldoutF1SeedLowerBoundPositive': f1_lb > 0.0,
        'meanHeldoutMarginGainPositive': mean_delta_margin > 0.0,
        'heldoutMarginSeedLowerBoundPositive': margin_lb > 0.0,
        'perceptualHeldoutTop1AtLeast60Pct': perceptual_top1 >= 0.60,
        'heldoutTop1ImprovementAtLeast20Points': perceptual_top1 - baseline_top1 >= 0.20,
        'perceptualSelectionTop1AtLeast70Pct': perceptual_selection_top1 >= 0.70,
        'atLeastSixConceptsPositiveF1': len(positive_concepts) >= 6,
        'atLeastFiveConceptsHeldoutTop1AtLeastHalf': len(strong_top1_concepts) >= 5,
        'noConceptDominatesPositiveF1': max_contribution <= 0.35,
    }
    decision = 'PERCEPTUAL_SEMANTIC_STEERING_MECHANICALLY_PROMISING' if all(gates.values()) else 'PERCEPTUAL_SEMANTIC_STEERING_NOT_READY'

    result = {
        'decision': decision,
        'blockCount': len(rows),
        'seedCount': len(SEEDS),
        'conceptCount': len(PROMPTS),
        'seeds': list(SEEDS),
        'prompts': list(PROMPTS),
        'tCriticalOneSidedDf11': T_CRIT_ONE_SIDED_DF11,
        'gates': gates,
        'overall': {
            'meanDeltaHeldoutTargetF1': mean_delta_f1,
            'heldoutF1OneSided95LowerBound': f1_lb,
            'meanDeltaHeldoutMargin': mean_delta_margin,
            'heldoutMarginOneSided95LowerBound': margin_lb,
            'baselineHeldoutTop1Fraction': baseline_top1,
            'perceptualHeldoutTop1Fraction': perceptual_top1,
            'heldoutTop1Improvement': perceptual_top1 - baseline_top1,
            'baselineSelectionTop1Fraction': baseline_selection_top1,
            'perceptualSelectionTop1Fraction': perceptual_selection_top1,
            'positiveConceptCount': len(positive_concepts),
            'strongHeldoutTop1ConceptCount': len(strong_top1_concepts),
            'maxPositiveF1ContributionShare': max_contribution,
        },
        'masterSeedMeans': seed_means,
        'conceptMeans': concept_means,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
