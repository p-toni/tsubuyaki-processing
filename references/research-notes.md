# Research Notes: #つぶやきProcessing

This document records the evidence used to design the skill. It is deliberately separate from `SKILL.md` so an agent can load historical context only when useful.

## 1. Origin and definition

#つぶやきProcessing was initiated by **Hau-kun (@Hau_kun)** in 2019. Hau-kun's retrospective says the idea emerged in May and embeds the May 27, 2019 announcement creating the hashtag. On June 5, 2019, he defined the challenge as using Processing to see how much art could be expressed by a program that fits inside one tweet.

Sources:

- Hau-kun, “#つぶやきProcessing をはじめました” (2019-07-14): https://haukun.projectroom.jp/archives/328
- Official portal: https://tweetprocessing.projectroom.jp/

The portal makes the format broader than Java Processing: Processing, p5.js, Processing.py and related Processing-family approaches are accepted. A post should contain the code, `#つぶやきProcessing`, and the rendered image/video.

## 2. Early evolution

Hau-kun's 2019 monthly archives show rapid exploration rather than a fixed look: grids, noise, 3D forms, trails, tunnels, and animation. The portal archive notes that participation rose sharply in August 2019. This matters: the modern dense organic point style is an influential later vocabulary, not the only historically valid form.

Sources:

- Hau-kun tag archive: https://haukun.projectroom.jp/archives/tag/%E3%81%A4%E3%81%B6%E3%82%84%E3%81%8Dprocessing
- October 2019 roundup: https://haukun.projectroom.jp/archives/362

For this skill, however, the requested target is intentionally narrower: the mature mathematically dense, organic p5.js mode strongly associated with @yuruyurau and adjacent contemporary work.

## 3. Community scale

A 2022 Processing presentation by Koji Saito reports:

- more than **350 participants** and **7,600 works** as of 2022-05-31
- more than **8,100 works** as of 2022-08-15

Source:

- Koji Saito, Processing presentation PDF: https://ll.jus.or.jp/2022/publish_LearnLanguages2022_KojiSaito.pdf

As a current but imperfect proxy, the public mirror of @TweetProcessing displayed roughly **18K tweets** and **1K followers** when checked in August 2026. Treat mirror counts as indicative, not canonical platform statistics.

- X account: https://x.com/TweetProcessing
- Portal link explaining the bot: https://tweetprocessing.projectroom.jp/%E3%83%AA%E3%83%B3%E3%82%AF%E9%9B%86

## 4. Why the mature style feels distinctive

A study set of more than twenty published works was inspected, with heavy emphasis on @yuruyurau. The most consistent contemporary pattern is not “particles following noise”; it is **mass sampling of a compact parametric or iterated equation**.

Recurring observations:

- one helper arrow function often maps a sample parameter to `point(x,y)`
- helper default parameters double as cheap local bindings
- `mag(k,e)` creates an implicit radius or body coordinate
- the same latent variables (`k`, `e`, `d`, `q`, `c`) are reused across shape and motion
- nested `sin`/`cos`, powers, reciprocal terms, modulo/parity and phase offsets create folds and appendages
- a small time variable `t` is incremented slowly, while local expressions multiply/divide it at different rates
- many recent examples use 10k–40k points on a 400×400 canvas
- near-black backgrounds and translucent pale strokes let density encode surface structure

This is why the output often reads as biological—frills, tentacles, shells, flowers, masks—even when no biological object is explicitly modeled.

Representative sources:

- @yuruyurau, widely circulated 2025 work: https://x.com/yuruyurau/status/1933629116575855091
- @TweetProcessing feed/mirror for multiple current 2026 works: https://x.com/TweetProcessing
- Youtoy's expansion/explanation of a 2022 @yuruyurau sketch: https://qiita.com/youtoy/items/263f407021c4b3003365

## 5. Empirical defaults from the sampled works

These are **observed tendencies**, not rules.

| Dimension | Common contemporary values | Interpretation |
|---|---|---|
| Canvas | 400×400 | one `w` value can serve width, height, center/color tricks |
| Samples/frame | `1e4`, `2e4`, `3e4`, `4e4` | enough density to reveal a continuous manifold |
| Background | grayscale around 6–12 | nearly black without spending palette logic |
| Stroke | pale/white alpha around 35–110 | overlap becomes a density map |
| Primitive | `point()` | maximum geometric information per character |
| Time step | `PI/240` … `PI/20` | slow global evolution; faster local motion comes from phase multipliers |
| Domain | one loop or flattened 2D loop | avoids nested-loop syntax overhead |

Early Processing/Java works often used 720×720; other community p5.js works use 500, 600, 720, 800, 900, etc. Therefore 400 is a strong modern default, not a regulation.

## 6. Code-golf lineage

The community has documented a rich set of shortening methods.

### WGG (2020)

WGG separates automatic minification from semantic rewriting. Their article covers whitespace removal, one-character renaming, scientific notation, omitted leading zeroes, arrow functions, function aliases, replacing `frameCount/width/height` with short variables, folding setup into draw, shorter primitives, translations, compressed loops, `clear()`, and `TAU`.

