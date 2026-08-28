#!/usr/bin/env python3
"""Calibrate a dependency-aware route-first deferred K2 scheduler."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('route_balanced_reproduce',HERE/'reproduce.py')
if SPEC is None or SPEC.loader is None: raise RuntimeError('could not load reproduce.py')
mod=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(mod)

EXPECTED_EAGER={
    7:'83aeec36847752f988f436aa6d506f86f06bf6146f56cd20c02d48f716361c55',
    19:'acbe0cbc6801fa71dcce31a8544aed0ed83a042e4a08918f548828964157c4df',
    43:'a2bf05f23ee714ccb9d8801106d48cd3bfa49a529dfdf0dd166833c0daf3e099',
}


class RouteFirstScheduler(mod.DeferredRouteScheduler):
    """Balance local route reviews first; defer cross-route pairs until local work clears."""
    def flush(self):
        if self.queue_dir is None or not self.proposals: return []
        historical={}
        sealed_path=self.queue_dir/'sealed-mapping.json'
        if sealed_path.exists():
            sealed=json.loads(sealed_path.read_text())
            for group in sealed.get('reviewGroups',{}).values(): historical[group]=historical.get(group,0)+1
        priority={f'route:{route}':i for i,route in enumerate(self.route_priority)}
        indexed=list(enumerate(self.proposals))
        def key(item):
            i,p=item; group=p['review_group'] or ''
            phase=0 if group.startswith('route:') else 1
            return (phase,historical.get(group,0),priority.get(group,len(priority)+1),i)
        indexed.sort(key=key)
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
            created=mod.create_review_bundle(
                self.queue_dir,brief=p['brief_text'],times=self.times,
                a_frames=p['a_frames'],b_frames=p['b_frames'],
                a_candidate_id=p['a_id'],b_candidate_id=p['b_id'],review_group=p['review_group'],
            )
            if created!=p['pair_id']: raise RuntimeError('review bundle pair id drift')
        return [p['review_group'] for p in chosen]


def run(seed,max_replays=80):
    brief=mod._brief()
    with TemporaryDirectory() as td:
        root=Path(td); queue=root/'review'; out=root/'search'
        review_rounds=0; replays=0; first_round={}; batch_groups=[]; final_state=final_report=None
        while replays<max_replays:
            replays+=1
            selector=RouteFirstScheduler(render_frame=mod.render_candidate_frame,times=mod.TIMES,queue_dir=queue,batch_size=2)
            final_state,final_report=mod.run_search_from_starts(brief,seed,out,mod._starts(brief,seed),selector)
            selector.flush()
            pending=mod._pending(queue)
            if not pending: break
            groups=[mod._group_for_pair(queue,pid,final_state) for pid in pending]
            batch_groups.append(groups)
            for group in groups: first_round.setdefault(group,review_rounds+1)
            mod._resolve_pending(queue); review_rounds+=1
        else: raise AssertionError('route-first-k2 did not converge')
        row={
            'policy':'route-first-k2','ratings':mod._pair_count(queue),'reviewRounds':review_rounds,'searchReplays':replays,
            'trajectorySignature':mod._signature(final_state,final_report),'firstReviewRoundByGroup':first_round,
            'firstBatchGroups':batch_groups[0] if batch_groups else [],'batchGroups':batch_groups,
            'selectionStatus':final_report['selectionStatus'],'winner':final_report.get('winner'),'frontierSize':len(final_report.get('artisticFrontier',[])),
        }
        if row['trajectorySignature']!=EXPECTED_EAGER[seed]:
            raise AssertionError(f"trajectory divergence seed={seed}")
        return row


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,required=True); args=ap.parse_args()
    if args.seed not in EXPECTED_EAGER: raise SystemExit(f'unfrozen seed: {args.seed}')
    print(json.dumps({'version':1,'seed':args.seed,'purpose':'route-first scheduler calibration only; synthetic oracle is not artistic evidence','policy':run(args.seed)},indent=2))


if __name__=='__main__': main()
