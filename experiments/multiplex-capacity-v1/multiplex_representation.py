"""Neutral index-multiplexed geometry for multiplex-capacity-v1.

This is a mechanism probe, not a port of any public sketch. The same genome is
used by the full grammar and four ablations so the experiment can attribute
capacity to topology rather than to a larger parameter set.
"""
from __future__ import annotations

import math
from typing import Iterable

VARIANTS = (
    "multiplex-full",
    "multiplex-no-branch",
    "multiplex-regular-grid",
    "multiplex-no-reuse",
    "multiplex-no-singular",
)

# Search may mutate only dimensions that are phenotypically active in *every*
# variant. Mechanism-specific parameters still vary across independent starts,
# but an ablation cannot lose search budget merely because a removed mechanism
# makes some genome keys inert.
COMMON_MUTABLE_KEYS = (
    "slow_freq", "slow_amp", "fast1", "fast2", "fast_mix",
    "turn", "phase_latent", "cross", "cross2",
    "base_r", "radial_u", "radial_latent", "radial_fast",
    "weave", "y_latent", "motion", "sx", "sy", "time1", "time2", "time3",
)


def _clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value


def seed_genome(rng) -> dict[str, float]:
    return {
        "samples": rng.choice([2200, 2600, 3000]),
        "branches": rng.choice([2, 3, 4, 5]),
        "slow_freq": rng.uniform(0.55, 1.8),
        "slow_amp": rng.uniform(0.08, 0.42),
        "fast1": rng.uniform(1.8, 5.8),
        "fast2": rng.uniform(2.4, 8.2),
        "fast_mix": rng.uniform(0.35, 1.05),
        "branch_mix": rng.uniform(0.12, 0.62),
        "branch_phase": rng.uniform(0.35, 1.45),
        "turn": rng.uniform(1.0, 4.2),
        "phase_latent": rng.uniform(0.35, 2.1),
        "cross": rng.uniform(0.08, 0.62),
        "cross2": rng.uniform(0.03, 0.28),
        "base_r": rng.uniform(0.18, 0.48),
        "radial_u": rng.uniform(0.05, 0.32),
        "radial_latent": rng.uniform(0.08, 0.42),
        "radial_fast": rng.uniform(0.03, 0.18),
        "weave": rng.uniform(0.04, 0.24),
        "branch_spread": rng.uniform(0.08, 0.42),
        "y_latent": rng.uniform(0.03, 0.22),
        "motion": rng.uniform(0.02, 0.18),
        "singular_gain": rng.uniform(0.015, 0.11),
        "singular_floor": rng.uniform(0.16, 0.42),
        "singular_offset": rng.uniform(0.35, 1.25),
        "singular_cap": rng.uniform(1.5, 4.0),
        "sx": rng.uniform(105.0, 170.0),
        "sy": rng.uniform(85.0, 145.0),
        "time1": rng.uniform(18.0, 48.0),
        "time2": rng.uniform(20.0, 54.0),
        "time3": rng.uniform(14.0, 42.0),
        "alpha": rng.randint(28, 52),
    }


def mutate_genome(genome: dict[str, float], rng, scale: float = 1.0) -> dict[str, float]:
    """One-coordinate mutation with the historical +/-18% law.

    Only the common active parameter subset is eligible. Sampling density,
    branch-specific controls, and reciprocal-specific controls remain fixed per
    start so no ablation pays a no-op mutation tax.
    """
    out = dict(genome)
    key = rng.choice(COMMON_MUTABLE_KEYS)
    value = out[key]
    delta = rng.uniform(-0.18, 0.18) * (abs(value) if abs(value) > 1e-6 else 1.0) * scale
    out[key] = value + delta
    if rng.random() < 0.25:
        out["alpha"] = int(_clamp(out["alpha"] + rng.randint(-5, 5), 22, 60))
    out["sx"] = _clamp(float(out["sx"]), 70.0, 210.0)
    out["sy"] = _clamp(float(out["sy"]), 60.0, 190.0)
    out["time1"] = _clamp(float(out["time1"]), 7.0, 90.0)
    out["time2"] = _clamp(float(out["time2"]), 7.0, 90.0)
    out["time3"] = _clamp(float(out["time3"]), 7.0, 90.0)
    return out


