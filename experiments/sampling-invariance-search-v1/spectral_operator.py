from __future__ import annotations

import math

import numpy as np

EPSILON = 1e-15


def normalize(coefficients: np.ndarray) -> np.ndarray:
    value = np.asarray(coefficients, dtype=float)
    norm = float(np.linalg.norm(value))
    if norm <= EPSILON:
        raise ValueError("coefficient vector norm vanished")
    return value / norm


def projective_angle(a: np.ndarray, b: np.ndarray) -> float:
    aa = normalize(a)
    bb = normalize(b)
    similarity = abs(float(aa @ bb))
    similarity = min(1.0, max(0.0, similarity))
    return math.acos(similarity)


def geodesic_mutate(
    coefficients: np.ndarray,
    rng: np.random.Generator,
    theta: float,
) -> np.ndarray:
    if not (0.0 < theta < math.pi / 2.0):
        raise ValueError("theta must lie strictly inside (0, pi/2)")
    parent = normalize(coefficients)
    for _ in range(128):
        direction = rng.normal(size=parent.shape)
        direction = direction - float(direction @ parent) * parent
        norm = float(np.linalg.norm(direction))
        if norm > EPSILON:
            direction /= norm
            child = math.cos(theta) * parent + math.sin(theta) * direction
            return normalize(child)
    raise RuntimeError("failed to draw nondegenerate tangent direction")
