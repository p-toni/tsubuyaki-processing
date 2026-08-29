#!/usr/bin/env python3
"""Route-aware genome partitions and restricted numeric mutations for basin trust regions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class GenomePartition:
    sampling: tuple[str, ...]
    identity: tuple[str, ...]
    local: tuple[str, ...]

    @property
    def frozen(self) -> tuple[str, ...]:
        return self.sampling + self.identity


PARTITIONS: Mapping[str, GenomePartition] = {
    "recurrence": GenomePartition(
        sampling=("samples",),
        identity=("base_r", "taper", "f1", "f2", "f4", "sx", "sy", "side", "curl"),
        local=("f3", "f5", "side_decay", "twist", "warp", "time", "time2", "time3", "time4", "alpha"),
    ),
    "orbit": GenomePartition(
        sampling=("samples",),
        identity=("radius", "sx", "sy", "f1", "f2", "f3", "dent", "dent_k"),
        local=(
            "lobe", "ripple", "asym", "phase", "asym_phase", "dent_phase", "warp",
            "fold", "fold2", "side", "width_phase", "time", "time2", "time3",
            "time4", "time5", "alpha",
        ),
    ),
    "family": GenomePartition(
        sampling=("root_nu", "root_nv", "organ_samples"),
        identity=("root_aspect", "root_w", "root_h", "split", "split_top", "organs", "fan", "organ_len"),
        local=(
            "root_fold", "root_freq", "root_time", "root_time2", "root_twist",
            "organ_w", "organ_taper", "organ_freq", "organ_time", "motion_time",
            "ribs", "phase", "alpha",
        ),
    ),
    "sheet": GenomePartition(
        sampling=("nu", "nv"),
        identity=("sx", "sy", "cavity", "cavity_top"),
        local=(
            "fold", "fold_freq", "wave", "wave_freq", "phase", "arch", "twist",
            "twist_freq", "time", "time2", "time3", "alpha",
        ),
    ),
    "filament": GenomePartition(
        sampling=("samples",),
        identity=("sx", "sy", "fold", "f1"),
        local=("fold2", "f2", "f3", "f4", "phase", "drift", "side", "taper", "time", "time2", "time3", "alpha"),
    ),
}


def partition_for(route: str) -> GenomePartition:
    try:
        return PARTITIONS[route]
    except KeyError as exc:
        raise KeyError(f"no trust-region partition for route {route!r}") from exc


def validate_partition(route: str, genome: Mapping[str, object]) -> None:
    p = partition_for(route)
    groups = [set(p.sampling), set(p.identity), set(p.local)]
    if any(groups[i] & groups[j] for i in range(len(groups)) for j in range(i + 1, len(groups))):
        raise AssertionError(f"overlapping genome partition for {route}")
    declared = set().union(*groups)
    actual = set(genome)
    if declared != actual:
        raise AssertionError(
            f"partition mismatch for {route}: missing={sorted(actual - declared)} extra={sorted(declared - actual)}"
        )


def signature(genome: Mapping[str, object], keys: Sequence[str]) -> tuple[tuple[str, object], ...]:
    return tuple((key, genome[key]) for key in keys)


def frozen_signature(route: str, genome: Mapping[str, object]) -> tuple[tuple[str, object], ...]:
    p = partition_for(route)
    return signature(genome, p.frozen)


def identity_signature(route: str, genome: Mapping[str, object]) -> tuple[tuple[str, object], ...]:
    return signature(genome, partition_for(route).identity)


def changed_keys(a: Mapping[str, object], b: Mapping[str, object], keys: Sequence[str]) -> list[str]:
    return [key for key in keys if a[key] != b[key]]


def changed_frozen_keys(route: str, a: Mapping[str, object], b: Mapping[str, object]) -> list[str]:
    return changed_keys(a, b, partition_for(route).frozen)


def changed_identity_keys(route: str, a: Mapping[str, object], b: Mapping[str, object]) -> list[str]:
    return changed_keys(a, b, partition_for(route).identity)


def _mutate_numeric_keys(genome: Mapping[str, object], rng, scale: float, keys: Sequence[str], *, alpha_jitter: bool) -> dict:
    """Apply the current ±18% single-key numeric law inside a declared key set.

    This intentionally mirrors `representations.mutate_numeric` rather than
    inventing a new local step size. The intervention is key eligibility only.
    """
    out = dict(genome)
    selectable = [key for key in keys if key != "alpha"]
    if not selectable:
        raise ValueError("restricted mutation needs at least one non-alpha key")
    key = rng.choice(selectable)
    value = genome[key]
    if not isinstance(value, (int, float)):
        raise TypeError(f"restricted mutation key {key!r} is not numeric")
    new_value = value + rng.uniform(-0.18, 0.18) * (abs(value) if abs(value) > 1e-6 else 1) * scale
    out[key] = max(1, int(round(new_value))) if isinstance(value, int) else new_value

    if alpha_jitter and "alpha" in keys and "alpha" in out and rng.random() < 0.25:
        out["alpha"] = int(max(22, min(60, out["alpha"] + rng.randint(-5, 5))))
    return out


def trust_region_mutate(route: str, genome: Mapping[str, object], rng, scale: float = 1.0) -> dict:
    validate_partition(route, genome)
    return _mutate_numeric_keys(genome, rng, scale, partition_for(route).local, alpha_jitter=True)


def identity_mutate(route: str, genome: Mapping[str, object], rng, scale: float = 1.0) -> dict:
    validate_partition(route, genome)
    return _mutate_numeric_keys(genome, rng, scale, partition_for(route).identity, alpha_jitter=False)
