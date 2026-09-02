#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_PATH = ROOT / "experiments" / "semantic-judge-prospective-v1-replacement" / "generate_review.py"

spec = importlib.util.spec_from_file_location("_late_refinement_base_generator", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load base generator: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

EXPERIMENT = "late-refinement-artistic-prospective-v1"
REVIEW_SEEDS = (758003, 758019, 758037, 758053, 758071, 758089, 758107, 758127)
SMOKE_SEED = 758999
BLIND_SALT = "late-refinement-artistic-prospective-v1-20260902"

# Preserve the validated generator and change only the preregistered fresh namespace
# and experiment identity. Pair sampling, rendering, budgets, routes, and ordering
# remain inherited from the frozen base generator.
base.REVIEW_SEEDS = REVIEW_SEEDS
base.SMOKE_SEED = SMOKE_SEED
base.BLIND_SALT = BLIND_SALT


def _brief(route: str) -> dict:
    return {
        "name": EXPERIMENT,
        "artistic_intent": "discover a strong compact mathematical form with coherent structure and meaningful temporal development",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": base.search_engine.MIXED_1D_V1,
    }


base._brief = _brief


def generate(output_root: Path, smoke: bool) -> dict:
    summary = base.generate(output_root, smoke)

    contract_path = output_root / "review" / "review-contract.json"
    contract = json.loads(contract_path.read_text())
    contract["experiment"] = EXPERIMENT
    contract.pop("allowedModelJudgments", None)
    contract.pop("predictionCanonicalization", None)
    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")

    key_path = output_root / "key" / "key.json"
    key = json.loads(key_path.read_text())
    key["experiment"] = EXPERIMENT
    key["blindSalt"] = BLIND_SALT
    key_path.write_text(json.dumps(key, indent=2, sort_keys=True) + "\n")

    summary["experiment"] = EXPERIMENT
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(Path(args.output_root), args.smoke), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
