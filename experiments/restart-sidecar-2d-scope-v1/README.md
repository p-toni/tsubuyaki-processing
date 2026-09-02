# Restart sidecar 2-D route-scope v1

## Question

Does the already-supported **baseline-preserving independent-start sidecar** produce the same kind of mechanical coverage gain on the two intrinsic-2D incumbent routes, `family` and `sheet`, that it produced on the evidence-authorized intrinsic-1D route class?

This is a route-scope experiment only. It does not test artistic quality, does not modify baseline search, and does not authorize automatic sidecar promotion.

## Why this is distinct

The restart line through #110–#118 and the budget-efficiency confirmation in #126 were evaluated on `recurrence`, `orbit`, and `filament`. Production therefore deliberately keeps:

```text
EVIDENCE_AUTHORIZED_RESTART_ROUTES = (recurrence, orbit, filament)
```

`family` and `sheet` are ordinary baseline routes but have never been admitted to that sidecar authority boundary. Earlier generic breadth/depth experiments do not answer this exact question because they changed the search policy itself rather than appending an isolated post-search sidecar while preserving baseline bytes/state.

## Frozen intervention

Routes:

```text
family
sheet
```

For each route and master seed:

1. run the current 20-generated-attempt **native-only** baseline with one hard-valid start, `4 explore + 4 roundA + 12 refine`;
2. freeze the complete hard-valid generated archive and target-blind three-item max-dispersion delivery;
3. generate exactly **8 independent route-prior sidecar attempts** using the existing `restart-sidecar-v1` RNG namespace and candidate contract;
4. invalid sidecar draws consume their attempt and are not retried;
5. sidecar candidates remain outside baseline `SearchState`, cannot parent baseline search, and cannot replace baseline delivery automatically;
6. compare baseline vs baseline+sidecar only after both archives are fixed.

The experiment reproduces the sidecar generation mechanics locally without changing `restart_route_authority.py`; `family`/`sheet` therefore remain unauthorized in production throughout the experiment.

## Mechanical surfaces

Primary surfaces reuse the established restart/delivery instrumentation:

- full hard-valid archive recovery over the frozen 15 structural targets;
- target-blind max-dispersion delivery-trio recovery over the same targets;
- minimum pairwise distance of the target-blind delivery trio;
- hard-valid sidecar rate and distinct temporal phenotypes added.

Generation and delivery selection are target-independent. Targets are constructed/scored only after the baseline and sidecar archives are fixed.

## Fresh population

Excluded smoke:

```text
760999
```

Authoritative master seeds:

```text
760003 760019 760037 760053 760071
760089 760107 760127 760149 760167
760181 760199 760223 760239 760257
760277 760293 760311 760331 760349
```

The `760` namespace must be absent from the frozen pre-experiment base `5aafb1a238c9f01fecbc7594d8cd631283a81dc1` before smoke or authoritative execution.

## Preregistered gate

Historical restart meaningful-effect bar:

```text
0.003255297955511336
```

`SIDECAR_2D_SCOPE_MECHANICALLY_SUPPORTED` requires **all**:

1. complete 20-seed × 2-route rectangle and all hard invariants;
2. pooled sidecar hard-valid rate >= 95%;
3. full-archive recovery mean delta > the historical meaningful-effect bar;
4. full-archive one-sided 95% master-seed bootstrap lower bound > 0;
5. max-dispersion delivery recovery mean delta > the same meaningful-effect bar;
6. delivery one-sided 95% master-seed bootstrap lower bound > 0;
7. mean minimum-pairwise-dispersion delta > 0;
8. both route-specific archive means > 0;
9. both route-specific delivery means > 0.

No route vote substitutes for the complete-master-seed inference.

### Pass

A pass authorizes one narrow integration change: add `family` and `sheet` to the **opt-in exploratory restart-sidecar route authority** while preserving all existing isolation flags and `defaultEnabled: false`. It does not authorize artistic promotion, baseline parenting, delivery replacement, or enabling the sidecar by default.

### Fail

A fail leaves the current 1-D-only evidence-authority boundary unchanged and closes this exact `family`/`sheet` eight-attempt sidecar-scope hypothesis. No tuning on consumed `760xxx` evidence.

## Visual-review boundary

No human or model artistic judgment is collected in this experiment. Visual review is explicitly out of scope.
