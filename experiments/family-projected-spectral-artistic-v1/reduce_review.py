#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

ALLOWED = {"A>B", "B>A", "equivalent", "unreviewable"}
EXPECTED_BLOCKS = tuple(f"R{i:02d}" for i in range(1, 25))


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


def _winner_mode(judgment: str, a_mode: str, b_mode: str) -> str | None:
    if judgment in {"equivalent", "unreviewable"}:
        return None
    return a_mode if judgment == "A>B" else b_mode


def _one_sided_binomial_p(wins: int, n: int) -> float:
    if n <= 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(wins, n + 1)) / (2 ** n)


def reduce_review(ratings_path: str, key_path: str) -> dict:
    ratings = normalize_ratings(load(ratings_path))
    key = load(key_path)
    if key.get("smoke"):
        raise ValueError("smoke key cannot be used for authoritative review reduction")
    blocks = key.get("blocks", [])
    if tuple(sorted(str(b["blockId"]) for b in blocks)) != EXPECTED_BLOCKS:
        raise ValueError("key does not cover the frozen 24-block review")

    rows = []
    reviewable = 0
    decisive = 0
    projected_wins = 0
    native_wins = 0
    counts = Counter()

    for block in sorted(blocks, key=lambda x: x["blockId"]):
        bid = str(block["blockId"])
        if str(block.get("route")) != "family":
            raise ValueError(f"route drift in {bid}: {block.get('route')!r}")
        a_mode = str(block["A"])
        b_mode = str(block["B"])
        if {a_mode, b_mode} != {"native", "projected"}:
            raise ValueError(f"identity drift in {bid}: A={a_mode!r} B={b_mode!r}")

        judgment = ratings[bid]
        counts[judgment] += 1
        if judgment != "unreviewable":
            reviewable += 1
        winner_mode = _winner_mode(judgment, a_mode, b_mode)
        if winner_mode is not None:
            decisive += 1
            if winner_mode == "projected":
                projected_wins += 1
            elif winner_mode == "native":
                native_wins += 1
            else:
                raise AssertionError(f"unknown winner mode {winner_mode!r}")

        rows.append({
            "blockId": bid,
            "seed": int(block["seed"]),
            "judgment": judgment,
            "A": a_mode,
            "B": b_mode,
            "winnerMode": winner_mode,
        })

    projected_win_rate = projected_wins / decisive if decisive else 0.0
    p_value = _one_sided_binomial_p(projected_wins, decisive)
    gates = {
        "atLeast18Reviewable": reviewable >= 18,
        "atLeast12Decisive": decisive >= 12,
        "projectedDecisiveWinRateAbove065": projected_win_rate > 0.65,
        "oneSidedExactBinomialPAtMost010": p_value <= 0.10,
    }
    passed = all(gates.values())

    return {
        "version": 1,
        "decision": (
            "FAMILY_PROJECTED_SPECTRAL_ARTISTIC_SUPPORT"
            if passed
            else "FAMILY_PROJECTED_SPECTRAL_ARTISTIC_SUPPORT_NOT_DEMONSTRATED"
        ),
        "blockCount": 24,
        "reviewableCount": reviewable,
        "decisiveCount": decisive,
        "judgmentCounts": dict(counts),
        "projectedWins": projected_wins,
        "nativeWins": native_wins,
        "projectedDecisiveWinRate": projected_win_rate,
        "oneSidedExactBinomialP": p_value,
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
