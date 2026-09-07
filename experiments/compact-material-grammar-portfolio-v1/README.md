# Compact material grammar portfolio v1

## Decision

Can deployment-native compact material become artistically useful when it is offered as **optional portfolio material** rather than forced onto every good native filament?

This study follows three facts:

1. expanded intrinsic-1D spectral material had positive portfolio-level artistic evidence;
2. the complete filament workflow audit could select expanded spectral work but could not preserve it through post-hoc <=280-character compression;
3. two mandatory compact treatments were artistically negative (`SHEAR3` 0/12; `PHASEPACK` 2/10 decisive).

The experimental unit therefore changes from a matched mandatory treatment to an equal-budget search portfolio whose every candidate is already deployment-valid.

Frozen base: `3aa01609c6812db5ab3d68f0c256809a17df9850`.

## Population

Excluded smoke: `771999`.

Authoritative master seeds:

```text
771003 771019 771037 771053 771071 771089
771107 771127 771149 771167 771181 771199
```

All are fresh relative to the frozen base.

## Candidate budget

Each master seed produces two 12-candidate portfolios.

### NATIVE12

Twelve independently sampled compact native filament posts.

### MIXED12

Exactly:

- the **first six NATIVE12 candidates byte-identically**;
- two fresh `CHIRP` candidates;
- two fresh `EPICYCLE` candidates;
- two fresh `COUNTER` candidates.

Thus both arms have exactly 12 generated candidates and the mixed arm has an exact six-candidate common native prefix. No retries or adaptive reallocation are allowed.

## Shared compact base grammar

Every candidate starts from the same bounded two-scale filament vocabulary:

```text
x = 200 + sx*u
phase = f1*u + m*sin(mf*u) - t/t1
y = 200 + sy*(a1*sin(phase) + a2*sin(f2*u + t/t2))
```

Frozen base ranges:

- `sx`: 132..156
- `sy`: 58..82
- `f1`: 4.5..7.5
- `m`: 0.35..0.95
- `mf`: 2.0..4.5
- `a1`: 0.55..0.82
- `a2`: 0.10..0.24
- `f2`: 6.0..10.5
- `t1`: 20..36
- `t2`: 24..44

Floating literals are quantized to one decimal place before post construction.

## Frozen material grammar

The three material mechanisms are intentionally different from the consumed three-shear and shared-latent PHASEPACK treatments.

### CHIRP

Add intrinsic quadratic phase curvature:

```text
phase += c*u*u
```

`|c|` is 0.6..1.8 with random frozen sign.

### EPICYCLE

Add one bounded traveling intrinsic looplet:

```text
z = h*u - t/t3
x += r*cos(z)
y += r*sin(z)
```

Ranges:

- `r`: 6..12 px
- `h`: 1.6..3.0
- `t3`: 40..70

The frozen ranges guarantee `sx > r*h`, so x remains strictly monotone analytically; the numerical hard check must also pass.

### COUNTER

Add one compact counter-propagating nearby-frequency component:

```text
y += sy*e*sin((f1+d)*u + t/t3)
```

Ranges:

- `e`: 0.12..0.28
- `d`: 0.5..1.4
- `t3`: 38..70

No parameter is tuned after rendering.

## Hard candidate preconditions

Every one of the 18 unique generated posts per seed (12 native + 6 material; the mixed six native are shared) must:

1. end with `//#つぶやきProcessing`;
2. fit <=280 raw Unicode code points and <=280 X-weighted characters;
3. execute at review frames `1, 50, 100, 150` and delivery frames `30, 90, 150`;
4. remain one continuous open filament with strictly monotone x;
5. retain >=95% in-frame points at every review frame;
6. retain x span >=240 px and y span >=35 px at every review frame;
7. show nontrivial temporal change over the review horizon.

The portfolio-level hard checks also require:

- exact 12 vs 12 slots;
- exact six-post common native prefix;
- exact mixed mechanism counts `native=6, chirp=2, epicycle=2, counter=2`;
- all 12 authoritative pairs present.

Mechanical checks are vetoes only.

## Frozen delivery

Delivery reuses the supported target-blind raw-pixel max-dispersion rule from #106.

For every candidate, render grayscale frames `t=30,90,150`, resize each to `100x100` with nearest-neighbor, and define candidate distance as mean absolute pixel difference across all three frames, normalized to `[0,1]`.

For each 12-candidate arm:

1. enumerate every 3-candidate combination in generation-order index order;
2. compute its three pairwise distances;
3. lexicographically maximize `(minimum pairwise distance, mean pairwise distance)`;
4. exact ties keep the first combination.

No brief target, mechanism label, score, human judgment, semantic model, or prior rating enters delivery.

The **complete generated archive is preserved** before human review so later bottleneck diagnosis never requires regenerating consumed evidence.

## Blinded portfolio review

The authoritative job produces separate artifacts:

- reviewer package: 12 A/B portfolio rows; each side shows its three delivered candidates across review frames `1,50,100,150`;
- sealed archive/key: A/B identity, all 18 unique candidate posts and parameters, mechanism labels, shortlist indices, and orientation salt;
- mechanical summary.

A cryptographically random per-run salt determines A/B orientation. The sealed archive/key is not opened until all ratings are committed.

Reviewer question:

> Which three-item portfolio would you rather keep as a source of finished compact #つぶやきProcessing filament works, considering the strength of the individual pieces, visual coherence and smoothness through time, and useful range across the three alternatives?

Allowed: `A>B`, `B>A`, `equivalent`, `unreviewable`.

## Advancement gate

`COMPACT_MATERIAL_GRAMMAR_PORTFOLIO_ARTISTIC_SUPPORT` requires all:

1. every hard precondition passes;
2. >=10 reviewable pairs;
3. >=8 decisive pairs;
4. MIXED12 decisive win rate >0.65;
5. one-sided exact binomial p<=0.10 against p=0.5.

If the gate fails, close this exact grammar/allocation without tuning on consumed `771xxx`.

If it passes, the result supports a compact-material grammar as an **optional discovery surface** only. It does not establish any single mechanism as artistically causal; a fresh mechanism ablation would be required before promoting individual primitives.
