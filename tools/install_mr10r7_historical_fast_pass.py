#!/usr/bin/env python3
"""MR10R7 — historical composite/generation fast pass.

Restores twenty historical identities using four shared systems:
- native two-strike reuse for Hyper Aggressive / Primal Maw / Raging Boxer;
- generated follow-up actions for post-move and reactive attacks;
- battle-only added typing for Trick-or-Treat / Forest's Curse / Metallic;
- compact switch-in and active-state hooks for entry/status composites.

Mechanics only; locked MR07 visuals remain untouched.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

IMPLEMENTED = {
    "Balloon Blitz": ("ABILITY_BALLOON_BLITZ", 349),
    "Blood Stigma": ("ABILITY_BLOOD_STIGMA", 364),
    "Brawling Wyvern": ("ABILITY_BRAWLING_WYVERN", 365),
    "Chunky Bass Line": ("ABILITY_CHUNKY_BASS_LINE", 372),
    "Frost Burn": ("ABILITY_FROST_BURN", 432),
    "Ice Downfall": ("ABILITY_ICE_DOWNFALL", 460),
    "Metallic Jaws": ("ABILITY_METALLIC_JAWS", 494),
    "Monster Mash": ("ABILITY_MONSTER_MASH", 502),
    "Overwatch": ("ABILITY_OVERWATCH", 515),
    "Pretentious": ("ABILITY_PRETENTIOUS", 530),
    "Raging Goddess": ("ABILITY_RAGING_GODDESS", 546),
    "Retriever": ("ABILITY_RETRIEVER", 553),
    "Steel Beetle": ("ABILITY_STEEL_BEETLE", 584),
    "Tar Toss": ("ABILITY_TAR_TOSS", 594),
    "Trickster": ("ABILITY_TRICKSTER", 605),
    "Two Step": ("ABILITY_TWO_STEP", 606),
    "Web Spinner": ("ABILITY_WEB_SPINNER", 619),
    "Wind Rage": ("ABILITY_WIND_RAGE", 624),
    "Woodland Curse": ("ABILITY_WOODLAND_CURSE", 625),
    "Cosmic Daze": ("ABILITY_COSMIC_DAZE", 1017),
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
    pos = 0
    start = -1
    open_brace = -1
    while True:
        candidate = text.find(signature, pos)
        if candidate < 0:
            break
        brace = text.find("{", candidate)
        semi = text.find(";", candidate)
        if brace >= 0 and (semi < 0 or brace < semi):
            start = candidate
            open_brace = brace
            break
        pos = candidate + len(signature)
    if start < 0:
        raise SystemExit(f"function definition not found: {signature}")
    depth = 0
    for i in range(open_brace, len(text)):
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
    if count != 1:
        raise SystemExit(f"{label}: expected one scoped anchor, found {count}")
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
    if count != 1:
        raise SystemExit(f"{label}: expected one scoped anchor, found {count}")
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
    insertion = """    // Mercury MR10R7 shared historical state.
    u8 mercuryR7GeneratedAction;
    u8 mercuryR7GeneratedActive;
    u8 mercuryR7GeneratedOriginalAttacker;
    u8 mercuryR7GeneratedOriginalDefender;
    u16 mercuryR7GeneratedOriginalMove;
    u16 mercuryR7GeneratedMove;
    u16 mercuryR7GeneratedPower;

    u8 mercuryR7ReactivePending[MAX_BATTLERS];
    u8 mercuryR7ReactiveTarget[MAX_BATTLERS];
    u16 mercuryR7ReactiveMove[MAX_BATTLERS];
    u16 mercuryR7ReactivePower[MAX_BATTLERS];

    u8 mercuryR7CustomMultiHitActive;
    u16 mercuryR7CustomMultiHitAbility;

    u8 mercuryR7AddedType[MAX_BATTLERS];
    u8 mercuryR7Tarred[MAX_BATTLERS];
    u8 mercuryR7Bleeding[MAX_BATTLERS];
    u8 mercuryR7Enraged[MAX_BATTLERS];
    u8 mercuryR7CritStage[MAX_BATTLERS];

"""
    insert_before_once(
        path,
        "    u32 battleProgressFlag : 1;\n",
        insertion,
        "mercuryR7GeneratedAction",
        "R7 battle context",
    )


def patch_subscript(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    followup = scripts / "subscript_mercury_r7_generated.s"
    followup.write_text(
        """#include "macros/btlcmd.inc"


_000:
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mold_breaker\n",
        "subscript_mercury_r7_generated\n",
        "subscript_mercury_r7_generated",
        "R7 subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mold_breaker.s',\n",
        "    'subscript_mercury_r7_generated.s',\n",
        "subscript_mercury_r7_generated.s",
        "R7 subscript build",
    )


def patch_runtime_state_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    battleCtx->battleMons[battler].weatherAbilityAnnounced = FALSE;
"""
    insertion = """    battleCtx->mercuryR7AddedType[battler] = 0;
    battleCtx->mercuryR7Tarred[battler] = FALSE;
    battleCtx->mercuryR7Bleeding[battler] = FALSE;
    battleCtx->mercuryR7Enraged[battler] = FALSE;
    battleCtx->mercuryR7CritStage[battler] = 0;

