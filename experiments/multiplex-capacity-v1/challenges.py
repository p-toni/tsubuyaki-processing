"""Frozen neutral challenge generators for multiplex-capacity-v1.

Challenge equations are intentionally different from multiplex_representation.py.
They encode structural demands, not copies of any public artwork. Randomness is
sampled only at the challenge-parameter level; point evaluation itself is smooth
and deterministic.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Challenge:
    id: str
    family: str
    variant: int
    smooth_plausible: bool


CHALLENGES = tuple(
    [Challenge(f"linked-{i}", "linked-submanifolds", i, i in (1, 3)) for i in range(1, 4)]
    + [Challenge(f"woven-{i}", "woven-single-index", i, i == 2) for i in range(1, 4)]
    + [Challenge(f"coupled-{i}", "radius-motion-coupling", i, i == 3) for i in range(1, 4)]
    + [Challenge(f"detail-{i}", "localized-curvature", i, True) for i in range(1, 4)]
)

CHALLENGE_IDS = tuple(c.id for c in CHALLENGES)
FAMILIES = tuple(dict.fromkeys(c.family for c in CHALLENGES))


def _rng(seed: int, challenge: Challenge) -> random.Random:
    family_code = FAMILIES.index(challenge.family) + 1
    return random.Random(seed * 10007 + family_code * 1009 + challenge.variant * 97 + 0x5EED)


def _linked(seed: int, challenge: Challenge, t: float, width: int, height: int):
    """Explicit phase-linked bands, no residue-class indexing or organ anchors."""
    rng = _rng(seed, challenge)
    lanes = 3 + (challenge.variant % 2)
    samples = 720
    base = rng.uniform(70, 104)
    eccentric = rng.uniform(0.72, 1.18)
    lobe = rng.uniform(0.08, 0.21)
    drift = rng.uniform(0.04, 0.13)
    phase_time = rng.uniform(21.0, 37.0)
    radial_time = rng.uniform(24.0, 46.0)
    lane_phase_step = rng.uniform(0.18, 0.42)
    lane_offset_step = rng.uniform(8.0, 17.0)
    points = []
    for lane in range(lanes):
        lane_phase = (lane - (lanes - 1) / 2.0) * lane_phase_step
        lane_offset = (lane - (lanes - 1) / 2.0) * lane_offset_step
        for j in range(samples):
            q = 2.0 * math.pi * j / samples
            phase = q + lane_phase + 0.10 * math.sin((2 + challenge.variant) * q - t / phase_time)
            radial = base * (1.0 + lobe * math.sin((2 + lane % 2) * q + t / radial_time))
            x = width / 2 + (radial + lane_offset) * math.cos(phase) + drift * base * math.sin(5 * q - t / 29.0)
            y = height / 2 + eccentric * (radial - 0.35 * lane_offset) * math.sin(phase) + 8.0 * math.sin(3 * q + lane_phase + t / 41.0)
            points.append((x, y))
    return points


def _woven(seed: int, challenge: Challenge, t: float, width: int, height: int):
    """One smooth parameter winds repeatedly through two apparent dimensions."""
    rng = _rng(seed, challenge)
    n = 2700
    a = rng.choice([3, 4, 5]) + challenge.variant
    b = rng.choice([5, 7, 8])
    amp_x = rng.uniform(115, 155)
    amp_y = rng.uniform(85, 132)
    carrier_time = rng.uniform(17.0, 31.0)
    weave_time = rng.uniform(31.0, 49.0)
    points = []
    for j in range(n):
        s = j / max(1, n - 1)
        q = 2.0 * math.pi * s
        carrier = math.sin((a + 0.35) * q - t / carrier_time)
        weave = math.sin(b * q + 0.55 * math.sin(2 * q) + t / weave_time)
        x = width / 2 + amp_x * (0.74 * math.sin(q) + 0.22 * carrier * math.cos((challenge.variant + 1) * q))
        y = height / 2 + amp_y * (0.62 * math.sin(2 * q + 0.2) + 0.25 * weave + 0.12 * carrier * weave)
        points.append((x, y))
    return points


def _coupled(seed: int, challenge: Challenge, t: float, width: int, height: int):
    """A radial field controls both static geometry and local motion magnitude."""
    rng = _rng(seed, challenge)
    n = 2500
    lobes = 2 + challenge.variant
    base = rng.uniform(72, 108)
    ax = rng.uniform(0.85, 1.25)
    ay = rng.uniform(0.78, 1.18)
    radial_strength = rng.uniform(0.18, 0.30)
    motion_strength = rng.uniform(8.0, 17.0)
    motion_time = rng.uniform(13.0, 27.0)
    points = []
    for j in range(n):
        q = 2.0 * math.pi * j / n
        field = 0.5 + 0.5 * math.sin(lobes * q + 0.35 * math.sin(3 * q))
        radial = base * (0.78 + radial_strength * field + 0.08 * math.cos((lobes + 2) * q))
        motion = field * motion_strength * math.sin(t / motion_time + 2.0 * q)
        phase = q + 0.07 * field * math.sin(t / 33.0 + q)
        x = width / 2 + ax * radial * math.cos(phase) + motion * math.cos(q + math.pi / 2)
        y = height / 2 + ay * radial * math.sin(phase) + motion * math.sin(q + math.pi / 2)
        points.append((x, y))
    return points


def _detail(seed: int, challenge: Challenge, t: float, width: int, height: int):
    """Explicit 2-D sheet with localized curvature and moving deformation spots."""
    rng = _rng(seed, challenge)
    nu, nv = 68, 52
    sx = rng.uniform(112, 146)
    sy = rng.uniform(86, 124)
    spot_u = rng.uniform(-0.45, 0.45)
    spot_v = rng.uniform(-0.35, 0.35)
    sigma = rng.uniform(0.16, 0.34)
    ridge_time = rng.uniform(19.0, 37.0)
    bend_strength = rng.uniform(0.06, 0.16)
    arch = rng.uniform(-0.05, 0.14)
    detail_strength = rng.uniform(10.0, 22.0)
    points = []
    for iv in range(nv):
        v = -1.0 + 2.0 * iv / max(1, nv - 1)
        for iu in range(nu):
            u = -1.0 + 2.0 * iu / max(1, nu - 1)
            r2 = (u - spot_u) ** 2 + (v - spot_v) ** 2
            local = math.exp(-r2 / max(1e-6, 2.0 * sigma * sigma))
            ridge = math.sin((4 + challenge.variant) * u + 2.0 * v - t / ridge_time)
            bend = bend_strength * math.sin(2.0 * v + t / 43.0)
            x = width / 2 + sx * (u + bend * (1 - u * u)) + (8 + 4 * challenge.variant) * local * ridge
            y = height / 2 + sy * (v + arch * u * u) + detail_strength * local * math.sin(3 * u - t / 31.0)
            points.append((x, y))
    return points


def points(seed: int, challenge: Challenge, t: float, width: int = 400, height: int = 400):
    if challenge.family == "linked-submanifolds":
        return _linked(seed, challenge, t, width, height)
    if challenge.family == "woven-single-index":
        return _woven(seed, challenge, t, width, height)
    if challenge.family == "radius-motion-coupling":
        return _coupled(seed, challenge, t, width, height)
    if challenge.family == "localized-curvature":
        return _detail(seed, challenge, t, width, height)
    raise ValueError(challenge.family)
