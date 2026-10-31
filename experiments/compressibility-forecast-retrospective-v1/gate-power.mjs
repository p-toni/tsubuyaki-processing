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