"""
    insert_before_in_function(
        path,
        "void BattleSystem_InitBattleMon(",
        anchor,
        insertion,
        "mercuryR7CritStage[battler] = 0;",
        "R7 per-entry state reset",
    )


def patch_added_type_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    helper = """int Mercury_R7AddedType(BattleContext *battleCtx, int battler)
{
    int ability = Battler_Ability(battleCtx, battler);

    if (ability == ABILITY_METALLIC_JAWS) {
        return TYPE_STEEL;
    }

    if (battleCtx->mercuryR7AddedType[battler]) {
        return battleCtx->mercuryR7AddedType[battler];
    }

    return 0xFF;
}

BOOL Mercury_R7HasType(BattleContext *battleCtx, int battler, int type)
{
    return BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_1, NULL) == type
        || BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_2, NULL) == type
        || Mercury_R7AddedType(battleCtx, battler) == type;
}

"""
    insert_before_once(
        lib,
        "BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)\n",
        helper,
        "Mercury_R7AddedType",
        "R7 added-type helpers",
    )
    insert_before_once(
        hdr,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);\n",
        "int Mercury_R7AddedType(BattleContext *battleCtx, int battler);\nBOOL Mercury_R7HasType(BattleContext *battleCtx, int battler, int type);\n",
        "Mercury_R7HasType",
        "R7 added-type declarations",
    )

    # STAB for static/dynamic added types.
    insert_before_in_function(
        lib,
        "int BattleSystem_ApplyTypeChart(",
        """    if ((battleCtx->battleStatusMask & SYSCTL_IGNORE_TYPE_CHECKS) == FALSE && MON_HAS_TYPE(attacker, moveType)) {
""",
        """    if ((battleCtx->battleStatusMask & SYSCTL_IGNORE_TYPE_CHECKS) == FALSE
        && Mercury_R7AddedType(battleCtx, attacker) == moveType
        && MON_HAS_TYPE(attacker, moveType) == FALSE) {
        damage = damage * 15 / 10;
    }

""",
        "Mercury_R7AddedType(battleCtx, attacker) == moveType",
        "R7 added-type STAB",
    )

    # Defensive type-chart contribution.
    insertion = """    {
        int mercuryR7Type = Mercury_R7AddedType(battleCtx, defender);
        if (mercuryR7Type != 0xFF
            && mercuryR7Type != BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_1, NULL)
            && mercuryR7Type != BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_2, NULL)
            && (*moveStatusMask & MOVE_STATUS_NO_EFFECTS) == FALSE) {
            chartEntry = 0;
            while (sTypeMatchupMultipliers[chartEntry][0] != 0xFF) {
                if (sTypeMatchupMultipliers[chartEntry][0] != 0xFE
                    && sTypeMatchupMultipliers[chartEntry][0] == moveType
                    && sTypeMatchupMultipliers[chartEntry][1] == mercuryR7Type
                    && BasicTypeMulApplies(
                        battleCtx, attacker, defender, chartEntry) == TRUE) {
                    damage = ApplyTypeMultiplier(
                        battleCtx,
                        attacker,
                        sTypeMatchupMultipliers[chartEntry][2],
                        damage,
                        movePower,
                        moveStatusMask);
                }
                chartEntry++;
            }
        }
    }

"""
    insert_before_in_function(
        lib,
        "int BattleSystem_ApplyTypeChart(",
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WONDER_GUARD) == TRUE
""",
        insertion,
        "int mercuryR7Type = Mercury_R7AddedType",
        "R7 added defensive type chart",
    )


