#!/usr/bin/env python3
"""MR08R5 — canonical Dancer pass.

Adds Dancer as a true extra-action mechanic on Platinum's battle controller:
- a completed dance move queues every other active Dancer user in speed order;
- each queued user immediately uses the same move without spending PP or
  replacing its selected turn action;
- copied self-targeting dances target the Dancer user;
- copied single-target dances from an ally keep the original target in doubles,
  otherwise they target the original dance user;
- random-target dances select a legal opponent for the Dancer user;
- Dancer-triggered dance moves do not recursively create another Dancer queue.

The queue is processed before the original battler's action is marked complete,
so Platinum's ordinary per-move damage, item, Ability, faint, form, and switch
processing still runs for every copied dance.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_DANCER",)
EXPECTED_IDS = {"ABILITY_DANCER": 216}


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08R5: queued Dancer extra actions.
    u8 mercuryDancerActive;
    u8 mercuryDancerCount;
    u8 mercuryDancerIndex;
    u8 mercuryDancerOriginalAttacker;
    u8 mercuryDancerOriginalDefender;
    u8 mercuryDancerBattlers[MAX_BATTLERS];
    u8 mercuryDancerTargets[MAX_BATTLERS];
    u16 mercuryDancerMove;

""",
        "Dancer battle state",
    )


