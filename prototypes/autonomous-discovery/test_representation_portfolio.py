#!/usr/bin/env python3
from __future__ import annotations
import hashlib, io, json, random, tempfile
from pathlib import Path
import run
from decision_ledger import decode_blind_decision_dirs
from judge_queue import QueueingSelector
from pairwise_selector import DeterministicTemporalSelector, PairwiseSelector, PairwiseDecision, DimensionVote
from portfolio_runner import _arm_search, run_policy
from rng_streams import representation_rng

PARITY={
    'recurrence':('b17e7ba5a9c405546bd1f6d66ee6611aa44057bff08f677a403a8622afcdbe9f','025715fe49a84f4ca9d3cc1c047882ed6ce63ee960d101cdd11f225db5b8a475'),
    'family':('c69269733e540d9f39f2e0bfca1e0f7a698264efa54ce056a2727a46636bc461','b58d7a8cef473f10003af5bb80ac0de255fb5cb051c5ab41941494c6e5e6ecfe'),
}

class AlwaysTie(PairwiseSelector):
    name='always-tie'
    def compare(self,a,b,brief):
        return PairwiseDecision(a.id,b.id,'tie','defer',(DimensionVote('test','tie','force queue'),),self.name)

def png_hash(im):
    b=io.BytesIO(); im.save(b,format='PNG'); return hashlib.sha256(b.getvalue()).hexdigest()

def genome_hash(g):
    return hashlib.sha256(json.dumps(g,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    for route,(gh,ih) in PARITY.items():
        r=random.Random(260826); g=run.ROUTES[route]['seed'](r)
        assert genome_hash(g)==gh
        assert png_hash(run.draw_points(run.ROUTES[route]['render'](g,90),g['alpha']))==ih

    for route in ['recurrence','family','sheet','filament']:
        for seed in range(6):
            r=random.Random(seed); c=run.Candidate('x',route,'x',run.ROUTES[route]['seed'](r),None,'test'); run.evaluate_candidate(c,run.default_brief())
            assert c.checks['valid'],(route,seed,c.checks)

    r=random.Random(1); g=run.ROUTES['sheet']['seed'](r); g['nv']=4; c=run.Candidate('s','sheet','s',g,None,'test'); run.evaluate_candidate(c,run.default_brief()); assert not c.checks['valid']
    r=random.Random(2); g=run.ROUTES['filament']['seed'](r); g['sx']=12; c=run.Candidate('f','filament','f',g,None,'test'); run.evaluate_candidate(c,run.default_brief()); assert not c.checks['valid']

    a=representation_rng(77,'sheet','1','portfolio'); b=representation_rng(77,'sheet','1','portfolio'); _=representation_rng(77,'family','1','portfolio')
    assert [a.random() for _ in range(10)]==[b.random() for _ in range(10)]

    brief={'name':'test','artistic_intent':'living abstract form','eligible_routes':['recurrence','family','sheet','filament'],'route_first':'sheet','bbox_target':[.55,.82]}; selector=DeterministicTemporalSelector()
    shallow=_arm_search(brief,123,'sheet',6,selector,starts=2); deep=_arm_search(brief,123,'sheet',18,selector,starts=2)
    for cid,c in shallow['candidates'].items():
        assert cid in deep['candidates'] and deep['candidates'][cid].genome==c.genome

    with tempfile.TemporaryDirectory() as td:
        _,pr,_,_=run_policy(brief,123,Path(td)/'p','portfolio-equal',24,selector,starts=2)
        _,rr,_,_=run_policy(brief,123,Path(td)/'r','route-first',24,selector,starts=2)
        assert pr['routeBudgets']=={'family':6,'filament':6,'recurrence':6,'sheet':6}
        assert sum(x['attempts'] for x in pr['representationChampions'])==24
        assert rr['routeBudgets']=={'sheet':24} and rr['representationChampions'][0]['attempts']==24

    with tempfile.TemporaryDirectory() as td:
        q=QueueingSelector(AlwaysTie(),Path(td)/'q',run.render_candidate_frame,run.TIMES)
        ra=random.Random(10); rb=random.Random(11)
        a=run.Candidate('a','sheet','a',run.ROUTES['sheet']['seed'](ra),None,'t'); b=run.Candidate('b','filament','b',run.ROUTES['filament']['seed'](rb),None,'t'); run.evaluate_candidate(a,brief); run.evaluate_candidate(b,brief); q.compare(a,b,brief)
        doc=json.loads((Path(td)/'q'/'queue.json').read_text()); assert doc['pairs']
        assert set(doc['pairs'][0])=={'pairId','panel','briefName','times','promptVersion','instruction'}
        pair_id=doc['pairs'][0]['pairId']; d=json.loads((Path(td)/'q'/'decisions-template.json').read_text()); d['decisions'][pair_id]['verdict']='tie'; (Path(td)/'q'/'decisions-template.json').write_text(json.dumps(d))
        assert decode_blind_decision_dirs([Path(td)/'q'])[pair_id]=='tie'

    print('representation portfolio tests: PASS')

if __name__=='__main__': main()
