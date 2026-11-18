import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { runInNewContext } from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const generator = join(here, 'mechanical-post.mjs');
const checker = join(here, '../../scripts/check-length.mjs');
const draft = source => spawnSync(process.execPath, [generator, source], { encoding: 'utf8' });

test('the 18 October sources reproduce the recorded post bytes and lengths', () => {
  const rows = readFileSync(join(here, 'october-posts.tsv'), 'utf8').trimEnd().split('\n').slice(1);
  assert.equal(rows.length, 18);
  let fits = 0;
  for (const row of rows) {
    const [source, weighted, hash] = row.split('\t');
    const post = draft(join(here, source));
    assert.equal(post.status, 0, `${source}: ${post.stderr}`);
    assert.equal(createHash('sha256').update(post.stdout).digest('hex'), hash, source);
    const checked = spawnSync(process.execPath, [checker], { input: post.stdout, encoding: 'utf8' });
    assert.equal(checked.status, Number(weighted) <= 280 ? 0 : 1, source);
    const length = JSON.parse(checked.stdout);
    assert.equal(length.xWeightedLength, Number(weighted), source);
    if (length.pass) fits++;
  }
  assert.equal(fits, 8);
});

test('Pleated lantern reproduces the complete first attempt after selection', () => {
  const study = join(here, '../pleated-lantern-v1');
  const post = draft(join(study, 'v2.js'));
  assert.equal(post.status, 0, post.stderr);
  assert.equal(post.stdout + '\n', readFileSync(join(study, 'attempt-1.txt'), 'utf8'));
});

function sketch(t, source) {
  const directory = mkdtempSync(join(tmpdir(), 'mechanical-post-'));
  t.after(() => rmSync(directory, { recursive: true }));
  const file = join(directory, 'sketch.js');
  writeFileSync(file, source);
  return draft(file);
}

test('keeps p5 callback names, quoted text and property names', t => {
  const post = sketch(t, `mouseDragged = () => {
    const value = .5;
    text('mark;}', view?.value, value);
  };`);
  assert.equal(post.status, 0, post.stderr);
  const calls = [];
  const p5 = { view: { value: 7 }, text: (...args) => calls.push(args) };
  runInNewContext(post.stdout, p5);
  p5.mouseDragged();
  assert.deepEqual(calls, [['mark;}', 7, .5]]);
});

test('removes uninitialized declarations without leaving a trailing comma or losing a loop separator', t => {
  const post = sketch(t, `draw = () => {
    let before, total = 1, unused, after;
    for (let scratch; total < 3; total++) point(total, 0);
  };`);
  assert.equal(post.status, 0, post.stderr);
  const calls = [];
  const p5 = { point: (...args) => calls.push(args) };
  runInNewContext(post.stdout, p5);
  p5.draw();
  assert.deepEqual(calls, [[1, 0], [2, 0]]);
});

test('writes no candidate for empty, unsupported, or syntactically invalid input or output', t => {
  for (const source of [
    '// no sketch', 'draw=()=>{', 'const value=1; draw=()=>text(`${value}`);',
    'const alpha=1\nconst beta=2\ndraw=()=>point(alpha,beta)',
  ]) {
    const post = sketch(t, source);
    assert.equal(post.status, 1);
    assert.equal(post.stdout, '');
    assert.ok(post.stderr);
  }
});
