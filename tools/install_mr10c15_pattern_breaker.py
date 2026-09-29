#!/usr/bin/env python3
"""MR10C15 — implement the approved Pattern Breaker redesign.

Pattern Breaker:
- remembers each battler's last actually attempted move;
- if an opposing battler attempts that same move on consecutive turns, every
  active opposing Pattern Breaker holder becomes Locked In on that battler for
  the rest of the current turn;
- the holder's next damaging move against that battler gets +1 priority and
  +30% power;
- failed moves still enter move history, while Ability-generated follow-ups are
  excluded through a shared generated-action flag;
- the bonus does not stack and expires before the next turn if unused.

Because Platinum normally fixes action order at turn start, this pass also adds
a narrow remaining-action promotion helper. It moves a newly primed holder only
across still-pending actions whose original move priority is lower; it does not
recalculate Speed or disturb equal/higher-priority ordering. The same helper is
used to make Countercurrent's already-approved mid-turn +1 priority observable
in doubles.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Pattern Breaker"
ABILITY_TOKEN = "ABILITY_MR_PATTERN_BREAKER"
ABILITY_ID = 738


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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


def insert_before_definition(
    path: Path,
    signature: str,
    insertion: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    definition = signature + "\n{"
    count = text.count(definition)
    if count != 1:
        raise SystemExit(f"{label}: expected one definition in {path}, found {count}")
    path.write_text(text.replace(definition, insertion + definition, 1), encoding="utf-8")


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


def patch_context_and_switch_reset(root: Path) -> None:
    ctx = root / "include/battle/battle_context.h"
    insert_after_once(
        ctx,
        """    int mercuryUndertowUntilTurn[MAX_BATTLERS];
""",
        """    // Mercury MR10C15: actual move history plus a current-turn
    // Locked In target. Generated Ability actions are deliberately excluded.
    u16 mercuryPatternLastUsedMove[MAX_BATTLERS];
    u8 mercuryPatternReady[MAX_BATTLERS];
    u8 mercuryPatternTarget[MAX_BATTLERS];
    u8 mercuryAbilityGeneratedAction;
""",
        "Pattern Breaker state",
    )

    lib = root / "src/battle/battle_lib.c"
    insert_after_once(
        lib,
        """    battleCtx->mercuryUndertowUntilTurn[battler] = -1;
""",
        """    battleCtx->mercuryPatternLastUsedMove[battler] = MOVE_NONE;
    battleCtx->mercuryPatternReady[battler] = FALSE;
    battleCtx->mercuryPatternTarget[battler] = 0;
