#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const [basePath,variantPath,contractPath,controlName,...args]=process.argv.slice(2);
let diffThreshold=18,maskThreshold=16;
for(const a of args){
  if(a.startsWith('--threshold=')) diffThreshold=+a.split('=')[1];
  if(a.startsWith('--mask-threshold=')) maskThreshold=+a.split('=')[1];
}
if(!basePath||!variantPath||!contractPath||!controlName){
  console.error('Usage: node scripts/check-control-scope.mjs baseline.png variant.png morphology.json controlName [--threshold=18] [--mask-threshold=16]');
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
        const a=x>=ch?row[x-ch]:0,c=prev[x]||0,ul=x>=ch?prev[x-ch]:0;
        const pred=f===0?0:f===1?a:f===2?c:f===3?Math.floor((a+c)/2):f===4?paeth(a,c,ul):NaN;
        if(Number.isNaN(pred)) throw new Error(`unsupported PNG filter ${f}`);
        row[x]=(src[x]+pred)&255;
      }
      rows.push(row);prev=row;
    }
    const rgba=new Uint8Array(w*h*4);
    for(let y=0;y<h;y++) for(let x=0;x<w;x++){
      const s=x*ch,d=(y*w+x)*4,r=rows[y];
      if(type===0) rgba.set([r[s],r[s],r[s],255],d);
      if(type===2) rgba.set([r[s],r[s+1],r[s+2],255],d);
      if(type===4) rgba.set([r[s],r[s],r[s],r[s+1]],d);
      if(type===6) rgba.set([r[s],r[s+1],r[s+2],r[s+3]],d);
    }
    return {w,h,rgba};
  }catch(e){throw new Error(`${file}: ${e.message}`)}
}
const lum=(r,g,b)=>.2126*r+.7152*g+.0722*b;
const sameSize=(a,b,label)=>{if(a.w!==b.w||a.h!==b.h)throw new Error(`${label}: image dimensions ${b.w}x${b.h} do not match ${a.w}x${a.h}`)};

try{
  const contract=JSON.parse(fs.readFileSync(contractPath,'utf8'));
  const control=contract.controls?.[controlName];
  if(!control) throw new Error(`${contractPath}: unknown control '${controlName}'`);
  if(!['region','subtree','surface','global'].includes(control.scope)) throw new Error(`${contractPath}: control '${controlName}' has invalid scope '${control.scope}'`);
  if(control.scope!=='global'&&!contract.regions?.[control.region]) throw new Error(`${contractPath}: control '${controlName}' references unknown region '${control.region}'`);

  const base=decodePNG(basePath),variant=decodePNG(variantPath);sameSize(base,variant,variantPath);
  const n=base.w*base.h,contractDir=path.dirname(contractPath),regionMasks={};
  for(const [name,r] of Object.entries(contract.regions||{})){
    if(!r.mask) throw new Error(`${contractPath}: region '${name}' is missing mask`);
    const file=path.resolve(contractDir,r.mask),im=decodePNG(file);sameSize(base,im,file);
    const mask=new Uint8Array(n);
    for(let p=0;p<n;p++){
      const i=p*4,a=im.rgba[i+3]/255,L=lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a;
      if(L>=maskThreshold) mask[p]=1;
    }
    regionMasks[name]=mask;
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
  for(const r of allowedRegions) for(let p=0;p<n;p++) if(regionMasks[r]?.[p]) allowed[p]=1;

  let totalEnergy=0,allowedEnergy=0,changed=0,allowedChanged=0;
  const regionEnergy=Object.fromEntries(Object.keys(regionMasks).map(r=>[r,0]));
  for(let p=0;p<n;p++){
    const i=p*4,d=Math.abs(lum(base.rgba[i],base.rgba[i+1],base.rgba[i+2])-lum(variant.rgba[i],variant.rgba[i+1],variant.rgba[i+2]));
    totalEnergy+=d;if(allowed[p])allowedEnergy+=d;
    for(const [r,m] of Object.entries(regionMasks))if(m[p])regionEnergy[r]+=d;
    if(d>=diffThreshold){changed++;if(allowed[p])allowedChanged++}
  }
  const spillEnergy=totalEnergy-allowedEnergy,spillRatio=totalEnergy?spillEnergy/totalEnergy:0;
  const result={
    control:controlName,
    declared:{region:control.region??null,scope:control.scope,allowedRegions},
    thresholds:{difference:diffThreshold,mask:maskThreshold},
    changedFraction:+(changed/n).toFixed(4),
    allowedChangedFractionOfChanged:changed?+(allowedChanged/changed).toFixed(4):1,
    totalDifferenceEnergy:+totalEnergy.toFixed(1),
    allowedDifferenceEnergy:+allowedEnergy.toFixed(1),
    unexpectedSpillEnergy:+spillEnergy.toFixed(1),
    spillRatio:+spillRatio.toFixed(4),
    regionEnergyFractions:Object.fromEntries(Object.entries(regionEnergy).map(([r,e])=>[r,totalEnergy?+(e/totalEnergy).toFixed(4):0])),
    interpretation:control.scope==='global'
      ?'Global scope permits organism-wide influence; spill is not meaningful beyond declared masks.'
      :'Lower spill means the observed change is better contained inside the declared region/subtree. Region masks may overlap, so per-region fractions need not sum to 1. Treat thresholds as project-calibrated diagnostics, not universal aesthetic laws.'
  };
  console.log(JSON.stringify(result,null,2));
}catch(e){console.error(e.message);process.exit(2)}