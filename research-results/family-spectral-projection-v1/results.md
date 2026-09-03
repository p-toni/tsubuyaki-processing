# Family spectral law-projection v1 — result

**Decision:** `FAMILY_SPECTRAL_PROJECTION_MECHANICALLY_SUPPORTED`

The fresh experiment cleanly replicated both sides of the #89 family signal:

1. generic K=2 / amplitude-16 spectral deformation provides large structural-recovery leverage over native mutation;
2. the generic pointwise warp breaks the pre-existing sibling-scale family law often enough to fail the hard-validity requirement.

The preregistered family-law projection removes that validity failure while retaining essentially all of the generic spectral recovery gain.

No artistic judgment was collected. This is mechanical family-operator evidence only.

## Frozen execution

- 20 untouched `762xxx` master seeds;
- 2 shared hard-valid family starts per seed;
- 12 challenger attempts per arm per seed;
- native, generic spectral, and projected spectral arms fixed before target construction/scoring;
- generic/projected spectral arms use identical paired field seeds;
- K=2 and amplitude 16 unchanged from #89;
- 15 new target images across five structural families, fingerprint-disjoint from all prior sampling/material-control target suites through the runtime suite;
- no retries for invalid challengers.

Authoritative workflow run: `33702918218`.

Generation head: `cc495405740b3240d76dae0ae2cafad2ab51813b`.

Summary artifact: `9874188296`.

Summary digest: `sha256:e10fd321f2990bc5c5902b6d5512bd3350b524924bcd6f1915bf57741c7cce19`.

## Generic spectral diagnostic

The generic arm reproduced the earlier leverage:

- valid: `197 / 240 = 82.08%`;
- sibling-scale law failures: `43`;
- mean added recovery: `+0.0299116`;
- native mean added recovery: `+0.00868412`;
- generic-minus-native mean: `+0.0212275`;
- one-sided 95% master-seed bootstrap lower: `+0.0172643`;
- meaningful wins: `255`;
- meaningful losses: `23`;
- every target-family mean is positive.

The only frozen generic support gate that fails is validity (`82.08% < 95%`). This independently reproduces the #89 failure mode rather than relying on the consumed #89 population.

## Projected spectral treatment

The treatment keeps the exact generic pointwise spectral warp, but for each sibling rescales the warped organ around its warped anchor so the native anchor→tip length is preserved exactly.

Result:

- valid: **`240 / 240 = 100%`**;
- sibling-scale law failures: **`0`**;
- mean added recovery: `+0.0295644`;
- retained generic added recovery: **`98.84%`**;
- projected-minus-native mean: **`+0.0208803`**;
- one-sided 95% master-seed bootstrap lower: **`+0.0159774`**;
- meaningful wins: `250`;
- meaningful losses: `21`;
- largest target-family share of positive advantage: `24.03%`.

Every preregistered projected-support gate passes.

## Target-family stability

Projected-minus-native mean recovery delta:

| target family | delta |
| --- | ---: |
| concave loops | `+0.0219998` |
| dense regions | `+0.0264496` |
| disconnected loops | `+0.0200525` |
| nested loops | `+0.0167504` |
| open networks | `+0.0191489` |

The gain is broad rather than concentrated in one target family.

## Causal interpretation

The fresh data strongly support the specific mechanism hypothesized from #89:

```text
generic spectral field
→ useful structural variation
→ but nonlinear independent anchor/tip transport
→ sibling-scale coherence failure

family-law projection
→ same field + same amplitude + same anchor/root motion
→ exact native sibling terminal scale
→ validity repaired
→ recovery leverage preserved
```

This is materially stronger than simply retrying invalid spectral draws or lowering amplitude, because the repair acts on the pre-existing representation law and leaves the intervention's search field unchanged.

## Consequence

This result authorizes one later **isolated, opt-in family projected-spectral integration experiment** if useful. It does not authorize:

- changing the baseline/native family search;
- enabling family spectral control by default;
- applying the treatment to `sheet`;
- artistic promotion or reviewed-lineage authority;
- tuning K, amplitude, projection strength, or validity thresholds on consumed `762xxx` evidence.

Because visual-review research remains paused after #125, the highest-value follow-up should remain mechanically answerable: test the projected operator in the same baseline-preserving portfolio/runtime architecture used for supported 1-D material control, without making an artistic claim.
