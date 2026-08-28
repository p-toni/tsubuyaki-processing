"""Blinded three-phenotype review transport with three explicit pair verdicts.

This is the transitivity-free triad transport selected by
``experiments/triad-pair-matrix-v1``. One A/B/C panel records three independent
pair judgments and decodes them to the existing v3 ``PhenotypePreferenceEvidence``
objects. No pair relation is inferred from a ranking.

Dependency-safe triad scheduling is intentionally outside this module.
"""
from __future__ import annotations

import hashlib
import io
import itertools
import json
from pathlib import Path
from typing import Mapping,Sequence

from PIL import Image,ImageDraw

from phenotype_preference_evidence import PhenotypePreferenceEvidence
from review_evidence_queue import THUMB,pair_id_for_phenotypes,phenotype_fingerprint

VERSION=1
REVIEW_TYPE='triad-pair-matrix'
PROMPT_VERSION='evidence-triad-pair-matrix-v1'
LABELS=('A','B','C')
PAIR_KEYS=('A:B','A:C','B:C')
PAIR_LABELS={
    'A:B':('A','B'),
    'A:C':('A','C'),
    'B:C':('B','C'),
}
ALLOWED_SOURCE_CLASSES=('human','independent-model','same-model','deterministic-proxy')
ALLOWED_CONFIDENCE=('strong','low','defer')


def _png_bytes(im:Image.Image)->bytes:
    b=io.BytesIO(); im.convert('RGB').save(b,format='PNG'); return b.getvalue()


def _sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def _strip(frames:Sequence[Image.Image])->Image.Image:
    out=Image.new('RGB',(THUMB*len(frames),THUMB),(18,18,18))
    for i,im in enumerate(frames):
        out.paste(im.convert('RGB').resize((THUMB,THUMB)),(i*THUMB,0))
    return out


def triad_matrix_id_for_phenotypes(*,brief:str,times:Sequence[float],fingerprints:Sequence[str])->str:
    fps=tuple(fingerprints)
    if len(fps)!=3 or len(set(fps))!=3 or not all(fps):
        raise ValueError('exactly three distinct phenotype fingerprints are required')
    config={
        'promptVersion':PROMPT_VERSION,
        'brief':brief,
        'times':list(times),
        'phenotypes':sorted(fps),
    }
    return _sha(json.dumps(config,sort_keys=True,separators=(',',':')).encode())


def _ordered_items(task_id:str,items):
    """Stable anonymous label order independent of caller candidate order."""
    base=sorted(items,key=lambda item:item[1])
    perms=tuple(itertools.permutations(range(3)))
    idx=int(hashlib.sha256((task_id+':label-order').encode()).hexdigest(),16)%len(perms)
    return [base[i] for i in perms[idx]]


def _empty_pair_verdicts()->dict[str,None]:
    return {key:None for key in PAIR_KEYS}


def _validate_pair_verdicts(value)->dict[str,str]|None:
    """Return normalized complete pair verdicts, None if wholly unresolved.

    Partial completion fails closed. Each verdict is independent, so cyclic
    matrices remain valid evidence.
    """
    if not isinstance(value,Mapping) or set(value)!=set(PAIR_KEYS):
        raise ValueError('pairVerdicts must contain exactly A:B, A:C, and B:C')
    if all(value[key] is None for key in PAIR_KEYS):
        return None
    if any(value[key] is None for key in PAIR_KEYS):
        raise ValueError('triad pair-matrix decisions cannot be partially completed')
    out={}
    for key in PAIR_KEYS:
        verdict=value[key]; left,right=PAIR_LABELS[key]
        if verdict not in {left,right,'tie'}:
            raise ValueError(f'invalid verdict for {key}: {verdict!r}')
        out[key]=str(verdict)
    return out


