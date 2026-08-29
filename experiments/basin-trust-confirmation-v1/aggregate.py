#!/usr/bin/env python3
"""Fail-closed reducer for the fresh basin trust-region confirmation."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
SEEDS = (
    2003, 2011, 2017, 2027,
    2029, 2039, 2053, 2063,
    2069, 2081, 2083, 2087,
    2089, 2099, 2111, 2113,
    2129, 2131, 2137, 2141,
    2143, 2153, 2161, 2179,
    2203, 2207, 2213, 2221,
    2237, 2239, 2243, 2251,
)
REGIMES = ("same-basin", "identity-jump")
T_ONE_SIDED_95_DF31 = 1.695519


def _mean(values):
    values = list(values)
    if not values:
        raise AssertionError("cannot average empty values")
    return statistics.fmean(values)


def _load_blocks(results_dir: Path) -> dict[tuple[str, int], dict]:
    blocks = {}
    for path in sorted(results_dir.rglob("*.json")):
        data = json.loads(path.read_text())
        route = data.get("route")
        seed = data.get("seed")
        if route not in ROUTES or seed not in SEEDS:
            raise AssertionError(f"unexpected confirmation block {route=} {seed=} from {path}")
        key = (route, int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate confirmation block {key}")
        if data.get("confirmationSeed") is not True or data.get("freshSearchEvidence") is not True:
            raise AssertionError(f"non-fresh block entered confirmation reducer: {key}")
        if data.get("mechanismFrozen") is not True:
            raise AssertionError(f"unfrozen mechanism marker: {key}")
        blocks[key] = data

    expected = {(route, seed) for route in ROUTES for seed in SEEDS}
    missing = expected - set(blocks)
    extra = set(blocks) - expected
    if missing or extra:
        raise AssertionError(f"confirmation rectangle mismatch missing={sorted(missing)} extra={sorted(extra)}")
    return blocks


def _summary(values: list[float]) -> dict:
    n = len(values)
    if n != len(SEEDS):
        raise AssertionError(f"expected {len(SEEDS)} complete master-seed effects, got {n}")
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    se = sd / math.sqrt(n)
    lower = mean - T_ONE_SIDED_95_DF31 * se
    return {
        "n": n,
        "mean": mean,
        "median": statistics.median(values),
        "sd": sd,
        "se": se,
        "oneSided95LowerBound": lower,
    }


def reduce(results_dir: Path) -> dict:
    blocks = _load_blocks(results_dir)
    rows = []
    hard = {
        "sameRepresentativeForBothPolicies": True,
        "equalTwentyCandidateBudgets": True,
        "trustChampionFrozenDriftZero": True,
        "sameBasinTargetFrozenDriftZero": True,
        "identityJumpTargetCrossesIdentity": True,
        "frozenMechanismMarker": True,
    }

    for route in ROUTES:
        for seed in SEEDS:
            block = blocks[(route, seed)]
            if block.get("mechanismFrozen") is not True:
                hard["frozenMechanismMarker"] = False
            deltas = {}
            selected_ancestor = {}
            yields = {}
            for regime in REGIMES:
                rec = block["regimes"][regime]
                generic = rec["policies"]["generic"]
                trust = rec["policies"]["trust-region"]
                if generic["initialCandidate"] != trust["initialCandidate"]:
                    hard["sameRepresentativeForBothPolicies"] = False
                if generic["candidateCount"] != 20 or trust["candidateCount"] != 20:
                    hard["equalTwentyCandidateBudgets"] = False
                if trust["championFrozenDriftKeys"]:
                    hard["trustChampionFrozenDriftZero"] = False
                if regime == "same-basin" and rec["target"]["frozenDeltaKeysFromAncestor"]:
                    hard["sameBasinTargetFrozenDriftZero"] = False
                if regime == "identity-jump" and not rec["target"]["identityDeltaKeysFromAncestor"]:
                    hard["identityJumpTargetCrossesIdentity"] = False
                deltas[regime] = float(rec["deltaTrustMinusGeneric"])
                selected_ancestor[regime] = bool(rec["discovery"]["selectedAncestorBasin"])
                yields[regime] = {
                    "generic": float(generic["validYield"]),
                    "trust": float(trust["validYield"]),
                }

            rows.append({
                "route": route,
                "seed": seed,
                "sameBasinDelta": deltas["same-basin"],
                "identityJumpDelta": deltas["identity-jump"],
                "interaction": deltas["same-basin"] - deltas["identity-jump"],
                "sameBasinSelectedAncestor": selected_ancestor["same-basin"],
                "identityJumpSelectedAncestor": selected_ancestor["identity-jump"],
                "validYield": yields,
            })

    failed_hard = [name for name, passed in hard.items() if not passed]
    if failed_hard:
        raise AssertionError(f"hard basin confirmation invariant failure: {failed_hard}")

    same_seed = {}
    jump_seed = {}
    interaction_seed = {}
    for seed in SEEDS:
        seed_rows = [row for row in rows if row["seed"] == seed]
        if len(seed_rows) != len(ROUTES):
            raise AssertionError(f"seed {seed} is not a complete route block")
        same = _mean(row["sameBasinDelta"] for row in seed_rows)
        jump = _mean(row["identityJumpDelta"] for row in seed_rows)
        same_seed[str(seed)] = same
        jump_seed[str(seed)] = jump
        interaction_seed[str(seed)] = same - jump

    same_values = list(same_seed.values())
    jump_values = list(jump_seed.values())
    interaction_values = list(interaction_seed.values())
    same_summary = _summary(same_values)
    interaction_summary = _summary(interaction_values)

    route_effects = {}
    for route in ROUTES:
        route_rows = [row for row in rows if row["route"] == route]
        route_effects[route] = {
            "sameBasinMean": _mean(row["sameBasinDelta"] for row in route_rows),
            "identityJumpMean": _mean(row["identityJumpDelta"] for row in route_rows),
            "interactionMean": _mean(row["interaction"] for row in route_rows),
            "sameBasinSelectedAncestorRate": _mean(1.0 if row["sameBasinSelectedAncestor"] else 0.0 for row in route_rows),
            "identityJumpSelectedAncestorRate": _mean(1.0 if row["identityJumpSelectedAncestor"] else 0.0 for row in route_rows),
        }

    leave_one_route_out = []
    for omitted in ROUTES:
        effects = []
        for seed in SEEDS:
            kept = [row["sameBasinDelta"] for row in rows if row["seed"] == seed and row["route"] != omitted]
            if len(kept) != len(ROUTES) - 1:
                raise AssertionError(f"incomplete leave-one-route block for {omitted=} {seed=}")
            effects.append(_mean(kept))
        leave_one_route_out.append({
            "omittedRoute": omitted,
            "sameBasinMean": _mean(effects),
        })
    loro_values = [row["sameBasinMean"] for row in leave_one_route_out]

    checks = {
        "sameBasinOneSided95LowerBoundAboveZero": same_summary["oneSided95LowerBound"] > 0.0,
        "everyLeaveOneRouteOutSameBasinMeanAboveZero": min(loro_values) > 0.0,
        "interactionOneSided95LowerBoundAboveZero": interaction_summary["oneSided95LowerBound"] > 0.0,
    }
    confirmed = all(checks.values())

    return {
        "version": 1,
        "classification": "CONFIRMED" if confirmed else "NOT_CONFIRMED",
        "boundary": "fresh mechanical confirmation only; not artistic evidence or automatic production adoption",
        "population": {
            "routes": list(ROUTES),
            "masterSeeds": list(SEEDS),
            "completeMasterSeeds": len(SEEDS),
            "routeSeedBlocks": len(rows),
            "targetRegimes": list(REGIMES),
        },
        "hardInvariants": hard,
        "criticalValue": {
            "distribution": "Student-t",
            "oneSidedConfidence": 0.95,
            "df": 31,
            "t": T_ONE_SIDED_95_DF31,
        },
        "primary": {
            "sameBasin": same_summary,
            "identityJumpMean": _mean(jump_values),
            "interaction": interaction_summary,
            "sameBasinSeedEffects": same_seed,
            "identityJumpSeedEffects": jump_seed,
            "interactionSeedEffects": interaction_seed,
            "leaveOneRouteOut": leave_one_route_out,
            "leaveOneRouteOutSameBasinRange": [min(loro_values), max(loro_values)],
            "confirmationChecks": checks,
        },
        "routeEffects": route_effects,
        "diagnostics": {
            "sameBasinSelectedAncestorRate": _mean(1.0 if row["sameBasinSelectedAncestor"] else 0.0 for row in rows),
            "identityJumpSelectedAncestorRate": _mean(1.0 if row["identityJumpSelectedAncestor"] else 0.0 for row in rows),
            "meanGenericValidYield": _mean(row["validYield"][regime]["generic"] for row in rows for regime in REGIMES),
            "meanTrustValidYield": _mean(row["validYield"][regime]["trust"] for row in rows for regime in REGIMES),
        },
        "rows": rows,
        "next": (
            "integrate basin identity as explicit search state, then test phenotype-structural repertoire allocation"
            if confirmed
            else "do not tune local mutation on fresh evidence; move to archive/repertoire architecture using completed evidence"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(reduce(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
