#!/usr/bin/env python3
"""MR08G — canonical Ability fast pass, late-generation shared hooks.

Ports ten more official/current-mainline Ability mechanics using Platinum's
existing battle lanes and the pinned hg-engine behavior as the DS reference:

- Beast Boost
- Thermal Exchange
- Purifying Salt
- Well-Baked Body
- Guard Dog
- Rocky Payload
- Good as Gold
- Sharpness
- Armor Tail
- Earth Eater

This is mechanics-only. Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_BEAST_BOOST",
    "ABILITY_THERMAL_EXCHANGE",
    "ABILITY_PURIFYING_SALT",
    "ABILITY_WELL_BAKED_BODY",
    "ABILITY_GUARD_DOG",
    "ABILITY_ROCKY_PAYLOAD",
    "ABILITY_GOOD_AS_GOLD",
    "ABILITY_SHARPNESS",
    "ABILITY_ARMOR_TAIL",
    "ABILITY_EARTH_EATER",
)

EXPECTED_IDS = {
    "ABILITY_BEAST_BOOST": 224,
    "ABILITY_THERMAL_EXCHANGE": 270,
    "ABILITY_PURIFYING_SALT": 272,
    "ABILITY_WELL_BAKED_BODY": 273,
    "ABILITY_GUARD_DOG": 275,
    "ABILITY_ROCKY_PAYLOAD": 276,
    "ABILITY_GOOD_AS_GOLD": 283,
    "ABILITY_SHARPNESS": 292,
    "ABILITY_ARMOR_TAIL": 296,
    "ABILITY_EARTH_EATER": 297,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {count}"
        )
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    checks: dict[str, bool] = {}
    for token, expected in EXPECTED_IDS.items():
        checks[f"{token.lower()}_id"] = (
            len(abilities) > expected and abilities[expected] == token
        )
    return checks


def patch_battle_lib(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Sharpness uses the pinned hg-engine slicing table.
    insert_before_once(
        path,
        """static BOOL Mercury_MoveIsBiting(int move)
""",
        """static BOOL Mercury_MoveIsSlicing(int move)
{
    switch (move) {
    case MOVE_AERIAL_ACE:
    case MOVE_AIR_CUTTER:
    case MOVE_AIR_SLASH:
    case MOVE_AQUA_CUTTER:
    case MOVE_BEHEMOTH_BLADE:
    case MOVE_BITTER_BLADE:
    case MOVE_CEASELESS_EDGE:
    case MOVE_CROSS_POISON:
    case MOVE_CRUSH_CLAW:
    case MOVE_CUT:
    case MOVE_DIRE_CLAW:
    case MOVE_DRAGON_CLAW:
    case MOVE_FURY_CUTTER:
    case MOVE_KOWTOW_CLEAVE:
    case MOVE_LEAF_BLADE:
    case MOVE_METAL_CLAW:
    case MOVE_MIGHTY_CLEAVE:
    case MOVE_NIGHT_SLASH:
    case MOVE_POPULATION_BOMB:
    case MOVE_PSYBLADE:
    case MOVE_PSYCHO_CUT:
    case MOVE_RAZOR_LEAF:
    case MOVE_RAZOR_SHELL:
    case MOVE_SACRED_SWORD:
    case MOVE_SECRET_SWORD:
    case MOVE_SHADOW_CLAW:
    case MOVE_SLASH:
    case MOVE_SOLAR_BLADE:
    case MOVE_STONE_AXE:
    case MOVE_TACHYON_CUTTER:
    case MOVE_X_SCISSOR:
        return TRUE;
    default:
        return FALSE;
    }
}

