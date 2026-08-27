#!/usr/bin/env python3
"""Temporal A/B artifact queue for unresolved pairwise artistic judgments."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable, Dict, Mapping, Sequence

from PIL import Image, ImageDraw

from pairwise_selector import PairwiseDecision, PairwiseSelector


class QueueingSelector(PairwiseSelector):
    """Wrap a selector and export every tie/defer as a blinded temporal panel.

    The wrapper does not turn asynchronous review into fake synchronous certainty.
    During the current run a tie remains a tie. The exported decision file can be
    completed later and replayed with ``RecordedDecisionSelector`` under the same seed.
    """

    name = "queueing-selector"

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
        self._sealed: Dict[str, Dict[str, str]] = {}
        self._flush()

    @staticmethod
    def pair_key(a_id: str, b_id: str) -> str:
        raw = "::".join(sorted((a_id, b_id)))
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def _blind_order(self, pair_id: str, a, b):
        # Deterministic without exposing lexical candidate order to the evaluator.
        flip = int(hashlib.sha256(pair_id.encode()).hexdigest(), 16) & 1
        return (("A", a), ("B", b)) if not flip else (("A", b), ("B", a))

    def _render_panel(self, pair_id: str, a, b) -> Path:
        order = self._blind_order(pair_id, a, b)
        thumb = 150
        label_w = 52
        title_h = 28
        row_h = thumb + 2
        can = Image.new("RGB", (label_w + thumb*len(self.times), title_h + row_h*2), (26,26,26))
        draw = ImageDraw.Draw(can)
        draw.text((6,6), "A / B / tie — matched temporal horizon", fill=(240,240,240))
        for row,(label,cand) in enumerate(order):
            y = title_h + row*row_h
            draw.text((17,y+thumb//2), label, fill=(240,240,240))
            for col,t in enumerate(self.times):
                im = self.render_frame(cand, t).convert("RGB").resize((thumb,thumb))
                can.paste(im, (label_w+col*thumb, y))
        path = self.out_dir / "panels" / f"{pair_id}.png"
        can.save(path)
        self._sealed[pair_id] = {label: cand.id for label,cand in order}
        return path

    def _flush(self):
        self.queue_path.write_text(json.dumps({"pairs": list(self._queue.values())}, indent=2) + "\n")
        self.sealed_path.write_text(json.dumps(self._sealed, indent=2) + "\n")
        template = {
            pair_id: {"verdict": None, "allowed": ["A","B","tie"]}
            for pair_id in self._queue
        }
        self.decisions_path.write_text(json.dumps(template, indent=2) + "\n")

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        decision = self.inner.compare(a, b, brief)
        if decision.verdict != "tie":
            return decision
        pair_id = self.pair_key(a.id, b.id)
        if pair_id not in self._queue:
            panel = self._render_panel(pair_id, a, b)
            self._queue[pair_id] = {
                "pairId": pair_id,
                "panel": str(panel),
                "briefName": brief.get("name"),
                "routes": sorted({a.route, b.route}),
                "times": list(self.times),
                "instruction": "Choose A, B, or tie. Judge the defining phenotype across the full temporal horizon; do not use code length.",
                "proxyDecision": decision.to_json(),
            }
            self._flush()
        return decision


def decode_blind_decisions(queue_dir: Path) -> Dict[str, str]:
    """Convert completed blind A/B decisions into RecordedDecisionSelector format."""
    queue_dir = Path(queue_dir)
    sealed = json.loads((queue_dir / "sealed-mapping.json").read_text())
    decisions = json.loads((queue_dir / "decisions-template.json").read_text())
    out: Dict[str,str] = {}
    for pair_id, item in decisions.items():
        verdict = item.get("verdict")
        if verdict is None:
            continue
        mapping = sealed[pair_id]
        candidate_ids = sorted(mapping.values())
        key = "::".join(candidate_ids)
        if verdict == "tie":
            out[key] = "tie"
        elif verdict in ("A","B"):
            out[key] = mapping[verdict]
        else:
            raise ValueError(f"invalid verdict {verdict!r} for {pair_id}")
    return out
