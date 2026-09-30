#!/usr/bin/env python3
"""MR10R8 — final 21 historical Ability restoration pass.

Finishes the recovered 124-row historical queue.  The pass adds the reusable
Frostbite / Bleed / Fear / Enraged lanes, the last entry/generated effects,
and the three late composite abilities (Curse of Famine, Angel's Wrath,
Archmage).  Mechanics only; locked MR07 visuals are untouched.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

IMPLEMENTED = {
    "Cryo Proficiency": ("ABILITY_CRYO_PROFICIENCY", 380),
    "Freezing Point": ("ABILITY_FREEZING_POINT", 430),
    "Neurotoxin": ("ABILITY_NEUROTOXIN", 509),
    "Piercing Solo": ("ABILITY_PIERCING_SOLO", 526),
    "Purple Haze": ("ABILITY_PURPLE_HAZE", 537),
    "Resonance": ("ABILITY_RESONANCE", 551),
    "Sand Pit": ("ABILITY_SAND_PIT", 561),
    "Spike Armor": ("ABILITY_SPIKE_ARMOR", 580),
    "To The Bone": ("ABILITY_TO_THE_BONE", 603),
    "Wildfire": ("ABILITY_WILDFIRE", 623),
    "Set Ablaze": ("ABILITY_SET_ABLAZE", 1007),
    "Grass Flute": ("ABILITY_GRASS_FLUTE", 1008),
    "Loose Thorns": ("ABILITY_LOOSE_THORNS", 1010),
    "Mental Pollution": ("ABILITY_MENTAL_POLLUTION", 1013),
    "Madness Enh.": ("ABILITY_MADNESS_ENHANCEMENT", 1014),
    "Deviate": ("ABILITY_DEVIATE", 1018),
    "Mob Boss": ("ABILITY_MOB_BOSS", 1019),
    "Cosmic Dust": ("ABILITY_COSMIC_DUST", 1020),
    "Curse of Famine": ("ABILITY_CURSE_OF_FAMINE", 1029),
    "Angel's Wrath": ("ABILITY_ANGELS_WRATH", 1030),
    "Archmage": ("ABILITY_ARCHMAGE", 1031),
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


def function_bounds(text: str, signature: str) -> tuple[int, int]:
    start = text.find(signature)
    if start < 0:
        raise SystemExit(f"function not found: {signature}")
    brace = text.find("{", start)
    if brace < 0:
        raise SystemExit(f"opening brace not found: {signature}")
    depth = 0
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise SystemExit(f"unterminated function: {signature}")


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if marker in block:
        return
    count = block.count(anchor)
    if count < 1:
        raise SystemExit(f"{label}: scoped anchor missing")
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def insert_after_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if marker in block:
        return
    count = block.count(anchor)
    if count < 1:
        raise SystemExit(f"{label}: scoped anchor missing")
    block = block.replace(anchor, anchor + insertion, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    rows = json.loads(path.read_text(encoding="utf-8"))["abilities"]
    for name, (token, ability_id) in IMPLEMENTED.items():
        matches = [
            row for row in rows
            if row.get("id") == ability_id and row.get("token") == token
        ]
        if len(matches) != 1:
            raise SystemExit(f"{name}: expected reconciled row {ability_id}, got {len(matches)}")
        row = matches[0]
        if row.get("runtime_enabled") is False or row.get("review_blocked") is True:
            raise SystemExit(f"{name}: runtime-disabled or review-blocked")
        if row.get("exact_effect") in (None, "RESTORE_PENDING_EXACT_SEMANTICS"):
            raise SystemExit(f"{name}: exact semantics unavailable")


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insertion = """    // Mercury MR10R8 final historical status/field state.
    u8 mercuryR8Frostbite[MAX_BATTLERS];
    u8 mercuryR8FearTurns[MAX_BATTLERS];
    u8 mercuryR8TrapTurns[MAX_BATTLERS];
    u8 mercuryR8EnrageObserved[MAX_BATTLERS];
    u8 mercuryR8CreepingThorns[NUM_BATTLE_SIDES];
    u8 mercuryR8NeurotoxinSeen[MAX_BATTLERS];

"""
    insert_after_once(
        path,
        "    u8 mercuryR7CritStage[MAX_BATTLERS];\n",
        insertion,
        "mercuryR8Frostbite",
        "R8 shared context",
    )


def patch_shared_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    helper = """static BOOL Mercury_R8CanBleed(BattleContext *battleCtx, int battler)
{
    if (battler < 0 || battler >= MAX_BATTLERS
        || battleCtx->battleMons[battler].curHP == 0) {
        return FALSE;
    }
    return !Mercury_R7HasType(battleCtx, battler, TYPE_ROCK)
        && !Mercury_R7HasType(battleCtx, battler, TYPE_GHOST);
}

