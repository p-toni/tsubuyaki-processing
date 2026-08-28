#!/usr/bin/env python3
"""Re-run only the corrected deferred scheduler against frozen eager signatures."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('route_balanced_reproduce',HERE/'reproduce.py')
if SPEC is None or SPEC.loader is None: raise RuntimeError('could not load reproduce.py')
mod=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(mod)

EXPECTED_EAGER={
    7:'83aeec36847752f988f436aa6d506f86f06bf6146f56cd20c02d48f716361c55',
    19:'acbe0cbc6801fa71dcce31a8544aed0ed83a042e4a08918f548828964157c4df',
    43:'a2bf05f23ee714ccb9d8801106d48cd3bfa49a529dfdf0dd166833c0daf3e099',
}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,required=True); args=ap.parse_args()
    if args.seed not in EXPECTED_EAGER: raise SystemExit(f'unfrozen seed: {args.seed}')
    brief=mod._brief()
    rows=[mod.run_policy(brief,args.seed,p) for p in ('scheduled-k2','scheduled-k3')]
    for row in rows:
        if row['trajectorySignature']!=EXPECTED_EAGER[args.seed]:
            raise AssertionError(f"trajectory divergence seed={args.seed} policy={row['policy']}")
    print(json.dumps({
        'version':2,
        'seed':args.seed,
        'purpose':'corrected deferred scheduling calibration only; synthetic oracle is not artistic evidence',
        'expectedEagerTrajectorySignature':EXPECTED_EAGER[args.seed],
        'policies':rows,
    },indent=2))


if __name__=='__main__': main()
