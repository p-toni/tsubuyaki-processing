# Borrowed spin

A copper whorl brushes a blue one. Watch the small curl inside the blue rim as the copper pulls away. The curl keeps turning, then slows as the gap widens. Both forms are drawn with the same stack of 65 eccentric discs. [Watch the 12-second animation](borrowed-spin.mp4?raw=1) · [Readable source](v2.js) · [Complete executable sketch](sketch.txt)

**Keep, provisional B.** In the first sketch the copper centre parked against the rim. In the selected version it sweeps along the edge while transferring spin. The handoff is legible and the second encounter repeats the copper path. The authoring agent wrote the brief and gave both grades. The brief supplied the desired interaction and left its representation open. [Frozen brief](brief.md) · [Visual selection and matched stills](selection.md)

## What contact changed

The receiver starts still. When the gap closes, its speed approaches the driver's spin rate and it turns in the opposite direction. Once a gap opens, drag reduces the speed it has already acquired. The copper path and its spin are prescribed throughout.

The rims first touched at frame 124 and parted after frame 241. We measured the blue curl's angle from its drawn centre and tip. In the control we set only the contact torque to zero in the exact sketch. The copper's geometry and colour matched on every frame.

| Blue whorl after first separation | Original | Transfer disabled |
| --- | ---: | ---: |
| First second, frames 242–301 | 76.4° counterclockwise | 0° |
| Next second, frames 302–361 | 29.0° counterclockwise | 0° |

The first 123 rendered frames were identical with and without transfer. From frame 124 onward the two renders differed on all 597 frames. Every differing pixel lay within one pixel of the blue disc or inside it. The second contact started at frame 488. [Reproducible coast test](check-coast.mjs) · [Measurements](result.json)

## Compact delivery

The first compact attempt used **371 raw code points and 375 X-weighted characters**, including the hashtag. We kept it with the curved contact path, the light on the ridges, and the decaying spin intact. Two readable sketches and one compact attempt were used.

All 720 PNG pairs from the selected source and the exact sketch were byte-identical in p5.js 1.11.3 and Chromium 153.0.8010.12. Ordinary p5 playback also matched the reference PNG at frames 45, 181, and 301. The published 400 × 400 film is encoded from the compact run at 60 fps. [Frame renderer](../compact-preflight-v1/render.mjs)

Run these commands from the repository root. The second command reports status 1 because the sketch exceeds standard-post size.

```sh
node experiments/borrowed-spin-v1/check-coast.mjs
node scripts/check-length.mjs experiments/borrowed-spin-v1/sketch.txt
```
