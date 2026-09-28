#!/usr/bin/env python3
"""MR08D — unchanged canonical Ability fast pass, core battle hooks.

Adds ten more official/mainline Ability mechanics using Platinum-native hooks
and the pinned hg-engine behavior as the DS reference.

Implemented:
- Defeatist
- Friend Guard
- Sand Rush
- Wonder Skin
- Analytic
- Bulletproof
- Stamina
- Water Compaction
- Steelworker
- Tangling Hair

No Summary/Skills/editor visuals are changed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_DEFEATIST",
    "ABILITY_FRIEND_GUARD",
    "ABILITY_SAND_RUSH",
    "ABILITY_WONDER_SKIN",
    "ABILITY_ANALYTIC",
    "ABILITY_BULLETPROOF",
    "ABILITY_STAMINA",
    "ABILITY_WATER_COMPACTION",
    "ABILITY_STEELWORKER",
    "ABILITY_TANGLING_HAIR",
)

EXPECTED_IDS = {
    "ABILITY_DEFEATIST": 129,
    "ABILITY_FRIEND_GUARD": 132,
    "ABILITY_SAND_RUSH": 146,
    "ABILITY_WONDER_SKIN": 147,
    "ABILITY_ANALYTIC": 148,
    "ABILITY_BULLETPROOF": 171,
    "ABILITY_STAMINA": 192,
    "ABILITY_WATER_COMPACTION": 195,
    "ABILITY_STEELWORKER": 200,
    "ABILITY_TANGLING_HAIR": 221,
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


def patch_damage_and_speed(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    # Sand Rush: current canonical +100% Speed in sand.
    replace_once(
        lib,
        """        if ((battler1Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler1Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)) {
            battler1Speed *= 2;
        }
""",
        """        if ((battler1Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler1Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler1Ability == ABILITY_SAND_RUSH && WEATHER_IS_SAND)) {
            battler1Speed *= 2;
        }
""",
        "Sand Rush battler1 speed",
    )

    replace_once(
        lib,
        """        if ((battler2Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler2Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)) {
            battler2Speed *= 2;
        }
""",
        """        if ((battler2Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler2Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler2Ability == ABILITY_SAND_RUSH && WEATHER_IS_SAND)) {
            battler2Speed *= 2;
        }
""",
        "Sand Rush battler2 speed",
    )

    # Analytic uses hg-engine's slowest-active-battler rule. ignoreQuickClaw
    # keeps this deterministic for damage prediction and mirrors the donor.
    insert_before_once(
        lib,
        """int BattleSystem_CountAbility(BattleSystem *battleSys, BattleContext *battleCtx, enum CountAbilityMode mode, int battler, int ability)
""",
        """static BOOL Mercury_AnalyticApplies(BattleSystem *battleSys, BattleContext *battleCtx, int attacker)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    for (i = 0; i < maxBattlers; i++) {
        if (i == attacker || battleCtx->battleMons[i].curHP == 0) {
            continue;
        }

        if (BattleSystem_CompareBattlerSpeed(
                battleSys,
                battleCtx,
                attacker,
                i,
                TRUE) != COMPARE_SPEED_SLOWER) {
            return FALSE;
        }
    }

    return TRUE;
}

""",
        "Analytic helper",
    )

    # Defeatist, Analytic, and Steelworker all fit the normal base-damage path.
    replace_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
""",
        """    if (attackerParams.ability == ABILITY_DEFEATIST
        && attackerParams.curHP <= attackerParams.maxHP / 2) {
        attackStat /= 2;
        spAttackStat /= 2;
    }

    if (attackerParams.ability == ABILITY_ANALYTIC
        && Mercury_AnalyticApplies(battleSys, battleCtx, attacker)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_STEELWORKER
        && moveType == TYPE_STEEL) {
        movePower = movePower * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
""",
        "Defeatist / Analytic / Steelworker damage hooks",
    )

    # Friend Guard protects allies, not the holder itself. MR08B already
    # provides Mercury_AllyHasAbility for the normal doubles-side lookup.
    insert_before_once(
        lib,
        """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
""",
        """    if (Mercury_AllyHasAbility(
            battleSys,
            battleCtx,
            defender,
            ABILITY_FRIEND_GUARD)) {
        damage = damage * 75 / 100;
    }

""",
        "Friend Guard final damage",
    )


