#!/usr/bin/env node
import fs from 'node:fs';

// Intended for Tsubuyaki Processing posts: source code + hashtag, no URLs.
// X/Twitter's twitter-text v3 config uses max 280, scale 100,
// default weight 200 and these one-weight ranges.
const ONE_WEIGHT_RANGES = [
  [0, 4351],
  [8192, 8205],
  [8208, 8223],
  [8242, 8247],
];

function codePointWeight(cp) {
  return ONE_WEIGHT_RANGES.some(([a, b]) => cp >= a && cp <= b) ? 1 : 2;
}

function weightedLength(text) {
  // This is exact for the intended code-post domain (no URL transformation,
  // no emoji grapheme collapsing). Reject those inputs rather than pretending.
  if (/https?:\/\//u.test(text)) {
    throw new Error('URLs require full twitter-text URL transformation; remove the URL before checking.');
  }
  if (/\p{Extended_Pictographic}/u.test(text)) {
    throw new Error('Emoji require twitter-text grapheme parsing; this checker expects code + hashtag only.');
  }
  let n = 0;
  for (const ch of text) n += codePointWeight(ch.codePointAt(0));
  return n;
}

let text;
if (process.argv[2]) {
  text = fs.readFileSync(process.argv[2], 'utf8');
} else {
  text = fs.readFileSync(0, 'utf8');
}

text = text.replace(/\r?\n$/u, '');
const raw = [...text].length;
const weighted = weightedLength(text);
const pass = raw <= 280 && weighted <= 280;

console.log(JSON.stringify({
  rawCodePoints: raw,
  xWeightedLength: weighted,
  rawLimit: 280,
  weightedLimit: 280,
  pass,
}, null, 2));

process.exitCode = pass ? 0 : 1;
