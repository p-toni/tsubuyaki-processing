# Roadmap review — maximizing learning progress, autonomously

*Review of the [research roadmap](research-roadmap.md) and experiment portfolio at
`2b79bc9` (2026-10-31), under the constraint that experiments run with **no human
involvement**. These are recommendations; the roadmap is unchanged. Numbers
computed here are descriptive statistics on consumed archives. They change no
recorded grade, selection, or decision.*

## Summary

The project has built an excellent **vault** — preregistration, hashes, sealed
keys, closed populations — around a weak **thermometer**. With no human available
as a reference, the thermometer has to be calibrated the way thermometers are
calibrated without one: against **fixed points**, cases whose answer is known by
construction.

1. **The outcome measure is uncalibrated.** October gates rest on same-agent
   grades that were never tested for consistency or sensitivity. Every October
   delivery was graded B and no October candidate received an A. The
   compact-preflight gate failed on one such judgment (Wake).
2. **The length outcome was forecastable for free.** A mechanical, idiom-free
   minification of the readable source predicts the agent's compact length at
   0.88 ± 0.04 ([retrospective](../experiments/compressibility-forecast-retrospective-v1/README.md)).
   Sources forecast ≤ 300 delivered 10/10 on the first attempt; > 340 delivered
   0/5 across 10 attempts. The minification alone, audited exact over 720 frames,
   already fits for 10 of the 15 October deliveries. Under exact-equivalence
   compaction, length is decided while authoring, not while golfing.
3. **The gates could rarely pass, even for a real effect — and autonomy is the
   cure.** Allowing for briefs that differ in difficulty, the feedback-value rule
   passes 9% of the time if a treatment adds 25 points of delivery. Without human
   time as the bottleneck, 24 briefs × 3 isolated runs per arm reach about 95%
   power at an 11% false-pass rate ([gate-power.mjs](../experiments/compressibility-forecast-retrospective-v1/gate-power.mjs)).
4. **Independence must come from structure.** Brief author, solver, judges, and
   auditor belong in separate sessions. Requirements that can be specified become
   executable contracts; a validated model panel judges only what remains.
5. **Next, all on existing archives and without new solver runs:** validate a
   judge panel, build executable brief contracts, measure the golf ceiling. Then
   run a sealed, stratified benchmark at power and spend intervention studies on
   the frontier.

## 1. What learning progress means operationally

Learning progress is decision-relevant uncertainty removed per unit of cost. Ask
four questions before freezing any protocol:

| Test | Failure mode it prevents |
| --- | --- |
| **Forecastable?** Write the expected outcome per arm and brief. | Running a study whose answer was already known. |
| **Valid instrument?** The outcome measure is consistent and passes known-answer controls on this surface. | Precise measurement of noise or of the wrong thing. |
| **Powered?** Compute the gate's pass probability under the null and under the smallest effect worth adopting. | A gate that fails whether or not the treatment works. |
| **Frontier?** Target tasks where baseline success is intermediate, roughly 30–70%. | Ceiling tasks always pass; floor tasks always fail; both teach little. |

The last test is the "Goldilocks" principle from learning-progress-driven
curricula: competence improves fastest, and is most measurable, where it is
neither saturated nor absent. A fully autonomous program can apply it to itself
(CURRICULUM-1).

## 2. Portfolio diagnosis

| Era | Studies | Outcome measure | Yield |
| --- | --- | --- | --- |
| Search runtime, through September 3 | ~100 experiment folders, 65 CI workflows | Mechanical proxies, with outcome gates at the end of chains | Of 8 interventions that reached a blinded human artistic gate, **2 passed**. The [complete workflow audit](../research-results/complete-workflow-audit-v2/results.md) then found 12/12 simple deliveries versus 0/12 for the research workflow. |
| Compact material, September 6–7 | 3 | 12 blinded human pairs each | **High.** Decisive results in two days: [SHEAR3 0/12](../research-results/compact-symplectic-material-v1/results.md), [PHASEPACK 2/10](../research-results/phase-native-material-v1/results.md), [MIXED12 4/12](../research-results/compact-material-grammar-portfolio-v1/results.md). |
| Agent loop, October 24–31 | pilot, feedback, preflight, Pulse vessel | Same-agent grades, 3–6 briefs | **Low per study.** Low-power gates, forecastable length outcomes, an uncalibrated judge. |

