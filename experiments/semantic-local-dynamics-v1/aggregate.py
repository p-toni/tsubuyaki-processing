from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

import unseen_targets

T_CRIT_DF11_ONE_SIDED_95 = 1.795884819
EXPECTED_SEEDS = (
    734300011, 734300029, 734300041, 734300067, 734300079, 734300101,
    734300113, 734300137, 734300151, 734300173, 734300197, 734300211,
)


def aggregate(input_dir: Path) -> dict:
    files = sorted(input_dir.rglob('*.json'))
    rows = []
    for path in files:
        row = json.loads(path.read_text())
        if not row.get('smoke', False):
            rows.append(row)
    by_seed = {int(r['seed']): r for r in rows}
    complete = tuple(sorted(by_seed)) == tuple(sorted(EXPECTED_SEEDS))
    if not complete:
        raise AssertionError(f'incomplete consumed rectangle: {sorted(by_seed)}')

    prompts = tuple(unseen_targets.PROMPTS)
    hard = all(all(bool(v) for v in r['hardInvariants'].values()) for r in rows)
    model_shas = {str(r['modelSha256']) for r in rows}
    cells = []
    seed_means = {}
    for seed, row in sorted(by_seed.items()):
        if tuple(row['prompts']) != prompts:
            raise AssertionError('prompt rectangle drifted')
        deltas = []
        for prompt in prompts:
            c = row['concepts'][prompt]
            d = float(c['deltaHeldoutTargetF1'])
            deltas.append(d)
            cells.append((
                seed,
                prompt,
                d,
                bool(c['breadthHeldoutTop1']),
                bool(c['localDynamicsHeldoutTop1']),
                c,
            ))
        seed_means[str(seed)] = statistics.fmean(deltas)

    seed_values = list(seed_means.values())
    mean_delta = statistics.fmean(seed_values)
    sd = statistics.stdev(seed_values)
    lb = mean_delta - T_CRIT_DF11_ONE_SIDED_95 * sd / math.sqrt(len(seed_values))
    breadth_top1 = statistics.fmean(1.0 if c[3] else 0.0 for c in cells)
    local_top1 = statistics.fmean(1.0 if c[4] else 0.0 for c in cells)

    concept_stats = {}
    positive_totals = {}
    for prompt in prompts:
        pcells = [c for c in cells if c[1] == prompt]
        deltas = [c[2] for c in pcells]
        concept_stats[prompt] = {
            'meanDeltaHeldoutTargetF1': statistics.fmean(deltas),
            'breadthHeldoutTop1Fraction': statistics.fmean(1.0 if c[3] else 0.0 for c in pcells),
            'localDynamicsHeldoutTop1Fraction': statistics.fmean(1.0 if c[4] else 0.0 for c in pcells),
        }
        positive_totals[prompt] = sum(max(0.0, d) for d in deltas)

    total_positive = sum(positive_totals.values())
    shares = {p: (v / total_positive if total_positive > 1e-12 else 0.0) for p, v in positive_totals.items()}
    concept_positive = sum(1 for p in prompts if concept_stats[p]['meanDeltaHeldoutTargetF1'] > 0.0)
    concept_top1_half = sum(1 for p in prompts if concept_stats[p]['localDynamicsHeldoutTop1Fraction'] >= 0.50)

    gates = {
        'completeRectangle': complete and len(cells) == 12 * 8,
        'hardInvariants': hard,
        'identicalFrozenModelAcrossSeeds': len(model_shas) == 1,
        'meanDeltaHeldoutTargetF1AbovePoint05': mean_delta > 0.05,
        'seedMeanDeltaOneSided95LowerBoundPositive': lb > 0.0,
        'localDynamicsHeldoutTop1AtLeastPoint75': local_top1 >= 0.75,
        'top1ImprovementAtLeastPoint15': local_top1 - breadth_top1 >= 0.15,
        'atLeastSixConceptsPositiveMeanF1Delta': concept_positive >= 6,
        'atLeastSixConceptsTop1AtLeastPoint50': concept_top1_half >= 6,
        'noConceptDominatesPositiveDelta': max(shares.values(), default=0.0) <= 0.40,
        'allSelectedFinalCandidatesValid': all(c[5]['breadth60']['valid'] and c[5]['localDynamics60']['valid'] for c in cells),
    }
    decision = 'LOCAL_DYNAMICS_SEMANTIC_NAVIGATION_PROMISING' if all(gates.values()) else 'LOCAL_DYNAMICS_SEMANTIC_NAVIGATION_NOT_PROMISING'
    return {
        'version': 1,
        'decision': decision,
        'trainingContainsSemanticTargets': False,
        'calibrationContainsSemanticTargets': False,
        'semanticTargetRole': 'external-controller-evaluation-only',
        'seedCount': len(rows),
        'conceptCount': len(prompts),
        'cellCount': len(cells),
        'modelSha256': next(iter(model_shas)) if len(model_shas) == 1 else sorted(model_shas),
        'meanDeltaHeldoutTargetF1': mean_delta,
        'seedMeanDeltaStdDev': sd,
        'seedMeanDeltaOneSided95LowerBound': lb,
        'breadthHeldoutTop1Fraction': breadth_top1,
        'localDynamicsHeldoutTop1Fraction': local_top1,
        'top1FractionDelta': local_top1 - breadth_top1,
        'concepts': concept_stats,
        'positiveDeltaContributionShare': shares,
        'maxPositiveDeltaContributionShare': max(shares.values(), default=0.0),
        'seedMeanDelta': seed_means,
        'gates': gates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(aggregate(args.input_dir), indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
