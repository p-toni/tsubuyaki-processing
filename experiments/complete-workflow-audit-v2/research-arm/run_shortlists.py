#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,itertools,json,statistics,sys,tempfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageOps

HERE=Path(__file__).resolve().parent
EXP=HERE.parent
ROOT=HERE.parents[2]
PROTO=ROOT/'prototypes'/'autonomous-discovery'
sys.path.insert(0,str(PROTO))
import core,search_engine
from material_control import CONTROL_KEY
from rng_streams import derived_seed

DISTANCE_TIMES=(30,90,150)
DISTANCE_SIZE=100
MIN_VALID_GENERATED=12
SMOKE_SEED=768999
MASTER_SEEDS={
 'F01':768003,'F02':768019,'F03':768037,'F04':768053,'F05':768071,'F06':768089,
 'F07':768107,'F08':768127,'F09':768149,'F10':768167,'F11':768181,'F12':768199,
}

def runtime_brief(item):
    return {
      'name':'complete-workflow-audit-v2',
      'artistic_intent':item['intent'],
      'routes':['filament'],'bbox_target':[.55,.82],
      'starts_per_route':1,'explore_per_basin':4,'roundA_per_survivor':4,'total_extra_budget':12,
      'mutation_portfolio':search_engine.MIXED_1D_V1,
    }

def generated_valid(state):
    return [c for c in state.candidates.values() if c.stage!='start' and c.checks.get('generationOperator') in {'native','spectral'} and c.checks.get('valid',False)]

def phenotype_hash(c):
    h=hashlib.sha256()
    for t in DISTANCE_TIMES: h.update(core.render_candidate_frame(c,t).tobytes());h.update(b'\0')
    return h.hexdigest()

def vector(c):
    out=[]
    for t in DISTANCE_TIMES:
        im=core.render_candidate_frame(c,t).convert('L').resize((DISTANCE_SIZE,DISTANCE_SIZE),Image.Resampling.NEAREST)
        out.append(np.frombuffer(im.tobytes(),dtype=np.uint8).astype(np.int16))
    return np.concatenate(out)

def select_dispersion(cands):
    if len(cands)<MIN_VALID_GENERATED: raise AssertionError(f'need >={MIN_VALID_GENERATED} hard-valid generated candidates; found {len(cands)}')
    hashes=[phenotype_hash(c) for c in cands]
    if len(set(hashes))<3: raise AssertionError('fewer than three distinct generated phenotypes')
    v=[vector(c) for c in cands];n=len(v);d=np.zeros((n,n),dtype=float)
    for i in range(n):
      for j in range(i+1,n): d[i,j]=d[j,i]=float(np.abs(v[i]-v[j]).mean())/255.0
    best=None;score=None;eps=1e-15
    for combo in itertools.combinations(range(n),3):
        ds=(float(d[combo[0],combo[1]]),float(d[combo[0],combo[2]]),float(d[combo[1],combo[2]]));s=(min(ds),statistics.fmean(ds))
        if score is None or s[0]>score[0]+eps or (abs(s[0]-score[0])<=eps and s[1]>score[1]+eps): best,score=combo,s
    chosen=[cands[i] for i in best]
    if len({phenotype_hash(c) for c in chosen})!=3: raise AssertionError('shortlist phenotype collision')
    return chosen,{'indices':list(best),'minimumPairwiseDistance':score[0],'meanPairwiseDistance':score[1]}

def operator_diag(state):
    xs=[c for c in state.candidates.values() if c.stage!='start' and c.checks.get('generationOperator') in {'native','spectral'}]
    return {'total':len(xs),'native':sum(c.checks.get('generationOperator')=='native' for c in xs),'spectral':sum(c.checks.get('generationOperator')=='spectral' for c in xs),'valid':sum(bool(c.checks.get('valid')) for c in xs)}

def render_review_row(item,shortlist,thumb=110):
    times=item['horizonFrames'];row=Image.new('RGB',(thumb*12,thumb+28),(18,18,18));draw=ImageDraw.Draw(row)
    for ci,c in enumerate(shortlist):
      label=chr(ord('A')+ci);draw.text((ci*4*thumb+5,5),f"{item['id']} {label}",fill=(235,235,235))
      for ti,t in enumerate(times):
        im=ImageOps.autocontrast(core.render_candidate_frame(c,int(t))).convert('RGB').resize((thumb,thumb),Image.Resampling.LANCZOS)
        row.paste(im,((ci*4+ti)*thumb,28))
    return row

def one(item,master_seed,out_root):
    bid=item['id'];search_seed=derived_seed(master_seed,'complete-workflow-audit-v2',bid,'filament')
    with tempfile.TemporaryDirectory(prefix=f'cwa-v2-{bid}-') as td:
        state,report=search_engine.run_search(runtime_brief(item),search_seed,Path(td))
    diag=operator_diag(state)
    if diag['total']!=20 or diag['native']!=10 or diag['spectral']!=10: raise AssertionError(f'{bid} mixed budget drift: {diag}')
    valid=generated_valid(state);shortlist,disp=select_dispersion(valid)
    rec={'briefId':bid,'masterSeed':master_seed,'searchSeed':search_seed,'operatorDiagnostics':diag,'validGeneratedCount':len(valid),'selectionStatus':report['selectionStatus'],'dispersion':disp,'labels':{}}
    sealed={'briefId':bid,'masterSeed':master_seed,'searchSeed':search_seed,'labels':{}}
    for i,c in enumerate(shortlist):
        label=chr(ord('A')+i);control=c.genome.get(CONTROL_KEY);meta={'candidateId':c.id,'generationOperator':c.checks.get('generationOperator'),'phenotypeHash':phenotype_hash(c),'materialControlType':control.get('type') if isinstance(control,dict) else None,'genome':c.genome,'features':c.features}
        sealed['labels'][label]=meta;rec['labels'][label]={'phenotypeHash':meta['phenotypeHash']}
    return rec,sealed,render_review_row(item,shortlist)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--smoke',action='store_true');args=ap.parse_args()
    briefs=json.loads((EXP/'briefs.json').read_text())['briefs'];out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    if args.smoke:
        items=[briefs[0]];seeds={'F01':SMOKE_SEED};status='excluded-smoke'
    else:
        items=briefs;seeds=MASTER_SEEDS;status='authoritative-shortlists'
    records=[];sealed=[];rows=[]
    for item in items:
        rec,key,row=one(item,seeds[item['id']],out);records.append(rec);sealed.append(key);rows.append(row)
    sheet=Image.new('RGB',(rows[0].width,sum(r.height for r in rows)),(18,18,18));y=0
    for row in rows: sheet.paste(row,(0,y));y+=row.height
    sheet.save(out/'shortlist-contact-sheet.png')
    public={'version':2,'status':status,'artisticAuthority':False,'operatorIdentityBlindedForReview':True,'distanceFrames':list(DISTANCE_TIMES),'distanceSize':DISTANCE_SIZE,'selection':'target-blind raw-pixel max-dispersion size 3','records':records}
    (out/'review-manifest.json').write_text(json.dumps(public,indent=2,sort_keys=True)+'\n')
    (out/'sealed-shortlist-mapping.json').write_text(json.dumps({'version':2,'status':status,'records':sealed},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':status,'briefs':len(records),'allMixedBudgetExact':all(r['operatorDiagnostics']['total']==20 and r['operatorDiagnostics']['native']==10 and r['operatorDiagnostics']['spectral']==10 for r in records),'allMinimumValid':all(r['validGeneratedCount']>=MIN_VALID_GENERATED for r in records)},indent=2))
if __name__=='__main__': main()
