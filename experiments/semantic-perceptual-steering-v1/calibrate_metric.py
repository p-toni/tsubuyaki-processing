#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD_DIR = ROOT / 'experiments' / 'semantic-shape-steering-v1'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(OLD_DIR))

import fresh_targets
import perceptual_metric as pm


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OLD = _load('semantic_shape_v1_for_perceptual_calibration', OLD_DIR / 'semantic_targets.py')
TRANSFORMS = (
    (0.80, -3.0, 5, -4),
    (0.80, 0.0, -5, 4),
    (0.80, 3.0, 4, 5),
    (1.00, -3.0, 0, 0),
    (1.00, 0.0, 0, 0),
    (1.00, 3.0, 0, 0),
)


def transform(image: Image.Image, scale: float, angle: float, dx: int, dy: int) -> Image.Image:
    bg = int(pm.core.BG)
    work = image.convert('L').rotate(angle, resample=Image.Resampling.BILINEAR, expand=False, fillcolor=bg)
    new_w = max(1, int(round(work.width * scale)))
    new_h = max(1, int(round(work.height * scale)))
    resized = work.resize((new_w, new_h), Image.Resampling.BILINEAR)
    canvas = Image.new('L', work.size, bg)
    canvas.paste(resized, ((work.width - new_w) // 2 + dx, (work.height - new_h) // 2 + dy))
    return canvas


def suite_records(targets) -> list[dict]:
    bank = pm.PrototypeBank(targets)
    rows = []
    for target in targets:
        for scale, angle, dx, dy in TRANSFORMS:
            record = bank.image_record(transform(target.image, scale, angle, dx, dy), target.id)
            rows.append({'target': target.id, 'scale': scale, 'angle': angle, 'dx': dx, 'dy': dy, **record})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('metric-calibration.json'))
    args = parser.parse_args()

    old_rows = suite_records(OLD.build_semantic_targets())
    fresh_rows = suite_records(fresh_targets.build_targets())
    all_rows = old_rows + fresh_rows
    finite = all(math.isfinite(float(row[k])) for row in all_rows for k in ('targetDistance','bestOtherDistance','margin'))
    old_top1 = sum(bool(r['top1']) for r in old_rows) / len(old_rows)
    fresh_top1 = sum(bool(r['top1']) for r in fresh_rows) / len(fresh_rows)
    old_min_margin = min(float(r['margin']) for r in old_rows)
    fresh_min_margin = min(float(r['margin']) for r in fresh_rows)
    gates = {
        'oldIdentityTransformsAllTop1': old_top1 == 1.0,
        'freshIdentityTransformsAllTop1': fresh_top1 == 1.0,
        'oldMinimumPrototypeMarginAbovePoint05': old_min_margin > 0.05,
        'freshMinimumPrototypeMarginAbovePoint05': fresh_min_margin > 0.05,
        'allScoresFinite': finite,
    }
    decision = 'PERCEPTUAL_PROTOTYPE_METRIC_CALIBRATED' if all(gates.values()) else 'PERCEPTUAL_PROTOTYPE_METRIC_INVALID'
    result = {
        'decision': decision,
        'gates': gates,
        'oldIdentityTransformTop1Fraction': old_top1,
        'freshIdentityTransformTop1Fraction': fresh_top1,
        'oldMinimumPrototypeMargin': old_min_margin,
        'freshMinimumPrototypeMargin': fresh_min_margin,
        'oldTransformCount': len(old_rows),
        'freshTransformCount': len(fresh_rows),
        'transforms': [list(x) for x in TRANSFORMS],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