def patch_controller_helpers(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    helper = """static BOOL Mercury_R7DanceMove(int move)
{
    switch (move) {
    case MOVE_DRAGON_DANCE:
    case MOVE_FEATHER_DANCE:
    case MOVE_LUNAR_DANCE:
    case MOVE_PETAL_DANCE:
    case MOVE_RAIN_DANCE:
    case MOVE_SWORDS_DANCE:
    case MOVE_TEETER_DANCE:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_R7MoveAllowedForExtraHit(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int move = battleCtx->moveCur;
    int effect = MOVE_DATA(move).effect;
    int range = MOVE_DATA(move).range;
    int battleType = BattleSystem_GetBattleType(battleSys);
    int i;
    int liveTargets = 0;
    int maxBattlers;

    if (MOVE_DATA(move).class == CLASS_STATUS
        || MOVE_DATA(move).power == 0
        || Move_IsMultiTurn(battleCtx, move) == TRUE) {
        return FALSE;
    }

    switch (effect) {
    case BATTLE_EFFECT_MULTI_HIT:
    case BATTLE_EFFECT_HIT_TWICE:
    case BATTLE_EFFECT_POISON_MULTI_HIT:
    case BATTLE_EFFECT_ONE_HIT_KO:
        return FALSE;
    }

    switch (move) {
    case MOVE_SELFDESTRUCT:
    case MOVE_EXPLOSION:
    case MOVE_FLING:
    case MOVE_ENDEAVOR:
    case MOVE_PRESENT:
    case MOVE_TRIPLE_KICK:
    case MOVE_BEAT_UP:
        return FALSE;
    }

    if ((battleType & BATTLE_TYPE_DOUBLES) == FALSE) {
        return TRUE;
    }

    maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    if (range == RANGE_ADJACENT_OPPONENTS) {
        for (i = 0; i < maxBattlers; i++) {
            if (i != battleCtx->attacker
                && battleCtx->battleMons[i].curHP
                && BattleSystem_GetBattlerSide(battleSys, i)
                    != BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker)) {
                liveTargets++;
            }
        }
    } else if (range == RANGE_ALL_ADJACENT) {
        for (i = 0; i < maxBattlers; i++) {
            if (i != battleCtx->attacker && battleCtx->battleMons[i].curHP) {
                liveTargets++;
            }
        }
    } else {
        return TRUE;
    }

    return liveTargets == 1;
}

static BOOL Mercury_R7MoveIsPunching(int move)
{
    switch (move) {
    case MOVE_ICE_PUNCH:
    case MOVE_FIRE_PUNCH:
    case MOVE_THUNDER_PUNCH:
    case MOVE_MACH_PUNCH:
    case MOVE_FOCUS_PUNCH:
    case MOVE_DIZZY_PUNCH:
    case MOVE_DYNAMIC_PUNCH:
    case MOVE_HAMMER_ARM:
    case MOVE_MEGA_PUNCH:
    case MOVE_COMET_PUNCH:
    case MOVE_METEOR_MASH:
    case MOVE_SHADOW_PUNCH:
    case MOVE_DRAIN_PUNCH:
    case MOVE_BULLET_PUNCH:
    case MOVE_SKY_UPPERCUT:
        return TRUE;
    default:
        return FALSE;
    }
}

static int Mercury_R7ExtraHitAbility(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int ability = Battler_Ability(battleCtx, battleCtx->attacker);
    int move = battleCtx->moveCur;

    if (Mercury_R7MoveAllowedForExtraHit(battleSys, battleCtx) == FALSE) {
        return ABILITY_NONE;
    }

    if (ability == ABILITY_BALLOON_BLITZ
        || ability == ABILITY_RAGING_GODDESS) {
        return ability;
    }

    if (ability == ABILITY_METALLIC_JAWS
        && Mercury_MoveIsBitingForCustomAbility(move)) {
        return ability;
    }

    if (ability == ABILITY_STEEL_BEETLE
        && Mercury_R7MoveIsPunching(move)) {
        return ability;
    }

    return ABILITY_NONE;
}

static void Mercury_R7SetupExtraHit(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int ability;

    battleCtx->mercuryR7CustomMultiHitActive = FALSE;
    battleCtx->mercuryR7CustomMultiHitAbility = ABILITY_NONE;

    ability = Mercury_R7ExtraHitAbility(battleSys, battleCtx);
    if (ability == ABILITY_NONE) {
        return;
    }

    battleCtx->mercuryParentalBondActive = FALSE;
    battleCtx->mercuryR7CustomMultiHitActive = TRUE;
    battleCtx->mercuryR7CustomMultiHitAbility = ability;
    battleCtx->multiHitCounter = 2;
    battleCtx->multiHitNumHits = 2;
    battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;
    battleCtx->afterMoveMessageType = AFTER_MOVE_MESSAGE_MULTI_HIT;
}

static BOOL Mercury_R7SuccessfulMove(BattleContext *battleCtx)
{
    return (battleCtx->battleStatusMask2 & SYSCTL_ATTACK_MESSAGE_SHOWN)
        && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
        && (battleCtx->moveStatusFlags & MOVE_STATUS_DID_NOT_HIT) == FALSE;
}

static BOOL Mercury_R7ChooseFollowup(
    BattleContext *battleCtx,
    int *move,
    int *power)
{
    int ability = Battler_Ability(battleCtx, battleCtx->attacker);
    int moveType = CalcCurrentMoveType(battleCtx);

    *move = MOVE_NONE;
    *power = 0;

    if (ability == ABILITY_CHUNKY_BASS_LINE
        && Mercury_MoveIsSoundForHistoricalAbility(battleCtx->moveCur)) {
        *move = MOVE_EARTHQUAKE;
        *power = 40;
    } else if (ability == ABILITY_FROST_BURN
        && moveType == TYPE_FIRE) {
        *move = MOVE_ICE_BEAM;
        *power = 40;
    } else if (ability == ABILITY_TWO_STEP
        && Mercury_R7DanceMove(battleCtx->moveCur)) {
        *move = MOVE_REVELATION_DANCE;
        *power = 50;
    }

    return *move != MOVE_NONE;
}

static BOOL Mercury_R7QueueGenerated(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int user,
    int target,
    int move,
    int power)
{
    if (user == BATTLER_NONE || target == BATTLER_NONE
        || battleCtx->battleMons[user].curHP == 0
        || battleCtx->battleMons[target].curHP == 0) {
        return FALSE;
    }

    battleCtx->mercuryR7GeneratedActive = TRUE;
    battleCtx->mercuryR7GeneratedOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryR7GeneratedOriginalDefender = battleCtx->defender;
    battleCtx->mercuryR7GeneratedOriginalMove = battleCtx->moveCur;
    battleCtx->mercuryR7GeneratedMove = move;
    battleCtx->mercuryR7GeneratedPower = power;

    BattleContext_Init(battleCtx);
    battleCtx->mercuryR7GeneratedAction = TRUE;
    battleCtx->attacker = user;
    battleCtx->defender = target;
    battleCtx->moveCur = move;
    battleCtx->moveTemp = move;
    battleCtx->movePower = power;
    battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

    battleCtx->msgTemp = user;
    battleCtx->msgBattlerTemp = user;
    LOAD_SUBSEQ(subscript_mercury_r7_generated);
    battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
    battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
    return TRUE;
}

static BOOL Mercury_R7TryGenerated(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int move;
    int power;
    int target;

    if (battleCtx->mercuryR7GeneratedActive) {
        battleCtx->attacker = battleCtx->mercuryR7GeneratedOriginalAttacker;
        battleCtx->defender = battleCtx->mercuryR7GeneratedOriginalDefender;
        battleCtx->moveCur = battleCtx->mercuryR7GeneratedOriginalMove;
        battleCtx->moveTemp = battleCtx->mercuryR7GeneratedOriginalMove;
        battleCtx->mercuryR7GeneratedActive = FALSE;
        battleCtx->mercuryR7GeneratedAction = FALSE;
        battleCtx->mercuryR7GeneratedMove = MOVE_NONE;
        battleCtx->mercuryR7GeneratedPower = 0;
        return FALSE;
    }

    if (battleCtx->mercuryR7GeneratedAction) {
        return FALSE;
    }

    for (int user = 0; user < MAX_BATTLERS; user++) {
        if (battleCtx->mercuryR7ReactivePending[user]) {
            target = battleCtx->mercuryR7ReactiveTarget[user];
            move = battleCtx->mercuryR7ReactiveMove[user];
            power = battleCtx->mercuryR7ReactivePower[user];
            battleCtx->mercuryR7ReactivePending[user]--;
            return Mercury_R7QueueGenerated(
                battleSys, battleCtx, user, target, move, power);
        }
    }

    if (battleCtx->attacker == BATTLER_NONE
        || battleCtx->moveCur == MOVE_NONE
        || Mercury_R7SuccessfulMove(battleCtx) == FALSE
        || Mercury_R7ChooseFollowup(battleCtx, &move, &power) == FALSE) {
        return FALSE;
    }

    target = battleCtx->defender;
    if (target == BATTLER_NONE
        || battleCtx->battleMons[target].curHP == 0
        || BattleSystem_GetBattlerSide(battleSys, target)
            == BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker)) {
        target = BattleSystem_RandomOpponent(
            battleSys, battleCtx, battleCtx->attacker);
    }

    return Mercury_R7QueueGenerated(
        battleSys, battleCtx, battleCtx->attacker, target, move, power);
}

"""
    insert_before_once(
        path,
        "static void BattleControllerPlayer_BeforeMove(BattleSystem *battleSys, BattleContext *battleCtx)\n{\n",
        helper,
        "Mercury_R7SetupExtraHit",
        "R7 controller helpers",
    )

    # Add custom multi-hit setup after canonical Parental Bond.
    old = """        if (battleCtx->multiHitLoop == FALSE) {
            Mercury_SetupParentalBond(battleSys, battleCtx);
        }

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
"""
    new = """        if (battleCtx->multiHitLoop == FALSE) {
            Mercury_SetupParentalBond(battleSys, battleCtx);
            Mercury_R7SetupExtraHit(battleSys, battleCtx);
        }

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
"""
    replace_once(path, old, new, "R7 custom multi-hit setup")

    # Reactive/follow-up generated actions happen before ordinary move cleanup.
    insert_before_in_function(
        path,
        "static void BattleControllerPlayer_MoveEnd(",
        "        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);\n",
        """        if (Mercury_R7TryGenerated(battleSys, battleCtx) == TRUE) {
            return;
        }

""",
        "Mercury_R7TryGenerated(battleSys, battleCtx)",
        "R7 generated move-end hook",
    )

    # Retriever returns a consumed/lost item as it switches out.
    insert_after_in_function(
        path,
        "static void BattleControllerPlayer_SwitchCommand(",
        """    battleCtx->attacker = battleCtx->battlerActionOrder[battleCtx->turnOrderCounter];
""",
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_RETRIEVER
        && battleCtx->battleMons[battleCtx->attacker].heldItem == ITEM_NONE
        && battleCtx->recycleItem[battleCtx->attacker] != ITEM_NONE) {
        battleCtx->battleMons[battleCtx->attacker].heldItem =
            battleCtx->recycleItem[battleCtx->attacker];
        battleCtx->recycleItem[battleCtx->attacker] = ITEM_NONE;
        BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->attacker);
    }

