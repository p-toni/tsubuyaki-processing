#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

SEEDS = (732100011,732100027,732100039,732100057,732100081,732100103,732100119,732100143,732100157,732100181,732100207,732100229)
PROMPTS = ('diamond','spiral','lightning','leaf','umbrella','crown','letter-s','sailboat')
WEAK = ('spiral','umbrella','crown','letter-s')


def load_blocks(root: Path) -> list[dict]:
    blocks = []
    for seed in SEEDS:
        matches = list(root.rglob(f'archive-{seed}.json'))
        if len(matches) != 1:
            raise AssertionError(f'expected one archive for {seed}, found {len(matches)}')
        d = json.loads(matches[0].read_text())
        if int(d['masterSeed']) != seed:
            raise AssertionError('seed mismatch')
        if not all(d['hardInvariants'].values()):
            raise AssertionError(f'hard invariant failure for {seed}: {d["hardInvariants"]}')
        blocks.append(d)
    return blocks


def aggregate(blocks: list[dict]) -> dict:
    if len(blocks) != len(SEEDS):
        raise AssertionError('incomplete seed rectangle')
    pooled_attempts = sum(int(b['totalAttempts']) for b in blocks)
    pooled_valid = sum(int(b['totalValid']) for b in blocks)
    route_attempts = {r: 0 for r in ('recurrence','orbit','filament')}
    route_valid = {r: 0 for r in route_attempts}
    for b in blocks:
        for r in route_attempts:
            route_attempts[r] += int(b['routes'][r]['attempted'])
            route_valid[r] += int(b['routes'][r]['valid'])

    concept = {}
    found_cells = 0
    total_positive_mass = 0.0
    for p in PROMPTS:
        records = [b['concepts'][p] for b in blocks]
        found = sum(bool(r['top1Found']) for r in records)
        found_cells += found
        mean_top1_f1 = sum(float(r['bestTop1TargetF1']) for r in records) / len(records)
        mean_any_f1 = sum(float(r['bestAnyTargetF1']) for r in records) / len(records)
        positive_mass = sum(float(r['bestTop1TargetF1']) for r in records)
        total_positive_mass += positive_mass
        concept[p] = {
            'top1FoundCount': found,
            'top1FoundFraction': found / len(records),
            'meanBestTop1TargetF1': mean_top1_f1,
            'meanBestAnyTargetF1': mean_any_f1,
            'positiveTop1F1Mass': positive_mass,
        }

    all_cell_f1 = [float(b['concepts'][p]['bestTop1TargetF1']) for b in blocks for p in PROMPTS]
    overall_found = found_cells / (len(blocks) * len(PROMPTS))
    mean_best_top1_f1 = sum(all_cell_f1) / len(all_cell_f1)
    max_share = 0.0
    if total_positive_mass > 0:
        max_share = max(v['positiveTop1F1Mass'] / total_positive_mass for v in concept.values())
    for v in concept.values():
        v['positiveTop1F1ContributionShare'] = v['positiveTop1F1Mass'] / total_positive_mass if total_positive_mass > 0 else 0.0

    pooled_valid_fraction = pooled_valid / pooled_attempts
    route_valid_fraction = {r: route_valid[r] / route_attempts[r] for r in route_attempts}
    gates = {
        'completeSeedRectangle': len(blocks) == 12,
        'exactAttemptBudgets': all(int(b['totalAttempts']) == 1536 and b['attempted'] == {'native':768,'spectral':768} for b in blocks),
        'pooledValidityAtLeastPoint90': pooled_valid_fraction >= 0.90,
        'everyRouteValidityAtLeastPoint85': all(v >= 0.85 for v in route_valid_fraction.values()),
        'top1FoundAtLeast80PctCells': overall_found >= 0.80,
        'everyConceptFoundAtLeast50Pct': all(v['top1FoundFraction'] >= 0.50 for v in concept.values()),
        'weakConceptsFoundAtLeast50Pct': all(concept[p]['top1FoundFraction'] >= 0.50 for p in WEAK),
        'meanBestTop1F1AtLeastPoint45': mean_best_top1_f1 >= 0.45,
        'noConceptDominatesTop1F1Mass': max_share <= 0.35,
    }
    decision = 'ACCESSIBLE_SEMANTIC_CAPACITY_PRESENT' if all(gates.values()) else 'ACCESSIBLE_SEMANTIC_CAPACITY_LIMITED'
    return {
        'decision': decision,
        'seedCount': len(SEEDS),
        'seeds': list(SEEDS),
        'conceptCount': len(PROMPTS),
        'prompts': list(PROMPTS),
        'weakConcepts': list(WEAK),
        'overall': {
            'totalAttempts': pooled_attempts,
            'totalValid': pooled_valid,
            'pooledValidFraction': pooled_valid_fraction,
            'routeValidFraction': route_valid_fraction,
            'top1FoundFraction': overall_found,
            'meanBestTop1TargetF1': mean_best_top1_f1,
            'maxTop1F1ContributionShare': max_share,
        },
        'conceptMeans': concept,
        'gates': gates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = aggregate(load_blocks(args.input_root))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
