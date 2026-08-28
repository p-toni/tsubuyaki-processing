#!/usr/bin/env python3
"""Exhaustive synthetic calibration for pending-review caps.

Model one deterministic incumbent/challenger tournament whose true pairwise
preferences come from a hidden strict total order. Unknown comparisons preserve
the incumbent, matching the search contract. A replay round exposes at most
``cap`` previously unseen pairs, reviews them, then reruns from the same start.
"""
from __future__ import annotations

import itertools
import json
import math
import statistics


def simulate(order, cap=None):
    rank={candidate:i for i,candidate in enumerate(order)}
    evidence={}
    reviews=0
    rounds=0
    while True:
        pending=[]
        incumbent=0
        for challenger in range(1,len(order)):
            key=tuple(sorted((incumbent,challenger)))
            if key in evidence:
                if evidence[key]==challenger:
                    incumbent=challenger
            elif cap is None or len(pending)<cap:
                pending.append(key)
        if not pending:
            return reviews,rounds,incumbent
        rounds+=1
        for a,b in pending:
            evidence[(a,b)]=a if rank[a]<rank[b] else b
        reviews+=len(pending)


def summarize(n):
    rows={}
    orders=list(itertools.permutations(range(n)))
    for cap in (1,2,3,None):
        runs=[simulate(order,cap) for order in orders]
        assert all(run[2]==order[0] for run,order in zip(runs,orders))
        reviews=[run[0] for run in runs]
        rounds=[run[1] for run in runs]
        key='eager' if cap is None else str(cap)
        rows[key]={
            'orders':math.factorial(n),
            'meanReviews':statistics.mean(reviews),
            'maxReviews':max(reviews),
            'meanReviewRounds':statistics.mean(rounds),
            'maxReviewRounds':max(rounds),
            'championPreservation':1.0,
        }
    return rows


def main():
    result={str(n):summarize(n) for n in range(4,9)}
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
