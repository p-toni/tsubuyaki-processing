// Forecast registry: predictions committed before a study runs, scored after.
//
// forecasts.json: { study, forecasts: [{ id, quantity, p, arm?, brief?, rationale? }] }
//   quantity: what is predicted, e.g. "deliver", "contract", "prefer"; p: probability it happens.
// outcomes.json:  { study, outcomes: { "<id>": 0 | 1 } }
//
// A study whose outcomes are mostly forecast with confidence teaches little:
// validation reports the share of forecasts in the uncertain band.

export const UNCERTAIN = [0.1, 0.9];   // p inside this band counts as genuinely uncertain
export const MIN_UNCERTAIN_SHARE = 0.5; // below this, most of the study is already predicted

export function validateForecasts(doc) {
  const errors = [], warnings = [], ids = new Set();
  if (!doc || typeof doc.study !== 'string' || !doc.study) errors.push('missing study name');
  if (!Array.isArray(doc?.forecasts) || !doc.forecasts.length) errors.push('forecasts must be a non-empty array');
  for (const [i, f] of (doc?.forecasts ?? []).entries()) {
    if (typeof f.id !== 'string' || !f.id) errors.push(`forecast ${i}: missing id`);
    else if (ids.has(f.id)) errors.push(`forecast ${i}: duplicate id ${f.id}`);
    else ids.add(f.id);
    if (typeof f.quantity !== 'string' || !f.quantity) errors.push(`forecast ${f.id ?? i}: missing quantity`);
    if (!(typeof f.p === 'number' && f.p >= 0 && f.p <= 1)) errors.push(`forecast ${f.id ?? i}: p must be a probability`);
  }
  const ps = (doc?.forecasts ?? []).map(f => f.p).filter(p => typeof p === 'number');
  const uncertainShare = ps.length ? ps.filter(p => p > UNCERTAIN[0] && p < UNCERTAIN[1]).length / ps.length : 0;
  if (ps.length && uncertainShare < MIN_UNCERTAIN_SHARE) {
    warnings.push(`only ${(100 * uncertainShare).toFixed(0)}% of outcomes are uncertain (p within ${UNCERTAIN.join('-')}); the study may teach little — redesign or skip`);
  }
  return { ok: errors.length === 0, errors, warnings, count: ps.length, uncertainShare };
}

export function scoreForecasts(doc, outcomesDoc) {
  const outcomes = outcomesDoc.outcomes ?? {}, rows = [], missing = [];
  for (const f of doc.forecasts) {
    if (!(f.id in outcomes)) { missing.push(f.id); continue; }
    const o = outcomes[f.id];
    if (o !== 0 && o !== 1) throw new Error(`outcome for ${f.id} must be 0 or 1`);
    rows.push({ ...f, outcome: o, brier: (f.p - o) ** 2, logLoss: -Math.log(Math.max(1e-6, o ? f.p : 1 - f.p)) });
  }
  const mean = xs => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null);
  const byQuantity = {};
  for (const r of rows) (byQuantity[r.quantity] ??= []).push(r);
  const bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0001].slice(0, -1).map((lo, i, arr) => {
    const hi = i + 1 < arr.length ? arr[i + 1] : 1.0001, inBin = rows.filter(r => r.p >= lo && r.p < hi);
    return { range: [lo, Math.min(1, hi)], n: inBin.length, meanForecast: mean(inBin.map(r => r.p)), observedRate: mean(inBin.map(r => r.outcome)) };
  });
  const base = mean(rows.map(r => r.outcome));
  return {
    study: doc.study, scored: rows.length, missing,
    brier: mean(rows.map(r => r.brier)),
    // Brier of always forecasting the observed base rate; skill > 0 beats it.
    brierSkill: rows.length && base !== null && base > 0 && base < 1 ? 1 - mean(rows.map(r => r.brier)) / (base * (1 - base)) : null,
    logLoss: mean(rows.map(r => r.logLoss)),
    byQuantity: Object.fromEntries(Object.entries(byQuantity).map(([q, rs]) => [q, { n: rs.length, brier: mean(rs.map(r => r.brier)) }])),
    calibration: bins,
    biggestMisses: [...rows].sort((a, b) => b.brier - a.brier).slice(0, 5).map(r => ({ id: r.id, p: r.p, outcome: r.outcome })),
  };
}
