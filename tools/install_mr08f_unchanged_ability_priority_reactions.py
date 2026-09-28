#!/usr/bin/env python3
"""MR08F — unchanged canonical Ability fast pass, priority/reaction family.

Ports ten more official/current-mainline Ability mechanics whose behavior is
unchanged in the pinned Elite Redux reference, using hg-engine as the DS-native
mechanics reference:

- Strong Jaw
- Sweet Veil
- Steam Engine
- Punk Rock
- Sand Spit
- Perish Body
- Pastel Veil
- Quick Draw
- Chilling Neigh
- Grim Neigh

Also closes the remaining Water Bubble burn-immunity piece from MR08B.
Locked MR07 Summary/Skills visuals are not touched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_STRONG_JAW",
    "ABILITY_SWEET_VEIL",
    "ABILITY_STEAM_ENGINE",
    "ABILITY_PUNK_ROCK",
    "ABILITY_SAND_SPIT",
    "ABILITY_PERISH_BODY",
    "ABILITY_PASTEL_VEIL",
    "ABILITY_QUICK_DRAW",
    "ABILITY_CHILLING_NEIGH",
    "ABILITY_GRIM_NEIGH",
)

EXPECTED_IDS = {
    "ABILITY_STRONG_JAW": 173,
    "ABILITY_SWEET_VEIL": 175,
    "ABILITY_STEAM_ENGINE": 243,
    "ABILITY_PUNK_ROCK": 244,
    "ABILITY_SAND_SPIT": 245,
    "ABILITY_PERISH_BODY": 253,
    "ABILITY_PASTEL_VEIL": 257,
    "ABILITY_QUICK_DRAW": 259,
    "ABILITY_CHILLING_NEIGH": 264,
    "ABILITY_GRIM_NEIGH": 265,
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

    # Shared canonical move-property helpers, mirrored from the pinned
    # hg-engine tables. Modern move constants are already installed earlier in
    # the Mercury workflow.
    insert_before_once(
        path,
        """static BOOL Mercury_MoveIsBallOrBomb(int move)
""",
        """static BOOL Mercury_MoveIsBiting(int move)
{
    switch (move) {
    case MOVE_BITE:
    case MOVE_CRUNCH:
    case MOVE_FIRE_FANG:
    case MOVE_FISHIOUS_REND:
    case MOVE_HYPER_FANG:
    case MOVE_ICE_FANG:
    case MOVE_JAW_LOCK:
    case MOVE_POISON_FANG:
    case MOVE_PSYCHIC_FANGS:
    case MOVE_THUNDER_FANG:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_MoveIsSound(int move)
{
    switch (move) {
    case MOVE_ALLURING_VOICE:
    case MOVE_BOOMBURST:
    case MOVE_BUG_BUZZ:
    case MOVE_CHATTER:
    case MOVE_CLANGING_SCALES:
    case MOVE_CLANGOROUS_SOUL:
    case MOVE_CLANGOROUS_SOULBLAZE:
    case MOVE_CONFIDE:
    case MOVE_DISARMING_VOICE:
    case MOVE_ECHOED_VOICE:
    case MOVE_EERIE_SPELL:
    case MOVE_GRASS_WHISTLE:
    case MOVE_GROWL:
    case MOVE_HEAL_BELL:
    case MOVE_HOWL:
    case MOVE_HYPER_VOICE:
    case MOVE_METAL_SOUND:
    case MOVE_NOBLE_ROAR:
    case MOVE_OVERDRIVE:
    case MOVE_PARTING_SHOT:
    case MOVE_PERISH_SONG:
    case MOVE_PSYCHIC_NOISE:
    case MOVE_RELIC_SONG:
    case MOVE_ROAR:
    case MOVE_ROUND:
    case MOVE_SCREECH:
    case MOVE_SING:
    case MOVE_SNARL:
    case MOVE_SNORE:
    case MOVE_SPARKLING_ARIA:
    case MOVE_SUPERSONIC:
    case MOVE_TORCH_SONG:
    case MOVE_UPROAR:
        return TRUE;
    default:
        return FALSE;
    }
}

""",
        "Strong Jaw / Punk Rock move-property helpers",
    )

    # Strong Jaw and Punk Rock share the normal move-power lane.
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_ANALYTIC
""",
        """    if (attackerParams.ability == ABILITY_STRONG_JAW
        && Mercury_MoveIsBiting(move)) {
        movePower = movePower * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_PUNK_ROCK
        && Mercury_MoveIsSound(move)) {
        movePower = movePower * 13 / 10;
    }

""",
        "Strong Jaw / Punk Rock offensive modifiers",
    )

    # Punk Rock also halves incoming sound-move damage and is Mold Breaker
    # ignorable in the pinned DS reference.
    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_ICE_SCALES) == TRUE
