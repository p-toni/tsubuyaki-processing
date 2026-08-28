#!/usr/bin/env python3
"""Calibrate dependency-safe triad review on the real adaptive search.

A triad is allowed only when two unresolved comparisons share one incumbent and
both challengers are already-fixed siblings from explore/roundA. Refine is never
packed because later candidate generation can depend on an earlier promotion.

Synthetic outcomes drive convergence only; they are not artistic evidence.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/'prototypes'/'autonomous-discovery'
sys.path.insert(0,str(PROTO))

from core import TIMES,default_brief,render_candidate_frame
from pairwise_selector import DimensionVote,PairwiseDecision,PairwiseSelector
from representation_capacity import _generate_route_archive
from review_evidence_queue import PROMPT_VERSION,phenotype_fingerprint
from search_engine import run_search_from_starts

# Reuse the exact pairwise oracle from route-balanced-review-v1 so the existing
# eager trajectory signatures remain a frozen comparison target.
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


def _pair_id(brief_text,times,afp,bfp):
    config={'promptVersion':PROMPT_VERSION,'brief':brief_text,'times':list(times),'phenotypes':sorted((afp,bfp))}
    return hashlib.sha256(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _oracle_winner(brief_text,afp,bfp):
    """Return winning phenotype fingerprint or None for tie."""
    pid=_pair_id(brief_text,TIMES,afp,bfp)
    h=int(hashlib.sha256((ORACLE_ID+':'+pid).encode()).hexdigest(),16)
    if h%7==0:
        return None
    ordered=sorted((afp,bfp))
    return ordered[(h>>3)&1]


def _pair_outcome(brief_text,left,right):
    winner=_oracle_winner(brief_text,left,right)
    if winner is None: return 'tie'
    return 'left' if winner==left else 'right'


def weak_orders(labels=('A','B','C')):
    """All 13 ordered partitions / total preorders of three labels."""
    labels=tuple(labels); out=[]
    for ranks in itertools.product(range(len(labels)),repeat=len(labels)):
        used=set(ranks)
        if used!=set(range(max(ranks)+1)):
            continue
        tiers=[]
        for rank in range(max(ranks)+1):
            tiers.append(tuple(labels[i] for i,r in enumerate(ranks) if r==rank))
        out.append(tuple(tiers))
    return tuple(out)


def outcomes_for_order(order):
    rank={label:i for i,tier in enumerate(order) for label in tier}
    out={}
    for a,b in itertools.combinations(('A','B','C'),2):
        out[(a,b)]='tie' if rank[a]==rank[b] else (a if rank[a]<rank[b] else b)
    return out


def order_for_outcomes(outcomes):
    matches=[]
    for order in weak_orders():
        if outcomes_for_order(order)==outcomes:
            matches.append(order)
    if len(matches)>1:
        raise AssertionError('weak-order decoding is ambiguous')
    return matches[0] if matches else None


@dataclass(frozen=True)
class Proposal:
    index:int
    pair_id:str
    brief_text:str
    a_id:str
    b_id:str
    afp:str
    bfp:str
    a_route:str
    b_route:str
    a_stage:str
    b_stage:str
    a_parent:str|None
    b_parent:str|None

    @property
    def group(self):
        if self.a_route==self.b_route:
            return f'route:{self.a_route}'
        return 'cross:'+('|'.join(sorted((self.a_route,self.b_route))))


class ProposalSelector(PairwiseSelector):
    name='triad-review-proposal-selector-v1'
    def __init__(self,evidence):
        self.evidence=dict(evidence)
        self.proposals=[]; self._seen=set(); self._fp_cache={}

    def _fp(self,cand):
        genome=json.dumps(getattr(cand,'genome',{}),sort_keys=True,separators=(',',':'),default=str)
        key=(cand.id,genome)
        if key not in self._fp_cache:
            frames=[render_candidate_frame(cand,t) for t in TIMES]
            self._fp_cache[key]=phenotype_fingerprint(frames)
        return self._fp_cache[key]

    def compare(self,a,b,brief):
        av=bool(a.checks.get('valid',False)); bv=bool(b.checks.get('valid',False))
        if av!=bv:
            verdict='a' if av else 'b'
            return PairwiseDecision(a.id,b.id,verdict,'clear',(DimensionVote('route-validity',verdict,'hard validity'),),self.name+':hard-validity')
        if not av and not bv:
            return PairwiseDecision(a.id,b.id,'tie','defer',(DimensionVote('route-validity','tie','both invalid'),),self.name+':hard-validity')
        afp=self._fp(a); bfp=self._fp(b)
        if afp==bfp:
            return PairwiseDecision(a.id,b.id,'tie','clear',(DimensionVote('phenotype','tie','identical phenotype'),),self.name)
        bt=_brief_text(brief); pid=_pair_id(bt,TIMES,afp,bfp)
        if pid in self.evidence:
            winner=self.evidence[pid]
            verdict='tie' if winner is None else ('a' if winner==afp else 'b')
            return PairwiseDecision(a.id,b.id,verdict,'clear',(DimensionVote('synthetic-evidence',verdict,'experiment replay evidence only'),),self.name)
        if pid not in self._seen:
            self._seen.add(pid)
            self.proposals.append(Proposal(
                len(self.proposals),pid,bt,a.id,b.id,afp,bfp,str(a.route),str(b.route),
                str(getattr(a,'stage','')),str(getattr(b,'stage','')),
                getattr(a,'parent_id',None),getattr(b,'parent_id',None),
            ))
        return PairwiseDecision(a.id,b.id,'tie','defer',(DimensionVote('synthetic-evidence','tie','unresolved experiment proposal'),),self.name)


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
        'candidates':[{ 'id':c.id,'route':c.route,'basin':c.basin,'parent':c.parent_id,'stage':c.stage,'genome':c.genome,'valid':bool(c.checks.get('valid',False)) } for c in sorted(state.candidates.values(),key=lambda x:x.id)],
        'winner':report.get('winner'),'provisionalChampion':report.get('provisionalChampion'),'selectionStatus':report.get('selectionStatus'),
        'frontier':sorted(report.get('artisticFrontier',[])),'allocations':report.get('allocations',{}),
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _safe_sibling_pair(p):
    return (
        p.a_route==p.b_route and
        p.b_stage in SAFE_TRIAD_STAGES and
        p.b_parent==p.a_id
    )


def _triad_opportunities(proposals):
    """Return rankable dependency-safe triads, ordered by earliest pair proposal."""
    by_inc={}
    for p in proposals:
        if _safe_sibling_pair(p):
            by_inc.setdefault((p.a_id,p.afp,p.b_stage,p.a_route),[]).append(p)
    opportunities=[]
    for key,items in by_inc.items():
        items=sorted(items,key=lambda p:p.index)
        for p,q in itertools.combinations(items,2):
            if p.b_id==q.b_id or p.bfp==q.bfp: continue
            labels={'A':p.afp,'B':p.bfp,'C':q.bfp}
            outcomes={}
            for x,y in itertools.combinations(('A','B','C'),2):
                winner=_oracle_winner(p.brief_text,labels[x],labels[y])
                outcomes[(x,y)]='tie' if winner is None else (x if winner==labels[x] else y)
            order=order_for_outcomes(outcomes)
            if order is None:
                continue
            pair_ids={
                tuple(sorted((x,y))):_pair_id(p.brief_text,TIMES,labels[x],labels[y])
                for x,y in itertools.combinations(('A','B','C'),2)
            }
            opportunities.append({
                'index':min(p.index,q.index),'group':p.group,'proposals':(p,q),
                'labels':labels,'order':order,'pairIds':pair_ids,
            })
            break
    return sorted(opportunities,key=lambda x:x['index'])


def _resolve_pair_task(p,evidence):
    evidence[p.pair_id]=_oracle_winner(p.brief_text,p.afp,p.bfp)
    return {'kind':'pair','group':p.group,'candidateExposures':2,'relations':1,'proposalIndex':p.index}


def _resolve_triad_task(t,evidence):
    labels=t['labels']; rank={label:i for i,tier in enumerate(t['order']) for label in tier}
    for x,y in itertools.combinations(('A','B','C'),2):
        pid=t['pairIds'][tuple(sorted((x,y)))]
        evidence[pid]=None if rank[x]==rank[y] else labels[x if rank[x]<rank[y] else y]
    return {'kind':'triad','group':t['group'],'candidateExposures':3,'relations':3,'proposalIndex':t['index']}


def _select_tasks(proposals,evidence,policy,max_tasks=2):
    unresolved=[p for p in proposals if p.pair_id not in evidence]
    triads=_triad_opportunities(unresolved) if policy=='triad-k2' else []
    triad_by_index={t['index']:t for t in triads}
    selected=[]; used_groups=set(); covered=set()
    for p in unresolved:
        if len(selected)>=max_tasks: break
        if p.pair_id in covered or p.group in used_groups: continue
        t=triad_by_index.get(p.index)
        if t is not None:
            tids=set(t['pairIds'].values())
            if not tids & covered:
                selected.append(('triad',t)); used_groups.add(t['group']); covered.update(tids); continue
        selected.append(('pair',p)); used_groups.add(p.group); covered.add(p.pair_id)
    return selected


def run_policy(brief,seed,policy,max_replays=80):
    evidence={}; rounds=0; replays=0; task_log=[]; final_state=final_report=None
    with TemporaryDirectory() as td:
        out=Path(td)/'search'
        while replays<max_replays:
            replays+=1
            selector=ProposalSelector(evidence)
            final_state,final_report=run_search_from_starts(brief,seed,out,_starts(brief,seed),selector)
            proposals=[p for p in selector.proposals if p.pair_id not in evidence]
            if not proposals:
                break
            tasks=_select_tasks(proposals,evidence,policy,max_tasks=2)
            if not tasks:
                raise AssertionError(f'{policy} produced unresolved proposals but no review task')
            round_items=[]
            for kind,item in tasks:
                round_items.append(_resolve_triad_task(item,evidence) if kind=='triad' else _resolve_pair_task(item,evidence))
            task_log.append(round_items); rounds+=1
        else:
            raise AssertionError(f'{policy} did not converge')
    signature=_signature(final_state,final_report)
    if signature!=EXPECTED_EAGER_SIGNATURES[seed]:
        raise AssertionError(f'trajectory divergence seed={seed} policy={policy}: {signature}')
    flat=[t for r in task_log for t in r]
    return {
        'policy':policy,'reviewTasks':len(flat),'reviewRounds':rounds,'searchReplays':replays,
        'candidateExposures':sum(t['candidateExposures'] for t in flat),
        'pairRelationsElicited':sum(t['relations'] for t in flat),
        'triadTasks':sum(t['kind']=='triad' for t in flat),
        'pairTasks':sum(t['kind']=='pair' for t in flat),
        'firstBatchGroups':[t['group'] for t in task_log[0]] if task_log else [],
        'taskLog':task_log,'trajectorySignature':signature,
        'selectionStatus':final_report['selectionStatus'],'winner':final_report.get('winner'),
    }


def run_seed(seed):
    if seed not in SEEDS: raise ValueError(seed)
    brief=_brief(); rows=[run_policy(brief,seed,p) for p in ('pair-k2','triad-k2')]
    return {
        'version':1,'seed':seed,
        'purpose':'dependency-safe review-task compression calibration; synthetic oracle is not artistic evidence',
        'oracleId':ORACLE_ID,
        'safeTriadStages':sorted(SAFE_TRIAD_STAGES),
        'refinePacking':'forbidden because later candidate phenotypes can depend on earlier promotions',
        'expectedEagerTrajectorySignature':EXPECTED_EAGER_SIGNATURES[seed],
        'policies':rows,
    }


def run_experiment():
    blocks=[run_seed(s) for s in SEEDS]; summary={}
    for policy in ('pair-k2','triad-k2'):
        rows=[next(r for r in b['policies'] if r['policy']==policy) for b in blocks]
        summary[policy]={
            'meanReviewTasks':statistics.fmean(r['reviewTasks'] for r in rows),
            'meanReviewRounds':statistics.fmean(r['reviewRounds'] for r in rows),
            'meanCandidateExposures':statistics.fmean(r['candidateExposures'] for r in rows),
            'meanPairRelationsElicited':statistics.fmean(r['pairRelationsElicited'] for r in rows),
            'meanTriadTasks':statistics.fmean(r['triadTasks'] for r in rows),
        }
    return {'version':1,'seeds':list(SEEDS),'summary':summary,'blocks':blocks}


def main(): print(json.dumps(run_experiment(),indent=2))
if __name__=='__main__': main()
