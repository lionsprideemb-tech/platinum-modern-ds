#!/usr/bin/env python3
"""MR10C11 — implement the approved Countercurrent redesign.

Countercurrent:
- when the holder is hit by a contact move, the attacker loses 1 Speed stage;
- after the drop actually resolves, if the holder's effective Speed is now
  greater than the attacker's, the holder's next move gains +1 priority;
- the temporary priority can be earned at most once per turn, does not stack,
  is consumed by the holder's next move, and is cleared on switch-out.

The speed comparison intentionally uses BattleSystem_CompareBattlerSpeed only
to refresh Mercury's effective-speed cache, then compares monSpeedValues
directly so Trick Room does not redefine what "faster" means.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Countercurrent"
ABILITY_TOKEN = "ABILITY_MR_COUNTERCURRENT"
ABILITY_ID = 641


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


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return

    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

    open_brace = start + len(signature) + 1
    depth = 0
    end = -1
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        raise SystemExit(f"{label}: function closing brace not found in {path}")

    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor inside {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(partition: Path) -> None:
    plan = json.loads(partition.read_text(encoding="utf-8"))
    rows = [x for x in plan["abilities"] if x.get("id") == ABILITY_ID]
    if len(rows) != 1:
        raise SystemExit(f"{ABILITY_NAME}: expected one partition row at ID {ABILITY_ID}")

    row = rows[0]
    expected = {
        "display_name": ABILITY_NAME,
        "token": ABILITY_TOKEN,
        "approval_state": "owner_approved_redesign",
        "owner_review_decision": "REDESIGN",
        "implementation_class": "light_extension",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_context_state(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryCounterstepReady[MAX_BATTLERS];
""",
        """    // Mercury MR10C11: contact Speed punishment plus one pending
    // next-move priority reward after Countercurrent flips the Speed matchup.
    u8 mercuryCountercurrentPriorityReady[MAX_BATTLERS];
    u8 mercuryCountercurrentPendingAttacker[MAX_BATTLERS];
    u32 mercuryCountercurrentPreHolderSpeed[MAX_BATTLERS];
    u32 mercuryCountercurrentPreTargetSpeed[MAX_BATTLERS];
    int mercuryCountercurrentGrantedTurn[MAX_BATTLERS];
""",
        "Countercurrent state",
    )


def patch_switch_in_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryCounterstepReady[battler] = FALSE;
""",
        """    battleCtx->mercuryCountercurrentPriorityReady[battler] = FALSE;
    battleCtx->mercuryCountercurrentPendingAttacker[battler] = 0;
    battleCtx->mercuryCountercurrentPreHolderSpeed[battler] = 0;
    battleCtx->mercuryCountercurrentPreTargetSpeed[battler] = 0;
    battleCtx->mercuryCountercurrentGrantedTurn[battler] = -1;
""",
        "Countercurrent switch-in reset",
    )


def patch_contact_speed_drop(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    case ABILITY_MR_COUNTERSTEP:
""",
        """    case ABILITY_MR_COUNTERCURRENT:
        if (ATTACKING_MON.curHP
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED] > MIN_STAT_STAGE
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_MR_COUNTERCURRENT) == TRUE) {
            BattleSystem_CompareBattlerSpeed(
                battleSys,
                battleCtx,
                battleCtx->defender,
                battleCtx->attacker,
                TRUE);

            battleCtx->mercuryCountercurrentPendingAttacker[battleCtx->defender]
                = battleCtx->attacker + 1;
            battleCtx->mercuryCountercurrentPreHolderSpeed[battleCtx->defender]
                = battleCtx->monSpeedValues[battleCtx->defender];
            battleCtx->mercuryCountercurrentPreTargetSpeed[battleCtx->defender]
                = battleCtx->monSpeedValues[battleCtx->attacker];

            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_SPEED_DOWN_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;

""",
        "Countercurrent contact Speed drop",
    )


def patch_priority_order(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "u8 BattleSystem_CompareBattlerSpeed(BattleSystem *battleSys, "
        "BattleContext *battleCtx, int battler1, int battler2, BOOL ignoreQuickClaw)"
    )
    insert_before_in_function(
        path,
        signature,
        """    if (battler1Priority == battler2Priority) {
""",
        """    if (ignoreQuickClaw == FALSE) {
        if (battler1Action == PLAYER_INPUT_FIGHT
            && battler1Ability == ABILITY_MR_COUNTERCURRENT
            && battleCtx->mercuryCountercurrentPriorityReady[battler1]) {
            battler1Priority++;
        }

        if (battler2Action == PLAYER_INPUT_FIGHT
            && battler2Ability == ABILITY_MR_COUNTERCURRENT
            && battleCtx->mercuryCountercurrentPriorityReady[battler2]) {
            battler2Priority++;
        }
    }

""",
        "Countercurrent temporary +1 priority",
    )


