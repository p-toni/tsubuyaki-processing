#!/usr/bin/env python3
"""Pairwise temporal selector primitives for autonomous discovery.

This module deliberately avoids a universal scalar beauty score.
A selector returns only a clear preference or a tie/defer, plus auditable
per-dimension evidence. Search policy decides what to do with that verdict.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import statistics
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class DimensionVote:
    name: str
    winner: str  # "a", "b", or "tie"
    reason: str
    a_value: object = None
    b_value: object = None


@dataclass(frozen=True)
class PairwiseDecision:
    a_id: str
    b_id: str
    verdict: str  # "a", "b", "tie"
    confidence: str  # "clear" or "defer"
    dimensions: Tuple[DimensionVote, ...]
    source: str

    def to_json(self):
        return {
            "aId": self.a_id,
            "bId": self.b_id,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "dimensions": [asdict(d) for d in self.dimensions],
            "source": self.source,
        }


class PairwiseSelector:
    """Interface implemented by all artistic selectors."""

    name = "pairwise-selector"

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        raise NotImplementedError


def _lower_better(name, av, bv, threshold, reason) -> DimensionVote:
    if av is None or bv is None:
        return DimensionVote(name, "tie", "insufficient evidence", av, bv)
    delta = av - bv
    if abs(delta) <= threshold:
        return DimensionVote(name, "tie", f"difference <= {threshold:g}", av, bv)
    return DimensionVote(name, "a" if delta < 0 else "b", reason, av, bv)


def _higher_better(name, av, bv, threshold, reason) -> DimensionVote:
    if av is None or bv is None:
        return DimensionVote(name, "tie", "insufficient evidence", av, bv)
    delta = av - bv
    if abs(delta) <= threshold:
        return DimensionVote(name, "tie", f"difference <= {threshold:g}", av, bv)
    return DimensionVote(name, "a" if delta > 0 else "b", reason, av, bv)


def _band_distance(v: float, lo: float, hi: float) -> float:
    if lo <= v <= hi:
        return 0.0
    return lo - v if v < lo else v - hi


def _band_better(name, av, bv, lo, hi, threshold, reason) -> DimensionVote:
    ad = _band_distance(av, lo, hi)
    bd = _band_distance(bv, lo, hi)
    return _lower_better(name, ad, bd, threshold, reason)


def _mean(values: Sequence[float]) -> Optional[float]:
    vals = [v for v in values if isinstance(v, (int, float))]
    return statistics.fmean(vals) if vals else None


class DeterministicTemporalSelector(PairwiseSelector):
    """Executable proxy judge for the prototype.

    It uses matched temporal evidence and route-semantic diagnostics, but never
    collapses them into one continuous aesthetic score. Each dimension votes
    independently. A preference is emitted only when the evidence has a clear
    margin; otherwise the result is tie/defer.

    This is intentionally a proxy, not a claim that these hand-built dimensions
    encode artistic quality. The interface is designed so a human or multimodal
    model judge can replace it without changing search policy.
    """

    name = "deterministic-temporal-proxy-v1"

    def __init__(self, min_vote_margin: int = 1, min_decisive_dimensions: int = 2):
        self.min_vote_margin = min_vote_margin
        self.min_decisive_dimensions = min_decisive_dimensions

    def _validity(self, a, b) -> Optional[PairwiseDecision]:
        av = bool(a.checks.get("valid", False))
        bv = bool(b.checks.get("valid", False))
        if av and bv:
            return None
        if av != bv:
            vote = DimensionVote(
                "route-validity", "a" if av else "b",
                "invalid candidates cannot win artistic promotion",
                av, bv,
            )
            return PairwiseDecision(
                a.id, b.id, "a" if av else "b", "clear", (vote,), self.name
            )
        return PairwiseDecision(
            a.id, b.id, "tie", "defer",
            (DimensionVote("route-validity", "tie", "both candidates are invalid", av, bv),),
            self.name,
        )

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        validity = self._validity(a, b)
        if validity is not None:
            return validity

        votes: List[DimensionVote] = []
        af, bf = a.features, b.features

        # Universal visual / temporal evidence.
        bbox_lo, bbox_hi = brief.get("bbox_target", [0.55, 0.82])
        a_span = max(float(af.get("bbox_w_mean", 0)), float(af.get("bbox_h_mean", 0)))
        b_span = max(float(bf.get("bbox_w_mean", 0)), float(bf.get("bbox_h_mean", 0)))
        votes.append(_band_better(
            "composition-span", a_span, b_span, float(bbox_lo), float(bbox_hi), 0.025,
            "one candidate is materially closer to the requested canvas span",
        ))

        ac = float(af.get("center_dx_mean", 1)) + float(af.get("center_dy_mean", 1))
        bc = float(bf.get("center_dx_mean", 1)) + float(bf.get("center_dy_mean", 1))
        votes.append(_lower_better(
            "composition-centering", ac, bc, 0.035,
            "one candidate has materially stronger framing balance",
        ))

        at = float(af.get("temporal_change_mean", 0))
        bt = float(bf.get("temporal_change_mean", 0))
        # Enough motion to matter, but not a flicker/explosion proxy. Validity
        # already handles discontinuity; this criterion only distinguishes static-ish work.
        votes.append(_band_better(
            "temporal-interest", at, bt, 0.006, 0.09, 0.004,
            "one candidate has a more useful amount of visible change across the review horizon",
        ))

        atc = float(af.get("temporal_change_cv", 0))
        btc = float(bf.get("temporal_change_cv", 0))
        votes.append(_lower_better(
            "temporal-consistency", atc, btc, 0.18,
            "one candidate distributes motion more coherently across the review horizon",
        ))

        # Same-route semantic evidence. Cross-route comparisons deliberately avoid
        # pretending route-specific quantities are commensurate.
        if a.route == b.route == "recurrence":
            adiag = a.checks.get("diagnostics", {})
            bdiag = b.checks.get("diagnostics", {})
            acv = _mean([x.get("p95_over_median") for x in adiag.get("spineContinuityByFrame", [])])
            bcv = _mean([x.get("p95_over_median") for x in bdiag.get("spineContinuityByFrame", [])])
            votes.append(_lower_better(
                "filament-continuity", acv, bcv, 0.35,
                "one filament has materially more coherent axial sampling",
            ))
            asp = _mean([x.get("dominant") for x in adiag.get("spineBBoxByFrame", [])])
            bsp = _mean([x.get("dominant") for x in bdiag.get("spineBBoxByFrame", [])])
            if asp is not None and bsp is not None:
                votes.append(_band_better(
                    "filament-spine-span", asp, bsp, 0.48, 0.88, 0.035,
                    "one filament has a more useful axial composition",
                ))
            # Occupancy is intentionally not used on recurrence.

        elif a.route == b.route == "family":
            adiag = a.checks.get("diagnostics", {})
            bdiag = b.checks.get("diagnostics", {})
            acv = _mean(adiag.get("siblingLengthCVByFrame", []))
            bcv = _mean(bdiag.get("siblingLengthCVByFrame", []))
            votes.append(_lower_better(
                "family-coherence", acv, bcv, 0.025,
                "one candidate preserves the shared sibling law more coherently",
            ))
            agap = _mean(adiag.get("minimumAnchorGapRatioByFrame", []))
            bgap = _mean(bdiag.get("minimumAnchorGapRatioByFrame", []))
            if agap is not None and bgap is not None:
                votes.append(_higher_better(
                    "family-separation", agap, bgap, 0.012,
                    "one candidate keeps repeated organs more distinctly separated",
                ))
            # For the family route, occupancy is only a weak material cue and is
            # considered as a band, never as a global success score.
            ao = float(af.get("occupancy_mean", 0))
            bo = float(bf.get("occupancy_mean", 0))
            votes.append(_band_better(
                "family-material-presence", ao, bo, 0.035, 0.12, 0.012,
                "one candidate is materially closer to the expected repeated-family material density",
            ))

        aw = sum(v.winner == "a" for v in votes)
        bw = sum(v.winner == "b" for v in votes)
        decisive = aw + bw
        margin = aw - bw

        if decisive < self.min_decisive_dimensions or abs(margin) < self.min_vote_margin:
            verdict = "tie"
            confidence = "defer"
        else:
            verdict = "a" if margin > 0 else "b"
            confidence = "clear"

        return PairwiseDecision(a.id, b.id, verdict, confidence, tuple(votes), self.name)


class RecordedDecisionSelector(PairwiseSelector):
    """Replay human/external pairwise judgments with an optional fallback selector.

    Decisions are keyed by the unordered candidate pair and expressed as the winning
    candidate id or ``"tie"``. This lets experiments inject independently collected
    judgments without changing the search loop.
    """

    name = "recorded-pairwise-decisions"

    def __init__(self, decisions: Mapping[str, str], fallback: Optional[PairwiseSelector] = None):
        self.decisions = dict(decisions)
        self.fallback = fallback

    @staticmethod
    def key(a_id: str, b_id: str) -> str:
        return "::".join(sorted((a_id, b_id)))

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        key = self.key(a.id, b.id)
        if key not in self.decisions:
            if self.fallback is None:
                return PairwiseDecision(
                    a.id, b.id, "tie", "defer",
                    (DimensionVote("recorded-judgment", "tie", "no recorded decision"),),
                    self.name,
                )
            return self.fallback.compare(a, b, brief)
        result = self.decisions[key]
        if result == "tie":
            verdict = "tie"
        elif result == a.id:
            verdict = "a"
        elif result == b.id:
            verdict = "b"
        else:
            raise ValueError(f"recorded winner {result!r} is not part of pair {a.id!r}, {b.id!r}")
        return PairwiseDecision(
            a.id, b.id, verdict, "defer" if verdict == "tie" else "clear",
            (DimensionVote("recorded-judgment", verdict, "independent recorded pairwise judgment", result, result),),
            self.name,
        )


def incumbent_challenge(selector: PairwiseSelector, incumbent, challenger, brief):
    """Elite-preserving promotion: challenger replaces incumbent only on clear win."""
    decision = selector.compare(incumbent, challenger, brief)
    if decision.verdict == "b":
        return challenger, decision
    return incumbent, decision


def tournament_champion(selector: PairwiseSelector, candidates: Sequence[object], brief):
    """Return an elite-preserving champion plus every pairwise decision made.

    Ties preserve the current incumbent rather than manufacturing a preference.
    """
    if not candidates:
        raise ValueError("tournament requires at least one candidate")
    champion = candidates[0]
    decisions: List[PairwiseDecision] = []
    for challenger in candidates[1:]:
        champion, decision = incumbent_challenge(selector, champion, challenger, brief)
        decisions.append(decision)
    return champion, decisions


def clear_loss_frontier(selector: PairwiseSelector, candidates: Sequence[object], brief):
    """Find a champion, then preserve all candidates it cannot clearly beat."""
    champion, tournament = tournament_champion(selector, candidates, brief)
    survivors = [champion]
    comparisons: List[PairwiseDecision] = []
    for cand in candidates:
        if cand.id == champion.id:
            continue
        decision = selector.compare(champion, cand, brief)
        comparisons.append(decision)
        if decision.verdict != "a":
            survivors.append(cand)
    return champion, survivors, tournament + comparisons


def route_aware_frontier(selector: PairwiseSelector, candidates: Sequence[object], brief):
    """Reduce candidates within each route before asking for cross-route judgment.

    This prevents a cross-route tie from shielding obvious same-route losses. If
    cross-route evidence is insufficient, each surviving route keeps its local
    frontier rather than forcing unrelated representations into one total order.
    """
    if not candidates:
        raise ValueError("route-aware frontier requires candidates")
    by_route: Dict[str, List[object]] = {}
    for cand in candidates:
        by_route.setdefault(cand.route, []).append(cand)

    route_frontiers: Dict[str, List[object]] = {}
    route_champions: List[object] = []
    decisions: List[PairwiseDecision] = []
    for route in sorted(by_route):
        champion, survivors, ds = clear_loss_frontier(selector, by_route[route], brief)
        route_champions.append(champion)
        route_frontiers[route] = survivors
        decisions.extend(ds)

    if len(route_champions) == 1:
        only = route_champions[0]
        return only, list(route_frontiers[only.route]), decisions

    global_champion, surviving_route_champions, cross = clear_loss_frontier(selector, route_champions, brief)
    decisions.extend(cross)
    surviving_routes = {c.route for c in surviving_route_champions}
    survivors: List[object] = []
    for route in sorted(surviving_routes):
        survivors.extend(route_frontiers[route])
    return global_champion, survivors, decisions
