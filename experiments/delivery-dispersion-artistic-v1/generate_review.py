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
SHORTLIST_DIR = ROOT / "experiments" / "delivery-dispersion-shortlist-v1"
sys.path.insert(0, str(SHORTLIST_DIR))

import run_shortlist as shortlist

core = shortlist.core
search_engine = shortlist.search_engine
derived_seed = shortlist.derived_seed

ROUTES = ("recurrence", "orbit", "filament")
REVIEW_SEEDS = (743003, 743021, 743043, 743063)
SMOKE_SEED = 743999
TIMES = (30, 90, 150)
MIN_VALID_GENERATED = 12
BLIND_SALT = "delivery-dispersion-artistic-v1-20260831-fresh"
THUMB = 140
PAPER = (250, 248, 245)
INK = (42, 40, 36)
LINE = (235, 230, 221)


def _brief(route: str) -> dict:
    return {
        "name": "delivery-dispersion-artistic-v1",
        "artistic_intent": "blind human comparison of two target-blind delivery shortlists",
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


def _run_archive(route: str, seed: int, root: Path) -> dict:
    search_seed = derived_seed(seed, "delivery-dispersion-artistic-v1", route)
    state, report = search_engine.run_search(_brief(route), search_seed, root)
    diag = shortlist._operator_diag(state)
    if diag["total"] != 20 or diag["native"] != 10 or diag["spectral"] != 10:
        raise AssertionError(f"mixed budget drift for route={route} seed={seed}: {diag}")

    generated = shortlist._generated_valid(state)
    if len(generated) < MIN_VALID_GENERATED:
        raise AssertionError(
            f"need >={MIN_VALID_GENERATED} hard-valid generated challengers; "
            f"found {len(generated)} for route={route} seed={seed}"
        )
    selected = shortlist._select_shortlists(generated)
    quantile = selected["quantileCandidates"]
    dispersion = selected["dispersionCandidates"]
    qdiag = selected["quantile"]
    ddiag = selected["dispersion"]

    qhash = [_display_hash(c) for c in quantile]
    dhash = [_display_hash(c) for c in dispersion]
    if len(set(qhash)) != 3 or len(set(dhash)) != 3:
        raise AssertionError("display shortlist does not contain three distinct phenotypes")
    if qhash == dhash:
        raise AssertionError(
            f"presentation-integrity failure: quantile and dispersion portfolios are display-identical "
            f"for route={route} seed={seed}"
        )
    lift = float(ddiag["minimumPairwiseDistance"]) - float(qdiag["minimumPairwiseDistance"])
    if lift < -1e-15:
        raise AssertionError(f"dispersion minimum distance below quantile baseline: {lift}")

    return {
        "quantile": quantile,
        "dispersion": dispersion,
        "searchSeed": search_seed,
        "operatorDiagnostics": diag,
        "validGeneratedCount": len(generated),
        "selectionStatus": report["selectionStatus"],
        "provisionalChampion": report["provisionalChampion"],
        "quantileDiagnostics": {
            **qdiag,
            "displayPhenotypes": qhash,
        },
        "dispersionDiagnostics": {
            **ddiag,
            "displayPhenotypes": dhash,
        },
        "minimumPairwiseDistanceLift": lift,
    }


def _a_is_dispersion(block_id: str) -> bool:
    digest = hashlib.sha256(f"{BLIND_SALT}:{block_id}".encode()).digest()
    return bool(digest[0] & 1)


def _candidate_row(cand, index: int) -> Image.Image:
    label_w = 26
    footer = 16
    canvas = Image.new("RGB", (label_w + THUMB * len(TIMES), THUMB + footer), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((8, THUMB // 2 - 6), str(index), fill=INK)
    for i, t in enumerate(TIMES):
        x = label_w + i * THUMB
        canvas.paste(_display_frame(cand, t), (x, 0))
        draw.text((x + 4, THUMB + 1), f"t={t}", fill=INK)
    return canvas


def _side_panel(cands: list, label: str) -> Image.Image:
    side_header = 24
    gap = 4
    rows = [_candidate_row(c, i + 1) for i, c in enumerate(cands)]
    w = max(r.width for r in rows)
    h = side_header + sum(r.height for r in rows) + gap * (len(rows) - 1)
    canvas = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 6), label, fill=INK)
    y = side_header
    for row in rows:
        canvas.paste(row, (0, y))
        y += row.height + gap
    return canvas


def _block_image(block_id: str, a: list, b: list, path: Path) -> None:
    panel_a = _side_panel(a, "A")
    panel_b = _side_panel(b, "B")
    header = 28
    gap = 10
    w = max(panel_a.width, panel_b.width)
    h = header + panel_a.height + gap + panel_b.height
    canvas = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 7), block_id, fill=INK)
    draw.line((0, header - 1, w, header - 1), fill=LINE)
    canvas.paste(panel_a, (0, header))
    canvas.paste(panel_b, (0, header + panel_a.height + gap))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def _contact_sheet(block_paths: list[Path], out: Path) -> None:
    thumbs = []
    for path in block_paths:
        im = Image.open(path).convert("RGB")
        target_w = 480
        target_h = round(im.height * target_w / im.width)
        thumbs.append(im.resize((target_w, target_h)))
    cols = 2
    rows = math.ceil(len(thumbs) / cols)
    pad = 12
    cell_w = max(im.width for im in thumbs)
    cell_h = max(im.height for im in thumbs)
    canvas = Image.new(
        "RGB",
        (cols * cell_w + (cols + 1) * pad, rows * cell_h + (rows + 1) * pad),
        PAPER,
    )
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
    public_blocks = []
    key_blocks = []
    block_paths = []
    seq = 0

    with tempfile.TemporaryDirectory(prefix="delivery-dispersion-artistic-") as td:
        temp = Path(td)
        for seed in seeds:
            for route in ROUTES:
                seq += 1
                block_id = f"S{seq:02d}" if smoke else f"R{seq:02d}"
                archive = _run_archive(route, seed, temp / block_id)
                a_is_dispersion = _a_is_dispersion(block_id)
                a = archive["dispersion"] if a_is_dispersion else archive["quantile"]
                b = archive["quantile"] if a_is_dispersion else archive["dispersion"]
                block_path = review_dir / f"{block_id}.png"
                _block_image(block_id, a, b, block_path)
                block_paths.append(block_path)

                public_blocks.append({"blockId": block_id})
                key_blocks.append({
                    "blockId": block_id,
                    "route": route,
                    "seed": seed,
                    "A": "dispersion" if a_is_dispersion else "quantile",
                    "B": "quantile" if a_is_dispersion else "dispersion",
                    "searchSeed": archive["searchSeed"],
                    "operatorDiagnostics": archive["operatorDiagnostics"],
                    "validGeneratedCount": archive["validGeneratedCount"],
                    "selectionStatus": archive["selectionStatus"],
                    "provisionalChampion": archive["provisionalChampion"],
                    "quantile": archive["quantileDiagnostics"],
                    "dispersion": archive["dispersionDiagnostics"],
                    "minimumPairwiseDistanceLift": archive["minimumPairwiseDistanceLift"],
                })

    _contact_sheet(block_paths, review_dir / "contact-sheet.png")

    contract = {
        "version": 1,
        "smoke": smoke,
        "question": "Which side contains the stronger portfolio of mathematical forms worth keeping or developing further?",
        "allowedJudgments": ["A>B", "B>A", "equivalent", "unreviewable"],
        "frames": list(TIMES),
        "candidatesPerSide": 3,
        "minimumValidGenerated": MIN_VALID_GENERATED,
        "blockCount": len(public_blocks),
        "blocks": public_blocks,
        "supportGate": {
            "minimumReviewable": 9 if not smoke else None,
            "totalDispersionVsQuantileNetPreference": ">0" if not smoke else None,
            "everyLeaveOneRouteOutNetPreference": ">0" if not smoke else None,
        },
        "identityFieldsExcluded": [
            "route", "seed", "deliveryPolicy", "candidateId", "genome",
            "operatorHistory", "structuralScores", "ABKey"
        ],
    }
    (review_dir / "review-contract.json").write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n"
    )

    key = {
        "version": 1,
        "smoke": smoke,
        "blindSalt": BLIND_SALT,
        "blocks": key_blocks,
    }
    (key_dir / "key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n")

    return {
        "smoke": smoke,
        "blockCount": len(public_blocks),
        "reviewDir": str(review_dir),
        "keyDir": str(key_dir),
        "minimumValidGenerated": MIN_VALID_GENERATED,
        "allMixedBudgetsExact": all(
            b["operatorDiagnostics"]["total"] == 20
            and b["operatorDiagnostics"]["native"] == 10
            and b["operatorDiagnostics"]["spectral"] == 10
            for b in key_blocks
        ),
        "allMinimumValidGeneratedMet": all(
            b["validGeneratedCount"] >= MIN_VALID_GENERATED for b in key_blocks
        ),
        "allShortlistsThreeDistinct": all(
            len(set(b["quantile"]["displayPhenotypes"])) == 3
            and len(set(b["dispersion"]["displayPhenotypes"])) == 3
            for b in key_blocks
        ),
        "allPortfoliosNonidentical": all(
            b["quantile"]["displayPhenotypes"] != b["dispersion"]["displayPhenotypes"]
            for b in key_blocks
        ),
        "allDispersionMinimumsAtLeastQuantile": all(
            b["minimumPairwiseDistanceLift"] >= -1e-15 for b in key_blocks
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output-root", required=True)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    result = generate(Path(args.output_root), args.smoke)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
