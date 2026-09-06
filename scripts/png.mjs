import fs from 'node:fs';
import zlib from 'node:zlib';

// Shared decoder for the validators' non-interlaced 8-bit PNG inputs.
const SIG=Buffer.from([137,80,78,71,13,10,26,10]);
const paeth=(a,b,c)=>{let p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c};

export function decodePNG(path){
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
