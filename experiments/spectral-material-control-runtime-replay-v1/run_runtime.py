#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
METRIC_DIR = ROOT / 'experiments' / 'spectral-material-control-v1'
for p in (PROTO, METRIC_DIR):
    sys.path.insert(0, str(p))

from orbit_representation import register_orbit
register_orbit()

import core
import fast_grayscale_metric as metric
import material_control
import search_engine
from targets_runtime import build_targets_runtime

ROUTES = ('recurrence', 'orbit', 'filament')
TIMES = tuple(core.TIMES)
CANONICAL_TIME = 90
SMOKE_SEED = 123999
MASTER_SEEDS = (
    124003, 124009, 124021, 124037,
    124051, 124067, 124087, 124097,
    124121, 124123, 124133, 124139,
    124147, 124153, 124171, 124181,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str, mode: str | None) -> dict:
    brief = {
        'name': 'spectral-material-control-runtime-replay-v1',
        'artistic_intent': 'mechanical runtime replay only; selector is not outcome authority',
        'routes': [route],
        'bbox_target': [.55, .82],
        'starts_per_route': 1,
        'explore_per_basin': 4,
        'roundA_per_survivor': 4,
        'total_extra_budget': 12,
    }
    if mode is not None:
        brief['mutation_portfolio'] = mode
    return brief


def _phenotype_hash(cand) -> str:
    h = hashlib.sha256()
    for t in TIMES:
        h.update(core.render_candidate_frame(cand, t).tobytes())
        h.update(b'\0')
    return h.hexdigest()


def _trajectory(state, report) -> dict:
    return {
        'candidates': {
            cid: {
                'route': c.route,
                'basin': c.basin,
                'genome': c.genome,
                'parentId': c.parent_id,
                'stage': c.stage,
                'valid': bool(c.checks.get('valid', False)),
                'generationOperator': c.checks.get('generationOperator'),
                'phenotype': _phenotype_hash(c),
            }
            for cid, c in sorted(state.candidates.items())
        },
        'stageDecisions': state.stage_decisions,
        'winnerId': state.winner_id,
        'selectionStatus': report['selectionStatus'],
        'artisticFrontier': report['artisticFrontier'],
        'provisionalChampion': report['provisionalChampion'],
    }


def _run(route: str, seed: int, mode: str | None, root: Path, label: str):
    out = root / f'{route}-{label}'
    state, report = search_engine.run_search(_brief(route, mode), seed, out)
    return state, report


def _start_candidate(state):
    starts = [c for c in state.candidates.values() if c.stage == 'start' and c.checks.get('valid', False)]
    if len(starts) != 1:
        raise AssertionError(f'expected one valid start, found {len(starts)}')
    return starts[0]


def _valid_images(state):
    return [core.render_candidate_frame(c, CANONICAL_TIME) for c in state.candidates.values() if c.checks.get('valid', False)]


def _recovery(image, target_image) -> float:
    return 1.0 - float(metric.sparse_geometry_distance((image,), (target_image,))['distance'])


def _diag(state, report) -> dict:
    challengers = [c for c in state.candidates.values() if c.stage != 'start' and not c.id.endswith(tuple(f'-invalid{i}' for i in range(1, 21)))]
    # Invalid start attempts are explicitly outside the 20-challenger budget.
    generated = [c for c in challengers if c.checks.get('generationOperator') in {'native', 'spectral'}]
    native = [c for c in generated if c.checks.get('generationOperator') == 'native']
    spectral = [c for c in generated if c.checks.get('generationOperator') == 'spectral']
    for c in spectral:
        record = c.genome.get(material_control.CONTROL_KEY)
        if not isinstance(record, dict):
            raise AssertionError('spectral candidate missing serialized material control')
        if record.get('type') != material_control.CONTROL_TYPE or int(record.get('bandwidth', -1)) != 2 or float(record.get('amplitude', -1)) != 16.0:
            raise AssertionError('spectral material-control record drift')
        if len(record.get('coefficients', [])) != 25:
            raise AssertionError('spectral coefficient dimension drift')
    return {
        'totalChallengers': len(generated),
        'nativeChallengers': len(native),
        'spectralChallengers': len(spectral),
        'nativeValid': sum(bool(c.checks.get('valid', False)) for c in native),
        'spectralValid': sum(bool(c.checks.get('valid', False)) for c in spectral),
        'reportOperatorCounts': dict(report['generationOperatorCounts']),
    }


