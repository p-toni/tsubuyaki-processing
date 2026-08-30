#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

MASTER_SEEDS = (
    124003, 124009, 124021, 124037,
    124051, 124067, 124087, 124097,
    124121, 124123, 124133, 124139,
    124147, 124153, 124171, 124181,
)
ROUTES = ('recurrence', 'orbit', 'filament')
FAMILIES = ('disconnected-loops', 'nested-loops', 'concave-loops', 'open-networks', 'dense-regions')
CELLS_PER_SEED = 45
MEAN_MARGIN = 0.003
MEANINGFUL_MARGIN = 0.005
T95_DF15_ONE_SIDED = 1.7530503556925547
EPS = 1e-12


def _load(paths):
    out = []
    for p in paths:
        d = json.loads(p.read_text())
        if isinstance(d, dict) and 'masterSeed' in d:
            out.append(d)
    return out


def _summary(values):
    return {
        'n': len(values),
        'mean': statistics.fmean(values) if values else None,
        'median': statistics.median(values) if values else None,
        'sd': statistics.stdev(values) if len(values) > 1 else 0.0,
        'min': min(values) if values else None,
        'max': max(values) if values else None,
    }


def _lower95(values):
    if len(values) != len(MASTER_SEEDS):
        raise AssertionError('seed mean count drift')
    return statistics.fmean(values) - T95_DF15_ONE_SIDED * statistics.stdev(values) / math.sqrt(len(values))


