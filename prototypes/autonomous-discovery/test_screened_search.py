import json
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw
from screened_search import prepare_probe, resume_adaptive_search

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

def test_four_probe_minimum_and_authoritative_narrowing():
    with TemporaryDirectory() as td:
        s=prepare_probe(brief={"name":"x"},seed=9,out_dir=td,minimum_per_route=4,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        assert s["probeBudget"]==20
        assert set(s["probeAllocation"].values())=={4}
        fill_screen(td,{"orbit"})
        rep=resume_adaptive_search(out_dir=td,total_start_budget=26,source_class="human",source_id="reviewer",render_frame=render,generate_route_archive=gen,run_search_from_starts=fake_adaptive)
        assert rep["narrowingAuthorized"]
        assert rep["activeRoutes"]==["orbit"]
        assert rep["additionalStartsByRoute"]["orbit"]==6
        assert rep["adaptiveSearch"]["startCount"]==10
        assert rep["probeReplay"]["orbit"]["sourcePrefixVerified"]
        assert rep["probeReplay"]["orbit"]["phenotypePrefixVerified"]

def test_same_model_screen_remains_broad():
    with TemporaryDirectory() as td:
        prepare_probe(brief={"name":"x"},seed=9,out_dir=td,minimum_per_route=4,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        fill_screen(td,{"orbit"})
        rep=resume_adaptive_search(out_dir=td,total_start_budget=25,source_class="same-model",source_id="judge",render_frame=render,generate_route_archive=gen,run_search_from_starts=fake_adaptive)
        assert not rep["narrowingAuthorized"]
        assert set(rep["activeRoutes"])==set(R)
        assert rep["adaptiveSearch"]["startCount"]==25

def test_probe_budget_cannot_undercut_minimum():
    with TemporaryDirectory() as td:
        try:
            prepare_probe(brief={"name":"x"},seed=9,out_dir=td,probe_budget=19,minimum_per_route=4,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        except ValueError as e:
            assert "need >= 20" in str(e)
        else:
            raise AssertionError("expected probe minimum failure")

def test_replay_detects_changed_source_or_phenotype():
    with TemporaryDirectory() as td:
        prepare_probe(brief={"name":"x"},seed=9,out_dir=td,minimum_per_route=4,routes=R,times=(0,1),render_frame=render,generate_route_archive=gen)
        fill_screen(td,{"family"})
        def bad_gen(brief,seed,route,n):
            xs,_=gen(brief,seed,route,n)
            if route=="family": xs[0].genome["i"]=999
            return xs,n
        try:
            resume_adaptive_search(out_dir=td,total_start_budget=26,source_class="human",source_id="reviewer",render_frame=render,generate_route_archive=bad_gen,run_search_from_starts=fake_adaptive)
        except RuntimeError as e:
            assert "prefix changed" in str(e)
        else:
            raise AssertionError("expected replay mismatch")

if __name__=="__main__":
    for name,fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn(); print(name,"PASS")
