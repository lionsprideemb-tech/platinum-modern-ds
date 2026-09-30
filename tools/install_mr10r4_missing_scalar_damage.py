#!/usr/bin/env python3
"""MR10R4 — restore low-risk scalar damage/stat historical Abilities.

This batch deliberately stays on already-certified CalcMoveDamage hooks so a
larger group can be restored together without introducing new battle state.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

IMPLEMENTED = {
    "Cryptic Power": ("ABILITY_MR_CRYPTIC_POWER", 323),
    "Nocturnal": ("ABILITY_MR_NOCTURNAL", 325),
    "Prism Scales": ("ABILITY_MR_PRISM_SCALES", 328),
    "Antarctic Bird": ("ABILITY_MR_ANTARCTIC_BIRD", 329),
    "Fossilized": ("ABILITY_MR_FOSSILIZED", 330),
    "Combustion": ("ABILITY_MR_COMBUSTION", 377),
    "Dragonslayer": ("ABILITY_MR_DRAGONSLAYER", 394),
    "Dune Terror": ("ABILITY_MR_DUNE_TERROR", 399),
    "Earthbound": ("ABILITY_MR_EARTHBOUND", 401),
    "Electrocytes": ("ABILITY_MR_ELECTROCYTES", 404),
    "Exploit Weakness": ("ABILITY_MR_EXPLOIT_WEAKNESS", 415),
    "Fae Hunter": ("ABILITY_MR_FAE_HUNTER", 416),
    "Forest Rage": ("ABILITY_MR_FOREST_RAGE", 427),
    "Hellblaze": ("ABILITY_MR_HELLBLAZE", 449),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


def insert_before_once(path: Path, anchor: str, insertion: str, marker: str, label: str) -> None:
    text=path.read_text(encoding="utf-8")
    if marker in text:
        return
    count=text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor,insertion+anchor,1),encoding="utf-8")


def validate_partition(path: Path) -> None:
    rows=json.loads(path.read_text(encoding="utf-8"))["abilities"]
    for name,(token,aid) in IMPLEMENTED.items():
        matches=[r for r in rows if r.get("id")==aid and r.get("token")==token]
        if len(matches)!=1:
            raise SystemExit(f"{name}: expected one reconciled row at {aid}, got {len(matches)}")
        row=matches[0]
        if row.get("runtime_enabled") is False or row.get("review_blocked") is True:
            raise SystemExit(f"{name}: not runtime-approved")
        if row.get("exact_effect") in (None,"RESTORE_PENDING_EXACT_SEMANTICS"):
            raise SystemExit(f"{name}: exact semantics unavailable")


def patch_damage(root: Path) -> None:
    path=root/"src/battle/battle_lib.c"

    stat_anchor="""    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
"""
    stat_insertion="""    if (attackerParams.ability == ABILITY_MR_CRYPTIC_POWER) {
        spAttackStat *= 2;
    }

"""
    insert_before_once(
        path,stat_anchor,stat_insertion,
        "attackerParams.ability == ABILITY_MR_CRYPTIC_POWER",
        "Cryptic Power SpAtk double",
    )

    offense_anchor="""    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE
"""
    offense="""    if (attackerParams.ability == ABILITY_MR_NOCTURNAL
        && moveType == TYPE_DARK && movePower) {
        movePower = movePower * 125 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_ANTARCTIC_BIRD
        && (moveType == TYPE_ICE || moveType == TYPE_FLYING) && movePower) {
        movePower = movePower * 130 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_FOSSILIZED
        && moveType == TYPE_ROCK && movePower) {
        movePower = movePower * 120 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_COMBUSTION
        && moveType == TYPE_FIRE && movePower) {
        movePower = movePower * 150 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_DRAGONSLAYER
        && (defenderParams.type1 == TYPE_DRAGON || defenderParams.type2 == TYPE_DRAGON)
        && movePower) {
        movePower = movePower * 150 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_DUNE_TERROR
        && (fieldConditions & FIELD_CONDITION_SANDSTORM)
        && moveType == TYPE_GROUND && movePower) {
        movePower = movePower * 120 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_EARTHBOUND
        && moveType == TYPE_GROUND && movePower) {
        movePower = movePower * 125 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_ELECTROCYTES
        && moveType == TYPE_ELECTRIC && movePower) {
        movePower = movePower * 125 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_EXPLOIT_WEAKNESS
        && defenderParams.statusMask && movePower) {
        movePower = movePower * 125 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_FAE_HUNTER
        && (defenderParams.type1 == TYPE_FAIRY || defenderParams.type2 == TYPE_FAIRY)
        && movePower) {
        movePower = movePower * 150 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_FOREST_RAGE
        && moveType == TYPE_GRASS && movePower) {
        movePower = movePower
            * (attackerParams.curHP <= attackerParams.maxHP / 3 ? 180 : 130)
            / 100;
    }

    if (attackerParams.ability == ABILITY_MR_HELLBLAZE
        && moveType == TYPE_FIRE && movePower) {
        movePower = movePower
            * (attackerParams.curHP <= attackerParams.maxHP / 3 ? 180 : 130)
            / 100;
    }

