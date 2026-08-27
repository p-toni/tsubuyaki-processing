#!/usr/bin/env python3
from __future__ import annotations
import json, math, random
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image, ImageDraw

from core import Candidate, SearchState, ROUTES, TIMES, evaluate_candidate, render_candidate_frame
from pairwise_selector import PairwiseSelector, DeterministicTemporalSelector, incumbent_challenge, route_aware_frontier

def _record(state,stage,decisions):
    for d in decisions:
        x=d.to_json(); x['stage']=stage; state.stage_decisions.append(x)

def _select_local(selector,incumbent,challengers,brief,state,stage):
    champion=incumbent
    for c in challengers:
        champion,d=incumbent_challenge(selector,champion,c,brief); _record(state,stage,[d])
    return champion

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

def run_search(brief,seed,out_dir:Path,selector:Optional[PairwiseSelector]=None):
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
    for bid,inc in list(basins.items()):
        ch=[]
        for j in range(int(brief.get('explore_per_basin',4))):
            cid=f'{bid}-E{j+1}'; c=Candidate(cid,inc.route,bid,ROUTES[inc.route]['mutate'](inc.genome,rng,1),inc.id,'explore'); evaluate_candidate(c,brief); state.candidates[cid]=c; ch.append(c)
        basins[bid]=_select_local(selector,inc,ch,brief,state,'explore')
    montage(list(basins.values()),out_dir/'stage1_representatives.png','Stage 1 representatives')
    _,survivors,ds=route_aware_frontier(selector,list(basins.values()),brief); _record(state,'frontier',ds); live={c.basin for c in survivors}; basins={k:v for k,v in basins.items() if k in live}
    for bid,inc in list(basins.items()):
        ch=[]
        for j in range(max(1,int(brief.get('roundA_per_survivor',3)))):
            cid=f'{bid}-A{j+1}'; c=Candidate(cid,inc.route,bid,ROUTES[inc.route]['mutate'](inc.genome,rng,.7),inc.id,'roundA'); evaluate_candidate(c,brief); state.candidates[cid]=c; ch.append(c)
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
            c=Candidate(cid,inc.route,bid,ROUTES[inc.route]['mutate'](parent.genome,rng,scale),parent.id,'refine'); evaluate_candidate(c,brief); state.candidates[cid]=c; champion,d=incumbent_challenge(selector,champion,c,brief); _record(state,'refine',[d])
        basins[bid]=champion
    winner,frontier,ds=route_aware_frontier(selector,list(basins.values()),brief); _record(state,'final',ds); status='clear' if len(frontier)==1 else 'tie-defer'; state.winner_id=winner.id if status=='clear' else None
    montage(frontier,out_dir/'finalists.png','Artistic frontier'); timeline(winner,out_dir/'winner_timeline.png')
    invalid=[c for c in state.candidates.values() if not c.checks.get('valid',False)]; counts={'a':0,'b':0,'tie':0}; sources={}
    for d in state.stage_decisions:
        if d.get('verdict') in counts: counts[d['verdict']]+=1
        if d.get('source'): sources[d['source']]=sources.get(d['source'],0)+1
    report={'winner':winner.id if status=='clear' else None,'provisionalChampion':winner.id,'route':winner.route,'diagnosticScore':winner.score,'selectionStatus':status,'artisticFrontier':[c.id for c in frontier],'features':winner.features,'winnerChecks':winner.checks,'allocations':allocations,'selector':selector.name,'selectorSummary':{'diagnosticScoreUsedForPromotion':False,'decisionCount':sum(counts.values()),'verdictCounts':counts,'sourceCounts':sources},'checkerSummary':{'totalCandidates':len(state.candidates),'invalidCandidates':len(invalid),'invalidByRoute':{r:sum(c.route==r for c in invalid) for r in brief['routes']},'occupancyPolicy':'diagnostic-only; representation validity is topology/geometry-specific'},'finalists':[{'id':c.id,'route':c.route,'diagnosticScore':c.score,'valid':c.checks.get('valid',False)} for c in frontier]}
    (out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n'); (out_dir/'search_state.json').write_text(json.dumps(state.to_json(),indent=2)+'\n'); return state,report
