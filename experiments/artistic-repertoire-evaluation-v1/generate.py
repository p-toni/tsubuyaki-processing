#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PILOT_PATH = ROOT / "experiments" / "repertoire-allocation-v1" / "run.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


pilot = _load("artistic_repertoire_allocation_v1", PILOT_PATH)

REVIEW_SEEDS = (41011, 41017, 41023, 41047)
ROUTE_ORDER = tuple(pilot.ROUTE_ORDER)
TIMES = tuple(pilot.v1.TIMES)
POLICIES = ("lineage-depth", "repertoire-preserving")

BLOCKS = {
    "R01": (41011, "filament"),
    "R02": (41017, "filament"),
    "R03": (41017, "orbit"),
    "R04": (41017, "family"),
    "R05": (41017, "sheet"),
    "R06": (41011, "sheet"),
    "R07": (41017, "recurrence"),
    "R08": (41047, "sheet"),
    "R09": (41047, "recurrence"),
    "R10": (41047, "family"),
    "R11": (41023, "filament"),
    "R12": (41023, "orbit"),
    "R13": (41023, "family"),
    "R14": (41047, "orbit"),
    "R15": (41011, "recurrence"),
    "R16": (41011, "orbit"),
    "R17": (41011, "family"),
    "R18": (41023, "recurrence"),
    "R19": (41023, "sheet"),
    "R20": (41047, "filament"),
}


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _candidate_by_id(policy_result: dict) -> dict[str, object]:
    out = {c.id: c for c in policy_result["starts"]}
    out.update({c.id: c for c in policy_result["generated"]})
    return out


def _endpoint_by_basin(policy_result: dict) -> dict[str, object]:
    starts = {c.basin: c for c in policy_result["starts"]}
    candidates = _candidate_by_id(policy_result)
    events_by_basin: dict[str, list[dict]] = defaultdict(list)
    for event in policy_result["events"]:
        events_by_basin[str(event["basin"])].append(event)

    endpoints = {}
    for basin in sorted(starts):
        endpoint = starts[basin]
        for event in reversed(events_by_basin[basin]):
            if bool(event["childValid"]):
                endpoint = candidates[str(event["child"])]
                break
        if not endpoint.checks.get("valid", False):
            raise AssertionError(f"selected endpoint is invalid: {basin}/{endpoint.id}")
        endpoints[basin] = endpoint
    if len(endpoints) != pilot.STARTS_PER_ROUTE:
        raise AssertionError("endpoint count drift")
    return endpoints


def _candidate_side(label: str, seed: int, route: str) -> str:
    payload = f"artistic-repertoire-evaluation-v1|{label}|{seed}|{route}|side".encode()
    bit = hashlib.sha256(payload).digest()[0] & 1
    return "A" if bit else "B"


def _render(candidate) -> list[Image.Image]:
    return [pilot.v1.render_candidate_frame(candidate, t).convert("RGB") for t in TIMES]


def _draw_sheet(label: str, side_endpoints: dict[str, dict[str, object]]) -> Image.Image:
    frame_w = frame_h = 400
    gap = 10
    side_gap = 36
    header_h = 92
    row_label_w = 42
    side_width = row_label_w + 3 * frame_w + 2 * gap
    width = side_width * 2 + side_gap
    height = header_h + pilot.STARTS_PER_ROUTE * frame_h
    sheet = Image.new("RGB", (width, height), (9, 9, 9))
    draw = ImageDraw.Draw(sheet)
    title_font = _font(30)
    label_font = _font(24)
    small_font = _font(18)

    draw.text((16, 10), f"Blind review {label}", fill=(245, 245, 245), font=title_font)
    draw.text((16, 52), "Choose the stronger portfolio: A>B, B>A, equivalent, or unreviewable", fill=(210, 210, 210), font=small_font)

    for side_index, side in enumerate(("A", "B")):
        x0 = side_index * (side_width + side_gap)
        draw.text((x0 + row_label_w, 10), side, fill=(255, 255, 255), font=title_font)
        endpoints = side_endpoints[side]
        for row_index, basin in enumerate(sorted(endpoints)):
            y0 = header_h + row_index * frame_h
            draw.text((x0 + 8, y0 + 12), str(row_index + 1), fill=(220, 220, 220), font=label_font)
            frames = _render(endpoints[basin])
            for frame_index, frame in enumerate(frames):
                x = x0 + row_label_w + frame_index * (frame_w + gap)
                sheet.paste(frame, (x, y0))
                if row_index == 0:
                    draw.text((x + 8, y0 + 8), f"t={TIMES[frame_index]}", fill=(210, 210, 210), font=small_font)

    return sheet


