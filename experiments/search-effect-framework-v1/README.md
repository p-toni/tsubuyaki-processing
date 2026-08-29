# Search effect framework v1

## Purpose

Replace the retired `seed majority -> route majority` stochastic gate with one fixed paired-effect analysis contract for future search-quality experiments.

This framework is frozen before the next fresh search-policy confirmation. It separates:

1. the **estimand** we care about;
2. the source of stochastic replication;
3. fixed route heterogeneity;
4. diagnostics for outlier dependence;
5. the randomness-coupling requirements of paired simulation.

It does not decide which search policy to test.

## Domain and estimand

The current math-first search domain contains five fixed route strata:

```text
recurrence
orbit
family
sheet
filament
```

They are not treated as five random draws from a hypothetical population of representations. They are the domain the current system actually supports.

For a frozen policy contrast, define the route×seed paired effect:

```text
delta[r,s] = candidate_policy_score[r,s]
           - baseline_policy_score[r,s]
```

where the score is the preregistered route×seed search-quality outcome, typically equal-weighted over local/global target regimes when both are part of the benchmark.

For each fresh master seed:

```text
seed_effect[s] = mean_r delta[r,s]
```

The primary general-policy estimand is:

```text
Delta = E_seed[ seed_effect[s] ]
```

with every current route receiving equal weight.

This makes the stochastic replicate the **master seed / complete five-route scenario**, not each of the 15 route×seed cells independently.

## Why seed-level aggregation is primary

A master seed can induce correlated outcomes across routes through shared experiment construction choices, and the five routes are fixed strata whose heterogeneity is scientifically meaningful.

Treating all route×seed cells as independent would create pseudo-replication and make the confidence interval narrower than the design justifies.

Therefore:

```text
fixed routes      -> stratification / heterogeneity
fresh seeds       -> stochastic replication / uncertainty
```

The overall point estimate is still the balanced mean across all route×seed effects, but uncertainty is computed from the seed-level equal-route means.

## Required summaries

Every stochastic search-policy result must preserve:

### Cell evidence

- every route×seed delta;
- local/global component deltas where defined;
- baseline and candidate raw scores.

### Route evidence

For each route:

- mean delta across seeds;
- median delta across seeds;
- minimum / maximum seed delta.

These are heterogeneity diagnostics, not five binary votes.

### Seed evidence

For each seed:

- equal-route mean delta (`seed_effect`);
- median route delta;
- minimum / maximum route delta.

### Overall evidence

- mean seed effect;
- median seed effect;
- sample standard deviation of seed effects;
- standard error of the mean seed effect;
- 95% Student-t interval over seed effects when `n >= 5`;
- deterministic seed-bootstrap percentile interval as a secondary robustness diagnostic;
- strict positive / non-negative counts only as descriptive diagnostics.

For historical consumed-seed blocks with only three seeds, intervals are explicitly exploratory and cannot manufacture confirmation.

## Influence diagnostics

Every result must report:

```text
leave-one-seed-out mean range
leave-one-route-out mean range
largest absolute route×seed delta
largest cell contribution to the overall balanced mean
```

A policy whose apparent benefit disappears when one seed or route is removed is classified as fragile/heterogeneous even if the aggregate point estimate is positive.

Do not silently Winsorize or delete an outlier because it is inconvenient. If a cell is invalid for a predeclared mechanical reason, report both the invalidation and the unchanged complete-case record.

## Calibration and holdout

Hyperparameter/policy selection and confirmatory inference remain separate.

```text
consumed calibration evidence
→ freeze one policy contrast
→ freeze analysis contract
→ open untouched fresh seeds
```

Do not select among several candidate policies using the same fresh seeds later used to claim confirmation.

Historical replay may choose which mechanism deserves a fresh experiment, but it is not itself fresh confirmation.

## Pairing and random streams

Pairing should preserve as much shared exogenous randomness as the policy contrast allows.

