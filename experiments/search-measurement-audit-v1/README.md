# Search measurement audit v1

## Why this exists

The recent search-policy arc used two pieces of research instrumentation that were never validated as a pair:

1. a stochastic two-stage route vote (`>=2/3` seed wins -> route support; `>=4/5` routes -> general support);
2. matched-frame mean absolute pixel difference as the objective target-recovery distance for sparse line art.

Deterministic scheduler gates are proof-like: trajectory preservation either holds or does not. Search-quality comparisons are noisy stochastic measurements and need a different epistemic treatment.

This audit runs before any further topology, mutation-scale, or route-specific tuning.

No fresh seeds are consumed. Objective tests use already-consumed seeds `101,103,107` across all five representations and both local/global target regimes: 30 targets total.

## Part A — route-vote gate audit

For an odd number `n` of independent seed comparisons, the historical route gate supports a route when a strict majority wins. Five routes then pass the general gate at `>=4/5` route supports.

Compute exactly:

- route-support probability under per-seed win probability `p`;
- overall `>=4/5` probability;
- null false-positive rate at `p=0.5` for `n=3,9,21`;
- power at `p=0.55,0.60,0.65,0.70` for the same `n`.

### Falsification / retirement criterion

If the overall null pass probability remains above `0.10` as `n` grows, the two-stage route vote is not calibrated for confirmatory stochastic search-quality decisions and is retired from that role.

This does not affect deterministic scheduler pass/fail checks.

### Replacement direction

Do not choose a replacement decision threshold in this audit. Preserve continuous paired effects instead:

```text
route x seed paired delta
-> equal-route seed aggregate
-> continuous seed-level effect distribution
```

Future confirmatory rules must be designed only after the objective itself is validated and a meaningful effect scale exists.

## Part B — sparse-image objective audit

Current target distance is per-pixel grayscale MAE averaged across matched frames.

Each generated target is compared with controlled variants:

- `exact`: target itself;
- `shift3`: exact target translated three pixels horizontally, background-filled;
- `fade50`: exact target with ink amplitude halved toward the background;
- `blank`: pure background;
- `valid-alpha`: same target genome with alpha reduced to the valid lower range;
- `valid-neighbor`: one route-native valid mutation from the target;
- `unrelated-valid`: an independently generated valid common start from the same route.

The last three are real candidates evaluated by the existing mathematical checker. The first four are diagnostic image perturbations only.

### Current MAE falsification contract

A three-pixel translation is only `0.75%` of a 400-pixel canvas dimension and preserves the exact structure.

The current MAE is falsified as a structural target-recovery objective if **any** of the 30 targets satisfies:

```text
distance(blank, target) < distance(shift3, target)
```

One failure is decisive because this is a deterministic metric sanity contract, not a stochastic quality claim.

Also record, without making them hard gates:

- blank outranking a real valid route-native neighbor;
- blank outranking an unrelated valid candidate;
- distance versus candidate ink mass.

## Candidate sparse-shape metric

Test, but do not adopt, `sparse-shape-v1`:

1. foreground support is `pixel > 20`, matching the prototype occupancy threshold;
2. shape distance is `1 - tolerant F1`, using a 3-pixel support dilation on each side;
3. ink-mass error is relative absolute foreground-mass error;
4. total distance is:

```text
0.8 * shape_distance + 0.2 * ink_mass_error
```

Matched-frame distances are averaged over time.

### Candidate qualification contract

`sparse-shape-v1` earns a later benchmark-replacement experiment only if all 30 targets satisfy all of:

```text
exact distance == 0
shift3 distance < blank distance
fade50 distance < blank distance
valid-alpha distance < blank distance
blank distance >= 0.99
shift3 distance <= 0.25
```

The valid-neighbor and unrelated-valid comparisons remain diagnostics because route-native mutation does not guarantee semantic closeness.

Passing this audit does **not** authorize replacing the benchmark. It only authorizes a later replay of prior search-policy comparisons under a validated candidate metric.

## Boundary

This is research-instrument validation. It has no artistic-promotion authority, no representation-pruning authority, and no production/default effect.