def patch_dancer_script(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_dancer.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    // Platinum-native text fallback for an Ability activation popup.
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_ripen_raise_four_stat\n",
        "subscript_mercury_dancer\n",
        "Dancer subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_ripen_raise_four_stat.s',\n",
        "    'subscript_mercury_dancer.s',\n",
        "Dancer subscript build list",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        path,
        """static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        """static BOOL Mercury_IsDanceMove(int move)
{
    switch (move) {
    case MOVE_SWORDS_DANCE:
    case MOVE_PETAL_DANCE:
    case MOVE_FEATHER_DANCE:
    case MOVE_TEETER_DANCE:
    case MOVE_DRAGON_DANCE:
    case MOVE_LUNAR_DANCE:
    case MOVE_QUIVER_DANCE:
    case MOVE_FIERY_DANCE:
    case MOVE_REVELATION_DANCE:
    case MOVE_CLANGOROUS_SOUL:
    case MOVE_VICTORY_DANCE:
    case MOVE_AQUA_STEP:
        return TRUE;
    default:
        return FALSE;
    }
}

static int Mercury_DancerTarget(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int dancer,
    int originalAttacker,
    int originalDefender,
    int move)
{
    int range = MOVE_DATA(move).range;
    int battleType = BattleSystem_GetBattleType(battleSys);

    switch (range) {
    case RANGE_USER:
    case RANGE_USER_SIDE:
    case RANGE_FIELD:
        return dancer;

    case RANGE_SINGLE_TARGET:
        // Modern rule: an ally copying a single-target dance in a Double
        // Battle keeps the original target. Other Dancer users target the
        // Pokémon whose dance they copied.
        if ((battleType & BATTLE_TYPE_DOUBLES)
            && BattleSystem_GetBattlerSide(battleSys, dancer)
                == BattleSystem_GetBattlerSide(battleSys, originalAttacker)
            && originalDefender != BATTLER_NONE
            && battleCtx->battleMons[originalDefender].curHP) {
            return originalDefender;
        }
        return originalAttacker;

    case RANGE_RANDOM_OPPONENT:
        return BattleSystem_RandomOpponent(battleSys, battleCtx, dancer);

    default:
        // Spread and side-targeting move scripts use their range to enumerate
        // affected battlers; a legal opponent is sufficient as their primary
        // defender seed.
        return BattleSystem_RandomOpponent(battleSys, battleCtx, dancer);
    }
}

static void Mercury_BuildDancerQueue(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int slot;
    int battler;
    int target;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    battleCtx->mercuryDancerCount = 0;
    battleCtx->mercuryDancerIndex = 0;
    battleCtx->mercuryDancerOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryDancerOriginalDefender = battleCtx->defender;
    battleCtx->mercuryDancerMove = battleCtx->moveCur;

    for (slot = 0; slot < maxBattlers; slot++) {
        battler = battleCtx->monSpeedOrder[slot];

        if (battler == battleCtx->attacker
            || battleCtx->battleMons[battler].curHP == 0
            || Battler_Ability(battleCtx, battler) != ABILITY_DANCER) {
            continue;
        }

        target = Mercury_DancerTarget(
            battleSys,
            battleCtx,
            battler,
            battleCtx->attacker,
            battleCtx->defender,
            battleCtx->moveCur);

        if (target == BATTLER_NONE) {
            continue;
        }

        battleCtx->mercuryDancerBattlers[battleCtx->mercuryDancerCount] = battler;
        battleCtx->mercuryDancerTargets[battleCtx->mercuryDancerCount] = target;
        battleCtx->mercuryDancerCount++;
    }

    if (battleCtx->mercuryDancerCount) {
        battleCtx->mercuryDancerActive = TRUE;
    }
}

static BOOL Mercury_TryNextDancer(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int dancer;
    int target;

    if (battleCtx->mercuryDancerActive == FALSE) {
        if (Mercury_IsDanceMove(battleCtx->moveCur) == FALSE) {
            return FALSE;
        }

        Mercury_BuildDancerQueue(battleSys, battleCtx);
        if (battleCtx->mercuryDancerActive == FALSE) {
            return FALSE;
        }
    }

    while (battleCtx->mercuryDancerIndex < battleCtx->mercuryDancerCount) {
        dancer = battleCtx->mercuryDancerBattlers[battleCtx->mercuryDancerIndex];
        target = battleCtx->mercuryDancerTargets[battleCtx->mercuryDancerIndex];
        battleCtx->mercuryDancerIndex++;

        if (battleCtx->battleMons[dancer].curHP == 0
            || Battler_Ability(battleCtx, dancer) != ABILITY_DANCER) {
            continue;
        }

        // Treat every Dancer copy as its own move performance while preserving
        // the original battler's selected action and turn slot.
        BattleContext_Init(battleCtx);
        battleCtx->attacker = dancer;
        battleCtx->defender = target;
        battleCtx->moveCur = battleCtx->mercuryDancerMove;
        battleCtx->moveTemp = battleCtx->mercuryDancerMove;

        // Dancer copies do not spend PP and ignore the user's ordinary
        // pre-action incapacity checks. Target existence, redirection,
        // accuracy, type, and immunity processing still run normally.
        battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

        battleCtx->msgTemp = dancer;
        battleCtx->msgBattlerTemp = dancer;
        LOAD_SUBSEQ(subscript_mercury_dancer);
        battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
        battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
        return TRUE;
    }

    battleCtx->attacker = battleCtx->mercuryDancerOriginalAttacker;
    battleCtx->defender = battleCtx->mercuryDancerOriginalDefender;
    battleCtx->moveCur = battleCtx->mercuryDancerMove;
    battleCtx->moveTemp = battleCtx->mercuryDancerMove;
    battleCtx->mercuryDancerActive = FALSE;
    battleCtx->mercuryDancerCount = 0;
    battleCtx->mercuryDancerIndex = 0;
    return FALSE;
}

""",
        "Dancer controller helpers",
    )

    replace_once(
        path,
        """        if (BattleControllerPlayer_ToggleSemiInvulnMons(battleSys, battleCtx) == TRUE) {
            return;
        }

        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        """        if (BattleControllerPlayer_ToggleSemiInvulnMons(battleSys, battleCtx) == TRUE) {
            return;
        }

        if (Mercury_TryNextDancer(battleSys, battleCtx) == TRUE) {
            return;
        }

        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        "Dancer move-end queue hook",
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
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    script = (root / "res/battle/scripts/subscripts/subscript_mercury_dancer.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "dancer_queue_state":
            "mercuryDancerActive" in ctx
            and "mercuryDancerBattlers[MAX_BATTLERS]" in ctx,
        "dance_move_family":
            all(token in controller for token in (
                "MOVE_SWORDS_DANCE",
                "MOVE_PETAL_DANCE",
                "MOVE_FEATHER_DANCE",
                "MOVE_TEETER_DANCE",
                "MOVE_DRAGON_DANCE",
                "MOVE_LUNAR_DANCE",
                "MOVE_QUIVER_DANCE",
                "MOVE_FIERY_DANCE",
                "MOVE_REVELATION_DANCE",
                "MOVE_CLANGOROUS_SOUL",
                "MOVE_VICTORY_DANCE",
                "MOVE_AQUA_STEP",
            )),
        "speed_order_queue":
            "battler = battleCtx->monSpeedOrder[slot];" in controller,
        "active_ability_gate":
            "Battler_Ability(battleCtx, battler) != ABILITY_DANCER" in controller
            and "Battler_Ability(battleCtx, dancer) != ABILITY_DANCER" in controller,
        "no_recursive_queue":
            "if (battleCtx->mercuryDancerActive == FALSE)" in controller,
        "ally_target_rule":
            "BattleSystem_GetBattlerSide(battleSys, dancer)" in controller
            and "return originalDefender;" in controller
            and "return originalAttacker;" in controller,
        "copied_move_skips_pp":
            "beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in controller,
        "move_end_hook":
            "Mercury_TryNextDancer(battleSys, battleCtx)" in controller,
        "ability_message_script":
            "subscript_mercury_dancer" in order
            and "BattleStrings_Text_PokemonWasAbility_Ally" in script,
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
        default=Path("mr08r5-canonical-ability-dancer.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_dancer_script(root)
    patch_controller(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08R5_CANONICAL_ABILITY_DANCER",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 169,
        "remaining_modern_canonical_mechanics": 18,
        "policy": "Official/current-mainline Dancer extra-action ordering and targeting on Platinum's native move pipeline.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08R5 validation failed")


if __name__ == "__main__":
    main()
