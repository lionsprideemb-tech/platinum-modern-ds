#!/usr/bin/env python3
"""MR10R1 — restore first missing historical Ability runtime batch.

This batch ports ten low-risk mechanics whose exact Elite Redux v2.65 beta
semantics can be expressed on existing Mercury/Platinum hooks without adding a
new persistent battle subsystem.
"""

from __future__ import annotations
import argparse, json
from pathlib import Path

IMPLEMENTED = {
    "Chrome Coat": ("ABILITY_CHROME_COAT", 371),
    "Sharp Edges": ("ABILITY_DOUBLE_IRON_BARBS", 391),
    "Early Grave": ("ABILITY_EARLY_GRAVE", 400),
    "Fighter": ("ABILITY_FIGHTER", 420),
    "Fire Scales": ("ABILITY_FIRE_SCALES", 421),
    "Gladiator": ("ABILITY_GLADIATOR", 439),
    "Higher Rank": ("ABILITY_HIGHER_RANK", 450),
    "Purgatory": ("ABILITY_PURGATORY", 536),
    "Shiny Lightning": ("ABILITY_SHINY_LIGHTNING", 566),
    "Tidal Rush": ("ABILITY_WATER_GALE_WINGS", 616),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text=path.read_text(encoding="utf-8")
    if new in text: return
    count=text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old,new,1),encoding="utf-8")

def insert_before_once(path: Path, anchor: str, ins: str, marker: str, label: str) -> None:
    text=path.read_text(encoding="utf-8")
    if marker in text: return
    count=text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor,ins+anchor,1),encoding="utf-8")

def insert_after_once(path: Path, anchor: str, ins: str, marker: str, label: str) -> None:
    text=path.read_text(encoding="utf-8")
    if marker in text: return
    count=text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor,anchor+ins,1),encoding="utf-8")

def validate_partition(path: Path) -> None:
    rows=json.loads(path.read_text(encoding="utf-8"))["abilities"]
    for name,(tok,aid) in IMPLEMENTED.items():
        m=[x for x in rows if x.get("display_name")==name]
        if len(m)!=1:
            raise SystemExit(f"{name}: expected exactly one partition row, got {len(m)}")
        row=m[0]
        if row.get("id")!=aid or row.get("token")!=tok:
            raise SystemExit(f"{name}: ID/token mismatch {row.get('id')} {row.get('token')}")
        if row.get("runtime_enabled") is False:
            raise SystemExit(f"{name}: runtime-disabled in full partition")

