#!/usr/bin/env python3
from __future__ import annotations
import json, math, random
from pathlib import Path
from typing import Dict, List, Optional, Sequence
from PIL import Image, ImageDraw

from core import Candidate, SearchState, ROUTES, TIMES, evaluate_candidate, render_candidate_frame
from material_control import mutate_native, with_spectral_control, with_family_projected_spectral_control
from rng_streams import derived_seed
from pairwise_selector import PairwiseSelector, DeterministicTemporalSelector, incumbent_challenge, route_aware_frontier

NATIVE_ONLY = 'native-only'
MIXED_1D_V1 = 'native-spectral-50-50-v1'
FAMILY_PROJECTED_V1 = 'native-family-projected-spectral-50-50-v1'


def _record(state,stage,decisions):
    for d in decisions:
        x=d.to_json(); x['stage']=stage; state.stage_decisions.append(x)

def _select_local(selector,incumbent,challengers,brief,state,stage):
    champion=incumbent
    for c in challengers:
        champion,d=incumbent_challenge(selector,champion,c,brief); _record(state,stage,[d])
    return champion

def _portfolio_mode(brief):
    mode=str(brief.get('mutation_portfolio',NATIVE_ONLY))
    if mode not in {NATIVE_ONLY,MIXED_1D_V1,FAMILY_PROJECTED_V1}:
        raise ValueError(f'unsupported mutation_portfolio {mode!r}')
    return mode

def _eligible_routes_for_portfolio(brief):
    mode=_portfolio_mode(brief)
    routes=list(brief.get('routes') or [])
    if mode==MIXED_1D_V1:
        return [r for r in routes if int(ROUTES[r].get('intrinsic_dimension',-1))==1]
    if mode==FAMILY_PROJECTED_V1:
        return [r for r in routes if r=='family']
    return []
def _operator_for(brief,route,index,count):
    mode=_portfolio_mode(brief)
    if mode==NATIVE_ONLY:
        return 'native'
    eligible=(mode==MIXED_1D_V1 and int(ROUTES[route].get('intrinsic_dimension',-1))==1) or (mode==FAMILY_PROJECTED_V1 and route=='family')
    if not eligible:
        return 'native'
    # Preserve the native prefix, then spend the remaining half on the confirmed
    # spectral operator. Odd batches conservatively keep the extra attempt native.
    native_n=(int(count)+1)//2
    if int(index)<native_n:
        return 'native'
    return 'spectral' if mode==MIXED_1D_V1 else 'projected-spectral'
def _spawn(brief,seed,parent,cid,stage,index,count,rng,scale):
    op=_operator_for(brief,parent.route,index,count)
    if op=='native':
        if _portfolio_mode(brief)==NATIVE_ONLY:
            genome=ROUTES[parent.route]['mutate'](parent.genome,rng,scale)
        else:
            genome=mutate_native(ROUTES[parent.route],parent.genome,rng,scale)
    elif op=='spectral':
        field_seed=derived_seed(seed,'runtime-spectral-material-control-v1',parent.route,parent.basin,stage,index,parent.id)
        genome=with_spectral_control(parent.genome,field_seed)
    elif op=='projected-spectral':
        field_seed=derived_seed(seed,'runtime-family-projected-spectral-control-v1',parent.route,parent.basin,stage,index,parent.id)
        genome=with_family_projected_spectral_control(parent.genome,field_seed)
    else:
        raise AssertionError(f'unknown generation operator {op!r}')
    c=Candidate(cid,parent.route,parent.basin,genome,parent.id,stage); evaluate_candidate(c,brief)
    c.checks['generationOperator']=op
    return c

