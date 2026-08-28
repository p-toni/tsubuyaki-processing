import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw
from route_screen_queue import build_route_screen, decode_route_screen

@dataclass
class C:
    id: str
    value: int

def render(c, t):
    im = Image.new("L", (60, 60), 0); d = ImageDraw.Draw(im)
    d.ellipse((5+c.value, 10, 35+c.value, 40), outline=120+int(t)%100, width=3)
    return im


def test_roundtrip_and_sealing():
    with TemporaryDirectory() as td:
        p = Path(td)
        q = build_route_screen(
            brief={"brief": "a living ring with a split"},
            route_candidates={
                "recurrence": [C("r1", 1), C("r2", 2)],
                "orbit": [C("o1", 4), C("o2", 5)],
                "family": [C("f1", 7), C("f2", 8)],
            },
            render_frame=render, times=(0, 1, 2), out_dir=p,
        )
        assert Path(q["panel"]).exists()
        sealed = json.loads((p / "sealed-mapping.json").read_text())
        assert set(x["route"] for x in sealed["groups"].values()) == {"recurrence", "orbit", "family"}
        decisions = json.loads((p / "decisions-template.json").read_text())
        labs = list(decisions["decisions"])
        decisions["decisions"][labs[0]].update(verdict="keep", confidence="strong")
        decisions["decisions"][labs[1]].update(verdict="drop", confidence="low")
        decisions["decisions"][labs[2]].update(verdict="defer", confidence="defer")
        (p / "decisions-template.json").write_text(json.dumps(decisions))
        out = decode_route_screen(p, source_class="human", source_id="reviewer")
        assert len(out) == 3
        assert sorted(e.verdict for e in out) == ["defer", "drop", "keep"]
        assert sum(e.authoritative for e in out) == 1
        evidence_doc = json.loads((p / "route-evidence.json").read_text())
        assert evidence_doc["sourceClass"] == "human"
        assert evidence_doc["sourceId"] == "reviewer"
        assert len(evidence_doc["evidence"]) == 3
        assert all(item["groupFingerprint"] for item in evidence_doc["evidence"])


def test_incomplete_decisions_are_not_invented():
    with TemporaryDirectory() as td:
        p = Path(td)
        build_route_screen(
            brief={"brief": "test"},
            route_candidates={"a": [C("a",1)], "b": [C("b",2)]},
            render_frame=render, times=(0,), out_dir=p,
        )
        out = decode_route_screen(p, source_class="human", source_id="reviewer")
        assert out == []


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn(); print(name, "PASS")
