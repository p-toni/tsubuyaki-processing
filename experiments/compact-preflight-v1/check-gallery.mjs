// Verify the archived gallery and actual playback; this does not grade the art.
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
  await page.waitForFunction(() => document.querySelectorAll('video').length === 4 &&
    [...document.querySelectorAll('video')].every(v => v.readyState >= 1));
  const videos = await page.locator('video').evaluateAll(vs => vs.map(v => ({
    duration:v.duration,width:v.videoWidth,height:v.videoHeight,loop:v.loop,autoplay:v.autoplay
  })));
  for (const v of videos) assert.deepEqual(v, {duration:12,width:400,height:400,loop:false,autoplay:false});
  assert.equal(await page.locator('article').count(),8);
  assert.equal(await page.locator('img.poster').count(),4);
  await page.locator('video').evaluateAll(vs => Promise.all(vs.map(v => v.play())));
  await page.waitForFunction(() => [...document.querySelectorAll('video')].every(v => v.currentTime > .2));
  const playbackTimes = await page.locator('video').evaluateAll(vs => vs.map(v => {v.pause();return v.currentTime;}));
  // Reload to restore posters before checking the presentation.
  await page.reload();
  await page.screenshot({path:path.join(output,'desktop.png')});
  await page.locator('#P04').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(output,'desktop-wake.png')});
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(() => scrollTo(0,0));
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({path:path.join(output,'mobile.png')});
  assert.deepEqual(errors, []);
  results.gallery = {videos,playbackTimes,cards:8,readableOnlyPosters:4,
    mobileWidth:390,mobileOverflow:false,errors};
  await page.close();

  const entries = JSON.parse(fs.readFileSync(path.join(here,'gallery/manifest.json')));
  assert.equal(entries.length,8);
  const checkSketch = async entry => {
    const p = await browser.newPage({viewport:{width:850,height:950},deviceScaleFactor:1});
    const errors = [];
    p.on('pageerror', e => errors.push(String(e)));
    await p.goto(pathToFileURL(path.join(here,'gallery',entry.page)).href);
    await p.waitForFunction(() => window.studyState?.().frame === 1 && !!document.querySelector('#stage canvas'));
    const source = await p.locator('#sketch-source').textContent();
    assert.equal(source.trimEnd(),fs.readFileSync(path.join(here,entry.source),'utf8').trimEnd());
    const png = await p.locator('canvas').evaluate(c => c.toDataURL('image/png'));
    assert.ok(Buffer.from(png.split(',')[1],'base64').equals(fs.readFileSync(path.join(here,entry.firstFrame))),entry.page+' first-frame mismatch');
    await p.getByRole('button',{name:'Play',exact:true}).click();
    await p.waitForFunction(() => studyState().frame >= 20);
    await p.getByRole('button',{name:'Pause',exact:true}).click();
    const paused = await p.evaluate(() => studyState().frame);
    await p.waitForTimeout(150);
    assert.deepEqual(await p.evaluate(() => studyState()),{frame:paused,playing:false});
    await p.getByRole('button',{name:'Play',exact:true}).click();
    await p.waitForFunction(previous => studyState().frame > previous,paused);
    await p.getByRole('button',{name:'Pause',exact:true}).click();
    await p.getByRole('button',{name:'Restart',exact:true}).click();
    await p.waitForFunction(() => studyState().frame === 1);
    const start = Date.now();
    await p.getByRole('button',{name:'Play',exact:true}).click();
    await p.waitForFunction(() => studyState().frame >= 720,undefined,{timeout:60000});
    const wallPlaybackSeconds = (Date.now()-start)/1000;
    await p.waitForTimeout(150);
    assert.deepEqual(await p.evaluate(() => studyState()),{frame:720,playing:false});
    assert.equal(await p.locator('#play').textContent(),'Play');
    await p.screenshot({path:path.join(output,entry.page.replace('.html','.png'))});
    await p.getByRole('button',{name:'Play',exact:true}).click();
    await p.waitForFunction(() => studyState().frame > 1 && studyState().frame < 720);
    await p.getByRole('button',{name:'Pause',exact:true}).click();
    await p.setViewportSize({width:390,height:844});
    assert.ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert.deepEqual(errors,[]);
    await p.close();
    console.log(entry.page+' passed');
    return {...entry,sourceMatches:true,firstFrameRasterMatches:true,pauseResumeRestartReplay:true,
      stoppedAt:720,wallPlaybackSeconds,mobileOverflow:false,errors};
  };
  for(let offset=0;offset<entries.length;offset+=3){
    results.sketches.push(...await Promise.all(entries.slice(offset,offset+3).map(checkSketch)));
  }
  fs.writeFileSync(path.join(here,'browser-checks.json'),JSON.stringify(results,null,2)+'\n');
  console.log('PASS: 4 clips, 8 exact-source live pages, complete playback and responsive layouts.');
} finally {
  await browser.close();
}
