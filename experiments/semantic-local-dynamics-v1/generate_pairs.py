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
import local_dynamics as ld


def _valid_parent_pair(seed: int, route: str, base_index: int, rng: random.Random):
    for attempt in range(256):
        base = core.ROUTES[route]['seed'](rng)
        native_visual, native_valid = ld.visual_for_state(route, base, f'{route}-base-{base_index}-{attempt}-native')
        if not native_valid:
            continue
        spectral = with_spectral_control(
            base,
            derived_seed(seed, ld.STREAM, 'parent-field', route, base_index, attempt),
        )
        spectral_visual, spectral_valid = ld.visual_for_state(route, spectral, f'{route}-base-{base_index}-{attempt}-spectral')
        if spectral_valid:
            return (base, native_visual), (spectral, spectral_visual), attempt
    raise RuntimeError(f'failed to draw valid native+spectral parent pair route={route} base={base_index}')


def generate(seed: int, bases_per_route: int) -> dict[str, np.ndarray]:
    X = []
    Y_delta = []
    valid = []
    route_idx = []
    family_idx = []
    parent_valid = []
    parent_attempts = []

    for ri, route in enumerate(ld.ROUTES):
        rng = random.Random(derived_seed(seed, ld.STREAM, 'training-bases', route))
        for base_index in range(int(bases_per_route)):
            native, spectral, attempts = _valid_parent_pair(seed, route, base_index, rng)
            parent_attempts.append(attempts)
            for material_index, (parent_genome, parent_visual) in enumerate((native, spectral)):
                parent_valid.append(1)
                action_seed = derived_seed(seed, ld.STREAM, 'training-actions', route, base_index, material_index)
                actions = ld.action_set(route, parent_genome, action_seed, ld.ACTION_FAMILY_COUNT)
                if [family for _, family in actions] != list(range(ld.ACTION_FAMILY_COUNT)):
                    raise AssertionError('action-family rectangle drifted')
                for action_index, (child_genome, family) in enumerate(actions):
                    child_visual, child_valid = ld.visual_for_state(
                        route,
                        child_genome,
                        f'{route}-{base_index}-{material_index}-a{action_index}',
                    )
                    X.append(ld.input_vector(parent_visual, route, parent_genome, child_genome))
                    Y_delta.append(child_visual - parent_visual)
                    valid.append(1.0 if child_valid else 0.0)
                    route_idx.append(ri)
                    family_idx.append(family)

    expected = len(ld.ROUTES) * int(bases_per_route) * 2 * ld.ACTION_FAMILY_COUNT
    if len(X) != expected:
        raise AssertionError(f'transition rows {len(X)} != {expected}')
    return {
        'X': np.asarray(X, dtype=np.float64),
        'Y_delta': np.asarray(Y_delta, dtype=np.float64),
        'valid': np.asarray(valid, dtype=np.float64),
        'route_idx': np.asarray(route_idx, dtype=np.int16),
        'family_idx': np.asarray(family_idx, dtype=np.int16),
        'seed': np.asarray([int(seed)], dtype=np.int64),
        'bases_per_route': np.asarray([int(bases_per_route)], dtype=np.int32),
        'row_count': np.asarray([expected], dtype=np.int32),
        'parent_valid': np.asarray(parent_valid, dtype=np.int8),
        'parent_attempts': np.asarray(parent_attempts, dtype=np.int16),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--bases-per-route', type=int, default=24)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = generate(args.seed, args.bases_per_route)
    np.savez_compressed(args.output, **data)


if __name__ == '__main__':
    main()