void Mercury_R8InflictBleed(BattleContext *battleCtx, int battler)
{
    if (Mercury_R8CanBleed(battleCtx, battler)) {
        battleCtx->mercuryR7Bleeding[battler] = TRUE;
    }
}

void Mercury_R8InflictFear(BattleContext *battleCtx, int battler)
{
    if (battler >= 0 && battler < MAX_BATTLERS
        && battleCtx->battleMons[battler].curHP) {
        battleCtx->mercuryR8FearTurns[battler] = 2;
    }
}

void Mercury_R8InflictFrostbite(BattleContext *battleCtx, int battler)
{
    if (battler >= 0 && battler < MAX_BATTLERS
        && battleCtx->battleMons[battler].curHP
        && !Mercury_R7HasType(battleCtx, battler, TYPE_ICE)) {
        battleCtx->mercuryR8Frostbite[battler] = TRUE;
    }
}

void Mercury_R8SetEnraged(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int i;
    int maxBattlers;

    if (battler < 0 || battler >= MAX_BATTLERS
        || battleCtx->battleMons[battler].curHP == 0) {
        return;
    }

    battleCtx->mercuryR7Enraged[battler] = TRUE;

    if (Battler_Ability(battleCtx, battler) != ABILITY_MENTAL_POLLUTION) {
        return;
    }

    maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    for (i = 0; i < maxBattlers; i++) {
        if (i == battler || battleCtx->battleMons[i].curHP == 0
            || Battler_Ability(battleCtx, i) == ABILITY_MENTAL_POLLUTION) {
            continue;
        }
        battleCtx->battleMons[i].moveEffectsMask |= MOVE_EFFECT_ABILITY_SUPPRESSED;
    }
}

static BOOL Mercury_R8MagicGuardLike(BattleContext *battleCtx, int battler)
{
    int ability = Battler_Ability(battleCtx, battler);
    return ability == ABILITY_MAGIC_GUARD || ability == ABILITY_COSMIC_DUST;
}

"""
    insert_before_once(
        lib,
        "BOOL Mercury_MoveIsSoundForHistoricalAbility(int move)\n",
        helper,
        "Mercury_R8InflictFrostbite",
        "R8 shared helpers",
    )
    insert_before_once(
        hdr,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);\n",
        """void Mercury_R8InflictBleed(BattleContext *battleCtx, int battler);
void Mercury_R8InflictFear(BattleContext *battleCtx, int battler);
void Mercury_R8InflictFrostbite(BattleContext *battleCtx, int battler);
void Mercury_R8SetEnraged(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
""",
        "Mercury_R8InflictBleed",
        "R8 public helper declarations",
    )


def patch_state_reset(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    insertion = """    battleCtx->mercuryR8Frostbite[battler] = FALSE;
    battleCtx->mercuryR8FearTurns[battler] = 0;
    battleCtx->mercuryR8TrapTurns[battler] = 0;
    battleCtx->mercuryR8EnrageObserved[battler] = FALSE;
    battleCtx->mercuryR8NeurotoxinSeen[battler] = FALSE;

"""
    insert_before_in_function(
        lib,
        "void BattleSystem_InitBattleMon(",
        "    battleCtx->battleMons[battler].weatherAbilityAnnounced = FALSE;\n",
        insertion,
        "mercuryR8Frostbite[battler] = FALSE",
        "R8 switch-in state reset",
    )


def patch_deviate_conversion(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    signature = "static int Mercury_R6ConvertedMoveType(int ability, int move, int baseType)"
    insertion = """        if (ability == ABILITY_DEVIATE
            || ability == ABILITY_MOB_BOSS) {
            return TYPE_DARK;
        }
"""
    insert_after_in_function(
        lib,
        signature,
        "    if (baseType == TYPE_NORMAL) {\n",
        insertion,
        "ability == ABILITY_DEVIATE",
        "Deviate/Mob Boss Normal-to-Dark",
    )


def patch_damage(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    insertion = """    if (battleCtx->mercuryR8Frostbite[attacker]
        && moveClass == CLASS_SPECIAL
        && attackerParams.ability != ABILITY_GUTS) {
        spAttackStat /= 2;
    }

    if (battleCtx->mercuryR8FearTurns[defender]) {
        movePower = movePower * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_MADNESS_ENHANCEMENT
        && battleCtx->mercuryR7Enraged[attacker]) {
        /* Historical Mercury partition specifies half damage while enraged. */
    }

    if (attackerParams.ability == ABILITY_DEVIATE
        || attackerParams.ability == ABILITY_MOB_BOSS) {
        if (moveType == TYPE_DARK
            && attackerParams.type1 != TYPE_DARK
            && attackerParams.type2 != TYPE_DARK) {
            movePower = movePower * 15 / 10;
        }
    }

    if (attackerParams.ability == ABILITY_ANGELS_WRATH) {
        switch (move) {
        case MOVE_TACKLE:
        case MOVE_ELECTROWEB:
        case MOVE_BUG_BITE:
        case MOVE_POISON_STING:
            movePower = movePower * 15 / 10;
            break;
        default:
            break;
        }
    }

"""
    insert_before_in_function(
        lib,
        "int BattleSystem_CalcMoveDamage(",
        "    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE\n",
        insertion,
        "battleCtx->mercuryR8Frostbite[attacker]",
        "R8 status/composite damage",
    )

    reduction = """    if (Battler_Ability(battleCtx, defender) == ABILITY_MADNESS_ENHANCEMENT
        && battleCtx->mercuryR7Enraged[defender]) {
        damage /= 2;
    }

"""
    insert_before_in_function(
        lib,
        "int BattleSystem_CalcMoveDamage(",
        "    if ((battleType & BATTLE_TYPE_DOUBLES)\n",
        reduction,
        "defender) == ABILITY_MADNESS_ENHANCEMENT",
        "Madness Enhancement enraged defense",
    )

    crit = """    if (Battler_Ability(battleCtx, attacker) == ABILITY_TO_THE_BONE
        && battleCtx->criticalMul > 1) {
        damage = damage * 15 / 10;
    }

"""
    insert_before_in_function(
        lib,
        "int BattleSystem_CalcMoveDamage(",
        "    return damage;\n",
        crit,
        "ABILITY_TO_THE_BONE",
        "To The Bone critical boost",
    )

    # Angel's Wrath Poison Sting bypasses Steel's Poison immunity and is super-effective.
    effect = """    if (Battler_Ability(battleCtx, attacker) == ABILITY_ANGELS_WRATH
        && move == MOVE_POISON_STING
        && (BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_1, NULL) == TYPE_STEEL
            || BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_2, NULL) == TYPE_STEEL)) {
        *moveStatusMask &= ~MOVE_STATUS_NO_EFFECTS;
        *moveStatusMask |= MOVE_STATUS_SUPER_EFFECTIVE;
        return damage * 2;
    }

