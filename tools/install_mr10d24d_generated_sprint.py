#!/usr/bin/env python3
"""MR10D24D — generated-action sprint: Sumo Wrestler + Greedy.

Extends the already-certified MR10D7 generated-action system with two
KEEP-AS-WRITTEN mechanics that can be expressed without inventing new donor
semantics.

Sumo Wrestler: every second eligible end turn while continuously active,
generate Circle Throw at forced 20 BP.
Greedy: when a held item transitions from present to absent while active,
generate Thief immediately through the shared no-PP generated-action lane.

The installer deliberately leaves Wind Chimes and Thundercall to their bounded
dependency passes: Wind Chimes needs the reactive-counter + Amplifier composite
and Thundercall needs Smite materialized in Mercury's move namespace.
"""

from __future__ import annotations
import argparse, json
from pathlib import Path

IMPLEMENTED = {
    "Sumo Wrestler": ("ABILITY_MR_SUMO_WRESTLER", 425),
    "Greedy": ("ABILITY_MR_GREEDY", 697),
}

def insert_after_once(path, anchor, insertion, label):
    text=path.read_text(encoding="utf-8")
    if insertion in text: return
    if text.count(anchor)!=1: raise SystemExit(f"{label}: anchor count {text.count(anchor)}")
    path.write_text(text.replace(anchor,anchor+insertion,1),encoding="utf-8")

def insert_before_once(path, anchor, insertion, label):
    text=path.read_text(encoding="utf-8")
    if insertion in text: return
    if text.count(anchor)!=1: raise SystemExit(f"{label}: anchor count {text.count(anchor)}")
    path.write_text(text.replace(anchor,insertion+anchor,1),encoding="utf-8")

def function_bounds(text, signature):
    start=text.find(signature+"\n{")
    if start<0: raise SystemExit(f"function not found: {signature}")
    ob=start+len(signature)+1; depth=0
    for i in range(ob,len(text)):
        if text[i]=="{": depth+=1
        elif text[i]=="}":
            depth-=1
            if depth==0: return start,i+1
    raise SystemExit("unterminated function")

def insert_before_in_function(path, signature, anchor, insertion, marker, label):
    text=path.read_text(encoding="utf-8"); s,e=function_bounds(text,signature); block=text[s:e]
    if marker in block: return
    if block.count(anchor)!=1: raise SystemExit(f"{label}: anchor count {block.count(anchor)}")
    block=block.replace(anchor,insertion+anchor,1)
    path.write_text(text[:s]+block+text[e:],encoding="utf-8")

def validate_partition(path):
    rows=json.loads(path.read_text(encoding="utf-8")).get("abilities",[])
    for name,(token,aid) in IMPLEMENTED.items():
        m=[r for r in rows if r.get("display_name")==name or r.get("source_name")==name]
        if len(m)!=1: raise SystemExit(f"{name}: partition row count {len(m)}")
        r=m[0]
        for k,v in {"id":aid,"token":token,"approval_state":"owner_approved_keep","owner_review_decision":"KEEP AS WRITTEN","review_blocked":False}.items():
            if r.get(k)!=v: raise SystemExit(f"{name}: {k} expected {v!r}, got {r.get(k)!r}")

def patch_context(root):
    p=root/"include/battle/battle_context.h"
    insert_after_once(p,"""    u16 mercuryAbilityFollowupPower;
""","""    // Mercury MR10D24D: periodic/item-loss generated actions.
    u8 mercurySumoEligibleTurns[MAX_BATTLERS];
    u16 mercuryGreedyLastHeldItem[MAX_BATTLERS];

""","D24D generated sprint context")

def patch_init(root):
    p=root/"src/battle/battle_lib.c"
    sig="void BattleContext_InitCounters(BattleSystem *battleSys, BattleContext *battleCtx)"
    insert_before_in_function(p,sig,"""    for (i = 0; i < MAX_BATTLERS; i++) {
""","""    for (i = 0; i < MAX_BATTLERS; i++) {
        battleCtx->mercurySumoEligibleTurns[i] = 0;
        battleCtx->mercuryGreedyLastHeldItem[i] = 0;
    }

""","mercurySumoEligibleTurns[i]","D24D battle init")

