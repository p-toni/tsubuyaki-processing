# Late-refinement artistic preference prospective v1

## Motivation

After the generic semantic judge and the morphology-context judge both failed prospectively, a post-hoc screen of the three consumed blinded reviewer populations (`755xxx`, `756xxx`, `757xxx`) found a simpler signal: the human reviewer chose the later generation-order `q=0.75` challenger 45 / 72 times (62.5%). Because that observation was discovered after labels were consumed, it is hypothesis generation only.

This experiment is the first confirmatory test of that signal.

## Question

On a fresh untouched population, is the later within-trajectory challenger at generation-order `q=0.75` artistically preferred over the earlier `q=0.35` challenger more often than chance?

## Fresh population

Authoritative review seeds:

- `758003`
- `758019`
- `758037`
- `758053`
- `758071`
- `758089`
- `758107`
- `758127`

Excluded smoke seed: `758999`.

Routes:

- recurrence
- orbit
- filament

Eight seeds × three routes = **24 authoritative blocks**.

The `758xxx` namespace must be absent from repository history before preregistration/generation.

## Frozen generation

Each block uses the current supported intrinsic-1D substrate:

- one hard-valid route-prior start;
- exactly 20 generated attempts;
- `native-spectral-50-50-v1`: exactly 10 native + 10 spectral attempts;
- current single-incumbent search;
- no restart sidecar;
- no artistic model or human scorer during generation.

The brief and generation code do not know the test outcome.

## Frozen pair selection

After the full trajectory exists:

1. exclude the original start;
2. retain hard-valid generated challengers in deterministic generation order;
3. require at least 12 valid generated challengers;
4. choose `q=0.35` and `q=0.75` using `floor((n-1)*q)`;
5. do not resample identical displays.

A/B orientation is randomized by frozen blind salt and block id. The human reviewer sees only block id, A/B temporal pixels at `t=30,90,150`, and the frozen question.

The identity key containing route, seed, candidate ids, quantiles, operators, and generation metadata is uploaded separately and must remain unopened until all 24 human judgments are frozen.

## Human judgment

Question:

> Which candidate is the stronger mathematical form worth keeping or developing further?

Allowed labels:

- `A>B`
- `B>A`
- `equivalent`
- `unreviewable`

The reviewer must not know which side is `q=0.35` or `q=0.75` before all ratings are frozen.

## Scoring

For each human-decisive block, unblind the identity key only after ratings are fixed and score whether the preferred candidate is `q=0.75`.

Primary outcome: `q=0.75` win rate among decisive blocks.

## Frozen gate

`LATE_REFINEMENT_ARTISTIC_PREFERENCE_SUPPORTED` requires all:

1. at least **18 / 24** human-reviewable blocks;
2. at least **12** human-decisive blocks;
3. `q=0.75` decisive win rate **> 0.65**;
4. one-sided exact binomial p-value vs `p=0.5` **<= 0.10**;
5. every route with at least three decisive blocks has `q=0.75` win rate **>= 0.50**.

Otherwise: `LATE_REFINEMENT_ARTISTIC_PREFERENCE_NOT_SUPPORTED`.

## Boundary

- Positive: authorize one second fresh prospective replication of this exact `q=0.35` vs `q=0.75` test. Do not yet replace artistic judgment with generation order or change search allocation.
- Negative: close this post-hoc line. Do not tune nearby quantiles, stage cutoffs, route-specific thresholds, operators, or seed sets on consumed populations.
- Validity/custody failure: record invalid/inconclusive and replace only on a fresh namespace.
