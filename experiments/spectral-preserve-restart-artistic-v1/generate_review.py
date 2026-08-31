#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SP_DIR = ROOT / "experiments" / "independent-starts-spectral-preserve-v1"
sys.path.insert(0, str(SP_DIR))

import run_spectral_preserve as sp

core = sp.core
ROUTES = ("recurrence", "orbit", "filament")
REVIEW_SEEDS = (752003, 752021, 752043, 752063)
SMOKE_SEED = 752999
TIMES = (30, 90, 150)
MIN_VALID_GENERATED = 12
BLIND_SALT = "spectral-preserve-restart-artistic-v1-20260831-stage-a"
THUMB = 140
PAPER = (250, 248, 245)
INK = (42, 40, 36)
LINE = (235, 230, 221)


def _display_frame(cand, t: int) -> Image.Image:
    frame = core.render_candidate_frame(cand, t).convert("RGB")
    return frame.resize((THUMB, THUMB))


def _display_hash(cand) -> str:
    h = hashlib.sha256()
    for t in TIMES:
        h.update(_display_frame(cand, t).tobytes())
        h.update(b"\0")
    return h.hexdigest()


def _fingerprint(cands) -> list[dict]:
    return sp._fingerprint(list(cands))


def _run_arms(route: str, seed: int) -> dict:
    # Reuse the exact mechanically-confirmed #113 implementation. Only the
    # master-seed population changes; the search-seed namespace and both arms
    # are otherwise identical to #113.
    search_seed = sp.derived_seed(seed, "independent-starts-spectral-preserve-v1", route)
    baseline = sp.op._run_arm(route, search_seed, "baseline10x10")
    treatment = sp._run_spectral_preserve(route, search_seed)

    baseline_attempts = sp.op._operator_attempts(baseline["state"])
    if len(baseline_attempts) != 20:
        raise AssertionError(f"baseline budget drift route={route} seed={seed}")

    shared_exact = (
        _fingerprint(baseline_attempts[:10])
        == treatment["record"]["sharedPrefixFingerprint"]
    )
    start_exact = (
        baseline["record"]["startPhenotypeHash"]
        == treatment["record"]["startPhenotypeHash"]
    )
    if not shared_exact or not start_exact:
        raise AssertionError(f"shared start/prefix drift route={route} seed={seed}")

    r10_r12_exact = (
        _fingerprint(baseline_attempts[17:20])
        == _fingerprint(treatment["spectralTail"][3:6])
    )
    if not r10_r12_exact:
        raise AssertionError(f"R10-R12 spectral replay drift route={route} seed={seed}")

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
        and tdiag["native"] == 6
        and tdiag["spectral"] == 10
        and tdiag["restart"] == 4
    ):
        raise AssertionError(f"treatment allocation drift: {tdiag}")

    if len(baseline["generatedValid"]) < MIN_VALID_GENERATED:
        raise AssertionError("baseline valid archive below review minimum")
    if len(treatment["generatedValid"]) < MIN_VALID_GENERATED:
        raise AssertionError("treatment valid archive below review minimum")

    baseline_delivery = list(baseline["deliveryCandidates"])
    treatment_delivery = list(treatment["deliveryCandidates"])
    if len(baseline_delivery) != 3 or len(treatment_delivery) != 3:
        raise AssertionError("delivery shortlist size drift")

    # Duplicate visual phenotypes are intentionally admissible artistic
    # evidence. We record them only in the sealed key and never reject/resample.
    baseline_hashes = [_display_hash(c) for c in baseline_delivery]
    treatment_hashes = [_display_hash(c) for c in treatment_delivery]

    # Renderability itself is a hard presentation invariant.
    for cand in baseline_delivery + treatment_delivery:
        for t in TIMES:
            _display_frame(cand, t)

    return {
        "baseline": baseline_delivery,
        "treatment": treatment_delivery,
        "searchSeed": search_seed,
        "sharedStartExact": start_exact,
        "sharedFirst10Exact": shared_exact,
        "r10R12SpectralExact": r10_r12_exact,
        "baselineDiagnostics": {
            "total": bdiag["total"],
            "native": bdiag["native"],
            "spectral": bdiag["spectral"],
            "restart": 0,
            "validGeneratedCount": len(baseline["generatedValid"]),
            "displayPhenotypes": baseline_hashes,
            "withinSideDistinctPhenotypeCount": len(set(baseline_hashes)),
        },
        "treatmentDiagnostics": {
            "total": tdiag["totalGenerated"],
            "native": tdiag["native"],
            "spectral": tdiag["spectral"],
            "restart": tdiag["restart"],
            "validGeneratedCount": len(treatment["generatedValid"]),
            "validRestarts": tdiag["validRestarts"],
            "displayPhenotypes": treatment_hashes,
            "withinSideDistinctPhenotypeCount": len(set(treatment_hashes)),
        },
        "displayIdenticalAcrossSides": baseline_hashes == treatment_hashes,
    }


