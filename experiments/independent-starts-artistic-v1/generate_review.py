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
SUB_DIR = ROOT / "experiments" / "independent-starts-substitution-v1"
sys.path.insert(0, str(SUB_DIR))

import run_substitution as sub

base = sub.base
core = sub.core

ROUTES = ("recurrence", "orbit", "filament")
REVIEW_SEEDS = (749003, 749021, 749043, 749063)
SMOKE_SEED = 749999
TIMES = (30, 90, 150)
MIN_VALID_GENERATED = 12
BLIND_SALT = "independent-starts-artistic-v1-20260831-fresh-v2"
THUMB = 140
PAPER = (250, 248, 245)
INK = (42, 40, 36)
LINE = (235, 230, 221)


def _display_frame(cand, t: int) -> Image.Image:
    return core.render_candidate_frame(cand, t).convert("RGB").resize((THUMB, THUMB))


def _display_hash(cand) -> str:
    h = hashlib.sha256()
    for t in TIMES:
        h.update(_display_frame(cand, t).tobytes())
        h.update(b"\0")
    return h.hexdigest()


def _run_arms(route: str, seed: int) -> dict:
    search_seed = sub.derived_seed(seed, "independent-starts-substitution-v1", route)
    baseline = sub.op._run_arm(route, search_seed, "baseline10x10")
    treatment = sub._run_restart_tail(route, search_seed)

    baseline_attempts = sub.op._operator_attempts(baseline["state"])
    if len(baseline_attempts) != 20:
        raise AssertionError(f"baseline budget drift route={route} seed={seed}")
    if len(treatment["record"]["sharedPrefixFingerprint"]) != 16:
        raise AssertionError(f"treatment shared prefix drift route={route} seed={seed}")

    prefix_exact = (
        sub._fingerprint(baseline_attempts[:16])
        == treatment["record"]["sharedPrefixFingerprint"]
    )
    start_exact = (
        baseline["record"]["startPhenotypeHash"]
        == treatment["record"]["startPhenotypeHash"]
    )
    if not prefix_exact or not start_exact:
        raise AssertionError(f"shared start/prefix drift route={route} seed={seed}")

    bdiag = baseline["record"]["operatorDiagnostics"]
    tdiag = treatment["record"]
    if not (
        bdiag["total"] == 20
        and bdiag["native"] == 10
        and bdiag["spectral"] == 10
    ):
        raise AssertionError(f"baseline allocation drift: {bdiag}")
    if not (
        tdiag["totalGenerated"] == 20
        and tdiag["native"] == 10
        and tdiag["spectral"] == 6
        and tdiag["restart"] == 4
    ):
        raise AssertionError(f"treatment allocation drift: {tdiag}")

    if len(baseline["generatedValid"]) < MIN_VALID_GENERATED:
        raise AssertionError("baseline valid archive below review minimum")
    if len(treatment["generatedValid"]) < MIN_VALID_GENERATED:
        raise AssertionError("treatment valid archive below review minimum")

    baseline_delivery = baseline["deliveryCandidates"]
    treatment_delivery = treatment["deliveryCandidates"]
    if len(baseline_delivery) != 3 or len(treatment_delivery) != 3:
        raise AssertionError("delivery shortlist size drift")

    baseline_hashes = [_display_hash(c) for c in baseline_delivery]
    treatment_hashes = [_display_hash(c) for c in treatment_delivery]
    if len(set(baseline_hashes)) != 3 or len(set(treatment_hashes)) != 3:
        raise AssertionError("display shortlist does not contain three distinct phenotypes")
    if baseline_hashes == treatment_hashes:
        raise AssertionError(
            f"presentation-integrity failure: portfolios display-identical route={route} seed={seed}"
        )

    return {
        "baseline": baseline_delivery,
        "treatment": treatment_delivery,
        "searchSeed": search_seed,
        "sharedStartExact": start_exact,
        "sharedFirst16Exact": prefix_exact,
        "baselineDiagnostics": {
            "total": bdiag["total"],
            "native": bdiag["native"],
            "spectral": bdiag["spectral"],
            "restart": 0,
            "validGeneratedCount": len(baseline["generatedValid"]),
            "displayPhenotypes": baseline_hashes,
        },
        "treatmentDiagnostics": {
            "total": tdiag["totalGenerated"],
            "native": tdiag["native"],
            "spectral": tdiag["spectral"],
            "restart": tdiag["restart"],
            "validGeneratedCount": len(treatment["generatedValid"]),
            "validRestarts": tdiag["validRestarts"],
            "displayPhenotypes": treatment_hashes,
        },
    }


def _a_is_treatment(block_id: str) -> bool:
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

    with tempfile.TemporaryDirectory(prefix="independent-starts-artistic-") as td:
        _ = Path(td)
        for seed in seeds:
            for route in ROUTES:
                seq += 1
                block_id = f"S{seq:02d}" if smoke else f"R{seq:02d}"
                arms = _run_arms(route, seed)
                a_is_treatment = _a_is_treatment(block_id)
                a = arms["treatment"] if a_is_treatment else arms["baseline"]
                b = arms["baseline"] if a_is_treatment else arms["treatment"]
                block_path = review_dir / f"{block_id}.png"
                _block_image(block_id, a, b, block_path)
                block_paths.append(block_path)

                public_blocks.append({"blockId": block_id})
                key_blocks.append({
                    "blockId": block_id,
                    "route": route,
                    "seed": seed,
                    "A": "restartTail20" if a_is_treatment else "baseline20",
                    "B": "baseline20" if a_is_treatment else "restartTail20",
                    "searchSeed": arms["searchSeed"],
                    "sharedStartExact": arms["sharedStartExact"],
                    "sharedFirst16Exact": arms["sharedFirst16Exact"],
                    "baseline": arms["baselineDiagnostics"],
                    "restartTail": arms["treatmentDiagnostics"],
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
            "totalRestartTailVsBaselineNetPreference": ">0" if not smoke else None,
            "everyLeaveOneRouteOutNetPreference": ">0" if not smoke else None,
        },
        "identityFieldsExcluded": [
            "route", "seed", "armIdentity", "candidateId", "genome",
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
        "allBudgetsExact": all(
            b["baseline"]["total"] == 20
            and b["baseline"]["native"] == 10
            and b["baseline"]["spectral"] == 10
            and b["baseline"]["restart"] == 0
            and b["restartTail"]["total"] == 20
            and b["restartTail"]["native"] == 10
            and b["restartTail"]["spectral"] == 6
            and b["restartTail"]["restart"] == 4
            for b in key_blocks
        ),
        "allSharedStartsExact": all(b["sharedStartExact"] for b in key_blocks),
        "allSharedFirst16Exact": all(b["sharedFirst16Exact"] for b in key_blocks),
        "allMinimumValidGeneratedMet": all(
            b["baseline"]["validGeneratedCount"] >= MIN_VALID_GENERATED
            and b["restartTail"]["validGeneratedCount"] >= MIN_VALID_GENERATED
            for b in key_blocks
        ),
        "allShortlistsThreeDistinct": all(
            len(set(b["baseline"]["displayPhenotypes"])) == 3
            and len(set(b["restartTail"]["displayPhenotypes"])) == 3
            for b in key_blocks
        ),
        "allPortfoliosNonidentical": all(
            b["baseline"]["displayPhenotypes"] != b["restartTail"]["displayPhenotypes"]
            for b in key_blocks
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
