# tsubuyaki-processing

An Agent Skill for original **#つぶやきProcessing**: compact mathematical systems whose animations are richer than their source.

The deliverable is a compelling, runnable p5.js sketch that retains its defining behavior in a complete post of at most 280 characters.

## Use the skill

Start with [SKILL.md](SKILL.md). The ordinary workflow is:

```text
choose a suitable mathematical representation
→ build and inspect a readable sketch
→ explore alternatives if they would help
→ compress while preserving its cause and animation
→ verify the exact post
```

Keep a good incumbent. More search, a larger archive or a higher diagnostic score does not by itself improve the art.

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

The [paired route-search study](experiments/paired-route-search/results.md) suggests useful route-specific starting points. Its aesthetic audit used the same model that produced the experiment, after proxy-based candidate reduction. It supports working heuristics, not a universally optimal stage schedule.

The [description-length study](experiments/description-length-pressure/results.md) found 3/4 deployable winners with late-only compression and 4/4 with preflight. Early filtering also achieved 4/4 but removed 17/48 candidates before visual review. This small study motivates checking compression before committing to a deployment candidate; it does not require every sketch to run a search experiment.

Mechanical gains do not establish artistic gains. The [family projected-spectral review](research-results/family-projected-spectral-artistic-v1/results.md) found 18 equivalent pairs and only six decisive judgments, with two favoring projected-spectral. Artistic support was not demonstrated; that runtime remains opt-in and default-off.

Research protocols, code and results remain in [experiments](experiments/), [research-results](research-results/) and [research-commitments](research-commitments/). The [research roadmap](references/research-roadmap.md) tracks further hypotheses. These records support evaluation and reproduction; they are not prerequisites for making a sketch.

## Local checks

The skill's JavaScript tools use Node.js built-ins:

```sh
node scripts/test-discovery-state.mjs
node --test scripts/test-png.mjs
```

Python prototype setup and tests are documented in its own README.
