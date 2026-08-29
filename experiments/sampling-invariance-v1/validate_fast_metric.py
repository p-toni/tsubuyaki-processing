from __future__ import annotations

import json
import random
import sys

from PIL import Image

import field as frozen_field

sys.modules.setdefault("sampling_invariance_field", frozen_field)

import capacity
import fast_binary_metric as fast


def shift(image: Image.Image, dx: int, dy: int) -> Image.Image:
    out = Image.new("L", image.size, capacity.BG)
    out.paste(image, (dx, dy))
    return out


def random_binary(seed: int, count: int) -> Image.Image:
    rng = random.Random(seed)
    data = [capacity.BG] * (capacity.W * capacity.H)
    for _ in range(count):
        x = rng.randrange(capacity.W)
        y = rng.randrange(capacity.H)
        data[y * capacity.W + x] = capacity.FG
    image = Image.new("L", (capacity.W, capacity.H))
    image.putdata(data)
    return image


def compare(candidate: Image.Image, target: Image.Image) -> float:
    original = capacity.metric.sparse_geometry_distance((candidate,), (target,))
    optimized = fast.sparse_geometry_distance((candidate,), (target,))
    diffs = [abs(float(original["distance"]) - float(optimized["distance"]))]
    diffs.extend(
        abs(float(original["components"][name]) - float(optimized["components"][name]))
        for name in ("placement", "shape", "extent", "mass")
    )
    diffs.append(abs(float(original["meanInkMass"]) - float(optimized["meanInkMass"])))
    diffs.append(abs(float(original["meanSupport"]) - float(optimized["meanSupport"])))
    return max(diffs)


def main() -> None:
    targets = capacity.build_targets()
    cases = []
    for target in targets:
        candidates = (
            ("exact", target.image),
            ("shift+1", shift(target.image, 1, 0)),
            ("shift-3+2", shift(target.image, -3, 2)),
            ("blank", Image.new("L", target.image.size, capacity.BG)),
            ("random-sparse", random_binary(7000 + len(cases), 900)),
            ("random-dense", random_binary(9000 + len(cases), 18000)),
        )
        for label, candidate in candidates:
            diff = compare(candidate, target.image)
            cases.append({"target": target.id, "candidate": label, "maxAbsoluteDifference": diff})

    max_diff = max(case["maxAbsoluteDifference"] for case in cases)
    result = {
        "experiment": "sampling-invariance-capacity-v1",
        "check": "fast-binary-metric-equivalence",
        "cases": len(cases),
        "maxAbsoluteDifference": max_diff,
        "tolerance": 1e-12,
        "pass": max_diff <= 1e-12,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
