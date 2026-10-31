// Brief text: feedback-value-v1/protocol.md (F03 Reflect).
// Thresholds were fixed before the first validation run.
import { median } from '../lib/observables.mjs';

const ACTIVE = 0.3;         // a point is disturbed when displaced > 30% of that frame's maximum
const EVENT_MIN_PX = 2;     // frames with < 2 px maximum displacement have no event
const LOCAL_MAX = 0.35;     // localized: disturbed points <= 35% of the membrane (median frame)
const TRAVEL_MIN = 0.3;     // travels: the disturbance centroid spans >= 30% of the membrane width
const EDGE_ZONE = 0.25;     // reflects: turns within 25% of the width from a lateral extreme...
const RETURN_MIN = 0.3;     // ...and comes back by >= 30% of the width
const EDGE_SHARE = 0.02;    // lateral edges: the 2% of points nearest each side at rest
const EDGE_MOVE_MAX = 3;    // anchored: <= 3 px from rest over the horizon

function analyse(ctx) {
  const frames = ctx.frames.map(f => ctx.frame(f)), n = frames[0].n;
  const rx = new Float64Array(n), ry = new Float64Array(n);
  for (let k = 0; k < n; k++) {
    rx[k] = median(frames.map(fr => fr.data[k * 7]));
    ry[k] = median(frames.map(fr => fr.data[k * 7 + 1]));
  }
  let x0 = Infinity, x1 = -Infinity;
  for (let k = 0; k < n; k++) { x0 = Math.min(x0, rx[k]); x1 = Math.max(x1, rx[k]); }
  const width = x1 - x0, series = [];
  for (const fr of frames) {
    const disp = Array.from({ length: n }, (_, k) => Math.hypot(fr.data[k * 7] - rx[k], fr.data[k * 7 + 1] - ry[k]));
    const max = Math.max(...disp);
    if (max < EVENT_MIN_PX) { series.push(null); continue; }
    let share = 0, cx = 0, w = 0;
    for (let k = 0; k < n; k++) if (disp[k] > ACTIVE * max) { share++; cx += rx[k] * disp[k]; w += disp[k]; }
    series.push({ share: share / n, x: (cx / w - x0) / width });
  }
  return { rx, ry, width, x0, x1, series, frames, n };
}
const memo = new WeakMap();
const A = ctx => { if (!memo.has(ctx)) memo.set(ctx, analyse(ctx)); return memo.get(ctx); };

export default {
  brief: 'F03', title: 'Reflect',
  text: 'A localized disturbance travels across a finite membrane, reflects at the far edge, and returns. Both lateral edges stay anchored. Uniform whole-sheet oscillation without a localized traveling event fails.',
  requirements: [
    {
      id: 'localized_traveling_event', kind: 'executable', label: 'localized_event',
      check: ctx => {
        const ev = A(ctx).series.filter(Boolean);
        if (ev.length < ctx.frames.length / 4) return { pass: false, value: { framesWithEvent: ev.length } };
        const share = median(ev.map(e => e.share)), xs = ev.map(e => e.x), span = Math.max(...xs) - Math.min(...xs);
        return { pass: share <= LOCAL_MAX && span >= TRAVEL_MIN, value: { medianDisturbedShare: share, centroidSpan: span } };
      },
    },
    {
      id: 'reflects_and_returns', kind: 'executable', label: 'reflection_and_return',
      check: ctx => {
        const xs = A(ctx).series.map(e => (e ? e.x : null));
        for (let i = 1; i + 1 < xs.length; i++) {
          if (xs[i] === null) continue;
          const nearEdge = xs[i] <= EDGE_ZONE || xs[i] >= 1 - EDGE_ZONE;
          if (!nearEdge) continue;
          const before = xs.slice(0, i).filter(v => v !== null), after = xs.slice(i + 1).filter(v => v !== null);
          if (!before.length || !after.length) continue;
          const came = Math.max(...before.map(v => Math.abs(v - xs[i]))), back = Math.max(...after.map(v => Math.abs(v - xs[i])));
          if (came >= RETURN_MIN && back >= RETURN_MIN) return { pass: true, value: { turnAtFrame: ctx.frames[i], turnPosition: xs[i] } };
        }
        return { pass: false, value: 'no reversal near a lateral edge' };
      },
    },
    {
      id: 'anchored_lateral_edges', kind: 'executable', label: 'anchored_lateral_edges',
      check: ctx => {
        const a = A(ctx), order = [...a.rx.keys()].sort((p, q) => a.rx[p] - a.rx[q]), m = Math.max(1, Math.round(EDGE_SHARE * a.n));
        const edge = [...order.slice(0, m), ...order.slice(-m)];
        let worst = 0;
        for (const fr of a.frames) for (const k of edge) worst = Math.max(worst, Math.hypot(fr.data[k * 7] - a.rx[k], fr.data[k * 7 + 1] - a.ry[k]));
        return { pass: worst <= EDGE_MOVE_MAX, value: { maxEdgeMotion: worst } };
      },
    },
  ],
};
