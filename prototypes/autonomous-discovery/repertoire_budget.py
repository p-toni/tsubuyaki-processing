"""Authority boundary between route-safe and repertoire allocation.

This module intentionally does *not* choose an inner allocation policy. It only
validates the envelope any future quality-diversity allocator must obey:

1. `route_allocation_policy.BudgetPlan` owns the amount of compute per route.
2. repertoire allocation may distribute that amount only among archived entries
   belonging to the same active route.
3. no inner novelty/uncertainty signal can transfer budget across routes, revive a
   hard-dropped route, or silently leave an active route's assigned budget unused.

Keeping this as a validator rather than a policy lets future allocator experiments
change their ranking logic without weakening the existing representation-safety
contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from repertoire_archive import RepertoireArchive
from route_allocation_policy import BudgetPlan


@dataclass(frozen=True)
class ValidatedInnerAllocation:
    """Canonical allocation proven to conserve the outer route budget."""

    units_by_candidate: tuple[tuple[str, int], ...]
    spent_by_route: tuple[tuple[str, int], ...]
    outer_budget_by_route: tuple[tuple[str, int], ...]
    total_units: int

    def candidate_units(self) -> dict[str, int]:
        return dict(self.units_by_candidate)

    def route_spend(self) -> dict[str, int]:
        return dict(self.spent_by_route)


@dataclass(frozen=True)
class BasinConcentration:
    """Diagnostic allocation concentration after route-budget validation.

    A single basin lineage may legitimately occupy multiple phenotype niches. This
    summary aggregates those entries back to the route+basin level so an allocator
    experiment cannot mistake many niche entries from one lineage for many
    independent mathematical basins. It reports concentration only; it imposes no
    cap or ranking policy.
    """

    units_by_route_basin: tuple[tuple[str, str, int], ...]
    distinct_funded_basins_by_route: tuple[tuple[str, int], ...]
    max_basin_share_by_route: tuple[tuple[str, float], ...]

    def maximum_share(self) -> dict[str, float]:
        return dict(self.max_basin_share_by_route)


def _checked_units(candidate_id: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"allocation for {candidate_id!r} must be an integer")
    if value < 0:
        raise ValueError(f"allocation for {candidate_id!r} must be >= 0")
    return value


def validate_inner_allocation(
    outer: BudgetPlan,
    archive: RepertoireArchive,
    units_by_candidate: Mapping[str, int],
) -> ValidatedInnerAllocation:
    """Fail closed unless an inner allocation exactly preserves outer authority.

    Zero-unit entries are allowed in the input for convenient deterministic policy
    output, but are omitted from the canonical result. Every positive allocation
    must name an entry already admitted to the repertoire.
    """

    active = tuple(outer.active_routes)
    if len(set(active)) != len(active):
        raise ValueError("outer budget contains duplicate active routes")
    active_set = set(active)
    dropped = set(outer.hard_excluded_routes)
    if active_set & dropped:
        raise ValueError("outer budget marks a route both active and hard-excluded")

    outer_budget: dict[str, int] = {}
    for route in active:
        raw = outer.allocation.get(route, 0)
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
            raise ValueError(f"outer budget for route {route!r} must be a nonnegative integer")
        outer_budget[route] = raw

    unexpected_outer = set(outer.allocation) - active_set
    if unexpected_outer:
        raise ValueError(f"outer allocation names inactive route(s): {sorted(unexpected_outer)}")

    spent = {route: 0 for route in active}
    canonical: list[tuple[str, int]] = []
    for candidate_id, raw_units in units_by_candidate.items():
        units = _checked_units(candidate_id, raw_units)
        if units == 0:
            continue
        try:
            entry = archive.get(candidate_id)
        except KeyError as exc:
            raise ValueError(f"inner allocation names unknown archive entry {candidate_id!r}") from exc

        if entry.route in dropped:
            raise ValueError(f"inner allocation attempts to revive hard-dropped route {entry.route!r}")
        if entry.route not in active_set:
            raise ValueError(
                f"inner allocation entry {candidate_id!r} belongs to inactive route {entry.route!r}"
            )
        spent[entry.route] += units
        canonical.append((candidate_id, units))

    mismatches = {
        route: (outer_budget[route], spent[route])
        for route in active
        if spent[route] != outer_budget[route]
    }
    if mismatches:
        detail = ", ".join(
            f"{route}: outer={expected}, inner={actual}"
            for route, (expected, actual) in sorted(mismatches.items())
        )
        raise ValueError(f"inner allocation violates per-route budget conservation: {detail}")

    return ValidatedInnerAllocation(
        units_by_candidate=tuple(sorted(canonical)),
        spent_by_route=tuple(sorted(spent.items())),
        outer_budget_by_route=tuple(sorted(outer_budget.items())),
        total_units=sum(spent.values()),
    )


def summarize_basin_concentration(
    allocation: ValidatedInnerAllocation,
    archive: RepertoireArchive,
) -> BasinConcentration:
    """Aggregate a validated candidate allocation by explicit basin lineage.

    This is intentionally downstream of `validate_inner_allocation`: concentration
    diagnostics must never become an alternate route-budget authority.
    """

    spend_by_route = allocation.route_spend()
    route_basin_units: dict[tuple[str, str], int] = {}
    for candidate_id, units in allocation.units_by_candidate:
        entry = archive.get(candidate_id)
        key = (entry.route, entry.basin_id)
        route_basin_units[key] = route_basin_units.get(key, 0) + units

    distinct: dict[str, int] = {}
    maximum_share: dict[str, float] = {}
    for route, route_units in spend_by_route.items():
        basin_units = [
            units
            for (entry_route, _basin), units in route_basin_units.items()
            if entry_route == route and units > 0
        ]
        distinct[route] = len(basin_units)
        maximum_share[route] = max(basin_units, default=0) / route_units if route_units > 0 else 0.0

    return BasinConcentration(
        units_by_route_basin=tuple(
            (route, basin, units)
            for (route, basin), units in sorted(route_basin_units.items())
        ),
        distinct_funded_basins_by_route=tuple(sorted(distinct.items())),
        max_basin_share_by_route=tuple(sorted(maximum_share.items())),
    )
