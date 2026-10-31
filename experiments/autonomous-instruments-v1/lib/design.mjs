// Study design power: how often a frozen gate passes under an assumed effect.
// Briefs differ in difficulty: each brief's control success is sigmoid(b) with
// b ~ N(logit(base), sd); the treatment adds a fixed logit shift. Arms run in
// isolated sessions, so runs are independent. Seeded, deterministic.

export const logit = p => Math.log(p / (1 - p));
export const sigmoid = x => 1 / (1 + Math.exp(-x));

const fact = n => (n <= 1 ? 1 : n * fact(n - 1));
export const binomTail = (n, k, p) => {
  let s = 0;
  for (let i = k; i <= n; i++) s += fact(n) / (fact(i) * fact(n - i)) * p ** i * (1 - p) ** (n - i);
  return s;
};

// One-sided Student t quantile by bisection on the regularized incomplete beta.
function betacf(a, b, x) {
  let c = 1, d = 1 - (a + b) * x / (a + 1);
  d = 1 / (Math.abs(d) < 1e-30 ? 1e-30 : d);
  let h = d;
  for (let m = 1; m <= 200; m++) {
    const m2 = 2 * m;
    let aa = m * (b - m) * x / ((a + m2 - 1) * (a + m2));
    d = 1 + aa * d; d = 1 / (Math.abs(d) < 1e-30 ? 1e-30 : d); c = 1 + aa / c; c = Math.abs(c) < 1e-30 ? 1e-30 : c; h *= d * c;
    aa = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1));
    d = 1 + aa * d; d = 1 / (Math.abs(d) < 1e-30 ? 1e-30 : d); c = 1 + aa / c; c = Math.abs(c) < 1e-30 ? 1e-30 : c;
    const del = d * c; h *= del;
    if (Math.abs(del - 1) < 1e-12) break;
  }
  return h;
}
function lgamma(x) {
  const g = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5];
  let y = x, tmp = x + 5.5, ser = 1.000000000190015;
  tmp -= (x + 0.5) * Math.log(tmp);
  for (const c of g) ser += c / ++y;
  return -tmp + Math.log(2.5066282746310005 * ser / x);
}
function ibeta(a, b, x) {
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  const bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
  return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
}
export const tUpperTail = (t, df) => (t <= 0 ? 1 - 0.5 * ibeta(df / 2, 0.5, df / (df + t * t)) : 0.5 * ibeta(df / 2, 0.5, df / (df + t * t)));
export function tCritical(alpha, df) {
  let lo = 0, hi = 50;
  for (let i = 0; i < 100; i++) { const mid = (lo + hi) / 2; if (tUpperTail(mid, df) > alpha) lo = mid; else hi = mid; }
  return (lo + hi) / 2;
}

function rng(seed) {
  let s = seed | 0;
  const rand = () => { s = (s + 0x6d2b79f5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const gauss = () => Math.sqrt(-2 * Math.log(1 - rand())) * Math.cos(2 * Math.PI * rand());
  return { rand, gauss };
}

// test: 'paired-t' (per-brief success-rate differences), 'sign' (briefs where
// one arm wins more runs), or a custom gate(wins, losses, diffs) -> boolean.
export function passProbability({ briefs, runs = 1, base = 0.5, sd = 1, shift = 0, test = 'paired-t', alpha = 0.1, sims = 4000, seed = 20261031, gate = null }) {
  const { rand, gauss } = rng(seed), crit = test === 'paired-t' ? tCritical(alpha, briefs - 1) : null;
  let pass = 0;
  for (let s = 0; s < sims; s++) {
    let wins = 0, losses = 0; const diffs = [];
    for (let b = 0; b < briefs; b++) {
      const level = logit(base) + sd * gauss();
      let c = 0, t = 0;
      for (let r = 0; r < runs; r++) { c += rand() < sigmoid(level); t += rand() < sigmoid(level + shift); }
      wins += t > c; losses += c > t; diffs.push((t - c) / runs);
    }
    if (gate) pass += !!gate(wins, losses, diffs);
    else if (test === 'sign') pass += wins + losses > 0 && binomTail(wins + losses, wins, 0.5) <= alpha;
    else {
      const m = diffs.reduce((a, d) => a + d, 0) / briefs, v = diffs.reduce((a, d) => a + (d - m) ** 2, 0) / (briefs - 1);
      pass += v > 0 && m / Math.sqrt(v / briefs) > crit;
    }
  }
  return pass / sims;
}

// Logit shift that raises a typical brief's success from base by `points` (0-1).
export const shiftFor = (base, points) => logit(Math.min(0.999, base + points)) - logit(base);

export function assess(design) {
  const shift = design.shift ?? shiftFor(design.base ?? 0.5, design.effect ?? 0.25);
  const power = passProbability({ ...design, shift }), falsePass = passProbability({ ...design, shift: 0, seed: (design.seed ?? 20261031) + 1 });
  return { ...design, shift: +shift.toFixed(4), power, falsePass };
}

// Smallest number of briefs reaching the target power (searching up to maxBriefs).
export function briefsFor(design, target = 0.8, maxBriefs = 64) {
  for (let n = 4; n <= maxBriefs; n += 2) if (assess({ ...design, briefs: n, sims: design.sims ?? 2000 }).power >= target) return n;
  return null;
}
