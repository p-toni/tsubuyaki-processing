#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path

from core import *
from search_engine import run_search
from pairwise_selector import PairwiseSelector, DeterministicTemporalSelector
from judge_queue import QueueingSelector, RecordedPhenotypeDecisionSelector, decode_blind_decisions

_render_candidate_frame = render_candidate_frame

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--brief',default=''); ap.add_argument('--seed',type=int,default=260826); ap.add_argument('--out',default='autonomous_discovery_run'); ap.add_argument('--judge-queue',default=''); ap.add_argument('--blind-decisions-dir',default=''); ap.add_argument('--multimodal-judge',action='store_true'); ap.add_argument('--judge-model',default=os.getenv('OPENAI_JUDGE_MODEL','gpt-5.6-terra')); ap.add_argument('--judge-reasoning',default='medium',choices=['low','medium','high','max']); ap.add_argument('--judge-image-detail',default='high',choices=['low','high','auto']); ap.add_argument('--judge-max-api-calls',type=int,default=80); ap.add_argument('--judge-cache',default=''); ap.add_argument('--judge-audit-dir',default=''); ap.add_argument('--judge-no-symmetry',action='store_true'); args=ap.parse_args()
    brief=default_brief() if not args.brief else json.loads(Path(args.brief).read_text()); out=Path(args.out); selector:PairwiseSelector=DeterministicTemporalSelector()
    if args.blind_decisions_dir: selector=RecordedPhenotypeDecisionSelector(decode_blind_decisions(Path(args.blind_decisions_dir)),render_candidate_frame,TIMES,fallback=selector)
    if args.multimodal_judge:
        from multimodal_judge import MultimodalEscalatingSelector
        selector=MultimodalEscalatingSelector(coarse=selector,render_frame=render_candidate_frame,times=TIMES,model=args.judge_model,reasoning_effort=args.judge_reasoning,image_detail=args.judge_image_detail,max_api_calls=args.judge_max_api_calls,cache_path=Path(args.judge_cache) if args.judge_cache else out/'judge-cache.json',audit_dir=Path(args.judge_audit_dir) if args.judge_audit_dir else out/'judge-audit',symmetry=not args.judge_no_symmetry)
    if args.judge_queue: selector=QueueingSelector(selector,Path(args.judge_queue),render_candidate_frame,TIMES)
    _,report=run_search(brief,args.seed,out,selector); print(json.dumps(report,indent=2)); print(out/'winner_timeline.png')

if __name__=='__main__': main()
