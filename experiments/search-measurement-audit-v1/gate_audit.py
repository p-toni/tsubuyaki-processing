#!/usr/bin/env python3
from __future__ import annotations

import json
import math

SEED_COUNTS = (3, 9, 21)
WIN_PROBS = (0.50, 0.55, 0.60, 0.65, 0.70)
ROUTES = 5
ROUTE_THRESHOLD = 4


def route_support_probability(p: float, n: int) -> float:
    threshold = n // 2 + 1
    return sum(math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(threshold, n + 1))


def general_support_probability(p: float, n: int) -> float:
    q = route_support_probability(p, n)
    return sum(math.comb(ROUTES, k) * q**k * (1-q)**(ROUTES-k) for k in range(ROUTE_THRESHOLD, ROUTES + 1))


def main() -> None:
    rows = []
    for n in SEED_COUNTS:
        for p in WIN_PROBS:
            rows.append({
                "seedsPerRoute": n,
                "perSeedWinProbability": p,
                "routeSupportProbability": route_support_probability(p, n),
                "generalGateProbability": general_support_probability(p, n),
            })
    null_rates = {str(n): general_support_probability(0.5, n) for n in SEED_COUNTS}
    result = {
        "version": 1,
        "historicalGate": {
            "routeRule": "strict majority of seed wins",
            "generalRule": ">=4/5 route supports",
        },
        "rows": rows,
        "nullGeneralPassProbability": null_rates,
        "retirementCriterion": "retire confirmatory stochastic use if null pass probability remains above 0.10 as seed count grows",
        "retireForConfirmatoryStochasticUse": any(v > 0.10 for v in null_rates.values()),
        "replacementDirection": "preserve continuous paired route x seed deltas; aggregate equal-route effects at seed level; choose uncertainty/practical-effect rule only after objective validation",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
