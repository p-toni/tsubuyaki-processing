#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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
REVIEW_SEEDS = (126007, 126011, 126019, 126031)
SMOKE_SEED = 126999
TIMES = (30, 90, 150)
BLIND_SALT = "spectral-material-control-artistic-v1-frozen-20260831"
THUMB = 220
PAPER = (250, 248, 245)
INK = (42, 40, 36)
LINE = (235, 230, 221)


def _brief(route: str, mode: str) -> dict:
    return {
        "name": "spectral-material-control-artistic-v1",
        "artistic_intent": "blind human review only; same-grammar equal-budget runtime comparison",
        "routes": [route],
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
        if c.stage != "start" and c.checks.get("generationOperator") in {"native", "spectral"}
    ]
    native = [c for c in generated if c.checks.get("generationOperator") == "native"]
    spectral = [c for c in generated if c.checks.get("generationOperator") == "spectral"]
    return {
        "total": len(generated),
        "native": len(native),
        "spectral": len(spectral),
        "nativeValid": sum(bool(c.checks.get("valid", False)) for c in native),
        "spectralValid": sum(bool(c.checks.get("valid", False)) for c in spectral),
    }


def _run_pair(route: str, seed: int, root: Path) -> dict:
    native_state, native_report = search_engine.run_search(
        _brief(route, search_engine.NATIVE_ONLY), seed, root / "native"
    )
    mixed_state, mixed_report = search_engine.run_search(
        _brief(route, search_engine.MIXED_1D_V1), seed, root / "mixed"
    )

    ns = _start(native_state)
    ms = _start(mixed_state)
    if ns.genome != ms.genome or _phenotype_hash(ns) != _phenotype_hash(ms):
        raise AssertionError("native and mixed arms do not share the exact start")

    nd = _operator_diag(native_state)
    md = _operator_diag(mixed_state)
    if nd["total"] != 20 or nd["native"] != 20 or nd["spectral"] != 0:
        raise AssertionError(f"native budget drift: {nd}")
    if md["total"] != 20 or md["native"] != 10 or md["spectral"] != 10:
        raise AssertionError(f"mixed budget drift: {md}")

    nc = _champion(native_state, native_report)
    mc = _champion(mixed_state, mixed_report)
    return {
        "native": nc,
        "mixed": mc,
        "nativeDiag": nd,
        "mixedDiag": md,
        "startIdNative": ns.id,
        "startIdMixed": ms.id,
        "startPhenotype": _phenotype_hash(ns),
        "nativeSelectionStatus": native_report.get("selectionStatus"),
        "mixedSelectionStatus": mixed_report.get("selectionStatus"),
    }


def _a_is_mixed(block_id: str) -> bool:
    digest = hashlib.sha256(f"{BLIND_SALT}:{block_id}".encode()).digest()
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
        target_w = 420
        target_h = round(im.height * target_w / im.width)
        thumbs.append(im.resize((target_w, target_h)))
    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    pad = 12
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
    block_paths: list[Path] = []
    key_blocks = []
    public_blocks = []
    seq = 0

    with tempfile.TemporaryDirectory(prefix="spectral-artistic-review-") as td:
        temp = Path(td)
        for seed in seeds:
            for route in ROUTES:
                seq += 1
                block_id = f"R{seq:02d}" if not smoke else f"S{seq:02d}"
                pair = _run_pair(route, seed, temp / block_id)
                a_is_mixed = _a_is_mixed(block_id)
                a = pair["mixed"] if a_is_mixed else pair["native"]
                b = pair["native"] if a_is_mixed else pair["mixed"]
                block_path = review_dir / f"{block_id}.png"
                _block_image(block_id, a, b, block_path)
                block_paths.append(block_path)

                public_blocks.append({"blockId": block_id})
                key_blocks.append({
                    "blockId": block_id,
                    "route": route,
                    "seed": seed,
                    "A": "mixed" if a_is_mixed else "native",
                    "B": "native" if a_is_mixed else "mixed",
                    "nativeChampionId": pair["native"].id,
                    "mixedChampionId": pair["mixed"].id,
                    "nativeChampionPhenotype": _phenotype_hash(pair["native"]),
                    "mixedChampionPhenotype": _phenotype_hash(pair["mixed"]),
                    "sharedStartPhenotype": pair["startPhenotype"],
                    "nativeDiagnostics": pair["nativeDiag"],
                    "mixedDiagnostics": pair["mixedDiag"],
                    "nativeSelectionStatus": pair["nativeSelectionStatus"],
                    "mixedSelectionStatus": pair["mixedSelectionStatus"],
                })

    _contact_sheet(block_paths, review_dir / "contact-sheet.png")

    contract = {
        "version": 1,
        "smoke": smoke,
        "question": "Which side is the stronger mathematical form worth keeping or developing further?",
        "allowedJudgments": ["A>B", "B>A", "equivalent", "unreviewable"],
        "frames": list(TIMES),
        "blockCount": len(public_blocks),
        "blocks": public_blocks,
        "supportGate": {
            "minimumReviewable": 9 if not smoke else None,
            "totalMixedVsNativeNetPreference": ">0" if not smoke else None,
            "everyLeaveOneRouteOutNetPreference": ">0" if not smoke else None,
        },
        "identityFieldsExcluded": ["route", "seed", "runtimeMode", "candidateId", "genome", "operatorHistory", "ABKey"],
    }
    (review_dir / "review-contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")

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
        "allNativeBudgetsExact": all(b["nativeDiagnostics"] == {"total": 20, "native": 20, "spectral": 0, "nativeValid": b["nativeDiagnostics"]["nativeValid"], "spectralValid": 0} for b in key_blocks),
        "allMixedBudgetsExact": all(b["mixedDiagnostics"]["total"] == 20 and b["mixedDiagnostics"]["native"] == 10 and b["mixedDiagnostics"]["spectral"] == 10 for b in key_blocks),
        "allStartsShared": all(bool(b["sharedStartPhenotype"]) for b in key_blocks),
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
