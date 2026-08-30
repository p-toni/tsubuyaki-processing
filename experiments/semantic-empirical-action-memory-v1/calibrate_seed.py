from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
LOCAL_DIR = ROOT / 'experiments' / 'semantic-local-dynamics-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(LOCAL_DIR))
sys.path.insert(0, str(HERE))

from orbit_representation import register_orbit
register_orbit()

from rng_streams import derived_seed
import empirical_memory as em
import generate_pairs
import local_dynamics as ld
import world_model as wm

PSEUDO_SLOTS = (3, 11, 19, 27)
RETRIEVAL_ACTIONS = 32


def _mse_stats(memory, data):
    X = np.asarray(data['X'], dtype=np.float64)
    Y = np.asarray(data['Y_delta'], dtype=np.float64)
    route_idx = np.asarray(data['route_idx'], dtype=np.int16)
    family_idx = np.asarray(data['family_idx'], dtype=np.int16)
    parent = em.parent_visual_from_x(X)
    action = em.action_delta_from_x(X)

    memory_sse = 0.0
    mean_sse = 0.0
    zero_sse = 0.0
    route = {
        name: {'rowCount': 0, 'memorySSE': 0.0, 'meanSSE': 0.0, 'zeroSSE': 0.0, 'elementCount': 0}
        for name in ld.ROUTES
    }
    nearest = []
    effective = []
    for i in range(len(X)):
        ri = int(route_idx[i]); fi = int(family_idx[i])
        pred, diag = em.predict_delta(memory, parent[i], action[i], ri, fi)
        mean = em.mean_delta(memory, ri, fi)
        e_mem = (pred - Y[i]) ** 2
        e_mean = (mean - Y[i]) ** 2
        e_zero = Y[i] ** 2
        memory_sse += float(e_mem.sum()); mean_sse += float(e_mean.sum()); zero_sse += float(e_zero.sum())
        r = route[ld.ROUTES[ri]]
        r['rowCount'] += 1
        r['memorySSE'] += float(e_mem.sum()); r['meanSSE'] += float(e_mean.sum()); r['zeroSSE'] += float(e_zero.sum())
        r['elementCount'] += int(e_mem.size)
        nearest.append(float(diag['nearestDistance']))
        effective.append(float(diag['effectiveNeighborCount']))

    return {
        'rowCount': int(len(X)),
        'memorySSE': memory_sse,
        'meanSSE': mean_sse,
        'zeroSSE': zero_sse,
        'elementCount': int(Y.size),
        'route': route,
        'neighborDiagnostics': {
            'meanNearestDistance': float(np.mean(nearest)),
            'maxNearestDistance': float(np.max(nearest)),
            'meanEffectiveNeighborCount': float(np.mean(effective)),
        },
    }


def _rank_record(predicted: np.ndarray, actual: np.ndarray, actual_valid: np.ndarray, goal_idx: int) -> dict:
    valid_indices = [i for i, ok in enumerate(actual_valid) if ok]
    goal = actual[goal_idx]
    true_distance = np.asarray([
        wm.model_distance(actual[i], goal) if actual_valid[i] else float('inf')
        for i in range(len(actual))
    ], dtype=np.float64)
    pred_distance = np.asarray([wm.model_distance(predicted[i], goal) for i in range(len(predicted))], dtype=np.float64)
    if not np.all(np.isfinite(pred_distance)):
        raise AssertionError('non-finite empirical predicted distance')
    predicted_order = sorted(range(len(predicted)), key=lambda i: (float(pred_distance[i]), i))
    true_order = sorted(valid_indices, key=lambda i: (float(true_distance[i]), i))
    top1 = predicted_order[0]
    true_rank = true_order.index(top1) if top1 in true_order else len(true_order)
    top_quartile_cut = max(1, int(math.ceil(len(true_order) * 0.25)))
    return {
        'goalInPredictedTop4': bool(goal_idx in predicted_order[:4]),
        'predictedTop1TrueTopQuartile': bool(true_rank < top_quartile_cut),
        'predictedTop1TrueRank': int(true_rank),
        'predictedTop1TrueRegret': float(true_distance[top1]) if top1 in valid_indices else 1.0,
    }


def _retrieval_tasks(seed: int, memory):
    tasks = []
    hard = {
        'allParentsValid': True,
        'exactActionPools': True,
        'finiteDistances': True,
        'memoryConfigFinite': True,
    }
    nearest = []
    for route in ld.ROUTES:
        rng = random.Random(derived_seed(seed, em.STREAM, 'calibration-bases', route))
        for base_index in range(4):
            native, spectral, _ = generate_pairs._valid_parent_pair(seed, route, base_index, rng)
            for material_index, (parent_genome, parent_visual) in enumerate((native, spectral)):
                action_seed = derived_seed(seed, em.STREAM, 'calibration-retrieval', route, base_index, material_index)
                actions = ld.action_set(route, parent_genome, action_seed, RETRIEVAL_ACTIONS)
                if len(actions) != RETRIEVAL_ACTIONS:
                    hard['exactActionPools'] = False
                memory_pred, diags = em.predict_children(memory, parent_visual, route, parent_genome, actions, mode='memory')
                mean_pred, _ = em.predict_children(memory, parent_visual, route, parent_genome, actions, mode='mean')
                nearest.extend(float(d['nearestDistance']) for d in diags)
                actual = []
                actual_valid = []
                for j, (child, _) in enumerate(actions):
                    vec, ok = ld.visual_for_state(route, child, f'emp-cal-{seed}-{route}-{base_index}-{material_index}-{j}')
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
                if len(pseudo) < 4:
                    hard['allParentsValid'] = False
                    continue
                for goal_idx in pseudo[:4]:
                    try:
                        memory_rec = _rank_record(memory_pred, actual, actual_valid, goal_idx)
                        mean_rec = _rank_record(mean_pred, actual, actual_valid, goal_idx)
                    except AssertionError:
                        hard['finiteDistances'] = False
                        raise
                    tasks.append({
                        'route': route,
                        'goalIndex': int(goal_idx),
                        'validActionCount': len(valid_indices),
                        'memory': memory_rec,
                        'mean': mean_rec,
                    })
    k, weight, shrinkage = em.selected_config(memory)
    if not math.isfinite(weight) or not math.isfinite(shrinkage) or k <= 0:
        hard['memoryConfigFinite'] = False
    return tasks, hard, {
        'meanNearestDistance': float(np.mean(nearest)),
        'maxNearestDistance': float(np.max(nearest)),
    }


def run(seed: int, memory_path: Path) -> dict:
    memory = em.load_memory(memory_path)
    pair_data = generate_pairs.generate(seed, bases_per_route=8)
    mse = _mse_stats(memory, pair_data)
    tasks, hard, neighbor = _retrieval_tasks(seed, memory)
    k, weight, shrinkage = em.selected_config(memory)
    return {
        'version': 1,
        'seed': int(seed),
        'calibrationContainsSemanticTargets': False,
        'priorExperienceOnly': True,
        'selectedConfig': {'k': k, 'actionWeight': weight, 'shrinkage': shrinkage},
        'pairStats': mse,
        'retrievalTasks': tasks,
        'retrievalNeighborDiagnostics': neighbor,
        'hardInvariants': hard,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--memory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(args.seed, args.memory), indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
