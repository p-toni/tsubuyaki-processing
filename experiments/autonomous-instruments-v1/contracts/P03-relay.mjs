// Brief text: compact-preflight-v1/protocol.md (P03 Relay).
// Thresholds were fixed before the first validation run (b57306e).
//
// v1.1 POST-HOC REPAIR, after the frozen run (results/contract-validation-v1-frozen.json):
// bending was measured against the reference frame used to find units, at
// which some units were already mid-pulse; that distorted their series. It is
// now measured against each point's rest position (temporal median). No
// threshold changed. The repair was informed by the cases it is re-tested on.
import { bestLag, median, nonSimilarity, positions } from '../lib/observables.mjs';

const MIN_UNIT = 0.002;     // a unit covers >= 0.2% of the canvas
const BASE_SHARE = 0.03;    // a unit's base: its lowest 3% of points at the reference frame
const BASE_MOVE_MAX = 3;    // bases stay fixed: <= 3 px over the horizon
const BEND_MIN = 0.02;      // each unit deforms: peak non-similarity >= 0.02
const LAG_MIN = 2;          // visibly different peak times: >= 2 samples (8 frames) between neighbors
const LAG_MAX = 30;         // search window: 30 samples (2 s)
const CORR_MIN = 0.3;       // neighbors respond to one shared event

function units(ctx) {
  let best = null;
  for (const f of ctx.frames) {
    const regs = ctx.regions(f, MIN_UNIT);
    if (!best || regs.list.length > best.regs.list.length) best = { f, regs };
  }
  const { f, regs } = best, frame = ctx.frame(f), order = [...regs.list].sort((a, b) => a.cx - b.cx);
  const unitOf = new Int16Array(frame.n).fill(-1);
  for (let k = 0; k < frame.n; k++) {
    const c = ctx.cell(frame.data[k * 7], frame.data[k * 7 + 1]);
    if (c >= 0 && regs.labels[c] >= 0) unitOf[k] = order.findIndex(r => r.id === regs.labels[c]);
  }
  const all = ctx.frames.map(g => ctx.frame(g));
  const rest = { ...frame, data: Float64Array.from(frame.data) };
  for (let k = 0; k < frame.n; k++) {
    rest.data[k * 7] = median(all.map(fr => fr.data[k * 7]));
    rest.data[k * 7 + 1] = median(all.map(fr => fr.data[k * 7 + 1]));
  }
  const bend = order.map((_, u) => all.map(fr => nonSimilarity(positions(rest, k => unitOf[k] === u), positions(fr, k => unitOf[k] === u))));
  return { f, order, unitOf, frame, bend };
}
const memo = new WeakMap();
const U = ctx => { if (!memo.has(ctx)) memo.set(ctx, units(ctx)); return memo.get(ctx); };

export default {
  brief: 'P03', title: 'Relay', version: '1.1-post-hoc',
  text: 'At least five rooted soft units receive a localized bending event in sequence across the group. Bases stay fixed, each unit deforms, and neighboring response peaks occur at visibly different times. Uniform global swaying, rigid translation, or unrelated flicker fails.',
  requirements: [
    {
      id: 'at_least_five_units', kind: 'executable', label: 'at_least_five_units',
      check: ctx => { const u = U(ctx); return { pass: u.order.length >= 5, value: { units: u.order.length, atFrame: u.f } }; },
    },
    {
      id: 'fixed_bases', kind: 'executable', label: 'fixed_bases',
      check: ctx => {
        const u = U(ctx); let worst = 0;
        u.order.forEach((_, i) => {
          const ks = [];
          for (let k = 0; k < u.frame.n; k++) if (u.unitOf[k] === i) ks.push(k);
          ks.sort((a, b) => u.frame.data[b * 7 + 1] - u.frame.data[a * 7 + 1]);
          const base = ks.slice(0, Math.max(1, Math.round(BASE_SHARE * ks.length)));
          for (const g of ctx.frames) {
            const fr = ctx.frame(g);
            for (const k of base) worst = Math.max(worst, Math.hypot(fr.data[k * 7] - u.frame.data[k * 7], fr.data[k * 7 + 1] - u.frame.data[k * 7 + 1]));
          }
        });
        return { pass: u.order.length > 0 && worst <= BASE_MOVE_MAX, value: { maxBaseMotion: worst } };
      },
    },
    {
      id: 'each_unit_deforms', kind: 'executable', label: 'local_deformation',
      check: ctx => {
        const peaks = U(ctx).bend.map(s => Math.max(...s));
        return { pass: peaks.length > 0 && peaks.every(p => p >= BEND_MIN), value: { minPeakNonSimilarity: Math.min(...peaks) } };
      },
    },
    {
      id: 'sequential_response', kind: 'executable', label: 'sequential_response',
      check: ctx => {
        const b = U(ctx).bend, lags = [];
        for (let i = 0; i + 1 < b.length; i++) lags.push(bestLag(b[i], b[i + 1], LAG_MAX));
        const signs = new Set(lags.map(l => Math.sign(l.lag)));
        const pass = lags.length >= 4 && !signs.has(0) && signs.size === 1 && lags.every(l => Math.abs(l.lag) >= LAG_MIN && l.correlation >= CORR_MIN);
        return { pass, value: { neighborLagsInFrames: lags.map(l => l.lag * ctx.o.step), correlations: lags.map(l => +l.correlation.toFixed(2)) } };
      },
    },
  ],
};
