# tsubuyaki-processing

An Agent Skill and research project for **autonomous discovery of compact mathematical animations**, expressed as original **#つぶやきProcessing**.

Given a fresh visual brief and an attempt budget, can an agent choose the mathematics, inspect what it made, and decide what to keep, revise, or abandon? A successful run delivers a worthwhile p5.js sketch without human creative intervention and verifies that its defining behavior survives compression. Aim for 280 characters including the hashtag. Keep a longer version when the extra code earns its place in the animation. Report its exact length and whether it fits a standard post.

For **Thirst**, the brief asked only for a second encounter changed by the first. The agent chose a feather and two equal drops of ink. The feather drinks the first drop. Half the second rolls off the tip. Clearing the stain makes the first encounter replay exactly for 360 frames. The chosen sketch takes 634 weighted characters, so economy remains an open question. [Watch the 12-second film](experiments/second-encounter-v1/thirst.mp4?raw=1) · [Sketch, reset test, and self-grade](experiments/second-encounter-v1/README.md)

Organic form and apparent life are the starting aesthetic. Earlier sketches preserve a traveling fold at 280 weighted characters, a pocket in silk at 316, and a transfer of spin at 375. Each archive records what survived compression and how the work was judged. [Pleated lantern](experiments/pleated-lantern-v1/README.md) · [Pearl and silk](experiments/pearl-and-silk-v1/README.md) · [Borrowed spin](experiments/borrowed-spin-v1/README.md) · [Research roadmap](references/research-roadmap.md)

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

When aiming for 280, the executable suffix `//#つぶやきProcessing` leaves **259 X-weighted characters for code**. The checker reports both counts and exits with status 1 when the standard-post size is exceeded.

```sh
node scripts/check-length.mjs post.txt
```

An optional command can produce a first compact draft of a selected arithmetic sketch. Render the exact post over the chosen time span and verify that it preserves the relationships that made the readable sketch work. [Mechanical draft and archive results](experiments/compressibility-forecast-retrospective-v1/README.md)

## Where to look

- [Examples](examples/) and [templates](templates/) provide starting points.
- [Discovery search](references/discovery-search.md) offers route-specific heuristics when iteration is useful.
- [Discovery state](references/discovery-state.md) provides optional reproducible bookkeeping for resumable searches and experiments. Create state with the CLI's `init` command.
- [Compression promotion](references/compression-promotion.md) explains visual selection, compression survival and fallback.
- [Autonomous discovery prototype](prototypes/autonomous-discovery/README.md) is a separate research runtime. It does not implement the final golf boundary and is not required to use the skill.

## Evidence and limits

Pulse vessel produced one provisional B from four readable candidates. Its 336- and 323-weighted-character attempts missed that study's required post size. Their visual equivalence remains unverified. [Pulse vessel archive](experiments/compact-representation-v1/README.md)

The compact-preflight comparison delivered 3/4 briefs with early checking and 1/4 with late checking. Aperture recovered without a clear artistic loss. The delivered Wake was less expressive than the late readable selection, which kept early length checks from becoming the default. All four deliveries passed 720-frame verification and 64 sampled image comparisons (48 unique). The same author knew both arms, and the early arm used more readable candidates. [Compact-preflight comparison](experiments/compact-preflight-v1/README.md)

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