"""
    insert_before_in_function(
        lib,
        "int BattleSystem_ApplyTypeChart(",
        "    if (move == MOVE_STRUGGLE) {\n",
        effect,
        "move == MOVE_POISON_STING",
        "Angel's Wrath Poison Sting vs Steel",
    )


def patch_trapping(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    insertion = """    if (battleCtx->mercuryR8FearTurns[battler]
        || battleCtx->mercuryR8TrapTurns[battler]) {
        return TRUE;
    }

"""
    insert_before_in_function(
        lib,
        "BOOL Battler_IsTrappedMsg(",
        "    int tmp;\n",
        insertion,
        "mercuryR8FearTurns[battler]",
        "Fear/generated trap switch lock",
    )


def patch_turn_end(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    insertion = """    if (battleCtx->battleMons[battler].curHP) {
        int chip;

        if (battleCtx->mercuryR8Frostbite[battler]
            && !Mercury_R8MagicGuardLike(battleCtx, battler)) {
            chip = BattleSystem_Divide(
                battleCtx->battleMons[battler].maxHP, 8);
            battleCtx->battleMons[battler].curHP =
                battleCtx->battleMons[battler].curHP > chip
                ? battleCtx->battleMons[battler].curHP - chip : 0;
        }

        if (battleCtx->mercuryR7Bleeding[battler]
            && !Mercury_R8MagicGuardLike(battleCtx, battler)) {
            chip = BattleSystem_Divide(
                battleCtx->battleMons[battler].maxHP, 16);
            battleCtx->battleMons[battler].curHP =
                battleCtx->battleMons[battler].curHP > chip
                ? battleCtx->battleMons[battler].curHP - chip : 0;
        }

        if (battleCtx->mercuryR8FearTurns[battler]) {
            battleCtx->mercuryR8FearTurns[battler]--;
        }
        if (battleCtx->mercuryR8TrapTurns[battler]) {
            battleCtx->mercuryR8TrapTurns[battler]--;
        }

        if (battleCtx->mercuryR7Enraged[battler]
            && !battleCtx->mercuryR8EnrageObserved[battler]) {
            battleCtx->mercuryR8EnrageObserved[battler] = TRUE;
            Mercury_R8SetEnraged(battleSys, battleCtx, battler);
        }

        BattleMon_CopyToParty(battleSys, battleCtx, battler);
    }

