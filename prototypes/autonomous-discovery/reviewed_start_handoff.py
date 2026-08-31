from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

from core import Candidate, TIMES, evaluate_candidate, render_candidate_frame
from restart_route_authority import (
    EVIDENCE_AUTHORIZED_RESTART_ROUTES,
    restart_route_registry,
)

HANDOFF_VERSION = 1
AUTHORITY = "explicit-independent-artistic-selection-v1"
SIDECAR_MODE = "restart-sidecar-v1"


def phenotype_hash(cand: Candidate) -> str:
    h = hashlib.sha256()
    h.update(cand.route.encode("utf-8"))
    for t in TIMES:
        h.update(render_candidate_frame(cand, t).tobytes())
    return h.hexdigest()


def _resolved(manifest_path: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else manifest_path.parent / p


def load_reviewed_starts(
    manifest_path: Path,
    brief: Dict[str, object],
) -> Tuple[List[Candidate], Dict[str, object]]:
    """Load sidecar candidates selected by explicit external artistic authority.

    This function does not infer artistic quality. It verifies that the selected
    phenotypes came from the isolated restart sidecar, still hash exactly, remain
    hard-valid under the active brief, and cover every active route before handing
    them to `run_search_from_starts` as a new isolated lineage.
    """
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    if int(manifest.get("version", -1)) != HANDOFF_VERSION:
        raise ValueError("unsupported reviewed-start handoff version")
    if manifest.get("authority") != AUTHORITY:
        raise ValueError(
            f"reviewed-start handoff requires authority={AUTHORITY!r}; "
            "the runtime cannot infer artistic approval"
        )

    source_candidates_path = _resolved(manifest_path, str(manifest.get("sourceCandidates", "")))
    source_report_path = _resolved(manifest_path, str(manifest.get("sourceReport", "")))
    if not source_candidates_path.is_file() or not source_report_path.is_file():
        raise ValueError("reviewed-start handoff requires existing sourceCandidates and sourceReport files")

    source_report = json.loads(source_report_path.read_text())
    if source_report.get("mode") != SIDECAR_MODE:
        raise ValueError("reviewed starts must originate from restart-sidecar-v1")
    if source_report.get("authority") != "exploratory-sidecar-only; no automatic artistic promotion":
        raise ValueError("source sidecar authority contract drift")
    if source_report.get("evidenceAuthorizedRoutes") != list(EVIDENCE_AUTHORIZED_RESTART_ROUTES):
        raise ValueError("source sidecar evidence-authority route contract drift")
    expected_contract = {
        "searchStateMutationAllowed": False,
        "selectorDecisionMutationAllowed": False,
        "baselineParentingAllowed": False,
        "baselineDeliveryReplacementAllowed": False,
        "defaultEnabled": False,
    }
    if source_report.get("baselineContract") != expected_contract:
        raise ValueError("source sidecar baseline-isolation contract drift")

    candidate_bytes = source_candidates_path.read_bytes()
    observed_candidate_digest = hashlib.sha256(candidate_bytes).hexdigest()
    if observed_candidate_digest != source_report.get("candidatesSha256"):
        raise ValueError("source sidecar candidates.json digest mismatch")
    raw_candidates = json.loads(candidate_bytes.decode("utf-8"))
    if not isinstance(raw_candidates, list):
        raise ValueError("sourceCandidates must contain a candidate list")
    by_id = {}
    for record in raw_candidates:
        cid = record.get("id")
        if not cid or cid in by_id:
            raise ValueError("source candidate ids must be present and unique")
        by_id[cid] = record

    selected_ids = list(manifest.get("selectedCandidateIds") or [])
    if not selected_ids or len(selected_ids) != len(set(selected_ids)):
        raise ValueError("selectedCandidateIds must be a non-empty unique list")
    valid_source_ids = set(source_report.get("validCandidateIds") or [])
    active_routes = tuple(brief.get("routes") or ())
    if not active_routes:
        raise ValueError("brief must define active routes")
    unauthorized = [r for r in active_routes if r not in EVIDENCE_AUTHORIZED_RESTART_ROUTES]
    if unauthorized:
        raise ValueError(
            "reviewed restart lineage is limited to the frozen evidence-authorized route class; "
            f"unauthorized active route(s): {unauthorized}"
        )

    starts: List[Candidate] = []
    provenance = []
    # Orbit is deliberately not a baseline registry member. Temporarily expose
    # it only while verifying the selected phenotype(s), then restore registry.
    with restart_route_registry(active_routes):
        for cid in selected_ids:
            if cid not in by_id:
                raise ValueError(f"selected candidate {cid!r} is absent from sourceCandidates")
            if cid not in valid_source_ids:
                raise ValueError(f"selected candidate {cid!r} was not hard-valid in the source sidecar")
            record = by_id[cid]
            if record.get("stage") != "restart-sidecar":
                raise ValueError(f"selected candidate {cid!r} is not a restart-sidecar candidate")
            if record.get("parent_id") is not None or record.get("basin") != cid:
                raise ValueError(f"selected candidate {cid!r} violates independent-start provenance")
            route = str(record.get("route"))
            if route not in active_routes:
                raise ValueError(f"selected candidate {cid!r} uses inactive route {route!r}")

            cand = Candidate(cid, route, cid, dict(record["genome"]), None, "reviewed-start")
            observed_hash = phenotype_hash(cand)
            if observed_hash != record.get("phenotypeHash"):
                raise ValueError(f"selected candidate {cid!r} phenotype hash mismatch")
            evaluate_candidate(cand, brief)
            if not cand.checks.get("valid", False):
                raise ValueError(f"selected candidate {cid!r} is no longer hard-valid under the active brief")
            cand.reviews.append(
                {
                    "source": "reviewed-start-handoff",
                    "authority": AUTHORITY,
                    "sourceMode": SIDECAR_MODE,
                    "sourceSidecarMasterSeed": source_report.get("masterSeed"),
                    "sourcePhenotypeHash": observed_hash,
                    "sourceCandidatesSha256": observed_candidate_digest,
                    "automaticPromotion": False,
                }
            )
            starts.append(cand)
            provenance.append(
                {
                    "candidateId": cid,
                    "route": route,
                    "phenotypeHash": observed_hash,
                }
            )

    represented = {c.route for c in starts}
    missing = [r for r in active_routes if r not in represented]
    if missing:
        raise ValueError(
            "explicit reviewed starts must preserve route exposure; "
            f"missing active route(s): {missing}"
        )

    receipt: Dict[str, object] = {
        "version": HANDOFF_VERSION,
        "authority": AUTHORITY,
        "sourceMode": SIDECAR_MODE,
        "sourceSidecarMasterSeed": source_report.get("masterSeed"),
        "sourceCandidatesSha256": observed_candidate_digest,
        "evidenceAuthorizedRoutes": list(EVIDENCE_AUTHORIZED_RESTART_ROUTES),
        "selectedCandidateIds": selected_ids,
        "selected": provenance,
        "activeRoutes": list(active_routes),
        "routeExposurePreserved": True,
        "automaticPromotion": False,
        "newIsolatedLineage": True,
        "sourceCandidates": str(source_candidates_path),
        "sourceReport": str(source_report_path),
    }
    if manifest.get("selectionNote") is not None:
        receipt["selectionNote"] = str(manifest["selectionNote"])
    return starts, receipt


def run_reviewed_start_lineage(
    manifest_path: Path,
    brief: Dict[str, object],
    seed: int,
    out_dir: Path,
    selector=None,
):
    """Verify an explicit handoff and run one new isolated search lineage.

    Experimental route registration is scoped to this opt-in operation. Ordinary
    baseline processes remain unchanged before and after the call.
    """
    active_routes = tuple(brief.get("routes") or ())
    if not active_routes:
        raise ValueError("brief must define active routes")

    from search_engine import run_search_from_starts

    out_dir = Path(out_dir)
    with restart_route_registry(active_routes):
        starts, receipt = load_reviewed_starts(Path(manifest_path), brief)
        _, report = run_search_from_starts(brief, int(seed), out_dir, starts, selector)
        (out_dir / "reviewed_start_handoff.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        )
    return report, receipt
