#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ALLOWED = {"A>B", "B>A", "equivalent", "unreviewable"}
ROUTES = ("recurrence", "orbit", "filament")
EXPECTED_BLOCKS = tuple(f"R{i:02d}" for i in range(1, 13))
TREATMENT = "spectralPreserve20"
BASELINE = "baseline20"


def load(path: str):
    return json.loads(Path(path).read_text())


def normalize_ratings(obj) -> dict[str, str]:
    if isinstance(obj, dict) and "ratings" in obj:
        obj = obj["ratings"]
    if isinstance(obj, dict):
        ratings = {str(k): str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        ratings = {str(x["blockId"]): str(x["judgment"]) for x in obj}
    else:
        raise ValueError("ratings must be a mapping or a list of blockId/judgment records")
    if tuple(sorted(ratings)) != EXPECTED_BLOCKS:
        raise ValueError(f"ratings must cover exactly {EXPECTED_BLOCKS}; got {tuple(sorted(ratings))}")
    bad = {k: v for k, v in ratings.items() if v not in ALLOWED}
    if bad:
        raise ValueError(f"invalid judgments: {bad}")
    return ratings


def score(judgment: str, a_arm: str, b_arm: str) -> int:
    if judgment in {"equivalent", "unreviewable"}:
        return 0
    winner = "A" if judgment == "A>B" else "B"
    winner_arm = a_arm if winner == "A" else b_arm
    if winner_arm == TREATMENT:
        return 1
    if winner_arm == BASELINE:
        return -1
    raise ValueError(f"unknown winner arm {winner_arm!r}")


def one_sided_sign_p(treatment_wins: int, baseline_wins: int) -> float:
    n = treatment_wins + baseline_wins
    if n <= 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(treatment_wins, n + 1)) / (2 ** n)


def reduce_review(ratings_path: str, key_path: str) -> dict:
    ratings = normalize_ratings(load(ratings_path))
    key = load(key_path)
    if key.get("smoke"):
        raise ValueError("smoke key cannot be used for authoritative review reduction")
    blocks = key.get("blocks", [])
    if tuple(sorted(str(b["blockId"]) for b in blocks)) != EXPECTED_BLOCKS:
        raise ValueError("key does not cover the frozen 12-block review")

    rows = []
    route_net = defaultdict(int)
    route_counts = defaultdict(Counter)
    total_net = 0
    reviewable = 0
    decisive = 0
    treatment_wins = 0
    baseline_wins = 0
    counts = Counter()

    for block in sorted(blocks, key=lambda x: x["blockId"]):
        bid = str(block["blockId"])
        judgment = ratings[bid]
        if judgment != "unreviewable":
            reviewable += 1
        value = score(judgment, str(block["A"]), str(block["B"]))
        if value > 0:
            treatment_wins += 1
            decisive += 1
        elif value < 0:
            baseline_wins += 1
            decisive += 1

        total_net += value
        route = str(block["route"])
        route_net[route] += value
        route_counts[route]["treatmentWins" if value > 0 else "baselineWins" if value < 0 else "tiesOrUnreviewable"] += 1
        counts[judgment] += 1
        rows.append({
            "blockId": bid,
            "route": route,
            "seed": int(block["seed"]),
            "judgment": judgment,
            "A": block["A"],
            "B": block["B"],
            "spectralPreserveVsBaselineScore": value,
        })

    if set(route_net) != set(ROUTES):
        raise ValueError(f"route strata drift: {dict(route_net)}")

    sign_p = one_sided_sign_p(treatment_wins, baseline_wins)
    leave_one = {route: total_net - route_net[route] for route in ROUTES}
    positive_route_count = sum(route_net[r] > 0 for r in ROUTES)

    gates = {
        "atLeastNineReviewable": reviewable >= 9,
        "atLeastEightDecisive": decisive >= 8,
        "treatmentWinsExceedBaselineWins": treatment_wins > baseline_wins,
        "oneSidedExactSignPAtMostPoint10": sign_p <= 0.10,
        "everyRouteNetNonnegative": all(route_net[r] >= 0 for r in ROUTES),
        "atLeastTwoRouteNetsPositive": positive_route_count >= 2,
        "everyLeaveOneRouteOutNetPositive": all(v > 0 for v in leave_one.values()),
    }
    passed = all(gates.values())

    return {
        "version": 1,
        "decision": (
            "SPECTRAL_PRESERVE_RESTART_ARTISTIC_SUPPORT_STAGE_A"
            if passed
            else "SPECTRAL_PRESERVE_RESTART_ARTISTIC_SUPPORT_STAGE_A_NOT_DEMONSTRATED"
        ),
        "blockCount": 12,
        "reviewableCount": reviewable,
        "decisiveCount": decisive,
        "judgmentCounts": dict(counts),
        "treatmentWins": treatment_wins,
        "baselineWins": baseline_wins,
        "oneSidedExactSignP": sign_p,
        "totalSpectralPreserveVsBaselineNetPreference": total_net,
        "routeNetPreference": dict(route_net),
        "routeCounts": {r: dict(route_counts[r]) for r in ROUTES},
        "positiveRouteNetCount": positive_route_count,
        "leaveOneRouteOutNetPreference": leave_one,
        "gates": gates,
        "artisticSupportStageAPassed": passed,
        "productionDecision": (
            "AUTHORIZE_FRESH_STAGE_B_REPLICATION_ONLY"
            if passed
            else "KEEP_BASELINE20_TEST_RESTART_CULTIVATION_NEXT"
        ),
        "rows": rows,
        "authority": "independent-human-artistic-usefulness-stage-a-only",
        "interpretation": (
            "The corrected spectral-preserving restart integration clears the stricter fresh Stage-A artistic boundary. Production remains unchanged; one independently seeded Stage-B blinded replication under the same frozen contract is required before default-runtime promotion can be considered."
            if passed else
            "The corrected spectral-preserving native-swap integration does not clear the stricter fresh Stage-A artistic boundary. Keep the supported baseline runtime, stop ratio/position tuning for this integration, and test the separately preregistered restart-cultivation loophole next."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ratings", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = reduce_review(args.ratings, args.key)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
