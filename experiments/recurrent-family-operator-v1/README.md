# Recurrent family operator v1

## Question

Can a small **weight-tied learned transition** repeatedly refine a real `family` mathematical form toward a target phenotype, continue improving materially beyond its 16-step training horizon, and remain hard-valid when run for up to 256 iterations?

This is the first isolated experiment released by the recurrent-operator roadmap after #135 closed the family projected-spectral artistic chain.

It is not an artistic experiment and does not modify production search.

## Why this is distinct

Existing search work mostly scales test-time compute by evaluating more candidate forms. This experiment tests a different computation primitive:

```text
state_0
  -> F_theta(state_0, target phenotype)
  -> F_theta(state_1, target phenotype)
  -> ...
```

The same learned transition is intentionally reapplied to its own outputs. The target is mechanical reconstruction of a held-out form from the incumbent `family` grammar; there is no aesthetic or semantic scorer.

This is not a learned world model. The model does not predict `state + action -> consequence` for an external controller. It directly implements `state -> next state`.

## Representation/state contract

Route: `family` only.

The transition may change exactly the 19 continuous native family parameters:

```text
root_aspect root_w root_h split split_top root_fold root_freq
root_time root_time2 root_twist fan organ_w organ_taper organ_freq
organ_len organ_time motion_time ribs phase
```

Each parameter is linearly normalized from its frozen native seed range into `[-1,1]`.

The discrete/native identity fields remain fixed from the target for the entire trajectory:

```text
root_nu root_nv organs organ_samples alpha
```

The ordinary production `family` checker remains external authority. The learned model cannot redefine hard validity or the sibling-scale law.

## Target observation

The model never receives the target genome at inference.

Its target observation is a 192-value phenotype descriptor:

- render the target at `t=30,90,150`;
- threshold each 400x400 grayscale frame at the existing support threshold `>20`;
- average-pool the binary support into an 8x8 grid;
- concatenate the three 64-value grids.

Training may use the known target genome as supervision; evaluation supplies only this phenotype descriptor plus the current state.

## Learned transition

Every transition module is a residual tanh MLP:

```text
u = concat(current 19-D normalized state, 192-D target descriptor)
h = tanh(W1 u + b1)
d = tanh(W2 h + b2)
next = clip(current + 0.02 * d, -1, 1)
```

The small `0.02` residual step is frozen so solving requires repeated application rather than unconstrained one-shot replacement.

### Main model — tied + late-state burn-in

- one shared transition module;
- hidden width `17`;
- parameter count `3946`;
- training horizon `16`;
- every optimization batch chooses burn-in depth uniformly from `{0,4,8,12}`;
- burn-in iterations run without gradient tracking;
- gradients are propagated through exactly the following `4` recurrent steps;
- loss is mean normalized-parameter MSE to the hidden training target over those four tracked states.

### Control A — tied shallow

Identical architecture, parameter count, optimizer, data, and four-step gradient window, but burn-in depth is always `0`.

This isolates whether practice on later recurrent states improves long-horizon stability.

### Control B — untied equal-parameter stack

- 16 distinct transition modules;
- hidden width `1` per module;
- total parameter count `4000` (within 1.4% of the tied model);
- same burn-in depths and four-step truncated-gradient windows;
- training uses absolute modules 0..15;
- inference beyond step 16 repeats the learned 16-module cycle.

This is the fixed-total-parameter control.

### Control C — untied equal-step-compute stack

- 16 distinct transition modules;
- hidden width `17` per module;
- total parameter count `63136`;
- same per-step architecture/compute as the tied model but ~16x parameters;
- same training schedule and 16-module cyclic inference beyond the training horizon.

This prevents a tied advantage from being attributed only to a stronger per-step module under the fixed-parameter comparison.

## Frozen training protocol

Authoritative training corpus master seed: `766001`.

- build exactly 256 hard-valid target forms from deterministic route-prior `family` draws;
- invalid training target draws are discarded deterministically and consume their draw; maximum 512 draws;
- all four models use the exact same target corpus;
- optimizer schedule seed: `766089`;
- mini-batch size: `64`;
- optimizer updates per model: `1600`;
- Adam: lr `0.002`, beta1 `0.9`, beta2 `0.999`, epsilon `1e-8`;
- global gradient norm clip: `1.0`;
- training start state: target normalized state plus iid Gaussian noise sigma `0.40`, clipped to `[-1,1]`;
- gradient window length: `4`.

Weight initialization seeds:

```text
tied-burnin          766019
tied-shallow         766037
untied-equal-param   766053
untied-equal-compute 766071
```

