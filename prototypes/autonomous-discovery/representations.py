from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Mapping

Genome = Dict[str, float]
Geometry = Dict[str, object]


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def mutate_numeric(g: Genome, rng, scale: float = 1.0) -> Genome:
    """Legacy-compatible local numeric mutation used by the first four adapters."""
    out = dict(g)
    keys = list(g.keys())
    mutable = keys[:-1] if keys and keys[-1] == "alpha" else [k for k in keys if k != "alpha"]
    k = rng.choice(mutable)
    v = g[k]
    if isinstance(v, (int, float)):
        nv = v + rng.uniform(-.18, .18) * (abs(v) if abs(v) > 1e-6 else 1) * scale
        out[k] = max(1, int(round(nv))) if isinstance(v, int) else nv
    if rng.random() < .25 and "alpha" in out:
        out["alpha"] = int(clamp(out["alpha"] + rng.randint(-5, 5), 22, 60))
    return out


@dataclass(frozen=True)
class RepresentationSpec:
    id: str
    prefix: str
    version: str
    intrinsic_dimension: int
    target_occupancy: tuple[float, float]
    seed_fn: Callable[[object], Genome]
    mutate_fn: Callable[[Genome, object, float], Genome]
    geometry_fn: Callable[[Genome, float, int, int], Geometry]

    def seed(self, rng) -> Genome:
        return self.seed_fn(rng)

    def mutate(self, genome: Genome, rng, scale: float = 1.0) -> Genome:
        return self.mutate_fn(genome, rng, scale)

    def geometry(self, genome: Genome, t: float, width: int, height: int) -> Geometry:
        return self.geometry_fn(genome, t, width, height)

    def points(self, genome: Genome, t: float, width: int, height: int):
        return self.geometry(genome, t, width, height)["all"]


def recurrence_geometry(g, t, W, H):
    spine = []; sides = []; n = int(g['samples'])
    for i in range(n):
        u = -1 + 2*i/max(1, n-1)
        r = g['base_r']*(.55+.45*math.sin(math.pi*(u+1)/2)**g['taper'])
        ph = g['f1']*u + g['f2']*u*u + g['f3']*math.sin(g['f4']*u-t/g['time'])
        x = W/2 + g['sx']*(r*math.cos(ph)+.15*math.sin(t/g['time2']+g['warp']*u))
        y = H/2 + g['sy']*(u+g['curl']*r*math.sin(ph*.5+t/g['time3']))
        x += g['twist']*math.sin(g['f5']*u+t/g['time4'])
        spine.append((x, y))
        if i % 2 == 0:
            side = g['side']*(.2+.8*(1-abs(u))**g['side_decay'])
            for sign in (-1, 1):
                sides.append((x+sign*side*math.cos(ph+math.pi/2), y+sign*side*math.sin(ph+math.pi/2)))
    return {'spine': spine, 'sides': sides, 'all': spine+sides}


def recurrence_seed(r):
    return {'samples':r.choice([2200,2600,3000]),'base_r':r.uniform(.08,.32),'taper':r.uniform(.8,2.3),'f1':r.uniform(8,18),'f2':r.uniform(4,14),'f3':r.uniform(.5,2.5),'f4':r.uniform(2,9),'f5':r.uniform(1,7),'sx':r.uniform(130,180),'sy':r.uniform(115,165),'side':r.uniform(8,30),'side_decay':r.uniform(.8,2.2),'curl':r.uniform(.05,.4),'twist':r.uniform(5,26),'warp':r.uniform(1,8),'time':r.uniform(12,32),'time2':r.uniform(17,41),'time3':r.uniform(19,47),'time4':r.uniform(15,39),'alpha':r.randint(28,48)}


def family_geometry(g, t, W, H):
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


def family_seed(r):
    return {'root_nu':r.choice([80,90,100]),'root_nv':r.choice([70,80,90]),'root_aspect':r.uniform(.75,1.05),'root_w':r.uniform(65,95),'root_h':r.uniform(50,80),'split':r.uniform(.08,.2),'split_top':r.uniform(.25,.7),'root_fold':r.uniform(.05,.22),'root_freq':r.uniform(2.5,5.5),'root_time':r.uniform(16,42),'root_time2':r.uniform(18,44),'root_twist':r.uniform(4,15),'organs':r.choice([5,6,7,8]),'fan':r.uniform(.8,1.4),'organ_samples':r.choice([450,550,650]),'organ_w':r.uniform(5,14),'organ_taper':r.uniform(.7,1.6),'organ_freq':r.uniform(2.2,5.4),'organ_len':r.uniform(42,78),'organ_time':r.uniform(12,28),'motion_time':r.uniform(16,34),'ribs':r.uniform(1.4,3.5),'phase':r.uniform(.45,1.0),'alpha':r.randint(34,54)}


