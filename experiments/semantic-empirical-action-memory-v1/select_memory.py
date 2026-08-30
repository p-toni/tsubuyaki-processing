from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import empirical_memory as em
import local_dynamics as ld
import world_model as wm

BASE_CHOICES = (0, 6, 12, 18)


def _load_shards(input_dir: Path) -> list[tuple[int, dict[str, np.ndarray]]]:
    shards = []
    for path in sorted(input_dir.rglob('train-*.npz')):
        with np.load(path, allow_pickle=False) as data:
            d = {k: data[k] for k in data.files}
        seed = int(d['seed'][0])
        shards.append((seed, d))
    if tuple(sorted(seed for seed, _ in shards)) != em.TRAIN_SEEDS:
        raise AssertionError(f'training artifact rectangle drifted: {[seed for seed, _ in shards]}')
    return shards


def _group_rows(route_index: int, base_index: int, material_index: int) -> np.ndarray:
    route_block = 24 * 2 * ld.ACTION_FAMILY_COUNT
    base_block = 2 * ld.ACTION_FAMILY_COUNT
    start = route_index * route_block + base_index * base_block + material_index * ld.ACTION_FAMILY_COUNT
    return np.arange(start, start + ld.ACTION_FAMILY_COUNT, dtype=np.int64)


def _stratum_stats(memory, train_mask, route_index: int, family: int):
    mask = train_mask & (memory['route_idx'] == int(route_index)) & (memory['family_idx'] == int(family))
    idx = np.flatnonzero(mask)
    if len(idx) != (len(em.TRAIN_SEEDS) - 1) * 48:
        raise AssertionError(f'LOSO stratum count drifted route={route_index} family={family}: {len(idx)}')
    std = em.action_std_for_stratum(memory['action_delta'][idx])
    baseline = np.asarray(memory['y_delta'][idx], dtype=np.float64).mean(axis=0)
    return idx, std, baseline


