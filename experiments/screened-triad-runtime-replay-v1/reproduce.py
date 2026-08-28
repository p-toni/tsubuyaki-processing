#!/usr/bin/env python3
"""Replay the opt-in pair-matrix scheduler through screened_search itself.

Synthetic outcomes are scheduling/convergence evidence only, never artistic
authority. The frozen signatures and cost targets come from the earlier real-search
pair/triad calibrations.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/'prototypes'/'autonomous-discovery'
sys.path.insert(0,str(PROTO))

from core import TIMES,default_brief,render_candidate_frame
from representation_capacity import _generate_route_archive
from review_evidence_queue import PROMPT_VERSION
from screened_search import prepare_probe,resume_adaptive_search
from search_engine import run_search_from_starts
from triad_pair_matrix_review_queue import PAIR_KEYS,PAIR_LABELS

ORACLE_ID='synthetic-route-scheduler-oracle-v1'
SEEDS=(7,19,43)
EXPECTED={
    7:{
        'signature':'83aeec36847752f988f436aa6d506f86f06bf6146f56cd20c02d48f716361c55',
        'pair':{'reviewTasks':18,'reviewRounds':10,'candidateExposures':36},
        'triad':{'reviewTasks':14,'reviewRounds':9,'candidateExposures':32},
    },
    19:{
        'signature':'acbe0cbc6801fa71dcce31a8544aed0ed83a042e4a08918f548828964157c4df',
        'pair':{'reviewTasks':19,'reviewRounds':11,'candidateExposures':38},
        'triad':{'reviewTasks':15,'reviewRounds':9,'candidateExposures':33},
    },
    43:{
        'signature':'a2bf05f23ee714ccb9d8801106d48cd3bfa49a529dfdf0dd166833c0daf3e099',
        'pair':{'reviewTasks':21,'reviewRounds':11,'candidateExposures':42},
        'triad':{'reviewTasks':17,'reviewRounds':9,'candidateExposures':37},
    },
}


def _brief():
    base=default_brief()
    return {**base,'routes':['recurrence','family','sheet'],'explore_per_basin':4,'roundA_per_survivor':1,'total_extra_budget':3}


def _pair_id(brief_text,times,afp,bfp):
    config={'promptVersion':PROMPT_VERSION,'brief':brief_text,'times':list(times),'phenotypes':sorted((afp,bfp))}
    return hashlib.sha256(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _oracle_winner(brief_text,afp,bfp):
    pid=_pair_id(brief_text,TIMES,afp,bfp)
    h=int(hashlib.sha256((ORACLE_ID+':'+pid).encode()).hexdigest(),16)
    if h%7==0:
        return None
    ordered=sorted((afp,bfp))
    return ordered[(h>>3)&1]


def _fill_route_screen(out):
    screen=Path(out)/'route-screen'
    sealed=json.loads((screen/'sealed-mapping.json').read_text())
    decisions=json.loads((screen/'decisions-template.json').read_text())
    for label in sealed['groups']:
        decisions['decisions'][label].update(verdict='keep',confidence='strong',rationale='runtime replay: preserve all frozen routes')
    (screen/'decisions-template.json').write_text(json.dumps(decisions,indent=2)+'\n')


def _pending_pair_ids(queue):
    path=Path(queue)/'decisions.json'
    if not path.exists(): return []
    doc=json.loads(path.read_text())
    return [pid for pid,item in doc.get('decisions',{}).items() if item.get('verdict') is None]


def _pending_triad_ids(queue):
    path=Path(queue)/'decisions.json'
    if not path.exists(): return []
    doc=json.loads(path.read_text()); pending=[]
    for tid,item in doc.get('decisions',{}).items():
        verdicts=item.get('pairVerdicts')
        if not isinstance(verdicts,dict) or any(verdicts.get(key) is None for key in PAIR_KEYS): pending.append(tid)
    return pending


def _resolve_pair_pending(queue):
    pending=_pending_pair_ids(queue)
    if not pending: return []
    root=Path(queue); sealed=json.loads((root/'sealed-mapping.json').read_text()); qdoc=json.loads((root/'queue.json').read_text()); decisions=json.loads((root/'decisions.json').read_text())
    for pid in pending:
        mapping=sealed['pairs'][pid]; task=qdoc['pairs'][pid]
        afp=mapping['A']['phenotypeFingerprint']; bfp=mapping['B']['phenotypeFingerprint']
        winner=_oracle_winner(task['brief'],afp,bfp)
        verdict='tie' if winner is None else ('A' if winner==afp else 'B')
        decisions['decisions'][pid].update(
            verdict=verdict,sourceClass='independent-model',sourceId=ORACLE_ID,
            confidence='strong',rationale='synthetic screened runtime replay oracle; not artistic evidence',
        )
    (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
    return pending


def _resolve_triad_pending(queue):
    pending=_pending_triad_ids(queue)
    if not pending: return []
    root=Path(queue); sealed=json.loads((root/'sealed-mapping.json').read_text()); qdoc=json.loads((root/'queue.json').read_text()); decisions=json.loads((root/'decisions.json').read_text())
    for tid in pending:
        mapping=sealed['triads'][tid]; task=qdoc['triads'][tid]; verdicts={}
        for key in PAIR_KEYS:
            left,right=PAIR_LABELS[key]
            lfp=mapping[left]['phenotypeFingerprint']; rfp=mapping[right]['phenotypeFingerprint']
            winner=_oracle_winner(task['brief'],lfp,rfp)
            verdicts[key]='tie' if winner is None else (left if winner==lfp else right)
        decisions['decisions'][tid].update(
            pairVerdicts=verdicts,sourceClass='independent-model',sourceId=ORACLE_ID,
            confidence='strong',rationale='synthetic screened runtime replay oracle; not artistic evidence',
        )
    (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
    return pending


def _task_counts(pair_queue,triad_queue=None):
    pp=Path(pair_queue)/'decisions.json'; tp=Path(triad_queue)/'decisions.json' if triad_queue is not None else None
    pairs=len(json.loads(pp.read_text()).get('decisions',{})) if pp.exists() else 0
    triads=len(json.loads(tp.read_text()).get('decisions',{})) if tp is not None and tp.exists() else 0
    return pairs,triads


def _signature(state,report):
    payload={
        'candidates':[
            {'id':c.id,'route':c.route,'basin':c.basin,'parent':c.parent_id,'stage':c.stage,'genome':c.genome,'valid':bool(c.checks.get('valid',False))}
            for c in sorted(state.candidates.values(),key=lambda x:x.id)
        ],
        'winner':report.get('winner'),'provisionalChampion':report.get('provisionalChampion'),
        'selectionStatus':report.get('selectionStatus'),'frontier':sorted(report.get('artisticFrontier',[])),
        'allocations':report.get('allocations',{}),
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _prepare(out,brief,seed):
    prepare_probe(
        brief=brief,seed=seed,out_dir=out,probe_budget=3,minimum_per_route=1,
        include_orbit=False,routes=brief['routes'],times=TIMES,render_frame=render_candidate_frame,
        generate_route_archive=_generate_route_archive,
    )
    _fill_route_screen(out)


def _run_policy(seed,*,triads,max_replays=80):
    brief=_brief()
    with TemporaryDirectory() as td:
        root=Path(td); _prepare(root,brief,seed)
        pairq=root/'candidate-review'; triadq=root/'candidate-triad-review' if triads else None
        rounds=0; replays=0; batches=[]; captured={}
        while replays<max_replays:
            replays+=1
            captured.clear()
            def capture_run(active_brief,run_seed,out,starts,selector=None):
                state,report=run_search_from_starts(active_brief,run_seed,out,starts,selector)
                captured['state']=state; captured['report']=report
                return state,report
            result=resume_adaptive_search(
                out_dir=root,total_start_budget=3,source_class='human',source_id='runtime-route-screen',
                evidence_authoritative_promotion=True,candidate_review_queue=pairq,
                candidate_max_pending_reviews=2,candidate_max_pending_reviews_per_group=1,
                candidate_pair_matrix_triads=triads,candidate_triad_review_queue=triadq,
                render_frame=render_candidate_frame,generate_route_archive=_generate_route_archive,
                run_search_from_starts=capture_run,
            )
            pending_pairs=_pending_pair_ids(pairq); pending_triads=_pending_triad_ids(triadq) if triadq is not None else []
            if triads:
                batches.append(result['candidateQueuedReviewTasks']) if result['candidateQueuedReviewTasks'] else None
            elif pending_pairs:
                # Eager pair mode does not return queued task metadata; capture the pending IDs.
                batches.append([{'kind':'pair','id':pid} for pid in pending_pairs])
            if not pending_pairs and not pending_triads:
                break
            _resolve_pair_pending(pairq)
            if triadq is not None: _resolve_triad_pending(triadq)
            rounds+=1
        else:
            raise AssertionError('screened runtime replay did not converge')
        pairs,n_triads=_task_counts(pairq,triadq)
        report=captured['report']; state=captured['state']
        return {
            'policy':'screened-matrix-triad-k2' if triads else 'screened-current-pair-k2',
            'reviewTasks':pairs+n_triads,'reviewRounds':rounds,'searchReplays':replays,
            'candidateExposures':pairs*2+n_triads*3,'pairRelationsElicited':pairs+n_triads*3,
            'pairTasks':pairs,'triadTasks':n_triads,'batches':batches,
            'trajectorySignature':_signature(state,report),'winner':report.get('winner'),
        }


def run_seed(seed):
    if seed not in EXPECTED: raise ValueError(f'unsupported frozen seed: {seed}')
    pair=_run_policy(seed,triads=False); triad=_run_policy(seed,triads=True); expected=EXPECTED[seed]
    for row in (pair,triad):
        if row['trajectorySignature']!=expected['signature']:
            raise AssertionError(f"screened runtime trajectory divergence seed={seed} policy={row['policy']}")
    for metric,value in expected['pair'].items():
        if pair[metric]!=value: raise AssertionError(f'pair runtime metric drift seed={seed} {metric}: {pair[metric]} != {value}')
    for metric,value in expected['triad'].items():
        if triad[metric]!=value: raise AssertionError(f'triad runtime metric drift seed={seed} {metric}: {triad[metric]} != {value}')
    if triad['reviewRounds']>pair['reviewRounds'] or triad['reviewTasks']>=pair['reviewTasks'] or triad['candidateExposures']>=pair['candidateExposures']:
        raise AssertionError(f'triad runtime efficiency gate failed seed={seed}')
    return {'version':1,'seed':seed,'expected':expected,'policies':[pair,triad]}


def main():
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--seed',type=int,required=True); args=parser.parse_args()
    print(json.dumps(run_seed(args.seed),indent=2))


if __name__=='__main__': main()
