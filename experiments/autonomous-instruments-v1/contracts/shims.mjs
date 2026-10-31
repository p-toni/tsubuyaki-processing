// Role probes for archived sources that predate the `role` convention.
// Each shim was written after reading its source, so validation of
// role-dependent requirements on these sources is not blind to the
// implementation. Prospective sketches must declare roles themselves.
const byCallOrder = { rule: 'the first 4,000 point calls (loop indices i >= 8000) draw the rear layer', fn: k => (k < 4000 ? 'rear' : 'front') };

export const SHIMS = {
  'compact-preflight-v1/P01/late/v1.js': byCallOrder,
  'compact-preflight-v1/P01/late/v2.js': byCallOrder,
  'compact-preflight-v1/P01/early/v3.js': {
    rule: 'visibility selection: rear shade 80±40, front shade 180±60; gray below 120 is rear',
    fn: (k, frame) => (frame.data[k * 7 + 3] < 120 ? 'rear' : 'front'),
  },
};
