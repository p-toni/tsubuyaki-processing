#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from core import TIMES, render_candidate_frame
from pairwise_selector import DeterministicTemporalSelector
from portfolio_runner import run_policy


def build_selector(args, out):
    selector=DeterministicTemporalSelector()
    if args.blind_decisions_dir:
        from decision_ledger import decode_blind_decision_dirs
        from judge_queue import RecordedPhenotypeDecisionSelector
        selector=RecordedPhenotypeDecisionSelector(
            decode_blind_decision_dirs(args.blind_decisions_dir),
            render_candidate_frame,
            TIMES,
            fallback=selector,
        )
    if args.multimodal_judge:
        from multimodal_judge import MultimodalEscalatingSelector
        selector=MultimodalEscalatingSelector(
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
        selector=QueueingSelector(selector,Path(args.judge_queue),render_candidate_frame,TIMES)
    return selector


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--brief',required=True)
    ap.add_argument('--seed',type=int,required=True)
    ap.add_argument('--total-budget',type=int,default=48)
    ap.add_argument('--starts',type=int,default=2)
    ap.add_argument('--out',required=True)
    ap.add_argument('--judge-queue',default='')
    ap.add_argument('--blind-decisions-dir',action='append',default=[])
    ap.add_argument('--multimodal-judge',action='store_true')
    ap.add_argument('--judge-model',default=os.getenv('OPENAI_JUDGE_MODEL','gpt-5.6-terra'))
    ap.add_argument('--judge-reasoning',default='medium',choices=['low','medium','high','max'])
    ap.add_argument('--judge-image-detail',default='high',choices=['low','high','auto'])
    ap.add_argument('--judge-max-api-calls',type=int,default=240)
    ap.add_argument('--judge-no-symmetry',action='store_true')
    args=ap.parse_args()
    brief=json.loads(Path(args.brief).read_text()); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    selector=build_selector(args,out)
    _,rf_report,rf_winner,rf_frontier=run_policy(brief,args.seed,out/'route-first','route-first',args.total_budget,selector,starts=args.starts)
    _,pf_report,pf_winner,pf_frontier=run_policy(brief,args.seed,out/'portfolio-equal','portfolio-equal',args.total_budget,selector,starts=args.starts)
    final=None
    if len(rf_frontier)==1 and len(pf_frontier)==1:
        d=selector.compare(rf_winner,pf_winner,brief)
        final=d.to_json(); final['leftPolicy']='route-first'; final['rightPolicy']='portfolio-equal'
    report={
        'seed':args.seed,
        'totalAttemptBudgetPerPolicy':args.total_budget,
        'routeFirst':rf_report,
        'portfolioEqual':pf_report,
        'policyFinalComparison':final,
        'status':'ready-final-comparison' if final is not None else 'pending-internal-frontiers',
    }
    (out/'paired_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
