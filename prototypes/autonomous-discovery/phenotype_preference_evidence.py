"""Order-independent phenotype preference evidence for artistic promotion."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional

VALID_CONFIDENCE={"strong","low","defer"}
VALID_SOURCE_CLASS={"human","independent-model","same-model","deterministic-proxy"}
AUTHORITATIVE_SOURCE_CLASS={"human","independent-model"}

@dataclass(frozen=True)
class PhenotypePreferenceEvidence:
    pair_id:str
    phenotype_fingerprints:tuple[str,str]
    winner_fingerprint:str|None
    source_class:str
    source_id:str
    confidence:str="strong"
    rationale:str=""
    def __post_init__(self):
        pair=tuple(sorted(self.phenotype_fingerprints))
        if len(pair)!=2 or not all(pair): raise ValueError("exactly two phenotype fingerprints are required")
        object.__setattr__(self,"phenotype_fingerprints",pair)
        if self.winner_fingerprint is not None and self.winner_fingerprint not in pair:
            raise ValueError("winner fingerprint must belong to the phenotype pair")
        if self.source_class not in VALID_SOURCE_CLASS: raise ValueError(f"invalid source class: {self.source_class}")
        if self.confidence not in VALID_CONFIDENCE: raise ValueError(f"invalid confidence: {self.confidence}")
        if not self.pair_id or not self.source_id: raise ValueError("pair_id and source_id are required")
    @property
    def authoritative(self)->bool:
        return self.source_class in AUTHORITATIVE_SOURCE_CLASS and self.confidence=="strong" and self.winner_fingerprint is not None

@dataclass(frozen=True)
class PhenotypePromotionResolution:
    winner_fingerprint:str|None
    confidence:str
    reason:str
    authoritative_sources:tuple[str,...]

def resolve_phenotype_promotion_evidence(evidence:Iterable[PhenotypePreferenceEvidence],*,pair_id:Optional[str]=None)->PhenotypePromotionResolution:
    items=list(evidence)
    if pair_id is not None: items=[e for e in items if e.pair_id==pair_id]
    if not items: return PhenotypePromotionResolution(None,"defer","no phenotype preference evidence",())
    pair_ids={e.pair_id for e in items}
    if len(pair_ids)!=1: raise ValueError("all evidence must refer to one phenotype pair")
    pairs={e.phenotype_fingerprints for e in items}
    if len(pairs)!=1: raise ValueError("evidence for one pair_id disagrees on phenotype fingerprints")
    by_source={}
    for e in items:
        if not e.authoritative: continue
        prev=by_source.get(e.source_id)
        if prev is not None and prev!=e.winner_fingerprint:
            return PhenotypePromotionResolution(None,"defer","one authoritative source issued conflicting clear winners",tuple(sorted(by_source)))
        by_source[e.source_id]=e.winner_fingerprint
    if not by_source:
        return PhenotypePromotionResolution(None,"defer","only advisory, tie, or low-confidence evidence is available",())
    winners=set(by_source.values())
    if len(winners)!=1:
        return PhenotypePromotionResolution(None,"defer","independent authoritative evidence conflicts",tuple(sorted(by_source)))
    return PhenotypePromotionResolution(next(iter(winners)),"clear","authoritative phenotype evidence supports promotion",tuple(sorted(by_source)))
