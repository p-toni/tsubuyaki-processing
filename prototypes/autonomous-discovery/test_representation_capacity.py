#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from pairwise_selector import DimensionVote, PairwiseDecision, PairwiseSelector
from representation_capacity import run_capacity


class AlwaysTie(PairwiseSelector):
    name = "always-tie-test"

    def compare(self, a, b, brief):
        return PairwiseDecision(
            a.id,
            b.id,
            "tie",
            "defer",
            (DimensionVote("test", "tie", "force unresolved selection"),),
            self.name,
        )


def brief(routes):
    return {
        "name": "capacity-regression",
        "artistic_intent": "An ambiguous living mathematical form with coherent motion and non-generic structure.",
        "eligible_routes": list(routes),
        "route_first": "sheet" if "sheet" in routes else routes[0],
        "bbox_target": [0.50, 0.84],
    }


def genomes(state, route):
    return [c["genome"] for c in state["archives"][route]]


def main():
    routes = ["recurrence", "family", "sheet", "filament"]
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        # Archive generation is selector-independent.
        s1, r1 = run_capacity(brief(routes), 424242, td / "proxy", 3)
        s2, r2 = run_capacity(brief(routes), 424242, td / "tie", 3, AlwaysTie())
        assert r1["routeArchiveHashes"] == r2["routeArchiveHashes"]
        assert r1["candidateCount"] == 12
        assert r2["selectionStatus"] == "pending-route-frontiers"
        assert not r2["globalFrontier"]

        # Route order cannot perturb representation-local archives.
        reversed_routes = list(reversed(routes))
        s3, r3 = run_capacity(brief(reversed_routes), 424242, td / "reversed", 3)
        assert r1["routeArchiveHashes"] == r3["routeArchiveHashes"]

        # Adding/removing another representation cannot perturb shared routes.
        subset = ["recurrence", "sheet", "filament"]
        s4, _ = run_capacity(brief(subset), 424242, td / "subset", 3)
        for route in subset:
            assert genomes(s1, route) == genomes(s4, route)

        # Capacity candidates are independent starts, never descendants of selector winners.
        for route in routes:
            assert len(s1["archives"][route]) == 3
            assert all(c["parent_id"] is None for c in s1["archives"][route])
            assert all(c["stage"] == "capacity-start" for c in s1["archives"][route])
            assert all(c["checks"]["valid"] for c in s1["archives"][route])

        assert r1["generationDependsOnSelector"] is False
        assert r1["diagnosticScoreUsedForPromotion"] is False

    print("representation capacity tests: PASS")


if __name__ == "__main__":
    main()
