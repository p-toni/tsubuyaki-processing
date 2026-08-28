#!/usr/bin/env python3
"""CLI for two-phase route-screened adaptive search."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from screened_search import (
    DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS,
    DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS_PER_GROUP,
    DEFAULT_MIN_PROBES_PER_ROUTE,
    prepare_probe,
    resume_adaptive_search,
)


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare')
    p.add_argument('--brief',required=True); p.add_argument('--seed',type=int,required=True); p.add_argument('--out',required=True)
    p.add_argument('--probe-budget',type=int,default=None); p.add_argument('--minimum-per-route',type=int,default=DEFAULT_MIN_PROBES_PER_ROUTE)
    p.add_argument('--no-orbit',action='store_true')
    r=sub.add_parser('resume')
    r.add_argument('--out',required=True); r.add_argument('--total-start-budget',type=int,required=True)
    r.add_argument('--source-class',required=True,choices=['human','independent-model','same-model','deterministic-proxy','text-prior'])
    r.add_argument('--source-id',required=True)
    r.add_argument('--evidence-authoritative-promotion',action='store_true')
    r.add_argument('--candidate-evidence-dir',action='append',default=[])
    r.add_argument('--candidate-review-queue',default='')
    r.add_argument('--candidate-max-pending-reviews',type=int,default=DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS)
    r.add_argument('--candidate-max-pending-reviews-per-group',type=int,default=DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS_PER_GROUP)
    r.add_argument('--candidate-pair-matrix-triads',action='store_true')
    r.add_argument('--candidate-triad-review-queue',default='')
    args=ap.parse_args()
    if args.command=='prepare':
        brief=json.loads(Path(args.brief).read_text())
        result=prepare_probe(brief=brief,seed=args.seed,out_dir=Path(args.out),probe_budget=args.probe_budget,minimum_per_route=args.minimum_per_route,include_orbit=not args.no_orbit)
    else:
        out=Path(args.out)
        review_queue=(Path(args.candidate_review_queue) if args.candidate_review_queue else (out/'candidate-review' if args.evidence_authoritative_promotion else None))
        triad_review_queue=(Path(args.candidate_triad_review_queue) if args.candidate_triad_review_queue else (out/'candidate-triad-review' if args.candidate_pair_matrix_triads else None))
        result=resume_adaptive_search(
            out_dir=out,
            total_start_budget=args.total_start_budget,
            source_class=args.source_class,
            source_id=args.source_id,
            evidence_authoritative_promotion=args.evidence_authoritative_promotion,
            candidate_evidence_dirs=[Path(x) for x in args.candidate_evidence_dir],
            candidate_review_queue=review_queue,
            candidate_max_pending_reviews=args.candidate_max_pending_reviews,
            candidate_max_pending_reviews_per_group=args.candidate_max_pending_reviews_per_group,
            candidate_pair_matrix_triads=args.candidate_pair_matrix_triads,
            candidate_triad_review_queue=triad_review_queue,
        )
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
