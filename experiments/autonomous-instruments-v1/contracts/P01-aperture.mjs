// Brief text: compact-preflight-v1/protocol.md (P01 Aperture).
// Thresholds were fixed before the first validation run (b57306e).
//
// v1.1 POST-HOC REPAIR, after the frozen run (results/contract-validation-v1-frozen.json):
// - visible rear used an owner buffer that ignored points covering < 0.5 of a
//   cell, so 1-px points (Aperture v3) were never seen. It now uses role-weighted
//   compositing; INK_MIN is new.
// - occlusion closed and eroded role masks, which bridged small apertures and
//   counted adjacent rear and front points as overlap. It now compares
//   per-pixel overlap at full resolution; VACUOUS and LEAK_MAX are new.
// These repairs were informed by the labeled cases they are re-tested on.
import { nonSimilarity, positions } from '../lib/observables.mjs';
import { foreground, luminance } from '../lib/raster.mjs';

const OPEN_MIN = 0.01;          // an open aperture shows rear material on >= 1% of the canvas
const CLOSED_MAX = 0.02;        // closed: visible rear <= 2% of its own maximum
const CHANGE_MIN = 0.5;         // changing: visible rear varies by >= 50% of its maximum
const OCCLUSION_MAX = 12;       // a pixel leaks when composite and front-alone differ by > 12 levels
const REAR_MOTION_MIN = 4;      // moving rear: visible rear brightness changes >= 4 levels in 0.5 s
const FOLD_MIN = 0.01;          // deforming annulus: non-similarity over 1 s >= 0.01
const INK_MIN = 0.1;            // v1.1: a cell shows a role when layers supply >= 10% of its colour
const VACUOUS = 0.005;          // v1.1: overlap below 0.5% of front pixels means nothing to hide
const LEAK_MAX = 0.1;           // v1.1: <= 10% of overlapping pixels may show the rear

const L = (r, i) => luminance(r.img[3 * i], r.img[3 * i + 1], r.img[3 * i + 2]);
const rearShows = (w, i) => {
  const rear = w.roles.rear?.[i] ?? 0, front = w.roles.front?.[i] ?? 0;
  return rear + front >= INK_MIN && rear > front;
};
const cache = new WeakMap();
function visibleRear(ctx) {
  if (cache.has(ctx)) return cache.get(ctx);
  const series = ctx.frames.map(f => {
    const w = ctx.weighted(f);
    if (!w.roles) throw new Error('requirement needs roles');
    let n = 0;
    for (let i = 0; i < w.W * w.H; i++) if (rearShows(w, i)) n++;
    return n;
  });
  cache.set(ctx, series);
  return series;
}

export default {
  brief: 'P01', title: 'Aperture', version: '1.1-post-hoc',
  text: 'An opaque folded annular membrane opens and closes an irregular central aperture, revealing a moving layer behind it. The foreground must hide the rear layer where they overlap. Local folds must deform; a rigid spinning ring, transparent overlay, or hole that never changes fails.',
  requirements: [
    {
      id: 'aperture_closure', kind: 'roles', label: 'aperture_closure',
      check: ctx => {
        const s = visibleRear(ctx), max = Math.max(...s), min = Math.min(...s), cells = ctx.o.size ** 2;
        return { pass: max >= OPEN_MIN * cells && min <= CLOSED_MAX * max, value: { maxOpenFraction: max / cells, closedRatio: max ? min / max : null } };
      },
    },
    {
      id: 'changing_aperture', kind: 'roles', label: 'changing_irregular_aperture',
      note: 'Checks that the aperture changes. Irregularity of its outline is judgment-only in v1.',
      check: ctx => {
        const s = visibleRear(ctx), max = Math.max(...s), min = Math.min(...s);
        return { pass: max >= OPEN_MIN * ctx.o.size ** 2 && (max - min) / max >= CHANGE_MIN, value: { relativeChange: max ? (max - min) / max : 0 } };
      },
    },
    {
      id: 'opaque_occlusion', kind: 'roles', label: 'opaque_occlusion',
      check: ctx => {
        let overlap = 0, leaks = 0, front = 0;
        for (const f of ctx.frames.filter((_, i) => i % 4 === 0)) {
          const all = ctx.fullRes(f), fr = ctx.fullRes(f, 'front'), fm = foreground(fr, ctx.o.threshold), rm = foreground(ctx.fullRes(f, 'rear'), ctx.o.threshold);
          for (let i = 0; i < fm.length; i++) {
            if (!fm[i]) continue;
            front++;
            if (!rm[i]) continue;
            overlap++;
            if (Math.abs(L(all, i) - L(fr, i)) > OCCLUSION_MAX) leaks++;
          }
        }
        const vacuous = overlap < VACUOUS * front, leak = overlap ? leaks / overlap : 0;
        return { pass: vacuous || leak <= LEAK_MAX, value: { overlapShareOfFront: front ? overlap / front : 0, leakingShare: leak, vacuous } };
      },
    },
    {
      id: 'moving_rear_layer', kind: 'roles', label: 'moving_rear_layer',
      check: ctx => {
        const s = visibleRear(ctx), open = OPEN_MIN * ctx.o.size ** 2, lag = 30;
        let sum = 0, frames = 0;
        ctx.frames.forEach((f, i) => {
          if (i % 2 || f + lag > ctx.o.horizon || s[i] < open) return;
          const a = ctx.weighted(f), b = ctx.weighted(f + lag);
          let d = 0, n = 0;
          for (let c = 0; c < a.W * a.H; c++) if (rearShows(a, c) && rearShows(b, c)) { d += Math.abs(L(a, c) - L(b, c)); n++; }
          if (n) { sum += d / n; frames++; }
        });
        const mean = frames ? sum / frames : 0;
        return { pass: mean >= REAR_MOTION_MIN, value: { meanRearChange: mean, framesOpen: frames } };
      },
    },
    {
      id: 'deforming_folded_annulus', kind: 'roles', label: 'deforming_folded_annulus',
      check: ctx => {
        const vals = [];
        ctx.frames.forEach((f, i) => {
          if (i % 4 || f + 60 > ctx.o.horizon) return;
          const a = ctx.frame(f), b = ctx.frame(f + 60);
          const keep = k => a.roles[k] === 'front' && b.roles[k] === 'front';
          vals.push(nonSimilarity(positions(a, keep), positions(b, keep)));
        });
        const mean = vals.reduce((x, y) => x + y, 0) / vals.length;
        return { pass: mean >= FOLD_MIN, value: { meanNonSimilarity: mean } };
      },
    },
  ],
};
