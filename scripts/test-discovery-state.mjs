#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const cli=path.join(root,'scripts/discovery-state.mjs');
const sourceGrammar=path.join(root,'templates/mutation-grammar.json');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'tsubuyaki-discovery-'));
const grammar=path.join(dir,'grammar.json');
const state=path.join(dir,'state.json');

function run(args,expect=0){
  const r=spawnSync(process.execPath,[cli,...args],{encoding:'utf8'});
  if(r.status!==expect)throw new Error(`${args.join(' ')}: expected exit ${expect}, got ${r.status}\n${r.stdout}\n${r.stderr}`);
  return r;
}
const read=()=>JSON.parse(fs.readFileSync(state,'utf8'));
const write=x=>fs.writeFileSync(state,JSON.stringify(x,null,2)+'\n');

try{
  fs.copyFileSync(sourceGrammar,grammar);
  run(['init',state,'--route=filament','--elite=E0','--brief=translucent ribbon','--invariant=axial identity',`--grammar=${grammar}`]);
  let s=read();
  if(s.version!==3||!s.grammar?.sha256)throw new Error('v3 grammar pin missing');

  run(['add',state,'L1','--class=harmonic-family','--operator=5->7'],1);
  run(['add',state,'L2','--class=numeric-frequency','--class=numeric-fold','--operator=frequency'],1);
  run(['add',state,'E1','--class=numeric-frequency','--operator=secondaryFrequency']);
  run(['review',state,'E1','--valid=pass','--adherent=pass','--preference=archive','--reason=near-neighbor']);
  run(['unlock',state,'2','--reason=stage 1 saturated'],1);
  run(['unlock',state,'2','--reason=stage 1 saturated','--evidence=E1']);

  run(['add',state,'E2','--class=harmonic-family','--class=fold-law','--operator=secondaryFrequency:5->7','--operator=fold:sine->pulse']);
  run(['review',state,'E2','--valid=pass','--adherent=pass','--preference=prefer','--reason=stronger across matched times']);
  run(['promote',state,'E2','--reason=visual and temporal preference']);
  s=read();
  if(s.candidates.E2.mutation.changes.length!==2)throw new Error('paired changes not preserved');
  const first=s.candidates.E2.mutation.changes[0];
  if(first.class!=='harmonic-family'||first.operator!=='secondaryFrequency:5->7')throw new Error('class/operator pairing lost');
  const unlock=s.events.find(e=>e.type==='unlock'&&e.stage===2);
  const binding=unlock.evidence?.[0];
  if(binding?.candidateId!=='E1'||!Number.isInteger(binding.reviewSeq))throw new Error('review-bound evidence missing');
  const review=s.events.find(e=>e.seq===binding.reviewSeq);
  if(review?.type!=='review'||review.id!=='E1'||review.seq>=unlock.seq)throw new Error('review binding invalid');

  run(['unlock',state,'3','--reason=try topology','--evidence=E2'],1);
  run(['validate',state]);
  const baseline=read();

  let edited=structuredClone(baseline);
  edited.candidates.E1.mutation.changes[0].class='harmonic-family';
  write(edited);run(['validate',state],1);

  edited=structuredClone(baseline);
  const u=edited.events.find(e=>e.type==='unlock'&&e.stage===2);
  u.evidence[0].reviewSeq=edited.events.find(e=>e.type==='init').seq;
  write(edited);run(['validate',state],1);

  edited=structuredClone(baseline);
  const u2=edited.events.find(e=>e.type==='unlock'&&e.stage===2);
  u2.evidence[0].candidateId='E2';
  u2.evidence[0].reviewSeq=edited.events.find(e=>e.type==='review'&&e.id==='E2').seq;
  write(edited);run(['validate',state],1);

  write(baseline);run(['validate',state]);
  fs.appendFileSync(grammar,'\n');
  run(['validate',state],1);

  console.log('discovery-state binding regression test: PASS');
}finally{
  fs.rmSync(dir,{recursive:true,force:true});
}
