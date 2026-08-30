from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

import unseen_targets

T_CRIT_DF11_ONE_SIDED_95 = 1.795884819
EXPECTED_SEEDS = (733300011, 733300029, 733300041, 733300067, 733300079, 733300101, 733300113, 733300137, 733300151, 733300173, 733300197, 733300211)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    files = sorted(args.input_dir.rglob('*.json'))
    rows = [json.loads(p.read_text()) for p in files if not json.loads(p.read_text()).get('smoke', False)]
    by_seed = {int(r['seed']): r for r in rows}
    complete = tuple(sorted(by_seed)) == tuple(sorted(EXPECTED_SEEDS))
    if not complete:
        raise AssertionError(f'incomplete consumed rectangle: {sorted(by_seed)}')
    prompts = tuple(unseen_targets.PROMPTS)
    model_shas = {r['modelSha256'] for r in rows}
    hard = all(all(bool(v) for v in r['hardInvariants'].values()) for r in rows)

    cells = []
    concept_stats = {}
    seed_means = {}
    for seed, r in sorted(by_seed.items()):
        if tuple(r['prompts']) != prompts:
            raise AssertionError('prompt rectangle drifted')
        deltas = []
        for prompt in prompts:
            c = r['concepts'][prompt]
            delta = float(c['deltaHeldoutTargetF1'])
            deltas.append(delta)
            cells.append((seed, prompt, delta, bool(c['breadthHeldoutTop1']), bool(c['worldModelHeldoutTop1']), c))
        seed_means[str(seed)] = statistics.fmean(deltas)

    seed_values = list(seed_means.values())
    mean_delta = statistics.fmean(seed_values)
    sd = statistics.stdev(seed_values)
    lb = mean_delta - T_CRIT_DF11_ONE_SIDED_95 * sd / math.sqrt(len(seed_values))
    breadth_top1 = statistics.fmean(1.0 if x[3] else 0.0 for x in cells)
    world_top1 = statistics.fmean(1.0 if x[4] else 0.0 for x in cells)

    positive_totals = {}
    for prompt in prompts:
        pcells = [x for x in cells if x[1] == prompt]
        ds = [x[2] for x in pcells]
        world_fraction = statistics.fmean(1.0 if x[4] else 0.0 for x in pcells)
        breadth_fraction = statistics.fmean(1.0 if x[3] else 0.0 for x in pcells)
        concept_stats[prompt] = {
            'meanDeltaHeldoutTargetF1': statistics.fmean(ds),
            'breadthHeldoutTop1Fraction': breadth_fraction,
            'worldModelHeldoutTop1Fraction': world_fraction,
        }
        positive_totals[prompt] = sum(max(0.0, d) for d in ds)

    loo = {}
    for omitted in prompts:
        vals = [x[2] for x in cells if x[1] != omitted]
        loo[omitted] = statistics.fmean(vals)
    total_positive = sum(positive_totals.values())
    shares = {p: (v / total_positive if total_positive > 1e-12 else 0.0) for p, v in positive_totals.items()}

    route_attempted = {r: 0 for r in ('recurrence', 'orbit', 'filament')}
    route_valid = {r: 0 for r in route_attempted}
    for _, _, _, _, _, c in cells:
        counts = c['worldModel60']['validityCounts']
        for route in route_attempted:
            for op in ('native', 'spectral'):
                route_attempted[route] += int(counts[route][op][0])
                route_valid[route] += int(counts[route][op][1])
    route_valid_fraction = {r: route_valid[r] / route_attempted[r] if route_attempted[r] else 0.0 for r in route_attempted}
    pooled_valid = sum(route_valid.values()) / sum(route_attempted.values())

    concept_nonnegative = sum(1 for p in prompts if concept_stats[p]['meanDeltaHeldoutTargetF1'] >= 0.0)
    concept_top1_half = sum(1 for p in prompts if concept_stats[p]['worldModelHeldoutTop1Fraction'] >= 0.50)
    gates = {
        'completeRectangle': complete and len(cells) == 12 * 8,
        'hardInvariants': hard,
        'identicalFrozenModelAcrossSeeds': len(model_shas) == 1,
        'meanDeltaHeldoutTargetF1AbovePoint05': mean_delta > 0.05,
        'seedMeanDeltaOneSided95LowerBoundPositive': lb > 0.0,
        'worldModelHeldoutTop1AtLeastPoint75': world_top1 >= 0.75,
        'top1ImprovementAtLeastPoint15': world_top1 - breadth_top1 >= 0.15,
        'atLeastSixConceptsTop1AtLeastPoint50': concept_top1_half >= 6,
        'atLeastSevenConceptsNonnegativeMeanF1Delta': concept_nonnegative >= 7,
        'everyLeaveOneConceptOutMeanDeltaPositive': all(v > 0.0 for v in loo.values()),
        'noConceptDominatesPositiveDelta': max(shares.values(), default=0.0) <= 0.40,
        'pooledValidityAtLeastPoint90': pooled_valid >= 0.90,
        'everyRouteValidityAtLeastPoint85': all(v >= 0.85 for v in route_valid_fraction.values()),
    }
    decision = 'SEMANTIC_WORLD_MODEL_NAVIGATION_PROMISING' if all(gates.values()) else 'SEMANTIC_WORLD_MODEL_NAVIGATION_NOT_PROMISING'
    result = {
        'version': 1,
        'decision': decision,
        'seedCount': len(rows),
        'conceptCount': len(prompts),
        'cellCount': len(cells),
        'trainingContainsSemanticTargets': False,
        'modelSha256': next(iter(model_shas)) if len(model_shas) == 1 else sorted(model_shas),
        'meanDeltaHeldoutTargetF1': mean_delta,
        'seedMeanDeltaStdDev': sd,
        'seedMeanDeltaOneSided95LowerBound': lb,
        'breadthHeldoutTop1Fraction': breadth_top1,
        'worldModelHeldoutTop1Fraction': world_top1,
        'top1FractionDelta': world_top1 - breadth_top1,
        'concepts': concept_stats,
        'leaveOneConceptOutMeanDelta': loo,
        'positiveDeltaContributionShare': shares,
        'maxPositiveDeltaContributionShare': max(shares.values(), default=0.0),
        'seedMeanDelta': seed_means,
        'worldModelPooledValidity': pooled_valid,
        'worldModelRouteValidity': route_valid_fraction,
        'gates': gates,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
