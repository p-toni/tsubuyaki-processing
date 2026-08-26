// Design-time math probe for repeated-family / latent-space validation.
// This file is NOT tweet code. Keep it pure: no canvas, no p5 renderer, no globals.
// The checker imports this module, perturbs one control, and evaluates the same samples.

export const controls = {
  familyExtent: 72,
  familyPhase: 0.4,
};

export const probeConfig = {
  samples: 12000,
  time: 1.5,
};

// Return null for samples that do not belong to a family being probed.
// Otherwise return:
//   family   — repeated generator name
//   instance — stable sibling id, usually derived from modulo/parity
//   x/y      — optional continuous projection before rasterization
//   latent   — meaningful pre-raster mathematical fields
export function sample(i, t, p = controls) {
  const instance = i % 5;
  const u = i / 180;
  const phase = u + instance * 1.1 + t / 8;
  const radial = 35 + p.familyExtent * (0.5 + 0.5 * Math.sin(u / 7 + instance));
  const axial = 10 * Math.cos(u / 5 + p.familyPhase * instance);

  return {
    family: 'arms',
    instance,
    x: 200 + radial * Math.cos(phase),
    y: 200 + radial * Math.sin(phase) + axial,
    latent: { radial, axial, phase },
  };
}
