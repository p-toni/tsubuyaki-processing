# Roadmap review — maximizing learning progress

*Review of the [research roadmap](research-roadmap.md) and experiment portfolio at
`2b79bc9` (2026-10-31). These are recommendations; the roadmap is unchanged.
Numbers computed here are descriptive statistics on consumed archives. They
change no recorded grade, selection, or decision.*

## Summary

The project has built an excellent **vault** — preregistration, hashes, sealed
keys, closed populations — around a weak **thermometer**. Learning speed is now
limited by what the studies can measure, not by how safely they store it.

1. **The outcome measure is unvalidated.** The October studies replaced blinded
   human pairs with same-agent grades. Model-mediated artistic judges were tested
   prospectively twice and agreed with the human on 7/24 and 12/24 pairs. Every
   October delivery was graded B and no October candidate received an A. The
   compact-preflight gate failed on one such judgment (Wake).
2. **The length outcome was forecastable for free.** A mechanical, idiom-free
   minification of the readable source predicts the agent's compact length at
   0.88 ± 0.04 ([retrospective](../experiments/compressibility-forecast-retrospective-v1/README.md)).
   Sources forecast ≤ 300 delivered 10/10 on the first attempt; > 340 delivered
   0/5 across 10 attempts. The minification alone, audited exact over 720 frames,
   already fits for 10 of the 15 October deliveries. Under exact-equivalence
   compaction, length is decided while authoring, not while golfing.
3. **The gates could rarely pass, even for a real effect.** If a treatment truly raised delivery from 50%
   to 75%, the feedback-value gate would pass 14% of the time and the
   compact-preflight gate 34% (upper bounds; [gate-power.mjs](../experiments/compressibility-forecast-retrospective-v1/gate-power.mjs)).
   Against that alternative, a failed gate carries likelihood ratios of only 0.89
   and 0.76.
4. **Shared context is a choice.** Fresh sessions per arm and a separate blind
   judge would remove the contamination every October README discloses, and make
   cost measurable.
5. **Next:** calibrate the judge against the human (≈30 human minutes), measure the
   golf ceiling on closed failures, build a held-out difficulty-stratified brief
   bank with an A/A baseline, then spend intervention studies on the frontier.

## 1. What learning progress means operationally

Learning progress is decision-relevant uncertainty removed per unit of cost. Ask
four questions before freezing any protocol:

| Test | Failure mode it prevents |
| --- | --- |
| **Forecastable?** Write the expected outcome per arm and brief. | Running a study whose answer was already known. |
| **Valid instrument?** The outcome measure has demonstrated agreement with the artistic authority on this surface. | Precise measurement of the wrong thing. |
| **Powered?** Compute the gate's pass probability under the null and under the smallest effect worth adopting. | A gate that fails whether or not the treatment works. |
| **Frontier?** Target tasks where baseline success is intermediate, roughly 30–70%. | Ceiling tasks always pass; floor tasks always fail; both teach little. |

The last test is the "Goldilocks" principle from learning-progress-driven
curricula: competence improves fastest, and is most measurable, where it is
neither saturated nor absent.

## 2. Portfolio diagnosis

| Era | Studies | Outcome measure | Yield |
| --- | --- | --- | --- |
| Search runtime, through September 3 | ~100 experiment folders, 65 CI workflows | Mechanical proxies, with human gates at the end of chains | Of 8 interventions that reached a blinded human artistic gate, **2 passed**. The [complete workflow audit](../research-results/complete-workflow-audit-v2/results.md) then found 12/12 simple deliveries versus 0/12 for the research workflow. |
| Compact material, September 6–7 | 3 | 12 blinded human pairs each | **High.** Decisive results in two days: [SHEAR3 0/12](../research-results/compact-symplectic-material-v1/results.md), [PHASEPACK 2/10](../research-results/phase-native-material-v1/results.md), [MIXED12 4/12](../research-results/compact-material-grammar-portfolio-v1/results.md). |
| Agent loop, October 24–31 | pilot, feedback, preflight, Pulse vessel | Same-agent grades, 3–6 briefs | **Low per study.** Gates with 14–34% power, forecastable length outcomes, an uncalibrated judge. |

The October pivot rightly moved from proxies to the end-to-end task. It also
dropped the project's own earlier rule — "Human review remains the artistic
authority" — that the September studies applied so efficiently. *Autonomy
describes how the loop operates, not who measures it.* A blinded rating after a
run is measurement, not rescue.

