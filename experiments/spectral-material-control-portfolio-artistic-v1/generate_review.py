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
REVIEW_SEEDS = (127003, 127021, 127043, 127063)
SMOKE_SEED = 127999
TIMES = (30, 90, 150)
QUANTILES = (0.20, 0.50, 0.80)
BLIND_SALT = "spectral-material-control-portfolio-artistic-v1-frozen-20260831"
THUMB = 140
PAPER = (250, 248, 245)
INK = (42, 40, 36)
LINE = (235, 230, 221)


def _brief(route: str, mode: str) -> dict:
    return {
        "name": "spectral-material-control-portfolio-artistic-v1",
        "artistic_intent": "blind human portfolio review; target-blind fixed sampling",
        "routes": [route],
        "bbox_target": [.55, .82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
        "mutation_portfolio": mode,
    }


def _display_frame(cand, t: int) -> Image.Image:
    return core.render_candidate_frame(cand, t).convert("RGB").resize((THUMB, THUMB))


def _display_phenotype_hash(cand) -> str:
    h = hashlib.sha256()
    for t in TIMES:
        h.update(_display_frame(cand, t).tobytes())
        h.update(b"\0")
    return h.hexdigest()


def _start(state):
    starts = [c for c in state.candidates.values() if c.stage == "start" and c.checks.get("valid", False)]
    if len(starts) != 1:
        raise AssertionError(f"expected exactly one hard-valid start; found {len(starts)}")
    return starts[0]


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


def _portfolio(state) -> tuple[list, dict]:
    generated = [
        c for c in state.candidates.values()
        if c.stage != "start"
        and c.checks.get("generationOperator") in {"native", "spectral"}
        and c.checks.get("valid", False)
    ]
    if len(generated) < 15:
        raise AssertionError(f"portfolio requires >=15 hard-valid challengers; found {len(generated)}")
    indices = [int((len(generated) - 1) * q) for q in QUANTILES]
    if len(set(indices)) != len(QUANTILES):
        raise AssertionError(f"portfolio quantile indices collapsed: {indices}")
    selected = [generated[i] for i in indices]
    hashes = [_display_phenotype_hash(c) for c in selected]
    return selected, {
        "validGeneratedCount": len(generated),
        "quantiles": list(QUANTILES),
        "indices": indices,
        "candidateIds": [c.id for c in selected],
        "displayPhenotypes": hashes,
        "uniqueDisplayPhenotypes": len(set(hashes)),
    }


def _run_pair(route: str, seed: int, root: Path) -> dict:
    native_state, _ = search_engine.run_search(
        _brief(route, search_engine.NATIVE_ONLY), seed, root / "native"
    )
    mixed_state, _ = search_engine.run_search(
        _brief(route, search_engine.MIXED_1D_V1), seed, root / "mixed"
    )

    ns = _start(native_state)
    ms = _start(mixed_state)
    start_hash_native = _display_phenotype_hash(ns)
    start_hash_mixed = _display_phenotype_hash(ms)
    if ns.genome != ms.genome or start_hash_native != start_hash_mixed:
        raise AssertionError("native and mixed arms do not share the exact start")

    nd = _operator_diag(native_state)
    md = _operator_diag(mixed_state)
    if nd["total"] != 20 or nd["native"] != 20 or nd["spectral"] != 0:
        raise AssertionError(f"native budget drift: {nd}")
    if md["total"] != 20 or md["native"] != 10 or md["spectral"] != 10:
        raise AssertionError(f"mixed budget drift: {md}")

    native_portfolio, npd = _portfolio(native_state)
    mixed_portfolio, mpd = _portfolio(mixed_state)

    if npd["displayPhenotypes"] == mpd["displayPhenotypes"]:
        raise AssertionError("presentation-integrity failure: native and mixed portfolios are display-identical")

    return {
        "native": native_portfolio,
        "mixed": mixed_portfolio,
        "nativeDiag": nd,
        "mixedDiag": md,
        "nativePortfolio": npd,
        "mixedPortfolio": mpd,
        "sharedStartPhenotype": start_hash_native,
    }


def _a_is_mixed(block_id: str) -> bool:
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
    for r in rows:
        canvas.paste(r, (0, y))
        y += r.height + gap
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
    for p in block_paths:
        im = Image.open(p).convert("RGB")
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
    block_paths: list[Path] = []
    key_blocks = []
    public_blocks = []
    seq = 0

    with tempfile.TemporaryDirectory(prefix="spectral-portfolio-artistic-review-") as td:
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
                    "sharedStartPhenotype": pair["sharedStartPhenotype"],
                    "nativeDiagnostics": pair["nativeDiag"],
                    "mixedDiagnostics": pair["mixedDiag"],
                    "nativePortfolio": pair["nativePortfolio"],
                    "mixedPortfolio": pair["mixedPortfolio"],
                })

    _contact_sheet(block_paths, review_dir / "contact-sheet.png")

    contract = {
        "version": 1,
        "smoke": smoke,
        "question": "Which side contains the stronger portfolio of mathematical forms worth keeping or developing further?",
        "allowedJudgments": ["A>B", "B>A", "equivalent", "unreviewable"],
        "frames": list(TIMES),
        "candidatesPerSide": 3,
        "samplingRule": "hard-valid generated challengers in generation order; floor((n-1)*q), q=0.20/0.50/0.80",
        "blockCount": len(public_blocks),
        "blocks": public_blocks,
        "supportGate": {
            "minimumReviewable": 9 if not smoke else None,
            "totalMixedVsNativeNetPreference": ">0" if not smoke else None,
            "everyLeaveOneRouteOutNetPreference": ">0" if not smoke else None,
        },
        "identityFieldsExcluded": [
            "route", "seed", "runtimeMode", "candidateId", "genome",
            "operatorHistory", "ABKey"
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
        "allNativeBudgetsExact": all(
            b["nativeDiagnostics"]["total"] == 20
            and b["nativeDiagnostics"]["native"] == 20
            and b["nativeDiagnostics"]["spectral"] == 0
            for b in key_blocks
        ),
        "allMixedBudgetsExact": all(
            b["mixedDiagnostics"]["total"] == 20
            and b["mixedDiagnostics"]["native"] == 10
            and b["mixedDiagnostics"]["spectral"] == 10
            for b in key_blocks
        ),
        "allStartsShared": all(bool(b["sharedStartPhenotype"]) for b in key_blocks),
        "allPortfoliosNonidentical": all(
            b["nativePortfolio"]["displayPhenotypes"] != b["mixedPortfolio"]["displayPhenotypes"]
            for b in key_blocks
        ),
        "allPortfoliosThreeCandidates": all(
            len(b["nativePortfolio"]["candidateIds"]) == 3
            and len(b["mixedPortfolio"]["candidateIds"]) == 3
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
