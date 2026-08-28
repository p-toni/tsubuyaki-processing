import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image,ImageDraw
from evidence_selector import EvidenceAuthoritySelector
from phenotype_evidence_replay import decode_review_phenotype_evidence
from pairwise_selector import PairwiseSelector,PairwiseDecision,DimensionVote
from review_evidence_queue import create_review_bundle,phenotype_fingerprint

@dataclass
class C:
    id:str; value:int; checks:dict; route:str='recurrence'

def render(c,t):
    im=Image.new('L',(50,50),0); d=ImageDraw.Draw(im); d.ellipse((5+c.value,8,25+c.value,28),outline=180+int(t)*10,width=3); return im

def _decision_doc(d): return json.loads((Path(d)/'decisions.json').read_text())

def fill_winner_for_candidate(d,pair_id,candidate_id,source='human',confidence='strong',source_id='reviewer'):
    sealed=json.loads((Path(d)/'sealed-mapping.json').read_text()); dec=_decision_doc(d)
    label=next(l for l,m in sealed['pairs'][pair_id].items() if m['candidateId']==candidate_id)
    dec['decisions'][pair_id].update(verdict=label,sourceClass=source,sourceId=source_id,confidence=confidence)
    (Path(d)/'decisions.json').write_text(json.dumps(dec))

def fill_tie(d,pair_id,source='human',confidence='strong',source_id='reviewer'):
    dec=_decision_doc(d); dec['decisions'][pair_id].update(verdict='tie',sourceClass=source,sourceId=source_id,confidence=confidence)
    (Path(d)/'decisions.json').write_text(json.dumps(dec))

def pending_count(d):
    p=Path(d)/'decisions.json'
    if not p.exists(): return 0
    return sum(x.get('verdict') is None for x in json.loads(p.read_text()).get('decisions',{}).values())

class Advisory(PairwiseSelector):
    name='advisory'
    def compare(self,a,b,brief): return PairwiseDecision(a.id,b.id,'b','clear',(DimensionVote('proxy','b','proxy'),),self.name)

def test_reversal_replay_tracks_actual_phenotype():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); times=(0,1,2); brief='one living form'
    with TemporaryDirectory() as td:
        pid=create_review_bundle(Path(td),brief=brief,times=times,a_frames=[render(a,t) for t in times],b_frames=[render(b,t) for t in times],a_candidate_id=a.id,b_candidate_id=b.id)
        fill_winner_for_candidate(td,pid,a.id)
        ev=decode_review_phenotype_evidence(Path(td)); afp=phenotype_fingerprint([render(a,t) for t in times])
        assert ev[0].winner_fingerprint==afp
        s=EvidenceAuthoritySelector(render_frame=render,times=times,evidence_dirs=[Path(td)])
        assert s.compare(a,b,{'brief':brief}).verdict=='a'
        assert s.compare(b,a,{'brief':brief}).verdict=='b'

def test_same_model_and_low_confidence_cannot_promote():
    for source,confidence in [('same-model','strong'),('human','low')]:
        a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); times=(0,1); brief='x'
        with TemporaryDirectory() as td:
            pid=create_review_bundle(Path(td),brief=brief,times=times,a_frames=[render(a,t) for t in times],b_frames=[render(b,t) for t in times],a_candidate_id=a.id,b_candidate_id=b.id)
            fill_winner_for_candidate(td,pid,b.id,source,confidence)
            s=EvidenceAuthoritySelector(render_frame=render,times=times,evidence_dirs=[Path(td)],advisory=Advisory())
            d=s.compare(a,b,{'brief':brief}); assert d.verdict=='tie' and d.confidence=='defer'

def test_missing_evidence_queues_but_does_not_promote():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); times=(0,1)
    with TemporaryDirectory() as td:
        s=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=Path(td),advisory=Advisory())
        d=s.compare(a,b,{'brief':'x'}); assert d.verdict=='tie'
        q=json.loads((Path(td)/'queue.json').read_text()); assert len(q['pairs'])==1

