#!/usr/bin/env python3
from __future__ import annotations

import json, random, tempfile
from pathlib import Path

import run
from judge_queue import QueueingSelector, decode_blind_decisions
from pairwise_selector import DeterministicTemporalSelector, RecordedDecisionSelector


def valid(route, seed, cid):
    rng=random.Random(seed)
    for _ in range(100):
        c=run.Candidate(cid,route,cid,run.ROUTES[route]['seed'](rng),None,'test')
        run.evaluate_candidate(c,run.default_brief())
        if c.checks['valid']:
            return c
    raise AssertionError('no valid candidate')


def main():
    a=valid('family',1,'A1')
    b=valid('recurrence',2,'B1')
    brief=run.default_brief()

    def render(c,t):
        return run.draw_points(run.ROUTES[c.route]['render'](c.genome,t),alpha=c.genome['alpha'])

    with tempfile.TemporaryDirectory() as td:
        q=QueueingSelector(DeterministicTemporalSelector(),Path(td),render,run.TIMES)
        d=q.compare(a,b,brief)
        assert d.verdict == 'tie'  # cross-route proxy is intentionally conservative here
        q.compare(a,b,brief)       # duplicate comparison must not duplicate queue entry
        queue=json.loads(Path(td,'queue.json').read_text())
        assert len(queue['pairs']) == 1
        pair_id=queue['pairs'][0]['pairId']
        assert Path(queue['pairs'][0]['panel']).exists()
        decisions=json.loads(Path(td,'decisions-template.json').read_text())
        decisions[pair_id]['verdict']='A'
        Path(td,'decisions-template.json').write_text(json.dumps(decisions,indent=2)+'\n')
        decoded=decode_blind_decisions(Path(td))
        replay=RecordedDecisionSelector(decoded)
        rd=replay.compare(a,b,brief)
        assert rd.verdict in {'a','b'}

    print('judge queue tests: PASS')

if __name__=='__main__':
    main()
