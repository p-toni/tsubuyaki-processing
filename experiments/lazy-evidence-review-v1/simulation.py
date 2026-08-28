#!/usr/bin/env python3
"""Exhaustive synthetic calibration for pending-review caps.

The search contract is modeled as a deterministic incumbent/challenger sequence.
Unknown comparisons preserve the incumbent. A replay exposes at most ``cap``
previously unseen pairs, resolves those pairs, then reruns from the same start.

Two preference models are exhausted:
1. hidden strict total orders for 4..8 candidates;
2. every win/loss/tie assignment for every pair at 4..5 candidates, including
   non-transitive preference structures.
"""
from __future__ import annotations

import itertools
import json
import math
import statistics

CAPS=(1,2,3,None)


def run_replay(n,resolve_pair,cap=None):
    evidence={}
    reviews=0
    rounds=0
    while True:
        pending=[]
        incumbent=0
        for challenger in range(1,n):
            key=tuple(sorted((incumbent,challenger)))
            if key in evidence:
                winner=evidence[key]
                if winner is not None and winner==challenger:
                    incumbent=challenger
            elif cap is None or len(pending)<cap:
                pending.append(key)
        if not pending:
            return reviews,rounds,incumbent
        rounds+=1
        for key in pending:
            evidence[key]=resolve_pair(key)
        reviews+=len(pending)


def fully_evidenced_result(n,resolve_pair):
    incumbent=0
    for challenger in range(1,n):
        winner=resolve_pair(tuple(sorted((incumbent,challenger))))
        if winner is not None and winner==challenger:
            incumbent=challenger
    return incumbent


def summarize_runs(runs):
    reviews=[run[0] for run in runs]
    rounds=[run[1] for run in runs]
    return {
        'meanReviews':statistics.mean(reviews),
        'maxReviews':max(reviews),
        'meanReviewRounds':statistics.mean(rounds),
        'maxReviewRounds':max(rounds),
        'resultPreservation':1.0,
    }


def summarize_total_order(n):
    rows={}
    orders=list(itertools.permutations(range(n)))
    for cap in CAPS:
        runs=[]
        for order in orders:
            rank={candidate:i for i,candidate in enumerate(order)}
            def resolve(key,rank=rank):
                a,b=key
                return a if rank[a]<rank[b] else b
            run=run_replay(n,resolve,cap)
            assert run[2]==order[0]
            runs.append(run)
        key='eager' if cap is None else str(cap)
        rows[key]={'orders':math.factorial(n),**summarize_runs(runs)}
    return rows


def summarize_arbitrary_pairwise(n):
    pairs=list(itertools.combinations(range(n),2))
    rows={cap:[] for cap in CAPS}
    count=0
    # 0 = first candidate wins, 1 = second candidate wins, 2 = explicit tie.
    for choices in itertools.product((0,1,2),repeat=len(pairs)):
        outcomes={
            pair:(pair[0] if choice==0 else pair[1] if choice==1 else None)
            for pair,choice in zip(pairs,choices)
        }
        resolve=lambda key,outcomes=outcomes: outcomes[key]
        expected=fully_evidenced_result(n,resolve)
        for cap in CAPS:
            run=run_replay(n,resolve,cap)
            assert run[2]==expected
            rows[cap].append(run)
        count+=1
    return {
        ('eager' if cap is None else str(cap)):{'matrices':count,**summarize_runs(runs)}
        for cap,runs in rows.items()
    }


def main():
    result={
        'strictTotalOrder':{str(n):summarize_total_order(n) for n in range(4,9)},
        'arbitraryPairwiseWithTies':{str(n):summarize_arbitrary_pairwise(n) for n in range(4,6)},
    }
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