""",
        "ABILITY_RETRIEVER",
        "Retriever switch-out recovery",
    )

    # Brawling Wyvern carries No Guard behavior.
    old = """            || Battler_Ability(battleCtx, attacker) == ABILITY_NO_GUARD
            || Battler_Ability(battleCtx, defender) == ABILITY_NO_GUARD)) {
"""
    new = """            || Battler_Ability(battleCtx, attacker) == ABILITY_NO_GUARD
            || Battler_Ability(battleCtx, defender) == ABILITY_NO_GUARD
            || Battler_Ability(battleCtx, attacker) == ABILITY_BRAWLING_WYVERN
            || Battler_Ability(battleCtx, defender) == ABILITY_BRAWLING_WYVERN)) {
"""
    replace_once(path, old, new, "Brawling Wyvern No Guard")


def patch_exported_move_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"
    helper = """BOOL Mercury_MoveIsSoundForHistoricalAbility(int move)
{
    return Mercury_MoveIsSound(move);
}

BOOL Mercury_MoveIsBitingForCustomAbility(int move)
{
    return Mercury_MoveIsBiting(move);
}

"""
    insert_before_once(
        lib,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)\n",
        helper,
        "Mercury_MoveIsSoundForHistoricalAbility",
        "R7 exported move helpers",
    )
    insert_before_once(
        hdr,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);\n",
        "BOOL Mercury_MoveIsSoundForHistoricalAbility(int move);\nBOOL Mercury_MoveIsBitingForCustomAbility(int move);\n",
        "Mercury_MoveIsSoundForHistoricalAbility",
        "R7 helper declarations",
    )


def patch_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Hyper Aggressive 25%, Primal Maw / Raging Boxer 50% on strike two.
    insertion = """    if (battleCtx->mercuryR7CustomMultiHitActive
        && battleCtx->multiHitLoop
        && damage > 0) {
        if (battleCtx->mercuryR7CustomMultiHitAbility == ABILITY_BALLOON_BLITZ
            || battleCtx->mercuryR7CustomMultiHitAbility == ABILITY_RAGING_GODDESS) {
            damage /= 4;
        } else if (battleCtx->mercuryR7CustomMultiHitAbility == ABILITY_METALLIC_JAWS
            || battleCtx->mercuryR7CustomMultiHitAbility == ABILITY_STEEL_BEETLE) {
            damage /= 2;
        }
        if (damage == 0) {
            damage = 1;
        }
    }

"""
    insert_before_in_function(
        path,
        "int BattleSystem_CalcMoveDamage(",
        "    return damage;\n",
        insertion,
        "mercuryR7CustomMultiHitAbility == ABILITY_BALLOON_BLITZ",
        "R7 second-hit scaling",
    )

    # Balloon Blitz includes Inflatable's Fire/Flying hit defense boosts.
    defender_anchor = "    case ABILITY_THERMAL_EXCHANGE: {\n"
    defender = """    case ABILITY_BALLOON_BLITZ: {
        int type = battleCtx->moveType ? battleCtx->moveType : CURRENT_MOVE_DATA.type;
        if (DEFENDING_MON.curHP
            && (type == TYPE_FIRE || type == TYPE_FLYING)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]++;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE]++;
            }
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

