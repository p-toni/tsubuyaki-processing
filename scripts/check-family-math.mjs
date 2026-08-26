#!/usr/bin/env node
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const [probePath,contractPath,controlName,...args]=process.argv.slice(2);
let factor=null,delta=null,samples=null,time=null;
for(const a of args){
  if(a.startsWith('--factor=')) factor=+a.split('=')[1];
  else if(a.startsWith('--delta=')) delta=+a.split('=')[1];
  else if(a.startsWith('--samples=')) samples=+a.split('=')[1];
  else if(a.startsWith('--time=')) time=+a.split('=')[1];
}
if(!probePath||!contractPath||!controlName){
  console.error('Usage: node scripts/check-family-math.mjs probe.mjs morphology.json controlName [--factor=1.2|--delta=N] [--samples=N] [--time=T]');
  process.exit(2);
}
if(factor!==null&&delta!==null){console.error('Use either --factor or --delta, not both');process.exit(2)}

const median=a=>{if(!a.length)return null;const s=[...a].sort((x,y)=>x-y),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2};
const mad=a=>{const m=median(a);return m===null?null:median(a.map(x=>Math.abs(x-m)))};
function aggregate(values,metric){
  if(!values.length)return null;
  if(metric==='max')return Math.max(...values);
  if(metric==='min')return Math.min(...values);
  if(metric==='range')return Math.max(...values)-Math.min(...values);
  if(metric==='mean')return values.reduce((a,b)=>a+b,0)/values.length;
  if(metric==='rms')return Math.sqrt(values.reduce((a,b)=>a+b*b,0)/values.length);
  if(metric==='absMax')return Math.max(...values.map(Math.abs));
  throw new Error(`unsupported math-family metric '${metric}'`);
}
function fieldValue(s,field){
  if(field==='x'||field==='y')return s[field];
  if(field.startsWith('latent.'))return s.latent?.[field.slice(7)];
  return s.latent?.[field] ?? s[field];
}
function collect(mod,params,N,T,family,field){
  const out=new Map();
  for(let i=0;i<N;i++){
    const s=mod.sample(i,T,params);
    if(!s||s.family!==family||s.instance===undefined||s.instance===null)continue;
    const v=fieldValue(s,field);
    if(!Number.isFinite(v))continue;
    const k=String(s.instance);
    if(!out.has(k))out.set(k,[]);
    out.get(k).push(v);
  }
  return out;
}

try{
  const contract=JSON.parse(fs.readFileSync(contractPath,'utf8'));
  const control=contract.controls?.[controlName];
  if(!control)throw new Error(`${contractPath}: unknown control '${controlName}'`);
  const effect=control.effect;
  if(!effect||effect.source!=='math-family')throw new Error(`${contractPath}: control '${controlName}' needs effect.source='math-family'`);
  const family=effect.family||control.region,field=effect.field,metric=effect.metric||'max',direction=effect.direction||'increase';
  if(!family||!field)throw new Error(`${contractPath}: math-family effect requires family and field`);
  if(!['increase','decrease','any'].includes(direction))throw new Error(`${contractPath}: invalid direction '${direction}'`);

  const absProbe=path.resolve(probePath),mod=await import(pathToFileURL(absProbe).href+`?v=${Date.now()}`);
  if(typeof mod.sample!=='function'||!mod.controls)throw new Error(`${probePath}: must export controls and sample(i,time,params)`);
  if(!(controlName in mod.controls))throw new Error(`${probePath}: controls has no '${controlName}'`);

  const N=samples??mod.probeConfig?.samples??10000,T=time??mod.probeConfig?.time??0;
  if(!Number.isInteger(N)||N<1)throw new Error('--samples must be a positive integer');
  const base={...mod.controls},variant={...mod.controls};
  const baseValue=base[controlName];
  if(!Number.isFinite(baseValue))throw new Error(`${probePath}: control '${controlName}' must be numeric`);
  const appliedDelta=delta!==null?delta:baseValue*((factor??effect.variantFactor??1.2)-1);
  variant[controlName]=baseValue+appliedDelta;

  const B=collect(mod,base,N,T,family,field),V=collect(mod,variant,N,T,family,field);
  const ids=[...new Set([...B.keys(),...V.keys()])].sort((a,b)=>+a-+b);
  if(!ids.length)throw new Error(`${probePath}: no samples found for family '${family}'`);

  const rows=[],relative=[];
  for(const id of ids){
    const b=aggregate(B.get(id)||[],metric),v=aggregate(V.get(id)||[],metric);
    if(b===null||v===null){rows.push({instance:id,baseline:b,variant:v,relativeChange:null});continue}
    const r=b?((v-b)/Math.abs(b)):null;
    rows.push({instance:id,baseline:+b.toFixed(6),variant:+v.toFixed(6),relativeChange:r===null?null:+r.toFixed(6),baselineSamples:(B.get(id)||[]).length,variantSamples:(V.get(id)||[]).length});
    if(r!==null&&Number.isFinite(r))relative.push(r);
  }
  if(!relative.length)throw new Error('No finite per-instance relative changes could be computed');

  const med=median(relative),disp=mad(relative);
  const signAgreement=direction==='any'
    ? relative.filter(r=>Math.abs(r)>1e-12).length/relative.length
    : relative.filter(r=>direction==='increase'?r>0:r<0).length/relative.length;
  const minMedian=effect.minMedianRelativeChange??effect.minRelativeChange??0;
  const minAgreement=effect.minAgreement??0.8;
  const maxMAD=effect.maxRelativeMAD??null;
  const directionOk=direction==='any'||(direction==='increase'&&med>0)||(direction==='decrease'&&med<0);
  const strengthOk=Math.abs(med)>=minMedian;
  const agreementOk=signAgreement>=minAgreement;
  const dispersionOk=maxMAD===null||disp<=maxMAD;
  const pass=directionOk&&strengthOk&&agreementOk&&dispersionOk;

  console.log(JSON.stringify({
    control:controlName,
    probe:path.resolve(probePath),
    sampling:{samples:N,time:T,baselineControl:baseValue,variantControl:variant[controlName],appliedDelta},
    declared:{source:'math-family',family,field,metric,direction,minMedianRelativeChange:minMedian,minAgreement,maxRelativeMAD:maxMAD},
    familySummary:{instanceCount:ids.length,medianRelativeChange:+med.toFixed(6),directionalAgreement:+signAgreement.toFixed(4),relativeMAD:+disp.toFixed(6),minRelativeChange:+Math.min(...relative).toFixed(6),maxRelativeChange:+Math.max(...relative).toFixed(6)},
    checks:{direction:directionOk,strength:strengthOk,agreement:agreementOk,dispersion:dispersionOk},
    pass,
    instances:rows,
    interpretation:'Math-family validation inspects each repeated instance in latent space before rasterization. Run raster scope validation separately: math correctness does not prove visual locality or aesthetic quality.'
  },null,2));
}catch(e){console.error(e.message);process.exit(2)}
