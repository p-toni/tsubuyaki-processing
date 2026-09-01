#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

FEATURES = (
    'ink_mean',
    'ink_sd',
    'bbox_span_mean',
    'center_offset_mean',
    'temporal_change_mean',
    'temporal_change_sd',
    'candidate_dispersion_mean',
    'candidate_dispersion_min',
    'candidate_dispersion_sd',
)

RATINGS = {
    '104': {
        'R01':'B>A','R02':'B>A','R03':'A>B','R04':'B>A','R05':'A>B','R06':'A>B',
        'R07':'A>B','R08':'A>B','R09':'A>B','R10':'B>A','R11':'A>B','R12':'A>B',
    },
    '107': {
        'R01':'B>A','R02':'B>A','R03':'B>A','R04':'B>A','R05':'B>A','R06':'A>B',
        'R07':'B>A','R08':'A>B','R09':'B>A','R10':'B>A','R11':'A>B','R12':'A>B',
    },
    '112': {
        'R01':'B>A','R02':'B>A','R03':'A>B','R04':'B>A','R05':'A>B','R06':'A>B',
        'R07':'equivalent','R08':'B>A','R09':'equivalent','R10':'B>A','R11':'A>B','R12':'A>B',
    },
    '114': {
        'R01':'A>B','R02':'A>B','R03':'equivalent','R04':'equivalent','R05':'A>B','R06':'B>A',
        'R07':'A>B','R08':'A>B','R09':'A>B','R10':'A>B','R11':'A>B','R12':'A>B',
    },
    '79': {f'R{i:02d}':'equivalent' for i in range(1,21)},
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resize_tile(arr: np.ndarray) -> np.ndarray:
    im = Image.fromarray(arr.astype(np.uint8), mode='L')
    return np.asarray(im.resize((96,96), Image.Resampling.NEAREST), dtype=np.float64)


def _crop_frac(arr: np.ndarray, left: float, top: float, right: float, bottom: float) -> np.ndarray:
    h,w = arr.shape
    x0 = int(round(w*left)); x1 = int(round(w*(1-right)))
    y0 = int(round(h*top)); y1 = int(round(h*(1-bottom)))
    if x1 <= x0 or y1 <= y0:
        raise AssertionError('fractional crop collapsed')
    return arr[y0:y1,x0:x1]


def _vertical_tiles(path: Path):
    arr = np.asarray(Image.open(path).convert('L'))
    h,w = arr.shape
    dark = (arr < 50).mean(axis=1)
    runs=[]; start=None
    for i,v in enumerate(dark):
        if v > 0.80 and start is None:
            start=i
        if start is not None and (v <= 0.80 or i == h-1):
            end=i if v <= 0.80 else i+1
            if end-start >= 100:
                runs.append((start,end))
            start=None
    if len(runs) != 6:
        raise AssertionError(f'{path}: expected six dark strips, got {runs}')
    sides={'A':[], 'B':[]}
    for ri,(y0,y1) in enumerate(runs):
        row=[]
        strip=arr[y0:y1,:]
        for t in range(3):
            x0=(t*w)//3; x1=((t+1)*w)//3
            tile=_crop_frac(strip[:,x0:x1], .05,.05,.05,.05)
            row.append(_resize_tile(tile))
        sides['A' if ri < 3 else 'B'].append(row)
    return sides


def _horizontal79_tiles(path: Path):
    arr=np.asarray(Image.open(path).convert('L'))
    h,w=arr.shape
    lo=int(w*.40); hi=int(w*.60)
    bright=(arr[:,lo:hi] > 30).mean(axis=0)
    divider=lo+int(np.argmax(bright))
    if not (w*.45 <= divider <= w*.55):
        raise AssertionError(f'{path}: invalid divider {divider}/{w}')
    body_start=int(round(h*.04))
    sides={}
    for name,(xlo,xhi) in {'A':(0,divider),'B':(divider+1,w)}.items():
        half=arr[body_start:h,xlo:xhi]
        hh,ww=half.shape
        rows=[]
        for r in range(6):
            y0=(r*hh)//6; y1=((r+1)*hh)//6
            row=[]
            band=half[y0:y1,:]
            for t in range(3):
                xx0=(t*ww)//3; xx1=((t+1)*ww)//3
                tile=_crop_frac(band[:,xx0:xx1], .05,.15,.05,.10)
                row.append(_resize_tile(tile))
            rows.append(row)
        sides[name]=rows
    return sides


def _tile_stats(tile: np.ndarray):
    mask=tile > 20
    ink=float(mask.mean())
    if not mask.any():
        return ink,0.0,1.0
    ys,xs=np.nonzero(mask)
    bbox=max((xs.max()-xs.min()+1)/96.0,(ys.max()-ys.min()+1)/96.0)
    dx=(xs.mean()-47.5)/48.0; dy=(ys.mean()-47.5)/48.0
    center=(dx*dx+dy*dy)**0.5/(2**0.5)
    return ink,float(bbox),float(center)


def _mad(a: np.ndarray,b: np.ndarray) -> float:
    return float(np.mean(np.abs(a-b))/255.0)


def side_features(rows):
    inks=[]; bbox=[]; centers=[]; temporal=[]
    for row in rows:
        if len(row) != 3:
            raise AssertionError('every candidate row must have three temporal frames')
        for tile in row:
            i,b,c=_tile_stats(tile); inks.append(i); bbox.append(b); centers.append(c)
        temporal.extend((_mad(row[0],row[1]),_mad(row[1],row[2])))
    pair_d=[]
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):
            pair_d.append(float(np.mean([_mad(rows[i][t],rows[j][t]) for t in range(3)])))
    if not pair_d:
        raise AssertionError('need at least two candidates per side')
    vals={
        'ink_mean':float(np.mean(inks)),
        'ink_sd':float(np.std(inks)),
        'bbox_span_mean':float(np.mean(bbox)),
        'center_offset_mean':float(np.mean(centers)),
        'temporal_change_mean':float(np.mean(temporal)),
        'temporal_change_sd':float(np.std(temporal)),
        'candidate_dispersion_mean':float(np.mean(pair_d)),
        'candidate_dispersion_min':float(np.min(pair_d)),
        'candidate_dispersion_sd':float(np.std(pair_d)),
    }
    return np.asarray([vals[k] for k in FEATURES],dtype=np.float64),vals


