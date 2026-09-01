#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
sys.path.insert(0, str(PROTO))

from orbit_representation import register_orbit
register_orbit()

import core
import search_engine

ROUTES = ("recurrence", "orbit", "filament")
REVIEW_SEEDS = (755003, 755019, 755037, 755053, 755071, 755089, 755107, 755127)
SMOKE_SEED = 755999
TIMES = (30, 90, 150)
QUANTILES = (0.35, 0.75)
MIN_VALID_GENERATED = 12
BLIND_SALT = "semantic-judge-prospective-v1-20260901"
THUMB = 180
PAPER = (250, 248, 245)
INK = (42, 40, 36)
LINE = (235, 230, 221)


def _brief(route: str) -> dict:
    return {
        "name": "semantic-judge-prospective-v1",
        "artistic_intent": "discover a strong compact mathematical form with coherent structure and meaningful temporal development",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": search_engine.MIXED_1D_V1,
    }


def _display_frame(cand, t: int) -> Image.Image:
    return core.render_candidate_frame(cand, t).convert("RGB").resize((THUMB, THUMB))


def _display_hash(cand) -> str:
    h = hashlib.sha256()
    for t in TIMES:
        h.update(_display_frame(cand, t).tobytes())
        h.update(b"\0")
    return h.hexdigest()


def _operator_diag(state) -> dict:
    generated = [
        c for c in state.candidates.values()
        if c.stage != "start" and c.checks.get("generationOperator") in {"native", "spectral"}
    ]
    native = [c for c in generated if c.checks.get("generationOperator") == "native"]
    spectral = [c for c in generated if c.checks.get("generationOperator") == "spectral"]
    return {
        "total": len(generated),
        "native": len(native),
        "spectral": len(spectral),
        "valid": sum(bool(c.checks.get("valid", False)) for c in generated),
        "nativeValid": sum(bool(c.checks.get("valid", False)) for c in native),
        "spectralValid": sum(bool(c.checks.get("valid", False)) for c in spectral),
    }


def _select_pair(state, route: str, seed: int):
    generated = [
        c for c in state.candidates.values()
        if c.stage != "start"
        and c.checks.get("generationOperator") in {"native", "spectral"}
        and c.checks.get("valid", False)
    ]
    if len(generated) < MIN_VALID_GENERATED:
        raise AssertionError(
            f"requires >={MIN_VALID_GENERATED} hard-valid generated candidates; "
            f"found {len(generated)} route={route} seed={seed}"
        )
    indices = [int((len(generated) - 1) * q) for q in QUANTILES]
    if indices[0] == indices[1]:
        raise AssertionError(f"quantile indices collapsed: {indices}")
    selected = [generated[i] for i in indices]
    return selected, {
        "validGeneratedCount": len(generated),
        "quantiles": list(QUANTILES),
        "indices": indices,
        "candidateIds": [c.id for c in selected],
        "generationOperators": [c.checks.get("generationOperator") for c in selected],
        "displayPhenotypes": [_display_hash(c) for c in selected],
    }


def _run_block(route: str, seed: int, out: Path):
    state, _ = search_engine.run_search(_brief(route), seed, out)
    diag = _operator_diag(state)
    if diag["total"] != 20 or diag["native"] != 10 or diag["spectral"] != 10:
        raise AssertionError(f"mixed runtime budget drift: {diag}")
    starts = [c for c in state.candidates.values() if c.stage == "start" and c.checks.get("valid", False)]
    if len(starts) != 1:
        raise AssertionError(f"expected one hard-valid start, got {len(starts)}")
    selected, pair_diag = _select_pair(state, route, seed)
    return selected, {
        "runtime": diag,
        "startPhenotype": _display_hash(starts[0]),
        "pair": pair_diag,
        "displayIdentical": pair_diag["displayPhenotypes"][0] == pair_diag["displayPhenotypes"][1],
    }


def _a_is_first(block_id: str) -> bool:
    digest = hashlib.sha256(f"{BLIND_SALT}:{block_id}".encode()).digest()
    return bool(digest[0] & 1)


def _candidate_panel(cand, label: str) -> Image.Image:
    header = 28
    footer = 18
    w = THUMB * len(TIMES)
    h = header + THUMB + footer
    canvas = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 7), label, fill=INK)
    for i, t in enumerate(TIMES):
        x = i * THUMB
        canvas.paste(_display_frame(cand, t), (x, header))
        draw.text((x + 5, header + THUMB + 2), f"t={t}", fill=INK)
    return canvas


