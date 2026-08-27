const vm=require('node:vm'),fs=require('node:fs');
const code=fs.readFileSync(process.argv[2],'utf8');
let bad=0,calls=0,frame=0,samples={};
const keep=new Set([30,90,150]);
const ctx={sin:Math.sin,cos:Math.cos,exp:Math.exp,createCanvas:()=>{},background:()=>{},stroke:()=>{},point:(x,y)=>{calls++;if(!Number.isFinite(x)||!Number.isFinite(y))bad++;if(keep.has(frame)){let a=samples[frame]||(samples[frame]=[]);if(a.length<20)a.push([x,y])}}};
vm.createContext(ctx);
let parse=true,error=null;
try{vm.runInContext(code,ctx,{timeout:1000});for(frame=1;frame<=150;frame++)ctx.draw()}catch(e){parse=false;error=String(e)}
console.log(JSON.stringify({parseRuntimePass:parse,error,badPointCalls:bad,totalPointCalls:calls,samples}));
