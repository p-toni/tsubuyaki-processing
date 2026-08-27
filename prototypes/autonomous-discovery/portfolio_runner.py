from __future__ import annotations
import json, math
from dataclasses import asdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from core import Candidate, ROUTES, TIMES, evaluate_candidate, render_candidate_frame
from pairwise_selector import DeterministicTemporalSelector, incumbent_challenge, route_aware_frontier
from rng_streams import representation_rng

ARM_STREAM = 'representation-portfolio-arm-v1'

def _decision_json(d, stage):
    x=d.to_json(); x['stage']=stage; return x

def _arm_search(brief, seed, route, attempt_budget, selector, starts=2):
    if attempt_budget < starts:
        raise ValueError(f'arm budget {attempt_budget} must be >= starts {starts}')
    rng=representation_rng(seed,route,ROUTES[route].get('version','1'),ARM_STREAM)
    prefix=ROUTES[route].get('prefix',route[:1].upper()); candidates={}; decisions=[]; basins=[]; attempts=0; seed_index=0
    while len(basins)<starts and attempts<attempt_budget:
        seed_index+=1; cid=f'{prefix}P{seed_index}'; c=Candidate(cid,route,cid,ROUTES[route]['seed'](rng),None,'portfolio-start'); evaluate_candidate(c,brief); attempts+=1; candidates[cid]=c
        if c.checks.get('valid',False):basins.append(c)
    if len(basins) < starts:
        raise RuntimeError(f'portfolio arm {route} produced only {len(basins)}/{starts} valid starts within budget')
    champions={c.basin:c for c in basins}; basin_order=[c.basin for c in basins]; mutation_index=0
    while attempts<attempt_budget:
        bid=basin_order[mutation_index%len(basin_order)]; inc=champions[bid]; mutation_index+=1
        scale=1.15 if mutation_index % 5 == 0 else .72
        cid=f'{bid}-M{mutation_index}'; c=Candidate(cid,route,bid,ROUTES[route]['mutate'](inc.genome,rng,scale),inc.id,'portfolio-mutate'); evaluate_candidate(c,brief); attempts+=1; candidates[cid]=c
        champion,d=incumbent_challenge(selector,inc,c,brief); decisions.append(_decision_json(d,f'arm:{route}')); champions[bid]=champion
    arm_champion,frontier,ds=route_aware_frontier(selector,list(champions.values()),brief); decisions.extend(_decision_json(d,f'arm-frontier:{route}') for d in ds)
    return {'route':route,'budget':attempt_budget,'attempts':attempts,'candidateCount':len(candidates),'invalidCount':sum(not c.checks.get('valid',False) for c in candidates.values()),'champion':arm_champion,'frontier':frontier,'candidates':candidates,'decisions':decisions}

def _montage(cands,out,title):
    thumb=170; cols=min(4,max(1,len(cands))); rows=max(1,math.ceil(len(cands)/cols)); can=Image.new('RGB',(cols*thumb,28+rows*(thumb+20)),(26,26,26)); d=ImageDraw.Draw(can); d.text((6,6),title,fill=(240,240,240))
    for i,c in enumerate(cands):
        x=(i%cols)*thumb; y=28+(i//cols)*(thumb+20); im=ImageOps.autocontrast(render_candidate_frame(c,90)).convert('RGB').resize((thumb,thumb)); can.paste(im,(x,y)); d.text((x+4,y+thumb+2),c.id,fill=(220,220,220))
    can.save(out)
def _timeline(c,out):
    thumb=180; can=Image.new('RGB',(thumb*len(TIMES),thumb+20),(26,26,26)); d=ImageDraw.Draw(can)
    for i,t in enumerate(TIMES):can.paste(render_candidate_frame(c,t).convert('RGB').resize((thumb,thumb)),(i*thumb,0)); d.text((i*thumb+6,thumb+2),f't={t}',fill=(230,230,230))
    can.save(out)
def run_policy(brief,seed,out_dir:Path,policy,total_budget,selector=None,starts=2):
    selector=selector or DeterministicTemporalSelector(); out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    eligible=list(brief.get('eligible_routes') or brief.get('routes') or [])
    if not eligible:raise ValueError('brief must define eligible_routes or routes')
    unknown=[r for r in eligible if r not in ROUTES]
    if unknown:raise ValueError(f'unknown eligible representation(s): {unknown}')
    if policy=='route-first':
        chosen=brief.get('route_first')
        if chosen not in eligible:raise ValueError('route-first policy requires brief.route_first to be one eligible route')
        routes=[chosen]; budgets={chosen:int(total_budget)}
    elif policy=='portfolio-equal':
        routes=sorted(eligible)
        if int(total_budget)%len(routes):raise ValueError('portfolio-equal requires total_budget divisible by eligible route count')
        each=int(total_budget)//len(routes); budgets={r:each for r in routes}
    else:raise ValueError(f'unknown policy {policy!r}')
    arms=[]; all_candidates={}; all_decisions=[]
    for route in routes:
        arm=_arm_search(brief,seed,route,budgets[route],selector,starts=starts); arms.append(arm); all_candidates.update(arm['candidates']); all_decisions.extend(arm['decisions'])
    arm_champions=[a['champion'] for a in arms]
    winner,frontier,ds=route_aware_frontier(selector,arm_champions,brief); all_decisions.extend(_decision_json(d,'representation-frontier') for d in ds)
    status='clear' if len(frontier)==1 else 'tie-defer'; _montage(arm_champions,out_dir/'representation_champions.png','Representation champions'); _montage(frontier,out_dir/'finalists.png','Policy artistic frontier'); _timeline(winner,out_dir/'winner_timeline.png')
    verdict_counts={'a':0,'b':0,'tie':0}; sources={}
    for d in all_decisions:
        if d.get('verdict') in verdict_counts:verdict_counts[d['verdict']]+=1
        s=d.get('source')
        if s: sources[s]=sources.get(s,0)+1
    report={'policy':policy,'seed':seed,'totalAttemptBudget':int(total_budget),'routeBudgets':budgets,'eligibleRoutes':eligible,'routeFirst':brief.get('route_first'),'rngPolicy':'representation-substreams-v1','armStream':ARM_STREAM,'selectionStatus':status,'winner':winner.id if status=='clear' else None,'provisionalChampion':winner.id,'winnerRoute':winner.route,'artisticFrontier':[c.id for c in frontier],'representationChampions':[{'route':a['route'],'id':a['champion'].id,'budget':a['budget'],'attempts':a['attempts'],'candidateCount':a['candidateCount'],'invalidCount':a['invalidCount']} for a in arms],'selector':selector.name,'selectorSummary':{'decisionCount':sum(verdict_counts.values()),'verdictCounts':verdict_counts,'sourceCounts':sources,'diagnosticScoreUsedForPromotion':False}}
    state={'brief':brief,'seed':seed,'policy':policy,'rngPolicy':'representation-substreams-v1','routeBudgets':budgets,'candidates':{k:asdict(v) for k,v in all_candidates.items()},'decisions':all_decisions,'frontier':[c.id for c in frontier]}
    (out_dir/'portfolio_report.json').write_text(json.dumps(report,indent=2)+'\n'); (out_dir/'portfolio_state.json').write_text(json.dumps(state,indent=2)+'\n'); return state,report,winner,frontier
