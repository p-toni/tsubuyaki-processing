#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const argv=process.argv.slice(2);
const command=argv.shift();
const statePath=argv.shift();

function usage(code=2){
  console.error(`Usage:
  node scripts/discovery-state.mjs init STATE --route=filament --elite=E0 --brief="..." --invariant="..." [--grammar=templates/mutation-grammar.json]
  node scripts/discovery-state.mjs add STATE ID --parent=E0 --class=numeric-frequency [--class=...] --operator=frequency [--operator=...] [--note="..."] [--artifact=path]
  node scripts/discovery-state.mjs review STATE ID --valid=pass --adherent=pass --preference=prefer|archive|reject|undecided --reason="..."
  node scripts/discovery-state.mjs promote STATE ID --reason="..."
  node scripts/discovery-state.mjs unlock STATE STAGE --reason="..." --evidence=E1 [--evidence=E2] [--brief-change=true] [--experimental=true]
  node scripts/discovery-state.mjs summary STATE
  node scripts/discovery-state.mjs validate STATE`);
  process.exit(code);
}
if(!command||!statePath)usage();

function parseOptions(items){
  const out={_:[]};
  const repeatable=new Set(['invariant','artifact','note','class','operator','evidence']);
  for(const item of items){
    if(!item.startsWith('--')){out._.push(item);continue}
    const p=item.slice(2);const eq=p.indexOf('=');
    const k=eq<0?p:p.slice(0,eq),v=eq<0?'true':p.slice(eq+1);
    if(repeatable.has(k))(out[k]??=[]).push(v);else out[k]=v;
  }
  return out;
}
const opt=parseOptions(argv);
const bool=v=>v===true||v==='true'||v==='1'||v==='yes'||v==='pass';
const fail=m=>{throw new Error(m)};
const load=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const save=(p,x)=>{fs.mkdirSync(path.dirname(path.resolve(p)),{recursive:true});fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n')};
const nextSeq=s=>s.events.length?Math.max(...s.events.map(e=>e.seq||0))+1:1;
const event=(s,type,data={})=>s.events.push({seq:nextSeq(s),type,...data});
const sha256=b=>crypto.createHash('sha256').update(b).digest('hex');

function resolveGrammar(raw,stateFile){
  if(path.isAbsolute(raw))return raw;
  const fromCwd=path.resolve(raw);if(fs.existsSync(fromCwd))return fromCwd;
  const fromState=path.resolve(path.dirname(path.resolve(stateFile)),raw);if(fs.existsSync(fromState))return fromState;
  const fromScript=path.resolve(here,'..',raw);if(fs.existsSync(fromScript))return fromScript;
  return fromCwd;
}
function readGrammar(raw,stateFile){
  const gp=resolveGrammar(raw,stateFile),bytes=fs.readFileSync(gp),g=JSON.parse(bytes.toString('utf8'));
  return {gp,g,hash:sha256(bytes)};
}
function grammarInfo(s,verify=true){
  if(!s.grammar||typeof s.grammar!=='object'||!s.grammar.path)fail('grammar pin missing; expected grammar.path/version/sha256');
  const {gp,g,hash}=readGrammar(s.grammar.path,statePath);
  if(verify){
    if(s.grammar.version!==g.version)fail(`grammar version mismatch: state=${s.grammar.version}, file=${g.version}`);
    if(s.grammar.sha256!==hash)fail(`grammar hash mismatch: state=${s.grammar.sha256}, file=${hash}`);
  }
  return {gp,g,hash};
}
function routeInfo(s,verify=true){
  const {gp,g,hash}=grammarInfo(s,verify),r=g.routes?.[s.route];
  if(!r)fail(`route '${s.route}' not found in ${gp}`);return {g,r,gp,hash};
}
function stageInfo(s,n=s.stage){const {r}=routeInfo(s);const x=r.stages.find(z=>z.stage===n);if(!x)fail(`stage ${n} not defined for route '${s.route}'`);return x}
function classesThrough(r,n){return [...new Set(r.stages.filter(x=>x.stage<=n).flatMap(x=>x.classes||[]))]}
function unlockedClasses(s){const {r}=routeInfo(s);return classesThrough(r,s.stage)}
function requireCandidate(s,id){const c=s.candidates[id];if(!c)fail(`candidate '${id}' not found`);return c}
function reviewedEvidence(s,id){
  const c=requireCandidate(s,id);
  if(c.parentId===null)fail(`evidence '${id}' is the incumbent, not a searched challenger`);
  if(c.stage!==s.stage)fail(`evidence '${id}' belongs to stage ${c.stage}; unlock evidence must come from current stage ${s.stage}`);
  if(c.review.valid==='unknown'||c.review.adherent==='unknown'||c.review.preference==='undecided')fail(`evidence '${id}' has not completed review`);
  return c;
}
function validateState(s){
  const errs=[];
  if(s.version!==2)errs.push('version must be 2');
  if(!s.route)errs.push('route missing');
  if(!s.brief||!Array.isArray(s.brief.invariants))errs.push('brief.invariants missing');
  if(!s.eliteId||!s.candidates?.[s.eliteId])errs.push('eliteId must name an existing candidate');
  if(!Number.isInteger(s.stage)||s.stage<1)errs.push('stage must be a positive integer');
  let r=null;
  try{({r}=routeInfo(s));if(!r.stages.some(x=>x.stage===s.stage))errs.push(`stage ${s.stage} not defined for route '${s.route}'`)}catch(e){errs.push(e.message)}
  for(const [id,c] of Object.entries(s.candidates||{})){
    if(c.id!==id)errs.push(`${id}: candidate.id mismatch`);
    if(c.parentId&&!s.candidates[c.parentId])errs.push(`${id}: parent '${c.parentId}' missing`);
    if(c.parentId===id)errs.push(`${id}: cannot parent itself`);
    if(!Number.isInteger(c.stage)||c.stage<0||c.stage>s.stage)errs.push(`${id}: invalid historical stage ${c.stage}`);
    if(c.mutation){
      if(!Array.isArray(c.mutation.classes)||!c.mutation.classes.length)errs.push(`${id}: mutation.classes must be a non-empty array`);
      if(!Array.isArray(c.mutation.operators)||!c.mutation.operators.length)errs.push(`${id}: mutation.operators must be a non-empty array`);
      if(r&&Array.isArray(c.mutation.classes)){
        const legal=new Set(classesThrough(r,c.stage));
        for(const cls of c.mutation.classes)if(!legal.has(cls))errs.push(`${id}: mutation class '${cls}' was not unlocked at historical stage ${c.stage}`);
      }
    }else if(c.parentId!==null)errs.push(`${id}: non-incumbent candidate must record mutation cause`);
  }
  let lastSeq=0;
  for(const e of s.events||[]){
    if(!Number.isInteger(e.seq)||e.seq<=lastSeq)errs.push(`event sequence must be strictly increasing at ${e.seq}`);lastSeq=e.seq||lastSeq;
    if(e.type==='unlock'){
      if(!Array.isArray(e.evidenceCandidateIds)||!e.evidenceCandidateIds.length)errs.push(`unlock stage ${e.stage}: evidenceCandidateIds required`);
      for(const id of e.evidenceCandidateIds||[])if(!s.candidates?.[id])errs.push(`unlock stage ${e.stage}: evidence candidate '${id}' missing`);
    }
  }
  return errs;
}

if(command==='init'){
  if(fs.existsSync(statePath))fail(`${statePath} already exists`);
  const route=opt.route;if(!route)fail('--route is required');
  const grammarPath=opt.grammar||'templates/mutation-grammar.json';
  const {g,hash}=readGrammar(grammarPath,statePath);if(!g.routes?.[route])fail(`route '${route}' not found in ${resolveGrammar(grammarPath,statePath)}`);
  const eliteId=opt.elite||'E0';
  const state={version:2,route,grammar:{path:grammarPath,version:g.version,sha256:hash},stage:1,eliteId,brief:{text:opt.brief||'',invariants:opt.invariant||[]},candidates:{},events:[]};
  state.candidates[eliteId]={id:eliteId,parentId:null,stage:0,mutation:null,status:'elite',artifacts:[],notes:['initial incumbent'],review:{valid:'pass',adherent:'pass',preference:'incumbent',reason:'initial viable incumbent'}};
  event(state,'init',{eliteId,route,stage:1,grammar:{version:g.version,sha256:hash}});
  save(statePath,state);console.log(JSON.stringify({state:statePath,eliteId,route,stage:1,grammar:state.grammar,unlocked:unlockedClasses(state)},null,2));process.exit(0);
}

const state=load(statePath);
if(command==='add'){
  routeInfo(state);
  const id=opt._[0];if(!id)fail('candidate ID is required');if(state.candidates[id])fail(`candidate '${id}' already exists`);
  const parentId=opt.parent||state.eliteId;requireCandidate(state,parentId);
  const classes=opt.class||[];if(!classes.length)fail('at least one --class is required');
  const operators=opt.operator||[];if(!operators.length)fail('at least one --operator is required to record concrete mathematical cause');
  const allowed=new Set(unlockedClasses(state));for(const cls of classes)if(!allowed.has(cls))fail(`mutation class '${cls}' is locked at stage ${state.stage}`);
  state.candidates[id]={id,parentId,stage:state.stage,mutation:{classes:[...new Set(classes)],operators,detail:opt.detail||null},status:'candidate',artifacts:opt.artifact||[],notes:opt.note||[],review:{valid:'unknown',adherent:'unknown',preference:'undecided',reason:''}};
  event(state,'add',{id,parentId,stage:state.stage,classes:state.candidates[id].mutation.classes,operators});save(statePath,state);console.log(JSON.stringify(state.candidates[id],null,2));
}else if(command==='review'){
  routeInfo(state);
  const id=opt._[0];if(!id)fail('candidate ID is required');const c=requireCandidate(state,id);
  const valid=opt.valid||c.review.valid,adherent=opt.adherent||c.review.adherent,preference=opt.preference||c.review.preference;
  for(const [k,v] of Object.entries({valid,adherent}))if(!['pass','fail','unknown'].includes(v))fail(`--${k} must be pass|fail|unknown`);
  if(!['prefer','archive','reject','undecided','incumbent'].includes(preference))fail('--preference must be prefer|archive|reject|undecided|incumbent');
  c.review={valid,adherent,preference,reason:opt.reason||c.review.reason||''};
  if(opt.note)c.notes.push(...opt.note);
  if(valid==='fail'||adherent==='fail'||preference==='reject')c.status='rejected';else if(preference==='archive')c.status='archived';else if(c.status!=='elite')c.status='reviewed';
  event(state,'review',{id,valid,adherent,preference});save(statePath,state);console.log(JSON.stringify(c,null,2));
}else if(command==='promote'){
  routeInfo(state);
  const id=opt._[0];if(!id)fail('candidate ID is required');const c=requireCandidate(state,id);const reason=opt.reason;if(!reason)fail('--reason is required');
  if(c.review.valid!=='pass')fail(`candidate '${id}' cannot be promoted: valid=${c.review.valid}`);
  if(c.review.adherent!=='pass')fail(`candidate '${id}' cannot be promoted: adherent=${c.review.adherent}`);
  if(c.review.preference!=='prefer')fail(`candidate '${id}' cannot be promoted: preference must be 'prefer' after visual/temporal review`);
  const old=state.eliteId;if(state.candidates[old])state.candidates[old].status='prior-elite';
  state.eliteId=id;c.status='elite';event(state,'promote',{from:old,to:id,reason});save(statePath,state);console.log(JSON.stringify({from:old,to:id,stage:state.stage,reason},null,2));
}else if(command==='unlock'){
  routeInfo(state);
  const target=Number(opt._[0]);if(!Number.isInteger(target))fail('target STAGE integer is required');
  if(target!==state.stage+1)fail(`unlock must advance exactly one stage (${state.stage} -> ${state.stage+1})`);
  const next=stageInfo(state,target),reason=opt.reason;if(!reason)fail('--reason is required');
  const evidenceCandidateIds=[...new Set(opt.evidence||[])];if(!evidenceCandidateIds.length)fail('at least one --evidence candidate is required');
  for(const id of evidenceCandidateIds)reviewedEvidence(state,id);
  if(next.requiresBriefChange&&!bool(opt['brief-change']))fail(`stage ${target} requires --brief-change=true for route '${state.route}'`);
  if(next.experimental&&!bool(opt.experimental))fail(`stage ${target} is experimental; pass --experimental=true explicitly`);
  state.stage=target;event(state,'unlock',{stage:target,name:next.name,reason,evidenceCandidateIds});save(statePath,state);console.log(JSON.stringify({stage:target,name:next.name,evidenceCandidateIds,unlocked:unlockedClasses(state)},null,2));
}else if(command==='summary'){
  routeInfo(state);
  const counts={};for(const c of Object.values(state.candidates))counts[c.status]=(counts[c.status]||0)+1;
  const stage=stageInfo(state);console.log(JSON.stringify({route:state.route,brief:state.brief,grammar:state.grammar,eliteId:state.eliteId,stage:state.stage,stageName:stage.name,unlocked:unlockedClasses(state),candidates:Object.keys(state.candidates).length,statusCounts:counts,events:state.events.length},null,2));
}else if(command==='validate'){
  const errs=validateState(state);console.log(JSON.stringify({ok:errs.length===0,errors:errs},null,2));if(errs.length)process.exit(1);
}else usage();
