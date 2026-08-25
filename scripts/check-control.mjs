#!/usr/bin/env node
import fs from 'node:fs';
import zlib from 'node:zlib';

const [basePath,variantPath,...args]=process.argv.slice(2);
let threshold=18,low=.01,high=.99;
for(const a of args){
  if(a.startsWith('--threshold=')) threshold=+a.split('=')[1];
  if(a.startsWith('--quantiles=')) [low,high]=a.split('=')[1].split(',').map(Number);
}
if(!basePath||!variantPath){
  console.error('Usage: node scripts/check-control.mjs baseline.png variant.png [--threshold=18]');
  process.exit(2);
}

const SIG=Buffer.from([137,80,78,71,13,10,26,10]);
const paeth=(a,b,c)=>{let p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c};

function decodePNG(path){
  const b=fs.readFileSync(path);
  if(!b.subarray(0,8).equals(SIG)) throw new Error(`${path}: not a PNG`);
  let p=8,w,h,depth,type,interlace,idat=[];
  while(p<b.length){
    const n=b.readUInt32BE(p),t=b.toString('ascii',p+4,p+8),d=b.subarray(p+8,p+8+n);p+=12+n;
    if(t==='IHDR'){w=d.readUInt32BE(0);h=d.readUInt32BE(4);depth=d[8];type=d[9];interlace=d[12]}
    else if(t==='IDAT') idat.push(d);
    else if(t==='IEND') break;
  }
  if(depth!==8||interlace!==0||![0,2,4,6].includes(type)) throw new Error(`${path}: supports non-interlaced 8-bit grayscale/RGB/RGBA PNGs only`);
  const channels={0:1,2:3,4:2,6:4}[type],stride=w*channels,raw=zlib.inflateSync(Buffer.concat(idat)),rows=[];
  let o=0,prev=Buffer.alloc(stride);
  for(let y=0;y<h;y++){
    const f=raw[o++],src=raw.subarray(o,o+stride),row=Buffer.alloc(stride);o+=stride;
    for(let x=0;x<stride;x++){
      const a=x>=channels?row[x-channels]:0,c=prev[x]||0,ul=x>=channels?prev[x-channels]:0;
      const pred=f===0?0:f===1?a:f===2?c:f===3?Math.floor((a+c)/2):f===4?paeth(a,c,ul):NaN;
      if(Number.isNaN(pred)) throw new Error(`${path}: unsupported PNG filter ${f}`);
      row[x]=(src[x]+pred)&255;
    }
    rows.push(row);prev=row;
  }
  const rgba=new Uint8Array(w*h*4);
  for(let y=0;y<h;y++) for(let x=0;x<w;x++){
    const s=x*channels,d=(y*w+x)*4,r=rows[y];
    if(type===0) rgba.set([r[s],r[s],r[s],255],d);
    if(type===2) rgba.set([r[s],r[s+1],r[s+2],255],d);
    if(type===4) rgba.set([r[s],r[s],r[s],r[s+1]],d);
    if(type===6) rgba.set([r[s],r[s+1],r[s+2],r[s+3]],d);
  }
  return {w,h,rgba};
}

const lum=(r,g,b)=>.2126*r+.7152*g+.0722*b;
const quantile=(hist,total,q)=>{let s=0,target=total*q;for(let i=0;i<hist.length;i++){s+=hist[i];if(s>=target)return i}return hist.length-1};

try{
  const a=decodePNG(basePath),b=decodePNG(variantPath);
  if(a.w!==b.w||a.h!==b.h) throw new Error('Images must have identical dimensions');
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
  const out={baseline:basePath,variant:variantPath,width:w,height:h,threshold,changedPixels:changed,changedFraction:+(changed/(w*h)).toFixed(4),meanLumaDelta:+(totalDelta/(w*h)).toFixed(3),maxLumaDelta:+maxDelta.toFixed(1)};
  if(changed){
    const x0=quantile(hx,changed,low),x1=quantile(hx,changed,high),y0=quantile(hy,changed,low),y1=quantile(hy,changed,high);
    out.robustDifferenceBBox={x:x0,y:y0,width:x1-x0+1,height:y1-y0+1,widthRatio:+((x1-x0+1)/w).toFixed(3),heightRatio:+((y1-y0+1)/h).toFixed(3),quantiles:[low,high]};
    out.differenceCentroid={x:+(sx/changed).toFixed(1),y:+(sy/changed).toFixed(1)};
  }
  out.interpretation='Compare this difference region with the semantic control intent. Locality is desirable for local controls; global controls may legitimately affect most of the frame.';
  console.log(JSON.stringify(out,null,2));
}catch(e){console.error(e.message);process.exit(2)}