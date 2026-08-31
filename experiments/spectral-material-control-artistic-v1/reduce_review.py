#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ALLOWED = {"A>B", "B>A", "equivalent", "unreviewable"}
ROUTES = ("recurrence", "orbit", "filament")
EXPECTED_BLOCKS = tuple(f"R{i:02d}" for i in range(1, 13))


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


def score(judgment: str, a_mode: str, b_mode: str) -> int:
    if judgment in {"equivalent", "unreviewable"}:
        return 0
    winner = "A" if judgment == "A>B" else "B"
    winner_mode = a_mode if winner == "A" else b_mode
    return 1 if winner_mode == "mixed" else -1


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
    total_net = 0
    reviewable = 0
    counts = Counter()
    for block in sorted(blocks, key=lambda x: x["blockId"]):
        bid = str(block["blockId"])
        judgment = ratings[bid]
        if judgment != "unreviewable":
            reviewable += 1
        value = score(judgment, str(block["A"]), str(block["B"]))
        total_net += value
        route = str(block["route"])
        route_net[route] += value
        counts[judgment] += 1
        rows.append({
            "blockId": bid,
            "route": route,
            "seed": int(block["seed"]),
            "judgment": judgment,
            "A": block["A"],
            "B": block["B"],
            "mixedVsNativeScore": value,
        })

    if set(route_net) != set(ROUTES):
        raise ValueError(f"route strata drift: {dict(route_net)}")
    leave_one = {route: total_net - route_net[route] for route in ROUTES}
    gates = {
        "atLeastNineReviewable": reviewable >= 9,
        "totalMixedVsNativeNetPositive": total_net > 0,
        "everyLeaveOneRouteOutNetPositive": all(v > 0 for v in leave_one.values()),
    }
    passed = all(gates.values())
    return {
        "version": 1,
        "decision": "ARTISTIC_SUPPORT" if passed else "ARTISTIC_SUPPORT_NOT_DEMONSTRATED",
        "blockCount": 12,
        "reviewableCount": reviewable,
        "judgmentCounts": dict(counts),
        "totalMixedVsNativeNetPreference": total_net,
        "routeNetPreference": dict(route_net),
        "leaveOneRouteOutNetPreference": leave_one,
        "gates": gates,
        "artisticSupportPassed": passed,
        "rows": rows,
        "authority": "independent-human-artistic-usefulness-only",
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
