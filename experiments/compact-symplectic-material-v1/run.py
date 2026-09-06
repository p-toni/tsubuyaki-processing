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
SMOKE_SEED = 769999
MASTER_SEEDS = (
    769003, 769019, 769037, 769053, 769071, 769089,
    769107, 769127, 769149, 769167, 769181, 769199,
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
        'mod': round(r.uniform(.35, .95), 1),
        'mf': round(r.uniform(2.0, 4.5), 1),
        'a1': round(r.uniform(.55, .82), 1),
        'a2': round(r.uniform(.10, .24), 1),
        'f2': round(r.uniform(6.0, 10.5), 1),
        't1': r.randint(20, 36),
        't2': r.randint(24, 44),
    }
    shear = {
        'A': r.randint(7, 14), 'q': r.randint(24, 44),
        'B': r.randint(7, 14), 'r': r.randint(24, 44),
        'C': r.randint(7, 14), 's': r.randint(24, 44),
        'ts': r.randint(38, 64),
    }
    return {'base': base, 'shear': shear}


def post(base: dict, shear: dict | None) -> str:
    b = base
    code = (
        'setup=_=>createCanvas(w=400,w);draw=_=>{background(9);stroke(w);t=frameCount;'
        'for(i=1e3;i--;point(x,y)){u=i/500-1;'
        f"x=200+{fmt(b['sx'])}*u;"
        f"y=200+{fmt(b['sy'])}*({fmt(b['a1'])}*sin({fmt(b['f1'])}*u+{fmt(b['mod'])}*sin({fmt(b['mf'])}*u)-t/{fmt(b['t1'])})"
        f"+{fmt(b['a2'])}*sin({fmt(b['f2'])}*u+t/{fmt(b['t2'])}));"
    )
    if shear is not None:
        s = shear
        code += (
            f"x+={fmt(s['A'])}*sin(y/{fmt(s['q'])}+t/{fmt(s['ts'])});"
            f"y+={fmt(s['B'])}*sin(x/{fmt(s['r'])}-t/{fmt(s['ts'])});"
            f"x+={fmt(s['C'])}*sin(y/{fmt(s['s'])}+t/{fmt(s['ts'])})"
        )
    return code + '}}//#つぶやきProcessing'


def base_point(base: dict, u: float, t: float) -> tuple[float, float]:
    x = 200 + base['sx'] * u
    y = 200 + base['sy'] * (
        base['a1'] * math.sin(base['f1'] * u + base['mod'] * math.sin(base['mf'] * u) - t / base['t1'])
        + base['a2'] * math.sin(base['f2'] * u + t / base['t2'])
    )
    return x, y


def shear_forward(s: dict, x: float, y: float, t: float) -> tuple[float, float]:
    x = x + s['A'] * math.sin(y / s['q'] + t / s['ts'])
    y = y + s['B'] * math.sin(x / s['r'] - t / s['ts'])
    x = x + s['C'] * math.sin(y / s['s'] + t / s['ts'])
    return x, y


def shear_inverse(s: dict, x: float, y: float, t: float) -> tuple[float, float]:
    x = x - s['C'] * math.sin(y / s['s'] + t / s['ts'])
    y = y - s['B'] * math.sin(x / s['r'] - t / s['ts'])
    x = x - s['A'] * math.sin(y / s['q'] + t / s['ts'])
    return x, y