def aggregate(blocks):
    seeds = [int(b['masterSeed']) for b in blocks]
    if len(seeds) != len(set(seeds)):
        raise AssertionError('duplicate master seed')
    if tuple(sorted(seeds)) != tuple(sorted(MASTER_SEEDS)):
        raise AssertionError(f'consumed seed set mismatch: {sorted(seeds)}')
    settings = blocks[0]['settings']
    if any(b['settings'] != settings for b in blocks[1:]):
        raise AssertionError('settings drift')
    if settings['routes'] != list(ROUTES) or settings['challengersPerRouteArm'] != 20 or settings['mixedNativePerRoute'] != 10 or settings['mixedSpectralPerRoute'] != 10:
        raise AssertionError('runtime budget/settings drift')
    if settings['spectralBandwidth'] != 2 or float(settings['spectralAmplitude']) != 16.0:
        raise AssertionError('spectral operator drift')

    cells = []
    signature = None
    for block in blocks:
        if not all(block.get('hardInvariants', {}).values()):
            raise AssertionError(f"hard invariant failure in seed {block['masterSeed']}")
        if len(block['cells']) != CELLS_PER_SEED:
            raise AssertionError('cell count drift')
        sig = tuple(sorted((c['route'], c['targetId'], c['targetFamily']) for c in block['cells']))
        if len(sig) != len(set(sig)):
            raise AssertionError('duplicate route/target cell')
        if signature is None: signature = sig
        elif sig != signature: raise AssertionError('target rectangle drift')
        cells.extend(block['cells'])
    if len(cells) != len(MASTER_SEEDS) * CELLS_PER_SEED:
        raise AssertionError('aggregate rectangle incomplete')
    if Counter(c['targetFamily'] for c in blocks[0]['cells']) != Counter({f: 9 for f in FAMILIES}):
        raise AssertionError('target family rectangle drift')

    deltas = [float(c['delta']) for c in cells]
    native_recovery = [float(c['nativeRecovery']) for c in cells]
    mixed_recovery = [float(c['mixedRecovery']) for c in cells]
    by_seed = defaultdict(list); by_route = defaultdict(list); by_route_seed = defaultdict(list); by_family = defaultdict(list)
    for c in cells:
        d = float(c['delta']); seed = int(c['masterSeed']); route = c['route']
        by_seed[seed].append(d); by_route[route].append(d); by_route_seed[(route, seed)].append(d); by_family[c['targetFamily']].append(d)
    seed_means = {str(s): statistics.fmean(by_seed[s]) for s in MASTER_SEEDS}
    seed_values = [seed_means[str(s)] for s in MASTER_SEEDS]
    route_means = {r: statistics.fmean(by_route[r]) for r in ROUTES}
    route_seed_stats = {}
    for route in ROUTES:
        per_seed = {str(s): statistics.fmean(by_route_seed[(route, s)]) for s in MASTER_SEEDS}
        values = [per_seed[str(s)] for s in MASTER_SEEDS]
        route_seed_stats[route] = {**_summary(values), 'oneSided95Lower': _lower95(values), 'perSeed': per_seed}
    family_means = {f: statistics.fmean(by_family[f]) for f in FAMILIES}
    loo_family = {f: statistics.fmean(float(c['delta']) for c in cells if c['targetFamily'] != f) for f in FAMILIES}
    win_fraction = sum(d > MEANINGFUL_MARGIN for d in deltas) / len(deltas)
    loss_fraction = sum(d < -MEANINGFUL_MARGIN for d in deltas) / len(deltas)

    spectral_valid = spectral_attempts = 0
    spectral_by_route = {r: [0, 0] for r in ROUTES}
    for block in blocks:
        for route in ROUTES:
            diag = block['routeDiagnostics'][route]['mixed']
            if diag['totalChallengers'] != 20 or diag['nativeChallengers'] != 10 or diag['spectralChallengers'] != 10:
                raise AssertionError('mixed runtime allocation drift')
            sv = int(diag['spectralValid']); sa = int(diag['spectralChallengers'])
            spectral_valid += sv; spectral_attempts += sa
            spectral_by_route[route][0] += sv; spectral_by_route[route][1] += sa
    spectral_pooled = spectral_valid / spectral_attempts
    spectral_route_valid = {r: v / a for r, (v, a) in spectral_by_route.items()}

    positive_by_family = {f: sum(max(0.0, float(c['delta'])) for c in cells if c['targetFamily'] == f) for f in FAMILIES}
    total_positive = sum(positive_by_family.values())
    shares = {f: (v / total_positive if total_positive > EPS else 0.0) for f, v in positive_by_family.items()}
    max_share = max(shares.values(), default=1.0)

    gates = {
        'completeHardInvariantRectangle': True,
        'exactRuntimeBudgetEveryRouteSeed': True,
        'exactMixed10Native10SpectralEveryRouteSeed': True,
        'meanDeltaAtLeast003': statistics.fmean(seed_values) >= MEAN_MARGIN,
        'globalMasterSeedLower95Positive': _lower95(seed_values) > 0.0,
        'allThreeRouteMeansPositive': all(route_means[r] > 0.0 for r in ROUTES),
        'allThreeRouteSeedLower95Positive': all(route_seed_stats[r]['oneSided95Lower'] > 0.0 for r in ROUTES),
        'allLeaveOneFamilyOutPositive': all(loo_family[f] > 0.0 for f in FAMILIES),
        'meaningfulWinsExceedLosses': win_fraction > loss_fraction,
        'spectralValidityRetained': spectral_pooled >= 0.95 and min(spectral_route_valid.values()) >= 0.90,
        'positiveAdvantageNotFamilyConcentrated': total_positive > EPS and max_share <= 0.50,
    }
    decision = 'SPECTRAL_MATERIAL_CONTROL_RUNTIME_PROMISING' if all(gates.values()) else 'SPECTRAL_MATERIAL_CONTROL_RUNTIME_NOT_PROMISING'
    return {
        'version': 1,
        'decision': decision,
        'population': {'masterSeeds': list(MASTER_SEEDS), 'routes': list(ROUTES), 'targetFamilies': list(FAMILIES), 'cells': len(cells), 'settings': settings},
        'gates': gates,
        'delta': _summary(deltas),
        'masterSeedDelta': {**_summary(seed_values), 'oneSided95Lower': _lower95(seed_values), 'tCritical': T95_DF15_ONE_SIDED, 'perSeed': seed_means},
        'routeMeanDelta': route_means,
        'routeMasterSeedDelta': route_seed_stats,
        'familyMeanDelta': family_means,
        'leaveOneFamilyOutMeanDelta': loo_family,
        'meaningful': {'margin': MEANINGFUL_MARGIN, 'winFraction': win_fraction, 'lossFraction': loss_fraction},
        'recovery': {'native': _summary(native_recovery), 'mixed': _summary(mixed_recovery)},
        'validity': {'spectralPooled': spectral_pooled, 'spectralByRoute': spectral_route_valid},
        'positiveAdvantageConcentration': {'byFamily': positive_by_family, 'shareByFamily': shares, 'maxFamilyShare': max_share},
    }


def main():
    p = argparse.ArgumentParser(); p.add_argument('--input-root', required=True); p.add_argument('--output')
    args = p.parse_args()
    result = aggregate(_load(sorted(Path(args.input_root).rglob('*.json'))))
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output: Path(args.output).write_text(text)
    else: print(text, end='')


if __name__ == '__main__': main()
