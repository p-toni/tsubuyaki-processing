"""Preference-evidence policy for artistic promotion.

This module is intentionally separate from the legacy v2 replay path. Historical
experiments remain reproducible, while future search can distinguish advisory
judgments from promotion-authoritative evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

VALID_VERDICTS = {"a", "b", "tie"}
VALID_CONFIDENCE = {"strong", "low", "defer"}
VALID_SOURCE_CLASS = {"human", "independent-model", "same-model", "deterministic-proxy"}
AUTHORITATIVE_SOURCE_CLASS = {"human", "independent-model"}


@dataclass(frozen=True)
class PreferenceEvidence:
    pair_id: str
    verdict: str
    source_class: str
    source_id: str
    confidence: str = "strong"
    rationale: str = ""

    def __post_init__(self):
        if self.verdict not in VALID_VERDICTS:
            raise ValueError(f"invalid verdict: {self.verdict}")
        if self.confidence not in VALID_CONFIDENCE:
            raise ValueError(f"invalid confidence: {self.confidence}")
        if self.source_class not in VALID_SOURCE_CLASS:
            raise ValueError(f"invalid source class: {self.source_class}")
        if not self.pair_id:
            raise ValueError("pair_id is required")
        if not self.source_id:
            raise ValueError("source_id is required")

    @property
    def authoritative(self) -> bool:
        return (
            self.source_class in AUTHORITATIVE_SOURCE_CLASS
            and self.confidence == "strong"
            and self.verdict in {"a", "b"}
        )


@dataclass(frozen=True)
class PromotionResolution:
    verdict: str
    confidence: str
    reason: str
    authoritative_sources: tuple[str, ...]


def resolve_promotion_evidence(
    evidence: Iterable[PreferenceEvidence],
    *,
    pair_id: Optional[str] = None,
) -> PromotionResolution:
    """Resolve evidence without treating repeated votes as scalar fitness.

    Rules:
    - only strong human/independent-model evidence can promote;
    - low-confidence, same-model, and deterministic-proxy evidence is advisory;
    - one source_id contributes at most one authoritative verdict;
    - conflicting authoritative verdicts fail closed to defer;
    - authoritative ties are not promotions and do not erase clear evidence.
    """
    items = list(evidence)
    if pair_id is not None:
        items = [e for e in items if e.pair_id == pair_id]
    if not items:
        return PromotionResolution("tie", "defer", "no preference evidence", ())

    pair_ids = {e.pair_id for e in items}
    if len(pair_ids) != 1:
        raise ValueError("all evidence must refer to one phenotype pair")

    by_source = {}
    for e in items:
        if not e.authoritative:
            continue
        prev = by_source.get(e.source_id)
        if prev is not None and prev != e.verdict:
            return PromotionResolution(
                "tie", "defer", "one authoritative source issued conflicting clear verdicts", tuple(sorted(by_source))
            )
        by_source[e.source_id] = e.verdict

    if not by_source:
        return PromotionResolution(
            "tie", "defer", "only advisory or low-confidence evidence is available", ()
        )

    winners = set(by_source.values())
    if len(winners) > 1:
        return PromotionResolution(
            "tie", "defer", "independent authoritative evidence conflicts", tuple(sorted(by_source))
        )

    verdict = next(iter(winners))
    return PromotionResolution(
        verdict, "clear", "authoritative preference evidence supports promotion", tuple(sorted(by_source))
    )


def evidence_record(
    *, pair_id: str, verdict: str, source_class: str, source_id: str,
    confidence: str = "strong", rationale: str = ""
) -> dict:
    """Stable JSON shape for future queue/ledger artifacts."""
    e = PreferenceEvidence(pair_id, verdict, source_class, source_id, confidence, rationale)
    return {
        "pairId": e.pair_id,
        "verdict": e.verdict,
        "sourceClass": e.source_class,
        "sourceId": e.source_id,
        "confidence": e.confidence,
        "rationale": e.rationale,
        "promotionAuthoritative": e.authoritative,
    }
