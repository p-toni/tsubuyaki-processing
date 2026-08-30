# Perceptual semantic steering v1 — result

**Decision:** `PERCEPTUAL_SEMANTIC_STEERING_NOT_READY`

Authoritative workflow run: `33318093451`  
Aggregate artifact: `9734211299`  
Digest: `sha256:c5d6da3daf0b647d6451068ef5950a57a3ade22989965a59376995f0535335c6`

The discriminative perceptual selector is materially better than the previous sparse-geometry selector, but it does not meet the preregistered semantic promotion bar.

## Strong evidence

- 96/96 paired blocks complete at exact equal budget.
- mean held-out target-F1 delta: `+0.1159155115`
- one-sided 95% lower bound: `+0.0916290217`
- mean held-out target-vs-alternative margin delta: `+0.0916628700`
- one-sided 95% lower bound: `+0.0601268798`
- held-out top-1: `17.71% -> 38.54%` (`+20.83` percentage points)
- every one of the eight fresh concepts has positive mean held-out F1 delta.

## Failed promotion gates

- held-out top-1 must be >=60%; observed `38.54%`.
- selector-space top-1 must be >=70%; observed `58.33%`.
- at least 5/8 concepts must individually reach >=50% held-out top-1; observed 4/8.

Weakest semantic identities are `letter-s` (0% held-out top-1), `spiral` (8.3%), `umbrella` (8.3%), and `crown` (25%). In contrast, `diamond` (83.3%), `lightning` (75%), `sailboat` (58.3%), and `leaf` (50%) show that the objective can work when the incumbent search space contains a compatible global form.

## Interpretation

The human failure in semantic-shape-steering-v1 was not only an objective-metric problem. A more global and discriminative objective delivers a large mechanical gain, yet some concepts remain nearly unreachable under the current intrinsic-1D route repertoire and fixed runtime budget.

The next experiment should therefore distinguish **representation/search-space capacity** from **selector quality**. Do not tune this exact perceptual metric on the consumed seeds. Audit whether large target-blind archives from the current routes contain held-out-recognizable instances of the weak concepts at all. If they do not, the next intervention belongs in the representation/grammar layer rather than the selector.