No training/validation curve is used to choose a checkpoint. The final update `1600` is the only authoritative checkpoint.

Excluded smoke uses training seed `766999` and evaluation seed `767999` with a deliberately tiny update count only to exercise code/invariants. It is not inferential evidence.

## Fresh confirmatory evaluation

Authoritative master seeds:

```text
767003 767019 767037 767053 767071
767089 767107 767127 767149 767167
767181 767199 767223 767239 767257
767277 767293 767311 767331 767349
```

For each master seed:

1. deterministically draw the first hard-valid native `family` target, with at most 32 route-prior draws;
2. preserve its five discrete fields exactly;
3. generate one Gaussian perturbation direction for the 19 continuous normalized parameters;
4. try fixed perturbation scales `0.40 * 0.75^k`, `k=0..7`, and select the first hard-valid perturbed start;
5. the same target and exact same valid start are given to all four learned models;
6. no evaluation seed is resampled based on model outcome.

Evaluation horizons:

```text
0 1 2 4 8 16 32 64 128 256
```

At every horizon, reconstruct the native genome, run the ordinary hard-validity checker, and measure three-frame structural recovery against the target with the existing sparse-grayscale metric:

```text
recovery = 1 - sparse_geometry_distance(candidate[t=30,90,150], target[t=30,90,150])
```

Also record normalized parameter MSE, state-step norms, bound saturation, sibling-scale-law failures, fixed-point behavior, and 2-cycle diagnostics.

## Current-search references

For each authoritative seed, the same valid start is also handed to the existing search runtime for two target-blind 20-challenger reference trajectories:

- `native-only`;
- `native-family-projected-spectral-50-50-v1`.

The target recovery metric is applied only after each search trajectory is complete. These references are descriptive and do not enter the recurrent gate.

## Inference / aggregation

Bootstrap unit: authoritative master seed.

One-sided 95% bootstrap lower bounds use 50,000 draws with reducer seed `767555001`.

Existing project meaningful-recovery bar: `0.005`.

### Gate A — recurrent viability

All are required:

1. complete 20-seed rectangle with all target/start/data invariants;
2. tied-burnin hard-valid rate >=95% independently at horizons 32, 64, 128, and 256;
3. zero tied-burnin sibling-scale-law failures at horizons 16, 32, 64, 128, and 256;
4. mean tied-burnin recovery gain `R128 - R16 >= 0.005`;
5. one-sided 95% bootstrap lower bound for `R128 - R16` >0;
6. mean tied-burnin recovery gain `R256 - R16 >= 0.005`;
7. one-sided 95% bootstrap lower bound for `R256 - R16` >0;
8. no material late collapse: mean `R256 >= R128 - 0.005`.

### Gate B — weight-sharing efficiency

All are required:

1. tied-burnin mean recovery at 128 exceeds untied-equal-parameter by >=`0.005`;
2. the one-sided 95% bootstrap lower bound of that paired difference >0;
3. tied-burnin is non-inferior to the ~16x larger equal-step-compute untied stack at 128 within `0.005`;
4. tied-burnin is non-inferior to the ~16x larger equal-step-compute untied stack at 256 within `0.005`.

### Diagnostic — late-state burn-in

`lateStateTrainingAddsTailStability` is true only if:

- tied-burnin recovery at 256 exceeds tied-shallow recovery at 256 by >=`0.003`; and
- the one-sided 95% bootstrap lower bound of that paired difference >0.

This diagnostic does not veto recurrent viability. A useful recurrent operator may exist even if this particular burn-in schedule does not isolate an additional effect.

## Terminal decisions

`RECURRENT_FAMILY_OPERATOR_PROMISING`

- Gate A passes;
- Gate B passes.

This permits one fresh second experiment to test generality or downstream search integration. It does not authorize production use or artistic claims.

`RECURRENT_FAMILY_ITERATION_PRESENT_TYING_EFFICIENCY_NOT_DEMONSTRATED`

- Gate A passes;
- Gate B fails.

This establishes long-horizon learned iteration but does not support the weight-sharing efficiency claim. Do not tune on consumed `766/767` evidence; any follow-up must change the scientific question materially.

`RECURRENT_FAMILY_OPERATOR_NOT_PROMISING`

- Gate A fails.

Close this exact architecture/training-horizon/residual-step hypothesis. No nearby width, step-size, burn-in-depth, seed, or horizon tuning on consumed `766/767` evidence.

## Visual-review boundary

No human or model artistic judgment is collected. This experiment is mechanical only.
