# Compact preflight timing

Earlier compact checks delivered **3/4 briefs**, versus **1/4** after readable exploration closed. Aperture recovered without a clear artistic loss, but the delivered Wake was less expressive than the late arm's readable selection. **The frozen advancement gate fails.** Keep the production policy unchanged and investigate compact representations that retain artistic quality.

This is a same-author engineering comparison on four fresh, model-authored briefs. The early arm knew the completed late exploration. These are provisional model judgments, not a clean causal estimate, independent artistic validation, or a general success rate.

[Open the comparison gallery](gallery/index.html), including all four failed deliveries as runnable readable studies. Clone or download this directory together with the sibling `autonomous-discovery-pilot-v1` directory to run the gallery locally; GitHub's file viewer does not execute its HTML. The sibling supplies the pinned p5.js runtime, its license, and the length checker.

## What happened

| Brief | Early selection and second attempt | Late selection and second attempt | Outcome |
| --- | --- | --- | --- |
| P01 Aperture | v3 · **272/280**, delivered | v2 · 371/280, failed | Early wins; no clear artistic loss |
| P02 Thread | v4 · 290/280, failed | v2 · 372/280, failed | Both fail; late readable art preferred |
| P03 Relay | v2 · **280/280**, delivered | v2 · **280/280**, delivered | Equivalent; identical source and post |
| P04 Wake | v4 · **243/280**, delivered | v2 · 408/280, failed | Early wins, with an artistic regression |

Lengths are X-weighted counts of complete posts including the hashtag. Raw Unicode counts are four fewer in every attempt. All first attempts exceeded the limit: Aperture 387, Thread 401, Relay 296, Wake 425. Both arms consumed exactly two compact attempts per brief; all sixteen parse. The overlength attempts were not executed or verified for equivalence. They establish failures within this budget, not that the representations are impossible to compress.

All eight final readable selections met their brief requirements and received provisional **B** grades: coherent interesting studies worth keeping. None received an A. Confidence was lower for the early Thread and Wake and for Relay in both arms. A technical pass does not upgrade a grade.

- **Aperture:** a shared radial sampler and front/rear visibility rule replaced separate layers while retaining a changing, fully closing opening and coupled folds. This is the clean recovery in this study.
- **Thread:** the simpler representation recovered opaque crossings after an inadequate intermediate candidate, but its material was less expressive and the second post remained ten weighted characters over budget.
- **Relay:** algebra and syntax changes fit the existing selected behavior exactly. This success was available to both arms; it is not evidence for a representation change or early timing.
- **Wake:** a shared sampler retained the forcing spot, delayed local deformation, and relaxation. It fit, but lost some of the late selection's material and exciter expression. Meeting the brief did not prevent an artistic loss.

The pair rule yields two early wins, zero late wins, one equivalent pair, and one both-fail pair. Advancement also required no clear artistic regression against the late A/B readable selections, including those that could not be compacted. Wake violates that requirement. Thread's readable regression is recorded too, but it was not delivered. Do not count a shorter post as an artistic improvement.

## Protocol and evidence order

The [protocol](protocol.md) was published in commit `8700b01`, and the [four shared initial sources](initial-commitment.json) in `0b3e85e`, before rendering. The late arm then completed readable exploration and [froze all four v2 selections](late-selection.json), requirements, grades, and source hashes in `da67d56` before either arm wrote or counted a compact program.

The early arm reused the initial trajectories, charging each use to its own budget, then attempted compact delivery before further readable work. Failed preflight could inform a representation change within the remaining allowance. The late arm could only compact its frozen selections after that. Both had caps of four readable candidates and two compact attempts per brief. Grades and final early selections were frozen before their remaining compact counts.

The original Aperture v1 review was too lenient: its opening narrowed but never fully closed. That judgment was corrected before compact work, and v2 met the full closure requirement. The correction remains in the [decision log](decisions.md) and [candidate reviews](candidate-reviews.json).

The order protects late selections from observed compact feedback, but gives the early arm knowledge of the late exploration. One agent authored the briefs, programs, revisions, and grades in shared context. Source commitments prevent retrospective edits; they do not remove that confound. Visual review used sixteen sampled stills per unique readable program, with selected full-size inspections. Full-frame execution and playback checks are not perceptual assessment of every moment or independent taste validation.

## Verification

