#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from orbit_representation import ORBIT_SPEC, check_orbit, register_orbit
from pairwise_selector import DimensionVote, PairwiseDecision, PairwiseSelector
from representation_capacity import run_capacity
from rng_streams import representation_rng


class AlwaysTie(PairwiseSelector):
    name = "always-tie-orbit-test"

    def compare(self, a, b, brief):
        return PairwiseDecision(
            a.id,
            b.id,
            "tie",
            "defer",
            (DimensionVote("test", "tie", "force tie"),),
            self.name,
        )


def main():
    register_orbit()
    import core

    brief = {
        "eligible_routes": ["recurrence", "sheet", "orbit"],
        "route_first": "recurrence",
        "bbox_target": [0.50, 0.84],
    }

    # Generic capacity runner can use orbit without modifying baseline generation semantics.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        s3, r3 = run_capacity(brief, 12345, td / "three", 3, AlwaysTie())
        assert r3["candidateCount"] == 9
        assert all(c["checks"]["valid"] for c in s3["archives"]["orbit"])
        assert r3["selectionStatus"] == "pending-route-frontiers"

        # Adding orbit cannot perturb existing representation archives.
        two = dict(brief)
        two["eligible_routes"] = ["recurrence", "sheet"]
        _, r2 = run_capacity(two, 12345, td / "two", 3, AlwaysTie())
        for route in ("recurrence", "sheet"):
            assert r2["routeArchiveHashes"][route] == r3["routeArchiveHashes"][route]

    # Healthy closed manifold has aperture + angular coverage and never uses occupancy as a gate.
    rng = representation_rng(999, "orbit", ORBIT_SPEC.version, "orbit-test")
    for _ in range(50):
        g = ORBIT_SPEC.seed(rng)
        checks = check_orbit(
            g,
            core.TIMES,
            lambda gg, t: ORBIT_SPEC.geometry(gg, t, core.W, core.H),
            core.W,
            core.H,
        )
        if checks["valid"]:
            break
    else:
        raise AssertionError("could not find a valid orbit seed")
    assert checks["diagnostics"]["occupancyUsedAsGate"] is False
    assert min(checks["diagnostics"]["angularCoverageByFrame"]) >= 0.88
    assert min(checks["diagnostics"]["apertureRadiusFractionByFrame"]) >= 0.055

    # Breaking periodic winding creates a visible seam and must fail closedness.
    broken = dict(g)
    broken["f2"] = 5.5
    bad = check_orbit(
        broken,
        core.TIMES,
        lambda gg, t: ORBIT_SPEC.geometry(gg, t, core.W, core.H),
        core.W,
        core.H,
    )
    assert not bad["valid"] and any("visible seam" in x for x in bad["failures"])

    # Collapsing one axis or over-denting the loop must destroy the aperture/topology contract.
    collapsed = dict(g)
    collapsed["sx"] = 0.08
    bad = check_orbit(
        collapsed,
        core.TIMES,
        lambda gg, t: ORBIT_SPEC.geometry(gg, t, core.W, core.H),
        core.W,
        core.H,
    )
    assert not bad["valid"]
    dented = dict(g)
    dented["dent"] = 1.1
    bad = check_orbit(
        dented,
        core.TIMES,
        lambda gg, t: ORBIT_SPEC.geometry(gg, t, core.W, core.H),
        core.W,
        core.H,
    )
    assert not bad["valid"] and any("aperture" in x for x in bad["failures"])

    print("orbit representation tests: PASS")


if __name__ == "__main__":
    main()
