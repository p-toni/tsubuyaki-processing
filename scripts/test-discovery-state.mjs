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
  if(r.status!==expect){
    console.error(r.stdout);console.error(r.stderr);
    throw new Error(`${args.join(' ')}: expected exit ${expect}, got ${r.status}`);
  }
  return r;
}
function read(){return JSON.parse(fs.readFileSync(state,'utf8'))}
function write(x){fs.writeFileSync(state,JSON.stringify(x,null,2)+'\n')}

try{
  fs.copyFileSync(sourceGrammar,grammar);

  // Pin the grammar and start with only stage-1 filament mutations unlocked.
  run(['init',state,'--route=filament','--elite=E0','--brief=translucent ribbon','--invariant=axial identity',`--grammar=${grammar}`]);
  let s=read();
  if(s.version!==2||!s.grammar?.sha256||s.grammar.version!==1)throw new Error('grammar pin missing');

  // Historical lock enforcement at write time.
  run(['add',state,'BAD','--class=harmonic-family','--operator=5->7'],1);
  run(['add',state,'E1','--class=numeric-frequency','--operator=secondaryFrequency']);
  run(['review',state,'E1','--valid=pass','--adherent=pass','--preference=archive','--reason=near-neighbor']);

  // Unlocks now require reviewed evidence from the current stage.
  run(['unlock',state,'2','--reason=stage 1 saturated'],1);
  run(['unlock',state,'2','--reason=stage 1 saturated','--evidence=E1']);

  // One phenotype may have multiple causal mutation classes/operators.
  run(['add',state,'E2','--class=harmonic-family','--class=fold-law','--operator=secondaryFrequency:5->7','--operator=fold:sine->pulse']);
  run(['review',state,'E2','--valid=pass','--adherent=pass','--preference=prefer','--reason=stronger across matched times']);
  run(['promote',state,'E2','--reason=visual and temporal preference']);
  s=read();
  if(s.candidates.E2.mutation.classes.length!==2||s.candidates.E2.mutation.operators.length!==2)throw new Error('compound cause not preserved');
  const unlock=s.events.find(e=>e.type==='unlock'&&e.stage===2);
  if(JSON.stringify(unlock.evidenceCandidateIds)!==JSON.stringify(['E1']))throw new Error('unlock evidence not preserved');

  // Stage 3 remains brief-gated even with valid stage-2 evidence.
  run(['unlock',state,'3','--reason=try topology','--evidence=E2'],1);
  run(['validate',state]);

  // Manual history corruption must be caught: stage-1 candidate cannot claim a stage-2 class.
  const clean=read();
  const corrupt=structuredClone(clean);
  corrupt.candidates.E1.mutation.classes=['harmonic-family'];
  write(corrupt);
  run(['validate',state],1);
  write(clean);
  run(['validate',state]);

  // Grammar drift must invalidate an existing search record.
  fs.appendFileSync(grammar,'\n');
  run(['validate',state],1);

  console.log('discovery-state fidelity regression test: PASS');
}finally{
  fs.rmSync(dir,{recursive:true,force:true});
}