- https://wgg.hatenablog.jp/entry/20200524/1590315560

### Snowman-s (2020)

The Qiita article focuses on Processing/Java: combining variable declarations, using a short custom frame counter, representing white as `-1`, assignment expressions, and removing whitespace.

- https://qiita.com/Snowman-s/items/f405526a040e0729a5d7

### Watabo-shi / Kani (2021)

The note article collects p5.js-specific golf: implicit globals, arrow functions, compact frame counters, setup removal, aliases, countdown loops, flattened loops, and other short idioms.

- https://note.com/aq_kani/n/nc25b1f26ba7d

### Gorilla Sun (2022/2023)

“9 Tips for Tsubuyaki Processing” explains JavaScript mechanics that make the idioms work: assignment expressions, setup omission via a first-frame guard, aliases, arrow functions, ternaries, countdown loops, moving work into `for` clauses, boolean arithmetic, and destructuring.

- https://www.gorillasun.de/blog/9-tips-for-tsubuyaki-processing/

### Koma Tebe (2022)

The two-part walkthrough is especially useful because it starts with a readable 3D sketch and compresses it step by step. It illustrates `f++||createCanvas(...)`, replacing `frameCount`, reusing `W=400`, scientific notation, omitting visually irrelevant/default arguments, expression side effects, array iteration for repeated calls, and even fragile renderer-specific tricks.

- Part 1: https://medium.com/@koma.tebe/tiny-code-dbf26d84fe38
- Part 2: https://medium.com/@koma.tebe/compressing-the-tiny-code-fceba1b3eb56

These sources motivate a key skill rule: **generic minifiers are only phase one**. The largest savings come from changing representation and exploiting the semantics of the specific sketch.

## 7. Tweet-length reality

The familiar “280 characters” is a **weighted** X/Twitter limit, not a simple Unicode code-point count. Twitter/X's open-source `twitter-text` v3 configuration has `maxWeightedTweetLength: 280`; its default weight is 2, with selected Unicode ranges (including ASCII) weighted 1. CJK/Hiragana therefore consume more budget than ASCII source code.

Sources:

- twitter-text configuration explanation: https://github.com/twitter/twitter-text/blob/master/config/README.md
- v3 configuration: https://github.com/twitter/twitter-text/blob/master/config/v3.json

Because `#つぶやきProcessing` contains Japanese characters, a raw `.length <= 280` check is not sufficient. This repository adds `scripts/check-length.mjs` to enforce both raw code-point and weighted length for the intended no-URL code-post domain.

## 8. Existing tools and archives

The official portal lists:

- **Skepara** — extracts numeric parameters from p5.js and produces sliders.
- **つぶやきProcessing Editor** by Naoto Hieda — historical p5.js editor with minification and GIF export. Koma Tebe noted in 2022 that it no longer existed; its old Glitch URL is no longer a dependable workflow.
- **Tweet Processing Player** by nariakiiwatani — loads/runs posted sketches.
- **@TweetProcessing bot** — redistributes posts containing the hashtag.
- **PCJ ZINE vol.1** — a free Processing Community Japan zine devoted to #つぶやきProcessing.

Portal links: https://tweetprocessing.projectroom.jp/%E3%83%AA%E3%83%B3%E3%82%AF%E9%9B%86

A newer tool, **p5.js packer v0.1.0**, was published in June 2025 specifically for minifying p5.js for Tsubuyaki Processing:

- announcement: https://www.dbc-works.org/feedback/entry/tags/Processing/
- app: https://dbc-works.github.io/p5js-packer/

## 9. Agent Skill design research

Anthropic's 2026 skill-building guide describes Skills as folders centered on a required `SKILL.md`, with optional supporting scripts/references/assets. The design principle most relevant here is **progressive disclosure**: keep routing and high-priority workflow in `SKILL.md`, and load deep references only when needed.

- Anthropic guide: https://claude.com/blog/complete-guide-to-building-skills-for-claude

Anthropic's official `algorithmic-art` skill adds two principles worth retaining:

1. let a computational idea determine the algorithm rather than choosing from a menu of superficial patterns;
2. create original art instead of copying a named artist's exact work.

- official skill: https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/SKILL.md

Community mirrors/catalogues generally preserve the same folder/`SKILL.md` convention and expose the skill to several agent hosts. The lesson is portability: avoid host-specific prose where the workflow itself can be tool-agnostic.

## 10. Design consequences for this repository

The research leads to five concrete decisions:

1. **Formula invention and code golf are separate stages.** An LLM that tries to invent directly in golf notation tends to produce generic or broken work.
2. **The skill teaches latent geometry, not recipes.** `k/e/d/q/c` are roles, not fixed formulas.
3. **The 280 limit is mechanically testable.** A deterministic checker is more reliable than model counting.
4. **Real examples are analyzed, not copied.** The reference file extracts structural patterns and links to originals; it deliberately avoids reproducing full third-party sketches.
5. **The target is deliberately narrower than historical #つぶやきProcessing.** It specializes in the dense organic mathematical lineage requested by the user while retaining historical context.