def _digest(*parts: object) -> bytes:
    text = ":".join(str(p) for p in parts)
    return hashlib.sha256(f"{BLIND_SALT}:{text}".encode()).digest()


def _authoritative_pairs() -> list[tuple[int, str]]:
    pairs = [(seed, route) for seed in REVIEW_SEEDS for route in ROUTES]
    return sorted(pairs, key=lambda x: _digest("block-order", x[0], x[1]))


def _treatment_a_map() -> dict[tuple[int, str], bool]:
    # Balance treatment A/B exactly 2/2 within every route. The choice of which
    # two seeds place treatment on side A is deterministic from the blind salt.
    out = {}
    for route in ROUTES:
        ordered = sorted(
            REVIEW_SEEDS,
            key=lambda seed: _digest("orientation", route, seed),
        )
        treatment_a = set(ordered[:2])
        for seed in REVIEW_SEEDS:
            out[(seed, route)] = seed in treatment_a
    return out


def _smoke_treatment_a(route: str) -> bool:
    return bool(_digest("smoke-orientation", route)[0] & 1)


def _permute_for_display(cands: list, block_id: str, side: str) -> list:
    if len(cands) != 3:
        raise AssertionError("display permutation requires three candidates")
    indices = sorted(range(3), key=lambda i: _digest("display-order", block_id, side, i))
    return [cands[i] for i in indices]