def _coordinates(index: int, n: int, branches: int, variant: str) -> tuple[float, float, float, float]:
    """Return slow, residue, normalized raw index, and explicit second axis.

    Full multiplex uses quotient + residue + raw-index phase from one scalar
    index. regular-grid instead exposes two smooth coordinates explicitly.
    no-branch collapses the quotient/residue decomposition to one channel, so the
    branch-count parameter becomes genuinely inert in that ablation.
    """
    s = index / max(1, n - 1)
    if variant == "multiplex-regular-grid":
        nu = max(8, int(round(math.sqrt(n * 1.35))))
        nv = max(8, math.ceil(n / nu))
        iu = index % nu
        iv = min(nv - 1, index // nu)
        u = -1.0 + 2.0 * iu / max(1, nu - 1)
        v = -1.0 + 2.0 * iv / max(1, nv - 1)
        residue = round(((v + 1.0) / 2.0) * (branches - 1))
        b = (residue - (branches - 1) / 2.0) / max(1.0, (branches - 1) / 2.0)
        return u, b, s, v

    effective_branches = 1 if variant == "multiplex-no-branch" else branches
    quotient = index // effective_branches
    qn = math.ceil(n / effective_branches)
    u = -1.0 + 2.0 * quotient / max(1, qn - 1)
    if variant == "multiplex-no-branch":
        return u, 0.0, s, 0.0
    residue = index % effective_branches
    b = (residue - (effective_branches - 1) / 2.0) / max(1.0, (effective_branches - 1) / 2.0)
    return u, b, s, 0.0


def points(genome: dict[str, float], t: float, variant: str, width: int = 400, height: int = 400):
    if variant not in VARIANTS:
        raise ValueError(f"unknown multiplex variant {variant!r}")
    n = int(genome["samples"])
    branches = int(genome["branches"])
    phase_branches = 1 if variant == "multiplex-no-branch" else branches
    tau = 2.0 * math.pi
    out = []

    for index in range(n):
        u, b, s, grid_v = _coordinates(index, n, branches, variant)
        branch_phase = 0.0 if variant == "multiplex-no-branch" else b * genome["branch_phase"]

        if variant == "multiplex-regular-grid":
            fast_a = math.sin(tau * genome["fast1"] * grid_v + branch_phase)
            fast_b = math.cos(tau * genome["fast2"] * u - 0.7 * branch_phase)
            slow_driver = u
            second_driver = grid_v
        else:
            fast_a = math.sin(tau * genome["fast1"] * s * phase_branches + branch_phase)
            fast_b = math.cos(tau * genome["fast2"] * s * phase_branches - 0.7 * branch_phase)
            slow_driver = u
            second_driver = b

        slow_wave = math.sin(tau * genome["slow_freq"] * slow_driver - t / genome["time1"])
        slow_field = slow_driver + genome["slow_amp"] * slow_wave
        latent = math.hypot(
            slow_field,
            genome["fast_mix"] * fast_a + genome["branch_mix"] * second_driver,
        )

        if variant == "multiplex-no-reuse":
            phase_energy = abs(0.62 * slow_driver + 0.38 * fast_b)
            motion_energy = 0.45 + 0.55 * abs(fast_a)
            response_energy = abs(0.55 * slow_driver + 0.45 * fast_b)
            deform_energy = abs(0.50 * slow_driver + 0.50 * fast_a)
        else:
            phase_energy = latent
            motion_energy = latent
            response_energy = latent
            deform_energy = latent

        phase = (
            genome["turn"] * slow_driver
            + genome["phase_latent"] * phase_energy
            + genome["cross"] * slow_driver * fast_b
            + t / genome["time2"]
        )
        radius = (
            genome["base_r"]
            + genome["radial_u"] * (1.0 - min(1.0, slow_driver * slow_driver))
            + genome["radial_latent"] * latent
            + genome["radial_fast"] * fast_a
        )

        if variant == "multiplex-no-singular":
            response = 0.0
        else:
            denominator = max(
                genome["singular_floor"],
                abs(genome["singular_offset"] + response_energy + 0.22 * fast_b),
            )
            response = genome["singular_gain"] * min(genome["singular_cap"], 1.0 / denominator)

        x_unit = (
            radius * math.cos(phase)
            + genome["weave"] * fast_a * (0.35 + 0.65 * abs(second_driver))
            + response * fast_b
        )
        y_unit = (
            0.72 * slow_driver
            + genome["branch_spread"] * second_driver * (0.30 + 0.70 * (1.0 - min(1.0, slow_driver * slow_driver)))
            + genome["y_latent"] * deform_energy * math.sin(0.55 * phase + fast_b)
            + genome["cross2"] * slow_driver * fast_a
            + genome["motion"] * motion_energy * math.sin(t / genome["time3"] + 1.7 * fast_b)
            - 0.6 * response * fast_a
        )
        out.append((width / 2.0 + genome["sx"] * x_unit, height / 2.0 + genome["sy"] * y_unit))
    return out


def hard_valid(genome: dict[str, float], variant: str, times: Iterable[float], draw_points, width: int = 400, height: int = 400) -> dict[str, object]:
    finite = []
    in_frame = []
    bbox = []
    support = []
    for t in times:
        pts = points(genome, t, variant, width, height)
        finite.append(bool(pts) and all(math.isfinite(x) and math.isfinite(y) for x, y in pts))
        in_frame.append(sum(0 <= x < width and 0 <= y < height for x, y in pts) / len(pts) if pts else 0.0)
        xs = [x for x, y in pts if 0 <= x < width and 0 <= y < height]
        ys = [y for x, y in pts if 0 <= x < width and 0 <= y < height]
        if xs and ys:
            bbox.append(((max(xs) - min(xs)) / width, (max(ys) - min(ys)) / height))
        else:
            bbox.append((0.0, 0.0))
        im = draw_points(pts, int(genome["alpha"]))
        support.append(sum(1 for value in im.tobytes() if value > 20))

    failures = []
    if not all(finite):
        failures.append("non-finite or empty geometry")
    if min(in_frame, default=0.0) < 0.78:
        failures.append("too much geometry leaves canvas")
    if min((w for w, _h in bbox), default=0.0) < 0.20 or min((h for _w, h in bbox), default=0.0) < 0.20:
        failures.append("insufficient two-axis span")
    if min(support, default=0) < 140:
        failures.append("insufficient visible support")
    return {
        "valid": not failures,
        "failures": failures,
        "diagnostics": {
            "finiteByFrame": finite,
            "inFrameFractionByFrame": in_frame,
            "bboxByFrame": bbox,
            "visibleSupportByFrame": support,
            "occupancyUsedAsGate": False,
        },
    }
