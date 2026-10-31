// Brief contracts: executable checks of brief requirements over a point stream.
//
// A contract module exports { brief, title, text, observation, requirements }.
// Each requirement has an id, a kind and check(ctx) -> { pass, value, ... }:
//   executable  - needs only points and rasters;
//   roles       - needs per-point roles (a declared probe or a documented shim).
// Requirements a contract cannot execute are listed in coverage.json, not here.
import { STRIDE } from './runtime.mjs';
import { rasterize, foreground } from './raster.mjs';
import { close, positions, range, regions } from './observables.mjs';

export const OBSERVATION = {
  horizon: 720,   // frames 1-720, the October studies' frozen interval
  step: 4,        // sampled every 4th frame for time series
  size: 200,      // raster cells across (2 canvas pixels per cell)
  threshold: 16,  // luminance difference from background that counts as ink
  closeRadius: 2, // morphological closing, in cells, to bridge point sampling gaps
};

export function onlyRole(frame, role) {
  if (!frame.roles) throw new Error('requirement needs roles: declare `role` in the sketch or supply a shim');
  const data = [];
  for (let k = 0; k < frame.n; k++) if (frame.roles[k] === role) for (let j = 0; j < STRIDE; j++) data.push(frame.data[k * STRIDE + j]);
  return { ...frame, data: Float64Array.from(data), n: data.length / STRIDE, roles: null };
}

export function context(sketch, overrides = {}) {
  const o = { ...OBSERVATION, ...overrides };
  const frames = range(1, o.horizon, o.step);
  const memo = new Map();
  const once = (key, fn) => { if (!memo.has(key)) memo.set(key, fn()); return memo.get(key); };
  const ctx = {
    sketch, o, frames,
    frame: f => sketch.frame(f),
    pos: (f, keep = null) => positions(sketch.frame(f), keep),
    raster: (f, opts = {}) => once(`r${f}:${opts.owner ? 1 : 0}`, () => rasterize(sketch.frame(f), { size: o.size, owner: !!opts.owner })),
    weighted: f => once(`w${f}`, () => rasterize(sketch.frame(f), { size: o.size, roleWeights: true })),
    fullRes: (f, role = null) => once(`f${f}:${role}`, () => rasterize(role ? onlyRole(sketch.frame(f), role) : sketch.frame(f), { size: 400 })),
    roleRaster: (f, role) => once(`rr${f}:${role}`, () => rasterize(onlyRole(sketch.frame(f), role), { size: o.size })),
    mask: f => once(`m${f}`, () => close(foreground(ctx.raster(f), o.threshold), o.size, o.size, o.closeRadius)),
    roleMask: (f, role) => once(`rm${f}:${role}`, () => close(foreground(ctx.roleRaster(f, role), o.threshold), o.size, o.size, o.closeRadius)),
    regions: (f, minFrac) => once(`g${f}:${minFrac}`, () => regions(ctx.mask(f), o.size, o.size, { minArea: Math.ceil(minFrac * o.size * o.size) })),
    cell: (x, y) => {
      const s = o.size / 400, cx = Math.floor(x * s), cy = Math.floor(y * s);
      return cx >= 0 && cy >= 0 && cx < o.size && cy < o.size ? cy * o.size + cx : -1;
    },
    // Largest per-point displacement between consecutive frames over the whole horizon.
    continuity: () => once('continuity', () => {
      let worst = 0, at = 0, prev = sketch.frame(1);
      for (let f = 2; f <= o.horizon; f++) {
        const cur = sketch.frame(f), n = Math.min(prev.n, cur.n);
        for (let k = 0; k < n; k++) {
          const d = Math.hypot(cur.data[k * STRIDE] - prev.data[k * STRIDE], cur.data[k * STRIDE + 1] - prev.data[k * STRIDE + 1]);
          if (d > worst) { worst = d; at = f; }
        }
        prev = cur;
      }
      return { worst, at };
    }),
  };
  return ctx;
}

export function runContract(contract, sketch, overrides = {}) {
  const ctx = context(sketch, { ...contract.observation, ...overrides });
  return contract.requirements.map(req => {
    const started = performance.now();
    try {
      const r = req.check(ctx);
      return { id: req.id, kind: req.kind, pass: !!r.pass, ...r, ms: Math.round(performance.now() - started) };
    } catch (e) {
      return { id: req.id, kind: req.kind, pass: false, error: e.message };
    }
  });
}
