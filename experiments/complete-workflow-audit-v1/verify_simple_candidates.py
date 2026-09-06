#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nstdout:\n{p.stdout}\nstderr:\n{p.stderr}")
    return p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidates', default=str(HERE / 'simple-arm-candidates-v1.json'))
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    data = json.loads(Path(args.candidates).read_text())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    records = []

    for item in data['candidates']:
        bid = item['briefId']
        root = out / bid
        root.mkdir(parents=True, exist_ok=True)
        post_path = root / 'post.txt'
        post_path.write_text(item['post'] + '\n')

        length_run = run(['node', 'scripts/check-length.mjs', str(post_path)])
        length = json.loads(length_run.stdout)
        if not length['pass']:
            raise AssertionError(f'{bid} length failed: {length}')

        frames = [str(int(x)) for x in item['horizonFrames']]
        run([
            'node',
            'experiments/complete-workflow-audit-v1/render_exact_post.mjs',
            str(post_path),
            str(root / 'frames'),
            *frames,
        ])
        records.append({
            'briefId': bid,
            'candidateRender': int(item['candidateRender']),
            'concept': item['concept'],
            'horizonFrames': [int(x) for x in item['horizonFrames']],
            'length': length,
            'runtimePass': True,
        })

    thumb = 150
    label_h = 28
    pair_w = thumb * 4
    cols = 2
    rows = (len(records) + cols - 1) // cols
    sheet = Image.new('RGB', (pair_w * cols, rows * (thumb + label_h)), (18, 18, 18))
    draw = ImageDraw.Draw(sheet)
    for idx, rec in enumerate(records):
        x0 = (idx % cols) * pair_w
        y0 = (idx // cols) * (thumb + label_h)
        draw.text((x0 + 5, y0 + 5), rec['briefId'], fill=(235, 235, 235))
        for j, frame in enumerate(rec['horizonFrames']):
            p = out / rec['briefId'] / 'frames' / f'frame-{frame:03d}.png'
            im = Image.open(p).convert('RGB').resize((thumb, thumb), Image.Resampling.LANCZOS)
            sheet.paste(im, (x0 + j * thumb, y0 + label_h))
    sheet.save(out / 'contact-sheet.png')

    result = {
        'version': 1,
        'arm': 'S',
        'status': 'candidate-render-1-verified',
        'count': len(records),
        'allLengthPass': all(x['length']['pass'] for x in records),
        'allRuntimePass': all(x['runtimePass'] for x in records),
        'records': records,
    }
    (out / 'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
