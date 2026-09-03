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
for path in (HERE, PROTO, FIELD_DIR, CONTROL_DIR):
    sys.path.insert(0, str(path))

import field as frozen_field
import core
from rng_streams import derived_seed, representation_rng
from spectral_control import velocity_rms, warp_geometry
import fast_grayscale_metric as metric
from family_projection import warp_family_projected, terminal_length_error
from targets import build_targets_family_projection, target_contract_family_projection

ROUTE = "family"
TIMES = (30.0, 90.0, 150.0)
CANONICAL_TIME = 90.0
STARTS_PER_SEED = 2
CHALLENGERS_PER_START = 6
CHALLENGERS_PER_ARM = STARTS_PER_SEED * CHALLENGERS_PER_START
SPECTRAL_AMPLITUDE = 16.0
FIELD_BANDWIDTH = 2
MAX_START_ATTEMPTS = 128
SMOKE_SEED = 762999
MASTER_SEEDS = (
    762003, 762019, 762037, 762053, 762071,
    762089, 762107, 762127, 762149, 762167,
    762181, 762199, 762223, 762239, 762257,
    762277, 762293, 762311, 762331, 762349,
)
ALLOWED_SEEDS = (SMOKE_SEED,) + MASTER_SEEDS
LAW_FAILURE = "shared family law loses sibling-scale coherence"


def _valid(genome: dict, geometry_fn) -> dict:
    return core.check_candidate(ROUTE, genome, TIMES, geometry_fn, core.W, core.H)


def _native_geometry(genome: dict, t: float):
    return core.ROUTES[ROUTE]["geometry"](genome, t)


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
        "family-spectral-projection-v1-starts",
    )
    starts = []
    attempts = 0
    while len(starts) < STARTS_PER_SEED and attempts < MAX_START_ATTEMPTS:
        attempts += 1
        genome = core.ROUTES[ROUTE]["seed"](rng)
        checks = _valid(genome, _native_geometry)
        if checks.get("valid", False):
            starts.append(genome)
    if len(starts) != STARTS_PER_SEED:
        raise AssertionError(
            f"failed to establish {STARTS_PER_SEED} family starts for {master_seed}"
        )
    return starts, attempts


def _native_challengers(master_seed: int, starts: list[dict]) -> list[dict]:
    version = str(core.ROUTES[ROUTE]["version"])
    records = []
    for start_index, base in enumerate(starts):
        rng = representation_rng(
            master_seed,
            ROUTE,
            version,
            f"family-spectral-projection-v1-native-{start_index}",
        )
        for challenger_index in range(CHALLENGERS_PER_START):
            genome = core.ROUTES[ROUTE]["mutate"](base, rng, 1.0)
            checks = _valid(genome, _native_geometry)
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
    if len(records) != CHALLENGERS_PER_ARM:
        raise AssertionError("native challenger budget drift")
    return records


def _spectral_pair(master_seed: int, starts: list[dict]) -> tuple[list[dict], list[dict]]:
    generic_records = []
    projected_records = []
    for start_index, base in enumerate(starts):
        for challenger_index in range(CHALLENGERS_PER_START):
            field_seed = derived_seed(
                master_seed,
                "family-spectral-projection-v1",
                "spectral",
                start_index,
                challenger_index,
            )
            field = frozen_field.random_field(FIELD_BANDWIDTH, field_seed)
            rms = velocity_rms(field)

            def generic_geometry(g, t, *, _field=field, _rms=rms):
                native = _native_geometry(g, t)
                return warp_geometry(
                    _field,
                    native,
                    SPECTRAL_AMPLITUDE,
                    core.W,
                    core.H,
                    rms=_rms,
                )

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

            generic_checks = _valid(base, generic_geometry)
            projected_checks = _valid(base, projected_geometry)
            generic_valid = bool(generic_checks.get("valid", False))
            projected_valid = bool(projected_checks.get("valid", False))

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

            generic_records.append(
                {
                    "startIndex": start_index,
                    "challengerIndex": challenger_index,
                    "fieldSeed": field_seed,
                    "valid": generic_valid,
                    "failures": list(generic_checks.get("failures", [])),
                    "image": _render_geometry(generic_geometry(base, CANONICAL_TIME), base)
                    if generic_valid else None,
                }
            )
            projected_records.append(
                {
                    "startIndex": start_index,
                    "challengerIndex": challenger_index,
                    "fieldSeed": field_seed,
                    "valid": projected_valid,
                    "failures": list(projected_checks.get("failures", [])),
                    "maxTerminalLengthError": max_terminal_error,
                    "image": _render_geometry(projected_geometry(base, CANONICAL_TIME), base)
                    if projected_valid else None,
                }
            )

    if len(generic_records) != CHALLENGERS_PER_ARM:
        raise AssertionError("generic spectral challenger budget drift")
    if len(projected_records) != CHALLENGERS_PER_ARM:
        raise AssertionError("projected spectral challenger budget drift")
    return generic_records, projected_records


