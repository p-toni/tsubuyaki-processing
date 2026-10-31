#!/usr/bin/env node
// Pass probability of frozen advancement gates under assumed true effects.
// Pairs are independent briefs; each arm delivers with its own probability.
// A pair is a treatment win when only the treatment delivers, a control win
// when only the control delivers, and otherwise tied. Extra conjuncts in the
// real gates (no fewer deliveries, no artistic regression) only lower the pass
// probability, so these are upper bounds. Node built-ins only.
const fact = n => (n <= 1 ? 1 : n * fact(n - 1));

function passProbability(n, pT, pC, gate) {
  const win = pT * (1 - pC), loss = (1 - pT) * pC, tie = 1 - win - loss;
  let total = 0;
  for (let t = 0; t <= n; t++) for (let c = 0; c + t <= n; c++) {
    const e = n - t - c;
    if (gate(t, c)) total += fact(n) / (fact(t) * fact(c) * fact(e)) * win ** t * loss ** c * tie ** e;
  }
  return total;
}

const binomTail = (n, k, p) => {
  let s = 0;
  for (let i = k; i <= n; i++) s += fact(n) / (fact(i) * fact(n - i)) * p ** i * (1 - p) ** (n - i);
  return s;
};

const gates = [
  { name: 'feedback-value-v1 (>=4 treatment wins, <=1 control win, 6 briefs)', n: 6, gate: (t, c) => t >= 4 && c <= 1 },
  { name: 'compact-preflight-v1 (>=2 treatment wins, 0 control wins, 4 briefs)', n: 4, gate: (t, c) => t >= 2 && c === 0 },
];
const fmt = x => `${(100 * x).toFixed(0)}%`;
for (const g of gates) {
  const nullPass = passProbability(g.n, 0.5, 0.5, g.gate);
  console.log(g.name);
  for (const [pC, pT] of [[0.5, 0.75], [0.5, 0.9], [0.6, 0.8]]) {
    const pass = passProbability(g.n, pT, pC, g.gate);
    console.log(`  delivery ${fmt(pC)} -> ${fmt(pT)}: pass ${fmt(pass)}; null pass ${(100 * nullPass).toFixed(1)}%; likelihood ratio of a fail ${((1 - pass) / (1 - nullPass)).toFixed(2)}`);
  }
}
// Human-pair template used in September: decisive win rate > 0.65 and one-sided p <= 0.10.
for (const n of [12, 24]) {
  let k = 0;
  while (binomTail(n, k, 0.5) > 0.10 || k / n <= 0.65) k++;
  console.log(`${n} decisive human pairs (needs >= ${k}): false pass ${(100 * binomTail(n, k, 0.5)).toFixed(1)}%; power at true 65% ${fmt(binomTail(n, k, 0.65))}, 75% ${fmt(binomTail(n, k, 0.75))}, 85% ${fmt(binomTail(n, k, 0.85))}`);
}

// Autonomous designs, simulated with brief-to-brief heterogeneity: each brief's
// control success is sigmoid(b), b ~ N(0, 1); treatment shifts b by a fixed logit.
// Arms run in isolated sessions, so runs are independent. Seeded for reproducibility.
let seed = 20261031;
const rand = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const gauss = () => Math.sqrt(-2 * Math.log(1 - rand())) * Math.cos(2 * Math.PI * rand());
const sigmoid = x => 1 / (1 + Math.exp(-x));
const T_CRIT = { 11: 1.3634, 23: 1.3195 }; // one-sided alpha 0.10
function simulate(briefs, runs, shift, rule, sims = 4000) {
  let pass = 0;
  for (let s = 0; s < sims; s++) {
    let wins = 0, losses = 0; const diffs = [];
    for (let b = 0; b < briefs; b++) {
      const base = gauss(); let c = 0, t = 0;
      for (let r = 0; r < runs; r++) { c += rand() < sigmoid(base); t += rand() < sigmoid(base + shift); }
      wins += t > c; losses += c > t; diffs.push((t - c) / runs);
    }
    if (rule === 'october') pass += wins >= 4 && losses <= 1;
    else if (rule === 'sign') pass += wins + losses > 0 && binomTail(wins + losses, wins, 0.5) <= 0.10;
    else {
      const m = diffs.reduce((a, d) => a + d, 0) / briefs;
      const v = diffs.reduce((a, d) => a + (d - m) ** 2, 0) / (briefs - 1);
      pass += v > 0 && m / Math.sqrt(v / briefs) > T_CRIT[briefs - 1];
    }
  }
  return pass / sims;
}
console.log('\nWith brief heterogeneity (logit sd 1): pass probability');
const designs = [['feedback-value rule, 6 briefs x 1 run', 6, 1, 'october'], ['24 briefs x 1 run, sign test', 24, 1, 'sign'],
  ['12 briefs x 3 runs, paired t', 12, 3, 't'], ['24 briefs x 3 runs, paired t', 24, 3, 't']];
for (const [label, shift] of [['+25 points (logit +1.10)', 1.10], ['+15 points (logit +0.62)', 0.62], ['no effect', 0]]) {
  console.log(`  ${label}: ` + designs.map(([name, n, r, rule]) => `${name} ${fmt(simulate(n, r, shift, rule))}`).join('; '));
}