def patch_speed_and_priority(root: Path) -> None:
    path=root/"src/battle/battle_lib.c"

    anchor="""    battler1Speed = battleCtx->battleMons[battler1].speed * sStatStageBoosts[battler1SpeedStage].numerator / sStatStageBoosts[battler1SpeedStage].denominator;
    battler2Speed = battleCtx->battleMons[battler2].speed * sStatStageBoosts[battler2SpeedStage].numerator / sStatStageBoosts[battler2SpeedStage].denominator;

"""
    ins="""    if (battler1Ability == ABILITY_CHROME_COAT) {
        battler1Speed = battler1Speed * 90 / 100;
    }
    if (battler2Ability == ABILITY_CHROME_COAT) {
        battler2Speed = battler2Speed * 90 / 100;
    }

"""
    insert_after_once(path,anchor,ins,"battler1Ability == ABILITY_CHROME_COAT","Chrome Coat Speed penalty")

    priority_anchor="""        battler1Priority = MOVE_DATA(battler1Move).priority;
        battler2Priority = MOVE_DATA(battler2Move).priority;
"""
    priority_ins="""
        if (battler1Move != MOVE_NONE
            && battleCtx->battleMons[battler1].curHP == battleCtx->battleMons[battler1].maxHP) {
            if (battler1Ability == ABILITY_EARLY_GRAVE
                && MOVE_DATA(battler1Move).type == TYPE_GHOST) {
                battler1Priority++;
            }
            if (battler1Ability == ABILITY_WATER_GALE_WINGS
                && MOVE_DATA(battler1Move).type == TYPE_WATER) {
                battler1Priority++;
            }
        }

        if (battler2Move != MOVE_NONE
            && battleCtx->battleMons[battler2].curHP == battleCtx->battleMons[battler2].maxHP) {
            if (battler2Ability == ABILITY_EARLY_GRAVE
                && MOVE_DATA(battler2Move).type == TYPE_GHOST) {
                battler2Priority++;
            }
            if (battler2Ability == ABILITY_WATER_GALE_WINGS
                && MOVE_DATA(battler2Move).type == TYPE_WATER) {
                battler2Priority++;
            }
        }
"""
    insert_after_once(path,priority_anchor,priority_ins,"ABILITY_WATER_GALE_WINGS","Early Grave/Tidal Rush priority")


    helper_old="""    if (Battler_Ability(battleCtx, attacker) == ABILITY_GALE_WINGS
        && battleCtx->battleMons[attacker].curHP
            == battleCtx->battleMons[attacker].maxHP
        && moveType == TYPE_FLYING) {
        priority++;
    }
"""
    helper_new="""    if (battleCtx->battleMons[attacker].curHP
            == battleCtx->battleMons[attacker].maxHP
        && ((Battler_Ability(battleCtx, attacker) == ABILITY_GALE_WINGS
                && moveType == TYPE_FLYING)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_EARLY_GRAVE
                && moveType == TYPE_GHOST)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_WATER_GALE_WINGS
                && moveType == TYPE_WATER))) {
        priority++;
    }
"""
    replace_once(path,helper_old,helper_new,"Early Grave/Tidal Rush priority helper")

def patch_damage(root: Path) -> None:
    path=root/"src/battle/battle_lib.c"

    offense_anchor="""    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE
"""
    offense="""    if (attackerParams.ability == ABILITY_FIGHTER
        && moveType == TYPE_FIGHTING && movePower) {
        movePower = movePower
            * (attackerParams.curHP <= attackerParams.maxHP / 3 ? 150 : 120)
            / 100;
    }

    if (attackerParams.ability == ABILITY_GLADIATOR
        && moveType == TYPE_FIGHTING && movePower) {
        movePower = movePower
            * (attackerParams.curHP <= attackerParams.maxHP / 3 ? 180 : 130)
            / 100;
    }

    if (attackerParams.ability == ABILITY_PURGATORY
        && moveType == TYPE_GHOST && movePower) {
        movePower = movePower
            * (attackerParams.curHP <= attackerParams.maxHP / 3 ? 180 : 130)
            / 100;
    }

    if (attackerParams.ability == ABILITY_HIGHER_RANK
        && MOVE_DATA(move).priority > 0 && movePower) {
        movePower = movePower * 120 / 100;
    }

"""
    insert_before_once(path,offense_anchor,offense,"attackerParams.ability == ABILITY_GLADIATOR","restored offensive scalars")

    defensive_anchor="""    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
"""
    defensive="""    if (moveClass == CLASS_SPECIAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_FIRE_SCALES) == TRUE) {
        damage /= 2;
    }

    if (moveClass == CLASS_SPECIAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_CHROME_COAT) == TRUE) {
        damage = damage * 60 / 100;
    }

"""
    insert_before_once(path,defensive_anchor,defensive,"ABILITY_CHROME_COAT) == TRUE","Fire Scales/Chrome Coat special reduction")

def patch_sharp_edges(root: Path) -> None:
    path=root/"src/battle/battle_lib.c"
    anchor="""    case ABILITY_ROUGH_SKIN:
"""
    ins="""    case ABILITY_DOUBLE_IRON_BARBS:
        if (ATTACKING_MON.curHP
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_MAGIC_GUARD
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (battleCtx->battleStatusMask & SYSCTL_FIRST_OF_MULTI_TURN) == FALSE
            && (battleCtx->battleStatusMask2 & SYSCTL_UTURN_ACTIVE) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)) {
            battleCtx->hpCalcTemp =
                BattleSystem_Divide(ATTACKING_MON.maxHP * -1, 6);
            battleCtx->msgBattlerTemp = battleCtx->attacker;
            *subscript = subscript_rough_skin;
            result = TRUE;
        }
        break;

"""
    insert_before_once(path,anchor,ins,"case ABILITY_DOUBLE_IRON_BARBS:","Sharp Edges contact recoil")

