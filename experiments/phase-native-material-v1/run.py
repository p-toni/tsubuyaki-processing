#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import secrets
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RENDER = ROOT / 'experiments' / 'complete-workflow-audit-v2' / 'render_exact_post.mjs'
FRAMES = (1, 50, 100, 150)
SMOKE_SEED = 770999
MASTER_SEEDS = (
    770003, 770019, 770037, 770053, 770071, 770089,
    770107, 770127, 770149, 770167, 770181, 770199,
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


def params(seed: int) -> dict:
    r = random.Random(seed)
    base = {
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
    phasepack = {
        'g': round(r.uniform(1.5, 3.5), 1),
        'd': round(r.uniform(.5, 1.2), 1),
        'e': round(r.uniform(.12, .26), 1),
        't3': r.randint(45, 75),
    }
    return {'base': base, 'phasepack': phasepack}


def post(base: dict, phasepack: dict | None) -> str:
    b = base
    code = (
        'setup=_=>createCanvas(w=400,w);draw=_=>{background(9);stroke(w);t=frameCount;'
        'for(i=1e3;i--;point(x,y)){u=i/500-1;'
        f"x=200+{fmt(b['sx'])}*u;"
    )
    if phasepack is None:
        code += (
            f"y=200+{fmt(b['sy'])}*({fmt(b['a1'])}*sin({fmt(b['f1'])}*u+{fmt(b['m'])}*sin({fmt(b['mf'])}*u)-t/{fmt(b['t1'])})"
            f"+{fmt(b['a2'])}*sin({fmt(b['f2'])}*u+t/{fmt(b['t2'])}))"
        )
    else:
        p = phasepack
        code += (
            f"z={fmt(p['g'])}*u-t/{fmt(p['t3'])};"
            f"y=200+{fmt(b['sy'])}*(({fmt(b['a1'])}+{fmt(p['e'])}*cos(z))*sin({fmt(b['f1'])}*u+{fmt(b['m'])}*sin({fmt(b['mf'])}*u+{fmt(p['d'])}*sin(z))-t/{fmt(b['t1'])})"
            f"+{fmt(b['a2'])}*sin({fmt(b['f2'])}*u+t/{fmt(b['t2'])}))"
        )
    return code + '}}//#つぶやきProcessing'


def point(base: dict, phasepack: dict | None, u: float, t: float) -> tuple[float, float, float | None]:
    x = 200 + base['sx'] * u
    if phasepack is None:
        y = 200 + base['sy'] * (
            base['a1'] * math.sin(base['f1'] * u + base['m'] * math.sin(base['mf'] * u) - t / base['t1'])
            + base['a2'] * math.sin(base['f2'] * u + t / base['t2'])
        )
        return x, y, None
    p = phasepack
    z = p['g'] * u - t / p['t3']
    envelope = base['a1'] + p['e'] * math.cos(z)
    y = 200 + base['sy'] * (
        envelope * math.sin(base['f1'] * u + base['m'] * math.sin(base['mf'] * u + p['d'] * math.sin(z)) - t / base['t1'])
        + base['a2'] * math.sin(base['f2'] * u + t / base['t2'])
    )
    return x, y, envelope


def geometry_checks(p: dict) -> dict:
    base, phasepack = p['base'], p['phasepack']
    arms = {'native': [], 'phasepack': []}
    min_envelope = float('inf')
    series = {'native': [], 'phasepack': []}
    for t in FRAMES:
        for name, pp in (('native', None), ('phasepack', phasepack)):
            pts = []
            for i in range(1000):
                u = i / 500 - 1
                x, y, env = point(base, pp, u, t)
                if env is not None:
                    min_envelope = min(min_envelope, env)
                pts.append((x, y))
            xs = [x for x, _ in pts]; ys = [y for _, y in pts]
            dxs = [b[0] - a[0] for a, b in zip(pts, pts[1:])]
            arms[name].append({
                'frame': t,
                'inFrameFraction': sum(0 <= x < 400 and 0 <= y < 400 for x, y in pts) / len(pts),
                'xSpan': max(xs) - min(xs),
                'ySpan': max(ys) - min(ys),
                'strictlyMonotoneX': min(dxs) > 0,
            })
            series[name].append([y for _, y in pts])
    temporal = {}
    for name, frames in series.items():
        changes = [
            sum(abs(a - b) for a, b in zip(frames[i], frames[i + 1])) / len(frames[i])
            for i in range(len(frames) - 1)
        ]
        temporal[name] = changes
    hard = {
        'nativeStrictlyMonotoneX': all(x['strictlyMonotoneX'] for x in arms['native']),
        'phasepackStrictlyMonotoneX': all(x['strictlyMonotoneX'] for x in arms['phasepack']),
        'nativeInFrame': all(x['inFrameFraction'] >= .98 for x in arms['native']),
        'phasepackInFrame': all(x['inFrameFraction'] >= .98 for x in arms['phasepack']),
        'nativeAxialCoverage': all(x['xSpan'] >= 250 for x in arms['native']),
        'phasepackAxialCoverage': all(x['xSpan'] >= 250 for x in arms['phasepack']),
        'nativeTransverseExtent': all(x['ySpan'] >= 40 for x in arms['native']),
        'phasepackTransverseExtent': all(x['ySpan'] >= 40 for x in arms['phasepack']),
        'nativeTemporalChange': min(temporal['native']) >= 15,
        'phasepackTemporalChange': min(temporal['phasepack']) >= 15,
        'phasepackPositiveEnvelope': min_envelope > 0,
    }
    return {'frames': arms, 'meanAbsoluteTemporalChanges': temporal, 'minimumPhasepackEnvelope': min_envelope, 'hard': hard}


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nstdout:\n{p.stdout}\nstderr:\n{p.stderr}")
    return p


def verify_and_render(text: str, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    post_path = out / 'post.txt'; post_path.write_text(text + '\n')
    length = json.loads(run(['node', 'scripts/check-length.mjs', str(post_path)]).stdout)
    if not length['pass']:
        raise AssertionError(f'length failure: {length}')
    run(['node', str(RENDER), str(post_path), str(out / 'frames'), *[str(x) for x in FRAMES]])
    return length


def pair_image(pair_id: str, A_dir: Path, B_dir: Path, out: Path) -> None:
    thumb = 110; label = 26
    canvas = Image.new('RGB', (thumb * 8, thumb + label), (18, 18, 18)); d = ImageDraw.Draw(canvas)
    d.text((5, 5), f'{pair_id}  A', fill=(240, 240, 240)); d.text((thumb * 4 + 5, 5), 'B', fill=(240, 240, 240))
    for side, root in enumerate((A_dir, B_dir)):
        for j, t in enumerate(FRAMES):
            im = Image.open(root / 'frames' / f'frame-{t:03d}.png').convert('RGB').resize((thumb, thumb), Image.Resampling.LANCZOS)
            canvas.paste(im, ((side * 4 + j) * thumb, label))
    canvas.save(out)


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--smoke', action='store_true'); args = ap.parse_args()
    seeds = (SMOKE_SEED,) if args.smoke else MASTER_SEEDS
    salt = 'excluded-smoke-fixed-salt' if args.smoke else secrets.token_hex(32)
    root = Path(args.out); reviewer = root / 'reviewer'; key_dir = root / 'sealed-key'
    pairs_dir = reviewer / 'pairs'; pairs_dir.mkdir(parents=True, exist_ok=True); key_dir.mkdir(parents=True, exist_ok=True)
    key_records = []; public_records = []; mechanical_records = []; rows = []
    for idx, seed in enumerate(seeds, 1):
        pair_id = f'R{idx:02d}'
        p = params(seed); native = post(p['base'], None); phasepack = post(p['base'], p['phasepack'])
        geom = geometry_checks(p)
        if not all(geom['hard'].values()):
            raise AssertionError(f'{pair_id} geometry hard invariant failure: {geom["hard"]}')
        arms = {'native': native, 'phasepack': phasepack}
        flip = hashlib.sha256(f'{salt}:{seed}'.encode()).digest()[0] & 1
        mapping = {'A': 'phasepack', 'B': 'native'} if flip else {'A': 'native', 'B': 'phasepack'}
        pair_root = root / 'rendered' / pair_id; rendered = {}; lengths = {}
        for label in ('A', 'B'):
            arm = mapping[label]; arm_root = pair_root / label
            lengths[label] = verify_and_render(arms[arm], arm_root); rendered[label] = arm_root
        pair_png = pairs_dir / f'{pair_id}.png'; pair_image(pair_id, rendered['A'], rendered['B'], pair_png); rows.append(pair_png)
        public_records.append({'pairId': pair_id, 'frames': list(FRAMES)})
        key_records.append({'pairId': pair_id, 'masterSeed': seed, 'mapping': mapping, 'base': p['base'], 'phasepack': p['phasepack'], 'posts': arms, 'lengthsByLabel': lengths})
        mechanical_records.append({'pairId': pair_id, 'masterSeed': seed, 'baseByteIdenticalAcrossArms': True, 'geometry': geom, 'lengthsByLabel': lengths})
    ims = [Image.open(p).convert('RGB') for p in rows]; sheet = Image.new('RGB', (ims[0].width, sum(im.height for im in ims)), (18, 18, 18)); y = 0
    for im in ims: sheet.paste(im, (0, y)); y += im.height
    sheet.save(reviewer / 'contact-sheet.png')
    question = 'Which final compact animation would you rather keep, prioritizing visual coherence, smoothness, consistency of motion, and material richness across all four times?'
    (reviewer / 'ratings-template.json').write_text(json.dumps({'version':1,'ratings':{r['pairId']:None for r in public_records},'allowed':['A>B','B>A','equivalent','unreviewable']}, indent=2) + '\n')
    (reviewer / 'manifest.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','question':question,'pairs':public_records}, indent=2) + '\n')
    (key_dir / 'sealed-key.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','salt':salt,'records':key_records}, indent=2, sort_keys=True) + '\n')
    (root / 'mechanical.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','pairs':mechanical_records}, indent=2, sort_keys=True) + '\n')
    summary = {'status':'excluded-smoke' if args.smoke else 'authoritative','pairCount':len(seeds),'allHardPreconditions':all(all(p['geometry']['hard'].values()) and all(v['pass'] for v in p['lengthsByLabel'].values()) for p in mechanical_records)}
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
