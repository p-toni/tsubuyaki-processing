import json
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw
from screened_search import DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS, DEFAULT_MIN_PROBES_PER_ROUTE, prepare_probe, resume_adaptive_search

R=("recurrence","orbit","family","sheet","filament")

@dataclass
class C:
    id:str
    route:str
    basin:str
    genome:dict
    checks:dict=field(default_factory=lambda:{"valid":True})

def gen(brief,seed,route,n):
    return [C(f"{route}-{i+1}",route,f"{route}-{i+1}",{"seed":seed,"i":i+1,"brief":brief.get("name")}) for i in range(n)], n

def render(c,t):
    im=Image.new("L",(70,70),0); d=ImageDraw.Draw(im); k=(sum(map(ord,c.route))+c.genome["i"]*3)%20
    d.line((5,10+k,60,50-k),fill=150+int(t)%80,width=3); return im

def fill_screen(out, keep):
    screen=Path(out)/"route-screen"
    sealed=json.loads((screen/"sealed-mapping.json").read_text())
    dec=json.loads((screen/"decisions-template.json").read_text())
    for lab,m in sealed["groups"].items():
        dec["decisions"][lab].update(verdict="keep" if m["route"] in keep else "drop", confidence="strong")
    (screen/"decisions-template.json").write_text(json.dumps(dec))

def fake_adaptive(brief,seed,out,starts,selector=None):
    assert set(c.route for c in starts)==set(brief["routes"])
    out.mkdir(parents=True,exist_ok=True)
    report={"routes":brief["routes"],"startCount":len(starts),"startsByRoute":{r:sum(c.route==r for c in starts) for r in brief["routes"]}}
    return object(), report

