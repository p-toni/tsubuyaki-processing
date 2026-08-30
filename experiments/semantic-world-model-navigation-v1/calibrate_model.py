from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import generate_dataset as gd
import world_model as wm

CALIBRATION_SEEDS = (733200011, 733200029, 733200041, 733200067)
BASES_PER_ROUTE = 64


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    model = wm.load_model(args.model)

    datasets = []
    for seed in CALIBRATION_SEEDS:
        d = gd.generate(seed, BASES_PER_ROUTE)
        pred, pred_valid = wm.predict(model, d['X'])
        d['pred'] = pred; d['pred_valid'] = pred_valid
        datasets.append(d)

    Y = np.concatenate([d['Y'] for d in datasets], axis=0)
    P = np.concatenate([d['pred'] for d in datasets], axis=0)
    route = np.concatenate([d['route_idx'] for d in datasets], axis=0)
    operator = np.concatenate([d['operator_idx'] for d in datasets], axis=0)

    baseline = np.stack([model['baseline_visual'][int(r), int(o)] for r, o in zip(route, operator)], axis=0)
    model_mse = float(np.mean((P - Y) ** 2))
    baseline_mse = float(np.mean((baseline - Y) ** 2))
    overall_improvement = 1.0 - model_mse / max(1e-12, baseline_mse)
    route_improvement = {}
    for ri, route_name in enumerate(wm.ROUTES):
        mask = route == ri
        mm = float(np.mean((P[mask] - Y[mask]) ** 2))
        bm = float(np.mean((baseline[mask] - Y[mask]) ** 2))
        route_improvement[route_name] = 1.0 - mm / max(1e-12, bm)

    retrieval = []
    for si, d in enumerate(datasets):
        next_d = datasets[(si + 1) % len(datasets)]
        for ri, route_name in enumerate(wm.ROUTES):
            idx = np.where(d['route_idx'] == ri)[0]
            probe_idx = np.where(next_d['route_idx'] == ri)[0]
            if len(idx) != BASES_PER_ROUTE * 2 or len(probe_idx) != BASES_PER_ROUTE * 2:
                raise AssertionError('calibration route rectangle drifted')
            # Four target-free probe states per seed/route. The probes are actual
            # held-out generator phenotypes from the next calibration seed.
            for q in (3, 27, 71, 109):
                probe = next_d['Y'][probe_idx[q]]
                true_dist = np.asarray([wm.model_distance(d['Y'][j], probe) for j in idx])
                pred_dist = np.asarray([wm.model_distance(d['pred'][j], probe) for j in idx])
                oracle_local = int(np.argmin(true_dist))
                predicted_order = np.argsort(pred_dist)
                top8_recall = oracle_local in set(int(x) for x in predicted_order[:8])
                predicted_top1_true = float(true_dist[int(predicted_order[0])])
                retrieval.append({
                    'seed': int(d['seed'][0]),
                    'route': route_name,
                    'probeOrdinal': int(q),
                    'oracleInPredictedTop8': bool(top8_recall),
                    'predictedTop1BeatsMedian': predicted_top1_true <= float(np.median(true_dist)),
                    'predictedTop1Regret': predicted_top1_true - float(true_dist[oracle_local]),
                })

    top8_fraction = float(np.mean([r['oracleInPredictedTop8'] for r in retrieval]))
    top1_beats_median = float(np.mean([r['predictedTop1BeatsMedian'] for r in retrieval]))
    gates = {
        'exactCalibrationSeeds': len(datasets) == len(CALIBRATION_SEEDS),
        'overallMSEImprovementAtLeastPoint20': overall_improvement >= 0.20,
        'everyRouteMSEImprovementPositive': all(v > 0 for v in route_improvement.values()),
        'oracleTop8RecallAtLeastPoint50': top8_fraction >= 0.50,
        'predictedTop1BeatsMedianAtLeastPoint85': top1_beats_median >= 0.85,
    }
    decision = 'WORLD_MODEL_CALIBRATED' if all(gates.values()) else 'WORLD_MODEL_NOT_CALIBRATED'
    result = {
        'version': 1,
        'decision': decision,
        'trainingContainsSemanticTargets': False,
        'calibrationContainsSemanticTargets': False,
        'calibrationSeeds': list(CALIBRATION_SEEDS),
        'rows': int(len(Y)),
        'modelMSE': model_mse,
        'routeOperatorMeanBaselineMSE': baseline_mse,
        'overallMSEImprovement': overall_improvement,
        'routeMSEImprovement': route_improvement,
        'retrievalTaskCount': len(retrieval),
        'oracleInPredictedTop8Fraction': top8_fraction,
        'predictedTop1BeatsMedianFraction': top1_beats_median,
        'meanPredictedTop1Regret': float(np.mean([r['predictedTop1Regret'] for r in retrieval])),
        'gates': gates,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
