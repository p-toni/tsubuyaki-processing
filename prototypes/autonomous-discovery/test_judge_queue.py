#!/usr/bin/env python3
from __future__ import annotations

import json, random, tempfile
from pathlib import Path

import run
from judge_queue import (
    QueueingSelector,
    RecordedPhenotypeDecisionSelector,
    decode_blind_decisions,
    judgment_pair_key,
)
from pairwise_selector import DeterministicTemporalSelector


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
        q.compare(a,b,brief)       # duplicate visible pair must not duplicate queue entry
        queue=json.loads(Path(td,'queue.json').read_text())
        assert queue['version'] == 2
        assert len(queue['pairs']) == 1
        assert 'routes' not in queue['pairs'][0]
        assert 'proxyDecision' not in queue['pairs'][0]
        pair_id=queue['pairs'][0]['pairId']
        assert Path(queue['pairs'][0]['panel']).exists()

        decisions=json.loads(Path(td,'decisions-template.json').read_text())
        assert decisions['version'] == 2
        decisions['decisions'][pair_id]['verdict']='A'
        Path(td,'decisions-template.json').write_text(json.dumps(decisions,indent=2)+'\n')
        decoded=decode_blind_decisions(Path(td))
        replay=RecordedPhenotypeDecisionSelector(decoded,render,run.TIMES)
        rd=replay.compare(a,b,brief)
        assert rd.verdict in {'a','b'}
        reverse=replay.compare(b,a,brief)
        assert reverse.verdict in {'a','b'} and reverse.verdict != rd.verdict

        # Regression: replay can change which parent is mutated downstream while
        # preserving a candidate id. An old id-keyed judgment must not transfer.
        changed=run.Candidate(a.id,a.route,a.basin,dict(a.genome),a.parent_id,a.stage)
        changed.genome['organ_len'] *= 1.15
        run.evaluate_candidate(changed,brief)
        assert changed.checks['valid']
        old_key,*_=judgment_pair_key(a,b,brief,render,run.TIMES)
        changed_key,*_=judgment_pair_key(changed,b,brief,render,run.TIMES)
        assert changed_key != old_key
        miss=replay.compare(changed,b,brief)
        assert miss.verdict == 'tie' and miss.confidence == 'defer'

        # Aesthetic judgments are also brief-specific even when pixels are unchanged.
        changed_brief=dict(brief)
        changed_brief['artistic_intent']=brief['artistic_intent']+' Favor radical asymmetry.'
        changed_brief_key,*_=judgment_pair_key(a,b,changed_brief,render,run.TIMES)
        assert changed_brief_key != old_key
        miss=replay.compare(a,b,changed_brief)
        assert miss.verdict == 'tie' and miss.confidence == 'defer'

        # Legacy candidate-id queues are explicitly rejected rather than replayed unsafely.
        Path(td,'sealed-mapping.json').write_text(json.dumps({pair_id:{'A':a.id,'B':b.id}}))
        Path(td,'decisions-template.json').write_text(json.dumps({pair_id:{'verdict':'A'}}))
        try:
            decode_blind_decisions(Path(td))
        except ValueError as e:
            assert 'not replay-safe' in str(e)
        else:
            raise AssertionError('legacy id-keyed queue should be rejected')

    print('judge queue tests: PASS')

if __name__=='__main__':
    main()
