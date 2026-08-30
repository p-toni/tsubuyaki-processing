from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import local_dynamics as ld


def _load_shards(input_dir: Path):
    paths = sorted(input_dir.glob('*.npz'))
    if not paths:
        raise FileNotFoundError(f'no npz shards in {input_dir}')
    chunks = []
    seeds = []
    for path in paths:
        with np.load(path, allow_pickle=False) as d:
            chunks.append({k: d[k] for k in d.files})
            seeds.append(int(d['seed'][0]))
    return paths, chunks, seeds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--model-output', type=Path, required=True)
    parser.add_argument('--summary-output', type=Path, required=True)
    args = parser.parse_args()

    paths, chunks, seeds = _load_shards(args.input_dir)
    X = np.concatenate([c['X'] for c in chunks], axis=0)
    Y = np.concatenate([c['Y_delta'] for c in chunks], axis=0)
    valid = np.concatenate([c['valid'] for c in chunks], axis=0)
    route_idx = np.concatenate([c['route_idx'] for c in chunks], axis=0)
    family_idx = np.concatenate([c['family_idx'] for c in chunks], axis=0)

    model = ld.fit_model(X, Y, valid, route_idx, family_idx)
    pred_delta, pred_valid = ld.predict(model, X)
    training_mse = float(np.mean((pred_delta - Y) ** 2))
    validity_mae = float(np.mean(np.abs(pred_valid - valid)))

    zero_mse = float(np.mean(Y ** 2))
    mean_pred = np.asarray([model['baseline_delta'][int(r), int(f)] for r, f in zip(route_idx, family_idx)])
    mean_mse = float(np.mean((mean_pred - Y) ** 2))

    ld.save_model(args.model_output, model)
    summary = {
        'version': 1,
        'trainingContainsSemanticTargets': False,
        'shardCount': len(paths),
        'trainingSeeds': sorted(seeds),
        'rowCount': int(len(X)),
        'inputDim': int(X.shape[1]),
        'outputDim': int(Y.shape[1]),
        'trainingMSE': training_mse,
        'trainingZeroDeltaBaselineMSE': zero_mse,
        'trainingRouteFamilyMeanBaselineMSE': mean_mse,
        'trainingValidityMAE': validity_mae,
        'childValidityRate': float(np.mean(valid)),
        'metadata': ld.metadata(),
    }
    args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
