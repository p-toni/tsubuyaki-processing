#!/usr/bin/env python3
"""Generate one consumed-holdout route×seed block for niche qualification."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
if str(PROTO) not in sys.path:
    sys.path.insert(0, str(PROTO))

from orbit_representation import register_orbit
register_orbit()

from core import TIMES, default_brief, render_candidate_frame
from phenotype_descriptors import DESCRIPTOR_VERSION, describe_genome, niche_key
from representation_capacity import _generate_route_archive

ROUTE_ORDER = ("recurrence", "orbit", "family", "sheet", "filament")
HOLDOUT_SEEDS = (
    1087, 1091, 1093, 1097,
    1103, 1109, 1117, 1123,
    1129, 1151, 1153, 1163,
    1171, 1181, 1187, 1193,
    1201, 1213, 1217, 1223,
)
STARTS_PER_ROUTE = 6
EXPECTED_CANDIDATES = len(ROUTE_ORDER) * len(HOLDOUT_SEEDS) * STARTS_PER_ROUTE


def _phenotype_fingerprint(candidate) -> str:
    h = hashlib.sha256()
    for t in TIMES:
        h.update(render_candidate_frame(candidate, t).convert("L").tobytes())
        h.update(b"\0")
    return h.hexdigest()


def run_block(route: str, seed: int) -> dict:
    if route not in ROUTE_ORDER:
        raise ValueError(f"unknown route {route!r}")
    if seed not in HOLDOUT_SEEDS:
        raise ValueError(f"seed {seed} is not in the preregistered consumed holdout")

    brief = default_brief()
    brief.update(name=f"repertoire-niche-audit-{route}", routes=[route])
    candidates, attempts = _generate_route_archive(brief, seed, route, STARTS_PER_ROUTE)
    if len(candidates) != STARTS_PER_ROUTE:
        raise AssertionError("fixed archive candidate count drift")

    records = []
    for candidate in candidates:
        if not candidate.checks.get("valid", False):
            raise AssertionError(f"capacity archive returned invalid candidate {candidate.id}")
        descriptor = describe_genome(route, candidate.genome)
        niche = niche_key(descriptor)
        features = candidate.features
        records.append(
            {
                "seed": seed,
                "route": route,
                "candidateId": candidate.id,
                "phenotypeFingerprint": _phenotype_fingerprint(candidate),
                "descriptor": descriptor.to_json(),
                "niche": niche.to_json(),
                "diagnosticScore": candidate.score,
                "composition": {
                    "occupancyMean": features["occupancy_mean"],
                    "dominantBBoxSpan": max(features["bbox_w_mean"], features["bbox_h_mean"]),
                    "centeringError": features["center_dx_mean"] + features["center_dy_mean"],
                },
                "hardValid": True,
            }
        )

    return {
        "version": 1,
        "descriptorVersion": DESCRIPTOR_VERSION,
        "route": route,
        "seed": seed,
        "analysisSeed": True,
        "freshSearchEvidence": False,
        "startsPerRoute": STARTS_PER_ROUTE,
        "generation": "representation_capacity._generate_route_archive; selector-independent fixed viable starts",
        "attempts": attempts,
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=True, choices=ROUTE_ORDER)
    parser.add_argument("--seed", type=int, required=True, choices=HOLDOUT_SEEDS)
    args = parser.parse_args()
    print(json.dumps(run_block(args.route, args.seed), indent=2))


if __name__ == "__main__":
    main()
