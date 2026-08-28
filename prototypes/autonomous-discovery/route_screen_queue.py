"""Blinded representation-level visual screen with replay-safe provenance.

The reviewer sees anonymous groups of actual probe phenotypes and marks each group
keep / drop / defer. Route identity is sealed until decisions are persisted.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
from typing import Callable, Mapping, Sequence
from PIL import Image, ImageDraw

from route_allocation_policy import RouteEvidence

VERSION = 1
THUMB = 150


def _png_bytes(im: Image.Image) -> bytes:
    b = io.BytesIO(); im.convert("RGB").save(b, format="PNG"); return b.getvalue()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _candidate_strip(cand, render_frame: Callable, times: Sequence[float]) -> Image.Image:
    out = Image.new("RGB", (THUMB * len(times), THUMB), (18, 18, 18))
    for i, t in enumerate(times):
        out.paste(render_frame(cand, t).convert("RGB").resize((THUMB, THUMB)), (i * THUMB, 0))
    return out


def _group_fingerprint(candidates, render_frame, times) -> str:
    parts = [_png_bytes(_candidate_strip(c, render_frame, times)) for c in candidates]
    return _sha(b"\0".join(parts))


def _brief_text(brief: Mapping[str, object]) -> str:
    return str(brief.get("artistic_intent") or brief.get("brief") or brief.get("description") or brief.get("name") or "")


def build_route_screen(
    *,
    brief: Mapping[str, object],
    route_candidates: Mapping[str, Sequence[object]],
    render_frame: Callable[[object, float], Image.Image],
    times: Sequence[float],
    out_dir: Path,
) -> dict:
    routes = tuple(route_candidates)
    if len(routes) < 2 or len(routes) > 26:
        raise ValueError("route screen expects 2..26 routes")
    if any(not tuple(route_candidates[r]) for r in routes):
        raise ValueError("every route must expose at least one probe candidate")
    times = tuple(times)
    if not times:
        raise ValueError("times are required")
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    group_fp = {r: _group_fingerprint(tuple(route_candidates[r]), render_frame, times) for r in routes}
    config = {
        "version": VERSION,
        "brief": _brief_text(brief),
        "times": list(times),
        "groups": sorted(group_fp.values()),
    }
    screen_id = _sha(json.dumps(config, sort_keys=True, separators=(",", ":")).encode())
    order = sorted(routes, key=lambda r: _sha(f"{screen_id}:{group_fp[r]}".encode()))
    labels = [chr(ord("A") + i) for i in range(len(order))]
    mapping = dict(zip(labels, order))

    max_candidates = max(len(tuple(route_candidates[r])) for r in routes)
    strip_w = THUMB * len(times)
    label_w = 54; gap = 7; title_h = 40; row_h = THUMB + 24
    width = label_w + max_candidates * (strip_w + gap) + gap
    height = title_h + len(order) * row_h
    can = Image.new("RGB", (width, height), (246, 246, 244))
    draw = ImageDraw.Draw(can)
    draw.text((8, 8), "Route screen — mark each anonymous visual grammar keep / drop / defer", fill=(20, 20, 20))
    sealed = {}
    for i, label in enumerate(labels):
        route = mapping[label]; y = title_h + i * row_h
        draw.text((18, y + THUMB // 2), label, fill=(10, 10, 10))
        fps = []
        for j, cand in enumerate(route_candidates[route]):
            strip = _candidate_strip(cand, render_frame, times)
            x = label_w + j * (strip_w + gap)
            can.paste(strip, (x, y + 18))
            fps.append(_sha(_png_bytes(strip)))
        sealed[label] = {
            "route": route,
            "groupFingerprint": group_fp[route],
            "phenotypeFingerprints": fps,
        }
    panel = out_dir / "route-screen.png"; can.save(panel)
    queue = {
        "version": VERSION,
        "screenId": screen_id,
        "brief": _brief_text(brief),
        "times": list(times),
        "panel": str(panel),
        "groups": labels,
        "instruction": "For every group mark keep, drop, or defer. Keep means this visual grammar is worth deeper search for the brief; drop means clearly unsuitable; defer means uncertain.",
    }
    template = {
        "version": VERSION,
        "screenId": screen_id,
        "decisions": {lab: {"verdict": None, "confidence": None, "allowedVerdicts": ["keep", "drop", "defer"], "allowedConfidence": ["strong", "low", "defer"]} for lab in labels},
    }
    (out_dir / "queue.json").write_text(json.dumps(queue, indent=2) + "\n")
    (out_dir / "sealed-mapping.json").write_text(json.dumps({"version": VERSION, "screenId": screen_id, "groups": sealed}, indent=2) + "\n")
    (out_dir / "decisions-template.json").write_text(json.dumps(template, indent=2) + "\n")
    return queue


def decode_route_screen(queue_dir: Path, *, source_class: str, source_id: str) -> list[RouteEvidence]:
    queue_dir = Path(queue_dir)
    sealed = json.loads((queue_dir / "sealed-mapping.json").read_text())
    decisions = json.loads((queue_dir / "decisions-template.json").read_text())
    if sealed.get("version") != VERSION or decisions.get("version") != VERSION:
        raise ValueError("unsupported route-screen version")
    if sealed.get("screenId") != decisions.get("screenId"):
        raise ValueError("screen id mismatch")
    out = []
    for label, item in decisions["decisions"].items():
        verdict = item.get("verdict")
        confidence = item.get("confidence")
        if verdict is None:
            continue
        if verdict not in {"keep", "drop", "defer"}:
            raise ValueError(f"invalid verdict for {label}: {verdict!r}")
        if confidence not in {"strong", "low", "defer"}:
            raise ValueError(f"invalid confidence for {label}: {confidence!r}")
        route = sealed["groups"][label]["route"]
        out.append(RouteEvidence(
            route=route,
            verdict=verdict,
            source_class=source_class,
            source_id=source_id,
            confidence=confidence,
            rationale=f"blinded route screen {sealed['screenId']}",
        ))
    evidence_doc = {
        "version": VERSION,
        "screenId": sealed["screenId"],
        "sourceClass": source_class,
        "sourceId": source_id,
        "evidence": [
            {
                "route": e.route,
                "verdict": e.verdict,
                "confidence": e.confidence,
                "sourceClass": e.source_class,
                "sourceId": e.source_id,
                "rationale": e.rationale,
                "promotionAuthoritative": e.authoritative,
                "groupFingerprint": next(
                    item["groupFingerprint"] for item in sealed["groups"].values()
                    if item["route"] == e.route
                ),
            }
            for e in out
        ],
    }
    (queue_dir / "route-evidence.json").write_text(json.dumps(evidence_doc, indent=2) + "\n")
    return out
