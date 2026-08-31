from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
LOCAL_DIR = ROOT / 'experiments' / 'semantic-local-dynamics-v1'
for p in (PROTO, LOCAL_DIR, HERE):
    sys.path.insert(0, str(p))

from orbit_representation import register_orbit
register_orbit()

import core
import local_dynamics as ld
import targets

DISPLAY_SEEDS = {
    'star': 735500011,
    'tree': 735500029,
    'fish': 735500041,
    'chair': 735500067,
    'anchor': 735500079,
    'guitar': 735500101,
    'butterfly': 735500113,
    'bicycle': 735500137,
}
ORDER_SEED = 735590001
PANEL_IDS = tuple('ABCDEFGH')


def _fingerprint(image: Image.Image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _sheet(panels: list[tuple[str, Image.Image]], out_path: Path) -> None:
    cell = 430
    image_size = 400
    label_h = 30
    cols = 2
    rows = 4
    canvas = Image.new('RGB', (cols * cell, rows * (image_size + label_h)), (242, 242, 240))
    draw = ImageDraw.Draw(canvas)
    for i, (panel_id, image) in enumerate(panels):
        col = i % cols
        row = i // cols
        x = col * cell + 15
        y = row * (image_size + label_h)
        framed = ImageOps.expand(image.convert('RGB'), border=1, fill=(90, 90, 90))
        canvas.paste(framed, (x, y + label_h))
        draw.text((x + 4, y + 7), f'Panel {panel_id}', fill=(20, 20, 20))
    canvas.save(out_path)


def _load_seed(evidence_dir: Path, seed: int) -> dict:
    matches = list(evidence_dir.rglob(f'semantic-{seed}.json'))
    if len(matches) != 1:
        raise AssertionError(f'expected one evidence file for seed {seed}, got {matches}')
    return json.loads(matches[0].read_text())


def generate(summary_path: Path, evidence_dir: Path, output_root: Path) -> dict:
    summary = json.loads(summary_path.read_text())
    winning_arm = summary.get('winningArmForRecognition')
    output_root.mkdir(parents=True, exist_ok=True)
    if winning_arm != 'memoryHybrid60':
        skipped = {
            'skipped': True,
            'reason': 'replicated memory arm not authorized for recognition',
            'decision': summary.get('decision'),
        }
        (output_root / 'skipped.json').write_text(
            json.dumps(skipped, indent=2, sort_keys=True) + '\n'
        )
        return skipped

    prompts = tuple(targets.PROMPTS)
    if tuple(DISPLAY_SEEDS) != prompts:
        raise AssertionError('display seed concept order drifted')

    review_dir = output_root / 'review'
    key_dir = output_root / 'sealed-key'
    review_dir.mkdir(exist_ok=True)
    key_dir.mkdir(exist_ok=True)

    generated = {}
    fingerprints = set()
    for concept in prompts:
        seed = DISPLAY_SEEDS[concept]
        evidence = _load_seed(evidence_dir, seed)
        arm = evidence['concepts'][concept][winning_arm]
        route = arm['route']
        genome = arm['genome']
        cand = ld.quick_candidate(route, genome, f'replication-recognition-{concept}-{seed}')
        if not cand.checks.get('valid', False):
            raise AssertionError(f'frozen display output invalid for {concept}')
        image = core.render_candidate_frame(cand, 90).convert('L')
        fp = _fingerprint(image)
        if fp in fingerprints:
            raise AssertionError('duplicate frozen recognition phenotype')
        fingerprints.add(fp)
        generated[concept] = (
            image,
            {
                'concept': concept,
                'displaySeed': seed,
                'winningArm': winning_arm,
                'route': route,
                'candidateFingerprint': arm['fingerprint'],
                'phenotypeFingerprint': fp,
            },
        )

    order = list(prompts)
    random.Random(ORDER_SEED).shuffle(order)
    panels = []
    key = {}
    for panel_id, concept in zip(PANEL_IDS, order):
        image, meta = generated[concept]
        image.save(review_dir / f'panel-{panel_id}.png')
        panels.append((panel_id, image))
        key[panel_id] = meta
    _sheet(panels, review_dir / 'recognition-sheet.png')

    instructions = {
        'task': 'Match every anonymous panel A-H to exactly one concept label. Use every label exactly once.',
        'panels': list(PANEL_IDS),
        'labels': list(prompts),
        'targetSilhouettesShown': False,
        'qualityRatingRequested': False,
        'recognitionGateExactMatches': 6,
        'note': 'Record spontaneous recognizability separately before any forced-choice guess.',
    }
    (review_dir / 'instructions.json').write_text(
        json.dumps(instructions, indent=2, sort_keys=True) + '\n'
    )
    (review_dir / 'README.txt').write_text(
        'Match panels A-H to the following labels, using each exactly once:\n\n'
        + ', '.join(prompts)
        + '\n\nDo not rate artistic quality. Identify only the intended shape. '
        'If a panel is not spontaneously recognizable, note that before making any forced-choice guess.\n'
    )

    sealed = {
        'version': 1,
        'orderSeed': ORDER_SEED,
        'winningArm': winning_arm,
        'recognitionGateExactMatches': 6,
        'displaySeeds': DISPLAY_SEEDS,
        'panelKey': key,
    }
    (key_dir / 'recognition-key.json').write_text(
        json.dumps(sealed, indent=2, sort_keys=True) + '\n'
    )
    manifest = {
        'skipped': False,
        'winningArm': winning_arm,
        'panelCount': len(panels),
        'distinctPhenotypes': len(fingerprints) == len(prompts),
        'allDisplayOutputsValid': True,
        'reviewFiles': sorted(p.name for p in review_dir.iterdir()),
        'sealedKeyFiles': sorted(p.name for p in key_dir.iterdir()),
        'displaySeedSelectionFrozenBeforeSemanticOutcome': True,
    }
    (output_root / 'manifest.json').write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + '\n'
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.summary, args.evidence_dir, args.output_root), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
