#!/usr/bin/env python3
"""Fail-closed reducer for the consumed-seed basin trust-region pilot."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
SEEDS = (
    1009, 1013, 1019, 1021,
    1031, 1033, 1039, 1049,
    1051, 1061, 1063, 1069,
)
REGIMES = ("same-basin", "identity-jump")


def _load_blocks(results_dir: Path) -> dict[tuple[str, int], dict]:
    blocks = {}
    for path in sorted(results_dir.rglob("*.json")):
        data = json.loads(path.read_text())
        route = data.get("route")
        seed = data.get("seed")
        if route not in ROUTES or seed not in SEEDS:
            raise AssertionError(f"unexpected pilot block {route=} {seed=} from {path}")
        key = (route, int(seed))
        if key in blocks:
            raise AssertionError(f"duplicate pilot block {key}")
        if data.get("analysisSeed") is not True:
            raise AssertionError(f"non-analysis seed entered reducer: {key}")
        blocks[key] = data

    expected = {(route, seed) for route in ROUTES for seed in SEEDS}
    missing = expected - set(blocks)
    extra = set(blocks) - expected
    if missing or extra:
        raise AssertionError(f"pilot rectangle mismatch missing={sorted(missing)} extra={sorted(extra)}")
    return blocks


def _mean(values):
    values = list(values)
    if not values:
        raise AssertionError("cannot average empty values")
    return statistics.fmean(values)


def reduce(results_dir: Path) -> dict:
    blocks = _load_blocks(results_dir)
    rows = []
    hard = {
        "sameRepresentativeForBothPolicies": True,
        "equalTwentyCandidateBudgets": True,
        "trustChampionFrozenDriftZero": True,
        "sameBasinTargetFrozenDriftZero": True,
        "identityJumpTargetCrossesIdentity": True,
    }

    for route in ROUTES:
        for seed in SEEDS:
            block = blocks[(route, seed)]
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
        raise AssertionError(f"hard basin-trust invariant failure: {failed_hard}")

    seed_effects = {}
    jump_seed_effects = {}
    interaction_seed_effects = {}
    for seed in SEEDS:
        seed_rows = [row for row in rows if row["seed"] == seed]
        if len(seed_rows) != len(ROUTES):
            raise AssertionError(f"seed {seed} is not a complete route block")
        same = _mean(row["sameBasinDelta"] for row in seed_rows)
        jump = _mean(row["identityJumpDelta"] for row in seed_rows)
        seed_effects[str(seed)] = same
        jump_seed_effects[str(seed)] = jump
        interaction_seed_effects[str(seed)] = same - jump

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
        kept = [row for row in rows if row["route"] != omitted]
        leave_one_route_out.append({
            "omittedRoute": omitted,
            "sameBasinMean": _mean(row["sameBasinDelta"] for row in kept),
        })

    same_mean = _mean(seed_effects.values())
    jump_mean = _mean(jump_seed_effects.values())
    interaction_mean = _mean(interaction_seed_effects.values())
    loro_values = [row["sameBasinMean"] for row in leave_one_route_out]
    promising = min(loro_values) > 0.0 and interaction_mean > 0.0

    return {
        "version": 1,
        "classification": "PILOT_PROMISING" if promising else "PILOT_MIXED",
        "boundary": "consumed-seed architecture triage only; not confirmation or artistic evidence",
        "population": {
            "routes": list(ROUTES),
            "masterSeeds": list(SEEDS),
            "completeMasterSeeds": len(SEEDS),
            "routeSeedBlocks": len(rows),
            "targetRegimes": list(REGIMES),
        },
        "hardInvariants": hard,
        "primary": {
            "sameBasinMeanSeedEffect": same_mean,
            "identityJumpMeanSeedEffect": jump_mean,
            "meanInteraction": interaction_mean,
            "sameBasinMedianSeedEffect": statistics.median(seed_effects.values()),
            "sameBasinSeedEffects": seed_effects,
            "identityJumpSeedEffects": jump_seed_effects,
            "interactionSeedEffects": interaction_seed_effects,
            "leaveOneRouteOut": leave_one_route_out,
            "leaveOneRouteOutSameBasinRange": [min(loro_values), max(loro_values)],
            "pilotChecks": {
                "everyLeaveOneRouteOutSameBasinMeanAboveZero": min(loro_values) > 0.0,
                "meanInteractionAboveZero": interaction_mean > 0.0,
            },
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
            "freeze partition and preregister fresh mechanical confirmation"
            if promising
            else "do not consume fresh seeds; inspect route partition assumptions using only reserved consumed evidence"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(reduce(args.results_dir), indent=2))


if __name__ == "__main__":
    main()
