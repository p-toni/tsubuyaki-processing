#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from PIL import Image, ImageDraw, ImageOps

from core import Candidate, ROUTES, TIMES, evaluate_candidate, render_candidate_frame
from pairwise_selector import DeterministicTemporalSelector, PairwiseSelector, clear_loss_frontier
from rng_streams import representation_rng

STREAM = "representation-capacity-v1"


def _stable_hash(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _generate_route_archive(brief, seed: int, route: str, starts: int):
    """Generate a selector-independent fixed archive of viable independent starts."""
    rng = representation_rng(seed, route, ROUTES[route].get("version", "1"), STREAM)
    prefix = ROUTES[route].get("prefix", route[:1].upper())
    candidates: List[Candidate] = []
    attempts = 0
    max_attempts = max(starts, starts * 20)

    while len(candidates) < starts and attempts < max_attempts:
        attempts += 1
        cid = f"{prefix}C{len(candidates)+1}"
        cand = Candidate(cid, route, cid, ROUTES[route]["seed"](rng), None, "capacity-start")
        evaluate_candidate(cand, brief)
        if cand.checks.get("valid", False):
            candidates.append(cand)

    if len(candidates) != starts:
        raise RuntimeError(
            f"capacity archive {route} produced only {len(candidates)}/{starts} valid starts "
            f"within {attempts} attempts"
        )
    return candidates, attempts


def _route_archive_hash(candidates: List[Candidate]) -> str:
    return _stable_hash([{"id": c.id, "route": c.route, "genome": c.genome} for c in candidates])


def _montage(candidates: List[Candidate], out: Path, title: str):
    thumb = 150
    strip_w = thumb * len(TIMES)
    cols = 2
    rows = math.ceil(len(candidates) / cols)
    cell_w = strip_w + 10
    cell_h = thumb + 30
    canvas = Image.new("RGB", (cols * cell_w, 28 + rows * cell_h), (26, 26, 26))
    draw = ImageDraw.Draw(canvas)
    draw.text((6, 6), title, fill=(240, 240, 240))
    for i, cand in enumerate(candidates):
        x = (i % cols) * cell_w
        y = 28 + (i // cols) * cell_h
        draw.text((x + 4, y + 4), cand.id, fill=(225, 225, 225))
        for j, t in enumerate(TIMES):
            frame = ImageOps.autocontrast(render_candidate_frame(cand, t)).convert("RGB")
            canvas.paste(frame.resize((thumb, thumb)), (x + j * thumb, y + 22))
    canvas.save(out)


def run_capacity(
    brief,
    seed: int,
    out_dir: Path,
    starts_per_route: int = 6,
    selector: PairwiseSelector | None = None,
):
    """Measure representation capacity without adaptive search or allocation.

    Candidate generation is complete before selection and does not depend on selector
    outcomes. Each representation receives the same number of viable independent starts.
    Local route frontiers must resolve before cross-route comparison begins.
    """
    selector = selector or DeterministicTemporalSelector()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    routes = sorted(brief.get("eligible_routes") or brief.get("routes") or [])
    if not routes:
        raise ValueError("brief must define eligible_routes or routes")
    unknown = [r for r in routes if r not in ROUTES]
    if unknown:
        raise ValueError(f"unknown representation(s): {unknown}")
    if starts_per_route < 2:
        raise ValueError("starts_per_route must be >= 2")

    archives: Dict[str, List[Candidate]] = {}
    attempts: Dict[str, int] = {}
    archive_hashes: Dict[str, str] = {}
    route_frontiers: Dict[str, List[Candidate]] = {}
    route_champions: Dict[str, Candidate] = {}
    decisions = []

    # Generation phase: no selector calls are allowed above this boundary.
    for route in routes:
        candidates, n_attempts = _generate_route_archive(brief, seed, route, starts_per_route)
        archives[route] = candidates
        attempts[route] = n_attempts
        archive_hashes[route] = _route_archive_hash(candidates)
        _montage(candidates, out_dir / f"{route}_archive.png", f"{route}: fixed capacity archive")

    # Selection phase: first resolve capacity within each representation.
    for route in routes:
        champion, frontier, ds = clear_loss_frontier(selector, archives[route], brief)
        route_champions[route] = champion
        route_frontiers[route] = frontier
        for decision in ds:
            item = decision.to_json()
            item["stage"] = f"route:{route}"
            decisions.append(item)

    unresolved_routes = [r for r in routes if len(route_frontiers[r]) != 1]
    global_frontier: List[Candidate] = []
    global_champion = None

    if not unresolved_routes:
        global_champion, global_frontier, ds = clear_loss_frontier(
            selector, [route_champions[r] for r in routes], brief
        )
        for decision in ds:
            item = decision.to_json()
            item["stage"] = "global-route-frontier"
            decisions.append(item)

    if unresolved_routes:
        status = "pending-route-frontiers"
    elif len(global_frontier) == 1:
        status = "clear"
    else:
        status = "pending-global-frontier"

    heuristic_route = brief.get("route_first")
    global_routes = [c.route for c in global_frontier]
    all_candidates = [c for route in routes for c in archives[route]]
    report = {
        "seed": seed,
        "stream": STREAM,
        "startsPerRoute": int(starts_per_route),
        "routes": routes,
        "heuristicRoute": heuristic_route,
        "candidateCount": len(all_candidates),
        "attemptsByRoute": attempts,
        "routeArchiveHashes": archive_hashes,
        "routeFrontiers": {r: [c.id for c in route_frontiers[r]] for r in routes},
        "routeChampions": {r: route_champions[r].id for r in routes},
        "unresolvedRoutes": unresolved_routes,
        "globalFrontier": [c.id for c in global_frontier],
        "globalFrontierRoutes": global_routes,
        "provisionalChampion": global_champion.id if global_champion else None,
        "provisionalChampionRoute": global_champion.route if global_champion else None,
        "heuristicRouteInGlobalFrontier": (
            heuristic_route in set(global_routes) if global_frontier else None
        ),
        "selectionStatus": status,
        "selector": selector.name,
        "diagnosticScoreUsedForPromotion": False,
        "generationDependsOnSelector": False,
    }
    state = {
        "brief": brief,
        "seed": seed,
        "stream": STREAM,
        "archives": {r: [asdict(c) for c in archives[r]] for r in routes},
        "decisions": decisions,
    }
    (out_dir / "capacity_report.json").write_text(json.dumps(report, indent=2) + "\n")
    (out_dir / "capacity_state.json").write_text(json.dumps(state, indent=2) + "\n")
    return state, report


def _build_selector(args, out: Path):
    selector: PairwiseSelector = DeterministicTemporalSelector()
    if args.blind_decisions_dir:
        from decision_ledger import decode_blind_decision_dirs
        from judge_queue import RecordedPhenotypeDecisionSelector

        selector = RecordedPhenotypeDecisionSelector(
            decode_blind_decision_dirs(args.blind_decisions_dir),
            render_candidate_frame,
            TIMES,
            fallback=selector,
        )
    if args.multimodal_judge:
        from multimodal_judge import MultimodalEscalatingSelector

        selector = MultimodalEscalatingSelector(
            coarse=selector,
            render_frame=render_candidate_frame,
            times=TIMES,
            model=args.judge_model,
            reasoning_effort=args.judge_reasoning,
            image_detail=args.judge_image_detail,
            max_api_calls=args.judge_max_api_calls,
            cache_path=out / "judge-cache.json",
            audit_dir=out / "judge-audit",
            symmetry=not args.judge_no_symmetry,
        )
    if args.judge_queue:
        from judge_queue import QueueingSelector

        selector = QueueingSelector(selector, Path(args.judge_queue), render_candidate_frame, TIMES)
    return selector


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--starts-per-route", type=int, default=6)
    ap.add_argument("--out", required=True)
    ap.add_argument("--judge-queue", default="")
    ap.add_argument("--blind-decisions-dir", action="append", default=[])
    ap.add_argument("--multimodal-judge", action="store_true")
    ap.add_argument("--judge-model", default=os.getenv("OPENAI_JUDGE_MODEL", "gpt-5.6-terra"))
    ap.add_argument("--judge-reasoning", default="medium", choices=["low", "medium", "high", "max"])
    ap.add_argument("--judge-image-detail", default="high", choices=["low", "high", "auto"])
    ap.add_argument("--judge-max-api-calls", type=int, default=240)
    ap.add_argument("--judge-no-symmetry", action="store_true")
    args = ap.parse_args()

    brief = json.loads(Path(args.brief).read_text())
    out = Path(args.out)
    selector = _build_selector(args, out)
    _, report = run_capacity(brief, args.seed, out, args.starts_per_route, selector)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
