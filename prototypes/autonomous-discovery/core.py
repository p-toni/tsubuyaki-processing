from __future__ import annotations
import statistics
from dataclasses import dataclass,asdict,field
from typing import Dict,List
from PIL import Image
from checkers import check_candidate
from representations import REPRESENTATIONS,get_representation
W=H=400; BG=9; FG=255; TIMES=(30,90,150)
@dataclass
class Candidate:
    id:str; route:str; basin:str; genome:Dict[str,float]; parent_id:str|None; stage:str; features:Dict[str,float]=field(default_factory=dict); checks:Dict[str,object]=field(default_factory=dict); score:float=0.0; reviews:List[Dict[str,object]]=field(default_factory=list)
@dataclass
class SearchState:
    brief:Dict[str,object]; seed:int; candidates:Dict[str,Candidate]=field(default_factory=dict); stage_decisions:List[Dict[str,object]]=field(default_factory=list); winner_id:str|None=None
    def to_json(self):return {'brief':self.brief,'seed':self.seed,'candidates':{k:asdict(v) for k,v in self.candidates.items()},'stage_decisions':self.stage_decisions,'winner_id':self.winner_id}
def draw_points(points,alpha=48):
    data=[BG]*(W*H); a=alpha/255.0
    for x,y in points:
        xi=int(round(x)); yi=int(round(y))
        if 0<=xi<W and 0<=yi<H:
            k=yi*W+xi; data[k]=min(255,round(data[k]*(1-a)+FG*a))
    im=Image.new('L',(W,H)); im.putdata(data); return im

def _compat_route(spec):
    return {'render':lambda g,t,s=spec:s.points(g,t,W,H),'geometry':lambda g,t,s=spec:s.geometry(g,t,W,H),'target_occupancy':spec.target_occupancy,'seed':spec.seed,'mutate':spec.mutate,'prefix':spec.prefix,'version':spec.version,'intrinsic_dimension':spec.intrinsic_dimension}
ROUTES={rid:_compat_route(spec) for rid,spec in REPRESENTATIONS.items()}
def recurrence_geometry(g,t): return ROUTES['recurrence']['geometry'](g,t)
def recurrence_points(g,t): return ROUTES['recurrence']['render'](g,t)
def family_geometry(g,t): return ROUTES['family']['geometry'](g,t)
def family_points(g,t): return ROUTES['family']['render'](g,t)
def image_metrics(im):
    px=list(im.getdata()); lit=[i for i,v in enumerate(px) if v>20]
    if not lit:return dict(occupancy=0,bbox_w=0,bbox_h=0,center_dx=1,center_dy=1)
    xs=[i%W for i in lit]; ys=[i//W for i in lit]
    return {'occupancy':len(lit)/(W*H),'bbox_w':(max(xs)-min(xs)+1)/W,'bbox_h':(max(ys)-min(ys)+1)/H,'center_dx':abs(statistics.fmean(xs)-W/2)/(W/2),'center_dy':abs(statistics.fmean(ys)-H/2)/(H/2)}
def _frame_difference(a,b):
    ap=list(a.getdata()); bp=list(b.getdata()); return statistics.fmean(abs(x-y) for x,y in zip(ap,bp))/255 if ap and len(ap)==len(bp) else 0
def candidate_features(route,genome):
    ims=[draw_points(ROUTES[route]['render'](genome,t),genome['alpha']) for t in TIMES]; mets=[image_metrics(im) for im in ims]; changes=[_frame_difference(a,b) for a,b in zip(ims,ims[1:])]; mean=statistics.fmean(changes) if changes else 0
    return {'occupancy_mean':statistics.fmean(m['occupancy'] for m in mets),'occupancy_var':statistics.pvariance(m['occupancy'] for m in mets),'bbox_w_mean':statistics.fmean(m['bbox_w'] for m in mets),'bbox_h_mean':statistics.fmean(m['bbox_h'] for m in mets),'center_dx_mean':statistics.fmean(m['center_dx'] for m in mets),'center_dy_mean':statistics.fmean(m['center_dy'] for m in mets),'temporal_change_mean':mean,'temporal_change_cv':statistics.pstdev(changes)/mean if len(changes)>1 and mean>1e-9 else 0}
def diagnostic_score(route,f,brief):
    lo,hi=ROUTES[route]['target_occupancy']; occ=f['occupancy_mean']; occs=1 if lo<=occ<=hi else max(0,1-(lo-occ)/lo) if occ<lo else max(0,1-(occ-hi)/(1-hi)); blo,bhi=brief.get('bbox_target',[.55,.82]); span=max(f['bbox_w_mean'],f['bbox_h_mean']); fill=1 if blo<=span<=bhi else max(0,1-(blo-span)/blo) if span<blo else max(0,1-(span-bhi)/(1-bhi)); center=max(0,1-f['center_dx_mean']-f['center_dy_mean']); return .4*occs+.35*fill+.25*center
def evaluate_candidate(cand,brief):
    cand.checks=check_candidate(cand.route,cand.genome,TIMES,ROUTES[cand.route]['geometry'],W,H); cand.features=candidate_features(cand.route,cand.genome); cand.score=diagnostic_score(cand.route,cand.features,brief) if cand.checks['valid'] else -1e9; return cand
def render_candidate_frame(cand,t):return draw_points(ROUTES[cand.route]['render'](cand.genome,t),cand.genome['alpha'])
def default_brief():return {'name':'autonomous-discovery-prototype','artistic_intent':'Discover an original mathematically generated living form with coherent material, strong composition, and meaningful motion across time. Prefer distinctive non-generic structure over merely filling the canvas.','routes':['recurrence','family'],'bbox_target':[.55,.82],'starts_per_route':3,'explore_per_basin':4,'roundA_per_survivor':3,'total_extra_budget':12}