The September studies also left a consistent human signal: at compact scale,
added material complexity lost to the smoother native form three times. The
model's Wake judgment penalized the compact construction for losing "material and
exciter expression". Material richness is exactly the axis on which the human
preferred the simpler form. Whether the human agrees about Wake is unknown and
cheap to find out (CAL-1).

Rigor is also unevenly allocated. `feedback-value-v1` archives 1,051 files (62 MB)
— including playback, pause/resume, and mobile-overflow gallery checks — to
support six pair outcomes graded by an uncalibrated judge.

## 3. New evidence: length is decided at authoring time

The [compressibility retrospective](../experiments/compressibility-forecast-retrospective-v1/README.md)
pairs all 24 unique archived compact posts with their readable sources.

| Forecast zone | Compacted sources | Delivered | Attempts |
| --- | ---: | ---: | ---: |
| green ≤ 300 | 10 | 10 | 10 |
| amber 301–340 | 3 | 2 | 4 |
| red > 340 | 5 | 0 | 10 |

- **Most deliveries needed no golf at all.** The mechanical minification is itself
  an exact program: audited over 720 frames, it reproduces every point of its
  readable source with zero error. For 10 of the 15 October deliveries (8 of 12
  unique delivered sources) it already fits within 280.
- **Golf is worth ~11–14%; representation is worth 25–40%.** First attempts reach
  0.89 of the mechanical forecast and second attempts 0.86. Representation changes
  moved Aperture 432 → 306 and Wake 457 → 264.
- **Feedback has a length price.** Observation-led revisions mostly added
  structure: late-arm Thread +62, Relay +52, Wake +48; adaptive Weave 294 → 346 and
  Exchange 316 → 385. Both of the latter became their brief's only B and failed
  length. Exchange's in-budget alternatives lost its two-body identity (C).
- **The late arm's 1/4 was retrodicted** from its frozen selections: three red,
  one amber.
- **"Art first, count later" may not transfer.** The supporting
  [description-length study](../experiments/description-length-pressure/results.md)
  had 12 candidates per route, so late pressure had fallbacks. With one to four
  candidates, late knowledge mostly means late failure. This is a testable
  question (GAUGE-1), not a settled one.

The forecast is a **fuel gauge, not a fitness function**. Use it as a covariate,
a difficulty stratifier, and — only if GAUGE-1 supports it — an authoring aid.
Thresholds were chosen post hoc on 18 sources and need prospective validation.

It also makes the roadmap's bottleneck table operational: a red-zone A/B candidate
is a representation problem, a green-zone C is a generation problem, and an amber
candidate is a golf question until GOLF-1 says otherwise.

## 4. Existing studies through this lens

| Study | Established | Limited by | Verdict |
| --- | --- | --- | --- |
| [Discovery pilot](../experiments/autonomous-discovery-pilot-v1/README.md) | The simple loop runs end to end on three representations | Green-zone briefs (forecasts 234–247); self-grades | Right first step; outcome was predictable |
| [Feedback value](../experiments/feedback-value-v1/README.md) | Feedback improves readable studies, not deliveries | 14% gate power; revisions pushed two briefs into red; ties; shared context | Its real finding is feedback's length price |
| [Compact preflight](../experiments/compact-preflight-v1/README.md) | Representation change rescued 2 of 3 red sources | Late arm predetermined; early arm knew the late trajectory; gate decided by one uncalibrated judgment | Informative content is the rescue rate and the Wake judgment; the latter needs human calibration |
| Compact material trio | Shallow compact enrichment loses to native | — | Exemplary information per cost; reuse the template |
| [Pulse vessel](../experiments/compact-representation-v1/protocol.md) (in flight) | Not yet run | See below | Amend before the first render |

### Pulse vessel, before anything is rendered

The roadmap's active priority — compact representations that keep artistic
quality — is the right target, and the data above sharpen it. Pulse vessel is a
weak first instrument for it. Nothing has been rendered, so a documented amendment
costs no evidence. The study as frozen has low expected information:

- **n = 1, off the frontier.** The brief has one body and no second actor,
  occlusion, or depth layers — the features shared by every archived length
  failure. The likely outcome is a pass that motivates another single case.