def generate(label: str, out_dir: Path) -> dict:
    if label not in BLOCKS:
        raise ValueError(f"unknown block label {label!r}")
    seed, route = BLOCKS[label]
    if seed not in REVIEW_SEEDS or route not in ROUTE_ORDER:
        raise AssertionError("block mapping escaped frozen population")

    brief = pilot._brief(route)
    starts, start_attempts = pilot._generate_starts(brief, seed, route)
    baseline = pilot._run_policy(route, brief, seed, starts, "lineage-depth")
    candidate = pilot._run_policy(route, brief, seed, starts, "repertoire-preserving")

    if pilot._event_signature(baseline) != pilot._event_signature(candidate):
        raise AssertionError("matched event stream drift")
    if baseline["diagnostics"]["generatedCandidates"] != pilot.GENERATED_PER_ARM:
        raise AssertionError("baseline budget drift")
    if candidate["diagnostics"]["generatedCandidates"] != pilot.GENERATED_PER_ARM:
        raise AssertionError("candidate budget drift")

    baseline_endpoints = _endpoint_by_basin(baseline)
    candidate_endpoints = _endpoint_by_basin(candidate)
    if set(baseline_endpoints) != set(candidate_endpoints):
        raise AssertionError("matched basin set drift")

    candidate_side = _candidate_side(label, seed, route)
    baseline_side = "B" if candidate_side == "A" else "A"
    side_endpoints = {
        candidate_side: candidate_endpoints,
        baseline_side: baseline_endpoints,
    }

    sheet = _draw_sheet(label, side_endpoints)
    out_dir.mkdir(parents=True, exist_ok=True)
    sheet_dir = out_dir / "sheet"
    key_dir = out_dir / "key"
    sheet_dir.mkdir(exist_ok=True)
    key_dir.mkdir(exist_ok=True)
    sheet_path = sheet_dir / f"{label}.png"
    key_path = key_dir / f"{label}.json"
    sheet.save(sheet_path)

    key = {
        "version": 1,
        "label": label,
        "seed": seed,
        "route": route,
        "candidatePolicy": "repertoire-preserving",
        "baselinePolicy": "lineage-depth",
        "candidateSide": candidate_side,
        "baselineSide": baseline_side,
        "startGenerationAttempts": start_attempts,
        "rawRendererTimes": list(TIMES),
        "presentationEndpointRule": "latest hard-valid generated child per basin, otherwise shared start",
        "endpoints": {
            "A": [side_endpoints["A"][basin].id for basin in sorted(side_endpoints["A"])],
            "B": [side_endpoints["B"][basin].id for basin in sorted(side_endpoints["B"])],
        },
        "hardInvariants": {
            "sharedStarts": {c.id: pilot.v1.phenotype_fingerprint(c) for c in baseline["starts"]}
                == {c.id: pilot.v1.phenotype_fingerprint(c) for c in candidate["starts"]},
            "matchedEventStreams": pilot._event_signature(baseline) == pilot._event_signature(candidate),
            "equalGeneratedBudget": baseline["diagnostics"]["generatedCandidates"] == candidate["diagnostics"]["generatedCandidates"] == pilot.GENERATED_PER_ARM,
            "equalBasinBudget": baseline["diagnostics"]["eventsPerBasin"] == candidate["diagnostics"]["eventsPerBasin"],
            "sixPresentationEndpointsPerSide": len(baseline_endpoints) == len(candidate_endpoints) == pilot.STARTS_PER_ROUTE,
        },
    }
    if not all(key["hardInvariants"].values()):
        raise AssertionError(f"hard invariant failure: {key['hardInvariants']}")
    key_path.write_text(json.dumps(key, indent=2, sort_keys=True) + "\n")
    return key


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, choices=tuple(BLOCKS))
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    result = generate(args.label, Path(args.out_dir))
    print(json.dumps({"label": result["label"], "hardInvariants": result["hardInvariants"]}, sort_keys=True))


if __name__ == "__main__":
    main()
