from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPACITY_DIR = ROOT / "experiments" / "sampling-invariance-v1"
sys.path.insert(0, str(CAPACITY_DIR))

import run_capacity
import fast_binary_metric as metric

capacity = run_capacity.capacity

from spectral_operator import geodesic_mutate, projective_angle

SEEDS = (94001, 94007, 94009, 94033)
BASES_PER_SEED = 12
ANGLES = (0.04, 0.08, 0.16, 0.32)
REPLICATES = 4
STREAM = "sampling-invariance-search-calibration-v1"
EPSILON = 1e-12


def _rng(*parts: object) -> np.random.Generator:
    payload = "|".join(str(part) for part in (STREAM,) + parts)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big", signed=False))


def _fingerprint(image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()


def _draw_valid_bases(seed: int, rasterizer) -> list[tuple[np.ndarray, object]]:
    rng = _rng(seed, "bases")
    accepted = []
    attempts = 0
    while len(accepted) < BASES_PER_SEED and attempts < BASES_PER_SEED * 20:
        attempts += 1
        coefficients = capacity._draw_field_coefficients(rng)
        image = rasterizer.image(coefficients)
        valid, _geometry = capacity._field_valid(image)
        if valid:
            accepted.append((coefficients, image))
    if len(accepted) != BASES_PER_SEED:
        raise RuntimeError(f"seed {seed}: only {len(accepted)} valid calibration bases")
    return accepted


def run() -> dict:
    rasterizer = capacity.FieldRasterizer()
    records = []
    base_fingerprints = set()

    for seed in SEEDS:
        bases = _draw_valid_bases(seed, rasterizer)
        for base_index, (parent, parent_image) in enumerate(bases):
            parent_fp = _fingerprint(parent_image)
            base_fingerprints.add(parent_fp)
            for angle in ANGLES:
                for replicate in range(REPLICATES):
                    rng = _rng(seed, base_index, f"{angle:.12f}", replicate)
                    child = geodesic_mutate(parent, rng, angle)
                    realized = projective_angle(parent, child)
                    child_image = rasterizer.image(child)
                    valid, geometry = capacity._field_valid(child_image)
                    distance = float(
                        metric.sparse_geometry_distance((child_image,), (parent_image,))["distance"]
                    )
                    records.append(
                        {
                            "seed": seed,
                            "base": base_index,
                            "angle": angle,
                            "replicate": replicate,
                            "realizedProjectiveAngle": realized,
                            "absoluteAngleError": abs(realized - angle),
                            "valid": bool(valid),
                            "phenotypeDistance": distance,
                            "parentFingerprint": parent_fp,
                            "childFingerprint": _fingerprint(child_image),
                            "geometry": geometry,
                        }
                    )

    per_angle = {}
    medians = []
    for angle in ANGLES:
        subset = [row for row in records if abs(row["angle"] - angle) <= EPSILON]
        distances = [float(row["phenotypeDistance"]) for row in subset]
        valid_fraction = statistics.fmean(1.0 if row["valid"] else 0.0 for row in subset)
        distinct_fraction = statistics.fmean(
            1.0 if row["childFingerprint"] != row["parentFingerprint"] else 0.0
            for row in subset
        )
        summary = {
            "n": len(subset),
            "validFraction": valid_fraction,
            "distinctChildFraction": distinct_fraction,
            "phenotypeDistance": {
                "mean": statistics.fmean(distances),
                "median": statistics.median(distances),
                "sd": statistics.stdev(distances),
                "min": min(distances),
                "max": max(distances),
            },
            "maxAbsoluteAngleError": max(float(row["absoluteAngleError"]) for row in subset),
        }
        per_angle[str(angle)] = summary
        medians.append(summary["phenotypeDistance"]["median"])

    contracts = {
        "completeRectangle": len(records) == len(SEEDS) * BASES_PER_SEED * len(ANGLES) * REPLICATES,
        "basePhenotypesDistinct": len(base_fingerprints) == len(SEEDS) * BASES_PER_SEED,
        "exactProjectiveAngles": max(float(row["absoluteAngleError"]) for row in records) <= 1e-12,
        "medianPhenotypeDistanceStrictlyIncreasing": all(
            medians[index] + EPSILON < medians[index + 1]
            for index in range(len(medians) - 1)
        ),
        "validFractionAtLeast0p95": all(
            float(per_angle[str(angle)]["validFraction"]) >= 0.95 for angle in ANGLES
        ),
        "distinctChildFractionAtLeast0p95": all(
            float(per_angle[str(angle)]["distinctChildFraction"]) >= 0.95 for angle in ANGLES
        ),
    }

    return {
        "version": 1,
        "experiment": "sampling-invariance-search-calibration-v1",
        "population": "excluded-design",
        "operator": "isotropic-projective-geodesic-v1",
        "seeds": list(SEEDS),
        "settings": {
            "basesPerSeed": BASES_PER_SEED,
            "angles": list(ANGLES),
            "replicatesPerBaseAngle": REPLICATES,
            "fieldBandwidth": capacity.FIELD_BANDWIDTH,
            "metric": "sparse-geometry-v1-exact-binary-equivalent",
        },
        "perAngle": per_angle,
        "contracts": contracts,
        "decision": "CALIBRATION_VALID" if all(contracts.values()) else "CALIBRATION_NEEDS_REVISION",
    }


def main() -> None:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["decision"] != "CALIBRATION_VALID":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