def _block_image(block_id: str, a, b, path: Path) -> None:
    pa = _candidate_panel(a, "A")
    pb = _candidate_panel(b, "B")
    header = 30
    gap = 10
    footer = 40
    w = max(pa.width, pb.width)
    h = header + pa.height + gap + pb.height + footer
    canvas = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), block_id, fill=INK)
    draw.line((0, header - 1, w, header - 1), fill=LINE)
    canvas.paste(pa, (0, header))
    canvas.paste(pb, (0, header + pa.height + gap))
    draw.line((0, h - footer, w, h - footer), fill=LINE)
    draw.text((8, h - footer + 8), "Which candidate is the stronger mathematical form worth keeping or developing further?", fill=INK)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def _contact_sheet(paths: list[Path], out: Path) -> None:
    thumbs = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        target_w = 360
        target_h = round(im.height * target_w / im.width)
        thumbs.append(im.resize((target_w, target_h)))
    cols = 3
    rows = math.ceil(len(thumbs) / cols)
    pad = 10
    cell_w = max(im.width for im in thumbs)
    cell_h = max(im.height for im in thumbs)
    canvas = Image.new("RGB", (cols * cell_w + (cols + 1) * pad, rows * cell_h + (rows + 1) * pad), PAPER)
    for i, im in enumerate(thumbs):
        x = pad + (i % cols) * (cell_w + pad)
        y = pad + (i // cols) * (cell_h + pad)
        canvas.paste(im, (x, y))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def generate(output_root: Path, smoke: bool) -> dict:
    review_dir = output_root / "review"
    key_dir = output_root / "key"
    review_dir.mkdir(parents=True, exist_ok=True)
    key_dir.mkdir(parents=True, exist_ok=True)
    seeds = (SMOKE_SEED,) if smoke else REVIEW_SEEDS
    key_blocks = []
    public_blocks = []
    block_paths = []
    seq = 0

    with tempfile.TemporaryDirectory(prefix="semantic-judge-review-") as td:
        temp = Path(td)
        for seed in seeds:
            for route in ROUTES:
                seq += 1
                block_id = f"S{seq:02d}" if smoke else f"R{seq:02d}"
                pair, diag = _run_block(route, seed, temp / block_id)
                first_is_a = _a_is_first(block_id)
                a = pair[0] if first_is_a else pair[1]
                b = pair[1] if first_is_a else pair[0]
                block_path = review_dir / f"{block_id}.png"
                _block_image(block_id, a, b, block_path)
                block_paths.append(block_path)
                public_blocks.append({"blockId": block_id})
                key_blocks.append({
                    "blockId": block_id,
                    "route": route,
                    "seed": seed,
                    "A": diag["pair"]["candidateIds"][0 if first_is_a else 1],
                    "B": diag["pair"]["candidateIds"][1 if first_is_a else 0],
                    "AQuantile": QUANTILES[0 if first_is_a else 1],
                    "BQuantile": QUANTILES[1 if first_is_a else 0],
                    "AOperator": diag["pair"]["generationOperators"][0 if first_is_a else 1],
                    "BOperator": diag["pair"]["generationOperators"][1 if first_is_a else 0],
                    "displayIdentical": diag["displayIdentical"],
                    "runtime": diag["runtime"],
                    "startPhenotype": diag["startPhenotype"],
                    "pair": diag["pair"],
                })

    _contact_sheet(block_paths, review_dir / "contact-sheet.png")
    contract = {
        "version": 1,
        "smoke": smoke,
        "question": "Which candidate is the stronger mathematical form worth keeping or developing further?",
        "allowedHumanJudgments": ["A>B", "B>A", "equivalent", "unreviewable"],
        "allowedModelJudgments": ["A", "B", "tie"],
        "frames": list(TIMES),
        "pairSampling": {"quantiles": list(QUANTILES), "minimumValidGenerated": MIN_VALID_GENERATED, "resampleIdentical": False},
        "blockCount": len(public_blocks),
        "blocks": public_blocks,
        "identityFieldsExcluded": ["route", "seed", "candidateId", "generationIndex", "operator", "genome", "scores", "ABKey"],
    }
    (review_dir / "review-contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
    key = {"version": 1, "smoke": smoke, "blindSalt": BLIND_SALT, "blocks": key_blocks}
    (key_dir / "key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n")

    return {
        "smoke": smoke,
        "blockCount": len(public_blocks),
        "allBudgetsExact": all(b["runtime"]["total"] == 20 and b["runtime"]["native"] == 10 and b["runtime"]["spectral"] == 10 for b in key_blocks),
        "allPairsTwoCandidates": all(len(b["pair"]["candidateIds"]) == 2 for b in key_blocks),
        "allMinimumValidMet": all(b["pair"]["validGeneratedCount"] >= MIN_VALID_GENERATED for b in key_blocks),
        "identicalDisplayBlocks": sum(bool(b["displayIdentical"]) for b in key_blocks),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(Path(args.output_root), args.smoke), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
