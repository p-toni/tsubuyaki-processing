#!/usr/bin/env python3
"""Run one frozen seed of the route-balanced review calibration."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("route_balanced_reproduce", HERE / "reproduce.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load reproduce.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()
    brief = mod._brief()
    policies = ("global-k2", "group-k2", "scheduled-k2", "scheduled-k3", "eager")
    rows = [mod.run_policy(brief, args.seed, p) for p in policies]
    eager = next(r for r in rows if r["policy"] == "eager")
    for row in rows:
        if row["trajectorySignature"] != eager["trajectorySignature"]:
            raise AssertionError(f"trajectory divergence seed={args.seed} policy={row['policy']}")
    print(json.dumps({
        "version": 1,
        "seed": args.seed,
        "purpose": "review-scheduling calibration only; synthetic oracle is not artistic evidence",
        "policies": rows,
    }, indent=2))


if __name__ == "__main__":
    main()
