#!/usr/bin/env python3
"""Calibrate bounded phenotype review on the real adaptive search graph.

This is a search-policy experiment, not an artistic-quality experiment. A stable
synthetic pairwise oracle is written into temporary v3 review bundles using an
otherwise-authoritative source class so the production EvidenceAuthoritySelector
can be exercised end to end. No synthetic evidence is persisted as research
preference evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
sys.path.insert(0, str(PROTO))

from core import TIMES, default_brief
from evidence_selector import EvidenceAuthoritySelector
from search_engine import run_search

ORACLE_ID = "synthetic-dynamic-oracle-v1"
CAPS = (1, 2, 3, None)


def _oracle_verdict(pair_id: str, mapping: dict) -> str:
    """Stable symmetric A/B/tie outcome; deliberately permits non-transitivity."""
    labels = ("A", "B")
    fps = {label: mapping[label]["phenotypeFingerprint"] for label in labels}
    if fps["A"] == fps["B"]:
        return "tie"
    h = int(hashlib.sha256((ORACLE_ID + ":" + pair_id).encode()).hexdigest(), 16)
    if h % 7 == 0:
        return "tie"
    ordered = sorted(fps.items(), key=lambda item: item[1])
    winner_fp = ordered[(h >> 3) & 1][1]
    return next(label for label, fp in fps.items() if fp == winner_fp)


def _resolve_pending(queue_dir: Path) -> int:
    decisions_path = queue_dir / "decisions.json"
    if not decisions_path.exists():
        return 0
    sealed = json.loads((queue_dir / "sealed-mapping.json").read_text())
    decisions = json.loads(decisions_path.read_text())
    resolved = 0
    for pair_id, item in decisions["decisions"].items():
        if item.get("verdict") is not None:
            continue
        item.update(
            verdict=_oracle_verdict(pair_id, sealed["pairs"][pair_id]),
            sourceClass="independent-model",
            sourceId=ORACLE_ID,
            confidence="strong",
            rationale="synthetic search-policy oracle; not artistic evidence",
        )
        resolved += 1
    decisions_path.write_text(json.dumps(decisions, indent=2) + "\n")
    return resolved


def _pending_count(queue_dir: Path) -> int:
    path = queue_dir / "decisions.json"
    if not path.exists():
        return 0
    decisions = json.loads(path.read_text()).get("decisions", {})
    return sum(item.get("verdict") is None for item in decisions.values())


def _pair_count(queue_dir: Path) -> int:
    path = queue_dir / "decisions.json"
    if not path.exists():
        return 0
    return len(json.loads(path.read_text()).get("decisions", {}))


def _trajectory_signature(state, report) -> str:
    candidates = []
    for candidate_id in sorted(state.candidates):
        c = state.candidates[candidate_id]
        candidates.append({
            "id": c.id,
            "route": c.route,
            "basin": c.basin,
            "parent": c.parent_id,
            "stage": c.stage,
            "genome": c.genome,
            "valid": bool(c.checks.get("valid", False)),
        })
    payload = {
        "candidates": candidates,
        "winner": report.get("winner"),
        "provisionalChampion": report.get("provisionalChampion"),
        "selectionStatus": report.get("selectionStatus"),
        "artisticFrontier": sorted(report.get("artisticFrontier", [])),
        "allocations": report.get("allocations", {}),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_policy(brief: dict, seed: int, cap: int | None, *, max_replays: int = 80) -> dict:
    with TemporaryDirectory() as td:
        root = Path(td)
        queue = root / "review"
        search_out = root / "search"
        review_rounds = 0
        replays = 0
        final_state = final_report = None
        while replays < max_replays:
            replays += 1
            selector = EvidenceAuthoritySelector(
                render_frame=__import__("core").render_candidate_frame,
                times=TIMES,
                queue_dir=queue,
                max_pending_reviews=cap,
            )
            final_state, final_report = run_search(brief, seed, search_out, selector)
            pending = _pending_count(queue)
            if pending == 0:
                break
            resolved = _resolve_pending(queue)
            if resolved != pending:
                raise AssertionError(f"resolved {resolved}/{pending} pending pairs")
            review_rounds += 1
        else:
            raise AssertionError(f"did not converge inside {max_replays} replays")

        return {
            "cap": "eager" if cap is None else cap,
            "ratings": _pair_count(queue),
            "reviewRounds": review_rounds,
            "searchReplays": replays,
            "trajectorySignature": _trajectory_signature(final_state, final_report),
            "selectionStatus": final_report["selectionStatus"],
            "winner": final_report.get("winner"),
            "provisionalChampion": final_report.get("provisionalChampion"),
            "frontierSize": len(final_report.get("artisticFrontier", [])),
            "candidateCount": final_report["checkerSummary"]["totalCandidates"],
        }


def _scenarios(quick: bool):
    base = default_brief()
    scenarios = [
        ("single-recurrence", {**base, "routes": ["recurrence"], "starts_per_route": 1, "explore_per_basin": 4, "roundA_per_survivor": 3, "total_extra_budget": 8}),
        ("single-family", {**base, "routes": ["family"], "starts_per_route": 1, "explore_per_basin": 4, "roundA_per_survivor": 3, "total_extra_budget": 8}),
        ("paired", {**base, "routes": ["recurrence", "family"], "starts_per_route": 1, "explore_per_basin": 2, "roundA_per_survivor": 2, "total_extra_budget": 6}),
    ]
    seeds = [19] if quick else [7, 19, 43]
    if quick:
        scenarios = [scenarios[-1]]
    return scenarios, seeds


def run_experiment(*, quick: bool = False) -> dict:
    scenarios, seeds = _scenarios(quick)
    blocks = []
    for scenario, brief in scenarios:
        for seed in seeds:
            policies = [run_policy(brief, seed, cap) for cap in CAPS]
            eager = next(p for p in policies if p["cap"] == "eager")
            if any(p["trajectorySignature"] != eager["trajectorySignature"] for p in policies):
                raise AssertionError(f"final dynamic trajectory diverged for {scenario} seed={seed}")
            blocks.append({"scenario": scenario, "seed": seed, "policies": policies})

    def vals(cap, field):
        return [next(p for p in b["policies"] if p["cap"] == cap)[field] for b in blocks]

    summary = {}
    for cap in (1, 2, 3, "eager"):
        ratings = vals(cap, "ratings")
        rounds = vals(cap, "reviewRounds")
        replays = vals(cap, "searchReplays")
        summary[str(cap)] = {
            "meanRatings": statistics.fmean(ratings),
            "maxRatings": max(ratings),
            "meanReviewRounds": statistics.fmean(rounds),
            "maxReviewRounds": max(rounds),
            "meanSearchReplays": statistics.fmean(replays),
        }
    eager_ratings = summary["eager"]["meanRatings"]
    cap2_ratings = summary["2"]["meanRatings"]
    cap1_rounds = summary["1"]["meanReviewRounds"]
    cap2_rounds = summary["2"]["meanReviewRounds"]
    return {
        "version": 1,
        "purpose": "dynamic search-policy calibration only; synthetic oracle is not artistic evidence",
        "quick": quick,
        "blockCount": len(blocks),
        "trajectoryAgreement": "all caps exactly match eager final candidate trajectory in every block",
        "summary": summary,
        "cap2VsEagerMeanRatingReduction": (eager_ratings - cap2_ratings) / eager_ratings if eager_ratings else 0,
        "cap2VsCap1MeanRoundReduction": (cap1_rounds - cap2_rounds) / cap1_rounds if cap1_rounds else 0,
        "blocks": blocks,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--output")
    args = ap.parse_args()
    result = run_experiment(quick=args.quick)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
