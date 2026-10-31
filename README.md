# tsubuyaki-processing

An Agent Skill and research project for **autonomous discovery of compact mathematical animations**, expressed as original **#つぶやきProcessing**.

Given a fresh visual intent and a bounded budget, the agent should choose a representation, construct and inspect animated programs, use rendered feedback to improve or change direction, and deliver a verified result without requiring human rescue.

The research product is that discovery capability. Finished animations provide concrete evidence of its usefulness. Success requires worthwhile behavior, sound decisions, and transfer across different briefs; unattended execution or a large candidate archive alone does not establish it. This is the project's objective, not a claim that general autonomous discovery has already been demonstrated.

A successful run delivers a compelling, runnable p5.js sketch that retains its defining behavior in a complete post of at most 280 characters. Readable exploration may exceed that limit before compression. An honest failure is a valid way to stop, but still counts as an unsuccessful discovery attempt.

The [research roadmap](references/research-roadmap.md) defines the current milestone and evidence needed. The starting aesthetic is organic form and apparent life emerging from shared mathematical rules; no single formula family or search architecture defines the project.

## Use the skill

Start with [SKILL.md](SKILL.md). The simplest autonomous baseline uses the agent's existing coding, rendering, and inspection tools:

```text
choose a suitable mathematical representation
→ build and inspect a readable sketch
→ use observations to revise or change representation when useful
→ compress while preserving its cause and animation
→ verify the exact post
```

Keep a good incumbent and stop within the budget. More search, a larger archive or a higher diagnostic score does not by itself improve the art. The separate research runtime is optional; autonomy does not depend on adopting it.

The executable suffix `//#つぶやきProcessing` leaves **259 X-weighted characters for code**. Check the complete post:

```sh
node scripts/check-length.mjs post.txt
```

A length pass is only one requirement. Render the exact code across a meaningful temporal horizon and verify that compression preserved the relationships that made the selected sketch work.

## Where to look

- [Examples](examples/) and [templates](templates/) provide starting points.
- [Discovery search](references/discovery-search.md) offers route-specific heuristics when iteration is useful.
- [Discovery state](references/discovery-state.md) provides optional reproducible bookkeeping for resumable searches and experiments. Create state with the CLI's `init` command.
- [Compression promotion](references/compression-promotion.md) explains visual selection, compression survival and fallback.
- [Autonomous discovery prototype](prototypes/autonomous-discovery/README.md) is a separate research runtime. It does not implement the final golf boundary and is not required to use the skill.

## Evidence and limits

The [compact-preflight comparison](experiments/compact-preflight-v1/README.md) delivered 3/4 briefs with early checking and 1/4 with late checking. Aperture recovered without a clear artistic loss, but the delivered Wake was less expressive than the late readable selection. The no-regression gate therefore failed, and the production policy remains unchanged. All four deliveries passed 720-frame verification and 64 sampled image comparisons (48 unique). The same author knew both arms, and the early arm used more readable candidates; this is provisional engineering evidence, not a clean causal effect or equal-cost advantage. The next priority is compact representations that preserve artistic quality.

The [rendered-feedback comparison](experiments/feedback-value-v1/README.md) delivered four of six briefs in each arm: zero adaptive wins, one batch preference, three equivalents, and two both-fail pairs. Adaptive revision improved two additional readable studies, but neither passed the compact boundary within its budget. All eight delivered posts passed 720-frame verification and 128 sampled image comparisons. The same agent authored and graded both arms in shared context; this does not establish broad batch superiority or a clean causal effect. The advancement rule failed; revision remains targeted at concrete observed shortcomings.

The [first complete discovery pilot](experiments/autonomous-discovery-pilot-v1/README.md) delivered three different compact studies from five readable candidates and two observation-led revisions. All final posts passed 600-frame execution and geometry checks; 48 sampled readable/compact image pairs matched exactly. The same agent authored the briefs and gave all three provisional B grades. This establishes feasibility on those tasks, not independent artistic validation, a reliable success rate, or the causal benefit of visual feedback.

The [paired route-search study](experiments/paired-route-search/results.md) suggests useful route-specific starting points. Its aesthetic audit used the same model that produced the experiment, after proxy-based candidate reduction. It supports working heuristics, not a universally optimal stage schedule.

The [description-length study](experiments/description-length-pressure/results.md) found 3/4 deployable winners with late-only compression and 4/4 with preflight. Early filtering also achieved 4/4 but removed 17/48 candidates before visual review. This small study motivates checking compression before committing to a deployment candidate; it does not require every sketch to run a search experiment.

Mechanical gains do not establish artistic gains. The [family projected-spectral review](research-results/family-projected-spectral-artistic-v1/results.md) found 18 equivalent pairs and only six decisive judgments, with two favoring projected-spectral. Artistic support was not demonstrated; that runtime remains opt-in and default-off.

Research protocols, code and results remain in [experiments](experiments/), [research-results](research-results/) and [research-commitments](research-commitments/). Their results apply to their tested surfaces. Model self-assessment is provisional evidence and must not be presented as independent human validation. These records support evaluation and reproduction; they are not prerequisites for running the skill.

## Local checks

The skill's JavaScript tools use Node.js built-ins:

```sh
node scripts/test-discovery-state.mjs
node --test scripts/test-png.mjs
```

Python prototype setup and tests are documented in its own README.
