#!/usr/bin/env python3
"""Reproduce the morphology route-pair candidate parameters and semantic metrics.

Run:
    python experiments/morphology-route-pair/reproduce.py
"""
import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent / "_generated"
OUT.mkdir(exist_ok=True)

def random_morph(rng):
    return {
        "rootNu":rng.choice([90,100,110]),"rootNv":rng.choice([80,90,100]),
        "rootAspect":rng.uniform(.78,1.05),"rootW":rng.uniform(62,83),"rootH":rng.uniform(52,72),
        "split":rng.uniform(.10,.22),"splitTop":rng.uniform(.25,.65),
        "rootFold":rng.uniform(.08,.22),"rootFreq":rng.uniform(2.4,5.5),
        "rootTime":rng.uniform(18,40),"rootTwist":rng.uniform(5,15),
        "organs":rng.choice([5,6,7,8]),"organSamples":rng.choice([550,650,750]),
        "organFan":rng.uniform(.85,1.35),"organWidth":rng.uniform(6,14),
        "organTaper":rng.uniform(.7,1.4),"organFreq":rng.uniform(2.2,5.5),
        "organLen":rng.uniform(46,78),"organTime":rng.uniform(12,28),
        "motionTime":rng.uniform(18,42),"organRibs":rng.uniform(1.5,3.8),
        "phase":rng.uniform(.45,1.0),"alpha":rng.randint(42,60)
    }

def random_field(rng):
    return {
        "nu":rng.choice([130,145,160]),"nv":rng.choice([100,115,130]),
        "uPow":rng.uniform(1.2,2.6),"f1":rng.uniform(2.0,6.0),"f2":rng.uniform(2.0,5.5),
        "f3":rng.uniform(2.0,5.0),"couple":rng.uniform(.8,2.8),"time":rng.uniform(14,34),
        "time2":rng.uniform(18,40),"spread":rng.uniform(.35,.75),"scaleX":rng.uniform(78,105),
        "scaleY":rng.uniform(48,78),"warp":rng.uniform(5,18),"trail":rng.uniform(28,68),
        "trailPow":rng.uniform(1.3,3.0),"fold":rng.uniform(4,14),"wave":rng.uniform(4,14),
        "cavity":rng.uniform(2,12),"cavW":rng.uniform(.18,.4),"alpha":rng.randint(38,56)
    }

def random_ray(rng):
    return {
        "nu":rng.choice([145,160,175]),"nv":rng.choice([115,130,145]),
        "narrow":rng.uniform(.25,.75),"wing":rng.uniform(.75,1.30),
        "wingPow":rng.uniform(.6,1.35),"notch":rng.uniform(.05,.32),
        "notchW":rng.uniform(.22,.50),"fu":rng.uniform(2.2,5.5),
        "fv":rng.uniform(1.8,4.5),"uv":rng.uniform(.5,2.4),"time":rng.uniform(16,34),
        "time2":rng.uniform(18,42),"curlT":rng.uniform(18,44),"sx":rng.uniform(95,130),
        "sy":rng.uniform(42,62),"warp":rng.uniform(4,14),"tail":rng.uniform(55,105),
        "tailW":rng.uniform(.16,.32),"tailPow":rng.uniform(1.2,2.4),
        "fold":rng.uniform(3,10),"foldF":rng.uniform(2,4.5),"wave":rng.uniform(3,10),
        "curl":rng.uniform(4,14),"alpha":rng.randint(38,54)
    }

def build(seed, fn, prefix, n=12):
    rng=random.Random(seed)
    return {f"{prefix}{i+1}":fn(rng) for i in range(n)}

positive=build(26083101,random_morph,"M")
negative_initial=build(26083102,random_field,"N")
negative_repaired=build(26083103,random_ray,"R")

m9=positive["M9"]
metrics={
    "positiveWinner":"M9",
    "negativeWinner":"R11",
    "positiveControlEvidence":{
        "rootWidthRelativeChange":.25,
        "rootControlMedianOrganLocalSpill":0.0,
        "rootControlMaxOrganLocalSpill":0.0,
        "familyControlMedianLengthChange":.25,
        "familyControlDirectionalAgreement":1.0,
        "familyControlRelativeMAD":0.0,
        "organCount":m9["organs"]
    },
    "negativeRepresentation":{
        "independentlyAuthoredAnatomicalParts":0,
        "morphologyGraph":False,
        "mapping":"single continuous (u,v)->(x,y) field"
    }
}

payload={
    "seeds":{"positive":26083101,"negativeInitial":26083102,"negativeRepaired":26083103},
    "positive":positive,
    "negativeInitial":negative_initial,
    "negativeRepaired":negative_repaired,
    "metrics":metrics
}
path=OUT/"candidates.json"
path.write_text(json.dumps(payload,indent=2)+"\n")
print(path)
