// Render supplied source in full, pinned p5.js; no candidate generation or ranking.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const here=path.dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const [sourceArg,outArg,mode='samples']=process.argv.slice(2);
const source=path.resolve(sourceArg),out=path.resolve(outArg);
const freeze=JSON.parse(fs.readFileSync(path.join(here,'freeze.json')));
if(!['samples','clip'].includes(mode))throw Error('mode must be samples or clip');
fs.mkdirSync(out,{recursive:true});
fs.copyFileSync(source,path.join(out,'candidate.js'));
const wrapper=path.join(out,'render.html');
fs.writeFileSync(wrapper,`<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#090909}canvas{display:block}</style>
<script src="${pathToFileURL(path.join(here,'../autonomous-discovery-pilot-v1/p5.min.js'))}"></script>
<script>p5.disableFriendlyErrors=true;</script>
<script src="${pathToFileURL(path.join(out,'candidate.js'))}"></script>
<script>window.__candidateDraw=draw;const originalSetup=window.setup;
setup=()=>{if(originalSetup)originalSetup();pixelDensity(1);noLoop();window.__ready=true;};draw=()=>{};</script>`);
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
const page=await browser.newPage({viewport:{width:400,height:400},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
const timings=[];
try{
  await page.goto(pathToFileURL(wrapper).href);
  await page.waitForFunction(()=>window.__ready===true);
  const frames=mode==='clip'?Array.from({length:freeze.horizon},(_,i)=>i+1):freeze.reviewFrames;
  const capture=new Set(frames);
  const steps=Array.from({length:freeze.horizon},(_,i)=>({frame:i+1,capture:capture.has(i+1)}));
  for(let start=0;start<steps.length;start+=20){
    const batch=await page.evaluate(targets=>targets.map(({frame:f,capture})=>{
      frameCount=f;const before=performance.now();__candidateDraw();
      const canvas=document.querySelector('canvas');
      if(canvas.width!==400||canvas.height!==400)throw Error('Unexpected canvas size');
      return {frame:f,ms:performance.now()-before,png:capture?canvas.toDataURL('image/png'):null};
    }),steps.slice(start,start+20));
    for(const item of batch){
      if(item.png)fs.writeFileSync(path.join(out,String(item.frame).padStart(4,'0')+'.png'),Buffer.from(item.png.split(',')[1],'base64'));
      timings.push(item.ms);
    }
    if(mode==='clip'&&(start+20)%120===0)console.log(`${path.basename(source)}: ${start+20}/${frames.length} frames`);
  }
  if(errors.length)throw Error(errors.join('\n'));
  if(mode==='clip'){
    const ff=spawnSync(process.env.FFMPEG||'ffmpeg',['-v','error','-y','-framerate','60','-i',path.join(out,'%04d.png'),'-frames:v',String(freeze.horizon),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,'clip.mp4')],{encoding:'utf8'});
    if(ff.status!==0)throw Error(ff.stderr||String(ff.error));
  }
  const sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  const sorted=[...timings].sort((a,b)=>a-b);
  const result={source:path.relative(here,source),sourceSha256:sha(source),runtime:'p5.js 1.11.3',runtimeSha256:sha(path.join(here,'../autonomous-discovery-pilot-v1/p5.min.js')),browser:await browser.version(),mode,frames,drawFrames:steps.length,errors,drawMs:{median:sorted[Math.floor(sorted.length/2)],max:Math.max(...timings)},scheduler:'sequential frameCount 1..horizon; exact candidate draw; p5 noLoop wrapper'};
  fs.writeFileSync(path.join(out,'render.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({source:result.source,mode,frames:frames.length,drawMs:result.drawMs,errors}));
}finally{await browser.close();}