def patch_wonder_skin(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    u16 hitRate = MOVE_DATA(move).accuracy;
    if (hitRate == 0) {
        return 0;
    }
""",
        """    u16 hitRate = MOVE_DATA(move).accuracy;
    if (hitRate == 0) {
        return 0;
    }

    // Current canonical Wonder Skin: status moves above 50 base accuracy are
    // capped at 50 before normal accuracy/evasion and other modifiers.
    if (MOVE_DATA(move).class == CLASS_STATUS
        && hitRate > 50
        && Battler_IgnorableAbility(
               battleCtx,
               attacker,
               defender,
               ABILITY_WONDER_SKIN) == TRUE) {
        hitRate = 50;
    }
""",
        "Wonder Skin accuracy cap",
    )


def patch_bulletproof(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """static u16 sSoundMoves[] = {
""",
        """static const u16 sBallBombMoves[] = {
    MOVE_ACID_SPRAY,
    MOVE_AURA_SPHERE,
    MOVE_BARRAGE,
    MOVE_BEAK_BLAST,
    MOVE_BULLET_SEED,
    MOVE_EGG_BOMB,
    MOVE_ELECTRO_BALL,
    MOVE_ENERGY_BALL,
    MOVE_FOCUS_BLAST,
    MOVE_GYRO_BALL,
    MOVE_ICE_BALL,
    MOVE_MAGNET_BOMB,
    MOVE_MIST_BALL,
    MOVE_MUD_BOMB,
    MOVE_OCTAZOOKA,
    MOVE_POLLEN_PUFF,
    MOVE_PYRO_BALL,
    MOVE_ROCK_BLAST,
    MOVE_ROCK_WRECKER,
    MOVE_SEARING_SHOT,
    MOVE_SEED_BOMB,
    MOVE_SHADOW_BALL,
    MOVE_SLUDGE_BOMB,
    MOVE_SYRUP_BOMB,
    MOVE_WEATHER_BALL,
    MOVE_ZAP_CANNON,
};

""",
        "Bulletproof move table",
    )

    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOUNDPROOF) == TRUE) {
""",
        """    if (Battler_IgnorableAbility(
            battleCtx,
            attacker,
            defender,
            ABILITY_BULLETPROOF) == TRUE) {
        for (int i = 0; i < NELEMS(sBallBombMoves); i++) {
            if (sBallBombMoves[i] == battleCtx->moveCur) {
                // Platinum's Soundproof block subscript is generic: it reads
                // the defender's live Ability and the attacker's move name.
                subscript = subscript_blocked_by_soundproof;
                break;
            }
        }
    }

""",
        "Bulletproof immunity hook",
    )


def patch_on_hit_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    case ABILITY_AFTERMATH:
""",
        """    case ABILITY_STAMINA:
        if (DEFENDING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;

    case ABILITY_WATER_COMPACTION: {
        int moveType;

        if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NORMALIZE) {
            moveType = TYPE_NORMAL;
        } else if (battleCtx->moveType) {
            moveType = battleCtx->moveType;
        } else {
            moveType = CURRENT_MOVE_DATA.type;
        }

        if (DEFENDING_MON.curHP
            && moveType == TYPE_WATER
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_DEFENSE_UP_2_STAGES;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;
    }

    case ABILITY_TANGLING_HAIR:
        if (ATTACKING_MON.curHP
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)
            && ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED] > MIN_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_SPEED_DOWN_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;

""",
        "Stamina / Water Compaction / Tangling Hair on-hit hooks",
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
    controller = (
        root / "src/battle/battle_controller_player.c"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "defeatist_hook":
            "attackerParams.ability == ABILITY_DEFEATIST" in lib
            and "attackStat /= 2;" in lib,
        "friend_guard_hook":
            "ABILITY_FRIEND_GUARD" in lib
            and "damage = damage * 75 / 100;" in lib,
        "sand_rush_hook":
            lib.count("ABILITY_SAND_RUSH && WEATHER_IS_SAND") == 2,
        "wonder_skin_hook":
            "ABILITY_WONDER_SKIN" in controller
            and "hitRate = 50;" in controller,
        "analytic_hook":
            "Mercury_AnalyticApplies" in lib
            and "attackerParams.ability == ABILITY_ANALYTIC" in lib,
        "bulletproof_hook":
            "sBallBombMoves" in lib
            and "ABILITY_BULLETPROOF" in lib,
        "stamina_hook":
            "case ABILITY_STAMINA:" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in lib,
        "water_compaction_hook":
            "case ABILITY_WATER_COMPACTION:" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_2_STAGES" in lib,
        "steelworker_hook":
            "attackerParams.ability == ABILITY_STEELWORKER" in lib
            and "moveType == TYPE_STEEL" in lib,
        "tangling_hair_hook":
            "case ABILITY_TANGLING_HAIR:" in lib
            and "MOVE_SUBSCRIPT_PTR_SPEED_DOWN_1_STAGE" in lib,
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
        default=Path("mr08d-unchanged-ability-core-hooks.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_damage_and_speed(root)
    patch_wonder_skin(root)
    patch_bulletproof(root)
    patch_on_hit_family(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08D_UNCHANGED_ABILITY_CORE_HOOKS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 35,
        "policy": "Official/current-mainline mechanics only in this fast pass.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08D validation failed")


if __name__ == "__main__":
    main()
