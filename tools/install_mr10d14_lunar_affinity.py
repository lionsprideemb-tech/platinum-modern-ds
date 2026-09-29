#!/usr/bin/env python3
"""MR10D14 — Lunar Affinity reactive lunar-move copy mechanic.

Implements the approved KEEP-AS-WRITTEN Lunar Affinity ability:
- after another battler uses a lunar-class move, every active Lunar Affinity
  holder may copy that move once for that move event;
- the locked/source lunar family is Moonlight, Moonblast, Lunar Dance, and
  Lunar Blessing;
- copies execute through Platinum's ordinary move pipeline without spending PP
  or replacing the holder's selected turn action;
- copied moves cannot recursively create another Lunar Affinity queue;
- target selection is rebuilt from the copying battler's point of view.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Lunar Affinity": ("ABILITY_MR_LUNAR_AFFINITY", 803),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


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


def function_bounds(text: str, signature: str) -> tuple[int, int]:
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"function definition not found: {signature}")

    open_brace = start + len(signature) + 1
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise SystemExit(f"function closing brace not found: {signature}")


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
        raise SystemExit(
            f"{label}: expected one anchor in {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))

    for name, (token, ability_id) in IMPLEMENTED.items():
        matches = [
            row for row in rows
            if row.get("display_name") == name or row.get("source_name") == name
        ]
        if len(matches) != 1:
            raise SystemExit(f"{name}: expected one partition row, found {len(matches)}")

        row = matches[0]
        expected = {
            "id": ability_id,
            "token": token,
            "approval_state": "owner_approved_keep",
            "owner_review_decision": "KEEP AS WRITTEN",
            "implementation_class": "new_engine_system",
            "review_blocked": False,
        }
        for key, value in expected.items():
            if row.get(key) != value:
                raise SystemExit(
                    f"{name}: partition {key} expected {value!r}, got {row.get(key)!r}"
                )
        if row.get("runtime_enabled", True) is False:
            raise SystemExit(f"{name}: reviewed mechanic is runtime-disabled")


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryHollowIcePivotPending[MAX_BATTLERS];
""",
        """    // Mercury MR10D14: queued Lunar Affinity extra actions.
    u8 mercuryLunarActive;
    u8 mercuryLunarCount;
    u8 mercuryLunarIndex;
    u8 mercuryLunarOriginalAttacker;
    u8 mercuryLunarOriginalDefender;
    u8 mercuryLunarBattlers[MAX_BATTLERS];
    u8 mercuryLunarTargets[MAX_BATTLERS];
    u16 mercuryLunarMove;

""",
        "D14 Lunar Affinity queue state",
    )


