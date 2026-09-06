#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {decodePNG} from './png.mjs';

const [basePath,variantPath,contractPath,controlName,...args]=process.argv.slice(2);
let diffThreshold=18,maskThreshold=16,dilate=0,baselineMaskDir=null,variantMaskDir=null;
for(const a of args){
  if(a.startsWith('--threshold=')) diffThreshold=+a.split('=')[1];
  else if(a.startsWith('--mask-threshold=')) maskThreshold=+a.split('=')[1];
  else if(a.startsWith('--dilate=')) dilate=+a.split('=')[1];
  else if(a.startsWith('--baseline-mask-dir=')) baselineMaskDir=a.slice(a.indexOf('=')+1);
  else if(a.startsWith('--variant-mask-dir=')) variantMaskDir=a.slice(a.indexOf('=')+1);
}
if(!basePath||!variantPath||!contractPath||!controlName){
  console.error('Usage: node scripts/check-control-scope.mjs baseline.png variant.png morphology.json controlName [--baseline-mask-dir=DIR] [--variant-mask-dir=DIR] [--dilate=0] [--threshold=18] [--mask-threshold=16]');
  process.exit(2);
}
if(!Number.isInteger(dilate)||dilate<0||dilate>32){console.error('--dilate must be an integer from 0 to 32');process.exit(2)}
if(variantMaskDir&&!baselineMaskDir){console.error('--variant-mask-dir requires --baseline-mask-dir');process.exit(2)}

const lum=(r,g,b)=>.2126*r+.7152*g+.0722*b;
const sameSize=(a,b,label)=>{if(a.w!==b.w||a.h!==b.h)throw new Error(`${label}: image dimensions ${b.w}x${b.h} do not match ${a.w}x${a.h}`)};
const toMask=(im,threshold)=>{const n=im.w*im.h,m=new Uint8Array(n);for(let p=0;p<n;p++){const i=p*4,a=im.rgba[i+3]/255;if(lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a>=threshold)m[p]=1}return m};
const count=m=>{let n=0;for(const v of m)n+=v;return n};
function dilateMask(src,w,h,r){
  if(!r)return src;
  const dst=new Uint8Array(src.length),rr=r*r;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(src[y*w+x]){
    for(let dy=-r;dy<=r;dy++)for(let dx=-r;dx<=r;dx++)if(dx*dx+dy*dy<=rr){const X=x+dx,Y=y+dy;if(X>=0&&X<w&&Y>=0&&Y<h)dst[Y*w+X]=1}
  }
  return dst;
}

try{
  const contract=JSON.parse(fs.readFileSync(contractPath,'utf8'));
  const control=contract.controls?.[controlName];
  if(!control) throw new Error(`${contractPath}: unknown control '${controlName}'`);
  if(!['region','subtree','surface','global'].includes(control.scope)) throw new Error(`${contractPath}: control '${controlName}' has invalid scope '${control.scope}'`);
  if(control.scope!=='global'&&!contract.regions?.[control.region]) throw new Error(`${contractPath}: control '${controlName}' references unknown region '${control.region}'`);

  const base=decodePNG(basePath),variant=decodePNG(variantPath);sameSize(base,variant,variantPath);
  const n=base.w*base.h,contractDir=path.dirname(contractPath),regionMasks={},regionSupport={};
  const maskMode=baselineMaskDir?(variantMaskDir?'dual-state':'baseline-override'):'contract-static';
  for(const [name,r] of Object.entries(contract.regions||{})){
    if(!r.mask) throw new Error(`${contractPath}: region '${name}' is missing mask`);
    const relative=path.basename(r.mask);
    const baseFile=baselineMaskDir?path.resolve(baselineMaskDir,relative):path.resolve(contractDir,r.mask);
    const variantFile=variantMaskDir?path.resolve(variantMaskDir,relative):baseFile;
    const bm=decodePNG(baseFile),vm=decodePNG(variantFile);sameSize(base,bm,baseFile);sameSize(base,vm,variantFile);
    const bmask=toMask(bm,maskThreshold),vmask=toMask(vm,maskThreshold),union=new Uint8Array(n);
    for(let p=0;p<n;p++)union[p]=bmask[p]||vmask[p]?1:0;
    regionMasks[name]=dilateMask(union,base.w,base.h,dilate);
    regionSupport[name]={baselinePixels:count(bmask),variantPixels:count(vmask),unionPixels:count(union),allowedPixelsAfterDilation:count(regionMasks[name])};
  }

  const descendants=name=>{
    const out=[name],q=[name];
    while(q.length){const p=q.shift();for(const [n,r] of Object.entries(contract.regions||{}))if(r.parent===p&&!out.includes(n)){out.push(n);q.push(n)}}
    return out;
  };
  let allowedRegions=[];
  if(control.scope==='global') allowedRegions=Object.keys(regionMasks);
  else if(control.scope==='subtree') allowedRegions=descendants(control.region);
  else allowedRegions=[control.region];

  const allowed=new Uint8Array(n);
  for(const r of allowedRegions)for(let p=0;p<n;p++)if(regionMasks[r]?.[p])allowed[p]=1;

  let totalEnergy=0,allowedEnergy=0,changed=0,allowedChanged=0;
  const regionEnergy=Object.fromEntries(Object.keys(regionMasks).map(r=>[r,0]));
  for(let p=0;p<n;p++){
    const i=p*4,d=Math.abs(lum(base.rgba[i],base.rgba[i+1],base.rgba[i+2])-lum(variant.rgba[i],variant.rgba[i+1],variant.rgba[i+2]));
    totalEnergy+=d;if(allowed[p])allowedEnergy+=d;
    for(const [r,m] of Object.entries(regionMasks))if(m[p])regionEnergy[r]+=d;
    if(d>=diffThreshold){changed++;if(allowed[p])allowedChanged++}
  }
  const spillEnergy=totalEnergy-allowedEnergy,spillRatio=totalEnergy?spillEnergy/totalEnergy:0;
  const warnings=[];
  if(maskMode!=='dual-state'&&control.scope!=='global')warnings.push('Static/baseline-only masks can overestimate spill for geometry controls that move a region. Prefer both --baseline-mask-dir and --variant-mask-dir.');
  const result={
    control:controlName,
    declared:{region:control.region??null,scope:control.scope,allowedRegions},
    maskSupport:{mode:maskMode,baselineMaskDir,variantMaskDir,dilate,regions:regionSupport},
    thresholds:{difference:diffThreshold,mask:maskThreshold},
    changedFraction:+(changed/n).toFixed(4),
    allowedChangedFractionOfChanged:changed?+(allowedChanged/changed).toFixed(4):1,
    totalDifferenceEnergy:+totalEnergy.toFixed(1),
    allowedDifferenceEnergy:+allowedEnergy.toFixed(1),
    unexpectedSpillEnergy:+spillEnergy.toFixed(1),
    spillRatio:+spillRatio.toFixed(4),
    regionEnergyFractions:Object.fromEntries(Object.entries(regionEnergy).map(([r,e])=>[r,totalEnergy?+(e/totalEnergy).toFixed(4):0])),
    warnings,
    interpretation:control.scope==='global'
      ?'Global scope permits organism-wide influence; spill is not meaningful beyond declared masks.'
      :'For moving geometry, allowed support is the union of baseline and variant region masks. Lower spill means change is better contained inside the declared region/subtree. Optional dilation is only a tolerance for raster/attachment boundaries; do not use it to hide real leakage.'
  };
  console.log(JSON.stringify(result,null,2));
}catch(e){console.error(e.message);process.exit(2)}