def test_authoritative_tie_is_terminal_and_frees_lazy_slot():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); c=C('c',20,{'valid':True}); times=(0,1); brief='x'
    with TemporaryDirectory() as td:
        q=Path(td)
        s=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=q,max_pending_reviews=1)
        d=s.compare(a,b,{'brief':brief}); assert d.verdict=='tie' and pending_count(q)==1
        pid=next(iter(_decision_doc(q)['decisions']))
        fill_tie(q,pid)
        replay=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=q,max_pending_reviews=1)
        resolved=replay.compare(a,b,{'brief':brief})
        assert resolved.verdict=='tie' and resolved.confidence=='clear'
        replay.compare(a,c,{'brief':brief})
        assert pending_count(q)==1
        assert len(_decision_doc(q)['decisions'])==2

def test_lazy_queue_avoids_pairs_made_unreachable_by_promotion():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); c=C('c',20,{'valid':True}); times=(0,1); brief='x'
    with TemporaryDirectory() as lazy_td, TemporaryDirectory() as eager_td:
        lazy=Path(lazy_td); eager=Path(eager_td)
        s=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=lazy,max_pending_reviews=1)
        s.compare(a,b,{'brief':brief}); s.compare(a,c,{'brief':brief})
        assert len(_decision_doc(lazy)['decisions'])==1 and pending_count(lazy)==1
        first=next(iter(_decision_doc(lazy)['decisions'])); fill_winner_for_candidate(lazy,first,b.id)
        replay=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=lazy,max_pending_reviews=1)
        assert replay.compare(a,b,{'brief':brief}).verdict=='b'
        replay.compare(b,c,{'brief':brief})
        assert len(_decision_doc(lazy)['decisions'])==2 and pending_count(lazy)==1

        e=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=eager)
        e.compare(a,b,{'brief':brief}); e.compare(a,c,{'brief':brief})
        assert len(_decision_doc(eager)['decisions'])==2
        first_e=next(pid for pid,item in json.loads((eager/'sealed-mapping.json').read_text())['pairs'].items() if {m['candidateId'] for m in item.values()}=={'a','b'})
        fill_winner_for_candidate(eager,first_e,b.id)
        e2=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=eager)
        e2.compare(b,c,{'brief':brief})
        assert len(_decision_doc(eager)['decisions'])==3

def test_route_group_cap_spreads_a_lazy_batch_without_reordering_search():
    r0=C('r0',2,{'valid':True},'recurrence'); r1=C('r1',8,{'valid':True},'recurrence'); r2=C('r2',14,{'valid':True},'recurrence')
    f0=C('f0',20,{'valid':True},'family'); f1=C('f1',26,{'valid':True},'family'); times=(0,1); brief={'brief':'x','routes':['recurrence','family']}
    with TemporaryDirectory() as td:
        q=Path(td)
        s=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=q,max_pending_reviews=2,max_pending_reviews_per_group=1)
        s.compare(r0,r1,brief)
        blocked=s.compare(r0,r2,brief)
        s.compare(f0,f1,brief)
        assert pending_count(q)==2
        sealed=json.loads((q/'sealed-mapping.json').read_text())
        groups=[sealed['reviewGroups'][pid] for pid,item in _decision_doc(q)['decisions'].items() if item.get('verdict') is None]
        assert sorted(groups)==['route:family','route:recurrence']
        assert 'group cap' in blocked.dimensions[0].reason

def test_route_group_cap_survives_partial_replay():
    r0=C('r0',2,{'valid':True},'recurrence'); r1=C('r1',8,{'valid':True},'recurrence'); r2=C('r2',14,{'valid':True},'recurrence')
    f0=C('f0',20,{'valid':True},'family'); f1=C('f1',26,{'valid':True},'family'); f2=C('f2',32,{'valid':True},'family'); times=(0,1); brief={'brief':'x','routes':['recurrence','family']}
    with TemporaryDirectory() as td:
        q=Path(td)
        s=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=q,max_pending_reviews=2,max_pending_reviews_per_group=1)
        s.compare(r0,r1,brief); s.compare(f0,f1,brief)
        sealed=json.loads((q/'sealed-mapping.json').read_text())
        recurrence_pid=next(pid for pid,g in sealed['reviewGroups'].items() if g=='route:recurrence')
        fill_tie(q,recurrence_pid)
        replay=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=q,max_pending_reviews=2,max_pending_reviews_per_group=1)
        replay.compare(r0,r1,brief)
        replay.compare(f0,f2,brief)
        replay.compare(r0,r2,brief)
        pending=[pid for pid,item in _decision_doc(q)['decisions'].items() if item.get('verdict') is None]
        groups=[json.loads((q/'sealed-mapping.json').read_text())['reviewGroups'][pid] for pid in pending]
        assert sorted(groups)==['route:family','route:recurrence']

