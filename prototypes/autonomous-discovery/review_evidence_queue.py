"""Replay-safe v3 human/independent review bundle with evidence provenance.

Legacy judge_queue.py v2 remains untouched. This layer is for calibration-aware
artistic promotion after judge-dependence was observed experimentally.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw

from preference_evidence import PreferenceEvidence

VERSION = 3
PROMPT_VERSION = "evidence-pairwise-v3"
THUMB = 240


def _png_bytes(im: Image.Image) -> bytes:
    b = io.BytesIO(); im.convert("RGB").save(b, format="PNG"); return b.getvalue()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _strip(frames: Sequence[Image.Image]) -> Image.Image:
    out = Image.new("RGB", (THUMB * len(frames), THUMB), (18, 18, 18))
    for i, im in enumerate(frames):
        out.paste(im.convert("RGB").resize((THUMB, THUMB)), (i * THUMB, 0))
    return out


def phenotype_fingerprint(frames: Sequence[Image.Image]) -> str:
    return _sha(_png_bytes(_strip(frames)))


def create_review_bundle(
    out_dir: Path,
    *,
    brief: str,
    times: Sequence[float],
    a_frames: Sequence[Image.Image],
    b_frames: Sequence[Image.Image],
    a_candidate_id: str,
    b_candidate_id: str,
) -> str:
    """Create one blinded pair and persist the exact sealed mapping."""
    out_dir = Path(out_dir); (out_dir / "panels").mkdir(parents=True, exist_ok=True)
    if len(a_frames) != len(times) or len(b_frames) != len(times):
        raise ValueError("frame counts must match temporal horizon")
    afp = phenotype_fingerprint(a_frames); bfp = phenotype_fingerprint(b_frames)
    config = {
        "promptVersion": PROMPT_VERSION,
        "brief": brief,
        "times": list(times),
        "phenotypes": sorted((afp, bfp)),
    }
    pair_id = _sha(json.dumps(config, sort_keys=True, separators=(",", ":")).encode())
    flip = int(hashlib.sha256(pair_id.encode()).hexdigest(), 16) & 1
    raw = [
        (a_candidate_id, afp, a_frames),
        (b_candidate_id, bfp, b_frames),
    ]
    ordered = raw[::-1] if flip else raw

    label_w, title_h, row_h = 54, 44, THUMB + 2
    panel = Image.new("RGB", (label_w + THUMB * len(times), title_h + 2 * row_h), (24,24,24))
    d = ImageDraw.Draw(panel)
    d.text((7, 8), "A / B / tie — judge the complete temporal horizon", fill=(245,245,245))
    for row, (label, item) in enumerate(zip(("A","B"), ordered)):
        cid, fp, frames = item
        y = title_h + row * row_h
        d.text((18, y + THUMB // 2), label, fill=(245,245,245))
        panel.paste(_strip(frames), (label_w, y))
    panel_path = out_dir / "panels" / f"{pair_id[:14]}.png"
    panel.save(panel_path)

    sealed_path = out_dir / "sealed-mapping.json"
    queue_path = out_dir / "queue.json"
    decisions_path = out_dir / "decisions.json"
    sealed = {"version": VERSION, "pairs": {}}
    queue = {"version": VERSION, "pairs": {}}
    decisions = {"version": VERSION, "decisions": {}}
    for path, doc in ((sealed_path,sealed),(queue_path,queue),(decisions_path,decisions)):
        if path.exists():
            loaded = json.loads(path.read_text())
            if loaded.get("version") != VERSION:
                raise ValueError(f"{path.name} has incompatible version")
            if path == sealed_path: sealed = loaded
            elif path == queue_path: queue = loaded
            else: decisions = loaded

    sealed["pairs"][pair_id] = {
        label: {"candidateId": item[0], "phenotypeFingerprint": item[1]}
        for label, item in zip(("A","B"), ordered)
    }
    queue["pairs"][pair_id] = {
        "pairId": pair_id,
        "panel": str(panel_path),
        "brief": brief,
        "times": list(times),
        "promptVersion": PROMPT_VERSION,
        "instruction": "Choose A, B, or tie; record source and confidence. Low-confidence evidence cannot promote.",
    }
    decisions["decisions"].setdefault(pair_id, {
        "verdict": None,
        "sourceClass": None,
        "sourceId": None,
        "confidence": None,
        "rationale": "",
        "allowedVerdicts": ["A","B","tie"],
        "allowedSourceClasses": ["human","independent-model","same-model","deterministic-proxy"],
        "allowedConfidence": ["strong","low","defer"],
    })
    sealed_path.write_text(json.dumps(sealed, indent=2) + "\n")
    queue_path.write_text(json.dumps(queue, indent=2) + "\n")
    decisions_path.write_text(json.dumps(decisions, indent=2) + "\n")
    return pair_id


def decode_review_evidence(out_dir: Path) -> list[PreferenceEvidence]:
    out_dir = Path(out_dir)
    sealed = json.loads((out_dir / "sealed-mapping.json").read_text())
    decisions = json.loads((out_dir / "decisions.json").read_text())
    if sealed.get("version") != VERSION or decisions.get("version") != VERSION:
        raise ValueError("review bundle must be v3")
    out = []
    for pair_id, item in decisions["decisions"].items():
        verdict = item.get("verdict")
        if verdict is None:
            continue
        if verdict not in {"A","B","tie"}:
            raise ValueError(f"invalid verdict for {pair_id}")
        source_class = item.get("sourceClass")
        source_id = item.get("sourceId")
        confidence = item.get("confidence")
        if not source_class or not source_id or not confidence:
            raise ValueError(f"decision {pair_id} is missing provenance/confidence")
        if verdict == "tie":
            canonical = "tie"
        else:
            mapping = sealed["pairs"][pair_id][verdict]
            other = sealed["pairs"][pair_id]["B" if verdict == "A" else "A"]
            canonical = "tie" if mapping["phenotypeFingerprint"] == other["phenotypeFingerprint"] else verdict.lower()
        out.append(PreferenceEvidence(
            pair_id=pair_id,
            verdict=canonical,
            source_class=source_class,
            source_id=source_id,
            confidence=confidence,
            rationale=item.get("rationale", ""),
        ))
    return out
