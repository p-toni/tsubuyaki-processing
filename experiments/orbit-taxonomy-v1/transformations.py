"""Experiment-only minimal closure transformations used by orbit-taxonomy-v1.

These functions intentionally add no genome parameters. They document the two
validity repairs that were tested over the existing recurrence genome.
"""
import math


def distributed_seam_correction(spine):
    sp = list(spine)
    if len(sp) < 2:
        return sp
    dx = sp[0][0] - sp[-1][0]
    dy = sp[0][1] - sp[-1][1]
    n = len(sp)
    return [(x + (i / (n - 1)) * dx, y + (i / (n - 1)) * dy) for i, (x, y) in enumerate(sp)]


def local_quadratic_bridge(spine):
    sp = list(spine)
    if len(sp) < 2:
        return sp
    a, b = sp[-1], sp[0]
    dx, dy = b[0] - a[0], b[1] - a[1]
    chord = max(1e-9, math.hypot(dx, dy))
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    nx, ny = -dy / chord, dx / chord
    bow = min(8.0, 0.12 * chord)
    c = (mx + bow * nx, my + bow * ny)
    nconn = max(16, min(96, int(chord * 2)))
    conn = []
    for k in range(1, nconn + 1):
        s = k / nconn
        om = 1 - s
        conn.append((
            om * om * a[0] + 2 * om * s * c[0] + s * s * b[0],
            om * om * a[1] + 2 * om * s * c[1] + s * s * b[1],
        ))
    return sp + conn
