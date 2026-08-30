from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
PERCEPTUAL = ROOT / 'experiments' / 'semantic-perceptual-steering-v1'
sys.path.insert(0, str(PROTO))
sys.path.insert(0, str(PERCEPTUAL))

from orbit_representation import register_orbit
register_orbit()

import core
import perceptual_metric as pm
from material_control import CONTROL_KEY, control_record

ROUTES = ('recurrence', 'orbit', 'filament')
MODEL_BLOCKS = ('grid16', 'grid8', 'projectionX', 'projectionY', 'polar', 'orientation', 'radial', 'symmetry', 'topology')
HIDDEN = 512
RIDGE = 1e-2
FEATURE_SEED = 733000001


def _parameter_keys() -> tuple[str, ...]:
    keys = set()
    for i, route in enumerate(ROUTES):
        genome = core.ROUTES[route]['seed'](random.Random(733000100 + i))
        keys.update(k for k, v in genome.items() if k != CONTROL_KEY and isinstance(v, (int, float)))
    return tuple(sorted(keys))


PARAM_KEYS = _parameter_keys()
COEFF_COUNT = 25


def native_genome(genome: dict) -> dict:
    return {k: v for k, v in genome.items() if k != CONTROL_KEY}


def math_vector(route: str, genome: dict) -> np.ndarray:
    if route not in ROUTES:
        raise KeyError(route)
    native = native_genome(genome)
    route_onehot = [1.0 if route == r else 0.0 for r in ROUTES]
    numeric = [float(native.get(k, 0.0)) for k in PARAM_KEYS]
    record = control_record(genome)
    has_control = 1.0 if record is not None else 0.0
    coeffs = [0.0] * COEFF_COUNT
    if record is not None:
        values = [float(v) for v in record['coefficients']]
        if len(values) != COEFF_COUNT:
            raise AssertionError('spectral coefficient dimension drift')
        coeffs = values
    return np.asarray(route_onehot + numeric + [has_control] + coeffs, dtype=np.float64)


def descriptor_dict(image) -> dict[str, np.ndarray]:
    return pm.descriptor(image)


def visual_vector_from_descriptor(desc: dict[str, np.ndarray]) -> np.ndarray:
    return np.concatenate([np.asarray(desc[k], dtype=np.float64).reshape(-1) for k in MODEL_BLOCKS])


def visual_vector(image) -> np.ndarray:
    return visual_vector_from_descriptor(descriptor_dict(image))


def visual_vector_for_candidate(cand) -> np.ndarray:
    return visual_vector(pm.binary_candidate_image(cand))


def block_slices() -> dict[str, slice]:
    dummy = pm.descriptor(core.draw_points([]))
    out = {}
    start = 0
    for key in MODEL_BLOCKS:
        n = int(np.asarray(dummy[key]).size)
        out[key] = slice(start, start + n)
        start += n
    return out


BLOCK_SLICES = block_slices()
VISUAL_DIM = max(s.stop for s in BLOCK_SLICES.values())
MATH_DIM = len(ROUTES) + len(PARAM_KEYS) + 1 + COEFF_COUNT


def _mass(values: np.ndarray) -> np.ndarray:
    x = np.clip(np.asarray(values, dtype=np.float64), 0.0, None)
    total = float(x.sum())
    return x / total if total > 1e-12 else np.zeros_like(x)


def sanitize_visual(vector: np.ndarray) -> np.ndarray:
    v = np.asarray(vector, dtype=np.float64).reshape(-1).copy()
    if v.size != VISUAL_DIM:
        raise ValueError(f'visual dimension {v.size} != {VISUAL_DIM}')
    for key in ('grid16', 'grid8', 'projectionX', 'projectionY', 'polar', 'orientation'):
        sl = BLOCK_SLICES[key]
        v[sl] = _mass(v[sl])
    for key in ('radial', 'symmetry', 'topology'):
        sl = BLOCK_SLICES[key]
        v[sl] = np.clip(v[sl], 0.0, 1.0)
    return v


def model_distance(a: np.ndarray, b: np.ndarray) -> float:
    a = sanitize_visual(a); b = sanitize_visual(b)
    grid = float(np.mean([
        0.5 * np.abs(a[BLOCK_SLICES['grid16']] - b[BLOCK_SLICES['grid16']]).sum(),
        0.5 * np.abs(a[BLOCK_SLICES['grid8']] - b[BLOCK_SLICES['grid8']]).sum(),
    ]))
    projection = float(0.25 * (
        np.abs(a[BLOCK_SLICES['projectionX']] - b[BLOCK_SLICES['projectionX']]).sum() +
        np.abs(a[BLOCK_SLICES['projectionY']] - b[BLOCK_SLICES['projectionY']]).sum()
    ))
    polar = float(0.5 * np.abs(a[BLOCK_SLICES['polar']] - b[BLOCK_SLICES['polar']]).sum())
    orientation = float(0.5 * np.abs(a[BLOCK_SLICES['orientation']] - b[BLOCK_SLICES['orientation']]).sum())
    radial = float(np.mean(np.abs(a[BLOCK_SLICES['radial']] - b[BLOCK_SLICES['radial']])))
    symmetry = float(np.mean(np.abs(a[BLOCK_SLICES['symmetry']] - b[BLOCK_SLICES['symmetry']])))
    topology = float(np.mean(np.abs(a[BLOCK_SLICES['topology']] - b[BLOCK_SLICES['topology']])))
    value = float(np.mean([grid, projection, polar, orientation, radial, symmetry, topology]))
    if not math.isfinite(value):
        raise AssertionError('non-finite model distance')
    return value