def test_two_probe_default_and_authoritative_narrowing():
    assert DEFAULT_MIN_PROBES_PER_ROUTE==2
    with TemporaryDirectory() as td:
        s=prepare_probe(brief={"name":"x"},seed=9,out_dir=td,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        assert s["probeBudget"]==10
        assert s["minimumPerRoute"]==2
        assert set(s["probeAllocation"].values())=={2}
        fill_screen(td,{"orbit"})
        rep=resume_adaptive_search(out_dir=td,total_start_budget=18,source_class="human",source_id="reviewer",render_frame=render,generate_route_archive=gen,run_search_from_starts=fake_adaptive)
        assert rep["narrowingAuthorized"]
        assert rep["activeRoutes"]==["orbit"]
        assert rep["additionalStartsByRoute"]["orbit"]==8
        assert rep["adaptiveSearch"]["startCount"]==10
        assert rep["probeReplay"]["orbit"]["sourcePrefixVerified"]
        assert rep["probeReplay"]["orbit"]["phenotypePrefixVerified"]
        assert rep["candidatePromotionMode"]=="legacy-default"

def test_explicit_four_probe_override_remains_supported():
    with TemporaryDirectory() as td:
        s=prepare_probe(brief={"name":"x"},seed=9,out_dir=td,minimum_per_route=4,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        assert s["probeBudget"]==20
        assert set(s["probeAllocation"].values())=={4}

def test_same_model_screen_remains_broad():
    with TemporaryDirectory() as td:
        prepare_probe(brief={"name":"x"},seed=9,out_dir=td,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        fill_screen(td,{"orbit"})
        rep=resume_adaptive_search(out_dir=td,total_start_budget=15,source_class="same-model",source_id="judge",render_frame=render,generate_route_archive=gen,run_search_from_starts=fake_adaptive)
        assert not rep["narrowingAuthorized"]
        assert set(rep["activeRoutes"])==set(R)
        assert rep["adaptiveSearch"]["startCount"]==15

def test_probe_budget_cannot_undercut_declared_minimum():
    with TemporaryDirectory() as td:
        try:
            prepare_probe(brief={"name":"x"},seed=9,out_dir=td,probe_budget=9,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        except ValueError as e:
            assert "need >= 10" in str(e)
        else:
            raise AssertionError("expected probe minimum failure")

def test_one_probe_is_explicit_not_default():
    with TemporaryDirectory() as td:
        s=prepare_probe(brief={"name":"x"},seed=9,out_dir=td,minimum_per_route=1,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        assert s["probeBudget"]==5
        assert s["minimumPerRoute"]==1

def test_candidate_evidence_options_require_authority_mode():
    with TemporaryDirectory() as td:
        prepare_probe(brief={"name":"x"},seed=9,out_dir=td,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        fill_screen(td,{"orbit"})
        try:
            resume_adaptive_search(
                out_dir=td,total_start_budget=18,source_class="human",source_id="reviewer",
                candidate_review_queue=Path(td)/"candidate-review",
                render_frame=render,generate_route_archive=gen,run_search_from_starts=fake_adaptive,
            )
        except ValueError as e:
            assert "require evidence_authoritative_promotion=True" in str(e)
        else:
            raise AssertionError("expected candidate-evidence mode guard")

def test_evidence_authority_selector_reaches_adaptive_search_with_lazy_default():
    assert DEFAULT_MAX_PENDING_CANDIDATE_REVIEWS==2
    with TemporaryDirectory() as td:
        prepare_probe(brief={"name":"x"},seed=9,out_dir=td,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        fill_screen(td,{"orbit"})
        queue=Path(td)/"candidate-review"
        def evidence_adaptive(brief,seed,out,starts,selector=None):
            from evidence_selector import EvidenceAuthoritySelector
            assert isinstance(selector,EvidenceAuthoritySelector)
            assert selector.queue_dir==queue
            assert selector.max_pending_reviews==2
            return fake_adaptive(brief,seed,out,starts,selector)
        rep=resume_adaptive_search(
            out_dir=td,total_start_budget=18,source_class="human",source_id="reviewer",
            evidence_authoritative_promotion=True,candidate_review_queue=queue,
            render_frame=render,generate_route_archive=gen,run_search_from_starts=evidence_adaptive,
        )
        assert rep["narrowingAuthorized"]
        assert rep["candidatePromotionMode"]=="phenotype-evidence-authority-v1"
        assert rep["candidateReviewQueue"]==str(queue)
        assert rep["candidateEvidenceDirs"]==[]
        assert rep["candidateMaxPendingReviews"]==2

def test_explicit_one_review_cap_remains_supported():
    with TemporaryDirectory() as td:
        prepare_probe(brief={"name":"x"},seed=9,out_dir=td,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        fill_screen(td,{"orbit"})
        queue=Path(td)/"candidate-review"
        def evidence_adaptive(brief,seed,out,starts,selector=None):
            assert selector.max_pending_reviews==1
            return fake_adaptive(brief,seed,out,starts,selector)
        rep=resume_adaptive_search(
            out_dir=td,total_start_budget=18,source_class="human",source_id="reviewer",
            evidence_authoritative_promotion=True,candidate_review_queue=queue,candidate_max_pending_reviews=1,
            render_frame=render,generate_route_archive=gen,run_search_from_starts=evidence_adaptive,
        )
        assert rep["candidateMaxPendingReviews"]==1

def test_invalid_candidate_review_cap_fails_closed():
    with TemporaryDirectory() as td:
        prepare_probe(brief={"name":"x"},seed=9,out_dir=td,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        fill_screen(td,{"orbit"})
        try:
            resume_adaptive_search(
                out_dir=td,total_start_budget=18,source_class="human",source_id="reviewer",
                evidence_authoritative_promotion=True,candidate_review_queue=Path(td)/"candidate-review",
                candidate_max_pending_reviews=0,
                render_frame=render,generate_route_archive=gen,run_search_from_starts=fake_adaptive,
            )
        except ValueError as e:
            assert "candidate_max_pending_reviews" in str(e)
        else:
            raise AssertionError("expected review-cap guard")

def test_replay_detects_changed_source_or_phenotype():
    with TemporaryDirectory() as td:
        prepare_probe(brief={"name":"x"},seed=9,out_dir=td,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        fill_screen(td,{"family"})
        def bad_gen(brief,seed,route,n):
            xs,_=gen(brief,seed,route,n)
            if route=="family": xs[0].genome["i"]=999
            return xs,n
        try:
            resume_adaptive_search(out_dir=td,total_start_budget=18,source_class="human",source_id="reviewer",render_frame=render,generate_route_archive=bad_gen,run_search_from_starts=fake_adaptive)
        except RuntimeError as e:
            assert "prefix changed" in str(e)
        else:
            raise AssertionError("expected replay mismatch")

if __name__=="__main__":
    for name,fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn(); print(name,"PASS")