def test_route_group_cap_does_not_reduce_single_route_k2():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); c=C('c',20,{'valid':True}); times=(0,1); brief={'brief':'x','routes':['recurrence']}
    with TemporaryDirectory() as td:
        q=Path(td)
        s=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=q,max_pending_reviews=2,max_pending_reviews_per_group=1)
        s.compare(a,b,brief); s.compare(a,c,brief)
        assert pending_count(q)==2

def test_resolved_weak_queue_evidence_is_not_noop_requeued():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); times=(0,1); brief='x'
    with TemporaryDirectory() as td:
        q=Path(td)
        pid=create_review_bundle(q,brief=brief,times=times,a_frames=[render(a,t) for t in times],b_frames=[render(b,t) for t in times],a_candidate_id=a.id,b_candidate_id=b.id)
        fill_winner_for_candidate(q,pid,b.id,'human','low','reviewer-low')
        before=_decision_doc(q)
        s=EvidenceAuthoritySelector(render_frame=render,times=times,queue_dir=q,max_pending_reviews=1)
        d=s.compare(a,b,{'brief':brief})
        after=_decision_doc(q)
        assert d.verdict=='tie' and d.confidence=='defer'
        assert before==after and pending_count(q)==0 and len(after['decisions'])==1
        assert 'new independent review bundle' in d.dimensions[0].reason

def test_weak_external_evidence_can_queue_fresh_independent_review():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); times=(0,1); brief='x'
    with TemporaryDirectory() as evidence_td, TemporaryDirectory() as queue_td:
        evidence=Path(evidence_td); q=Path(queue_td)
        pid=create_review_bundle(evidence,brief=brief,times=times,a_frames=[render(a,t) for t in times],b_frames=[render(b,t) for t in times],a_candidate_id=a.id,b_candidate_id=b.id)
        fill_winner_for_candidate(evidence,pid,b.id,'human','low','reviewer-low')
        s=EvidenceAuthoritySelector(render_frame=render,times=times,evidence_dirs=[evidence],queue_dir=q,max_pending_reviews=1)
        d=s.compare(a,b,{'brief':brief})
        assert d.verdict=='tie' and pending_count(q)==1 and len(_decision_doc(q)['decisions'])==1

def test_hard_validity_remains_authoritative():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':False})
    s=EvidenceAuthoritySelector(render_frame=render,times=(0,1))
    assert s.compare(a,b,{'brief':'x'}).verdict=='a'

def test_conflicting_authoritative_sources_defer_without_requeue():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); times=(0,1); brief='x'
    with TemporaryDirectory() as t1, TemporaryDirectory() as t2, TemporaryDirectory() as tq:
        d1=Path(t1); d2=Path(t2); q=Path(tq)
        p1=create_review_bundle(d1,brief=brief,times=times,a_frames=[render(a,t) for t in times],b_frames=[render(b,t) for t in times],a_candidate_id=a.id,b_candidate_id=b.id)
        p2=create_review_bundle(d2,brief=brief,times=times,a_frames=[render(a,t) for t in times],b_frames=[render(b,t) for t in times],a_candidate_id=a.id,b_candidate_id=b.id)
        fill_winner_for_candidate(d1,p1,a.id,'human','strong','human-1')
        fill_winner_for_candidate(d2,p2,b.id,'independent-model','strong','judge-2')
        s=EvidenceAuthoritySelector(render_frame=render,times=times,evidence_dirs=[d1,d2],queue_dir=q,max_pending_reviews=1)
        d=s.compare(a,b,{'brief':brief}); assert d.verdict=='tie' and d.confidence=='defer'
        assert not (q/'decisions.json').exists()

if __name__=='__main__':
    for n,f in sorted(globals().items()):
        if n.startswith('test_'): f(); print(n,'PASS')