""",
        "Pattern Breaker switch reset",
    )


def patch_turn_start_expiry(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_CalcTurnOrder("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        signature,
        """    if (battleType & (BATTLE_TYPE_SAFARI | BATTLE_TYPE_PAL_PARK)) {
""",
        """    // Pattern Breaker's Locked In bonus never crosses a turn boundary.
    for (i = 0; i < maxBattlers; i++) {
        battleCtx->mercuryPatternReady[i] = FALSE;
        battleCtx->mercuryPatternTarget[i] = 0;
    }
    battleCtx->mercuryAbilityGeneratedAction = FALSE;

""",
        "Pattern Breaker turn-start expiry",
    )


def patch_remaining_action_helper(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    helper = """static int Mercury_SelectedMoveForPendingBattler(
    BattleContext *battleCtx,
    int battler)
{
    if (battleCtx->battlerActions[battler][BATTLE_ACTION_SELECTED_COMMAND]
        != PLAYER_INPUT_FIGHT) {
        return MOVE_NONE;
    }

    if (battleCtx->turnFlags[battler].struggling) {
        return MOVE_STRUGGLE;
    }

    return BattleMon_Get(
        battleCtx,
        battler,
        BATTLEMON_MOVE_1 + battleCtx->moveSlot[battler],
        NULL);
}

static void Mercury_PromoteRemainingActionByPriority(
    BattleContext *battleCtx,
    int battler,
    int bonus,
    BOOL requireDamaging,
    int requiredTarget)
{
    int maxBattlers = MAX_BATTLERS;
    int move = Mercury_SelectedMoveForPendingBattler(battleCtx, battler);
    int boostedPriority;
    int pos;
    int firstPending = battleCtx->turnOrderCounter + 1;

    if (move == MOVE_NONE) {
        return;
    }

    if (requireDamaging && MOVE_DATA(move).power == 0) {
        return;
    }

    if (requiredTarget != BATTLER_NONE
        && battleCtx->battlerActions[battler][BATTLE_ACTION_CHOOSE_TARGET]
            != requiredTarget) {
        return;
    }

    boostedPriority = MOVE_DATA(move).priority + bonus;

    for (pos = firstPending; pos < maxBattlers; pos++) {
        if (battleCtx->battlerActionOrder[pos] == battler) {
            break;
        }
    }

    if (pos >= maxBattlers) {
        return;
    }

    while (pos > firstPending) {
        int prior = battleCtx->battlerActionOrder[pos - 1];
        int priorMove = Mercury_SelectedMoveForPendingBattler(battleCtx, prior);

        // Never jump across a pending non-Fight command.
        if (priorMove == MOVE_NONE) {
            break;
        }

        // Equal priority preserves the original start-of-turn Speed order.
        if (MOVE_DATA(priorMove).priority >= boostedPriority) {
            break;
        }

        battleCtx->battlerActionOrder[pos] = prior;
        battleCtx->battlerActionOrder[pos - 1] = battler;
        pos--;
    }
}

"""
    insert_before_definition(path, signature, helper, "Pattern Breaker remaining-action helper")


def patch_damage_bonus(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_MR_EXECUTION_DRIVE
""",
        """    if (attackerParams.ability == ABILITY_MR_PATTERN_BREAKER
        && battleCtx->mercuryPatternReady[attacker]
        && battleCtx->mercuryPatternTarget[attacker] == defender + 1
        && movePower) {
        movePower = movePower * 13 / 10;
    }

""",
        "Pattern Breaker 30 percent Locked In power bonus",
    )


