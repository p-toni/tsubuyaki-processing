#!/usr/bin/env node
// Produce a candidate from a selected arithmetic sketch in p5 global mode.
// Dropping declarations changes scope. Check the result against the readable render.
import { readFileSync } from 'node:fs';
import { Script } from 'node:vm';

const PUNCT = ['>>>=', '...', '===', '!==', '**=', '<<=', '>>=', '>>>', '&&=', '||=', '??=',
  '=>', '==', '!=', '<=', '>=', '&&', '||', '??', '?.', '++', '--', '+=', '-=', '*=', '/=',
  '%=', '&=', '|=', '^=', '**', '<<', '>>'];
const HOOKS = new Set(['setup', 'draw', 'preload', 'mousePressed', 'mouseMoved', 'keyPressed', 'windowResized']);
const DECL = new Set(['const', 'let', 'var']);
const wordy = c => /[A-Za-z0-9_$]/.test(c);
const OPEN = new Set(['(', '[', '{']);
const CLOSE = new Set([')', ']', '}']);

function tokenize(source) {
  const tokens = [];
  const lexeme = /\s+|\/\/[^\r\n\u2028\u2029]*|\/\*[\s\S]*?\*\/|[A-Za-z_$][A-Za-z0-9_$]*|0[xX][0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?/y;
  let start = 0;
  while (start < source.length) {
    lexeme.lastIndex = start;
    const match = lexeme.exec(source);
    if (match) {
      const text = match[0];
      if (!/^\s|^\//.test(text)) {
        tokens.push({ kind: /^[A-Za-z_$]/.test(text) ? 'id' : 'num', text });
      }
      start = lexeme.lastIndex;
      continue;
    }
    const first = source[start];
    if (first === '"' || first === "'" || first === '`') {
      let end = start + 1;
      while (end < source.length && source[end] !== first) {
        if (first === '`' && source.startsWith('${', end)) {
          throw new Error('Interpolated templates require manual compression.');
        }
        end += source[end] === '\\' ? 2 : 1;
      }
      tokens.push({ kind: 'str', text: source.slice(start, end + 1) });
      start = end + 1;
      continue;
    }
    const operator = PUNCT.find(op => source.startsWith(op, start) && !(op === '?.' && /\d/.test(source[start + 2] || '')));
    const text = operator || first;
    tokens.push({ kind: 'punc', text });
    start += text.length;
  }
  return tokens;
}

function shortNumber(text) {
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

function mechanicalMinify(source) {
  const tokens = tokenize(source);
  const declared = new Set();
  tokens.forEach((x, i) => {
    const prev = tokens[i - 1], next = tokens[i + 1];
    if (x.kind === 'id' && DECL.has(x.text)) {
      if (next && next.kind === 'id') declared.add(next.text);
      for (let j = i + 1, depth = 0; j < tokens.length; j++) {
        const y = tokens[j];
        if (OPEN.has(y.text)) depth++;
        else if (CLOSE.has(y.text)) { if (--depth < 0) break; }
        else if (y.text === ';' && depth === 0) break;
        else if (y.text === ',' && depth === 0 && tokens[j + 1] && tokens[j + 1].kind === 'id') declared.add(tokens[j + 1].text);
      }
    }
    if (x.text === '=>') {
      if (prev && prev.kind === 'id') declared.add(prev.text);
      if (prev?.text === ')') {
        const params = [];
        let j = i - 2;
        while (j >= 0 && (tokens[j].kind === 'id' || tokens[j].text === ',')) {
          if (tokens[j].kind === 'id') params.push(tokens[j].text);
          j--;
        }
        if (tokens[j]?.text === '(') params.forEach(name => declared.add(name));
      }
    }
  });
  for (const h of HOOKS) declared.delete(h);
  for (const d of DECL) declared.delete(d);
  const occupied = new Set(tokens.filter(x => x.kind === 'id').map(x => x.text));
  const pool = [...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$'].filter(c => !occupied.has(c));
  const freq = new Map();
  for (const { kind, text } of tokens) {
    if (kind === 'id' && text.length > 1 && declared.has(text)) {
      freq.set(text, (freq.get(text) || 0) + 1);
    }
  }
  const rename = new Map();
  for (const [name] of [...freq].sort((a, b) => b[1] - a[1])) {
    if (rename.size === pool.length) break;
    rename.set(name, pool[rename.size]);
  }
  // Declarators without an initializer (`let x, y;`, `let q = 1, r;`) are
  // dropped: under implicit globals they would become bare `x,y;` references.
  const skip = new Set();
  tokens.forEach((x, i) => {
    if (!(x.kind === 'id' && DECL.has(x.text))) return;
    const starts = [i + 1];
    let end = -1;
    for (let j = i + 1, depth = 0; j < tokens.length; j++) {
      const y = tokens[j];
      if (OPEN.has(y.text)) depth++;
      else if (CLOSE.has(y.text)) { if (--depth < 0) return; } // for (...) header: keep as is
      else if (depth === 0 && (y.text === 'of' || y.text === 'in')) return; // for-of / for-in
      else if (depth === 0 && y.text === ',') starts.push(j + 1);
      else if (depth === 0 && y.text === ';') { end = j; break; }
    }
    if (end < 0) return;
    let hasInitializer = false;
    for (const start of starts) {
      const bare = tokens[start]?.kind === 'id' && [',', ';'].includes(tokens[start + 1]?.text);
      if (start !== starts[0] && (bare || !hasInitializer)) skip.add(start - 1);
      if (bare) skip.add(start);
      else hasInitializer = true;
    }
    const inForHeader = tokens[i - 1]?.text === '(' && tokens[i - 2]?.text === 'for';
    if (!hasInitializer && !inForHeader) skip.add(end);
  });
  let out = '';
  tokens.forEach((x, i) => {
    if (skip.has(i) || (x.kind === 'id' && DECL.has(x.text))) return;
    let t = x.text;
    const previous = tokens[i - 1]?.text;
    if (x.kind === 'id' && rename.has(t) && previous !== '.' && previous !== '?.') t = rename.get(t);
    if (x.kind === 'num') t = shortNumber(t);
    if (t === '}' && out.endsWith(';')) out = out.slice(0, -1);
    const last = out.at(-1);
    if (last && ((wordy(last) && wordy(t[0])) || (last === '+' && t[0] === '+') || (last === '-' && t[0] === '-') || (/\d/.test(last) && t[0] === '.'))) out += ' ';
    out += t;
  });
  return out;
}

const [file, ...extra] = process.argv.slice(2);
if (!file || extra.length) {
  console.error('Usage: node mechanical-post.mjs SELECTED.js');
  process.exitCode = 2;
} else {
  try {
    const source = readFileSync(file, 'utf8');
    new Script(source, { filename: file });
    const code = mechanicalMinify(source);
    if (!code) throw new Error('The source contains no sketch code.');
    const post = code + '//#つぶやきProcessing';
    new Script(post, { filename: 'mechanical-post.js' });
    process.stdout.write(post);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
