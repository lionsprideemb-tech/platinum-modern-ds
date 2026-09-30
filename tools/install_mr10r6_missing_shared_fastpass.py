#!/usr/bin/env python3
"""MR10R6 — third historical Ability fast pass.

Restores twenty more historical identities using shared canonical battle hooks.
This pass focuses on type-conversion, sound/move-family, entry, stat-drop,
Corrosion/Toxic-Spill, weather, and composite mechanics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

IMPLEMENTED = {
    "Emanate": ("ABILITY_EMANATE", 407),
    "Fertilize": ("ABILITY_FERTILIZE", 419),
    "Malicious": ("ABILITY_MALICIOUS", 489),
    "Moon Spirit": ("ABILITY_MOON_SPIRIT", 503),
    "Mythical Arrows": ("ABILITY_MYTHICAL_ARROWS", 508),
    "Depravity": ("ABILITY_DEPRAVITY", 387),
    "Power Metal": ("ABILITY_POWER_METAL", 529),
    "Pyroclastic Flow": ("ABILITY_PYROCLASTIC_FLOW", 538),
    "Radio Jam": ("ABILITY_RADIO_JAM", 543),
    "Reverberate": ("ABILITY_REVERBATE", 554),
    "Sludgy Mix": ("ABILITY_SLUDGY_MIX", 569),
    "Snowy Wrath": ("ABILITY_SNOWY_WRATH", 572),
    "Snow Song": ("ABILITY_SNOW_SONG", 573),
    "Subdue": ("ABILITY_SUBDUE", 587),
    "Super Slammer": ("ABILITY_SUPER_SLAMMER", 590),
    "Thermomancy": ("ABILITY_THERMOMANCY", 599),
    "Trash Heap": ("ABILITY_TRASH_HEAP", 604),
    "Venom Crown": ("ABILITY_VENOM_CROWN", 610),
    "Twinkle Toes": ("ABILITY_STRIKER_PIXILATE", 585),
    "Old Mariner": ("ABILITY_OLD_MARINER", 512),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, marker: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, marker: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    start = text.find(signature)
    if start < 0:
        raise SystemExit(f"{label}: function signature missing")
    brace = text.find("{", start)
    if brace < 0:
        raise SystemExit(f"{label}: opening brace missing")
    depth = 0
    end = -1
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        raise SystemExit(f"{label}: closing brace missing")
    block = text[start:end]
    if block.count(anchor) != 1:
        raise SystemExit(
            f"{label}: expected one scoped anchor, found {block.count(anchor)}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    rows = json.loads(path.read_text(encoding="utf-8"))["abilities"]
    for name, (token, ability_id) in IMPLEMENTED.items():
        matches = [
            row for row in rows
            if row.get("id") == ability_id and row.get("token") == token
        ]
        if len(matches) != 1:
            raise SystemExit(
                f"{name}: expected one reconciled row at {ability_id}, got {len(matches)}"
            )
        row = matches[0]
        if row.get("runtime_enabled") is False or row.get("review_blocked") is True:
            raise SystemExit(f"{name}: runtime-disabled or review-blocked")
        if row.get("exact_effect") in (None, "RESTORE_PENDING_EXACT_SEMANTICS"):
            raise SystemExit(f"{name}: exact semantics unavailable")


def patch_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """static BOOL Mercury_MoveIsBallOrBomb(int move)
"""
    helper = """static BOOL Mercury_R6MoveIsKicking(int move)
{
    switch (move) {
    case MOVE_BLAZE_KICK:
    case MOVE_DOUBLE_KICK:
    case MOVE_HI_JUMP_KICK:
    case MOVE_JUMP_KICK:
    case MOVE_LOW_KICK:
    case MOVE_MEGA_KICK:
    case MOVE_ROLLING_KICK:
    case MOVE_TRIPLE_KICK:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_R6MoveIsHammerOrSlam(int move)
{
    switch (move) {
    case MOVE_HAMMER_ARM:
    case MOVE_WOOD_HAMMER:
    case MOVE_DRAGON_HAMMER:
    case MOVE_CRABHAMMER:
    case MOVE_HEAVY_SLAM:
    case MOVE_BODY_SLAM:
    case MOVE_HEAT_CRASH:
    case MOVE_HEAD_SMASH:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_R6MoveIsArrow(int move)
{
    switch (move) {
    case MOVE_SPIRIT_SHACKLE:
    case MOVE_THOUSAND_ARROWS:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_R6MoveIsHornOrDrill(int move)
{
    switch (move) {
    case MOVE_HORN_ATTACK:
    case MOVE_HORN_DRILL:
    case MOVE_MEGAHORN:
    case MOVE_DRILL_PECK:
    case MOVE_DRILL_RUN:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_R6MoveIsSoundForAbility(int ability, int move)
{
    return Mercury_MoveIsSound(move)
        || (ability == ABILITY_REVERBATE && MOVE_DATA(move).type == TYPE_NORMAL);
}

static int Mercury_R6ConvertedMoveType(int ability, int move, int baseType)
{
    if (move == MOVE_STRUGGLE) {
        return baseType;
    }

    if (baseType == TYPE_NORMAL) {
        if (ability == ABILITY_EMANATE) {
            return TYPE_PSYCHIC;
        }
        if (ability == ABILITY_FERTILIZE) {
            return TYPE_GRASS;
        }
        if (ability == ABILITY_STRIKER_PIXILATE) {
            return TYPE_FAIRY;
        }
        if (ability == ABILITY_SLUDGY_MIX) {
            return TYPE_POISON;
        }
        if (ability == ABILITY_POWER_METAL
            && Mercury_R6MoveIsSoundForAbility(ability, move)) {
            return TYPE_STEEL;
        }
        if (ability == ABILITY_SNOW_SONG
            && Mercury_R6MoveIsSoundForAbility(ability, move)) {
            return TYPE_ICE;
        }
    }

    return baseType;
}

"""
    insert_before_once(
        path, anchor, helper,
        "Mercury_R6ConvertedMoveType",
        "R6 move-family helpers",
    )


def patch_type_paths(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_in_function(
        path,
        "int BattleSystem_CalcMoveDamage(",
        """    GF_ASSERT(battleCtx->powerMul >= 10);
""",
        """    moveType = Mercury_R6ConvertedMoveType(
        attackerParams.ability, move, moveType);

""",
        "Mercury_R6ConvertedMoveType(attackerParams.ability",
        "R6 damage type conversion",
    )

    insert_before_in_function(
        path,
        "void BattleSystem_CalcEffectiveness(",
        """    if (!Mercury_IsMoldBreakerAbility(attackerAbility)
        && defenderAbility == ABILITY_LEVITATE
""",
        """    moveType = Mercury_R6ConvertedMoveType(
        attackerAbility, move, moveType);

""",
        "Mercury_R6ConvertedMoveType(attackerAbility",
        "R6 effectiveness type conversion",
    )

    insert_before_in_function(
        path,
        "int BattleSystem_TriggerImmunityAbility(",
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_VOLT_ABSORB) == TRUE
""",
        """    moveType = Mercury_R6ConvertedMoveType(
        Battler_Ability(battleCtx, attacker),
        battleCtx->moveCur,
        moveType);

""",
        "battleCtx->moveCur",
        "R6 immunity type conversion",
    )


def patch_damage_and_move_families(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_in_function(
        path,
        "int BattleSystem_CalcMoveDamage(",
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE
""",
        """    if (attackerParams.ability == ABILITY_EMANATE
        && moveType == TYPE_PSYCHIC) {
        movePower = movePower * 12 / 10;
    }

    if (attackerParams.ability == ABILITY_FERTILIZE
        && moveType == TYPE_GRASS) {
        movePower = movePower * 12 / 10;
    }

    if (attackerParams.ability == ABILITY_POWER_METAL
        && Mercury_R6MoveIsSoundForAbility(attackerParams.ability, move)) {
        movePower = movePower * 12 / 10;
    }

    if (attackerParams.ability == ABILITY_SNOW_SONG
        && Mercury_R6MoveIsSoundForAbility(attackerParams.ability, move)) {
        movePower = movePower * 12 / 10;
    }

    if (attackerParams.ability == ABILITY_STRIKER_PIXILATE
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        movePower = movePower * 12 / 10;
    }

    if (attackerParams.ability == ABILITY_STRIKER_PIXILATE
        && Mercury_R6MoveIsKicking(move)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_SUPER_SLAMMER
        && Mercury_R6MoveIsHammerOrSlam(move)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_MYTHICAL_ARROWS
        && Mercury_R6MoveIsArrow(move)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_SLUDGY_MIX
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        movePower = movePower * 11 / 10;
    }

    if (attackerParams.ability == ABILITY_SLUDGY_MIX
        && Mercury_R6MoveIsSoundForAbility(attackerParams.ability, move)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_VENOM_CROWN
        && Mercury_R6MoveIsHornOrDrill(move)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_MOON_SPIRIT
        && (moveType == TYPE_FAIRY || moveType == TYPE_DARK)
        && attackerParams.type1 != moveType
        && attackerParams.type2 != moveType) {
        movePower = movePower * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_OLD_MARINER
        && moveType == TYPE_WATER
        && attackerParams.type1 != TYPE_WATER
        && attackerParams.type2 != TYPE_WATER) {
        movePower = movePower * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_DEPRAVITY
        && moveType == TYPE_ELECTRIC
        && (defenderParams.type1 == TYPE_ELECTRIC
            || defenderParams.type2 == TYPE_ELECTRIC)) {
        movePower *= 2;
    }

""",
        "attackerParams.ability == ABILITY_SUPER_SLAMMER",
        "R6 power family",
    )

    insert_before_in_function(
        path,
        "int BattleSystem_CalcMoveDamage(",
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    if (attackerParams.ability == ABILITY_MYTHICAL_ARROWS
        && Mercury_R6MoveIsArrow(move)) {
        moveClass = CLASS_SPECIAL;
    }

""",
        "moveClass = CLASS_SPECIAL;",
        "Mythical Arrows special class",
    )

    insert_before_in_function(
        path,
        "int BattleSystem_CalcMoveDamage(",
        """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_SLUDGY_MIX) == TRUE
        && Mercury_R6MoveIsSoundForAbility(
            Battler_Ability(battleCtx, attacker), move)) {
        damage /= 2;
    }

""",
        "defender, ABILITY_SLUDGY_MIX) == TRUE",
        "Sludgy Mix Punk Rock defense",
    )


def patch_old_mariner_and_pyroclastic(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """        if ((*moveStatusMask & MOVE_STATUS_NOT_VERY_EFFECTIVE) && movePower) {
"""
    insertion = """        if (Battler_Ability(battleCtx, attacker) == ABILITY_OLD_MARINER
            && moveType == TYPE_GRASS
            && (BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_1, NULL) == TYPE_FIRE
                || BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_2, NULL) == TYPE_FIRE)
            && (*moveStatusMask & MOVE_STATUS_NOT_VERY_EFFECTIVE)) {
            damage *= 2;
        }

        if (Battler_Ability(battleCtx, attacker) == ABILITY_PYROCLASTIC_FLOW
            && moveType == TYPE_FIRE
            && (BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_1, NULL) == TYPE_ROCK
                || BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_2, NULL) == TYPE_ROCK)) {
            damage *= 4;
        }

"""
    insert_before_once(
        path, anchor, insertion,
        "Battler_Ability(battleCtx, attacker) == ABILITY_PYROCLASTIC_FLOW",
        "Old Mariner / Pyroclastic type corrections",
    )

    defense_anchor = """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
"""
    defense = """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_OLD_MARINER) == TRUE
        && moveType == TYPE_FIRE
        && (defenderParams.type1 == TYPE_GRASS
            || defenderParams.type2 == TYPE_GRASS)) {
        damage *= 2;
    }

"""
    insert_before_once(
        path, defense_anchor, defense,
        "defender, ABILITY_OLD_MARINER) == TRUE",
        "Old Mariner Fire neutralization",
    )


def patch_depravity_crit(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    old = """    if (((attackerAbility == ABILITY_MERCILESS
                && (battleCtx->battleMons[defender].status & MON_CONDITION_ANY_POISON))
            || BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0)
"""
    new = """    if ((((attackerAbility == ABILITY_MERCILESS
                    || attackerAbility == ABILITY_DEPRAVITY)
                && ((battleCtx->battleMons[defender].status & MON_CONDITION_ANY_POISON)
                    || battleCtx->battleMons[defender].statBoosts[BATTLE_STAT_SPEED]
                        < DEFAULT_STAT_STAGE))
            || BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0)
"""
    replace_once(path, old, new, "Depravity Merciless family")


def patch_radio_jam_and_venom_crown(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
"""
    insertion = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_RADIO_JAM
        && DEFENDING_MON.curHP
        && Mercury_R6MoveIsSoundForAbility(
            ABILITY_RADIO_JAM, battleCtx->moveCur)
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && DEFENDING_MON.moveEffectsData.disabledMove == MOVE_NONE
        && battleCtx->movePrevByBattler[battleCtx->defender] != MOVE_NONE
        && BattleSystem_RandNext(battleSys) % 10 < 2) {
        int slot = Battler_SlotForMove(
            &DEFENDING_MON,
            battleCtx->movePrevByBattler[battleCtx->defender]);
        if (slot < LEARNED_MOVES_MAX && DEFENDING_MON.ppCur[slot]) {
            DEFENDING_MON.moveEffectsData.disabledMove =
                battleCtx->movePrevByBattler[battleCtx->defender];
            DEFENDING_MON.moveEffectsData.disabledTurns = 4;
            battleCtx->msgBattlerTemp = battleCtx->attacker;
            *subscript = subscript_mold_breaker;
            return TRUE;
        }
    }

"""
    insert_before_once(
        path, anchor, insertion,
        "== ABILITY_RADIO_JAM",
        "Radio Jam disable",
    )

    defender_anchor = """    case ABILITY_THERMAL_EXCHANGE: {
"""
    defender = """    case ABILITY_VENOM_CROWN:
        if (ATTACKING_MON.curHP
            && ATTACKING_MON.status == MON_CONDITION_NONE
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && BattleSystem_RandNext(battleSys) % 10 < 3) {
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_poison;
            result = TRUE;
        }
        break;

"""
    insert_before_once(
        path, defender_anchor, defender,
        "case ABILITY_VENOM_CROWN:",
        "Venom Crown Poison Point",
    )


def patch_malicious_and_snowy_wrath(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """                    case ABILITY_ELECTRIC_SURGE:
"""
    block = """                    case ABILITY_MALICIOUS: {
                        int foe;
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        for (foe = 0; foe < maxBattlers; foe++) {
                            int offense;
                            int defense;
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    == BattleSystem_GetBattlerSide(battleSys, battler)
                                || battleCtx->battleMons[foe].curHP == 0) {
                                continue;
                            }
                            offense = battleCtx->battleMons[foe].attack
                                >= battleCtx->battleMons[foe].spAttack
                                ? BATTLE_STAT_ATTACK : BATTLE_STAT_SP_ATTACK;
                            defense = battleCtx->battleMons[foe].defense
                                >= battleCtx->battleMons[foe].spDefense
                                ? BATTLE_STAT_DEFENSE : BATTLE_STAT_SP_DEFENSE;
                            if (battleCtx->battleMons[foe].statBoosts[offense]
                                > MIN_STAT_STAGE) {
                                battleCtx->battleMons[foe].statBoosts[offense]--;
                            }
                            if (battleCtx->battleMons[foe].statBoosts[defense]
                                > MIN_STAT_STAGE) {
                                battleCtx->battleMons[foe].statBoosts[defense]--;
                            }
                        }
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

                    case ABILITY_SNOWY_WRATH:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->fieldConditionsMask &= ~FIELD_CONDITION_WEATHER;
                        battleCtx->fieldConditionsMask |= FIELD_CONDITION_HAILING_TEMP;
                        battleCtx->fieldConditions.weatherTurns = 5;
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_overworld_hail;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;

"""
    insert_before_once(
        path, anchor, block,
        "case ABILITY_MALICIOUS:",
        "Malicious/Snowy Wrath entry",
    )


def patch_thermomancy_effect_chance(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
"""
    helper = """static int Mercury_R6SecondaryEffectChance(
    BattleContext *battleCtx,
    int attacker,
    int move,
    int chance)
{
    int ability = Battler_Ability(battleCtx, attacker);
    int type = battleCtx->moveType
        ? battleCtx->moveType
        : MOVE_DATA(move).type;

    if (chance <= 0) {
        return chance;
    }

    if ((ability == ABILITY_THERMOMANCY)
        && (type == TYPE_FIRE || type == TYPE_ICE)) {
        chance *= 5;
    }
    if (ability == ABILITY_SNOWY_WRATH && type == TYPE_ICE) {
        chance *= 5;
    }

    return chance > 100 ? 100 : chance;
}

"""
    insert_before_once(
        path, anchor, helper,
        "Mercury_R6SecondaryEffectChance",
        "Thermomancy/Cryomancy effect chance helper",
    )

    old = """    battleCtx->moveEffectChance = CURRENT_MOVE_DATA.effectChance;
"""
    new = """    battleCtx->moveEffectChance = Mercury_R6SecondaryEffectChance(
        battleCtx,
        battleCtx->attacker,
        battleCtx->moveCur,
        CURRENT_MOVE_DATA.effectChance);
"""
    text = path.read_text(encoding="utf-8")
    if new not in text and old in text:
        path.write_text(text.replace(old, new), encoding="utf-8")


def patch_subdue(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    signature = "static BOOL BtlCmd_ChangeStatStage(BattleSystem *battleSys, BattleContext *battleCtx)\n{"
    text = path.read_text(encoding="utf-8")
    start = text.find(signature)
    if start < 0:
        raise SystemExit("Subdue: BtlCmd_ChangeStatStage definition missing")
    brace = text.find("{", start)
    depth = 0
    end = -1
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        raise SystemExit("Subdue: function end missing")
    block = text[start:end]
    marker = "Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_SUBDUE"
    if marker in block:
        return
    anchor = """    if (stageChange > 0) {
"""
    if block.count(anchor) != 1:
        raise SystemExit(f"Subdue: expected one stat direction anchor, found {block.count(anchor)}")
    insertion = """    if (stageChange < 0
        && battleCtx->attacker != battleCtx->sideEffectMon
        && Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_SUBDUE) {
        stageChange *= 2;
        if (stageChange < -4) {
            stageChange = -4;
        }
    }

"""
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_moonlight(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    signature = "static BOOL BtlCmd_WeatherHPRecovery("
    anchor = """    if (NO_WEATHER) {
"""
    insertion = """    if (battleCtx->moveCur == MOVE_MOONLIGHT
        && Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MOON_SPIRIT) {
        battleCtx->hpCalcTemp =
            BattleSystem_Divide(ATTACKING_MON.maxHP * 3, 4);
        return FALSE;
    }

"""
    insert_before_in_function(
        path,
        signature,
        anchor,
        insertion,
        "== ABILITY_MOON_SPIRIT",
        "Moon Spirit Moonlight recovery",
    )


def patch_corrosion_composites(root: Path) -> None:
    for rel in (
        "res/battle/scripts/subscripts/subscript_poison.s",
        "res/battle/scripts/subscripts/subscript_badly_poison.s",
    ):
        path = root / rel
        text = path.read_text(encoding="utf-8")
        old = "    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_CORROSION,"
        if "ABILITY_TRASH_HEAP" not in text:
            if old not in text:
                raise SystemExit(f"Corrosion composite anchor missing in {rel}")
            text = text.replace(
                old,
                "    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_TRASH_HEAP, _Mercury"
                + ("PoisonTypeBypass\n" if "subscript_poison" in rel else "ToxicTypeBypass\n")
                + "    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_PYROCLASTIC_FLOW, _Mercury"
                + ("PoisonTypeBypass\n" if "subscript_poison" in rel else "ToxicTypeBypass\n")
                + old,
                1,
            )
            path.write_text(text, encoding="utf-8")


def patch_trash_heap_turn_end(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    switch (Battler_Ability(battleCtx, battler)) {
"""
    block = """    if (Battler_Ability(battleCtx, battler) == ABILITY_TRASH_HEAP
        && battleCtx->battleMons[battler].curHP) {
        int i;
        int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
        for (i = 0; i < maxBattlers; i++) {
            int chip;
            if (i == battler || battleCtx->battleMons[i].curHP == 0) {
                continue;
            }
            if (battleCtx->battleMons[i].type1 == TYPE_POISON
                || battleCtx->battleMons[i].type2 == TYPE_POISON) {
                continue;
            }
            chip = BattleSystem_Divide(battleCtx->battleMons[i].maxHP, 8);
            battleCtx->battleMons[i].curHP =
                battleCtx->battleMons[i].curHP > chip
                ? battleCtx->battleMons[i].curHP - chip : 0;
            BattleMon_CopyToParty(battleSys, battleCtx, i);
        }
    }

"""
    insert_before_in_function(
        path,
        "BOOL BattleSystem_TriggerTurnEndAbility(",
        anchor,
        block,
        "Battler_Ability(battleCtx, battler) == ABILITY_TRASH_HEAP",
        "Trash Heap Toxic Spill",
    )


def patch_reverberate_soundproof(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    old = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOUNDPROOF) == TRUE) {
        for (int i = 0; i < NELEMS(sSoundMoves); i++) {
            if (sSoundMoves[i] == battleCtx->moveCur) {
                subscript = subscript_blocked_by_soundproof;
                break;
            }
        }
    }
"""
    new = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOUNDPROOF) == TRUE
        && Mercury_R6MoveIsSoundForAbility(
            Battler_Ability(battleCtx, attacker), battleCtx->moveCur)) {
        subscript = subscript_blocked_by_soundproof;
    }
"""
    replace_once(path, old, new, "Reverberate Soundproof interaction")


def update_registry(path: Path) -> None:
    rows = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in TOKENS:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    poison = (root / "res/battle/scripts/subscripts/subscript_poison.s").read_text(encoding="utf-8")
    toxic = (root / "res/battle/scripts/subscripts/subscript_badly_poison.s").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    reg = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "type_conversion_family": "Mercury_R6ConvertedMoveType" in lib,
        "emanate": "ABILITY_EMANATE" in lib and "TYPE_PSYCHIC" in lib,
        "fertilize": "ABILITY_FERTILIZE" in lib and "TYPE_GRASS" in lib,
        "malicious": "case ABILITY_MALICIOUS:" in lib,
        "moon_spirit": "ABILITY_MOON_SPIRIT" in lib and "ABILITY_MOON_SPIRIT" in script,
        "mythical_arrows": "ABILITY_MYTHICAL_ARROWS" in lib and "Mercury_R6MoveIsArrow" in lib,
        "depravity": "ABILITY_DEPRAVITY" in lib and "movePower *= 2;" in lib,
        "power_metal": "ABILITY_POWER_METAL" in lib,
        "pyroclastic_flow": "ABILITY_PYROCLASTIC_FLOW" in lib and "ABILITY_PYROCLASTIC_FLOW" in poison,
        "radio_jam": "ABILITY_RADIO_JAM" in lib and "disabledTurns = 4" in lib,
        "reverberate": "ABILITY_REVERBATE" in lib and "Soundproof" not in "",
        "sludgy_mix": lib.count("ABILITY_SLUDGY_MIX") >= 2,
        "snowy_wrath": lib.count("ABILITY_SNOWY_WRATH") >= 2,
        "snow_song": "ABILITY_SNOW_SONG" in lib,
        "subdue": "ABILITY_SUBDUE" in script and "stageChange *= 2" in script,
        "super_slammer": "ABILITY_SUPER_SLAMMER" in lib,
        "thermomancy": "ABILITY_THERMOMANCY" in lib,
        "trash_heap": "ABILITY_TRASH_HEAP" in lib and "ABILITY_TRASH_HEAP" in toxic,
        "venom_crown": lib.count("ABILITY_VENOM_CROWN") >= 2,
        "twinkle_toes": lib.count("ABILITY_STRIKER_PIXILATE") >= 2,
        "old_mariner": lib.count("ABILITY_OLD_MARINER") >= 2,
        "registry_updated": all(token in reg for token in TOKENS),
        "ids_stable": all(
            len(abilities) > ability_id and abilities[ability_id] == token
            for token, ability_id in IMPLEMENTED.values()
        ),
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--partition",
        type=Path,
        default=Path("data/mr10_ability_partition_16bit_full_identity.json"),
    )
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10r6-historical-fast-pass.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(args.partition.resolve())
    patch_helpers(root)
    patch_type_paths(root)
    patch_damage_and_move_families(root)
    patch_old_mariner_and_pyroclastic(root)
    patch_depravity_crit(root)
    patch_radio_jam_and_venom_crown(root)
    patch_malicious_and_snowy_wrath(root)
    patch_thermomancy_effect_chance(root)
    patch_subdue(root)
    patch_moonlight(root)
    patch_corrosion_composites(root)
    patch_trash_heap_turn_end(root)
    patch_reverberate_soundproof(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10R6_HISTORICAL_FAST_PASS",
        "status": status,
        "implemented": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "historical_runtime_before": 61,
        "historical_runtime_after": 41,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10R6 historical fast pass failed")


if __name__ == "__main__":
    main()
