from route_allocation_policy import *

R = ("recurrence", "orbit", "family", "sheet", "filament")


def test_prior_cannot_zero_probe_route():
    p = initial_probe_plan(R, probe_budget=10, prior_scores={"orbit": 100, "sheet": 50})
    assert sum(p.allocation.values()) == 10
    assert all(p.allocation[r] >= 1 for r in R)
    assert p.hard_excluded_routes == ()
    assert not p.narrowing_authorized


def test_same_model_drop_is_advisory_only():
    e = [RouteEvidence("family", "drop", "same-model", "judge-a")]
    s = resolve_screen(R, e)
    assert s["family"].status == "defer"
    p = deepening_plan(R, remaining_budget=15, evidence=e, prior_scores={"orbit": 10})
    assert "family" in p.active_routes
    assert p.allocation["family"] >= 1
    assert not p.narrowing_authorized


def test_low_confidence_human_cannot_drop():
    e = [RouteEvidence("sheet", "drop", "human", "toni", confidence="low")]
    assert resolve_screen(R, e)["sheet"].status == "defer"


def test_positive_only_keep_focuses_extras_without_pruning_omissions():
    e = [RouteEvidence("orbit", "keep", "human", "toni")]
    p = deepening_plan(R, remaining_budget=15, evidence=e, prior_scores={"family": 100})
    assert not p.narrowing_authorized
    assert set(p.active_routes) == set(R)
    assert p.hard_excluded_routes == ()
    assert p.status == "incomplete-screen-positive-focus"
    assert p.allocation["orbit"] == 11
    assert all(p.allocation[r] == 1 for r in R if r != "orbit")


def test_partial_authoritative_screen_fails_broad_but_focuses_keep():
    e = [
        RouteEvidence("orbit", "keep", "human", "toni"),
        RouteEvidence("sheet", "drop", "human", "toni"),
    ]
    p = deepening_plan(R, remaining_budget=12, evidence=e, prior_scores={"family": 100, "recurrence": 8})
    assert not p.narrowing_authorized
    assert "sheet" not in p.active_routes
    assert set(p.active_routes) == set(R) - {"sheet"}
    assert p.status == "incomplete-screen-positive-focus"
    assert p.allocation["orbit"] == 9
    assert all(p.allocation[r] == 1 for r in p.active_routes if r != "orbit")


def test_complete_authoritative_screen_can_narrow():
    e = [
        RouteEvidence("recurrence", "keep", "human", "toni"),
        RouteEvidence("orbit", "drop", "human", "toni"),
        RouteEvidence("family", "keep", "human", "toni"),
        RouteEvidence("sheet", "drop", "human", "toni"),
        RouteEvidence("filament", "drop", "human", "toni"),
    ]
    p = deepening_plan(R, remaining_budget=15, evidence=e, prior_scores={"family": 10, "recurrence": 9})
    assert p.narrowing_authorized
    assert p.active_routes == ("recurrence", "family")
    assert set(p.hard_excluded_routes) == {"orbit", "sheet", "filament"}
    assert sum(p.allocation.values()) == 15


def test_conflicting_independent_evidence_defers():
    e = [
        RouteEvidence("orbit", "keep", "human", "toni"),
        RouteEvidence("orbit", "drop", "independent-model", "judge-2"),
    ]
    assert resolve_screen(R, e)["orbit"].status == "defer"


def test_budget_failure_does_not_silently_topk():
    p = deepening_plan(R, remaining_budget=3, evidence=(), prior_scores={"orbit": 100})
    assert not p.narrowing_authorized
    assert p.status.startswith("insufficient-budget-for-safe-broadening")
    assert set(p.active_routes) == set(R)
    assert all(v == 0 for v in p.allocation.values())


def test_all_dropped_fails_broad_not_empty():
    e = [RouteEvidence(r, "drop", "human", "toni") for r in R]
    p = deepening_plan(R, remaining_budget=10, evidence=e)
    assert not p.narrowing_authorized
    assert set(p.active_routes) == set(R)
    assert p.hard_excluded_routes == ()
    assert all(p.allocation[r] >= 1 for r in R)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(t.__name__, "PASS")
