#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
ROOT = HERE.parents[2]
PROTO = ROOT / 'prototypes' / 'autonomous-discovery'
sys.path.insert(0, str(EXPERIMENT))
sys.path.insert(0, str(PROTO))

from orbit_representation import register_orbit
register_orbit()

import core
import run_block
from rng_streams import derived_seed
from semantic_targets import PROMPTS, resolve_prompt
from steering import target_distance

DISPLAY_SEEDS = {
    'heart': 126001,
    'star': 126011,
    'crescent': 126019,
    'fish': 126031,
    'butterfly': 126037,
    'tree': 126047,
    'letter-a': 126053,
    'flower': 126071,
}
ROUTES = run_block.ROUTES
PACKAGE_STREAM = 'semantic-shape-recognition-v1'
ORDER_SEED = derived_seed(126101, PACKAGE_STREAM, 'anonymous-panel-order')
PANEL_IDS = tuple('ABCDEFGH')


def _fingerprint(image: Image.Image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _operator_contract(report: dict) -> dict:
    counts = report['generationOperatorCounts']
    return {
        'total': int(counts.get('native', 0)) + int(counts.get('spectral', 0)),
        'native': int(counts.get('native', 0)),
        'spectral': int(counts.get('spectral', 0)),
    }


def _generate_one(concept: str, seed: int, work_root: Path):
    target = resolve_prompt(concept)
    champions = []
    route_meta = {}
    for route in ROUTES:
        start, attempts = run_block._valid_start(seed, concept, route)
        state, report, champion = run_block._run_arm(
            seed,
            concept,
            route,
            copy.deepcopy(start),
            target,
            True,
            work_root / concept / route,
        )
        if not champion.checks.get('valid', False):
            raise AssertionError(f'{concept}/{route} final champion invalid')
        contract = _operator_contract(report)
        if contract != {'total': 20, 'native': 10, 'spectral': 10}:
            raise AssertionError(f'{concept}/{route} operator budget drift: {contract}')
        champions.append(champion)
        route_meta[route] = {
            'startAttempts': attempts,
            'championId': champion.id,
            'championTargetDistance': target_distance(champion, target.image),
            'operatorContract': contract,
        }

    winner = min(champions, key=lambda c: target_distance(c, target.image))
    image = core.render_candidate_frame(winner, 90).convert('L')
    if not winner.checks.get('valid', False):
        raise AssertionError(f'{concept} chosen display output invalid')
    return image, {
        'concept': concept,
        'displaySeed': seed,
        'chosenRoute': winner.route,
        'chosenCandidateId': winner.id,
        'chosenTargetDistance': target_distance(winner, target.image),
        'phenotypeFingerprint': _fingerprint(image),
        'routes': route_meta,
    }


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


def generate(output_root: Path) -> dict:
    if tuple(DISPLAY_SEEDS) != PROMPTS:
        raise AssertionError('display concept order must match frozen prompt catalog')
    output_root.mkdir(parents=True, exist_ok=True)
    review_dir = output_root / 'review'
    key_dir = output_root / 'sealed-key'
    work_dir = output_root / 'work'
    review_dir.mkdir(exist_ok=True)
    key_dir.mkdir(exist_ok=True)
    work_dir.mkdir(exist_ok=True)

    generated = {}
    fingerprints = set()
    for concept in PROMPTS:
        image, meta = _generate_one(concept, DISPLAY_SEEDS[concept], work_dir)
        fp = meta['phenotypeFingerprint']
        if fp in fingerprints:
            raise AssertionError('duplicate display phenotype fingerprint')
        fingerprints.add(fp)
        generated[concept] = (image, meta)

    order = list(PROMPTS)
    rng = random.Random(ORDER_SEED)
    rng.shuffle(order)
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
        'labels': list(PROMPTS),
        'targetSilhouettesShown': False,
        'qualityRatingRequested': False,
        'recognitionGateExactMatches': 6,
    }
    (review_dir / 'instructions.json').write_text(json.dumps(instructions, indent=2) + '\n')
    (review_dir / 'README.txt').write_text(
        'Match panels A-H to the following labels, using each exactly once:\n\n'
        + ', '.join(PROMPTS)
        + '\n\nDo not rate artistic quality; only identify the intended shape.\n'
    )

    sealed = {
        'version': 1,
        'orderSeed': ORDER_SEED,
        'recognitionGateExactMatches': 6,
        'panelKey': key,
    }
    (key_dir / 'recognition-key.json').write_text(json.dumps(sealed, indent=2, sort_keys=True) + '\n')
    return {
        'panelCount': len(panels),
        'distinctPhenotypes': len(fingerprints) == len(PROMPTS),
        'reviewFiles': sorted(p.name for p in review_dir.iterdir()),
        'sealedKeyFiles': sorted(p.name for p in key_dir.iterdir()),
        'allDisplayOutputsValid': True,
        'exactBudgetPerConcept': 60,
        'exactNativePerConcept': 30,
        'exactSpectralPerConcept': 30,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    manifest = generate(args.output_root)
    (args.output_root / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