def patch_accuracy(root: Path) -> None:
    path=root/"src/battle/battle_controller_player.c"
    anchor="""    if (Battler_Ability(battleCtx, attacker) == ABILITY_COMPOUND_EYES) {
        hitRate = hitRate * 130 / 100;
    }

"""
    ins="""    if (Battler_Ability(battleCtx, attacker) == ABILITY_SHINY_LIGHTNING) {
        if (move == MOVE_THUNDER) {
            hitRate = 100;
        } else {
            hitRate = hitRate * 120 / 100;
        }
    }

"""
    insert_after_once(path,anchor,ins,"ABILITY_SHINY_LIGHTNING","Shiny Lightning accuracy")

def update_registry(path: Path) -> None:
    lines=[x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for tok in TOKENS:
        if tok not in lines: lines.append(tok)
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")

def validate(root: Path, registry: Path) -> dict[str,bool]:
    lib=(root/"src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl=(root/"src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    abilities=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
    reg=set(registry.read_text().splitlines())
    checks={
        "chrome_coat_speed_90":"ABILITY_CHROME_COAT" in lib and "battler1Speed = battler1Speed * 90 / 100;" in lib,
        "chrome_coat_special_60":"damage = damage * 60 / 100;" in lib,
        "sharp_edges_one_sixth":"ABILITY_DOUBLE_IRON_BARBS" in lib and "ATTACKING_MON.maxHP * -1, 6" in lib,
        "early_grave_priority":"ABILITY_EARLY_GRAVE" in lib and "TYPE_GHOST" in lib,
        "tidal_rush_priority":"ABILITY_WATER_GALE_WINGS" in lib and "TYPE_WATER" in lib,
        "priority_blocker_helper_restored":"Mercury_CurrentMovePriority" in lib and "ABILITY_WATER_GALE_WINGS" in lib,
        "fighter_scalars":"ABILITY_FIGHTER" in lib and "? 150 : 120" in lib,
        "gladiator_scalars":"ABILITY_GLADIATOR" in lib and "? 180 : 130" in lib,
        "purgatory_scalars":"ABILITY_PURGATORY" in lib and "moveType == TYPE_GHOST" in lib,
        "fire_scales_half_special":"ABILITY_FIRE_SCALES" in lib and "damage /= 2;" in lib,
        "higher_rank_priority_power":"ABILITY_HIGHER_RANK" in lib and "MOVE_DATA(move).priority > 0" in lib,
        "shiny_lightning_accuracy":"ABILITY_SHINY_LIGHTNING" in ctl and "move == MOVE_THUNDER" in ctl,
        "registry_updated":all(tok in reg for tok in TOKENS),
        "ids_stable":all(len(abilities)>aid and abilities[aid]==tok for tok,aid in (v for v in IMPLEMENTED.values())),
    }
    return checks

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("--partition",type=Path,default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
    ap.add_argument("--implemented-registry",type=Path,required=True)
    ap.add_argument("--report",type=Path,default=Path("mr10r1-missing-scalar-priority.json"))
    a=ap.parse_args()
    root=a.pokeplatinum_root.resolve()
    validate_partition(a.partition.resolve())
    patch_speed_and_priority(root)
    patch_damage(root)
    patch_sharp_edges(root)
    patch_accuracy(root)
    update_registry(a.implemented_registry.resolve())
    checks=validate(root,a.implemented_registry.resolve())
    status="PASS" if all(checks.values()) else "FAIL"
    report={"gate":"MERCURY_MR10R1_MISSING_SCALAR_PRIORITY","status":status,"implemented":list(IMPLEMENTED),"implemented_count":len(IMPLEMENTED),"checks":checks}
    a.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if status!="PASS": raise SystemExit("MR10R1 validation failed")

if __name__=="__main__":
    main()
