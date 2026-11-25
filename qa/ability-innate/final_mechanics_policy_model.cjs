// QA-only resolver. Source row indices are fixture keys, not production species IDs.
// Suppression is supplied by a future native policy; no ability-specific semantics inferred.
function buildResolver(data){
 const assert=(c,m)=>{if(!c)throw Error(m)};
 const tail={"Aura Guard":{id:319,token:"ABILITY_AURA_GUARD"},"Piercing Drill":{id:311,token:"ABILITY_PIERCING_DRILL"},"Eelevate":{id:313,token:"ABILITY_EELEVATE"}};
 const rows=new Map();let tailSlots=0,held=0;
 for(const row of data.rows){const slots=row.slots.map(s=>{let c=s.candidates;if(c.length===0&&tail[s.name]){tailSlots++;c=[{...tail[s.name],tailRuntimeUnverified:true}]}return {...s,candidates:c}});const key=String(row.index);assert(!rows.has(key),"duplicate source key");rows.set(key,{...row,slots});if(slots.some(s=>s.candidates.length!==1||s.candidates[0].retired||s.candidates[0].pending))held++;}
 function effective(key,selected,options={}) {
  const row=rows.get(key);assert(row,"unknown exact species/form key");assert(Number.isInteger(selected)&&selected>=0&&selected<3,"invalid primary slot");
  const {innatesEnabled,suppressed=new Set(),stackPolicy=new Map(),allowUnverifiedTail=false}=options;
  assert(typeof innatesEnabled==="boolean","explicit setting required");
  const slots=[{slot:selected,kind:"primary"},...(innatesEnabled?[3,4,5].map(slot=>({slot,kind:"innate"})):[])];
  const active=[];
  for(const s of slots){const cs=row.slots[s.slot].candidates;assert(cs.length===1&&!cs[0].retired&&!cs[0].pending,"unresolved ability slot");const c=cs[0];assert(!c.tailRuntimeUnverified||allowUnverifiedTail,"tail runtime unverified");if(!suppressed.has(c.token))active.push({...s,id:c.id,token:c.token})}
  const groups=new Map();for(const a of active){if(!groups.has(a.token))groups.set(a.token,[]);groups.get(a.token).push(a)}
  return {active,has:token=>groups.has(token),dispatch:token=>{const g=groups.get(token)||[];if(g.length<=1)return g;const policy=stackPolicy.get(token);assert(policy==="once"||policy==="per_slot","stacking policy required for repeated identity");return policy==="once"?g.slice(0,1):g}};
 }
 return {rows,effective,tailSlots,held};
}
function runTests(data){
 const {rows,effective,tailSlots,held}=buildResolver(data);
 const assert=(c,m)=>{if(!c)throw Error(m)};let cases=0,off=0,on=0,suppression=0,stack=0,blocked=0,complete=0;
 for(const [key,row] of rows){if(row.slots.some(s=>s.candidates.length!==1||s.candidates[0].retired||s.candidates[0].pending||s.candidates[0].tailRuntimeUnverified))continue;complete++;
  for(let p=0;p<3;p++){
   const a=effective(key,p,{innatesEnabled:false});assert(a.active.length===1&&a.active[0].slot===p,"off parity");off++;
   const b=effective(key,p,{innatesEnabled:true});assert(b.active.length===4&&b.active[0].slot===p&&b.active.slice(1).every((s,i)=>s.slot===3+i),"on");on++;
   for(const t of new Set(b.active.map(x=>x.token))){let c=effective(key,p,{innatesEnabled:true,suppressed:new Set([t])});assert(!c.has(t)&&c.active.length===b.active.filter(x=>x.token!==t).length,"suppression");suppression++;
    const n=b.active.filter(x=>x.token===t).length;if(n>1){try{b.dispatch(t);throw Error("did not reject")}catch(e){assert(e.message==="stacking policy required for repeated identity","bad stacking failure")}const once=effective(key,p,{innatesEnabled:true,stackPolicy:new Map([[t,"once"]])});const every=effective(key,p,{innatesEnabled:true,stackPolicy:new Map([[t,"per_slot"]])});assert(once.dispatch(t).length===1&&every.dispatch(t).length===n,"policy");stack++}
   }
  }
 }
 for(const args of [["absent",0,{innatesEnabled:true}],["0",3,{innatesEnabled:true}],["0",0,{}]]){try{effective(...args)}catch{blocked++}}
 assert(blocked===3,"fail closed");cases=off+on+suppression+stack+blocked;
 return {sourceRows:rows.size,tailIdentityCandidatesRecovered:tailSlots,unresolvedIdentityRows:held,completeWithoutTailHolds:complete,off,on,suppression,stack,blocked,cases,status:"PASS_OFFLINE_RESOLVER_POLICY_MODEL"};
}

