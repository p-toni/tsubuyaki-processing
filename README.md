# tsubuyaki-processing

A production-oriented Agent Skill for generating authentic, tweet-sized **#つぶやきProcessing**: dense mathematical p5.js sketches whose organic forms emerge from compact coupled equations.

This repository specializes in the point-based, biomorphic contemporary vocabulary strongly associated with @yuruyurau and the Japanese creative-coding community, while preserving the broader history of the hashtag.

## What the skill does

Given a visual direction such as “breathing seed pod,” “alien flower,” “folded creature,” or “abstract living knot,” an agent should:

1. design a readable mathematical system first;
2. render it as a dense point field or related compact topology;
3. tune silhouette, density and motion;
4. semantically code-golf the sketch;
5. return both readable and tweet-ready p5.js;
6. mechanically verify that the complete post, including `#つぶやきProcessing`, fits the 280-character budget.

## Repository

```text
tsubuyaki-processing/
├── SKILL.md
├── README.md
├── references/
│   ├── research-notes.md
│   ├── code-golf-techniques.md
│   ├── mathematical-patterns.md
│   ├── style-guide.md
│   └── real-examples.md
├── templates/
│   ├── basic-skeleton.js
│   └── advanced-parametrics.js
├── examples/
│   ├── 01-breathing-calyx.md
│   ├── 02-folded-creature.md
│   └── 03-coupled-attractor.md
└── scripts/
    └── check-length.mjs
```

## Why there is a length checker

“280 characters” on X/Twitter is a weighted limit. ASCII source characters usually cost 1, while the Japanese characters in `#つぶやきProcessing` cost more. The script uses the published `twitter-text` v3 weighting ranges for the intended domain of **code + hashtag with no URL/emoji**.

Check a final one-liner:

```sh
printf %s 't=0,draw=_=>{/*...*/}//#つぶやきProcessing' | node scripts/check-length.mjs
```

Or check a file:

```sh
node scripts/check-length.mjs sketch.tweet.js
```

It reports both raw Unicode code points and weighted length and exits non-zero if either exceeds 280.

## Installation

Use the normal skill-directory mechanism for your Agent Skills-compatible host. The essential invariant is that the host can discover:

```text
tsubuyaki-processing/SKILL.md
```

For a project-local installation, copy the entire folder into the agent's project skills directory. Keeping the references/templates beside `SKILL.md` allows progressive disclosure rather than bloating the primary instruction file.

## Example prompt

```text
Create an original #つぶやきProcessing sketch that feels like a translucent seed pod slowly unfolding. Use the tsubuyaki-processing skill. Give me the expanded source, tweet-ready code, verified length, and three mathematically meaningful variants.
```

## Design stance

### Authenticity over generic p5

The skill does not treat “generative art” as a bag of flow fields, Perlin noise, random particles, and palettes. It prioritizes compact latent geometry: high sample counts, coupled trigonometric fields, radial/body coordinates, phase reuse, controlled nonlinearities, and internal temporal deformation.

### Original systems, not artist copying

The research analyzes real works and extracts structural techniques. `references/real-examples.md` intentionally contains only short identifying fragments and annotations, not complete third-party one-liners. New outputs should invent their own sampling topology, equations, ratios, projection, and temporal behavior.

### Readable first, golf second

A strong 250-character sketch is usually the compressed form of a coherent larger idea. Designing directly in opaque one-letter code makes it harder for an LLM to reason about causality, tune motion, or detect errors. The workflow therefore preserves a readable source as the semantic truth.

### Deterministic checks for deterministic constraints

An LLM should not “eyeball” a hard 280-character limit. The repository includes executable validation because this is exactly the kind of brittle mechanical requirement a script handles better than prose instructions.

## Research basis

See `references/research-notes.md` for the detailed source-backed history, community scale, code-golf literature, tool ecosystem, current examples, X/Twitter counting rules, and Agent Skill design rationale.

Primary/reference sources include:

- Hau-kun's origin post: https://haukun.projectroom.jp/archives/328
- official portal: https://tweetprocessing.projectroom.jp/
- official portal link/tool index: https://tweetprocessing.projectroom.jp/%E3%83%AA%E3%83%B3%E3%82%AF%E9%9B%86
- WGG compression article: https://wgg.hatenablog.jp/entry/20200524/1590315560
- Snowman-s Qiita: https://qiita.com/Snowman-s/items/f405526a040e0729a5d7
- Watabo-shi/Kani tips: https://note.com/aq_kani/n/nc25b1f26ba7d
- Gorilla Sun's tips: https://www.gorillasun.de/blog/9-tips-for-tsubuyaki-processing/
- Koma Tebe's compression walkthrough: https://medium.com/@koma.tebe/compressing-the-tiny-code-fceba1b3eb56
- Anthropic Agent Skill guide: https://claude.com/blog/complete-guide-to-building-skills-for-claude
- Anthropic algorithmic-art skill: https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/SKILL.md
- twitter-text v3 configuration: https://github.com/twitter/twitter-text/blob/master/config/v3.json

## Future improvements

- add a headless p5 visual regression harness that renders both expanded and golfed versions and compares frames
- add a browser-based parameter explorer that can export constants back into the readable sketch
- wrap the official `twitter-text` package when network/dependency availability is guaranteed, enabling exact URL/emoji handling too
- build a curated, permissioned dataset of source + preview + structural annotations across several hundred hashtag works
- add benchmark prompts and acceptance tests for trigger precision, originality, syntax validity, frame rate, visual density, and length compliance
- add separate sub-guides for historical Java Processing, Processing.py, WEBGL tiny-code, and shader/GLSL-adjacent lineages
