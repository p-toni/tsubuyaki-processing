# Multiplex capacity v1

Decision: **MULTIPLEX_CAPACITY_NOT_PROMISING**

Consumed-seed mechanism-capacity pilot of the frozen index-multiplexed latent-geometry grammar and four same-schema causal ablations. This result is not a production-route admission test and does not use fresh search evidence.

## Evidence

- Authoritative workflow run: `33275549621`
- Aggregate artifact: `9722532548`
- Artifact digest: `sha256:6c6f7d2b6e05f3a223ca125f71b481c2d0d806dc24de00d2f77d739cd68549df`
- Frozen population: 20 consumed master seeds x 12 challenges = 240 seed-challenge cells
- Representations: 5 current routes + full multiplex + 4 multiplex ablations = 10
- Candidate evaluations per representation/challenge: 20
- No fresh seeds; excluded seed `9001` was smoke only.

## Preregistered gates

1. complete hard-invariant rectangle: **PASS**
2. full mean advantage over best current route > 0: **FAIL**
3. every leave-one-challenge-family-out mean > 0: **FAIL**
4. full mean advantage over every ablation > 0: **FAIL**
5. rarefied structural-niche density >= 1.25x strongest ablation: **FAIL**
6. no challenge family > 60% of positive primary contribution: **PASS**

The result therefore fails the frozen capacity gate without needing any post-hoc threshold interpretation.

## Primary effect: full multiplex - best current route

Across complete master seeds:

- n: `20`
- mean: `-0.0732205465797186`
- median: `-0.07059275692407557`
- SD: `0.0327422572196542`
- min: `-0.15246064712797536`
- max: `-0.027219573734425313`

Every one of the 20 master-seed effects is negative. This is not a result driven by one bad seed.

Leave-one-family-out means are also uniformly negative:

- omit linked-submanifolds: `-0.07164213279021821`
- omit woven-single-index: `-0.09134685525365423`
- omit radius-motion-coupling: `-0.08636463296959555`
- omit localized-curvature: `-0.04352856530540642`

Family means:

- linked-submanifolds: `-0.07795578794821978`
- woven-single-index: `-0.01884162055791172`
- radius-motion-coupling: `-0.03378828741008777`
- localized-curvature: `-0.16229649040265512`

Localized curvature is the clearest failure mode: all three detail challenges are strongly negative and the family contributes zero positive primary effect.

## Causal ablations

Mean full-minus-ablation recovery advantage:

- no branch: `+0.06223276991663515`
- no reuse: `-0.020091603277707055`
- no singular/local reciprocal response: `+0.0002962560048856644`
- regular grid instead of index multiplexing: `-0.0005971871614398503`

The important mechanistic reading is asymmetric:

- residue/parity branching contributes recovery inside this grammar;
- latent reuse does **not** support the bundled capacity hypothesis here: removing it improves recovery on average;
- replacing the multiplexed single-index topology with an explicit regular grid is essentially neutral/slightly better, so the distinctive index-multiplexing mechanism itself receives no positive capacity evidence;
- reciprocal/local singular response is effectively neutral at this scale.

These are diagnostics of the frozen v1 grammar, not permission to isolate and optimize the apparently favorable submechanism on the same 20 seeds.

## Structural niche coverage

- full rarefied niche density: `0.003827507017096198`
- strongest ablation: `multiplex-no-branch`
- strongest-ablation density: `0.003827507017096198`
- full / strongest-ablation density ratio: `1.0`
- preregistered requirement: `>= 1.25`

Full multiplex and no-branch each occupy 15 rarefied `structural-v1` niches. The full mechanism therefore does not buy the incremental structural-niche density that motivated the capacity gate.

Unique-rendered-phenotype rate is ~1.0 for every multiplex variant, so the failure is not explained by obvious duplicate/no-op search collapse.

## Current-route coverage diagnostic

Best-current route across the 240 seed-challenge cells:

- sheet: `151`
- orbit: `72`
- filament: `16`
- recurrence: `1`
- family: `0`

The existing repertoire, especially sheet and orbit, already covers these synthetic structural demands better under the frozen equal candidate budget.

## Interpretation

`multiplex-capacity-v1` falsifies the useful version of the bundled hypothesis tested here: exposing raw index + quotient/residue identity + latent reuse + local response as one grammar did **not** create incremental structural recovery or niche coverage over the current repertoire.

The strongest evidence is not merely that a threshold was missed. The full grammar loses on every master seed, every challenge-family mean is negative, the regular-grid ablation is not worse, and the no-reuse ablation is better. The distinctive claim that index topology itself supplies useful additional capacity is therefore unsupported in v1.

This does **not** show that arithmetic aliasing, state-dependent exponentiation, or all discrete-index mechanisms are unproductive. Those were explicitly held out as materially different future hypotheses and cannot be injected post hoc into this consumed experiment.

## Next step

Per the preregistered stop rule:

```text
do not retune multiplex-capacity-v1 on these 20 seeds
```

Close this mechanism family as tested. The next active representation-level hypothesis should be materially different rather than a nearby multiplex parameterization. #81 / PR #82 (`sampling-invariance-v1`) qualifies: it tests the opposing idea that phenotype structure lives in a finite continuous spectral field and sampling coordinates are observations rather than latent identity.

PR #82 remains Stage-A excluded smoke only. Any later capacity comparison must receive its own frozen targets, budgets, and untouched holdout after the representation-validity stage passes.
