#!/usr/bin/env node
import fs from 'node:fs';
import zlib from 'node:zlib';

const [input,id,out,...args]=process.argv.slice(2);
let time=7.5,width=320,height=320;
for(const a of args){if(a.startsWith('--time='))time=+a.split('=')[1];else if(a.startsWith('--size='))width=height=+a.split('=')[1]}
if(!input||!id||!out){console.error('Usage: node experiments/search-lab/render-genotype.mjs candidates.json candidateId out.png [--time=7.5] [--size=320]');process.exit(2)}
const doc=JSON.parse(fs.readFileSync(input,'utf8'));
const candidate=(doc.candidates||[]).find(x=>x.id===id);
if(!candidate)throw new Error(`candidate '${id}' not found in ${input}`);
const g=candidate.genotype,BG=9,N=g.samples|0,cx=width/2,cy=height/2,pts=[];
const add=(x,y)=>{if(Number.isFinite(x)&&Number.isFinite(y))pts.push([x,y])};
const mag=Math.hypot;

if(g.topology==='family'){
  const [f1,f2,f3]=g.latentHarmonics;
  for(let i=0;i<N;i++){
    const m=i%g.familyCount*g.familyPhaseStep,k=g.bodyScale*Math.sin(i*f1)*Math.sin(i/2),e=g.bodyScale*Math.cos(i*f2)*Math.cos(i/f3);
    const d=mag(k,e)**g.distancePower/Math.max(1,g.distanceDivisor)+1.4-Math.sin(time/2+m)**3/4;
    let p;
    if(g.deformation==='power-sine')p=d**Math.sin(d*d/2-time+m);
    else if(g.deformation==='sine-feedback')p=d*(1+.6*Math.sin(d*d/3-time+m));
    else if(g.deformation==='reciprocal')p=d+4/(.6+d)+Math.sin(d*3-time+m);
    else p=1+.035*d**3+Math.sin(d-time+m);
    const c=d/Math.max(3,g.phaseDivisor)-time/Math.max(4,g.timeDivisor)+m;
    if(g.projection==='harmonic')add(cx+96*Math.sin(c)+k*p,cy+88*Math.sin(c*g.projectionHarmonic)+e*p);
    else if(g.projection==='polar-mix'){const q=55+8*p+2*k;add(cx+q*Math.cos(c)+k*p*.5,cy+q*.78*Math.sin(c)+e*p*.5)}
    else{const q=45+7*p+Math.abs(k)*3;add(cx+q*Math.cos(c),cy+q*.65*Math.sin(c)+e*2)}
  }
}else if(g.topology==='recurrence'){
  let x=9,y=9,z=9;
  for(let i=0;i<N;i++){
    const j=i%g.familyCount,e=Math.sin(time/3-x*x/99+j)+1;
    let X,Y;
    if(g.projection==='polar'){
      const q=x*e+g.radialOffset,c=z/g.stateDivisor-e/29+time/g.timeDivisor+j*g.familyPhaseStep;X=cx+q*Math.cos(c);Y=cy-(q+45*Math.cos(c/2))*Math.sin(c);
    }else if(g.projection==='double-polar'){
      const c=z/g.stateDivisor+j*g.familyPhaseStep+time/g.timeDivisor,q=65+x*e+12*Math.sin(y/8);X=cx+q*Math.cos(c)+y*.8;Y=cy+(.62*q+10*Math.cos(c*2))*Math.sin(c);
    }else{
      const c=(z+y)/70+j*g.familyPhaseStep,q=58+x*e+8*Math.sin(z/9-time);X=cx+q*Math.cos(c);Y=cy+q*.55*Math.sin(c)+y*1.2;
    }
    add(X,Y);
    const X0=x,Y0=y,Z0=z,dt=g.dt;x=X0+g.sigma*(Y0-X0)*dt;y=Y0+(X0*(g.rho-Z0)-Y0)*dt;z=Z0+(X0*Y0-g.beta*Z0)*dt;
  }
}else if(g.topology==='sheet'){
  const cols=g.columns|0;
  for(let i=0;i<N;i++){
    const u=i%cols/g.xScale-cols/(2*g.xScale),v=i/cols/g.yScale-N/cols/(2*g.yScale),d=mag(u,v),c=d/3-time/8+Math.sin(v/g.foldFrequency)/4,q=52+d*3+g.warp*Math.sin(d*d/(8+g.distancePower)-time);
    if(g.projection==='folded')add(cx+(q+u*2)*Math.cos(c),cy+(q*.55+v)*Math.sin(c));
    else if(g.projection==='shell')add(cx+(q+8*Math.sin(v))*Math.cos(c),cy+q*.5*Math.sin(c)+u*v/8);
    else{const s=u>=0?1:-1;add(cx+s*(24+Math.abs(u)*5+8*Math.sin(v/3-time)),cy+v*5+u*Math.sin(d-time))}
  }
}else if(g.topology==='filament'){
  for(let i=0;i<N;i++){
    const u=i/N*Math.PI*10-5*Math.PI,fam=i%g.familyCount,r=g.radius+g.fold*Math.sin(g.secondaryFrequency*u-time+fam);
    if(g.projection==='axial')add(cx+g.radius*.45*Math.sin(g.primaryFrequency*u+time)+g.twist*u,cy+u*5+r*.13*Math.sin(u+fam));
    else if(g.projection==='polar-ribbon'){const c=u/3+fam*Math.PI/Math.max(1,g.familyCount)+time/9;add(cx+r*Math.cos(c),cy+r*.55*Math.sin(c)+10*Math.sin(g.primaryFrequency*u))}
    else{const c=u/2+time/10;add(cx+(r+12*Math.sin(g.primaryFrequency*u))*Math.cos(c),cy+r*.6*Math.sin(c)+8*Math.sin(g.secondaryFrequency*u))}
  }
}else throw new Error(`unsupported topology '${g.topology}'`);

const pixels=Buffer.alloc(width*height,BG),alpha=Math.max(.03,Math.min(.55,g.alpha/255));
for(const [x,y] of pts){const X=Math.round(x),Y=Math.round(y);if(X>=0&&X<width&&Y>=0&&Y<height){const p=Y*width+X;pixels[p]=Math.round(pixels[p]*(1-alpha)+255*alpha)}}

const table=new Uint32Array(256);
for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=(c&1)?0xedb88320^(c>>>1):c>>>1;table[n]=c>>>0}
const crc=b=>{let c=0xffffffff;for(const x of b)c=table[(c^x)&255]^(c>>>8);return(c^0xffffffff)>>>0};
const chunk=(type,data)=>{const t=Buffer.from(type),body=Buffer.concat([t,data]),o=Buffer.alloc(12+data.length);o.writeUInt32BE(data.length,0);body.copy(o,4);o.writeUInt32BE(crc(body),8+data.length);return o};
const ihdr=Buffer.alloc(13);ihdr.writeUInt32BE(width,0);ihdr.writeUInt32BE(height,4);ihdr[8]=8;ihdr[9]=0;ihdr[10]=ihdr[11]=ihdr[12]=0;
const raw=Buffer.alloc((width+1)*height);for(let y=0;y<height;y++){raw[y*(width+1)]=0;pixels.copy(raw,y*(width+1)+1,y*width,(y+1)*width)}
const png=Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',ihdr),chunk('IDAT',zlib.deflateSync(raw)),chunk('IEND',Buffer.alloc(0))]);
fs.writeFileSync(out,png);
console.log(JSON.stringify({candidate:id,topology:g.topology,points:pts.length,size:[width,height],time,out},null,2));
