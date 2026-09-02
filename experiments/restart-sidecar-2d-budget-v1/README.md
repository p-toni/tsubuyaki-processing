# Restart sidecar intrinsic-2D budget v1

## Question

After #128/#129 authorized `family` and `sheet` for the opt-in exploratory restart sidecar at eight attempts per route, can either route use fewer attempts while preserving the mechanically demonstrated coverage gain?

This is a compute-efficiency experiment only. It does not rank routes, remove route exposure, change baseline search, or provide artistic authority.

## Why this remains open

#126 established that the intrinsic-1D route class needs eight sidecar attempts per route to retain the established coverage effect. #128 established that eight attempts also produce strong mechanical gains on `family` and `sheet`, but did not measure the nested lower-budget curve for those two routes.

Therefore only the 2-D budget remains unresolved.

## Frozen intervention

Routes:

```text
family
sheet
```

Budgets are nested prefixes of one frozen eight-attempt sidecar stream:

```text
k = 1, 2, 4, 8
```

For each route/master-seed:

1. run the current native-only 20-generated-attempt baseline;
2. freeze the complete hard-valid baseline archive and target-blind three-item max-dispersion delivery;
3. generate exactly eight independent sidecar attempts with the production `restart-sidecar-v1` namespace;
4. construct k=1/2/4/8 arms from exact prefixes of that eight-attempt stream;
5. invalid sidecar draws consume budget and are not retried;
6. sidecar candidates remain outside baseline state and cannot parent or replace delivery;
7. construct/score the frozen 15 structural targets only after all archives and target-blind deliveries are fixed.

An excluded smoke run must additionally prove that the production sidecar API reproduces the frozen prefix exactly for both routes.

## Mechanical surfaces

For each k:

- full hard-valid archive structural recovery;
- target-blind max-dispersion delivery-trio recovery;
- minimum pairwise delivery dispersion;
- hard-valid sidecar rate;
- distinct valid temporal phenotypes added.

No human/model artistic judgment is collected.

## Fresh population

Excluded smoke:

```text
761999
```

Authoritative master seeds:

```text
761003 761019 761037 761053 761071
761089 761107 761127 761149 761167
761181 761199 761223 761239 761257
761277 761293 761311 761331 761349
```

The exact namespace must be absent from frozen pre-experiment base `144db8a9b361b3c8421ddd0736ed6690f6929813`.

## Prerequisite: k=8 must replicate the effect

Before interpreting efficiency, the fresh k=8 arm must satisfy all:

1. pooled hard-valid sidecar rate >=95%;
2. pooled archive mean delta > `0.003255297955511336` and one-sided 95% master-seed bootstrap lower >0;
3. pooled delivery mean delta > the same historical meaningful-effect bar and lower >0;
4. pooled minimum-pairwise-dispersion delta >0;
5. `family` and `sheet` archive means >0;
6. `family` and `sheet` delivery means >0.

If these fail, decision is `SIDECAR_2D_BUDGET_EFFECT_NOT_REPLICATED`; no lower-budget conclusion is authorized.

## Efficiency gate

For k in 1/2/4/8, compare gains against k=8. A smaller k is mechanically sufficient only if **all**:

1. pooled archive gain ratio >=90%;
2. pooled delivery gain ratio >=90%;
3. pooled minimum-pairwise-dispersion gain ratio >=90%;
4. `family` archive gain ratio vs its own k=8 gain >=90%;
5. `family` delivery gain ratio vs its own k=8 gain >=90%;
6. `sheet` archive gain ratio vs its own k=8 gain >=90%;
7. `sheet` delivery gain ratio vs its own k=8 gain >=90%;
8. both routes remain non-negative on archive, delivery, and dispersion deltas.

Select the smallest sufficient k.

Decision labels:

- k=1 or 2: `SIDECAR_2D_SMALLER_BUDGET_SUFFICIENT`
- k=4: `SIDECAR_2D_FOUR_MECHANICALLY_EFFICIENT`
- k=8: `SIDECAR_2D_EIGHT_REQUIRED_FOR_COVERAGE`

A lower-budget result may inform a later route-specific compute-policy integration. It does not authorize route pruning or artistic promotion.
