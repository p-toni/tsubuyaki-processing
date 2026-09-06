import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {test} from 'node:test';
import {decodePNG} from './png.mjs';

// Each 3x5 fixture contains one row for each PNG filter (0 through 4).
const fixtures = [
  {
    "kind": 0,
    "png": "iVBORw0KGgoAAAANSUhEUgAAAAMAAAAFCAAAAAClGgl+AAAAGklEQVR4nGMQTtvJ6BMczGRpaclc4+bGAqQBMOEEjbYBP0wAAAAASUVORK5CYII=",
    "rgba": "131313ff666666ffb9b9b9ff4c4c4cff9f9f9ffff2f2f2ff858585ffd8d8d8ff2b2b2bffbebebeff111111ff646464fff7f7f7ff4a4a4aff9d9d9dff"
  },
  {
    "kind": 2,
    "png": "iVBORw0KGgoAAAANSUhEUgAAAAMAAAAFCAIAAAAPE8H1AAAAKklEQVR4nGMQTtvJE7+JNWI1o8/8Tz/BgMkSBphrlvpLzpQEIhYgDyILABrsFp0RXhJPAAAAAElFTkSuQmCC",
    "rgba": "1366b9ff0c5fb2ff0558abff4c9ff2ff4598ebff3e91e4ff85d82bff7ed124ff77ca1dffbe1164ffb70a5dffb00356fff74a9dfff04396ffe93c8fff"
  },
  {
    "kind": 4,
    "png": "iVBORw0KGgoAAAANSUhEUgAAAAMAAAAFCAQAAAAqeJ4pAAAAJ0lEQVR4nGMQTtvJE7+J0Wf+MiBgsgQD5pqlHwoKPrBYWt63vH8fAOYZDlxCdr7fAAAAAElFTkSuQmCC",
    "rgba": "13131366b9b9b90c5f5f5fb24c4c4c9ff2f2f245989898eb858585d82b2b2b7ed1d1d124bebebe11646464b70a0a0a5df7f7f74a9d9d9df043434396"
  },
  {
    "kind": 6,
    "png": "iVBORw0KGgoAAAANSUhEUgAAAAMAAAAFCAYAAACAcVaiAAAAK0lEQVR4nGMQTtvJE7+JNWL1v8AljD7zP7n6QAGTJRJgrlnqX+EMBSzIMgC8iBMvIhxRVwAAAABJRU5ErkJggg==",
    "rgba": "1366b90c5fb20558abfe51a44c9ff24598eb3e91e4378add85d82b7ed12477ca1d70c316be1164b70a5db00356a9fc4ff74a9df04396e93c8fe23588"
  }
];

for (const fixture of fixtures) {
  test(`decode color type ${fixture.kind} with all five filters`, () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'tsubuyaki-png-'));
    try {
      const file = path.join(dir, 'frame.png');
      fs.writeFileSync(file, Buffer.from(fixture.png, 'base64'));
      const image = decodePNG(file);
      assert.equal(image.w, 3);
      assert.equal(image.h, 5);
      assert.deepEqual(Buffer.from(image.rgba), Buffer.from(fixture.rgba, 'hex'));
    } finally {
      fs.rmSync(dir, {recursive: true, force: true});
    }
  });
}

const invalidFixtures = [
  {
    "name": "signature",
    "png": "bm90IGEgUE5H",
    "error": "not a PNG"
  },
  {
    "name": "depth",
    "png": "iVBORw0KGgoAAAANSUhEUgAAAAMAAAAFEAAAAAD1itU9AAAAC0lEQVR4nGNgwAQAABQAAX3+Hu4AAAAASUVORK5CYII=",
    "error": "supports non-interlaced 8-bit"
  },
  {
    "name": "filter",
    "png": "iVBORw0KGgoAAAANSUhEUgAAAAMAAAAFCAAAAAClGgl+AAAADklEQVR4nGNlYGBgRcMAAUAAGk/iEHIAAAAASUVORK5CYII=",
    "error": "unsupported PNG filter 5"
  }
];
for (const fixture of invalidFixtures) {
  test(`reject unsupported ${fixture.name} with the file path`, () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'tsubuyaki-png-'));
    try {
      const file = path.join(dir, 'bad.png');
      fs.writeFileSync(file, Buffer.from(fixture.png, 'base64'));
      assert.throws(() => decodePNG(file), error =>
        error.message.startsWith(`${file}: `) && error.message.includes(fixture.error));
    } finally {
      fs.rmSync(dir, {recursive: true, force: true});
    }
  });
}