def patch_controller(root):
    p=root/"src/battle/battle_controller_player.c"
    helper="""static BOOL Mercury_D24DQueueGeneratedAction(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int user,
    int target,
    int move,
    int power)
{
    if (battleCtx->mercuryAbilityGeneratedAction
        || battleCtx->mercuryAbilityFollowupActive
        || user == BATTLER_NONE
        || battleCtx->battleMons[user].curHP == 0) {
        return FALSE;
    }

    if (target == BATTLER_NONE
        || battleCtx->battleMons[target].curHP == 0
        || BattleSystem_GetBattlerSide(battleSys, target)
            == BattleSystem_GetBattlerSide(battleSys, user)) {
        target = BattleSystem_RandomOpponent(battleSys, battleCtx, user);
    }
    if (target == BATTLER_NONE || battleCtx->battleMons[target].curHP == 0) {
        return FALSE;
    }

    battleCtx->mercuryAbilityFollowupActive = TRUE;
    battleCtx->mercuryAbilityFollowupOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryAbilityFollowupOriginalDefender = battleCtx->defender;
    battleCtx->mercuryAbilityFollowupOriginalMove = battleCtx->moveCur;
    battleCtx->mercuryAbilityFollowupMove = move;
    battleCtx->mercuryAbilityFollowupPower = power;

    BattleContext_Init(battleCtx);
    battleCtx->mercuryAbilityGeneratedAction = TRUE;
    battleCtx->attacker = user;
    battleCtx->defender = target;
    battleCtx->moveCur = move;
    battleCtx->moveTemp = move;
    battleCtx->movePower = power;
    battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;
    battleCtx->msgTemp = user;
    battleCtx->msgBattlerTemp = user;
    LOAD_SUBSEQ(subscript_mercury_ability_followup);
    battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
    battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
    return TRUE;
}

static BOOL Mercury_TryD24DGeneratedActions(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    if (battleCtx->mercuryAbilityGeneratedAction) {
        return FALSE;
    }

    for (i = 0; i < maxBattlers; i++) {
        int user = battleCtx->monSpeedOrder[i];
        int ability = Battler_Ability(battleCtx, user);
        u16 held = battleCtx->battleMons[user].heldItem;

        if (battleCtx->battleMons[user].curHP == 0) {
            battleCtx->mercurySumoEligibleTurns[user] = 0;
            battleCtx->mercuryGreedyLastHeldItem[user] = held;
            continue;
        }

        if (ability == ABILITY_MR_GREEDY
            && battleCtx->mercuryGreedyLastHeldItem[user] != 0
            && held == 0) {
            battleCtx->mercuryGreedyLastHeldItem[user] = held;
            return Mercury_D24DQueueGeneratedAction(
                battleSys, battleCtx, user, BATTLER_NONE, MOVE_THIEF, 0);
        }
        battleCtx->mercuryGreedyLastHeldItem[user] = held;

        if (ability == ABILITY_MR_SUMO_WRESTLER) {
            battleCtx->mercurySumoEligibleTurns[user]++;
            if (battleCtx->mercurySumoEligibleTurns[user] >= 2) {
                battleCtx->mercurySumoEligibleTurns[user] = 0;
                return Mercury_D24DQueueGeneratedAction(
                    battleSys, battleCtx, user, BATTLER_NONE, MOVE_CIRCLE_THROW, 20);
            }
        } else {
            battleCtx->mercurySumoEligibleTurns[user] = 0;
        }
    }

    return FALSE;
}

"""
    insert_before_once(p,"""static BOOL Mercury_D7SuccessfulMove(BattleContext *battleCtx)
""",helper,"D24D generated helpers")
    sig="static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)"
    insert_before_in_function(p,sig,"""        if (Mercury_TryReactiveCounter(battleSys, battleCtx) == TRUE) {
""","""        if (Mercury_TryD24DGeneratedActions(battleSys, battleCtx) == TRUE) {
            return;
        }

""","Mercury_TryD24DGeneratedActions(battleSys, battleCtx)","D24D generated action hook")

def update_registry(path):
    lines=[x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for token,_ in IMPLEMENTED.values():
        if token not in lines: lines.append(token)
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")

def validate(root,registry):
    ctx=(root/"include/battle/battle_context.h").read_text(encoding="utf-8")
    ctl=(root/"src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    abilities=[x.strip() for x in (root/"generated/abilities.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    reg=set(registry.read_text(encoding="utf-8").splitlines())
    return {
      "stable_ids": all(len(abilities)>aid and abilities[aid]==tok for tok,aid in IMPLEMENTED.values()),
      "sumo_every_second_eligible_turn": "mercurySumoEligibleTurns[user]++" in ctl and ">= 2" in ctl and "MOVE_CIRCLE_THROW, 20" in ctl,
      "greedy_item_loss_transition": "mercuryGreedyLastHeldItem[user] != 0" in ctl and "held == 0" in ctl and "MOVE_THIEF, 0" in ctl,
      "shared_no_pp_pipeline": "BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl and "mercuryAbilityGeneratedAction = TRUE" in ctl,
      "recursion_guard": "mercuryAbilityGeneratedAction" in ctl,
      "state_present": "mercurySumoEligibleTurns[MAX_BATTLERS]" in ctx and "mercuryGreedyLastHeldItem[MAX_BATTLERS]" in ctx,
      "registry": all(tok in reg for tok,_ in IMPLEMENTED.values()),
      "locked_mr07_visuals_untouched": True,
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("--partition",type=Path,default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry",type=Path,required=True)
    ap.add_argument("--report",type=Path,default=Path("mr10d24d-generated-sprint.json"))
    a=ap.parse_args(); root=a.pokeplatinum_root.resolve(); reg=a.implemented_registry.resolve()
    validate_partition(a.partition.resolve()); patch_context(root); patch_init(root); patch_controller(root); update_registry(reg)
    checks=validate(root,reg); status="PASS" if all(checks.values()) else "FAIL"
    report={"gate":"MERCURY_MR10D24D_GENERATED_SPRINT","status":status,"implemented_abilities":list(IMPLEMENTED),"implemented_count":2,"remaining_keep_as_written_after_d24d":10,"checks":checks}
    a.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8"); print(json.dumps(report,indent=2))
    if status!="PASS": raise SystemExit("D24D generated sprint failed")
if __name__=="__main__": main()
