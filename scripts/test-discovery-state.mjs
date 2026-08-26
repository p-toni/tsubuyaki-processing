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
  if(r.status!==expect){console.error(r.stdout);console.error(r.stderr);throw new Error(`${args.join(' ')}: expected exit ${expect}, got ${r.status}`)}
  return r;
}
function read(){return JSON.parse(fs.readFileSync(state,'utf8'))}
function write(x){fs.writeFileSync(state,JSON.stringify(x,null,2)+'\n')}

try{
  fs.copyFileSync(sourceGrammar,grammar);
  run(['init',state,'--route=filament','--elite=E0','--brief=translucent ribbon','--invariant=axial identity',`--grammar=${grammar}`]);
  let s=read();
  if(s.version!==3||!s.grammar?.sha256||s.grammar.version!==1)throw new Error('v3 grammar pin missing');

  // Locked class is rejected at write time.
  run(['add',state,'BAD','--change=harmonic-family::5->7'],1);
  run(['add',state,'E1','--change=numeric-frequency::secondaryFrequency']);
  run(['review',state,'E1','--valid=pass','--adherent=pass','--preference=archive','--reason=near-neighbor']);

  // Unlock requires evidence and binds it to the actual prior review event.
  run(['unlock',state,'2','--reason=stage 1 saturated'],1);
  run(['unlock',state,'2','--reason=stage 1 saturated','--evidence=E1']);
  s=read();
  const unlock=s.events.find(e=>e.type==='unlock'&&e.stage===2);
  const e1Review=s.events.find(e=>e.type==='review'&&e.id==='E1');
  if(unlock.evidence[0].candidateId!=='E1'||unlock.evidence[0].reviewSeq!==e1Review.seq)throw new Error('review-bound evidence not preserved');

  // Compound causes are paired records, not parallel arrays.
  run(['add',state,'E2','--change=harmonic-family::secondaryFrequency:5->7','--change=fold-law::sine->pulse']);
  run(['review',state,'E2','--valid=pass','--adherent=pass','--preference=prefer','--reason=stronger across matched times']);
  run(['promote',state,'E2','--reason=visual and temporal preference']);
  s=read();
  if(s.candidates.E2.mutation.changes.length!==2||s.candidates.E2.mutation.changes[1].class!=='fold-law')throw new Error('paired compound cause not preserved');

  // Stage 3 brief guard still holds.
  run(['unlock',state,'3','--reason=try topology','--evidence=E2'],1);
  run(['validate',state]);
  const clean=read();

  // Historical-stage corruption is caught.
  let corrupt=structuredClone(clean);
  corrupt.candidates.E1.mutation.changes[0].class='harmonic-family';
  write(corrupt);run(['validate',state],1);write(clean);

  // Malformed causal pair is caught.
  corrupt=structuredClone(clean);
  delete corrupt.candidates.E2.mutation.changes[0].operator;
  write(corrupt);run(['validate',state],1);write(clean);

  // Unlock evidence cannot be redirected to an unrelated/later review.
  corrupt=structuredClone(clean);
  const u=corrupt.events.find(e=>e.type==='unlock'&&e.stage===2);
  const e2Review=corrupt.events.find(e=>e.type==='review'&&e.id==='E2');
  u.evidence=[{candidateId:'E1',reviewSeq:e2Review.seq}];
  write(corrupt);run(['validate',state],1);write(clean);

  // Review must precede unlock.
  corrupt=structuredClone(clean);
  const unlock2=corrupt.events.find(e=>e.type==='unlock'&&e.stage===2);
  unlock2.evidence[0].reviewSeq=unlock2.seq+100;
  write(corrupt);run(['validate',state],1);write(clean);
  run(['validate',state]);

  // Grammar drift still invalidates the record.
  fs.appendFileSync(grammar,'\n');
  run(['validate',state],1);

  console.log('discovery-state evidence fidelity regression test: PASS');
}finally{fs.rmSync(dir,{recursive:true,force:true})}