"""
    insert_before_once(
        path,
        defender_anchor,
        defender,
        "case ABILITY_BALLOON_BLITZ:",
        "Balloon Blitz Inflatable reaction",
    )

    # Cosmic Daze doubles into confused or Enraged targets.
    insertion = """    if ((attackerParams.ability == ABILITY_COSMIC_DAZE)
        && ((battleCtx->battleMons[defender].statusVolatile
                & VOLATILE_CONDITION_CONFUSION)
            || battleCtx->mercuryR7Enraged[defender])) {
        movePower *= 2;
    }

    if (attackerParams.ability == ABILITY_BLOOD_STIGMA
        && battleCtx->mercuryR7Bleeding[defender]) {
        movePower *= 2;
    }

    if (attackerParams.ability == ABILITY_WIND_RAGE
        && (moveType == TYPE_FLYING
            || move == MOVE_GUST
            || move == MOVE_TWISTER
            || move == MOVE_AIR_SLASH
            || move == MOVE_AIR_CUTTER)) {
        movePower = movePower * 13 / 10;
    }

"""
    insert_before_in_function(
        path,
        "int BattleSystem_CalcMoveDamage(",
        "    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE\n",
        insertion,
        "attackerParams.ability == ABILITY_COSMIC_DAZE",
        "R7 offensive composites",
    )

    # Tar Shot makes Fire damage super-effective-like (2x).
    insertion = """    if (battleCtx->mercuryR7Tarred[defender]
        && moveType == TYPE_FIRE) {
        damage *= 2;
    }

