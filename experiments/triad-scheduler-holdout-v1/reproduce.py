#!/usr/bin/env python3
"""Fresh-seed holdout for the merged opt-in screened triad scheduler.

Seeds are predeclared in README/workflow as the first nine primes above 43.
Synthetic outcomes remain scheduling/convergence evidence only.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE_PATH=ROOT/'experiments'/'screened-triad-runtime-replay-v1'/'reproduce.py'
spec=importlib.util.spec_from_file_location('screened_runtime_replay_v1',BASE_PATH)
base=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

HOLDOUT_SEEDS=(47,53,59,61,67,71,73,79,83)


def run_seed(seed:int)->dict:
    if seed not in HOLDOUT_SEEDS:
        raise ValueError(f'seed {seed} is not in the predeclared holdout')
    pair=base._run_policy(seed,triads=False)
    triad=base._run_policy(seed,triads=True)

    if pair['trajectorySignature']!=triad['trajectorySignature']:
        raise AssertionError(f'full search trajectory diverged at holdout seed {seed}')
    if pair['winner']!=triad['winner']:
        raise AssertionError(f'winner diverged at holdout seed {seed}')
    for metric in ('reviewTasks','reviewRounds','searchReplays','candidateExposures'):
        if triad[metric]>pair[metric]:
            raise AssertionError(
                f'triad scheduler regressed {metric} at seed {seed}: '
                f"{triad[metric]} > {pair[metric]}"
            )

    return {
        'version':1,
        'seed':seed,
        'trajectorySignature':pair['trajectorySignature'],
        'winner':pair['winner'],
        'currentPairK2':{
            key:pair[key] for key in (
                'reviewTasks','reviewRounds','searchReplays','candidateExposures',
                'pairRelationsElicited','pairTasks','triadTasks',
            )
        },
        'matrixTriadK2':{
            key:triad[key] for key in (
                'reviewTasks','reviewRounds','searchReplays','candidateExposures',
                'pairRelationsElicited','pairTasks','triadTasks',
            )
        },
        'gates':{
            'sameFullTrajectory':True,
            'sameWinner':True,
            'noTaskRegression':triad['reviewTasks']<=pair['reviewTasks'],
            'noRoundRegression':triad['reviewRounds']<=pair['reviewRounds'],
            'noReplayRegression':triad['searchReplays']<=pair['searchReplays'],
            'noExposureRegression':triad['candidateExposures']<=pair['candidateExposures'],
        },
    }


def main():
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--seed',type=int,required=True); args=parser.parse_args()
    print(json.dumps(run_seed(args.seed),indent=2))


if __name__=='__main__': main()
