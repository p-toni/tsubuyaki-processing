#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from generate import BLOCKS, INCUMBENT_ROUTES

ALLOWED = {"A>B", "B>A", "equivalent", "unreviewable"}


def _load_keys(key_dir: Path) -> dict[str, dict]:
    keys = {}
    for path in sorted(key_dir.glob("R*.json")):
        record = json.loads(path.read_text())
        label = str(record["label"])
        if label in keys:
            raise AssertionError(f"duplicate key for {label}")
        keys[label] = record
    return keys


def _load_judgments(path: Path) -> dict[str, str]:
    raw = json.loads(path.read_text())
    if isinstance(raw, dict) and "judgments" in raw:
        raw = raw["judgments"]
    if not isinstance(raw, dict):
        raise ValueError("judgments must be an object mapping Rxx -> verdict")
    out = {str(label): str(verdict) for label, verdict in raw.items()}
    for label, verdict in out.items():
        if verdict not in ALLOWED:
            raise ValueError(f"{label}: invalid judgment {verdict!r}")
    return out


def _spectral_score(verdict: str, spectral_side: str) -> int:
    if verdict in {"equivalent", "unreviewable"}:
        return 0
    winner = "A" if verdict == "A>B" else "B"
    return 1 if winner == spectral_side else -1


def _one_sided_sign_test(candidate_wins: int, incumbent_wins: int) -> float:
    decisive = candidate_wins + incumbent_wins
    if decisive <= 0:
        return 1.0
    # P[X >= candidate_wins] for X ~ Binomial(decisive, 0.5).
    return sum(math.comb(decisive, k) for k in range(candidate_wins, decisive + 1)) / (2 ** decisive)


def reduce(keys: dict[str, dict], judgments: dict[str, str]) -> dict:
    expected = set(BLOCKS)
    hard = {
        "completeKeyRectangle": set(keys) == expected,
        "completeJudgmentRectangle": set(judgments) == expected,
        "allKeysArtisticEvidence": len(keys) == len(expected)
        and all(bool(record.get("artisticReviewEvidence")) for record in keys.values()),
        "allGenerationInvariants": len(keys) == len(expected)
        and all(all(record.get("hardInvariants", {}).values()) for record in keys.values()),
        "exactIncumbentRouteRectangle": len(keys) == len(expected)
        and all(sum(1 for record in keys.values() if record["incumbentRoute"] == route) == 4 for route in INCUMBENT_ROUTES),
    }
    if not all(hard.values()):
        return {
            "version": 1,
            "experiment": "artistic-sampling-invariance-evaluation-v1",
            "decision": "INVALID_INCOMPLETE_ARTISTIC_EVIDENCE",
            "hardInvariants": hard,
        }

    rows = []
    for label in sorted(expected):
        record = keys[label]
        verdict = judgments[label]
        score = _spectral_score(verdict, str(record["spectralSide"]))
        rows.append(
            {
                "label": label,
                "seed": int(record["seed"]),
                "incumbentRoute": str(record["incumbentRoute"]),
                "judgment": verdict,
                "spectralSide": str(record["spectralSide"]),
                "spectralScore": score,
                "reviewable": verdict != "unreviewable",
            }
        )

    reviewable = sum(1 for row in rows if row["reviewable"])
    total_net = sum(row["spectralScore"] for row in rows)
    route_nets = {
        route: sum(row["spectralScore"] for row in rows if row["incumbentRoute"] == route)
        for route in INCUMBENT_ROUTES
    }
    loo_nets = {
        route: sum(row["spectralScore"] for row in rows if row["incumbentRoute"] != route)
        for route in INCUMBENT_ROUTES
    }
    counts = Counter(row["judgment"] for row in rows)
    spectral_wins = sum(1 for row in rows if row["spectralScore"] > 0)
    incumbent_wins = sum(1 for row in rows if row["spectralScore"] < 0)

    gates = {
        "atLeast15Reviewable": reviewable >= 15,
        "totalSpectralNetPositive": total_net > 0,
        "everyLeaveOneIncumbentRouteOutNetPositive": all(value > 0 for value in loo_nets.values()),
    }
    decision = "ARTISTIC_ADMISSION_SUPPORT" if all(gates.values()) else "ARTISTIC_ADMISSION_NOT_SUPPORTED"

    seed_nets = defaultdict(int)
    for row in rows:
        seed_nets[row["seed"]] += row["spectralScore"]

    return {
        "version": 1,
        "experiment": "artistic-sampling-invariance-evaluation-v1",
        "decision": decision,
        "hardInvariants": hard,
        "gates": gates,
        "primary": {
            "reviewable": reviewable,
            "totalBlocks": len(rows),
            "totalSpectralNetPreference": total_net,
            "spectralWins": spectral_wins,
            "incumbentWins": incumbent_wins,
            "equivalent": counts.get("equivalent", 0),
            "unreviewable": counts.get("unreviewable", 0),
            "leaveOneIncumbentRouteOutNet": loo_nets,
        },
        "diagnostics": {
            "incumbentRouteNet": route_nets,
            "seedNet": {str(seed): seed_nets[seed] for seed in sorted(seed_nets)},
            "oneSidedExactSignTestP": _one_sided_sign_test(spectral_wins, incumbent_wins),
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-dir", required=True)
    parser.add_argument("--judgments", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = reduce(_load_keys(Path(args.key_dir)), _load_judgments(Path(args.judgments)))
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"decision": result["decision"], "gates": result.get("gates"), "primary": result.get("primary")}, indent=2))


if __name__ == "__main__":
    main()
