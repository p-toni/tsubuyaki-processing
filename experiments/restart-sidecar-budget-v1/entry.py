#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "run_budget.py"
spec = importlib.util.spec_from_file_location("_restart_sidecar_budget_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load runner: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

# Pure memoization only: preserve exact rendering and metric functions while
# avoiding repeated work across the nested 1/2/4/8 archives.
_image_cache = {}
_recovery_cache = {}


def _cached_images(cands):
    out = []
    for cand in cands:
        key = id(cand)
        if key not in _image_cache:
            _image_cache[key] = base.core.render_candidate_frame(cand, base.CANONICAL_TIME)
        out.append(_image_cache[key])
    return out


def _cached_recovery(image, target_image):
    key = (id(image), id(target_image))
    if key not in _recovery_cache:
        _recovery_cache[key] = base.shortlist._recovery(image, target_image)
    return _recovery_cache[key]


base._images = _cached_images
base._recovery = _cached_recovery


# The production sidecar's persisted phenotypeHash intentionally includes the
# route name. The experiment's target-blind dispersion hash intentionally does
# not. Replay must compare production hash to production hash, not cross the two
# conventions.
def _production_replay_check(brief, master_seed, route, expected, root):
    out = root / f"production-{route}"
    base.restart_sidecar.generate_restart_sidecar(
        brief, master_seed, out, attempts_per_route=4
    )
    records = json.loads((out / "candidates.json").read_text())
    got = [r["phenotypeHash"] for r in records]
    want = [base.restart_sidecar._phenotype_hash(c) for c in expected[:4]]
    return got == want


base._production_replay_check = _production_replay_check


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--output")
    args = p.parse_args()
    result = base.run_seed(args.seed, smoke=args.smoke)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
