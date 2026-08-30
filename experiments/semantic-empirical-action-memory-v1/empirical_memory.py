from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
LOCAL_DIR = ROOT / 'experiments' / 'semantic-local-dynamics-v1'
WM_DIR = ROOT / 'experiments' / 'semantic-world-model-navigation-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(LOCAL_DIR))
sys.path.insert(0, str(WM_DIR))

from orbit_representation import register_orbit
register_orbit()

import local_dynamics as ld
import world_model as wm

STREAM = 'semantic-empirical-action-memory-v1'
PRIOR_TRAIN_RUN_ID = 33336810605
PRIOR_TRAIN_HEAD_SHA = 'a22ad8d607b8f879949fec3f3c8f537079629ed6'
TRAIN_SEEDS = (
    734100011, 734100029, 734100041, 734100067,
    734100079, 734100101, 734100113, 734100137,
    734100151, 734100173, 734100197, 734100211,
)
K_GRID = (4, 8, 16, 32, 64)
ACTION_WEIGHT_GRID = (0.0, 0.25, 1.0, 4.0)
SHRINKAGE_GRID = (0.25, 0.50, 0.75, 1.00)
DISTANCE_FLOOR = 0.02
INDICATOR_DIM = len(ld.ROUTES) + 1
ACTION_OFFSET = wm.VISUAL_DIM + INDICATOR_DIM


