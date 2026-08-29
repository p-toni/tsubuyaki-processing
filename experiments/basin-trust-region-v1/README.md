# Basin trust region v1

## Purpose

Start the post-#71 search architecture phase by testing the causal claim left by `hybrid-portfolio-search`:

> once broad search has found a useful mathematical basin, exploitation should preserve the dimensions that define that basin instead of continuing to mutate the whole genome.

This is **not** a new representation and not an artistic-quality benchmark. It is a mechanistic search pilot using only already-consumed seeds.

## Why this is a different research layer

#56–#71 tested local topology / scale / schedule knobs. #71 ended that line: `m=1.25` reproduced a positive point estimate but failed the fixed-sample confidence gate, so the default stays `m=1.0` and nearby knob tuning stops.

The hybrid portfolio evidence already showed the higher-level failure mode:

```text
broad discovery can find a good basin
-> generic exploitation can mutate away from the niche that made it good
```

The intervention here therefore changes **which genome dimensions are eligible during exploitation**, not mutation magnitude.

## Frozen parameter partitions

Every route genome is partitioned into three disjoint classes before execution:

1. `sampling` — render/discretization density; frozen during trust-region exploitation;
2. `identity` — topology/layout/coarse mathematical structure; frozen during trust-region exploitation;
3. `local` — deformation/detail/phase/time/material dimensions; eligible during trust-region exploitation.

The implementation asserts that the three sets are disjoint and exactly cover every genome key.

### recurrence

```text
sampling: samples
identity: base_r taper f1 f2 f4 sx sy side curl
local:    f3 f5 side_decay twist warp time time2 time3 time4 alpha
```

### orbit

```text
sampling: samples
identity: radius sx sy f1 f2 f3 dent dent_k
local:    lobe ripple asym phase asym_phase dent_phase warp fold fold2 side
          width_phase time time2 time3 time4 time5 alpha
```

### family

```text
sampling: root_nu root_nv organ_samples
identity: root_aspect root_w root_h split split_top organs fan organ_len
local:    root_fold root_freq root_time root_time2 root_twist organ_w
          organ_taper organ_freq organ_time motion_time ribs phase alpha
```

### sheet

```text
sampling: nu nv
identity: sx sy cavity cavity_top
local:    fold fold_freq wave wave_freq phase arch twist twist_freq
          time time2 time3 alpha
```

### filament

```text
sampling: samples
identity: sx sy fold f1
local:    fold2 f2 f3 f4 phase drift side taper time time2 time3 alpha
```

These are semantic/mathematical choices, not partitions tuned from target-recovery results.

## Population

Pilot seeds are the first 12 master seeds already consumed by #71:

```text
1009, 1013, 1019, 1021,
1031, 1033, 1039, 1049,
1051, 1061, 1063, 1069
```

All five current routes are fixed strata:

```text
recurrence, orbit, family, sheet, filament
```

No fresh seed is consumed. The remaining #71 seeds stay unused by this pilot so they can support at most one later consumed-seed partition diagnosis if this first partition is structurally wrong.

Smoke seed `9001` is infrastructure-only and excluded from analysis.

## Controlled targets

Each route×seed begins from the same three valid common starts used by the search-leverage benchmark. Start 1 is the hidden target ancestor.

Two target regimes are constructed.

### `same-basin`

Six accepted sequential mutations using **local keys only** at scale `0.65`.

By construction, target sampling + identity signatures exactly equal the ancestor signature.

### `identity-jump`

One accepted mutation restricted to **identity keys only** at scale `1.2`, followed by five accepted local-only mutations at scale `0.65`.

The identity mutation must actually change the frozen identity signature.

This is a specificity control: a trust region should help more when the target is inside the current basin than when reaching the target requires crossing the frozen identity boundary.

## Shared broad discovery

Before the policies fork, both receive exactly the same target-independent discovery pool:

```text
3 common starts
+ 4 ordinary broad mutations from each start
= 15 discovery candidates including starts
```

Discovery mutations use the current ordinary route mutator at scale `1.0`.

For each target regime, the qualified `sparse-geometry-v1` target selector picks the best representative within each basin and then the best discovered basin. This is an objective mechanistic oracle, not an artistic selector.

The selected basin/representative is therefore identical for both exploitation policies.

## Exploitation fork

Both policies receive the same selected representative and the same 20-candidate budget.

Parent/scale schedule is frozen from the current refine stage:

```text
first 14 events: parent = current champion, scale = 0.55
last  6 events: parent = original selected representative, scale = 1.20
```

Policies:

### `generic`

Uses the current route mutator unchanged. Any non-alpha genome key can be selected; alpha retains the current 25% jitter behavior.

### `trust-region`

Uses the same numeric perturbation law, scales, candidate budget and alpha-jitter probability, but the selected mutation key must come from the route's frozen `local` set.

Sampling and identity keys cannot change.

## RNG coupling

Candidate randomness is event-keyed with the existing `derived_seed(master_seed, *labels)` primitive.

The same route×seed×regime×event label is used by both exploitation policies. This prevents earlier winner divergence from shifting a stateful PRNG stream into unrelated future draws.

The distributions differ only where the intervention requires them to differ: generic chooses from the whole eligible genome; trust-region chooses from the local subspace.

## Metric and primary effects

The target objective is the exact qualified `sparse-geometry-v1` metric from #69.

For policy `p`:

```text
normalized improvement[p]
  = (selected-discovery-distance - final-best-distance[p])
    / selected-discovery-distance
```

Per route×seed×regime:

```text
delta = trust-region improvement - generic improvement
```

Primary stochastic replicate remains the complete master seed:

```text
same_basin_seed_effect[s] = mean over five route deltas on same-basin target
jump_seed_effect[s]       = mean over five route deltas on identity-jump target
interaction[s]            = same_basin_seed_effect[s] - jump_seed_effect[s]
```

## Hard invariants

The pilot fails mechanically if any of these fail:

- all route genome partitions are exact/disjoint;
- both policies start from the exact same discovered representative;
- both policies generate exactly 20 exploitation candidates;
- trust-region champion changes zero sampling/identity keys from the selected representative;
- same-basin target changes zero sampling/identity keys from its ancestor;
- identity-jump target changes at least one identity key;
- every expected route×seed block is present exactly once.

## Pilot decision rule

This is consumed-seed architecture triage, not confirmation. No p-value or adoption threshold is introduced.

Call the mechanism `PILOT_PROMISING` only if all hard invariants pass and both are true:

1. every leave-one-route-out mean of the **same-basin** delta is > 0;
2. mean interaction (`same-basin delta - identity-jump delta`) is > 0.

Otherwise call it `PILOT_MIXED`.

Route means, seed effects, target-ancestor basin recovery, validity yield and identity drift are diagnostics; routes are not converted into stochastic votes.

## Next boundary

If `PILOT_PROMISING`:

- freeze the partition and mechanism;
- preregister one fresh master-seed confirmation;
- only after mechanical confirmation test whether basin preservation improves artistic outcomes with independent/human evidence.

If `PILOT_MIXED`:

- do **not** consume fresh seeds;
- inspect which mathematical partition assumption failed;
- at most one partition revision may use the remaining already-consumed #71 seeds;
- if no coherent partition emerges, move up again to explicit archive / repertoire allocation rather than tuning local mutation knobs.

## Boundary

Experiment only. No production/default search change, representation pruning/promotion, artistic authority, or `SKILL.md` change.