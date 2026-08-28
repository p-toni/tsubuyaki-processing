import json
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw

from screened_search import prepare_probe, resume_adaptive_search

ROUTES=('recurrence','family')
TIMES=(0,1)


@dataclass
class C:
    id:str
    route:str
    basin:str
    genome:dict
    checks:dict=field(default_factory=lambda:{'valid':True})
    features:dict=field(default_factory=dict)
    stage:str='start'
    parent_id:str|None=None


def gen(brief,seed,route,n):
    return [C(f'{route}-{i+1}',route,f'{route}-{i+1}',{'seed':seed,'i':i+1}) for i in range(n)],n


def render(c,t):
    im=Image.new('L',(60,60),0); d=ImageDraw.Draw(im)
    k=(sum(map(ord,c.id))+int(t)*5)%20
    d.line((5,8+k,52,45-k),fill=180,width=3)
    return im


def fill_screen(out):
    screen=Path(out)/'route-screen'
    sealed=json.loads((screen/'sealed-mapping.json').read_text())
    dec=json.loads((screen/'decisions-template.json').read_text())
    for label in sealed['groups']:
        dec['decisions'][label].update(verdict='keep',confidence='strong')
    (screen/'decisions-template.json').write_text(json.dumps(dec))


def comparing_adaptive(brief,seed,out,starts,selector=None):
    out.mkdir(parents=True,exist_ok=True)
    a=C('root','recurrence','root',{'v':1},stage='start',parent_id=None)
    b=C('child-b','recurrence','b',{'v':2},stage='explore',parent_id='root')
    c=C('child-c','recurrence','c',{'v':3},stage='explore',parent_id='root')
    selector.compare(a,b,brief); selector.compare(a,c,brief)
    return object(),{'winner':a.id}


def test_opt_in_screened_path_flushes_one_pair_matrix_triad_after_search():
    with TemporaryDirectory() as td:
        root=Path(td)
        prepare_probe(
            brief={'brief':'x'},seed=9,out_dir=root,minimum_per_route=1,routes=ROUTES,times=TIMES,
            render_frame=render,generate_route_archive=gen,
        )
        fill_screen(root)
        rep=resume_adaptive_search(
            out_dir=root,total_start_budget=4,source_class='human',source_id='route-reviewer',
            evidence_authoritative_promotion=True,candidate_pair_matrix_triads=True,
            render_frame=render,generate_route_archive=gen,run_search_from_starts=comparing_adaptive,
        )
        assert rep['candidateReviewSchedulingMode']=='pair-matrix-triad-opt-in-v1'
        assert rep['candidatePairMatrixTriads'] is True
        assert len(rep['candidateQueuedReviewTasks'])==1
        assert rep['candidateQueuedReviewTasks'][0]['kind']=='triad'
        assert rep['candidateReviewQueue']==str(root/'candidate-review')
        assert rep['candidateTriadReviewQueue']==str(root/'candidate-triad-review')
        assert not (root/'candidate-review'/'decisions.json').exists()
        triad_decisions=json.loads((root/'candidate-triad-review'/'decisions.json').read_text())['decisions']
        assert len(triad_decisions)==1


def test_default_evidence_authority_path_remains_eager_pair_queue_only():
    with TemporaryDirectory() as td:
        root=Path(td)
        prepare_probe(
            brief={'brief':'x'},seed=9,out_dir=root,minimum_per_route=1,routes=ROUTES,times=TIMES,
            render_frame=render,generate_route_archive=gen,
        )
        fill_screen(root)
        pairq=root/'candidate-review'
        rep=resume_adaptive_search(
            out_dir=root,total_start_budget=4,source_class='human',source_id='route-reviewer',
            evidence_authoritative_promotion=True,candidate_review_queue=pairq,
            render_frame=render,generate_route_archive=gen,run_search_from_starts=comparing_adaptive,
        )
        assert rep['candidateReviewSchedulingMode']=='eager-pair-v1'
        assert rep['candidatePairMatrixTriads'] is False
        assert rep['candidateTriadReviewQueue'] is None
        assert rep['candidateQueuedReviewTasks']==[]
        pair_decisions=json.loads((pairq/'decisions.json').read_text())['decisions']
        assert len(pair_decisions)==1


def test_triad_scheduler_requires_evidence_authority_mode():
    with TemporaryDirectory() as td:
        root=Path(td)
        prepare_probe(
            brief={'brief':'x'},seed=9,out_dir=root,minimum_per_route=1,routes=ROUTES,times=TIMES,
            render_frame=render,generate_route_archive=gen,
        )
        fill_screen(root)
        try:
            resume_adaptive_search(
                out_dir=root,total_start_budget=4,source_class='human',source_id='route-reviewer',
                candidate_pair_matrix_triads=True,
                render_frame=render,generate_route_archive=gen,run_search_from_starts=comparing_adaptive,
            )
        except ValueError as exc:
            assert 'require evidence_authoritative_promotion=True' in str(exc)
        else:
            raise AssertionError('expected evidence-authority guard')


def test_incomplete_triad_queue_fails_closed():
    with TemporaryDirectory() as td:
        root=Path(td)
        prepare_probe(
            brief={'brief':'x'},seed=9,out_dir=root,minimum_per_route=1,routes=ROUTES,times=TIMES,
            render_frame=render,generate_route_archive=gen,
        )
        fill_screen(root)
        triadq=root/'candidate-triad-review'; triadq.mkdir()
        (triadq/'decisions.json').write_text('{}')
        try:
            resume_adaptive_search(
                out_dir=root,total_start_budget=4,source_class='human',source_id='route-reviewer',
                evidence_authoritative_promotion=True,candidate_pair_matrix_triads=True,
                candidate_triad_review_queue=triadq,
                render_frame=render,generate_route_archive=gen,run_search_from_starts=comparing_adaptive,
            )
        except ValueError as exc:
            assert 'triad review queue is incomplete' in str(exc)
        else:
            raise AssertionError('expected incomplete triad queue guard')


if __name__=='__main__':
    for name,fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn(); print(name,'PASS')
