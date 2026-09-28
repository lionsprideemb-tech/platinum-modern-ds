#!/usr/bin/env python3
"""MR08J — canonical Ability fast pass, conversion/item/reaction family.

Adds fifteen official/current-mainline Ability mechanics using shared Platinum
battle hooks:

- Pixilate
- Aerilate
- Galvanize
- Liquid Voice
- Unnerve
- Poison Touch
- Harvest
- Cheek Pouch
- Stakeout
- Corrosion
- Hospitality
- Toxic Debris
- Toxic Chain
- Innards Out
- Mirror Armor

Mechanics-only pass; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_PIXILATE",
    "ABILITY_AERILATE",
    "ABILITY_GALVANIZE",
    "ABILITY_LIQUID_VOICE",
    "ABILITY_UNNERVE",
    "ABILITY_POISON_TOUCH",
    "ABILITY_HARVEST",
    "ABILITY_CHEEK_POUCH",
    "ABILITY_STAKEOUT",
    "ABILITY_CORROSION",
    "ABILITY_HOSPITALITY",
    "ABILITY_TOXIC_DEBRIS",
    "ABILITY_TOXIC_CHAIN",
    "ABILITY_INNARDS_OUT",
    "ABILITY_MIRROR_ARMOR",
)

EXPECTED_IDS = {
    "ABILITY_UNNERVE": 127,
    "ABILITY_HARVEST": 139,
    "ABILITY_POISON_TOUCH": 143,
    "ABILITY_CHEEK_POUCH": 167,
    "ABILITY_PIXILATE": 182,
    "ABILITY_AERILATE": 184,
    "ABILITY_STAKEOUT": 198,
    "ABILITY_LIQUID_VOICE": 204,
    "ABILITY_GALVANIZE": 206,
    "ABILITY_CORROSION": 212,
    "ABILITY_INNARDS_OUT": 215,
    "ABILITY_MIRROR_ARMOR": 240,
    "ABILITY_TOXIC_DEBRIS": 295,
    "ABILITY_HOSPITALITY": 299,
    "ABILITY_TOXIC_CHAIN": 305,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all_exact(path: Path, old: str, new: str, expected: int, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise SystemExit(
            f"{label}: expected exactly {expected} matches in {path}, found {count}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_type_conversion_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    if (attackerParams.ability == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (attackerParams.ability == ABILITY_REFRIGERATE
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        moveType = TYPE_ICE;
    } else if (inType == TYPE_NORMAL) {
        moveType = MOVE_DATA(move).type;
    } else {
        moveType = inType & 0x3F;
    }
""",
        """    if (attackerParams.ability == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (attackerParams.ability == ABILITY_LIQUID_VOICE
        && Mercury_MoveIsSound(move)) {
        moveType = TYPE_WATER;
    } else if (inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        if (attackerParams.ability == ABILITY_REFRIGERATE) {
            moveType = TYPE_ICE;
        } else if (attackerParams.ability == ABILITY_PIXILATE) {
            moveType = TYPE_FAIRY;
        } else if (attackerParams.ability == ABILITY_AERILATE) {
            moveType = TYPE_FLYING;
        } else if (attackerParams.ability == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else {
            moveType = MOVE_DATA(move).type;
        }
    } else if (inType == TYPE_NORMAL) {
        moveType = MOVE_DATA(move).type;
    } else {
        moveType = inType & 0x3F;
    }
""",
        "Pixilate/Aerilate/Galvanize/Liquid Voice damage type",
    )

    replace_once(
        path,
        """    if (attackerParams.ability == ABILITY_REFRIGERATE
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        movePower = movePower * 12 / 10;
    }

    if (attackerParams.ability == ABILITY_MEGA_LAUNCHER
""",
        """    if ((attackerParams.ability == ABILITY_REFRIGERATE
            || attackerParams.ability == ABILITY_PIXILATE
            || attackerParams.ability == ABILITY_AERILATE
            || attackerParams.ability == ABILITY_GALVANIZE)
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        movePower = movePower * 12 / 10;
    }

    if (attackerParams.ability == ABILITY_MEGA_LAUNCHER
""",
        "-ate power family",
    )

    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (Battler_Ability(battleCtx, attacker) == ABILITY_REFRIGERATE
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        moveType = TYPE_ICE;
    } else if (inType) {
        moveType = inType;
    } else {
        moveType = MOVE_DATA(move).type;
    }

    movePower = MOVE_DATA(move).power;
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (Battler_Ability(battleCtx, attacker) == ABILITY_LIQUID_VOICE
        && Mercury_MoveIsSound(move)) {
        moveType = TYPE_WATER;
    } else if (inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        int ability = Battler_Ability(battleCtx, attacker);

        if (ability == ABILITY_REFRIGERATE) {
            moveType = TYPE_ICE;
        } else if (ability == ABILITY_PIXILATE) {
            moveType = TYPE_FAIRY;
        } else if (ability == ABILITY_AERILATE) {
            moveType = TYPE_FLYING;
        } else if (ability == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else {
            moveType = inType;
        }
    } else if (inType) {
        moveType = inType;
    } else {
        moveType = MOVE_DATA(move).type;
    }

    movePower = MOVE_DATA(move).power;
""",
        "-ate/Liquid Voice type-chart type",
    )

    replace_once(
        path,
        """    if (attackerAbility == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (attackerAbility == ABILITY_REFRIGERATE
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        moveType = TYPE_ICE;
    } else if (inType) {
        moveType = inType;
    } else {
        moveType = MOVE_DATA(move).type;
    }

    if (!Mercury_IsMoldBreakerAbility(attackerAbility)
""",
        """    if (attackerAbility == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (attackerAbility == ABILITY_LIQUID_VOICE
        && Mercury_MoveIsSound(move)) {
        moveType = TYPE_WATER;
    } else if (inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        if (attackerAbility == ABILITY_REFRIGERATE) {
            moveType = TYPE_ICE;
        } else if (attackerAbility == ABILITY_PIXILATE) {
            moveType = TYPE_FAIRY;
        } else if (attackerAbility == ABILITY_AERILATE) {
            moveType = TYPE_FLYING;
        } else if (attackerAbility == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else {
            moveType = inType;
        }
    } else if (inType) {
        moveType = inType;
    } else {
        moveType = MOVE_DATA(move).type;
    }

    if (!Mercury_IsMoldBreakerAbility(attackerAbility)
""",
        "-ate/Liquid Voice generic effectiveness type",
    )

    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (Battler_Ability(battleCtx, attacker) == ABILITY_REFRIGERATE
        && battleCtx->moveType == TYPE_NORMAL
        && CURRENT_MOVE_DATA.type == TYPE_NORMAL
        && battleCtx->moveCur != MOVE_STRUGGLE) {
        moveType = TYPE_ICE;
    } else if (battleCtx->moveType) {
        moveType = battleCtx->moveType;
    } else {
        moveType = CURRENT_MOVE_DATA.type;
    }

    if (attacker != defender
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (Battler_Ability(battleCtx, attacker) == ABILITY_LIQUID_VOICE
        && Mercury_MoveIsSound(battleCtx->moveCur)) {
        moveType = TYPE_WATER;
    } else if (battleCtx->moveType == TYPE_NORMAL
        && CURRENT_MOVE_DATA.type == TYPE_NORMAL
        && battleCtx->moveCur != MOVE_STRUGGLE) {
        int ability = Battler_Ability(battleCtx, attacker);

        if (ability == ABILITY_REFRIGERATE) {
            moveType = TYPE_ICE;
        } else if (ability == ABILITY_PIXILATE) {
            moveType = TYPE_FAIRY;
        } else if (ability == ABILITY_AERILATE) {
            moveType = TYPE_FLYING;
        } else if (ability == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else {
            moveType = TYPE_NORMAL;
        }
    } else if (battleCtx->moveType) {
        moveType = battleCtx->moveType;
    } else {
        moveType = CURRENT_MOVE_DATA.type;
    }

    if (attacker != defender
""",
        "-ate/Liquid Voice immunity-path type",
    )

    replace_once(
        path,
        """    case ABILITY_COLOR_CHANGE:
        u8 moveType;

        if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NORMALIZE) {
            moveType = TYPE_NORMAL;
        } else if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_REFRIGERATE
            && battleCtx->moveType == TYPE_NORMAL
            && CURRENT_MOVE_DATA.type == TYPE_NORMAL
            && battleCtx->moveCur != MOVE_STRUGGLE) {
            moveType = TYPE_ICE;
        } else if (battleCtx->moveType) {
            moveType = battleCtx->moveType;
        } else {
            moveType = CURRENT_MOVE_DATA.type;
        }
""",
        """    case ABILITY_COLOR_CHANGE:
        u8 moveType;

        if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NORMALIZE) {
            moveType = TYPE_NORMAL;
        } else if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_LIQUID_VOICE
            && Mercury_MoveIsSound(battleCtx->moveCur)) {
            moveType = TYPE_WATER;
        } else if (battleCtx->moveType == TYPE_NORMAL
            && CURRENT_MOVE_DATA.type == TYPE_NORMAL
            && battleCtx->moveCur != MOVE_STRUGGLE) {
            int ability = Battler_Ability(battleCtx, battleCtx->attacker);

            if (ability == ABILITY_REFRIGERATE) {
                moveType = TYPE_ICE;
            } else if (ability == ABILITY_PIXILATE) {
                moveType = TYPE_FAIRY;
            } else if (ability == ABILITY_AERILATE) {
                moveType = TYPE_FLYING;
            } else if (ability == ABILITY_GALVANIZE) {
                moveType = TYPE_ELECTRIC;
            } else {
                moveType = TYPE_NORMAL;
            }
        } else if (battleCtx->moveType) {
            moveType = battleCtx->moveType;
        } else {
            moveType = CURRENT_MOVE_DATA.type;
        }
""",
        "-ate/Liquid Voice Color Change type",
    )


def patch_item_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """BOOL BattleSystem_TriggerHeldItem(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
{
    BOOL result = FALSE;
    int subscript;
    int itemEffect = Battler_HeldItemEffect(battleCtx, battler);
    int itemPower = Battler_HeldItemPower(battleCtx, battler, ITEM_POWER_CHECK_ALL);

    if (battleCtx->battleMons[battler].curHP) {
""",
        """BOOL BattleSystem_TriggerHeldItem(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
{
    BOOL result = FALSE;
    int subscript;
    int itemEffect = Battler_HeldItemEffect(battleCtx, battler);
    int itemPower = Battler_HeldItemPower(battleCtx, battler, ITEM_POWER_CHECK_ALL);

    if (Item_IsBerry(Battler_HeldItem(battleCtx, battler))
        && BattleSystem_CountAbility(
            battleSys,
            battleCtx,
            COUNT_ALIVE_BATTLERS_THEIR_SIDE,
            battler,
            ABILITY_UNNERVE)) {
        return FALSE;
    }

    if (battleCtx->battleMons[battler].curHP) {
""",
        "Unnerve berry suppression",
    )

    replace_all_exact(
        path,
        """        if (result == TRUE) {
            battleCtx->msgBattlerTemp = battler;
            battleCtx->msgItemTemp = Battler_HeldItem(battleCtx, battler);

            LOAD_SUBSEQ(subscript);
""",
        """        if (result == TRUE) {
            if (Battler_Ability(battleCtx, battler) == ABILITY_CHEEK_POUCH
                && Item_IsBerry(Battler_HeldItem(battleCtx, battler))
                && battleCtx->battleMons[battler].curHP
                    < battleCtx->battleMons[battler].maxHP) {
                battleCtx->battleMons[battler].curHP +=
                    BattleSystem_Divide(battleCtx->battleMons[battler].maxHP, 3);
                if (battleCtx->battleMons[battler].curHP
                    > battleCtx->battleMons[battler].maxHP) {
                    battleCtx->battleMons[battler].curHP =
                        battleCtx->battleMons[battler].maxHP;
                }
                BattleMon_CopyToParty(battleSys, battleCtx, battler);
            }

            battleCtx->msgBattlerTemp = battler;
            battleCtx->msgItemTemp = Battler_HeldItem(battleCtx, battler);

            LOAD_SUBSEQ(subscript);
""",
        3,
        "Cheek Pouch berry heal",
    )

    replace_once(
        path,
        """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_HEALER: {
""",
        """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_HARVEST:
        if (battleCtx->battleMons[battler].curHP
            && battleCtx->battleMons[battler].heldItem == ITEM_NONE
            && Item_IsBerry(battleCtx->recycleItem[battler])
            && (WEATHER_IS_SUN || BattleSystem_RandNext(battleSys) % 2 == 0)) {
            battleCtx->battleMons[battler].heldItem = battleCtx->recycleItem[battler];
            battleCtx->recycleItem[battler] = ITEM_NONE;
            BattleMon_CopyToParty(battleSys, battleCtx, battler);
            battleCtx->msgBattlerTemp = battler;
            subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_HEALER: {
""",
        "Harvest end-turn recovery",
    )


def patch_stakeout(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_STRONG_JAW
""",
        """    if (attackerParams.ability == ABILITY_STAKEOUT
        && battleCtx->battlerActions[defender][BATTLE_ACTION_PICK_COMMAND]
            == BATTLE_CONTROL_PARTY) {
        movePower *= 2;
    }

""",
        "Stakeout switched-target power",
    )


def patch_attacker_reactions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    header = root / "include/battle/battle_lib.h"
    controller = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        lib,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
""",
        """BOOL Mercury_TriggerAttackerOnHitAbility(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int *subscript)
{
    if (battleCtx->defender == BATTLER_NONE
        || Battler_SubstituteWasHit(battleCtx, battleCtx->defender) == TRUE
        || (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS)) {
        return FALSE;
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH
        && DEFENDING_MON.curHP
        && DEFENDING_MON.status == MON_CONDITION_NONE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && Mercury_MoveMakesContact(
            battleCtx, battleCtx->attacker, battleCtx->moveCur)
        && BattleSystem_RandNext(battleSys) % 10 < 3) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_poison;
        return TRUE;
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
        && DEFENDING_MON.curHP
        && DEFENDING_MON.status == MON_CONDITION_NONE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && BattleSystem_RandNext(battleSys) % 10 < 3) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_badly_poison;
        return TRUE;
    }

    return FALSE;
}

""",
        "attacker on-hit Ability dispatcher",
    )

    insert_before_once(
        header,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        """BOOL Mercury_TriggerAttackerOnHitAbility(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        "attacker on-hit Ability declaration",
    )

    replace_once(
        controller,
        """    ONE_HIT_TRIGGER_ABILITY,
    ONE_HIT_EXTRA_FLINCH,
""",
        """    ONE_HIT_TRIGGER_ABILITY,
    ONE_HIT_TRIGGER_ATTACKER_ABILITY,
    ONE_HIT_EXTRA_FLINCH,
""",
        "one-hit attacker Ability state enum",
    )
    replace_once(
        controller,
        """    MULTI_HIT_TRIGGER_ABILITY,
    MULTI_HIT_STATUS,
""",
        """    MULTI_HIT_TRIGGER_ABILITY,
    MULTI_HIT_TRIGGER_ATTACKER_ABILITY,
    MULTI_HIT_STATUS,
""",
        "multi-hit attacker Ability state enum",
    )

    replace_once(
        controller,
        """        case ONE_HIT_EXTRA_FLINCH:
            battleCtx->afterMoveMessageState++;
""",
        """        case ONE_HIT_TRIGGER_ATTACKER_ABILITY:
            int attackerAbilitySeq;

            battleCtx->afterMoveMessageState++;
            if (Mercury_TriggerAttackerOnHitAbility(
                    battleSys, battleCtx, &attackerAbilitySeq) == TRUE) {
                LOAD_SUBSEQ(attackerAbilitySeq);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                return;
            }

        case ONE_HIT_EXTRA_FLINCH:
            battleCtx->afterMoveMessageState++;
""",
        "one-hit attacker Ability controller hook",
    )

    replace_once(
        controller,
        """        case MULTI_HIT_STATUS:
            battleCtx->afterMoveMessageState++;
""",
        """        case MULTI_HIT_TRIGGER_ATTACKER_ABILITY:
            int attackerAbilitySeq;

            battleCtx->afterMoveMessageState++;
            if (Mercury_TriggerAttackerOnHitAbility(
                    battleSys, battleCtx, &attackerAbilitySeq) == TRUE) {
                LOAD_SUBSEQ(attackerAbilitySeq);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                return;
            }

        case MULTI_HIT_STATUS:
            battleCtx->afterMoveMessageState++;
""",
        "multi-hit attacker Ability controller hook",
    )


def patch_defender_reactions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    case ABILITY_THERMAL_EXCHANGE: {
""",
        """    case ABILITY_TOXIC_DEBRIS:
        if (DEFENDING_MON.curHP
            && DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken) {
            int side = BattleSystem_GetBattlerSide(
                battleSys, battleCtx->attacker);

            if (battleCtx->sideConditions[side].toxicSpikesLayers < 2) {
                battleCtx->sideConditions[side].toxicSpikesLayers++;
                battleCtx->sideConditionsMask[side] |= SIDE_CONDITION_TOXIC_SPIKES;
                battleCtx->msgBattlerTemp = battleCtx->defender;
                *subscript = subscript_mold_breaker;
                result = TRUE;
            }
        }
        break;

    case ABILITY_INNARDS_OUT:
        if (battleCtx->defender == battleCtx->faintedMon
            && ATTACKING_MON.curHP
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_MAGIC_GUARD
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int damageTaken = DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                ? DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                : DEFENDER_SELF_TURN_FLAGS.specialDamageTaken;

            battleCtx->hpCalcTemp = damageTaken;
            battleCtx->msgBattlerTemp = battleCtx->attacker;
            *subscript = subscript_rough_skin;
            result = TRUE;
        }
        break;

""",
        "Toxic Debris / Innards Out on-hit family",
    )


def patch_corrosion(root: Path) -> None:
    poison = root / "res/battle/scripts/subscripts/subscript_poison.s"
    toxic = root / "res/battle/scripts/subscripts/subscript_badly_poison.s"

    replace_once(
        poison,
        """    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_TOXIC, _243
    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_1, TYPE_POISON, _266
""",
        """    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_TOXIC, _243
    CompareVarToValue OPCODE_EQU, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_TOXIC_SPIKES, _MercuryPoisonTypeChecks
    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_CORROSION, _MercuryPoisonTypeBypass
_MercuryPoisonTypeChecks:
    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_1, TYPE_POISON, _266
""",
        "Corrosion regular poison entry",
    )
    replace_once(
        poison,
        """    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_2, TYPE_STEEL, _266
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_NONE, _217
""",
        """    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_2, TYPE_STEEL, _266
_MercuryPoisonTypeBypass:
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_NONE, _217
""",
        "Corrosion regular poison bypass label",
    )

    replace_once(
        toxic,
        """    CheckSubstitute BTLSCR_SIDE_EFFECT_MON, _275
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_POISON, _296
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_TOXIC, _296
    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_1, TYPE_POISON, _314
""",
        """    CheckSubstitute BTLSCR_SIDE_EFFECT_MON, _275
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_POISON, _296
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_TOXIC, _296
    CompareVarToValue OPCODE_EQU, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_TOXIC_SPIKES, _MercuryToxicTypeChecks
    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_CORROSION, _MercuryToxicTypeBypass
_MercuryToxicTypeChecks:
    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_1, TYPE_POISON, _314
""",
        "Corrosion badly poison entry",
    )
    replace_once(
        toxic,
        """    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_2, TYPE_STEEL, _314
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_NONE, _275
""",
        """    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_2, TYPE_STEEL, _314
_MercuryToxicTypeBypass:
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_STATUS, MON_CONDITION_NONE, _275
""",
        "Corrosion badly poison bypass label",
    )


def patch_hospitality(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """                    case ABILITY_SCREEN_CLEANER:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->sideConditionsMask[0] &=
                            ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);
                        battleCtx->sideConditionsMask[1] &=
                            ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);
                        battleCtx->sideConditions[0].reflectTurns = 0;
                        battleCtx->sideConditions[0].lightScreenTurns = 0;
                        battleCtx->sideConditions[1].reflectTurns = 0;
                        battleCtx->sideConditions[1].lightScreenTurns = 0;
                        break;
""",
        """                    case ABILITY_SCREEN_CLEANER:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->sideConditionsMask[0] &=
                            ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);
                        battleCtx->sideConditionsMask[1] &=
                            ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);
                        battleCtx->sideConditions[0].reflectTurns = 0;
                        battleCtx->sideConditions[0].lightScreenTurns = 0;
                        battleCtx->sideConditions[1].reflectTurns = 0;
                        battleCtx->sideConditions[1].lightScreenTurns = 0;
                        break;

                    case ABILITY_HOSPITALITY: {
                        int ally = battler ^ 2;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (ally < maxBattlers
                            && battleCtx->battleMons[ally].curHP
                            && battleCtx->battleMons[ally].curHP
                                < battleCtx->battleMons[ally].maxHP) {
                            battleCtx->battleMons[ally].curHP +=
                                BattleSystem_Divide(
                                    battleCtx->battleMons[ally].maxHP, 4);
                            if (battleCtx->battleMons[ally].curHP
                                > battleCtx->battleMons[ally].maxHP) {
                                battleCtx->battleMons[ally].curHP =
                                    battleCtx->battleMons[ally].maxHP;
                            }
                            BattleMon_CopyToParty(battleSys, battleCtx, ally);
                            battleCtx->msgBattlerTemp = battler;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
                    }
""",
        "Hospitality switch-in heal",
    )


def patch_mirror_armor(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    replace_once(
        path,
        """    } else {
        if ((battleCtx->sideEffectFlags & MOVE_SIDE_EFFECT_CANNOT_PREVENT) == FALSE) {
            if (battleCtx->attacker != battleCtx->sideEffectMon) {
                if (battleCtx->sideConditions[BattleSystem_GetBattlerSide(battleSys, battleCtx->sideEffectMon)].mistTurns) {
""",
        """    } else {
        if ((battleCtx->sideEffectFlags & MOVE_SIDE_EFFECT_CANNOT_PREVENT) == FALSE
            && battleCtx->attacker != battleCtx->sideEffectMon
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->sideEffectMon,
                ABILITY_MIRROR_ARMOR) == TRUE) {
            BattleMon *reflectedMon = &battleCtx->battleMons[battleCtx->attacker];
            int reflectedStat = BATTLE_STAT_ATTACK + statOffset;

            if (reflectedMon->statBoosts[reflectedStat] > MIN_STAT_STAGE) {
                reflectedMon->statBoosts[reflectedStat] += stageChange;
                if (reflectedMon->statBoosts[reflectedStat] < MIN_STAT_STAGE) {
                    reflectedMon->statBoosts[reflectedStat] = MIN_STAT_STAGE;
                }
            }
            battleCtx->msgBuffer.id = BattleStrings_Text_PokemonsAbilityPreventsStatLoss_Ally;
            battleCtx->msgBuffer.tags = TAG_NICKNAME_ABILITY;
            battleCtx->msgBuffer.params[0] = BattleSystem_NicknameTag(
                battleCtx, battleCtx->sideEffectMon);
            battleCtx->msgBuffer.params[1] = ABILITY_MIRROR_ARMOR;
            result = 1;
        } else if ((battleCtx->sideEffectFlags & MOVE_SIDE_EFFECT_CANNOT_PREVENT) == FALSE) {
            if (battleCtx->attacker != battleCtx->sideEffectMon) {
                if (battleCtx->sideConditions[BattleSystem_GetBattlerSide(battleSys, battleCtx->sideEffectMon)].mistTurns) {
""",
        "Mirror Armor stat-drop reflection",
    )


def update_registry(path: Path) -> None:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    poison = (root / "res/battle/scripts/subscripts/subscript_poison.s").read_text(encoding="utf-8")
    toxic = (root / "res/battle/scripts/subscripts/subscript_badly_poison.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "pixilate_hook": "ABILITY_PIXILATE" in lib and "TYPE_FAIRY" in lib,
        "aerilate_hook": "ABILITY_AERILATE" in lib and "TYPE_FLYING" in lib,
        "galvanize_hook": "ABILITY_GALVANIZE" in lib and "TYPE_ELECTRIC" in lib,
        "liquid_voice_hook": "ABILITY_LIQUID_VOICE" in lib and "Mercury_MoveIsSound" in lib,
        "unnerve_hook": "ABILITY_UNNERVE" in lib and "COUNT_ALIVE_BATTLERS_THEIR_SIDE" in lib,
        "poison_touch_hook": "ABILITY_POISON_TOUCH" in lib and "Mercury_TriggerAttackerOnHitAbility" in lib,
        "harvest_hook": "case ABILITY_HARVEST:" in lib and "recycleItem[battler]" in lib,
        "cheek_pouch_hook": "ABILITY_CHEEK_POUCH" in lib and "maxHP, 3" in lib,
        "stakeout_hook": "ABILITY_STAKEOUT" in lib and "BATTLE_CONTROL_PARTY" in lib,
        "corrosion_hook": "ABILITY_CORROSION" in poison and "ABILITY_CORROSION" in toxic,
        "hospitality_hook": "case ABILITY_HOSPITALITY:" in lib and "maxHP, 4" in lib,
        "toxic_debris_hook": "case ABILITY_TOXIC_DEBRIS:" in lib and "toxicSpikesLayers++" in lib,
        "toxic_chain_hook": "ABILITY_TOXIC_CHAIN" in lib and "subscript_badly_poison" in lib,
        "innards_out_hook": "case ABILITY_INNARDS_OUT:" in lib and "subscript_rough_skin" in lib,
        "mirror_armor_hook": "ABILITY_MIRROR_ARMOR" in script and "reflectedMon" in script,
        "attacker_reaction_controller": "ONE_HIT_TRIGGER_ATTACKER_ABILITY" in controller and "MULTI_HIT_TRIGGER_ATTACKER_ABILITY" in controller,
        "implemented_registry_updated": all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr08j-canonical-ability-conversion-item-reaction.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_type_conversion_family(root)
    patch_item_family(root)
    patch_stakeout(root)
    patch_attacker_reactions(root)
    patch_defender_reactions(root)
    patch_corrosion(root)
    patch_hospitality(root)
    patch_mirror_armor(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08J_CANONICAL_ABILITY_CONVERSION_ITEM_REACTION",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 110,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08J validation failed")


if __name__ == "__main__":
    main()
