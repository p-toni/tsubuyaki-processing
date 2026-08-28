"""Two-phase route-screened adaptive search.

Phase 1 generates deterministic, nonzero probes for every mathematical
representation and exports a blinded route-level visual screen. Phase 2 replays
those exact probe prefixes, applies only authoritative route evidence, allocates
additional independent starts, and enters the existing adaptive search from the
reviewed phenotypes themselves.
"""
from __future__ import annotations

import hashlib
import io
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

from PIL import Image

from route_allocation_policy import deepening_plan, initial_probe_plan
from route_screen_queue import build_route_screen, decode_route_screen

VERSION = 1
# Human probe-depth calibration preserved the same route decision at 2 vs 4
# exemplars on 3/3 nested cases (v18) and 5/5 fresh holdout cases (v19).
# One exemplar remains unevidenced and must be requested explicitly.
DEFAULT_MIN_PROBES_PER_ROUTE = 2
# Synthetic exhaustive tournament replay shows two pending comparisons preserve
# much of lazy review's rating efficiency without forcing one reviewer round per
# comparison. One remains available as an explicit maximum-laziness override.
DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS = 2
# Three frozen real-search trajectories showed that a global K=2 batch can be
# monopolized by one route. Reserving at most one unresolved review per hidden
# route/cross-route group improved early coverage and reduced mean ratings and
# reviewer rounds versus global K=2 while preserving the eager trajectory.
DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS_PER_GROUP = 1


