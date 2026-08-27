#!/usr/bin/env python3
"""Temporal A/B artifact queue for unresolved pairwise artistic judgments.

Offline/session judgments are keyed by what the evaluator actually saw, not by
candidate ids. This matters because replay can change an earlier promotion,
which can change the genome rendered later under the same downstream candidate id.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from typing import Callable, Dict, Mapping, Optional, Sequence

from PIL import Image, ImageDraw

from pairwise_selector import DimensionVote, PairwiseDecision, PairwiseSelector

QUEUE_PROMPT_VERSION = "filesystem-pairwise-v2"
THUMB = 150


def _png_bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _brief_text(brief: Mapping[str, object]) -> str:
    explicit = brief.get("artistic_intent") or brief.get("brief") or brief.get("description")
    if explicit:
        return str(explicit)
    return str(brief.get("name", "Create the strongest generative-art phenotype for the supplied brief."))


def _strip(cand, render_frame: Callable[[object, float], Image.Image], times: Sequence[float]) -> Image.Image:
    times = tuple(times)
    strip = Image.new("RGB", (THUMB * len(times), THUMB), (18, 18, 18))
    for i, t in enumerate(times):
        im = render_frame(cand, t).convert("RGB").resize((THUMB, THUMB))
        strip.paste(im, (i * THUMB, 0))
    return strip


def phenotype_fingerprint(cand, render_frame, times) -> str:
    """Fingerprint the exact matched-time strip shown to the offline evaluator."""
    return _sha(_png_bytes(_strip(cand, render_frame, times)))


def judgment_pair_key(a, b, brief, render_frame, times):
    """Return an order-independent judgment key plus each current phenotype hash."""
    afp = phenotype_fingerprint(a, render_frame, times)
    bfp = phenotype_fingerprint(b, render_frame, times)
    config = {
        "promptVersion": QUEUE_PROMPT_VERSION,
        "times": list(times),
        "brief": _brief_text(brief),
        "phenotypes": sorted((afp, bfp)),
    }
    pair_id = _sha(json.dumps(config, sort_keys=True, separators=(",", ":")).encode())
    return pair_id, afp, bfp


class RecordedPhenotypeDecisionSelector(PairwiseSelector):
    """Replay offline judgments only when the current visible phenotypes still match."""

    name = "recorded-phenotype-decisions-v2"

    def __init__(
        self,
        decisions: Mapping[str, str],
        render_frame: Callable[[object, float], Image.Image],
        times: Sequence[float],
        fallback: Optional[PairwiseSelector] = None,
    ):
        self.decisions = dict(decisions)
        self.render_frame = render_frame
        self.times = tuple(times)
        self.fallback = fallback

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        pair_id, afp, bfp = judgment_pair_key(a, b, brief, self.render_frame, self.times)
        if pair_id not in self.decisions:
            if self.fallback is not None:
                return self.fallback.compare(a, b, brief)
            return PairwiseDecision(
                a.id,
                b.id,
                "tie",
                "defer",
                (DimensionVote("recorded-phenotype-judgment", "tie", "no recorded judgment for the current rendered phenotypes"),),
                self.name,
            )

        result = self.decisions[pair_id]
        if result == "tie" or afp == bfp:
            verdict = "tie"
        elif result == afp:
            verdict = "a"
        elif result == bfp:
            verdict = "b"
        else:
            # The pair id already commits to both phenotype fingerprints, so this
            # should indicate a corrupt/stale decision artifact. Fail closed.
            verdict = "tie"

        return PairwiseDecision(
            a.id,
            b.id,
            verdict,
            "defer" if verdict == "tie" else "clear",
            (DimensionVote("recorded-phenotype-judgment", verdict, "replayed judgment for the same visible phenotype pair", result, result),),
            self.name,
        )


class QueueingSelector(PairwiseSelector):
    """Wrap a selector and export every unresolved visible phenotype pair.

    During the originating run a tie remains a tie. Completed judgments can be
    replayed later, but only if brief, temporal horizon, and rendered phenotypes
    still match.
    """

    name = "queueing-selector-v2"

    def __init__(
        self,
        inner: PairwiseSelector,
        out_dir: Path,
        render_frame: Callable[[object, float], Image.Image],
        times: Sequence[float],
    ):
        self.inner = inner
        self.out_dir = Path(out_dir)
        self.render_frame = render_frame
        self.times = tuple(times)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "panels").mkdir(exist_ok=True)
        self.queue_path = self.out_dir / "queue.json"
        self.sealed_path = self.out_dir / "sealed-mapping.json"
        self.decisions_path = self.out_dir / "decisions-template.json"
        self._queue: Dict[str, Dict[str, object]] = {}
        self._sealed: Dict[str, Dict[str, object]] = {}
        self._flush()

    def _blind_order(self, pair_id: str, a, b, afp: str, bfp: str):
        flip = int(hashlib.sha256(pair_id.encode()).hexdigest(), 16) & 1
        rows = ((a, afp), (b, bfp)) if not flip else ((b, bfp), (a, afp))
        return (("A", rows[0][0], rows[0][1]), ("B", rows[1][0], rows[1][1]))

    def _render_panel(self, pair_id: str, order) -> Path:
        label_w = 52
        title_h = 28
        row_h = THUMB + 2
        can = Image.new("RGB", (label_w + THUMB * len(self.times), title_h + row_h * 2), (26, 26, 26))
        draw = ImageDraw.Draw(can)
        draw.text((6, 6), "A / B / tie — matched temporal horizon", fill=(240, 240, 240))
        for row, (label, cand, _) in enumerate(order):
            y = title_h + row * row_h
            draw.text((17, y + THUMB // 2), label, fill=(240, 240, 240))
            can.paste(_strip(cand, self.render_frame, self.times), (label_w, y))
        path = self.out_dir / "panels" / f"{pair_id[:14]}.png"
        can.save(path)
        return path

    def _flush(self):
        self.queue_path.write_text(json.dumps({"version": 2, "pairs": list(self._queue.values())}, indent=2) + "\n")
        self.sealed_path.write_text(json.dumps({"version": 2, "pairs": self._sealed}, indent=2) + "\n")
        template = {
            pair_id: {"verdict": None, "allowed": ["A", "B", "tie"]}
            for pair_id in self._queue
        }
        self.decisions_path.write_text(json.dumps({"version": 2, "decisions": template}, indent=2) + "\n")

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        decision = self.inner.compare(a, b, brief)
        if decision.verdict != "tie":
            return decision

        pair_id, afp, bfp = judgment_pair_key(a, b, brief, self.render_frame, self.times)
        # Pixel-identical visible evidence cannot support a meaningful A/B preference.
        if afp == bfp:
            return decision

        if pair_id not in self._queue:
            order = self._blind_order(pair_id, a, b, afp, bfp)
            panel = self._render_panel(pair_id, order)
            self._sealed[pair_id] = {
                **{
                    label: {"candidateId": cand.id, "phenotypeFingerprint": fp}
                    for label, cand, fp in order
                },
                "proxyDecision": decision.to_json(),
            }
            self._queue[pair_id] = {
                "pairId": pair_id,
                "panel": str(panel),
                "briefName": brief.get("name"),
                "times": list(self.times),
                "promptVersion": QUEUE_PROMPT_VERSION,
                "instruction": "Choose A, B, or tie. Judge the defining phenotype across the full temporal horizon; do not use code length.",
            }
            self._flush()
        return decision


def decode_blind_decisions(queue_dir: Path) -> Dict[str, str]:
    """Decode completed v2 blind decisions into pair-id -> winner-fingerprint/tie."""
    queue_dir = Path(queue_dir)
    sealed_doc = json.loads((queue_dir / "sealed-mapping.json").read_text())
    decisions_doc = json.loads((queue_dir / "decisions-template.json").read_text())
    if sealed_doc.get("version") != 2 or decisions_doc.get("version") != 2:
        raise ValueError("legacy id-keyed judge queues are not replay-safe; regenerate the queue with v2")
    sealed = sealed_doc["pairs"]
    decisions = decisions_doc["decisions"]
    out: Dict[str, str] = {}
    for pair_id, item in decisions.items():
        verdict = item.get("verdict")
        if verdict is None:
            continue
        mapping = sealed[pair_id]
        if verdict == "tie":
            out[pair_id] = "tie"
        elif verdict in ("A", "B"):
            afp = mapping["A"]["phenotypeFingerprint"]
            bfp = mapping["B"]["phenotypeFingerprint"]
            out[pair_id] = "tie" if afp == bfp else mapping[verdict]["phenotypeFingerprint"]
        else:
            raise ValueError(f"invalid verdict {verdict!r} for {pair_id}")
    return out