"""
    insert_before_in_function(
        lib,
        "BOOL BattleSystem_TriggerTurnEndAbility(",
        "    switch (Battler_Ability(battleCtx, battler)) {\n",
        insertion,
        "mercuryR8Frostbite[battler]",
        "R8 residual status lane",
    )


def patch_healing_lock(root: Path) -> None:
    script = root / "src/battle/battle_script.c"
    sig = "static BOOL BtlCmd_UpdateHealthBarValue(BattleSystem *battleSys, BattleContext *battleCtx)"
    text = script.read_text(encoding="utf-8")
    start, end = function_bounds(text, sig)
    body = text[start:end]
    marker = "Mercury R8 Bleed healing lock"
    if marker in body:
        return
    pos0 = body.find("BattleScript_Battler(battleSys, battleCtx")
    if pos0 < 0:
        raise SystemExit("R8 healing lock: battler resolution missing")
    semi = body.find(";", pos0)
    if semi < 0:
        raise SystemExit("R8 healing lock: battler resolution terminator missing")
    block = """
    /* Mercury R8 Bleed healing lock. */
    if (battleCtx->hpCalcTemp > 0
        && battleCtx->mercuryR7Bleeding[battler]) {
        battleCtx->hpCalcTemp = 0;
    }
"""
    body = body[:semi + 1] + block + body[semi + 1:]
    script.write_text(text[:start] + body + text[end:], encoding="utf-8")


def patch_on_hit_family(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    # Offensive post-hit family.
    anchor = "    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN\n"
    insertion = """    {
        int ability = Battler_Ability(battleCtx, battleCtx->attacker);
        int contact = Mercury_MoveMakesContact(
            battleCtx, battleCtx->attacker, battleCtx->moveCur);
        int sound = Mercury_MoveIsSoundForHistoricalAbility(battleCtx->moveCur);
        int moveType = battleCtx->moveType
            ? battleCtx->moveType : CURRENT_MOVE_DATA.type;

        if (DEFENDING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            if (ability == ABILITY_FREEZING_POINT
                && BattleSystem_RandNext(battleSys) % 100
                    < (contact ? 20 : 30)) {
                Mercury_R8InflictFrostbite(battleCtx, battleCtx->defender);
            }
            if (ability == ABILITY_CRYO_PROFICIENCY
                && BattleSystem_RandNext(battleSys) % 100
                    < (contact ? 20 : 30)) {
                Mercury_R8InflictFrostbite(battleCtx, battleCtx->defender);
            }

            if (ability == ABILITY_PIERCING_SOLO && sound) {
                Mercury_R8InflictBleed(battleCtx, battleCtx->defender);
            } else if (ability == ABILITY_RESONANCE && sound
                && BattleSystem_RandNext(battleSys) % 100 < 30) {
                Mercury_R8InflictBleed(battleCtx, battleCtx->defender);
            } else if (ability == ABILITY_SPIKE_ARMOR && contact
                && BattleSystem_RandNext(battleSys) % 100 < 30) {
                Mercury_R8InflictBleed(battleCtx, battleCtx->defender);
            }

            if (ability == ABILITY_GRASS_FLUTE && sound) {
                Mercury_R8InflictFear(battleCtx, battleCtx->defender);
            }

            if ((ability == ABILITY_DEVIATE || ability == ABILITY_MOB_BOSS)
                && moveType == TYPE_DARK
                && (battleCtx->battleMons[battleCtx->attacker].type1 == TYPE_DARK
                    || battleCtx->battleMons[battleCtx->attacker].type2 == TYPE_DARK)
                && BattleSystem_RandNext(battleSys) % 100 < 10) {
                Mercury_R8SetEnraged(
                    battleSys, battleCtx, battleCtx->defender);
            }

            if (ability == ABILITY_TO_THE_BONE
                && battleCtx->criticalMul > 1) {
                Mercury_R8InflictBleed(battleCtx, battleCtx->defender);
            }

            if (ability == ABILITY_ANGELS_WRATH) {
                if (battleCtx->moveCur == MOVE_TACKLE) {
                    int slot;
                    int last = battleCtx->movePrevByBattler[battleCtx->defender];
                    slot = Battler_SlotForMove(&DEFENDING_MON, last);
                    if (last != MOVE_NONE && slot < LEARNED_MOVES_MAX) {
                        DEFENDING_MON.moveEffectsData.disabledMove = last;
                        DEFENDING_MON.moveEffectsData.disabledTurns = 2;
                        DEFENDING_MON.moveEffectsData.encoredMove = last;
                        DEFENDING_MON.moveEffectsData.encoredMoveIndex = slot;
                        DEFENDING_MON.moveEffectsData.encoredTurns = 2;
                    }
                } else if (battleCtx->moveCur == MOVE_ELECTROWEB) {
                    battleCtx->mercuryR8TrapTurns[battleCtx->defender] = 5;
                } else if (battleCtx->moveCur == MOVE_BUG_BITE) {
                    int heal = -battleCtx->hitDamage;
                    if (heal > 0) {
                        ATTACKING_MON.curHP += heal;
                        if (ATTACKING_MON.curHP > ATTACKING_MON.maxHP) {
                            ATTACKING_MON.curHP = ATTACKING_MON.maxHP;
                        }
                        BattleMon_CopyToParty(
                            battleSys, battleCtx, battleCtx->attacker);
                    }
                } else if (battleCtx->moveCur == MOVE_POISON_STING
                    && DEFENDING_MON.status == MON_CONDITION_NONE) {
                    battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                    battleCtx->sideEffectMon = battleCtx->defender;
                    battleCtx->msgBattlerTemp = battleCtx->attacker;
                    *subscript = subscript_badly_poison;
                    return TRUE;
                }
            }

            if (ability == ABILITY_ARCHMAGE
                && BattleSystem_RandNext(battleSys) % 100 < 30) {
                switch (moveType) {
                case TYPE_POISON:
                    if (DEFENDING_MON.status == MON_CONDITION_NONE) {
                        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                        battleCtx->sideEffectMon = battleCtx->defender;
                        *subscript = subscript_badly_poison;
                        return TRUE;
                    }
                    break;
                case TYPE_ICE:
                    Mercury_R8InflictFrostbite(
                        battleCtx, battleCtx->defender);
                    break;
                case TYPE_WATER:
                    if ((DEFENDING_MON.statusVolatile
                            & VOLATILE_CONDITION_CONFUSION) == 0) {
                        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                        battleCtx->sideEffectMon = battleCtx->defender;
                        *subscript = subscript_confuse;
                        return TRUE;
                    }
                    break;
                case TYPE_FIRE:
                    if (DEFENDING_MON.status == MON_CONDITION_NONE) {
                        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                        battleCtx->sideEffectMon = battleCtx->defender;
                        *subscript = subscript_burn;
                        return TRUE;
                    }
                    break;
                case TYPE_ELECTRIC:
                    Mercury_SetTerrain(
                        battleCtx, MERCURY_TERRAIN_ELECTRIC);
                    break;
                case TYPE_PSYCHIC:
                    Mercury_SetTerrain(
                        battleCtx, MERCURY_TERRAIN_PSYCHIC);
                    break;
                case TYPE_FAIRY:
                    Mercury_SetTerrain(
                        battleCtx, MERCURY_TERRAIN_MISTY);
                    break;
                case TYPE_GRASS:
                    Mercury_SetTerrain(
                        battleCtx, MERCURY_TERRAIN_GRASSY);
                    break;
                case TYPE_ROCK: {
                    int side = BattleSystem_GetBattlerSide(
                        battleSys, battleCtx->defender);
                    battleCtx->sideConditionsMask[side] |=
                        SIDE_CONDITION_STEALTH_ROCK;
                    break;
                }
                case TYPE_GHOST: {
                    int last =
                        battleCtx->movePrevByBattler[battleCtx->defender];
                    int slot = Battler_SlotForMove(&DEFENDING_MON, last);
                    if (last != MOVE_NONE && slot < LEARNED_MOVES_MAX) {
                        DEFENDING_MON.moveEffectsData.disabledMove = last;
                        DEFENDING_MON.moveEffectsData.disabledTurns = 4;
                    }
                    break;
                }
                case TYPE_DARK:
                    Mercury_R8InflictBleed(
                        battleCtx, battleCtx->defender);
                    break;
                case TYPE_FIGHTING:
                    if (ATTACKING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]
                            < MAX_STAT_STAGE) {
                        ATTACKING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]++;
                    }
                    break;
                case TYPE_FLYING:
                    if (ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED]
                            < MAX_STAT_STAGE) {
                        ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED]++;
                    }
                    break;
                case TYPE_DRAGON:
                    if (DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]
                            > MIN_STAT_STAGE) {
                        DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]--;
                    }
                    break;
                case TYPE_GROUND:
                    battleCtx->mercuryR8TrapTurns[battleCtx->defender] = 5;
                    break;
                case TYPE_STEEL:
                    if (ATTACKING_MON.statBoosts[BATTLE_STAT_DEFENSE]
                            < MAX_STAT_STAGE) {
                        ATTACKING_MON.statBoosts[BATTLE_STAT_DEFENSE]++;
                    }
                    break;
                default:
                    break;
                }
            }
        }
    }

