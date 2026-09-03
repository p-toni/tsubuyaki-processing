#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

MASTER_SEEDS = (
    764003, 764019, 764037, 764053, 764071,
    764089, 764107, 764127, 764149, 764167,
    764181, 764199, 764223, 764239, 764257,
    764277, 764293, 764311, 764331, 764349,
)
FAMILIES = (
    'disconnected-loops',
    'nested-loops',
    'concave-loops',
    'open-networks',
    'dense-regions',
)
BOOTSTRAP_DRAWS = 50000
BOOTSTRAP_SEED = 764555001
MEANINGFUL_BAR = 0.005
EPS = 1e-12
LAW_FAILURE = 'shared family law loses sibling-scale coherence'


def _mean(xs):
    return statistics.fmean(xs) if xs else 0.0


def _bootstrap_lower(values: list[float], rng: random.Random) -> float:
    n = len(values)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        draws.append(_mean([values[rng.randrange(n)] for _ in range(n)]))
    draws.sort()
    return draws[int(0.05 * (len(draws) - 1))]


def aggregate(input_dir: Path) -> dict:
    records = [json.loads(p.read_text()) for p in sorted(input_dir.glob('seed-*.json'))]
    seeds = sorted(int(r['masterSeed']) for r in records)
    if seeds != sorted(MASTER_SEEDS):
        raise AssertionError(f'incomplete or unexpected authoritative seed set: {seeds}')
    if not all(r['smoke'] is False and all(r['hardInvariants'].values()) for r in records):
        raise AssertionError('authoritative record failed hard invariant')

    all_cells = []
    signature = None
    seed_deltas = defaultdict(list)
    family_deltas = defaultdict(list)
    native_attempts = native_valid = 0
    mixed_attempts = mixed_valid = 0
    projected_attempts = projected_valid = 0
    projected_law_failures = 0

    for record in records:
        cells = record['cells']
        if len(cells) != 15:
            raise AssertionError(f"seed {record['masterSeed']} cell-count drift")
        sig = tuple(sorted((c['targetId'], c['targetFamily']) for c in cells))
        if len(sig) != len(set(sig)):
            raise AssertionError('duplicate target cell')
        if signature is None:
            signature = sig
        elif sig != signature:
            raise AssertionError('target rectangle drift')
        all_cells.extend(cells)
        for c in cells:
            d = float(c['delta'])
            seed_deltas[int(record['masterSeed'])].append(d)
            family_deltas[c['targetFamily']].append(d)

        nd = record['nativeDiagnostics']
        md = record['mixedDiagnostics']
        native_attempts += int(nd['nativeChallengers'])
        native_valid += int(nd['nativeValid'])
        mixed_attempts += int(md['nativeChallengers']) + int(md['projectedSpectralChallengers'])
        mixed_valid += int(md['nativeValid']) + int(md['projectedSpectralValid'])
        projected_attempts += int(md['projectedSpectralChallengers'])
        projected_valid += int(md['projectedSpectralValid'])
        projected_law_failures += int(md['projectedSiblingScaleLawFailures'])

    if len(all_cells) != 300:
        raise AssertionError(f'aggregate rectangle drift: {len(all_cells)}')
    if set(family_deltas) != set(FAMILIES):
        raise AssertionError(f'target-family drift: {sorted(family_deltas)}')

    seed_means = {str(s): _mean(seed_deltas[s]) for s in MASTER_SEEDS}
    seed_values = [seed_means[str(s)] for s in MASTER_SEEDS]
    rng = random.Random(BOOTSTRAP_SEED)
    delta_mean = _mean(seed_values)
    delta_lower = _bootstrap_lower(seed_values, rng)
    family_means = {f: _mean(family_deltas[f]) for f in FAMILIES}
    leave_one_out = {
        f: _mean([
            float(c['delta']) for c in all_cells
            if c['targetFamily'] != f
        ])
        for f in FAMILIES
    }

    deltas = [float(c['delta']) for c in all_cells]
    wins = sum(d > MEANINGFUL_BAR for d in deltas)
    losses = sum(d < -MEANINGFUL_BAR for d in deltas)

    positive_by_family = {
        f: sum(
            max(0.0, float(c['delta'])) for c in all_cells
            if c['targetFamily'] == f
        )
        for f in FAMILIES
    }
    total_positive = sum(positive_by_family.values())
    shares = {
        f: (v / total_positive if total_positive > EPS else 0.0)
        for f, v in positive_by_family.items()
    }
    max_share = max(shares.values(), default=1.0)

    native_rate = native_valid / native_attempts
    mixed_rate = mixed_valid / mixed_attempts
    projected_rate = projected_valid / projected_attempts

    gates = {
        'completeHardInvariantRectangle': True,
        'exactTwentyVsTwentyBudgets': native_attempts == 400 and mixed_attempts == 400,
        'exactProjectedAllocation': projected_attempts == 200,
        'allSharedStartsExact': all(bool(r['sameStart']) for r in records),
        'meanDeltaAtLeast005': delta_mean >= MEANINGFUL_BAR,
        'masterSeedBootstrapLower95Positive': delta_lower > 0.0,
        'everyTargetFamilyMeanPositive': all(v > 0.0 for v in family_means.values()),
        'everyLeaveOneTargetFamilyOutMeanPositive': all(v > 0.0 for v in leave_one_out.values()),
        'meaningfulWinsExceedLosses': wins > losses,
        'projectedSpectralValidityAtLeast95Pct': projected_rate >= 0.95,
        'projectedSiblingScaleLawFailuresZero': projected_law_failures == 0,
        'mixedValidityWithin5ppOfBaseline': mixed_rate >= native_rate - 0.05,
        'positiveAdvantageNotFamilyConcentrated': total_positive > EPS and max_share <= 0.50,
    }
    decision = (
        'FAMILY_PROJECTED_SPECTRAL_RUNTIME_PROMISING'
        if all(gates.values())
        else 'FAMILY_PROJECTED_SPECTRAL_RUNTIME_NOT_PROMISING'
    )

    return {
        'version': 1,
        'experiment': 'family-projected-spectral-runtime-replay-v1',
        'artisticEvidence': False,
        'authority': 'mechanical-family-runtime-only',
        'seedCount': len(records),
        'cellCount': len(all_cells),
        'bootstrap': {
            'draws': BOOTSTRAP_DRAWS,
            'seed': BOOTSTRAP_SEED,
            'unit': 'master-seed mean across 15 target cells',
        },
        'meaningfulRecoveryBar': MEANINGFUL_BAR,
        'deltaMean': delta_mean,
        'deltaOneSided95BootstrapLower': delta_lower,
        'masterSeedDelta': seed_means,
        'targetFamilyDeltaMeans': family_means,
        'leaveOneTargetFamilyOutDeltaMeans': leave_one_out,
        'meaningfulWins': wins,
        'meaningfulLosses': losses,
        'validity': {
            'nativeAttempts': native_attempts,
            'nativeValid': native_valid,
            'nativeRate': native_rate,
            'mixedAttempts': mixed_attempts,
            'mixedValid': mixed_valid,
            'mixedRate': mixed_rate,
            'projectedSpectralAttempts': projected_attempts,
            'projectedSpectralValid': projected_valid,
            'projectedSpectralRate': projected_rate,
            'projectedSiblingScaleLawFailures': projected_law_failures,
        },
        'positiveAdvantageConcentration': {
            'byFamily': positive_by_family,
            'shareByFamily': shares,
            'maxFamilyShare': max_share,
        },
        'gates': gates,
        'decision': decision,
        'interpretation': (
            'Fresh adaptive-runtime replay of native-only versus the family-only '
            '50/50 projected-spectral portfolio. A positive decision mechanically '
            'validates the opt-in family runtime mode but grants no artistic authority.'
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    result = aggregate(Path(args.input_dir))
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
