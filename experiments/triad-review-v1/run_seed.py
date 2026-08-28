#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from reproduce import run_seed

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,required=True); args=ap.parse_args()
    print(json.dumps(run_seed(args.seed),indent=2))

if __name__=='__main__': main()
