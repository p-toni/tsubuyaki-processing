from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import world_model as wm


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--model-output', type=Path, required=True)
    parser.add_argument('--summary-output', type=Path, required=True)
    args = parser.parse_args()

    files = sorted(args.input_dir.rglob('*.npz'))
    if not files:
        raise RuntimeError('no training shards found')
    blocks = []
    seeds = []
    for path in files:
        with np.load(path, allow_pickle=False) as d:
            blocks.append({k: d[k] for k in ('X', 'Y', 'valid', 'route_idx', 'operator_idx')})
            seeds.append(int(d['seed'][0]))
    X = np.concatenate([b['X'] for b in blocks], axis=0)
    Y = np.concatenate([b['Y'] for b in blocks], axis=0)
    valid = np.concatenate([b['valid'] for b in blocks], axis=0)
    route_idx = np.concatenate([b['route_idx'] for b in blocks], axis=0)
    operator_idx = np.concatenate([b['operator_idx'] for b in blocks], axis=0)

    model = wm.fit_model(X, Y, valid, route_idx, operator_idx)
    wm.save_model(args.model_output, model)

    pred, pred_valid = wm.predict(model, X)
    mse = float(np.mean((pred - Y) ** 2))
    valid_mae = float(np.mean(np.abs(pred_valid - valid)))
    summary = {
        'version': 1,
        'trainingSeeds': sorted(seeds),
        'shardCount': len(files),
        'rowCount': int(len(X)),
        'mathDim': wm.MATH_DIM,
        'visualDim': wm.VISUAL_DIM,
        'trainingMSE': mse,
        'trainingValidityMAE': valid_mae,
        'modelMetadata': wm.metadata(),
    }
    args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
