#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
sys.path.insert(0, str(PROTO))

import core
import material_control
import search_engine

ROUTE = "family"
REVIEW_SEEDS = (
    765003, 765019, 765037, 765053, 765071, 765089,
    765107, 765127, 765149, 765167, 765181, 765199,
    765223, 765239, 765257, 765277, 765293, 765311,
    765331, 765349, 765367, 765383, 765401, 765419,
)
SMOKE_SEED = 765999
TIMES = (30, 90, 150)
THUMB = 220
PAPER = (250, 248, 245)
INK = (42, 40, 36)
LINE = (235, 230, 221)


def _brief(mode: str) -> dict:
    return {
        "name": "family-projected-spectral-artistic-v1",
        "artistic_intent": "blind human review only; same-start equal-budget family runtime comparison",
        "routes": [ROUTE],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": mode,
    }


def _phenotype_hash(cand) -> str:
    h = hashlib.sha256()
    for t in core.TIMES:
        h.update(core.render_candidate_frame(cand, t).tobytes())
        h.update(b"\0")
    return h.hexdigest()


def _start(state):
    starts = [c for c in state.candidates.values() if c.stage == "start" and c.checks.get("valid", False)]
    if len(starts) != 1:
        raise AssertionError(f"expected exactly one hard-valid start; found {len(starts)}")
    return starts[0]


def _champion(state, report):
    cid = report.get("provisionalChampion")
    if not cid or cid not in state.candidates:
        raise AssertionError("runtime report has no resolvable provisional champion")
    cand = state.candidates[cid]
    if not cand.checks.get("valid", False):
        raise AssertionError("provisional champion is not hard-valid")
    return cand


def _operator_diag(state) -> dict:
    generated = [
        c for c in state.candidates.values()
        if c.stage != "start" and c.checks.get("generationOperator") in {"native", "projected-spectral"}
    ]
    native = [c for c in generated if c.checks.get("generationOperator") == "native"]
    projected = [c for c in generated if c.checks.get("generationOperator") == "projected-spectral"]
    for c in projected:
        record = c.genome.get(material_control.CONTROL_KEY)
        if not isinstance(record, dict):
            raise AssertionError("projected-spectral candidate missing serialized material control")
        if record.get("type") != material_control.FAMILY_PROJECTED_CONTROL_TYPE:
            raise AssertionError("family projected material-control type drift")
        if int(record.get("bandwidth", -1)) != 2 or float(record.get("amplitude", -1)) != 16.0:
            raise AssertionError("family projected spectral parameter drift")
    return {
        "total": len(generated),
        "native": len(native),
        "projectedSpectral": len(projected),
        "nativeValid": sum(bool(c.checks.get("valid", False)) for c in native),
        "projectedSpectralValid": sum(bool(c.checks.get("valid", False)) for c in projected),
    }


def _run_pair(seed: int, root: Path) -> dict:
    native_state, native_report = search_engine.run_search(
        _brief(search_engine.NATIVE_ONLY), seed, root / "native"
    )
    projected_state, projected_report = search_engine.run_search(
        _brief(search_engine.FAMILY_PROJECTED_V1), seed, root / "projected"
    )

    ns = _start(native_state)
    ps = _start(projected_state)
    if ns.genome != ps.genome or _phenotype_hash(ns) != _phenotype_hash(ps):
        raise AssertionError("native and projected arms do not share the exact start")

    nd = _operator_diag(native_state)
    pd = _operator_diag(projected_state)
    if nd["total"] != 20 or nd["native"] != 20 or nd["projectedSpectral"] != 0:
        raise AssertionError(f"native budget drift: {nd}")
    if pd["total"] != 20 or pd["native"] != 10 or pd["projectedSpectral"] != 10:
        raise AssertionError(f"projected budget drift: {pd}")

    nc = _champion(native_state, native_report)
    pc = _champion(projected_state, projected_report)
    return {
        "native": nc,
        "projected": pc,
        "nativeDiag": nd,
        "projectedDiag": pd,
        "startPhenotype": _phenotype_hash(ns),
        "nativeSelectionStatus": native_report.get("selectionStatus"),
        "projectedSelectionStatus": projected_report.get("selectionStatus"),
    }


def _a_is_projected(blind_salt: str, block_id: str) -> bool:
    digest = hashlib.sha256(f"{blind_salt}:{block_id}".encode()).digest()
    return bool(digest[0] & 1)


def _raw_frame(cand, t: int) -> Image.Image:
    return core.render_candidate_frame(cand, t).convert("RGB").resize((THUMB, THUMB))