def geometry_checks(p: dict) -> dict:
    base, shear = p['base'], p['shear']
    max_inverse_error = 0.0
    arms = {'native': [], 'shear3': []}
    for t in FRAMES:
        native = []
        treated = []
        for i in range(1000):
            u = i / 500 - 1
            x0, y0 = base_point(base, u, t)
            x1, y1 = shear_forward(shear, x0, y0, t)
            xr, yr = shear_inverse(shear, x1, y1, t)
            max_inverse_error = max(max_inverse_error, abs(xr - x0), abs(yr - y0))
            native.append((x0, y0)); treated.append((x1, y1))
        for name, pts in (('native', native), ('shear3', treated)):
            xs = [x for x, _ in pts]; ys = [y for _, y in pts]
            inframe = sum(0 <= x < 400 and 0 <= y < 400 for x, y in pts) / len(pts)
            endpoint = math.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1])
            arms[name].append({
                'frame': t,
                'inFrameFraction': inframe,
                'xSpan': max(xs) - min(xs),
                'ySpan': max(ys) - min(ys),
                'endpointDistance': endpoint,
            })
    hard = {
        'inverseRoundtrip': max_inverse_error <= 1e-9,
        'nativeInFrame': all(x['inFrameFraction'] >= .98 for x in arms['native']),
        'shear3InFrame': all(x['inFrameFraction'] >= .95 for x in arms['shear3']),
        'nativeAxialCoverage': all(x['xSpan'] >= 220 for x in arms['native']),
        'shear3AxialCoverage': all(x['xSpan'] >= 220 for x in arms['shear3']),
        'nativeEndpointDistinct': all(x['endpointDistance'] >= 150 for x in arms['native']),
        'shear3EndpointDistinct': all(x['endpointDistance'] >= 150 for x in arms['shear3']),
        'nativeTransverseMotion': all(x['ySpan'] >= 35 for x in arms['native']),
        'shear3TransverseMotion': all(x['ySpan'] >= 35 for x in arms['shear3']),
    }
    return {'maxInverseRoundtripError': max_inverse_error, 'frames': arms, 'hard': hard}


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
    key_records = []; public_records = []; mechanical_records = []
    rows = []
    for idx, seed in enumerate(seeds, 1):
        pair_id = f'R{idx:02d}'
        p = params(seed); native = post(p['base'], None); shear3 = post(p['base'], p['shear'])
        geom = geometry_checks(p)
        if not all(geom['hard'].values()):
            raise AssertionError(f'{pair_id} geometry hard invariant failure: {geom["hard"]}')
        arms = {'native': native, 'shear3': shear3}
        flip = hashlib.sha256(f'{salt}:{seed}'.encode()).digest()[0] & 1
        mapping = {'A': 'shear3', 'B': 'native'} if flip else {'A': 'native', 'B': 'shear3'}
        pair_root = root / 'rendered' / pair_id
        rendered = {}; lengths = {}
        for label in ('A', 'B'):
            arm = mapping[label]; arm_root = pair_root / label
            lengths[label] = verify_and_render(arms[arm], arm_root); rendered[label] = arm_root
        if not all(x['pass'] for x in lengths.values()): raise AssertionError(f'{pair_id} exact length failure')
        pair_png = pairs_dir / f'{pair_id}.png'; pair_image(pair_id, rendered['A'], rendered['B'], pair_png); rows.append(pair_png)
        public_records.append({'pairId': pair_id, 'frames': list(FRAMES)})
        key_records.append({'pairId': pair_id, 'masterSeed': seed, 'mapping': mapping, 'base': p['base'], 'shear': p['shear'], 'posts': arms, 'lengthsByLabel': lengths})
        mechanical_records.append({'pairId': pair_id, 'masterSeed': seed, 'baseByteIdenticalAcrossArms': True, 'geometry': geom, 'lengthsByLabel': lengths})
    # stack reviewer rows without exposing identity metadata
    ims = [Image.open(p).convert('RGB') for p in rows]; sheet = Image.new('RGB', (ims[0].width, sum(im.height for im in ims)), (18, 18, 18)); y = 0
    for im in ims: sheet.paste(im, (0, y)); y += im.height
    sheet.save(reviewer / 'contact-sheet.png')
    (reviewer / 'ratings-template.json').write_text(json.dumps({'version':1,'ratings':{r['pairId']:None for r in public_records},'allowed':['A>B','B>A','equivalent','unreviewable']}, indent=2) + '\n')
    (reviewer / 'manifest.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','question':'Which final compact animation would you rather keep as an original #つぶやきProcessing filament, considering material richness, coherence, composition and motion across all four times?','pairs':public_records}, indent=2) + '\n')
    (key_dir / 'sealed-key.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','salt':salt,'records':key_records}, indent=2, sort_keys=True) + '\n')
    (root / 'mechanical.json').write_text(json.dumps({'version':1,'status':'excluded-smoke' if args.smoke else 'authoritative','pairs':mechanical_records}, indent=2, sort_keys=True) + '\n')
    summary = {'status':'excluded-smoke' if args.smoke else 'authoritative','pairCount':len(seeds),'allHardPreconditions':all(all(p['geometry']['hard'].values()) and all(v['pass'] for v in p['lengthsByLabel'].values()) for p in mechanical_records)}
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
