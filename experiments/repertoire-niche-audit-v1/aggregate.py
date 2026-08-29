#!/usr/bin/env python3
"""Fail-closed reducer for repertoire-niche-audit-v1."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from run import EXPECTED_CANDIDATES, HOLDOUT_SEEDS, ROUTE_ORDER, STARTS_PER_ROUTE

EXPECTED_BLOCKS = len(HOLDOUT_SEEDS) * len(ROUTE_ORDER)
AXES = ("anisotropy", "central_void", "shape_motion")
PROXIES = ("diagnosticScore", "occupancyMean", "dominantBBoxSpan", "centeringError")


def _load_blocks(root: Path) -> list[dict]:
    blocks = []
    for path in sorted(root.rglob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception as exc:
            raise AssertionError(f"invalid JSON artifact {path}: {exc}") from exc
        if isinstance(data, dict) and "records" in data and "route" in data and "seed" in data:
            blocks.append(data)
    return blocks


def _average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        average = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = average
        i = j
    return ranks


def _pearson(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("correlation vectors must be equal and non-empty")
    ma = statistics.fmean(a)
    mb = statistics.fmean(b)
    da = [x - ma for x in a]
    db = [y - mb for y in b]
    va = sum(x * x for x in da)
    vb = sum(y * y for y in db)
    if va <= 1e-18 or vb <= 1e-18:
        return 0.0
    return sum(x * y for x, y in zip(da, db)) / math.sqrt(va * vb)


def _spearman(a: list[float], b: list[float]) -> float:
    return _pearson(_average_ranks(a), _average_ranks(b))


def _niche_tuple(record: dict) -> tuple[int, int, int, int, str]:
    niche = record["niche"]
    return (
        int(niche["intrinsic_dimension"]),
        int(niche["anisotropy_bin"]),
        int(niche["central_void_bin"]),
        int(niche["motion_bin"]),
        str(niche["version"]),
    )


def _niche_label(niche: tuple[int, int, int, int, str]) -> str:
    d, a, v, m, version = niche
    return f"{version}:d{d}-a{a}-v{v}-m{m}"


def _quantiles(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "q25": 0.0, "median": 0.0, "q75": 0.0, "max": 0.0}
    ordered = sorted(values)

    def q(fraction: float) -> float:
        idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * fraction))))
        return ordered[idx]

    return {
        "min": ordered[0],
        "q25": q(0.25),
        "median": statistics.median(ordered),
        "q75": q(0.75),
        "max": ordered[-1],
    }


def aggregate(results_dir: Path) -> dict:
    blocks = _load_blocks(results_dir)
    if len(blocks) != EXPECTED_BLOCKS:
        raise AssertionError(f"expected {EXPECTED_BLOCKS} route×seed blocks, found {len(blocks)}")

    seen = set()
    records = []
    for block in blocks:
        key = (block["route"], int(block["seed"]))
        if key in seen:
            raise AssertionError(f"duplicate block {key}")
        seen.add(key)
        if key[0] not in ROUTE_ORDER or key[1] not in HOLDOUT_SEEDS:
            raise AssertionError(f"out-of-contract block {key}")
        if block.get("freshSearchEvidence") is not False:
            raise AssertionError(f"block {key} is not marked consumed-only")
        if int(block.get("startsPerRoute", -1)) != STARTS_PER_ROUTE:
            raise AssertionError(f"block {key} candidate count contract drift")
        if len(block["records"]) != STARTS_PER_ROUTE:
            raise AssertionError(f"block {key} records drift")
        records.extend(block["records"])

    expected_keys = {(route, seed) for route in ROUTE_ORDER for seed in HOLDOUT_SEEDS}
    if seen != expected_keys:
        raise AssertionError("route×seed rectangle is incomplete")
    if len(records) != EXPECTED_CANDIDATES:
        raise AssertionError(f"expected {EXPECTED_CANDIDATES} candidates, found {len(records)}")
    if not all(record.get("hardValid") is True for record in records):
        raise AssertionError("audit population contains invalid candidate")

    route_niches: dict[str, set] = {route: set() for route in ROUTE_ORDER}
    niche_routes: dict[tuple, set[str]] = defaultdict(set)
    niche_route_counts: dict[tuple, Counter] = defaultdict(Counter)
    niche_counts = Counter()
    for record in records:
        niche = _niche_tuple(record)
        route = record["route"]
        route_niches[route].add(niche)
        niche_routes[niche].add(route)
        niche_route_counts[niche][route] += 1
        niche_counts[niche] += 1

    cross_route = [niche for niche, routes in niche_routes.items() if len(routes) >= 2]
    weighted_purity = sum(max(counts.values()) for counts in niche_route_counts.values()) / len(records)

    correlations = {}
    max_abs_leakage = 0.0
    for axis in AXES:
        correlations[axis] = {}
        x = [float(record["descriptor"][axis]) for record in records]
        for proxy in PROXIES:
            if proxy == "diagnosticScore":
                y = [float(record["diagnosticScore"]) for record in records]
            else:
                y = [float(record["composition"][proxy]) for record in records]
            rho = _spearman(x, y)
            correlations[axis][proxy] = rho
            max_abs_leakage = max(max_abs_leakage, abs(rho))

    descriptor_fields = (
        "anisotropy", "central_void", "radial_cv", "angular_coverage", "shape_motion"
    )
    route_descriptor_ranges = {}
    for route in ROUTE_ORDER:
        subset = [record for record in records if record["route"] == route]
        route_descriptor_ranges[route] = {
            field: _quantiles([float(record["descriptor"][field]) for record in subset])
            for field in descriptor_fields
        }

    unique_per_route = {route: len(route_niches[route]) for route in ROUTE_ORDER}
    gates = {
        "completeValidPopulation": len(records) == EXPECTED_CANDIDATES,
        "everyRouteAtLeastTwoNiches": all(value >= 2 for value in unique_per_route.values()),
        "atLeastEightNichesOverall": len(niche_counts) >= 8,
        "atLeastTwoCrossRouteNiches": len(cross_route) >= 2,
        "noNearFitnessLeakage": max_abs_leakage < 0.90,
    }
    qualified = all(gates.values())

    occupancy_histogram = Counter(niche_counts.values())
    return {
        "version": 1,
        "decision": "NICHE_MAP_QUALIFIED" if qualified else "NICHE_MAP_NOT_QUALIFIED",
        "freshSearchEvidence": False,
        "population": {
            "masterSeeds": len(HOLDOUT_SEEDS),
            "routes": len(ROUTE_ORDER),
            "startsPerRoute": STARTS_PER_ROUTE,
            "candidates": len(records),
        },
        "gates": gates,
        "niches": {
            "occupied": len(niche_counts),
            "uniqueByRoute": unique_per_route,
            "crossRouteCount": len(cross_route),
            "crossRoute": {
                _niche_label(niche): sorted(niche_routes[niche]) for niche in sorted(cross_route)
            },
            "weightedDominantRoutePurity": weighted_purity,
            "occupancyByCell": {
                _niche_label(niche): niche_counts[niche] for niche in sorted(niche_counts)
            },
            "occupancyHistogram": {str(k): v for k, v in sorted(occupancy_histogram.items())},
        },
        "fitnessLeakage": {
            "spearman": correlations,
            "maxAbsolute": max_abs_leakage,
            "threshold": 0.90,
        },
        "descriptorRangesByRoute": route_descriptor_ranges,
        "failureDiscipline": "do not retune structural-v1 axes/bins on these 20 holdout seeds",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(Path(args.results_dir)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