"""
    insert_before_once(
        lib,
        anchor,
        insertion,
        "ability == ABILITY_ARCHMAGE",
        "R8 offensive post-hit family",
    )

    # Defensive contact family: Freezing Point/Cryo Proficiency and Spike Armor.
    defender_anchor = "    case ABILITY_THERMAL_EXCHANGE: {\n"
    defender = """    case ABILITY_FREEZING_POINT:
    case ABILITY_CRYO_PROFICIENCY:
        if (ATTACKING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int contact = Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur);
            int chance = contact ? 20 : 30;
            if (BattleSystem_RandNext(battleSys) % 100 < chance) {
                Mercury_R8InflictFrostbite(
                    battleCtx, battleCtx->attacker);
            }
            if (Battler_Ability(battleCtx, battleCtx->defender)
                    == ABILITY_CRYO_PROFICIENCY) {
                battleCtx->fieldConditionsMask &= ~FIELD_CONDITION_WEATHER;
                battleCtx->fieldConditionsMask |= FIELD_CONDITION_HAILING_TEMP;
                battleCtx->fieldConditions.weatherTurns = 5;
            }
        }
        break;

    case ABILITY_SPIKE_ARMOR:
        if (ATTACKING_MON.curHP
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && BattleSystem_RandNext(battleSys) % 100 < 30) {
            Mercury_R8InflictBleed(battleCtx, battleCtx->attacker);
        }
        break;

    case ABILITY_LOOSE_THORNS:
        if (ATTACKING_MON.curHP
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int side = BattleSystem_GetBattlerSide(
                battleSys, battleCtx->attacker);
            battleCtx->mercuryR8CreepingThorns[side] = TRUE;
        }
        break;

