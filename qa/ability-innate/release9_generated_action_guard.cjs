// Candidate cross-family recursion guard. QA only; ordering and cross-trigger policy require acceptance.
// node release9_generated_action_guard.cjs <combined source tree> <fresh output dir>
const fs=require("node:fs"),path=require("node:path");
const edits=[
  {
    "file": "src/battle/battle_controller_player.c",
    "source": 0,
    "old": "    if (battleCtx->mercuryAbilityGeneratedAction\n        || battleCtx->attacker == BATTLER_NONE\n        || battleCtx->moveCur == MOVE_NONE\n        || Mercury_D7SuccessfulMove(battleCtx) == FALSE",
    "new": "    if (battleCtx->mercuryAbilityGeneratedAction\n        || battleCtx->mercuryR7GeneratedAction\n        || battleCtx->attacker == BATTLER_NONE\n        || battleCtx->moveCur == MOVE_NONE\n        || Mercury_D7SuccessfulMove(battleCtx) == FALSE"
  },
  {
    "file": "src/battle/battle_lib.c",
    "source": 1,
    "old": "        if (qualifies\n            && battleCtx->mercuryAbilityGeneratedAction == FALSE\n            && battleCtx->attacker != BATTLER_NONE",
    "new": "        if (qualifies\n            && battleCtx->mercuryAbilityGeneratedAction == FALSE\n            && battleCtx->mercuryR7GeneratedAction == FALSE\n            && battleCtx->attacker != BATTLER_NONE"
  },
  {
    "file": "src/battle/battle_controller_player.c",
    "source": 1,
    "old": "    if (battleCtx->mercuryAbilityGeneratedAction) {\n        return FALSE;\n    }\n\n    for (i = 0; i < maxBattlers; i++) {",
    "new": "    if (battleCtx->mercuryAbilityGeneratedAction || battleCtx->mercuryR7GeneratedAction) {\n        return FALSE;\n    }\n\n    for (i = 0; i < maxBattlers; i++) {"
  },
  {
    "file": "src/battle/battle_controller_player.c",
    "source": 2,
    "old": "    if (battleCtx->mercuryR7GeneratedAction) {\n        return FALSE;\n    }\n\n    for (int user = 0; user < MAX_BATTLERS; user++) {",
    "new": "    if (battleCtx->mercuryR7GeneratedAction || battleCtx->mercuryAbilityGeneratedAction) {\n        return FALSE;\n    }\n\n    for (int user = 0; user < MAX_BATTLERS; user++) {"
  },
  {
    "file": "src/battle/battle_lib.c",
    "source": 2,
    "old": "            && battleCtx->mercuryR7GeneratedAction == FALSE) {\n            int user = battleCtx->defender;\n            if (battleCtx->mercuryR7ReactivePending[user] < 9)",
    "new": "            && battleCtx->mercuryR7GeneratedAction == FALSE\n            && battleCtx->mercuryAbilityGeneratedAction == FALSE) {\n            int user = battleCtx->defender;\n            if (battleCtx->mercuryR7ReactivePending[user] < 9)"
  },
  {
    "file": "src/battle/battle_controller_player.c",
    "source": 3,
    "old": "            && Battler_Ability(battleCtx,battleCtx->attacker)==ABILITY_ANGELS_WRATH\n            && battleCtx->mercuryR7GeneratedAction==FALSE\n            && (battleCtx->moveStatusFlags&MOVE_STATUS_NO_EFFECTS)==FALSE)",
    "new": "            && Battler_Ability(battleCtx,battleCtx->attacker)==ABILITY_ANGELS_WRATH\n            && battleCtx->mercuryR7GeneratedAction==FALSE\n            && battleCtx->mercuryAbilityGeneratedAction==FALSE\n            && (battleCtx->moveStatusFlags&MOVE_STATUS_NO_EFFECTS)==FALSE)"
  }
];
function patch(files,edits){
 const next={...files};for(const e of edits){let s=next[e.file];if(!s||s.includes(e.new)||s.split(e.old).length!==2)throw Error("missing, duplicate, or already patched gate: "+e.file);next[e.file]=s.replace(e.old,()=>e.new)}return next;
}
const [root,out]=process.argv.slice(2);if(!root||!out||fs.existsSync(out))throw Error("fresh output required");
const files=Object.fromEntries([...new Set(edits.map(e=>e.file))].map(p=>[p,fs.readFileSync(path.join(root,p),"utf8")]));
const next=patch(files,edits);fs.mkdirSync(out,{recursive:false});
for(const [p,s] of Object.entries(next)){const dest=path.join(out,p);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,s)}
console.log("Prepared six candidate cross-family start gates; native validation and policy acceptance pending.");
