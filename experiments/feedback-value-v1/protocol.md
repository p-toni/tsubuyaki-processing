# Rendered feedback value v1 — frozen prospective comparison

## Decision and limits

Does intermediate rendered feedback improve compact discoveries over generating
a batch before seeing renders, enough to justify additional revision? Test the
existing agent and tools; do not build a search engine or train a judge.

One primary agent authors both arms, the briefs, and provisional ratings in one
conversation. It may remember its own batch plans. This is a comparison within
that agent, not independent trials, blinded authorship, human validation, or a
population success-rate estimate. Exact source commitments prevent batch edits
after feedback; they cannot remove shared-context effects. No claim of cleanly
isolated causal effects follows from this design alone.

## Six fresh briefs

- **F01 Separate:** One material body separates into two clearly spaced lobes
  and reunites. Material deforms during the transition. Merely translating two
  rigid circles, fading one out, or replacing one image with another fails.
- **F02 Weave:** A woven structure has crossing bands with readable alternating
  over/under relationships while a disturbance travels through it. A flat grid,
  transparent crossings with no depth order, or global flicker fails.
- **F03 Reflect:** A localized disturbance travels across a finite membrane,
  reflects at the far edge, and returns. Both lateral edges stay anchored.
  Uniform whole-sheet oscillation without a localized traveling event fails.
- **F04 Exchange:** Two soft bodies with fixed centers exchange deformation,
  with a visible passage of influence between them. The receiving body responds
  after the passage. Alternating sizes with an unrelated decorative bridge fails.
- **F05 Twist:** A hanging sheet twists through depth while both upper corners
  stay fixed. Its moving fold has readable front/back occlusion. A rotating flat
  rectangle, detached corners, or transparent overlap without depth order fails.
- **F06 Divert:** A continuous stream splits around a persistent empty obstacle
  and rejoins downstream. Paths are coherent; points never pass through the
  obstacle. Simple circulation around a ring without upstream/downstream flow
  fails. Off-canvas recycling is allowed as declared below.

These are outcome requirements, not required formula families. They are authored
for this experiment and not independently held out. Every brief remains in the
result even if both arms fail.

## Arms, order, and budget

For each brief, preserve four readable batch candidates before rendering anything
in this study. Copy the first batch candidate as the adaptive starting candidate.
Commit all batch source hashes and shared starts before any rendered feedback.

Finish adaptive generation for all six briefs before rendering the remaining
batch candidates. Each adaptive run may inspect its own candidates, revise,
change representation, or keep an incumbent. Reusing a planned batch alternative
counts against its allowance. It may stop early when no concrete worthwhile
improvement is identified. It may not inspect unrendered batch images.

Each arm has at most four readable candidates and two compact attempts per brief,
including fallbacks. A behavior-changing repair counts as a candidate. Execution
and geometry diagnostics count as feedback and cannot revise a frozen batch.
Infrastructure repairs do not consume creative budget, but must be logged.
Shared initial renders are reused and charged to both arm budgets; physical
render counts are reported separately. No hidden sweeps, brief replacements,
or parameter tuning after terminal selection.

After generation, inspect every candidate made by each arm and freeze selection,
brief adherence, provisional grade, and defining relationships before counting
characters. Both arms get this same terminal selection opportunity. Keep a ranked
fallback only if it was already inspected and meets the brief. Compression may
change syntax but not the selected mathematical behavior.

Record actual candidate, render, review, and compact-attempt counts. Report known
wall times separately from active effort. Tokens, cost, or active reasoning time
may be unavailable; do not infer equal total cost from equal candidate caps.

## Rendering and technical contract

Use full p5.js 1.11.3, 400×400 pixels, and frames 1–720 at 60 fps (12 seconds).
Inspect sixteen uniformly spaced stills over that interval for every candidate.
No shorter or extended horizon is allowed in this comparison. Record sampled
visual review separately from complete numerical checks and playback testing.

A delivered post must fit 280 raw and X-weighted characters including its hashtag,
execute without browser errors, and preserve the selected readable coordinates
and drawing styles at every frame (coordinate tolerance 1e-7). Require finite
geometry, stable primitive identities, at least 95% of point centers in frame,
and at most 10 px movement per indexed point per frame. Final selected readable
and compact samples must also have identical pixels in the same raster runtime.

F06 alone permits horizontal recycling: a point may leave through x>395 and
reappear at x<5, or the reverse. For those transitions only, measure horizontal
movement modulo 400; vertical movement must remain within the same 10 px combined
limit. Report reset counts. A jump anywhere else remains a failure. This exception
is frozen for open flow before any candidates and is not available to rescue
other briefs. It does not permit teleporting through the visible obstacle.

All formulas and full sampled archives survive failure. A readable artistic
discovery that cannot be delivered still counts as an unsuccessful compact run.

## Review, comparison, and advancement

Use the pilot rubric: A = distinctive finished work, B = coherent interesting
study worth keeping, C = functioning demonstration, D = broken/incoherent.
Record each brief requirement as met, unmet, or uncertain. Uncertain adherence
does not count as success. A run succeeds only with all requirements met, A/B
quality, and passing exact compact delivery. Grades are model-only and provisional.

For each pair, an arm wins if it alone succeeds. If both succeed, prefer one only
when the final delivered animation has a clear, named expressive advantage across
the horizon. Otherwise record equivalent. If neither succeeds, record both-fail;
do not turn a prettier failure into a discovery win. Also report readable outcomes
and delivered-only preferences separately so compression cannot hide losses.

Provisional advancement requires at least four adaptive pair wins, no more than
one batch win, and no fewer adaptive compact successes. This is a practical gate
for another prospective test, not statistical significance or human validation.
If it passes, retain adaptive revision and identify which observations helped.
If it fails, do not expand revision machinery: keep a small first-candidate loop,
revise for explicit observed shortcomings, and investigate any repeated unmet
requirement. A batch advantage would support removing unnecessary revision.

Freeze results before changing the roadmap. Do not tune this consumed population
to improve its grades. No mid-run human creative decisions are required.
