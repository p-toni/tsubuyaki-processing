"""Review-gated repertoire archive for quality-diversity search.

The archive preserves phenotype niches without pretending the existing
`diagnostic_score` is artistic quality. A candidate may enter an empty capacity
slot automatically, but any replacement of an incumbent requires an explicit
caller decision from an authorized selector/reviewer.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Mapping

from phenotype_descriptors import NicheKey, PhenotypeDescriptor, niche_key


@dataclass(frozen=True)
class ArchiveEntry:
    candidate_id: str
    route: str
    basin_id: str
    descriptor: PhenotypeDescriptor
    parent_id: str | None = None
    stage: str = ""

    @property
    def niche(self) -> NicheKey:
        return niche_key(self.descriptor)

    def to_json(self) -> dict[str, object]:
        payload = asdict(self)
        payload["niche"] = self.niche.to_json()
        return payload


@dataclass(frozen=True)
class InsertDecision:
    status: str
    candidate_id: str
    niche: NicheKey
    route: str
    review_with: tuple[str, ...] = ()
    reason: str = ""

    @property
    def accepted(self) -> bool:
        return self.status == "accepted"

    @property
    def review_required(self) -> bool:
        return self.status == "review-required"

    def to_json(self) -> dict[str, object]:
        return {
            "status": self.status,
            "candidateId": self.candidate_id,
            "niche": self.niche.to_json(),
            "route": self.route,
            "reviewWith": list(self.review_with),
            "reason": self.reason,
        }


class RepertoireArchive:
    """Sparse phenotype archive retaining bounded basin diversity per route/cell.

    Cells are phenotype-defined and therefore representation-agnostic. Within a
    cell, entries are route-stratified so one mathematical representation cannot
    erase all evidence from another merely by occupying the same phenotype niche.
    The scheduler still owns the non-zero route exposure guarantee.
    """

    def __init__(self, *, max_basins_per_route: int = 2):
        if max_basins_per_route < 1:
            raise ValueError("max_basins_per_route must be >= 1")
        self.max_basins_per_route = int(max_basins_per_route)
        self._cells: dict[NicheKey, dict[str, list[ArchiveEntry]]] = {}
        self._candidate_locations: dict[str, tuple[NicheKey, str]] = {}

    def __len__(self) -> int:
        return len(self._candidate_locations)

    @property
    def cell_count(self) -> int:
        return len(self._cells)

    def niches(self) -> tuple[NicheKey, ...]:
        return tuple(sorted(self._cells))

    def entries(self) -> tuple[ArchiveEntry, ...]:
        out: list[ArchiveEntry] = []
        for niche in self.niches():
            for route in sorted(self._cells[niche]):
                out.extend(self._cells[niche][route])
        return tuple(out)

    def cell_entries(self, niche: NicheKey, route: str | None = None) -> tuple[ArchiveEntry, ...]:
        routes = self._cells.get(niche, {})
        if route is not None:
            return tuple(routes.get(route, ()))
        out: list[ArchiveEntry] = []
        for route_name in sorted(routes):
            out.extend(routes[route_name])
        return tuple(out)

    def get(self, candidate_id: str) -> ArchiveEntry:
        try:
            niche, route = self._candidate_locations[candidate_id]
        except KeyError as exc:
            raise KeyError(f"candidate {candidate_id!r} is not in the repertoire") from exc
        for entry in self._cells[niche][route]:
            if entry.candidate_id == candidate_id:
                return entry
        raise AssertionError("repertoire candidate index is inconsistent")

    def propose(self, entry: ArchiveEntry) -> InsertDecision:
        """Describe insertion without mutating the archive."""
        if entry.candidate_id in self._candidate_locations:
            raise ValueError(f"candidate {entry.candidate_id!r} already exists in repertoire")
        niche = entry.niche
        bucket = self._cells.get(niche, {}).get(entry.route, [])
        same_basin = tuple(e.candidate_id for e in bucket if e.basin_id == entry.basin_id)
        if same_basin:
            return InsertDecision(
                "review-required",
                entry.candidate_id,
                niche,
                entry.route,
                same_basin,
                "same basin already occupies this phenotype niche",
            )
        if len(bucket) < self.max_basins_per_route:
            return InsertDecision(
                "accepted",
                entry.candidate_id,
                niche,
                entry.route,
                (),
                "unused basin-capacity slot",
            )
        return InsertDecision(
            "review-required",
            entry.candidate_id,
            niche,
            entry.route,
            tuple(e.candidate_id for e in bucket),
            "route-stratified niche capacity is full",
        )

    def insert(self, entry: ArchiveEntry) -> InsertDecision:
        """Insert only when no incumbent replacement is required."""
        decision = self.propose(entry)
        if not decision.accepted:
            return decision
        self._add(entry)
        return decision

    def replace(self, incumbent_id: str, challenger: ArchiveEntry) -> None:
        """Apply an explicit reviewer/selector replacement decision.

        This method deliberately has no score argument and makes no comparison.
        The caller is responsible for having authority to choose the challenger.
        """
        incumbent = self.get(incumbent_id)
        if incumbent.niche != challenger.niche:
            raise ValueError("replacement must stay within the same phenotype niche")
        if incumbent.route != challenger.route:
            raise ValueError("replacement must stay within the same route stratum")
        if challenger.candidate_id in self._candidate_locations:
            raise ValueError(f"challenger {challenger.candidate_id!r} already exists in repertoire")
        self.remove(incumbent_id)
        self._add(challenger)

    def remove(self, candidate_id: str) -> ArchiveEntry:
        entry = self.get(candidate_id)
        niche, route = self._candidate_locations.pop(candidate_id)
        bucket = self._cells[niche][route]
        bucket.remove(entry)
        if not bucket:
            del self._cells[niche][route]
        if not self._cells[niche]:
            del self._cells[niche]
        return entry

    def _add(self, entry: ArchiveEntry) -> None:
        niche = entry.niche
        bucket = self._cells.setdefault(niche, {}).setdefault(entry.route, [])
        if len(bucket) >= self.max_basins_per_route:
            raise AssertionError("cannot add beyond route-stratified niche capacity")
        bucket.append(entry)
        bucket.sort(key=lambda e: (e.basin_id, e.candidate_id))
        self._candidate_locations[entry.candidate_id] = (niche, entry.route)

    def summary(self) -> dict[str, object]:
        route_counts: dict[str, int] = {}
        basin_ids = set()
        for entry in self.entries():
            route_counts[entry.route] = route_counts.get(entry.route, 0) + 1
            basin_ids.add((entry.route, entry.basin_id))
        return {
            "cells": self.cell_count,
            "entries": len(self),
            "distinctRouteBasins": len(basin_ids),
            "entriesByRoute": dict(sorted(route_counts.items())),
            "maxBasinsPerRoutePerNiche": self.max_basins_per_route,
            "automaticReplacement": False,
        }

    def to_json(self) -> dict[str, object]:
        return {
            "summary": self.summary(),
            "entries": [entry.to_json() for entry in self.entries()],
        }