def label_value(j: str) -> int:
    return 1 if j=='A>B' else -1 if j=='B>A' else 0


def load_blocks(root: Path, exp: str, horizontal79: bool=False):
    rows=[]
    ratings=RATINGS[exp]
    for label,j in ratings.items():
        path=root/f'{label}.png'
        if not path.is_file():
            raise AssertionError(f'missing {path}')
        sides=_horizontal79_tiles(path) if horizontal79 else _vertical_tiles(path)
        fa,da=side_features(sides['A']); fb,db=side_features(sides['B'])
        rows.append({
            'experiment':exp,'label':label,'judgment':j,'y':label_value(j),
            'x':(fa-fb).tolist(),'A':da,'B':db,'imageSha256':_sha256(path),
        })
    return rows


def fit_predict(train, test):
    X=np.asarray([r['x'] for r in train],dtype=np.float64)
    y=np.asarray([r['y'] for r in train],dtype=np.float64)
    T=np.asarray([r['x'] for r in test],dtype=np.float64)
    mu=X.mean(axis=0); sd=X.std(axis=0); sd=np.where(sd>1e-12,sd,1.0)
    Xz=(X-mu)/sd; Tz=(T-mu)/sd
    w=np.linalg.solve(Xz.T@Xz + np.eye(Xz.shape[1]), Xz.T@y)
    return Tz@w, w, mu, sd


