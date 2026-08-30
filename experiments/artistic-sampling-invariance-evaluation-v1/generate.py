#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPACITY_PATH = ROOT / "experiments" / "sampling-invariance-v1" / "capacity.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


capacity = _load("artistic_sampling_invariance_capacity", CAPACITY_PATH)

STREAM = "artistic-sampling-invariance-evaluation-v1"
REVIEW_SEEDS = (98009, 98011, 98017, 98041)
SMOKE_SEED = 9001
INCUMBENT_ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
SPECTRAL_ROUTE = "bandlimited-k2"
EXEMPLARS_PER_SIDE = 6
CANONICAL_TIME = 90.0
NEUTRAL_ALPHA = 48
MAX_ATTEMPTS = 256

BLOCKS = {
    "R01": (98009, "sheet"),
    "R02": (98011, "filament"),
    "R03": (98041, "sheet"),
    "R04": (98041, "family"),
    "R05": (98011, "sheet"),
    "R06": (98011, "family"),
    "R07": (98041, "filament"),
    "R08": (98009, "family"),
    "R09": (98009, "recurrence"),
    "R10": (98017, "family"),
    "R11": (98009, "filament"),
    "R12": (98017, "orbit"),
    "R13": (98017, "recurrence"),
    "R14": (98017, "filament"),
    "R15": (98041, "orbit"),
    "R16": (98009, "orbit"),
    "R17": (98041, "recurrence"),
    "R18": (98017, "sheet"),
    "R19": (98011, "recurrence"),
    "R20": (98011, "orbit"),
}
SMOKE_BLOCKS = {
    "S01": (SMOKE_SEED, "recurrence"),
    "S02": (SMOKE_SEED, "orbit"),
    "S03": (SMOKE_SEED, "family"),
    "S04": (SMOKE_SEED, "sheet"),
    "S05": (SMOKE_SEED, "filament"),
}
ALL_BLOCKS = {**BLOCKS, **SMOKE_BLOCKS}


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _hash_u64(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big", signed=False)


def _fingerprint(image: Image.Image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _candidate_side(label: str, seed: int, incumbent_route: str) -> str:
    bit = hashlib.sha256(f"{STREAM}|{label}|{seed}|{incumbent_route}|side".encode()).digest()[0] & 1
    return "A" if bit else "B"


def _permutation(label: str, side: str) -> list[int]:
    values = list(range(EXEMPLARS_PER_SIDE))
    values.sort(key=lambda index: _hash_u64(STREAM, label, side, index, "order"))
    return values


def _generate_incumbent(route: str, seed: int, label: str):
    brief = capacity._route_brief(route)
    version = capacity.ROUTES[route].get("version", "1")
    rng_stream = f"{STREAM}|{label}|native-prior"
    rng = capacity.representation_rng(seed, route, version, rng_stream)
    prefix = capacity.ROUTES[route].get("prefix", route[0].upper())
    accepted = []
    attempts = 0
    while len(accepted) < EXEMPLARS_PER_SIDE and attempts < MAX_ATTEMPTS:
        attempts += 1
        candidate = capacity.Candidate(
            f"{prefix}{attempts}",
            route,
            f"{prefix}{attempts}",
            capacity.ROUTES[route]["seed"](rng),
            None,
            "artistic-sampling-invariance-review",
        )
        capacity.evaluate_candidate(candidate, brief)
        if not candidate.checks.get("valid", False):
            continue
        accepted.append(candidate)
    if len(accepted) != EXEMPLARS_PER_SIDE:
        raise RuntimeError(f"{label}/{route}: only {len(accepted)}/{EXEMPLARS_PER_SIDE} valid incumbents in {attempts} attempts")
    return accepted, attempts, rng_stream


def _generate_spectral(seed: int, label: str, incumbent_route: str, rasterizer):
    rng_seed = _hash_u64(STREAM, label, seed, incumbent_route, SPECTRAL_ROUTE, "coefficient-prior")
    rng = np.random.default_rng(rng_seed)
    accepted: list[tuple[np.ndarray, Image.Image]] = []
    attempts = 0
    while len(accepted) < EXEMPLARS_PER_SIDE and attempts < MAX_ATTEMPTS:
        attempts += 1
        coefficients = capacity._draw_field_coefficients(rng)
        binary = rasterizer.image(coefficients)
        valid, _geometry = capacity._field_valid(binary)
        if not valid:
            continue
        accepted.append((coefficients.copy(), binary))
    if len(accepted) != EXEMPLARS_PER_SIDE:
        raise RuntimeError(f"{label}/{SPECTRAL_ROUTE}: only {len(accepted)}/{EXEMPLARS_PER_SIDE} valid fields in {attempts} attempts")
    return accepted, attempts, rng_seed


def _neutral_incumbent(candidate) -> Image.Image:
    points = capacity.ROUTES[candidate.route]["render"](candidate.genome, CANONICAL_TIME)
    return capacity.draw_points(points, NEUTRAL_ALPHA).convert("RGB")


def _neutral_spectral(binary: Image.Image) -> Image.Image:
    array = np.asarray(binary, dtype=np.uint8)
    ys, xs = np.nonzero(array > 20)
    points = [(float(x), float(y)) for y, x in zip(ys, xs)]
    return capacity.draw_points(points, NEUTRAL_ALPHA).convert("RGB")


def _render_portfolios(incumbent_candidates, spectral_candidates):
    incumbent = [_neutral_incumbent(candidate) for candidate in incumbent_candidates]
    spectral = [_neutral_spectral(binary) for _coefficients, binary in spectral_candidates]
    return incumbent, spectral


def _draw_sheet(label: str, side_images: dict[str, list[Image.Image]]) -> Image.Image:
    frame_w = frame_h = 400
    cols = 3
    rows = 2
    gap = 12
    side_gap = 38
    header_h = 126
    side_width = cols * frame_w + (cols - 1) * gap
    side_height = rows * frame_h + (rows - 1) * gap
    width = side_width * 2 + side_gap
    height = header_h + side_height
    sheet = Image.new("RGB", (width, height), (9, 9, 9))
    draw = ImageDraw.Draw(sheet)
    title_font = _font(30)
    label_font = _font(26)
    small_font = _font(18)

    draw.text((16, 10), f"Blind form-grammar review {label}", fill=(245, 245, 245), font=title_font)
    draw.text(
        (16, 50),
        "Which side contains the stronger static mathematical-form grammar worth keeping/developing?",
        fill=(210, 210, 210),
        font=small_font,
    )
    draw.text((16, 76), "Answer: A>B, B>A, equivalent, or unreviewable", fill=(190, 190, 190), font=small_font)

    for side_index, side in enumerate(("A", "B")):
        x0 = side_index * (side_width + side_gap)
        draw.text((x0 + side_width // 2, 108), side, fill=(255, 255, 255), font=label_font, anchor="mm")
        images = side_images[side]
        for slot, image in enumerate(images):
            row = slot // cols
            col = slot % cols
            x = x0 + col * (frame_w + gap)
            y = header_h + row * (frame_h + gap)
            sheet.paste(image, (x, y))

    divider_x = side_width + side_gap // 2
    draw.line((divider_x, header_h, divider_x, height), fill=(70, 70, 70), width=2)
    return sheet


def generate(label: str, out_dir: Path) -> dict:
    if label not in ALL_BLOCKS:
        raise ValueError(f"unknown block label {label!r}")
    seed, incumbent_route = ALL_BLOCKS[label]
    review_evidence = label in BLOCKS
    if review_evidence:
        if seed not in REVIEW_SEEDS or incumbent_route not in INCUMBENT_ROUTES:
            raise AssertionError("block escaped frozen review population")
    elif seed != SMOKE_SEED or incumbent_route not in INCUMBENT_ROUTES:
        raise AssertionError("smoke block escaped excluded population")

    rasterizer = capacity.FieldRasterizer()
    incumbent_candidates, incumbent_attempts, incumbent_rng_stream = _generate_incumbent(incumbent_route, seed, label)
    spectral_candidates, spectral_attempts, spectral_rng_seed = _generate_spectral(seed, label, incumbent_route, rasterizer)
    incumbent_images, spectral_images = _render_portfolios(incumbent_candidates, spectral_candidates)

    spectral_side = _candidate_side(label, seed, incumbent_route)
    incumbent_side = "B" if spectral_side == "A" else "A"
    raw_side_images = {spectral_side: spectral_images, incumbent_side: incumbent_images}
    side_images = {
        side: [raw_side_images[side][index] for index in _permutation(label, side)]
        for side in ("A", "B")
    }

    all_fps = [_fingerprint(image) for side in ("A", "B") for image in side_images[side]]
    if len(set(all_fps)) != 2 * EXEMPLARS_PER_SIDE:
        raise AssertionError(f"{label}: rendered review phenotypes are not all distinct")

    sheet = _draw_sheet(label, side_images)
    out_dir.mkdir(parents=True, exist_ok=True)
    sheet_dir = out_dir / "sheet"
    key_dir = out_dir / "key"
    sheet_dir.mkdir(exist_ok=True)
    key_dir.mkdir(exist_ok=True)
    sheet_path = sheet_dir / f"{label}.png"
    key_path = key_dir / f"{label}.json"
    sheet.save(sheet_path)

    incumbent_fps = [_fingerprint(image) for image in incumbent_images]
    spectral_fps = [_fingerprint(image) for image in spectral_images]
    key = {
        "version": 1,
        "experiment": "artistic-sampling-invariance-evaluation-v1",
        "label": label,
        "seed": seed,
        "incumbentRoute": incumbent_route,
        "artisticReviewEvidence": review_evidence,
        "spectralRepresentation": SPECTRAL_ROUTE,
        "spectralSide": spectral_side,
        "incumbentSide": incumbent_side,
        "canonicalTime": CANONICAL_TIME,
        "neutralAlpha": NEUTRAL_ALPHA,
        "exemplarsPerSide": EXEMPLARS_PER_SIDE,
        "incumbentAttempts": incumbent_attempts,
        "spectralAttempts": spectral_attempts,
        "incumbentRngStream": incumbent_rng_stream,
        "spectralRngSeed": spectral_rng_seed,
        "sideOrder": {side: _permutation(label, side) for side in ("A", "B")},
        "renderedFingerprints": {
            "spectral": spectral_fps,
            "incumbent": incumbent_fps,
            "A": [_fingerprint(image) for image in side_images["A"]],
            "B": [_fingerprint(image) for image in side_images["B"]],
        },
        "incumbentCandidateIds": [candidate.id for candidate in incumbent_candidates],
        "spectralCoefficientHashes": [
            hashlib.sha256(np.asarray(coefficients, dtype=np.float64).tobytes()).hexdigest()
            for coefficients, _binary in spectral_candidates
        ],
        "hardInvariants": {
            "sixIncumbentPhenotypes": len(incumbent_candidates) == EXEMPLARS_PER_SIDE,
            "sixSpectralPhenotypes": len(spectral_candidates) == EXEMPLARS_PER_SIDE,
            "allIncumbentsHardValid": all(candidate.checks.get("valid", False) for candidate in incumbent_candidates),
            "allSpectralHardValid": all(capacity._field_valid(binary)[0] for _coefficients, binary in spectral_candidates),
            "canonicalTimeIs90": CANONICAL_TIME == 90.0,
            "neutralAlphaIs48": NEUTRAL_ALPHA == 48,
            "allRenderedPhenotypesDistinct": len(set(all_fps)) == 2 * EXEMPLARS_PER_SIDE,
            "oppositeSides": spectral_side != incumbent_side and {spectral_side, incumbent_side} == {"A", "B"},
        },
    }
    if not all(key["hardInvariants"].values()):
        raise AssertionError(f"{label}: hard invariant failure {key['hardInvariants']}")
    key_path.write_text(json.dumps(key, indent=2, sort_keys=True) + "\n")
    return key


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, choices=tuple(ALL_BLOCKS))
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    result = generate(args.label, Path(args.out_dir))
    print(json.dumps({"label": result["label"], "artisticReviewEvidence": result["artisticReviewEvidence"], "hardInvariants": result["hardInvariants"]}, sort_keys=True))


if __name__ == "__main__":
    main()
