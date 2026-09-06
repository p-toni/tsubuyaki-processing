#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RENDER=HERE.parent/'render_exact_post.mjs'


def run(cmd):
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed: {' '.join(map(str,cmd))}\nstdout:\n{p.stdout}\nstderr:\n{p.stderr}")
    return p


def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--attempt',required=True); ap.add_argument('--out',required=True); args=ap.parse_args()
    attempt=Path(args.attempt)
    data=json.loads(attempt.read_text()); records=data['records']
    if len(records)!=9: raise AssertionError(f'expected 9 selected R compression records, got {len(records)}')
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True); verified=[]
    for rec in records:
        bid=rec['briefId']; root=out/bid; root.mkdir(parents=True,exist_ok=True)
        post=root/'post.txt'; post.write_text(rec['post']+'\n')
        length=json.loads(run(['node','scripts/check-length.mjs',str(post)]).stdout)
        if not length['pass']: raise AssertionError(f'{bid} exact post length failed: {length}')
        frames=[str(int(x)) for x in rec['horizonFrames']]
        run(['node',str(RENDER),str(post),str(root/'frames'),*frames])
        verified.append({'briefId':bid,'sourceCandidateId':rec['sourceCandidateId'],'horizonFrames':rec['horizonFrames'],'length':length,'runtimePass':True,'spectralModes':rec.get('retainedModes',rec.get('dominantMode'))})
    thumb=140; label=24; sheet=Image.new('RGB',(thumb*4,len(verified)*(thumb+label)),(18,18,18)); d=ImageDraw.Draw(sheet)
    for i,rec in enumerate(verified):
        y=i*(thumb+label); d.text((5,y+4),rec['briefId'],fill=(235,235,235))
        for j,t in enumerate(rec['horizonFrames']):
            im=Image.open(out/rec['briefId']/'frames'/f'frame-{int(t):03d}.png').convert('RGB').resize((thumb,thumb),Image.Resampling.LANCZOS)
            sheet.paste(im,(j*thumb,y+label))
    sheet.save(out/'contact-sheet.png')
    result={'version':1,'arm':'R','stage':data['stage']+'-exact-verification','attemptFile':attempt.name,'count':len(verified),'allLengthPass':all(r['length']['pass'] for r in verified),'allRuntimePass':True,'records':verified}
    (out/'verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()
