#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';

const [,,postPath,outDir,...frameArgs]=process.argv;
if(!postPath||!outDir||!frameArgs.length){
  console.error('usage: node render_exact_post.mjs POST OUT_DIR FRAME...');
  process.exit(2);
}
const frames=frameArgs.map(Number);
if(frames.some(x=>!Number.isInteger(x)||x<1))throw new Error('frames must be positive integers');
const post=fs.readFileSync(postPath,'utf8').trimEnd();
if(!post.endsWith('//#つぶやきProcessing'))throw new Error('post must end with //#つぶやきProcessing');
fs.mkdirSync(outDir,{recursive:true});

function chrome(){
  for(const c of ['google-chrome','google-chrome-stable','chromium','chromium-browser']){
    const r=spawnSync(c,['--version'],{encoding:'utf8'});
    if(r.status===0)return c;
  }
  throw new Error('no supported Chrome/Chromium executable found');
}
const browser=chrome();
const p5lite=path.resolve('templates/p5-lite.js');
if(!fs.existsSync(p5lite))throw new Error('templates/p5-lite.js missing');

const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'tsubuyaki-audit-render-'));
try{
  for(const target of frames){
    const statusId='audit-status';
    const html=`<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}</style><div id="${statusId}" data-ready="0" data-error=""></div><script src="${pathToFileURL(p5lite)}"></script><script>\n${post}\n</script><script>\n(()=>{const s=document.getElementById('${statusId}'),d=globalThis.draw;addEventListener('error',e=>s.dataset.error=String(e.message||e.error||'error'));globalThis.draw=()=>{try{if(typeof d==='function')d();if(globalThis.frameCount>=${target}){globalThis.noLoop();s.dataset.ready='1'}}catch(e){s.dataset.error=String(e&&e.stack||e);throw e}}})();\n</script>`;
    const hp=path.join(tmp,`frame-${target}.html`);
    fs.writeFileSync(hp,html);
    const url=pathToFileURL(hp).href;
    const common=['--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--window-size=400,400','--virtual-time-budget=7000',url];
    const dom=spawnSync(browser,[...common.slice(0,-1),'--dump-dom',url],{encoding:'utf8',maxBuffer:20*1024*1024});
    if(dom.status!==0)throw new Error(`browser runtime failed at frame ${target}: ${dom.stderr}`);
    const ready=/id="audit-status"[^>]*data-ready="1"/.test(dom.stdout);
    const err=(dom.stdout.match(/id="audit-status"[^>]*data-error="([^"]*)"/)||[])[1]||'';
    if(!ready||err)throw new Error(`post failed at frame ${target}: ready=${ready} error=${err}`);
    const png=path.resolve(outDir,`frame-${String(target).padStart(3,'0')}.png`);
    const shot=spawnSync(browser,[...common.slice(0,-1),`--screenshot=${png}`,url],{encoding:'utf8',maxBuffer:20*1024*1024});
    if(shot.status!==0||!fs.existsSync(png))throw new Error(`screenshot failed at frame ${target}: ${shot.stderr}`);
  }
  fs.writeFileSync(path.join(outDir,'render.json'),JSON.stringify({post:path.basename(postPath),frames,browser},null,2)+'\n');
}finally{
  fs.rmSync(tmp,{recursive:true,force:true});
}
