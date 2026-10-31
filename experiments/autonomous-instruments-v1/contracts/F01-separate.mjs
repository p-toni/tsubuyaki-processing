// Brief text: feedback-value-v1/protocol.md (F01 Separate).
// Thresholds were fixed before the first validation run.
import { dilate, holes, nonSimilarity, positions, regions } from '../lib/observables.mjs';

const MIN_REGION = 0.005;   // a lobe covers >= 0.5% of the canvas
const GAP_CELLS = 2;        // clearly spaced: still apart after dilating by 2 cells (gap >= ~8 px)
const HOLLOW_MAX = 0.1;     // material, not rings: enclosed holes <= 10% of foreground area (median)
const DEFORM_MIN = 0.02;    // each lobe deforms: non-similarity between separated and joined >= 0.02
const STEP_MAX = 10;        // continuity: no point moves > 10 px between consecutive frames
const MASS_MIN = 0.6;       // not fading: foreground area never drops below 60% of its maximum

function phases(ctx) {
  const W = ctx.o.size, min = Math.ceil(MIN_REGION * W * W);
  return ctx.frames.map(f => {
    const regs = ctx.regions(f, MIN_REGION).list;
    let separated = false;
    if (regs.length === 2) separated = regions(dilate(ctx.mask(f), W, W, GAP_CELLS), W, W, { minArea: min }).list.length === 2;
    const fg = ctx.mask(f).reduce((a, b) => a + b, 0), hole = holes(ctx.mask(f), W, W, { minArea: 4 }).reduce((a, h) => a + h.area, 0);
    return { f, n: regs.length, joined: regs.length === 1, separated, hollow: fg ? hole / fg : 0, fg };
  });
}
const memo = new WeakMap();
const ph = ctx => { if (!memo.has(ctx)) memo.set(ctx, phases(ctx)); return memo.get(ctx); };

function sequence(p) {
  const j1 = p.findIndex(x => x.joined);
  const s = j1 < 0 ? -1 : p.findIndex((x, i) => i > j1 && x.separated);
  const j2 = s < 0 ? -1 : p.findIndex((x, i) => i > s && x.joined);
  return { j1, s, j2 };
}

export default {
  brief: 'F01', title: 'Separate',
  text: 'One material body separates into two clearly spaced lobes and reunites. Material deforms during the transition. Merely translating two rigid circles, fading one out, or replacing one image with another fails.',
  requirements: [
    {
      id: 'separation_and_reunion', kind: 'executable',
      check: ctx => {
        const { j1, s, j2 } = sequence(ph(ctx));
        return { pass: j1 >= 0 && s >= 0 && j2 >= 0, value: { joinedAt: ctx.frames[j1] ?? null, separatedAt: ctx.frames[s] ?? null, rejoinedAt: ctx.frames[j2] ?? null } };
      },
    },
    {
      id: 'material_lobes', kind: 'executable',
      check: ctx => {
        const rel = ph(ctx).filter(x => x.joined || x.separated).map(x => x.hollow).sort((a, b) => a - b);
        const med = rel.length ? rel[Math.floor(rel.length / 2)] : 1;
        return { pass: rel.length > 0 && med <= HOLLOW_MAX, value: { medianHoleFraction: med } };
      },
    },
    {
      id: 'material_deforms', kind: 'executable',
      check: ctx => {
        const p = ph(ctx), { j1, s, j2 } = sequence(p);
        if (s < 0) return { pass: false, value: 'no separated phase' };
        const fs = p[s].f, W = ctx.o.size, lab = ctx.regions(fs, MIN_REGION);
        const frame = ctx.frame(fs), lobe = new Int8Array(frame.n).fill(-1);
        for (let k = 0; k < frame.n; k++) {
          const c = ctx.cell(frame.data[k * 7], frame.data[k * 7 + 1]);
          const id = c >= 0 ? lab.labels[c] : -1, idx = lab.list.findIndex(r => r.id === id);
          lobe[k] = idx;
        }
        const joinedF = p[j2 >= 0 ? j2 : j1].f, vals = [0, 1].map(L => nonSimilarity(positions(frame, k => lobe[k] === L), positions(ctx.frame(joinedF), k => lobe[k] === L)));
        return { pass: vals.every(v => v >= DEFORM_MIN), value: { lobeNonSimilarity: vals } };
      },
    },
    {
      id: 'continuous_motion', kind: 'executable',
      note: 'Rejects replacing one image with another; checks all 720 frames.',
      check: ctx => { const c = ctx.continuity(); return { pass: c.worst <= STEP_MAX, value: c }; },
    },
    {
      id: 'material_conserved', kind: 'executable',
      check: ctx => {
        const fg = ph(ctx).map(x => x.fg), ratio = Math.min(...fg) / Math.max(...fg);
        return { pass: ratio >= MASS_MIN, value: { minToMaxArea: ratio } };
      },
    },
  ],
};
