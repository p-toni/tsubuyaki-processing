from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from PIL import Image, ImageDraw

from core import Candidate, ROUTES, TIMES, evaluate_candidate, render_candidate_frame
from rng_streams import derived_seed

SIDECAR_VERSION = 1
SIDECAR_NAMESPACE = "restart-sidecar-v1"
DEFAULT_ATTEMPTS_PER_ROUTE = 4


def _eligible_routes(brief: Dict[str, object]) -> List[str]:
    routes = list(brief.get("routes") or [])
    return [
        route
        for route in routes
        if route in ROUTES and int(ROUTES[route].get("intrinsic_dimension", -1)) == 1
    ]


def _phenotype_hash(cand: Candidate) -> str:
    h = hashlib.sha256()
    h.update(cand.route.encode("utf-8"))
    for t in TIMES:
        h.update(render_candidate_frame(cand, t).tobytes())
    return h.hexdigest()


def _spawn_restart(brief: Dict[str, object], master_seed: int, route: str, index: int) -> Candidate:
    rng = random.Random(derived_seed(master_seed, SIDECAR_NAMESPACE, route, index))
    prefix = str(ROUTES[route].get("prefix", route[:1].upper()))
    cid = f"SC-{prefix}{index + 1}"
    cand = Candidate(
        cid,
        route,
        cid,
        ROUTES[route]["seed"](rng),
        None,
        "restart-sidecar",
    )
    evaluate_candidate(cand, brief)
    cand.checks["generationOperator"] = "restart-sidecar"
    cand.checks["sidecarVersion"] = SIDECAR_VERSION
    cand.checks["mayEnterBaselineSearch"] = False
    cand.checks["mayParentBaselineSearch"] = False
    cand.checks["mayReplaceBaselineDelivery"] = False
    return cand


def _write_timeline(cand: Candidate, path: Path) -> None:
    thumb = 180
    canvas = Image.new("RGB", (thumb * len(TIMES), thumb + 20), (26, 26, 26))
    draw = ImageDraw.Draw(canvas)
    for i, t in enumerate(TIMES):
        frame = render_candidate_frame(cand, t).convert("RGB").resize(
            (thumb, thumb), Image.Resampling.NEAREST
        )
        canvas.paste(frame, (i * thumb, 0))
        draw.text((i * thumb + 6, thumb + 2), f"t={t}", fill=(230, 230, 230))
    canvas.save(path)


def _write_contact_sheet(cands: List[Candidate], path: Path) -> None:
    if not cands:
        return
    thumb = 150
    label_h = 22
    cols = min(4, len(cands))
    rows = math.ceil(len(cands) / cols)
    canvas = Image.new("RGB", (cols * thumb, rows * (thumb + label_h)), (26, 26, 26))
    draw = ImageDraw.Draw(canvas)
    for i, cand in enumerate(cands):
        x = (i % cols) * thumb
        y = (i // cols) * (thumb + label_h)
        frame = render_candidate_frame(cand, 90).convert("RGB").resize(
            (thumb, thumb), Image.Resampling.NEAREST
        )
        canvas.paste(frame, (x, y))
        draw.text((x + 4, y + thumb + 3), f"{cand.id} · {cand.route}", fill=(230, 230, 230))
    canvas.save(path)


def generate_restart_sidecar(
    brief: Dict[str, object],
    master_seed: int,
    out_dir: Path,
    attempts_per_route: int = DEFAULT_ATTEMPTS_PER_ROUTE,
) -> Dict[str, object]:
    """Generate isolated route-prior discoveries without touching baseline search state.

    The sidecar is deliberately post-search and authority-limited. Candidates are never
    compared with, inserted into, or allowed to parent the baseline search. Invalid draws
    consume their attempt and are not retried.
    """
    attempts_per_route = int(attempts_per_route)
    if attempts_per_route <= 0:
        raise ValueError("attempts_per_route must be positive when the sidecar is enabled")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timelines_dir = out_dir / "timelines"
    timelines_dir.mkdir(parents=True, exist_ok=True)

    eligible = _eligible_routes(brief)
    candidates: List[Candidate] = []
    for route in eligible:
        for index in range(attempts_per_route):
            candidates.append(_spawn_restart(brief, master_seed, route, index))

    valid = [c for c in candidates if bool(c.checks.get("valid", False))]
    for cand in valid:
        _write_timeline(cand, timelines_dir / f"{cand.id}.png")
    if valid:
        _write_contact_sheet(valid, out_dir / "contact_sheet.png")

    candidate_records = []
    for cand in candidates:
        record = asdict(cand)
        record["phenotypeHash"] = _phenotype_hash(cand)
        candidate_records.append(record)
    candidate_text = json.dumps(candidate_records, indent=2, sort_keys=True) + "\n"
    candidate_digest = hashlib.sha256(candidate_text.encode("utf-8")).hexdigest()

    by_route = {}
    for route in eligible:
        route_cands = [c for c in candidates if c.route == route]
        by_route[route] = {
            "attempted": len(route_cands),
            "valid": sum(bool(c.checks.get("valid", False)) for c in route_cands),
            "candidateIds": [c.id for c in route_cands],
            "validCandidateIds": [c.id for c in route_cands if bool(c.checks.get("valid", False))],
        }

    report: Dict[str, object] = {
        "version": SIDECAR_VERSION,
        "mode": SIDECAR_NAMESPACE,
        "masterSeed": int(master_seed),
        "attemptsPerEligibleRoute": attempts_per_route,
        "eligibleRoutes": eligible,
        "attemptedCandidates": len(candidates),
        "validCandidates": len(valid),
        "byRoute": by_route,
        "candidatesSha256": candidate_digest,
        "baselineContract": {
            "searchStateMutationAllowed": False,
            "selectorDecisionMutationAllowed": False,
            "baselineParentingAllowed": False,
            "baselineDeliveryReplacementAllowed": False,
            "defaultEnabled": False,
        },
        "authority": "exploratory-sidecar-only; no automatic artistic promotion",
        "policy": "independent route-prior draw; hard validity only; invalid consumes budget; no retry; never parent; never replace baseline delivery",
        "validCandidateIds": [c.id for c in valid],
    }

    (out_dir / "candidates.json").write_text(candidate_text)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report
