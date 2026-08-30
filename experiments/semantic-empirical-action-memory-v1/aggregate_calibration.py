from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

CALIBRATION_SEEDS = (735200011, 735200029, 735200041, 735200067, 735200079, 735200101)


def _metrics(tasks, mode: str) -> dict:
    return {
        'goalInPredictedTop4Fraction': sum(1 for t in tasks if t[mode]['goalInPredictedTop4']) / len(tasks),
        'predictedTop1TrueTopQuartileFraction': sum(1 for t in tasks if t[mode]['predictedTop1TrueTopQuartile']) / len(tasks),
        'meanPredictedTop1TrueRegret': sum(float(t[mode]['predictedTop1TrueRegret']) for t in tasks) / len(tasks),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    rows = [json.loads(p.read_text()) for p in sorted(args.input_dir.rglob('calibration-*.json'))]
    by_seed = {int(r['seed']): r for r in rows}
    if tuple(sorted(by_seed)) != CALIBRATION_SEEDS:
        raise AssertionError(f'calibration seed rectangle drifted: {sorted(by_seed)}')
    configs = {(int(r['selectedConfig']['k']), float(r['selectedConfig']['actionWeight']), float(r['selectedConfig']['shrinkage'])) for r in rows}
    if len(configs) != 1:
        raise AssertionError(f'memory config drifted: {configs}')

    hard = all(all(bool(v) for v in r['hardInvariants'].values()) for r in rows)
    pair_rows = sum(int(r['pairStats']['rowCount']) for r in rows)
    element_count = sum(int(r['pairStats']['elementCount']) for r in rows)
    memory_sse = sum(float(r['pairStats']['memorySSE']) for r in rows)
    mean_sse = sum(float(r['pairStats']['meanSSE']) for r in rows)
    zero_sse = sum(float(r['pairStats']['zeroSSE']) for r in rows)
    memory_mse = memory_sse / element_count
    mean_mse = mean_sse / element_count
    zero_mse = zero_sse / element_count
    improvement = 1.0 - memory_mse / mean_mse

    route = {}
    for route_name in ('recurrence', 'orbit', 'filament'):
        e = sum(int(r['pairStats']['route'][route_name]['elementCount']) for r in rows)
        ms = sum(float(r['pairStats']['route'][route_name]['memorySSE']) for r in rows)
        bs = sum(float(r['pairStats']['route'][route_name]['meanSSE']) for r in rows)
        zs = sum(float(r['pairStats']['route'][route_name]['zeroSSE']) for r in rows)
        route[route_name] = {
            'memoryMSE': ms / e,
            'routeActionMeanMSE': bs / e,
            'zeroDeltaMSE': zs / e,
            'improvement': 1.0 - (ms / e) / (bs / e),
        }

    tasks = [task for r in rows for task in r['retrievalTasks']]
    if len(tasks) != len(CALIBRATION_SEEDS) * 96:
        raise AssertionError(f'retrieval task rectangle drifted: {len(tasks)}')
    memory_metric = _metrics(tasks, 'memory')
    mean_metric = _metrics(tasks, 'mean')
    route_retrieval = {}
    for route_name in ('recurrence', 'orbit', 'filament'):
        rt = [t for t in tasks if t['route'] == route_name]
        route_retrieval[route_name] = {'memory': _metrics(rt, 'memory'), 'mean': _metrics(rt, 'mean')}

    nearest_mean = sum(float(r['retrievalNeighborDiagnostics']['meanNearestDistance']) for r in rows) / len(rows)
    nearest_max = max(float(r['retrievalNeighborDiagnostics']['maxNearestDistance']) for r in rows)
    selected_k, selected_weight, selected_shrinkage = next(iter(configs))

    regret_improvement_fraction = (
        (mean_metric['meanPredictedTop1TrueRegret'] - memory_metric['meanPredictedTop1TrueRegret'])
        / mean_metric['meanPredictedTop1TrueRegret']
    )
    route_topq_wins = sum(
        1 for v in route_retrieval.values()
        if v['memory']['predictedTop1TrueTopQuartileFraction'] > v['mean']['predictedTop1TrueTopQuartileFraction']
    )
    route_regret_wins = sum(
        1 for v in route_retrieval.values()
        if v['memory']['meanPredictedTop1TrueRegret'] < v['mean']['meanPredictedTop1TrueRegret']
    )
    gates = {
        'allShardHardInvariants': hard,
        'calibrationContainsNoSemanticTargets': all(not bool(r['calibrationContainsSemanticTargets']) for r in rows),
        'exactCalibrationSeeds': tuple(sorted(by_seed)) == CALIBRATION_SEEDS,
        'exactCalibrationPairRows': pair_rows == len(CALIBRATION_SEEDS) * 384,
        'exactRetrievalTaskCount': len(tasks) == len(CALIBRATION_SEEDS) * 96,
        'identicalFrozenMemoryConfig': len(configs) == 1,
        'overallMSEImprovementOverMeanNonnegative': improvement >= 0.0,
        'memoryPseudoGoalTop4AtLeastPoint20': memory_metric['goalInPredictedTop4Fraction'] >= 0.20,
        'memoryTop4ImprovementOverMeanAtLeastPoint03': memory_metric['goalInPredictedTop4Fraction'] - mean_metric['goalInPredictedTop4Fraction'] >= 0.03,
        'memoryPredictedTop1TrueTopQuartileAtLeastPoint45': memory_metric['predictedTop1TrueTopQuartileFraction'] >= 0.45,
        'memoryTopQuartileImprovementOverMeanAtLeastPoint08': memory_metric['predictedTop1TrueTopQuartileFraction'] - mean_metric['predictedTop1TrueTopQuartileFraction'] >= 0.08,
        'memoryMeanRegretAtMostPoint035': memory_metric['meanPredictedTop1TrueRegret'] <= 0.035,
        'memoryRegretImprovementOverMeanAtLeastEightPercent': regret_improvement_fraction >= 0.08,
        'topQuartileImprovesOnAtLeastTwoRoutes': route_topq_wins >= 2,
        'regretImprovesOnAtLeastTwoRoutes': route_regret_wins >= 2,
        'neighborDistancesFinite': math.isfinite(nearest_mean) and math.isfinite(nearest_max),
    }
    decision = 'EMPIRICAL_ACTION_MEMORY_CALIBRATED' if all(gates.values()) else 'EMPIRICAL_ACTION_MEMORY_NOT_CALIBRATED'
    result = {
        'version': 1,
        'decision': decision,
        'trainingContainsSemanticTargets': False,
        'calibrationContainsSemanticTargets': False,
        'semanticEvidenceConsumed': False,
        'selectedConfig': {'k': selected_k, 'actionWeight': selected_weight, 'shrinkage': selected_shrinkage},
        'calibrationSeeds': list(CALIBRATION_SEEDS),
        'pairRows': pair_rows,
        'retrievalTaskCount': len(tasks),
        'memoryMSE': memory_mse,
        'routeActionMeanMSE': mean_mse,
        'zeroDeltaMSE': zero_mse,
        'overallMSEImprovementOverMean': improvement,
        'routeMSE': route,
        'memoryRetrieval': memory_metric,
        'meanRetrieval': mean_metric,
        'top4FractionDeltaVsMean': memory_metric['goalInPredictedTop4Fraction'] - mean_metric['goalInPredictedTop4Fraction'],
        'topQuartileFractionDeltaVsMean': memory_metric['predictedTop1TrueTopQuartileFraction'] - mean_metric['predictedTop1TrueTopQuartileFraction'],
        'regretDeltaVsMean': memory_metric['meanPredictedTop1TrueRegret'] - mean_metric['meanPredictedTop1TrueRegret'],
        'regretImprovementFractionVsMean': regret_improvement_fraction,
        'routeTopQuartileWinCount': route_topq_wins,
        'routeRegretWinCount': route_regret_wins,
        'routeRetrieval': route_retrieval,
        'neighborDiagnostics': {'meanNearestDistance': nearest_mean, 'maxNearestDistance': nearest_max},
        'gates': gates,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
