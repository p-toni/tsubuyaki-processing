#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import tempfile
from collections import deque
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
REVIEW_SEEDS = (757003, 757019, 757037, 757053, 757071, 757089, 757107, 757127)
SMOKE_SEED = 757999
TIMES = (30, 90, 150)
QUANTILES = (0.35, 0.75)
MIN_VALID_GENERATED = 12
BLIND_SALT = "morphology-context-judge-prospective-v1-20260901"
THUMB = 180
MORPH_SIZE = 100
MORPH_THRESHOLD = 20
GRID_N = 4
PAPER = (250, 248, 245)
INK = (42, 40, 36)
LINE = (235, 230, 221)
QUESTION = "Which candidate is the stronger mathematical form worth keeping or developing further?"
MODEL_INSTRUCTION = (
    "Judge visible artistic quality. Consider composition/material coherence, structural distinctiveness, "
    "temporal quality, and originality/non-genericness. The morphology card is descriptive evidence, not "
    "a quality score: no metric or direction is automatically preferable. Use it only to make spatial "
    "organization and temporal behavior explicit. Prefer tie whenever the artistic margin is not meaningful. "
    "Do not infer or reward route, search stage, mathematical elegance, code complexity, compression, or hidden metadata."
)


def _brief(route: str) -> dict:
    return {
        "name": "morphology-context-judge-prospective-v1",
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


def _raw_frame(cand, t: int) -> Image.Image:
    return core.render_candidate_frame(cand, t).convert("L")


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


def _mask_frame(im: Image.Image) -> tuple[list[bool], dict]:
    small = im.resize((MORPH_SIZE, MORPH_SIZE), Image.Resampling.BILINEAR)
    px = list(small.getdata())
    mask = [v > MORPH_THRESHOLD for v in px]
    lit = [i for i, on in enumerate(mask) if on]
    if not lit:
        return mask, {
            "occupancy": 0.0,
            "bbox_w": 0.0,
            "bbox_h": 0.0,
            "bbox_fill": 0.0,
            "components": 0,
            "largest_component_share": 0.0,
            "grid_entropy": 0.0,
            "anisotropy": 0.0,
            "edge_fraction": 0.0,
            "mirror_x_iou": 0.0,
            "mirror_y_iou": 0.0,
            "centroid_x": 0.5,
            "centroid_y": 0.5,
        }

    xs = [i % MORPH_SIZE for i in lit]
    ys = [i // MORPH_SIZE for i in lit]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    bbox_pixels = (maxx - minx + 1) * (maxy - miny + 1)
    cx = statistics.fmean(xs)
    cy = statistics.fmean(ys)

    seen = [False] * len(mask)
    component_sizes = []
    neighbors8 = ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1))
    for idx in lit:
        if seen[idx]:
            continue
        q = deque([idx])
        seen[idx] = True
        size = 0
        while q:
            cur = q.popleft()
            size += 1
            x = cur % MORPH_SIZE
            y = cur // MORPH_SIZE
            for dx, dy in neighbors8:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MORPH_SIZE and 0 <= ny < MORPH_SIZE:
                    ni = ny * MORPH_SIZE + nx
                    if mask[ni] and not seen[ni]:
                        seen[ni] = True
                        q.append(ni)
        component_sizes.append(size)

    cell_counts = [0] * (GRID_N * GRID_N)
    for x, y in zip(xs, ys):
        gx = min(GRID_N - 1, x * GRID_N // MORPH_SIZE)
        gy = min(GRID_N - 1, y * GRID_N // MORPH_SIZE)
        cell_counts[gy * GRID_N + gx] += 1
    total = len(lit)
    probs = [c / total for c in cell_counts if c]
    entropy = -sum(p * math.log(p) for p in probs) / math.log(GRID_N * GRID_N) if probs else 0.0

    var_x = statistics.fmean((x - cx) ** 2 for x in xs)
    var_y = statistics.fmean((y - cy) ** 2 for y in ys)
    cov_xy = statistics.fmean((x - cx) * (y - cy) for x, y in zip(xs, ys))
    trace = var_x + var_y
    disc = math.sqrt(max(0.0, (var_x - var_y) ** 2 + 4 * cov_xy * cov_xy))
    major = (trace + disc) / 2
    minor = (trace - disc) / 2
    anisotropy = 1.0 - (minor / major) if major > 1e-12 else 0.0

    edge = 0
    neighbors4 = ((-1,0),(1,0),(0,-1),(0,1))
    for idx in lit:
        x = idx % MORPH_SIZE
        y = idx // MORPH_SIZE
        boundary = False
        for dx, dy in neighbors4:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < MORPH_SIZE and 0 <= ny < MORPH_SIZE):
                boundary = True
                break
            if not mask[ny * MORPH_SIZE + nx]:
                boundary = True
                break
        if boundary:
            edge += 1

    def mirror_iou(axis: str) -> float:
        inter = union = 0
        for y in range(MORPH_SIZE):
            for x in range(MORPH_SIZE):
                a = mask[y * MORPH_SIZE + x]
                mx, my = (MORPH_SIZE - 1 - x, y) if axis == "x" else (x, MORPH_SIZE - 1 - y)
                b = mask[my * MORPH_SIZE + mx]
                inter += int(a and b)
                union += int(a or b)
        return inter / union if union else 0.0

    metrics = {
        "occupancy": total / (MORPH_SIZE * MORPH_SIZE),
        "bbox_w": (maxx - minx + 1) / MORPH_SIZE,
        "bbox_h": (maxy - miny + 1) / MORPH_SIZE,
        "bbox_fill": total / bbox_pixels if bbox_pixels else 0.0,
        "components": len(component_sizes),
        "largest_component_share": max(component_sizes) / total,
        "grid_entropy": entropy,
        "anisotropy": anisotropy,
        "edge_fraction": edge / total,
        "mirror_x_iou": mirror_iou("x"),
        "mirror_y_iou": mirror_iou("y"),
        "centroid_x": cx / (MORPH_SIZE - 1),
        "centroid_y": cy / (MORPH_SIZE - 1),
    }
    return mask, metrics


def _mask_iou(a: list[bool], b: list[bool]) -> float:
    inter = sum(x and y for x, y in zip(a, b))
    union = sum(x or y for x, y in zip(a, b))
    return inter / union if union else 0.0


def _round_metrics(x):
    if isinstance(x, float):
        return round(x, 6)
    if isinstance(x, dict):
        return {k: _round_metrics(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_round_metrics(v) for v in x]
    return x


def _candidate_morphology(cand) -> dict:
    masks = []
    frames = []
    for t in TIMES:
        mask, metrics = _mask_frame(_raw_frame(cand, t))
        masks.append(mask)
        frames.append({"t": t, **metrics})

    ious = []
    occ_changes = []
    centroid_drifts = []
    bbox_area_changes = []
    component_changes = []
    for a_mask, b_mask, a, b in zip(masks, masks[1:], frames, frames[1:]):
        ious.append(_mask_iou(a_mask, b_mask))
        occ_changes.append(abs(a["occupancy"] - b["occupancy"]))
        centroid_drifts.append(math.hypot(a["centroid_x"] - b["centroid_x"], a["centroid_y"] - b["centroid_y"]))
        bbox_area_changes.append(abs(a["bbox_w"] * a["bbox_h"] - b["bbox_w"] * b["bbox_h"]))
        component_changes.append(abs(a["components"] - b["components"]))

    temporal = {
        "mask_iou_mean": statistics.fmean(ious),
        "occupancy_change_mean": statistics.fmean(occ_changes),
        "centroid_drift_mean": statistics.fmean(centroid_drifts),
        "bbox_area_change_mean": statistics.fmean(bbox_area_changes),
        "component_change_mean": statistics.fmean(component_changes),
    }
    return _round_metrics({"frames": frames, "temporal": temporal})


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
    draw.text((8, h - footer + 8), QUESTION, fill=INK)
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
    context_dir = output_root / "model-context"
    key_dir = output_root / "key"
    review_dir.mkdir(parents=True, exist_ok=True)
    context_dir.mkdir(parents=True, exist_ok=True)
    key_dir.mkdir(parents=True, exist_ok=True)
    seeds = (SMOKE_SEED,) if smoke else REVIEW_SEEDS
    key_blocks = []
    public_blocks = []
    context_blocks = []
    block_paths = []
    seq = 0

    with tempfile.TemporaryDirectory(prefix="morphology-context-review-") as td:
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
                context_blocks.append({
                    "blockId": block_id,
                    "A": _candidate_morphology(a),
                    "B": _candidate_morphology(b),
                })
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
        "experiment": "morphology-context-judge-prospective-v1",
        "smoke": smoke,
        "question": QUESTION,
        "allowedHumanJudgments": ["A>B", "B>A", "equivalent", "unreviewable"],
        "allowedModelJudgments": ["A", "B", "tie"],
        "frames": list(TIMES),
        "pairSampling": {"quantiles": list(QUANTILES), "minimumValidGenerated": MIN_VALID_GENERATED, "resampleIdentical": False},
        "blockCount": len(public_blocks),
        "blocks": public_blocks,
        "identityFieldsExcluded": ["route", "seed", "candidateId", "generationIndex", "operator", "genome", "scores", "ABKey"],
        "humanSeesMorphologyContext": False,
        "predictionCanonicalization": "json.dumps(predictions, indent=2, sort_keys=True) + newline",
    }
    (review_dir / "review-contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")

    model_context = {
        "version": 1,
        "experiment": "morphology-context-judge-prospective-v1",
        "smoke": smoke,
        "question": QUESTION,
        "instruction": MODEL_INSTRUCTION,
        "descriptorContract": {
            "resolution": [MORPH_SIZE, MORPH_SIZE],
            "threshold": MORPH_THRESHOLD,
            "grid": [GRID_N, GRID_N],
            "frames": list(TIMES),
            "descriptorsAreScores": False,
        },
        "blocks": context_blocks,
    }
    (context_dir / "model-context.json").write_text(json.dumps(model_context, indent=2, sort_keys=True) + "\n")

    key = {
        "version": 1,
        "experiment": "morphology-context-judge-prospective-v1",
        "smoke": smoke,
        "blindSalt": BLIND_SALT,
        "blocks": key_blocks,
    }
    (key_dir / "key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n")

    return {
        "smoke": smoke,
        "blockCount": len(public_blocks),
        "contextBlockCount": len(context_blocks),
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