def create_triad_pair_matrix_bundle(
    out_dir:Path,
    *,
    brief:str,
    times:Sequence[float],
    a_frames:Sequence[Image.Image],
    b_frames:Sequence[Image.Image],
    c_frames:Sequence[Image.Image],
    a_candidate_id:str,
    b_candidate_id:str,
    c_candidate_id:str,
    review_group:str|None=None,
)->str:
    """Create one blinded A/B/C panel whose decision contains three pair verdicts."""
    out_dir=Path(out_dir); (out_dir/'panels').mkdir(parents=True,exist_ok=True)
    frame_sets=(a_frames,b_frames,c_frames)
    if any(len(frames)!=len(times) for frames in frame_sets):
        raise ValueError('frame counts must match temporal horizon')
    candidate_ids=(a_candidate_id,b_candidate_id,c_candidate_id)
    if len(set(candidate_ids))!=3 or not all(candidate_ids):
        raise ValueError('triad candidate ids must be distinct and non-empty')
    fps=tuple(phenotype_fingerprint(frames) for frames in frame_sets)
    task_id=triad_matrix_id_for_phenotypes(brief=brief,times=times,fingerprints=fps)
    raw=[
        (a_candidate_id,fps[0],a_frames),
        (b_candidate_id,fps[1],b_frames),
        (c_candidate_id,fps[2],c_frames),
    ]
    ordered=_ordered_items(task_id,raw)

    label_w,title_h,row_h=54,56,THUMB+2
    panel=Image.new('RGB',(label_w+THUMB*len(times),title_h+3*row_h),(24,24,24))
    d=ImageDraw.Draw(panel)
    d.text((7,8),'Judge all three pairs independently: A/B, A/C, B/C — ties allowed',fill=(245,245,245))
    d.text((7,28),'Use the complete temporal horizon; do not force a total ranking',fill=(210,210,210))
    for row,(label,item) in enumerate(zip(LABELS,ordered)):
        _,_,frames=item; y=title_h+row*row_h
        d.text((18,y+THUMB//2),label,fill=(245,245,245))
        panel.paste(_strip(frames),(label_w,y))
    panel_path=out_dir/'panels'/f'{task_id[:14]}.png'; panel.save(panel_path)

    sealed_path=out_dir/'sealed-mapping.json'; queue_path=out_dir/'queue.json'; decisions_path=out_dir/'decisions.json'
    sealed={'version':VERSION,'reviewType':REVIEW_TYPE,'triads':{},'reviewGroups':{}}
    queue={'version':VERSION,'reviewType':REVIEW_TYPE,'triads':{}}
    decisions={'version':VERSION,'reviewType':REVIEW_TYPE,'decisions':{}}
    for path in (sealed_path,queue_path,decisions_path):
        if not path.exists(): continue
        loaded=json.loads(path.read_text())
        if loaded.get('version')!=VERSION or loaded.get('reviewType')!=REVIEW_TYPE:
            raise ValueError(f'{path.name} has incompatible triad pair-matrix schema')
        if path==sealed_path: sealed=loaded
        elif path==queue_path: queue=loaded
        else: decisions=loaded

    sealed['triads'][task_id]={
        label:{'candidateId':item[0],'phenotypeFingerprint':item[1]}
        for label,item in zip(LABELS,ordered)
    }
    if review_group:
        sealed.setdefault('reviewGroups',{})[task_id]=review_group
    queue['triads'][task_id]={
        'triadId':task_id,
        'panel':str(panel_path),
        'brief':brief,
        'times':list(times),
        'promptVersion':PROMPT_VERSION,
        'instruction':'Judge A:B, A:C, and B:C independently. For each pair choose one endpoint or tie. Cyclic preferences are valid; do not convert them to a total ranking. Record source and confidence.',
        'pairKeys':list(PAIR_KEYS),
        'decisionExample':{'A:B':'A','A:C':'C','B:C':'B'},
    }
    decisions['decisions'].setdefault(task_id,{
        'pairVerdicts':_empty_pair_verdicts(),
        'sourceClass':None,
        'sourceId':None,
        'confidence':None,
        'rationale':'',
        'allowedVerdicts':{
            key:[*PAIR_LABELS[key],'tie'] for key in PAIR_KEYS
        },
        'allowedSourceClasses':list(ALLOWED_SOURCE_CLASSES),
        'allowedConfidence':list(ALLOWED_CONFIDENCE),
    })
    sealed_path.write_text(json.dumps(sealed,indent=2)+'\n')
    queue_path.write_text(json.dumps(queue,indent=2)+'\n')
    decisions_path.write_text(json.dumps(decisions,indent=2)+'\n')
    return task_id


def decode_triad_pair_matrix_evidence(out_dir:Path)->list[PhenotypePreferenceEvidence]:
    """Decode completed explicit pair verdicts into existing v3 pair evidence."""
    out_dir=Path(out_dir)
    sealed=json.loads((out_dir/'sealed-mapping.json').read_text())
    queue=json.loads((out_dir/'queue.json').read_text())
    decisions=json.loads((out_dir/'decisions.json').read_text())
    docs=(sealed,queue,decisions)
    if any(doc.get('version')!=VERSION or doc.get('reviewType')!=REVIEW_TYPE for doc in docs):
        raise ValueError('triad pair-matrix bundle must use the v1 pair-matrix schema')
    out=[]
    for task_id,item in decisions.get('decisions',{}).items():
        verdicts=_validate_pair_verdicts(item.get('pairVerdicts'))
        if verdicts is None:
            continue
        source_class=item.get('sourceClass'); source_id=item.get('sourceId'); confidence=item.get('confidence')
        if source_class not in ALLOWED_SOURCE_CLASSES or not source_id or confidence not in ALLOWED_CONFIDENCE:
            raise ValueError(f'triad pair-matrix decision {task_id} is missing or has invalid provenance/confidence')
        mapping=sealed.get('triads',{}).get(task_id)
        if not mapping or set(mapping)!=set(LABELS):
            raise ValueError(f'triad pair-matrix decision {task_id} has no complete sealed mapping')
        label_fp={label:mapping[label].get('phenotypeFingerprint') for label in LABELS}
        if not all(label_fp.values()) or len(set(label_fp.values()))!=3:
            raise ValueError(f'triad pair-matrix decision {task_id} contains missing or duplicate phenotypes')
        task=queue.get('triads',{}).get(task_id)
        if not task:
            raise ValueError(f'triad pair-matrix decision {task_id} has no queue metadata')
        if task.get('triadId')!=task_id or task.get('promptVersion')!=PROMPT_VERSION:
            raise ValueError(f'triad pair-matrix decision {task_id} has incompatible queue identity metadata')
        if task.get('pairKeys')!=list(PAIR_KEYS) or 'brief' not in task or 'times' not in task:
            raise ValueError(f'triad pair-matrix decision {task_id} has incomplete queue metadata')
        brief=task['brief']; times=task['times']
        expected=triad_matrix_id_for_phenotypes(brief=brief,times=times,fingerprints=tuple(label_fp.values()))
        if expected!=task_id:
            raise ValueError(f'triad pair-matrix decision {task_id} failed replay-integrity verification')

        for key in PAIR_KEYS:
            left,right=PAIR_LABELS[key]; lfp=label_fp[left]; rfp=label_fp[right]
            verdict=verdicts[key]
            winner=None if verdict=='tie' else label_fp[verdict]
            pair_id=pair_id_for_phenotypes(
                brief=brief,times=times,a_fingerprint=lfp,b_fingerprint=rfp,
            )
            out.append(PhenotypePreferenceEvidence(
                pair_id=pair_id,
                phenotype_fingerprints=(lfp,rfp),
                winner_fingerprint=winner,
                source_class=source_class,
                source_id=source_id,
                confidence=confidence,
                rationale=item.get('rationale',''),
            ))
    return out
