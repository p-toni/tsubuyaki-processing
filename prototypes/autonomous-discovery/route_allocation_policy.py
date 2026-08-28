"""Research policy: semantic priors may allocate compute, never authorize artistic exclusion.

The policy separates three concerns:
1. mathematical hard validity (elsewhere),
2. cheap text/same-model priors for ordering and nonzero probe allocation,
3. authoritative visual evidence for route elimination.

A route remains artistically alive until a strong human or independent-model visual
screen explicitly drops it. Incomplete screens fail broad, not narrow. Positive
human/independent keeps may focus *extra* budget while every unresolved route still
receives its minimum safe allocation.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

SOURCE_CLASSES = {"human", "independent-model", "same-model", "deterministic-proxy", "text-prior"}
AUTHORITATIVE = {"human", "independent-model"}
CONFIDENCE = {"strong", "low", "defer"}
VERDICTS = {"keep", "drop", "defer"}


@dataclass(frozen=True)
class RouteEvidence:
    route: str
    verdict: str
    source_class: str
    source_id: str
    confidence: str = "strong"
    rationale: str = ""

    def __post_init__(self):
        if self.verdict not in VERDICTS:
            raise ValueError(f"invalid verdict {self.verdict!r}")
        if self.source_class not in SOURCE_CLASSES:
            raise ValueError(f"invalid source class {self.source_class!r}")
        if self.confidence not in CONFIDENCE:
            raise ValueError(f"invalid confidence {self.confidence!r}")
        if not self.route or not self.source_id:
            raise ValueError("route and source_id are required")

    @property
    def authoritative(self) -> bool:
        return (
            self.source_class in AUTHORITATIVE
            and self.confidence == "strong"
            and self.verdict in {"keep", "drop"}
        )


@dataclass(frozen=True)
class RouteResolution:
    route: str
    status: str
    reason: str
    authoritative_sources: tuple[str, ...]


@dataclass(frozen=True)
class BudgetPlan:
    stage: str
    allocation: Mapping[str, int]
    active_routes: tuple[str, ...]
    hard_excluded_routes: tuple[str, ...]
    status: str
    narrowing_authorized: bool


def _dedupe_routes(routes: Sequence[str]) -> tuple[str, ...]:
    out = []
    for route in routes:
        if route not in out:
            out.append(route)
    if not out:
        raise ValueError("at least one route is required")
    return tuple(out)


def prior_order(routes: Sequence[str], scores: Mapping[str, float] | None = None) -> tuple[str, ...]:
    """Return a deterministic advisory ordering. Scores never imply exclusion."""
    routes = _dedupe_routes(routes)
    scores = scores or {}
    index = {r: i for i, r in enumerate(routes)}
    return tuple(sorted(routes, key=lambda r: (-float(scores.get(r, 0.0)), index[r])))


def resolve_route_evidence(route: str, evidence: Iterable[RouteEvidence]) -> RouteResolution:
    """Resolve one route. Advisory/low-confidence evidence cannot keep or drop it authoritatively."""
    by_source: dict[str, str] = {}
    for item in evidence:
        if item.route != route or not item.authoritative:
            continue
        prev = by_source.get(item.source_id)
        if prev is not None and prev != item.verdict:
            return RouteResolution(route, "defer", "one authoritative source conflicts with itself", tuple(sorted(by_source)))
        by_source[item.source_id] = item.verdict

    if not by_source:
        return RouteResolution(route, "defer", "no strong independent visual evidence", ())
    verdicts = set(by_source.values())
    if len(verdicts) != 1:
        return RouteResolution(route, "defer", "authoritative visual evidence conflicts", tuple(sorted(by_source)))
    status = next(iter(verdicts))
    return RouteResolution(route, status, "authoritative visual evidence resolved route", tuple(sorted(by_source)))


def resolve_screen(routes: Sequence[str], evidence: Iterable[RouteEvidence]) -> dict[str, RouteResolution]:
    routes = _dedupe_routes(routes)
    items = tuple(evidence)
    unknown = sorted({e.route for e in items} - set(routes))
    if unknown:
        raise ValueError(f"evidence names unknown route(s): {unknown}")
    return {r: resolve_route_evidence(r, items) for r in routes}


def _round_robin_allocate(targets: Sequence[str], units: int, order: Sequence[str]) -> dict[str, int]:
    out = {r: 0 for r in targets}
    if units <= 0 or not targets:
        return out
    ordered = [r for r in order if r in out]
    ordered += [r for r in targets if r not in ordered]
    for i in range(units):
        out[ordered[i % len(ordered)]] += 1
    return out


def initial_probe_plan(
    routes: Sequence[str],
    *,
    probe_budget: int,
    prior_scores: Mapping[str, float] | None = None,
    minimum_per_route: int = 1,
) -> BudgetPlan:
    """Give every representation nonzero visual exposure; priors may only distribute extras."""
    routes = _dedupe_routes(routes)
    required = minimum_per_route * len(routes)
    if minimum_per_route < 1:
        raise ValueError("minimum_per_route must be >= 1")
    if probe_budget < required:
        raise ValueError(f"probe_budget {probe_budget} cannot preserve all {len(routes)} routes; need >= {required}")
    allocation = {r: minimum_per_route for r in routes}
    order = prior_order(routes, prior_scores)
    extras = _round_robin_allocate(routes, probe_budget - required, order)
    for r, n in extras.items():
        allocation[r] += n
    return BudgetPlan("probe", allocation, routes, (), "broad-probe", False)


def deepening_plan(
    routes: Sequence[str],
    *,
    remaining_budget: int,
    evidence: Iterable[RouteEvidence] = (),
    prior_scores: Mapping[str, float] | None = None,
    minimum_if_unresolved: int = 1,
) -> BudgetPlan:
    """Allocate deeper search while making hard pruning authority explicit.

    Rules:
    - only explicit strong human/independent `drop` can remove a route;
    - an omitted/unresolved route stays alive and receives a nonzero minimum;
    - explicit strong `keep` may focus *extra* budget even when the screen is incomplete;
    - if the budget cannot preserve every non-dropped route, fail closed rather than top-k;
    - hard narrowing is authorized only when every route is authoritatively resolved.
    """
    routes = _dedupe_routes(routes)
    if remaining_budget < 0:
        raise ValueError("remaining_budget must be >= 0")
    screen = resolve_screen(routes, evidence)
    drops = tuple(r for r in routes if screen[r].status == "drop")
    keeps = tuple(r for r in routes if screen[r].status == "keep")
    unresolved = tuple(r for r in routes if screen[r].status == "defer")
    base_order = prior_order(routes, prior_scores)

    screen_complete = not unresolved
    narrowing_authorized = screen_complete and bool(keeps)

    if narrowing_authorized:
        active = keeps
        allocation = _round_robin_allocate(active, remaining_budget, base_order)
        return BudgetPlan("deepen", allocation, active, drops, "authoritative-narrowing", True)

    active = tuple(r for r in routes if r not in drops)
    if not active:
        active = routes
        drops = ()
    required = minimum_if_unresolved * len(active)
    if minimum_if_unresolved < 1:
        raise ValueError("minimum_if_unresolved must be >= 1")
    if remaining_budget < required:
        return BudgetPlan(
            "deepen", {r: 0 for r in active}, active, drops,
            f"insufficient-budget-for-safe-broadening: need {required}, have {remaining_budget}", False,
        )

    allocation = {r: minimum_if_unresolved for r in active}
    extra_units = remaining_budget - required

    # Positive-only review mode: a reviewer can name only the grammar(s) worth
    # deeper exploration. Unmentioned routes are *not* inferred as drops; they stay
    # alive at the minimum. Extra budget is focused on explicit strong keeps.
    focused_keeps = tuple(r for r in base_order if r in keeps and r in active)
    if focused_keeps:
        extras = _round_robin_allocate(focused_keeps, extra_units, focused_keeps)
        status = "incomplete-screen-positive-focus"
    else:
        extras = _round_robin_allocate(active, extra_units, base_order)
        status = "incomplete-screen-fail-broad"
    for r, n in extras.items():
        allocation[r] += n
    return BudgetPlan("deepen", allocation, active, drops, status, False)
