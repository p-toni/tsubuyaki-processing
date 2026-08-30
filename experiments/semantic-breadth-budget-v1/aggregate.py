#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

PROMPTS = ('diamond', 'spiral', 'lightning', 'leaf', 'umbrella', 'crown', 'letter-s', 'sailboat')
BUDGETS = (60, 120, 240, 480)
CANDIDATE_BUDGETS = (120, 240, 480)
SEEDS = (
    732500011, 732500029, 732500041, 732500067, 732500079,
    732500101, 732500113, 732500137, 732500151, 732500173,
    732500197, 732500211, 732500233, 732500257, 732500271,
    732500293, 732500317, 732500341, 732500363, 732500389,
)
TCRIT_95_ONE_SIDED_DF19 = 1.7291328115213682


def _load_archives(root: Path) -> list[dict]:
    out = []
    for path in sorted(root.rglob('*.json')):
        try:
            d = json.loads(path.read_text())
        except Exception:
            continue
        if isinstance(d, dict) and 'masterSeed' in d and 'budgets' in d and 'archiveSignature' in d:
            out.append(d)
    return out


def _mean(xs):
    return statistics.fmean(xs) if xs else float('nan')


def _budget_summary(archives: list[dict], budget: int) -> dict:
    key = str(budget)
    cells = []
    for a in archives:
        for prompt in PROMPTS:
            cells.append((int(a['masterSeed']), prompt, a['budgets'][key]['concepts'][prompt]))

    top1 = _mean([1.0 if c['heldoutTop1'] else 0.0 for _, _, c in cells])
    mean_f1 = _mean([float(c['heldoutTargetF1']) for _, _, c in cells])
    concept = {}
    for prompt in PROMPTS:
        pcells = [c for _, p, c in cells if p == prompt]
        concept[prompt] = {
            'heldoutTop1Fraction': _mean([1.0 if c['heldoutTop1'] else 0.0 for c in pcells]),
            'meanHeldoutTargetF1': _mean([float(c['heldoutTargetF1']) for c in pcells]),
        }

    total_attempts = 0
    total_valid = 0
    route_attempts = {r: 0 for r in ('recurrence','orbit','filament')}
    route_valid = {r: 0 for r in ('recurrence','orbit','filament')}
    for a in archives:
        contract = a['budgets'][key]['contract']
        total_attempts += int(contract['totalAttempts'])
        total_valid += int(contract['totalValid'])
        for route in route_attempts:
            route_attempts[route] += int(contract['routes'][route]['attempted'])
            route_valid[route] += int(contract['routes'][route]['valid'])

    return {
        'heldoutTop1Fraction': top1,
        'meanHeldoutTargetF1': mean_f1,
        'pooledValidFraction': total_valid / total_attempts if total_attempts else 0.0,
        'routeValidFraction': {
            r: route_valid[r] / route_attempts[r] if route_attempts[r] else 0.0
            for r in route_attempts
        },
        'concepts': concept,
    }


def _comparison(archives: list[dict], budget: int, baseline: int = 60) -> dict:
    bk = str(baseline); ck = str(budget)
    deltas = []
    top1_base = []
    top1_candidate = []
    by_seed = {s: [] for s in SEEDS}
    by_concept = {p: [] for p in PROMPTS}
    positive_mass = {p: 0.0 for p in PROMPTS}

    for a in archives:
        seed = int(a['masterSeed'])
        for prompt in PROMPTS:
            b = a['budgets'][bk]['concepts'][prompt]
            c = a['budgets'][ck]['concepts'][prompt]
            delta = float(c['heldoutTargetF1']) - float(b['heldoutTargetF1'])
            deltas.append(delta)
            by_seed[seed].append(delta)
            by_concept[prompt].append(delta)
            positive_mass[prompt] += max(0.0, delta)
            top1_base.append(1.0 if b['heldoutTop1'] else 0.0)
            top1_candidate.append(1.0 if c['heldoutTop1'] else 0.0)

    seed_means = [_mean(by_seed[s]) for s in SEEDS]
    sd = statistics.stdev(seed_means) if len(seed_means) > 1 else 0.0
    lb = _mean(seed_means) - TCRIT_95_ONE_SIDED_DF19 * sd / math.sqrt(len(seed_means))
    base_top1 = _mean(top1_base)
    candidate_top1 = _mean(top1_candidate)
    total_positive = sum(positive_mass.values())
    shares = {p: positive_mass[p] / total_positive if total_positive > 0 else 0.0 for p in PROMPTS}
    loo = {
        omitted: _mean([d for p in PROMPTS if p != omitted for d in by_concept[p]])
        for omitted in PROMPTS
    }
    return {
        'meanDeltaHeldoutTargetF1': _mean(deltas),
        'seedMeanDeltaStdDev': sd,
        'seedMeanDeltaOneSided95LowerBound': lb,
        'baselineHeldoutTop1Fraction': base_top1,
        'candidateHeldoutTop1Fraction': candidate_top1,
        'top1FractionDelta': candidate_top1 - base_top1,
        'conceptMeanDeltaHeldoutTargetF1': {p: _mean(by_concept[p]) for p in PROMPTS},
        'leaveOneConceptOutMeanDelta': loo,
        'positiveDeltaContributionShare': shares,
        'maxPositiveDeltaContributionShare': max(shares.values()) if shares else 0.0,
        'seedMeanDelta': {str(s): _mean(by_seed[s]) for s in SEEDS},
    }


