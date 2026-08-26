#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const [basePath,variantPath,contractPath,controlName,...args]=process.argv.slice(2);
let maskThreshold=16,contrastThreshold=18,baselineMaskDir=null,variantMaskDir=null;
for(const a of args){
  if(a.startsWith('--mask-threshold='))maskThreshold=+a.split('=')[1];
  else if(a.startsWith('--contrast-threshold='))contrastThreshold=+a.split('=')[1];
  else if(a.startsWith('--baseline-mask-dir='))baselineMaskDir=a.slice(a.indexOf('=')+1);
  else if(a.startsWith('--variant-mask-dir='))variantMaskDir=a.slice(a.indexOf('=')+1);
}
if(!basePath||!variantPath||!contractPath||!controlName||!baselineMaskDir||!variantMaskDir){
  console.error('Usage: node scripts/check-control-effect.mjs baseline.png variant.png morphology.json controlName --baseline-mask-dir=DIR --variant-mask-dir=DIR [--mask-threshold=16] [--contrast-threshold=18]');
  process.exit(2);
}
const SIG=Buffer.from([137,80,78,71,13,10,26,10]);
const paeth=(a,b,c)=>{let p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c};
function decodePNG(file){try{const b=fs.readFileSync(file);if(!b.subarray(0,8).equals(SIG))throw new Error('not a PNG');let p=8,w,h,depth,type,interlace,idat=[];while(p<b.length){const n=b.readUInt32BE(p),t=b.toString('ascii',p+4,p+8),d=b.subarray(p+8,p+8+n);p+=12+n;if(t==='IHDR'){w=d.readUInt32BE(0);h=d.readUInt32BE(4);depth=d[8];type=d[9];interlace=d[12]}else if(t==='IDAT')idat.push(d);else if(t==='IEND')break}if(depth!==8||interlace!==0||![0,2,4,6].includes(type))throw new Error('supports non-interlaced 8-bit grayscale/RGB/RGBA PNGs only');const ch={0:1,2:3,4:2,6:4}[type],stride=w*ch,raw=zlib.inflateSync(Buffer.concat(idat)),rows=[];let o=0,prev=Buffer.alloc(stride);for(let y=0;y<h;y++){const f=raw[o++],src=raw.subarray(o,o+stride),row=Buffer.alloc(stride);o+=stride;for(let x=0;x<stride;x++){const A=x>=ch?row[x-ch]:0,C=prev[x]||0,U=x>=ch?prev[x-ch]:0,pred=f===0?0:f===1?A:f===2?C:f===3?Math.floor((A+C)/2):f===4?paeth(A,C,U):NaN;if(Number.isNaN(pred))throw new Error(`unsupported PNG filter ${f}`);row[x]=(src[x]+pred)&255}rows.push(row);prev=row}const rgba=new Uint8Array(w*h*4);for(let y=0;y<h;y++)for(let x=0;x<w;x++){const s=x*ch,d=(y*w+x)*4,r=rows[y];if(type===0)rgba.set([r[s],r[s],r[s],255],d);if(type===2)rgba.set([r[s],r[s+1],r[s+2],255],d);if(type===4)rgba.set([r[s],r[s],r[s],r[s+1]],d);if(type===6)rgba.set([r[s],r[s+1],r[s+2],r[s+3]],d)}return{w,h,rgba}}catch(e){throw new Error(`${file}: ${e.message}`)}}
const lum=(r,g,b)=>.2126*r+.7152*g+.0722*b;
const same=(a,b,label)=>{if(a.w!==b.w||a.h!==b.h)throw new Error(`${label}: image dimensions mismatch`)};
function bg(im){const n=Math.max(2,Math.floor(Math.min(im.w,im.h)*.03)),v=[];for(const[x0,y0]of[[0,0],[im.w-n,0],[0,im.h-n],[im.w-n,im.h-n]])for(let y=y0;y<y0+n;y++)for(let x=x0;x<x0+n;x++){const i=(y*im.w+x)*4,a=im.rgba[i+3]/255;v.push(lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a+255*(1-a))}v.sort((a,b)=>a-b);return v[Math.floor(v.length/2)]}
function makeMask(im){const m=new Uint8Array(im.w*im.h);for(let p=0;p<m.length;p++){const i=p*4,a=im.rgba[i+3]/255;if(lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a>=maskThreshold)m[p]=1}return m}
function stats(im,mask){let minX=im.w,minY=im.h,maxX=-1,maxY=-1,n=0,sx=0,sy=0,vis=0,energy=0,B=bg(im);for(let p=0;p<mask.length;p++)if(mask[p]){const x=p%im.w,y=Math.floor(p/im.w),i=p*4,a=im.rgba[i+3]/255,L=lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a+B*(1-a),d=Math.abs(L-B);n++;sx+=x;sy+=y;energy+=d;if(d>=contrastThreshold)vis++;if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y}return{area:n,width:n?maxX-minX+1:0,height:n?maxY-minY+1:0,centroidX:n?sx/n:0,centroidY:n?sy/n:0,visibleFraction:n?vis/n:0,meanContrast:n?energy/n:0}}
function value(s,metric){if(!(metric in s))throw new Error(`unsupported effect metric '${metric}'`);return s[metric]}
try{
  const contract=JSON.parse(fs.readFileSync(contractPath,'utf8')),control=contract.controls?.[controlName];if(!control)throw new Error(`${contractPath}: unknown control '${controlName}'`);if(!control.effect)throw new Error(`${contractPath}: control '${controlName}' has no effect descriptor`);
  const {source='mask',metric,direction='any',minRelativeChange=0}=control.effect;if(!['mask','image'].includes(source))throw new Error(`${contractPath}: invalid effect source '${source}'`);if(!['increase','decrease','any'].includes(direction))throw new Error(`${contractPath}: invalid effect direction '${direction}'`);
  const region=control.region;if(!region||!contract.regions?.[region])throw new Error(`${contractPath}: effect validation requires a known control region`);
  const base=decodePNG(basePath),variant=decodePNG(variantPath);same(base,variant,variantPath);const rel=path.basename(contract.regions[region].mask),bm=decodePNG(path.resolve(baselineMaskDir,rel)),vm=decodePNG(path.resolve(variantMaskDir,rel));same(base,bm,rel);same(base,vm,rel);const bs=stats(base,makeMask(bm)),vs=stats(variant,makeMask(vm)),b=value(bs,metric),v=value(vs,metric),delta=v-b,relative=b?delta/Math.abs(b):null;
  const signOk=direction==='any'||(direction==='increase'&&delta>0)||(direction==='decrease'&&delta<0),strengthOk=minRelativeChange<=0||(relative!==null&&Math.abs(relative)>=minRelativeChange),pass=signOk&&strengthOk;
  console.log(JSON.stringify({control:controlName,declared:{region,source,metric,direction,minRelativeChange},baseline:{value:+b.toFixed(4),stats:bs},variant:{value:+v.toFixed(4),stats:vs},delta:+delta.toFixed(4),relativeChange:relative===null?null:+relative.toFixed(4),checks:{direction:signOk,strength:strengthOk},pass,interpretation:'This validates the declared observable effect, not scope. Run check-control-scope.mjs separately to validate where the change occurred.'},null,2));
}catch(e){console.error(e.message);process.exit(2)}