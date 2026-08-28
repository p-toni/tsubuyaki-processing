"""Pairwise selector whose artistic promotions require authoritative phenotype evidence."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Mapping,Optional,Sequence
from pairwise_selector import DimensionVote,PairwiseDecision,PairwiseSelector
from phenotype_preference_evidence import resolve_phenotype_promotion_evidence
from phenotype_evidence_replay import decode_review_phenotype_evidence
from review_evidence_queue import create_review_bundle,pair_id_for_phenotypes,phenotype_fingerprint


def _brief_text(brief:Mapping[str,object])->str:
    return str(brief.get('artistic_intent') or brief.get('brief') or brief.get('description') or brief.get('name') or '')

def _pair_id(brief_text:str,times,afp:str,bfp:str)->str:
    return pair_id_for_phenotypes(
        brief=brief_text,times=times,a_fingerprint=afp,b_fingerprint=bfp,
    )

class EvidenceAuthoritySelector(PairwiseSelector):
    """Advisory judges can triage; only strong human/independent evidence can promote.

    ``max_pending_reviews`` bounds speculative human work. ``max_pending_reviews_per_group``
    can additionally reserve a lazy batch for diverse scheduling groups (normally
    routes) without changing comparison order or promotion semantics. Group labels
    are sealed from the artistic reviewer and survive deterministic replay.
    """
    name='phenotype-evidence-authority-v1'
    def __init__(self,*,render_frame,times:Sequence[float],evidence_dirs:Sequence[Path]=(),queue_dir:Optional[Path]=None,advisory:Optional[PairwiseSelector]=None,max_pending_reviews:Optional[int]=None,max_pending_reviews_per_group:Optional[int]=None):
        self.render_frame=render_frame; self.times=tuple(times); self.queue_dir=Path(queue_dir) if queue_dir else None; self.advisory=advisory
        if max_pending_reviews is not None and max_pending_reviews<1: raise ValueError('max_pending_reviews must be >= 1 or None')
        if max_pending_reviews_per_group is not None and max_pending_reviews_per_group<1: raise ValueError('max_pending_reviews_per_group must be >= 1 or None')
        self.max_pending_reviews=max_pending_reviews; self.max_pending_reviews_per_group=max_pending_reviews_per_group
        self.evidence=[]; loaded=set()
        for d in evidence_dirs:
            p=Path(d)
            self.evidence.extend(decode_review_phenotype_evidence(p)); loaded.add(p.resolve())
        self.pending_review_ids=set(); self.queue_pair_ids=set(); self.pending_review_groups={}
        if self.queue_dir is not None:
            decisions_path=self.queue_dir/'decisions.json'; sealed_path=self.queue_dir/'sealed-mapping.json'
            if decisions_path.exists() and sealed_path.exists():
                if self.queue_dir.resolve() not in loaded:
                    self.evidence.extend(decode_review_phenotype_evidence(self.queue_dir))
                decisions=json.loads(decisions_path.read_text()); sealed=json.loads(sealed_path.read_text())
                items=decisions.get('decisions',{})
                self.queue_pair_ids=set(items)
                self.pending_review_ids={pid for pid,item in items.items() if item.get('verdict') is None}
                groups=sealed.get('reviewGroups',{})
                self.pending_review_groups={pid:groups[pid] for pid in self.pending_review_ids if groups.get(pid)}
    def _frames(self,cand): return [self.render_frame(cand,t) for t in self.times]
    def _review_group(self,a,b,brief:Mapping[str,object])->str|None:
        if self.max_pending_reviews_per_group is None: return None
        routes=tuple(dict.fromkeys(brief.get('routes') or ()))
        if len(routes)<2: return None
        ar=getattr(a,'route',None); br=getattr(b,'route',None)
        if not ar or not br: return None
        return f'route:{ar}' if ar==br else 'cross:'+('|'.join(sorted((str(ar),str(br)))))
    def _can_queue(self,pair_id:str,review_group:str|None)->bool:
        if self.queue_dir is None or pair_id in self.queue_pair_ids: return False
        if self.max_pending_reviews is not None and len(self.pending_review_ids)>=self.max_pending_reviews: return False
        if review_group is not None and self.max_pending_reviews_per_group is not None:
            n=sum(group==review_group for group in self.pending_review_groups.values())
            if n>=self.max_pending_reviews_per_group: return False
        return True
    def _queue(self,*,pair_id,brief_text,a_frames,b_frames,a_id,b_id,review_group)->bool:
        if not self._can_queue(pair_id,review_group): return False
        created=create_review_bundle(self.queue_dir,brief=brief_text,times=self.times,a_frames=a_frames,b_frames=b_frames,a_candidate_id=a_id,b_candidate_id=b_id,review_group=review_group)
        if created!=pair_id: raise RuntimeError('review bundle pair id drift')
        self.queue_pair_ids.add(pair_id)
        decisions=json.loads((self.queue_dir/'decisions.json').read_text())
        if decisions['decisions'][pair_id].get('verdict') is None:
            self.pending_review_ids.add(pair_id)
            if review_group is not None: self.pending_review_groups[pair_id]=review_group
        return True
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
            return PairwiseDecision(a.id,b.id,'tie','clear',(DimensionVote('phenotype-evidence','tie','visible phenotypes are identical'),),self.name)
        brief_text=_brief_text(brief); pair_id=_pair_id(brief_text,self.times,afp,bfp)
        resolution=resolve_phenotype_promotion_evidence(self.evidence,pair_id=pair_id)
        if resolution.confidence=='clear':
            if resolution.winner_fingerprint==afp: verdict='a'
            elif resolution.winner_fingerprint==bfp: verdict='b'
            else: verdict='tie'
            return PairwiseDecision(a.id,b.id,verdict,'clear',(DimensionVote('phenotype-evidence',verdict,resolution.reason,resolution.authoritative_sources,resolution.winner_fingerprint),),self.name)
        queued=False; review_group=self._review_group(a,b,brief)
        if resolution.review_needed:
            queued=self._queue(pair_id=pair_id,brief_text=brief_text,a_frames=a_frames,b_frames=b_frames,a_id=a.id,b_id=b.id,review_group=review_group)
        advisory=self.advisory.compare(a,b,brief) if self.advisory is not None else None
        reason=resolution.reason
        if resolution.review_needed and self.queue_dir is not None and not queued:
            if pair_id in self.pending_review_ids:
                reason+='; review is already pending'
            elif pair_id in self.queue_pair_ids:
                reason+='; existing queue evidence is non-authoritative, so additional evidence must come from a new independent review bundle'
            elif review_group is not None and self.max_pending_reviews_per_group is not None and sum(group==review_group for group in self.pending_review_groups.values())>=self.max_pending_reviews_per_group:
                reason+='; review deferred behind the pending-review group cap'
            else:
                reason+='; review deferred behind the pending-review cap'
        dims=[DimensionVote('promotion-authority','tie',reason)]
        if advisory is not None:
            dims.append(DimensionVote('advisory-only',advisory.verdict,f'{advisory.source} suggestion is non-authoritative'))
        return PairwiseDecision(a.id,b.id,'tie','defer',tuple(dims),self.name)