def parent_visual_from_x(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    return X[:, :wm.VISUAL_DIM]


def action_delta_from_x(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    if X.shape[1] != ld.INPUT_DIM:
        raise ValueError(f'bad local-dynamics input dim {X.shape}')
    return X[:, ACTION_OFFSET:]


def state_distances(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Vectorized exact analogue of world_model.model_distance(query, row)."""
    q = wm.sanitize_visual(np.asarray(query, dtype=np.float64).reshape(-1))
    M = np.asarray(matrix, dtype=np.float64)
    if M.ndim != 2 or M.shape[1] != wm.VISUAL_DIM:
        raise ValueError(f'bad visual matrix shape {M.shape}')

    def l1(key: str, factor: float) -> np.ndarray:
        sl = wm.BLOCK_SLICES[key]
        return factor * np.abs(M[:, sl] - q[sl][None, :]).sum(axis=1)

    def mean_abs(key: str) -> np.ndarray:
        sl = wm.BLOCK_SLICES[key]
        return np.abs(M[:, sl] - q[sl][None, :]).mean(axis=1)

    grid = 0.5 * (l1('grid16', 0.5) + l1('grid8', 0.5))
    projection = 0.25 * (
        np.abs(M[:, wm.BLOCK_SLICES['projectionX']] - q[wm.BLOCK_SLICES['projectionX']][None, :]).sum(axis=1)
        + np.abs(M[:, wm.BLOCK_SLICES['projectionY']] - q[wm.BLOCK_SLICES['projectionY']][None, :]).sum(axis=1)
    )
    polar = l1('polar', 0.5)
    orientation = l1('orientation', 0.5)
    radial = mean_abs('radial')
    symmetry = mean_abs('symmetry')
    topology = mean_abs('topology')
    out = np.mean(np.stack([grid, projection, polar, orientation, radial, symmetry, topology], axis=1), axis=1)
    if not np.all(np.isfinite(out)):
        raise AssertionError('non-finite empirical state distance')
    return out


def action_std_for_stratum(action_delta: np.ndarray) -> np.ndarray:
    x = np.asarray(action_delta, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != wm.MATH_DIM:
        raise ValueError(f'bad action-delta shape {x.shape}')
    std = x.std(axis=0)
    std[std < 1e-8] = 0.0
    return std


def action_distances(query: np.ndarray, matrix: np.ndarray, std: np.ndarray) -> np.ndarray:
    q = np.asarray(query, dtype=np.float64).reshape(-1)
    M = np.asarray(matrix, dtype=np.float64)
    s = np.asarray(std, dtype=np.float64).reshape(-1)
    if M.shape[1] != wm.MATH_DIM or q.size != wm.MATH_DIM or s.size != wm.MATH_DIM:
        raise ValueError('action distance dimensional drift')
    active = s > 1e-8
    if not np.any(active):
        return np.zeros(len(M), dtype=np.float64)
    return np.mean(np.abs((M[:, active] - q[active][None, :]) / s[active][None, :]), axis=1)


def predict_delta_from_arrays(
    parent_visual: np.ndarray,
    action_delta: np.ndarray,
    memory_parent_visual: np.ndarray,
    memory_action_delta: np.ndarray,
    memory_y_delta: np.ndarray,
    action_std: np.ndarray,
    k: int,
    action_weight: float,
) -> tuple[np.ndarray, dict]:
    n = int(len(memory_y_delta))
    if n <= 0:
        raise ValueError('empty empirical stratum')
    state_d = state_distances(parent_visual, memory_parent_visual)
    action_d = action_distances(action_delta, memory_action_delta, action_std)
    combined = state_d + float(action_weight) * action_d
    kk = min(int(k), n)
    if kk <= 0:
        raise ValueError('non-positive k')
    idx = np.argpartition(combined, kk - 1)[:kk]
    order = idx[np.argsort(combined[idx], kind='stable')]
    d = combined[order]
    weights = 1.0 / (d + DISTANCE_FLOOR)
    weights /= weights.sum()
    pred = np.sum(np.asarray(memory_y_delta, dtype=np.float64)[order] * weights[:, None], axis=0)
    return pred, {
        'neighborCount': kk,
        'nearestDistance': float(d[0]),
        'meanNeighborDistance': float(np.mean(d)),
        'effectiveNeighborCount': float(1.0 / np.sum(weights ** 2)),
    }


def build_memory(shards: list[tuple[int, dict[str, np.ndarray]]], selected_k: int, selected_action_weight: float, selected_shrinkage: float) -> dict[str, np.ndarray]:
    if tuple(sorted(seed for seed, _ in shards)) != tuple(sorted(TRAIN_SEEDS)):
        raise AssertionError('training-shard seed rectangle drifted')

    parent_visual = []
    action_delta = []
    y_delta = []
    valid = []
    route_idx = []
    family_idx = []
    row_seed = []
    for seed, data in sorted(shards):
        X = np.asarray(data['X'], dtype=np.float64)
        Y = np.asarray(data['Y_delta'], dtype=np.float64)
        r = np.asarray(data['route_idx'], dtype=np.int16)
        f = np.asarray(data['family_idx'], dtype=np.int16)
        v = np.asarray(data['valid'], dtype=np.float64)
        if len(X) != 1152 or Y.shape != (1152, wm.VISUAL_DIM):
            raise AssertionError(f'training shard {seed} shape drifted')
        parent_visual.append(parent_visual_from_x(X))
        action_delta.append(action_delta_from_x(X))
        y_delta.append(Y)
        valid.append(v)
        route_idx.append(r)
        family_idx.append(f)
        row_seed.append(np.full(len(X), int(seed), dtype=np.int64))

    pv = np.concatenate(parent_visual, axis=0)
    ad = np.concatenate(action_delta, axis=0)
    yd = np.concatenate(y_delta, axis=0)
    vv = np.concatenate(valid, axis=0)
    rr = np.concatenate(route_idx, axis=0)
    ff = np.concatenate(family_idx, axis=0)
    ss = np.concatenate(row_seed, axis=0)
    expected = 1152 * len(TRAIN_SEEDS)
    if len(pv) != expected:
        raise AssertionError(f'memory rows {len(pv)} != {expected}')

    baseline = np.zeros((len(ld.ROUTES), ld.ACTION_FAMILY_COUNT, wm.VISUAL_DIM), dtype=np.float64)
    action_std = np.ones((len(ld.ROUTES), ld.ACTION_FAMILY_COUNT, wm.MATH_DIM), dtype=np.float64)
    for ri in range(len(ld.ROUTES)):
        for fi in range(ld.ACTION_FAMILY_COUNT):
            mask = (rr == ri) & (ff == fi)
            if int(mask.sum()) != len(TRAIN_SEEDS) * 48:
                raise AssertionError(f'stratum count drift route={ri} family={fi}: {int(mask.sum())}')
            baseline[ri, fi] = yd[mask].mean(axis=0)
            action_std[ri, fi] = action_std_for_stratum(ad[mask])

    return {
        'parent_visual': pv.astype(np.float32),
        'action_delta': ad.astype(np.float32),
        'y_delta': yd.astype(np.float32),
        'valid': vv.astype(np.float32),
        'route_idx': rr.astype(np.int16),
        'family_idx': ff.astype(np.int16),
        'row_seed': ss.astype(np.int64),
        'baseline_delta': baseline.astype(np.float32),
        'action_std': action_std.astype(np.float32),
        'selected_k': np.asarray([int(selected_k)], dtype=np.int32),
        'selected_action_weight': np.asarray([float(selected_action_weight)], dtype=np.float64),
        'selected_shrinkage': np.asarray([float(selected_shrinkage)], dtype=np.float64),
        'prior_train_run_id': np.asarray([PRIOR_TRAIN_RUN_ID], dtype=np.int64),
        'prior_train_head_sha': np.asarray([PRIOR_TRAIN_HEAD_SHA], dtype='U40'),
        'train_seeds': np.asarray(TRAIN_SEEDS, dtype=np.int64),
        'visual_dim': np.asarray([wm.VISUAL_DIM], dtype=np.int32),
        'math_dim': np.asarray([wm.MATH_DIM], dtype=np.int32),
    }


def save_memory(path: Path, memory: dict[str, np.ndarray]) -> None:
    np.savez_compressed(path, **memory)


def load_memory(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        memory = {k: data[k] for k in data.files}
    if int(memory['prior_train_run_id'][0]) != PRIOR_TRAIN_RUN_ID:
        raise AssertionError('memory provenance run drifted')
    if str(memory['prior_train_head_sha'][0]) != PRIOR_TRAIN_HEAD_SHA:
        raise AssertionError('memory provenance head drifted')
    if tuple(int(x) for x in memory['train_seeds']) != TRAIN_SEEDS:
        raise AssertionError('memory training seeds drifted')
    if int(memory['visual_dim'][0]) != wm.VISUAL_DIM or int(memory['math_dim'][0]) != wm.MATH_DIM:
        raise AssertionError('memory dimensions drifted')
    return memory


def selected_config(memory: dict[str, np.ndarray]) -> tuple[int, float, float]:
    return (
        int(memory['selected_k'][0]),
        float(memory['selected_action_weight'][0]),
        float(memory['selected_shrinkage'][0]),
    )


def _stratum_indices(memory: dict[str, np.ndarray], route_index: int, family: int) -> np.ndarray:
    return np.flatnonzero((memory['route_idx'] == int(route_index)) & (memory['family_idx'] == int(family)))


def predict_delta(
    memory: dict[str, np.ndarray],
    parent_visual: np.ndarray,
    action_delta: np.ndarray,
    route_index: int,
    family: int,
) -> tuple[np.ndarray, dict]:
    idx = _stratum_indices(memory, route_index, family)
    k, action_weight, shrinkage = selected_config(memory)
    neighbor_delta, diag = predict_delta_from_arrays(
        parent_visual,
        action_delta,
        memory['parent_visual'][idx],
        memory['action_delta'][idx],
        memory['y_delta'][idx],
        memory['action_std'][int(route_index), int(family)],
        k,
        action_weight,
    )
    baseline = mean_delta(memory, route_index, family)
    pred = baseline + float(shrinkage) * (neighbor_delta - baseline)
    diag = dict(diag)
    diag['shrinkage'] = float(shrinkage)
    return pred, diag


def mean_delta(memory: dict[str, np.ndarray], route_index: int, family: int) -> np.ndarray:
    return np.asarray(memory['baseline_delta'][int(route_index), int(family)], dtype=np.float64)


def action_delta(route: str, parent_genome: dict, child_genome: dict) -> np.ndarray:
    return wm.math_vector(route, child_genome) - wm.math_vector(route, parent_genome)


def predict_child_visual(
    memory: dict[str, np.ndarray],
    parent_visual: np.ndarray,
    route: str,
    parent_genome: dict,
    child_genome: dict,
    family: int,
    mode: str,
) -> tuple[np.ndarray, dict]:
    ri = ld.ROUTES.index(route)
    ad = action_delta(route, parent_genome, child_genome)
    if mode == 'memory':
        delta, diag = predict_delta(memory, parent_visual, ad, ri, int(family))
    elif mode == 'mean':
        delta = mean_delta(memory, ri, int(family))
        diag = {'neighborCount': 0, 'nearestDistance': math.nan, 'meanNeighborDistance': math.nan, 'effectiveNeighborCount': math.nan}
    else:
        raise KeyError(mode)
    predicted = wm.sanitize_visual(np.asarray(parent_visual, dtype=np.float64) + np.asarray(delta, dtype=np.float64))
    return predicted, diag


def predict_children(
    memory: dict[str, np.ndarray],
    parent_visual: np.ndarray,
    route: str,
    parent_genome: dict,
    actions: list[tuple[dict, int]],
    mode: str,
) -> tuple[np.ndarray, list[dict]]:
    predicted = []
    diagnostics = []
    for child, family in actions:
        pv, diag = predict_child_visual(memory, parent_visual, route, parent_genome, child, family, mode)
        predicted.append(pv)
        diagnostics.append(diag)
    return np.asarray(predicted, dtype=np.float64), diagnostics
