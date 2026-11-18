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

from PIL import Image, ImageChops, ImageDraw, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RENDER = ROOT / 'experiments' / 'complete-workflow-audit-v2' / 'render_exact_post.mjs'
REVIEW_FRAMES = (1, 50, 100, 150)
DISTANCE_FRAMES = (30, 90, 150)
ALL_FRAMES = tuple(sorted(set(REVIEW_FRAMES + DISTANCE_FRAMES)))
SMOKE_SEED = 772999
MASTER_SEEDS = (
    772003, 772019, 772037, 772053, 772071, 772089,
    772107, 772127, 772149, 772167, 772181, 772199,
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


def shared_params(seed: int) -> dict:
    r = random.Random(seed)
    return {
        'sx': r.randint(132, 156),
        'sy': r.randint(56, 70),
        'f': round(r.uniform(4.5, 7.5), 1),
        'm': round(r.uniform(.25, .75), 1),
        'mf': round(r.uniform(2.0, 4.5), 1),
        't1': r.randint(20, 36),
        't2': r.randint(24, 44),
    }


def native_params(seed: int) -> dict:
    r = random.Random(seed)
    return {
        'a1': round(r.uniform(.55, .82), 1),
        'a2': round(r.uniform(.10, .24), 1),
        'f2': round(r.uniform(6.0, 10.5), 1),
    }


def iterative_params(seed: int) -> dict:
    r = random.Random(seed)
    return {
        'b': round(r.uniform(.4, .9), 1),
        'c': round(r.uniform(.4, .9), 1),
        'g': round(r.uniform(2.5, 6.0), 1),
        'd': round(r.uniform(.10, .30), 1),
    }


def native_post(s: dict, p: dict) -> str:
    return (
        'setup=_=>createCanvas(w=400,w);draw=_=>{background(9);stroke(w);t=frameCount;'
        'for(i=1e3;i--;point(x,y)){u=i/500-1;'
        f"x=200+{fmt(s['sx'])}*u;"
        f"y=200+{fmt(s['sy'])}*({fmt(p['a1'])}*sin({fmt(s['f'])}*u+{fmt(s['m'])}*sin({fmt(s['mf'])}*u)-t/{s['t1']})"
        f"+{fmt(p['a2'])}*sin({fmt(p['f2'])}*u+t/{s['t2']}))"
        '}}//#つぶやきProcessing'
    )


def iterative_post(s: dict, p: dict) -> str:
    return (
        'setup=_=>createCanvas(w=400,w);draw=_=>{background(9);stroke(w);t=frameCount;q=r=0;'
        'for(i=1e3;i--;point(x,y)){u=i/500-1;'
        f"x=200+{fmt(s['sx'])}*u;"
        f"q=.9*q+.1*sin({fmt(s['f'])}*u+{fmt(p['b'])}*r+{fmt(s['m'])}*sin({fmt(s['mf'])}*u)-t/{s['t1']});"
        f"r=.9*r+.1*sin({fmt(p['g'])}*u+{fmt(p['c'])}*q+t/{s['t2']});"
        f"y=200+{fmt(s['sy'])}*(q+{fmt(p['d'])}*r)"
        '}}//#つぶやきProcessing'
    )


def native_series(s: dict, p: dict, t: float) -> tuple[list[tuple[float, float]], dict]:
    pts = []
    for i in range(999, -1, -1):
        u = i / 500 - 1
        x = 200 + s['sx'] * u
        phase = s['f'] * u + s['m'] * math.sin(s['mf'] * u) - t / s['t1']
        y = 200 + s['sy'] * (p['a1'] * math.sin(phase) + p['a2'] * math.sin(p['f2'] * u + t / s['t2']))
        pts.append((x, y))
    return pts, {'maxAbsQ': None, 'maxAbsR': None}


def iterative_series(s: dict, p: dict, t: float) -> tuple[list[tuple[float, float]], dict]:
    q = 0.0
    r = 0.0
    max_q = 0.0
    max_r = 0.0
    pts = []
    for i in range(999, -1, -1):
        u = i / 500 - 1
        x = 200 + s['sx'] * u
        q = .9 * q + .1 * math.sin(s['f'] * u + p['b'] * r + s['m'] * math.sin(s['mf'] * u) - t / s['t1'])
        r = .9 * r + .1 * math.sin(p['g'] * u + p['c'] * q + t / s['t2'])
        max_q = max(max_q, abs(q))
        max_r = max(max_r, abs(r))
        y = 200 + s['sy'] * (q + p['d'] * r)
        pts.append((x, y))
    return pts, {'maxAbsQ': max_q, 'maxAbsR': max_r}


def geometry_checks(candidate: dict) -> dict:
    frame_rows = []
    y_series = []
    state_bounds = []
    for t in REVIEW_FRAMES:
        if candidate['representation'] == 'native':
            pts, state = native_series(candidate['shared'], candidate['specific'], t)
        else:
            pts, state = iterative_series(candidate['shared'], candidate['specific'], t)
        xs = [x for x, _ in pts]
        ys = [y for _, y in pts]
        dxs = [b - a for a, b in zip(xs, xs[1:])]
        yjumps = [abs(b - a) for a, b in zip(ys, ys[1:])]
        frame_rows.append({
            'frame': t,
            'inFrameFraction': sum(0 <= x < 400 and 0 <= y < 400 for x, y in pts) / len(pts),
            'xSpan': max(xs) - min(xs),
            'ySpan': max(ys) - min(ys),
            'strictlyMonotoneX': max(dxs) < 0,
            'maxAdjacentYJump': max(yjumps),
            **state,
        })
        y_series.append(ys)
        if state['maxAbsQ'] is not None:
            state_bounds.append(max(state['maxAbsQ'], state['maxAbsR']))
    temporal = [sum(abs(a - b) for a, b in zip(y_series[i], y_series[i + 1])) / len(y_series[i]) for i in range(3)]
    hard = {
        'strictlyMonotoneX': all(x['strictlyMonotoneX'] for x in frame_rows),
        'inFrame': all(x['inFrameFraction'] >= .95 for x in frame_rows),
        'axialCoverage': all(x['xSpan'] >= 240 for x in frame_rows),
        'transverseExtent': all(x['ySpan'] >= 35 for x in frame_rows),
        'temporalChange': min(temporal) >= 10,
        'adjacentSmoothness': all(x['maxAdjacentYJump'] <= 14 for x in frame_rows),
    }
    if candidate['representation'] == 'iterative':
        hard['stateBound'] = max(state_bounds) <= 1 + 1e-12
    return {'frames': frame_rows, 'meanAbsoluteTemporalChanges': temporal, 'hard': hard}


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nstdout:\n{p.stdout}\nstderr:\n{p.stderr}")
    return p


def verify_and_render(candidate: dict, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    post_path = out / 'post.txt'
    post_path.write_text(candidate['post'] + '\n')
    length = json.loads(run(['node', 'scripts/check-length.mjs', str(post_path)]).stdout)
    if not length['pass']:
        raise AssertionError(f"length failure for {candidate['id']}: {length}")
    run(['node', str(RENDER), str(post_path), str(out / 'frames'), *[str(x) for x in ALL_FRAMES]])
    return length


def phenotype(root: Path) -> tuple[list[Image.Image], str]:
    ims = []
    h = hashlib.sha256()
    for t in DISTANCE_FRAMES:
        im = Image.open(root / 'frames' / f'frame-{t:03d}.png').convert('L').resize((100, 100), Image.Resampling.NEAREST)
        ims.append(im)
        h.update(im.tobytes())
    return ims, h.hexdigest()


def image_distance(a: list[Image.Image], b: list[Image.Image]) -> float:
    vals = []
    for ia, ib in zip(a, b):
        vals.append(ImageStat.Stat(ImageChops.difference(ia, ib)).mean[0] / 255.0)
    return sum(vals) / len(vals)


def max_dispersion(candidate_ids: list[str], roots: dict[str, Path]) -> dict:
    features = {}
    hashes = {}
    for cid in candidate_ids:
        features[cid], hashes[cid] = phenotype(roots[cid])
    distances = {}
    for i, a in enumerate(candidate_ids):
        for b in candidate_ids[i + 1:]:
            distances[(a, b)] = image_distance(features[a], features[b])
    best = None
    for combo in itertools.combinations(candidate_ids, 3):
        ds = []
        for a, b in itertools.combinations(combo, 2):
            key = (a, b) if (a, b) in distances else (b, a)
            ds.append(distances[key])
        score = (min(ds), sum(ds) / 3)
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


def build_candidates(master: int) -> tuple[list[dict], list[str], list[str]]:
    out = []
    native_ids = []
    iterative_ids = []
    for i in range(12):
        shared_seed = derived_seed(master, 'compact-iterative-shared', i)
        shared = shared_params(shared_seed)
        nseed = derived_seed(master, 'compact-iterative-native', i)
        iseed = derived_seed(master, 'compact-iterative-state', i)
        n = {
            'id': f'N{i:02d}', 'representation': 'native', 'ordinal': i,
            'sharedSeed': shared_seed, 'specificSeed': nseed,
            'shared': shared, 'specific': native_params(nseed),
        }
        n['post'] = native_post(n['shared'], n['specific'])
        it = {
            'id': f'I{i:02d}', 'representation': 'iterative', 'ordinal': i,
            'sharedSeed': shared_seed, 'specificSeed': iseed,
            'shared': shared, 'specific': iterative_params(iseed),
        }
        it['post'] = iterative_post(it['shared'], it['specific'])
        out.extend((n, it))
        native_ids.append(n['id'])
        iterative_ids.append(it['id'])
    return out, native_ids, iterative_ids


def portfolio_image(pair_id: str, mapping: dict, shortlists: dict, roots: dict[str, Path], out: Path) -> None:
    thumb = 82
    label = 26
    side_w = thumb * 4
    side_h = label + thumb * 3
    canvas = Image.new('RGB', (side_w * 2, side_h), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    d.text((5, 5), f'{pair_id}  A', fill=(240, 240, 240))
    d.text((side_w + 5, 5), 'B', fill=(240, 240, 240))
    for side_index, side in enumerate(('A', 'B')):
        arm = mapping[side]
        for row, cid in enumerate(shortlists[arm]['candidateIds']):
            for col, t in enumerate(REVIEW_FRAMES):
                im = Image.open(roots[cid] / 'frames' / f'frame-{t:03d}.png').convert('RGB').resize((thumb, thumb), Image.Resampling.LANCZOS)
                canvas.paste(im, (side_index * side_w + col * thumb, label + row * thumb))
    canvas.save(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--smoke', action='store_true')
    args = ap.parse_args()

    seeds = (SMOKE_SEED,) if args.smoke else MASTER_SEEDS
    salt = 'excluded-smoke-fixed-salt' if args.smoke else secrets.token_hex(32)
    root = Path(args.out)
    reviewer = root / 'reviewer'
    sealed = root / 'sealed-archive'
    archive_root = sealed / 'rendered'
    pairs_dir = reviewer / 'pairs'
    pairs_dir.mkdir(parents=True, exist_ok=True)
    archive_root.mkdir(parents=True, exist_ok=True)

    public_pairs = []
    sealed_pairs = []
    mechanical_pairs = []
    pair_images = []

    for pi, master in enumerate(seeds, 1):
        pair_id = f'R{pi:02d}'
        candidates, native_ids, iterative_ids = build_candidates(master)
        roots = {}
        lengths = {}
        geometries = {}

        for c in candidates:
            geom = geometry_checks(c)
            if not all(geom['hard'].values()):
                raise AssertionError(f"geometry hard failure {pair_id}/{c['id']}: {geom}")
            croot = archive_root / pair_id / c['id']
            lengths[c['id']] = verify_and_render(c, croot)
            geometries[c['id']] = geom
            roots[c['id']] = croot

        by_id = {c['id']: c for c in candidates}
        for i in range(12):
            n = by_id[f'N{i:02d}']
            it = by_id[f'I{i:02d}']
            if n['sharedSeed'] != it['sharedSeed'] or n['shared'] != it['shared']:
                raise AssertionError('matched outer parameter contract failed')

        shortlists = {
            'native12': max_dispersion(native_ids, roots),
            'iter12': max_dispersion(iterative_ids, roots),
        }

        bit = hashlib.sha256(f'{salt}:{pair_id}'.encode()).digest()[0] & 1
        mapping = {'A': 'native12', 'B': 'iter12'} if bit == 0 else {'A': 'iter12', 'B': 'native12'}
        pair_path = pairs_dir / f'{pair_id}.png'
        portfolio_image(pair_id, mapping, shortlists, roots, pair_path)
        pair_images.append(pair_path)

        all_lengths_pass = all(lengths[c['id']]['pass'] for c in candidates)
        all_geometry_pass = all(all(geometries[c['id']]['hard'].values()) for c in candidates)
        if not all_lengths_pass or not all_geometry_pass:
            raise AssertionError('candidate hard contract failed')

        public_pairs.append({'pairId': pair_id})
        mechanical_pairs.append({
            'pairId': pair_id,
            'masterSeed': master,
            'uniqueCandidateCount': len(candidates),
            'nativeSlots': len(native_ids),
            'iterativeSlots': len(iterative_ids),
            'matchedOuterPairs': 12,
            'allLengthsPass': all_lengths_pass,
            'allGeometryHardPass': all_geometry_pass,
        })
        sealed_pairs.append({
            'pairId': pair_id,
            'masterSeed': master,
            'mapping': mapping,
            'nativeCandidateIds': native_ids,
            'iterativeCandidateIds': iterative_ids,
            'shortlists': shortlists,
            'candidates': candidates,
            'lengths': lengths,
            'geometries': geometries,
        })

    if not args.smoke and [x['masterSeed'] for x in mechanical_pairs] != list(MASTER_SEEDS):
        raise AssertionError('authoritative population mismatch')

    reviewer.mkdir(parents=True, exist_ok=True)
    if pair_images:
        opened = [Image.open(p).convert('RGB') for p in pair_images]
        w = max(im.width for im in opened)
        h = sum(im.height for im in opened)
        sheet = Image.new('RGB', (w, h), (18, 18, 18))
        y = 0
        for im in opened:
            sheet.paste(im, (0, y))
            y += im.height
        sheet.save(reviewer / 'contact-sheet.png')

    ratings = '\n'.join(f'R{i:02d} ' for i in range(1, len(seeds) + 1)) + '\n'
    (reviewer / 'ratings-template.txt').write_text(ratings)
    (reviewer / 'README.txt').write_text(
        'Choose A>B, B>A, equivalent, or unreviewable for each row.\n'
        'Judge the three-item portfolio as a source of finished compact filament works: individual strength, coherence/smoothness through time, and useful range.\n'
    )

    sealed_payload = {
        'version': 'compact-iterative-filament-v1',
        'status': 'excluded-smoke' if args.smoke else 'authoritative',
        'salt': salt,
        'pairs': sealed_pairs,
    }
    (sealed / 'sealed-key-and-archive.json').write_text(json.dumps(sealed_payload, indent=2, sort_keys=True))

    mechanical = {
        'version': 'compact-iterative-filament-v1',
        'status': 'excluded-smoke' if args.smoke else 'authoritative',
        'pairs': mechanical_pairs,
        'reviewerPairs': public_pairs,
        'hardInvariants': {
            'expectedPairCount': len(mechanical_pairs) == (1 if args.smoke else 12),
            'exactCandidateBudgets': all(x['nativeSlots'] == 12 and x['iterativeSlots'] == 12 for x in mechanical_pairs),
            'exactMatchedOuterPairs': all(x['matchedOuterPairs'] == 12 for x in mechanical_pairs),
            'allLengthsPass': all(x['allLengthsPass'] for x in mechanical_pairs),
            'allGeometryHardPass': all(x['allGeometryHardPass'] for x in mechanical_pairs),
        },
    }
    (root / 'mechanical.json').write_text(json.dumps(mechanical, indent=2, sort_keys=True))
    if not all(mechanical['hardInvariants'].values()):
        raise AssertionError(mechanical['hardInvariants'])
    print(json.dumps(mechanical['hardInvariants'], sort_keys=True))


if __name__ == '__main__':
    main()
