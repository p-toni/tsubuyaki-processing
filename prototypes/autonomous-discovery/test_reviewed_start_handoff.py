from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import restart_sidecar
from reviewed_start_handoff import AUTHORITY, load_reviewed_starts
from search_engine import run_search_from_starts


def _brief(routes=("recurrence",)):
    return {
        "name": "reviewed-start-handoff-test",
        "artistic_intent": "test only",
        "routes": list(routes),
        "bbox_target": [0.55, 0.82],
        "starts_per_route": 1,
        "explore_per_basin": 1,
        "roundA_per_survivor": 1,
        "total_extra_budget": 2,
        "mutation_portfolio": "native-spectral-50-50-v1",
    }


def _make_sidecar(tmp_path: Path, routes=("recurrence",), seed=881039):
    brief = _brief(routes)
    root = tmp_path / "sidecar"
    report = restart_sidecar.generate_restart_sidecar(
        brief, seed, root, attempts_per_route=4
    )
    for route in routes:
        assert report["byRoute"][route]["validCandidateIds"], (route, report)
    return brief, root, report


def _manifest(tmp_path: Path, sidecar_root: Path, selected_ids, authority=AUTHORITY):
    path = tmp_path / "handoff.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "authority": authority,
                "sourceCandidates": str(sidecar_root / "candidates.json"),
                "sourceReport": str(sidecar_root / "report.json"),
                "selectedCandidateIds": list(selected_ids),
                "selectionNote": "explicit test selection",
            },
            indent=2,
        )
        + "\n"
    )
    return path


def test_reviewed_sidecar_start_creates_new_lineage_with_persistent_provenance(tmp_path):
    brief, root, report = _make_sidecar(tmp_path)
    cid = report["byRoute"]["recurrence"]["validCandidateIds"][0]
    manifest = _manifest(tmp_path, root, [cid])

    starts, receipt = load_reviewed_starts(manifest, brief)
    assert len(starts) == 1
    assert receipt["automaticPromotion"] is False
    assert receipt["newIsolatedLineage"] is True
    assert receipt["routeExposurePreserved"] is True
    assert receipt["sourceCandidatesSha256"] == report["candidatesSha256"]

    out = tmp_path / "lineage"
    state, _ = run_search_from_starts(brief, 991003, out, starts)
    source = state.candidates[cid]
    assert source.stage == "reviewed-start"
    assert source.parent_id is None
    assert source.basin == cid
    assert source.reviews == [
        {
            "source": "reviewed-start-handoff",
            "authority": AUTHORITY,
            "sourceMode": "restart-sidecar-v1",
            "sourceSidecarMasterSeed": report["masterSeed"],
            "sourcePhenotypeHash": receipt["selected"][0]["phenotypeHash"],
            "sourceCandidatesSha256": report["candidatesSha256"],
            "automaticPromotion": False,
        }
    ]
    persisted = json.loads((out / "search_state.json").read_text())
    assert persisted["candidates"][cid]["reviews"] == source.reviews


def test_handoff_rejects_fake_authority(tmp_path):
    brief, root, report = _make_sidecar(tmp_path)
    cid = report["byRoute"]["recurrence"]["validCandidateIds"][0]
    manifest = _manifest(tmp_path, root, [cid], authority="automatic-proxy-promotion")
    with pytest.raises(ValueError, match="requires authority"):
        load_reviewed_starts(manifest, brief)


def test_handoff_rejects_tampered_candidate_file_digest(tmp_path):
    brief, root, report = _make_sidecar(tmp_path)
    cid = report["byRoute"]["recurrence"]["validCandidateIds"][0]
    manifest = _manifest(tmp_path, root, [cid])
    with (root / "candidates.json").open("a") as f:
        f.write(" \n")
    with pytest.raises(ValueError, match="candidates.json digest mismatch"):
        load_reviewed_starts(manifest, brief)


def test_handoff_rejects_stale_phenotype_even_if_record_digest_is_rebound(tmp_path):
    brief, root, report = _make_sidecar(tmp_path)
    cid = report["byRoute"]["recurrence"]["validCandidateIds"][0]
    manifest = _manifest(tmp_path, root, [cid])

    candidates_path = root / "candidates.json"
    records = json.loads(candidates_path.read_text())
    record = next(x for x in records if x["id"] == cid)
    record["genome"]["alpha"] = 1
    text = json.dumps(records, indent=2, sort_keys=True) + "\n"
    candidates_path.write_text(text)

    report_path = root / "report.json"
    rebound = json.loads(report_path.read_text())
    rebound["candidatesSha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    report_path.write_text(json.dumps(rebound, indent=2, sort_keys=True) + "\n")

    with pytest.raises(ValueError, match="phenotype hash mismatch"):
        load_reviewed_starts(manifest, brief)


def test_handoff_preserves_active_route_exposure(tmp_path):
    brief, root, report = _make_sidecar(tmp_path, routes=("recurrence", "orbit"), seed=881057)
    recurrence_only = report["byRoute"]["recurrence"]["validCandidateIds"][0]
    manifest = _manifest(tmp_path, root, [recurrence_only])
    with pytest.raises(ValueError, match="missing active route"):
        load_reviewed_starts(manifest, brief)


def test_handoff_rejects_source_candidate_not_marked_valid(tmp_path):
    brief, root, report = _make_sidecar(tmp_path)
    cid = report["byRoute"]["recurrence"]["validCandidateIds"][0]
    manifest = _manifest(tmp_path, root, [cid])
    source_report = json.loads((root / "report.json").read_text())
    source_report["validCandidateIds"] = [x for x in source_report["validCandidateIds"] if x != cid]
    (root / "report.json").write_text(json.dumps(source_report, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="was not hard-valid"):
        load_reviewed_starts(manifest, brief)
