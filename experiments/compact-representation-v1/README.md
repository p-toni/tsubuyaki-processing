# Pulse vessel: compact representation case

**No compact delivery.** A swept surface reached provisional grade B after one revision, but its two attempted posts were **336 and 323 X-weighted characters**. An implicit-field alternative remained grade C and received no compact attempt. The case fails; the production policy stays unchanged.

[Open the gallery](gallery/index.html) to run all four readable candidates, including failures. Clone this directory together with the sibling `autonomous-discovery-pilot-v1` directory, which supplies the pinned p5.js runtime, its license, and the length checker. GitHub's file viewer does not execute the HTML.

## Brief and result

The fresh brief required one opaque, two-chambered soft vessel with a continuous narrow waist. A localized squeeze had to visit both chambers, pass through the waist, and return, with material relaxing behind it. Global scaling, rigid motion, disconnected blobs, and decorative traveling stripes did not qualify.

| Representation | Initial candidate | Revised candidate | Compact outcome |
| --- | --- | --- | --- |
| R1: swept surface | C: bright bow-tie demonstration | **B, lower confidence**: contraction-driven folds, curved axis, oblique surface | 336/280, then 323/280; both fail |
| R2: implicit field | C: faint, flat volume | C: improved lighting, still a demonstration with a background patch | No attempt; no eligible A/B selection |

R1/v2 is the frozen preferred readable incumbent. Its traveling contraction drives both the narrowed body and gathered skin folds. The material response is interesting enough to keep as a study, but rim sampling artifacts detract from finish. It is not A-rated work.

R2/v2 derives lighting from the actual gradient of its joint field. That improves volume without making it artistically worthwhile under this review. A darker rectangular sampling area also remains visible in the actual render. This is an artistic failure, not a failed compact attempt or proof against implicit representations generally.

All causal brief requirements were judged met in both v2 candidates. Adherence alone did not make R2 eligible. Only one of the four readable candidates earned B; three remained C and none earned A. These are provisional judgments from the same agent that authored the programs.

The case required a verified A/B post with no clear artistic loss against the best readable incumbent. It fails because there is no qualifying post. R1's second attempt uses shared trigonometric and fold terms, algebraic factoring, and loop sequencing. It still exceeds the limit by 43 weighted characters. Raw lengths are 332 and 319. Both attempts parse, but neither was executed or verified for readable/compact equivalence. This establishes failure within the frozen budget, not impossibility of compression.

## Evidence order and limits

The [protocol](protocol.md) was published in `95cf305` before construction. Both [initial sources and hashes](initial-commitment.json) were published in `2b79bc9` before rendering. Each representation had at most two readable candidates and two compact attempts. One observation-led revision per representation consumed all four readable slots.

[Reviews](candidate-reviews.json), [requirements](requirements.json), all four source hashes, and the preferred incumbent were frozen in [selection.json](selection.json) before any compact program or character count. R1 then used both allowed attempts. R2's two unused slots were not transferred to R1. No new candidate, material change, or fallback followed selection. [Results](results.json) were frozen before documentation updates.

The agent authored the brief, representations, revisions, and judgments in shared context. The brief was fresh for this case, not independently held out. Visual review used sixteen sampled stills per program, plus selected full-size frames. Neither source commitments nor a separate review step make these judgments independent or blinded. This single case cannot establish a generally superior representation or autonomous discovery reliability.

Both constructions reduce to an axial radius multiplied by the same Gaussian contraction. The contrast primarily concerns the base profile, sampling, projection, and shading. Their shared construction limits what this case can say about representation diversity.

## What was verified

All four readable programs rendered **frames 1–720** without browser errors, using full **p5.js 1.11.3**, Chromium **153.0.8010.12**, and a 400×400 canvas. Sixty-four sampled review images and four contact sheets are archived. The renderer advances every frame even when capturing only samples.

The [gallery checks](browser-checks.json) verify four exact-source live pages: first-frame PNG identity, play/pause/resume/restart, stopping at frame 720, replay, and no horizontal overflow at a 390-pixel viewport. The twelve-second frame clock is not a guarantee of twelve-second native playback on every machine. No seamless loop is claimed.

There are **zero final numerical equivalence checks, zero final readable/compact raster comparisons, and zero verified final clips**. The overlength posts received only length and syntax checks. Readable browser execution does not establish the unused final contract's coordinate, indexed-motion, or compression-preservation requirements. R2's fixed screen samples describe changing material through the field and drawing styles; point-location stability alone would not verify its visual motion.

## Effort and archive

Four unique readable programs produced 2,880 draw frames and 64 sampled review frames. Two compact programs were attempted; two slots went unused. No human creative selection or formula correction was required. Recorded rendering subprocess times sum to 190.942 seconds, with overlap; this excludes authorship, reasoning, visual review, interruptions, and gallery QA. Tokens, monetary cost, and active reasoning time were not measured. No equal-cost claim is supported.

Each `R1` or `R2` directory preserves both sources, sampled frames, contact sheets, and execution records. R1 also preserves both attempted posts. [The attempt ledger](compact-attempts.json) contains hashes, exact counts, syntax outcomes, and timestamps. [The decision log](decisions.md) records the progression and closure.

From this directory, with Node.js available:

```sh
# Expected to report a length failure, with exit status 1.
node ../autonomous-discovery-pilot-v1/check-length.mjs R1/compact-2.txt
repro_dir=$(mktemp -d)
node render.mjs R1/v2.js "$repro_dir/surface-samples" samples
node check-gallery.mjs
```

Browser commands require Playwright and Chromium, optionally supplied through `PLAYWRIGHT_MODULE` and `CHROMIUM_PATH`. The last command writes QA reports and screenshots. Exact raster reproduction depends on the browser/runtime environment. The helpers execute trusted archived JavaScript; they are not an untrusted-code sandbox.

## Decision

Close this case without repairs. Keep R1's readable artistic result and R2's failure visible; do not remove material features or upgrade grades to improve the recorded score. The study does not identify an irreducible character cost for any individual feature.

The next engineering hypothesis is a fresh construction where shape, material, and motion require fewer independent expressions. The current shared contraction was not enough to make the complete construction fit. Try one small integrated construction before commissioning another comparison; a passing length check must still follow artistic selection and exact verification. This is a next step to test, not a validated production policy.
