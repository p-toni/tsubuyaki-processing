#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const [expandedPath,golfedPath,contractPath,...args]=process.argv.slice(2);
let maskThreshold=16,contrastThreshold=18,expandedFeatureDir=null,golfedFeatureDir=null;
for(const a of args){
  if(a.startsWith('--mask-threshold='))maskThreshold=+a.split('=')[1];
  else if(a.startsWith('--contrast-threshold='))contrastThreshold=+a.split('=')[1];
  else if(a.startsWith('--expanded-feature-dir='))expandedFeatureDir=a.slice(a.indexOf('=')+1);
  else if(a.startsWith('--golfed-feature-dir='))golfedFeatureDir=a.slice(a.indexOf('=')+1);
}
if(!expandedPath||!golfedPath||!contractPath){console.error('Usage: node scripts/check-morphology-survival.mjs expanded.png golfed.png morphology.json [--expanded-feature-dir=DIR --golfed-feature-dir=DIR] [--mask-threshold=16] [--contrast-threshold=18]');process.exit(2)}
if((expandedFeatureDir&&!golfedFeatureDir)||(!expandedFeatureDir&&golfedFeatureDir)){console.error('State-aware mode requires both --expanded-feature-dir and --golfed-feature-dir');process.exit(2)}

const SIG=Buffer.from([137,80,78,71,13,10,26,10]);
const paeth=(a,b,c)=>{let p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c};
function decodePNG(file){try{const b=fs.readFileSync(file);if(!b.subarray(0,8).equals(SIG))throw new Error('not a PNG');let p=8,w,h,depth,type,interlace,idat=[];while(p<b.length){const n=b.readUInt32BE(p),t=b.toString('ascii',p+4,p+8),d=b.subarray(p+8,p+8+n);p+=12+n;if(t==='IHDR'){w=d.readUInt32BE(0);h=d.readUInt32BE(4);depth=d[8];type=d[9];interlace=d[12]}else if(t==='IDAT')idat.push(d);else if(t==='IEND')break}if(depth!==8||interlace!==0||![0,2,4,6].includes(type))throw new Error('supports non-interlaced 8-bit grayscale/RGB/RGBA PNGs only');const ch={0:1,2:3,4:2,6:4}[type],stride=w*ch,raw=zlib.inflateSync(Buffer.concat(idat)),rows=[];let o=0,prev=Buffer.alloc(stride);for(let y=0;y<h;y++){const f=raw[o++],src=raw.subarray(o,o+stride),row=Buffer.alloc(stride);o+=stride;for(let x=0;x<stride;x++){const A=x>=ch?row[x-ch]:0,C=prev[x]||0,U=x>=ch?prev[x-ch]:0,pred=f===0?0:f===1?A:f===2?C:f===3?Math.floor((A+C)/2):f===4?paeth(A,C,U):NaN;if(Number.isNaN(pred))throw new Error(`unsupported PNG filter ${f}`);row[x]=(src[x]+pred)&255}rows.push(row);prev=row}const rgba=new Uint8Array(w*h*4);for(let y=0;y<h;y++)for(let x=0;x<w;x++){const s=x*ch,d=(y*w+x)*4,r=rows[y];if(type===0)rgba.set([r[s],r[s],r[s],255],d);if(type===2)rgba.set([r[s],r[s+1],r[s+2],255],d);if(type===4)rgba.set([r[s],r[s],r[s],r[s+1]],d);if(type===6)rgba.set([r[s],r[s+1],r[s+2],r[s+3]],d)}return{w,h,rgba}}catch(e){throw new Error(`${file}: ${e.message}`)}}
const lum=(r,g,b)=>.2126*r+.7152*g+.0722*b;
const same=(a,b,label)=>{if(a.w!==b.w||a.h!==b.h)throw new Error(`${label}: image dimensions mismatch`)};
function bg(im){const n=Math.max(2,Math.floor(Math.min(im.w,im.h)*.03)),v=[];for(const[x0,y0]of[[0,0],[im.w-n,0],[0,im.h-n],[im.w-n,im.h-n]])for(let y=y0;y<y0+n;y++)for(let x=x0;x<x0+n;x++){const i=(y*im.w+x)*4,a=im.rgba[i+3]/255;v.push(lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a+255*(1-a))}v.sort((a,b)=>a-b);return v[Math.floor(v.length/2)]}
function makeMask(im){const m=new Uint8Array(im.w*im.h);for(let p=0;p<m.length;p++){const i=p*4,a=im.rgba[i+3]/255;if(lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a>=maskThreshold)m[p]=1}return m}
function stats(im,mask){let n=0,minX=im.w,minY=im.h,maxX=-1,maxY=-1,sx=0,sy=0,vis=0,energy=0,B=bg(im);for(let p=0;p<mask.length;p++)if(mask[p]){const x=p%im.w,y=Math.floor(p/im.w),i=p*4,a=im.rgba[i+3]/255,L=lum(im.rgba[i],im.rgba[i+1],im.rgba[i+2])*a+B*(1-a),d=Math.abs(L-B);n++;sx+=x;sy+=y;energy+=d;if(d>=contrastThreshold)vis++;if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y}return{area:n,width:n?maxX-minX+1:0,height:n?maxY-minY+1:0,centroidX:n?sx/n:0,centroidY:n?sy/n:0,meanContrast:n?energy/n:0,visibleFraction:n?vis/n:0}}
const ratio=(a,b)=>a?b/a:null;
try{
  const expanded=decodePNG(expandedPath),golfed=decodePNG(golfedPath);same(expanded,golfed,golfedPath);const contract=JSON.parse(fs.readFileSync(contractPath,'utf8')),features=contract.survivalFeatures||{};if(!Object.keys(features).length)throw new Error(`${contractPath}: no survivalFeatures declared`);const dir=path.dirname(contractPath),stateAware=!!expandedFeatureDir,out={};
  for(const[name,f]of Object.entries(features)){
    if(!['presence','void'].includes(f.kind))throw new Error(`${contractPath}: survival feature '${name}' has invalid kind '${f.kind}'`);if(!f.mask)throw new Error(`${contractPath}: survival feature '${name}' is missing mask`);const rel=path.basename(f.mask),eFile=stateAware?path.resolve(expandedFeatureDir,rel):path.resolve(dir,f.mask),gFile=stateAware?path.resolve(golfedFeatureDir,rel):eFile,eMaskIm=decodePNG(eFile),gMaskIm=decodePNG(gFile);same(expanded,eMaskIm,eFile);same(expanded,gMaskIm,gFile);const E=stats(expanded,makeMask(eMaskIm)),G=stats(golfed,makeMask(gMaskIm)),centroidShift=Math.hypot(G.centroidX-E.centroidX,G.centroidY-E.centroidY)/Math.hypot(expanded.w,expanded.h),r={kind:f.kind,expanded:E,golfed:G,geometry:{areaRatio:ratio(E.area,G.area),widthRatio:ratio(E.width,G.width),heightRatio:ratio(E.height,G.height),centroidShiftNormalized:+centroidShift.toFixed(4)}};
    if(f.kind==='presence'){r.appearance={meanContrastRatio:ratio(E.meanContrast,G.meanContrast),visibleFractionRatio:ratio(E.visibleFraction,G.visibleFraction)};r.interpretation='Presence survival is state-aware: compare each phenotype in its own feature support. Geometry ratios describe whether the feature still exists with similar scale/placement; appearance ratios describe whether it remains visually legible.'}
    else{r.appearance={visibleFractionDelta:+(G.visibleFraction-E.visibleFraction).toFixed(4),meanContrastDelta:+(G.meanContrast-E.meanContrast).toFixed(4)};r.interpretation='For voids, state-aware feature masks follow the intended cavity in each phenotype. Positive appearance deltas mean the golfed cavity became more filled/contrasty.'}
    out[name]=r;
  }
  console.log(JSON.stringify({expanded:expandedPath,golfed:golfedPath,mode:stateAware?'state-aware':'legacy-fixed-mask',thresholds:{mask:maskThreshold,contrast:contrastThreshold},features:out,warnings:stateAware?[]:['Fixed-mask mode can understate survival when golf moves a feature. Prefer both feature-directory arguments for compound morphology.'],interpretation:'Do not collapse survival to one score. Review feature existence/geometry, placement and appearance separately.'},null,2));
}catch(e){console.error(e.message);process.exit(2)}