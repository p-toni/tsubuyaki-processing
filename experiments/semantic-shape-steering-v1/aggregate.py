#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from semantic_targets import PROMPTS

SEEDS = (125003, 125011, 125017, 125029, 125047, 125053, 125063, 125087, 125101, 125113)
T_CRIT = 1.8331129326536335


def _one_sided_lb(values: list[float]) -> float:
    if len(values) < 2:
        return float('-inf')
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    return mean - T_CRIT * sd / math.sqrt(len(values))


def _load_blocks(root: Path) -> list[dict]:
    blocks = []
    for path in sorted(root.rglob('*.json')):
        try:
            d = json.loads(path.read_text())
        except Exception:
            continue
        if isinstance(d, dict) and 'masterSeed' in d and 'prompt' in d and 'deltaCoarse' in d and not d.get('smoke', False):
            d['_path'] = str(path)
            blocks.append(d)
    return blocks


def aggregate(root: Path) -> dict:
    blocks = _load_blocks(root)
    expected = {(s, p) for s in SEEDS for p in PROMPTS}
    got = {(int(d['masterSeed']), str(d['prompt'])) for d in blocks}
    duplicates = []
    seen = set()
    for d in blocks:
        key = (int(d['masterSeed']), str(d['prompt']))
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    missing = sorted(expected - got)
    extra = sorted(got - expected)

    hard_complete = len(blocks) == len(expected) and not missing and not extra and not duplicates
    hard_invariants = hard_complete and all(all(bool(v) for v in d['hardInvariants'].values()) for d in blocks)

    if not hard_complete:
        return {
            'decision': 'SEMANTIC_SHAPE_STEERING_NOT_READY',
            'completeRectangle': False,
            'blockCount': len(blocks),
            'missing': missing,
            'extra': extra,
            'duplicates': duplicates,
        }

    by_seed = {s: [d for d in blocks if int(d['masterSeed']) == s] for s in SEEDS}
    by_prompt = {p: [d for d in blocks if d['prompt'] == p] for p in PROMPTS}

    seed_coarse = [statistics.fmean(float(d['deltaCoarse']) for d in by_seed[s]) for s in SEEDS]
    seed_multi = [statistics.fmean(float(d['deltaMultiscale']) for d in by_seed[s]) for s in SEEDS]
    prompt_coarse = {p: statistics.fmean(float(d['deltaCoarse']) for d in by_prompt[p]) for p in PROMPTS}
    prompt_multi = {p: statistics.fmean(float(d['deltaMultiscale']) for d in by_prompt[p]) for p in PROMPTS}

    mean_coarse = statistics.fmean(float(d['deltaCoarse']) for d in blocks)
    mean_multi = statistics.fmean(float(d['deltaMultiscale']) for d in blocks)
    mean_objective_gain = statistics.fmean(float(d['guidedObjectiveGain']) for d in blocks)
    positive_objective_fraction = sum(float(d['guidedObjectiveGain']) > 0 for d in blocks) / len(blocks)

    coarse_positive_total = sum(max(0.0, v) for v in prompt_coarse.values())
    multi_positive_total = sum(max(0.0, v) for v in prompt_multi.values())
    coarse_share = {
        p: (max(0.0, prompt_coarse[p]) / coarse_positive_total if coarse_positive_total > 1e-15 else 0.0)
        for p in PROMPTS
    }
    multi_share = {
        p: (max(0.0, prompt_multi[p]) / multi_positive_total if multi_positive_total > 1e-15 else 0.0)
        for p in PROMPTS
    }

    positive_both = [p for p in PROMPTS if prompt_coarse[p] > 0 and prompt_multi[p] > 0]
    gates = {
        'completeHardInvariantRectangle': bool(hard_invariants),
        'meanCoarsePositive': mean_coarse > 0,
        'coarseSeedLowerBoundPositive': _one_sided_lb(seed_coarse) > 0,
        'meanMultiscalePositive': mean_multi > 0,
        'multiscaleSeedLowerBoundPositive': _one_sided_lb(seed_multi) > 0,
        'atLeastSixConceptsPositiveOnBoth': len(positive_both) >= 6,
        'meanGuidedObjectiveGainAbovePoint01': mean_objective_gain > 0.01,
        'guidedObjectivePositiveAtLeast65Pct': positive_objective_fraction >= 0.65,
        'coarseContributionNotDominated': max(coarse_share.values(), default=1.0) <= 0.40,
        'multiscaleContributionNotDominated': max(multi_share.values(), default=1.0) <= 0.40,
    }
    decision = 'SEMANTIC_SHAPE_STEERING_MECHANICALLY_PROMISING' if all(gates.values()) else 'SEMANTIC_SHAPE_STEERING_NOT_READY'

    return {
        'decision': decision,
        'completeRectangle': hard_complete,
        'blockCount': len(blocks),
        'seedCount': len(SEEDS),
        'conceptCount': len(PROMPTS),
        'gates': gates,
        'overall': {
            'meanDeltaCoarse': mean_coarse,
            'coarseOneSided95LowerBound': _one_sided_lb(seed_coarse),
            'meanDeltaMultiscale': mean_multi,
            'multiscaleOneSided95LowerBound': _one_sided_lb(seed_multi),
            'meanGuidedObjectiveGain': mean_objective_gain,
            'guidedObjectivePositiveFraction': positive_objective_fraction,
            'positiveBothConceptCount': len(positive_both),
            'positiveBothConcepts': positive_both,
        },
        'masterSeedMeans': {
            str(s): {
                'deltaCoarse': seed_coarse[i],
                'deltaMultiscale': seed_multi[i],
            }
            for i, s in enumerate(SEEDS)
        },
        'conceptMeans': {
            p: {
                'deltaCoarse': prompt_coarse[p],
                'deltaMultiscale': prompt_multi[p],
                'guidedObjectiveGain': statistics.fmean(float(d['guidedObjectiveGain']) for d in by_prompt[p]),
                'coarsePositiveContributionShare': coarse_share[p],
                'multiscalePositiveContributionShare': multi_share[p],
                'guidedTargetDistance': statistics.fmean(float(d['guidedFinal']['targetDistance']) for d in by_prompt[p]),
                'blindTargetDistance': statistics.fmean(float(d['blindFinal']['targetDistance']) for d in by_prompt[p]),
                'guidedCoarseSoftIoU': statistics.fmean(float(d['guidedFinal']['coarseSoftIoU']) for d in by_prompt[p]),
                'blindCoarseSoftIoU': statistics.fmean(float(d['blindFinal']['coarseSoftIoU']) for d in by_prompt[p]),
                'guidedMultiscaleF1': statistics.fmean(float(d['guidedFinal']['multiscaleF1']) for d in by_prompt[p]),
                'blindMultiscaleF1': statistics.fmean(float(d['blindFinal']['multiscaleF1']) for d in by_prompt[p]),
            }
            for p in PROMPTS
        },
        'tCriticalOneSidedDf9': T_CRIT,
        'seeds': list(SEEDS),
        'prompts': list(PROMPTS),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = aggregate(args.input_root)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
