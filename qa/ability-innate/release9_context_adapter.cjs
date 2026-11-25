// QA-only Release 9 patch. Apply only after Release 8 installer, not production.
// node release9_context_adapter.cjs <combined tree with R8 patch overlaid> <fresh output directory>
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const c={
  "contextAnchor": "    u32 battleProgressFlag : 1;\n",
  "contextField": "    /* MERCURY_QA_R9_CONTEXT_PROVIDER: per-battle, transient only. */\n    BOOL (*mercuryQARawInnateProvider)(BattleContext *, int, u16 [3]);\n\n",
  "ctorAnchor": "    MI_CpuClearFast(battleContext, sizeof(BattleContext));\n\n    BattleContext_Init(battleContext);",
  "ctorReplacement": "    MI_CpuClearFast(battleContext, sizeof(BattleContext));\n    battleContext->mercuryQARawInnateProvider = NULL;\n\n    BattleContext_Init(battleContext);",
  "oldDecl": "void Mercury_QA_SetRawInnateProvider(MercuryRawInnateProvider provider);",
  "newDecl": "void Mercury_QA_SetRawInnateProvider(BattleContext *battleCtx, MercuryRawInnateProvider provider);",
  "oldRaw": "/* MERCURY_QA_R8_RAW_INNATE_PROVIDER */\nstatic MercuryRawInnateProvider sMercuryQARawInnateProvider = NULL;\n\nvoid Mercury_QA_SetRawInnateProvider(MercuryRawInnateProvider provider)\n{\n    sMercuryQARawInnateProvider = provider;\n}\n\nstatic BOOL Mercury_QA_RawInnateContains(BattleContext *battleCtx, int battler, u16 ability)\n{\n    u16 slots[3] = { ABILITY_NONE, ABILITY_NONE, ABILITY_NONE };\n    int i;\n    if (battler < 0 || battler >= MAX_BATTLERS || ability == ABILITY_NONE\n        || sMercuryQARawInnateProvider == NULL\n        || !sMercuryQARawInnateProvider(battleCtx, battler, slots)) {\n        return FALSE;\n    }\n    for (i = 0; i < 3; i++) {\n        if (slots[i] == ability) {\n            return TRUE;\n        }\n    }\n    return FALSE;\n}\n\n",
  "newRaw": "/* MERCURY_QA_R8_RAW_INNATE_PROVIDER */\nvoid Mercury_QA_SetRawInnateProvider(BattleContext *battleCtx, MercuryRawInnateProvider provider)\n{\n    if (battleCtx != NULL) {\n        battleCtx->mercuryQARawInnateProvider = provider;\n    }\n}\n\nstatic BOOL Mercury_QA_RawInnateContains(BattleContext *battleCtx, int battler, u16 ability)\n{\n    u16 slots[3] = { ABILITY_NONE, ABILITY_NONE, ABILITY_NONE };\n    int i;\n    if (battleCtx == NULL || battler < 0 || battler >= MAX_BATTLERS || ability == ABILITY_NONE\n        || battleCtx->mercuryQARawInnateProvider == NULL\n        || !battleCtx->mercuryQARawInnateProvider(battleCtx, battler, slots)) {\n        return FALSE;\n    }\n    for (i = 0; i < 3; i++) {\n        if (slots[i] == ability) {\n            return TRUE;\n        }\n    }\n    return FALSE;\n}\n\n"
};
function apply(files,c){
 const check=(x,m)=>{if(!x)throw Error(m)};
 const once=(s,a,b)=>{check(s.split(a).length===2,"missing or repeated anchor: "+a.slice(0,70));return s.replace(a,()=>b)};
 check(!files.ctx.includes("MERCURY_QA_R9_CONTEXT_PROVIDER"),"already patched");
 check(files.lib.includes("MERCURY_QA_R8_EFFECTIVE_MEMBERSHIP")&&files.hdr.includes("MERCURY_QA_R8_EFFECTIVE_ABILITY_API"),"Release 8 source patch required");
 const ctx=once(files.ctx,c.contextAnchor,c.contextField+c.contextAnchor);
 const ctor=once(files.ctor,c.ctorAnchor,c.ctorReplacement);
 const hdr=once(files.hdr,c.oldDecl,c.newDecl);
 let lib=once(files.lib,c.oldRaw,c.newRaw);
 check(!lib.includes("sMercuryQARawInnateProvider"),"global provider survived");
 return {ctx,ctor,hdr,lib};
}
const [root,out]=process.argv.slice(2);
if(!root||!out||fs.existsSync(out))throw Error("fresh output required");
const paths={ctx:"include/battle/battle_context.h",ctor:"src/battle/battle_controller_player.c",hdr:"include/battle/battle_lib.h",lib:"src/battle/battle_lib.c"};
const files=Object.fromEntries(Object.entries(paths).map(([key,p])=>[key,fs.readFileSync(path.join(root,p),"utf8")]));
const next=apply(files,c);
fs.mkdirSync(out,{recursive:false});
for(const [key,relative] of Object.entries(paths)){const p=path.join(out,relative);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,next[key])}
const sha=s=>crypto.createHash("sha256").update(s).digest("hex");
fs.writeFileSync(path.join(out,"QA_CONTEXT_PATCH_REPORT.json"),JSON.stringify({status:"CONTEXT_PATCH_PREPARED_NOT_COMPILED",original:Object.fromEntries(Object.keys(paths).map(k=>[k,sha(files[k])])),patched:Object.fromEntries(Object.keys(paths).map(k=>[k,sha(next[k])])),production:false},null,2)+"\n");
