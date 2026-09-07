#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import secrets
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageChops, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RENDER = ROOT / 'experiments' / 'complete-workflow-audit-v2' / 'render_exact_post.mjs'
REVIEW_FRAMES = (1, 50, 100, 150)
DISTANCE_FRAMES = (30, 90, 150)
ALL_FRAMES = tuple(sorted(set(REVIEW_FRAMES + DISTANCE_FRAMES)))
SMOKE_SEED = 771999
MASTER_SEEDS = (
    771003, 771019, 771037, 771053, 771071, 771089,
    771107, 771127, 771149, 771167, 771181, 771199,
)


def fmt(x: float) -> str:
    if abs(x - round(x)) < 1e-12:
        return str(int(round(x)))
    s = f'{x:.1f}'.rstrip('0').rstrip('.')
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return s


def derived_seed(master: int, namespace: str, index: int) -> int:
    h = hashlib.sha256(f'{master}:{namespace}:{index}'.encode()).digest()
    return int.from_bytes(h[:8], 'big')


def base_params(seed: int) -> dict:
    r = random.Random(seed)
    return {
        'sx': r.randint(132, 156),
        'sy': r.randint(58, 82),
        'f1': round(r.uniform(4.5, 7.5), 1),
        'm': round(r.uniform(.35, .95), 1),
        'mf': round(r.uniform(2.0, 4.5), 1),
        'a1': round(r.uniform(.55, .82), 1),
        'a2': round(r.uniform(.10, .24), 1),
        'f2': round(r.uniform(6.0, 10.5), 1),
        't1': r.randint(20, 36),
        't2': r.randint(24, 44),
    }


def material_params(seed: int, mechanism: str) -> dict:
    r = random.Random(seed)
    if mechanism == 'chirp':
        c = round(r.uniform(.6, 1.8), 1)
        if r.randrange(2): c = -c
        return {'c': c}
    if mechanism == 'epicycle':
        return {'r': r.randint(6, 12), 'h': round(r.uniform(1.6, 3.0), 1), 't3': r.randint(40, 70)}
    if mechanism == 'counter':
        return {'e': round(r.uniform(.12, .28), 1), 'd': round(r.uniform(.5, 1.4), 1), 't3': r.randint(38, 70)}
    raise ValueError(mechanism)


def post(base: dict, mechanism: str = 'native', material: dict | None = None) -> str:
    b = base
    prefix = (
        'setup=_=>createCanvas(w=400,w);draw=_=>{background(9);stroke(w);t=frameCount;'
        'for(i=1e3;i--;point(x,y)){u=i/500-1;'
    )
    if mechanism == 'native':
        body = (
            f"x=200+{fmt(b['sx'])}*u;"
            f"y=200+{fmt(b['sy'])}*({fmt(b['a1'])}*sin({fmt(b['f1'])}*u+{fmt(b['m'])}*sin({fmt(b['mf'])}*u)-t/{b['t1']})"
            f"+{fmt(b['a2'])}*sin({fmt(b['f2'])}*u+t/{b['t2']}))"
        )
    elif mechanism == 'chirp':
        assert material is not None
        body = (
            f"x=200+{fmt(b['sx'])}*u;"
            f"y=200+{fmt(b['sy'])}*({fmt(b['a1'])}*sin({fmt(b['f1'])}*u+{fmt(material['c'])}*u*u+{fmt(b['m'])}*sin({fmt(b['mf'])}*u)-t/{b['t1']})"
            f"+{fmt(b['a2'])}*sin({fmt(b['f2'])}*u+t/{b['t2']}))"
        )
    elif mechanism == 'epicycle':
        assert material is not None
        body = (
            f"z={fmt(material['h'])}*u-t/{material['t3']};"
            f"x=200+{fmt(b['sx'])}*u+{fmt(material['r'])}*cos(z);"
            f"y=200+{fmt(b['sy'])}*({fmt(b['a1'])}*sin({fmt(b['f1'])}*u+{fmt(b['m'])}*sin({fmt(b['mf'])}*u)-t/{b['t1']})"
            f"+{fmt(b['a2'])}*sin({fmt(b['f2'])}*u+t/{b['t2']}))+{fmt(material['r'])}*sin(z)"
        )
    elif mechanism == 'counter':
        assert material is not None
        body = (
            f"x=200+{fmt(b['sx'])}*u;"
            f"y=200+{fmt(b['sy'])}*({fmt(b['a1'])}*sin({fmt(b['f1'])}*u+{fmt(b['m'])}*sin({fmt(b['mf'])}*u)-t/{b['t1']})"
            f"+{fmt(material['e'])}*sin(({fmt(b['f1'])}+{fmt(material['d'])})*u+t/{material['t3']})"
            f"+{fmt(b['a2'])}*sin({fmt(b['f2'])}*u+t/{b['t2']}))"
        )
    else:
        raise ValueError(mechanism)
    return prefix + body + '}}//#つぶやきProcessing'