def _row(cand, label: str) -> Image.Image:
    label_w = 38
    footer = 18
    canvas = Image.new("RGB", (label_w + THUMB * len(TIMES), THUMB + footer), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((11, THUMB // 2 - 6), label, fill=INK)
    for i, t in enumerate(TIMES):
        x = label_w + i * THUMB
        canvas.paste(_raw_frame(cand, t), (x, 0))
        draw.text((x + 5, THUMB + 2), f"t={t}", fill=INK)
    return canvas


def _block_image(block_id: str, a, b, path: Path) -> None:
    row_a = _row(a, "A")
    row_b = _row(b, "B")
    header = 30
    gap = 8
    w = max(row_a.width, row_b.width)
    h = header + row_a.height + gap + row_b.height
    canvas = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), block_id, fill=INK)
    draw.line((0, header - 1, w, header - 1), fill=LINE)
    canvas.paste(row_a, (0, header))
    canvas.paste(row_b, (0, header + row_a.height + gap))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def _contact_sheet(block_paths: list[Path], out: Path) -> None:
    thumbs = []
    for p in block_paths:
        im = Image.open(p).convert("RGB")
        target_w = 330
        target_h = round(im.height * target_w / im.width)
        thumbs.append(im.resize((target_w, target_h)))
    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
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
    blind_salt = "excluded-smoke-only" if smoke else secrets.token_hex(32)
    block_paths: list[Path] = []
    key_blocks = []
    public_blocks = []

    with tempfile.TemporaryDirectory(prefix="family-projected-artistic-review-") as td:
        temp = Path(td)
        for seq, seed in enumerate(seeds, 1):
            block_id = f"S{seq:02d}" if smoke else f"R{seq:02d}"
            pair = _run_pair(seed, temp / block_id)
            a_is_projected = _a_is_projected(blind_salt, block_id)
            a = pair["projected"] if a_is_projected else pair["native"]
            b = pair["native"] if a_is_projected else pair["projected"]
            block_path = review_dir / f"{block_id}.png"
            _block_image(block_id, a, b, block_path)
            block_paths.append(block_path)

            public_blocks.append({"blockId": block_id})
            key_blocks.append({
                "blockId": block_id,
                "route": ROUTE,
                "seed": seed,
                "A": "projected" if a_is_projected else "native",
                "B": "native" if a_is_projected else "projected",
                "nativeChampionId": pair["native"].id,
                "projectedChampionId": pair["projected"].id,
                "nativeChampionPhenotype": _phenotype_hash(pair["native"]),
                "projectedChampionPhenotype": _phenotype_hash(pair["projected"]),
                "sharedStartPhenotype": pair["startPhenotype"],
                "nativeDiagnostics": pair["nativeDiag"],
                "projectedDiagnostics": pair["projectedDiag"],
                "nativeSelectionStatus": pair["nativeSelectionStatus"],
                "projectedSelectionStatus": pair["projectedSelectionStatus"],
            })

    _contact_sheet(block_paths, review_dir / "contact-sheet.png")

    contract = {
        "version": 1,
        "smoke": smoke,
        "question": "Which candidate is the stronger mathematical form worth keeping or developing further?",
        "allowedJudgments": ["A>B", "B>A", "equivalent", "unreviewable"],
        "frames": list(TIMES),
        "blockCount": len(public_blocks),
        "blocks": public_blocks,
        "supportGate": {
            "minimumReviewable": 18 if not smoke else None,
            "minimumDecisive": 12 if not smoke else None,
            "projectedDecisiveWinRate": ">0.65" if not smoke else None,
            "oneSidedExactBinomialP": "<=0.10 vs p=0.5" if not smoke else None,
        },
        "identityFieldsExcluded": [
            "route", "seed", "runtimeMode", "candidateId", "genome",
            "operatorHistory", "selectionStatus", "ABKey", "blindSalt",
        ],
    }
    (review_dir / "review-contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")

    key = {
        "version": 1,
        "smoke": smoke,
        "blindSalt": blind_salt,
        "blocks": key_blocks,
    }
    (key_dir / "key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n")

    return {
        "smoke": smoke,
        "blockCount": len(public_blocks),
        "reviewDir": str(review_dir),
        "keyDir": str(key_dir),
        "allNativeBudgetsExact": all(
            b["nativeDiagnostics"]["total"] == 20
            and b["nativeDiagnostics"]["native"] == 20
            and b["nativeDiagnostics"]["projectedSpectral"] == 0
            for b in key_blocks
        ),
        "allProjectedBudgetsExact": all(
            b["projectedDiagnostics"]["total"] == 20
            and b["projectedDiagnostics"]["native"] == 10
            and b["projectedDiagnostics"]["projectedSpectral"] == 10
            for b in key_blocks
        ),
        "allStartsShared": all(bool(b["sharedStartPhenotype"]) for b in key_blocks),
        "allProjectedAttemptsValid": all(
            b["projectedDiagnostics"]["projectedSpectralValid"] == 10 for b in key_blocks
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
