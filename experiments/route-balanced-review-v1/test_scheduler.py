#!/usr/bin/env python3
"""Focused regression for deferred route-balanced review scheduling."""
from __future__ import annotations
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('route_balanced_reproduce',HERE/'reproduce.py')
if SPEC is None or SPEC.loader is None: raise RuntimeError('could not load reproduce.py')
mod=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(mod)

@dataclass
class C:
    id:str
    route:str
    value:int
    checks:dict


def render(c,t):
    im=Image.new('L',(48,48),0); d=ImageDraw.Draw(im)
    d.ellipse((4+c.value,8,20+c.value,24),outline=180+int(t)*10,width=3)
    return im


def main():
    times=(0,1)
    brief={'brief':'living mathematical form','routes':['recurrence','family','sheet']}
    pairs=[
        (C('r0','recurrence',1,{'valid':True}),C('r1','recurrence',5,{'valid':True})),
        (C('r0b','recurrence',2,{'valid':True}),C('r2','recurrence',8,{'valid':True})),
        (C('f0','family',10,{'valid':True}),C('f1','family',14,{'valid':True})),
        (C('s0','sheet',18,{'valid':True}),C('s1','sheet',22,{'valid':True})),
    ]
    with TemporaryDirectory() as td:
        q=Path(td)
        selector=mod.DeferredRouteScheduler(render_frame=render,times=times,queue_dir=q,batch_size=2)
        for a,b in pairs: selector.compare(a,b,brief)
        chosen=selector.flush()
        assert chosen==['route:family','route:sheet'],chosen
        decisions=json.loads((q/'decisions.json').read_text())
        assert len(decisions['decisions'])==2
        sealed=json.loads((q/'sealed-mapping.json').read_text())
        assert sorted(sealed['reviewGroups'].values())==['route:family','route:sheet']
        queue=json.loads((q/'queue.json').read_text())
        assert 'reviewGroups' not in queue
        assert all('route:' not in json.dumps(item) for item in queue['pairs'].values())
    print('deferred scheduler grouping PASS')


if __name__=='__main__': main()