def point(base: dict, mechanism: str, material: dict | None, u: float, t: float) -> tuple[float, float]:
    b = base
    phase = b['f1'] * u + b['m'] * math.sin(b['mf'] * u) - t / b['t1']
    x = 200 + b['sx'] * u
    y = 200 + b['sy'] * (b['a1'] * math.sin(phase) + b['a2'] * math.sin(b['f2'] * u + t / b['t2']))
    if mechanism == 'chirp':
        assert material is not None
        phase = b['f1'] * u + material['c'] * u * u + b['m'] * math.sin(b['mf'] * u) - t / b['t1']
        y = 200 + b['sy'] * (b['a1'] * math.sin(phase) + b['a2'] * math.sin(b['f2'] * u + t / b['t2']))
    elif mechanism == 'epicycle':
        assert material is not None
        z = material['h'] * u - t / material['t3']
        x += material['r'] * math.cos(z)
        y += material['r'] * math.sin(z)
    elif mechanism == 'counter':
        assert material is not None
        y += b['sy'] * material['e'] * math.sin((b['f1'] + material['d']) * u + t / material['t3'])
    elif mechanism != 'native':
        raise ValueError(mechanism)
    return x, y


def geometry_checks(candidate: dict) -> dict:
    b, mechanism, material = candidate['base'], candidate['mechanism'], candidate['material']
    frame_rows = []
    y_series = []
    for t in REVIEW_FRAMES:
        pts = [point(b, mechanism, material, i / 500 - 1, t) for i in range(1000)]
        xs = [x for x, _ in pts]; ys = [y for _, y in pts]
        dxs = [q[0] - p[0] for p, q in zip(pts, pts[1:])]
        frame_rows.append({
            'frame': t,
            'inFrameFraction': sum(0 <= x < 400 and 0 <= y < 400 for x, y in pts) / len(pts),
            'xSpan': max(xs) - min(xs),
            'ySpan': max(ys) - min(ys),
            'strictlyMonotoneX': min(dxs) > 0,
        })
        y_series.append(ys)
    temporal = [sum(abs(a - b) for a, b in zip(y_series[i], y_series[i+1])) / 1000 for i in range(3)]
    hard = {
        'strictlyMonotoneX': all(x['strictlyMonotoneX'] for x in frame_rows),
        'inFrame': all(x['inFrameFraction'] >= .95 for x in frame_rows),
        'axialCoverage': all(x['xSpan'] >= 240 for x in frame_rows),
        'transverseExtent': all(x['ySpan'] >= 35 for x in frame_rows),
        'temporalChange': min(temporal) >= 10,
    }
    if mechanism == 'epicycle':
        hard['analyticMonotoneMargin'] = b['sx'] - material['r'] * material['h'] > 0
    return {'frames': frame_rows, 'meanAbsoluteTemporalChanges': temporal, 'hard': hard}


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nstdout:\n{p.stdout}\nstderr:\n{p.stderr}")
    return p


