"""Pairwise selector whose artistic promotions require authoritative phenotype evidence."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Mapping,Optional,Sequence
from pairwise_selector import DimensionVote,PairwiseDecision,PairwiseSelector
from phenotype_preference_evidence import resolve_phenotype_promotion_evidence
from phenotype_evidence_replay import decode_review_phenotype_evidence
from review_evidence_queue import PROMPT_VERSION,create_review_bundle,phenotype_fingerprint


def _brief_text(brief:Mapping[str,object])->str:
    return str(brief.get('artistic_intent') or brief.get('brief') or brief.get('description') or brief.get('name') or '')

def _pair_id(brief_text:str,times,afp:str,bfp:str)->str:
    config={'promptVersion':PROMPT_VERSION,'brief':brief_text,'times':list(times),'phenotypes':sorted((afp,bfp))}
    return hashlib.sha256(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class EvidenceAuthoritySelector(PairwiseSelector):
    """Advisory judges can triage; only strong human/independent evidence can promote."""
    name='phenotype-evidence-authority-v1'
    def __init__(self,*,render_frame,times:Sequence[float],evidence_dirs:Sequence[Path]=(),queue_dir:Optional[Path]=None,advisory:Optional[PairwiseSelector]=None):
        self.render_frame=render_frame; self.times=tuple(times); self.queue_dir=Path(queue_dir) if queue_dir else None; self.advisory=advisory
        self.evidence=[]
        for d in evidence_dirs: self.evidence.extend(decode_review_phenotype_evidence(Path(d)))
    def _frames(self,cand): return [self.render_frame(cand,t) for t in self.times]
    def compare(self,a,b,brief:Mapping[str,object])->PairwiseDecision:
        av=bool(a.checks.get('valid',False)); bv=bool(b.checks.get('valid',False))
        if av!=bv:
            verdict='a' if av else 'b'
            return PairwiseDecision(a.id,b.id,verdict,'clear',(DimensionVote('route-validity',verdict,'invalid candidate cannot win artistic promotion',av,bv),),self.name+':hard-validity')
        if not av and not bv:
            return PairwiseDecision(a.id,b.id,'tie','defer',(DimensionVote('route-validity','tie','both candidates invalid',av,bv),),self.name+':hard-validity')
        a_frames=self._frames(a); b_frames=self._frames(b)
        afp=phenotype_fingerprint(a_frames); bfp=phenotype_fingerprint(b_frames)
        if afp==bfp:
            return PairwiseDecision(a.id,b.id,'tie','defer',(DimensionVote('phenotype-evidence','tie','visible phenotypes are identical'),),self.name)
        brief_text=_brief_text(brief); pair_id=_pair_id(brief_text,self.times,afp,bfp)
        resolution=resolve_phenotype_promotion_evidence(self.evidence,pair_id=pair_id)
        if resolution.confidence=='clear':
            if resolution.winner_fingerprint==afp: verdict='a'
            elif resolution.winner_fingerprint==bfp: verdict='b'
            else: verdict='tie'
            if verdict!='tie':
                return PairwiseDecision(a.id,b.id,verdict,'clear',(DimensionVote('phenotype-evidence',verdict,resolution.reason,resolution.authoritative_sources,resolution.winner_fingerprint),),self.name)
        if self.queue_dir is not None:
            create_review_bundle(self.queue_dir,brief=brief_text,times=self.times,a_frames=a_frames,b_frames=b_frames,a_candidate_id=a.id,b_candidate_id=b.id)
        advisory=self.advisory.compare(a,b,brief) if self.advisory is not None else None
        reason=resolution.reason
        dims=[DimensionVote('promotion-authority','tie',reason)]
        if advisory is not None:
            dims.append(DimensionVote('advisory-only',advisory.verdict,f'{advisory.source} suggestion is non-authoritative'))
        return PairwiseDecision(a.id,b.id,'tie','defer',tuple(dims),self.name)
