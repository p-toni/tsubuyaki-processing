#!/usr/bin/env python3
"""Time the first few real review replays for the five-route stress workload."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reproduce as stress


def run_mode(*, triads: bool, rounds: int = 5) -> dict:
    brief = stress._brief("living-form")
    seed = 89
    timings = []
    with TemporaryDirectory() as td:
        root = Path(td)
        t0 = time.perf_counter()
        stress._prepare(root, brief, seed)
        prepare_seconds = time.perf_counter() - t0
        print(json.dumps({"event": "prepare", "triads": triads, "seconds": prepare_seconds}), flush=True)

        pairq = root / "candidate-review"
        triadq = root / "candidate-triad-review" if triads else None
        for round_index in range(1, rounds + 1):
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
                render_frame=stress.base.render_candidate_frame,
                generate_route_archive=stress.base._generate_route_archive,
                run_search_from_starts=stress.base.run_search_from_starts,
            )
            seconds = time.perf_counter() - t0
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
        "replays": timings,
        "meanReplaySeconds": sum(item["seconds"] for item in timings) / max(1, len(timings)),
    }


def main() -> None:
    out = {
        "version": 1,
        "workload": "living-form-seed-89-five-routes",
        "pair": run_mode(triads=False),
        "triad": run_mode(triads=True),
    }
    print(json.dumps({"event": "summary", "result": out}), flush=True)


if __name__ == "__main__":
    main()
