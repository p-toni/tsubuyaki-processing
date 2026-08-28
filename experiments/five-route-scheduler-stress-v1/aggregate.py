#!/usr/bin/env python3
"""Aggregate independently executed pair/triad five-route stress artifacts."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPRO_PATH = HERE / "reproduce.py"
spec = importlib.util.spec_from_file_location("five_route_stress_reproduce", REPRO_PATH)
repro = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(repro)


def _load_policy_docs(results_dir: Path) -> dict[tuple[str, int, str], dict]:
    docs: dict[tuple[str, int, str], dict] = {}
    for path in sorted(results_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(doc, dict) or doc.get("policyKey") not in {"pair", "triad"}:
            continue
        key = (str(doc.get("brief")), int(doc.get("seed")), str(doc["policyKey"]))
        if key in docs:
            raise AssertionError(f"duplicate policy artifact for {key}: {path}")
        docs[key] = doc
    return docs


def aggregate(results_dir: Path) -> dict:
    docs = _load_policy_docs(results_dir)
    scenarios = []
    strict_savings = 0
    metric_pairs = {metric: [] for metric in ("reviewTasks", "reviewRounds", "searchReplays", "candidateExposures")}

    for brief in repro.BRIEFS:
        for seed in repro.SEEDS:
            pair_key = (brief, seed, "pair")
            triad_key = (brief, seed, "triad")
            if pair_key not in docs or triad_key not in docs:
                raise AssertionError(f"missing split artifacts for brief={brief} seed={seed}")
            pair = docs[pair_key]["result"]
            triad = docs[triad_key]["result"]
            scenario = repro.compare_policy_results(brief, seed, pair, triad)
            scenarios.append(scenario)
            strict_savings += int(scenario["gates"]["strictTaskSaving"])
            for metric in metric_pairs:
                metric_pairs[metric].append((pair[metric], triad[metric]))

    if strict_savings < 4:
        raise AssertionError(f"aggregate gate failed: strict task savings in {strict_savings}/6 scenarios; require >=4")

    summary = {}
    for metric, values in metric_pairs.items():
        pair_mean = sum(a for a, _ in values) / len(values)
        triad_mean = sum(b for _, b in values) / len(values)
        if triad_mean > pair_mean:
            raise AssertionError(f"aggregate gate failed: triad mean {metric} {triad_mean} > pair {pair_mean}")
        summary[metric] = {
            "pairMean": pair_mean,
            "triadMean": triad_mean,
            "relativeChangePct": ((triad_mean - pair_mean) / pair_mean * 100.0) if pair_mean else 0.0,
        }

    return {
        "version": 1,
        "allPassed": True,
        "strictTaskSavings": strict_savings,
        "summary": summary,
        "scenarios": scenarios,
        "decision": (
            "five-route scheduler-semantic stress passed; freeze scheduler-semantic research; "
            "pair-matrix triads remain opt-in because human artistic-judgment fidelity is untested"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