""",
        "Sharpness slicing helper",
    )

    # Armor Tail is the third canonical Queenly Majesty / Dazzling family
    # member and protects the holder's active side from opposing priority.
    replace_once(
        path,
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_QUEENLY_MAJESTY)
        || Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_DAZZLING)) {
        return TRUE;
    }
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_QUEENLY_MAJESTY)
        || Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_DAZZLING)
        || Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_ARMOR_TAIL)) {
        return TRUE;
    }
""",
        "Armor Tail holder priority protection",
    )

    replace_once(
        path,
        """    if (battleCtx->battleMons[partner].curHP
        && (Battler_IgnorableAbility(
                battleCtx, attacker, partner, ABILITY_QUEENLY_MAJESTY)
            || Battler_IgnorableAbility(
                battleCtx, attacker, partner, ABILITY_DAZZLING))) {
        return TRUE;
    }
""",
        """    if (battleCtx->battleMons[partner].curHP
        && (Battler_IgnorableAbility(
                battleCtx, attacker, partner, ABILITY_QUEENLY_MAJESTY)
            || Battler_IgnorableAbility(
                battleCtx, attacker, partner, ABILITY_DAZZLING)
            || Battler_IgnorableAbility(
                battleCtx, attacker, partner, ABILITY_ARMOR_TAIL))) {
        return TRUE;
    }
""",
        "Armor Tail ally priority protection",
    )

    # Earth Eater, Well-Baked Body and Good as Gold use Platinum's normal
    # pre-move immunity lane, so blocked moves terminate before damage/effects.
    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_BULLETPROOF) == TRUE
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_EARTH_EATER) == TRUE
        && moveType == TYPE_GROUND
        && attacker != defender
        && CURRENT_MOVE_DATA.power) {
        battleCtx->hpCalcTemp =
            BattleSystem_Divide(battleCtx->battleMons[defender].maxHP, 4);
        return subscript_ability_restores_hp;
    }

    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_WELL_BAKED_BODY) == TRUE
        && moveType == TYPE_FIRE
        && attacker != defender
        && (CURRENT_MOVE_DATA.power || battleCtx->moveCur == MOVE_WILL_O_WISP)) {
        battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_DEFENSE_UP_2_STAGES;
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = defender;
        return subscript_update_stat_stage;
    }

    if (attacker != defender
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_GOOD_AS_GOLD) == TRUE
        && CURRENT_MOVE_DATA.class == CLASS_STATUS
        && CURRENT_MOVE_DATA.range != RANGE_USER
        && CURRENT_MOVE_DATA.range != RANGE_USER_SIDE
        && CURRENT_MOVE_DATA.range != RANGE_OPPONENT_SIDE
        && CURRENT_MOVE_DATA.range != RANGE_FIELD) {
        return subscript_but_it_failed;
    }

""",
        "Earth Eater / Well-Baked Body / Good as Gold immunity hooks",
    )

    # Rocky Payload and Sharpness are ordinary 1.5x move-power families.
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_STRONG_JAW
""",
        """    if (attackerParams.ability == ABILITY_ROCKY_PAYLOAD
        && moveType == TYPE_ROCK) {
        movePower = movePower * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_SHARPNESS
        && Mercury_MoveIsSlicing(move)) {
        movePower = movePower * 15 / 10;
    }

""",
        "Rocky Payload / Sharpness power hooks",
    )

    # Purifying Salt halves incoming Ghost damage.
    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_PUNK_ROCK) == TRUE
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_PURIFYING_SALT) == TRUE
        && moveType == TYPE_GHOST) {
        damage /= 2;
    }

""",
        "Purifying Salt Ghost reduction",
    )

    # Thermal Exchange raises Attack after a damaging Fire hit. It is a
    # Mold-Breaker-ignorable defensive Ability in the pinned DS reference.
    insert_before_once(
        path,
        """    case ABILITY_STEAM_ENGINE: {
""",
        """    case ABILITY_THERMAL_EXCHANGE: {
        int moveType;

        if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NORMALIZE) {
            moveType = TYPE_NORMAL;
        } else if (battleCtx->moveType) {
            moveType = battleCtx->moveType;
        } else {
            moveType = CURRENT_MOVE_DATA.type;
        }

        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_THERMAL_EXCHANGE) == TRUE
            && DEFENDING_MON.curHP
            && moveType == TYPE_FIRE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;
    }

