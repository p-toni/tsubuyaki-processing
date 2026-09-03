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
for p in (HERE, PROTO, METRIC_DIR):
    sys.path.insert(0, str(p))
sys.path.insert(0, str(HERE))

import core
import fast_grayscale_metric as metric
import material_control
import search_engine
from targets_runtime import build_targets_family_runtime, target_contract_family_runtime

ROUTE = 'family'
TIMES = tuple(core.TIMES)
CANONICAL_TIME = 90
LAW_FAILURE = 'shared family law loses sibling-scale coherence'
SMOKE_SEED = 764999
MASTER_SEEDS = (
    764003, 764019, 764037, 764053, 764071,
    764089, 764107, 764127, 764149, 764167,
    764181, 764199, 764223, 764239, 764257,
    764277, 764293, 764311, 764331, 764349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _brief(route: str, mode: str | None) -> dict:
    brief = {
        'name': 'family-projected-spectral-runtime-replay-v1',
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
    starts = [
        c for c in state.candidates.values()
        if c.stage == 'start' and c.checks.get('valid', False)
    ]
    if len(starts) != 1:
        raise AssertionError(f'expected one valid start, found {len(starts)}')
    return starts[0]


def _valid_images(state):
    return [
        core.render_candidate_frame(c, CANONICAL_TIME)
        for c in state.candidates.values()
        if c.checks.get('valid', False)
    ]


def _recovery(image, target_image) -> float:
    return 1.0 - float(
        metric.sparse_geometry_distance((image,), (target_image,))['distance']
    )


def _diag(state, report) -> dict:
    generated = [
        c for c in state.candidates.values()
        if c.checks.get('generationOperator') in {'native', 'spectral', 'projected-spectral'}
    ]
    native = [c for c in generated if c.checks.get('generationOperator') == 'native']
    spectral = [c for c in generated if c.checks.get('generationOperator') == 'spectral']
    projected = [c for c in generated if c.checks.get('generationOperator') == 'projected-spectral']

    for c in spectral:
        record = c.genome.get(material_control.CONTROL_KEY)
        if not isinstance(record, dict):
            raise AssertionError('generic spectral candidate missing serialized material control')
        if (
            record.get('type') != material_control.CONTROL_TYPE
            or int(record.get('bandwidth', -1)) != 2
            or float(record.get('amplitude', -1)) != 16.0
            or len(record.get('coefficients', [])) != 25
        ):
            raise AssertionError('generic spectral material-control record drift')

    projected_law_failures = 0
    for c in projected:
        record = c.genome.get(material_control.CONTROL_KEY)
        if not isinstance(record, dict):
            raise AssertionError('projected candidate missing serialized material control')
        if (
            record.get('type') != material_control.FAMILY_PROJECTED_CONTROL_TYPE
            or int(record.get('bandwidth', -1)) != 2
            or float(record.get('amplitude', -1)) != 16.0
            or len(record.get('coefficients', [])) != 25
        ):
            raise AssertionError('family projected material-control record drift')
        projected_law_failures += sum(
            failure == LAW_FAILURE for failure in c.checks.get('failures', [])
        )

    return {
        'totalChallengers': len(generated),
        'nativeChallengers': len(native),
        'spectralChallengers': len(spectral),
        'projectedSpectralChallengers': len(projected),
        'nativeValid': sum(bool(c.checks.get('valid', False)) for c in native),
        'spectralValid': sum(bool(c.checks.get('valid', False)) for c in spectral),
        'projectedSpectralValid': sum(bool(c.checks.get('valid', False)) for c in projected),
        'projectedSiblingScaleLawFailures': projected_law_failures,
        'reportOperatorCounts': dict(report['generationOperatorCounts']),
        'eligibleRoutes': list(report['mutationPortfolioEligibleRoutes']),
    }


def smoke(seed: int) -> dict:
    if seed != SMOKE_SEED:
        raise ValueError('smoke uses only frozen excluded seed')
    target_contract = target_contract_family_runtime()
    with tempfile.TemporaryDirectory(prefix='family-runtime-replay-smoke-') as td:
        root = Path(td)
        omitted_state, omitted_report = _run(ROUTE, seed, None, root, 'native-omitted')
        explicit_state, explicit_report = _run(ROUTE, seed, search_engine.NATIVE_ONLY, root, 'native-explicit')
        mixed1_state, mixed1_report = _run(ROUTE, seed, search_engine.FAMILY_PROJECTED_V1, root, 'mixed-1')
        mixed2_state, mixed2_report = _run(ROUTE, seed, search_engine.FAMILY_PROJECTED_V1, root, 'mixed-2')
        sheet_state, sheet_report = _run('sheet', seed, search_engine.FAMILY_PROJECTED_V1, root, 'sheet-authority')
        recurrence_state, recurrence_report = _run('recurrence', seed, search_engine.MIXED_1D_V1, root, 'recurrence-existing-mode')

        native_replay = _trajectory(omitted_state, omitted_report) == _trajectory(explicit_state, explicit_report)
        mixed_replay = _trajectory(mixed1_state, mixed1_report) == _trajectory(mixed2_state, mixed2_report)
        start_same = _phenotype_hash(_start_candidate(omitted_state)) == _phenotype_hash(_start_candidate(mixed1_state))
        nd = _diag(omitted_state, omitted_report)
        md = _diag(mixed1_state, mixed1_report)
        sd = _diag(sheet_state, sheet_report)
        rd = _diag(recurrence_state, recurrence_report)

    hard = {
        'familyRouteClassExact': int(core.ROUTES['family']['intrinsic_dimension']) == 2,
        'nativeReplayExact': native_replay,
        'projectedReplayExact': mixed_replay,
        'sharedFamilyStartExact': start_same,
        'nativeBudgetExact': nd['totalChallengers'] == 20 and nd['nativeChallengers'] == 20 and nd['spectralChallengers'] == 0 and nd['projectedSpectralChallengers'] == 0,
        'familyProjectedBudgetExact': md['totalChallengers'] == 20 and md['nativeChallengers'] == 10 and md['projectedSpectralChallengers'] == 10 and md['spectralChallengers'] == 0,
        'familyProjectedAuthorityExact': md['eligibleRoutes'] == ['family'],
        'sheetExcludedFromFamilyMode': sd['totalChallengers'] == 20 and sd['nativeChallengers'] == 20 and sd['projectedSpectralChallengers'] == 0 and sd['spectralChallengers'] == 0 and sd['eligibleRoutes'] == [],
        'existing1DModeUnaffected': rd['totalChallengers'] == 20 and rd['nativeChallengers'] == 10 and rd['spectralChallengers'] == 10 and rd['projectedSpectralChallengers'] == 0 and rd['eligibleRoutes'] == ['recurrence'],
        'projectedLawFailureAbsent': md['projectedSiblingScaleLawFailures'] == 0,
        'freshTargetContractValid': bool(target_contract['valid']),
        'freshTargetsDisjointThroughFamilyPortfolio': bool(target_contract['disjointFromAllPriorSamplingMaterialTargetsThroughFamilyPortfolio']),
    }
    if not all(hard.values()):
        raise AssertionError(f'smoke hard invariant failure: {hard}')
    return {
        'version': 1,
        'experiment': 'family-projected-spectral-runtime-replay-v1',
        'seed': seed,
        'smoke': True,
        'hardInvariants': hard,
        'targetContract': target_contract,
        'family': {
            'nativeDiagnostics': nd,
            'mixedDiagnostics': md,
        },
        'scopeChecks': {
            'sheetDiagnostics': sd,
            'recurrence1DDiagnostics': rd,
        },
    }


def run_seed(seed: int) -> dict:
    if seed not in MASTER_SEEDS:
        raise ValueError(f'seed {seed} is not a frozen authoritative seed')
    with tempfile.TemporaryDirectory(prefix=f'family-runtime-replay-{seed}-') as td:
        root = Path(td)
        native_state, native_report = _run(ROUTE, seed, None, root, 'native')
        mixed_state, mixed_report = _run(ROUTE, seed, search_engine.FAMILY_PROJECTED_V1, root, 'mixed')
        nd = _diag(native_state, native_report)
        md = _diag(mixed_state, mixed_report)
        native_start = _start_candidate(native_state)
        mixed_start = _start_candidate(mixed_state)
        same_start = (
            native_start.genome == mixed_start.genome
            and _phenotype_hash(native_start) == _phenotype_hash(mixed_start)
        )
        native_images = _valid_images(native_state)
        mixed_images = _valid_images(mixed_state)

        # Target construction/scoring happens only after both full trajectories exist.
        targets = build_targets_family_runtime()
        cells = []
        for target in targets:
            native_recovery = max(_recovery(im, target.image) for im in native_images)
            mixed_recovery = max(_recovery(im, target.image) for im in mixed_images)
            cells.append({
                'masterSeed': seed,
                'targetId': target.id,
                'targetFamily': target.family,
                'nativeRecovery': native_recovery,
                'mixedRecovery': mixed_recovery,
                'delta': mixed_recovery - native_recovery,
            })

    hard = {
        'familyRouteClassExact': int(core.ROUTES['family']['intrinsic_dimension']) == 2,
        'sharedStartExact': same_start,
        'nativeBudgetExact': nd['totalChallengers'] == 20 and nd['nativeChallengers'] == 20 and nd['spectralChallengers'] == 0 and nd['projectedSpectralChallengers'] == 0,
        'mixedBudgetExact': md['totalChallengers'] == 20 and md['nativeChallengers'] == 10 and md['projectedSpectralChallengers'] == 10 and md['spectralChallengers'] == 0,
        'projectedAuthorityExact': md['eligibleRoutes'] == ['family'],
        'cellCountExact': len(cells) == 15,
    }
    if not all(hard.values()):
        raise AssertionError(f'authoritative hard invariant failure: {hard}')
    return {
        'version': 1,
        'experiment': 'family-projected-spectral-runtime-replay-v1',
        'masterSeed': seed,
        'smoke': False,
        'artisticEvidence': False,
        'authority': 'mechanical-family-runtime-only',
        'settings': {
            'route': ROUTE,
            'startsPerRoute': 1,
            'explorePerBasin': 4,
            'roundAPerSurvivor': 4,
            'totalExtraBudget': 12,
            'challengersPerArm': 20,
            'mixedNative': 10,
            'mixedProjectedSpectral': 10,
            'spectralBandwidth': 2,
            'spectralAmplitude': 16.0,
            'canonicalTime': CANONICAL_TIME,
            'metric': 'sparse-geometry-v1-exact-fast-grayscale',
            'selector': 'deterministic-temporal-selector-runtime-driver-only',
            'portfolioMode': search_engine.FAMILY_PROJECTED_V1,
        },
        'hardInvariants': hard,
        'sameStart': same_start,
        'nativeDiagnostics': nd,
        'mixedDiagnostics': md,
        'cells': cells,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--output')
    args = p.parse_args()
    if args.seed not in ALLOWED_SEEDS:
        raise ValueError(f'seed {args.seed} outside frozen population')
    if args.smoke != (args.seed == SMOKE_SEED):
        raise ValueError('smoke flag/seed mismatch')
    result = smoke(args.seed) if args.smoke else run_seed(args.seed)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
