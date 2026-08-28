#!/usr/bin/env python3
"""Profile the first real evidence replays for the five-route stress workload.

The goal is to locate the scaling cost, not to finish the full scheduler stress.
Each replay reports wall time plus time/call counts attributable to deterministic
archive generation, phenotype rendering/fingerprinting, and the adaptive search.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reproduce as stress

PROFILE_ROUNDS = 2
PROBES_PER_ROUTE = 2


def _meter(fn):
    stats = {"calls": 0, "seconds": 0.0}

    def wrapped(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            stats["calls"] += 1
            stats["seconds"] += time.perf_counter() - t0

    return wrapped, stats


def _snapshot(stats: dict) -> dict:
    return {name: {"calls": int(item["calls"]), "seconds": item["seconds"]} for name, item in stats.items()}


def _delta(after: dict, before: dict) -> dict:
    return {
        name: {
            "calls": after[name]["calls"] - before[name]["calls"],
            "seconds": after[name]["seconds"] - before[name]["seconds"],
        }
        for name in after
    }


def run_mode(*, triads: bool, rounds: int = PROFILE_ROUNDS) -> dict:
    brief = stress._brief("living-form")
    seed = 89
    timings = []

    render, render_stats = _meter(stress.base.render_candidate_frame)
    generate, generate_stats = _meter(stress.base._generate_route_archive)
    search, search_stats = _meter(stress.base.run_search_from_starts)
    meters = {"render": render_stats, "generate": generate_stats, "search": search_stats}

    with TemporaryDirectory() as td:
        root = Path(td)
        t0 = time.perf_counter()
        stress.base.prepare_probe(
            brief=brief,
            seed=seed,
            out_dir=root,
            probe_budget=stress.PROBE_BUDGET,
            minimum_per_route=PROBES_PER_ROUTE,
            include_orbit=True,
            routes=stress.ROUTES,
            times=stress.base.TIMES,
            render_frame=render,
            generate_route_archive=generate,
        )
        stress._fill_route_screen(root)
        prepare_seconds = time.perf_counter() - t0
        prepare_meter = _snapshot(meters)
        print(json.dumps({
            "event": "prepare",
            "triads": triads,
            "seconds": prepare_seconds,
            "meters": prepare_meter,
        }), flush=True)

        pairq = root / "candidate-review"
        triadq = root / "candidate-triad-review" if triads else None
        for round_index in range(1, rounds + 1):
            before = _snapshot(meters)
            t0 = time.perf_counter()
            result = stress.base.resume_adaptive_search(
                out_dir=root,
                total_start_budget=stress.TOTAL_START_BUDGET,
                source_class="independent-model",
                source_id=stress.ROUTE_SCREEN_ID,
                evidence_authoritative_promotion=True,
                candidate_review_queue=pairq,
                candidate_max_pending_reviews=2,
                candidate_max_pending_reviews_per_group=1,
                candidate_pair_matrix_triads=triads,
                candidate_triad_review_queue=triadq,
                render_frame=render,
                generate_route_archive=generate,
                run_search_from_starts=search,
            )
            seconds = time.perf_counter() - t0
            after = _snapshot(meters)
            pending_pairs = stress.base._pending_pair_ids(pairq)
            pending_triads = stress.base._pending_triad_ids(triadq) if triadq is not None else []
            queued = result.get("candidateQueuedReviewTasks") or []
            record = {
                "round": round_index,
                "seconds": seconds,
                "pendingPairs": len(pending_pairs),
                "pendingTriads": len(pending_triads),
                "queuedTasks": len(queued) if triads else len(pending_pairs),
                "queuedKinds": [item.get("kind") for item in queued],
                "meters": _delta(after, before),
            }
            timings.append(record)
            print(json.dumps({"event": "replay", "triads": triads, **record}), flush=True)
            if not pending_pairs and not pending_triads:
                break
            stress.base._resolve_pair_pending(pairq)
            if triadq is not None:
                stress.base._resolve_triad_pending(triadq)

    return {
        "triads": triads,
        "prepareSeconds": prepare_seconds,
        "prepareMeters": prepare_meter,
        "replays": timings,
        "meanReplaySeconds": sum(item["seconds"] for item in timings) / max(1, len(timings)),
    }


def main() -> None:
    out = {
        "version": 2,
        "workload": "living-form-seed-89-five-routes",
        "profileRounds": PROFILE_ROUNDS,
        "pair": run_mode(triads=False),
        "triad": run_mode(triads=True),
    }
    print(json.dumps({"event": "summary", "result": out}), flush=True)


if __name__ == "__main__":
    main()
