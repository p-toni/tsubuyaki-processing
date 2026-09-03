from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np

STATE_DIM = 19
TARGET_DIM = 192
INPUT_DIM = STATE_DIM + TARGET_DIM
RESIDUAL_STEP = 0.02
TRAINING_HORIZON = 16
WINDOW = 4
BURN_IN_DEPTHS = (0, 4, 8, 12)

MODEL_SPECS = {
    "tied-burnin": {"kind": "tied", "hidden": 17, "modules": 1, "burnin": True, "initSeed": 766019},
    "tied-shallow": {"kind": "tied", "hidden": 17, "modules": 1, "burnin": False, "initSeed": 766037},
    "untied-equal-param": {"kind": "untied", "hidden": 1, "modules": 16, "burnin": True, "initSeed": 766053},
    "untied-equal-compute": {"kind": "untied", "hidden": 17, "modules": 16, "burnin": True, "initSeed": 766071},
}


def module_parameter_count(hidden: int) -> int:
    return hidden * INPUT_DIM + hidden + STATE_DIM * hidden + STATE_DIM


def model_parameter_count(spec: Dict[str, object]) -> int:
    return int(spec["modules"]) * module_parameter_count(int(spec["hidden"]))


def _init_module(hidden: int, seed: int) -> List[np.ndarray]:
    rng = np.random.default_rng(seed)
    return [
        rng.normal(0.0, 0.05, size=(hidden, INPUT_DIM)).astype(np.float64),
        np.zeros(hidden, dtype=np.float64),
        rng.normal(0.0, 0.05, size=(STATE_DIM, hidden)).astype(np.float64),
        np.zeros(STATE_DIM, dtype=np.float64),
    ]


def init_model(name: str) -> Dict[str, object]:
    spec = MODEL_SPECS[name]
    modules = [
        _init_module(int(spec["hidden"]), int(spec["initSeed"]) + 1009 * i)
        for i in range(int(spec["modules"]))
    ]
    return {
        "name": name,
        "kind": str(spec["kind"]),
        "hidden": int(spec["hidden"]),
        "modules": modules,
        "parameterCount": model_parameter_count(spec),
    }


def _module_index(model: Dict[str, object], absolute_step: int) -> int:
    return 0 if model["kind"] == "tied" else int(absolute_step) % TRAINING_HORIZON


def forward_step(
    x: np.ndarray,
    target_descriptor: np.ndarray,
    model: Dict[str, object],
    absolute_step: int,
):
    idx = _module_index(model, absolute_step)
    W1, b1, W2, b2 = model["modules"][idx]
    u = np.concatenate((x, target_descriptor), axis=1)
    h = np.tanh(u @ W1.T + b1)
    q = np.tanh(h @ W2.T + b2)
    pre = x + RESIDUAL_STEP * q
    nxt = np.clip(pre, -1.0, 1.0)
    clip_mask = ((pre > -1.0) & (pre < 1.0)).astype(np.float64)
    cache = (idx, x, u, h, q, clip_mask)
    return nxt, cache


def run_no_grad(
    x: np.ndarray,
    target_descriptor: np.ndarray,
    model: Dict[str, object],
    start_step: int,
    count: int,
) -> np.ndarray:
    cur = x
    for offset in range(int(count)):
        cur, _ = forward_step(cur, target_descriptor, model, start_step + offset)
    return cur


def _zero_grads(model: Dict[str, object]):
    return [[np.zeros_like(p) for p in module] for module in model["modules"]]


def tracked_window_loss_and_grads(
    x: np.ndarray,
    target_descriptor: np.ndarray,
    target_state: np.ndarray,
    model: Dict[str, object],
    start_step: int,
    window: int = WINDOW,
):
    caches = []
    states = []
    cur = x
    loss = 0.0
    for offset in range(int(window)):
        cur, cache = forward_step(cur, target_descriptor, model, start_step + offset)
        caches.append(cache)
        states.append(cur)
        loss += float(np.mean((cur - target_state) ** 2))
    loss /= int(window)

    grads = _zero_grads(model)
    dnext = np.zeros_like(cur)
    batch = x.shape[0]

    for offset in reversed(range(int(window))):
        state = states[offset]
        idx, prior, u, h, q, clip_mask = caches[offset]
        W1, _b1, W2, _b2 = model["modules"][idx]

        dstate = 2.0 * (state - target_state) / (batch * STATE_DIM * int(window)) + dnext
        dpre = dstate * clip_mask
        dq = RESIDUAL_STEP * dpre
        dout = dq * (1.0 - q * q)

        grads[idx][2] += dout.T @ h
        grads[idx][3] += dout.sum(axis=0)
        dh = dout @ W2
        da = dh * (1.0 - h * h)
        grads[idx][0] += da.T @ u
        grads[idx][1] += da.sum(axis=0)
        du = da @ W1
        dnext = dpre + du[:, :STATE_DIM]

    return loss, grads, states[-1]


def _global_grad_norm(grads) -> float:
    return math.sqrt(sum(float(np.sum(g * g)) for module in grads for g in module))