The October pivot rightly moved to the end-to-end task and to unattended
operation. What it skipped is instrument validation. The project already knows
how to validate an instrument that has no ground truth: when pixel MAE failed,
the measurement-rehabilitation phase (#64–#67 in the
[earlier roadmap](../experiments/ROADMAP.md)) required that a metric "must first
defeat adversarial controls before it is allowed to evaluate search algorithms".
The artistic judge never went through that phase.

Two earlier lessons transfer without any human. A decisive outcome measure with a
dozen or more comparisons answers within days, as in September. And an outcome
gate placed first saves the mechanical work that end-of-chain gates later
invalidated, as in the search-runtime era.

Rigor is also unevenly allocated, and autonomy multiplies the cost.
`feedback-value-v1` archives 1,051 files (62 MB), including playback,
pause/resume, and mobile-overflow gallery checks, to support six pair outcomes
graded by an uncalibrated judge.

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
| [Feedback value](../experiments/feedback-value-v1/README.md) | Feedback improves readable studies, not deliveries | Low gate power; revisions pushed two briefs into red; ties; shared context | Its real finding is feedback's length price |
| [Compact preflight](../experiments/compact-preflight-v1/README.md) | Representation change rescued 2 of 3 red sources | Late arm predetermined; early arm knew the late trajectory; gate decided by one uncalibrated judgment | Informative content is the rescue rate; the Wake judgment needs a validated panel |
| Compact material trio | Shallow compact enrichment loses to native | — | Exemplary information per cost; reproduce its decisiveness with a validated panel and larger n |
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

Recommended amendment, committed before the first render:

- An executable contract for the brief, written in a separate session from the
  brief text alone and frozen before rendering. Validate it against adversarial
  programs built from the brief's own failure list: global scaling, rigid motion,
  unrelated flashing, a decorative traveling stripe, disconnected blobs, and a
  break at the waist. These are new programs, so building them observes nothing
  about R1 or R2.
- Self-grades remain, labeled provisional, until a JUDGE-1 panel exists.
- Forecasts recorded after the selection freeze as a calibration point, plus
  session cost.
- R2's convergence either fixed — for example, a moving local term in the
  distance product before thresholding — or recorded as a limitation.

Treat the result as a shakedown of these instruments, not as evidence for the
active priority. This review did not render its candidates and records no count
or forecast for them. A forecast was computed in scratch before the boundary was
noticed; it was not kept and is not reported. The committed forecast tool refuses
these sources until `selection.json` exists.

## 5. Proposed experiments, ranked by information per cost

Every study below runs without human involvement.

### JUDGE-1 — Validate a judge panel before it gates anything

*Archived candidates plus programmatic degradations; judge sessions only.*

**Question.** Which distinctions can a model judge panel make reliably on this
surface?

Without a human, some model judge is unavoidable: the October self-grades already
are one. JUDGE-1 makes that judge explicit and tests it. Using a judge to
evaluate finished runs is distinct from using one as a search objective, which
stays parked.

**Design.**

- *Panel.* Three judges, each in a fresh session with no authoring context, using
  at least two different models and two evidence formats: a 16-frame contact
  sheet and a motion sheet of frame differences. Sides are randomized and every
  pair is shown in both orders.
- *Fixed points.* Archived B-grade readable sources paired with programmatic
  degradations at graded strength, applied through the same instrumented runtime
  the auditor uses: drop a fraction of points, add positional jitter, freeze or
  strobe time, flatten shading, push the framing toward an edge, and — once
  contracts exist — violate a named requirement. The better side is known by
  construction, so no taste is needed to score it.
- *Real pairs.* The archived consequential pairs (Wake, Thread, Aperture, Twist,
  Divert, Weave, Exchange) measure inter-judge agreement. The panel also re-judges
  the frozen October verdicts, which annotates them without reopening their
  populations.

**Output.** A versioned **judge card**: flip consistency, known-answer accuracy as
a function of degradation strength, inter-judge agreement, and the resulting
resolution.

