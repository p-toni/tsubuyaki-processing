// Point-stream runtime shared by the judge-panel and brief-contract tools.
//
// Executes a p5.js global-mode sketch that uses createCanvas, background,
// stroke, strokeWeight and point (every archived readable source does) in a
// Node vm with p5-equivalent stubs, and records each frame's points in draw
// order: x, y, strokeWeight, r, g, b, alpha. Readable sketches are stateless
// functions of frameCount, so frames can be sampled in any order.
//
// Roles: a sketch may assign a global `role` before drawing points (for
// example role = 'rear'); the value is recorded per point. Archived sources
// predate this convention, so callers may pass a role shim instead.
//
// This executes trusted archived JavaScript. It is not a sandbox.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

export const STRIDE = 7;
export const IN_FLIGHT = ['compact-representation-v1'];

export function assertNotInFlight(file, allowInFlight = false) {
  if (allowInFlight) return;
  const parts = path.resolve(file).split(path.sep);
  const study = IN_FLIGHT.find(s => parts.includes(s));
  if (study) {
    throw new Error(`refusing ${file}: ${study} is in flight and its protocol forbids outside observation; ` +
      'only that study may pass allowInFlight');
  }
}

export function loadSketch(file, { allowInFlight = false, roleShim = null } = {}) {
  assertNotInFlight(file, allowInFlight);
  const source = fs.readFileSync(file, 'utf8');
  return loadSketchSource(source, { name: file, roleShim });
}

export function loadSketchSource(source, { name = 'sketch', roleShim = null } = {}) {
  const math = Object.fromEntries(Object.getOwnPropertyNames(Math).map(k => [k, Math[k]]));
  let data = [], roles = [], anyRole = false;
  let weight = 1, color = [255, 255, 255, 255], background = [0, 0, 0], canvas = null;
  const context = vm.createContext({
    ...math, PI: Math.PI, TAU: 2 * Math.PI, TWO_PI: 2 * Math.PI, HALF_PI: Math.PI / 2,
    frameCount: 0, role: undefined,
    createCanvas: (w, h) => { canvas = [w, h]; },
    background: (...v) => { background = v.length <= 2 ? [v[0], v[0], v[0]] : v.slice(0, 3); },
    strokeWeight: w => { weight = w; },
    stroke: (...v) => { color = v.length <= 2 ? [v[0], v[0], v[0], v[1] ?? 255] : [v[0], v[1], v[2], v[3] ?? 255]; },
    point: (x, y) => {
      data.push(x, y, weight, color[0], color[1], color[2], color[3]);
      roles.push(context.role);
      if (context.role !== undefined) anyRole = true;
    },
  });
  vm.runInContext(source, context, { filename: name });
  if (typeof context.setup === 'function') vm.runInContext('setup()', context);
  if (typeof context.draw !== 'function') throw new Error(`${name}: no draw()`);
  const draw = new vm.Script('draw()');
  const cache = new Map();

  function frame(f) {
    if (cache.has(f)) return cache.get(f);
    data = []; roles = []; anyRole = false;
    context.frameCount = f;
    draw.runInContext(context, { timeout: 20000 });
    const out = { frame: f, n: data.length / STRIDE, data: Float64Array.from(data), background: [...background], roles: null };
    if (anyRole) out.roles = roles.slice();
    if (roleShim) out.roles = Array.from({ length: out.n }, (_, k) => roleShim(k, out));
    for (let k = 0; k < out.data.length; k++) if (!Number.isFinite(out.data[k])) throw new Error(`${name}: non-finite value at frame ${f}`);
    if (cache.size > 400) cache.clear();
    cache.set(f, out);
    return out;
  }
  return { name, frame, get canvas() { return canvas; } };
}

// Wrap a sketch with a point-stream transform: transform(f, base) -> frame object.
// The transform may read any frame of the base sketch (for example a reference frame).
export function transformed(sketch, transform, label) {
  const cache = new Map();
  return {
    name: `${sketch.name} :: ${label}`,
    canvas: sketch.canvas,
    frame(f) {
      if (!cache.has(f)) cache.set(f, transform(f, sketch));
      return cache.get(f);
    },
  };
}