def _recovery(image, target_image) -> float:
    return 1.0 - float(
        metric.sparse_geometry_distance((image,), (target_image,))["distance"]
    )


def run_seed(master_seed: int, smoke: bool = False) -> dict:
    if master_seed not in ALLOWED_SEEDS:
        raise ValueError(f"seed {master_seed} outside frozen experiment population")
    if smoke != (master_seed == SMOKE_SEED):
        raise ValueError("smoke flag/seed mismatch")

    starts, start_attempts = _valid_starts(master_seed)
    base_images = [_render_native(g) for g in starts]
    native = _native_challengers(master_seed, starts)
    generic, projected = _spectral_pair(master_seed, starts)

    # Targets are constructed only after all candidate archives are frozen.
    targets = build_targets_family_projection()
    target_contract = target_contract_family_projection() if smoke else None

    native_images = [r["image"] for r in native if r["valid"]]
    generic_images = [r["image"] for r in generic if r["valid"]]
    projected_images = [r["image"] for r in projected if r["valid"]]

    cells = []
    for target in targets:
        base_recovery = max(_recovery(image, target.image) for image in base_images)
        native_recovery = max(
            [base_recovery] + [_recovery(image, target.image) for image in native_images]
        )
        generic_recovery = max(
            [base_recovery] + [_recovery(image, target.image) for image in generic_images]
        )
        projected_recovery = max(
            [base_recovery] + [_recovery(image, target.image) for image in projected_images]
        )
        cells.append(
            {
                "masterSeed": master_seed,
                "targetId": target.id,
                "targetFamily": target.family,
                "baseRecovery": base_recovery,
                "nativeRecovery": native_recovery,
                "genericRecovery": generic_recovery,
                "projectedRecovery": projected_recovery,
                "nativeAdded": native_recovery - base_recovery,
                "genericAdded": generic_recovery - base_recovery,
                "projectedAdded": projected_recovery - base_recovery,
                "genericDeltaVsNative": generic_recovery - native_recovery,
                "projectedDeltaVsNative": projected_recovery - native_recovery,
            }
        )

    generic_failures = [f for r in generic for f in r["failures"]]
    projected_failures = [f for r in projected for f in r["failures"]]
    hard = {
        "routeExact": ROUTE == "family",
        "twoSharedStarts": len(starts) == STARTS_PER_SEED,
        "nativeBudgetExact": len(native) == CHALLENGERS_PER_ARM,
        "genericBudgetExact": len(generic) == CHALLENGERS_PER_ARM,
        "projectedBudgetExact": len(projected) == CHALLENGERS_PER_ARM,
        "pairedFieldSeedsExact": [r["fieldSeed"] for r in generic]
        == [r["fieldSeed"] for r in projected],
        "projectionTerminalLengthsExact": max(
            (float(r["maxTerminalLengthError"]) for r in projected),
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
        "experiment": "family-spectral-projection-v1",
        "masterSeed": master_seed,
        "smoke": smoke,
        "artisticEvidence": False,
        "authority": "mechanical-family-operator-only",
        "settings": {
            "route": ROUTE,
            "times": list(TIMES),
            "canonicalTime": CANONICAL_TIME,
            "startsPerSeed": STARTS_PER_SEED,
            "challengersPerStart": CHALLENGERS_PER_START,
            "challengersPerArm": CHALLENGERS_PER_ARM,
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
            "nativeValid": sum(bool(r["valid"]) for r in native),
            "genericValid": sum(bool(r["valid"]) for r in generic),
            "projectedValid": sum(bool(r["valid"]) for r in projected),
            "genericLawFailures": sum(f == LAW_FAILURE for f in generic_failures),
            "projectedLawFailures": sum(f == LAW_FAILURE for f in projected_failures),
            "genericFailureModes": sorted(generic_failures),
            "projectedFailureModes": sorted(projected_failures),
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
