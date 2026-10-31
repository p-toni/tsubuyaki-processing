// Brief text: compact-preflight-v1/protocol.md (P01 Aperture).
// Thresholds were fixed before the first validation run.
import { erode, nonSimilarity, positions } from '../lib/observables.mjs';
import { foreground, luminance } from '../lib/raster.mjs';

const OPEN_MIN = 0.01;          // an open aperture shows rear material on >= 1% of the canvas
const CLOSED_MAX = 0.02;        // closed: visible rear <= 2% of its own maximum
const CHANGE_MIN = 0.5;         // changing: visible rear varies by >= 50% of its maximum
const OCCLUSION_MAX = 12;       // opaque: front interior differs from front-alone by <= 12 levels
const INTERIOR = 2;             // ignore 2 cells (4 px) at the front boundary: point radius, not depth
const REAR_MOTION_MIN = 4;      // moving rear: visible rear brightness changes >= 4 levels in 0.5 s
const FOLD_MIN = 0.01;          // deforming annulus: non-similarity over 1 s >= 0.01

const L = (r, i) => luminance(r.img[3 * i], r.img[3 * i + 1], r.img[3 * i + 2]);
const cache = new WeakMap();
function visibleRear(ctx) {
  if (cache.has(ctx)) return cache.get(ctx);
  const series = ctx.frames.map(f => {
    const r = ctx.raster(f, { owner: true }), roles = ctx.frame(f).roles;
    if (!roles) throw new Error('requirement needs roles');
    let n = 0;
    for (let i = 0; i < r.own.length; i++) if (r.own[i] >= 0 && roles[r.own[i]] === 'rear') n++;
    return n;
  });
  cache.set(ctx, series);
  return series;
}

export default {
  brief: 'P01', title: 'Aperture',
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
        let err = 0, n = 0;
        for (const f of ctx.frames.filter((_, i) => i % 4 === 0)) {
          const all = ctx.raster(f), front = ctx.roleRaster(f, 'front'), rear = foreground(ctx.roleRaster(f, 'rear'), ctx.o.threshold);
          const interior = erode(ctx.roleMask(f, 'front'), ctx.o.size, ctx.o.size, INTERIOR);
          for (let i = 0; i < rear.length; i++) if (rear[i] && interior[i]) { err += Math.abs(L(all, i) - L(front, i)); n++; }
        }
        const mean = n ? err / n : 0;
        return { pass: mean <= OCCLUSION_MAX, value: { meanDifference: mean, overlapCells: n } };
      },
    },
    {
      id: 'moving_rear_layer', kind: 'roles', label: 'moving_rear_layer',
      check: ctx => {
        const s = visibleRear(ctx), open = OPEN_MIN * ctx.o.size ** 2, lag = 30;
        let sum = 0, frames = 0;
        ctx.frames.forEach((f, i) => {
          if (i % 2 || f + lag > ctx.o.horizon || s[i] < open) return;
          const a = ctx.raster(f, { owner: true }), b = ctx.raster(f + lag, { owner: true });
          const ra = ctx.frame(f).roles, rb = ctx.frame(f + lag).roles;
          let d = 0, n = 0;
          for (let c = 0; c < a.own.length; c++) {
            if (a.own[c] >= 0 && b.own[c] >= 0 && ra[a.own[c]] === 'rear' && rb[b.own[c]] === 'rear') { d += Math.abs(L(a, c) - L(b, c)); n++; }
          }
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