def fit_model(X: np.ndarray, Y: np.ndarray, valid: np.ndarray, route_idx: np.ndarray, operator_idx: np.ndarray) -> dict[str, np.ndarray]:
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    valid = np.asarray(valid, dtype=np.float64).reshape(-1, 1)
    if X.ndim != 2 or X.shape[1] != MATH_DIM:
        raise ValueError('bad X shape')
    if Y.ndim != 2 or Y.shape[1] != VISUAL_DIM or Y.shape[0] != X.shape[0]:
        raise ValueError('bad Y shape')
    if valid.shape[0] != X.shape[0]:
        raise ValueError('bad validity shape')

    x_mean = X.mean(axis=0)
    x_std = X.std(axis=0)
    x_std[x_std < 1e-8] = 1.0
    Xz = (X - x_mean) / x_std

    y_mean = Y.mean(axis=0)
    y_std = Y.std(axis=0)
    y_std[y_std < 1e-8] = 1.0
    Yz = (Y - y_mean) / y_std

    rng = np.random.default_rng(FEATURE_SEED)
    W = rng.normal(0.0, 1.0 / math.sqrt(MATH_DIM), size=(MATH_DIM, HIDDEN))
    b = rng.uniform(-math.pi, math.pi, size=HIDDEN)
    H = np.tanh(Xz @ W + b)
    Z = np.concatenate([np.ones((len(X), 1)), Xz, H], axis=1)
    eye = np.eye(Z.shape[1]); eye[0, 0] = 0.0
    gram = Z.T @ Z + RIDGE * eye
    rhs_visual = Z.T @ Yz
    rhs_valid = Z.T @ valid
    beta_visual = np.linalg.solve(gram, rhs_visual)
    beta_valid = np.linalg.solve(gram, rhs_valid)

    baseline = np.zeros((len(ROUTES), 2, VISUAL_DIM), dtype=np.float64)
    baseline_valid = np.zeros((len(ROUTES), 2), dtype=np.float64)
    for r in range(len(ROUTES)):
        for o in range(2):
            mask = (route_idx == r) & (operator_idx == o)
            if not np.any(mask):
                raise AssertionError(f'missing training stratum route={r} operator={o}')
            baseline[r, o] = Y[mask].mean(axis=0)
            baseline_valid[r, o] = valid[mask, 0].mean()

    return {
        'x_mean': x_mean, 'x_std': x_std,
        'y_mean': y_mean, 'y_std': y_std,
        'W': W, 'b': b,
        'beta_visual': beta_visual, 'beta_valid': beta_valid,
        'baseline_visual': baseline, 'baseline_valid': baseline_valid,
        'parameter_keys': np.asarray(PARAM_KEYS, dtype='U64'),
        'model_blocks': np.asarray(MODEL_BLOCKS, dtype='U32'),
    }


def _design(model: dict[str, np.ndarray], X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    Xz = (X - model['x_mean']) / model['x_std']
    H = np.tanh(Xz @ model['W'] + model['b'])
    return np.concatenate([np.ones((len(X), 1)), Xz, H], axis=1)


def predict(model: dict[str, np.ndarray], X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    Z = _design(model, X)
    Yz = Z @ model['beta_visual']
    Y = Yz * model['y_std'] + model['y_mean']
    validity = np.clip((Z @ model['beta_valid']).reshape(-1), 0.0, 1.0)
    return Y, validity


def save_model(path: Path, model: dict[str, np.ndarray]) -> None:
    np.savez_compressed(path, **model)


def load_model(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        model = {k: data[k] for k in data.files}
    if tuple(str(x) for x in model['parameter_keys']) != PARAM_KEYS:
        raise AssertionError('model parameter-key contract drifted')
    if tuple(str(x) for x in model['model_blocks']) != MODEL_BLOCKS:
        raise AssertionError('model visual-block contract drifted')
    return model


def metadata() -> dict:
    return {
        'routes': list(ROUTES),
        'parameterKeys': list(PARAM_KEYS),
        'mathDim': MATH_DIM,
        'visualBlocks': list(MODEL_BLOCKS),
        'visualDim': VISUAL_DIM,
        'hidden': HIDDEN,
        'ridge': RIDGE,
        'featureSeed': FEATURE_SEED,
    }


if __name__ == '__main__':
    print(json.dumps(metadata(), indent=2, sort_keys=True))