**Frozen rule.** A panel may gate only distinctions on which it shows at least 90%
flip consistency and at least 90% known-answer accuracy. Fine B-versus-B
preferences may gate only if inter-judge agreement reaches κ ≥ 0.6; otherwise
they are reported descriptively.

**Decision.** What every later study may use as its quality outcome, and whether
the Wake verdict that failed compact-preflight survives a validated panel.

### CONTRACT-1 — Make brief adherence executable

*Archived briefs and candidates; no new solver runs.*

**Question.** How much of brief adherence can be verified from the exact point
stream instead of judged?

**Design.** For each of the 13 archived October briefs, a separate session writes
property tests from the brief text alone. They run over the per-frame points and
rasters that the archived auditor already produces. Examples: silhouette
connectivity, localized rather than global change, the travel path of the change
centroid, ordered response peaks, lag between drive and response, anchored
boundaries, and occlusion order by rendering with and without a layer. Where a
requirement needs roles (exciter versus membrane), require a declared probe and
cross-check it against the render, as the existing math-family probe convention
does. Validate each contract on:

- archived candidates judged to meet their requirements;
- candidates judged unmet — for example Aperture v1, which the agent first passed
  although its opening never closed;
- adversarial variants built from each brief's own listed failure modes, such as
  "a ridge that simply moves in lockstep with the exciter".

**Output.** A contract library and, for each requirement, whether it is
executable, partly executable, or judgment-only.

**Decision.** Executable requirements become objective gates; the panel handles
only the residual.

### GOLF-1 — Golf ceiling on closed failures

*One solver session; diagnostic.*

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

### BENCH-1 — Sealed, stratified brief bank with replicated runs

*36 solver sessions for the development set.*

**Question.** What is the baseline's success rate per difficulty stratum, and how
much does one run vary?

**Design.** A brief-author session — preferably a different model or prompt from
the solver — writes 24 briefs. Each comes with an executable contract, a reference
solution that proves feasibility, and adversarial negatives. They are hash-sealed
and split into 12 development and 12 test briefs across four structural strata:

| Stratum | Structure | Archived examples |
| --- | --- | --- |
| S1 | one body, one law | Hollow, Fronds |
| S2 | one body with a traveling or delayed event | Reflect, Relay, Separate |
| S3 | two coupled actors, or an actor and a medium | Wake, Exchange, Divert |
| S4 | depth order or occlusion | Aperture, Thread, Weave, Twist |

The unchanged skill runs each development brief three times in fresh sessions.
Scores are exact verification and length, contract pass, panel judgment at its
validated resolution, and session cost. The reference solution's forecast gives
each brief an independent difficulty score.

**Outputs.** Per-brief success probability and a competence map by stratum;
run-to-run variance, which sizes later gates; cost per verified, contract-passing
delivery. The strata are themselves a hypothesis about difficulty, and this tests
it. Rerun the development set after each skill change for a learning curve. Open
the test set only at milestones.

### GAUGE-1 — Does seeing the forecast while authoring help?

*S3/S4 briefs; two isolated arms.*

**Question.** Does a visible length gauge during readable exploration raise
verified deliveries without lowering quality, or cause the self-censorship seen
in Wake?

**Design.** The baseline arm hides counts until selection, as now. The gauge arm
sees the forecast after each readable candidate. Both use the same budgets. The
primary outcome is the rate of verified, contract-passing deliveries; the
secondary outcome is panel preference at its validated resolution; cost is
recorded.

**Size.** Briefs × three runs per arm, set from BENCH-1's variance. As an anchor,
12 briefs reach about 76% power for a 25-point gain and 24 briefs about 95%, with
an 11% false-pass rate.

**Decision.** Keep the "art first, count later" rule in [SKILL.md](../SKILL.md) and
[compression promotion](compression-promotion.md) with fresh evidence, or replace
it with authoring against a gauge.

### CONS-1 — A construction bank for expressiveness per character

**Question.** Does a short reference of compact constructions mined from this
project's own successes raise S3/S4 delivery without a loss in panel-judged
quality? Examples include a shared sampler with visibility selection
(Aperture v3), a highlighted actor on a shared field (Wake v4), a common pulse
delayed by identity (Relay), and index-partitioned roles that share formulas. The
bank should also record where a construction cost identity, as in Exchange v3's
merged surface.