def aggregate(archives: list[dict]) -> dict:
    observed = [int(a['masterSeed']) for a in archives]
    complete = len(archives) == len(SEEDS) and sorted(observed) == sorted(SEEDS) and len(set(observed)) == len(observed)
    hard_all = complete and all(all(bool(v) for v in a['hardInvariants'].values()) for a in archives)

    exact_contracts = hard_all
    expected_per_route = {60:20, 120:40, 240:80, 480:160}
    for a in archives:
        for budget in BUDGETS:
            c = a['budgets'][str(budget)]['contract']
            if int(c['totalAttempts']) != budget:
                exact_contracts = False
            if int(c['nativeAttempted']) != budget // 2 or int(c['spectralAttempted']) != budget // 2:
                exact_contracts = False
            for route in ('recurrence','orbit','filament'):
                rc = c['routes'][route]
                pr = expected_per_route[budget]
                if int(rc['attempted']) != pr:
                    exact_contracts = False
                if int(rc['nativeAttempted']) != pr // 2 or int(rc['spectralAttempted']) != pr // 2:
                    exact_contracts = False

    summaries = {str(b): _budget_summary(archives, b) for b in BUDGETS}
    comparisons = {str(b): _comparison(archives, b, 60) for b in CANDIDATE_BUDGETS}

    gates = {}
    sufficient = []
    for budget in CANDIDATE_BUDGETS:
        s = summaries[str(budget)]
        c = comparisons[str(budget)]
        g = {
            'completeRectangle': complete,
            'hardInvariants': hard_all,
            'exactNestedBudgets': exact_contracts,
            'targetBlindReplayDeterministic': hard_all,
            'pooledValidityAtLeastPoint90': s['pooledValidFraction'] >= 0.90,
            'everyRouteValidityAtLeastPoint85': all(v >= 0.85 for v in s['routeValidFraction'].values()),
            'heldoutTop1AtLeastPoint75': s['heldoutTop1Fraction'] >= 0.75,
            'everyConceptTop1AtLeastPoint50': all(v['heldoutTop1Fraction'] >= 0.50 for v in s['concepts'].values()),
            'meanHeldoutTargetF1AtLeastPoint60': s['meanHeldoutTargetF1'] >= 0.60,
            'meanF1ImprovementVs60AtLeastPoint03': c['meanDeltaHeldoutTargetF1'] >= 0.03,
            'seedMeanDeltaOneSided95LowerBoundPositive': c['seedMeanDeltaOneSided95LowerBound'] > 0.0,
            'top1ImprovementVs60AtLeastPoint15': c['top1FractionDelta'] >= 0.15,
            'everyLeaveOneConceptOutMeanDeltaPositive': all(v > 0.0 for v in c['leaveOneConceptOutMeanDelta'].values()),
            'noConceptDominatesPositiveDelta': c['maxPositiveDeltaContributionShare'] <= 0.30,
        }
        gates[str(budget)] = g
        if all(g.values()):
            sufficient.append(budget)

    if sufficient:
        smallest = min(sufficient)
        decision = f'SEMANTIC_BREADTH_BUDGET_{smallest}_SUFFICIENT'
    else:
        smallest = None
        decision = 'SEMANTIC_BREADTH_BUDGET_NOT_SUFFICIENT'

    return {
        'decision': decision,
        'smallestSufficientBudget': smallest,
        'seedCount': len(SEEDS),
        'conceptCount': len(PROMPTS),
        'archiveCount': len(archives),
        'budgets': summaries,
        'comparisonsVs60': comparisons,
        'gates': gates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    archives = _load_archives(args.input_root)
    result = aggregate(archives)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
