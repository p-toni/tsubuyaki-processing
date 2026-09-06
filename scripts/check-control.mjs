#!/usr/bin/env node
import {decodePNG} from './png.mjs';

const [basePath,variantPath,...args]=process.argv.slice(2);
let threshold=18,low=.01,high=.99;
for(const a of args){
  if(a.startsWith('--threshold=')) threshold=+a.split('=')[1];
  if(a.startsWith('--quantiles=')) [low,high]=a.split('=')[1].split(',').map(Number);
}
if(!basePath||!variantPath){
  console.error('Usage: node scripts/check-control.mjs baseline.png variant.png [--threshold=18] [--quantiles=.01,.99]');
  process.exit(2);
}
if(!(low>=0&&high<=1&&low<high)){
  console.error('--quantiles must be two fractions with 0 <= low < high <= 1, e.g. --quantiles=.01,.99');
  process.exit(2);
}

const lum=(r,g,b)=>.2126*r+.7152*g+.0722*b;
const quantile=(hist,total,q)=>{let s=0,target=total*q;for(let i=0;i<hist.length;i++){s+=hist[i];if(s>=target)return i}return hist.length-1};

try{
  const a=decodePNG(basePath),b=decodePNG(variantPath);
  if(a.w!==b.w||a.h!==b.h) throw new Error(`${basePath} vs ${variantPath}: images must have identical dimensions`);
  const {w,h}=a,hx=new Uint32Array(w),hy=new Uint32Array(h);
  let changed=0,sx=0,sy=0,totalDelta=0,maxDelta=0;
  for(let y=0;y<h;y++) for(let x=0;x<w;x++){
    const i=(y*w+x)*4;
    const La=lum(a.rgba[i],a.rgba[i+1],a.rgba[i+2]),Lb=lum(b.rgba[i],b.rgba[i+1],b.rgba[i+2]);
    const d=Math.abs(La-Lb);
    totalDelta+=d;maxDelta=Math.max(maxDelta,d);
    if(d<threshold) continue;
    changed++;sx+=x;sy+=y;hx[x]++;hy[y]++;
  }
  const out={baseline:basePath,variant:variantPath,width:w,height:h,threshold,quantiles:[low,high],changedPixels:changed,changedFraction:+(changed/(w*h)).toFixed(4),meanLumaDelta:+(totalDelta/(w*h)).toFixed(3),maxLumaDelta:+maxDelta.toFixed(1)};
  if(changed){
    const x0=quantile(hx,changed,low),x1=quantile(hx,changed,high),y0=quantile(hy,changed,low),y1=quantile(hy,changed,high);
    out.robustDifferenceBBox={x:x0,y:y0,width:x1-x0+1,height:y1-y0+1,widthRatio:+((x1-x0+1)/w).toFixed(3),heightRatio:+((y1-y0+1)/h).toFixed(3)};
    out.differenceCentroid={x:+(sx/changed).toFixed(1),y:+(sy/changed).toFixed(1)};
  }
  out.interpretation='Diagnostic only. Global diff size/centroid cannot verify semantic control locality in hierarchical morphology; use visual review until scope-aware validation is available.';
  console.log(JSON.stringify(out,null,2));
}catch(e){console.error(e.message);process.exit(2)}