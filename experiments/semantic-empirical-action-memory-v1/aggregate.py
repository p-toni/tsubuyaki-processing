from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WM_DIR = ROOT / 'experiments' / 'semantic-world-model-navigation-v1'
sys.path.insert(0, str(WM_DIR))
import unseen_targets

T_CRIT_DF11_ONE_SIDED_95 = 1.795884819
EXPECTED_SEEDS = (
    735300011, 735300029, 735300041, 735300067,
    735300079, 735300101, 735300113, 735300137,
    735300151, 735300173, 735300197, 735300211,
)


def _lb(values: list[float]) -> tuple[float, float, float]:
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    lb = mean - T_CRIT_DF11_ONE_SIDED_95 * sd / math.sqrt(len(values))
    return mean, sd, lb


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    files = sorted(args.input_dir.rglob('semantic-*.json'))
    rows = [json.loads(p.read_text()) for p in files]
    rows = [r for r in rows if not r.get('smoke', False)]
    by_seed = {int(r['seed']): r for r in rows}
    if tuple(sorted(by_seed)) != tuple(sorted(EXPECTED_SEEDS)):
        raise AssertionError(f'incomplete consumed rectangle: {sorted(by_seed)}')
    prompts = tuple(unseen_targets.PROMPTS)
    hard = all(all(bool(v) for v in r['hardInvariants'].values()) for r in rows)
    configs = {(int(r['selectedMemoryConfig']['k']), float(r['selectedMemoryConfig']['actionWeight']), float(r['selectedMemoryConfig']['shrinkage'])) for r in rows}
    if len(configs) != 1:
        raise AssertionError(f'memory config drifted: {configs}')

    cells = []
    seed_mb = {}; seed_mm = {}; seed_meanb = {}
    for seed, r in sorted(by_seed.items()):
        if tuple(r['prompts']) != prompts:
            raise AssertionError('prompt rectangle drifted')
        d_mb = []; d_mm = []; d_meanb = []
        for prompt in prompts:
            c = r['concepts'][prompt]
            mb = float(c['deltaHeldoutTargetF1MemoryVsBreadth'])
            mm = float(c['deltaHeldoutTargetF1MemoryVsMean'])
            meanb = float(c['deltaHeldoutTargetF1MeanVsBreadth'])
            d_mb.append(mb); d_mm.append(mm); d_meanb.append(meanb)
            cells.append({
                'seed': seed,
                'prompt': prompt,
                'memoryVsBreadth': mb,
                'memoryVsMean': mm,
                'meanVsBreadth': meanb,
                'breadthTop1': bool(c['breadthHeldoutTop1']),
                'meanTop1': bool(c['meanHeldoutTop1']),
                'memoryTop1': bool(c['memoryHeldoutTop1']),
            })
        seed_mb[str(seed)] = statistics.fmean(d_mb)
        seed_mm[str(seed)] = statistics.fmean(d_mm)
        seed_meanb[str(seed)] = statistics.fmean(d_meanb)

    mb_mean, mb_sd, mb_lb = _lb(list(seed_mb.values()))
    mm_mean, mm_sd, mm_lb = _lb(list(seed_mm.values()))
    meanb_mean, meanb_sd, meanb_lb = _lb(list(seed_meanb.values()))
    breadth_top1 = statistics.fmean(1.0 if c['breadthTop1'] else 0.0 for c in cells)
    mean_top1 = statistics.fmean(1.0 if c['meanTop1'] else 0.0 for c in cells)
    memory_top1 = statistics.fmean(1.0 if c['memoryTop1'] else 0.0 for c in cells)

    concept = {}
    positive_mb = {}
    positive_meanb = {}
    for prompt in prompts:
        pc = [c for c in cells if c['prompt'] == prompt]
        mb = [c['memoryVsBreadth'] for c in pc]
        mm = [c['memoryVsMean'] for c in pc]
        meanb = [c['meanVsBreadth'] for c in pc]
        concept[prompt] = {
            'meanMemoryVsBreadthF1': statistics.fmean(mb),
            'meanMemoryVsMeanF1': statistics.fmean(mm),
            'meanMeanVsBreadthF1': statistics.fmean(meanb),
            'breadthTop1Fraction': statistics.fmean(1.0 if c['breadthTop1'] else 0.0 for c in pc),
            'meanTop1Fraction': statistics.fmean(1.0 if c['meanTop1'] else 0.0 for c in pc),
            'memoryTop1Fraction': statistics.fmean(1.0 if c['memoryTop1'] else 0.0 for c in pc),
        }
        positive_mb[prompt] = sum(max(0.0, x) for x in mb)
        positive_meanb[prompt] = sum(max(0.0, x) for x in meanb)

    loo_mb = {p: statistics.fmean(c['memoryVsBreadth'] for c in cells if c['prompt'] != p) for p in prompts}
    loo_meanb = {p: statistics.fmean(c['meanVsBreadth'] for c in cells if c['prompt'] != p) for p in prompts}
    total_mb = sum(positive_mb.values())
    total_meanb = sum(positive_meanb.values())
    share_mb = {p: (v / total_mb if total_mb > 1e-12 else 0.0) for p, v in positive_mb.items()}
    share_meanb = {p: (v / total_meanb if total_meanb > 1e-12 else 0.0) for p, v in positive_meanb.items()}

    memory_positive_breadth = sum(1 for p in prompts if concept[p]['meanMemoryVsBreadthF1'] > 0.0)
    memory_positive_mean = sum(1 for p in prompts if concept[p]['meanMemoryVsMeanF1'] > 0.0)
    memory_top1_half = sum(1 for p in prompts if concept[p]['memoryTop1Fraction'] >= 0.50)
    mean_positive_breadth = sum(1 for p in prompts if concept[p]['meanMeanVsBreadthF1'] > 0.0)
    mean_top1_half = sum(1 for p in prompts if concept[p]['meanTop1Fraction'] >= 0.50)

    primary_gates = {
        'completeHardInvariantRectangle': hard and len(cells) == 12 * 8,
        'identicalFrozenMemoryConfig': len(configs) == 1,
        'memoryVsBreadthMeanF1AbovePoint05': mb_mean > 0.05,
        'memoryVsBreadthSeed95LowerBoundPositive': mb_lb > 0.0,
        'memoryVsMeanMeanF1AbovePoint015': mm_mean > 0.015,
        'memoryVsMeanSeed95LowerBoundPositive': mm_lb > 0.0,
        'memoryHeldoutTop1AtLeastPoint75': memory_top1 >= 0.75,
        'memoryTop1ImprovementOverBreadthAtLeastPoint15': memory_top1 - breadth_top1 >= 0.15,
        'atLeastSixConceptsMemoryPositiveVsBreadth': memory_positive_breadth >= 6,
        'atLeastFiveConceptsMemoryPositiveVsMean': memory_positive_mean >= 5,
        'atLeastSixConceptsMemoryTop1AtLeastPoint50': memory_top1_half >= 6,
        'everyLeaveOneConceptOutMemoryVsBreadthPositive': all(v > 0.0 for v in loo_mb.values()),
        'noConceptDominatesMemoryPositiveGain': max(share_mb.values(), default=0.0) <= 0.40,
    }
    mean_gates = {
        'completeHardInvariantRectangle': hard and len(cells) == 12 * 8,
        'meanVsBreadthMeanF1AbovePoint05': meanb_mean > 0.05,
        'meanVsBreadthSeed95LowerBoundPositive': meanb_lb > 0.0,
        'meanHeldoutTop1AtLeastPoint75': mean_top1 >= 0.75,
        'meanTop1ImprovementOverBreadthAtLeastPoint15': mean_top1 - breadth_top1 >= 0.15,
        'atLeastSixConceptsMeanPositiveVsBreadth': mean_positive_breadth >= 6,
        'atLeastSixConceptsMeanTop1AtLeastPoint50': mean_top1_half >= 6,
        'everyLeaveOneConceptOutMeanVsBreadthPositive': all(v > 0.0 for v in loo_meanb.values()),
        'noConceptDominatesMeanPositiveGain': max(share_meanb.values(), default=0.0) <= 0.40,
    }
    memory_pass = all(primary_gates.values())
    mean_pass = all(mean_gates.values())
    if memory_pass:
        decision = 'EMPIRICAL_ACTION_MEMORY_SEMANTIC_NAVIGATION_PROMISING'
        winning_arm = 'empiricalMemory60'
    elif mean_pass:
        decision = 'ROUTE_ACTION_MEAN_SEMANTIC_NAVIGATION_PROMISING'
        winning_arm = 'meanDynamics60'
    else:
        decision = 'EMPIRICAL_ACTION_NAVIGATION_NOT_PROMISING'
        winning_arm = None

    selected_k, selected_weight, selected_shrinkage = next(iter(configs))
    result = {
        'version': 1,
        'decision': decision,
        'winningArmForRecognition': winning_arm,
        'trainingContainsSemanticTargets': False,
        'semanticEvidenceConsumed': True,
        'seedCount': len(rows),
        'conceptCount': len(prompts),
        'cellCount': len(cells),
        'selectedMemoryConfig': {'k': selected_k, 'actionWeight': selected_weight, 'shrinkage': selected_shrinkage},
        'memoryVsBreadth': {'meanF1Delta': mb_mean, 'seedStdDev': mb_sd, 'seed95LowerBound': mb_lb},
        'memoryVsMean': {'meanF1Delta': mm_mean, 'seedStdDev': mm_sd, 'seed95LowerBound': mm_lb},
        'meanVsBreadth': {'meanF1Delta': meanb_mean, 'seedStdDev': meanb_sd, 'seed95LowerBound': meanb_lb},
        'breadthHeldoutTop1Fraction': breadth_top1,
        'meanHeldoutTop1Fraction': mean_top1,
        'memoryHeldoutTop1Fraction': memory_top1,
        'concepts': concept,
        'leaveOneConceptOutMemoryVsBreadth': loo_mb,
        'leaveOneConceptOutMeanVsBreadth': loo_meanb,
        'memoryPositiveContributionShare': share_mb,
        'meanPositiveContributionShare': share_meanb,
        'seedMeanMemoryVsBreadth': seed_mb,
        'seedMeanMemoryVsMean': seed_mm,
        'seedMeanMeanVsBreadth': seed_meanb,
        'primaryMemoryGates': primary_gates,
        'secondaryMeanGates': mean_gates,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
