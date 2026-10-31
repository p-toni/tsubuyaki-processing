#!/usr/bin/env node
// Compressibility forecast: mechanical, idiom-free minification of a readable
// p5.js sketch, reported as the X-weighted length of a complete post.
//
// It strips comments and whitespace, drops const/let/var, renames declared
// multi-character identifiers to unused single letters and shortens numeric
// literals. It never applies semantic golf (setup folding, aliases, counters,
// algebra). The output is a LENGTH FORECAST. It is not guaranteed to execute;
// any use as a post requires the normal exact verification.
//
// Protocol caution: a forecast is a character count. A study whose protocol
// forbids counts before readable selection is listed in IN_FLIGHT; the CLI
// refuses its sources until that study's selection.json exists.
//
// Usage: node forecast-length.mjs SKETCH.js [...]   (Node built-ins only)
import { existsSync, readFileSync } from 'node:fs';
import { join, resolve, sep } from 'node:path';

const IN_FLIGHT = ['compact-representation-v1'];

const HASHTAG_WEIGHT = 21; // "//#つぶやきProcessing": 17 ASCII + 4 kana at weight 2
const PUNCT = ['>>>=', '...', '===', '!==', '**=', '<<=', '>>=', '>>>', '&&=', '||=', '??=',
  '=>', '==', '!=', '<=', '>=', '&&', '||', '??', '?.', '++', '--', '+=', '-=', '*=', '/=',
  '%=', '&=', '|=', '^=', '**', '<<', '>>'];
const HOOKS = new Set(['setup', 'draw', 'preload', 'mousePressed', 'mouseMoved', 'keyPressed', 'windowResized']);
const DECL = new Set(['const', 'let', 'var']);
const wordy = c => /[A-Za-z0-9_$]/.test(c);
const OPEN = new Set(['(', '[', '{']);
const CLOSE = new Set([')', ']', '}']);

