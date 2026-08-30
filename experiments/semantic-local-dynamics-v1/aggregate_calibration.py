from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import local_dynamics as ld

EXPECTED_SEEDS = (734200011, 734200029, 734200041, 734200067)


def _sum_pair(rows, key):
    return float(sum(float(r['pairStats'][key]) for r in rows))


def _mse(sse: float, count: int) -> float:
    return float(sse / max(1, int(count)))


def _improvement(model_mse: float, zero_mse: float, mean_mse: float):
    baseline = min(zero_mse, mean_mse)
    value = (baseline - model_mse) / baseline if baseline > 1e-15 else 0.0
    kind = 'zero-delta' if zero_mse <= mean_mse else 'route-action-mean'
    return float(value), float(baseline), kind


def aggregate(input_dir: Path) -> dict:
    paths = sorted(input_dir.glob('*.json'))
    rows = [json.loads(p.read_text()) for p in paths]
    rows.sort(key=lambda x: int(x['seed']))
    seeds = tuple(int(r['seed']) for r in rows)

    element_count = int(sum(int(r['pairStats']['elementCount']) for r in rows))
    model_mse = _mse(_sum_pair(rows, 'modelSSE'), element_count)
    zero_mse = _mse(_sum_pair(rows, 'zeroSSE'), element_count)
    mean_mse = _mse(_sum_pair(rows, 'meanSSE'), element_count)
    overall_improvement, baseline_mse, baseline_kind = _improvement(model_mse, zero_mse, mean_mse)

    route_stats = {}
    for route in ld.ROUTES:
        count = int(sum(int(r['pairStats']['route'][route]['elementCount']) for r in rows))
        mm = _mse(sum(float(r['pairStats']['route'][route]['modelSSE']) for r in rows), count)
        zm = _mse(sum(float(r['pairStats']['route'][route]['zeroSSE']) for r in rows), count)
        am = _mse(sum(float(r['pairStats']['route'][route]['meanSSE']) for r in rows), count)
        imp, base, kind = _improvement(mm, zm, am)
        route_stats[route] = {
            'modelMSE': mm,
            'zeroDeltaMSE': zm,
            'routeActionMeanMSE': am,
            'strongerBaselineMSE': base,
            'strongerBaselineKind': kind,
            'improvement': imp,
        }

    tasks = [task for r in rows for task in r['retrievalTasks']]
    top4 = float(np.mean([bool(t['goalInPredictedTop4']) for t in tasks])) if tasks else 0.0
    top_quartile = float(np.mean([bool(t['predictedTop1TrueTopQuartile']) for t in tasks])) if tasks else 0.0
    regret = float(np.mean([float(t['predictedTop1TrueRegret']) for t in tasks])) if tasks else float('inf')
    route_retrieval = {}
    for route in ld.ROUTES:
        rt = [t for t in tasks if t['route'] == route]
        route_retrieval[route] = {
            'taskCount': len(rt),
            'goalInPredictedTop4Fraction': float(np.mean([bool(t['goalInPredictedTop4']) for t in rt])) if rt else 0.0,
            'predictedTop1TrueTopQuartileFraction': float(np.mean([bool(t['predictedTop1TrueTopQuartile']) for t in rt])) if rt else 0.0,
            'meanPredictedTop1TrueRegret': float(np.mean([float(t['predictedTop1TrueRegret']) for t in rt])) if rt else float('inf'),
        }

    conf = {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0, 'positive': 0, 'negative': 0}
    for r in rows:
        for key in conf:
            conf[key] += int(r['pairStats']['validity'][key])
    if conf['positive'] > 0 and conf['negative'] > 0:
        tpr = conf['tp'] / conf['positive']
        tnr = conf['tn'] / conf['negative']
        balanced_accuracy = float((tpr + tnr) / 2.0)
        validity_gate = balanced_accuracy >= 0.80
    else:
        balanced_accuracy = None
        validity_gate = True

    hard = {
        'exactCalibrationSeeds': seeds == EXPECTED_SEEDS,
        'exactCalibrationPairRows': sum(int(r['pairStats']['rowCount']) for r in rows) == 1536,
        'exactRetrievalTaskCount': len(tasks) == 384,
        'allShardHardInvariants': all(all(bool(v) for v in r['hardInvariants'].values()) for r in rows),
        'calibrationContainsNoSemanticTargets': all(not bool(r['calibrationContainsSemanticTargets']) for r in rows),
    }
    gates = {
        **hard,
        'overallMSEImprovementAtLeastPoint20': overall_improvement >= 0.20,
        'everyRouteMSEImprovementPositive': all(route_stats[r]['improvement'] > 0 for r in ld.ROUTES),
        'pseudoGoalInPredictedTop4AtLeastPoint55': top4 >= 0.55,
        'predictedTop1TrueTopQuartileAtLeastPoint80': top_quartile >= 0.80,
        'meanPredictedTop1RegretAtMostPoint035': regret <= 0.035,
        'validityBalancedAccuracyAtLeastPoint80OrDegenerate': validity_gate,
    }
    decision = 'LOCAL_DYNAMICS_CALIBRATED' if all(gates.values()) else 'LOCAL_DYNAMICS_NOT_CALIBRATED'
    return {
        'version': 1,
        'decision': decision,
        'trainingContainsSemanticTargets': False,
        'calibrationContainsSemanticTargets': False,
        'calibrationSeeds': list(seeds),
        'pairRows': sum(int(r['pairStats']['rowCount']) for r in rows),
        'modelMSE': model_mse,
        'zeroDeltaMSE': zero_mse,
        'routeActionMeanMSE': mean_mse,
        'strongerBaselineMSE': baseline_mse,
        'strongerBaselineKind': baseline_kind,
        'overallMSEImprovement': overall_improvement,
        'routeMSE': route_stats,
        'retrievalTaskCount': len(tasks),
        'goalInPredictedTop4Fraction': top4,
        'predictedTop1TrueTopQuartileFraction': top_quartile,
        'meanPredictedTop1TrueRegret': regret,
        'routeRetrieval': route_retrieval,
        'validityConfusion': conf,
        'validityBalancedAccuracy': balanced_accuracy,
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
