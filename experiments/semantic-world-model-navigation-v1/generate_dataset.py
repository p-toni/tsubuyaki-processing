from __future__ import annotations

import argparse
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

import core
from material_control import with_spectral_control
from rng_streams import derived_seed
import world_model as wm

STREAM = 'semantic-world-model-navigation-v1'


def _brief(route: str) -> dict:
    return {
        'name': STREAM,
        'artistic_intent': 'Target-blind generator world-model data.',
        'routes': [route],
        'bbox_target': [0.55, 0.82],
    }


def generate(seed: int, bases_per_route: int) -> dict[str, np.ndarray]:
    X = []; Y = []; valid = []; route_idx = []; operator_idx = []
    fingerprints = []
    for ri, route in enumerate(wm.ROUTES):
        rng = random.Random(derived_seed(seed, STREAM, 'dataset', route, 'bases'))
        brief = _brief(route)
        prefix = core.ROUTES[route].get('prefix', route[0].upper())
        for i in range(int(bases_per_route)):
            base = core.ROUTES[route]['seed'](rng)
            states = (
                ('native', base),
                ('spectral', with_spectral_control(base, derived_seed(seed, STREAM, 'dataset', route, i, 'field'))),
            )
            for oi, (operator, genome) in enumerate(states):
                cand = core.Candidate(f'{prefix}-{i:04d}-{operator}', route, f'{prefix}-{i:04d}', genome, None, 'world-model-data')
                core.evaluate_candidate(cand, brief)
                X.append(wm.math_vector(route, genome))
                Y.append(wm.visual_vector_for_candidate(cand))
                valid.append(1.0 if cand.checks.get('valid', False) else 0.0)
                route_idx.append(ri); operator_idx.append(oi)
                fingerprints.append(hash((route, i, operator, tuple(sorted((k, str(v)) for k, v in wm.native_genome(genome).items())))))
    expected = len(wm.ROUTES) * int(bases_per_route) * 2
    if len(X) != expected:
        raise AssertionError(f'dataset rows {len(X)} != {expected}')
    return {
        'X': np.asarray(X, dtype=np.float64),
        'Y': np.asarray(Y, dtype=np.float64),
        'valid': np.asarray(valid, dtype=np.float64),
        'route_idx': np.asarray(route_idx, dtype=np.int16),
        'operator_idx': np.asarray(operator_idx, dtype=np.int8),
        'seed': np.asarray([int(seed)], dtype=np.int64),
        'bases_per_route': np.asarray([int(bases_per_route)], dtype=np.int32),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--bases-per-route', type=int, default=80)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = generate(args.seed, args.bases_per_route)
    np.savez_compressed(args.output, **data)


if __name__ == '__main__':
    main()
