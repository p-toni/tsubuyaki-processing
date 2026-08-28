#!/usr/bin/env python3
"""Calibrate dependency-safe triad scheduling through the real queue transports.

This is the integration gate after the pair-matrix transport. The baseline uses
EvidenceAuthoritySelector exactly as screened search does today. The experimental
selector collects unresolved comparisons during one deterministic replay, then
flushes at most two reviewer tasks while preserving proposal order and the current
one-task-per-group policy. Only fixed explore/roundA siblings may be upgraded to a
three-pair triad.

Synthetic outcomes only drive replay and are never artistic evidence.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/'prototypes'/'autonomous-discovery'
sys.path.insert(0,str(PROTO))

from core import TIMES,default_brief,render_candidate_frame
from evidence_selector import EvidenceAuthoritySelector
from pairwise_selector import DimensionVote,PairwiseDecision,PairwiseSelector
from phenotype_evidence_replay import decode_review_phenotype_evidence
from phenotype_preference_evidence import resolve_phenotype_promotion_evidence
from representation_capacity import _generate_route_archive
from review_evidence_queue import create_review_bundle,pair_id_for_phenotypes,phenotype_fingerprint
from search_engine import run_search_from_starts
from triad_pair_matrix_review_queue import (
    PAIR_KEYS,PAIR_LABELS,
    create_triad_pair_matrix_bundle,
    decode_triad_pair_matrix_evidence,
)

ORACLE_ID='synthetic-route-scheduler-oracle-v1'
SEEDS=(7,19,43)
EXPECTED_EAGER_SIGNATURES={
    7:'83aeec36847752f988f436aa6d506f86f06bf6146f56cd20c02d48f716361c55',
    19:'acbe0cbc6801fa71dcce31a8544aed0ed83a042e4a08918f548828964157c4df',
    43:'a2bf05f23ee714ccb9d8801106d48cd3bfa49a529dfdf0dd166833c0daf3e099',
}
SAFE_TRIAD_STAGES={'explore','roundA'}


def _brief_text(brief):
    return str(brief.get('artistic_intent') or brief.get('brief') or brief.get('description') or brief.get('name') or '')


def _oracle_winner(brief_text,afp,bfp):
    pid=pair_id_for_phenotypes(brief=brief_text,times=TIMES,a_fingerprint=afp,b_fingerprint=bfp)
    h=int(hashlib.sha256((ORACLE_ID+':'+pid).encode()).hexdigest(),16)
    if h%7==0: return None
    return sorted((afp,bfp))[(h>>3)&1]


def _brief():
    base=default_brief()
    return {**base,'routes':['recurrence','family','sheet'],'explore_per_basin':4,'roundA_per_survivor':1,'total_extra_budget':3}


def _starts(brief,seed):
    starts=[]
    for route in brief['routes']:
        cands,_=_generate_route_archive(brief,seed,route,1)
        if len(cands)!=1: raise AssertionError(f'{route} did not yield one valid start')
        starts.extend(cands)
    return starts


def _signature(state,report):
    payload={
        'candidates':[{
            'id':c.id,'route':c.route,'basin':c.basin,'parent':c.parent_id,
            'stage':c.stage,'genome':c.genome,'valid':bool(c.checks.get('valid',False)),
        } for c in sorted(state.candidates.values(),key=lambda x:x.id)],
        'winner':report.get('winner'),'provisionalChampion':report.get('provisionalChampion'),
        'selectionStatus':report.get('selectionStatus'),
        'frontier':sorted(report.get('artisticFrontier',[])),'allocations':report.get('allocations',{}),
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _load_pair_evidence(queue_dir):
    q=Path(queue_dir)
    if not (q/'sealed-mapping.json').exists() or not (q/'decisions.json').exists(): return []
    return decode_review_phenotype_evidence(q)


def _load_triad_evidence(queue_dir):
    if queue_dir is None: return []
    q=Path(queue_dir)
    if not (q/'sealed-mapping.json').exists() or not (q/'decisions.json').exists(): return []
    return decode_triad_pair_matrix_evidence(q)


def _pending_pair_ids(queue):
    path=Path(queue)/'decisions.json'
    if not path.exists(): return []
    doc=json.loads(path.read_text())
    return [pid for pid,item in doc.get('decisions',{}).items() if item.get('verdict') is None]


def _pending_triad_ids(queue):
    if queue is None: return []
    path=Path(queue)/'decisions.json'
    if not path.exists(): return []
    doc=json.loads(path.read_text())
    out=[]
    for tid,item in doc.get('decisions',{}).items():
        verdicts=item.get('pairVerdicts',{})
        if verdicts and all(v is None for v in verdicts.values()): out.append(tid)
    return out


def _resolve_pair_pending(queue):
    pending=_pending_pair_ids(queue)
    if not pending: return []
    root=Path(queue); sealed=json.loads((root/'sealed-mapping.json').read_text()); qdoc=json.loads((root/'queue.json').read_text()); decisions=json.loads((root/'decisions.json').read_text())
    resolved=[]
    for pid in pending:
        mapping=sealed['pairs'][pid]; task=qdoc['pairs'][pid]
        afp=mapping['A']['phenotypeFingerprint']; bfp=mapping['B']['phenotypeFingerprint']
        winner=_oracle_winner(task['brief'],afp,bfp)
        verdict='tie' if winner is None else ('A' if winner==afp else 'B')
        decisions['decisions'][pid].update(
            verdict=verdict,sourceClass='independent-model',sourceId=ORACLE_ID,
            confidence='strong',rationale='synthetic queue replay oracle; not artistic evidence',
        )
        resolved.append(pid)
    (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
    return resolved


def _resolve_triad_pending(queue):
    pending=_pending_triad_ids(queue)
    if not pending: return []
    root=Path(queue); sealed=json.loads((root/'sealed-mapping.json').read_text()); qdoc=json.loads((root/'queue.json').read_text()); decisions=json.loads((root/'decisions.json').read_text())
    resolved=[]
    for tid in pending:
        mapping=sealed['triads'][tid]; task=qdoc['triads'][tid]
        verdicts={}
        for key in PAIR_KEYS:
            left,right=PAIR_LABELS[key]
            lfp=mapping[left]['phenotypeFingerprint']; rfp=mapping[right]['phenotypeFingerprint']
            winner=_oracle_winner(task['brief'],lfp,rfp)
            verdicts[key]='tie' if winner is None else (left if winner==lfp else right)
        decisions['decisions'][tid].update(
            pairVerdicts=verdicts,sourceClass='independent-model',sourceId=ORACLE_ID,
            confidence='strong',rationale='synthetic queue replay oracle; not artistic evidence',
        )
        resolved.append(tid)
    (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
    return resolved


def _pair_group(queue,pid):
    sealed=json.loads((Path(queue)/'sealed-mapping.json').read_text())
    return sealed.get('reviewGroups',{}).get(pid)


def _triad_group(queue,tid):
    sealed=json.loads((Path(queue)/'sealed-mapping.json').read_text())
    return sealed.get('reviewGroups',{}).get(tid)


@dataclass(frozen=True)
class Proposal:
    index:int
    pair_id:str
    brief_text:str
    a_id:str
    b_id:str
    afp:str
    bfp:str
    a_frames:tuple
    b_frames:tuple
    a_route:str
    b_route:str
    a_stage:str
    b_stage:str
    a_parent:str|None
    b_parent:str|None

    @property
    def group(self):
        if self.a_route==self.b_route: return f'route:{self.a_route}'
        return 'cross:'+('|'.join(sorted((self.a_route,self.b_route))))


class FileBackedProposalSelector(PairwiseSelector):
    """Collect unresolved proposals; resolved evidence still promotes normally."""
    name='file-backed-triad-proposal-selector-v1'
    def __init__(self,*,pair_queue,triad_queue=None):
        self.pair_queue=Path(pair_queue); self.triad_queue=Path(triad_queue) if triad_queue is not None else None
        self.evidence=_load_pair_evidence(self.pair_queue)+_load_triad_evidence(self.triad_queue)
        self.proposals=[]; self._seen=set(); self._frame_cache={}

    def _frames(self,cand):
        genome=json.dumps(getattr(cand,'genome',{}),sort_keys=True,separators=(',',':'),default=str)
        key=(cand.id,genome)
        if key not in self._frame_cache:
            self._frame_cache[key]=tuple(render_candidate_frame(cand,t) for t in TIMES)
        return self._frame_cache[key]

    def compare(self,a,b,brief):
        av=bool(a.checks.get('valid',False)); bv=bool(b.checks.get('valid',False))
        if av!=bv:
            verdict='a' if av else 'b'
            return PairwiseDecision(a.id,b.id,verdict,'clear',(DimensionVote('route-validity',verdict,'hard validity'),),self.name+':hard-validity')
        if not av and not bv:
            return PairwiseDecision(a.id,b.id,'tie','defer',(DimensionVote('route-validity','tie','both invalid'),),self.name+':hard-validity')
        afr=self._frames(a); bfr=self._frames(b); afp=phenotype_fingerprint(afr); bfp=phenotype_fingerprint(bfr)
        if afp==bfp:
            return PairwiseDecision(a.id,b.id,'tie','clear',(DimensionVote('phenotype','tie','identical phenotype'),),self.name)
        bt=_brief_text(brief); pid=pair_id_for_phenotypes(brief=bt,times=TIMES,a_fingerprint=afp,b_fingerprint=bfp)
        resolution=resolve_phenotype_promotion_evidence(self.evidence,pair_id=pid)
        if resolution.confidence=='clear':
            if resolution.winner_fingerprint==afp: verdict='a'
            elif resolution.winner_fingerprint==bfp: verdict='b'
            else: verdict='tie'
            return PairwiseDecision(a.id,b.id,verdict,'clear',(DimensionVote('phenotype-evidence',verdict,resolution.reason),),self.name)
        if pid not in self._seen and resolution.review_needed:
            self._seen.add(pid)
            self.proposals.append(Proposal(
                len(self.proposals),pid,bt,a.id,b.id,afp,bfp,afr,bfr,
                str(a.route),str(b.route),str(getattr(a,'stage','')),str(getattr(b,'stage','')),
                getattr(a,'parent_id',None),getattr(b,'parent_id',None),
            ))
        return PairwiseDecision(a.id,b.id,'tie','defer',(DimensionVote('promotion-authority','tie',resolution.reason),),self.name)

    def _safe_sibling(self,p):
        return p.a_route==p.b_route and p.b_stage in SAFE_TRIAD_STAGES and p.b_parent==p.a_id

    def _triad_for(self,p,unresolved,resolved_pair_ids):
        if self.triad_queue is None or not self._safe_sibling(p): return None
        for q in unresolved:
            if q.index<=p.index: continue
            if q.group!=p.group or q.a_id!=p.a_id or q.afp!=p.afp: continue
            if q.b_stage!=p.b_stage or not self._safe_sibling(q): continue
            if q.b_id==p.b_id or q.bfp==p.bfp: continue
            bc=pair_id_for_phenotypes(brief=p.brief_text,times=TIMES,a_fingerprint=p.bfp,b_fingerprint=q.bfp)
            ids={p.pair_id,q.pair_id,bc}
            if ids & resolved_pair_ids: continue
            return p,q,bc
        return None

    def flush(self,*,enable_triads,max_tasks=2):
        if _pending_pair_ids(self.pair_queue) or _pending_triad_ids(self.triad_queue):
            return []
        resolved_pair_ids={ev.pair_id for ev in self.evidence if ev.authoritative}
        unresolved=[p for p in self.proposals if p.pair_id not in resolved_pair_ids]
        selected=[]; used_groups=set(); covered=set()
        for p in unresolved:
            if len(selected)>=max_tasks: break
            if p.pair_id in covered or p.group in used_groups: continue
            triad=self._triad_for(p,unresolved,resolved_pair_ids) if enable_triads else None
            if triad is not None:
                first,second,bc=triad
                task_id=create_triad_pair_matrix_bundle(
                    self.triad_queue,brief=p.brief_text,times=TIMES,
                    a_frames=first.a_frames,b_frames=first.b_frames,c_frames=second.b_frames,
                    a_candidate_id=first.a_id,b_candidate_id=first.b_id,c_candidate_id=second.b_id,
                    review_group=p.group,
                )
                covered.update((first.pair_id,second.pair_id,bc)); used_groups.add(p.group)
                selected.append({'kind':'triad','id':task_id,'group':p.group,'pairIds':sorted((first.pair_id,second.pair_id,bc))})
                continue
            created=create_review_bundle(
                self.pair_queue,brief=p.brief_text,times=TIMES,
                a_frames=p.a_frames,b_frames=p.b_frames,a_candidate_id=p.a_id,b_candidate_id=p.b_id,
                review_group=p.group,
            )
            if created!=p.pair_id: raise RuntimeError('pair queue id drift')
            covered.add(p.pair_id); used_groups.add(p.group)
            selected.append({'kind':'pair','id':p.pair_id,'group':p.group,'pairIds':[p.pair_id]})
        return selected


def _task_counts(pair_queue,triad_queue=None):
    pair_path=Path(pair_queue)/'decisions.json'; triad_path=Path(triad_queue)/'decisions.json' if triad_queue is not None else None
    pairs=len(json.loads(pair_path.read_text()).get('decisions',{})) if pair_path.exists() else 0
    triads=len(json.loads(triad_path.read_text()).get('decisions',{})) if triad_path is not None and triad_path.exists() else 0
    return pairs,triads


def _baseline_current_group_k2(brief,seed,max_replays=80):
    with TemporaryDirectory() as td:
        root=Path(td); pairq=root/'pairs'; out=root/'search'; rounds=0; replays=0; batches=[]; state=report=None
        while replays<max_replays:
            replays+=1
            selector=EvidenceAuthoritySelector(
                render_frame=render_candidate_frame,times=TIMES,queue_dir=pairq,
                max_pending_reviews=2,max_pending_reviews_per_group=1,
            )
            state,report=run_search_from_starts(brief,seed,out,_starts(brief,seed),selector)
            pending=_pending_pair_ids(pairq)
            if not pending: break
            batches.append([{'kind':'pair','id':pid,'group':_pair_group(pairq,pid)} for pid in pending])
            _resolve_pair_pending(pairq); rounds+=1
        else: raise AssertionError('current-group-k2 did not converge')
        pairs,_=_task_counts(pairq)
        return {
            'policy':'current-group-k2','reviewTasks':pairs,'reviewRounds':rounds,'searchReplays':replays,
            'candidateExposures':pairs*2,'pairRelationsElicited':pairs,'pairTasks':pairs,'triadTasks':0,
            'batches':batches,'trajectorySignature':_signature(state,report),'winner':report.get('winner'),
        }


def _proposal_policy(brief,seed,*,enable_triads,max_replays=80):
    name='matrix-triad-file-k2' if enable_triads else 'collector-pair-k2'
    with TemporaryDirectory() as td:
        root=Path(td); pairq=root/'pairs'; triadq=root/'triads' if enable_triads else None; out=root/'search'; rounds=0; replays=0; batches=[]; state=report=None
        while replays<max_replays:
            replays+=1
            selector=FileBackedProposalSelector(pair_queue=pairq,triad_queue=triadq)
            state,report=run_search_from_starts(brief,seed,out,_starts(brief,seed),selector)
            selected=selector.flush(enable_triads=enable_triads,max_tasks=2)
            if not selected: break
            batches.append(selected)
            _resolve_pair_pending(pairq)
            if triadq is not None: _resolve_triad_pending(triadq)
            rounds+=1
        else: raise AssertionError(f'{name} did not converge')
        pairs,triads=_task_counts(pairq,triadq)
        return {
            'policy':name,'reviewTasks':pairs+triads,'reviewRounds':rounds,'searchReplays':replays,
            'candidateExposures':pairs*2+triads*3,'pairRelationsElicited':pairs+triads*3,
            'pairTasks':pairs,'triadTasks':triads,'batches':batches,
            'trajectorySignature':_signature(state,report),'winner':report.get('winner'),
        }


def run_seed(seed):
    brief=_brief()
    current=_baseline_current_group_k2(brief,seed)
    collector=_proposal_policy(brief,seed,enable_triads=False)
    triad=_proposal_policy(brief,seed,enable_triads=True)
    expected=EXPECTED_EAGER_SIGNATURES[seed]
    for row in (current,collector,triad):
        if row['trajectorySignature']!=expected:
            raise AssertionError(f"trajectory divergence seed={seed} policy={row['policy']}")
    current_batches=[[item['id'] for item in batch] for batch in current['batches']]
    collector_batches=[[item['id'] for item in batch] for batch in collector['batches']]
    if current_batches!=collector_batches:
        raise AssertionError(f'collector pair-only queue selection drift seed={seed}')
    return {'version':1,'seed':seed,'expectedEagerTrajectorySignature':expected,'policies':[current,collector,triad]}


def main():
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--seed',type=int,required=True); args=parser.parse_args()
    print(json.dumps(run_seed(args.seed),indent=2))

if __name__=='__main__': main()
