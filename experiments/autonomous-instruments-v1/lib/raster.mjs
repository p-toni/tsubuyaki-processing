// Software raster for point streams. p5's 2D renderer draws point() as a filled
// disc of diameter strokeWeight in the stroke colour; this approximates that
// with analytic edge coverage and source-over alpha compositing in draw order.
// It is a measurement and review renderer, not a byte-exact browser substitute.
import fs from 'node:fs';
import zlib from 'node:zlib';
import { STRIDE } from './runtime.mjs';

export function rasterize(frame, { size = 400, owner = false } = {}) {
  const scale = size / 400, W = size, H = size, img = new Float32Array(W * H * 3);
  const [br, bgG, bb] = frame.background;
  for (let i = 0; i < W * H; i++) { img[3 * i] = br; img[3 * i + 1] = bgG; img[3 * i + 2] = bb; }
  const own = owner ? new Int32Array(W * H).fill(-1) : null;
  const d = frame.data, cov = [];
  for (let p = 0, k = 0; p < d.length; p += STRIDE, k++) {
    const x = d[p] * scale, y = d[p + 1] * scale, r = Math.max(d[p + 2], 1) * scale / 2;
    const alpha = d[p + 6] / 255;
    if (alpha <= 0) continue;
    const reach = r + 0.5, x0 = Math.max(0, Math.floor(x - reach)), x1 = Math.min(W - 1, Math.floor(x + reach));
    const y0 = Math.max(0, Math.floor(y - reach)), y1 = Math.min(H - 1, Math.floor(y + reach));
    if (x0 > x1 || y0 > y1) continue;
    cov.length = 0;
    let total = 0;
    for (let py = y0; py <= y1; py++) for (let px = x0; px <= x1; px++) {
      const c = Math.min(1, Math.max(0, reach - Math.hypot(px + 0.5 - x, py + 0.5 - y)));
      if (c > 0) { cov.push(py * W + px, c); total += c; }
    }
    const area = Math.PI * r * r, norm = total > area ? area / total : 1; // small discs keep their area
    for (let j = 0; j < cov.length; j += 2) {
      const i = cov[j], a = alpha * cov[j + 1] * norm;
      img[3 * i] += (d[p + 3] - img[3 * i]) * a;
      img[3 * i + 1] += (d[p + 4] - img[3 * i + 1]) * a;
      img[3 * i + 2] += (d[p + 5] - img[3 * i + 2]) * a;
      if (own && cov[j + 1] * norm >= 0.5) own[i] = k;
    }
  }
  return { W, H, img, own, background: frame.background };
}

export const luminance = (r, g, b) => 0.2126 * r + 0.7152 * g + 0.0722 * b;

// Foreground mask: luminance differs from the background by more than threshold.
export function foreground(raster, threshold = 24) {
  const { W, H, img, background } = raster, bgL = luminance(...background), m = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) m[i] = Math.abs(luminance(img[3 * i], img[3 * i + 1], img[3 * i + 2]) - bgL) > threshold ? 1 : 0;
  return m;
}

export function toBytes(raster) {
  const { W, H, img } = raster, out = new Uint8Array(W * H * 3);
  for (let i = 0; i < out.length; i++) out[i] = Math.max(0, Math.min(255, Math.round(img[i])));
  return { W, H, rgb: out };
}

// Mean absolute luminance difference in 0..255 between two rasters of equal size.
export function meanAbsDifference(a, b) {
  let s = 0;
  for (let i = 0; i < a.W * a.H; i++) {
    s += Math.abs(luminance(a.img[3 * i], a.img[3 * i + 1], a.img[3 * i + 2]) - luminance(b.img[3 * i], b.img[3 * i + 1], b.img[3 * i + 2]));
  }
  return s / (a.W * a.H);
}

// Tiles RGB byte images (all the same size) into a grid with thin separators.
export function sheet(tiles, { columns = 4, gap = 4, gapValue = 40 } = {}) {
  const tw = tiles[0].W, th = tiles[0].H, rows = Math.ceil(tiles.length / columns);
  const W = columns * tw + (columns - 1) * gap, H = rows * th + (rows - 1) * gap, rgb = new Uint8Array(W * H * 3).fill(gapValue);
  tiles.forEach((t, n) => {
    const ox = (n % columns) * (tw + gap), oy = Math.floor(n / columns) * (th + gap);
    for (let y = 0; y < th; y++) rgb.set(t.rgb.subarray(y * tw * 3, (y + 1) * tw * 3), ((oy + y) * W + ox) * 3);
  });
  return { W, H, rgb };
}

const CRC_TABLE = Array.from({ length: 256 }, (_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
function crc32(buf) {
  let c = 0xffffffff;
  for (const b of buf) c = CRC_TABLE[(c ^ b) & 255] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function chunk(type, body) {
  const len = Buffer.alloc(4), crc = Buffer.alloc(4), head = Buffer.from(type, 'ascii');
  len.writeUInt32BE(body.length);
  crc.writeUInt32BE(crc32(Buffer.concat([head, body])));
  return Buffer.concat([len, head, body, crc]);
}

// Deterministic 8-bit RGB PNG (filter 0, fixed zlib level).
export function encodePNG({ W, H, rgb }) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(W, 0); ihdr.writeUInt32BE(H, 4); ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  const raw = Buffer.alloc((W * 3 + 1) * H);
  for (let y = 0; y < H; y++) { raw[y * (W * 3 + 1)] = 0; Buffer.from(rgb.buffer, rgb.byteOffset + y * W * 3, W * 3).copy(raw, y * (W * 3 + 1) + 1); }
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw, { level: 9 })), chunk('IEND', Buffer.alloc(0))]);
}

export function writePNG(file, image) { fs.writeFileSync(file, encodePNG(image)); }
