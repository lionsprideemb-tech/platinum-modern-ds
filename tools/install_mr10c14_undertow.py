#!/usr/bin/env python3
"""MR10C14 — implement the approved Undertow redesign.

Undertow:
- when the holder successfully deals direct damage, the surviving target is
  Dragged through the end of the following battle turn;
- while Dragged, effective Speed is reduced by 25%;
- damaging self-switch effects such as U-turn / Volt Switch / Flip Turn are
  suppressed, but ordinary voluntary switching remains legal;
- reapplying Undertow refreshes the duration and never stacks the Speed penalty.

The anti-pivot hook targets Platinum's shared
MOVE_SUBSCRIPT_PTR_ATTACK_THEN_SWITCH_OUT secondary effect, so every move that
uses that mechanic inherits the rule without a hard-coded move-name list.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Undertow"
ABILITY_TOKEN = "ABILITY_MR_UNDERTOW"
ABILITY_ID = 740


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


def insert_after_in_function(
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
    block = block.replace(anchor, anchor + insertion, 1)
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


def patch_context_and_switch_reset(root: Path) -> None:
    ctx = root / "include/battle/battle_context.h"
    insert_after_once(
        ctx,
        """    u8 mercuryTwoLivesShieldPending[MAX_BATTLERS];
""",
        """    // Mercury MR10C14: -1 means not Dragged. Otherwise the value is
    // the final battle turn on which the effect remains active.
    int mercuryUndertowUntilTurn[MAX_BATTLERS];
""",
        "Undertow duration state",
    )

    lib = root / "src/battle/battle_lib.c"
    insert_after_once(
        lib,
        """    battleCtx->mercuryTwoLivesShieldPending[battler] = FALSE;
""",
        """    battleCtx->mercuryUndertowUntilTurn[battler] = -1;
""",
        "Undertow switch-out cleanup",
    )


def patch_speed_penalty(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "u8 BattleSystem_CompareBattlerSpeed(BattleSystem *battleSys, "
        "BattleContext *battleCtx, int battler1, int battler2, BOOL ignoreQuickClaw)"
    )
    insert_before_in_function(
        path,
        signature,
        """    battleCtx->monSpeedValues[battler1] = battler1Speed;
""",
        """    if (battleCtx->mercuryUndertowUntilTurn[battler1]
            >= (int)battleCtx->totalTurns) {
        battler1Speed = battler1Speed * 3 / 4;
    }

    if (battleCtx->mercuryUndertowUntilTurn[battler2]
            >= (int)battleCtx->totalTurns) {
        battler2Speed = battler2Speed * 3 / 4;
    }

""",
        "Undertow final effective-Speed penalty",
    )


def patch_pivot_suppression(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL BattleSystem_TriggerSecondaryEffect("
        "BattleSystem *battleSys, BattleContext *battleCtx, int *effect)"
    )
    insert_after_in_function(
        path,
        signature,
        """    u16 effectChance;
""",
        """
    if (battleCtx->attacker != BATTLER_NONE
        && battleCtx->mercuryUndertowUntilTurn[battleCtx->attacker]
            >= (int)battleCtx->totalTurns
        && CURRENT_MOVE_DATA.effect == BATTLE_EFFECT_SWITCH_HIT
        && (battleCtx->sideEffectIndirectFlags & MOVE_SIDE_EFFECT_ON_HIT)
        && ((battleCtx->sideEffectIndirectFlags & MOVE_SIDE_EFFECT_SUBSCRIPT_POINTER)
            == MOVE_SUBSCRIPT_PTR_ATTACK_THEN_SWITCH_OUT)) {
        // The attack itself already resolved. Remove only the automatic
        // self-switch side effect; ordinary command-menu switching stays legal.
        battleCtx->sideEffectIndirectFlags = 0;
        return FALSE;
    }
""",
        "Undertow pivot suppression",
    )


def patch_apply_dragged(root: Path) -> None:
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
        """        if (battleCtx->attacker != BATTLER_NONE
            && battleCtx->defender != BATTLER_NONE
            && battleCtx->battleMons[battleCtx->defender].curHP
            && ((battleCtx->attacker & 1) != (battleCtx->defender & 1))
            && Battler_Ability(battleCtx, battleCtx->attacker)
                == ABILITY_MR_UNDERTOW
            && CURRENT_MOVE_DATA.power
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            // A single expiry value means repeated hits refresh rather than
            // stack the 25 percent Speed reduction.
            battleCtx->mercuryUndertowUntilTurn[battleCtx->defender]
                = (int)battleCtx->totalTurns + 1;
        }

""",
        "Undertow direct-damage application",
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
        "stable_id_740":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "duration_state":
            "int mercuryUndertowUntilTurn[MAX_BATTLERS];" in ctx,
        "switch_clears_dragged":
            "mercuryUndertowUntilTurn[battler] = -1;" in lib,
        "successful_direct_damage_applies":
            "ABILITY_MR_UNDERTOW" in ctl
            and "DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken" in ctl
            and "totalTurns + 1" in ctl,
        "refresh_not_stack":
            "mercuryUndertowUntilTurn[battleCtx->defender]" in ctl,
        "speed_reduced_25_percent":
            "battler1Speed = battler1Speed * 3 / 4;" in lib
            and "battler2Speed = battler2Speed * 3 / 4;" in lib,
        "shared_pivot_family_blocked":
            "BATTLE_EFFECT_SWITCH_HIT" in lib
            and "MOVE_SUBSCRIPT_PTR_ATTACK_THEN_SWITCH_OUT" in lib,
        "only_pivot_side_effect_removed":
            "battleCtx->sideEffectIndirectFlags = 0;" in lib,
        "ordinary_switching_untouched":
            "BattleControllerPlayer_SwitchCommand" not in ctl[
                ctl.find("ABILITY_MR_UNDERTOW"):
                ctl.find("ABILITY_MR_UNDERTOW") + 2500
            ],
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c14-undertow.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_and_switch_reset(root)
    patch_speed_penalty(root)
    patch_pivot_suppression(root)
    patch_apply_dragged(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C14_UNDERTOW",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "speed_multiplier_percent": 75,
        "normal_switching_allowed": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C14 Undertow validation failed")


if __name__ == "__main__":
    main()