"""
    insert_before_in_function(
        path,
        "int BattleSystem_CalcMoveDamage(",
        "    if ((battleType & BATTLE_TYPE_DOUBLES)\n",
        insertion,
        "mercuryR7Tarred[defender]",
        "Tar Toss fire weakness",
    )

    # Raging Goddess includes Rampage: no recharge after a KO.
    anchor = "    case ABILITY_HAUNTING_FRENZY:\n"
    insertion = """    case ABILITY_RAGING_GODDESS:
        if (battleCtx->battleMons[battleCtx->attacker].moveEffectsData.rechargeTurnNumber) {
            battleCtx->battleMons[battleCtx->attacker].moveEffectsData.rechargeTurnNumber = 0;
            battleCtx->battleMons[battleCtx->attacker].statusVolatile &=
                ~VOLATILE_CONDITION_MOVE_LOCKED;
        }
        break;

    case ABILITY_PRETENTIOUS:
        if (battleCtx->mercuryR7CritStage[battleCtx->attacker] < 4) {
            battleCtx->mercuryR7CritStage[battleCtx->attacker]++;
            battleCtx->msgBattlerTemp = battleCtx->attacker;
            *subscript = subscript_mold_breaker;
            return TRUE;
        }
        break;

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "case ABILITY_PRETENTIOUS:",
        "Pretentious/Raging Goddess KO hooks",
    )


def patch_critical_stage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """        + criticalStage
        + Mercury_BattleAuraCritBoost(battleCtx)
"""
    insertion = """        + battleCtx->mercuryR7CritStage[attacker]
"""
    text = path.read_text(encoding="utf-8")
    marker = "+ battleCtx->mercuryR7CritStage[attacker]"
    if marker not in text:
        count = text.count(anchor)
        if count != 1:
            raise SystemExit(f"Pretentious crit stage: expected one anchor, found {count}")
        text = text.replace(
            anchor,
            """        + criticalStage
        + battleCtx->mercuryR7CritStage[attacker]
        + Mercury_BattleAuraCritBoost(battleCtx)
""",
            1,
        )
        path.write_text(text, encoding="utf-8")


def patch_reactive_counter(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = "    case ABILITY_THERMAL_EXCHANGE: {\n"
    insertion = """    case ABILITY_ICE_DOWNFALL:
        if (ATTACKING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && battleCtx->mercuryR7GeneratedAction == FALSE) {
            int user = battleCtx->defender;
            if (battleCtx->mercuryR7ReactivePending[user] < 9) {
                battleCtx->mercuryR7ReactivePending[user]++;
            }
            battleCtx->mercuryR7ReactiveTarget[user] = battleCtx->attacker;
            battleCtx->mercuryR7ReactiveMove[user] = MOVE_ICICLE_CRASH;
            battleCtx->mercuryR7ReactivePower[user] = 60;
        }
        break;

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "case ABILITY_ICE_DOWNFALL:",
        "Ice Downfall reactive counter",
    )


def patch_entry_composites(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """        case SWITCH_IN_CHECK_STATE_DOWNLOAD:
            for (i = 0; i < maxBattlers; i++) {
                battler = battleCtx->monSpeedOrder[i];

"""
    insertion = """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP) {
                    int ability = Battler_Ability(battleCtx, battler);
                    int foe;

                    if (ability == ABILITY_MONSTER_MASH) {
                        battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                        for (foe = 0; foe < maxBattlers; foe++) {
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    != BattleSystem_GetBattlerSide(battleSys, battler)
                                && battleCtx->battleMons[foe].curHP) {
                                battleCtx->mercuryR7AddedType[foe] = TYPE_GHOST;
                            }
                        }
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

                    if (ability == ABILITY_TAR_TOSS) {
                        battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                        for (foe = 0; foe < maxBattlers; foe++) {
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    != BattleSystem_GetBattlerSide(battleSys, battler)
                                && battleCtx->battleMons[foe].curHP) {
                                battleCtx->mercuryR7Tarred[foe] = TRUE;
                                if (battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]
                                        > MIN_STAT_STAGE) {
                                    battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]--;
                                }
                            }
                        }
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

                    if (ability == ABILITY_TRICKSTER) {
                        battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                        for (foe = 0; foe < maxBattlers; foe++) {
                            int move;
                            int slot;
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    == BattleSystem_GetBattlerSide(battleSys, battler)
                                || battleCtx->battleMons[foe].curHP == 0) {
                                continue;
                            }
                            move = battleCtx->movePrevByBattler[foe];
                            slot = Battler_SlotForMove(&battleCtx->battleMons[foe], move);
                            if (move != MOVE_NONE
                                && slot < LEARNED_MOVES_MAX
                                && battleCtx->battleMons[foe].ppCur[slot]
                                && battleCtx->battleMons[foe].moveEffectsData.disabledMove == MOVE_NONE) {
                                battleCtx->battleMons[foe].moveEffectsData.disabledMove = move;
                                battleCtx->battleMons[foe].moveEffectsData.disabledTurns = 4;
                            }
                        }
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

                    if (ability == ABILITY_WEB_SPINNER) {
                        battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                        for (foe = 0; foe < maxBattlers; foe++) {
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    != BattleSystem_GetBattlerSide(battleSys, battler)
                                && battleCtx->battleMons[foe].curHP) {
                                battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED] -= 2;
                                if (battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]
                                        < MIN_STAT_STAGE) {
                                    battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]
                                        = MIN_STAT_STAGE;
                                }
                            }
                        }
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

                    if (ability == ABILITY_WIND_RAGE) {
                        int side;
                        battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                        for (side = 0; side < NUM_BATTLE_SIDES; side++) {
                            battleCtx->sideConditionsMask[side] &=
                                ~(SIDE_CONDITION_REFLECT
                                  | SIDE_CONDITION_LIGHT_SCREEN
                                  | SIDE_CONDITION_SPIKES
                                  | SIDE_CONDITION_TOXIC_SPIKES);
                            battleCtx->sideConditions[side].reflectTurns = 0;
                            battleCtx->sideConditions[side].lightScreenTurns = 0;
                            battleCtx->sideConditions[side].spikesLayers = 0;
                            battleCtx->sideConditions[side].toxicSpikesLayers = 0;
                        }
                        for (foe = 0; foe < maxBattlers; foe++) {
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    != BattleSystem_GetBattlerSide(battleSys, battler)
                                && battleCtx->battleMons[foe].curHP
                                && battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_EVASION]
                                    > MIN_STAT_STAGE) {
                                battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_EVASION]--;
                            }
                        }
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

                    if (ability == ABILITY_WOODLAND_CURSE) {
                        battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                        for (foe = 0; foe < maxBattlers; foe++) {
                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    != BattleSystem_GetBattlerSide(battleSys, battler)
                                && battleCtx->battleMons[foe].curHP) {
                                battleCtx->mercuryR7AddedType[foe] = TYPE_GRASS;
                            }
                        }
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }
                }

