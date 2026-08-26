#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const cli=path.join(root,'scripts/discovery-state.mjs');
const grammar=path.join(root,'templates/mutation-grammar.json');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'tsubuyaki-discovery-'));
const state=path.join(dir,'state.json');

function run(args,expect=0){
  const r=spawnSync(process.execPath,[cli,...args],{encoding:'utf8'});
  if(r.status!==expect){
    console.error(r.stdout);console.error(r.stderr);
    throw new Error(`${args.join(' ')}: expected exit ${expect}, got ${r.status}`);
  }
  return r;
}

try{
  run(['init',state,'--route=filament','--elite=E0','--brief=translucent ribbon','--invariant=axial identity',`--grammar=${grammar}`]);
  run(['add',state,'BAD','--class=harmonic-family'],1);
  run(['add',state,'E1','--class=numeric-frequency','--operator=secondaryFrequency']);
  run(['review',state,'E1','--valid=pass','--adherent=pass','--preference=archive','--reason=near-neighbor']);
  run(['unlock',state,'2','--reason=stage 1 saturated']);
  run(['add',state,'E2','--class=harmonic-family','--operator=5->7']);
  run(['review',state,'E2','--valid=pass','--adherent=pass','--preference=prefer','--reason=stronger across matched times']);
  run(['promote',state,'E2','--reason=visual and temporal preference']);
  run(['unlock',state,'3','--reason=try topology'],1);
  run(['validate',state]);
  const s=JSON.parse(fs.readFileSync(state,'utf8'));
  if(s.eliteId!=='E2'||s.stage!==2)throw new Error('unexpected final state');
  console.log('discovery-state regression test: PASS');
}finally{
  fs.rmSync(dir,{recursive:true,force:true});
}