- **The two representations nearly coincide.** R2 solves its Cassini field for the
  transverse radius and tests `y² < c(x,t)² · cassini(x)`, shading by depth over
  radius. R1 uses `r(x,t) = c(x,t) · profile(x)` with the same contraction
  `1 − 0.6·exp(−40d²)` and the same cylindrical shading. The contrast reduces to
  base profile and raster versus parametric sampling, so a tie would say little
  about representation.
- **The success criterion is self-judged.**

Recommended amendment, committed before the first render: make a blind human pair
the success authority (best R1 versus best R2 readable; delivery versus best
readable); record forecasts after the selection freeze as a calibration point; log
session cost. Either apply R2's squeeze inside the field — for example a moving
local term in the distance product before thresholding — or record the convergence
as a limitation. Treat the result as a shakedown of these instruments, not as
evidence for the active priority. This review did not render its candidates and
records no count or forecast for them. A forecast was computed in scratch before
the boundary was noticed; it was not kept and is not reported. The committed
forecast tool refuses these sources until `selection.json` exists.

## 5. Proposed experiments, ranked by information per cost

### CAL-1 — Calibrate the self-judge against the human

*About 30 human minutes; no new candidates.*

**Question.** Do the agent's frozen pairwise judgments on the October surface agree
with a blinded human?

**Design.** About 20 archived pairs whose model judgment is already committed in
`decisions.md`, `selection.json`, or `candidate-reviews.json`, rendered as
side-by-side 12-second clips:

- *Consequential pairs:* Wake early v4 / late v2 (the gate-deciding judgment);
  Thread early v4 / late v2; Aperture early v3 / late v2; Twist adaptive v2 /
  batch v4; Twist batch v4 / v3; Divert adaptive v3 / batch v4; Weave adaptive v4
  / batch v3; Exchange adaptive v4 / batch v2; Exchange adaptive v4 / v3 (the
  merged surface that lost two-body identity).
- *Repair pairs (C → B), as attention checks:* late v1 / v2 for Thread, Relay,
  and Wake; pilot Fronds and Gather v1 / v2.
- *Four side-flipped repeats* of consequential pairs, measuring position bias and
  test–retest consistency. The earlier replacement study's 20/24 side-B human
  wins makes this worth checking.

Use the existing reviewer and sealed-key mechanics and commit ratings before
unblinding. Record whether the reviewer recognizes a pair from the published
galleries.

**Frozen rule.** The self-judge may serve as a provisional screen only with at least
75% agreement on decisive consequential pairs and no reversal of a gate-deciding
judgment. Otherwise blinded human pairs become mandatory for every artistic gate.

**Either way** it decides what every later study can use as its outcome, and
answers whether Wake was an artistic loss to the human. The judgments in those
closed populations remain recorded as they are; the calibration annotates them.

### GOLF-1 — Golf ceiling on closed failures

*Agent only; one session; diagnostic.*

**Question.** In the amber and red zones, is the two-attempt cap or the
representation binding?

**Design.** For the five red and one amber failed sources, a fresh session receives
the readable source and the archived exact-equivalence auditor and makes up to
eight syntax- and algebra-only attempts. Record the length of each attempt. No
population is rescued or rescored.

**Decision.** If the floor ratio reaches about 0.75, extra golf attempts — cheap,
because they need no rendering — lift the amber zone, and the compact-attempt
budget should change. Near 0.80 or above, representation is binding and effort
belongs entirely in authoring.

### BENCH-1 — Held-out, stratified brief bank with an A/A baseline

*16 isolated agent runs; about 15 human minutes.*

**Question.** What is the baseline's success rate per difficulty stratum, and how
noisy is one run?

**Design.** A separate session, or the human, authors 16 briefs in four structural
strata and hash-seals them:

| Stratum | Structure | Archived examples |
| --- | --- | --- |
| S1 | one body, one law | Hollow, Fronds |
| S2 | one body with a traveling or delayed event | Reflect, Relay, Separate |
| S3 | two coupled actors, or an actor and a medium | Wake, Exchange, Divert |
| S4 | depth order or occlusion | Aperture, Thread, Weave, Twist |

Split them into eight development and eight sealed test briefs. Run the unchanged
skill twice on each development brief in fresh sessions. Record forecast
trajectories, delivery, self-grades, and session cost. The human gives each
delivery a binary *keep* judgment — the primary outcome the
[complete workflow audit](../experiments/complete-workflow-audit-v2/README.md)
already defined — and judges each A/A pair.

