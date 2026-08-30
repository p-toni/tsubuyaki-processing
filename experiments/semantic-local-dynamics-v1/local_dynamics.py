from __future__ import annotations

import copy
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
WM_DIR = ROOT / 'experiments' / 'semantic-world-model-navigation-v1'
SPECTRAL_DIR = ROOT / 'experiments' / 'sampling-invariance-search-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(WM_DIR))
sys.path.insert(0, str(SPECTRAL_DIR))

from orbit_representation import register_orbit
register_orbit()

import core
from material_control import (
    CONTROL_KEY,
    candidate_geometry,
    candidate_points,
    control_record,
    mutate_native,
    with_spectral_control,
    _velocity_rms,
)
from rng_streams import derived_seed
from spectral_operator import geodesic_mutate
import world_model as wm

STREAM = 'semantic-local-dynamics-v1'
ROUTES = wm.ROUTES
ACTION_SCALES = (0.35, 0.35, 0.70, 0.70, 1.00, 1.00)
MATERIAL_ANGLES = (0.04, 0.12)
ACTION_FAMILY_COUNT = 8
HIDDEN = 512
RIDGE = 2e-2
FEATURE_SEED = 734000001


def quick_candidate(route: str, genome: dict, cid: str):
    cand = core.Candidate(cid, route, cid, genome, None, 'local-dynamics')
    geometry_fn = lambda g, t: candidate_geometry(core.ROUTES[route], g, t, core.W, core.H)
    cand.checks = core.check_candidate(route, genome, core.TIMES, geometry_fn, core.W, core.H)
    return cand


def visual_for_state(route: str, genome: dict, cid: str) -> tuple[np.ndarray, bool]:
    cand = quick_candidate(route, genome, cid)
    return wm.visual_vector_for_candidate(cand), bool(cand.checks.get('valid', False))


def _material_child(route: str, genome: dict, seed: int, slot: int) -> dict:
    record = control_record(genome)
    if record is None:
        return with_spectral_control(genome, derived_seed(seed, STREAM, 'add-field', route, slot))
    out = copy.deepcopy(genome)
    rec = copy.deepcopy(record)
    coefficients = np.asarray(rec['coefficients'], dtype=float)
    theta = MATERIAL_ANGLES[slot % 2]
    rng = np.random.default_rng(derived_seed(seed, STREAM, 'field-geodesic', route, slot))
    child_coefficients = geodesic_mutate(coefficients, rng, theta)
    rec['coefficients'] = [float(x) for x in child_coefficients]
    rec['velocityRms'] = float(_velocity_rms(child_coefficients))
    out[CONTROL_KEY] = rec
    return out


def action_child(route: str, genome: dict, seed: int, action_index: int) -> tuple[dict, int]:
    family = int(action_index) % ACTION_FAMILY_COUNT
    if family < 6:
        rng = random.Random(derived_seed(seed, STREAM, 'native-action', route, action_index))
        child = mutate_native(core.ROUTES[route], genome, rng, ACTION_SCALES[family])
    else:
        child = _material_child(route, genome, seed, family - 6)
    return child, family


def action_set(route: str, genome: dict, seed: int, count: int) -> list[tuple[dict, int]]:
    return [action_child(route, genome, derived_seed(seed, STREAM, 'proposal', j), j) for j in range(int(count))]


def route_indicator(route: str, genome: dict) -> np.ndarray:
    record = control_record(genome)
    return np.asarray(
        [1.0 if route == r else 0.0 for r in ROUTES] + [1.0 if record is not None else 0.0],
        dtype=np.float64,
    )


def input_vector(parent_visual: np.ndarray, route: str, parent_genome: dict, child_genome: dict) -> np.ndarray:
    delta_math = wm.math_vector(route, child_genome) - wm.math_vector(route, parent_genome)
    return np.concatenate([
        np.asarray(parent_visual, dtype=np.float64).reshape(-1),
        route_indicator(route, parent_genome),
        delta_math,
    ])


INPUT_DIM = wm.VISUAL_DIM + len(ROUTES) + 1 + wm.MATH_DIM
OUTPUT_DIM = wm.VISUAL_DIM


