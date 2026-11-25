// QA-only offline source replay. Requires four existing clean Git checkouts.
// No clone, no build, no ROM, no upload. Run in a network-isolated environment.
// node release9_replay.cjs plan.json namespace.json mercury-checkout platinum-checkout hg-checkout community-checkout NEW-output-dir
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),cp=require("node:child_process");
function validatePlan(plan,ns){
 const check=(x,m)=>{if(!x)throw Error(m)};
 check(plan.schema==="mercury-release9-source-replay-plan"&&plan.steps.length===53,"plan shape");
 check(plan.steps[0].name==="Apply Mercury Platinum overlay"&&plan.steps.at(-2).name==="Rebase all runtime mechanics onto final 16-bit Ability IDs"&&plan.steps.at(-1).name==="Restore missing runtime batches R1 through R8 (shared implemented registry)","stage order");
 check(plan.steps.every(x=>typeof x.body==="string"&&x.body.length>0&&!/\b(?:sudo|git clone|make rom|curl|wget|apt-get)\b/.test(x.body)),"source-only stage");
 check((plan.steps.at(-1).body.match(/--implemented-registry mr10c-implemented-abilities.txt/g)||[]).length===8,"shared registry");
 check(ns.registry.length===1067&&new Set(ns.registry).size===1067,"registry");
 check(ns.keep_crosswalk.length===75&&ns.historical_crosswalk.length===125,"coverage targets");
 return true;
}
function validateRegistry(actual,implemented,ns){
 const check=(x,m)=>{if(!x)throw Error(m)};
 check(actual.length===ns.registry.length&&actual.every((x,i)=>x===ns.registry[i]),"final namespace differs");
 let tokens=new Set(implemented);check(tokens.size===implemented.length,"duplicate implemented tokens");
 check(implemented.every(t=>actual.includes(t)),"unknown implemented token");
 let required=[...ns.keep_crosswalk.map(x=>x.token),...ns.historical_crosswalk.map(x=>x.token)];
 check(required.every(t=>tokens.has(t)),"missing required implementation declaration");
 return {namespace:actual.length,implemented:tokens.size,required:new Set(required).size};
}
function blob(buf){return crypto.createHash("sha1").update("blob "+buf.length+"\0").update(buf).digest("hex")}
function readPinned(p,expected){let b=fs.readFileSync(p);if(blob(b)!==expected)throw Error("pinned artifact differs: "+p);return JSON.parse(b.toString("utf8"))}
const args=process.argv.slice(2);
if(args.length!==7)throw Error("seven paths required");
const [planFile,nsFile,m,p,h,c,outArg]=args;
const plan=readPinned(planFile,"a68c40c72b59d64bbb370504de505150137d944a"),ns=readPinned(nsFile,"d902d6ec26a43695a716f045dc880f5c1a3bd978");
validatePlan(plan,ns);
const repos={mercury:m,pokeplatinum:p,"hg-engine":h,"community-moves":c};
const out=path.resolve(outArg);if(fs.existsSync(out))throw Error("fresh output required");
const parent=fs.realpathSync(path.dirname(out));if(path.join(parent,path.basename(out))!==out)throw Error("output parent must resolve directly");
function git(root,...args){return cp.execFileSync("git",["-C",root,...args],{encoding:"utf8",maxBuffer:16*1024*1024}).trim()}
for(const [key,v] of Object.entries(repos)){
 let root=fs.realpathSync(v);repos[key]=root;
 if(out===root||out.startsWith(root+path.sep))throw Error("output inside source checkout");
 if(git(root,"rev-parse","HEAD")!==plan.pins[key])throw Error("wrong source commit: "+key);
 if(git(root,"status","--porcelain","--untracked-files=all"))throw Error("source checkout not clean: "+key);
}
fs.mkdirSync(out);const work=path.join(out,"work");fs.mkdirSync(work);const logs=path.join(out,"logs");fs.mkdirSync(logs);
const summary={status:"IN_PROGRESS",completed:[],failed:null,sourceOnly:true,nativeCertified:false};
const report=()=>fs.writeFileSync(path.join(out,"REPLAY_REPORT.json"),JSON.stringify(summary,null,2)+"\n");
function exportTree(key,dest){
 fs.mkdirSync(dest,{recursive:true});const tar=path.join(out,key+".tar");
 cp.execFileSync("git",["-C",repos[key],"archive","--format=tar","--output="+tar,plan.pins[key]],{stdio:"inherit"});
 cp.execFileSync("tar",["-xf",tar,"-C",dest],{stdio:"inherit"});fs.unlinkSync(tar);
}
try {
 report();exportTree("mercury",work);
 for(const key of ["pokeplatinum","hg-engine","community-moves"])exportTree(key,path.join(work,"vendor",key));
 for(const [i,step] of plan.steps.entries()){
  const filename=path.join(logs,String(i+1).padStart(2,"0")+".log");const fd=fs.openSync(filename,"w");
  summary.failed=step.name;report();
  let result;try{result=cp.spawnSync("bash",["-e","-u","-o","pipefail","-c",step.body],{cwd:work,stdio:["ignore",fd,fd],env:{...process.env,GIT_TERMINAL_PROMPT:"0",PYTHONDONTWRITEBYTECODE:"1"}})}finally{fs.closeSync(fd)}
  if(result.error||result.status!==0)throw Error("stage failed: "+step.name+"; see "+filename);
  summary.completed.push(step.name);summary.failed=null;report();
 }
 const lines=f=>fs.readFileSync(path.join(work,f),"utf8").split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
 summary.registry=validateRegistry(lines("vendor/pokeplatinum/generated/abilities.txt"),lines("mr10c-implemented-abilities.txt"),ns);
 // The historical reports are also checked by their own exact workflow commands.
 summary.status="SOURCE_REPLAY_PASS_NATIVE_UNTESTED";report();
} catch(e){summary.status="BLOCKED";summary.error=String(e);report();throw e}
