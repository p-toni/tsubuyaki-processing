"""Representation-specific hard-validity checks for autonomous discovery."""
from __future__ import annotations
import math, statistics
from typing import Tuple
Point=Tuple[float,float]

def _finite_points(points): return bool(points) and all(math.isfinite(x) and math.isfinite(y) for x,y in points)
def _in_frame_fraction(points,width,height): return sum(0<=x<width and 0<=y<height for x,y in points)/len(points) if points else 0.0
def _bbox(points,width,height):
    if not points:return {'width':0.0,'height':0.0,'dominant':0.0}
    xs=[p[0] for p in points]; ys=[p[1] for p in points]; bw=(max(xs)-min(xs))/width; bh=(max(ys)-min(ys))/height
    return {'width':bw,'height':bh,'dominant':max(bw,bh)}
def _step_stats(points):
    if len(points)<3:return {'median':0.0,'p95':float('inf'),'max':float('inf'),'p95_over_median':float('inf')}
    ds=[math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:])]; o=sorted(ds); med=statistics.median(o); p95=o[min(len(o)-1,int(len(o)*.95))]
    return {'median':med,'p95':p95,'max':o[-1],'p95_over_median':p95/med if med>1e-9 else float('inf')}
def _mean_corresponding_displacement(a,b,diagonal):
    n=min(len(a),len(b))
    if not n:return float('inf')
    step=max(1,n//512); ds=[math.hypot(a[i][0]-b[i][0],a[i][1]-b[i][1]) for i in range(0,n,step)]
    return statistics.fmean(ds)/diagonal if ds else 0.0
def _shared_frame_checks(frames,width,height):
    failures=[]; finite=[_finite_points(p) for p in frames]; in_frame=[_in_frame_fraction(p,width,height) for p in frames]; boxes=[_bbox(p,width,height) for p in frames]
    diagnostics={'finiteByFrame':finite,'inFrameFractionByFrame':in_frame,'bboxByFrame':boxes}
    if not all(finite):failures.append('non-finite or empty geometry')
    if min(in_frame,default=0.0)<.78:failures.append('too much geometry leaves the canvas')
    if min((b['dominant'] for b in boxes),default=0.0)<.28:failures.append('representation collapses to a very small form')
    return failures,diagnostics

def check_recurrence(genome,times,geometry_fn,width,height):
    geoms=[geometry_fn(genome,t) for t in times]; frames=[g['all'] for g in geoms]; spines=[g['spine'] for g in geoms]
    failures,diagnostics=_shared_frame_checks(frames,width,height); warnings=[]
    spine_in_frame=[_in_frame_fraction(s,width,height) for s in spines]; continuity=[_step_stats(s) for s in spines]; spine_boxes=[_bbox(s,width,height) for s in spines]; diagonal=math.hypot(width,height)
    temporal=[_mean_corresponding_displacement(a,b,diagonal) for a,b in zip(spines,spines[1:])]
    diagnostics.update({'spineInFrameFractionByFrame':spine_in_frame,'spineContinuityByFrame':continuity,'spineBBoxByFrame':spine_boxes,'temporalSpineDisplacement':temporal,'sideAmplitude':float(genome.get('side',0.0)),'occupancyUsedAsGate':False})
    if min(spine_in_frame,default=0)<.90:failures.append('axial spine leaves the canvas')
    if max((c['p95_over_median'] for c in continuity),default=float('inf'))>8:failures.append('axial sampling develops large discontinuities')
    if max((c['max'] for c in continuity),default=float('inf'))>18:failures.append('axial spine contains a large geometric jump')
    if min((b['dominant'] for b in spine_boxes),default=0)<.35:failures.append('axial spine loses meaningful canvas coverage')
    if float(genome.get('side',0))<3:warnings.append('side structure is extremely subtle; inspect filament identity')
    if temporal:
        if max(temporal)>.28:failures.append('temporal motion is too discontinuous across the review horizon')
        elif max(temporal)<.001:warnings.append('motion is nearly static across the review horizon')
    return {'route':'recurrence','valid':not failures,'failures':failures,'warnings':warnings,'diagnostics':diagnostics}

def check_filament(genome,times,geometry_fn,width,height):
    result=check_recurrence(genome,times,geometry_fn,width,height); result['route']='filament'; boxes=result['diagnostics'].get('spineBBoxByFrame',[])
    axial=[b['width']/max(1e-9,b['height']) for b in boxes]; result['diagnostics']['axialAspectByFrame']=axial
    if axial and min(axial)<1.15:
        result['failures'].append('intentional filament loses clear axial identity'); result['valid']=False
    return result

def check_family(genome,times,geometry_fn,width,height):
    geoms=[geometry_fn(genome,t) for t in times]; frames=[g['all'] for g in geoms]; failures,diagnostics=_shared_frame_checks(frames,width,height); warnings=[]
    expected=int(genome.get('organs',0)); counts=[len(g['organs']) for g in geoms]; root_boxes=[_bbox(g['root'],width,height) for g in geoms]; anchor_in=[]; tip_in=[]; length_cv=[]; gap_ratio=[]
    for g in geoms:
        anchors=g['anchors']; organs=g['organs']; anchor_in.append(_in_frame_fraction(anchors,width,height)); tips=[o[-1] for o in organs if o]; tip_in.append(_in_frame_fraction(tips,width,height)); lengths=[]
        for anchor,organ in zip(anchors,organs):
            if organ:lengths.append(math.hypot(organ[-1][0]-anchor[0],organ[-1][1]-anchor[1]))
        length_cv.append(statistics.pstdev(lengths)/statistics.fmean(lengths) if lengths and statistics.fmean(lengths)>1e-9 else float('inf'))
        gaps=[math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(anchors,anchors[1:])]; gap_ratio.append(min(gaps)/max(1.0,float(genome.get('root_w',1))*2) if gaps else 0)
    diagnostics.update({'expectedOrganCount':expected,'organCountByFrame':counts,'rootBBoxByFrame':root_boxes,'anchorInFrameFractionByFrame':anchor_in,'tipInFrameFractionByFrame':tip_in,'siblingLengthCVByFrame':length_cv,'minimumAnchorGapRatioByFrame':gap_ratio})
    if expected<3:failures.append('repeated family has fewer than three siblings')
    if any(c!=expected for c in counts):failures.append('repeated-family count is not preserved')
    if min((b['width'] for b in root_boxes),default=0)<.22 or min((b['height'] for b in root_boxes),default=0)<.18:failures.append('root mass collapses')
    if min(anchor_in,default=0)<1:failures.append('one or more family anchors leave the canvas')
    if min(tip_in,default=0)<.80:failures.append('too many organ tips leave the canvas')
    if max(length_cv,default=float('inf'))>.32:failures.append('shared family law loses sibling-scale coherence')
    if min(gap_ratio,default=0)<.045:warnings.append('family anchors are tightly packed; inspect merged-organ drift')
    return {'route':'family','valid':not failures,'failures':failures,'warnings':warnings,'diagnostics':diagnostics}

def check_sheet(genome,times,geometry_fn,width,height):
    geoms=[geometry_fn(genome,t) for t in times]; frames=[g['all'] for g in geoms]; failures,diagnostics=_shared_frame_checks(frames,width,height); warnings=[]; diag=math.hypot(width,height)
    row_spans=[]; col_spans=[]
    for g in geoms:
        rs=[]
        for row in g.get('rows',[]):
            if len(row)>=3: rs.append((max(p[0] for p in row)-min(p[0] for p in row))/width)
        cs=[]
        for col in g.get('cols',[]):
            if len(col)>=3: cs.append((max(p[1] for p in col)-min(p[1] for p in col))/height)
        row_spans.append(statistics.median(rs) if rs else 0.0); col_spans.append(statistics.median(cs) if cs else 0.0)
    boxes=diagnostics['bboxByFrame']; temporal=[_mean_corresponding_displacement(a,b,diag) for a,b in zip(frames,frames[1:])]
    diagnostics.update({'medianRowSpanByFrame':row_spans,'medianColumnSpanByFrame':col_spans,'temporalSheetDisplacement':temporal,'intrinsicDimension':2,'occupancyUsedAsGate':False})
    if min((b['width'] for b in boxes),default=0)<.38 or min((b['height'] for b in boxes),default=0)<.32:failures.append('sheet loses meaningful two-dimensional canvas coverage')
    if min(row_spans,default=0)<.30 or min(col_spans,default=0)<.24:failures.append('sampling collapses toward a one-dimensional manifold')
    if int(genome.get('nu',0))<24 or int(genome.get('nv',0))<24:failures.append('sheet sampling resolution is too low for a 2-D representation')
    if temporal:
        if max(temporal)>.24:failures.append('sheet motion is too discontinuous across the review horizon')
        elif max(temporal)<.001:warnings.append('sheet is nearly static across the review horizon')
    return {'route':'sheet','valid':not failures,'failures':failures,'warnings':warnings,'diagnostics':diagnostics}

def check_candidate(route,genome,times,geometry_fn,width,height):
    if route=='recurrence':return check_recurrence(genome,times,geometry_fn,width,height)
    if route=='family':return check_family(genome,times,geometry_fn,width,height)
    if route=='sheet':return check_sheet(genome,times,geometry_fn,width,height)
    if route=='filament':return check_filament(genome,times,geometry_fn,width,height)
    return {'route':route,'valid':False,'failures':[f'no checker registered for route {route!r}'],'warnings':[],'diagnostics':{}}
