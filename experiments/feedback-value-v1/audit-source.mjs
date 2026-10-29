// Verify trusted archived sketches, not untrusted JavaScript or aesthetic quality.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const here=path.dirname(fileURLToPath(import.meta.url));
const [readableArg,compactArg,outArg]=process.argv.slice(2);
const readable=path.resolve(readableArg),compact=compactArg==='-'?null:path.resolve(compactArg);
const freeze=JSON.parse(fs.readFileSync(path.join(here,'freeze.json')));
const sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
assert.equal(sha(path.join(here,'protocol.md')),freeze.protocolSha256);
const brief=path.relative(here,readable).split(path.sep)[0];
const math=Object.fromEntries(Object.getOwnPropertyNames(Math).map(k=>[k,Math[k]]));
const call=new vm.Script('draw()');
function runner(file){
  let points=[],canvas,background,weight=1,color=[0,0,0,255];
  const ctx=vm.createContext({...math,TAU:2*Math.PI,frameCount:0,
    createCanvas:(w,h)=>{canvas=[w,h];},
    background:(...v)=>{background=v;},strokeWeight:v=>{weight=v;},
    stroke:(...v)=>{color=v.length<=2?[v[0],v[0],v[0],v[1]??255]:[...v.slice(0,3),v[3]??255];},
    point:(x,y)=>{const p=[x,y,weight,...color];assert.ok(p.every(Number.isFinite),'Nonfinite geometry/style');points.push(...p);}
  });
  vm.runInContext(fs.readFileSync(file,'utf8'),ctx);
  if(typeof ctx.setup==='function')vm.runInContext('setup()',ctx);
  return frame=>{points=[];ctx.frameCount=frame;call.runInContext(ctx,{timeout:10000});return {points,canvas,background};};
}
const original=runner(readable),post=compact?runner(compact):null;
let previous=null,count=null,maxMotion=0,minInFrame=1,maxGeometryError=0,maxStyleError=0,resets=0,minCenterDistance=Infinity;
const start=performance.now();
for(let f=1;f<=freeze.horizon;f++){
  const a=original(f),b=post?post(f):a;
  assert.deepEqual(a.canvas,[400,400]);assert.deepEqual(b.canvas,a.canvas);assert.deepEqual(b.background,a.background);
  assert.equal(a.points.length,b.points.length);
  count??=b.points.length/7;assert.equal(b.points.length,count*7);
  let inside=0;
  for(let j=0;j<b.points.length;j+=7){
    const x=b.points[j],y=b.points[j+1];
    maxGeometryError=Math.max(maxGeometryError,Math.abs(x-a.points[j]),Math.abs(y-a.points[j+1]));
    for(let k=2;k<7;k++)maxStyleError=Math.max(maxStyleError,Math.abs(b.points[j+k]-a.points[j+k]));
    if(previous){
      let dx=x-previous[j];const dy=y-previous[j+1];
      if(brief==='F06'&&((previous[j]>395&&x<5)||(previous[j]<5&&x>395))){dx-=Math.sign(dx)*400;resets++;}
      maxMotion=Math.max(maxMotion,Math.hypot(dx,dy));
    }
    inside+=x>=0&&x<=400&&y>=0&&y<=400;
    minCenterDistance=Math.min(minCenterDistance,Math.hypot(x-200,y-200));
  }
  minInFrame=Math.min(minInFrame,inside/count);previous=b.points;
}
let length=null;
if(compact){
  const result=spawnSync(process.execPath,[path.join(here,'../autonomous-discovery-pilot-v1/check-length.mjs'),compact],{encoding:'utf8'});
  assert.ok(result.status===0||result.status===1,result.stderr);length=JSON.parse(result.stdout);
}
const result={brief,readable:path.relative(here,readable),readableSha256:sha(readable),compact:compact?path.relative(here,compact):null,
  compactSha256:compact?sha(compact):null,protocolSha256:freeze.protocolSha256,frames:freeze.horizon,pointsPerFrame:count,
  pointCalls:count*freeze.horizon*(post?2:1),minInFrame,maxMotion,horizontalResets:resets,minCenterDistance,
  maxGeometryError,maxStyleError,length,executionSeconds:(performance.now()-start)/1000,
  pass:minInFrame>=.95&&maxMotion<=10&&maxGeometryError<=1e-7&&maxStyleError<=1e-7&&(!length||length.pass),
  claim:'Exact-source geometry and drawing-style check; not an artistic or brief-adherence judgment.'};
fs.writeFileSync(path.resolve(outArg),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
