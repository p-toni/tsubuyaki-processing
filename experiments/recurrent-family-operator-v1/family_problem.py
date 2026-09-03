from __future__ import annotations

import random
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
METRIC_DIR = ROOT / "experiments" / "spectral-material-control-v1"
for p in (PROTO, METRIC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import core
import fast_grayscale_metric as metric
import search_engine
from rng_streams import derived_seed

ROUTE = "family"
TIMES = tuple(core.TIMES)
SUPPORT_THRESHOLD = 20
LAW_FAILURE = "shared family law loses sibling-scale coherence"

CONTINUOUS_RANGES = OrderedDict([
    ("root_aspect", (0.75, 1.05)),
    ("root_w", (65.0, 95.0)),
    ("root_h", (50.0, 80.0)),
    ("split", (0.08, 0.20)),
    ("split_top", (0.25, 0.70)),
    ("root_fold", (0.05, 0.22)),
    ("root_freq", (2.5, 5.5)),
    ("root_time", (16.0, 42.0)),
    ("root_time2", (18.0, 44.0)),
    ("root_twist", (4.0, 15.0)),
    ("fan", (0.8, 1.4)),
    ("organ_w", (5.0, 14.0)),
    ("organ_taper", (0.7, 1.6)),
    ("organ_freq", (2.2, 5.4)),
    ("organ_len", (42.0, 78.0)),
    ("organ_time", (12.0, 28.0)),
    ("motion_time", (16.0, 34.0)),
    ("ribs", (1.4, 3.5)),
    ("phase", (0.45, 1.0)),
])
DISCRETE_KEYS = ("root_nu", "root_nv", "organs", "organ_samples", "alpha")
STATE_KEYS = tuple(CONTINUOUS_RANGES)


def brief(mode: str | None = None) -> Dict[str, object]:
    out: Dict[str, object] = {
        "name": "recurrent-family-operator-v1",
        "artistic_intent": "mechanical target reconstruction only; no artistic authority",
        "routes": [ROUTE],
        "bbox_target": [0.55, 0.82],
        "starts_per_route": 1,
        "explore_per_basin": 4,
        "roundA_per_survivor": 4,
        "total_extra_budget": 12,
    }
    if mode is not None:
        out["mutation_portfolio"] = mode
    return out


def normalize_genome(genome: Dict[str, object]) -> np.ndarray:
    values = []
    for key, (lo, hi) in CONTINUOUS_RANGES.items():
        value = float(genome[key])
        values.append(-1.0 + 2.0 * (value - lo) / (hi - lo))
    return np.asarray(values, dtype=np.float64)


def genome_from_state(state: np.ndarray, template: Dict[str, object]) -> Dict[str, object]:
    state = np.asarray(state, dtype=np.float64)
    if state.shape != (len(STATE_KEYS),):
        raise ValueError(f"state shape drift: {state.shape}")
    out = dict(template)
    clipped = np.clip(state, -1.0, 1.0)
    for i, (key, (lo, hi)) in enumerate(CONTINUOUS_RANGES.items()):
        out[key] = lo + (float(clipped[i]) + 1.0) * 0.5 * (hi - lo)
    for key in DISCRETE_KEYS:
        out[key] = template[key]
    return out


def evaluate_genome(genome: Dict[str, object], cid: str = "F") -> core.Candidate:
    cand = core.Candidate(cid, ROUTE, cid, dict(genome), None, "recurrent-eval")
    core.evaluate_candidate(cand, brief())
    return cand


def target_frames(genome: Dict[str, object]):
    cand = core.Candidate("T", ROUTE, "T", dict(genome), None, "target")
    return tuple(core.render_candidate_frame(cand, t) for t in TIMES)


def phenotype_descriptor(genome: Dict[str, object]) -> np.ndarray:
    frames = target_frames(genome)
    pooled = []
    for image in frames:
        array = np.frombuffer(image.tobytes(), dtype=np.uint8).reshape((core.H, core.W))
        mask = (array > SUPPORT_THRESHOLD).astype(np.float64)
        # 400 is exactly divisible by 8; pool binary support over 50x50 cells.
        grid = mask.reshape(8, core.H // 8, 8, core.W // 8).mean(axis=(1, 3))
        pooled.extend(grid.reshape(-1).tolist())
    result = np.asarray(pooled, dtype=np.float64)
    if result.shape != (192,):
        raise AssertionError(f"descriptor shape drift: {result.shape}")
    return result


def recovery(genome: Dict[str, object], target_image_frames) -> float:
    frames = target_frames(genome)
    return 1.0 - float(metric.sparse_geometry_distance(frames, target_image_frames)["distance"])


def candidate_summary(genome: Dict[str, object], target_image_frames) -> Dict[str, object]:
    cand = evaluate_genome(genome)
    checks = cand.checks
    law_failures = sum(f == LAW_FAILURE for f in checks.get("failures", []))
    sibling = checks.get("diagnostics", {}).get("siblingLengthCVByFrame", [])
    return {
        "valid": bool(checks.get("valid", False)),
        "lawFailures": int(law_failures),
        "maxSiblingLengthCV": float(max(sibling)) if sibling else None,
        "recovery": recovery(genome, target_image_frames),
    }


def _route_prior_genome(master_seed: int, namespace: str, draw_index: int):
    rng = random.Random(derived_seed(master_seed, namespace, int(draw_index)))
    return core.ROUTES[ROUTE]["seed"](rng)


def first_hard_valid_target(master_seed: int, namespace: str, max_draws: int = 32):
    for draw in range(int(max_draws)):
        genome = _route_prior_genome(master_seed, namespace, draw)
        cand = evaluate_genome(genome, f"T{draw+1}")
        if cand.checks.get("valid", False):
            return genome, draw + 1
    raise RuntimeError(f"no hard-valid family target in {max_draws} deterministic draws")


def build_training_corpus(master_seed: int, count: int = 256, max_draws: int = 512):
    states = []
    descriptors = []
    accepted_draws = []
    for draw in range(int(max_draws)):
        genome = _route_prior_genome(master_seed, "recurrent-family-train-target-v1", draw)
        cand = evaluate_genome(genome, f"TR{draw+1}")
        if not cand.checks.get("valid", False):
            continue
        states.append(normalize_genome(genome))
        descriptors.append(phenotype_descriptor(genome))
        accepted_draws.append(draw)
        if len(states) == int(count):
            break
    if len(states) != int(count):
        raise RuntimeError(f"training corpus obtained {len(states)}/{count} valid targets")
    return np.asarray(states), np.asarray(descriptors), accepted_draws


def valid_perturbed_start(target_genome: Dict[str, object], master_seed: int):
    target_state = normalize_genome(target_genome)
    rng = np.random.default_rng(derived_seed(master_seed, "recurrent-family-eval-start-v1"))
    direction = rng.normal(0.0, 1.0, size=target_state.shape)
    scales = [0.40 * (0.75 ** k) for k in range(8)]
    for retry, scale in enumerate(scales):
        state = np.clip(target_state + scale * direction, -1.0, 1.0)
        genome = genome_from_state(state, target_genome)
        cand = evaluate_genome(genome, f"S{retry+1}")
        if cand.checks.get("valid", False):
            return state, genome, retry, scale
    raise RuntimeError("fixed perturbation backoff did not yield a hard-valid start")


def search_reference(
    start_genome: Dict[str, object],
    target_image_frames,
    seed: int,
    mode: str,
    out_dir: Path,
):
    start = core.Candidate("FS1", ROUTE, "FS1", dict(start_genome), None, "start")
    state, report = search_engine.run_search_from_starts(
        brief(mode),
        int(seed),
        Path(out_dir),
        [start],
    )
    # Target scoring is intentionally delayed until the full target-blind search exists.
    valid = [c for c in state.candidates.values() if c.checks.get("valid", False)]
    scores = [recovery(c.genome, target_image_frames) for c in valid]
    return {
        "bestArchiveRecovery": float(max(scores)),
        "validCandidateCount": len(valid),
        "totalCandidateCount": len(state.candidates),
        "selectionStatus": report["selectionStatus"],
        "provisionalChampion": report["provisionalChampion"],
        "generationOperatorCounts": report["generationOperatorCounts"],
    }
