// Review evidence for model judges, and manipulation checks for degradations.
import { rasterize, toBytes, sheet, meanAbsDifference, luminance } from './raster.mjs';

// The sixteen review frames frozen by the October studies (frames 1-720).
export const REVIEW_FRAMES = [1, 49, 97, 145, 193, 241, 289, 337, 384, 432, 480, 528, 576, 624, 672, 720];

// 4x4 contact sheet of stills, in reading order.
export function contactSheet(sketch, { frames = REVIEW_FRAMES, tile = 200 } = {}) {
  return sheet(frames.map(f => toBytes(rasterize(sketch.frame(f), { size: tile }))));
}

// 4x4 sheet of motion: brightness change over the next `lag` frames, amplified.
export function motionSheet(sketch, { frames = REVIEW_FRAMES, tile = 200, lag = 6, gain = 4 } = {}) {
  return sheet(frames.map(f => {
    const g = f + lag <= 720 ? f + lag : f - lag;
    const a = rasterize(sketch.frame(f), { size: tile }), b = rasterize(sketch.frame(g), { size: tile });
    const rgb = new Uint8Array(tile * tile * 3);
    for (let i = 0; i < tile * tile; i++) {
      const d = Math.min(255, gain * Math.abs(luminance(a.img[3 * i], a.img[3 * i + 1], a.img[3 * i + 2]) - luminance(b.img[3 * i], b.img[3 * i + 1], b.img[3 * i + 2])));
      rgb[3 * i] = rgb[3 * i + 1] = rgb[3 * i + 2] = d;
    }
    return { W: tile, H: tile, rgb };
  }));
}

// Mean change between consecutive review frames: how much the evidence moves.
export function motionEnergy(sketch, { frames = REVIEW_FRAMES, tile = 100 } = {}) {
  const r = frames.map(f => rasterize(sketch.frame(f), { size: tile }));
  let s = 0;
  for (let i = 1; i < r.length; i++) s += meanAbsDifference(r[i - 1], r[i]);
  return s / (r.length - 1);
}

// Magnitude of a degradation as visible in the evidence. Spatial degradations:
// mean per-frame difference from the original. Temporal (freeze): the fraction
// of evidence motion removed. Larger means a stronger, more visible change.
export function manipulation(base, degraded, kind, { frames = REVIEW_FRAMES, tile = 100 } = {}) {
  if (kind === 'freeze') {
    const m0 = motionEnergy(base, { frames, tile });
    return m0 > 0 ? 1 - motionEnergy(degraded, { frames, tile }) / m0 : 0;
  }
  let s = 0;
  for (const f of frames) s += meanAbsDifference(rasterize(base.frame(f), { size: tile }), rasterize(degraded.frame(f), { size: tile }));
  return s / frames.length;
}