def _candidate_row(cand, index: int) -> Image.Image:
    label_w, footer = 26, 16
    canvas = Image.new("RGB", (label_w + THUMB * len(TIMES), THUMB + footer), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((8, THUMB // 2 - 6), str(index), fill=INK)
    for i, t in enumerate(TIMES):
        x = label_w + i * THUMB
        canvas.paste(_display_frame(cand, t), (x, 0))
        draw.text((x + 4, THUMB + 1), f"t={t}", fill=INK)
    return canvas


def _side_panel(cands: list, label: str) -> Image.Image:
    side_header, gap = 24, 4
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
    pa, pb = _side_panel(a, "A"), _side_panel(b, "B")
    header, gap = 28, 10
    w = max(pa.width, pb.width)
    canvas = Image.new("RGB", (w, header + pa.height + gap + pb.height), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 7), block_id, fill=INK)
    draw.line((0, header - 1, w, header - 1), fill=LINE)
    canvas.paste(pa, (0, header))
    canvas.paste(pb, (0, header + pa.height + gap))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def _contact_sheet(block_paths: list[Path], out: Path) -> None:
    thumbs = []
    for path in block_paths:
        im = Image.open(path).convert("RGB")
        target_w = 480
        thumbs.append(im.resize((target_w, round(im.height * target_w / im.width))))
    cols, pad = 2, 12
    rows = math.ceil(len(thumbs) / cols)
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
    review_dir, key_dir = output_root / "review", output_root / "key"
    review_dir.mkdir(parents=True, exist_ok=True)
    key_dir.mkdir(parents=True, exist_ok=True)

    if smoke:
        pairs = [(SMOKE_SEED, route) for route in ROUTES]
        orientation = {(SMOKE_SEED, route): _smoke_treatment_a(route) for route in ROUTES}
    else:
        pairs = _authoritative_pairs()
        orientation = _treatment_a_map()

    public_blocks, key_blocks, block_paths = [], [], []
    for seq, (seed, route) in enumerate(pairs, start=1):
        block_id = f"S{seq:02d}" if smoke else f"R{seq:02d}"
        arms = _run_arms(route, seed)
        a_is_treatment = orientation[(seed, route)]
        raw_a = arms["treatment"] if a_is_treatment else arms["baseline"]
        raw_b = arms["baseline"] if a_is_treatment else arms["treatment"]
        a = _permute_for_display(raw_a, block_id, "A")
        b = _permute_for_display(raw_b, block_id, "B")

        block_path = review_dir / f"{block_id}.png"
        _block_image(block_id, a, b, block_path)
        block_paths.append(block_path)
        public_blocks.append({"blockId": block_id})

        key_blocks.append({
            "blockId": block_id,
            "route": route,
            "seed": seed,
            "A": "spectralPreserve20" if a_is_treatment else "baseline20",
            "B": "baseline20" if a_is_treatment else "spectralPreserve20",
            "searchSeed": arms["searchSeed"],
            "sharedStartExact": arms["sharedStartExact"],
            "sharedFirst10Exact": arms["sharedFirst10Exact"],
            "r10R12SpectralExact": arms["r10R12SpectralExact"],
            "displayIdenticalAcrossSidesBeforeDisplayPermutation": arms["displayIdenticalAcrossSides"],
            "baseline": arms["baselineDiagnostics"],
            "spectralPreserve": arms["treatmentDiagnostics"],
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
        "duplicatesWithinOrAcrossSidesAreValidEvidence": True,
        "blockCount": len(public_blocks),
        "blocks": public_blocks,
        "identityFieldsExcluded": [
            "route", "seed", "armIdentity", "candidateId", "genome",
            "operatorHistory", "structuralScores", "duplicateDiagnostics", "ABKey"
        ],
        "supportGate": None if smoke else {
            "minimumReviewable": 9,
            "minimumDecisive": 8,
            "treatmentWinsExceedBaselineWins": True,
            "oneSidedExactSignP": "<=0.10",
            "everyRouteNetPreference": ">=0",
            "minimumPositiveRouteNets": 2,
            "everyLeaveOneRouteOutNetPreference": ">0",
            "productionEffect": "stage-A pass authorizes fresh stage-B artistic replication only"
        },
    }
    (review_dir / "review-contract.json").write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n"
    )
    (key_dir / "key.json").write_text(
        json.dumps({
            "version": 1,
            "smoke": smoke,
            "blindSalt": BLIND_SALT,
            "blocks": key_blocks,
        }, indent=2, sort_keys=True) + "\n"
    )

    orientation_balance = defaultdict(lambda: {"treatmentA": 0, "treatmentB": 0})
    for block in key_blocks:
        route = block["route"]
        if block["A"] == "spectralPreserve20":
            orientation_balance[route]["treatmentA"] += 1
        else:
            orientation_balance[route]["treatmentB"] += 1

    all_renderable = all(
        len(block["baseline"]["displayPhenotypes"]) == 3
        and len(block["spectralPreserve"]["displayPhenotypes"]) == 3
        for block in key_blocks
    )

    return {
        "smoke": smoke,
        "blockCount": len(public_blocks),
        "reviewDir": str(review_dir),
        "keyDir": str(key_dir),
        "allBudgetsExact": all(
            b["baseline"]["total"] == 20
            and b["baseline"]["native"] == 10
            and b["baseline"]["spectral"] == 10
            and b["baseline"]["restart"] == 0
            and b["spectralPreserve"]["total"] == 20
            and b["spectralPreserve"]["native"] == 6
            and b["spectralPreserve"]["spectral"] == 10
            and b["spectralPreserve"]["restart"] == 4
            for b in key_blocks
        ),
        "allSharedStartsExact": all(b["sharedStartExact"] for b in key_blocks),
        "allSharedFirst10Exact": all(b["sharedFirst10Exact"] for b in key_blocks),
        "allR10R12SpectralExact": all(b["r10R12SpectralExact"] for b in key_blocks),
        "allMinimumValidGeneratedMet": all(
            b["baseline"]["validGeneratedCount"] >= MIN_VALID_GENERATED
            and b["spectralPreserve"]["validGeneratedCount"] >= MIN_VALID_GENERATED
            for b in key_blocks
        ),
        "allThreeDeliveredCandidatesRenderable": all_renderable,
        "orientationBalanceByRoute": dict(orientation_balance),
        "authoritativeOrientationBalanced2x2PerRoute": (
            True if smoke else all(
                orientation_balance[r] == {"treatmentA": 2, "treatmentB": 2}
                for r in ROUTES
            )
        ),
        "visualDuplicateFilteringApplied": False,
        "displayIdenticalAcrossSidesBlockCount": sum(
            bool(b["displayIdenticalAcrossSidesBeforeDisplayPermutation"])
            for b in key_blocks
        ),
        "withinSideVisualRedundancyObserved": any(
            b["baseline"]["withinSideDistinctPhenotypeCount"] < 3
            or b["spectralPreserve"]["withinSideDistinctPhenotypeCount"] < 3
            for b in key_blocks
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output-root", required=True)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    print(json.dumps(generate(Path(args.output_root), args.smoke), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