""",
        "Thermal Exchange on-hit Attack boost",
    )

    # Beast Boost shares the existing post-KO helper. hg-engine compares raw
    # stats in BattleMon order: Attack, Defense, Speed, Sp. Atk, Sp. Def.
    insert_before_once(
        path,
        """    case ABILITY_GRIM_NEIGH:
""",
        """    case ABILITY_BEAST_BOOST: {
        BattleMon *mon = &battleCtx->battleMons[battleCtx->attacker];
        int stat = BATTLE_STAT_ATTACK;
        int highest = mon->attack;

        if (mon->defense > highest) {
            highest = mon->defense;
            stat = BATTLE_STAT_DEFENSE;
        }
        if (mon->speed > highest) {
            highest = mon->speed;
            stat = BATTLE_STAT_SPEED;
        }
        if (mon->spAttack > highest) {
            highest = mon->spAttack;
            stat = BATTLE_STAT_SP_ATTACK;
        }
        if (mon->spDefense > highest) {
            stat = BATTLE_STAT_SP_DEFENSE;
        }

        if (mon->statBoosts[stat] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam =
                MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE
                + (stat - BATTLE_STAT_ATTACK);
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            *subscript = subscript_update_stat_stage;
            return TRUE;
        }
        break;
    }

""",
        "Beast Boost KO hook",
    )


def patch_status_immunities(root: Path) -> None:
    sleep = root / "res/battle/scripts/subscripts/subscript_fall_asleep.s"
    poison = root / "res/battle/scripts/subscripts/subscript_poison.s"
    toxic = root / "res/battle/scripts/subscripts/subscript_badly_poison.s"
    burn = root / "res/battle/scripts/subscripts/subscript_burn.s"
    freeze = root / "res/battle/scripts/subscripts/subscript_freeze.s"
    paralyze = root / "res/battle/scripts/subscripts/subscript_paralyze.s"

    # Purifying Salt blocks all nonvolatile status. Direct/non-Mold-Breaker
    # lanes use CheckAbility; move-caused lanes use CheckIgnorableAbility.
    replace_once(
        sleep,
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_INSOMNIA, _202
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_INSOMNIA, _202
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _202
""",
        "Purifying Salt sleep direct",
    )
    replace_once(
        sleep,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_INSOMNIA, _202
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_INSOMNIA, _202
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _202
""",
        "Purifying Salt sleep move",
    )

    replace_once(
        poison,
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _177
""",
        "Purifying Salt poison direct",
    )
    replace_once(
        poison,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _177
""",
        "Purifying Salt poison move",
    )

    # Bad poison has separate toxic-spikes/held-item and move lanes.
    replace_once(
        toxic,
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _249
""",
        "Purifying Salt toxic spikes",
    )
    replace_once(
        toxic,
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _248
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _248
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _248
""",
        "Purifying Salt toxic held item",
    )
    replace_once(
        toxic,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _249
""",
        "Purifying Salt toxic move",
    )

    # Thermal Exchange and Purifying Salt both forbid burns. MR08F already
    # inserted Water Bubble immediately after Water Veil.
    replace_once(
        burn,
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _211
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _211
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_THERMAL_EXCHANGE, _211
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _211
""",
        "Thermal Exchange / Purifying Salt burn direct",
    )
    replace_once(
        burn,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _264
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _264
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_THERMAL_EXCHANGE, _264
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _264
""",
        "Thermal Exchange / Purifying Salt burn move",
    )

    replace_once(
        freeze,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_MAGMA_ARMOR, _128
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_MAGMA_ARMOR, _128
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _128
""",
        "Purifying Salt freeze",
    )

    replace_once(
        paralyze,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_LIMBER, _170
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_LIMBER, _170
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PURIFYING_SALT, _170
""",
        "Purifying Salt paralysis",
    )


