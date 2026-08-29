#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ALLOWED = {"A>B", "B>A", "equivalent", "unreviewable"}
EXPECTED_LABELS = tuple(f"R{i:02d}" for i in range(1, 21))
ROUTE_ORDER = ("recurrence", "orbit", "family", "sheet", "filament")
MIN_REVIEWABLE = 15


def _load_keys(key_dir: Path) -> dict[str, dict]:
    keys = {}
    for path in sorted(key_dir.glob("R*.json")):
        data = json.loads(path.read_text())
        label = str(data["label"])
        if label in keys:
            raise AssertionError(f"duplicate key {label}")
        if data["route"] not in ROUTE_ORDER:
            raise AssertionError(f"unknown route in key {label}")
        if data["candidateSide"] not in ("A", "B"):
            raise AssertionError(f"invalid candidate side {label}")
        if not all(bool(v) for v in data.get("hardInvariants", {}).values()):
            raise AssertionError(f"generation invariant failure in {label}")
        keys[label] = data
    if tuple(sorted(keys)) != EXPECTED_LABELS:
        raise AssertionError(f"expected 20 blind keys, got {sorted(keys)}")
    return keys


def _load_judgments(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text())
    if set(data) != set(EXPECTED_LABELS):
        missing = sorted(set(EXPECTED_LABELS) - set(data))
        extra = sorted(set(data) - set(EXPECTED_LABELS))
        raise AssertionError(f"judgment rectangle mismatch: missing={missing}, extra={extra}")
    out = {}
    for label in EXPECTED_LABELS:
        value = str(data[label])
        if value not in ALLOWED:
            raise AssertionError(f"invalid judgment {label}={value!r}")
        out[label] = value
    return out


def _score(judgment: str, candidate_side: str) -> int:
    if judgment in ("equivalent", "unreviewable"):
        return 0
    winner = "A" if judgment == "A>B" else "B"
    return 1 if winner == candidate_side else -1


def _one_sided_sign_p(candidate_wins: int, baseline_wins: int) -> float:
    n = candidate_wins + baseline_wins
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(candidate_wins, n + 1)) / (2 ** n)


def aggregate(judgments_path: Path, key_dir: Path) -> dict:
    keys = _load_keys(key_dir)
    judgments = _load_judgments(judgments_path)

    rows = []
    for label in EXPECTED_LABELS:
        key = keys[label]
        judgment = judgments[label]
        score = _score(judgment, key["candidateSide"])
        rows.append({
            "label": label,
            "route": key["route"],
            "seed": int(key["seed"]),
            "judgment": judgment,
            "candidateSide": key["candidateSide"],
            "score": score,
            "reviewable": judgment != "unreviewable",
            "decisive": judgment in ("A>B", "B>A"),
        })

    reviewable = sum(row["reviewable"] for row in rows)
    candidate_wins = sum(row["score"] == 1 for row in rows)
    baseline_wins = sum(row["score"] == -1 for row in rows)
    equivalents = sum(row["judgment"] == "equivalent" for row in rows)
    unreviewable = sum(row["judgment"] == "unreviewable" for row in rows)
    net = sum(int(row["score"]) for row in rows)

    route_nets = {
        route: sum(int(row["score"]) for row in rows if row["route"] == route)
        for route in ROUTE_ORDER
    }
    leave_one_route_out = [
        {
            "omittedRoute": route,
            "netPreference": sum(int(row["score"]) for row in rows if row["route"] != route),
        }
        for route in ROUTE_ORDER
    ]

    gates = {
        "minimumReviewable": reviewable >= MIN_REVIEWABLE,
        "candidateNetPreferencePositive": net > 0,
        "everyLeaveOneRouteOutNetPositive": all(item["netPreference"] > 0 for item in leave_one_route_out),
    }
    supported = all(gates.values())

    return {
        "version": 1,
        "decision": "ARTISTIC_SUPPORT" if supported else "ARTISTIC_NOT_SUPPORTED",
        "reviewerCount": 1,
        "population": {
            "reviewBlocks": len(rows),
            "reviewable": reviewable,
            "decisive": candidate_wins + baseline_wins,
            "equivalent": equivalents,
            "unreviewable": unreviewable,
        },
        "gates": gates,
        "preference": {
            "candidateWins": candidate_wins,
            "baselineWins": baseline_wins,
            "net": net,
            "routeNets": route_nets,
            "leaveOneRouteOut": leave_one_route_out,
            "leaveOneRouteOutRange": [
                min(item["netPreference"] for item in leave_one_route_out),
                max(item["netPreference"] for item in leave_one_route_out),
            ],
        },
        "diagnostics": {
            "oneSidedExactSignTestP": _one_sided_sign_p(candidate_wins, baseline_wins),
            "note": "sign test and route-specific nets are diagnostics only; they cannot override the frozen artistic-support gate",
        },
        "decodedJudgments": rows,
        "interpretationBoundary": "single independent human reviewer; supports or fails artistic utility of the frozen confirmed allocator for the current repertoire, not universal aesthetic quality or route authority",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judgments", required=True)
    parser.add_argument("--key-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate(Path(args.judgments), Path(args.key_dir)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
