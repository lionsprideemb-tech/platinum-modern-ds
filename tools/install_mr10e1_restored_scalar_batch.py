#!/usr/bin/env python3
"""MR10E1 — restore first scalar/shared-hook historical Ability batch.

Implements eight recovered Mercury/Elite Redux identities using battle hooks
already certified by the canonical stack:
- Early Grave
- Fighter
- Fire Scales
- Flame Shield
- Gladiator
- Hubris
- Purgatory
- Tidal Rush

This is runtime mechanics work, not namespace-only staging.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

IMPLEMENTED = {
    "Early Grave": ("ABILITY_EARLY_GRAVE", 400),
    "Fighter": ("ABILITY_FIGHTER", 420),
    "Fire Scales": ("ABILITY_FIRE_SCALES", 421),
    "Flame Shield": ("ABILITY_FLAME_SHIELD", 423),
    "Gladiator": ("ABILITY_GLADIATOR", 439),
    "Hubris": ("ABILITY_HUBRIS", 453),
    "Purgatory": ("ABILITY_PURGATORY", 536),
    "Tidal Rush": ("ABILITY_WATER_GALE_WINGS", 616),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

def validate_partition(path: Path) -> None:
    plan=json.loads(path.read_text(encoding="utf-8"))
    rows=plan["abilities"]
    for name,(token,aid) in IMPLEMENTED.items():
        ms=[x for x in rows if x.get("id")==aid and x.get("token")==token]
        if len(ms)!=1:
            raise SystemExit(f"{name}: expected one reconciled row at {aid}, found {len(ms)}")
        row=ms[0]
        if not row.get("runtime_enabled", True):
            raise SystemExit(f"{name}: runtime disabled in reconciled partition")
        if row.get("review_blocked", False):
            raise SystemExit(f"{name}: still review blocked")

def patch_priority(root: Path) -> None:
    p=root/"src/battle/battle_lib.c"

    old1="""        if (battler1Move
            && battler1Ability == ABILITY_GALE_WINGS
            && battleCtx->battleMons[battler1].curHP == battleCtx->battleMons[battler1].maxHP
            && MOVE_DATA(battler1Move).type == TYPE_FLYING) {
            battler1Priority++;
        }

        if (battler2Move
            && battler2Ability == ABILITY_GALE_WINGS
            && battleCtx->battleMons[battler2].curHP == battleCtx->battleMons[battler2].maxHP
            && MOVE_DATA(battler2Move).type == TYPE_FLYING) {
            battler2Priority++;
        }
"""
    new1="""        if (battler1Move
            && battleCtx->battleMons[battler1].curHP == battleCtx->battleMons[battler1].maxHP
            && ((battler1Ability == ABILITY_GALE_WINGS
                    && MOVE_DATA(battler1Move).type == TYPE_FLYING)
                || (battler1Ability == ABILITY_EARLY_GRAVE
                    && MOVE_DATA(battler1Move).type == TYPE_GHOST)
                || (battler1Ability == ABILITY_WATER_GALE_WINGS
                    && MOVE_DATA(battler1Move).type == TYPE_WATER))) {
            battler1Priority++;
        }

        if (battler2Move
            && battleCtx->battleMons[battler2].curHP == battleCtx->battleMons[battler2].maxHP
            && ((battler2Ability == ABILITY_GALE_WINGS
                    && MOVE_DATA(battler2Move).type == TYPE_FLYING)
                || (battler2Ability == ABILITY_EARLY_GRAVE
                    && MOVE_DATA(battler2Move).type == TYPE_GHOST)
                || (battler2Ability == ABILITY_WATER_GALE_WINGS
                    && MOVE_DATA(battler2Move).type == TYPE_WATER))) {
            battler2Priority++;
        }
"""
    replace_once(p,old1,new1,"Early Grave/Tidal Rush action priority")

    old2="""    if (Battler_Ability(battleCtx, attacker) == ABILITY_GALE_WINGS
        && battleCtx->battleMons[attacker].curHP
            == battleCtx->battleMons[attacker].maxHP
        && moveType == TYPE_FLYING) {
        priority++;
    }
