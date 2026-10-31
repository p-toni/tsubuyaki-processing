// Brief text: autonomous-discovery-pilot-v1/protocol.md (B03 Gather).
// Thresholds were fixed before the first validation run.
import { nonSimilarity, positions, quantile, spread, median } from '../lib/observables.mjs';

const GATHER = 0.7;         // gathers: spread falls to <= 70% of the spread before and after
const JERK_MAX = 0.5;       // coherent paths: median per-frame second difference <= 0.5 px
const STAGGER_MIN = 8;      // staggered: interquartile range of per-point gathering times >= 8 frames
const WINDOW = 120;         // frames either side of the tightest gathering searched per point
const SHAPE_MIN = 0.05;     // not whole-object rotation: non-similarity reaches >= 0.05

const memo = new WeakMap();
function spreads(ctx) {
  if (!memo.has(ctx)) memo.set(ctx, ctx.frames.map(f => spread(ctx.pos(f))));
  return memo.get(ctx);
}

export default {
  brief: 'B03', title: 'Gather',
  text: 'An organized swarm gathers into a readable structure and releases again. Individual paths remain coherent and the timing is staggered. Whole-object rotation and random jitter do not meet the brief.',
  requirements: [
    {
      id: 'gathers_and_releases', kind: 'executable',
      check: ctx => {
        const s = spreads(ctx);
        for (let i = 1; i + 1 < s.length; i++) {
          const before = Math.max(...s.slice(0, i)), after = Math.max(...s.slice(i + 1));
          if (s[i] <= GATHER * Math.min(before, after)) return { pass: true, value: { tightestFrame: ctx.frames[i], ratio: s[i] / Math.min(before, after) } };
        }
        return { pass: false, value: { minToMaxSpread: Math.min(...s) / Math.max(...s) } };
      },
    },
    {
      id: 'coherent_paths', kind: 'executable',
      check: ctx => {
        const jerks = [];
        for (const f of ctx.frames.filter((_, i) => i % 6 === 0 && _ + 2 <= ctx.o.horizon)) {
          const a = ctx.frame(f), b = ctx.frame(f + 1), c = ctx.frame(f + 2);
          for (let k = 0; k < a.n; k += 7) jerks.push(Math.hypot(c.data[k * 7] - 2 * b.data[k * 7] + a.data[k * 7], c.data[k * 7 + 1] - 2 * b.data[k * 7 + 1] + a.data[k * 7 + 1]));
        }
        const m = median(jerks);
        return { pass: m <= JERK_MAX, value: { medianSecondDifference: m } };
      },
    },
    {
      id: 'staggered_timing', kind: 'executable',
      check: ctx => {
        const s = spreads(ctx), i0 = s.indexOf(Math.min(...s)), f0 = ctx.frames[i0];
        const win = ctx.frames.filter(f => Math.abs(f - f0) <= WINDOW), frames = win.map(f => ctx.frame(f)), n = frames[0].n, times = [];
        const cs = frames.map(fr => { let x = 0, y = 0; for (let k = 0; k < n; k++) { x += fr.data[k * 7]; y += fr.data[k * 7 + 1]; } return [x / n, y / n]; });
        for (let k = 0; k < n; k += 3) {
          let best = Infinity, at = 0;
          frames.forEach((fr, j) => { const r = Math.hypot(fr.data[k * 7] - cs[j][0], fr.data[k * 7 + 1] - cs[j][1]); if (r < best) { best = r; at = win[j]; } });
          times.push(at);
        }
        const iqr = quantile(times, 0.75) - quantile(times, 0.25);
        return { pass: iqr >= STAGGER_MIN, value: { gatheringTimeIQR: iqr } };
      },
    },
    {
      id: 'not_whole_object_rotation', kind: 'executable',
      check: ctx => {
        const ref = ctx.pos(1), m = Math.max(...ctx.frames.map(f => nonSimilarity(ref, ctx.pos(f))));
        return { pass: m >= SHAPE_MIN, value: { maxNonSimilarity: m } };
      },
    },
  ],
};