def sheet_geometry(g, t, W, H):
    points=[]; rows=[]; cols=[[] for _ in range(int(g['nu']))]
    nu=int(g['nu']); nv=int(g['nv']); cx=W/2; cy=H/2
    for j in range(nv):
        v=-1+2*j/max(1,nv-1); row=[]
        for i in range(nu):
            u=-1+2*i/max(1,nu-1)
            gap=g['cavity']*(.35+.65*(1-v*v))
            if abs(u)<gap and v < g['cavity_top']:
                continue
            fold=math.sin(g['fold_freq']*v + t/g['time'])
            ripple=math.sin(g['wave_freq']*u - t/g['time2'] + g['phase']*v)
            x=cx + g['sx']*(u + g['fold']*fold*(1-u*u)) + g['twist']*v*math.sin(g['twist_freq']*u+t/g['time3'])
            y=cy + g['sy']*(v + g['arch']*u*u) + g['wave']*ripple*(1-v*v)
            p=(x,y); row.append(p); cols[i].append(p); points.append(p)
        rows.append(row)
    return {'sheet':points,'rows':rows,'cols':cols,'all':points}


def sheet_seed(r):
    return {
        'nu':r.choice([72,84,96]), 'nv':r.choice([56,68,80]),
        'sx':r.uniform(105,155), 'sy':r.uniform(90,135),
        'cavity':r.uniform(.07,.20), 'cavity_top':r.uniform(.15,.65),
        'fold':r.uniform(.06,.22), 'fold_freq':r.uniform(2.0,5.5),
        'wave':r.uniform(5,22), 'wave_freq':r.uniform(2.0,6.0),
        'phase':r.uniform(.2,1.2), 'arch':r.uniform(-.10,.22),
        'twist':r.uniform(3,18), 'twist_freq':r.uniform(1.5,5.0),
        'time':r.uniform(18,42), 'time2':r.uniform(14,36), 'time3':r.uniform(20,50),
        'alpha':r.randint(26,46),
    }


def filament_geometry(g, t, W, H):
    spine=[]; sides=[]; n=int(g['samples'])
    for i in range(n):
        u=-1+2*i/max(1,n-1)
        phase=g['f1']*u + g['phase']*math.sin(g['f2']*u)
        x=W/2 + g['sx']*(u + g['drift']*math.sin(g['f3']*u+t/g['time3']))
        y=H/2 + g['sy']*(g['fold']*math.sin(phase-t/g['time']) + g['fold2']*math.sin(g['f4']*u+t/g['time2']))
        spine.append((x,y))
        dx=g['sx']*(1 + g['drift']*g['f3']*math.cos(g['f3']*u+t/g['time3']))
        dy=g['sy']*(g['fold']*(g['f1']+g['phase']*g['f2']*math.cos(g['f2']*u))*math.cos(phase-t/g['time']) + g['fold2']*g['f4']*math.cos(g['f4']*u+t/g['time2']))
        mag=max(1e-6, math.hypot(dx,dy)); nx,ny=-dy/mag,dx/mag
        width=g['side']*(.35+.65*(1-abs(u))**g['taper'])
        if i%2==0:
            sides.extend([(x+width*nx,y+width*ny),(x-width*nx,y-width*ny)])
    return {'spine':spine,'sides':sides,'all':spine+sides}


def filament_seed(r):
    return {
        'samples':r.choice([2200,2600,3000]), 'sx':r.uniform(120,165), 'sy':r.uniform(55,100),
        'fold':r.uniform(.45,.95), 'fold2':r.uniform(.08,.28),
        'f1':r.uniform(3.5,8.5), 'f2':r.uniform(1.5,5.0), 'f3':r.uniform(1.0,4.0), 'f4':r.uniform(5.0,11.0),
        'phase':r.uniform(.25,1.1), 'drift':r.uniform(.025,.11),
        'side':r.uniform(5,18), 'taper':r.uniform(.7,2.0),
        'time':r.uniform(18,38), 'time2':r.uniform(20,46), 'time3':r.uniform(24,52),
        'alpha':r.randint(28,48),
    }


REPRESENTATIONS: Mapping[str, RepresentationSpec] = {
    'recurrence': RepresentationSpec('recurrence','R','1',1,(.012,.05),recurrence_seed,mutate_numeric,recurrence_geometry),
    'family': RepresentationSpec('family','F','1',2,(.035,.12),family_seed,mutate_numeric,family_geometry),
    'sheet': RepresentationSpec('sheet','S','1',2,(.05,.18),sheet_seed,mutate_numeric,sheet_geometry),
    'filament': RepresentationSpec('filament','L','1',1,(.008,.05),filament_seed,mutate_numeric,filament_geometry),
}


def get_representation(route: str) -> RepresentationSpec:
    try:
        return REPRESENTATIONS[route]
    except KeyError:
        raise KeyError(f"unknown representation {route!r}; available={sorted(REPRESENTATIONS)}")
