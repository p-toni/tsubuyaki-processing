# Operator novelty allocation v1 — result

Decision: **`NOVELTY_OPERATOR_ALLOCATION_NOT_PROMISING`**.

Authoritative run: `33405389033` at frozen scientific head `90f0ffc79764b100dcde36350b43fb9d71a50add`.

Summary artifact: `9763132890`, digest `sha256:d030d4d48293b450013e58f7e1d7eb6d0a3dd217d41c64bfb8acba4596d206df`.

No authoritative seed artifact was inspected individually. The excluded `745999` smoke first proved the custom `baseline10x10` arm reproduced the current runtime phenotype-for-phenotype on recurrence, orbit, and filament.

## Result

The target-blind prefix novelty rule selected **spectral on all 60/60 route-seed trajectories**.

Favoring that winner with a 12-spectral / 8-native final budget did improve the complete hard-valid archive mechanically:

- adaptive vs current 10/10 archive: `+0.0015827452` mean;
- one-sided 95% seed-bootstrap lower bound: `+0.0007456397`;
- adaptive vs anti-adaptive archive: `+0.0032071769` mean;
- lower bound: `+0.0020282971`;
- every route was positive in both archive comparisons.

But the preregistered meaningful-effect bar was `+0.0032552980`. The adaptive-vs-baseline archive gain did **not** clear it.

The already-promoted max-dispersion delivery surface also moved the wrong way:

- adaptive vs baseline delivery mean: `-0.0010158533`;
- recurrence: `+0.0015002790`;
- orbit: `-0.0023256500`;
- filament: `-0.0022221890`.

Validity was unchanged at `0.995` for both adaptive and baseline.

## Interpretation

The raw early phenotype-novelty statistic is not functioning as a trajectory-specific allocator here. It is effectively a global spectral-preference detector.

That preference is not meaningless: 12 spectral / 8 native improves full-archive structural recovery statistically relative to both 10/10 and the complementary 8 spectral / 12 native policy. But the improvement over the current runtime is too small to clear the frozen complexity threshold, and the promoted three-item delivery surface does not improve.

Therefore the preregistered core performance gate fails. The separate `GLOBAL_OPERATOR_BIAS_INDICATED` branch required core performance to pass before operator-decision diversity could redirect the experiment to a fixed-ratio replication, so that branch is **not authorized** either.

## Research consequence

Stop this exact:

- eight-attempt prefix;
- leave-one-out raw phenotype novelty statistic;
- 12/8 operator allocation;
- deterministic native tie rule;
- current raw multi-time distance representation.

Do not tune those choices on consumed `745xxx` evidence.

The supported runtime remains:

- single-incumbent search;
- fixed 20 generated attempts;
- 10 native + 10 spectral attempts;
- preserve the complete hard-valid archive;
- target-blind max-dispersion three-item delivery shortlist;
- human artistic authority at the final boundary.