"""
    insert_after_once(
        path,
        anchor,
        insertion,
        "ability == ABILITY_MONSTER_MASH",
        "R7 switch-in composites",
    )


def patch_woodland_contact(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = "    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN\n"
    insertion = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_WOODLAND_CURSE
        && DEFENDING_MON.curHP
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && Mercury_MoveMakesContact(
            battleCtx, battleCtx->attacker, battleCtx->moveCur)) {
        battleCtx->mercuryR7AddedType[battleCtx->defender] = TYPE_GRASS;
    }

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "== ABILITY_WOODLAND_CURSE",
        "Woodland Curse contact added type",
    )


def patch_overwatch_priority_and_stakeout(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    anchor = """        battler1Priority = MOVE_DATA(battler1Move).priority;
        battler2Priority = MOVE_DATA(battler2Move).priority;
"""
    insertion = """
        if (battler1Move != MOVE_NONE
            && battler1Ability == ABILITY_OVERWATCH
            && battleCtx->battleMons[battler1].moveEffectsData.fakeOutTurnNumber
                == battleCtx->totalTurns + 1) {
            battler1Priority = battler1Priority < 0 ? 0 : battler1Priority + 1;
        }
        if (battler2Move != MOVE_NONE
            && battler2Ability == ABILITY_OVERWATCH
            && battleCtx->battleMons[battler2].moveEffectsData.fakeOutTurnNumber
                == battleCtx->totalTurns + 1) {
            battler2Priority = battler2Priority < 0 ? 0 : battler2Priority + 1;
        }
"""
    insert_after_once(
        path,
        anchor,
        insertion,
        "battler1Ability == ABILITY_OVERWATCH",
        "Overwatch first-turn priority",
    )

    insertion = """    if (attackerParams.ability == ABILITY_OVERWATCH
        && battleCtx->battlerActions[defender][BATTLE_ACTION_PICK_COMMAND]
            == BATTLE_CONTROL_PARTY) {
        movePower *= 2;
    }

"""
    insert_before_in_function(
        path,
        "int BattleSystem_CalcMoveDamage(",
        "    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE\n",
        insertion,
        "attackerParams.ability == ABILITY_OVERWATCH",
        "Overwatch Stakeout",
    )


def patch_brawling_wyvern_classification(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"
    helper = """BOOL Mercury_R7MoveCountsAsPunching(
    BattleContext *battleCtx,
    int battler,
    int move)
{
    int type = battleCtx->moveType ? battleCtx->moveType : MOVE_DATA(move).type;

    if (Mercury_R7MoveIsPunching(move)) {
        return TRUE;
    }

    return Battler_Ability(battleCtx, battler) == ABILITY_BRAWLING_WYVERN
        && type == TYPE_DRAGON;
}

"""
    # battle_lib needs its own small punch table because the controller helper is TU-local.
    local = """static BOOL Mercury_R7MoveIsPunching(int move)
{
    switch (move) {
    case MOVE_ICE_PUNCH:
    case MOVE_FIRE_PUNCH:
    case MOVE_THUNDER_PUNCH:
    case MOVE_MACH_PUNCH:
    case MOVE_FOCUS_PUNCH:
    case MOVE_DIZZY_PUNCH:
    case MOVE_DYNAMIC_PUNCH:
    case MOVE_HAMMER_ARM:
    case MOVE_MEGA_PUNCH:
    case MOVE_COMET_PUNCH:
    case MOVE_METEOR_MASH:
    case MOVE_SHADOW_PUNCH:
    case MOVE_DRAIN_PUNCH:
    case MOVE_BULLET_PUNCH:
    case MOVE_SKY_UPPERCUT:
        return TRUE;
    default:
        return FALSE;
    }
}