def cross_validate(shards: list[tuple[int, dict[str, np.ndarray]]]) -> dict:
    configs = [
        (int(k), float(w), float(a))
        for k in em.K_GRID
        for w in em.ACTION_WEIGHT_GRID
        for a in em.SHRINKAGE_GRID
    ]
    stats = {
        c: {
            'sse': 0.0,
            'baselineSSE': 0.0,
            'elementCount': 0,
            'goalTop2': 0,
            'top1TrueTopQuartile': 0,
            'taskCount': 0,
            'regretSum': 0.0,
            'foldSeedMeanSquaredError': {},
        }
        for c in configs
    }
    baseline_rank = {'goalTop2': 0, 'top1TrueTopQuartile': 0, 'taskCount': 0, 'regretSum': 0.0}

    complete = em.build_memory(shards, 16, 1.0, 0.5)
    for held_seed, held in sorted(shards):
        train_mask = complete['row_seed'] != int(held_seed)
        Xh = np.asarray(held['X'], dtype=np.float64)
        Yh = np.asarray(held['Y_delta'], dtype=np.float64)
        Vh = np.asarray(held['valid'], dtype=np.float64) >= 0.5
        Rh = np.asarray(held['route_idx'], dtype=np.int16)
        Fh = np.asarray(held['family_idx'], dtype=np.int16)
        parent_h = em.parent_visual_from_x(Xh)
        action_h = em.action_delta_from_x(Xh)

        fold_sse = {c: 0.0 for c in configs}
        fold_elements = 0
        stratum_cache = {
            (ri, fi): _stratum_stats(complete, train_mask, ri, fi)
            for ri in range(len(ld.ROUTES))
            for fi in range(ld.ACTION_FAMILY_COUNT)
        }

        for ri in range(len(ld.ROUTES)):
            for base_index in BASE_CHOICES:
                for material_index in range(2):
                    rows = _group_rows(ri, base_index, material_index)
                    if list(int(x) for x in Fh[rows]) != list(range(ld.ACTION_FAMILY_COUNT)):
                        raise AssertionError('held-out action-family group drifted')
                    if not np.all(Rh[rows] == ri):
                        raise AssertionError('held-out route group drifted')
                    if not np.allclose(parent_h[rows], parent_h[rows[0]][None, :], atol=1e-12, rtol=0.0):
                        raise AssertionError('parent visual not constant within action group')

                    predictions = {c: [] for c in configs}
                    baseline_predictions = []
                    actual_children = []
                    actual_valid = []
                    for row in rows:
                        fi = int(Fh[row])
                        idx, std, baseline = stratum_cache[(ri, fi)]
                        state_d = em.state_distances(parent_h[row], complete['parent_visual'][idx])
                        action_d = em.action_distances(action_h[row], complete['action_delta'][idx], std)
                        actual_delta = Yh[row]
                        baseline_error = (baseline - actual_delta) ** 2
                        actual_children.append(wm.sanitize_visual(parent_h[row] + actual_delta))
                        actual_valid.append(bool(Vh[row]))
                        baseline_predictions.append(wm.sanitize_visual(parent_h[row] + baseline))

                        neighbor_cache = {}
                        for k in em.K_GRID:
                            for w in em.ACTION_WEIGHT_GRID:
                                combined = state_d + float(w) * action_d
                                kk = min(int(k), len(idx))
                                nearest = np.argpartition(combined, kk - 1)[:kk]
                                weights = 1.0 / (combined[nearest] + em.DISTANCE_FLOOR)
                                weights /= weights.sum()
                                neighbor_cache[(int(k), float(w))] = np.sum(
                                    np.asarray(complete['y_delta'][idx[nearest]], dtype=np.float64) * weights[:, None],
                                    axis=0,
                                )
                        for k, w, a in configs:
                            neighbor = neighbor_cache[(k, w)]
                            pred_delta = baseline + a * (neighbor - baseline)
                            error = (pred_delta - actual_delta) ** 2
                            s = stats[(k, w, a)]
                            s['sse'] += float(error.sum())
                            s['baselineSSE'] += float(baseline_error.sum())
                            s['elementCount'] += int(error.size)
                            fold_sse[(k, w, a)] += float(error.sum())
                            predictions[(k, w, a)].append(wm.sanitize_visual(parent_h[row] + pred_delta))
                        fold_elements += int(actual_delta.size)

                    actual_children = np.asarray(actual_children, dtype=np.float64)
                    baseline_predictions = np.asarray(baseline_predictions, dtype=np.float64)
                    valid_indices = [i for i, ok in enumerate(actual_valid) if ok]
                    if len(valid_indices) < 4:
                        raise AssertionError('too few valid actions in LOSO pseudo-goal group')

                    for goal_idx in valid_indices:
                        goal = actual_children[goal_idx]
                        true_distance = np.asarray([
                            wm.model_distance(actual_children[i], goal) if i in valid_indices else float('inf')
                            for i in range(ld.ACTION_FAMILY_COUNT)
                        ], dtype=np.float64)
                        true_order = sorted(valid_indices, key=lambda i: (float(true_distance[i]), i))
                        top_quartile_cut = max(1, int(math.ceil(len(true_order) * 0.25)))

                        baseline_distance = np.asarray([
                            wm.model_distance(baseline_predictions[i], goal)
                            for i in range(ld.ACTION_FAMILY_COUNT)
                        ], dtype=np.float64)
                        baseline_order = sorted(range(ld.ACTION_FAMILY_COUNT), key=lambda i: (float(baseline_distance[i]), i))
                        baseline_top1 = baseline_order[0]
                        baseline_rank_value = true_order.index(baseline_top1) if baseline_top1 in true_order else len(true_order)
                        baseline_rank['goalTop2'] += int(goal_idx in baseline_order[:2])
                        baseline_rank['top1TrueTopQuartile'] += int(baseline_rank_value < top_quartile_cut)
                        baseline_rank['taskCount'] += 1
                        baseline_rank['regretSum'] += float(true_distance[baseline_top1]) if baseline_top1 in valid_indices else 1.0

                        for c in configs:
                            predicted = np.asarray(predictions[c], dtype=np.float64)
                            pred_distance = np.asarray([
                                wm.model_distance(predicted[i], goal)
                                for i in range(ld.ACTION_FAMILY_COUNT)
                            ], dtype=np.float64)
                            pred_order = sorted(range(ld.ACTION_FAMILY_COUNT), key=lambda i: (float(pred_distance[i]), i))
                            top1 = pred_order[0]
                            true_rank = true_order.index(top1) if top1 in true_order else len(true_order)
                            s = stats[c]
                            s['goalTop2'] += int(goal_idx in pred_order[:2])
                            s['top1TrueTopQuartile'] += int(true_rank < top_quartile_cut)
                            s['taskCount'] += 1
                            s['regretSum'] += float(true_distance[top1]) if top1 in valid_indices else 1.0

        for c in configs:
            stats[c]['foldSeedMeanSquaredError'][str(held_seed)] = fold_sse[c] / fold_elements

    mean_baseline = {
        'goalInPredictedTop2Fraction': baseline_rank['goalTop2'] / baseline_rank['taskCount'],
        'predictedTop1TrueTopQuartileFraction': baseline_rank['top1TrueTopQuartile'] / baseline_rank['taskCount'],
        'meanPredictedTop1TrueRegret': baseline_rank['regretSum'] / baseline_rank['taskCount'],
        'taskCount': baseline_rank['taskCount'],
    }

    rows = []
    for k, w, a in configs:
        s = stats[(k, w, a)]
        mse = s['sse'] / s['elementCount']
        baseline_mse = s['baselineSSE'] / s['elementCount']
        goal2 = s['goalTop2'] / s['taskCount']
        topq = s['top1TrueTopQuartile'] / s['taskCount']
        regret = s['regretSum'] / s['taskCount']
        regret_improvement = (
            (mean_baseline['meanPredictedTop1TrueRegret'] - regret)
            / mean_baseline['meanPredictedTop1TrueRegret']
        )
        row = {
            'k': k,
            'actionWeight': w,
            'shrinkage': a,
            'mse': mse,
            'routeActionMeanMSE': baseline_mse,
            'mseImprovement': 1.0 - mse / baseline_mse,
            'goalInPredictedTop2Fraction': goal2,
            'goalTop2DeltaVsMean': goal2 - mean_baseline['goalInPredictedTop2Fraction'],
            'predictedTop1TrueTopQuartileFraction': topq,
            'topQuartileDeltaVsMean': topq - mean_baseline['predictedTop1TrueTopQuartileFraction'],
            'meanPredictedTop1TrueRegret': regret,
            'regretImprovementFractionVsMean': regret_improvement,
            'taskCount': s['taskCount'],
            'queryRows': s['elementCount'] // wm.VISUAL_DIM,
            'foldSeedMeanSquaredError': s['foldSeedMeanSquaredError'],
        }
        row['cvUtility'] = (
            row['topQuartileDeltaVsMean']
            + row['goalTop2DeltaVsMean']
            + row['regretImprovementFractionVsMean']
            + max(0.0, row['mseImprovement'])
        )
        rows.append(row)

    eligible = [r for r in rows if r['mseImprovement'] >= 0.0]
    ranked = sorted(
        eligible if eligible else rows,
        key=lambda r: (
            r['cvUtility'],
            r['topQuartileDeltaVsMean'],
            r['regretImprovementFractionVsMean'],
            r['goalTop2DeltaVsMean'],
            r['mseImprovement'],
            -r['k'],
            -r['actionWeight'],
            -r['shrinkage'],
        ),
        reverse=True,
    )
    selected = ranked[0]
    return {
        'version': 1,
        'trainingContainsSemanticTargets': False,
        'selectionUsesOnlyPriorTargetBlindTrainingArtifacts': True,
        'priorTrainingRunId': em.PRIOR_TRAIN_RUN_ID,
        'priorTrainingHeadSha': em.PRIOR_TRAIN_HEAD_SHA,
        'trainingSeeds': list(em.TRAIN_SEEDS),
        'candidateConfigCount': len(rows),
        'meanBaseline': mean_baseline,
        'selected': selected,
        'cvPromising': bool(
            selected['mseImprovement'] >= 0.0
            and selected['topQuartileDeltaVsMean'] >= 0.05
            and selected['regretImprovementFractionVsMean'] >= 0.05
            and selected['goalTop2DeltaVsMean'] >= 0.0
        ),
        'configs': rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--memory-output', type=Path, required=True)
    parser.add_argument('--summary-output', type=Path, required=True)
    args = parser.parse_args()
    shards = _load_shards(args.input_dir)
    summary = cross_validate(shards)
    selected = summary['selected']
    memory = em.build_memory(
        shards,
        int(selected['k']),
        float(selected['actionWeight']),
        float(selected['shrinkage']),
    )
    em.save_memory(args.memory_output, memory)
    args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
