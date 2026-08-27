#!/usr/bin/env python3
"""Direct multimodal pairwise artistic judge via the OpenAI Responses API.

The judge is an escalation layer: route validity and the deterministic coarse
selector run first. Only unresolved tie/defer pairs are sent to the model.

The model never sees candidate ids, genomes, code length, compression data, or
legacy diagnostic scores. It receives only the artistic brief and matched
rendered temporal evidence.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Mapping, Optional, Sequence

from PIL import Image, ImageDraw

from pairwise_selector import DimensionVote, PairwiseDecision, PairwiseSelector

PROMPT_VERSION = "multimodal-pairwise-v1"
RESPONSES_URL = "https://api.openai.com/v1/responses"

_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["A", "B", "tie"]},
        "confidence": {"type": "string", "enum": ["clear", "defer"]},
        "rationale": {"type": "string"},
        "brief_adherence": {"type": "string", "enum": ["A", "B", "tie"]},
        "composition_material": {"type": "string", "enum": ["A", "B", "tie"]},
        "temporal_quality": {"type": "string", "enum": ["A", "B", "tie"]},
        "originality": {"type": "string", "enum": ["A", "B", "tie"]},
    },
    "required": [
        "verdict", "confidence", "rationale", "brief_adherence",
        "composition_material", "temporal_quality", "originality",
    ],
    "additionalProperties": False,
}


def _png_bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def _data_url(im: Image.Image) -> str:
    return "data:image/png;base64," + base64.b64encode(_png_bytes(im)).decode("ascii")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _brief_text(brief: Mapping[str, object]) -> str:
    explicit = brief.get("artistic_intent") or brief.get("brief") or brief.get("description")
    if explicit:
        return str(explicit)
    return str(brief.get("name", "Create the strongest generative-art phenotype for the supplied brief."))


def _extract_output_text(response: Mapping[str, object]) -> Optional[str]:
    # REST Responses shape: output -> message -> content -> output_text.text
    for item in response.get("output", []) or []:
        if not isinstance(item, Mapping) or item.get("type") != "message":
            continue
        for content in item.get("content", []) or []:
            if isinstance(content, Mapping) and content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str):
                    return text
    # Some test transports / wrappers expose a convenience output_text field.
    text = response.get("output_text")
    return text if isinstance(text, str) else None


class OpenAIResponsesTransport:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 90.0):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.timeout = timeout

    def __call__(self, payload: Mapping[str, object]) -> Mapping[str, object]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        req = urllib.request.Request(
            RESPONSES_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


class DirectMultimodalSelector(PairwiseSelector):
    name = "openai-direct-multimodal-v1"

    def __init__(
        self,
        render_frame: Callable[[object, float], Image.Image],
        times: Sequence[float],
        model: str = "gpt-5.6-terra",
        reasoning_effort: str = "medium",
        image_detail: str = "high",
        max_api_calls: int = 80,
        cache_path: Optional[Path] = None,
        audit_dir: Optional[Path] = None,
        symmetry: bool = True,
        transport: Optional[Callable[[Mapping[str, object]], Mapping[str, object]]] = None,
    ):
        if image_detail not in {"low", "high", "auto"}:
            raise ValueError("image_detail must be low, high, or auto")
        self.render_frame = render_frame
        self.times = tuple(times)
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.image_detail = image_detail
        self.max_api_calls = max_api_calls
        self.symmetry = symmetry
        self.transport = transport or OpenAIResponsesTransport()
        self.api_calls = 0
        self.cache_path = Path(cache_path) if cache_path else None
        self.audit_dir = Path(audit_dir) if audit_dir else None
        self.cache = {}
        if self.cache_path and self.cache_path.exists():
            try:
                self.cache = json.loads(self.cache_path.read_text())
            except Exception:
                self.cache = {}
        if self.audit_dir:
            (self.audit_dir / "panels").mkdir(parents=True, exist_ok=True)

    def _strip(self, cand) -> Image.Image:
        thumb = 180
        strip = Image.new("RGB", (thumb*len(self.times), thumb), (18,18,18))
        for i,t in enumerate(self.times):
            im = self.render_frame(cand, t).convert("RGB").resize((thumb,thumb))
            strip.paste(im, (i*thumb,0))
        return strip

    def _panel(self, a, b, *, swap: bool = False) -> Image.Image:
        first, second = (b,a) if swap else (a,b)
        thumb = 180
        label_w = 54
        title_h = 34
        row_h = thumb + 2
        can = Image.new("RGB", (label_w + thumb*len(self.times), title_h + 2*row_h), (24,24,24))
        d = ImageDraw.Draw(can)
        d.text((7,8), "Matched temporal horizon — left to right", fill=(240,240,240))
        for row,(label,cand) in enumerate((("A",first),("B",second))):
            y = title_h + row*row_h
            d.text((20,y+thumb//2), label, fill=(245,245,245))
            strip = self._strip(cand)
            can.paste(strip, (label_w,y))
        return can

    def _fingerprint(self, cand) -> str:
        return _sha(_png_bytes(self._strip(cand)))

    def _cache_key(self, a, b, brief: Mapping[str, object]) -> tuple[str,str,str]:
        afp, bfp = self._fingerprint(a), self._fingerprint(b)
        canonical = sorted((afp,bfp))
        config = {
            "promptVersion": PROMPT_VERSION,
            "model": self.model,
            "reasoningEffort": self.reasoning_effort,
            "imageDetail": self.image_detail,
            "times": list(self.times),
            "brief": _brief_text(brief),
            "phenotypes": canonical,
            "symmetry": self.symmetry,
        }
        key = _sha(json.dumps(config, sort_keys=True, separators=(",",":")).encode())
        return key, afp, bfp

    def _flush_cache(self):
        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache, indent=2) + "\n")

    def _payload(self, panel: Image.Image, brief: Mapping[str, object]) -> dict:
        developer = (
            "You are a conservative pairwise judge for generative art. Judge only what is visibly present "
            "across the full temporal sequence and the supplied artistic brief. Prefer a clear winner only "
            "when the margin is meaningful; otherwise return tie with confidence=defer. Consider brief "
            "adherence, composition/material coherence, temporal quality, and originality/non-genericness. "
            "Do not infer or reward code complexity, implementation effort, route, mathematical elegance, "
            "compression, character count, or hidden metadata."
        )
        user = (
            f"ARTISTIC BRIEF:\n{_brief_text(brief)}\n\n"
            f"The image contains candidate A on the first row and candidate B on the second row. "
            f"Each row shows the same matched time samples {list(self.times)} from left to right. "
            "Return the strongest candidate, or tie if the difference is not artistically meaningful."
        )
        payload = {
            "model": self.model,
            "store": False,
            "reasoning": {"effort": self.reasoning_effort},
            "input": [
                {"role":"developer","content":[{"type":"input_text","text":developer}]},
                {"role":"user","content":[
                    {"type":"input_text","text":user},
                    {"type":"input_image","image_url":_data_url(panel),"detail":self.image_detail},
                ]},
            ],
            "text": {"format": {
                "type":"json_schema",
                "name":"pairwise_art_judgment",
                "description":"Conservative pairwise temporal generative-art judgment",
                "strict": True,
                "schema": _SCHEMA,
            }},
            "max_output_tokens": 700,
        }
        return payload

    def _one_pass(self, a, b, brief, *, swap: bool):
        if self.api_calls >= self.max_api_calls:
            return {"ok":False,"error":"api-call-budget-exhausted"}
        panel = self._panel(a,b,swap=swap)
        if self.audit_dir:
            key,_,_ = self._cache_key(a,b,brief)
            suffix = "ba" if swap else "ab"
            panel.save(self.audit_dir / "panels" / f"{key[:14]}-{suffix}.png")
        try:
            self.api_calls += 1
            response = self.transport(self._payload(panel,brief))
            text = _extract_output_text(response)
            if not text:
                return {"ok":False,"error":"missing-output-text","responseId":response.get("id")}
            parsed = json.loads(text)
            if parsed.get("verdict") not in {"A","B","tie"} or parsed.get("confidence") not in {"clear","defer"}:
                return {"ok":False,"error":"invalid-structured-output","responseId":response.get("id")}
            parsed["ok"] = True
            parsed["responseId"] = response.get("id")
            parsed["usage"] = response.get("usage")
            return parsed
        except Exception as e:
            return {"ok":False,"error":f"{type(e).__name__}: {e}"}

    @staticmethod
    def _actual_winner(pass_result, a_fp, b_fp, *, swap: bool):
        if not pass_result.get("ok"):
            return None
        if pass_result.get("confidence") != "clear" or pass_result.get("verdict") == "tie":
            return None
        verdict = pass_result["verdict"]
        if not swap:
            return a_fp if verdict == "A" else b_fp
        return b_fp if verdict == "A" else a_fp

    def _decision_from_record(self, a, b, record, a_fp, b_fp):
        winner_fp = record.get("winnerFingerprint")
        if winner_fp == a_fp:
            verdict, confidence = "a", "clear"
        elif winner_fp == b_fp:
            verdict, confidence = "b", "clear"
        else:
            verdict, confidence = "tie", "defer"
        rationale = record.get("rationale") or record.get("status", "multimodal judgment deferred")
        vote = DimensionVote("multimodal-artistic-judgment", verdict, str(rationale), None, None)
        return PairwiseDecision(a.id,b.id,verdict,confidence,(vote,),f"{self.name}:{self.model}")

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        # Invalid candidates should normally be intercepted by the coarse selector,
        # but fail closed here too.
        av = bool(a.checks.get("valid",False)); bv = bool(b.checks.get("valid",False))
        if av != bv:
            verdict = "a" if av else "b"
            return PairwiseDecision(a.id,b.id,verdict,"clear",(
                DimensionVote("route-validity",verdict,"invalid candidate cannot win",av,bv),
            ),self.name)
        if not av and not bv:
            return PairwiseDecision(a.id,b.id,"tie","defer",(
                DimensionVote("route-validity","tie","both candidates invalid",av,bv),
            ),self.name)

        key,a_fp,b_fp = self._cache_key(a,b,brief)
        if key in self.cache:
            return self._decision_from_record(a,b,self.cache[key],a_fp,b_fp)

        calls_needed = 2 if self.symmetry else 1
        if self.api_calls + calls_needed > self.max_api_calls:
            record={"status":"api-call-budget-exhausted","winnerFingerprint":None,"rationale":"judge call budget exhausted"}
            self.cache[key]=record; self._flush_cache()
            return self._decision_from_record(a,b,record,a_fp,b_fp)

        p1 = self._one_pass(a,b,brief,swap=False)
        p2 = self._one_pass(a,b,brief,swap=True) if self.symmetry else None
        w1 = self._actual_winner(p1,a_fp,b_fp,swap=False)
        w2 = self._actual_winner(p2,a_fp,b_fp,swap=True) if self.symmetry else w1

        if w1 and w2 and w1 == w2:
            winner_fp = w1
            status = "clear"
            rationale = p1.get("rationale", "")
        else:
            winner_fp = None
            status = "defer"
            if not p1.get("ok") or (self.symmetry and not p2.get("ok")):
                rationale = "judge API/output failure; defer"
            elif w1 != w2:
                rationale = "A/B symmetry passes disagree or include a tie; defer"
            else:
                rationale = "model confidence is insufficient; defer"

        record={
            "status":status,
            "winnerFingerprint":winner_fp,
            "rationale":rationale,
            "phenotypes":sorted((a_fp,b_fp)),
            "passAB":p1,
            "passBA":p2,
            "model":self.model,
            "promptVersion":PROMPT_VERSION,
            "times":list(self.times),
        }
        self.cache[key]=record; self._flush_cache()
        return self._decision_from_record(a,b,record,a_fp,b_fp)


class MultimodalEscalatingSelector(PairwiseSelector):
    """Use a conservative coarse selector first; escalate only unresolved ties."""
    name = "coarse-then-openai-multimodal-v1"

    def __init__(self, coarse: PairwiseSelector, **judge_kwargs):
        self.coarse = coarse
        self.direct = DirectMultimodalSelector(**judge_kwargs)

    def compare(self, a, b, brief: Mapping[str, object]) -> PairwiseDecision:
        coarse = self.coarse.compare(a,b,brief)
        if coarse.verdict != "tie":
            return coarse
        return self.direct.compare(a,b,brief)