def binom_one_sided(correct: int,n: int) -> float:
    return sum(math.comb(n,k) for k in range(correct,n+1))/(2**n)


def analyze(roots):
    experiments={e:load_blocks(Path(roots[e]),e,False) for e in ('104','107','112','114')}
    neutral=load_blocks(Path(roots['79']),'79',True)
    folds=[]; all_decisive=[]
    for hold in ('104','107','112','114'):
        train=[r for e,rr in experiments.items() if e!=hold for r in rr]
        test=experiments[hold]
        pred,w,mu,sd=fit_predict(train,test)
        decisive=[]
        for r,p in zip(test,pred):
            if r['y']:
                correct=int((p>0 and r['y']>0) or (p<0 and r['y']<0))
                signed=float(r['y']*p)
                decisive.append({'label':r['label'],'y':r['y'],'prediction':float(p),'correct':correct,'signedMargin':signed})
                all_decisive.append(decisive[-1] | {'experiment':hold})
        acc=sum(d['correct'] for d in decisive)/len(decisive)
        margin=float(np.mean([d['signedMargin'] for d in decisive]))
        folds.append({'holdout':hold,'decisiveCount':len(decisive),'accuracy':acc,'meanSignedMargin':margin,'weights':dict(zip(FEATURES,map(float,w))),'decisive':decisive})
    correct=sum(d['correct'] for d in all_decisive); n=len(all_decisive); acc=correct/n; p=binom_one_sided(correct,n)
    train_all=[r for rr in experiments.values() for r in rr]
    neutral_pred,w,mu,sd=fit_predict(train_all,neutral)
    neutral_mean_abs=float(np.mean(np.abs(neutral_pred)))
    neutral_rows=[{'label':r['label'],'prediction':float(v)} for r,v in zip(neutral,neutral_pred)]
    gates={
        'invariantsFinite': bool(np.isfinite([d['prediction'] for d in all_decisive]).all() and np.isfinite(neutral_pred).all()),
        'pooledAccuracyAbovePoint60': acc>0.60,
        'oneSidedBinomialPAtMostPoint10': p<=0.10,
        'everyHoldoutAccuracyAtLeastPoint50': all(f['accuracy']>=0.50 for f in folds),
        'everyHoldoutMeanSignedMarginPositive': all(f['meanSignedMargin']>0 for f in folds),
        'externalAllEquivalentMeanAbsPredictionAtMostPoint25': neutral_mean_abs<=0.25,
    }
    decision='SIMPLE_ARTISTIC_SIGNAL_PROMISING' if all(gates.values()) else 'SIMPLE_ARTISTIC_SIGNAL_NOT_PROMISING'
    return {
        'version':1,'decision':decision,'features':list(FEATURES),'model':'zero-intercept ridge alpha=1.0; train-fold standardization',
        'population':{'modelBlocks':48,'modelDecisive':44,'modelEquivalent':4,'externalNeutralBlocks':20},
        'pooledDecisive':{'correct':correct,'count':n,'accuracy':acc,'oneSidedExactBinomialP':p},
        'folds':folds,
        'externalNeutral79':{'meanAbsolutePrediction':neutral_mean_abs,'predictions':neutral_rows,'weights':dict(zip(FEATURES,map(float,w)))},
        'gates':gates,
        'sourceBlocks':{e:experiments[e] for e in experiments} | {'79':neutral},
        'boundary':'retrospective consumed-human-label audit only; positive authorizes fresh prospective scorer test, not production; negative closes exact handcrafted descriptor family without tuning',
    }


def main():
    ap=argparse.ArgumentParser()
    for e in ('104','107','112','114','79'):
        ap.add_argument(f'--root{e}',required=True)
    ap.add_argument('--output',default='')
    a=ap.parse_args(); roots={e:getattr(a,f'root{e}') for e in ('104','107','112','114','79')}
    result=analyze(roots)
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.output: Path(a.output).write_text(text)
    print(text,end='')

if __name__=='__main__': main()
