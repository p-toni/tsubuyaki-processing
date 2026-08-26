#!/usr/bin/env python3
"""Reproduce the morphology route-pair candidates and semantic evidence.

Pure-Python reproduction always regenerates parameters + control metrics.
If Pillow is installed, it also renders winner timelines.

Run:
    python experiments/morphology-route-pair/reproduce.py
"""
import json
import math
import random
import statistics
from pathlib import Path

OUT = Path(__file__).resolve().parent / "_generated"
OUT.mkdir(exist_ok=True)
W = H = 340

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

def morph_points(g,t,root_control=1.0,organ_control=1.0,motion_control=1.0,with_meta=False):
    pts=[]
    organ_meta=[]
    cx,cy=W/2,H*.57
    for iu in range(g["rootNu"]):
        u=-1+2*iu/(g["rootNu"]-1)
        for iv in range(g["rootNv"]):
            v=-1+2*iv/(g["rootNv"]-1)
            if u*u+(v/g["rootAspect"])**2>1:
                continue
            split=g["split"]*(.55+.45*(1-v*v))
            if abs(u)<split and v<g["splitTop"]:
                continue
            fold=1+g["rootFold"]*math.sin(g["rootFreq"]*v+.6*math.sin(t/g["rootTime"]))
            x=cx+root_control*g["rootW"]*u*fold*(.92+.08*math.cos(3*v+t/19))
            y=cy+g["rootH"]*v+g["rootTwist"]*u*math.sin(2*v-t/23)
            pts.append((x,y))
    n=g["organs"]
    for j in range(n):
        q=(j-(n-1)/2)/max(1,(n-1)/2)
        ax=cx+root_control*g["rootW"]*.78*q
        ay=cy-g["rootH"]*(.78-.20*q*q)
        ang=-math.pi/2+q*g["organFan"]+.06*motion_control*math.sin(t/g["motionTime"]+j*.7)
        local=[]
        for k in range(g["organSamples"]):
            s=k/(g["organSamples"]-1)
            width=g["organWidth"]*math.sin(math.pi*s)**g["organTaper"]
            wav=math.sin(g["organFreq"]*s*math.pi+j*g["phase"]-motion_control*t/g["organTime"])
            along=organ_control*g["organLen"]*(s+.08*wav*math.sin(math.pi*s))
            side=width*(math.sin(2*math.pi*(s*g["organRibs"]+j*.17))*.35+(2*(k%2)-1)*.18)
            ca,sa=math.cos(ang),math.sin(ang)
            pts.append((ax+along*ca-side*sa, ay+along*sa+side*ca))
            local.append((along,side))
        organ_meta.append({"anchor":(ax,ay),"local":local})
    return (pts,organ_meta) if with_meta else pts

def ray_points(g,t):
    pts=[]
    for iu in range(g["nu"]):
        u=-1+2*iu/(g["nu"]-1)
        for iv in range(g["nv"]):
            v=-1+2*iv/(g["nv"]-1)
            s=(v+1)/2
            width=(1-s)**g["narrow"]*(.40+g["wing"]*math.sin(math.pi*s)**g["wingPow"])
            width*=1-g["notch"]*math.exp(-(v/g["notchW"])**2)
            phase=g["fu"]*u+g["fv"]*v+g["uv"]*u*v-t/g["time"]
            x=W/2+g["sx"]*u*width+g["warp"]*math.sin(phase)*(1-.35*s)
            center=g["tail"]*math.exp(-(u/g["tailW"])**2)*s**g["tailPow"]
            y=H*.38+g["sy"]*v+center+g["fold"]*u*math.sin(g["foldF"]*v-t/g["time2"])
            y+=g["wave"]*math.cos(phase*1.2)*(1-u*u)
            y+=g["curl"]*(u*u-.35)*math.sin(math.pi*s+t/g["curlT"])
            pts.append((x,y))
    return pts

def root_only(g,t,root_control):
    pts=[]
    cx,cy=W/2,H*.57
    for iu in range(g["rootNu"]):
        u=-1+2*iu/(g["rootNu"]-1)
        for iv in range(g["rootNv"]):
            v=-1+2*iv/(g["rootNv"]-1)
            if u*u+(v/g["rootAspect"])**2>1:
                continue
            split=g["split"]*(.55+.45*(1-v*v))
            if abs(u)<split and v<g["splitTop"]:
                continue
            fold=1+g["rootFold"]*math.sin(g["rootFreq"]*v+.6*math.sin(t/g["rootTime"]))
            x=cx+root_control*g["rootW"]*u*fold*(.92+.08*math.cos(3*v+t/19))
            y=cy+g["rootH"]*v+g["rootTwist"]*u*math.sin(2*v-t/23)
            pts.append((x,y))
    return pts

def organ_lengths(meta):
    return [max(p[0] for p in o["local"])-min(p[0] for p in o["local"]) for o in meta]

positive=build(26083101,random_morph,"M")
negative_initial=build(26083102,random_field,"N")
negative_repaired=build(26083103,random_ray,"R")
m9=positive["M9"]
r11=negative_repaired["R11"]

_,base_meta=morph_points(m9,12,with_meta=True)
_,root_meta=morph_points(m9,12,root_control=1.25,with_meta=True)
_,family_meta=morph_points(m9,12,organ_control=1.25,with_meta=True)
base_len=organ_lengths(base_meta)
root_len=organ_lengths(root_meta)
family_len=organ_lengths(family_meta)
root_spill=[abs(b-a)/a for a,b in zip(base_len,root_len)]
fam_change=[(b-a)/a for a,b in zip(base_len,family_len)]

base_root=root_only(m9,12,1)
var_root=root_only(m9,12,1.25)
rw0=max(x for x,y in base_root)-min(x for x,y in base_root)
rw1=max(x for x,y in var_root)-min(x for x,y in var_root)
med=statistics.median(fam_change)
mad=statistics.median(abs(x-med) for x in fam_change)/abs(med)

metrics={
    "positiveWinner":"M9",
    "negativeWinner":"R11",
    "positiveControlEvidence":{
        "rootWidthRelativeChange":(rw1-rw0)/rw0,
        "rootControlMedianOrganLocalSpill":statistics.median(root_spill),
        "rootControlMaxOrganLocalSpill":max(root_spill),
        "familyControlMedianLengthChange":med,
        "familyControlDirectionalAgreement":sum(x>0 for x in fam_change)/len(fam_change),
        "familyControlRelativeMAD":mad,
        "organCount":len(base_len)
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
(OUT/"candidates.json").write_text(json.dumps(payload,indent=2)+"\n")
(OUT/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")

try:
    from PIL import Image

    def render(points,alpha):
        bg=9
        data=[bg]*(W*H)
        a=alpha/255
        for x,y in points:
            X=int(round(x));Y=int(round(y))
            if 0<=X<W and 0<=Y<H:
                k=Y*W+X
                data[k]=round(data[k]*(1-a)+255*a)
        im=Image.new("L",(W,H));im.putdata(data)
        return im.convert("RGB")

    times=(0,12,24,36)
    tw=170
    for name,g,fn in [("M9",m9,morph_points),("R11",r11,ray_points)]:
        can=Image.new("RGB",(4*tw,tw),(28,28,28))
        for i,t in enumerate(times):
            can.paste(render(fn(g,t),g["alpha"]).resize((tw,tw)),(i*tw,0))
        can.save(OUT/f"{name}-timeline.png")
except ImportError:
    pass

print(OUT/"candidates.json")
print(OUT/"metrics.json")
