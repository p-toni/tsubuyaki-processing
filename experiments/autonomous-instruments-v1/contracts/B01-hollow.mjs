// Brief text: autonomous-discovery-pilot-v1/protocol.md (B01 Hollow).
// Thresholds were fixed before the first validation run.
import { holes, nonSimilarity, regions } from '../lib/observables.mjs';

const CAVITY_MIN = 0.01;    // a legible cavity: enclosed background >= 1% of the canvas...
const CENTRAL = 0.25;       // ...centred within 25% of the form's extent from its centre
const DEFORM_MIN = 0.02;    // deforms internally: non-similarity reaches >= 0.02

export default {
  brief: 'B01', title: 'Hollow',
  text: 'A soft hollow form breathes through changing folds. Its cavity remains legible while the surrounding material deforms internally. A rigidly rotating outline or an ordinary oscillating line does not meet the brief.',
  requirements: [
    {
      id: 'cavity_remains', kind: 'executable',
      check: ctx => {
        const W = ctx.o.size;
        let missing = 0;
        for (const f of ctx.frames.filter((_, i) => i % 2 === 0)) {
          const m = ctx.mask(f), body = regions(m, W, W, { minArea: 20 }).list;
          if (!body.length) { missing++; continue; }
          let x0 = W, y0 = W, x1 = 0, y1 = 0;
          for (const r of body) { x0 = Math.min(x0, r.x0); y0 = Math.min(y0, r.y0); x1 = Math.max(x1, r.x1); y1 = Math.max(y1, r.y1); }
          const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, ex = x1 - x0, ey = y1 - y0;
          const ok = holes(m, W, W, { minArea: Math.ceil(CAVITY_MIN * W * W) }).some(h => Math.abs(h.cx - cx) <= CENTRAL * ex && Math.abs(h.cy - cy) <= CENTRAL * ey);
          if (!ok) missing++;
        }
        return { pass: missing === 0, value: { framesWithoutCavity: missing } };
      },
    },
    {
      id: 'material_deforms_internally', kind: 'executable',
      check: ctx => {
        const ref = ctx.pos(1), m = Math.max(...ctx.frames.map(f => nonSimilarity(ref, ctx.pos(f))));
        return { pass: m >= DEFORM_MIN, value: { maxNonSimilarity: m } };
      },
    },
  ],
};
