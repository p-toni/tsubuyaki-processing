#!/usr/bin/env python3
from __future__ import annotations

import math, random, statistics
from dataclasses import dataclass, asdict, field
from typing import Dict, List
from PIL import Image

from checkers import check_candidate

W = H = 400
BG = 9
FG = 255
TIMES = (30, 90, 150)

@dataclass
class Candidate:
    id: str
    route: str
    basin: str
    genome: Dict[str, float]
    parent_id: str | None
    stage: str
    features: Dict[str, float] = field(default_factory=dict)
    checks: Dict[str, object] = field(default_factory=dict)
    score: float = 0.0  # diagnostic only; never promotion fitness
    reviews: List[Dict[str, object]] = field(default_factory=list)

@dataclass
class SearchState:
    brief: Dict[str, object]
    seed: int
    candidates: Dict[str, Candidate] = field(default_factory=dict)
    stage_decisions: List[Dict[str, object]] = field(default_factory=list)
    winner_id: str | None = None
    def to_json(self):
        return {
            'brief': self.brief,
            'seed': self.seed,
            'candidates': {k: asdict(v) for k,v in self.candidates.items()},
            'stage_decisions': self.stage_decisions,
            'winner_id': self.winner_id,
        }

def clamp(x, lo, hi): return lo if x < lo else hi if x > hi else x

def draw_points(points, alpha=48):
    data=[BG]*(W*H); a=alpha/255.0
    for x,y in points:
        xi=int(round(x)); yi=int(round(y))
        if 0<=xi<W and 0<=yi<H:
            k=yi*W+xi
            data[k]=min(255,round(data[k]*(1-a)+FG*a))
    im=Image.new('L',(W,H)); im.putdata(data); return im

def recurrence_geometry(g,t):
    spine=[]; sides=[]; n=int(g['samples'])
    for i in range(n):
        u=-1+2*i/max(1,n-1)
        r=g['base_r']*(.55+.45*math.sin(math.pi*(u+1)/2)**g['taper'])
        ph=g['f1']*u+g['f2']*u*u+g['f3']*math.sin(g['f4']*u-t/g['time'])
        x=W/2+g['sx']*(r*math.cos(ph)+.15*math.sin(t/g['time2']+g['warp']*u))
        y=H/2+g['sy']*(u+g['curl']*r*math.sin(ph*.5+t/g['time3']))
        x+=g['twist']*math.sin(g['f5']*u+t/g['time4'])
        spine.append((x,y))
        if i%2==0:
            side=g['side']*(.2+.8*(1-abs(u))**g['side_decay'])
            for sign in (-1,1):
                sides.append((x+sign*side*math.cos(ph+math.pi/2),y+sign*side*math.sin(ph+math.pi/2)))
    return {'spine':spine,'sides':sides,'all':spine+sides}

def recurrence_points(g,t): return recurrence_geometry(g,t)['all']

def family_geometry(g,t):
    root=[]; organs=[]; anchors=[]; cx,cy=W/2,H*.58
    for iu in range(int(g['root_nu'])):
        u=-1+2*iu/max(1,int(g['root_nu'])-1)
        for iv in range(int(g['root_nv'])):
            v=-1+2*iv/max(1,int(g['root_nv'])-1)
            if u*u+(v/g['root_aspect'])**2>1: continue
            split=g['split']*(.5+.5*(1-v*v))
            if abs(u)<split and v<g['split_top']: continue
            fold=1+g['root_fold']*math.sin(g['root_freq']*v+t/g['root_time'])
            root.append((cx+g['root_w']*u*fold,cy+g['root_h']*v+g['root_twist']*u*math.sin(2*v-t/g['root_time2'])))
    count=int(g['organs'])
    for j in range(count):
        q=(j-(count-1)/2)/max(1,(count-1)/2)
        ax=cx+g['root_w']*.82*q; ay=cy-g['root_h']*(.78-.18*q*q); anchors.append((ax,ay))
        ang=-math.pi/2+q*g['fan']+.08*math.sin(t/g['motion_time']+j*.6)
        organ=[]
        for k in range(int(g['organ_samples'])):
            s=k/max(1,int(g['organ_samples'])-1)
            width=g['organ_w']*math.sin(math.pi*s)**g['organ_taper']
            wav=math.sin(g['organ_freq']*s*math.pi+j*g['phase']-t/g['organ_time'])
            along=g['organ_len']*(s+.08*wav)
            side=width*(math.sin(2*math.pi*(s*g['ribs']+j*.17))*.35+(1 if k%2 else -1)*.18)
            ca,sa=math.cos(ang),math.sin(ang)
            organ.append((ax+along*ca-side*sa,ay+along*sa+side*ca))
        organs.append(organ)
    return {'root':root,'organs':organs,'anchors':anchors,'all':root+[p for o in organs for p in o]}

def family_points(g,t): return family_geometry(g,t)['all']

def mutate_numeric(g,rng,scale=1.0):
    out=dict(g); k=rng.choice(list(g.keys())[:-1]); v=g[k]
    if isinstance(v,(int,float)):
        nv=v+rng.uniform(-.18,.18)*(abs(v) if abs(v)>1e-6 else 1)*scale
        out[k]=max(1,int(round(nv))) if isinstance(v,int) else nv
    if rng.random()<.25: out['alpha']=int(clamp(out['alpha']+rng.randint(-5,5),22,60))
    return out

