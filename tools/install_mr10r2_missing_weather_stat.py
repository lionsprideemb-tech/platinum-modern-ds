#!/usr/bin/env python3
"""MR10R2 — restore weather/stat historical Ability batch.

Ports seven exact Elite Redux v2.65 beta mechanics using already-present
Platinum/Mercury weather, damage-stat, accuracy, switch-in, and KO hooks.
"""

from __future__ import annotations
import argparse, json
from pathlib import Path

IMPLEMENTED = {
    "Ectoplasm": ("ABILITY_ECTOPLASM", 402),
    "Ethereal Rush": ("ABILITY_ETHEREAL_RUSH", 413),
    "Headstrong": ("ABILITY_HEADSTRONG", 448),
    "Hubris": ("ABILITY_HUBRIS", 453),
    "Raging Storm": ("ABILITY_RAGING_STORM", 547),
    "Smokey Maneuvers": ("ABILITY_SMOKEY_MANEUVERS", 570),
    "Thermal Slide": ("ABILITY_THERMAL_SLIDE", 598),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text=path.read_text(encoding="utf-8")
    if new in text:
        return
    count=text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old,new,1),encoding="utf-8")

def insert_after_once(path: Path, anchor: str, ins: str, marker: str, label: str) -> None:
    text=path.read_text(encoding="utf-8")
    if marker in text:
        return
    count=text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor,anchor+ins,1),encoding="utf-8")

def insert_before_once(path: Path, anchor: str, ins: str, marker: str, label: str) -> None:
    text=path.read_text(encoding="utf-8")
    if marker in text:
        return
    count=text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor,ins+anchor,1),encoding="utf-8")

def validate_partition(path: Path) -> None:
    rows=json.loads(path.read_text(encoding="utf-8"))["abilities"]
    for name,(tok,aid) in IMPLEMENTED.items():
        m=[x for x in rows if x.get("display_name")==name]
        if len(m)!=1:
            raise SystemExit(f"{name}: expected one partition row, got {len(m)}")
        row=m[0]
        if row.get("id")!=aid or row.get("token")!=tok:
            raise SystemExit(f"{name}: ID/token mismatch")
        if row.get("exact_effect") in (None,"RESTORE_PENDING_EXACT_SEMANTICS"):
            raise SystemExit(f"{name}: exact semantics not recovered")

def patch_damage_stats(root: Path) -> None:
    path=root/"src/battle/battle_lib.c"
    anchor="""    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
"""
    ins="""
    if (attackerParams.ability == ABILITY_ECTOPLASM
        && (fieldConditions & FIELD_CONDITION_DEEP_FOG)) {
        if (attackStat >= spAttackStat) {
            attackStat = attackStat * 15 / 10;
        } else {
            spAttackStat = spAttackStat * 15 / 10;
        }
    }

    if (attackerParams.ability == ABILITY_RAGING_STORM
        && (fieldConditions & FIELD_CONDITION_RAINING)) {
        if (attackStat >= spAttackStat) {
            attackStat = attackStat * 15 / 10;
        } else {
            spAttackStat = spAttackStat * 15 / 10;
        }
    }
"""
    insert_after_once(path,anchor,ins,"attackerParams.ability == ABILITY_ECTOPLASM","Ectoplasm/Raging Storm attacking-stat boosts")

def patch_speed(root: Path) -> None:
    path=root/"src/battle/battle_lib.c"
    anchor="""    battler1Speed = battleCtx->battleMons[battler1].speed * sStatStageBoosts[battler1SpeedStage].numerator / sStatStageBoosts[battler1SpeedStage].denominator;
    battler2Speed = battleCtx->battleMons[battler2].speed * sStatStageBoosts[battler2SpeedStage].numerator / sStatStageBoosts[battler2SpeedStage].denominator;

"""
    ins="""    if (battler1Ability == ABILITY_ETHEREAL_RUSH
        && (battleCtx->fieldConditionsMask & FIELD_CONDITION_DEEP_FOG)) {
        battler1Speed = battler1Speed * 15 / 10;
    }
    if (battler2Ability == ABILITY_ETHEREAL_RUSH
        && (battleCtx->fieldConditionsMask & FIELD_CONDITION_DEEP_FOG)) {
        battler2Speed = battler2Speed * 15 / 10;
    }

    if (battler1Ability == ABILITY_THERMAL_SLIDE
        && (battleCtx->fieldConditionsMask
            & (FIELD_CONDITION_SUNNY | FIELD_CONDITION_HAILING))) {
        battler1Speed = battler1Speed * 15 / 10;
    }
    if (battler2Ability == ABILITY_THERMAL_SLIDE
        && (battleCtx->fieldConditionsMask
            & (FIELD_CONDITION_SUNNY | FIELD_CONDITION_HAILING))) {
        battler2Speed = battler2Speed * 15 / 10;
    }

"""
    insert_after_once(path,anchor,ins,"battler1Ability == ABILITY_ETHEREAL_RUSH","weather Speed boosts")