def patch_guard_dog(root: Path) -> None:
    force_switch = (
        root
        / "res/battle/scripts/subscripts/subscript_force_target_to_switch_or_flee.s"
    )
    intimidate = root / "res/battle/scripts/subscripts/subscript_intimidate.s"

    replace_once(
        force_switch,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_DEFENDER, ABILITY_SUCTION_CUPS, _079
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_DEFENDER, ABILITY_SUCTION_CUPS, _079
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_DEFENDER, ABILITY_GUARD_DOG, _079
""",
        "Guard Dog forced-switch immunity",
    )

    replace_once(
        intimidate,
        """    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_CUR_HP, 0, _038
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_ATTACK_DOWN_1_STAGE
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_ABILITY
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE

_038:
""",
        """    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_CUR_HP, 0, _038
    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_GUARD_DOG, _MercuryGuardDog
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_ATTACK_DOWN_1_STAGE
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_ABILITY
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE
    GoTo _038

_MercuryGuardDog:
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_ABILITY
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE

_038:
""",
        "Guard Dog Intimidate reversal",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    sleep = (root / "res/battle/scripts/subscripts/subscript_fall_asleep.s").read_text(encoding="utf-8")
    poison = (root / "res/battle/scripts/subscripts/subscript_poison.s").read_text(encoding="utf-8")
    toxic = (root / "res/battle/scripts/subscripts/subscript_badly_poison.s").read_text(encoding="utf-8")
    burn = (root / "res/battle/scripts/subscripts/subscript_burn.s").read_text(encoding="utf-8")
    freeze = (root / "res/battle/scripts/subscripts/subscript_freeze.s").read_text(encoding="utf-8")
    paralyze = (root / "res/battle/scripts/subscripts/subscript_paralyze.s").read_text(encoding="utf-8")
    force_switch = (
        root
        / "res/battle/scripts/subscripts/subscript_force_target_to_switch_or_flee.s"
    ).read_text(encoding="utf-8")
    intimidate = (root / "res/battle/scripts/subscripts/subscript_intimidate.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "beast_boost_hook":
            "case ABILITY_BEAST_BOOST:" in lib
            and "MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE" in lib,
        "thermal_exchange_hook":
            "case ABILITY_THERMAL_EXCHANGE:" in lib
            and "ABILITY_THERMAL_EXCHANGE, _264" in burn,
        "purifying_salt_hook":
            "ABILITY_PURIFYING_SALT" in lib
            and "ABILITY_PURIFYING_SALT, _202" in sleep
            and "ABILITY_PURIFYING_SALT, _177" in poison
            and "ABILITY_PURIFYING_SALT, _249" in toxic
            and "ABILITY_PURIFYING_SALT, _264" in burn
            and "ABILITY_PURIFYING_SALT, _128" in freeze
            and "ABILITY_PURIFYING_SALT, _170" in paralyze,
        "well_baked_body_hook":
            "ABILITY_WELL_BAKED_BODY" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_2_STAGES" in lib,
        "guard_dog_hook":
            "ABILITY_GUARD_DOG, _079" in force_switch
            and "_MercuryGuardDog" in intimidate,
        "rocky_payload_hook":
            "attackerParams.ability == ABILITY_ROCKY_PAYLOAD" in lib,
        "good_as_gold_hook":
            "ABILITY_GOOD_AS_GOLD" in lib
            and "CURRENT_MOVE_DATA.class == CLASS_STATUS" in lib,
        "sharpness_hook":
            "ABILITY_SHARPNESS" in lib
            and "Mercury_MoveIsSlicing" in lib,
        "armor_tail_hook":
            lib.count("ABILITY_ARMOR_TAIL") >= 2,
        "earth_eater_hook":
            "ABILITY_EARTH_EATER" in lib
            and "subscript_ability_restores_hp" in lib,
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr08g-canonical-ability-late-shared-hooks.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_battle_lib(root)
    patch_status_immunities(root)
    patch_guard_dog(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08G_CANONICAL_ABILITY_LATE_SHARED_HOOKS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 65,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08G validation failed")


if __name__ == "__main__":
    main()
