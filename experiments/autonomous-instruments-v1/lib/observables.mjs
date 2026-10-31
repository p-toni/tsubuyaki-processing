// Measurements over point streams and rasters, used by brief contracts.
import { STRIDE } from './runtime.mjs';

// ---- masks -------------------------------------------------------------

export function dilate(mask, W, H, r = 1) {
  const out = new Uint8Array(W * H);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    if (!mask[y * W + x]) continue;
    for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
      const X = x + dx, Y = y + dy;
      if (X >= 0 && Y >= 0 && X < W && Y < H && dx * dx + dy * dy <= r * r) out[Y * W + X] = 1;
    }
  }
  return out;
}
export function erode(mask, W, H, r = 1) {
  const inv = mask.map(v => 1 - v), d = dilate(inv, W, H, r);
  return d.map(v => 1 - v);
}
export const close = (mask, W, H, r = 1) => erode(dilate(mask, W, H, r), W, H, r);

// Connected regions of pixels equal to `value` (8-connected for foreground, 4 for background).
export function regions(mask, W, H, { value = 1, minArea = 1 } = {}) {
  const labels = new Int32Array(W * H).fill(-1), list = [], stack = [];
  const nbrs = value === 1 ? [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]] : [[1, 0], [-1, 0], [0, 1], [0, -1]];
  for (let s = 0; s < W * H; s++) {
    if (mask[s] !== value || labels[s] !== -1) continue;
    const id = list.length, reg = { id, area: 0, sx: 0, sy: 0, x0: W, y0: H, x1: 0, y1: 0, border: false };
    labels[s] = id; stack.push(s);
    while (stack.length) {
      const i = stack.pop(), x = i % W, y = (i - x) / W;
      reg.area++; reg.sx += x; reg.sy += y;
      reg.x0 = Math.min(reg.x0, x); reg.x1 = Math.max(reg.x1, x); reg.y0 = Math.min(reg.y0, y); reg.y1 = Math.max(reg.y1, y);
      if (x === 0 || y === 0 || x === W - 1 || y === H - 1) reg.border = true;
      for (const [dx, dy] of nbrs) {
        const X = x + dx, Y = y + dy;
        if (X < 0 || Y < 0 || X >= W || Y >= H) continue;
        const j = Y * W + X;
        if (mask[j] === value && labels[j] === -1) { labels[j] = id; stack.push(j); }
      }
    }
    reg.cx = reg.sx / reg.area; reg.cy = reg.sy / reg.area;
    list.push(reg);
  }
  const kept = list.filter(r => r.area >= minArea);
  return { labels, list: kept, all: list };
}

// Background regions fully enclosed by foreground (do not touch the canvas border).
export function holes(mask, W, H, { minArea = 1 } = {}) {
  return regions(mask, W, H, { value: 0, minArea }).list.filter(r => !r.border);
}

// ---- point geometry ----------------------------------------------------

export function positions(frame, filter = null) {
  const xs = [], ys = [];
  for (let k = 0, p = 0; p < frame.data.length; p += STRIDE, k++) {
    if (filter && !filter(k)) continue;
    xs.push(frame.data[p]); ys.push(frame.data[p + 1]);
  }
  return { xs, ys };
}

export function centroid({ xs, ys }) {
  let x = 0, y = 0;
  for (let i = 0; i < xs.length; i++) { x += xs[i]; y += ys[i]; }
  return [x / xs.length, y / ys.length];
}

export function spread(pos) {
  const [cx, cy] = centroid(pos);
  let s = 0;
  for (let i = 0; i < pos.xs.length; i++) s += (pos.xs[i] - cx) ** 2 + (pos.ys[i] - cy) ** 2;
  return Math.sqrt(s / pos.xs.length);
}

// Residual after the best similarity transform (rotation, uniform scale,
// translation) maps ref onto cur, relative to the reference spread. Rigid
// motion and global scaling give ~0; deformation in place gives > 0.
// Requires indexed identity (same point order in both frames).
export function nonSimilarity(ref, cur) {
  const n = Math.min(ref.xs.length, cur.xs.length);
  if (n < 3) return 0;
  const [ax, ay] = centroid(ref), [bx, by] = centroid(cur);
  let zz = 0, re = 0, im = 0;
  for (let i = 0; i < n; i++) {
    const zx = ref.xs[i] - ax, zy = ref.ys[i] - ay, wx = cur.xs[i] - bx, wy = cur.ys[i] - by;
    zz += zx * zx + zy * zy; re += zx * wx + zy * wy; im += zx * wy - zy * wx;
  }
  if (zz === 0) return 0;
  const sr = re / zz, si = im / zz;
  let res = 0;
  for (let i = 0; i < n; i++) {
    const zx = ref.xs[i] - ax, zy = ref.ys[i] - ay, wx = cur.xs[i] - bx, wy = cur.ys[i] - by;
    res += (wx - (sr * zx - si * zy)) ** 2 + (wy - (sr * zy + si * zx)) ** 2;
  }
  return Math.sqrt(res / zz);
}

// Largest per-point displacement between two frames with the same identities.
export function maxDisplacement(a, b) {
  let m = 0;
  const n = Math.min(a.xs.length, b.xs.length);
  for (let i = 0; i < n; i++) m = Math.max(m, Math.hypot(a.xs[i] - b.xs[i], a.ys[i] - b.ys[i]));
  return m;
}

export function meanDisplacement(a, b) {
  let s = 0;
  const n = Math.min(a.xs.length, b.xs.length);
  for (let i = 0; i < n; i++) s += Math.hypot(a.xs[i] - b.xs[i], a.ys[i] - b.ys[i]);
  return n ? s / n : 0;
}

// ---- time series -------------------------------------------------------

export const range = (from, to, step = 1) => Array.from({ length: Math.floor((to - from) / step) + 1 }, (_, i) => from + i * step);

export function median(values) {
  const a = [...values].sort((x, y) => x - y);
  return a.length ? a[Math.floor(a.length / 2)] : NaN;
}

export function quantile(values, q) {
  const a = [...values].sort((x, y) => x - y);
  return a.length ? a[Math.min(a.length - 1, Math.floor(q * a.length))] : NaN;
}

// Lag (in samples) maximizing the correlation of b against a; positive when b follows a.
export function bestLag(a, b, maxLag) {
  const mean = s => s.reduce((x, y) => x + y, 0) / s.length;
  const ma = mean(a), mb = mean(b);
  let best = 0, bestScore = -Infinity;
  for (let lag = -maxLag; lag <= maxLag; lag++) {
    let s = 0, na = 0, nb = 0;
    for (let i = 0; i < a.length; i++) {
      const j = i + lag;
      if (j < 0 || j >= b.length) continue;
      s += (a[i] - ma) * (b[j] - mb); na += (a[i] - ma) ** 2; nb += (b[j] - mb) ** 2;
    }
    const score = na && nb ? s / Math.sqrt(na * nb) : -Infinity;
    if (score > bestScore) { bestScore = score; best = lag; }
  }
  return { lag: best, correlation: bestScore };
}
