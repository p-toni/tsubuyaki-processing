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
    id:str; value:int; checks:dict

def render(c,t):
    im=Image.new('L',(50,50),0); d=ImageDraw.Draw(im); d.ellipse((5+c.value,8,25+c.value,28),outline=180+int(t)*10,width=3); return im

def fill_winner_for_candidate(d,pair_id,candidate_id,source='human',confidence='strong',source_id='reviewer'):
    sealed=json.loads((Path(d)/'sealed-mapping.json').read_text()); dec=json.loads((Path(d)/'decisions.json').read_text())
    label=next(l for l,m in sealed['pairs'][pair_id].items() if m['candidateId']==candidate_id)
    dec['decisions'][pair_id].update(verdict=label,sourceClass=source,sourceId=source_id,confidence=confidence)
    (Path(d)/'decisions.json').write_text(json.dumps(dec))

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

def test_hard_validity_remains_authoritative():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':False})
    s=EvidenceAuthoritySelector(render_frame=render,times=(0,1))
    assert s.compare(a,b,{'brief':'x'}).verdict=='a'

def test_conflicting_authoritative_sources_defer():
    a=C('a',2,{'valid':True}); b=C('b',12,{'valid':True}); times=(0,1); brief='x'
    with TemporaryDirectory() as t1, TemporaryDirectory() as t2:
        d1=Path(t1); d2=Path(t2)
        p1=create_review_bundle(d1,brief=brief,times=times,a_frames=[render(a,t) for t in times],b_frames=[render(b,t) for t in times],a_candidate_id=a.id,b_candidate_id=b.id)
        p2=create_review_bundle(d2,brief=brief,times=times,a_frames=[render(a,t) for t in times],b_frames=[render(b,t) for t in times],a_candidate_id=a.id,b_candidate_id=b.id)
        fill_winner_for_candidate(d1,p1,a.id,'human','strong','human-1')
        fill_winner_for_candidate(d2,p2,b.id,'independent-model','strong','judge-2')
        s=EvidenceAuthoritySelector(render_frame=render,times=times,evidence_dirs=[d1,d2])
        d=s.compare(a,b,{'brief':brief}); assert d.verdict=='tie' and d.confidence=='defer'

if __name__=='__main__':
    for n,f in sorted(globals().items()):
        if n.startswith('test_'): f(); print(n,'PASS')
