# Autonomous discovery pilot v1

This is a feasibility pilot of the existing agent plus coding and rendering tools.
The same agent authors the briefs, creates candidates, and evaluates them. These
are fresh tasks within this session, not independent held-out benchmarks or human
preference evidence. No new search engine or trained judge is part of this pilot.

## Frozen briefs

- **Hollow / B01:** A soft hollow form breathes through changing folds. Its cavity
  remains legible while the surrounding material deforms internally. A rigidly
  rotating outline or an ordinary oscillating line does not meet the brief.
- **Fronds / B02:** Several flexible fronds share a stable root. Bends travel toward
  the tips, with differences between fronds and coherent attachment throughout.
  The form should read as an organized living structure.
- **Gather / B03:** An organized swarm gathers into a readable structure and
  releases again. Individual paths remain coherent and the timing is staggered.
  Whole-object rotation and random jitter do not meet the brief.

## Budget and observation contract

Each brief gets at most four visually distinct readable candidates, including
revisions and representation switches. Preserve every candidate before rendering
and record observations before revising. Syntax repairs that change rendered
behavior count as another candidate. Infrastructure repairs are logged separately.
No replacing a failed brief, hidden parameter sweeps, or tuning prior populations.

Select by the brief and visual behavior before checking compact length. Allow at
most two compact attempts per brief, including any fallback. Preserve the readable
winner even if neither compact attempt survives. Readable source may exceed 280.

Use a 400x400 canvas and deterministic frame-based time at 60 fps. Observe frames
1..600 (ten seconds), with sixteen evenly spaced stills for initial visual review.
Choose motion rates that expose the required behavior within this interval. If a
representation needs a longer horizon, extend it before grading or compression
and retain that horizon for all subsequent comparisons in that brief. Never shorten
the horizon to rescue a result. No artificial seamless-loop claim.

## Acceptance and grading

Every delivered post must fit 280 raw and X-weighted characters including the
hashtag, execute in a pinned full p5.js browser runtime without errors, produce
finite geometry, keep at least 95% of point centers in frame, and maintain maximum
per-point motion of 10 px per frame over the complete horizon. Primitive identities
must be stable for that motion check; exceptions require explicit disclosure and
cannot count as passing this pilot's contract.

Before compression, record the defining relationships. Require the compact post
to preserve those relationships and match the readable geometry within 1e-7 at
every frame. Exact sampled raster parity in the same renderer provides an
additional check. No aesthetic changes hidden inside compression.

Artistic grade: A = distinctive finished work; B = coherent, interesting study
worth keeping; C = functioning demonstration; D = broken or incoherent. A discovery
success requires A/B, brief adherence, and successful compact delivery. Technical
passes do not imply artistic success. Honest failure counts as unsuccessful.

The reviewer will disclose the visual samples actually inspected, separately from
all-frame computational checks and playback tests. Model self-grades are provisional.
All three outcomes, attempts, revisions, costs available from tools, and human
interventions will be reported; no population-level reliability claim follows.

## Decision

Complete the simplest discovery loop on all three briefs, identify observed
bottlenecks, and update the roadmap only as far as the evidence supports. Keep
earlier results unchanged. Publication concerns reproducible sources and honest
results, not a claim of independently established artistic quality.
