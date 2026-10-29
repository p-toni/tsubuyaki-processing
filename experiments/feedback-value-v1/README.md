# Does rendered feedback improve compact discovery?

**Both arms delivered four of six briefs.** Adaptive revision produced two extra
worthwhile readable studies, but neither fitted the character limit within its
two allowed compact attempts. The final comparison has **zero adaptive wins,
one batch win, three equivalents, and two both-fail pairs**. The frozen
advancement rule fails. This does not establish broad batch superiority.

Open the [comparison gallery](gallery/index.html) locally for eight verified
clips and twelve live studies, including the unsuccessful runs. GitHub displays
the HTML source; the local gallery runs without a server. [Results](results.json),
[decisions](decisions.md), and the [frozen protocol](protocol.md) preserve the
evidence behind this conclusion.

The research objective is autonomous discovery of worthwhile compact animations.
Additional revision, a bigger archive, or a better readable sketch is useful only
if it improves that capability. This study supports keeping the small existing
loop and revising for specific observed problems. It gives no reason to expand
revision machinery. The next useful question concerns compact representations
for harder structural and temporal requirements.

## Outcomes

Grades are provisional judgments by the same agent that authored the briefs and
both arms: B means an interesting coherent study worth keeping, C a functioning
demonstration. No candidate received A. All selected studies were judged to meet
their brief; batch Weave and Exchange failed the artistic threshold.

| Brief | Adaptive selection | Batch selection | Final outcome |
| --- | --- | --- | --- |
| Separate | v2, B, 242 characters | v2, B, 242 characters | Equivalent; identical source |
| Weave | v4, B with lower confidence; 309 then 290 characters | v3, C; no compact promotion | Both fail |
| Reflect | v2, B, 228 characters | v4, B, 228 characters | Equivalent; identical source |
| Exchange | v4, B with lower confidence; 318 then 303 characters | v2, C; no compact promotion | Both fail |
| Twist | v2, B, 254 characters | v4, B, 238 characters | Batch preferred |
| Divert | v3, B, 262 characters | v4, B, 219 characters | Equivalent; no clear preference |

Lengths are X-weighted counts of the complete post, including the hashtag. The
eight delivered posts also pass the 280 raw-code-point limit. Weave's second
compact attempt additionally contains an exponentiation-precedence syntax error;
it remains preserved in [syntax-checks.json](syntax-checks.json). Both attempts
already exceed the length limit. The failed posts have no verified execution or
compression-equivalence claim, and no third attempt was made. This is a failure
within the allocated budget, not proof that these behaviors cannot be compressed.

The batch Twist has a more continuous opaque cloth and readable fold than the
adaptive arm's striped material. That preference was recorded before compression.
Divert's two material treatments have no clear expressive winner. Exact raster
preservation supports carrying those readable judgments to the delivered posts;
it does not independently validate their artistic quality.

Before compression, the adaptive arm had six B selections and the batch four.
Feedback made Weave's interlacing more legible and repaired Exchange's attachment
and pulse visibility. Those improvements did not yield additional successful
compact discoveries. All eight deliveries are B-grade studies, not A-grade
finished works.

## What was fixed before observation

The protocol, six briefs, 720-frame horizon, rubric, budgets, and advancement
rule were committed in `34188ba`. All 24 batch sources and the six identical
adaptive starts were committed in `9960623` before any study render. These were
local commits at the time and were published with the completed archive.

The adaptive arm could inspect and revise up to four candidates per brief, or
stop early. Adaptive generation and choices closed before the remaining batch
renders. Both arms then had a terminal selection opportunity and at most two
compact attempts per brief, including fallbacks. Choices, grades, requirements,
and any fallback were frozen before character counts. No selected behavior was
tuned after terminal selection.

The advancement rule required at least four adaptive pair wins, at most one
batch win, and no fewer adaptive deliveries. It is a practical decision rule,
not a significance test. Neither successful delivery nor a pair win can be
claimed for a prettier failure.

## Verification and effort

All eight delivered posts passed the frozen checks using full p5.js 1.11.3 at
400 × 400 pixels for frames 1–720 (12 seconds at 60 fps):

- Readable and compact coordinates match within 2.3e-13; drawing styles match
  exactly. Geometry and styles are finite, indexed point counts remain stable,
  and every point center stays in frame.
