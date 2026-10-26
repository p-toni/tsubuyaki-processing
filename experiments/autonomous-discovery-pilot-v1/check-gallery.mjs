// Check the delivered gallery, including actual ten-second playback of each sketch.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch({headless:true,
  ...(process.env.CHROMIUM_PATH ? {executablePath:process.env.CHROMIUM_PATH} : {})});
const output = path.join(here, 'gallery-checks');
fs.mkdirSync(output, {recursive:true});
const results = {browser:await browser.version(), gallery:{}, sketches:[]};
try {
  const page = await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(pathToFileURL(path.join(here,'gallery/index.html')).href);
  await page.waitForFunction(() => [...document.querySelectorAll('video')].length === 3 &&
    [...document.querySelectorAll('video')].every(v => v.readyState >= 1));
  const videos = await page.locator('video').evaluateAll(vs => vs.map(v => ({
    duration:v.duration,width:v.videoWidth,height:v.videoHeight,loop:v.loop,autoplay:v.autoplay
  })));
  for (const v of videos) assert.deepEqual(v, {duration:10,width:400,height:400,loop:false,autoplay:false});
  await page.locator('video').evaluateAll(vs => Promise.all(vs.map(v => v.play())));
  await page.waitForFunction(() => [...document.querySelectorAll('video')].every(v => v.currentTime > .2));
  const playbackTimes = await page.locator('video').evaluateAll(vs => vs.map(v => {v.pause();return v.currentTime;}));
  await page.locator('video').evaluateAll(vs => Promise.all(vs.map(v => new Promise(resolve => {
    v.onseeked=resolve;v.currentTime=0;
  }))));
  await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
  assert.deepEqual(errors, []);
  results.gallery = {videos,playbackTimes,mobileWidth:390,mobileOverflow:false,errors};
  await page.close();

  results.sketches = await Promise.all(['B01','B02','B03'].map(async brief => {
    const p = await browser.newPage({viewport:{width:850,height:850},deviceScaleFactor:1});
    const errors = [];
    p.on('pageerror', e => errors.push(String(e)));
    await p.goto(pathToFileURL(path.join(here,`gallery/${brief}.html`)).href);
    await p.waitForFunction(() => typeof t !== 'undefined' && t === 1 && !!document.querySelector('#stage canvas'));
    const source = await p.locator('#exact-post').textContent();
    assert.equal(source.trimEnd(), fs.readFileSync(path.join(here,brief,'compact-1.txt'),'utf8').trimEnd());
    const png = await p.locator('canvas').evaluate(c => c.toDataURL('image/png'));
    assert.ok(Buffer.from(png.split(',')[1],'base64').equals(fs.readFileSync(path.join(here,brief,'final-frames/0001.png'))));
    await p.getByRole('button',{name:'Play',exact:true}).click();
    await p.waitForFunction(() => t >= 20);
    await p.getByRole('button',{name:'Pause',exact:true}).click();
    const paused = await p.evaluate(() => t);
    await p.waitForTimeout(150);
    assert.equal(await p.evaluate(() => t), paused);
    await p.getByRole('button',{name:'Restart',exact:true}).click();
    await p.waitForFunction(() => t === 1);
    const start = Date.now();
    await p.getByRole('button',{name:'Play',exact:true}).click();
    await p.waitForFunction(() => t >= 600, undefined, {timeout:30000});
    const wallPlaybackSeconds = (Date.now()-start)/1000;
    assert.equal(await p.evaluate(() => t), 600);
    await p.waitForTimeout(150);
    assert.equal(await p.evaluate(() => t), 600);
    assert.equal(await p.locator('#play').textContent(), 'Play');
    await p.screenshot({path:path.join(output,`${brief}.png`)});
    await p.getByRole('button',{name:'Play',exact:true}).click();
    await p.waitForFunction(() => t > 1 && t < 600);
    await p.getByRole('button',{name:'Pause',exact:true}).click();
    await p.setViewportSize({width:390,height:844});
    assert.ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert.deepEqual(errors, []);
    await p.close();
    return {brief,sourceMatches:true,firstFrameRasterMatches:true,pauseRestartReplay:true,
      stoppedAt:600,wallPlaybackSeconds,mobileOverflow:false,errors};
  }));
  fs.writeFileSync(path.join(here,'browser-checks.json'),JSON.stringify(results,null,2)+'\n');
  console.log(JSON.stringify(results));
} finally {
  await browser.close();
}
