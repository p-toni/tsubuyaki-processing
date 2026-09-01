#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from PIL import Image
import torch
import torchvision
from torchvision.models import ResNet18_Weights, resnet18

ALPHA = 1.0
EXPECTED_TORCH = '2.10.0'
EXPECTED_TORCHVISION = '0.25.0'
EXPECTED_WEIGHT_URL = 'https://download.pytorch.org/models/resnet18-f37072fd.pth'
MODEL_EXPERIMENTS = ('104','107','112','114')
NEUTRAL_EXPERIMENT = '79'


def _load_base_analyzer(repo_root: Path):
    path = repo_root / 'experiments' / 'artistic-signal-retrospective-v1' / 'analyze.py'
    spec = importlib.util.spec_from_file_location('artistic_signal_v1_frozen', path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot import frozen extractor {path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def _checkpoint_path(weights: ResNet18_Weights) -> Path:
    filename=Path(urlparse(weights.url).path).name
    return Path(torch.hub.get_dir()) / 'checkpoints' / filename


def _build_encoder():
    if torch.__version__.split('+',1)[0] != EXPECTED_TORCH:
        raise AssertionError(f'torch version drift: {torch.__version__}')
    if torchvision.__version__.split('+',1)[0] != EXPECTED_TORCHVISION:
        raise AssertionError(f'torchvision version drift: {torchvision.__version__}')
    weights=ResNet18_Weights.IMAGENET1K_V1
    if weights.url != EXPECTED_WEIGHT_URL:
        raise AssertionError(f'weight URL drift: {weights.url}')
    model=resnet18(weights=weights)
    model.fc=torch.nn.Identity()
    model.eval()
    transform=weights.transforms()
    ckpt=_checkpoint_path(weights)
    if not ckpt.is_file():
        raise AssertionError(f'expected downloaded checkpoint missing: {ckpt}')
    return model,transform,weights,ckpt


def _encode_tiles(model, transform, tiles, batch_size=64):
    tensors=[]
    for tile in tiles:
        im=Image.fromarray(np.asarray(tile,dtype=np.uint8),mode='L').convert('RGB')
        tensors.append(transform(im))
    outputs=[]
    with torch.inference_mode():
        for i in range(0,len(tensors),batch_size):
            batch=torch.stack(tensors[i:i+batch_size],dim=0)
            out=model(batch).detach().cpu().numpy().astype(np.float64)
            outputs.append(out)
    emb=np.concatenate(outputs,axis=0)
    if emb.ndim != 2 or emb.shape[1] != 512 or not np.isfinite(emb).all():
        raise AssertionError(f'invalid embedding shape/values: {emb.shape}')
    return emb


def _side_representation(model, transform, rows):
    tiles=[tile for row in rows for tile in row]
    emb=_encode_tiles(model,transform,tiles)
    mean=emb.mean(axis=0)
    sd=emb.std(axis=0)
    rep=np.concatenate([mean,sd],axis=0)
    if rep.shape != (1024,) or not np.isfinite(rep).all():
        raise AssertionError('invalid side representation')
    return rep


def _label_value(j):
    return 1 if j=='A>B' else -1 if j=='B>A' else 0


def _load_blocks(root: Path, exp: str, base, model, transform, horizontal79=False):
    rows=[]
    ratings=base.RATINGS[exp]
    expected=20 if exp=='79' else 12
    pngs=sorted(root.glob('R*.png'))
    if len(pngs) != expected:
        raise AssertionError(f'{exp}: expected {expected} R*.png, got {len(pngs)} at {root}')
    for label,j in ratings.items():
        path=root/f'{label}.png'
        if not path.is_file():
            raise AssertionError(f'missing {path}')
        sides=base._horizontal79_tiles(path) if horizontal79 else base._vertical_tiles(path)
        ra=_side_representation(model,transform,sides['A'])
        rb=_side_representation(model,transform,sides['B'])
        rows.append({
            'experiment':exp,
            'label':label,
            'judgment':j,
            'y':_label_value(j),
            'x':ra-rb,
            'imageSha256':_sha256(path),
        })
    return rows


def _fit_predict(train,test):
    X=np.asarray([r['x'] for r in train],dtype=np.float64)
    y=np.asarray([r['y'] for r in train],dtype=np.float64)
    T=np.asarray([r['x'] for r in test],dtype=np.float64)
    mu=X.mean(axis=0)
    sd=X.std(axis=0)
    sd=np.where(sd>1e-12,sd,1.0)
    Xz=(X-mu)/sd
    Tz=(T-mu)/sd
    dual=np.linalg.solve(Xz@Xz.T + ALPHA*np.eye(Xz.shape[0]), y)
    pred=Tz@Xz.T@dual
    w=Xz.T@dual
    return pred,w


def _binom_one_sided(correct,n):
    return sum(math.comb(n,k) for k in range(correct,n+1))/(2**n)


def analyze(repo_root: Path, roots: dict[str,Path]):
    base,base_path=_load_base_analyzer(repo_root)
    base_blob=subprocess_git_hash_object(repo_root,base_path)
    expected_base_blob='2b57c5748c9aed1c522c9b2003623f62406f94cc'
    if base_blob != expected_base_blob:
        raise AssertionError(f'frozen extractor blob drift: {base_blob}')

    torch.manual_seed(0)
    torch.set_num_threads(max(1,min(4,torch.get_num_threads())))
    model,transform,weights,ckpt=_build_encoder()

    experiments={e:_load_blocks(roots[e],e,base,model,transform,False) for e in MODEL_EXPERIMENTS}
    neutral=_load_blocks(roots['79'],'79',base,model,transform,True)

    folds=[]; all_decisive=[]
    for hold in MODEL_EXPERIMENTS:
        train=[r for e,rr in experiments.items() if e!=hold for r in rr]
        test=experiments[hold]
        pred,w=_fit_predict(train,test)
        decisive=[]
        for r,p in zip(test,pred):
            if r['y']:
                correct=int((p>0 and r['y']>0) or (p<0 and r['y']<0))
                signed=float(r['y']*p)
                item={'label':r['label'],'y':r['y'],'prediction':float(p),'correct':correct,'signedMargin':signed}
                decisive.append(item); all_decisive.append(item|{'experiment':hold})
        acc=sum(d['correct'] for d in decisive)/len(decisive)
        margin=float(np.mean([d['signedMargin'] for d in decisive]))
        folds.append({
            'holdout':hold,
            'decisiveCount':len(decisive),
            'accuracy':acc,
            'meanSignedMargin':margin,
            'weightL2Norm':float(np.linalg.norm(w)),
            'decisive':decisive,
        })

    correct=sum(d['correct'] for d in all_decisive)
    n=len(all_decisive)
    acc=correct/n
    p=_binom_one_sided(correct,n)

    train_all=[r for rr in experiments.values() for r in rr]
    neutral_pred,w=_fit_predict(train_all,neutral)
    neutral_mean_abs=float(np.mean(np.abs(neutral_pred)))

    gates={
        'invariantsFinite': bool(np.isfinite([d['prediction'] for d in all_decisive]).all() and np.isfinite(neutral_pred).all()),
        'pooledAccuracyAbovePoint60': acc>0.60,
        'oneSidedBinomialPAtMostPoint10': p<=0.10,
        'everyHoldoutAccuracyAtLeastPoint50': all(f['accuracy']>=0.50 for f in folds),
        'everyHoldoutMeanSignedMarginPositive': all(f['meanSignedMargin']>0 for f in folds),
        'externalAllEquivalentMeanAbsPredictionAtMostPoint25': neutral_mean_abs<=0.25,
    }
    decision='RESNET18_ARTISTIC_SIGNAL_PROMISING' if all(gates.values()) else 'RESNET18_ARTISTIC_SIGNAL_NOT_PROMISING'
    return {
        'version':1,
        'decision':decision,
        'representation':{
            'name':'torchvision-resnet18-imagenet1k-v1-post-avgpool',
            'torch':torch.__version__,
            'torchvision':torchvision.__version__,
            'weightEnum':'ResNet18_Weights.IMAGENET1K_V1',
            'weightUrl':weights.url,
            'checkpointFilename':ckpt.name,
            'checkpointSha256':_sha256(ckpt),
            'tileTransform':str(transform),
            'sidePooling':'concat(population mean 512d, population sd 512d)',
            'blockOperation':'sideA - sideB',
            'dimension':1024,
            'frozenExtractorBlob':base_blob,
        },
        'model':'zero-intercept dual ridge alpha=1.0; train-fold standardization',
        'population':{'modelBlocks':48,'modelDecisive':44,'modelEquivalent':4,'externalNeutralBlocks':20},
        'pooledDecisive':{'correct':correct,'count':n,'accuracy':acc,'oneSidedExactBinomialP':p},
        'folds':folds,
        'externalNeutral79':{
            'meanAbsolutePrediction':neutral_mean_abs,
            'weightL2Norm':float(np.linalg.norm(w)),
            'predictions':[{'label':r['label'],'prediction':float(v)} for r,v in zip(neutral,neutral_pred)],
        },
        'gates':gates,
        'sourceImageSha256':{e:{r['label']:r['imageSha256'] for r in rr} for e,rr in experiments.items()} | {'79':{r['label']:r['imageSha256'] for r in neutral}},
        'boundary':'retrospective consumed-human-label audit only; positive authorizes fresh prospective exact-pipeline scorer test; negative closes generic frozen ImageNet embedding line without backbone/hyperparameter cycling',
    }


def subprocess_git_hash_object(repo_root: Path,path: Path):
    import subprocess
    return subprocess.check_output(['git','hash-object',str(path.relative_to(repo_root))],cwd=repo_root,text=True).strip()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',default='.')
    for e in (*MODEL_EXPERIMENTS,'79'):
        ap.add_argument(f'--root{e}',required=True)
    ap.add_argument('--output',required=True)
    a=ap.parse_args()
    roots={e:Path(getattr(a,f'root{e}')) for e in (*MODEL_EXPERIMENTS,'79')}
    result=analyze(Path(a.repo_root).resolve(),roots)
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    Path(a.output).write_text(text)
    print(json.dumps({
        'decision':result['decision'],
        'pooledDecisive':result['pooledDecisive'],
        'folds':[{k:f[k] for k in ('holdout','decisiveCount','accuracy','meanSignedMargin')} for f in result['folds']],
        'externalNeutral79':{'meanAbsolutePrediction':result['externalNeutral79']['meanAbsolutePrediction']},
        'gates':result['gates'],
        'checkpointSha256':result['representation']['checkpointSha256'],
    },indent=2,sort_keys=True))

if __name__=='__main__':
    main()
