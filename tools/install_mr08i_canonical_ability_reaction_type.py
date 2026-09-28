#!/usr/bin/env python3
"""MR08I — canonical Ability fast pass, reaction/type family.

Adds fifteen official/current-mainline Ability mechanics on shared Platinum
battle hooks:

- Defiant
- Cursed Body
- Weak Armor
- Overcoat
- Mummy
- Rattled
- Competitive
- Refrigerate
- Mega Launcher
- Triage
- Cotton Down
- Unseen Fist
- Lingering Aroma
- Anger Shell
- Electromorphosis

This pass changes mechanics only. Locked MR07 Summary/editor visuals remain
untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_DEFIANT",
    "ABILITY_CURSED_BODY",
    "ABILITY_WEAK_ARMOR",
    "ABILITY_OVERCOAT",
    "ABILITY_MUMMY",
    "ABILITY_RATTLED",
    "ABILITY_COMPETITIVE",
    "ABILITY_REFRIGERATE",
    "ABILITY_MEGA_LAUNCHER",
    "ABILITY_TRIAGE",
    "ABILITY_COTTON_DOWN",
    "ABILITY_UNSEEN_FIST",
    "ABILITY_LINGERING_AROMA",
    "ABILITY_ANGER_SHELL",
    "ABILITY_ELECTROMORPHOSIS",
)

EXPECTED_IDS = {
    "ABILITY_DEFIANT": 128,
    "ABILITY_CURSED_BODY": 130,
    "ABILITY_WEAK_ARMOR": 133,
    "ABILITY_OVERCOAT": 142,
    "ABILITY_MUMMY": 152,
    "ABILITY_RATTLED": 155,
    "ABILITY_COMPETITIVE": 172,
    "ABILITY_REFRIGERATE": 174,
    "ABILITY_MEGA_LAUNCHER": 178,
    "ABILITY_TRIAGE": 205,
    "ABILITY_COTTON_DOWN": 238,
    "ABILITY_UNSEEN_FIST": 260,
    "ABILITY_LINGERING_AROMA": 268,
    "ABILITY_ANGER_SHELL": 271,
    "ABILITY_ELECTROMORPHOSIS": 280,
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


def patch_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # CompareBattlerSpeed lives earlier in battle_lib.c than the shared helper
    # definitions, so Triage needs a narrow forward declaration.
    insert_before_once(
        path,
        """u8 BattleSystem_CompareBattlerSpeed(BattleSystem *battleSys, BattleContext *battleCtx, int battler1, int battler2, BOOL ignoreQuickClaw)
""",
        """static BOOL Mercury_MoveIsTriageHealing(int move);

""",
        "Triage helper forward declaration",
    )

    insert_before_once(
        path,
        """static BOOL Mercury_MoveIsBallOrBomb(int move)