export function tokenize(src) {
  const toks = [];
  let i = 0;
  while (i < src.length) {
    const c = src[i];
    if (/\s/.test(c)) { i++; continue; }
    if (src.startsWith('//', i)) { const j = src.indexOf('\n', i); i = j < 0 ? src.length : j; continue; }
    if (src.startsWith('/*', i)) { const j = src.indexOf('*/', i + 2); i = j < 0 ? src.length : j + 2; continue; }
    let m;
    if ((m = /^[A-Za-z_$][A-Za-z0-9_$]*/.exec(src.slice(i)))) { toks.push({ k: 'id', t: m[0] }); i += m[0].length; continue; }
    if ((m = /^(?:0[xX][0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)/.exec(src.slice(i)))) { toks.push({ k: 'num', t: m[0] }); i += m[0].length; continue; }
    if (c === '"' || c === "'" || c === '`') {
      let j = i + 1;
      while (j < src.length && src[j] !== c) j += src[j] === '\\' ? 2 : 1;
      toks.push({ k: 'str', t: src.slice(i, j + 1) }); i = j + 1; continue;
    }
    const p = PUNCT.find(q => src.startsWith(q, i) && !(q === '?.' && /\d/.test(src[i + 2] || '')));
    const t = p || c;
    toks.push({ k: 'punc', t }); i += t.length;
  }
  return toks;
}

export function shortNumber(text) {
  const v = Number(text);
  if (!Number.isFinite(v) || /^0[xX]/.test(text)) return text;
  const s = String(v);
  const cands = [text, s];
  if (s.startsWith('0.')) cands.push(s.slice(1));
  const z = /^(\d+?)(0+)$/.exec(s);
  if (z) cands.push(`${z[1]}e${z[2].length}`);
  for (let p = 0; p < 12; p++) cands.push(v.toExponential(p).replace('+', '').replace(/\.?0+e/, 'e'));
  return cands.filter(x => Number(x) === v).reduce((a, b) => (b.length < a.length ? b : a));
}

export function mechanicalMinify(src) {
  const toks = tokenize(src);
  const declared = new Set();
  toks.forEach((x, i) => {
    const prev = toks[i - 1], next = toks[i + 1];
    if (x.k === 'id' && DECL.has(x.t)) {
      if (next && next.k === 'id') declared.add(next.t);
      for (let j = i + 1, depth = 0; j < toks.length; j++) {
        const y = toks[j];
        if (OPEN.has(y.t)) depth++;
        else if (CLOSE.has(y.t)) { if (--depth < 0) break; }
        else if (y.t === ';' && depth === 0) break;
        else if (y.t === ',' && depth === 0 && toks[j + 1] && toks[j + 1].k === 'id') declared.add(toks[j + 1].t);
      }
    }
    if (x.t === '=>') {
      if (prev && prev.k === 'id') declared.add(prev.t);
      if (prev && prev.t === ')') for (let j = i - 2; j >= 0 && toks[j].t !== '('; j--) if (toks[j].k === 'id') declared.add(toks[j].t);
    }
    if (x.k === 'id' && next && next.t === '=' && !(prev && prev.t === '.')) declared.add(x.t);
  });
  for (const h of HOOKS) declared.delete(h);
  for (const d of DECL) declared.delete(d);
  const external = new Set(toks.filter(x => x.k === 'id' && !declared.has(x.t)).map(x => x.t));
  const pool = [...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$'].filter(c => !external.has(c));
  const freq = new Map();
  toks.forEach(x => { if (x.k === 'id' && declared.has(x.t)) freq.set(x.t, (freq.get(x.t) || 0) + 1); });
  const used = new Set([...declared].filter(n => n.length === 1));
  const rename = new Map();
  for (const [name] of [...freq].sort((a, b) => b[1] - a[1])) {
    if (name.length === 1) continue;
    const c = pool.find(q => !used.has(q));
    if (!c) break;
    used.add(c); rename.set(name, c);
  }
  // Declarators without an initializer (`let x, y;`, `let q = 1, r;`) are
  // dropped: under implicit globals they would become bare `x,y;` references.
  const skip = new Set();
  toks.forEach((x, i) => {
    if (!(x.k === 'id' && DECL.has(x.t))) return;
    const starts = [i + 1];
    let end = -1;
    for (let j = i + 1, depth = 0; j < toks.length; j++) {
      const y = toks[j];
      if (OPEN.has(y.t)) depth++;
      else if (CLOSE.has(y.t)) { if (--depth < 0) return; } // for (...) header: keep as is
      else if (depth === 0 && (y.t === 'of' || y.t === 'in')) return; // for-of / for-in
      else if (depth === 0 && y.t === ',') starts.push(j + 1);
      else if (depth === 0 && y.t === ';') { end = j; break; }
    }
    if (end < 0) return;
    const bare = starts.filter(s => toks[s] && toks[s].k === 'id' && [',', ';'].includes(toks[s + 1]?.t));
    if (bare.length === starts.length) { for (let k = i; k <= end; k++) skip.add(k); return; }
    for (const s of bare) {
      skip.add(s);
      if (toks[s + 1].t === ',') skip.add(s + 1); else skip.add(s - 1); // drop the adjoining comma
    }
  });
  let out = '';
  toks.forEach((x, i) => {
    if (skip.has(i) || (x.k === 'id' && DECL.has(x.t))) return;
    let t = x.t;
    if (x.k === 'id' && rename.has(t) && !(toks[i - 1] && toks[i - 1].t === '.')) t = rename.get(t);
    if (x.k === 'num') t = shortNumber(t);
    const last = out.at(-1);
    if (last && ((wordy(last) && wordy(t[0])) || (last === '+' && t[0] === '+') || (last === '-' && t[0] === '-') || (/\d/.test(last) && t[0] === '.'))) out += ' ';
    out += t;
  });
  return out.replace(/;}/g, '}');
}

// X-weighted length for ASCII code plus the standard hashtag suffix.
export function forecast(src) {
  const code = mechanicalMinify(src);
  const nonAscii = [...code].filter(ch => ch.codePointAt(0) > 0x7f).length;
  return { mechanicalCode: code, forecastPostWeighted: [...code].length + nonAscii + HASHTAG_WEIGHT };
}

export function zone(weighted) {
  return weighted <= 300 ? 'green' : weighted <= 340 ? 'amber' : 'red';
}

// Returns the in-flight study directory that still forbids counts, or null.
export function blockedStudy(file) {
  const parts = resolve(file).split(sep);
  for (const study of IN_FLIGHT) {
    const i = parts.indexOf(study);
    if (i >= 0 && !existsSync(join(parts.slice(0, i + 1).join(sep) || sep, 'selection.json'))) return study;
  }
  return null;
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) {
  const files = process.argv.slice(2);
  if (!files.length) { console.error('usage: node forecast-length.mjs SKETCH.js [...]'); process.exit(2); }
  for (const f of files) {
    const study = blockedStudy(f);
    if (study) {
      console.error(`refusing ${f}: ${study} forbids character counts before its readable selection is frozen (no selection.json yet)`);
      process.exitCode = 3;
      continue;
    }
    const { mechanicalCode, forecastPostWeighted } = forecast(readFileSync(f, 'utf8'));
    let parses = true;
    try { new Function(mechanicalCode); } catch { parses = false; }
    console.log(JSON.stringify({ file: f, forecastPostWeighted, zone: zone(forecastPostWeighted), mechanicalParses: parses }));
  }
}