def montage(cands,out,title):
    from PIL import ImageOps
    thumb=160; cols=3; rows=math.ceil(len(cands)/cols)
    can=Image.new('RGB',(cols*thumb,28+rows*(thumb+20)),(26,26,26)); d=ImageDraw.Draw(can); d.text((6,6),title,fill=(240,240,240))
    for i,c in enumerate(cands):
        x=(i%cols)*thumb; y=28+(i//cols)*(thumb+20)
        im=ImageOps.autocontrast(render_candidate_frame(c,90)).convert('RGB').resize((thumb,thumb)); can.paste(im,(x,y)); d.text((x+4,y+thumb+2),c.id,fill=(220,220,220))
    can.save(out)

def timeline(cand,out):
    thumb=180; can=Image.new('RGB',(thumb*len(TIMES),thumb+20),(26,26,26)); d=ImageDraw.Draw(can)
    for i,t in enumerate(TIMES):
        can.paste(render_candidate_frame(cand,t).convert('RGB').resize((thumb,thumb)),(i*thumb,0)); d.text((i*thumb+6,thumb+2),f't={t}',fill=(230,230,230))
    can.save(out)

def _finish_search(brief,seed,out_dir,selector,state,basins,rng):
    mode=_portfolio_mode(brief)
    if not basins:
        raise ValueError('adaptive search requires at least one valid start candidate')
    for bid,inc in list(basins.items()):
        ch=[]; n=int(brief.get('explore_per_basin',4))
        for j in range(n):
            cid=f'{bid}-E{j+1}'; c=_spawn(brief,seed,inc,cid,'explore',j,n,rng,1); state.candidates[cid]=c; ch.append(c)
        basins[bid]=_select_local(selector,inc,ch,brief,state,'explore')
    montage(list(basins.values()),out_dir/'stage1_representatives.png','Stage 1 representatives')
    _,survivors,ds=route_aware_frontier(selector,list(basins.values()),brief); _record(state,'frontier',ds); live={c.basin for c in survivors}; basins={k:v for k,v in basins.items() if k in live}
    for bid,inc in list(basins.items()):
        ch=[]; n=max(1,int(brief.get('roundA_per_survivor',3)))
        for j in range(n):
            cid=f'{bid}-A{j+1}'; c=_spawn(brief,seed,inc,cid,'roundA',j,n,rng,.7); state.candidates[cid]=c; ch.append(c)
        basins[bid]=_select_local(selector,inc,ch,brief,state,'roundA')
    _,survivors,ds=route_aware_frontier(selector,list(basins.values()),brief); _record(state,'allocate-frontier',ds); live={c.basin for c in survivors}; basins={k:v for k,v in basins.items() if k in live}; montage(list(basins.values()),out_dir/'stage2_survivors.png','Stage 2 survivors')
    remaining=int(brief.get('total_extra_budget',12)); vals=list(basins.values()); allocations={}
    share=remaining//len(vals)
    for c in vals: allocations[c.basin]=share
    for c in vals[:remaining-share*len(vals)]: allocations[c.basin]+=1
    for bid,budget in allocations.items():
        inc=basins[bid]; champion=inc
        for j in range(budget):
            parent=champion if j<budget*.7 else inc; scale=.55 if j<budget*.7 else 1.2; cid=f'{bid}-R{j+1}'
            c=_spawn(brief,seed,parent,cid,'refine',j,budget,rng,scale); state.candidates[cid]=c; champion,d=incumbent_challenge(selector,champion,c,brief); _record(state,'refine',[d])
        basins[bid]=champion
    winner,frontier,ds=route_aware_frontier(selector,list(basins.values()),brief); _record(state,'final',ds); status='clear' if len(frontier)==1 else 'tie-defer'; state.winner_id=winner.id if status=='clear' else None
    montage(frontier,out_dir/'finalists.png','Artistic frontier'); timeline(winner,out_dir/'winner_timeline.png')
    invalid=[c for c in state.candidates.values() if not c.checks.get('valid',False)]; counts={'a':0,'b':0,'tie':0}; sources={}
    for d in state.stage_decisions:
        if d.get('verdict') in counts: counts[d['verdict']]+=1
        if d.get('source'): sources[d['source']]=sources.get(d['source'],0)+1
    operator_counts={'native':0,'spectral':0}
    operator_valid={'native':0,'spectral':0}
    if mode==FAMILY_PROJECTED_V1:
        operator_counts['projected-spectral']=0; operator_valid['projected-spectral']=0
    for c in state.candidates.values():
        op=c.checks.get('generationOperator')
        if op in operator_counts:
            operator_counts[op]+=1
            if c.checks.get('valid',False): operator_valid[op]+=1
    report={'winner':winner.id if status=='clear' else None,'provisionalChampion':winner.id,'route':winner.route,'diagnosticScore':winner.score,'selectionStatus':status,'artisticFrontier':[c.id for c in frontier],'features':winner.features,'winnerChecks':winner.checks,'allocations':allocations,'selector':selector.name,'mutationPortfolio':mode,'mutationPortfolioEligibleRoutes':_eligible_routes_for_portfolio(brief),'generationOperatorCounts':operator_counts,'generationOperatorValidCounts':operator_valid,'selectorSummary':{'diagnosticScoreUsedForPromotion':False,'decisionCount':sum(counts.values()),'verdictCounts':counts,'sourceCounts':sources},'checkerSummary':{'totalCandidates':len(state.candidates),'invalidCandidates':len(invalid),'invalidByRoute':{r:sum(c.route==r for c in invalid) for r in brief['routes']},'occupancyPolicy':'diagnostic-only; representation validity is topology/geometry-specific'},'finalists':[{'id':c.id,'route':c.route,'diagnosticScore':c.score,'valid':c.checks.get('valid',False)} for c in frontier]}
    (out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n'); (out_dir/'search_state.json').write_text(json.dumps(state.to_json(),indent=2)+'\n'); return state,report

def run_search_from_starts(brief,seed,out_dir:Path,starts:Sequence[Candidate],selector:Optional[PairwiseSelector]=None):
    """Run the adaptive search from exact externally generated start phenotypes."""
    _portfolio_mode(brief)
    out_dir.mkdir(parents=True,exist_ok=True); selector=selector or DeterministicTemporalSelector(); rng=random.Random(seed); state=SearchState(brief,seed); basins={}
    routes=tuple(brief.get('routes') or ())
    if not routes: raise ValueError('brief must define at least one active route')
    start_list=list(starts)
    if not start_list: raise ValueError('starts must contain at least one candidate')
    by_route={r:0 for r in routes}
    for cand in start_list:
        if cand.route not in by_route: raise ValueError(f'start candidate {cand.id!r} uses inactive route {cand.route!r}')
        if cand.id in basins: raise ValueError(f'duplicate start candidate id {cand.id!r}')
        if cand.basin != cand.id: raise ValueError(f'start candidate {cand.id!r} must use its own id as basin')
        evaluate_candidate(cand,brief)
        if not cand.checks.get('valid',False): raise ValueError(f'start candidate {cand.id!r} is invalid under the active brief')
        state.candidates[cand.id]=cand; basins[cand.id]=cand; by_route[cand.route]+=1
    missing=[r for r,n in by_route.items() if n==0]
    if missing: raise ValueError(f'active route(s) have no reviewed start candidate: {missing}')
    return _finish_search(brief,seed,out_dir,selector,state,basins,rng)
def run_search(brief,seed,out_dir:Path,selector:Optional[PairwiseSelector]=None):
    _portfolio_mode(brief)
    rng=random.Random(seed); state=SearchState(brief,seed); out_dir.mkdir(parents=True,exist_ok=True); selector=selector or DeterministicTemporalSelector(); basins={}
    for route in brief['routes']:
        prefix=ROUTES[route].get('prefix',route[:1].upper())
        for i in range(int(brief.get('starts_per_route',3))):
            cid=f'{prefix}S{i+1}'; cand=None
            for attempt in range(1,21):
                trial=Candidate(cid,route,cid,ROUTES[route]['seed'](rng),None,'start'); evaluate_candidate(trial,brief)
                if trial.checks['valid']: cand=trial; break
                trial.id=f'{cid}-invalid{attempt}'; state.candidates[trial.id]=trial
            if cand is None: raise RuntimeError(f'could not seed valid {route}')
            state.candidates[cid]=cand; basins[cid]=cand
    return _finish_search(brief,seed,out_dir,selector,state,basins,rng)