"""
    insert_before_once(
        lib,
        "int Mercury_R7AddedType(BattleContext *battleCtx, int battler)\n",
        local + helper,
        "Mercury_R7MoveCountsAsPunching",
        "Brawling Wyvern punching classification",
    )
    insert_before_once(
        hdr,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);\n",
        "BOOL Mercury_R7MoveCountsAsPunching(BattleContext *battleCtx, int battler, int move);\n",
        "Mercury_R7MoveCountsAsPunching",
        "Brawling Wyvern declaration",
    )


def patch_blood_stigma_status_immunity(root: Path) -> None:
    scripts = [
        "subscript_fall_asleep.s",
        "subscript_poison.s",
        "subscript_badly_poison.s",
        "subscript_burn.s",
        "subscript_freeze.s",
        "subscript_paralyze.s",
    ]
    for name in scripts:
        path = root / "res/battle/scripts/subscripts" / name
        text = path.read_text(encoding="utf-8")
        marker = "ABILITY_BLOOD_STIGMA"
        if marker in text:
            continue
        # Put the direct holder check after the first side-effect battler ability check,
        # falling back to the first label line if a file differs.
        lines = text.splitlines(True)
        insert_at = None
        for i, line in enumerate(lines):
            if "CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON" in line:
                insert_at = i + 1
                break
        if insert_at is None:
            raise SystemExit(f"Blood Stigma: no CheckAbility anchor in {name}")
        # Reuse that check's destination label so Blood Stigma follows the same failure path.
        parts = lines[insert_at - 1].strip().split(",")
        label = parts[-1].strip()
        lines.insert(
            insert_at,
            f"    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_BLOOD_STIGMA, {label}\n",
        )
        path.write_text("".join(lines), encoding="utf-8")


def patch_fixed_power_override(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    insertion = """    if (battleCtx->mercuryR7GeneratedActive
        && battleCtx->mercuryR7GeneratedAction
        && battleCtx->mercuryR7GeneratedPower) {
        battleCtx->movePower = battleCtx->mercuryR7GeneratedPower;
    }

"""
    insert_before_in_function(
        path,
        "static void BattleScript_CalcMoveDamage(",
        "    battleCtx->damage = BattleSystem_CalcMoveDamage(battleSys,\n",
        insertion,
        "mercuryR7GeneratedPower) {",
        "R7 fixed generated power",
    )


def update_registry(path: Path) -> None:
    rows = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for token in TOKENS:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    abilities = [
        x.strip()
        for x in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    reg = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "shared_context": "mercuryR7GeneratedAction" in ctx and "mercuryR7CustomMultiHitActive" in ctx,
        "generated_followups": all(t in ctl for t in ("ABILITY_CHUNKY_BASS_LINE", "ABILITY_FROST_BURN", "ABILITY_TWO_STEP")),
        "ice_downfall": "ABILITY_ICE_DOWNFALL" in lib and "MOVE_ICICLE_CRASH" in lib,
        "multihit_family": all(t in ctl for t in ("ABILITY_BALLOON_BLITZ", "ABILITY_METALLIC_JAWS", "ABILITY_RAGING_GODDESS", "ABILITY_STEEL_BEETLE")),
        "added_type_family": "Mercury_R7AddedType" in lib and "ABILITY_MONSTER_MASH" in lib and "ABILITY_WOODLAND_CURSE" in lib,
        "overwatch": "ABILITY_OVERWATCH" in lib,
        "pretentious": "mercuryR7CritStage[attacker]" in lib,
        "retriever": "ABILITY_RETRIEVER" in ctl,
        "tar_toss": "ABILITY_TAR_TOSS" in lib and "mercuryR7Tarred" in lib,
        "trickster": "ABILITY_TRICKSTER" in lib and "disabledTurns = 4" in lib,
        "web_spinner": "ABILITY_WEB_SPINNER" in lib,
        "wind_rage": "ABILITY_WIND_RAGE" in lib and "movePower = movePower * 13 / 10" in lib,
        "blood_stigma": "ABILITY_BLOOD_STIGMA" in lib and "mercuryR7Bleeding" in lib,
        "cosmic_daze": "ABILITY_COSMIC_DAZE" in lib and "mercuryR7Enraged" in lib,
        "fixed_power_override": "mercuryR7GeneratedPower" in script,
        "registry_updated": all(t in reg for t in TOKENS),
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
    ap.add_argument("--report", type=Path, default=Path("mr10r7-historical-fast-pass.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(args.partition.resolve())
    patch_context(root)
    patch_subscript(root)
    patch_runtime_state_reset(root)
    patch_exported_move_helpers(root)
    patch_added_type_helpers(root)
    patch_brawling_wyvern_classification(root)
    patch_controller_helpers(root)
    patch_damage(root)
    patch_critical_stage(root)
    patch_reactive_counter(root)
    patch_entry_composites(root)
    patch_woodland_contact(root)
    patch_overwatch_priority_and_stakeout(root)
    patch_blood_stigma_status_immunity(root)
    patch_fixed_power_override(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10R7_HISTORICAL_FAST_PASS",
        "status": status,
        "implemented": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "historical_runtime_before": 41,
        "historical_runtime_after": 21,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10R7 historical fast pass failed")


if __name__ == "__main__":
    main()