**Outputs.** A competence map by stratum; the A/A disagreement rate, which sizes
every later gate; cost per kept result. The strata are themselves a hypothesis
about difficulty, and this tests it. Rerun the development set after each skill
change to get a learning curve. Open the test set only at milestones.

### GAUGE-1 — Does seeing the forecast while authoring help?

*S3/S4 briefs; two isolated arms.*

**Question.** Does a visible length gauge during readable exploration raise
human-judged kept deliveries, or cause the self-censorship seen in Wake?

**Design.** The baseline arm hides counts until selection, as now. The gauge arm
sees the forecast after each readable candidate. Both use the same budgets. The
outcome is blinded human keep judgments, plus a forced preference when both arms
deliver.

**Decision.** Keep the "art first, count later" rule in [SKILL.md](../SKILL.md) and
[compression promotion](compression-promotion.md) with fresh evidence, or replace
it with authoring against a gauge.

**Size.** Use BENCH-1's noise floor. As a planning anchor, 12 decisive human
comparisons give about 65% power at a true 3:1 preference; 24 give about 88%.

### CONS-1 — A construction bank for expressiveness per character

**Question.** Does a short reference of compact constructions mined from this
project's own successes raise S3/S4 delivery without a human-judged loss? Examples
include a shared sampler with visibility selection (Aperture v3), a highlighted
actor on a shared field (Wake v4), a common pulse delayed by identity (Relay), and
index-partitioned roles that share formulas. The bank should also record where a
construction cost identity, as in Exchange v3's merged surface.

**Design.** Same as GAUGE-1, or a 2×2 with it if budget allows. An interaction is
plausible: the bank probably matters most when the gauge shows the need.

**Decision.** Add the bank to the skill references or close it.

### Recorded alongside every study

Commit a `forecasts.json` with predicted delivery and preference per arm and brief
before any run, and score it afterward with a Brier score. Forecast skill over
successive studies is the research program's own learning curve. A study whose
outcome can be forecast confidently should be redesigned or skipped.

## 6. Process changes

1. **The human is the thermometer; the agent operates the loop.** Use blinded human
   pairs or within-brief rankings as gate outcomes; use model grades for triage.
2. **Isolate arms in fresh sessions, and judge in another.** This separates two
   kinds of independence the roadmap merges. A separate session cannot make taste
   independent, but it removes authorship, ordering, and memory contamination, and
   it blinds the judge to arm identity.
3. **Check power before freezing a gate.** Reject gates with less than 50% pass
   probability at the smallest effect worth adopting.
4. **Use two rigor tiers.** Screening studies: forecasts, human pairs or rankings,
   and exact verification of delivered posts. Confirmation and promotion: the full
   current custody. Clips, galleries, and playback QA are publication polish.
5. **Put the human gate first in any chain.** Two of eleven interventions survived
   it; screen before mechanical confirmation.
6. **Closed is not unreadable.** Keep the rule against tuning or rescoring closed
   populations. Allow labeled mechanism diagnostics that cannot change a recorded
   outcome, following the delivery-exposure diagnostic in the compact-grammar
   study. The retrospective above and GOLF-1 are such diagnostics.
7. **Separate brief authorship from solving.** Briefs should come from another
   session or the human and stay sealed until run.

## 7. Keep, stop, park

- **Keep:** preregistration and freezing; sealed keys; closure of negative branches;
  candid limitations; exact verification of delivered posts; the simple loop as
  baseline.
- **Stop:** model-only artistic gates; three- to six-brief gates with low power;
  gallery and playback QA in screening studies; briefs, arms, and grades authored
  in one shared context.
- **Park, unchanged:** learned search operators, automatic aesthetic judges, more
  filament machinery, and the research runtime as default.

## Suggested sequence

| Step | Work | Decision it unlocks |
| --- | --- | --- |
| 1 | CAL-1, GOLF-1, and the Pulse vessel amendment, in parallel | Outcome measure; compact-attempt budget |
| 2 | BENCH-1 development set with A/A runs | Noise floor; gate sizes; target strata |
| 3 | GAUGE-1, optionally crossed with CONS-1, on S3/S4 | Authoring policy in the skill |
| 4 | Sealed test set | First clean capability estimate per stratum |
