#!/usr/bin/env python3
"""MR10R5 — restore the remaining simple priority/KO-Speed family."""
from __future__ import annotations
import argparse, json
from pathlib import Path

IMPLEMENTED={
    "Frozen Soul":("ABILITY_MR_FROZEN_SOUL",322),
    "Adrenaline Rush":("ABILITY_MR_ADRENALINE_RUSH",332),
    "Stygian Rush":("ABILITY_MR_STYGIAN_RUSH",383),
    "Flaming Soul":("ABILITY_MR_FLAMING_SOUL",425),
}
TOKENS=tuple(v[0] for v in IMPLEMENTED.values())

def replace_once(path:Path,old:str,new:str,label:str)->None:
    text=path.read_text(encoding="utf-8")
    if new in text:return
    n=text.count(old)
    if n!=1:raise SystemExit(f"{label}: expected one match in {path}, found {n}")
    path.write_text(text.replace(old,new,1),encoding="utf-8")

def insert_before_once(path:Path,anchor:str,ins:str,marker:str,label:str)->None:
    text=path.read_text(encoding="utf-8")
    if marker in text:return
    n=text.count(anchor)
    if n!=1:raise SystemExit(f"{label}: expected one anchor in {path}, found {n}")
    path.write_text(text.replace(anchor,ins+anchor,1),encoding="utf-8")

def validate_partition(path:Path)->None:
    rows=json.loads(path.read_text(encoding="utf-8"))["abilities"]
    for name,(tok,aid) in IMPLEMENTED.items():
        m=[r for r in rows if r.get("id")==aid and r.get("token")==tok]
        if len(m)!=1:raise SystemExit(f"{name}: expected reconciled row {aid}, got {len(m)}")
        if m[0].get("runtime_enabled") is False or m[0].get("review_blocked") is True:
            raise SystemExit(f"{name}: not runtime-approved")

def patch_priority(root:Path)->None:
    path=root/"src/battle/battle_lib.c"
    anchor="""    if (battler1Priority == battler2Priority) {
"""
    ins="""    if (battler1Move != MOVE_NONE
        && battleCtx->battleMons[battler1].curHP
            == battleCtx->battleMons[battler1].maxHP) {
        if (battler1Ability == ABILITY_MR_FROZEN_SOUL
            && MOVE_DATA(battler1Move).type == TYPE_ICE) {
            battler1Priority++;
        }
        if (battler1Ability == ABILITY_MR_STYGIAN_RUSH
            && MOVE_DATA(battler1Move).type == TYPE_DARK) {
            battler1Priority++;
        }
        if (battler1Ability == ABILITY_MR_FLAMING_SOUL
            && MOVE_DATA(battler1Move).type == TYPE_FIRE) {
            battler1Priority++;
        }
    }

    if (battler2Move != MOVE_NONE
        && battleCtx->battleMons[battler2].curHP
            == battleCtx->battleMons[battler2].maxHP) {
        if (battler2Ability == ABILITY_MR_FROZEN_SOUL
            && MOVE_DATA(battler2Move).type == TYPE_ICE) {
            battler2Priority++;
        }
        if (battler2Ability == ABILITY_MR_STYGIAN_RUSH
            && MOVE_DATA(battler2Move).type == TYPE_DARK) {
            battler2Priority++;
        }
        if (battler2Ability == ABILITY_MR_FLAMING_SOUL
            && MOVE_DATA(battler2Move).type == TYPE_FIRE) {
            battler2Priority++;
        }
    }

"""
    insert_before_once(path,anchor,ins,"battler1Ability == ABILITY_MR_FROZEN_SOUL","R5 action priority")

    old="""            || (Battler_Ability(battleCtx, attacker) == ABILITY_CUTE_ANTECEDENCE
                && moveType == TYPE_FAIRY))) {
        priority++;
    }
"""
    new="""            || (Battler_Ability(battleCtx, attacker) == ABILITY_CUTE_ANTECEDENCE
                && moveType == TYPE_FAIRY)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_MR_FROZEN_SOUL
                && moveType == TYPE_ICE)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_MR_STYGIAN_RUSH
                && moveType == TYPE_DARK)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_MR_FLAMING_SOUL
                && moveType == TYPE_FIRE))) {
        priority++;
    }
"""
    replace_once(path,old,new,"R5 priority blocker helper")

def patch_ko_speed(root:Path)->None:
    path=root/"src/battle/battle_lib.c"
    anchor="""    case ABILITY_HAUNTING_FRENZY:
"""
    ins="""    case ABILITY_MR_ADRENALINE_RUSH:
        if (battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_SPEED]
            < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            *subscript = subscript_update_stat_stage;
            return TRUE;
        }
        break;

"""
    insert_before_once(path,anchor,ins,"case ABILITY_MR_ADRENALINE_RUSH:","Adrenaline Rush KO Speed")

def update_registry(path:Path)->None:
    rows=[x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for tok in TOKENS:
        if tok not in rows:rows.append(tok)
    path.write_text("\n".join(rows)+"\n",encoding="utf-8")

def validate(root:Path,registry:Path)->dict[str,bool]:
    lib=(root/"src/battle/battle_lib.c").read_text(encoding="utf-8")
    abilities=[x.strip() for x in (root/"generated/abilities.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    reg=set(registry.read_text(encoding="utf-8").splitlines())
    return {
        "frozen_soul_priority":"ABILITY_MR_FROZEN_SOUL" in lib and "moveType == TYPE_ICE" in lib,
        "stygian_rush_priority":"ABILITY_MR_STYGIAN_RUSH" in lib and "moveType == TYPE_DARK" in lib,
        "flaming_soul_priority":"ABILITY_MR_FLAMING_SOUL" in lib and "moveType == TYPE_FIRE" in lib,
        "adrenaline_rush_ko_speed":"case ABILITY_MR_ADRENALINE_RUSH:" in lib and "MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE" in lib,
        "registry_updated":all(t in reg for t in TOKENS),
        "ids_stable":all(len(abilities)>aid and abilities[aid]==tok for tok,aid in IMPLEMENTED.values()),
    }

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("--partition",type=Path,default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
    ap.add_argument("--implemented-registry",type=Path,required=True)
    ap.add_argument("--report",type=Path,default=Path("mr10r5-priority-ko.json"))
    a=ap.parse_args();root=a.pokeplatinum_root.resolve()
    validate_partition(a.partition.resolve())
    patch_priority(root)
    patch_ko_speed(root)
    update_registry(a.implemented_registry.resolve())
    checks=validate(root,a.implemented_registry.resolve())
    status="PASS" if all(checks.values()) else "FAIL"
    report={"gate":"MERCURY_MR10R5_PRIORITY_KO","status":status,"implemented":list(IMPLEMENTED),"implemented_count":len(IMPLEMENTED),"checks":checks}
    a.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    if status!="PASS":raise SystemExit("MR10R5 validation failed")

if __name__=="__main__":main()
