from __future__ import annotations

import pytest

from phenotype_descriptors import PhenotypeDescriptor
from repertoire_archive import ArchiveEntry, RepertoireArchive
from repertoire_budget import validate_inner_allocation
from route_allocation_policy import BudgetPlan


def _descriptor(anisotropy=0.2):
    return PhenotypeDescriptor(
        intrinsic_dimension=1,
        anisotropy=anisotropy,
        central_void=0.2,
        radial_cv=0.3,
        angular_coverage=0.8,
        shape_motion=0.2,
    )


def _archive():
    archive = RepertoireArchive(max_basins_per_route=2)
    for entry in (
        ArchiveEntry("F1", "family", "family-a", _descriptor()),
        ArchiveEntry("F2", "family", "family-b", _descriptor()),
        ArchiveEntry("S1", "sheet", "sheet-a", _descriptor()),
        ArchiveEntry("R1", "recurrence", "recurrence-a", _descriptor()),
    ):
        assert archive.insert(entry).accepted
    return archive


def _outer():
    return BudgetPlan(
        stage="deepen",
        allocation={"family": 3, "sheet": 2},
        active_routes=("family", "sheet"),
        hard_excluded_routes=("orbit",),
        status="incomplete-screen-positive-focus",
        narrowing_authorized=False,
    )


def test_inner_allocation_exactly_conserves_each_outer_route_budget():
    result = validate_inner_allocation(
        _outer(),
        _archive(),
        {"F1": 2, "F2": 1, "S1": 2},
    )
    assert result.route_spend() == {"family": 3, "sheet": 2}
    assert result.total_units == 5


def test_inner_allocation_cannot_transfer_compute_between_routes():
    with pytest.raises(ValueError, match="per-route budget conservation"):
        validate_inner_allocation(
            _outer(),
            _archive(),
            {"F1": 1, "S1": 4},  # same total, wrong route ownership
        )


def test_inner_allocation_cannot_spend_on_inactive_or_unknown_entries():
    with pytest.raises(ValueError, match="inactive route"):
        validate_inner_allocation(
            _outer(),
            _archive(),
            {"F1": 3, "S1": 2, "R1": 1},
        )

    with pytest.raises(ValueError, match="unknown archive entry"):
        validate_inner_allocation(
            _outer(),
            _archive(),
            {"F1": 3, "S1": 2, "MISSING": 1},
        )


def test_inner_allocation_cannot_silently_leave_a_route_budget_unspent():
    with pytest.raises(ValueError, match="per-route budget conservation"):
        validate_inner_allocation(
            _outer(),
            _archive(),
            {"F1": 3, "S1": 1},
        )


def test_inner_allocation_rejects_invalid_outer_contracts():
    invalid = BudgetPlan(
        stage="deepen",
        allocation={"family": 3, "orbit": 1},
        active_routes=("family",),
        hard_excluded_routes=("orbit",),
        status="invalid-fixture",
        narrowing_authorized=False,
    )
    with pytest.raises(ValueError, match="inactive route"):
        validate_inner_allocation(invalid, _archive(), {"F1": 3})