""",
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_PUNK_ROCK) == TRUE
        && Mercury_MoveIsSound(move)) {
        damage /= 2;
    }

""",
        "Punk Rock defensive modifier",
    )

    # Quick Draw uses the same action-order lane as Quick Claw, but only when
    # the battler actually selected a move. speedRand is fixed once per turn.
    insert_before_once(
        path,
        """    if (battler1Priority == battler2Priority) {
""",
        """    if (battler1Action == PLAYER_INPUT_FIGHT
        && battler1Ability == ABILITY_QUICK_DRAW
        && battleCtx->speedRand[battler1] % 10 < 3) {
        battler1QuickClaw = 1;
    }

    if (battler2Action == PLAYER_INPUT_FIGHT
        && battler2Ability == ABILITY_QUICK_DRAW
        && battleCtx->speedRand[battler2] % 10 < 3) {
        battler2QuickClaw = 1;
    }

""",
        "Quick Draw action-order hook",
    )

    # Steam Engine, Sand Spit, and Perish Body all trigger after a damaging
    # hit. Direct state updates are used for the +6 Speed and timed-weather /
    # perish counters because Platinum's stock stat/weather scripts cannot
    # encode those modern values exactly.
    insert_before_once(
        path,
        """    case ABILITY_BERSERK: {
""",
        """    case ABILITY_STEAM_ENGINE: {
        int moveType;

        if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NORMALIZE) {
            moveType = TYPE_NORMAL;
        } else if (battleCtx->moveType) {
            moveType = battleCtx->moveType;
        } else {
            moveType = CURRENT_MOVE_DATA.type;
        }

        if (DEFENDING_MON.curHP
            && (moveType == TYPE_FIRE || moveType == TYPE_WATER)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] < MAX_STAT_STAGE) {
            int newStage = DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] + 6;
            if (newStage > MAX_STAT_STAGE) {
                newStage = MAX_STAT_STAGE;
            }
            DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] = newStage;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

    case ABILITY_SAND_SPIT:
        if (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken) {
            battleCtx->fieldConditionsMask &= ~FIELD_CONDITION_WEATHER;
            battleCtx->fieldConditionsMask |= FIELD_CONDITION_SANDSTORM_TEMP;
            battleCtx->fieldConditions.weatherTurns = 5;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_PERISH_BODY: {
        BOOL applied = FALSE;

        if ((DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)) {
            if ((ATTACKING_MON.moveEffectsMask & MOVE_EFFECT_PERISH_SONG) == FALSE) {
                ATTACKING_MON.moveEffectsMask |= MOVE_EFFECT_PERISH_SONG;
                ATTACKING_MON.moveEffectsData.perishSongTurns = 3;
                applied = TRUE;
            }

            if ((DEFENDING_MON.moveEffectsMask & MOVE_EFFECT_PERISH_SONG) == FALSE) {
                DEFENDING_MON.moveEffectsMask |= MOVE_EFFECT_PERISH_SONG;
                DEFENDING_MON.moveEffectsData.perishSongTurns = 3;
                applied = TRUE;
            }
        }

        if (applied) {
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

""",
        "Steam Engine / Sand Spit / Perish Body reaction hooks",
    )

    # Chilling Neigh and Grim Neigh share the existing post-KO Moxie lane.
    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MOXIE
        && battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
        battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->attacker;
        *subscript = subscript_update_stat_stage;
        return TRUE;
    }

    return FALSE;
}
""",
        """    switch (Battler_Ability(battleCtx, battleCtx->attacker)) {
    case ABILITY_MOXIE:
    case ABILITY_CHILLING_NEIGH:
        if (battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            *subscript = subscript_update_stat_stage;
            return TRUE;
        }
        break;

    case ABILITY_GRIM_NEIGH:
        if (battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_SP_ATTACK_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            *subscript = subscript_update_stat_stage;
            return TRUE;
        }
        break;
    }

    return FALSE;
}
""",
        "Chilling Neigh / Grim Neigh KO hooks",
    )

    # Pastel Veil cures poison on the holder and its ally. The existing
    # forbidden-status switch-in lane already owns the cure script/message.
    replace_once(
        path,
        """BOOL BattleSystem_RecoverStatusByAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int skipLoad)
{
    BOOL result = FALSE;

    switch (Battler_Ability(battleCtx, battler)) {
""",
        """BOOL BattleSystem_RecoverStatusByAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int skipLoad)
{
    BOOL result = FALSE;
    int recoveryAbility = Battler_Ability(battleCtx, battler);

    if ((battleCtx->battleMons[battler].status & MON_CONDITION_ANY_POISON)
        && Mercury_AllyHasAbility(battleSys, battleCtx, battler, ABILITY_PASTEL_VEIL)) {
        recoveryAbility = ABILITY_PASTEL_VEIL;
    }

    switch (recoveryAbility) {
""",
        "Pastel Veil ally cure setup",
    )

    replace_once(
        path,
        """    case ABILITY_IMMUNITY:
        if (battleCtx->battleMons[battler].status & MON_CONDITION_ANY_POISON) {
""",
        """    case ABILITY_IMMUNITY:
    case ABILITY_PASTEL_VEIL:
        if (battleCtx->battleMons[battler].status & MON_CONDITION_ANY_POISON) {
""",
        "Pastel Veil poison cure",
    )

    replace_once(
        path,
        """        battleCtx->msgBattlerTemp = battler;
        battleCtx->msgAbilityTemp = Battler_Ability(battleCtx, battler);
""",
        """        battleCtx->msgBattlerTemp = battler;
        battleCtx->msgAbilityTemp = recoveryAbility;
""",
        "Pastel Veil cure message ability",
    )


def patch_team_status_checks(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    # Sweet Veil and Pastel Veil protect the holder plus its active ally.
    # Centralizing the holder lookup keeps sleep/poison scripts small and
    # preserves Mold Breaker behavior for move-caused status.
    insert_before_once(
        path,
        """static BOOL BtlCmd_CheckAbility(BattleSystem *battleSys, BattleContext *battleCtx)
""",
        """static int Mercury_FindTeamAbilityHolder(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int attacker,
    int battler,
    int ability,
    BOOL ignorable)
{
    int holder = battler;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    if (battleCtx->battleMons[holder].curHP
        && ((ignorable
                && Battler_IgnorableAbility(battleCtx, attacker, holder, ability) == TRUE)
            || (!ignorable && Battler_Ability(battleCtx, holder) == ability))) {
        return holder;
    }

    holder = battler ^ 2;
    if (holder < maxBattlers
        && BattleSystem_GetBattlerSide(battleSys, holder)
            == BattleSystem_GetBattlerSide(battleSys, battler)
        && battleCtx->battleMons[holder].curHP
        && ((ignorable
                && Battler_IgnorableAbility(battleCtx, attacker, holder, ability) == TRUE)
            || (!ignorable && Battler_Ability(battleCtx, holder) == ability))) {
        return holder;
    }

    return BATTLER_NONE;
}

""",
        "team Ability holder helper",
    )

    replace_once(
        path,
        """    } else {
        battler = BattleScript_Battler(battleSys, battleCtx, inBattler);

        if (op == CHECK_HAVE) {
            if (Battler_Ability(battleCtx, battler) == ability) {
                BattleScript_Iter(battleCtx, jump);
                battleCtx->abilityMon = battler;
            }
        } else if (Battler_Ability(battleCtx, battler) != ability) {
            BattleScript_Iter(battleCtx, jump);
            battleCtx->abilityMon = battler;
        }
    }

    return FALSE;
}

/**
 * @brief Generate a random value
""",
        """    } else {
        battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
        int holder = BATTLER_NONE;

        if (ability == ABILITY_SWEET_VEIL || ability == ABILITY_PASTEL_VEIL) {
            holder = Mercury_FindTeamAbilityHolder(
                battleSys, battleCtx, battleCtx->attacker, battler, ability, FALSE);
        } else if (Battler_Ability(battleCtx, battler) == ability) {
            holder = battler;
        }

        if (op == CHECK_HAVE) {
            if (holder != BATTLER_NONE) {
                BattleScript_Iter(battleCtx, jump);
                battleCtx->abilityMon = holder;
            }
        } else if (holder == BATTLER_NONE) {
            BattleScript_Iter(battleCtx, jump);
            battleCtx->abilityMon = battler;
        }
    }

    return FALSE;
}

/**
 * @brief Generate a random value
""",
        "team-aware CheckAbility",
    )

    replace_once(
        path,
        """    } else {
        battler = BattleScript_Battler(battleSys, battleCtx, inBattler);

        if (op == CHECK_HAVE) {
            if (Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battler, ability) == TRUE
                && battleCtx->battleMons[battler].curHP) {
                BattleScript_Iter(battleCtx, jump);
                battleCtx->abilityMon = battler;
            }
        } else if (Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battler, ability) == FALSE
            || battleCtx->battleMons[battler].curHP == 0) {
            BattleScript_Iter(battleCtx, jump);
            battleCtx->abilityMon = battler;
        }
    }

    return FALSE;
}

/**
 * @brief GoTo forward
""",
        """    } else {
        battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
        int holder = BATTLER_NONE;

        if (ability == ABILITY_SWEET_VEIL || ability == ABILITY_PASTEL_VEIL) {
            holder = Mercury_FindTeamAbilityHolder(
                battleSys, battleCtx, battleCtx->attacker, battler, ability, TRUE);
        } else if (Battler_IgnorableAbility(
                       battleCtx, battleCtx->attacker, battler, ability) == TRUE
            && battleCtx->battleMons[battler].curHP) {
            holder = battler;
        }

        if (op == CHECK_HAVE) {
            if (holder != BATTLER_NONE) {
                BattleScript_Iter(battleCtx, jump);
                battleCtx->abilityMon = holder;
            }
        } else if (holder == BATTLER_NONE) {
            BattleScript_Iter(battleCtx, jump);
            battleCtx->abilityMon = battler;
        }
    }

    return FALSE;
}

/**
 * @brief GoTo forward
""",
        "team-aware CheckIgnorableAbility",
    )


def patch_status_scripts(root: Path) -> None:
    sleep = root / "res/battle/scripts/subscripts/subscript_fall_asleep.s"
    poison = root / "res/battle/scripts/subscripts/subscript_poison.s"
    toxic = root / "res/battle/scripts/subscripts/subscript_badly_poison.s"
    burn = root / "res/battle/scripts/subscripts/subscript_burn.s"

    replace_once(
        sleep,
        """_000:
    CompareVarToValue OPCODE_EQU, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_DISOBEDIENCE, _147
    CompareVarToValue OPCODE_NEQ, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_MOVE_EFFECT, _055
""",
        """_000:
    CompareVarToValue OPCODE_EQU, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_DISOBEDIENCE, _147
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_SWEET_VEIL, _MercurySweetVeil
    CompareVarToValue OPCODE_NEQ, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_MOVE_EFFECT, _055
""",
        "Sweet Veil sleep prevention",
    )
    insert_before_once(
        sleep,
        """_337:
    End 
""",
        """_MercurySweetVeil:
    PrintMessage BattleStrings_Text_PokemonStayedAwakeBecauseOfItsAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_SIDE_EFFECT_MON, BTLSCR_ABILITY_MON
    Wait 
    WaitButtonABTime 30
    UpdateVar OPCODE_FLAG_ON, BTLVAR_MOVE_STATUS_FLAGS, MOVE_STATUS_NO_MORE_WORK
    End 

""",
        "Sweet Veil sleep message",
    )

    replace_once(
        poison,
        """_000:
    CompareVarToValue OPCODE_NEQ, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_TOXIC_SPIKES, _023
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177
""",
        """_000:
    CompareVarToValue OPCODE_NEQ, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_TOXIC_SPIKES, _023
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PASTEL_VEIL, _MercuryPastelVeil
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177
""",
        "Pastel Veil Toxic Spikes poison prevention",
    )
    replace_once(
        poison,
        """_023:
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177
""",
        """_023:
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PASTEL_VEIL, _MercuryPastelVeil
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177
""",
        "Pastel Veil poison prevention",
    )
    insert_before_once(
        poison,
        """_322:
    End 
""",
        """_MercuryPastelVeil:
    PrintMessage BattleStrings_Text_PokemonsAbilityPreventsPoisoning_Ally, TAG_NICKNAME_ABILITY, BTLSCR_SIDE_EFFECT_MON, BTLSCR_ABILITY_MON
    Wait 
    WaitButtonABTime 30
    UpdateVar OPCODE_FLAG_ON, BTLVAR_MOVE_STATUS_FLAGS, MOVE_STATUS_NO_MORE_WORK
    End 

""",
        "Pastel Veil poison message",
    )

    replace_once(
        toxic,
        """_000:
    CompareVarToValue OPCODE_NEQ, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_TOXIC_SPIKES, _023
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249
""",
        """_000:
    CompareVarToValue OPCODE_NEQ, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_TOXIC_SPIKES, _023
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PASTEL_VEIL, _MercuryPastelVeil
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249
""",
        "Pastel Veil Toxic Spikes toxic prevention",
    )
    replace_once(
        toxic,
        """_023:
    CompareVarToValue OPCODE_NEQ, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_HELD_ITEM, _094
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _248
""",
        """_023:
    CompareVarToValue OPCODE_NEQ, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_HELD_ITEM, _094
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PASTEL_VEIL, _MercuryPastelVeil
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _248
""",
        "Pastel Veil held-item toxic prevention",
    )
    replace_once(
        toxic,
        """_094:
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249
""",
        """_094:
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_PASTEL_VEIL, _MercuryPastelVeil
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249
""",
        "Pastel Veil toxic prevention",
    )
    insert_before_once(
        toxic,
        """_355:
    End 
""",
        """_MercuryPastelVeil:
    PrintMessage BattleStrings_Text_PokemonsAbilityPreventsPoisoning_Ally, TAG_NICKNAME_ABILITY, BTLSCR_SIDE_EFFECT_MON, BTLSCR_ABILITY_MON
    Wait 
    WaitButtonABTime 30
    UpdateVar OPCODE_FLAG_ON, BTLVAR_MOVE_STATUS_FLAGS, MOVE_STATUS_NO_MORE_WORK
    End 

""",
        "Pastel Veil toxic message",
    )

    # MR08B already installed Water Bubble's Water/Fire damage mechanics; add
    # the canonical burn immunity using the exact Water Veil lanes.
    replace_once(
        burn,
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _211
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _211
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _211
""",
        "Water Bubble held-item burn immunity",
    )
    replace_once(
        burn,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _264
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _264
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _264
""",
        "Water Bubble move burn immunity",
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
    sleep = (root / "res/battle/scripts/subscripts/subscript_fall_asleep.s").read_text(encoding="utf-8")
    poison = (root / "res/battle/scripts/subscripts/subscript_poison.s").read_text(encoding="utf-8")
    toxic = (root / "res/battle/scripts/subscripts/subscript_badly_poison.s").read_text(encoding="utf-8")
    burn = (root / "res/battle/scripts/subscripts/subscript_burn.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "strong_jaw_hook":
            "ABILITY_STRONG_JAW" in lib and "Mercury_MoveIsBiting" in lib,
        "sweet_veil_hook":
            "ABILITY_SWEET_VEIL" in script and "_MercurySweetVeil" in sleep,
        "steam_engine_hook":
            "case ABILITY_STEAM_ENGINE:" in lib and "+ 6" in lib,
        "punk_rock_hook":
            lib.count("ABILITY_PUNK_ROCK") >= 2 and "Mercury_MoveIsSound" in lib,
        "sand_spit_hook":
            "case ABILITY_SAND_SPIT:" in lib
            and "FIELD_CONDITION_SANDSTORM_TEMP" in lib
            and "weatherTurns = 5" in lib,
        "perish_body_hook":
            "case ABILITY_PERISH_BODY:" in lib and "perishSongTurns = 3" in lib,
        "pastel_veil_hook":
            "ABILITY_PASTEL_VEIL" in script
            and "_MercuryPastelVeil" in poison
            and "_MercuryPastelVeil" in toxic
            and "case ABILITY_PASTEL_VEIL:" in lib,
        "quick_draw_hook":
            "ABILITY_QUICK_DRAW" in lib and "speedRand[battler1] % 10 < 3" in lib,
        "chilling_neigh_hook":
            "case ABILITY_CHILLING_NEIGH:" in lib,
        "grim_neigh_hook":
            "case ABILITY_GRIM_NEIGH:" in lib,
        "water_bubble_burn_fix":
            "ABILITY_WATER_BUBBLE, _264" in burn
            and "ABILITY_WATER_BUBBLE, _211" in burn,
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
        default=Path("mr08f-unchanged-ability-priority-reactions.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_battle_lib(root)
    patch_team_status_checks(root)
    patch_status_scripts(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08F_UNCHANGED_ABILITY_PRIORITY_REACTIONS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 55,
        "completeness_fixes": ["Water Bubble burn immunity"],
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "elite_redux_reference": "Elite-Redux/eliteredux pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08F validation failed")


if __name__ == "__main__":
    main()