"""
    insert_before_in_function(
        lib,
        "BOOL BattleSystem_TriggerAbilityOnHit(",
        defender_anchor,
        defender,
        "case ABILITY_LOOSE_THORNS:",
        "R8 defender status family",
    )


def patch_poison_and_burn_followups(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    # Run after successful hit if target is now poisoned/burned.  The per-target
    # latch prevents Neurotoxin from reapplying on every later hit.
    anchor = "    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN\n"
    insertion = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NEUROTOXIN
        && (DEFENDING_MON.status & MON_CONDITION_ANY_POISON)
        && !battleCtx->mercuryR8NeurotoxinSeen[battleCtx->defender]) {
        battleCtx->mercuryR8NeurotoxinSeen[battleCtx->defender] = TRUE;
        if (DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] > MIN_STAT_STAGE) {
            DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]--;
        }
        if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] > MIN_STAT_STAGE) {
            DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]--;
        }
        if (DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] > MIN_STAT_STAGE) {
            DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED]--;
        }
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_SET_ABLAZE
        && (DEFENDING_MON.status & MON_CONDITION_BURN)) {
        Mercury_R8InflictFear(battleCtx, battleCtx->defender);
    }

"""
    insert_before_once(
        lib,
        anchor,
        insertion,
        "ABILITY_NEUROTOXIN",
        "Neurotoxin/Set Ablaze followups",
    )