def verify_and_render(candidate: dict, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    post_path = out / 'post.txt'; post_path.write_text(candidate['post'] + '\n')
    length = json.loads(run(['node', 'scripts/check-length.mjs', str(post_path)]).stdout)
    if not length['pass']:
        raise AssertionError(f"length failure for {candidate['id']}: {length}")
    run(['node', str(RENDER), str(post_path), str(out / 'frames'), *[str(x) for x in ALL_FRAMES]])
    return length


def phenotype(root: Path) -> tuple[list[Image.Image], str]:
    ims = []
    h = hashlib.sha256()
    for t in DISTANCE_FRAMES:
        im = Image.open(root / 'frames' / f'frame-{t:03d}.png').convert('L').resize((100,100), Image.Resampling.NEAREST)
        ims.append(im)
        h.update(im.tobytes())
    return ims, h.hexdigest()


def image_distance(a: list[Image.Image], b: list[Image.Image]) -> float:
    vals = []
    for ia, ib in zip(a, b):
        diff = ImageChops.difference(ia, ib)
        vals.append(ImageStat.Stat(diff).mean[0] / 255.0)
    return sum(vals) / len(vals)


def max_dispersion(candidate_ids: list[str], roots: dict[str, Path]) -> dict:
    features = {}; hashes = {}
    for cid in candidate_ids:
        features[cid], hashes[cid] = phenotype(roots[cid])
    distances = {}
    for i, a in enumerate(candidate_ids):
        for b in candidate_ids[i+1:]:
            distances[(a,b)] = image_distance(features[a], features[b])
    best = None
    for combo in itertools.combinations(candidate_ids, 3):
        ds = []
        for a,b in itertools.combinations(combo,2):
            key = (a,b) if (a,b) in distances else (b,a)
            ds.append(distances[key])
        score = (min(ds), sum(ds)/3)
        if best is None or score > best[0]:
            best = (score, combo, ds)
    assert best is not None
    score, combo, ds = best
    if len({hashes[c] for c in combo}) != 3:
        raise AssertionError('max-dispersion selected duplicate phenotype hashes')
    return {
        'candidateIds': list(combo),
        'minimumPairwiseDistance': score[0],
        'meanPairwiseDistance': score[1],
        'pairwiseDistances': ds,
        'phenotypeHashes': {c: hashes[c] for c in combo},
    }


def candidate(master: int, cid: str, mechanism: str, ordinal: int) -> dict:
    bseed = derived_seed(master, f'{mechanism}-base', ordinal)
    base = base_params(bseed)
    mseed = None if mechanism == 'native' else derived_seed(master, f'{mechanism}-material', ordinal)
    material = None if mseed is None else material_params(mseed, mechanism)
    return {
        'id': cid,
        'mechanism': mechanism,
        'ordinal': ordinal,
        'baseSeed': bseed,
        'materialSeed': mseed,
        'base': base,
        'material': material,
        'post': post(base, mechanism, material),
    }


def build_candidates(master: int) -> tuple[list[dict], list[str], list[str]]:
    native = [candidate(master, f'N{i:02d}', 'native', i) for i in range(12)]
    mechanisms = ('chirp','epicycle','counter','chirp','epicycle','counter')
    material = [candidate(master, f'M{i:02d}', mech, i) for i, mech in enumerate(mechanisms)]
    unique = native + material
    native_ids = [c['id'] for c in native]
    mixed_ids = native_ids[:6] + [c['id'] for c in material]
    return unique, native_ids, mixed_ids


def portfolio_image(pair_id: str, mapping: dict, shortlists: dict, roots: dict[str, Path], out: Path) -> None:
    thumb = 82; label = 26
    side_w = thumb * 4; side_h = label + thumb * 3
    canvas = Image.new('RGB', (side_w * 2, side_h), (18,18,18)); d = ImageDraw.Draw(canvas)
    d.text((5,5), f'{pair_id}  A', fill=(240,240,240)); d.text((side_w+5,5), 'B', fill=(240,240,240))
    for side_index, label_name in enumerate(('A','B')):
        arm = mapping[label_name]
        for row, cid in enumerate(shortlists[arm]['candidateIds']):
            for col, t in enumerate(REVIEW_FRAMES):
                im = Image.open(roots[cid] / 'frames' / f'frame-{t:03d}.png').convert('RGB').resize((thumb,thumb), Image.Resampling.LANCZOS)
                canvas.paste(im, (side_index*side_w + col*thumb, label + row*thumb))
    canvas.save(out)


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--smoke', action='store_true'); args = ap.parse_args()
    seeds = (SMOKE_SEED,) if args.smoke else MASTER_SEEDS
    salt = 'excluded-smoke-fixed-salt' if args.smoke else secrets.token_hex(32)
    root = Path(args.out); reviewer = root/'reviewer'; sealed = root/'sealed-archive'; archive_root = sealed/'rendered'
    pairs_dir = reviewer/'pairs'; pairs_dir.mkdir(parents=True, exist_ok=True); archive_root.mkdir(parents=True, exist_ok=True)
    public_pairs=[]; sealed_pairs=[]; mechanical_pairs=[]; row_paths=[]
    for pi, master in enumerate(seeds,1):
        pair_id=f'R{pi:02d}'
        unique, native_ids, mixed_ids = build_candidates(master)
        by_id={c['id']:c for c in unique}
        roots={}
        lengths={}; geometries={}
        for c in unique:
            geom=geometry_checks(c)
            if not all(geom['hard'].values()):
                raise AssertionError(f"{pair_id}/{c['id']} hard geometry failure: {geom['hard']}")
            croot=archive_root/pair_id/c['id']; roots[c['id']]=croot
            lengths[c['id']]=verify_and_render(c,croot); geometries[c['id']]=geom
        if native_ids[:6] != mixed_ids[:6]: raise AssertionError('common prefix id mismatch')
        if [by_id[x]['post'] for x in native_ids[:6]] != [by_id[x]['post'] for x in mixed_ids[:6]]: raise AssertionError('common prefix post mismatch')
        mechanisms=[by_id[x]['mechanism'] for x in mixed_ids]
        expected={'native':6,'chirp':2,'epicycle':2,'counter':2}
        actual={k:mechanisms.count(k) for k in expected}
        if actual != expected: raise AssertionError(f'mechanism allocation mismatch {actual}')
        shortlists={
            'native12': max_dispersion(native_ids, roots),
            'mixed12': max_dispersion(mixed_ids, roots),
        }
        flip=hashlib.sha256(f'{salt}:{master}'.encode()).digest()[0]&1
        mapping={'A':'mixed12','B':'native12'} if flip else {'A':'native12','B':'mixed12'}
        row=pairs_dir/f'{pair_id}.png'; portfolio_image(pair_id,mapping,shortlists,roots,row); row_paths.append(row)
        public_pairs.append({'pairId':pair_id,'reviewFrames':list(REVIEW_FRAMES),'portfolioSize':3})
        sealed_pairs.append({
            'pairId':pair_id,'masterSeed':master,'mapping':mapping,
            'nativeCandidateIds':native_ids,'mixedCandidateIds':mixed_ids,
            'shortlists':shortlists,'candidates':unique,'lengths':lengths,
        })
        mechanical_pairs.append({
            'pairId':pair_id,'masterSeed':master,'uniqueCandidateCount':len(unique),
            'nativeSlots':len(native_ids),'mixedSlots':len(mixed_ids),'commonNativePrefix':6,
            'mixedMechanismCounts':actual,
            'allLengthsPass':all(x['pass'] for x in lengths.values()),
            'allGeometryHardPass':all(all(g['hard'].values()) for g in geometries.values()),
            'geometry':geometries,
            'nativeDispersion':{k:v for k,v in shortlists['native12'].items() if k!='candidateIds' and k!='phenotypeHashes'},
            'mixedDispersion':{k:v for k,v in shortlists['mixed12'].items() if k!='candidateIds' and k!='phenotypeHashes'},
        })
    ims=[Image.open(p).convert('RGB') for p in row_paths]
    sheet=Image.new('RGB',(ims[0].width,sum(im.height for im in ims)),(18,18,18)); y=0
    for im in ims: sheet.paste(im,(0,y)); y+=im.height
    sheet.save(reviewer/'contact-sheet.png')
    question='Which three-item portfolio would you rather keep as a source of finished compact #つぶやきProcessing filament works, considering the strength of the individual pieces, visual coherence and smoothness through time, and useful range across the three alternatives?'
    (reviewer/'manifest.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','question':question,'pairs':public_pairs},indent=2)+'\n')
    (reviewer/'ratings-template.json').write_text(json.dumps({'version':1,'ratings':{x['pairId']:None for x in public_pairs},'allowed':['A>B','B>A','equivalent','unreviewable']},indent=2)+'\n')
    (sealed/'sealed-key-and-archive.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','salt':salt,'pairs':sealed_pairs},indent=2,sort_keys=True)+'\n')
    (root/'mechanical.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','pairs':mechanical_pairs},indent=2,sort_keys=True)+'\n')
    summary={
        'status':'excluded-smoke' if args.smoke else 'authoritative','pairCount':len(seeds),
        'allHardPreconditions':all(x['uniqueCandidateCount']==18 and x['nativeSlots']==12 and x['mixedSlots']==12 and x['commonNativePrefix']==6 and x['mixedMechanismCounts']=={'native':6,'chirp':2,'epicycle':2,'counter':2} and x['allLengthsPass'] and x['allGeometryHardPass'] for x in mechanical_pairs),
    }
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
