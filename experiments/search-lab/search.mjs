#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const seeds=JSON.parse(fs.readFileSync(path.join(here,'seed-genotypes.json'),'utf8'));
const briefs=JSON.parse(fs.readFileSync(path.join(here,'briefs.json'),'utf8'));

const args=Object.fromEntries(process.argv.slice(2).map(a=>{const [k,...v]=a.replace(/^--/,'').split('=');return[k,v.join('=')||true]}));
const brief=args.brief||'plankton_family',regime=(args.regime||'A').toUpperCase(),count=+(args.count||12),seed=+(args.seed||1),out=args.out||null;
if(!seeds[brief])throw new Error(`unknown brief '${brief}'`);
if(!['A','B','C'].includes(regime))throw new Error(`regime must be A, B or C`);
if(!Number.isInteger(count)||count<1)throw new Error('--count must be a positive integer');

function rng(s){let x=(s|0)||1;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return(x>>>0)/4294967296}}
const R=rng(seed);
const pick=a=>a[Math.floor(R()*a.length)];
const gaussian=()=>{let u=0,v=0;while(!u)u=R();while(!v)v=R();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)};
const mutateNum=(x,s=.16)=>x*(1+gaussian()*s);

function parameterMutation(base){
  const g=structuredClone(base);
  const skip=new Set(['samples','familyCount','columns','distancePower']);
  for(const [k,v] of Object.entries(g))if(typeof v==='number'&&!skip.has(k)){
    if(k==='alpha')g[k]=Math.max(25,Math.min(110,Math.round(mutateNum(v,.12))));
    else g[k]=+mutateNum(v).toFixed(6);
  }
  if(Array.isArray(g.latentHarmonics))g.latentHarmonics=g.latentHarmonics.map(v=>+mutateNum(v,.10).toFixed(4));
  return g;
}

function structuralMutation(base){
  const g=parameterMutation(base);
  if(g.topology==='family'){
    g.familyCount=pick([7,9,11,13,16]);
    g.distancePower=pick([1.5,2,2.5,3]);
    g.deformation=pick(['power-sine','sine-feedback','reciprocal','cubic']);
    g.projection=pick(['harmonic','polar-mix','folded']);
    g.projectionHarmonic=pick([2,3,4,5]);
    g.latentHarmonics=[pick([2,3,4,5]),pick([3,5,7]),pick([2,3,4,6])];
  }else if(g.topology==='recurrence'){
    g.familyCount=pick([3,5,7,9]);
    g.projection=pick(['polar','double-polar','folded']);
    g.sigma=pick([7.5,9,10,12]);
    g.beta=pick([1.8,2,2.4,8/3]);
  }else if(g.topology==='sheet'){
    g.columns=pick([110,130,150,173,190]);
    g.distancePower=pick([1,2,3]);
    g.projection=pick(['folded','shell','bilateral']);
    g.foldFrequency=pick([3.5,5,6,8,11]);
  }else if(g.topology==='filament'){
    g.familyCount=pick([1,2,3,5]);
    g.projection=pick(['axial','polar-ribbon','looped']);
    g.primaryFrequency=pick([1.5,2.5,3.5,5]);
    g.secondaryFrequency=pick([3,5,7,9]);
  }
  return g;
}

const base=seeds[brief];
const candidates=[];
if(regime==='A')candidates.push({id:`${brief}-A-${seed}-0`,brief,regime,seed,genotype:structuredClone(base)});
else for(let i=0;i<count;i++)candidates.push({id:`${brief}-${regime}-${seed}-${i}`,brief,regime,seed,index:i,genotype:regime==='B'?parameterMutation(base):structuralMutation(base)});

const result={
  experiment:'representation-vs-search-v1',
  frozenRepresentation:'v0.6',
  brief,
  prompt:briefs[brief].prompt,
  regime,
  seed,
  generationPolicy:regime==='A'?'one-shot seed genotype':regime==='B'?'numeric parameter mutation only':'fixed structural grammar + numeric mutation',
  candidates
};

const text=JSON.stringify(result,null,2)+'\n';
if(out){fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,text);console.error(`wrote ${out}`)}
else process.stdout.write(text);