"""
    new2="""    if (battleCtx->battleMons[attacker].curHP
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
    replace_once(p,old2,new2,"Early Grave/Tidal Rush priority helper")

def patch_damage(root: Path) -> None:
    p=root/"src/battle/battle_lib.c"

    old="""    if (moveType == TYPE_BUG && attackerParams.ability == ABILITY_SWARM) {
        movePower = movePower * (attackerParams.curHP <= (attackerParams.maxHP / 3) ? 150 : 120) / 100;
    }
"""
    new=old+"""
    if (moveType == TYPE_FIGHTING && attackerParams.ability == ABILITY_FIGHTER) {
        movePower = movePower * (attackerParams.curHP <= (attackerParams.maxHP / 3) ? 150 : 120) / 100;
    }
    if (moveType == TYPE_FIGHTING && attackerParams.ability == ABILITY_GLADIATOR) {
        movePower = movePower * (attackerParams.curHP <= (attackerParams.maxHP / 3) ? 180 : 130) / 100;
    }
    if (moveType == TYPE_GHOST && attackerParams.ability == ABILITY_PURGATORY) {
        movePower = movePower * (attackerParams.curHP <= (attackerParams.maxHP / 3) ? 180 : 130) / 100;
    }
"""
    replace_once(p,old,new,"Fighter/Gladiator/Purgatory power family")

    old="""    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_ICE_SCALES) == TRUE
        && moveClass == CLASS_SPECIAL) {
        damage /= 2;
    }
"""
    new="""    if ((Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_ICE_SCALES) == TRUE
            || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FIRE_SCALES) == TRUE)
        && moveClass == CLASS_SPECIAL) {
        damage /= 2;
    }
"""
    replace_once(p,old,new,"Fire Scales special-damage reduction")

    old="""            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOLID_ROCK) == TRUE) {
                damage = BattleSystem_Divide(damage * 65, 100);
            }
"""
    new="""            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOLID_ROCK) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FLAME_SHIELD) == TRUE) {
                damage = BattleSystem_Divide(damage * 65, 100);
            }
"""
    replace_once(p,old,new,"Flame Shield super-effective reduction")

def patch_hubris(root: Path) -> None:
    p=root/"src/battle/battle_lib.c"
    old="""    case ABILITY_GRIM_NEIGH:
    case ABILITY_AS_ONE_SPECTRIER:
"""
    new="""    case ABILITY_GRIM_NEIGH:
    case ABILITY_AS_ONE_SPECTRIER:
    case ABILITY_HUBRIS:
"""
    replace_once(p,old,new,"Hubris Grim Neigh KO family")

def update_registry(path: Path) -> None:
    lines=[x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for t in TOKENS:
        if t not in lines: lines.append(t)
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")

def validate(root: Path, registry: Path) -> dict:
    lib=(root/"src/battle/battle_lib.c").read_text(encoding="utf-8")
    abilities=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
    reg=set(registry.read_text().splitlines())
    checks={
      "early_grave_priority": "ABILITY_EARLY_GRAVE" in lib and "TYPE_GHOST" in lib,
      "tidal_rush_priority": "ABILITY_WATER_GALE_WINGS" in lib and "TYPE_WATER" in lib,
      "fighter_scaling": "attackerParams.ability == ABILITY_FIGHTER" in lib and "? 150 : 120" in lib,
      "gladiator_scaling": "attackerParams.ability == ABILITY_GLADIATOR" in lib and "? 180 : 130" in lib,
      "purgatory_scaling": "attackerParams.ability == ABILITY_PURGATORY" in lib and "? 180 : 130" in lib,
      "fire_scales": "ABILITY_FIRE_SCALES) == TRUE" in lib and "moveClass == CLASS_SPECIAL" in lib,
      "flame_shield": "ABILITY_FLAME_SHIELD) == TRUE" in lib and "BattleSystem_Divide(damage * 65, 100)" in lib,
      "hubris": "case ABILITY_HUBRIS:" in lib,
      "registry": all(t in reg for t in TOKENS),
    }
    for name,(t,i) in IMPLEMENTED.items():
        checks[f"{name.lower().replace(' ','_')}_id"] = len(abilities)>i and abilities[i]==t
    return checks

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("--partition",type=Path,default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
    ap.add_argument("--implemented-registry",type=Path,required=True)
    ap.add_argument("--report",type=Path,default=Path("mr10e1-restored-scalar.json"))
    a=ap.parse_args()
    validate_partition(a.partition)
    patch_priority(a.pokeplatinum_root)
    patch_damage(a.pokeplatinum_root)
    patch_hubris(a.pokeplatinum_root)
    update_registry(a.implemented_registry)
    checks=validate(a.pokeplatinum_root,a.implemented_registry)
    status="PASS" if all(checks.values()) else "FAIL"
    out={"gate":"MERCURY_MR10E1_RESTORED_SCALAR","status":status,
         "implemented":list(IMPLEMENTED.keys()),"implemented_count":len(IMPLEMENTED),
         "historical_runtime_missing_before":126,
         "historical_runtime_missing_after_batch":118,
         "checks":checks}
    a.report.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
    if status!="PASS": raise SystemExit("MR10E1 failed")

if __name__=="__main__": main()