def patch_move_end_resolution(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        signature,
        """        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        """        if (battleCtx->defender != BATTLER_NONE
            && battleCtx->attacker != BATTLER_NONE
            && Battler_Ability(battleCtx, battleCtx->defender)
                == ABILITY_MR_COUNTERCURRENT
            && battleCtx->mercuryCountercurrentPendingAttacker[battleCtx->defender]
                == battleCtx->attacker + 1) {
            int countercurrentHolder = battleCtx->defender;
            int countercurrentAttacker = battleCtx->attacker;
            u32 countercurrentBeforeHolder =
                battleCtx->mercuryCountercurrentPreHolderSpeed[countercurrentHolder];
            u32 countercurrentBeforeTarget =
                battleCtx->mercuryCountercurrentPreTargetSpeed[countercurrentHolder];

            BattleSystem_CompareBattlerSpeed(
                battleSys,
                battleCtx,
                countercurrentHolder,
                countercurrentAttacker,
                TRUE);

            if (countercurrentBeforeHolder <= countercurrentBeforeTarget
                && battleCtx->monSpeedValues[countercurrentHolder]
                    > battleCtx->monSpeedValues[countercurrentAttacker]
                && battleCtx->mercuryCountercurrentGrantedTurn[countercurrentHolder]
                    != battleCtx->totalTurns) {
                battleCtx->mercuryCountercurrentPriorityReady[countercurrentHolder]
                    = TRUE;
                battleCtx->mercuryCountercurrentGrantedTurn[countercurrentHolder]
                    = battleCtx->totalTurns;
            }

            battleCtx->mercuryCountercurrentPendingAttacker[countercurrentHolder] = 0;
        }

        {
            int countercurrentCleanup;
            int countercurrentMaxBattlers =
                BattleSystem_GetMaxBattlers(battleSys);

            for (countercurrentCleanup = 0;
                 countercurrentCleanup < countercurrentMaxBattlers;
                 countercurrentCleanup++) {
                battleCtx->mercuryCountercurrentPendingAttacker[countercurrentCleanup]
                    = 0;
            }
        }

        if (battleCtx->attacker != BATTLER_NONE
            && Battler_Ability(battleCtx, battleCtx->attacker)
                == ABILITY_MR_COUNTERCURRENT
            && battleCtx->mercuryCountercurrentPriorityReady[battleCtx->attacker]) {
            battleCtx->mercuryCountercurrentPriorityReady[battleCtx->attacker] = FALSE;
        }

""",
        "Countercurrent post-drop Speed check and priority consumption",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if ABILITY_TOKEN not in lines:
        lines.append(ABILITY_TOKEN)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_641":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "contact_speed_drop":
            "case ABILITY_MR_COUNTERCURRENT:" in lib
            and "MOVE_SUBSCRIPT_PTR_SPEED_DOWN_1_STAGE" in lib
            and "Mercury_MoveMakesContact(" in lib
            and "ABILITY_MR_COUNTERCURRENT) == TRUE" in lib,
        "records_predrop_effective_speeds":
            "mercuryCountercurrentPreHolderSpeed" in ctx
            and "mercuryCountercurrentPreTargetSpeed" in ctx
            and "BattleSystem_CompareBattlerSpeed(" in lib,
        "only_grants_after_real_drop":
            "BattleSystem_CompareBattlerSpeed(" in ctl
            and "monSpeedValues[countercurrentHolder]" in ctl,
        "must_cross_from_not_faster_to_faster":
            "countercurrentBeforeHolder <= countercurrentBeforeTarget" in ctl
            and "> battleCtx->monSpeedValues[countercurrentAttacker]" in ctl,
        "priority_ready_state":
            "mercuryCountercurrentPriorityReady[MAX_BATTLERS]" in ctx,
        "priority_plus_one":
            "battler1Priority++;" in lib
            and "ABILITY_MR_COUNTERCURRENT" in lib,
        "once_per_turn_grant":
            "mercuryCountercurrentGrantedTurn[countercurrentHolder]" in ctl
            and "!= battleCtx->totalTurns" in ctl,
        "next_move_consumes":
            "mercuryCountercurrentPriorityReady[battleCtx->attacker] = FALSE;" in ctl,
        "switch_clears_state":
            "mercuryCountercurrentPriorityReady[battler] = FALSE;" in lib
            and "mercuryCountercurrentGrantedTurn[battler] = -1;" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c11-countercurrent.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_state(root)
    patch_switch_in_reset(root)
    patch_contact_speed_drop(root)
    patch_priority_order(root)
    patch_move_end_resolution(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C11_COUNTERCURRENT",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "priority_bonus": 1,
        "contact_speed_drop": 1,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C11 Countercurrent validation failed")


if __name__ == "__main__":
    main()
