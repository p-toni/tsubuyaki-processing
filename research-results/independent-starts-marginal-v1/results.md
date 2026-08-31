# Independent starts marginal v1 — result

Decision: **`INDEPENDENT_STARTS_SCREEN_PROMISING`**.

Authoritative run: `33407757100` at frozen scientific head `3528af300c21952e0270a67bcd552a5abf5977b5`.

Summary artifact: `9764029285`, digest `sha256:02abaac2e00cfdbefcd3cc73a01de16002f08a4edf2d16d55b369341a3442aed`.

No authoritative seed artifact was inspected individually. The excluded `746999` smoke first proved that the shared custom 20-attempt baseline replay was phenotype-identical to the current runtime on recurrence, orbit, and filament.

## Result

After the exact supported 20-attempt trajectory, four additional independent one-shot route-prior starts were much more valuable mechanically than four additional low-scale local mutations.

Full-archive recovery:

- deep-local marginal gain over baseline: `+0.0025381071`;
- independent-start marginal gain over baseline: `+0.0262792611`;
- independent-start minus deep-local effect: `+0.0237411541`;
- one-sided 95% seed-bootstrap lower bound: `+0.0186713704`.

Every route was positive:

- recurrence: `+0.0147069115`;
- orbit: `+0.0240028838`;
- filament: `+0.0325136668`.

The already-promoted target-blind max-dispersion delivery surface improved as well:

- independent-start minus deep-local delivery: `+0.0273070980`;
- one-sided 95% lower bound: `+0.0192915702`;
- independent-start minus baseline delivery: `+0.0282848704`;
- lower bound: `+0.0206668668`.

Delivery effects were positive on every route, not merely inside the preregistered non-inferiority margin.

Marginal hard-validity:

- deep local: `234 / 240 = 0.975`;
- independent starts: `240 / 240 = 1.0`.

Every preregistered gate passed.

## Interpretation

This is the clearest evidence so far that the current one-start local trajectory leaves substantial global route-prior coverage unused.

The result is stronger than a generic diversity observation. Under exactly equal marginal candidate-evaluation count, independent starts:

1. recover much more of the frozen external structural target space than deeper local exploitation;
2. improve the production-facing max-dispersion delivery surface rather than only the hidden full archive;
3. do so consistently across recurrence, orbit, and filament;
4. incur no validity penalty in this fresh population.

However this experiment appended four candidates after the supported 20-attempt runtime. It does **not** establish that production should spend 24 attempts, nor does it identify which four current attempts should be removed to keep total compute fixed.

## Research consequence

Authorize one fresh **equal-20-budget substitution experiment** comparing the current supported runtime against a preregistered treatment that replaces exactly four existing local-search attempts with four independent one-shot route-prior starts.

The replacement positions must be chosen from architectural reasoning fixed before the fresh experiment. Consumed `746xxx` evidence must not be mined to choose them.

Until that equal-budget causal test passes:

- production remains one hard-valid start;
- fixed 20 generated attempts;
- 10 native + 10 spectral current trajectory;
- complete hard-valid archive preservation;
- target-blind max-dispersion three-item delivery;
- human artistic authority at the final boundary.
