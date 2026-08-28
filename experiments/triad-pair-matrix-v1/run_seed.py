#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from reproduce import run_seed


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,required=True)
    args=parser.parse_args()
    print(json.dumps(run_seed(args.seed),indent=2))

if __name__=='__main__':
    main()