**Design.** Same as GAUGE-1, or a 2×2 with it. An interaction is plausible: the
bank probably matters most when the gauge shows the need.

**Decision.** Add the bank to the skill references or close it.

### CURRICULUM-1 — Let the program choose its next briefs

*After contracts and a judge card exist.*

A generator session proposes new briefs with contracts. The program tracks success
by stratum across skill versions and allocates new briefs where success is
intermediate and changing. The meta-question is whether the development-set
learning curve rises faster than under uniform brief sampling at equal compute.
This is the autonomous form of maximizing learning progress. The sealed test set
stays outside the curriculum.

### Recorded alongside every study

Before any run, the research session commits a `forecasts.json` with predicted
delivery, contract pass, and preference per arm and brief. Afterward, score it
with a Brier score. Forecast skill over successive studies is the program's own
learning curve. A study whose outcome can be forecast confidently should be
redesigned or skipped.

## 6. Process changes

1. **Separate the powers.** Brief author, solver, judges, and auditor run in
   different sessions. Judges never see authoring context and never judge their
   own outputs. Structure supplies the independence that shared context removed.
2. **Execute before judging.** Every requirement that can be a contract is one;
   the panel decides only the residual.
3. **No gate without a judge card.** Validate the panel first, then version and
   freeze it per study. Keep a development panel for iteration and a separate test
   panel for decisions, so the solver is never tuned against its own examiner.
4. **Size by power, not by convenience.** Compute is now the binding cost. Reject
   gates with less than 50% pass probability at the smallest effect worth adopting.
5. **Use two rigor tiers.** Screening studies: forecasts, contracts, panel
   judgments, and exact verification of delivered posts. Confirmation and
   promotion: the full current custody. Clips, galleries, and playback QA are
   publication polish; at autonomous scale they become the dominant cost.
6. **Put the outcome gate first in any chain.** Two of eleven interventions
   survived it historically; screen before mechanical confirmation.
7. **Closed is not unreadable.** Keep the rule against tuning or rescoring closed
   populations. Allow labeled mechanism diagnostics that cannot change a recorded
   outcome, following the delivery-exposure diagnostic in the compact-grammar
   study. The retrospective above, GOLF-1, and the archival parts of JUDGE-1 and
   CONTRACT-1 are such diagnostics.
8. **Label every claim by its instrument:** mechanically verified,
   contract-verified, or panel-judged with a version.

## 7. What full autonomy can and cannot establish

It can establish delivery reliability, contract-verified brief adherence, cost,
robustness, transfer across strata, and panel-judged preference with known
consistency. It cannot establish that people would find the work worthwhile.
Earlier prospective tests found model and human choices diverging on this
project's surfaces (7/24 and 12/24 agreement), so panel-judged quality is a model
standard, not a proxy for human taste. That is a legitimate operating definition;
the [README](../README.md) already requires keeping it distinct from human
validation.

## 8. Keep, stop, park

- **Keep:** preregistration and freezing; sealed keys; closure of negative branches;
  candid limitations; exact verification of delivered posts; the simple loop as
  baseline.
- **Stop:** self-graded gates; gates on distinctions finer than the panel's
  validated resolution; briefs, arms, and grades authored in one shared context;
  three- to six-brief gates with low power; gallery and playback QA in screening
  studies.
- **Park, unchanged:** learned search operators, automatic aesthetic judges as
  search objectives, more filament machinery, and the research runtime as default.

## Suggested sequence

| Step | Work | Decision it unlocks |
| --- | --- | --- |
| 1 | JUDGE-1, CONTRACT-1, and GOLF-1 on archives, in parallel; Pulse vessel amendment | Quality outcome and its resolution; executable adherence; compact-attempt budget |
| 2 | BENCH-1 development set, three runs per brief | Run-to-run variance; competence map; gate sizes |
| 3 | GAUGE-1, optionally crossed with CONS-1, on S3/S4 at power | Authoring policy in the skill |
| 4 | Sealed test set, then CURRICULUM-1 | Capability estimate per stratum; autonomous experiment allocation |
