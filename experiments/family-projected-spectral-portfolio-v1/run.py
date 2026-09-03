#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
FIELD_DIR = ROOT / "experiments" / "sampling-invariance-v1"
CONTROL_DIR = ROOT / "experiments" / "spectral-material-control-v1"
PROJECTION_DIR = ROOT / "experiments" / "family-spectral-projection-v1"
for path in (HERE, PROTO, FIELD_DIR, CONTROL_DIR, PROJECTION_DIR):
    sys.path.insert(0, str(path))
# The projection experiment also has a module named targets.py. Reassert the
# current experiment directory so the local frozen target suite wins import
# resolution without changing any operator or experimental semantics.
sys.path.insert(0, str(HERE))

import field as frozen_field
import core
from rng_streams import derived_seed, representation_rng
from spectral_control import velocity_rms
import fast_grayscale_metric as metric
from family_projection import warp_family_projected, terminal_length_error
from targets import build_targets_family_portfolio, target_contract_family_portfolio

ROUTE = "family"
TIMES = (30.0, 90.0, 150.0)
CANONICAL_TIME = 90.0
STARTS_PER_SEED = 2
BASELINE_NATIVE_PER_START = 6
MIXED_NATIVE_PER_START = 3
MIXED_PROJECTED_PER_START = 3
TOTAL_CHALLENGERS_PER_ARM = 12
SPECTRAL_AMPLITUDE = 16.0
FIELD_BANDWIDTH = 2
MAX_START_ATTEMPTS = 128
LAW_FAILURE = "shared family law loses sibling-scale coherence"
SMOKE_SEED = 763999
MASTER_SEEDS = (
    763003, 763019, 763037, 763053, 763071,
    763089, 763107, 763127, 763149, 763167,
    763181, 763199, 763223, 763239, 763257,
    763277, 763293, 763311, 763331, 763349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS


def _native_geometry(genome: dict, t: float):
    return core.ROUTES[ROUTE]["geometry"](genome, t)


def _checks(genome: dict, geometry_fn) -> dict:
    return core.check_candidate(ROUTE, genome, TIMES, geometry_fn, core.W, core.H)


def _render_geometry(geometry: dict, genome: dict):
    return core.draw_points(geometry["all"], int(genome.get("alpha", 48)))


def _render_native(genome: dict):
    return _render_geometry(_native_geometry(genome, CANONICAL_TIME), genome)


def _valid_starts(master_seed: int) -> tuple[list[dict], int]:
    version = str(core.ROUTES[ROUTE]["version"])
    rng = representation_rng(
        master_seed,
        ROUTE,
        version,
        "family-projected-spectral-portfolio-v1-starts",
    )
    starts = []
    attempts = 0
    while len(starts) < STARTS_PER_SEED and attempts < MAX_START_ATTEMPTS:
        attempts += 1
        genome = core.ROUTES[ROUTE]["seed"](rng)
        if bool(_checks(genome, _native_geometry).get("valid", False)):
            starts.append(genome)
    if len(starts) != STARTS_PER_SEED:
        raise AssertionError(
            f"failed to establish {STARTS_PER_SEED} family starts for {master_seed}"
        )
    return starts, attempts


def _baseline_native(master_seed: int, starts: list[dict]) -> list[dict]:
    version = str(core.ROUTES[ROUTE]["version"])
    records = []
    for start_index, base in enumerate(starts):
        rng = representation_rng(
            master_seed,
            ROUTE,
            version,
            f"family-projected-spectral-portfolio-v1-native-{start_index}",
        )
        for challenger_index in range(BASELINE_NATIVE_PER_START):
            genome = core.ROUTES[ROUTE]["mutate"](base, rng, 1.0)
            checks = _checks(genome, _native_geometry)
            valid = bool(checks.get("valid", False))
            records.append(
                {
                    "startIndex": start_index,
                    "challengerIndex": challenger_index,
                    "valid": valid,
                    "failures": list(checks.get("failures", [])),
                    "image": _render_native(genome) if valid else None,
                }
            )
    if len(records) != TOTAL_CHALLENGERS_PER_ARM:
        raise AssertionError("baseline native budget drift")
    return records


def _mixed_native_prefix(baseline_native: list[dict]) -> list[dict]:
    records = [
        r for r in baseline_native
        if int(r["challengerIndex"]) < MIXED_NATIVE_PER_START
    ]
    if len(records) != STARTS_PER_SEED * MIXED_NATIVE_PER_START:
        raise AssertionError("mixed native prefix budget drift")
    return records


def _mixed_projected(master_seed: int, starts: list[dict]) -> list[dict]:
    records = []
    for start_index, base in enumerate(starts):
        for challenger_index in range(MIXED_PROJECTED_PER_START):
            field_seed = derived_seed(
                master_seed,
                "family-projected-spectral-portfolio-v1",
                "projected-spectral",
                start_index,
                challenger_index,
            )
            field = frozen_field.random_field(FIELD_BANDWIDTH, field_seed)
            rms = velocity_rms(field)

            def projected_geometry(g, t, *, _field=field, _rms=rms):
                native = _native_geometry(g, t)
                return warp_family_projected(
                    _field,
                    native,
                    SPECTRAL_AMPLITUDE,
                    core.W,
                    core.H,
                    rms=_rms,
                )

            checks = _checks(base, projected_geometry)
            valid = bool(checks.get("valid", False))
            max_terminal_error = 0.0
            for t in TIMES:
                native = _native_geometry(base, t)
                projected = projected_geometry(base, t)
                max_terminal_error = max(
                    max_terminal_error,
                    terminal_length_error(native, projected),
                )
            if max_terminal_error > 1e-8:
                raise AssertionError(
                    f"family terminal-length projection drift: {max_terminal_error}"
                )
            records.append(
                {
                    "startIndex": start_index,
                    "challengerIndex": challenger_index,
                    "fieldSeed": field_seed,
                    "valid": valid,
                    "failures": list(checks.get("failures", [])),
                    "maxTerminalLengthError": max_terminal_error,
                    "image": _render_geometry(projected_geometry(base, CANONICAL_TIME), base)
                    if valid else None,
                }
            )
    if len(records) != STARTS_PER_SEED * MIXED_PROJECTED_PER_START:
        raise AssertionError("mixed projected-spectral budget drift")
    return records


def _recovery(image, target_image) -> float:
    return 1.0 - float(
        metric.sparse_geometry_distance((image,), (target_image,))["distance"]
    )


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")
    if int(core.ROUTES[ROUTE].get("intrinsic_dimension", -1)) != 2:
        raise AssertionError("family intrinsic-dimension contract drift")

    starts, start_attempts = _valid_starts(master_seed)
    base_images = [_render_native(g) for g in starts]
    baseline_native = _baseline_native(master_seed, starts)
    mixed_native = _mixed_native_prefix(baseline_native)
    mixed_projected = _mixed_projected(master_seed, starts)

    # Build/score targets only after both challenger archives are frozen.
    targets = build_targets_family_portfolio()
    target_contract = target_contract_family_portfolio() if smoke else None

    baseline_images = [r["image"] for r in baseline_native if r["valid"]]
    mixed_native_images = [r["image"] for r in mixed_native if r["valid"]]
    mixed_projected_images = [r["image"] for r in mixed_projected if r["valid"]]

    cells = []
    for target in targets:
        base_recovery = max(_recovery(image, target.image) for image in base_images)
        baseline_recovery = max(
            [base_recovery]
            + [_recovery(image, target.image) for image in baseline_images]
        )
        mixed_recovery = max(
            [base_recovery]
            + [_recovery(image, target.image) for image in mixed_native_images]
            + [_recovery(image, target.image) for image in mixed_projected_images]
        )
        cells.append(
            {
                "masterSeed": master_seed,
                "targetId": target.id,
                "targetFamily": target.family,
                "baseRecovery": base_recovery,
                "baselineRecovery": baseline_recovery,
                "mixedRecovery": mixed_recovery,
                "baselineAdded": baseline_recovery - base_recovery,
                "mixedAdded": mixed_recovery - base_recovery,
                "delta": mixed_recovery - baseline_recovery,
            }
        )

    baseline_valid = sum(bool(r["valid"]) for r in baseline_native)
    mixed_native_valid = sum(bool(r["valid"]) for r in mixed_native)
    projected_valid = sum(bool(r["valid"]) for r in mixed_projected)
    projected_failures = [f for r in mixed_projected for f in r["failures"]]
    hard = {
        "routeExact": ROUTE == "family",
        "routeClassExact": int(core.ROUTES[ROUTE].get("intrinsic_dimension", -1)) == 2,
        "twoSharedStarts": len(starts) == STARTS_PER_SEED,
        "baselineBudgetExact": len(baseline_native) == TOTAL_CHALLENGERS_PER_ARM,
        "mixedBudgetExact": len(mixed_native) + len(mixed_projected) == TOTAL_CHALLENGERS_PER_ARM,
        "commonNativePrefixExact": mixed_native == [
            r for r in baseline_native
            if int(r["challengerIndex"]) < MIXED_NATIVE_PER_START
        ],
        "projectionTerminalLengthsExact": max(
            (float(r["maxTerminalLengthError"]) for r in mixed_projected),
            default=0.0,
        ) <= 1e-8,
        "targetCountExact": len(targets) == 15,
        "cellCountExact": len(cells) == 15,
    }
    if smoke:
        hard["freshTargetContractValid"] = bool(target_contract and target_contract["valid"])
    if not all(hard.values()):
        raise AssertionError(f"hard invariant failure: {hard}")

    return {
        "version": 1,
        "experiment": "family-projected-spectral-portfolio-v1",
        "masterSeed": master_seed,
        "smoke": smoke,
        "artisticEvidence": False,
        "authority": "mechanical-family-portfolio-only",
        "settings": {
            "route": ROUTE,
            "times": list(TIMES),
            "canonicalTime": CANONICAL_TIME,
            "startsPerSeed": STARTS_PER_SEED,
            "totalChallengersPerArm": TOTAL_CHALLENGERS_PER_ARM,
            "baselineNativePerStart": BASELINE_NATIVE_PER_START,
            "mixedNativePerStart": MIXED_NATIVE_PER_START,
            "mixedProjectedSpectralPerStart": MIXED_PROJECTED_PER_START,
            "nativeMutationScale": 1.0,
            "spectralAmplitude": SPECTRAL_AMPLITUDE,
            "fieldBandwidth": FIELD_BANDWIDTH,
            "metric": "sparse-geometry-v1-exact-fast-grayscale",
            "lawFailure": LAW_FAILURE,
        },
        "hardInvariants": hard,
        "targetContract": target_contract,
        "diagnostics": {
            "startAttempts": start_attempts,
            "baselineNativeAttempts": len(baseline_native),
            "baselineNativeValid": baseline_valid,
            "mixedNativeAttempts": len(mixed_native),
            "mixedNativeValid": mixed_native_valid,
            "mixedProjectedAttempts": len(mixed_projected),
            "mixedProjectedValid": projected_valid,
            "mixedProjectedLawFailures": sum(f == LAW_FAILURE for f in projected_failures),
            "mixedProjectedFailureModes": sorted(projected_failures),
        },
        "cells": cells,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run_seed(args.seed, smoke=args.smoke)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
