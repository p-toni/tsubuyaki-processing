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

// ---- judge card with synthetic judges ------------------------------------
import { judgeCard, fleissKappa, cohenKappa } from './lib/judgecard.mjs';

function syntheticKey() {
  const key = {};
  let pair = 0;
  for (const degradation of ['density', 'freeze']) for (const level of [2, 3]) for (let b = 0; b < 5; b++, pair++) {
    for (const flipped of [false, true]) key[`k${pair}${flipped ? 'b' : 'a'}`] = { pair, flipped, type: 'known', degradation, level, sideOfFirst: flipped ? 'B' : 'A', betterSide: flipped ? 'B' : 'A' };
  }
  for (let r = 0; r < 6; r++, pair++) {
    for (const flipped of [false, true]) key[`r${pair}${flipped ? 'b' : 'a'}`] = { pair, flipped, type: 'real', brief: `R${r}`, first: 'x', second: 'y', archivedVerdict: r % 2 ? 'second' : 'first', sideOfFirst: flipped ? 'B' : 'A' };
  }
  return key;
}
const judge = (key, fn) => Object.fromEntries(Object.entries(key).map(([id, k]) => [id, { id, choice: fn(k, id) }]));
const oracle = k => (k.type === 'known' ? k.betterSide : (k.pair % 2 ? (k.sideOfFirst === 'A' ? 'B' : 'A') : k.sideOfFirst));

test('judge card: an oracle is accurate, flip-consistent and unbiased; a panel of oracles may gate', () => {
  const key = syntheticKey(), card = judgeCard(key, { o1: judge(key, oracle), o2: judge(key, oracle) });
  const s = card.judges.o1;
  assert.equal(s.knownAccuracy, 1); assert.equal(s.flipConsistency.known, 1); assert.equal(s.flipConsistency.real, 1); assert.equal(s.positionBiasA, 0.5);
  assert.deepEqual(s.resolution, { density: 2, freeze: 2 });
  assert.equal(card.panel.fleissKappa, 1);
  assert.equal(card.gateable.knownAnswerDistinctions.length, 4);
  assert.equal(card.gateable.fineArtisticPreferences, true);
  assert.ok(card.panel.octoberVerdicts.every(v => v.agreesWithArchive));
});

test('judge card: an always-A judge is caught by position bias and the flip test', () => {
  const key = syntheticKey(), card = judgeCard(key, { o1: judge(key, oracle), left: judge(key, () => 'A') });
  const s = card.judges.left;
  assert.equal(s.positionBiasA, 1); assert.equal(s.knownAccuracy, 0.5); assert.equal(s.flipConsistency.known, 0);
  assert.deepEqual(card.gateable.knownAnswerDistinctions, []);
  assert.equal(card.gateable.fineArtisticPreferences, false);
});

test('judge card: a random judge is near chance and not gateable', () => {
  const key = syntheticKey(), card = judgeCard(key, { o1: judge(key, oracle), rnd: judge(key, (k, id) => (hash01(id.length, id.charCodeAt(1), id.charCodeAt(id.length - 1)) < 0.5 ? 'A' : 'B')) });
  assert.ok(card.judges.rnd.knownAccuracy > 0.2 && card.judges.rnd.knownAccuracy < 0.8);
  assert.equal(card.gateable.fineArtisticPreferences, false);
});

test('kappa statistics behave at their reference points', () => {
  assert.equal(cohenKappa(['first', 'second', 'equal'], ['first', 'second', 'equal']), 1);
  assert.ok(cohenKappa(['first', 'first', 'second', 'second'], ['second', 'second', 'first', 'first']) < 0);
  assert.equal(fleissKappa([['first', 'first', 'first'], ['second', 'second', 'second']]), 1);
});

test('role weights: a later opaque point hides an earlier one; thin points still register', () => {
  const fr = { ...pointFrame([[100, 100, 6, 80, 80, 80, 255], [100, 100, 6, 200, 200, 200, 255]]), roles: ['rear', 'front'] };
  const r = rasterize(fr, { size: 200, roleWeights: true }), i = 50 * 200 + 50;
  assert.ok(r.roles.front[i] > 0.9 && r.roles.rear[i] < 0.05, `front ${r.roles.front[i]} rear ${r.roles.rear[i]}`);
  const thin = { ...pointFrame(Array.from({ length: 40 }, () => [100.5, 100.5, 1, 255, 255, 255, 255])), roles: Array(40).fill('rear') };
  const t = rasterize(thin, { size: 200, roleWeights: true });
  assert.ok(t.roles.rear[i] > 0.9, `thin accumulated weight ${t.roles.rear[i]}`);
});