def patch_evasion(root: Path) -> None:
    path=root/"src/battle/battle_controller_player.c"
    anchor="""    if (NO_CLOUD_NINE) {
        if (WEATHER_IS_SAND && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SAND_VEIL) == TRUE) {
"""
    ins="""    if ((battleCtx->fieldConditionsMask & FIELD_CONDITION_DEEP_FOG)
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_SMOKEY_MANEUVERS) == TRUE) {
        hitRate = hitRate * 80 / 100;
    }

"""
    insert_before_once(path,anchor,ins,"ABILITY_SMOKEY_MANEUVERS","Smokey Maneuvers fog evasion")

def patch_headstrong(root: Path) -> None:
    path=root/"src/battle/battle_lib.c"
    anchor="""        case SWITCH_IN_CHECK_STATE_DOWNLOAD:
            for (i = 0; i < maxBattlers; i++) {
                battler = battleCtx->monSpeedOrder[i];

"""
    ins="""                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && Battler_Ability(battleCtx, battler) == ABILITY_HEADSTRONG) {
                    battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                    if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SP_DEFENSE]
                        < MAX_STAT_STAGE) {
                        battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SP_DEFENSE]++;
                    }
                    battleCtx->msgBattlerTemp = battler;
                    subscript = subscript_mold_breaker;
                    result = SWITCH_IN_CHECK_RESULT_BREAK;
                    break;
                }

"""
    insert_after_once(path,anchor,ins,"Battler_Ability(battleCtx, battler) == ABILITY_HEADSTRONG","Headstrong entry SpDef")

def patch_hubris(root: Path) -> None:
    path=root/"src/battle/battle_lib.c"
    old="""    case ABILITY_GRIM_NEIGH:
    case ABILITY_AS_ONE_SPECTRIER:
"""
    new="""    case ABILITY_GRIM_NEIGH:
    case ABILITY_AS_ONE_SPECTRIER:
    case ABILITY_HUBRIS:
"""
    replace_once(path,old,new,"Hubris Grim Neigh KO lane")

def update_registry(path: Path) -> None:
    lines=[x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for tok in TOKENS:
        if tok not in lines:
            lines.append(tok)
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")

def validate(root: Path, registry: Path) -> dict[str,bool]:
    lib=(root/"src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl=(root/"src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    abilities=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
    reg=set(registry.read_text().splitlines())
    checks={
        "ectoplasm_fog_highest_attack":"ABILITY_ECTOPLASM" in lib and "fieldConditions & FIELD_CONDITION_DEEP_FOG" in lib,
        "raging_storm_rain_highest_attack":"ABILITY_RAGING_STORM" in lib and "FIELD_CONDITION_RAINING" in lib,
        "ethereal_rush_fog_speed":"ABILITY_ETHEREAL_RUSH" in lib and "battler1Speed = battler1Speed * 15 / 10;" in lib,
        "thermal_slide_sun_hail_speed":"ABILITY_THERMAL_SLIDE" in lib and "FIELD_CONDITION_SUNNY | FIELD_CONDITION_HAILING" in lib,
        "smokey_maneuvers_fog_evasion":"ABILITY_SMOKEY_MANEUVERS" in ctl and "hitRate = hitRate * 80 / 100;" in ctl,
        "headstrong_entry_spdef":"ABILITY_HEADSTRONG" in lib and "BATTLE_STAT_SP_DEFENSE]++" in lib,
        "hubris_ko_spatk":"case ABILITY_HUBRIS:" in lib and "case ABILITY_GRIM_NEIGH:" in lib,
        "registry_updated":all(tok in reg for tok in TOKENS),
        "ids_stable":all(len(abilities)>aid and abilities[aid]==tok for tok,aid in IMPLEMENTED.values()),
    }
    return checks

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("--partition",type=Path,default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
    ap.add_argument("--implemented-registry",type=Path,required=True)
    ap.add_argument("--report",type=Path,default=Path("mr10r2-weather-stat.json"))
    a=ap.parse_args()
    root=a.pokeplatinum_root.resolve()
    validate_partition(a.partition.resolve())
    patch_damage_stats(root)
    patch_speed(root)
    patch_evasion(root)
    patch_headstrong(root)
    patch_hubris(root)
    update_registry(a.implemented_registry.resolve())
    checks=validate(root,a.implemented_registry.resolve())
    status="PASS" if all(checks.values()) else "FAIL"
    report={"gate":"MERCURY_MR10R2_WEATHER_STAT","status":status,"implemented":list(IMPLEMENTED),"implemented_count":len(IMPLEMENTED),"checks":checks}
    a.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if status!="PASS":
        raise SystemExit("MR10R2 validation failed")

if __name__=="__main__":
    main()
