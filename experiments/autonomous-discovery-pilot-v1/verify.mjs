// Independent exact-source execution and all-frame compression/motion comparison.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const here=path.dirname(fileURLToPath(import.meta.url));
const read=n=>JSON.parse(fs.readFileSync(path.join(here,n)));
const sha=f=>createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const freeze=read('freeze.json'), selection=read('selection.json');
assert.equal(sha(path.join(here,'protocol.md')),freeze.protocolSha256);
const run=new vm.Script('draw()');
function execute(source){
  let coords=[],canvas=null,style={};
  const ctx=vm.createContext({PI:Math.PI,TAU:2*Math.PI,...Object.fromEntries(['sin','cos','sqrt'].map(n=>[n,Math[n]])),
    createCanvas:(w,h)=>{canvas=[w,h];},background:(...a)=>{style.background=a;},stroke:(...a)=>{style.stroke=a;},
    point:(x,y)=>{assert.ok(Number.isFinite(x)&&Number.isFinite(y));coords.push(x,y);},frameCount:0});
  vm.runInContext(source,ctx);
  if(typeof ctx.setup==='function')vm.runInContext('setup()',ctx);
  return f=>{coords=[];ctx.frameCount=f;run.runInContext(ctx,{timeout:10000});return {coords,canvas,style};};
}
const results=[];
for(const s of selection.selected){
  const readable=path.join(here,s.brief,s.version+'.js');
  const compact=path.join(here,s.brief,'compact-1.txt');
  assert.equal(sha(readable),s.sourceSha256);
  const lengthProcess=spawnSync(process.execPath,[path.join(here,'check-length.mjs'),compact],{encoding:'utf8'});
  assert.equal(lengthProcess.status,0,lengthProcess.stdout+lengthProcess.stderr);
  const length=JSON.parse(lengthProcess.stdout), original=execute(fs.readFileSync(readable,'utf8')),post=execute(fs.readFileSync(compact,'utf8'));
  let previous=null,pointCount=null,maxGeometryError=0,maxMotion=0,minInFrame=1,minCenterDistance=Infinity,minOuterRadius=Infinity,maxOuterRadius=0,maxRootError=0;
  for(let f=1;f<=freeze.horizon;f++){
    const a=original(f),b=post(f);assert.deepEqual(a.canvas,[400,400]);assert.deepEqual(b.canvas,a.canvas);assert.deepEqual(b.style,a.style);
    assert.equal(a.coords.length,b.coords.length);
    if(pointCount===null)pointCount=b.coords.length/2;
    assert.equal(b.coords.length,pointCount*2);
    let inside=0,outer=0;
    for(let j=0;j<b.coords.length;j+=2){
      const x=b.coords[j],y=b.coords[j+1];
      maxGeometryError=Math.max(maxGeometryError,Math.abs(x-a.coords[j]),Math.abs(y-a.coords[j+1]));
      if(previous)maxMotion=Math.max(maxMotion,Math.hypot(x-previous[j],y-previous[j+1]));
      inside+=x>=0&&x<=400&&y>=0&&y<=400;
      const radius=Math.hypot(x-200,y-200);minCenterDistance=Math.min(minCenterDistance,radius);outer=Math.max(outer,radius);
    }
    minInFrame=Math.min(minInFrame,inside/pointCount);minOuterRadius=Math.min(minOuterRadius,outer);maxOuterRadius=Math.max(maxOuterRadius,outer);
    if(s.brief==='B02')maxRootError=Math.max(maxRootError,Math.hypot(b.coords.at(-2)-200,b.coords.at(-1)-320));
    previous=b.coords;
  }
  assert.ok(maxGeometryError<=1e-7);assert.ok(maxMotion<=10);assert.ok(minInFrame>=.95);
  const result={brief:s.brief,readable:s.version,readableSha256:s.sourceSha256,compact:'compact-1.txt',compactSha256:sha(compact),frames:freeze.horizon,pointsPerFrame:pointCount,totalPointsPerSource:pointCount*freeze.horizon,length,maxGeometryError,maxMotion,minInFrame,minCenterDistance,minOuterRadius,maxOuterRadius,...(s.brief==='B02'?{maxRootError}:{}),pass:true};
  results.push(result);console.log(JSON.stringify(result));
}
fs.writeFileSync(path.join(here,'verification.json'),JSON.stringify({protocolSha256:freeze.protocolSha256,independentExecution:'Node vm; exact readable and compact source; original point ordering',results},null,2)+'\n');
