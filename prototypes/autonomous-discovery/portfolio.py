#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from core import TIMES, render_candidate_frame
from pairwise_selector import DeterministicTemporalSelector
from portfolio_runner import run_policy


def build_selector(args, out):
    selector = DeterministicTemporalSelector()
    if args.blind_decisions_dir:
        from decision_ledger import decode_blind_decision_dirs
        from judge_queue import RecordedPhenotypeDecisionSelector
        selector = RecordedPhenotypeDecisionSelector(
            decode_blind_decision_dirs(args.blind_decisions_dir),
            render_candidate_frame,
            TIMES,
            fallback=selector,
        )
    if args.multimodal_judge:
        from multimodal_judge import MultimodalEscalatingSelector
        selector = MultimodalEscalatingSelector(
            coarse=selector,
            render_frame=render_candidate_frame,
            times=TIMES,
            model=args.judge_model,
            reasoning_effort=args.judge_reasoning,
            image_detail=args.judge_image_detail,
            max_api_calls=args.judge_max_api_calls,
            cache_path=out/'judge-cache.json',
            audit_dir=out/'judge-audit',
            symmetry=not args.judge_no_symmetry,
        )
    if args.judge_queue:
        from judge_queue import QueueingSelector
        selector = QueueingSelector(selector, Path(args.judge_queue), render_candidate_frame, TIMES)
    return selector


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--brief',required=True)
    ap.add_argument('--seed',type=int,required=True)
    ap.add_argument('--policy',required=True,choices=['route-first','portfolio-equal'])
    ap.add_argument('--total-budget',type=int,default=48)
    ap.add_argument('--starts',type=int,default=2)
    ap.add_argument('--out',required=True)
    ap.add_argument('--judge-queue',default='')
    ap.add_argument('--blind-decisions-dir',action='append',default=[])
    ap.add_argument('--multimodal-judge',action='store_true')
    ap.add_argument('--judge-model',default=os.getenv('OPENAI_JUDGE_MODEL','gpt-5.6-terra'))
    ap.add_argument('--judge-reasoning',default='medium',choices=['low','medium','high','max'])
    ap.add_argument('--judge-image-detail',default='high',choices=['low','high','auto'])
    ap.add_argument('--judge-max-api-calls',type=int,default=120)
    ap.add_argument('--judge-no-symmetry',action='store_true')
    args=ap.parse_args()
    brief=json.loads(Path(args.brief).read_text()); out=Path(args.out)
    selector=build_selector(args,out)
    _,report,_,_=run_policy(brief,args.seed,out,args.policy,args.total_budget,selector,starts=args.starts)
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