All four logical deliveries passed the frozen contract over **frames 1–720**, twelve seconds at a 60 fps frame clock, at 400×400 using full **p5.js 1.11.3** and Chromium **153.0.8010.12**. There is no recycling exception and no seamless-loop claim.

- Source and compact coordinates and drawing styles agree on every frame to tolerance `1e-7`; maximum observed error was `2.2737367544323206e-13`.
- All indexed point centers stayed in frame; maximum point motion was `2.504780437427968` pixels per frame, below the frozen limit of ten. Counts and identities remained stable and values finite.
- All **64 logical sampled PNG pairs** were byte-identical in the same raster runtime: 48 unique pairs, with Relay reused across arms.
- [Manual source checks](cause-preservation.json) retained the named relationships: occlusion and aperture closure, delayed rooted response, and a shared forcing cause with a 0.9-second wake delay.
- Four archived clips have 720 frames, 400×400 dimensions, and twelve-second duration. Three were rendered physically; the identical Relay clip was reused.
- The [browser checks](browser-checks.json) verify four video players and eight exact-source live pages: first-frame pixels, play/pause/resume/restart, stopping at frame 720, replay, and no horizontal overflow at a 390-pixel viewport. Live playback can take longer than twelve wall-clock seconds; the frame clock is not a hardware performance guarantee.

The numerical checks made 118,080,000 point calls across three unique readable/compact pairs. These checks establish the documented technical properties, not artistic quality or a generally reliable unattended service.

## Effort and reuse

| Charged work | Early | Late |
| --- | ---: | ---: |
| Readable candidates | 13 | 8 |
| Compact attempts | 8 | 8 |
| Successful compact deliveries | 3 | 1 |

There were 21 logical readable candidates, 13 unique readable renders, and eight reused render records. Review used 208 unique sampled frames, charged as 336 frame uses. Sixteen compact attempts contain eleven unique programs and five explicit reuses. Final rendering produced 2,160 physical frames for four logical 720-frame deliveries. No human creative selection or formula correction was required.

Recorded preview subprocess times sum to 208.106 seconds, final-render subprocess times to 65.897 seconds, and numerical execution times to 180.698 seconds. Some processes overlapped. These sums exclude authorship, reasoning, visual review, interruptions, and gallery QA; they are neither elapsed study time nor evidence of equal total cost. Tokens, monetary cost, and active reasoning time were not measured.

## Archive and reproduction

[Results](results.json) were frozen before documentation updates. [Selection](selection.json), [compact attempts](compact-attempts.json), [archive audit](archive-audit.json), [raster parity](raster-parity.json), and [clip verification](clip-verification.json) preserve the result. Each `Pxx/{early,late}` directory contains every readable source, review frames, and both attempted posts. Successful runs also contain `verification-2.json`, final samples, and `clip.mp4`.

Reuse is explicit in [readable renders](render-reuse.json), [compact programs](compact-reuse.json), [numerical verification](verification-reuse.json), and [final rendering](final-render-reuse.json). Reuse saves physical work without erasing charged attempts.

From this directory, with Node.js available:

```sh
node ../autonomous-discovery-pilot-v1/check-length.mjs P01/early/compact-2.txt
repro_dir=$(mktemp -d)
node audit-source.mjs P01/early/v3.js P01/early/compact-2.txt "$repro_dir/aperture-audit.json"
```

For browser reproduction, provide Playwright and its Chromium, optionally through `PLAYWRIGHT_MODULE` and `CHROMIUM_PATH`. Rendering clips also requires `ffmpeg` on PATH or `FFMPEG` set to its executable. The renderer uses the archived runtime and advances every frame even in sample mode:

```sh
node render.mjs P01/early/compact-2.txt "$repro_dir/aperture-samples" samples
node render.mjs P01/early/compact-2.txt "$repro_dir/aperture-clip" clip
node check-gallery.mjs
```

The last command writes gallery QA reports and screenshots. Exact raster reproduction requires the same browser/runtime environment. These helpers execute trusted archived JavaScript; they are not an untrusted-code sandbox.

## Decision

Close this population without further candidate or compact repairs. Keep the production skill unchanged. The next useful work is a small fresh test of whether a compact representation can preserve both difficult behavior and its artistic expression. Another timing sweep, a larger candidate quota, or a new runtime would not resolve the observed loss.