def train_model(
    name: str,
    target_states: np.ndarray,
    target_descriptors: np.ndarray,
    updates: int,
    schedule_seed: int,
    batch_size: int = 64,
    learning_rate: float = 0.002,
    noise_sigma: float = 0.40,
    beta1: float = 0.9,
    beta2: float = 0.999,
    epsilon: float = 1e-8,
    grad_clip: float = 1.0,
):
    if target_states.ndim != 2 or target_states.shape[1] != STATE_DIM:
        raise ValueError("target state matrix shape drift")
    if target_descriptors.shape != (target_states.shape[0], TARGET_DIM):
        raise ValueError("target descriptor matrix shape drift")

    model = init_model(name)
    spec = MODEL_SPECS[name]
    moments = [[np.zeros_like(p) for p in module] for module in model["modules"]]
    variances = [[np.zeros_like(p) for p in module] for module in model["modules"]]
    rng = np.random.default_rng(schedule_seed)
    losses = []
    burnin_counts = {str(depth): 0 for depth in BURN_IN_DEPTHS}

    for update in range(int(updates)):
        ids = rng.integers(0, target_states.shape[0], size=int(batch_size))
        target = target_states[ids]
        descriptor = target_descriptors[ids]
        start = np.clip(
            target + rng.normal(0.0, noise_sigma, size=target.shape),
            -1.0,
            1.0,
        )
        if bool(spec["burnin"]):
            burnin = int(rng.choice(BURN_IN_DEPTHS))
        else:
            burnin = 0
        burnin_counts[str(burnin)] = burnin_counts.get(str(burnin), 0) + 1

        detached = run_no_grad(start, descriptor, model, 0, burnin)
        loss, grads, _ = tracked_window_loss_and_grads(
            detached,
            descriptor,
            target,
            model,
            burnin,
            WINDOW,
        )
        losses.append(loss)

        norm = _global_grad_norm(grads)
        scale = 1.0 if norm <= grad_clip or norm <= 1e-15 else grad_clip / norm
        t = update + 1
        for mi, module in enumerate(model["modules"]):
            for pi, param in enumerate(module):
                grad = grads[mi][pi] * scale
                moments[mi][pi] = beta1 * moments[mi][pi] + (1.0 - beta1) * grad
                variances[mi][pi] = beta2 * variances[mi][pi] + (1.0 - beta2) * (grad * grad)
                mhat = moments[mi][pi] / (1.0 - beta1 ** t)
                vhat = variances[mi][pi] / (1.0 - beta2 ** t)
                param -= learning_rate * mhat / (np.sqrt(vhat) + epsilon)

    summary = {
        "name": name,
        "kind": model["kind"],
        "hidden": model["hidden"],
        "parameterCount": model["parameterCount"],
        "updates": int(updates),
        "scheduleSeed": int(schedule_seed),
        "batchSize": int(batch_size),
        "learningRate": float(learning_rate),
        "noiseSigma": float(noise_sigma),
        "residualStep": RESIDUAL_STEP,
        "window": WINDOW,
        "burninCounts": burnin_counts,
        "finalLoss": float(losses[-1]),
        "meanLast100Loss": float(np.mean(losses[-min(100, len(losses)):])),
        "checkpointSelection": "final-update-only",
    }
    return model, summary


def trajectory(
    model: Dict[str, object],
    start_state: np.ndarray,
    target_descriptor: np.ndarray,
    steps: int,
):
    if start_state.shape != (STATE_DIM,):
        raise ValueError("start state shape drift")
    if target_descriptor.shape != (TARGET_DIM,):
        raise ValueError("target descriptor shape drift")
    cur = start_state[None, :].astype(np.float64, copy=True)
    descriptor = target_descriptor[None, :].astype(np.float64, copy=False)
    states = [cur[0].copy()]
    step_norms = []
    for absolute_step in range(int(steps)):
        nxt, _ = forward_step(cur, descriptor, model, absolute_step)
        step_norms.append(float(np.linalg.norm(nxt[0] - cur[0])))
        cur = nxt
        states.append(cur[0].copy())
    return np.asarray(states), np.asarray(step_norms)


def save_models(path: Path, models: Dict[str, Dict[str, object]], metadata: Dict[str, object]) -> None:
    arrays = {}
    model_meta = {}
    for name, model in models.items():
        model_meta[name] = {
            "kind": model["kind"],
            "hidden": model["hidden"],
            "parameterCount": model["parameterCount"],
            "moduleCount": len(model["modules"]),
        }
        for mi, module in enumerate(model["modules"]):
            for pi, array in enumerate(module):
                arrays[f"{name}__m{mi}__p{pi}"] = array
    arrays["__metadata_json__"] = np.asarray(
        json.dumps({"models": model_meta, "metadata": metadata}, sort_keys=True)
    )
    np.savez_compressed(Path(path), **arrays)


def load_models(path: Path):
    with np.load(Path(path), allow_pickle=False) as data:
        payload = json.loads(str(data["__metadata_json__"]))
        models = {}
        for name, meta in payload["models"].items():
            modules = []
            for mi in range(int(meta["moduleCount"])):
                modules.append([
                    np.asarray(data[f"{name}__m{mi}__p{pi}"], dtype=np.float64).copy()
                    for pi in range(4)
                ])
            models[name] = {
                "name": name,
                "kind": meta["kind"],
                "hidden": int(meta["hidden"]),
                "parameterCount": int(meta["parameterCount"]),
                "modules": modules,
            }
    return models, payload["metadata"]