def fit_model(
    X: np.ndarray,
    Y_delta: np.ndarray,
    valid: np.ndarray,
    route_idx: np.ndarray,
    family_idx: np.ndarray,
) -> dict[str, np.ndarray]:
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y_delta, dtype=np.float64)
    valid = np.asarray(valid, dtype=np.float64).reshape(-1, 1)
    route_idx = np.asarray(route_idx, dtype=np.int16)
    family_idx = np.asarray(family_idx, dtype=np.int16)
    if X.ndim != 2 or X.shape[1] != INPUT_DIM:
        raise ValueError(f'bad X shape {X.shape}, expected (*,{INPUT_DIM})')
    if Y.shape != (len(X), OUTPUT_DIM):
        raise ValueError(f'bad Y shape {Y.shape}')

    x_mean = X.mean(axis=0)
    x_std = X.std(axis=0)
    x_std[x_std < 1e-8] = 1.0
    Xz = (X - x_mean) / x_std

    y_mean = Y.mean(axis=0)
    y_std = Y.std(axis=0)
    y_std[y_std < 1e-8] = 1.0
    Yz = (Y - y_mean) / y_std

    rng = np.random.default_rng(FEATURE_SEED)
    W = rng.normal(0.0, 1.0 / math.sqrt(INPUT_DIM), size=(INPUT_DIM, HIDDEN))
    b = rng.uniform(-math.pi, math.pi, size=HIDDEN)
    H = np.tanh(Xz @ W + b)
    Z = np.concatenate([np.ones((len(X), 1)), Xz, H], axis=1)
    eye = np.eye(Z.shape[1]); eye[0, 0] = 0.0
    gram = Z.T @ Z + RIDGE * eye
    beta_delta = np.linalg.solve(gram, Z.T @ Yz)
    beta_valid = np.linalg.solve(gram, Z.T @ valid)

    baseline_delta = np.zeros((len(ROUTES), ACTION_FAMILY_COUNT, OUTPUT_DIM), dtype=np.float64)
    baseline_valid = np.zeros((len(ROUTES), ACTION_FAMILY_COUNT), dtype=np.float64)
    for r in range(len(ROUTES)):
        for f in range(ACTION_FAMILY_COUNT):
            mask = (route_idx == r) & (family_idx == f)
            if not np.any(mask):
                raise AssertionError(f'missing training stratum route={r} family={f}')
            baseline_delta[r, f] = Y[mask].mean(axis=0)
            baseline_valid[r, f] = valid[mask, 0].mean()

    return {
        'x_mean': x_mean,
        'x_std': x_std,
        'y_mean': y_mean,
        'y_std': y_std,
        'W': W,
        'b': b,
        'beta_delta': beta_delta,
        'beta_valid': beta_valid,
        'baseline_delta': baseline_delta,
        'baseline_valid': baseline_valid,
        'model_blocks': np.asarray(wm.MODEL_BLOCKS, dtype='U32'),
        'routes': np.asarray(ROUTES, dtype='U32'),
        'input_dim': np.asarray([INPUT_DIM], dtype=np.int32),
        'output_dim': np.asarray([OUTPUT_DIM], dtype=np.int32),
    }


def _design(model: dict[str, np.ndarray], X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    Xz = (X - model['x_mean']) / model['x_std']
    H = np.tanh(Xz @ model['W'] + model['b'])
    return np.concatenate([np.ones((len(X), 1)), Xz, H], axis=1)


def predict(model: dict[str, np.ndarray], X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    Z = _design(model, X)
    delta_z = Z @ model['beta_delta']
    delta = delta_z * model['y_std'] + model['y_mean']
    valid = np.clip((Z @ model['beta_valid']).reshape(-1), 0.0, 1.0)
    return delta, valid


def predict_children(
    model: dict[str, np.ndarray],
    parent_visual: np.ndarray,
    route: str,
    parent_genome: dict,
    children: list[dict],
) -> tuple[np.ndarray, np.ndarray]:
    X = np.asarray([input_vector(parent_visual, route, parent_genome, child) for child in children], dtype=np.float64)
    delta, valid = predict(model, X)
    predicted = np.asarray(parent_visual, dtype=np.float64)[None, :] + delta
    predicted = np.asarray([wm.sanitize_visual(v) for v in predicted], dtype=np.float64)
    return predicted, valid


def save_model(path: Path, model: dict[str, np.ndarray]) -> None:
    np.savez_compressed(path, **model)


def load_model(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        model = {k: data[k] for k in data.files}
    if int(model['input_dim'][0]) != INPUT_DIM or int(model['output_dim'][0]) != OUTPUT_DIM:
        raise AssertionError('local-dynamics dimensional contract drifted')
    if tuple(str(x) for x in model['routes']) != ROUTES:
        raise AssertionError('local-dynamics route contract drifted')
    if tuple(str(x) for x in model['model_blocks']) != wm.MODEL_BLOCKS:
        raise AssertionError('local-dynamics visual-block contract drifted')
    return model


def metadata() -> dict:
    return {
        'routes': list(ROUTES),
        'actionScales': list(ACTION_SCALES),
        'materialAngles': list(MATERIAL_ANGLES),
        'actionFamilyCount': ACTION_FAMILY_COUNT,
        'inputDim': INPUT_DIM,
        'outputDim': OUTPUT_DIM,
        'hidden': HIDDEN,
        'ridge': RIDGE,
        'featureSeed': FEATURE_SEED,
    }


if __name__ == '__main__':
    print(json.dumps(metadata(), indent=2, sort_keys=True))