- Maximum measured per-point frame movement is below 4.403 pixels. Divert uses
  the preregistered horizontal recycling exception: 1,832 resets for adaptive
  and 2,744 for batch, with horizontal movement measured modulo the canvas width
  only at the boundary. These are not ordinary continuous point trajectories.
- All 128 sampled readable/compact PNG pairs are byte-identical in the recorded
  raster runtime (96 unique pairs, with two identical deliveries reused).
- Eight clips have 720 frames, 400 × 400 resolution, and 12-second duration.
  Browser checks passed exact source and first-frame identity, play, pause,
  resume, restart, end-of-horizon stopping, and replay for all twelve live pages.
  The comparison and live pages have no horizontal overflow at 390 pixels.

| Charged effort | Adaptive | Batch |
| --- | ---: | ---: |
| Readable candidates | 17 | 24 |
| Sampled review-frame uses | 272 | 384 |
| Compact attempts | 8 | 4 |
| Successful deliveries | 4 | 4 |

There were 28 unique readable programs and 13 render reuses: 448 unique sampled
frames, covering 656 charged frame uses. Each preview executed all 720 frames.
Six distinct final programs produced six physical clip renders; two identical
posts reused their clips. Six numerical source-pair checks made 47,520,000 point
calls, with two identical checks reused. No fallback was used. The archive
preserves every generated candidate and all failed compact attempts.

Per-process timings and their sums are recorded in [results.json](results.json).
Some subprocesses overlapped; their sums are not elapsed study time. Active
reasoning, review effort, token usage, and monetary cost were not measured.
Seventeen versus 24 candidates therefore does not prove lower total adaptive
cost. The work spanned interrupted sessions and required no human creative
selection or formula correction; this is not an unattended-runtime reliability
test.

## Limits and decision

The same agent authored the briefs, planned both arms, inspected images, selected
candidates, and graded the work in shared context. It remembered planned batch
alternatives and reused some. Source commitments stop later batch edits but do
not remove that contamination. Briefs were fresh for this run, not independently
held out. The design does not cleanly isolate a causal effect of feedback.

Visual review covered sixteen sampled stills for every unique program, with
additional full-size checks recorded in the decisions. Final contact sheets and
desktop/mobile gallery screenshots were inspected. Complete numerical execution
and playback checks are not perceptual assessment of every moment. Artistic
judgments, especially the two lower-confidence B grades, remain model-only.

Keep the small observation-led loop. Do not mandate four candidates, add a search
engine, or infer a universal batch policy from this comparison. On fresh briefs,
test whether compact preflight of a worthwhile incumbent exposes a representation
problem early enough to preserve the important behavior. Occlusion and delayed
attachment are concrete gaps suggested here. Do not repair this consumed
population and count it as new evidence.

## Reproduce and inspect

The protocol and source hashes are in [freeze.json](freeze.json),
[batch-commitment.json](batch-commitment.json),
[adaptive-selection.json](adaptive-selection.json), and
[selection.json](selection.json). [archive-audit.json](archive-audit.json) records
the closing integrity checks. The [previous pilot](../autonomous-discovery-pilot-v1/)
supplies the pinned p5.js runtime, its license, and the length checker; keep both
experiment directories together. The p5.js SHA-256 is
`af51e6211e061b5ae463fbc5c3c1c272e5ca67fa560ed3513fde17325d837506`.

From this directory, with Node.js available:

```sh
node ../autonomous-discovery-pilot-v1/check-length.mjs F05/batch/compact-1.txt
node audit-source.mjs F05/batch/v4.js F05/batch/compact-1.txt /tmp/twist-verification.json
```

Rendering and browser checks additionally require Playwright and Chromium;
clip rendering requires ffmpeg. Optional `PLAYWRIGHT_MODULE`, `CHROMIUM_PATH`,
and `FFMPEG` environment variables select installed dependencies. The recorded
browser was Chromium 153.0.8010.12; pixel bytes may differ in another raster
runtime. The renderer executes every frame even in `samples` mode:

```sh
node render.mjs F05/batch/compact-1.txt /tmp/twist-render samples
node render.mjs F05/batch/compact-1.txt /tmp/twist-clip clip
node check-gallery.mjs
```

The last command refreshes browser diagnostics and screenshots in this archive.
It checks presentation and playback, not the artistic grades. The numerical
auditor executes trusted archived sketches and is not a sandbox for untrusted
JavaScript. See [raster-parity.json](raster-parity.json),
[clip-verification.json](clip-verification.json), and
[browser-checks.json](browser-checks.json) for the recorded checks.
