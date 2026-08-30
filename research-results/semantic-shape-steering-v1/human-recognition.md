# Human recognition follow-up

## Status

**HUMAN_SEMANTIC_RECOGNITION_NOT_DEMONSTRATED**

The mechanical steering result remains `SEMANTIC_SHAPE_STEERING_MECHANICALLY_PROMISING`, but the stronger product-level claim — that a person can look at the generated output and recognize the requested named shape — is not supported by this review.

## Frozen package

Recognition workflow run: `33314386210`

Anonymous review artifact:
- id: `9733029514`
- digest: `sha256:ebcf3afe48c4965f2b36062a213456586d7793dd0cff78db64bdf128f85a6399`

Sealed key artifact, opened only after the reviewer had submitted an initial spontaneous mapping and then an invalid duplicate forced-choice completion:
- id: `9733029735`
- digest: `sha256:c8f9f65e727544a0b60a5230a57eaa6f61c2102a5057a39b65461fcd9260f138`

## Revealed key

- A = flower
- B = fish
- C = tree
- D = star
- E = crescent
- F = butterfly
- G = heart
- H = letter-a

## Human review evidence

Before the key was opened, the reviewer spontaneously identified only four panels with confidence:

- H -> heart
- D -> fish
- G -> butterfly
- E -> tree

All four were incorrect under the sealed key:

- H was letter-a
- D was star
- G was heart
- E was crescent

The reviewer explicitly reported no recognizable match for star, letter-a, or flower, and did not initially assign crescent.

A subsequent forced-choice completion was not a valid one-to-one assignment because panel F was assigned to both star and letter-a and panel E had already been assigned to tree before also being assigned to crescent. Therefore the preregistered `6/8 exact matches` forced-choice gate is formally **unscorable** for this review and should not be reported as a numeric forced-choice failure.

Among the second-round stated associations, `crescent -> E` was correct; the remaining stated associations were incorrect.

## Interpretation

The current sparse-geometry steering objective can move candidates closer to frozen target silhouettes according to geometric metrics, but those improvements do not reliably preserve the semantic identity that a human reviewer perceives.

This creates a clear construct-validity boundary:

> geometric target recovery != human-recognizable semantic shape formation.

Do not use the positive mechanical result to claim that the system can yet generate a human-recognizable requested shape.

## Research consequence

Do not tune this exact eight-concept / 60-budget protocol on the consumed seeds or display seeds.

A follow-up must change the **semantic objective/representation**, not merely increase search budget or retune the existing sparse-geometry distance. Candidate directions should be tested on fresh concepts/seeds and should explicitly optimize perceptual/structural invariants that survive the incumbent grammar, with human recognition remaining the authority for the final claim.