""",
        """static BOOL Mercury_MoveIsPulse(int move)
{
    switch (move) {
    case MOVE_AURA_SPHERE:
    case MOVE_DARK_PULSE:
    case MOVE_DRAGON_PULSE:
    case MOVE_HEAL_PULSE:
    case MOVE_ORIGIN_PULSE:
    case MOVE_TERRAIN_PULSE:
    case MOVE_WATER_PULSE:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_MoveIsTriageHealing(int move)
{
    switch (move) {
    case MOVE_ABSORB:
    case MOVE_DRAIN_PUNCH:
    case MOVE_DRAINING_KISS:
    case MOVE_DREAM_EATER:
    case MOVE_FLORAL_HEALING:
    case MOVE_GIGA_DRAIN:
    case MOVE_HEAL_ORDER:
    case MOVE_HEAL_PULSE:
    case MOVE_HEALING_WISH:
    case MOVE_HORN_LEECH:
    case MOVE_LEECH_LIFE:
    case MOVE_LUNAR_DANCE:
    case MOVE_MEGA_DRAIN:
    case MOVE_MILK_DRINK:
    case MOVE_MOONLIGHT:
    case MOVE_MORNING_SUN:
    case MOVE_OBLIVION_WING:
    case MOVE_PARABOLIC_CHARGE:
    case MOVE_PURIFY:
    case MOVE_RECOVER:
    case MOVE_REST:
    case MOVE_ROOST:
    case MOVE_SHORE_UP:
    case MOVE_SLACK_OFF:
    case MOVE_SOFT_BOILED:
    case MOVE_STRENGTH_SAP:
    case MOVE_SWALLOW:
    case MOVE_SYNTHESIS:
    case MOVE_WISH:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_MoveIsPowder(int move)
{
    switch (move) {
    case MOVE_COTTON_SPORE:
    case MOVE_POISON_POWDER:
    case MOVE_SLEEP_POWDER:
    case MOVE_STUN_SPORE:
    case MOVE_SPORE:
    case MOVE_POWDER:
    case MOVE_RAGE_POWDER:
    case MOVE_MAGIC_POWDER:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_AbilityCanBeOverwrittenByMummy(int ability)
{
    switch (ability) {
    case ABILITY_NONE:
    case ABILITY_MULTITYPE:
    case ABILITY_STANCE_CHANGE:
    case ABILITY_SCHOOLING:
    case ABILITY_COMATOSE:
    case ABILITY_SHIELDS_DOWN:
    case ABILITY_DISGUISE:
    case ABILITY_RKS_SYSTEM:
    case ABILITY_GULP_MISSILE:
    case ABILITY_ICE_FACE:
    case ABILITY_ZERO_TO_HERO:
    case ABILITY_COMMANDER:
    case ABILITY_TERA_SHIFT:
        return FALSE;
    default:
        return TRUE;
    }
}

""",
        "MR08I move/Ability helpers",
    )


def patch_triage_priority(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    if (battler1Priority == battler2Priority) {
""",
        """    if (battler1Move
        && battler1Ability == ABILITY_TRIAGE
        && Mercury_MoveIsTriageHealing(battler1Move)) {
        battler1Priority += 3;
    }

    if (battler2Move
        && battler2Ability == ABILITY_TRIAGE
        && Mercury_MoveIsTriageHealing(battler2Move)) {
        battler2Priority += 3;
    }

""",
        "Triage action-order priority",
    )

    insert_before_once(
        path,
        """    return priority;
}

static BOOL Mercury_PriorityBlockerActive(
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_TRIAGE
        && Mercury_MoveIsTriageHealing(battleCtx->moveCur)) {
        priority += 3;
    }

""",
        "Triage priority-blocker mirror",
    )


def patch_refrigerate_and_mega_launcher(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Damage-path move typing. inType == TYPE_NORMAL is Platinum's
    # "no external type override" sentinel.
    replace_once(
        path,
        """    if (attackerParams.ability == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (inType == TYPE_NORMAL) {
        moveType = MOVE_DATA(move).type;
    } else {
        moveType = inType & 0x3F;
    }
""",
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
        "Refrigerate damage move type",
    )

    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_STRONG_JAW
""",
        """    if (attackerParams.ability == ABILITY_REFRIGERATE
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        movePower = movePower * 12 / 10;
    }

    if (attackerParams.ability == ABILITY_MEGA_LAUNCHER
        && Mercury_MoveIsPulse(move)) {
        movePower = movePower * 15 / 10;
    }

""",
        "Refrigerate / Mega Launcher power hooks",
    )

    # Type chart / STAB path.
    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (inType) {
        moveType = inType;
    } else {
        moveType = MOVE_DATA(move).type;
    }

    movePower = MOVE_DATA(move).power;
""",
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
        "Refrigerate type-chart/STAB type",
    )

    # AI/general effectiveness path.
    replace_once(
        path,
        """    if (attackerAbility == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (inType) {
        moveType = inType;
    } else {
        moveType = MOVE_DATA(move).type;
    }

    if (!Mercury_IsMoldBreakerAbility(attackerAbility)
""",
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
        "Refrigerate generic effectiveness type",
    )

    # Pre-damage immunity path.
    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (battleCtx->moveType) {
        moveType = battleCtx->moveType;
    } else {
        moveType = CURRENT_MOVE_DATA.type;
    }

    if (attacker != defender
""",
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
        "Refrigerate immunity-path type",
    )

    # Color Change observes the converted type.
    replace_once(
        path,
        """    case ABILITY_COLOR_CHANGE:
        u8 moveType;

        if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NORMALIZE) {
            moveType = TYPE_NORMAL;
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
        "Refrigerate Color Change observed type",
    )


def patch_overcoat(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    script = root / "src/battle/battle_script.c"

    insert_before_once(
        lib,
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_SAP_SIPPER) == TRUE
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_OVERCOAT) == TRUE
        && Mercury_MoveIsPowder(battleCtx->moveCur)) {
        return subscript_but_it_failed;
    }

""",
        "Overcoat powder immunity",
    )

    replace_once(
        script,
        """            && Battler_Ability(battleCtx, battler) != ABILITY_SAND_VEIL
            && Battler_Ability(battleCtx, battler) != ABILITY_SAND_FORCE
            && (battleCtx->battleMons[battler].moveEffectsMask & MOVE_EFFECT_NO_WEATHER_DAMAGE) == FALSE) {
""",
        """            && Battler_Ability(battleCtx, battler) != ABILITY_SAND_VEIL
            && Battler_Ability(battleCtx, battler) != ABILITY_SAND_FORCE
            && Battler_Ability(battleCtx, battler) != ABILITY_OVERCOAT
            && (battleCtx->battleMons[battler].moveEffectsMask & MOVE_EFFECT_NO_WEATHER_DAMAGE) == FALSE) {
""",
        "Overcoat sandstorm immunity",
    )

    replace_once(
        script,
        """            } else if (type1 != TYPE_ICE
                && type2 != TYPE_ICE
                && Battler_Ability(battleCtx, battler) != ABILITY_SNOW_CLOAK) {
""",
        """            } else if (type1 != TYPE_ICE
                && type2 != TYPE_ICE
                && Battler_Ability(battleCtx, battler) != ABILITY_SNOW_CLOAK
                && Battler_Ability(battleCtx, battler) != ABILITY_OVERCOAT) {
""",
        "Overcoat hail/snow immunity",
    )


def patch_reaction_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    case ABILITY_THERMAL_EXCHANGE: {
""",
        """    case ABILITY_WEAK_ARMOR:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_WEAK_ARMOR) == TRUE
            && DEFENDING_MON.curHP
            && DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            && (DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] > MIN_STAT_STAGE
                || DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] < MAX_STAT_STAGE)) {
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] > MIN_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]--;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] += 2;
                if (DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] > MAX_STAT_STAGE) {
                    DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] = MAX_STAT_STAGE;
                }
            }
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_CURSED_BODY:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_CURSED_BODY) == TRUE
            && ATTACKING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && ATTACKING_MON.moveEffectsData.disabledMove == MOVE_NONE
            && battleCtx->moveCur != MOVE_NONE
            && BattleSystem_RandNext(battleSys) % 10 < 3) {
            int moveSlot;

            for (moveSlot = 0; moveSlot < LEARNED_MOVES_MAX; moveSlot++) {
                if (ATTACKING_MON.moves[moveSlot] == battleCtx->moveCur
                    && ATTACKING_MON.ppCur[moveSlot]) {
                    ATTACKING_MON.moveEffectsData.disabledMove = battleCtx->moveCur;
                    ATTACKING_MON.moveEffectsData.disabledTurns = 4;
                    battleCtx->msgBattlerTemp = battleCtx->defender;
                    *subscript = subscript_mold_breaker;
                    result = TRUE;
                    break;
                }
            }
        }
        break;

    case ABILITY_MUMMY:
    case ABILITY_LINGERING_AROMA: {
        int defenderAbility = Battler_Ability(battleCtx, battleCtx->defender);
        int attackerAbility = Battler_Ability(battleCtx, battleCtx->attacker);

        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                defenderAbility) == TRUE
            && ATTACKING_MON.curHP
            && attackerAbility != defenderAbility
            && Mercury_AbilityCanBeOverwrittenByMummy(attackerAbility)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)) {
            ATTACKING_MON.ability = defenderAbility;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

    case ABILITY_RATTLED: {
        int moveType;

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

        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_RATTLED) == TRUE
            && DEFENDING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (moveType == TYPE_BUG
                || moveType == TYPE_DARK
                || moveType == TYPE_GHOST)
            && DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;
    }

    case ABILITY_COTTON_DOWN:
        if (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken) {
            int i;
            int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
            BOOL lowered = FALSE;

            for (i = 0; i < maxBattlers; i++) {
                if (i != battleCtx->defender
                    && battleCtx->battleMons[i].curHP
                    && battleCtx->battleMons[i].statBoosts[BATTLE_STAT_SPEED]
                        > MIN_STAT_STAGE) {
                    battleCtx->battleMons[i].statBoosts[BATTLE_STAT_SPEED]--;
                    lowered = TRUE;
                }
            }

            if (lowered) {
                battleCtx->msgBattlerTemp = battleCtx->defender;
                *subscript = subscript_mold_breaker;
                result = TRUE;
            }
        }
        break;

    case ABILITY_ANGER_SHELL: {
        int damageTaken = DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            ? DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            : DEFENDER_SELF_TURN_FLAGS.specialDamageTaken;
        int hpBeforeHit = DEFENDING_MON.curHP - damageTaken;

        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_ANGER_SHELL) == TRUE
            && DEFENDING_MON.curHP
            && damageTaken < 0
            && hpBeforeHit > DEFENDING_MON.maxHP / 2
            && DEFENDING_MON.curHP <= DEFENDING_MON.maxHP / 2) {
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]++;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]++;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED]++;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] > MIN_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]--;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE] > MIN_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE]--;
            }
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

    case ABILITY_ELECTROMORPHOSIS:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_ELECTROMORPHOSIS) == TRUE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            DEFENDING_MON.moveEffectsMask |= MOVE_EFFECT_CHARGE;
            DEFENDING_MON.moveEffectsData.chargedTurns = 2;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

""",
        "MR08I defender reaction family",
    )


def patch_defiant_competitive(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_once(
        path,
        """        if (mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] < MIN_STAT_STAGE) {
            mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] = MIN_STAT_STAGE;
        }
    }

    return FALSE;
}
""",
        """        if (mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] < MIN_STAT_STAGE) {
            mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] = MIN_STAT_STAGE;
        }

        if (battleCtx->attacker != battleCtx->sideEffectMon
            && BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker)
                != BattleSystem_GetBattlerSide(
                    battleSys, battleCtx->sideEffectMon)) {
            if (Battler_Ability(
                    battleCtx, battleCtx->sideEffectMon) == ABILITY_DEFIANT
                && mon->statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_ATTACK] += 2;
                if (mon->statBoosts[BATTLE_STAT_ATTACK] > MAX_STAT_STAGE) {
                    mon->statBoosts[BATTLE_STAT_ATTACK] = MAX_STAT_STAGE;
                }
            } else if (Battler_Ability(
                           battleCtx,
                           battleCtx->sideEffectMon) == ABILITY_COMPETITIVE
                && mon->statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_SP_ATTACK] += 2;
                if (mon->statBoosts[BATTLE_STAT_SP_ATTACK] > MAX_STAT_STAGE) {
                    mon->statBoosts[BATTLE_STAT_SP_ATTACK] = MAX_STAT_STAGE;
                }
            }
        }
    }

    return FALSE;
}
""",
        "Defiant / Competitive opponent stat-drop response",
    )


def patch_unseen_fist(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    if (battleCtx->turnFlags[defender].protecting
        && (MOVE_DATA(move).flags & MOVE_FLAG_CAN_PROTECT)
        && (move != MOVE_CURSE || Move_IsGhostCurse(battleCtx, move, attacker) == TRUE) // Ghost-Curse can be Protected
""",
        """    if (battleCtx->turnFlags[defender].protecting
        && (MOVE_DATA(move).flags & MOVE_FLAG_CAN_PROTECT)
        && !(Battler_Ability(battleCtx, attacker) == ABILITY_UNSEEN_FIST
            && (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT))
        && (move != MOVE_CURSE || Move_IsGhostCurse(battleCtx, move, attacker) == TRUE) // Ghost-Curse can be Protected
""",
        "Unseen Fist Protect bypass",
    )


def patch_rattled_intimidate(root: Path) -> None:
    path = root / "res/battle/scripts/subscripts/subscript_intimidate.s"

    replace_once(
        path,
        """    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_ATTACK_DOWN_1_STAGE
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_ABILITY
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE
    GoTo _038

_MercuryGuardDog:
""",
        """    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_ATTACK_DOWN_1_STAGE
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_ABILITY
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_RATTLED, _038
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_ABILITY
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE
    GoTo _038

_MercuryGuardDog:
""",
        "Rattled Intimidate Speed boost",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    controller = (
        root / "src/battle/battle_controller_player.c"
    ).read_text(encoding="utf-8")
    intimidate = (
        root / "res/battle/scripts/subscripts/subscript_intimidate.s"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "defiant_hook":
            "ABILITY_DEFIANT" in script
            and "mon->statBoosts[BATTLE_STAT_ATTACK] += 2;" in script,
        "competitive_hook":
            "ABILITY_COMPETITIVE" in script
            and "mon->statBoosts[BATTLE_STAT_SP_ATTACK] += 2;" in script,
        "cursed_body_hook":
            "case ABILITY_CURSED_BODY:" in lib
            and "disabledTurns = 4;" in lib,
        "weak_armor_hook":
            "case ABILITY_WEAK_ARMOR:" in lib
            and "statBoosts[BATTLE_STAT_SPEED] += 2;" in lib,
        "overcoat_hook":
            "Mercury_MoveIsPowder" in lib
            and lib.count("ABILITY_OVERCOAT") >= 1
            and script.count("ABILITY_OVERCOAT") >= 2,
        "mummy_hook":
            "case ABILITY_MUMMY:" in lib
            and "Mercury_AbilityCanBeOverwrittenByMummy" in lib,
        "rattled_hook":
            "case ABILITY_RATTLED:" in lib
            and "ABILITY_RATTLED, _038" in intimidate,
        "refrigerate_hook":
            lib.count("ABILITY_REFRIGERATE") >= 5
            and "movePower = movePower * 12 / 10;" in lib,
        "mega_launcher_hook":
            "ABILITY_MEGA_LAUNCHER" in lib
            and "Mercury_MoveIsPulse" in lib,
        "triage_hook":
            lib.count("ABILITY_TRIAGE") >= 3
            and "Mercury_MoveIsTriageHealing" in lib,
        "cotton_down_hook":
            "case ABILITY_COTTON_DOWN:" in lib
            and "i != battleCtx->defender" in lib,
        "unseen_fist_hook":
            "ABILITY_UNSEEN_FIST" in controller
            and "MOVE_FLAG_MAKES_CONTACT" in controller,
        "lingering_aroma_hook":
            "case ABILITY_LINGERING_AROMA:" in lib,
        "anger_shell_hook":
            "case ABILITY_ANGER_SHELL:" in lib
            and "BATTLE_STAT_SP_DEFENSE" in lib,
        "electromorphosis_hook":
            "case ABILITY_ELECTROMORPHOSIS:" in lib
            and "moveEffectsData.chargedTurns = 2;" in lib,
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
        default=Path("mr08i-canonical-ability-reaction-type.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_helpers(root)
    patch_triage_priority(root)
    patch_refrigerate_and_mega_launcher(root)
    patch_overcoat(root)
    patch_reaction_family(root)
    patch_defiant_competitive(root)
    patch_unseen_fist(root)
    patch_rattled_intimidate(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08I_CANONICAL_ABILITY_REACTION_TYPE",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 95,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08I validation failed")


if __name__ == "__main__":
    main()
