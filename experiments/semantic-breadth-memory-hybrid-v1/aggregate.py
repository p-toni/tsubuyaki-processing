from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import targets

T_CRIT_DF11_ONE_SIDED_95 = 1.795884819
EXPECTED_SEEDS = (
    735400011, 735400029, 735400041, 735400067,
    735400079, 735400101, 735400113, 735400137,
    735400151, 735400173, 735400197, 735400211,
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

    rows = [json.loads(p.read_text()) for p in sorted(args.input_dir.rglob('semantic-*.json'))]
    rows = [r for r in rows if not r.get('smoke', False)]
    by_seed = {int(r['seed']): r for r in rows}
    if tuple(sorted(by_seed)) != tuple(sorted(EXPECTED_SEEDS)):
        raise AssertionError(f'incomplete fresh seed rectangle: {sorted(by_seed)}')

    prompts = tuple(targets.PROMPTS)
    hard = all(all(bool(v) for v in r['hardInvariants'].values()) for r in rows)
    configs = {
        (
            int(r['selectedMemoryConfig']['k']),
            float(r['selectedMemoryConfig']['actionWeight']),
            float(r['selectedMemoryConfig']['shrinkage']),
        )
        for r in rows
    }
    if len(configs) != 1:
        raise AssertionError(f'memory config drifted: {configs}')

    cells = []
    seed_mb = {}
    seed_mm = {}
    seed_meanb = {}
    for seed, row in sorted(by_seed.items()):
        if tuple(row['prompts']) != prompts:
            raise AssertionError('prompt rectangle drifted')
        if row['renderBudgetPerArmConcept'] != 60:
            raise AssertionError('render budget drifted')
        if row['breadthPrefixBudget'] != 48 or row['refinementBudget'] != 12:
            raise AssertionError('hybrid split drifted')
        d_mb = []
        d_mm = []
        d_meanb = []
        for prompt in prompts:
            c = row['concepts'][prompt]
            mb = float(c['deltaHeldoutTargetF1MemoryVsBreadth'])
            mm = float(c['deltaHeldoutTargetF1MemoryVsMean'])
            meanb = float(c['deltaHeldoutTargetF1MeanVsBreadth'])
            d_mb.append(mb)
            d_mm.append(mm)
            d_meanb.append(meanb)
            cells.append({
                'seed': seed,
                'prompt': prompt,
                'memoryVsBreadth': mb,
                'memoryVsMean': mm,
                'meanVsBreadth': meanb,
                'breadthTop1': bool(c['breadthHeldoutTop1']),
                'meanTop1': bool(c['meanHeldoutTop1']),
                'memoryTop1': bool(c['memoryHeldoutTop1']),
                'selectedProposalOverlapCount': int(c['selectedProposalOverlapCount']),
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
    proposal_overlap = statistics.fmean(c['selectedProposalOverlapCount'] / 12.0 for c in cells)

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
            'meanProposalOverlapFraction': statistics.fmean(c['selectedProposalOverlapCount'] / 12.0 for c in pc),
        }
        positive_mb[prompt] = sum(max(0.0, x) for x in mb)
        positive_meanb[prompt] = sum(max(0.0, x) for x in meanb)

    loo_mb = {
        p: statistics.fmean(c['memoryVsBreadth'] for c in cells if c['prompt'] != p)
        for p in prompts
    }
    loo_meanb = {
        p: statistics.fmean(c['meanVsBreadth'] for c in cells if c['prompt'] != p)
        for p in prompts
    }
    total_mb = sum(positive_mb.values())
    total_meanb = sum(positive_meanb.values())
    share_mb = {p: (v / total_mb if total_mb > 1e-12 else 0.0) for p, v in positive_mb.items()}
    share_meanb = {
        p: (v / total_meanb if total_meanb > 1e-12 else 0.0)
        for p, v in positive_meanb.items()
    }

    positive_memory_breadth = sum(1 for p in prompts if concept[p]['meanMemoryVsBreadthF1'] > 0.0)
    positive_memory_mean = sum(1 for p in prompts if concept[p]['meanMemoryVsMeanF1'] > 0.0)
    positive_mean_breadth = sum(1 for p in prompts if concept[p]['meanMeanVsBreadthF1'] > 0.0)

    memory_gates = {
        'completeHardInvariantRectangle': hard and len(cells) == 12 * 8,
        'identicalFrozenMemoryConfig': len(configs) == 1,
        'memoryVsBreadthMeanF1AbovePoint010': mb_mean > 0.010,
        'memoryVsBreadthSeed95LowerBoundPositive': mb_lb > 0.0,
        'memoryVsMeanMeanF1AbovePoint005': mm_mean > 0.005,
        'memoryVsMeanSeed95LowerBoundPositive': mm_lb > 0.0,
        'memoryTop1ImprovementOverBreadthAtLeastPoint05': memory_top1 - breadth_top1 >= 0.05,
        'atLeastFiveConceptsMemoryPositiveVsBreadth': positive_memory_breadth >= 5,
        'atLeastFiveConceptsMemoryPositiveVsMean': positive_memory_mean >= 5,
        'everyLeaveOneConceptOutMemoryVsBreadthPositive': all(v > 0.0 for v in loo_mb.values()),
        'noConceptDominatesMemoryPositiveGain': max(share_mb.values(), default=0.0) <= 0.50,
    }
    mean_gates = {
        'completeHardInvariantRectangle': hard and len(cells) == 12 * 8,
        'meanVsBreadthMeanF1AbovePoint010': meanb_mean > 0.010,
        'meanVsBreadthSeed95LowerBoundPositive': meanb_lb > 0.0,
        'meanTop1ImprovementOverBreadthAtLeastPoint05': mean_top1 - breadth_top1 >= 0.05,
        'atLeastFiveConceptsMeanPositiveVsBreadth': positive_mean_breadth >= 5,
        'everyLeaveOneConceptOutMeanVsBreadthPositive': all(v > 0.0 for v in loo_meanb.values()),
        'noConceptDominatesMeanPositiveGain': max(share_meanb.values(), default=0.0) <= 0.50,
    }

    memory_pass = all(memory_gates.values())
    mean_pass = all(mean_gates.values())
    if memory_pass:
        decision = 'EMPIRICAL_MEMORY_HYBRID_PROMISING'
        winning_arm = 'memoryHybrid60'
    elif mean_pass:
        decision = 'MEAN_REFINEMENT_HYBRID_PROMISING'
        winning_arm = 'meanHybrid60'
    else:
        decision = 'HYBRID_REFINEMENT_NOT_PROMISING'
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
        'selectedMemoryConfig': {
            'k': selected_k,
            'actionWeight': selected_weight,
            'shrinkage': selected_shrinkage,
        },
        'memoryVsBreadth': {
            'meanF1Delta': mb_mean,
            'seedStdDev': mb_sd,
            'seed95LowerBound': mb_lb,
        },
        'memoryVsMean': {
            'meanF1Delta': mm_mean,
            'seedStdDev': mm_sd,
            'seed95LowerBound': mm_lb,
        },
        'meanVsBreadth': {
            'meanF1Delta': meanb_mean,
            'seedStdDev': meanb_sd,
            'seed95LowerBound': meanb_lb,
        },
        'breadthHeldoutTop1Fraction': breadth_top1,
        'meanHeldoutTop1Fraction': mean_top1,
        'memoryHeldoutTop1Fraction': memory_top1,
        'meanSelectedProposalOverlapFraction': proposal_overlap,
        'concepts': concept,
        'leaveOneConceptOutMemoryVsBreadth': loo_mb,
        'leaveOneConceptOutMeanVsBreadth': loo_meanb,
        'memoryPositiveContributionShare': share_mb,
        'meanPositiveContributionShare': share_meanb,
        'seedMeanMemoryVsBreadth': seed_mb,
        'seedMeanMemoryVsMean': seed_mm,
        'seedMeanMeanVsBreadth': seed_meanb,
        'primaryMemoryGates': memory_gates,
        'secondaryMeanGates': mean_gates,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
