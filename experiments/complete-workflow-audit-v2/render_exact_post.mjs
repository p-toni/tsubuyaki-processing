#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';

const [,,postPath,outDir,...frameArgs]=process.argv;
if(!postPath||!outDir||!frameArgs.length){console.error('usage: node render_exact_post.mjs POST OUT_DIR FRAME...');process.exit(2)}
const frames=frameArgs.map(Number);
if(frames.some(x=>!Number.isInteger(x)||x<1))throw new Error('frames must be positive integers');
const post=fs.readFileSync(postPath,'utf8').trimEnd();
if(!post.endsWith('//#つぶやきProcessing'))throw new Error('post must end with //#つぶやきProcessing');
fs.mkdirSync(outDir,{recursive:true});
function chrome(){for(const c of ['google-chrome','google-chrome-stable','chromium','chromium-browser']){const r=spawnSync(c,['--version'],{encoding:'utf8'});if(r.status===0)return c}throw new Error('no supported Chrome/Chromium executable found')}
const browser=chrome(),p5lite=path.resolve('templates/p5-lite.js');
if(!fs.existsSync(p5lite))throw new Error('templates/p5-lite.js missing');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'tsubuyaki-audit-v2-'));
try{
  for(const target of frames){
    const html=`<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}</style><script>requestAnimationFrame=f=>setTimeout(()=>f(performance.now()),0)</script><script src="${pathToFileURL(p5lite)}"></script><script>\n${post}\n</script><script>(()=>{let d=globalThis.draw;globalThis.draw=()=>{if(typeof d==='function')d();if(globalThis.frameCount>=${target})globalThis.noLoop()}})()</script>`;
    const hp=path.join(tmp,`frame-${target}.html`);fs.writeFileSync(hp,html);const url=pathToFileURL(hp).href;
    const png=path.resolve(outDir,`frame-${String(target).padStart(3,'0')}.png`);
    const r=spawnSync(browser,['--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--window-size=400,400','--virtual-time-budget=1200',`--screenshot=${png}`,url],{encoding:'utf8',maxBuffer:20*1024*1024});
    if(r.status!==0||!fs.existsSync(png))throw new Error(`render failed at frame ${target}: ${r.stderr}`);
  }
  fs.writeFileSync(path.join(outDir,'render.json'),JSON.stringify({post:path.basename(postPath),frames,browser,scheduler:'deterministic-timeout-zero'},null,2)+'\n');
}finally{fs.rmSync(tmp,{recursive:true,force:true})}