ROUTES={
 'recurrence':{
  'render':recurrence_points,'geometry':recurrence_geometry,'target_occupancy':(.012,.05),
  'seed':lambda r:{'samples':r.choice([2200,2600,3000]),'base_r':r.uniform(.08,.32),'taper':r.uniform(.8,2.3),'f1':r.uniform(8,18),'f2':r.uniform(4,14),'f3':r.uniform(.5,2.5),'f4':r.uniform(2,9),'f5':r.uniform(1,7),'sx':r.uniform(130,180),'sy':r.uniform(115,165),'side':r.uniform(8,30),'side_decay':r.uniform(.8,2.2),'curl':r.uniform(.05,.4),'twist':r.uniform(5,26),'warp':r.uniform(1,8),'time':r.uniform(12,32),'time2':r.uniform(17,41),'time3':r.uniform(19,47),'time4':r.uniform(15,39),'alpha':r.randint(28,48)},
  'mutate':lambda g,r,scale=1.0:mutate_numeric(g,r,scale)},
 'family':{
  'render':family_points,'geometry':family_geometry,'target_occupancy':(.035,.12),
  'seed':lambda r:{'root_nu':r.choice([80,90,100]),'root_nv':r.choice([70,80,90]),'root_aspect':r.uniform(.75,1.05),'root_w':r.uniform(65,95),'root_h':r.uniform(50,80),'split':r.uniform(.08,.2),'split_top':r.uniform(.25,.7),'root_fold':r.uniform(.05,.22),'root_freq':r.uniform(2.5,5.5),'root_time':r.uniform(16,42),'root_time2':r.uniform(18,44),'root_twist':r.uniform(4,15),'organs':r.choice([5,6,7,8]),'fan':r.uniform(.8,1.4),'organ_samples':r.choice([450,550,650]),'organ_w':r.uniform(5,14),'organ_taper':r.uniform(.7,1.6),'organ_freq':r.uniform(2.2,5.4),'organ_len':r.uniform(42,78),'organ_time':r.uniform(12,28),'motion_time':r.uniform(16,34),'ribs':r.uniform(1.4,3.5),'phase':r.uniform(.45,1.0),'alpha':r.randint(34,54)},
  'mutate':lambda g,r,scale=1.0:mutate_numeric(g,r,scale)} }

def image_metrics(im):
    px=list(im.getdata()); lit=[i for i,v in enumerate(px) if v>20]
    if not lit: return dict(occupancy=0,bbox_w=0,bbox_h=0,center_dx=1,center_dy=1)
    xs=[i%W for i in lit]; ys=[i//W for i in lit]
    return {'occupancy':len(lit)/(W*H),'bbox_w':(max(xs)-min(xs)+1)/W,'bbox_h':(max(ys)-min(ys)+1)/H,'center_dx':abs(statistics.fmean(xs)-W/2)/(W/2),'center_dy':abs(statistics.fmean(ys)-H/2)/(H/2)}

def _frame_difference(a,b):
    ap=list(a.getdata()); bp=list(b.getdata())
    return statistics.fmean(abs(x-y) for x,y in zip(ap,bp))/255 if ap and len(ap)==len(bp) else 0

def candidate_features(route,genome):
    ims=[draw_points(ROUTES[route]['render'](genome,t),genome['alpha']) for t in TIMES]
    mets=[image_metrics(im) for im in ims]; changes=[_frame_difference(a,b) for a,b in zip(ims,ims[1:])]
    mean=statistics.fmean(changes) if changes else 0
    return {'occupancy_mean':statistics.fmean(m['occupancy'] for m in mets),'occupancy_var':statistics.pvariance(m['occupancy'] for m in mets),'bbox_w_mean':statistics.fmean(m['bbox_w'] for m in mets),'bbox_h_mean':statistics.fmean(m['bbox_h'] for m in mets),'center_dx_mean':statistics.fmean(m['center_dx'] for m in mets),'center_dy_mean':statistics.fmean(m['center_dy'] for m in mets),'temporal_change_mean':mean,'temporal_change_cv':statistics.pstdev(changes)/mean if len(changes)>1 and mean>1e-9 else 0}

def diagnostic_score(route,f,brief):
    lo,hi=ROUTES[route]['target_occupancy']; occ=f['occupancy_mean']
    occs=1 if lo<=occ<=hi else max(0,1-(lo-occ)/lo) if occ<lo else max(0,1-(occ-hi)/(1-hi))
    blo,bhi=brief.get('bbox_target',[.55,.82]); span=max(f['bbox_w_mean'],f['bbox_h_mean'])
    fill=1 if blo<=span<=bhi else max(0,1-(blo-span)/blo) if span<blo else max(0,1-(span-bhi)/(1-bhi))
    center=max(0,1-f['center_dx_mean']-f['center_dy_mean'])
    return .4*occs+.35*fill+.25*center

def evaluate_candidate(cand,brief):
    cand.checks=check_candidate(cand.route,cand.genome,TIMES,ROUTES[cand.route]['geometry'],W,H)
    cand.features=candidate_features(cand.route,cand.genome)
    cand.score=diagnostic_score(cand.route,cand.features,brief) if cand.checks['valid'] else -1e9
    return cand

def render_candidate_frame(cand,t):
    return draw_points(ROUTES[cand.route]['render'](cand.genome,t),cand.genome['alpha'])

def default_brief():
    return {'name':'autonomous-discovery-prototype','artistic_intent':'Discover an original mathematically generated living form with coherent material, strong composition, and meaningful motion across time. Prefer distinctive non-generic structure over merely filling the canvas.','routes':['recurrence','family'],'bbox_target':[.55,.82],'starts_per_route':3,'explore_per_basin':4,'roundA_per_survivor':3,'total_extra_budget':12}