def _stable(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(payload).hexdigest()


def _png_bytes(im: Image.Image) -> bytes:
    b = io.BytesIO(); im.convert("RGB").save(b, format="PNG"); return b.getvalue()


def _candidate_record(cand) -> dict:
    raw = asdict(cand) if is_dataclass(cand) else dict(getattr(cand, "__dict__", {}))
    return {
        "id": str(getattr(cand, "id", raw.get("id", ""))),
        "route": str(getattr(cand, "route", raw.get("route", ""))),
        "basin": str(getattr(cand, "basin", raw.get("basin", ""))),
        "genome": raw.get("genome", getattr(cand, "genome", None)),
        "checks": raw.get("checks", getattr(cand, "checks", None)),
    }


def _candidate_signature(cand) -> str:
    return _stable(_candidate_record(cand))


def _phenotype_fingerprint(cand, render_frame: Callable, times: Sequence[float]) -> str:
    parts = [_png_bytes(render_frame(cand, t)) for t in times]
    return hashlib.sha256(b"\0".join(parts)).hexdigest()


def _load_default_dependencies(*, include_orbit: bool):
    # Orbit intentionally remains research-registered instead of changing the
    # baseline four-route registry. The screened five-route path must opt into it
    # before importing the capacity generator, which snapshots core.ROUTES.
    if include_orbit:
        from orbit_representation import register_orbit
        register_orbit()
    from core import ROUTES, TIMES, render_candidate_frame
    from representation_capacity import _generate_route_archive
    from search_engine import run_search_from_starts
    return tuple(ROUTES), tuple(TIMES), render_candidate_frame, _generate_route_archive, run_search_from_starts


def prepare_probe(
    *,
    brief: Mapping[str, object],
    seed: int,
    out_dir: Path,
    probe_budget: int | None = None,
    minimum_per_route: int = DEFAULT_MIN_PROBES_PER_ROUTE,
    prior_scores: Mapping[str, float] | None = None,
    include_orbit: bool = True,
    routes: Sequence[str] | None = None,
    times: Sequence[float] | None = None,
    render_frame: Callable | None = None,
    generate_route_archive: Callable | None = None,
) -> dict:
    if minimum_per_route < 1:
        raise ValueError("minimum_per_route must be >= 1")
    if routes is None or times is None or render_frame is None or generate_route_archive is None:
        d_routes, d_times, d_render, d_generate, _ = _load_default_dependencies(include_orbit=include_orbit)
        routes = tuple(routes or d_routes)
        times = tuple(times or d_times)
        render_frame = render_frame or d_render
        generate_route_archive = generate_route_archive or d_generate
    else:
        routes = tuple(routes); times = tuple(times)
    if not routes:
        raise ValueError("at least one route is required")
    required = minimum_per_route * len(routes)
    if probe_budget is None:
        probe_budget = required
    if probe_budget < required:
        raise ValueError(f"probe_budget {probe_budget} cannot provide {minimum_per_route} probes for all {len(routes)} routes; need >= {required}")

    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    plan = initial_probe_plan(
        routes, probe_budget=probe_budget, prior_scores=prior_scores,
        minimum_per_route=minimum_per_route,
    )
    archives = {}; attempts = {}; source_signatures = {}; phenotype_fingerprints = {}
    for route in routes:
        n = int(plan.allocation[route])
        cands, n_attempts = generate_route_archive(brief, seed, route, n)
        if len(cands) != n:
            raise RuntimeError(f"route {route} returned {len(cands)}/{n} probe candidates")
        archives[route] = list(cands)
        attempts[route] = int(n_attempts)
        source_signatures[route] = [_candidate_signature(c) for c in cands]
        phenotype_fingerprints[route] = [_phenotype_fingerprint(c, render_frame, times) for c in cands]

    screen_dir = out_dir / "route-screen"
    queue = build_route_screen(
        brief=brief, route_candidates=archives, render_frame=render_frame,
        times=times, out_dir=screen_dir,
    )
    state = {
        "version": VERSION,
        "brief": dict(brief),
        "seed": int(seed),
        "routes": list(routes),
        "times": list(times),
        "includeOrbit": bool(include_orbit),
        "probeBudget": int(probe_budget),
        "minimumPerRoute": int(minimum_per_route),
        "priorScores": dict(prior_scores or {}),
        "probeAllocation": dict(plan.allocation),
        "probeAttempts": attempts,
        "probeSourceSignatures": source_signatures,
        "probePhenotypeFingerprints": phenotype_fingerprints,
        "routeScreen": str(screen_dir),
        "screenId": queue["screenId"],
    }
    (out_dir / "probe-state.json").write_text(json.dumps(state, indent=2) + "\n")
    return state


def resume_adaptive_search(
    *,
    out_dir: Path,
    total_start_budget: int,
    source_class: str,
    source_id: str,
    prior_scores: Mapping[str, float] | None = None,
    selector=None,
    evidence_authoritative_promotion: bool = False,
    candidate_evidence_dirs: Sequence[Path] = (),
    candidate_review_queue: Path | None = None,
    candidate_advisory_selector=None,
    candidate_max_pending_reviews: int | None = DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS,
    candidate_max_pending_reviews_per_group: int | None = DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS_PER_GROUP,
    candidate_pair_matrix_triads: bool = False,
    candidate_triad_review_queue: Path | None = None,
    render_frame: Callable | None = None,
    generate_route_archive: Callable | None = None,
    run_search_from_starts: Callable | None = None,
) -> dict:
    out_dir = Path(out_dir)
    state = json.loads((out_dir / "probe-state.json").read_text())
    routes = tuple(state["routes"])
    brief = dict(state["brief"]); seed = int(state["seed"])
    probe_budget = int(state["probeBudget"])
    if total_start_budget < probe_budget:
        raise ValueError("total_start_budget cannot be smaller than spent probe budget")

    evidence_dirs = tuple(Path(p) for p in candidate_evidence_dirs)
    review_queue = Path(candidate_review_queue) if candidate_review_queue is not None else None
    triad_review_queue = Path(candidate_triad_review_queue) if candidate_triad_review_queue is not None else None
    if not evidence_authoritative_promotion and (
        evidence_dirs or review_queue is not None or candidate_advisory_selector is not None
        or candidate_pair_matrix_triads or triad_review_queue is not None
    ):
        raise ValueError("candidate evidence/review options require evidence_authoritative_promotion=True")
    if evidence_authoritative_promotion and selector is not None:
        raise ValueError("caller selector cannot be combined with evidence-authoritative promotion mode")
    if candidate_triad_review_queue is not None and not candidate_pair_matrix_triads:
        raise ValueError("candidate_triad_review_queue requires candidate_pair_matrix_triads=True")
    if candidate_max_pending_reviews is not None and candidate_max_pending_reviews < 1:
        raise ValueError("candidate_max_pending_reviews must be >= 1 or None")
    if candidate_max_pending_reviews_per_group is not None and candidate_max_pending_reviews_per_group < 1:
        raise ValueError("candidate_max_pending_reviews_per_group must be >= 1 or None")
    if candidate_pair_matrix_triads:
        review_queue = review_queue or (out_dir / "candidate-review")
        triad_review_queue = triad_review_queue or (out_dir / "candidate-triad-review")

    if render_frame is None or generate_route_archive is None or run_search_from_starts is None:
        _, _, d_render, d_generate, d_run = _load_default_dependencies(include_orbit=bool(state.get("includeOrbit", True)))
        render_frame = render_frame or d_render
        generate_route_archive = generate_route_archive or d_generate
        run_search_from_starts = run_search_from_starts or d_run

    candidate_promotion_mode = getattr(selector, "name", "legacy-default") if selector is not None else "legacy-default"
    candidate_review_scheduling_mode = "legacy-or-eager-pair-v1"
    authority_selector = None
    if evidence_authoritative_promotion:
        from evidence_selector import EvidenceAuthoritySelector
        if candidate_advisory_selector is None:
            from pairwise_selector import DeterministicTemporalSelector
            candidate_advisory_selector = DeterministicTemporalSelector()
        extra_evidence = []
        if candidate_pair_matrix_triads and triad_review_queue is not None:
            required = (
                triad_review_queue / "decisions.json",
                triad_review_queue / "sealed-mapping.json",
                triad_review_queue / "queue.json",
            )
            if any(path.exists() for path in required):
                if not all(path.exists() for path in required):
                    raise ValueError("candidate triad review queue is incomplete")
                from triad_pair_matrix_review_queue import decode_triad_pair_matrix_evidence
                extra_evidence.extend(decode_triad_pair_matrix_evidence(triad_review_queue))
        selector = EvidenceAuthoritySelector(
            render_frame=render_frame,
            times=tuple(state["times"]),
            evidence_dirs=evidence_dirs,
            queue_dir=review_queue,
            advisory=candidate_advisory_selector,
            max_pending_reviews=candidate_max_pending_reviews,
            max_pending_reviews_per_group=candidate_max_pending_reviews_per_group,
            extra_evidence=extra_evidence,
            collect_review_proposals=candidate_pair_matrix_triads,
        )
        authority_selector = selector
        candidate_promotion_mode = selector.name
        candidate_review_scheduling_mode = (
            "pair-matrix-triad-opt-in-v1" if candidate_pair_matrix_triads else "eager-pair-v1"
        )

    evidence = decode_route_screen(
        Path(state["routeScreen"]), source_class=source_class, source_id=source_id,
    )
    remaining = total_start_budget - probe_budget
    plan = deepening_plan(
        routes,
        remaining_budget=remaining,
        evidence=evidence,
        prior_scores=prior_scores if prior_scores is not None else state.get("priorScores", {}),
    )
    if plan.status.startswith("insufficient-budget"):
        raise ValueError(plan.status)

    starts = []; replay = {}; added_by_route = {}
    for route in plan.active_routes:
        probe_n = int(state["probeAllocation"][route])
        extra_n = int(plan.allocation.get(route, 0))
        total_n = probe_n + extra_n
        cands, attempts = generate_route_archive(brief, seed, route, total_n)
        got_source = [_candidate_signature(c) for c in cands[:probe_n]]
        got_pheno = [_phenotype_fingerprint(c, render_frame, state["times"]) for c in cands[:probe_n]]
        expected_source = list(state["probeSourceSignatures"][route])
        expected_pheno = list(state["probePhenotypeFingerprints"][route])
        if got_source != expected_source:
            raise RuntimeError(f"route {route} deterministic probe source prefix changed before adaptive search")
        if got_pheno != expected_pheno:
            raise RuntimeError(f"route {route} rendered probe phenotype changed before adaptive search")
        replay[route] = {
            "sourcePrefixVerified": True,
            "phenotypePrefixVerified": True,
            "attempts": int(attempts),
        }
        starts.extend(cands)
        added_by_route[route] = extra_n

    active_brief = dict(brief)
    active_brief["routes"] = list(plan.active_routes)
    adaptive_out = out_dir / "adaptive-search"
    _, search_report = run_search_from_starts(
        active_brief, seed, adaptive_out, starts, selector,
    )

    queued_review_tasks = []
    if candidate_pair_matrix_triads:
        if authority_selector is None or review_queue is None or triad_review_queue is None:
            raise RuntimeError("pair-matrix triad scheduling requires an evidence-authority selector and both review queues")
        from candidate_review_scheduler import flush_review_proposals
        queued_review_tasks = flush_review_proposals(
            authority_selector.review_proposals,
            evidence=authority_selector.evidence,
            pair_queue_dir=review_queue,
            triad_queue_dir=triad_review_queue,
            times=tuple(state["times"]),
            enable_triads=True,
            max_tasks=candidate_max_pending_reviews,
            max_tasks_per_group=candidate_max_pending_reviews_per_group,
        )

    report = {
        "version": VERSION,
        "totalStartBudget": int(total_start_budget),
        "probeBudget": probe_budget,
        "remainingStartBudget": remaining,
        "minimumPerRoute": int(state["minimumPerRoute"]),
        "sourceClass": source_class,
        "sourceId": source_id,
        "allocationStatus": plan.status,
        "narrowingAuthorized": bool(plan.narrowing_authorized),
        "activeRoutes": list(plan.active_routes),
        "hardExcludedRoutes": list(plan.hard_excluded_routes),
        "additionalStartsByRoute": added_by_route,
        "probeReplay": replay,
        "candidatePromotionMode": candidate_promotion_mode,
        "candidateReviewSchedulingMode": candidate_review_scheduling_mode,
        "candidateEvidenceDirs": [str(p) for p in evidence_dirs],
        "candidateReviewQueue": str(review_queue) if review_queue is not None else None,
        "candidateTriadReviewQueue": str(triad_review_queue) if triad_review_queue is not None else None,
        "candidatePairMatrixTriads": bool(candidate_pair_matrix_triads),
        "candidateQueuedReviewTasks": queued_review_tasks,
        "candidateMaxPendingReviews": candidate_max_pending_reviews,
        "candidateMaxPendingReviewsPerGroup": candidate_max_pending_reviews_per_group,
        "adaptiveSearch": search_report,
    }
    (out_dir / "screened-search-report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