def smoke(seed: int) -> dict:
    if seed != SMOKE_SEED:
        raise ValueError('smoke uses only frozen excluded seed')
    routes = {}
    with tempfile.TemporaryDirectory(prefix='runtime-replay-smoke-') as td:
        root = Path(td)
        for route in ROUTES:
            omitted_state, omitted_report = _run(route, seed, None, root, 'native-omitted')
            explicit_state, explicit_report = _run(route, seed, search_engine.NATIVE_ONLY, root, 'native-explicit')
            mixed1_state, mixed1_report = _run(route, seed, search_engine.MIXED_1D_V1, root, 'mixed-1')
            mixed2_state, mixed2_report = _run(route, seed, search_engine.MIXED_1D_V1, root, 'mixed-2')
            native_replay = _trajectory(omitted_state, omitted_report) == _trajectory(explicit_state, explicit_report)
            mixed_replay = _trajectory(mixed1_state, mixed1_report) == _trajectory(mixed2_state, mixed2_report)
            start_same = _phenotype_hash(_start_candidate(omitted_state)) == _phenotype_hash(_start_candidate(mixed1_state))
            nd = _diag(omitted_state, omitted_report); md = _diag(mixed1_state, mixed1_report)
            routes[route] = {
                'nativeOmittedEqualsExplicit': native_replay,
                'mixedDeterministicReplay': mixed_replay,
                'sharedStartPhenotype': start_same,
                'nativeDiagnostics': nd,
                'mixedDiagnostics': md,
            }
    hard = {
        'allRoutesIntrinsic1D': all(int(core.ROUTES[r]['intrinsic_dimension']) == 1 for r in ROUTES),
        'nativeReplayExact': all(v['nativeOmittedEqualsExplicit'] for v in routes.values()),
        'mixedReplayExact': all(v['mixedDeterministicReplay'] for v in routes.values()),
        'sharedStartsExact': all(v['sharedStartPhenotype'] for v in routes.values()),
        'nativeBudgetExact': all(v['nativeDiagnostics']['totalChallengers'] == 20 and v['nativeDiagnostics']['nativeChallengers'] == 20 and v['nativeDiagnostics']['spectralChallengers'] == 0 for v in routes.values()),
        'mixedBudgetExact': all(v['mixedDiagnostics']['totalChallengers'] == 20 and v['mixedDiagnostics']['nativeChallengers'] == 10 and v['mixedDiagnostics']['spectralChallengers'] == 10 for v in routes.values()),
    }
    if not all(hard.values()):
        raise AssertionError(f'smoke hard invariant failure: {hard}')
    return {'version': 1, 'seed': seed, 'hardInvariants': hard, 'routes': routes}


def run_seed(seed: int) -> dict:
    if seed not in MASTER_SEEDS:
        raise ValueError(f'seed {seed} is not a frozen consumed seed')
    archives = {}
    route_diagnostics = {}
    with tempfile.TemporaryDirectory(prefix=f'runtime-replay-{seed}-') as td:
        root = Path(td)
        for route in ROUTES:
            native_state, native_report = _run(route, seed, None, root, 'native')
            mixed_state, mixed_report = _run(route, seed, search_engine.MIXED_1D_V1, root, 'mixed')
            nd = _diag(native_state, native_report); md = _diag(mixed_state, mixed_report)
            native_start = _start_candidate(native_state); mixed_start = _start_candidate(mixed_state)
            same_start = native_start.genome == mixed_start.genome and _phenotype_hash(native_start) == _phenotype_hash(mixed_start)
            route_diagnostics[route] = {
                'sameStart': same_start,
                'native': nd,
                'mixed': md,
            }
            archives[route] = {
                'nativeImages': _valid_images(native_state),
                'mixedImages': _valid_images(mixed_state),
            }

        # Outcome construction/scoring happens only after every trajectory exists.
        targets = build_targets_runtime()
        cells = []
        for route in ROUTES:
            for target in targets:
                native_recovery = max(_recovery(im, target.image) for im in archives[route]['nativeImages'])
                mixed_recovery = max(_recovery(im, target.image) for im in archives[route]['mixedImages'])
                cells.append({
                    'masterSeed': seed,
                    'route': route,
                    'targetId': target.id,
                    'targetFamily': target.family,
                    'nativeRecovery': native_recovery,
                    'mixedRecovery': mixed_recovery,
                    'delta': mixed_recovery - native_recovery,
                })

    hard = {
        'routeSetExact': tuple(route_diagnostics) == ROUTES,
        'allRoutesIntrinsic1D': all(int(core.ROUTES[r]['intrinsic_dimension']) == 1 for r in ROUTES),
        'sharedStartsExact': all(route_diagnostics[r]['sameStart'] for r in ROUTES),
        'nativeBudgetExact': all(route_diagnostics[r]['native']['totalChallengers'] == 20 and route_diagnostics[r]['native']['nativeChallengers'] == 20 and route_diagnostics[r]['native']['spectralChallengers'] == 0 for r in ROUTES),
        'mixedBudgetExact': all(route_diagnostics[r]['mixed']['totalChallengers'] == 20 and route_diagnostics[r]['mixed']['nativeChallengers'] == 10 and route_diagnostics[r]['mixed']['spectralChallengers'] == 10 for r in ROUTES),
        'cellCountExact': len(cells) == 45,
    }
    if not all(hard.values()):
        raise AssertionError(f'consumed hard invariant failure: {hard}')
    return {
        'version': 1,
        'masterSeed': seed,
        'artisticEvidence': False,
        'settings': {
            'routes': list(ROUTES),
            'startsPerRoute': 1,
            'explorePerBasin': 4,
            'roundAPerSurvivor': 4,
            'totalExtraBudget': 12,
            'challengersPerRouteArm': 20,
            'mixedNativePerRoute': 10,
            'mixedSpectralPerRoute': 10,
            'spectralBandwidth': 2,
            'spectralAmplitude': 16.0,
            'canonicalTime': CANONICAL_TIME,
            'metric': 'sparse-geometry-v1-exact-fast-grayscale',
            'selector': 'deterministic-temporal-selector-runtime-driver-only',
        },
        'hardInvariants': hard,
        'routeDiagnostics': route_diagnostics,
        'cells': cells,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--output')
    args = p.parse_args()
    result = smoke(args.seed) if args.smoke else run_seed(args.seed)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
