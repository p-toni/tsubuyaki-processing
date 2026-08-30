from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(HERE))

from orbit_representation import register_orbit
register_orbit()

from rng_streams import derived_seed
import generate_pairs
import local_dynamics as ld
import world_model as wm

PSEUDO_SLOTS = (3, 11, 19, 27)
RETRIEVAL_ACTIONS = 32


def _mse_stats(model, data):
    X = data['X']; Y = data['Y_delta']; valid = data['valid']
    route_idx = data['route_idx']; family_idx = data['family_idx']
    pred, pred_valid = ld.predict(model, X)
    errors = (pred - Y) ** 2
    zero_errors = Y ** 2
    mean_pred = np.asarray([model['baseline_delta'][int(r), int(f)] for r, f in zip(route_idx, family_idx)])
    mean_errors = (mean_pred - Y) ** 2

    out = {
        'rowCount': int(len(X)),
        'modelSSE': float(errors.sum()),
        'zeroSSE': float(zero_errors.sum()),
        'meanSSE': float(mean_errors.sum()),
        'elementCount': int(errors.size),
        'route': {},
    }
    for ri, route in enumerate(ld.ROUTES):
        mask = route_idx == ri
        out['route'][route] = {
            'rowCount': int(mask.sum()),
            'modelSSE': float(errors[mask].sum()),
            'zeroSSE': float(zero_errors[mask].sum()),
            'meanSSE': float(mean_errors[mask].sum()),
            'elementCount': int(errors[mask].size),
        }

    truth = valid >= 0.5
    guess = pred_valid >= 0.5
    out['validity'] = {
        'tp': int(np.count_nonzero(truth & guess)),
        'tn': int(np.count_nonzero(~truth & ~guess)),
        'fp': int(np.count_nonzero(~truth & guess)),
        'fn': int(np.count_nonzero(truth & ~guess)),
        'positive': int(np.count_nonzero(truth)),
        'negative': int(np.count_nonzero(~truth)),
    }
    return out


def _retrieval_tasks(seed: int, model):
    tasks = []
    hard = {'allParentsValid': True, 'exactActionPools': True, 'finiteDistances': True}
    for route in ld.ROUTES:
        rng = random.Random(derived_seed(seed, ld.STREAM, 'training-bases', route))
        for base_index in range(4):
            native, spectral, _ = generate_pairs._valid_parent_pair(seed, route, base_index, rng)
            for material_index, (parent_genome, parent_visual) in enumerate((native, spectral)):
                action_seed = derived_seed(seed, ld.STREAM, 'calibration-retrieval', route, base_index, material_index)
                actions = ld.action_set(route, parent_genome, action_seed, RETRIEVAL_ACTIONS)
                if len(actions) != RETRIEVAL_ACTIONS:
                    hard['exactActionPools'] = False
                children = [g for g, _ in actions]
                predicted, predicted_valid = ld.predict_children(model, parent_visual, route, parent_genome, children)
                actual = []
                actual_valid = []
                for j, child in enumerate(children):
                    vec, ok = ld.visual_for_state(route, child, f'cal-{seed}-{route}-{base_index}-{material_index}-{j}')
                    actual.append(vec); actual_valid.append(ok)
                actual = np.asarray(actual, dtype=np.float64)
                actual_valid = np.asarray(actual_valid, dtype=bool)
                if not actual_valid.any():
                    hard['allParentsValid'] = False
                    continue

                valid_indices = [i for i, ok in enumerate(actual_valid) if ok]
                pseudo = [slot for slot in PSEUDO_SLOTS if slot in valid_indices]
                if len(pseudo) < 4:
                    pseudo += [i for i in valid_indices if i not in pseudo][:4-len(pseudo)]
                for goal_idx in pseudo[:4]:
                    goal = actual[goal_idx]
                    true_distance = np.asarray([
                        wm.model_distance(actual[i], goal) if actual_valid[i] else float('inf')
                        for i in range(RETRIEVAL_ACTIONS)
                    ], dtype=float)
                    pred_distance = np.asarray([
                        wm.model_distance(predicted[i], goal)
                        for i in range(RETRIEVAL_ACTIONS)
                    ], dtype=float)
                    if not np.all(np.isfinite(pred_distance)):
                        hard['finiteDistances'] = False
                    predicted_order = sorted(
                        range(RETRIEVAL_ACTIONS),
                        key=lambda i: (0 if predicted_valid[i] >= 0.5 else 1, float(pred_distance[i]), i),
                    )
                    true_order = sorted(
                        valid_indices,
                        key=lambda i: (float(true_distance[i]), i),
                    )
                    top1 = predicted_order[0]
                    true_rank = true_order.index(top1) if top1 in true_order else len(true_order)
                    top_quartile_cut = max(1, int(np.ceil(len(true_order) * 0.25)))
                    tasks.append({
                        'route': route,
                        'goalIndex': int(goal_idx),
                        'goalInPredictedTop4': bool(goal_idx in predicted_order[:4]),
                        'predictedTop1TrueTopQuartile': bool(true_rank < top_quartile_cut),
                        'predictedTop1TrueRank': int(true_rank),
                        'predictedTop1TrueRegret': float(true_distance[top1]) if top1 in valid_indices else 1.0,
                        'validActionCount': len(valid_indices),
                    })
    return tasks, hard


def run(seed: int, model_path: Path) -> dict:
    model = ld.load_model(model_path)
    pair_data = generate_pairs.generate(seed, bases_per_route=8)
    mse = _mse_stats(model, pair_data)
    tasks, hard = _retrieval_tasks(seed, model)
    return {
        'version': 1,
        'seed': int(seed),
        'calibrationContainsSemanticTargets': False,
        'pairStats': mse,
        'retrievalTasks': tasks,
        'hardInvariants': hard,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(args.seed, args.model), indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