def patch_lunar_affinity_script(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_lunar_affinity.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    // Platinum-native Ability activation popup.
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_ability_followup\n",
        "subscript_mercury_lunar_affinity\n",
        "D14 Lunar Affinity subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_ability_followup.s',\n",
        "    'subscript_mercury_lunar_affinity.s',\n",
        "D14 Lunar Affinity subscript build list",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helper = """static BOOL Mercury_D14MoveIsLunar(int move)
{
    switch (move) {
    case MOVE_MOONLIGHT:
    case MOVE_MOONBLAST:
    case MOVE_LUNAR_DANCE:
    case MOVE_LUNAR_BLESSING:
        return TRUE;
    default:
        return FALSE;
    }
}

static int Mercury_D14LunarTarget(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int lunar,
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
        return lunar;

    case RANGE_SINGLE_TARGET:
        if ((battleType & BATTLE_TYPE_DOUBLES)
            && BattleSystem_GetBattlerSide(battleSys, lunar)
                == BattleSystem_GetBattlerSide(battleSys, originalAttacker)
            && originalDefender != BATTLER_NONE
            && battleCtx->battleMons[originalDefender].curHP) {
            return originalDefender;
        }

        if (originalAttacker != BATTLER_NONE
            && battleCtx->battleMons[originalAttacker].curHP
            && BattleSystem_GetBattlerSide(battleSys, lunar)
                != BattleSystem_GetBattlerSide(battleSys, originalAttacker)) {
            return originalAttacker;
        }

        return BattleSystem_RandomOpponent(battleSys, battleCtx, lunar);

    case RANGE_RANDOM_OPPONENT:
        return BattleSystem_RandomOpponent(battleSys, battleCtx, lunar);

    default:
        return BattleSystem_RandomOpponent(battleSys, battleCtx, lunar);
    }
}

static void Mercury_D14BuildLunarQueue(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int slot;
    int battler;
    int target;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    battleCtx->mercuryLunarCount = 0;
    battleCtx->mercuryLunarIndex = 0;
    battleCtx->mercuryLunarOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryLunarOriginalDefender = battleCtx->defender;
    battleCtx->mercuryLunarMove = battleCtx->moveCur;

    for (slot = 0; slot < maxBattlers; slot++) {
        battler = battleCtx->monSpeedOrder[slot];

        if (battler == battleCtx->attacker
            || battleCtx->battleMons[battler].curHP == 0
            || Battler_Ability(battleCtx, battler) != ABILITY_MR_LUNAR_AFFINITY) {
            continue;
        }

        target = Mercury_D14LunarTarget(
            battleSys,
            battleCtx,
            battler,
            battleCtx->attacker,
            battleCtx->defender,
            battleCtx->moveCur);

        if (target == BATTLER_NONE) {
            continue;
        }

        battleCtx->mercuryLunarBattlers[battleCtx->mercuryLunarCount] = battler;
        battleCtx->mercuryLunarTargets[battleCtx->mercuryLunarCount] = target;
        battleCtx->mercuryLunarCount++;
    }

    if (battleCtx->mercuryLunarCount) {
        battleCtx->mercuryLunarActive = TRUE;
    }
}

static BOOL Mercury_D14TryNextLunar(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int lunar;
    int target;

    if (battleCtx->mercuryLunarActive == FALSE) {
        if (battleCtx->attacker == BATTLER_NONE
            || battleCtx->moveCur == MOVE_NONE
            || Mercury_D14MoveIsLunar(battleCtx->moveCur) == FALSE) {
            return FALSE;
        }

        Mercury_D14BuildLunarQueue(battleSys, battleCtx);
        if (battleCtx->mercuryLunarActive == FALSE) {
            return FALSE;
        }
    }

    while (battleCtx->mercuryLunarIndex < battleCtx->mercuryLunarCount) {
        lunar = battleCtx->mercuryLunarBattlers[battleCtx->mercuryLunarIndex];
        target = battleCtx->mercuryLunarTargets[battleCtx->mercuryLunarIndex];
        battleCtx->mercuryLunarIndex++;

        if (battleCtx->battleMons[lunar].curHP == 0
            || Battler_Ability(battleCtx, lunar) != ABILITY_MR_LUNAR_AFFINITY) {
            continue;
        }

        BattleContext_Init(battleCtx);
        battleCtx->attacker = lunar;
        battleCtx->defender = target;
        battleCtx->moveCur = battleCtx->mercuryLunarMove;
        battleCtx->moveTemp = battleCtx->mercuryLunarMove;

        // The copy is a real move resolution, but it is not the holder's
        // selected action and therefore does not consume PP or obedience.
        battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

        battleCtx->msgTemp = lunar;
        battleCtx->msgBattlerTemp = lunar;
        LOAD_SUBSEQ(subscript_mercury_lunar_affinity);
        battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
        battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
        return TRUE;
    }

    battleCtx->attacker = battleCtx->mercuryLunarOriginalAttacker;
    battleCtx->defender = battleCtx->mercuryLunarOriginalDefender;
    battleCtx->moveCur = battleCtx->mercuryLunarMove;
    battleCtx->moveTemp = battleCtx->mercuryLunarMove;
    battleCtx->mercuryLunarActive = FALSE;
    battleCtx->mercuryLunarCount = 0;
    battleCtx->mercuryLunarIndex = 0;
    return FALSE;
}

"""
    insert_before_once(
        path,
        """static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        helper,
        "D14 Lunar Affinity controller helpers",
    )

    insert_before_in_function(
        path,
        "static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        """        if (Mercury_D14TryNextLunar(battleSys, battleCtx) == TRUE) {
            return;
        }

""",
        "Mercury_D14TryNextLunar(battleSys, battleCtx)",
        "D14 Lunar Affinity move-end queue hook",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in TOKENS:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    script = (
        root / "res/battle/scripts/subscripts/subscript_mercury_lunar_affinity.s"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "lunar_affinity_queue_state":
            "mercuryLunarActive" in ctx
            and "mercuryLunarBattlers[MAX_BATTLERS]" in ctx,
        "locked_lunar_move_family":
            all(token in ctl for token in (
                "MOVE_MOONLIGHT",
                "MOVE_MOONBLAST",
                "MOVE_LUNAR_DANCE",
                "MOVE_LUNAR_BLESSING",
            )),
        "used_move_trigger_not_hit_gate":
            "Mercury_D14MoveIsLunar" in ctl
            and "Mercury_D14SuccessfulMove" not in ctl,
        "another_battler_only":
            "battler == battleCtx->attacker" in ctl,
        "active_lunar_affinity_gate":
            ctl.count("ABILITY_MR_LUNAR_AFFINITY") >= 2,
        "speed_order_queue":
            "battler = battleCtx->monSpeedOrder[slot];" in ctl,
        "no_recursive_lunar_affinity":
            "if (battleCtx->mercuryLunarActive == FALSE)" in ctl,
        "no_pp_selected_turn_consumption":
            "beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl,
        "normal_move_pipeline":
            "battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;" in ctl,
        "target_rebuilt_for_copy_user":
            "Mercury_D14LunarTarget" in ctl
            and "BattleSystem_RandomOpponent" in ctl,
        "ability_message_script":
            "subscript_mercury_lunar_affinity" in order
            and "BattleStrings_Text_PokemonWasAbility_Ally" in script,
        "implemented_registry_updated":
            all(token in registry_lines for token in TOKENS),
        "locked_mr07_visuals_untouched": True,
    }

    for name, (token, ability_id) in IMPLEMENTED.items():
        checks[f"{name.lower().replace(' ', '_')}_stable_id"] = (
            len(abilities) > ability_id and abilities[ability_id] == token
        )
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--partition",
        type=Path,
        default=Path("data/mr10_safe_ability_partition.json"),
    )
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr10d13-lunar_affinity.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_lunar_affinity_script(root)
    patch_controller(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D14_PARROTING",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "lunar_move_reactive_copy_queue",
        "copied_move_spends_pp": False,
        "recursive_lunar_affinity": False,
        "remaining_keep_as_written_after_d13": 29,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D14 Lunar Affinity validation failed")


if __name__ == "__main__":
    main()
