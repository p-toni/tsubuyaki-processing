from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTROL_DIR = ROOT / "experiments" / "spectral-material-control-v1"
sys.path.insert(0, str(CONTROL_DIR))

from spectral_control import warp_geometry


def _length(a, b) -> float:
    return math.hypot(float(b[0]) - float(a[0]), float(b[1]) - float(a[1]))


def project_family_terminal_scale(native: dict, warped: dict) -> dict:
    """Project a generic spectral warp back onto the frozen family sibling-scale law.

    Root points and anchors remain exactly as produced by the generic spectral
    deformation. Each organ retains its warped shape directions, but all warped
    offsets around that sibling's warped anchor receive one scalar correction so
    its anchor->terminal length exactly matches the native sibling length.
    """
    native_anchors = list(native.get("anchors", []))
    native_organs = list(native.get("organs", []))
    warped_anchors = list(warped.get("anchors", []))
    warped_organs = list(warped.get("organs", []))
    if not (
        len(native_anchors)
        == len(native_organs)
        == len(warped_anchors)
        == len(warped_organs)
    ):
        raise ValueError("family organ/anchor topology drift")

    projected_organs = []
    for native_anchor, native_organ, warped_anchor, warped_organ in zip(
        native_anchors, native_organs, warped_anchors, warped_organs
    ):
        if not native_organ or not warped_organ:
            raise ValueError("family projection requires non-empty sibling organs")
        native_length = _length(native_anchor, native_organ[-1])
        warped_length = _length(warped_anchor, warped_organ[-1])
        if not math.isfinite(native_length) or native_length <= 1e-9:
            raise ValueError("degenerate native family terminal length")
        if not math.isfinite(warped_length) or warped_length <= 1e-9:
            raise ValueError("degenerate warped family terminal length")
        scale = native_length / warped_length
        ax, ay = float(warped_anchor[0]), float(warped_anchor[1])
        projected_organs.append(
            [
                (ax + scale * (float(x) - ax), ay + scale * (float(y) - ay))
                for x, y in warped_organ
            ]
        )

    out = dict(warped)
    out["organs"] = projected_organs
    out["all"] = list(out.get("root", [])) + [
        point for organ in projected_organs for point in organ
    ]
    return out


def warp_family_projected(
    field,
    native_geometry: dict,
    amplitude: float,
    width: int,
    height: int,
    *,
    rms: float,
) -> dict:
    generic = warp_geometry(
        field,
        native_geometry,
        amplitude,
        width,
        height,
        rms=rms,
    )
    return project_family_terminal_scale(native_geometry, generic)


def terminal_length_error(native: dict, projected: dict) -> float:
    errors = []
    for na, no, pa, po in zip(
        native["anchors"], native["organs"], projected["anchors"], projected["organs"]
    ):
        errors.append(abs(_length(na, no[-1]) - _length(pa, po[-1])))
    return max(errors, default=0.0)
