#!/usr/bin/env python3
"""Compare rank-only triads with explicit three-pair triad review.

The merged triad-review-v1 experiment only packed a three-candidate task when the
frozen arbitrary pairwise oracle happened to form a total preorder. A real review
cannot know that before showing the panel. This experiment removes that hidden
rankability precondition: one A/B/C panel explicitly records A-vs-B, A-vs-C, and
B-vs-C, so all 27 complete pairwise outcome matrices remain representable.

Synthetic outcomes drive convergence only; they are not artistic evidence.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import statistics
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[2]
BASE_PATH=ROOT/'experiments'/'triad-review-v1'/'reproduce.py'
spec=importlib.util.spec_from_file_location('triad_rank_base',BASE_PATH)
base=importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name]=base
spec.loader.exec_module(base)

SEEDS=base.SEEDS


def _matrix_triads(proposals):
    """Dependency-safe triads with no rankability filter."""
    by_inc={}
    for p in proposals:
        if base._safe_sibling_pair(p):
            by_inc.setdefault((p.a_id,p.afp,p.b_stage,p.a_route),[]).append(p)
    opportunities=[]
    for _,items in by_inc.items():
        items=sorted(items,key=lambda p:p.index)
        for p,q in itertools.combinations(items,2):
            if p.b_id==q.b_id or p.bfp==q.bfp:
                continue
            labels={'A':p.afp,'B':p.bfp,'C':q.bfp}
            outcomes={}
            pair_ids={}
            for x,y in itertools.combinations(('A','B','C'),2):
                winner=base._oracle_winner(p.brief_text,labels[x],labels[y])
                outcomes[(x,y)]='tie' if winner is None else (x if winner==labels[x] else y)
                pair_ids[tuple(sorted((x,y)))]=base._pair_id(p.brief_text,base.TIMES,labels[x],labels[y])
            opportunities.append({
                'index':min(p.index,q.index),
                'group':p.group,
                'proposals':(p,q),
                'labels':labels,
                'outcomes':outcomes,
                'pairIds':pair_ids,
                'rankable':base.order_for_outcomes(outcomes) is not None,
            })
            break
    return sorted(opportunities,key=lambda x:x['index'])


def _resolve_matrix_task(task,evidence):
    labels=task['labels']
    for x,y in itertools.combinations(('A','B','C'),2):
        pid=task['pairIds'][tuple(sorted((x,y)))]
        winner=base._oracle_winner(task['proposals'][0].brief_text,labels[x],labels[y])
        evidence[pid]=winner
    return {
        'kind':'pair-matrix-triad',
        'group':task['group'],
        'candidateExposures':3,
        'relations':3,
        'proposalIndex':task['index'],
        'rankable':bool(task['rankable']),
    }


def _select_matrix_tasks(proposals,evidence,max_tasks=2):
    unresolved=[p for p in proposals if p.pair_id not in evidence]
    triads=_matrix_triads(unresolved)
    triad_by_index={t['index']:t for t in triads}
    selected=[]; used_groups=set(); covered=set()
    for p in unresolved:
        if len(selected)>=max_tasks:
            break
        if p.pair_id in covered or p.group in used_groups:
            continue
        task=triad_by_index.get(p.index)
        if task is not None:
            tids=set(task['pairIds'].values())
            if not tids & covered:
                selected.append(('triad',task)); used_groups.add(task['group']); covered.update(tids); continue
        selected.append(('pair',p)); used_groups.add(p.group); covered.add(p.pair_id)
    return selected


def run_matrix_policy(brief,seed,max_replays=80):
    evidence={}; rounds=0; replays=0; task_log=[]; final_state=final_report=None
    with TemporaryDirectory() as td:
        out=Path(td)/'search'
        while replays<max_replays:
            replays+=1
            selector=base.ProposalSelector(evidence)
            final_state,final_report=base.run_search_from_starts(brief,seed,out,base._starts(brief,seed),selector)
            proposals=[p for p in selector.proposals if p.pair_id not in evidence]
            if not proposals:
                break
            tasks=_select_matrix_tasks(proposals,evidence,max_tasks=2)
            if not tasks:
                raise AssertionError('matrix-triad-k2 produced unresolved proposals but no review task')
            round_items=[]
            for kind,item in tasks:
                round_items.append(_resolve_matrix_task(item,evidence) if kind=='triad' else base._resolve_pair_task(item,evidence))
            task_log.append(round_items); rounds+=1
        else:
            raise AssertionError('matrix-triad-k2 did not converge')
    signature=base._signature(final_state,final_report)
    if signature!=base.EXPECTED_EAGER_SIGNATURES[seed]:
        raise AssertionError(f'trajectory divergence seed={seed} policy=matrix-triad-k2: {signature}')
    flat=[t for row in task_log for t in row]
    return {
        'policy':'matrix-triad-k2',
        'reviewTasks':len(flat),
        'reviewRounds':rounds,
        'searchReplays':replays,
        'candidateExposures':sum(t['candidateExposures'] for t in flat),
        'pairRelationsElicited':sum(t['relations'] for t in flat),
        'triadTasks':sum(t['kind']=='pair-matrix-triad' for t in flat),
        'nonRankableTriadTasks':sum(t['kind']=='pair-matrix-triad' and not t['rankable'] for t in flat),
        'pairTasks':sum(t['kind']=='pair' for t in flat),
        'firstBatchGroups':[t['group'] for t in task_log[0]] if task_log else [],
        'taskLog':task_log,
        'trajectorySignature':signature,
        'selectionStatus':final_report['selectionStatus'],
        'winner':final_report.get('winner'),
    }


def run_seed(seed):
    if seed not in SEEDS:
        raise ValueError(seed)
    brief=base._brief()
    pair=base.run_policy(brief,seed,'pair-k2')
    ranked=base.run_policy(brief,seed,'triad-k2')
    ranked['policy']='rank-triad-k2'
    matrix=run_matrix_policy(brief,seed)
    return {
        'version':1,
        'seed':seed,
        'purpose':'compare rank-constrained vs arbitrary-pair-preserving triad tasks',
        'oracleId':base.ORACLE_ID,
        'expectedEagerTrajectorySignature':base.EXPECTED_EAGER_SIGNATURES[seed],
        'policies':[pair,ranked,matrix],
    }


def run_experiment():
    blocks=[run_seed(seed) for seed in SEEDS]
    policies=('pair-k2','rank-triad-k2','matrix-triad-k2')
    summary={}
    for policy in policies:
        rows=[next(r for r in block['policies'] if r['policy']==policy) for block in blocks]
        summary[policy]={
            'meanReviewTasks':statistics.fmean(r['reviewTasks'] for r in rows),
            'meanReviewRounds':statistics.fmean(r['reviewRounds'] for r in rows),
            'meanCandidateExposures':statistics.fmean(r['candidateExposures'] for r in rows),
            'meanPairRelationsElicited':statistics.fmean(r['pairRelationsElicited'] for r in rows),
            'meanTriadTasks':statistics.fmean(r['triadTasks'] for r in rows),
            'meanNonRankableTriadTasks':statistics.fmean(r.get('nonRankableTriadTasks',0) for r in rows),
        }
    return {
        'version':1,
        'question':'Can one triad panel preserve arbitrary pairwise evidence without a hidden transitivity assumption?',
        'seeds':list(SEEDS),
        'trajectoryContract':'every policy must exactly reproduce the frozen eager trajectory',
        'summary':summary,
        'blocks':blocks,
    }


def main():
    print(json.dumps(run_experiment(),indent=2))

if __name__=='__main__':
    main()
