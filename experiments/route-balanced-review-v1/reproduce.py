#!/usr/bin/env python3
"""Compare lazy review scheduling policies on a real multi-route adaptive search.

Triggered by live-image-judge-v1: eight consecutive candidate review slots came
from recurrence before family/sheet under route-ordered traversal. The live visual
judgments were same-model advisory observations, not artistic authority. This
experiment tests scheduling only. Synthetic pair decisions are never used as
artistic evidence.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/'prototypes'/'autonomous-discovery'
sys.path.insert(0,str(PROTO))

from core import TIMES,default_brief,render_candidate_frame
from evidence_selector import EvidenceAuthoritySelector
from representation_capacity import _generate_route_archive
from review_evidence_queue import create_review_bundle
from search_engine import run_search_from_starts

ORACLE_ID='synthetic-route-scheduler-oracle-v1'
# Advisory ordering only. This affects which unresolved panels are surfaced first,
# never validity, candidate generation, promotion, or the synthetic oracle verdict.
ROUTE_PRIORITY=('family','sheet','recurrence')
SEEDS=(7,19,43)


def _oracle_verdict(pair_id,mapping):
    fps={label:mapping[label]['phenotypeFingerprint'] for label in ('A','B')}
    if fps['A']==fps['B']: return 'tie'
    h=int(hashlib.sha256((ORACLE_ID+':'+pair_id).encode()).hexdigest(),16)
    if h%7==0: return 'tie'
    ordered=sorted(fps.items(),key=lambda item:item[1])
    winner_fp=ordered[(h>>3)&1][1]
    return next(label for label,fp in fps.items() if fp==winner_fp)


def _pending(queue):
    p=queue/'decisions.json'
    if not p.exists(): return []
    return [pid for pid,item in json.loads(p.read_text()).get('decisions',{}).items() if item.get('verdict') is None]


def _pair_count(queue):
    p=queue/'decisions.json'
    return len(json.loads(p.read_text()).get('decisions',{})) if p.exists() else 0


def _resolve_pending(queue):
    pending=_pending(queue)
    if not pending: return 0
    sealed=json.loads((queue/'sealed-mapping.json').read_text())
    decisions=json.loads((queue/'decisions.json').read_text())
    for pid in pending:
        decisions['decisions'][pid].update(
            verdict=_oracle_verdict(pid,sealed['pairs'][pid]),
            sourceClass='independent-model',sourceId=ORACLE_ID,confidence='strong',
            rationale='synthetic scheduling oracle; not artistic evidence',
        )
    (queue/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
    return len(pending)


def _review_group(a,b,brief):
    ar=getattr(a,'route',None); br=getattr(b,'route',None)
    if not ar or not br: return None
    return f'route:{ar}' if ar==br else 'cross:'+('|'.join(sorted((str(ar),str(br)))))


class DeferredRouteScheduler(EvidenceAuthoritySelector):
    """Experimental selector that decouples comparison traversal from review batching."""
    def __init__(self,*args,batch_size=2,route_priority=ROUTE_PRIORITY,**kwargs):
        super().__init__(*args,max_pending_reviews=None,max_pending_reviews_per_group=None,**kwargs)
        self.batch_size=int(batch_size); self.route_priority=tuple(route_priority); self.proposals=[]; self._proposal_ids=set()

    def _review_group(self,a,b,brief):
        # The base implementation disables grouping when no per-group queue cap is
        # configured. Deferred scheduling still needs route provenance even though
        # it deliberately does not use the eager per-group cap.
        return _review_group(a,b,brief)

    def _queue(self,*,pair_id,brief_text,a_frames,b_frames,a_id,b_id,review_group):
        if self.queue_dir is None or pair_id in self.queue_pair_ids or pair_id in self._proposal_ids: return False
        self.proposals.append(dict(pair_id=pair_id,brief_text=brief_text,a_frames=a_frames,b_frames=b_frames,a_id=a_id,b_id=b_id,review_group=review_group))
        self._proposal_ids.add(pair_id)
        return True

    def flush(self):
        if self.queue_dir is None or not self.proposals: return []
        historical={}
        sealed_path=self.queue_dir/'sealed-mapping.json'
        if sealed_path.exists():
            sealed=json.loads(sealed_path.read_text())
            for group in sealed.get('reviewGroups',{}).values(): historical[group]=historical.get(group,0)+1
        priority={f'route:{route}':i for i,route in enumerate(self.route_priority)}
        indexed=list(enumerate(self.proposals))
        indexed.sort(key=lambda x:(historical.get(x[1]['review_group'],0),priority.get(x[1]['review_group'],len(priority)+1),x[0]))
        chosen=[]; used=set()
        for _,proposal in indexed:
            group=proposal['review_group']
            if group and group in used: continue
            chosen.append(proposal); used.add(group)
            if len(chosen)>=self.batch_size: break
        if len(chosen)<self.batch_size:
            for _,proposal in indexed:
                if proposal in chosen: continue
                chosen.append(proposal)
                if len(chosen)>=self.batch_size: break
        for p in chosen:
            created=create_review_bundle(
                self.queue_dir,brief=p['brief_text'],times=self.times,
                a_frames=p['a_frames'],b_frames=p['b_frames'],
                a_candidate_id=p['a_id'],b_candidate_id=p['b_id'],review_group=p['review_group'],
            )
            if created!=p['pair_id']: raise RuntimeError('review bundle pair id drift')
        return [p['review_group'] for p in chosen]


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


def _group_for_pair(queue,pid,state):
    sealed=json.loads((queue/'sealed-mapping.json').read_text())
    group=sealed.get('reviewGroups',{}).get(pid)
    if group: return group
    mapping=sealed['pairs'][pid]
    ids=[mapping[label]['candidateId'] for label in ('A','B')]
    routes=[state.candidates[cid].route for cid in ids]
    return f'route:{routes[0]}' if routes[0]==routes[1] else 'cross:'+('|'.join(sorted(routes)))


def run_policy(brief,seed,policy,max_replays=80):
    with TemporaryDirectory() as td:
        root=Path(td); queue=root/'review'; out=root/'search'
        review_rounds=0; replays=0; first_round={}; batch_groups=[]; final_state=final_report=None
        while replays<max_replays:
            replays+=1
            if policy=='global-k2':
                selector=EvidenceAuthoritySelector(render_frame=render_candidate_frame,times=TIMES,queue_dir=queue,max_pending_reviews=2)
            elif policy=='group-k2':
                selector=EvidenceAuthoritySelector(render_frame=render_candidate_frame,times=TIMES,queue_dir=queue,max_pending_reviews=2,max_pending_reviews_per_group=1)
            elif policy=='scheduled-k2':
                selector=DeferredRouteScheduler(render_frame=render_candidate_frame,times=TIMES,queue_dir=queue,batch_size=2)
            elif policy=='scheduled-k3':
                selector=DeferredRouteScheduler(render_frame=render_candidate_frame,times=TIMES,queue_dir=queue,batch_size=3)
            elif policy=='eager':
                selector=EvidenceAuthoritySelector(render_frame=render_candidate_frame,times=TIMES,queue_dir=queue)
            else: raise ValueError(policy)
            final_state,final_report=run_search_from_starts(brief,seed,out,_starts(brief,seed),selector)
            if isinstance(selector,DeferredRouteScheduler): selector.flush()
            pending=_pending(queue)
            if not pending: break
            groups=[_group_for_pair(queue,pid,final_state) for pid in pending]
            batch_groups.append(groups)
            for group in groups: first_round.setdefault(group,review_rounds+1)
            _resolve_pending(queue); review_rounds+=1
        else: raise AssertionError(f'{policy} did not converge')
        return {
            'policy':policy,'ratings':_pair_count(queue),'reviewRounds':review_rounds,'searchReplays':replays,
            'trajectorySignature':_signature(final_state,final_report),'firstReviewRoundByGroup':first_round,
            'firstBatchGroups':batch_groups[0] if batch_groups else [],'batchGroups':batch_groups,
            'selectionStatus':final_report['selectionStatus'],'winner':final_report.get('winner'),'frontierSize':len(final_report.get('artisticFrontier',[])),
        }


def run_experiment():
    brief=_brief(); policies=('global-k2','group-k2','scheduled-k2','scheduled-k3','eager'); blocks=[]
    for seed in SEEDS:
        rows=[run_policy(brief,seed,p) for p in policies]
        eager=next(r for r in rows if r['policy']=='eager')
        for row in rows:
            if row['trajectorySignature']!=eager['trajectorySignature']:
                raise AssertionError(f"trajectory divergence seed={seed} policy={row['policy']}")
        blocks.append({'seed':seed,'policies':rows})
    summary={}
    for policy in policies:
        rows=[next(r for r in b['policies'] if r['policy']==policy) for b in blocks]
        summary[policy]={
            'meanRatings':statistics.fmean(r['ratings'] for r in rows),
            'meanReviewRounds':statistics.fmean(r['reviewRounds'] for r in rows),
            'meanSearchReplays':statistics.fmean(r['searchReplays'] for r in rows),
            'meanFirstRoundRecurrence':statistics.fmean(r['firstReviewRoundByGroup'].get('route:recurrence',99) for r in rows),
            'meanFirstRoundFamily':statistics.fmean(r['firstReviewRoundByGroup'].get('route:family',99) for r in rows),
            'meanFirstRoundSheet':statistics.fmean(r['firstReviewRoundByGroup'].get('route:sheet',99) for r in rows),
            'meanDistinctRoutesFirstBatch':statistics.fmean(len({g for g in r['firstBatchGroups'] if g.startswith('route:')}) for r in rows),
        }
    return {
        'version':1,
        'trigger':'live-image-judge-v1 exposed 8/8 consecutive review slots from recurrence under route-ordered global K2',
        'purpose':'review-scheduling calibration only; synthetic oracle is not artistic evidence',
        'seeds':list(SEEDS),'routes':brief['routes'],'routePriority':list(ROUTE_PRIORITY),
        'routePriorityAuthority':'same-model advisory scheduling prior only',
        'trajectoryAgreement':'all policies exactly match eager final candidate trajectory in every block',
        'summary':summary,'blocks':blocks,
    }


def main():
    result=run_experiment(); print(json.dumps(result,indent=2))

if __name__=='__main__': main()
