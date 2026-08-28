from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw

from evidence_selector import EvidenceAuthoritySelector
from phenotype_preference_evidence import PhenotypePreferenceEvidence
from review_evidence_queue import pair_id_for_phenotypes, phenotype_fingerprint

TIMES=(0,1)


@dataclass
class C:
    id:str
    value:int
    checks:dict
    route:str='recurrence'
    stage:str='explore'
    parent_id:str|None='root'


def render(c,t):
    im=Image.new('L',(50,50),0); d=ImageDraw.Draw(im)
    d.ellipse((5+c.value,8+t,25+c.value,28+t),outline=180,width=3)
    return im


def test_collect_mode_records_without_writing_queue_during_compare():
    a=C('a',2,{'valid':True},stage='start',parent_id=None)
    b=C('b',12,{'valid':True},parent_id='a')
    c=C('c',20,{'valid':True},parent_id='a')
    brief={'brief':'x','routes':['recurrence','family']}
    with TemporaryDirectory() as td:
        q=Path(td)/'pairs'
        s=EvidenceAuthoritySelector(
            render_frame=render,times=TIMES,queue_dir=q,max_pending_reviews=2,
            max_pending_reviews_per_group=1,collect_review_proposals=True,
        )
        s.compare(a,b,brief); s.compare(a,c,brief)
        assert len(s.review_proposals)==2
        assert [p.index for p in s.review_proposals]==[0,1]
        assert all(p.review_group=='route:recurrence' for p in s.review_proposals)
        assert not (q/'decisions.json').exists()


def test_extra_authoritative_evidence_promotes_without_collecting():
    a=C('a',2,{'valid':True},stage='start',parent_id=None)
    b=C('b',12,{'valid':True},parent_id='a')
    afr=[render(a,t) for t in TIMES]; bfr=[render(b,t) for t in TIMES]
    afp=phenotype_fingerprint(afr); bfp=phenotype_fingerprint(bfr)
    pid=pair_id_for_phenotypes(brief='x',times=TIMES,a_fingerprint=afp,b_fingerprint=bfp)
    ev=PhenotypePreferenceEvidence(
        pair_id=pid,phenotype_fingerprints=(afp,bfp),winner_fingerprint=bfp,
        source_class='human',source_id='reviewer',confidence='strong',
    )
    s=EvidenceAuthoritySelector(
        render_frame=render,times=TIMES,extra_evidence=[ev],collect_review_proposals=True,
    )
    decision=s.compare(a,b,{'brief':'x','routes':['recurrence','family']})
    assert decision.verdict=='b' and decision.confidence=='clear'
    assert s.review_proposals==[]


if __name__=='__main__':
    for name,fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn(); print(name,'PASS')
