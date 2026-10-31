#!/usr/bin/env node
// Check a study design's power before freezing its gate.
//   node power.mjs --briefs=24 --runs=3 --base=0.5 --effect=0.25 [--sd=1] [--test=paired-t|sign] [--alpha=0.1] [--min-power=0.5]
// --effect is the delivery gain for a typical brief (0.25 = 25 points). Exits 1
// when power at that effect is below --min-power, so a protocol can gate on it.
import { assess, briefsFor } from './lib/design.mjs';

const arg = (name, fallback) => { const a = process.argv.find(x => x.startsWith(`--${name}=`)); return a ? a.split('=')[1] : fallback; };
const design = {
  briefs: Number(arg('briefs', 24)), runs: Number(arg('runs', 3)), base: Number(arg('base', 0.5)), effect: Number(arg('effect', 0.25)),
  sd: Number(arg('sd', 1)), test: arg('test', 'paired-t'), alpha: Number(arg('alpha', 0.1)), sims: Number(arg('sims', 4000)),
};
const minPower = Number(arg('min-power', 0.5));
const result = assess(design);
const needed = briefsFor(design, 0.8);
console.log(JSON.stringify({
  design: { briefs: design.briefs, runsPerArm: design.runs, baseline: design.base, effect: design.effect, briefSpreadLogitSD: design.sd, test: design.test, alpha: design.alpha },
  power: +result.power.toFixed(3), falsePass: +result.falsePass.toFixed(3), briefsFor80PercentPower: needed,
  verdict: result.power >= minPower ? 'adequate' : `underpowered: below ${minPower}`,
}, null, 1));
process.exitCode = result.power >= minPower ? 0 : 1;