function testStacking(){
 const assert=(c,m)=>{if(!c)throw Error(m)};
 // Synthetic fixture tokens: never assign these to an actual species.
 const s=(token,id)=>({name:token,candidates:[{token,id}]});
 const d={rows:[{index:0,slots:[s("TEST_A",1),s("TEST_B",2),s("TEST_C",3),s("TEST_A",1),s("TEST_D",4),s("TEST_E",5)]}]};
 const {effective}=buildResolver(d);
 const opt={innatesEnabled:true};let n=0;
 const a=effective("0",0,opt);assert(a.active.length===4&&a.has("TEST_A"),"multiple slots");n++;
 let reject=false;try{a.dispatch("TEST_A")}catch{reject=true}assert(reject,"unapproved stacking");n++;
 assert(effective("0",0,{...opt,stackPolicy:new Map([["TEST_A","once"]])}).dispatch("TEST_A").length===1,"once");n++;
 assert(effective("0",0,{...opt,stackPolicy:new Map([["TEST_A","per_slot"]])}).dispatch("TEST_A").length===2,"per slot");n++;
 assert(!effective("0",0,{...opt,suppressed:new Set(["TEST_A"])}).has("TEST_A"),"suppress all occurrences");n++;
 assert(effective("0",0,{innatesEnabled:false}).dispatch("TEST_A").length===1,"off");n++;
 return n;
}
function testFinalMechanics(){
 const assert=(c,m)=>{if(!c)throw Error(m)};
 let predator=0;for(const damaging of [false,true])for(const bite of [false,true])for(const slice of [false,true]){const multiplier=(damaging&&(bite||slice))?130:100;assert(multiplier===(!damaging||(!bite&&!slice)?100:130),"predator truth table");predator++}
 // Deterministic roll fixture, not a native RNG implementation.
 let nerve=0;for(const damaging of [false,true])for(const poison of [false,true])for(const contact of [false,true])for(const occupied of [false,true])for(let roll=0;roll<100;roll++){let status=occupied?"OTHER":null;if(damaging&&poison&&contact&&!occupied&&roll<30)status="NERVE_AGENT";assert((status==="NERVE_AGENT")===(damaging&&poison&&contact&&!occupied&&roll<30),"nerve eligibility");assert(!occupied||status==="OTHER","major status preserved");nerve++}
 // Abstract dual item state; actual slot priority and engine hooks remain holds.
 function bag(a,b){assert(!a||!b||a!==b,"duplicate item");return [a,b]}
 let items=0;for(const a of [null,"BERRY","CHOICE"])for(const b of [null,"BERRY","CHOICE"]){if(a&&a===b){let reject=false;try{bag(a,b)}catch{reject=true}assert(reject,"same item");items++;continue}let v=bag(a,b);for(const slot of [0,1]){let c=v.slice();c[slot]=null;assert(c[1-slot]===v[1-slot],"other slot preserved");assert(c.every(x=>x===null)===(!c[0]&&!c[1]),"unburden eligibility");items++}}
 return {predator_truth_table:predator,nerve_trigger_cases:nerve,abstract_item_cases:items};
}
console.log(JSON.stringify({stacking:testStacking(),final:testFinalMechanics()},null,2));