"""
    insert_before_once(
        path,offense_anchor,offense,
        "attackerParams.ability == ABILITY_MR_NOCTURNAL",
        "R4 offensive scalar family",
    )

    defensive_anchor="""    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
"""
    defensive="""    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_NOCTURNAL) == TRUE
        && (moveType == TYPE_DARK || moveType == TYPE_FAIRY)) {
        damage = damage * 75 / 100;
    }

    if (moveClass == CLASS_SPECIAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_PRISM_SCALES) == TRUE) {
        damage = damage * 70 / 100;
    }

    if (moveType == TYPE_ROCK
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_FOSSILIZED) == TRUE) {
        damage /= 2;
    }

    if ((fieldConditions & FIELD_CONDITION_SANDSTORM)
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_DUNE_TERROR) == TRUE) {
        damage = damage * 65 / 100;
    }

"""
    insert_before_once(
        path,defensive_anchor,defensive,
        "ABILITY_MR_PRISM_SCALES) == TRUE",
        "R4 defensive scalar family",
    )


def update_registry(path: Path) -> None:
    rows=[x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for token in TOKENS:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows)+"\n",encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str,bool]:
    lib=(root/"src/battle/battle_lib.c").read_text(encoding="utf-8")
    abilities=[x.strip() for x in (root/"generated/abilities.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    reg=set(registry.read_text(encoding="utf-8").splitlines())
    return {
        "cryptic_power_double_spa":"ABILITY_MR_CRYPTIC_POWER" in lib and "spAttackStat *= 2;" in lib,
        "nocturnal_dual_effect":"ABILITY_MR_NOCTURNAL" in lib and "damage = damage * 75 / 100;" in lib,
        "prism_scales_special_70":"ABILITY_MR_PRISM_SCALES" in lib and "damage = damage * 70 / 100;" in lib,
        "antarctic_bird_ice_flying_130":"ABILITY_MR_ANTARCTIC_BIRD" in lib and "TYPE_ICE || moveType == TYPE_FLYING" in lib,
        "fossilized_rock_boost_resist":"ABILITY_MR_FOSSILIZED" in lib and "moveType == TYPE_ROCK" in lib,
        "combustion_fire_150":"ABILITY_MR_COMBUSTION" in lib and "movePower = movePower * 150 / 100;" in lib,
        "dragonslayer_anti_dragon":"ABILITY_MR_DRAGONSLAYER" in lib and "defenderParams.type1 == TYPE_DRAGON" in lib,
        "dune_terror_sand_dual_effect":"ABILITY_MR_DUNE_TERROR" in lib and "FIELD_CONDITION_SANDSTORM" in lib,
        "earthbound_ground_125":"ABILITY_MR_EARTHBOUND" in lib and "moveType == TYPE_GROUND" in lib,
        "electrocytes_electric_125":"ABILITY_MR_ELECTROCYTES" in lib and "moveType == TYPE_ELECTRIC" in lib,
        "exploit_weakness_status_125":"ABILITY_MR_EXPLOIT_WEAKNESS" in lib and "defenderParams.statusMask" in lib,
        "fae_hunter_anti_fairy":"ABILITY_MR_FAE_HUNTER" in lib and "defenderParams.type1 == TYPE_FAIRY" in lib,
        "forest_rage_scaling":"ABILITY_MR_FOREST_RAGE" in lib and "? 180 : 130" in lib,
        "hellblaze_scaling":"ABILITY_MR_HELLBLAZE" in lib and "? 180 : 130" in lib,
        "registry_updated":all(token in reg for token in TOKENS),
        "ids_stable":all(len(abilities)>aid and abilities[aid]==token for token,aid in IMPLEMENTED.values()),
    }


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("--partition",type=Path,default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
    ap.add_argument("--implemented-registry",type=Path,required=True)
    ap.add_argument("--report",type=Path,default=Path("mr10r4-scalar-damage.json"))
    a=ap.parse_args()
    root=a.pokeplatinum_root.resolve()

    validate_partition(a.partition.resolve())
    patch_damage(root)
    update_registry(a.implemented_registry.resolve())
    checks=validate(root,a.implemented_registry.resolve())
    status="PASS" if all(checks.values()) else "FAIL"
    report={
        "gate":"MERCURY_MR10R4_SCALAR_DAMAGE",
        "status":status,
        "implemented":list(IMPLEMENTED),
        "implemented_count":len(IMPLEMENTED),
        "checks":checks,
    }
    a.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    if status!="PASS":
        raise SystemExit("MR10R4 validation failed")


if __name__=="__main__":
    main()
