"""Explicit mathematical basin identity for repertoire search.

Prepared after the consumed-seed trust-region pilot (#72). The partition is an
exact promotion of that pilot's frozen intervention boundary. This module does
not change search behavior by itself.

Important distinction:
- `identity` defines the mathematical basin.
- `sampling` is execution/resolution state and is tracked separately.
- a trust region freezes both identity and sampling, but changing resolution
  alone does not create a new mathematical basin.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping, Sequence


@dataclass(frozen=True)
class GenomePartition:
    sampling: tuple[str, ...]
    identity: tuple[str, ...]
    local: tuple[str, ...]

    @property
    def trust_frozen(self) -> tuple[str, ...]:
        return self.sampling + self.identity


# Exact key partition frozen by experiments/basin-trust-region-v1/policy.py.
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
        raise KeyError(f"no basin partition for route {route!r}") from exc


def validate_partition(route: str, genome: Mapping[str, object]) -> None:
    partition = partition_for(route)
    groups = [set(partition.sampling), set(partition.identity), set(partition.local)]
    if any(groups[i] & groups[j] for i in range(len(groups)) for j in range(i + 1, len(groups))):
        raise AssertionError(f"overlapping basin partition for {route}")
    declared = set().union(*groups)
    actual = set(genome)
    if declared != actual:
        raise AssertionError(
            f"basin partition mismatch for {route}: "
            f"missing={sorted(actual - declared)} extra={sorted(declared - actual)}"
        )


def signature(genome: Mapping[str, object], keys: Sequence[str]) -> tuple[tuple[str, object], ...]:
    return tuple((key, genome[key]) for key in keys)


def identity_signature(route: str, genome: Mapping[str, object]) -> tuple[tuple[str, object], ...]:
    validate_partition(route, genome)
    return signature(genome, partition_for(route).identity)


def sampling_signature(route: str, genome: Mapping[str, object]) -> tuple[tuple[str, object], ...]:
    validate_partition(route, genome)
    return signature(genome, partition_for(route).sampling)


def trust_region_signature(route: str, genome: Mapping[str, object]) -> tuple[tuple[str, object], ...]:
    validate_partition(route, genome)
    return signature(genome, partition_for(route).trust_frozen)


def _stable_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BasinIdentity:
    route: str
    identity: tuple[tuple[str, object], ...]
    basin_id: str

    @classmethod
    def from_genome(cls, route: str, genome: Mapping[str, object]) -> "BasinIdentity":
        ident = identity_signature(route, genome)
        digest = _stable_digest({"route": route, "identity": ident})[:16]
        return cls(route=route, identity=ident, basin_id=f"{route}:{digest}")


def same_basin(route: str, a: Mapping[str, object], b: Mapping[str, object]) -> bool:
    return identity_signature(route, a) == identity_signature(route, b)


def same_trust_region(route: str, a: Mapping[str, object], b: Mapping[str, object]) -> bool:
    return trust_region_signature(route, a) == trust_region_signature(route, b)


def changed_keys(a: Mapping[str, object], b: Mapping[str, object], keys: Sequence[str]) -> tuple[str, ...]:
    return tuple(key for key in keys if a[key] != b[key])


def changed_identity_keys(route: str, a: Mapping[str, object], b: Mapping[str, object]) -> tuple[str, ...]:
    return changed_keys(a, b, partition_for(route).identity)


def changed_sampling_keys(route: str, a: Mapping[str, object], b: Mapping[str, object]) -> tuple[str, ...]:
    return changed_keys(a, b, partition_for(route).sampling)


def changed_local_keys(route: str, a: Mapping[str, object], b: Mapping[str, object]) -> tuple[str, ...]:
    return changed_keys(a, b, partition_for(route).local)
