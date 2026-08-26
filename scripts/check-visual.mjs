#!/usr/bin/env node
import fs from 'node:fs';
import zlib from 'node:zlib';

const files=[];
let threshold=24,edge=.02,low=.01,high=.99;
for(const a of process.argv.slice(2)){
  if(a.startsWith('--threshold=')) threshold=+a.split('=')[1];
  else if(a.startsWith('--edge=')) edge=+a.split('=')[1];
  else if(a.startsWith('--quantiles=')) [low,high]=a.split('=')[1].split(',').map(Number);
  else files.push(a);
}
if(!files.length){
  console.error('Usage: node scripts/check-visual.mjs frame.png [frame2.png ...] [--threshold=24] [--edge=.02] [--quantiles=.01,.99]');
  process.exit(2);
}
if(!(low>=0&&high<=1&&low<high)){
  console.error('--quantiles must be two fractions with 0 <= low < high <= 1, e.g. --quantiles=.01,.99');
  process.exit(2);
}

const SIG=Buffer.from([137,80,78,71,13,10,26,10]);
const paeth=(a,b,c)=>{let p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c};

function decodePNG(path){
  try{
    const b=fs.readFileSync(path);
    if(!b.subarray(0,8).equals(SIG)) throw new Error('not a PNG');
    let p=8,w,h,depth,type,interlace,idat=[];
    while(p<b.length){
      const n=b.readUInt32BE(p),t=b.toString('ascii',p+4,p+8),d=b.subarray(p+8,p+8+n);p+=12+n;
      if(t==='IHDR'){w=d.readUInt32BE(0);h=d.readUInt32BE(4);depth=d[8];type=d[9];interlace=d[12]}
      else if(t==='IDAT') idat.push(d);
      else if(t==='IEND') break;
    }
    if(depth!==8||interlace!==0||![0,2,4,6].includes(type)) throw new Error('supports non-interlaced 8-bit grayscale/RGB/RGBA PNGs only');
    const channels={0:1,2:3,4:2,6:4}[type],stride=w*channels,raw=zlib.inflateSync(Buffer.concat(idat)),rows=[];
    let o=0,prev=Buffer.alloc(stride);
    for(let y=0;y<h;y++){
      const f=raw[o++],src=raw.subarray(o,o+stride),row=Buffer.alloc(stride);o+=stride;
      for(let x=0;x<stride;x++){
        const a=x>=channels?row[x-channels]:0,c=prev[x]||0,ul=x>=channels?prev[x-channels]:0;
        const pred=f===0?0:f===1?a:f===2?c:f===3?Math.floor((a+c)/2):f===4?paeth(a,c,ul):NaN;
        if(Number.isNaN(pred)) throw new Error(`unsupported PNG filter ${f}`);
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
  }catch(e){throw new Error(`${path}: ${e.message}`)}
}

const median=a=>{a.sort((x,y)=>x-y);return a[Math.floor(a.length/2)]};
const lum=(r,g,b)=>.2126*r+.7152*g+.0722*b;
function estimateBackground({w,h,rgba}){
  const n=Math.max(2,Math.floor(Math.min(w,h)*.03)),rs=[],gs=[],bs=[];
  for(const [x0,y0] of [[0,0],[w-n,0],[0,h-n],[w-n,h-n]]) for(let y=y0;y<y0+n;y++) for(let x=x0;x<x0+n;x++){
    const i=(y*w+x)*4,a=rgba[i+3]/255;if(a<.5) continue;
    rs.push(rgba[i]);gs.push(rgba[i+1]);bs.push(rgba[i+2]);
  }
  return rs.length?[median(rs),median(gs),median(bs)]:[255,255,255];
}
function quantile(hist,total,q){let s=0,target=total*q;for(let i=0;i<hist.length;i++){s+=hist[i];if(s>=target)return i}return hist.length-1}

function analyze(path){
  const im=decodePNG(path),{w,h,rgba}=im,bg=estimateBackground(im),bgL=lum(...bg),hx=new Uint32Array(w),hy=new Uint32Array(h);
  let lit=0,sx=0,sy=0,edgeLit=0;
  const ex=Math.max(1,Math.floor(w*edge)),ey=Math.max(1,Math.floor(h*edge));
  for(let y=0;y<h;y++) for(let x=0;x<w;x++){
    const i=(y*w+x)*4,a=rgba[i+3]/255,L=lum(rgba[i],rgba[i+1],rgba[i+2]);
    if(Math.abs((L*a+bgL*(1-a))-bgL)<threshold) continue;
    lit++;sx+=x;sy+=y;hx[x]++;hy[y]++;
    if(x<ex||x>=w-ex||y<ey||y>=h-ey) edgeLit++;
  }
  const occupancy=lit/(w*h),warnings=[];
  if(!lit) return {file:path,width:w,height:h,background:bg,threshold,litPixels:0,occupancy:0,warnings:['no visible pixels above threshold']};
  const x0=quantile(hx,lit,low),x1=quantile(hx,lit,high),y0=quantile(hy,lit,low),y1=quantile(hy,lit,high),bw=x1-x0+1,bh=y1-y0+1;
  const dominant=Math.max(bw/w,bh/h),cx=sx/lit,cy=sy/lit,ox=(cx-(w-1)/2)/w,oy=(cy-(h-1)/2)/h,edgeShare=edgeLit/lit;
  if(occupancy<.02) warnings.push('very low occupancy (<2%): likely wire/sparse unless intentionally filamentary');
  else if(occupancy<.04) warnings.push('low occupancy (2–4%): inspect whether the field reads as tissue or as a curve');
  else if(occupancy>.15) warnings.push('high occupancy (>15%): valid, but inspect for overfill/lost cavities');
  if(dominant<.55) warnings.push('small framing: robust form span is <55% of canvas');
  if(dominant>.9) warnings.push('very large framing: robust form span is >90% of canvas');
  if(Math.abs(ox)>.15||Math.abs(oy)>.15) warnings.push('off-centre: visible-pixel centroid is >15% of canvas from centre on an axis');
  if(edgeShare>.02) warnings.push('edge contact: >2% of visible pixels fall inside the outer edge band; inspect clipping');
  return {file:path,width:w,height:h,background:bg,threshold,litPixels:lit,occupancy:+occupancy.toFixed(4),robustBBox:{x:x0,y:y0,width:bw,height:bh,widthRatio:+(bw/w).toFixed(3),heightRatio:+(bh/h).toFixed(3),quantiles:[low,high]},centroid:{x:+cx.toFixed(1),y:+cy.toFixed(1),offsetX:+ox.toFixed(3),offsetY:+oy.toFixed(3)},edgeShare:+edgeShare.toFixed(4),warnings};
}

try{
  const frames=files.map(analyze),occ=frames.map(x=>x.occupancy),spans=frames.filter(x=>x.robustBBox).map(x=>Math.max(x.robustBBox.widthRatio,x.robustBBox.heightRatio));
  console.log(JSON.stringify({frames,summary:{occupancyRange:[Math.min(...occ),Math.max(...occ)],dominantSpanRange:spans.length?[Math.min(...spans),Math.max(...spans)]:null,interpretation:'Diagnostic only. Treat warnings as prompts for visual review, not universal aesthetic failures.'}},null,2));
}catch(e){console.error(e.message);process.exit(2)}