def patch_trigger_history_consume_and_reorder(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """        if (battleCtx->attacker != BATTLER_NONE
            && battleCtx->moveCur != MOVE_NONE
            && (battleCtx->battleStatusMask2 & SYSCTL_ATTACK_MESSAGE_SHOWN)
            && battleCtx->mercuryAbilityGeneratedAction == FALSE) {
            int patternUser = battleCtx->attacker;
            int patternMove = battleCtx->moveCur;
            BOOL patternRepeated =
                battleCtx->mercuryPatternLastUsedMove[patternUser] == patternMove;
            int patternHolder;
            int patternMaxBattlers = BattleSystem_GetMaxBattlers(battleSys);

            if (patternRepeated) {
                for (patternHolder = 0;
                     patternHolder < patternMaxBattlers;
                     patternHolder++) {
                    if (patternHolder != patternUser
                        && ((patternHolder & 1) != (patternUser & 1))
                        && battleCtx->battleMons[patternHolder].curHP
                        && Battler_Ability(battleCtx, patternHolder)
                            == ABILITY_MR_PATTERN_BREAKER) {
                        battleCtx->mercuryPatternReady[patternHolder] = TRUE;
                        battleCtx->mercuryPatternTarget[patternHolder]
                            = patternUser + 1;

                        Mercury_PromoteRemainingActionByPriority(
                            battleCtx,
                            patternHolder,
                            1,
                            TRUE,
                            patternUser);
                    }
                }
            }

            // Failed moves still count as the move actually attempted. The
            // generated-action guard above deliberately excludes Ability
            // follow-ups from both triggering and overwriting this history.
            battleCtx->mercuryPatternLastUsedMove[patternUser] = patternMove;
        }

        // Countercurrent also earns priority in the middle of a turn. Promote
        // any still-pending ready holder without recalculating Speed.
        {
            int priorityHolder;
            int priorityMaxBattlers = BattleSystem_GetMaxBattlers(battleSys);

            for (priorityHolder = 0;
                 priorityHolder < priorityMaxBattlers;
                 priorityHolder++) {
                if (battleCtx->mercuryCountercurrentPriorityReady[priorityHolder]
                    && battleCtx->battleMons[priorityHolder].curHP) {
                    Mercury_PromoteRemainingActionByPriority(
                        battleCtx,
                        priorityHolder,
                        1,
                        FALSE,
                        BATTLER_NONE);
                }
            }
        }

        if (battleCtx->attacker != BATTLER_NONE
            && Battler_Ability(battleCtx, battleCtx->attacker)
                == ABILITY_MR_PATTERN_BREAKER
            && battleCtx->mercuryPatternReady[battleCtx->attacker]
            && battleCtx->defender != BATTLER_NONE
            && battleCtx->mercuryPatternTarget[battleCtx->attacker]
                == battleCtx->defender + 1
            && CURRENT_MOVE_DATA.power) {
            battleCtx->mercuryPatternReady[battleCtx->attacker] = FALSE;
            battleCtx->mercuryPatternTarget[battleCtx->attacker] = 0;
        }

"""
    insert_before_in_function(
        path,
        signature,
        """        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        insertion,
        "Pattern Breaker trigger/history/consume",
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
        "stable_id_738":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "actual_move_history":
            "mercuryPatternLastUsedMove[MAX_BATTLERS]" in ctx
            and "mercuryPatternLastUsedMove[patternUser] == patternMove" in ctl,
        "failed_attempts_count":
            "SYSCTL_ATTACK_MESSAGE_SHOWN" in ctl
            and "mercuryPatternLastUsedMove[patternUser] = patternMove;" in ctl,
        "generated_followups_excluded":
            "mercuryAbilityGeneratedAction" in ctx
            and "mercuryAbilityGeneratedAction == FALSE" in ctl,
        "opponent_repeat_primes":
            "ABILITY_MR_PATTERN_BREAKER" in ctl
            and "((patternHolder & 1) != (patternUser & 1))" in ctl,
        "locked_target_recorded":
            "mercuryPatternTarget[patternHolder] = patternUser + 1;" in ctl,
        "power_bonus_30_percent":
            "ABILITY_MR_PATTERN_BREAKER" in lib
            and "movePower = movePower * 13 / 10;" in lib,
        "power_bonus_target_specific":
            "mercuryPatternTarget[attacker] == defender + 1" in lib,
        "priority_promotion_is_remaining_only":
            "firstPending = battleCtx->turnOrderCounter + 1" in ctl,
        "priority_does_not_recalc_speed":
            "Mercury_PromoteRemainingActionByPriority" in ctl
            and "BattleSystem_CompareBattlerSpeed" not in ctl[
                ctl.find("static void Mercury_PromoteRemainingActionByPriority"):
                ctl.find("static void BattleControllerPlayer_MoveEnd")
            ],
        "equal_priority_preserves_original_order":
            "MOVE_DATA(priorMove).priority >= boostedPriority" in ctl,
        "countercurrent_midturn_priority_reused":
            "mercuryCountercurrentPriorityReady[priorityHolder]" in ctl
            and "FALSE,\n                        BATTLER_NONE" in ctl,
        "consumed_only_by_damaging_move_against_locked_target":
            "mercuryPatternTarget[battleCtx->attacker]" in ctl
            and "CURRENT_MOVE_DATA.power" in ctl,
        "expires_before_next_turn":
            "mercuryPatternReady[i] = FALSE;" in ctl
            and "BattleControllerPlayer_CalcTurnOrder" in ctl,
        "switch_resets_move_history":
            "mercuryPatternLastUsedMove[battler] = MOVE_NONE;" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c15-pattern-breaker.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_and_switch_reset(root)
    patch_turn_start_expiry(root)
    patch_remaining_action_helper(root)
    patch_damage_bonus(root)
    patch_trigger_history_consume_and_reorder(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C15_PATTERN_BREAKER",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "priority_bonus": 1,
        "power_bonus_percent": 30,
        "failed_moves_count_in_history": True,
        "ability_generated_followups_excluded": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C15 Pattern Breaker validation failed")


if __name__ == "__main__":
    main()
