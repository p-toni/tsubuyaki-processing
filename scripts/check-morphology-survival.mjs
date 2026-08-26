#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const [expandedPath,golfedPath,contractPath,...args]=process.argv.slice(2);
let maskThreshold=16,contrastThreshold=18;
for(const a of args){
  if(a.startsWith('--mask-threshold=')) maskThreshold=+a.split('=')[1];
  else if(a.startsWith('--contrast-threshold=')) contrastThreshold=+a.split('=')[1];
}
if(!expandedPath||!golfedPath||!contractPath){
  console.error('Usage: node scripts/check-morphology-survival.mjs expanded.png golfed.png morphology.json [--mask-threshold=16] [--contrast-threshold=18]');
  process.exit(2);
}

const SIG=Buffer.from([137,80,78,71,13,10,26,10]);
const paeth=(a,b,c)=>{let p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c};
function decodePNG(file){
  try{
    const b=fs.readFileSync(file);
    if(!b.subarray(0,8).equals(SIG)) throw new Error('not a PNG');
    let p=8,w,h,depth,type,interlace,idat=[];
    while(p<b.length){
      const n=b.readUInt32BE(p),t=b.toString('ascii',p+4,p+8),d=b.subarray(p+8,p+8+n);p+=12+n;
      if(t==='IHDR'){w=d.readUInt32BE(0);h=d.readUInt32BE(4);depth=d[8];type=d[9];interlace=d[12]}
      else if(t==='IDAT') idat.push(d); else if(t==='IEND') break;
    }
    if(depth!==8||interlace!==0||![0,2,4,6].includes(type)) throw new Error('supports non-interlaced 8-bit grayscale/RGB/RGBA PNGs only');
    const ch={0:1,2:3,4:2,6:4}[type],stride=w*ch,raw=zlib.inflateSync(Buffer.concat(idat)),rows=[];
    let o=0,prev=Buffer.alloc(stride);
    for(let y=0;y<h;y++){
      const f=raw[o++],src=raw.subarray(o,o+stride),row=Buffer.alloc(stride);o+=stride;
      for(let x=0;x<stride;x++){
        const A=x>=ch?row[x-ch]:0,C=prev[x]||0,U=x>=ch?prev[x-ch]:0;
        const pred=f===0?0:f===1?A:f===2?C:f===3?Math.floor((A+C)/2):f===4?paeth(A,C,U):NaN;
        if(Number.isNaN(pred)) throw new Error(`unsupported PNG filter ${f}`);
        row[x]=(src[x]+pred)&255;
      }
      rows.push(row);prev=row;
    }
    const rgba=new Uint8Array(w*h*4);
    for(let y=0;y<h;y++)for(let x=0;x<w;x++){
      const s=x*ch,d=(y*w+x)*4,r=rows[y];
      if(type===0)rgba.set([r[s],r[s],r[s],255],d);
      if(type===2)rgba.set([r[s],r[s+1],r[s+2],255],d);
      if(type===4)rgba.set([r[s],r[s],r[s],r[s+1]],d);
      if(type===6)rgba.set([r[s],r[s+1],r[s+2],r[s+3]],d);
    }
    return {w,h,rgba};
  }catch(e){throw new Error(`${file}: ${e.message}`)}
}
const lum=(r,g,b)=>.2126*r+.7152*g+.0722*b;
const sameSize=(a,b,label)=>{if(a.w!==b.w||a.h!==b.h)throw new Error(`${label}: image dimensions ${b.w}x${b.h} do not match ${a.w}x${a.h}`)};
function estimateBackground(im){
  const {w,h,rgba}=im,n=Math.max(2,Math.floor(Math.min(w,h)*.03)),vals=[];
  for(const [x0,y0] of [[0,0],[w-n,0],[0,h-n],[w-n,h-n]])for(let y=y0;y<y0+n;y++)for(let x=x0;x<x0+n;x++){
    const i=(y*w+x)*4,a=rgba[i+3]/255;vals.push(lum(rgba[i],rgba[i+1],rgba[i+2])*a+255*(1-a));
  }
  vals.sort((a,b)=>a-b);return vals[Math.floor(vals.length/2)];
}
function featureStats(im,mask,bg){
  let pixels=0,energy=0,visible=0;
  for(let p=0;p<mask.length;p++)if(mask[p]){
    pixels++;const i=p*4,a=im.rgba[i+3]/255,L=lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a+bg*(1-a),d=Math.abs(L-bg);
    energy+=d;if(d>=contrastThreshold)visible++;
  }
  return {maskPixels:pixels,contrastEnergy:+energy.toFixed(1),meanContrast:pixels?+(energy/pixels).toFixed(3):0,visibleFraction:pixels?+(visible/pixels).toFixed(4):0};
}

try{
  const expanded=decodePNG(expandedPath),golfed=decodePNG(golfedPath);sameSize(expanded,golfed,golfedPath);
  const contract=JSON.parse(fs.readFileSync(contractPath,'utf8')),features=contract.survivalFeatures||{};
  if(!Object.keys(features).length) throw new Error(`${contractPath}: no survivalFeatures declared`);
  const dir=path.dirname(contractPath),n=expanded.w*expanded.h,bgExpanded=estimateBackground(expanded),bgGolfed=estimateBackground(golfed),out={};
  for(const [name,f] of Object.entries(features)){
    if(!['presence','void'].includes(f.kind)) throw new Error(`${contractPath}: survival feature '${name}' has invalid kind '${f.kind}'`);
    if(!f.mask) throw new Error(`${contractPath}: survival feature '${name}' is missing mask`);
    const maskIm=decodePNG(path.resolve(dir,f.mask));sameSize(expanded,maskIm,f.mask);
    const mask=new Uint8Array(n);
    for(let p=0;p<n;p++){const i=p*4,a=maskIm.rgba[i+3]/255;if(lum(maskIm.rgba[i],maskIm.rgba[i+1],maskIm.rgba[i+2])*a>=maskThreshold)mask[p]=1}
    const E=featureStats(expanded,mask,bgExpanded),G=featureStats(golfed,mask,bgGolfed);
    const result={kind:f.kind,expanded:E,golfed:G};
    if(f.kind==='presence'){
      result.energyRetention=E.contrastEnergy?+(G.contrastEnergy/E.contrastEnergy).toFixed(4):null;
      result.visibleFractionDelta=+(G.visibleFraction-E.visibleFraction).toFixed(4);
      result.interpretation='Presence features should retain enough contrast/coverage to remain legible after golf; compare features rather than applying a universal retention threshold.';
    }else{
      result.voidFillDelta=+(G.visibleFraction-E.visibleFraction).toFixed(4);
      result.contrastDelta=+(G.meanContrast-E.meanContrast).toFixed(3);
      result.interpretation='For void features, positive deltas mean the golfed phenotype filled an intended negative-space feature.';
    }
    out[name]=result;
  }
  console.log(JSON.stringify({expanded:expandedPath,golfed:golfedPath,thresholds:{mask:maskThreshold,contrast:contrastThreshold},features:out,interpretation:'Morphology survival is feature-wise, not one pixel-similarity score. A golfed result may move/deform while still preserving its defining regions and voids.'},null,2));
}catch(e){console.error(e.message);process.exit(2)}