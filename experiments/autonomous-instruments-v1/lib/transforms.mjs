// Point-stream transforms. Each returns transform(f, base) -> frame object for
// runtime.transformed(). Randomness is a deterministic integer hash.
//
// DEGRADATIONS make a known-worse twin of a sketch at graded strength. They are
// the fixed points of the judge-panel validation: the better side is known by
// construction.
//
// COUNTERFEITS keep a sketch's look but remove its cause, mimicking failure
// modes that briefs list explicitly (rigid rotation, uniform sway, global
// scaling, flashing, a decorative stripe, image replacement, transparency).
// Contracts must reject them.
import { STRIDE } from './runtime.mjs';
import { luminance } from './raster.mjs';

export function hash01(a, b = 0, c = 0) {
  let h = (Math.imul(a | 0, 374761393) + Math.imul(b | 0, 668265263) + Math.imul(c | 0, 1274126177)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}

const copy = fr => ({ ...fr, data: Float64Array.from(fr.data), roles: fr.roles ? fr.roles.slice() : null });

function mapPoints(fr, fn) {
  const out = copy(fr);
  for (let p = 0, k = 0; p < out.data.length; p += STRIDE, k++) fn(out.data, p, k);
  return out;
}

function filterPoints(fr, keep) {
  const data = [], roles = fr.roles ? [] : null;
  for (let p = 0, k = 0; p < fr.data.length; p += STRIDE, k++) {
    if (!keep(k)) continue;
    for (let j = 0; j < STRIDE; j++) data.push(fr.data[p + j]);
    if (roles) roles.push(fr.roles[k]);
  }
  return { ...fr, n: data.length / STRIDE, data: Float64Array.from(data), roles };
}

function frameCentroid(fr) {
  let x = 0, y = 0;
  for (let p = 0; p < fr.data.length; p += STRIDE) { x += fr.data[p]; y += fr.data[p + 1]; }
  const n = fr.data.length / STRIDE;
  return [x / n, y / n];
}

// ---- degradations (judge-panel fixed points) ----------------------------

export const DEGRADATIONS = {
  density: {
    describe: s => `drop ${Math.round(100 * s)}% of points (stable identities)`,
    levels: [0.5, 0.75, 0.9],
    make: (s, salt = 1) => (f, base) => filterPoints(base.frame(f), k => hash01(k, 0, salt) >= s),
  },
  jitter: {
    describe: s => `per-frame positional noise of ±${s}px`,
    levels: [1.5, 4, 10],
    make: (s, salt = 2) => (f, base) => mapPoints(base.frame(f), (d, p, k) => {
      d[p] += s * (2 * hash01(k, f, salt) - 1); d[p + 1] += s * (2 * hash01(k, f, salt + 1) - 1);
    }),
  },
  freeze: {
    describe: s => `remove ${Math.round(100 * s)}% of the motion (time compressed toward frame 1)`,
    levels: [0.75, 0.9, 1],
    make: s => (f, base) => ({ ...base.frame(1 + Math.round((f - 1) * (1 - s))), frame: f }),
  },
  flatten: {
    describe: s => `flatten ${Math.round(100 * s)}% of shading and alpha variation`,
    levels: [0.5, 0.8, 1],
    make: s => (f, base) => {
      const fr = base.frame(f);
      let n = 0, L = 0, A = 0;
      for (let p = 0; p < fr.data.length; p += STRIDE) { L += luminance(fr.data[p + 3], fr.data[p + 4], fr.data[p + 5]); A += fr.data[p + 6]; n++; }
      L /= n; A /= n;
      return mapPoints(fr, (d, p) => {
        for (let c = 3; c <= 5; c++) d[p + c] = L + (d[p + c] - L) * (1 - s);
        d[p + 6] = A + (d[p + 6] - A) * (1 - s);
      });
    },
  },
  offset: {
    describe: s => `shift the composition ${s}px toward a corner`,
    levels: [40, 90, 150],
    make: (s, salt = 3) => {
      const angle = Math.PI / 4 + Math.floor(4 * hash01(salt)) * Math.PI / 2;
      const dx = s * Math.cos(angle), dy = s * Math.sin(angle);
      return (f, base) => mapPoints(base.frame(f), (d, p) => { d[p] += dx; d[p + 1] += dy; });
    },
  },
  flicker: {
    describe: s => `per-frame brightness flicker up to ${Math.round(100 * s)}%`,
    levels: [0.4, 0.7, 0.95],
    make: (s, salt = 4) => (f, base) => {
      const gain = 1 - s * hash01(f, 0, salt);
      return mapPoints(base.frame(f), (d, p) => { d[p + 6] *= gain; });
    },
  },
};

// ---- counterfeits (contract adversaries) --------------------------------

const t = f => (f - 1) / 60;
const around = (fr, fn) => {
  const [cx, cy] = frameCentroid(fr);
  return mapPoints(fr, (d, p, k) => fn(d, p, k, cx, cy));
};

export const COUNTERFEITS = {
  freeze: {
    mimics: 'a form that never changes',
    make: (ref = 1) => (f, base) => ({ ...base.frame(ref), frame: f }),
  },
  rotate: {
    mimics: 'rigid rotation of an unchanging form',
    make: (ref = 1, omega = 0.6) => (f, base) => around(base.frame(ref), (d, p, k, cx, cy) => {
      const a = omega * t(f), x = d[p] - cx, y = d[p + 1] - cy;
      d[p] = cx + x * Math.cos(a) - y * Math.sin(a); d[p + 1] = cy + x * Math.sin(a) + y * Math.cos(a);
    }),
  },
  sway: {
    mimics: 'uniform global sway or translation',
    make: (ref = 1, amplitude = 30, axis = 'x', period = 4) => (f, base) => mapPoints(base.frame(ref), (d, p) => {
      d[p + (axis === 'x' ? 0 : 1)] += amplitude * Math.sin(2 * Math.PI * t(f) / period);
    }),
  },
  scale: {
    mimics: 'global scaling instead of local deformation',
    make: (ref = 1, amplitude = 0.25, period = 4) => (f, base) => around(base.frame(ref), (d, p, k, cx, cy) => {
      const s = 1 + amplitude * Math.sin(2 * Math.PI * t(f) / period);
      d[p] = cx + (d[p] - cx) * s; d[p + 1] = cy + (d[p + 1] - cy) * s;
    }),
  },
  flash: {
    mimics: 'unrelated flashing of an unchanging form',
    make: (ref = 1, period = 0.5) => (f, base) => mapPoints(base.frame(ref), (d, p) => {
      d[p + 6] *= 0.55 + 0.45 * Math.sin(2 * Math.PI * t(f) / period);
    }),
  },
  stripe: {
    mimics: 'a decorative traveling stripe on an unchanging form',
    make: (ref = 1, width = 24, period = 6) => (f, base) => {
      const center = 200 + 180 * Math.sin(2 * Math.PI * t(f) / period);
      return mapPoints(base.frame(ref), (d, p) => {
        if (Math.abs(d[p] - center) < width) for (let c = 3; c <= 5; c++) d[p + c] = Math.min(255, d[p + c] + 110);
      });
    },
  },
  cut: {
    mimics: 'replacing one image with another',
    make: (horizon = 720) => (f, base) => ({ ...base.frame(f < horizon / 2 ? 1 : horizon), frame: f }),
  },
  collapse: {
    mimics: 'an ordinary oscillating line in place of a form',
    make: (amplitude = 20, period = 4) => (f, base) => around(base.frame(f), (d, p, k, cx, cy) => {
      d[p + 1] = cy + 0.04 * (d[p + 1] - cy) + amplitude * Math.sin(2 * Math.PI * (t(f) / period + (d[p] - cx) / 200));
    }),
  },
  noise: {
    mimics: 'random jitter replacing coherent paths',
    make: (amplitude = 12, salt = 9) => (f, base) => mapPoints(base.frame(f), (d, p, k) => {
      d[p] += amplitude * (2 * hash01(k, f, salt) - 1); d[p + 1] += amplitude * (2 * hash01(k, f, salt + 1) - 1);
    }),
  },
  rigidHalves: {
    mimics: 'two rigid halves translated apart and back together',
    make: (ref = 1, gap = 60, period = 6) => (f, base) => {
      const fr = base.frame(ref), [cx] = frameCentroid(fr), open = gap * Math.max(0, Math.sin(2 * Math.PI * t(f) / period));
      return mapPoints(fr, (d, p) => { d[p] += d[p] < cx ? -open / 2 : open / 2; });
    },
  },
  fadeHalf: {
    mimics: 'one half fading out instead of separating',
    make: (ref = 1, period = 6) => (f, base) => {
      const fr = base.frame(ref), [cx] = frameCentroid(fr), keep = 0.5 + 0.5 * Math.cos(2 * Math.PI * t(f) / period);
      return mapPoints(fr, (d, p) => { if (d[p] >= cx) d[p + 6] *= keep; });
    },
  },
  // Requires roles: draws the rear role after everything else (no depth order).
  rearOnTop: {
    mimics: 'transparent overlap without depth order',
    make: () => (f, base) => {
      const fr = base.frame(f);
      if (!fr.roles) throw new Error('rearOnTop needs roles');
      const order = [...fr.roles.keys()].sort((a, b) => (fr.roles[a] === 'rear') - (fr.roles[b] === 'rear') || a - b);
      const data = new Float64Array(fr.data.length);
      order.forEach((k, i) => data.set(fr.data.subarray(k * STRIDE, (k + 1) * STRIDE), i * STRIDE));
      return { ...fr, data, roles: order.map(k => fr.roles[k]) };
    },
  },
  // Requires roles: makes the front role translucent.
  translucentFront: {
    mimics: 'a transparent overlay instead of an opaque foreground',
    make: (alpha = 0.3) => (f, base) => {
      const fr = base.frame(f);
      if (!fr.roles) throw new Error('translucentFront needs roles');
      return mapPoints(fr, (d, p, k) => { if (fr.roles[k] === 'front') d[p + 6] *= alpha; });
    },
  },
};

// Counterfeits by name, as protocols and brief banks refer to them. `ref` is the
// reference frame a counterfeit freezes or moves (default frame 1).
export function counterfeit(kind, ref = 1) {
  const makers = {
    rotate: () => COUNTERFEITS.rotate.make(ref),
    freeze: () => COUNTERFEITS.freeze.make(ref),
    sway: () => COUNTERFEITS.sway.make(ref, 30, 'x'),
    swayVertical: () => COUNTERFEITS.sway.make(ref, 30, 'y'),
    scale: () => COUNTERFEITS.scale.make(ref),
    flash: () => COUNTERFEITS.flash.make(ref),
    stripe: () => COUNTERFEITS.stripe.make(ref),
    cut: () => COUNTERFEITS.cut.make(720),
    collapse: () => COUNTERFEITS.collapse.make(),
    noise: () => COUNTERFEITS.noise.make(),
    rigidHalves: () => COUNTERFEITS.rigidHalves.make(ref),
    fadeHalf: () => COUNTERFEITS.fadeHalf.make(ref),
    rearOnTop: () => COUNTERFEITS.rearOnTop.make(),
    translucentFront: () => COUNTERFEITS.translucentFront.make(),
  };
  if (!makers[kind]) throw new Error(`unknown counterfeit ${kind}; known: ${Object.keys(makers).join(', ')}`);
  return makers[kind]();
}
export const COUNTERFEIT_MIMICS = { ...Object.fromEntries(Object.entries(COUNTERFEITS).map(([k, v]) => [k, v.mimics])), sway: 'uniform global sway or translation', swayVertical: 'uniform whole-sheet oscillation' };