Current code provides stable hash-derived RNG namespaces by master seed, representation, version and stream. That is useful, but many search paths still use stateful PRNG streams. If two policies alter control flow, candidate count, parent selection or draw order, later random draws can refer to different logical mutation events even under the same master seed.

Therefore distinguish two cases.

### A. Event-aligned contrasts

Examples:

- a frozen mutation-scale multiplier applied to the same mutation calls;
- a stage-specific scale schedule that preserves candidate IDs, candidate count and RNG consumption.

If the experiment proves exact call/count/RNG alignment, ordinary shared seed pairing is acceptable.

### B. Control-flow-changing contrasts

Examples:

- depth vs breadth topology;
- different survivor counts;
- adaptive budget allocation;
- different parent-selection paths;
- repertoire policies that generate different candidate sets.

For these, a shared master seed is a **scenario block**, not automatically event-level common random numbers.

Before fresh confirmation, prefer an experiment-local event-keyed randomization harness where mutation randomness is derived from stable logical event identity such as:

```text
master seed
route + representation version
stage
basin/start identity
candidate slot / event key
mutation role
```

rather than the number of prior RNG draws.

The harness must be verified to leave each policy's intended semantics unchanged except for how exogenous random draws are coupled across counterfactual policies.

If event-keyed coupling is not feasible, retain seed-level paired analysis but do not claim the stronger variance-reduction/counterfactual interpretation of common random numbers. Increase fresh replication as needed.

## Fresh-seed sample size

Do not use the historical `3 fresh seeds` convention automatically.

After one contrast is frozen, use consumed evidence only to estimate the variance of the primary `seed_effect`. Choose a fresh seed count before opening outcomes, with these constraints:

```text
minimum planned n = 8 complete master seeds
prefer n >= 12 when compute permits
all five routes must be complete for a seed to enter the primary estimand
```

The exact n should be justified by expected effect scale, seed-effect variance and compute cost in the experiment preregistration.

Do not stop early because the running mean looks favorable unless an explicit sequential design and error-spending rule was frozen in advance.

## General versus route-specific conclusions

A positive primary mean does not imply one policy is best for every representation.

Interpret jointly:

```text
primary seed-averaged effect
+ route means
+ influence diagnostics
```

Possible conclusions:

### General leverage

A reproducible positive seed-averaged effect with no route showing a material, persistent regression large enough to undermine a universal default.

### Route-conditional leverage

A stable overall or subset signal with material route heterogeneity whose mechanism is interpretable enough to preregister a route-specific policy.

### Heterogeneous / unresolved

A mean driven by one route, one seed, sign instability, or effects too small relative to seed variation to support a useful policy claim.

Numerical practical-harm / adoption margins are contrast-specific and must be frozen before the fresh holdout; they are not invented in this generic framework.

## Deterministic properties remain gates

This stochastic effect framework does not replace proof-like deterministic checks.

Examples that remain hard pass/fail invariants:

- exact baseline replay;
- candidate-count equality where required;
- sealed mapping integrity;
- RNG/event-key identity;
- queue bounds;
- route exposure guarantees;
- no unauthorized artistic promotion;
- exact trajectory equivalence when the experiment claims semantic preservation.

Do not average a deterministic invariant into a stochastic quality score.

## External design rationale

Simulation literature supports paired/common-random-number comparisons as a variance-reduction tool when the shared random inputs genuinely correspond across alternatives. It also documents that common random numbers can fail to reduce variance when the induced coupling is poor.

Recent event-keyed simulation work sharpens the software concern: reusing a stateful base seed does not guarantee that draw `k` represents the same causal event after policies alter execution paths. Stable event-keyed randomness is the cleaner counterfactual design when control flow diverges.

Modern empirical-design guidance likewise emphasizes performance variation, independent test scenarios and protection against hyperparameter/experimenter bias rather than relying on a single aggregate win count.

## Boundary

Research-method contract only. It does not adopt a search policy, metric, event-keyed runtime, production RNG change, representation pruning or `SKILL.md` change.
