# Compact iterative filament v1

## Decision

Can a compact **stateful iterative representation** create artistically stronger deployment-native filament portfolios than the current strong compact closed-form filament, at equal candidate budget?

This follows the workflow audit and three negative low-order compact-enrichment studies. The new hypothesis is materially different: use repeated computation along the filament to obtain expressive depth from a short law rather than storing many explicit material modes.

Frozen base: `e636ce85b05b876e37779ad19d22249a8a3c9a01`.

This is a mathematical representation experiment. It is **not** the parked Sotaku-inspired learned search operator: no model is trained and no search transition learns from outcomes.

## Population

Excluded smoke: `772999`.

Authoritative master seeds:

```text
772003 772019 772037 772053 772071 772089
772107 772127 772149 772167 772181 772199
```

All are fresh relative to the frozen base.

## Equal-budget portfolios

Each master seed produces exactly 12 matched candidate pairs, yielding two 12-candidate portfolios:

- `NATIVE12`: 12 closed-form compact native filament posts;
- `ITER12`: 12 compact two-state iterative filament posts.

For candidate index `j`, both arms share the exact same outer parameters `sx, sy, f, m, mf, t1, t2` sampled from one frozen shared seed. Each arm then receives only its representation-specific parameters from separate deterministic streams.

There are 24 unique complete posts per master seed. No retries, substitutions, adaptive allocation, or post-hoc parameter changes are allowed.

## Shared outer parameters

Frozen ranges, quantized before post construction:

- `sx`: 132..156 px
- `sy`: 56..70 px
- `f`: 4.5..7.5
- `m`: 0.25..0.75
- `mf`: 2.0..4.5
- `t1`: 20..36 frames
- `t2`: 24..44 frames

The x coordinate is always

```text
x = 200 + sx*u
```

so both representations are one open axial filament with strict monotone x by construction.

## NATIVE12 representation

The native arm uses the strong compact two-scale vocabulary:

```text
phase = f*u + m*sin(mf*u) - t/t1
y = 200 + sy*(a1*sin(phase) + a2*sin(f2*u + t/t2))
```

Frozen native-only ranges:

- `a1`: 0.55..0.82
- `a2`: 0.10..0.24
- `f2`: 6.0..10.5

## ITER12 representation

The iterative arm resets two bounded states once per frame:

```text
q = 0
r = 0
```

Then, in the exact point-generation order (`u` moves from approximately +1 to -1), each sample applies the same coupled update:

```text
q <- 0.9*q + 0.1*sin(f*u + b*r + m*sin(mf*u) - t/t1)
r <- 0.9*r + 0.1*sin(g*u + c*q + t/t2)
y  = 200 + sy*(q + d*r)
```

Frozen iterative-only ranges:

- `b`: 0.4..0.9
- `c`: 0.4..0.9
- `g`: 2.5..6.0
- `d`: 0.10..0.30

All floating representation-specific values are quantized to one decimal place.

### Analytic representation contract

Because each state update is a convex combination of its previous value and a sine value, starting from zero implies `q,r ∈ [-1,1]` for every sample and frame. With `d <= 0.3` and `sy <= 70`, y is analytically bounded inside `[109,291]` before numerical verification.

The iterative state is spatial working memory: its repeated update can encode effective multi-scale structure without an explicit high-dimensional spectral field.

## Hard candidate preconditions

Every one of the 24 unique posts per seed must:

1. end with `//#つぶやきProcessing`;
2. fit <=280 raw Unicode code points and <=280 X-weighted characters;
3. execute at review frames `1,50,100,150` and delivery frames `30,90,150`;
4. remain one continuous open filament with strictly monotone x in generation order;
5. retain >=95% in-frame points at every review frame;
6. retain x span >=240 px and y span >=35 px at every review frame;
7. show mean absolute temporal change >=10 px for every adjacent review-frame pair;
8. have maximum adjacent-sample y jump <=14 px at every review frame;
9. for ITER12, retain numerical `|q|,|r| <= 1 + 1e-12` at every sampled point.

Mechanical checks are vetoes only.

## Frozen delivery

Both arms use the already-supported target-blind raw-pixel max-dispersion three-item reducer from #106.

For each candidate, render grayscale frames `t=30,90,150`, resize to `100x100` with nearest-neighbor, and define distance as normalized mean absolute pixel difference across the three frames.

For each 12-candidate arm:

1. enumerate every 3-candidate combination in generation-order index order;
2. lexicographically maximize `(minimum pairwise distance, mean pairwise distance)`;
3. exact ties keep the first combination.

No representation label, target, structural score, semantic model, human label, or previous result enters delivery.

The **complete 24-candidate generated archive is preserved** before review.

## Blinded artistic portfolio review

The authoritative job produces three separate artifacts:

- reviewer package: 12 A/B portfolio rows, each side showing its three delivered candidates across frames `1,50,100,150`;
- sealed archive/key: A/B identity, all 24 exact posts and parameters, shortlist indices, shared parameter pairing, and orientation salt;
- mechanical summary.

A cryptographically random run salt determines A/B orientation. The sealed archive/key remains unopened until every human rating is committed.

Reviewer question:

> Which three-item portfolio would you rather keep as a source of finished compact #つぶやきProcessing filament works, considering individual strength, coherence and smoothness through time, and useful range across the three alternatives?

Allowed ratings: `A>B`, `B>A`, `equivalent`, `unreviewable`.

## Advancement gate

`COMPACT_ITERATIVE_FILAMENT_ARTISTIC_SUPPORT` requires all:

1. every hard precondition passes;
2. >=10 reviewable pairs;
3. >=8 decisive pairs;
4. ITER12 decisive win rate >0.65;
5. one-sided exact binomial p<=0.10 against p=0.5.

If the gate fails, close this exact two-state iterative family and parameter ranges without tuning against consumed `772xxx` ratings.

If it passes, the result supports the iterative representation family as a deployment-native discovery surface. It does **not** establish which recurrent ingredient is causal; the next step must be a fresh matched ablation of recurrence/state feedback rather than parameter tuning on `772xxx`.
