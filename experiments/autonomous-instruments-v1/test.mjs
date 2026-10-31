// node --test test.mjs   (Node built-ins only)
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { test } from 'node:test';
import { decodePNG } from '../../scripts/png.mjs';
import { loadSketch, loadSketchSource, transformed, STRIDE } from './lib/runtime.mjs';
import { rasterize, foreground, toBytes, encodePNG, luminance, meanAbsDifference } from './lib/raster.mjs';
import { regions, holes, nonSimilarity, bestLag, positions } from './lib/observables.mjs';
import { DEGRADATIONS, COUNTERFEITS, hash01 } from './lib/transforms.mjs';
import { manipulation } from './lib/evidence.mjs';

const pointFrame = pts => ({ frame: 1, n: pts.length, background: [0, 0, 0], roles: null, data: Float64Array.from(pts.flat()) });

test('a disc keeps its area: total ink matches pi r^2', () => {
  for (const w of [1, 2, 4, 8]) {
    const r = rasterize(pointFrame([[200.3, 199.7, w, 255, 255, 255, 255]]));
    let ink = 0;
    for (let i = 0; i < r.W * r.H; i++) ink += luminance(r.img[3 * i], r.img[3 * i + 1], r.img[3 * i + 2]) / 255;
    assert.ok(Math.abs(ink - Math.PI * (w / 2) ** 2) / (Math.PI * (w / 2) ** 2) < 0.15, `w=${w} ink=${ink}`);
  }
});

test('later points cover earlier ones and own their pixels', () => {
  const r = rasterize(pointFrame([[100, 100, 6, 255, 0, 0, 255], [100, 100, 6, 0, 0, 255, 255]]), { owner: true });
  const i = 100 * 400 + 100;
  assert.equal(r.own[i], 1);
  assert.ok(r.img[3 * i + 2] > 250 && r.img[3 * i] < 5);
});

test('PNG encoder round-trips through the repository decoder', () => {
  const rgb = new Uint8Array(5 * 3 * 3).map((_, i) => (i * 37) % 256), file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'inst-')), 'x.png');
  fs.writeFileSync(file, encodePNG({ W: 5, H: 3, rgb }));
  const back = decodePNG(file);
  assert.equal(back.w, 5); assert.equal(back.h, 3);
  for (let i = 0; i < 15; i++) for (let c = 0; c < 3; c++) assert.equal(back.rgba[4 * i + c], rgb[3 * i + c]);
});

test('regions and holes find a ring and its cavity', () => {
  const W = 40, H = 40, m = new Uint8Array(W * H);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const d = Math.hypot(x - 20, y - 20); m[y * W + x] = d > 8 && d < 14 ? 1 : 0; }
  assert.equal(regions(m, W, H, { minArea: 5 }).list.length, 1);
  const h = holes(m, W, H, { minArea: 5 });
  assert.equal(h.length, 1);
  assert.ok(Math.abs(h[0].cx - 20) < 0.5 && Math.abs(h[0].cy - 20) < 0.5);
});

test('non-similarity ignores rigid motion and scaling but sees local deformation', () => {
  const xs = [], ys = [];
  for (let k = 0; k < 500; k++) { xs.push(200 + 100 * (hash01(k) - 0.5)); ys.push(200 + 60 * (hash01(k, 1) - 0.5)); }
  const ref = { xs, ys }, a = 0.7, s = 1.3;
  const moved = { xs: xs.map((x, i) => 50 + s * (Math.cos(a) * x - Math.sin(a) * ys[i])), ys: ys.map((y, i) => -20 + s * (Math.sin(a) * xs[i] + Math.cos(a) * y)) };
  assert.ok(nonSimilarity(ref, moved) < 1e-9);
  const bent = { xs, ys: ys.map((y, i) => y + 8 * Math.sin(xs[i] / 15)) };
  assert.ok(nonSimilarity(ref, bent) > 0.05);
});

test('bestLag recovers a delay', () => {
  const a = Array.from({ length: 200 }, (_, i) => Math.exp(-(((i - 60) / 8) ** 2)));
  const b = Array.from({ length: 200 }, (_, i) => Math.exp(-(((i - 75) / 8) ** 2)));
  assert.equal(bestLag(a, b, 40).lag, 15);
});

const PILOT = new URL('../autonomous-discovery-pilot-v1/B03/v2.js', import.meta.url).pathname;

test('runtime is deterministic and stateless across frame order', () => {
  const s1 = loadSketch(PILOT), s2 = loadSketch(PILOT);
  const a = s1.frame(300), b = (s2.frame(17), s2.frame(300));
  assert.deepEqual(a.data, b.data);
  assert.equal(a.data.length / STRIDE, 1800);
});

test('roles are recorded when a sketch assigns them', () => {
  const s = loadSketchSource('setup=()=>createCanvas(400,400);draw=()=>{for(let i=4;i--;){role=i<2?"front":"rear";stroke(255);point(i,i)}}');
  assert.deepEqual(s.frame(1).roles, ['rear', 'rear', 'front', 'front']);
});

test('in-flight study sources are refused', () => {
  const inFlight = new URL('../compact-representation-v1/R1/v1.js', import.meta.url).pathname;
  assert.throws(() => loadSketch(inFlight), /in flight/);
});

test('degradations are deterministic and stronger levels change the evidence more', () => {
  const base = loadSketch(PILOT);
  for (const id of ['density', 'jitter', 'freeze', 'offset', 'flicker']) {
    const d = DEGRADATIONS[id];
    const size = d.levels.map(s => manipulation(base, transformed(base, d.make(s), id), id));
    assert.deepEqual(transformed(base, d.make(d.levels[0]), id).frame(240).data, transformed(base, d.make(d.levels[0]), id).frame(240).data);
    assert.ok(size[0] > 0 && size[1] > size[0] && size[2] > size[1], `${id}: ${size.map(x => x.toFixed(3))}`);
  }
  // A uniformly coloured sketch has no shading to flatten: the check must report ~0.
  const flat = DEGRADATIONS.flatten;
  assert.ok(manipulation(base, transformed(base, flat.make(1), 'flatten'), 'flatten') < 0.01);
});

test('counterfeits remove deformation but keep the look', () => {
  const base = loadSketch(PILOT);
  for (const id of ['rotate', 'sway', 'scale', 'freeze']) {
    const c = transformed(base, COUNTERFEITS[id].make(), id);
    assert.ok(nonSimilarity(positions(c.frame(1)), positions(c.frame(400))) < 1e-9, id);
  }
  assert.ok(nonSimilarity(positions(base.frame(1)), positions(base.frame(400))) > 0.05);
});
