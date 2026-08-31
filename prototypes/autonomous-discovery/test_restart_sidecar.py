from __future__ import annotations

import json
from pathlib import Path

import restart_sidecar as sidecar
from search_engine import run_search


BASELINE_FILES = (
    "report.json",
    "search_state.json",
    "stage1_representatives.png",
    "stage2_survivors.png",
    "finalists.png",
    "winner_timeline.png",
)


def _brief(route="recurrence"):
    return {
        "name": "restart-sidecar-test",
        "artistic_intent": "test only",
        "routes": [route],
        "bbox_target": [0.55, 0.82],
        "starts_per_route": 1,
        "explore_per_basin": 1,
        "roundA_per_survivor": 1,
        "total_extra_budget": 1,
        "mutation_portfolio": "native-spectral-50-50-v1",
    }


def _snapshot(root: Path):
    return {name: (root / name).read_bytes() for name in BASELINE_FILES}


def test_sidecar_is_post_search_and_baseline_artifacts_are_byte_identical(tmp_path):
    brief = _brief()
    baseline = tmp_path / "baseline"
    with_sidecar = tmp_path / "with-sidecar"

    run_search(brief, 880021, baseline)
    run_search(brief, 880021, with_sidecar)
    before = _snapshot(with_sidecar)

    report = sidecar.generate_restart_sidecar(
        brief,
        880021,
        with_sidecar / "restart_sidecar",
        attempts_per_route=4,
    )

    assert _snapshot(baseline) == before == _snapshot(with_sidecar)
    assert report["baselineContract"] == {
        "searchStateMutationAllowed": False,
        "selectorDecisionMutationAllowed": False,
        "baselineParentingAllowed": False,
        "baselineDeliveryReplacementAllowed": False,
        "defaultEnabled": False,
    }
    assert report["attemptedCandidates"] == 4
    assert report["eligibleRoutes"] == ["recurrence"]


def test_sidecar_generation_is_deterministic_and_candidates_never_parent(tmp_path):
    brief = _brief()
    a = tmp_path / "a"
    b = tmp_path / "b"

    ra = sidecar.generate_restart_sidecar(brief, 880039, a, attempts_per_route=4)
    rb = sidecar.generate_restart_sidecar(brief, 880039, b, attempts_per_route=4)

    assert ra == rb
    assert (a / "report.json").read_bytes() == (b / "report.json").read_bytes()
    assert (a / "candidates.json").read_bytes() == (b / "candidates.json").read_bytes()

    candidates = json.loads((a / "candidates.json").read_text())
    assert len(candidates) == 4
    assert all(len(c["phenotypeHash"]) == 64 for c in candidates)
    for cand in candidates:
        assert cand["parent_id"] is None
        assert cand["basin"] == cand["id"]
        assert cand["stage"] == "restart-sidecar"
        assert cand["checks"]["generationOperator"] == "restart-sidecar"
        assert cand["checks"]["mayEnterBaselineSearch"] is False
        assert cand["checks"]["mayParentBaselineSearch"] is False
        assert cand["checks"]["mayReplaceBaselineDelivery"] is False


def test_sidecar_excludes_non_intrinsic_1d_routes(tmp_path):
    report = sidecar.generate_restart_sidecar(
        _brief("family"),
        880057,
        tmp_path / "sidecar",
        attempts_per_route=4,
    )

    assert report["eligibleRoutes"] == []
    assert report["attemptedCandidates"] == 0
    assert report["validCandidates"] == 0
    assert json.loads((tmp_path / "sidecar" / "candidates.json").read_text()) == []
    assert not (tmp_path / "sidecar" / "contact_sheet.png").exists()


def test_invalid_restart_consumes_budget_without_retry(tmp_path, monkeypatch):
    def mark_invalid(cand, brief):
        cand.checks = {"valid": False, "failureModes": ["forced test invalid"]}
        cand.features = {}
        cand.score = -1e9
        return cand

    monkeypatch.setattr(sidecar, "evaluate_candidate", mark_invalid)
    report = sidecar.generate_restart_sidecar(
        _brief(),
        880073,
        tmp_path / "sidecar",
        attempts_per_route=3,
    )

    assert report["attemptedCandidates"] == 3
    assert report["validCandidates"] == 0
    assert report["byRoute"]["recurrence"]["attempted"] == 3
    assert report["byRoute"]["recurrence"]["valid"] == 0
    candidates = json.loads((tmp_path / "sidecar" / "candidates.json").read_text())
    assert len(candidates) == 3