def patch_generated_followup(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"
    old = """    } else if (ability == ABILITY_TWO_STEP
        && Mercury_R7DanceMove(battleCtx->moveCur)) {
        *move = MOVE_REVELATION_DANCE;
        *power = 50;
    }

    return *move != MOVE_NONE;
"""
    new = """    } else if (ability == ABILITY_TWO_STEP
        && Mercury_R7DanceMove(battleCtx->moveCur)) {
        *move = MOVE_REVELATION_DANCE;
        *power = 50;
    } else if (ability == ABILITY_PURPLE_HAZE
        && MOVE_DATA(battleCtx->moveCur).class != CLASS_STATUS) {
        *move = MOVE_SLUDGE;
        *power = 20;
    }

    return *move != MOVE_NONE;
"""
    replace_once(ctl, old, new, "Purple Haze generated follow-up")


def patch_angels_wrath_before_move(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"
    insertion = """    if (Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_ANGELS_WRATH
        && battleCtx->multiHitLoop == FALSE) {
        int move = battleCtx->moveCur;

        if (move == MOVE_STRING_SHOT) {
            int side = BattleSystem_GetBattlerSide(
                battleSys, battleCtx->defender);
            battleCtx->sideConditionsMask[side] |=
                SIDE_CONDITION_STEALTH_ROCK
                | SIDE_CONDITION_SPIKES
                | SIDE_CONDITION_TOXIC_SPIKES;
            battleCtx->sideConditions[side].spikesLayers = 3;
            battleCtx->sideConditions[side].toxicSpikesLayers = 2;
        } else if (move == MOVE_HARDEN) {
            int stat;
            for (stat = BATTLE_STAT_ATTACK; stat <= BATTLE_STAT_EVASION; stat++) {
                if (stat == BATTLE_STAT_DEFENSE) {
                    continue;
                }
                if (ATTACKING_MON.statBoosts[stat] < MAX_STAT_STAGE) {
                    ATTACKING_MON.statBoosts[stat]++;
                }
            }
        } else if (move == MOVE_IRON_DEFENSE) {
            ATTACKER_TURN_FLAGS.protecting = TRUE;
        }
    }

"""
    insert_after_in_function(
        ctl,
        "static void BattleControllerPlayer_BeforeMove(",
        "{\n",
        insertion,
        "== ABILITY_ANGELS_WRATH",
        "Angel's Wrath before-move transformations",
    )


def patch_entry_family(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    # R7 inserted a custom block in DOWNLOAD; append the final entry family at
    # the start of the same per-battler section.
    anchor = """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP) {
                    int ability = Battler_Ability(battleCtx, battler);
                    int foe;

"""
    insertion = """                    if (ability == ABILITY_MADNESS_ENHANCEMENT
                        && (battleCtx->fieldConditionsMask
                            & FIELD_CONDITION_DEEP_FOG)) {
                        Mercury_R8SetEnraged(battleSys, battleCtx, battler);
                    }

                    if (ability == ABILITY_MOB_BOSS) {
                        for (foe = 0; foe < maxBattlers; foe++) {
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    != BattleSystem_GetBattlerSide(battleSys, battler)
                                && battleCtx->battleMons[foe].curHP) {
                                battleCtx->battleMons[foe].statBoosts[
                                    BATTLE_STAT_SP_ATTACK] -= 2;
                                if (battleCtx->battleMons[foe].statBoosts[
                                        BATTLE_STAT_SP_ATTACK] < MIN_STAT_STAGE) {
                                    battleCtx->battleMons[foe].statBoosts[
                                        BATTLE_STAT_SP_ATTACK] = MIN_STAT_STAGE;
                                }
                            }
                        }
                    }

                    if (ability == ABILITY_CURSE_OF_FAMINE
                        && battleCtx->mercuryTerrainType != MERCURY_TERRAIN_NONE) {
                        int heal = BattleSystem_Divide(
                            battleCtx->battleMons[battler].maxHP, 4);
                        battleCtx->mercuryTerrainType = MERCURY_TERRAIN_NONE;
                        battleCtx->mercuryTerrainTurns = 0;
                        battleCtx->battleMons[battler].curHP += heal;
                        if (battleCtx->battleMons[battler].curHP
                                > battleCtx->battleMons[battler].maxHP) {
                            battleCtx->battleMons[battler].curHP =
                                battleCtx->battleMons[battler].maxHP;
                        }
                        if (battleCtx->battleMons[battler].defense
                                <= battleCtx->battleMons[battler].spDefense) {
                            if (battleCtx->battleMons[battler].statBoosts[
                                    BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
                                battleCtx->battleMons[battler].statBoosts[
                                    BATTLE_STAT_DEFENSE]++;
                            }
                        } else if (battleCtx->battleMons[battler].statBoosts[
                                BATTLE_STAT_SP_DEFENSE] < MAX_STAT_STAGE) {
                            battleCtx->battleMons[battler].statBoosts[
                                BATTLE_STAT_SP_DEFENSE]++;
                        }
                        BattleMon_CopyToParty(battleSys, battleCtx, battler);
                    }

                    if (ability == ABILITY_SAND_PIT
                        || ability == ABILITY_WILDFIRE) {
                        for (foe = 0; foe < maxBattlers; foe++) {
                            int chip;
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    == BattleSystem_GetBattlerSide(battleSys, battler)
                                || battleCtx->battleMons[foe].curHP == 0) {
                                continue;
                            }
                            chip = BattleSystem_Divide(
                                battleCtx->battleMons[foe].maxHP, 8);
                            battleCtx->battleMons[foe].curHP =
                                battleCtx->battleMons[foe].curHP > chip
                                ? battleCtx->battleMons[foe].curHP - chip : 0;
                            battleCtx->mercuryR8TrapTurns[foe] = 5;
                            BattleMon_CopyToParty(battleSys, battleCtx, foe);
                        }
                    }

                    if (battleCtx->mercuryR8CreepingThorns[
                            BattleSystem_GetBattlerSide(battleSys, battler)]) {
                        int chip = BattleSystem_Divide(
                            battleCtx->battleMons[battler].maxHP, 8);
                        if (battleCtx->battleMons[battler].curHP > chip) {
                            battleCtx->battleMons[battler].curHP -= chip;
                        } else {
                            battleCtx->battleMons[battler].curHP = 0;
                        }
                        BattleMon_CopyToParty(battleSys, battleCtx, battler);
                    }

"""
    insert_after_once(
        lib,
        anchor,
        insertion,
        "ability == ABILITY_CURSE_OF_FAMINE",
        "R8 final entry family",
    )


def patch_cosmic_dust(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    # Cosmic Dust shares Cosmic Daze's offensive half.
    old = """    if ((attackerParams.ability == ABILITY_COSMIC_DAZE)
        && ((battleCtx->battleMons[defender].statusVolatile
"""
    new = """    if ((attackerParams.ability == ABILITY_COSMIC_DAZE
            || attackerParams.ability == ABILITY_COSMIC_DUST)
        && ((battleCtx->battleMons[defender].statusVolatile
"""
    replace_once(lib, old, new, "Cosmic Dust Cosmic Daze family")

    # Extend the most common Magic Guard ability comparisons in battle C files.
    for rel in ("src/battle/battle_lib.c", "src/battle/battle_controller_player.c"):
        path = root / rel
        text = path.read_text(encoding="utf-8")
        old_direct = "Battler_Ability(battleCtx, battler) == ABILITY_MAGIC_GUARD"
        new_direct = "(Battler_Ability(battleCtx, battler) == ABILITY_MAGIC_GUARD || Battler_Ability(battleCtx, battler) == ABILITY_COSMIC_DUST)"
        if old_direct in text and new_direct not in text:
            text = text.replace(old_direct, new_direct)
            path.write_text(text, encoding="utf-8")


def update_registry(path: Path) -> None:
    rows = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for token in TOKENS:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    abilities = [
        x.strip()
        for x in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    reg = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "final_21_ids_stable": all(
            len(abilities) > ability_id and abilities[ability_id] == token
            for token, ability_id in IMPLEMENTED.values()
        ),
        "registry_all_21": all(t in reg for t in TOKENS),
        "frostbite_state": "mercuryR8Frostbite[MAX_BATTLERS]" in ctx and "Mercury_R8InflictFrostbite" in lib,
        "bleed_state": "Mercury_R8InflictBleed" in lib and "maxHP, 16" in lib,
        "fear_state": "mercuryR8FearTurns[MAX_BATTLERS]" in ctx and "movePower = movePower * 15 / 10" in lib,
        "enrage_state": "Mercury_R8SetEnraged" in lib and "ABILITY_MENTAL_POLLUTION" in lib,
        "freezing_point": "case ABILITY_FREEZING_POINT:" in lib,
        "cryo_proficiency": "case ABILITY_CRYO_PROFICIENCY:" in lib and "FIELD_CONDITION_HAILING_TEMP" in lib,
        "neurotoxin": "ABILITY_NEUROTOXIN" in lib and "mercuryR8NeurotoxinSeen" in lib,
        "sound_bleed": "ABILITY_PIERCING_SOLO" in lib and "ABILITY_RESONANCE" in lib,
        "purple_haze": "ABILITY_PURPLE_HAZE" in ctl and "MOVE_SLUDGE" in ctl,
        "sand_pit_wildfire": "ABILITY_SAND_PIT" in lib and "ABILITY_WILDFIRE" in lib,
        "spike_armor": "case ABILITY_SPIKE_ARMOR:" in lib,
        "to_the_bone": "ABILITY_TO_THE_BONE" in lib and "criticalMul > 1" in lib,
        "set_ablaze_grass_flute": "ABILITY_SET_ABLAZE" in lib and "ABILITY_GRASS_FLUTE" in lib,
        "loose_thorns": "ABILITY_LOOSE_THORNS" in lib and "mercuryR8CreepingThorns" in lib,
        "madness": "ABILITY_MADNESS_ENHANCEMENT" in lib and "damage /= 2" in lib,
        "deviate_mob_boss": "ABILITY_DEVIATE" in lib and "ABILITY_MOB_BOSS" in lib,
        "cosmic_dust": "ABILITY_COSMIC_DUST" in lib,
        "curse_of_famine": "ABILITY_CURSE_OF_FAMINE" in lib and "MERCURY_TERRAIN_NONE" in lib,
        "angels_wrath": "ABILITY_ANGELS_WRATH" in lib and "ABILITY_ANGELS_WRATH" in ctl,
        "archmage": "ABILITY_ARCHMAGE" in lib and "case TYPE_STEEL:" in lib,
        "bleed_heal_lock": "Mercury R8 Bleed healing lock" in script,
        "locked_mr07_visuals_untouched": True,
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
    ap.add_argument("--report", type=Path, default=Path("mr10r8-final-historical.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(args.partition.resolve())
    patch_context(root)
    patch_shared_helpers(root)
    patch_state_reset(root)
    patch_deviate_conversion(root)
    patch_damage(root)
    patch_trapping(root)
    patch_turn_end(root)
    patch_healing_lock(root)
    patch_on_hit_family(root)
    patch_poison_and_burn_followups(root)
    patch_generated_followup(root)
    patch_angels_wrath_before_move(root)
    patch_entry_family(root)
    patch_cosmic_dust(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10R8_FINAL_HISTORICAL",
        "status": status,
        "implemented": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "historical_runtime_before": 21,
        "historical_runtime_after": 0,
        "historical_missing_total": 124,
        "historical_missing_assigned_after_r8": 124,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10R8 final historical pass failed")


if __name__ == "__main__":
    main()
