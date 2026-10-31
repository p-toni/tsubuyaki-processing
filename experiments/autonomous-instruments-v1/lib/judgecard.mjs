// JUDGE-1 judge card: what a model judge panel can reliably distinguish.
// Pure functions over the revealed key and committed judgments.

export const GATE = { flip: 0.9, accuracy: 0.9, kappa: 0.6 }; // frozen before any judging

const under = (item, choice) => (choice === 'equal' ? 'equal' : choice === item.sideOfFirst ? 'first' : 'second');

export function cohenKappa(a, b) {
  const cats = ['first', 'second', 'equal'], n = a.length;
  if (!n) return null;
  const po = a.filter((x, i) => x === b[i]).length / n;
  const pe = cats.reduce((s, c) => s + (a.filter(x => x === c).length / n) * (b.filter(x => x === c).length / n), 0);
  return pe === 1 ? 1 : (po - pe) / (1 - pe);
}

export function fleissKappa(table) { // table: items x raters of categories
  const cats = ['first', 'second', 'equal'], N = table.length, n = table[0]?.length ?? 0;
  if (N === 0 || n < 2) return null;
  const counts = table.map(row => cats.map(c => row.filter(x => x === c).length));
  const p = cats.map((_, j) => counts.reduce((s, r) => s + r[j], 0) / (N * n));
  const P = counts.map(r => (r.reduce((s, x) => s + x * x, 0) - n) / (n * (n - 1)));
  const Pbar = P.reduce((s, x) => s + x, 0) / N, Pe = p.reduce((s, x) => s + x * x, 0);
  return Pe === 1 ? 1 : (Pbar - Pe) / (1 - Pe);
}

function judgeStats(key, choices) {
  const ids = Object.keys(key).filter(id => choices[id]);
  const decisive = ids.filter(id => choices[id].choice !== 'equal');
  const known = ids.filter(id => key[id].type === 'known');
  const byCell = {};
  for (const id of known) {
    const k = key[id], cell = `${k.degradation}@${k.level}`;
    byCell[cell] ??= { degradation: k.degradation, level: k.level, n: 0, correct: 0, equal: 0 };
    byCell[cell].n++;
    if (choices[id].choice === k.betterSide) byCell[cell].correct++;
    if (choices[id].choice === 'equal') byCell[cell].equal++;
  }
  for (const c of Object.values(byCell)) c.accuracy = c.correct / c.n;
  const pairs = {};
  for (const id of ids) (pairs[key[id].pair] ??= []).push(id);
  const flips = { known: [0, 0], real: [0, 0] };
  for (const group of Object.values(pairs)) {
    if (group.length !== 2) continue;
    const t = key[group[0]].type, [a, b] = group.map(id => under(key[id], choices[id].choice));
    flips[t][1]++;
    if (a === b) flips[t][0]++;
  }
  const resolution = {};
  for (const c of Object.values(byCell)) {
    if (c.accuracy >= GATE.accuracy && (resolution[c.degradation] === undefined || c.level < resolution[c.degradation])) resolution[c.degradation] = c.level;
  }
  return {
    judged: ids.length,
    positionBiasA: decisive.length ? decisive.filter(id => choices[id].choice === 'A').length / decisive.length : null,
    equalRate: ids.length ? (ids.length - decisive.length) / ids.length : null,
    knownAccuracy: known.length ? known.filter(id => choices[id].choice === key[id].betterSide).length / known.length : null,
    knownByCell: Object.values(byCell).sort((x, y) => x.degradation.localeCompare(y.degradation) || x.level - y.level),
    flipConsistency: { known: flips.known[1] ? flips.known[0] / flips.known[1] : null, real: flips.real[1] ? flips.real[0] / flips.real[1] : null },
    resolution,
  };
}

export function judgeCard(key, judgments) {
  const judges = Object.keys(judgments).sort(), perJudge = Object.fromEntries(judges.map(j => [j, judgeStats(key, judgments[j])]));
  const realIds = Object.keys(key).filter(id => key[id].type === 'real' && judges.every(j => judgments[j][id]));
  const table = realIds.map(id => judges.map(j => under(key[id], judgments[j][id].choice)));
  const pairwise = [];
  for (let a = 0; a < judges.length; a++) for (let b = a + 1; b < judges.length; b++) {
    pairwise.push({ judges: [judges[a], judges[b]], kappa: cohenKappa(table.map(r => r[a]), table.map(r => r[b])) });
  }
  const verdicts = {};
  for (const id of realIds) {
    const k = key[id], v = (verdicts[k.pair] ??= { brief: k.brief, first: k.first, second: k.second, archivedVerdict: k.archivedVerdict, votes: { first: 0, second: 0, equal: 0 } });
    for (const j of judges) v.votes[under(k, judgments[j][id].choice)]++;
  }
  for (const v of Object.values(verdicts)) {
    const top = Object.entries(v.votes).sort((x, y) => y[1] - x[1]);
    v.panelVerdict = top[0][1] > top[1][1] ? top[0][0] : 'tie';
    v.agreesWithArchive = v.panelVerdict === v.archivedVerdict;
  }
  const fleiss = table.length ? fleissKappa(table) : null;
  const flipOk = judges.every(j => (perJudge[j].flipConsistency.known ?? 0) >= GATE.flip);
  const gateable = {
    knownAnswerDistinctions: flipOk ? [...new Set(judges.flatMap(j => perJudge[j].knownByCell.filter(c => c.accuracy >= GATE.accuracy).map(c => `${c.degradation}@${c.level}`)))]
      .filter(cell => judges.every(j => perJudge[j].knownByCell.find(c => `${c.degradation}@${c.level}` === cell)?.accuracy >= GATE.accuracy)) : [],
    fineArtisticPreferences: fleiss !== null && fleiss >= GATE.kappa && judges.every(j => (perJudge[j].flipConsistency.real ?? 0) >= GATE.flip),
  };
  return { gate: GATE, judges: perJudge, panel: { realItemsRatedByAll: realIds.length, fleissKappa: fleiss, pairwiseKappa: pairwise, octoberVerdicts: Object.values(verdicts) }, gateable };
}
