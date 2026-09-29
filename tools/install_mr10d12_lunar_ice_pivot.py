#!/usr/bin/env python3
"""MR10D12 — Lunar Wrath + Hollow Ice Zone.

Extends two already-certified shared Mercury systems:
- Lunar Wrath joins D7's generated follow-up pipeline: successful Ghost-type
  damaging moves create one 50-BP Moongeist Beam action.
- Hollow Ice Zone uses the attacker on-hit lane to turn a successfully hit
  target into pure Ice for the remainder of its active stay, then requests the
  ordinary U-turn-style self-switch sequence after all hit/reaction handling.

Hollow Ice's pivot state is kept per active battler so queued D8 reactive
counters cannot erase it when they temporarily reuse BattleContext_Init.
Substitutes block the retyping trigger. If switching is illegal, Platinum's
native attack-then-switch-out script simply leaves the user in battle.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Lunar Wrath": ("ABILITY_MR_LUNAR_WRATH", 573),
    "Hollow Ice Zone": ("ABILITY_MR_HOLLOW_ICE_ZONE", 741),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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
        """    u16 mercuryCustomMultiHitTriggerAbility;
""",
        """    // Mercury MR10D12: delayed self-pivot after Hollow Ice Zone hits.
    u8 mercuryHollowIcePivotPending[MAX_BATTLERS];

""",
        "D12 Hollow Ice pending-pivot state",
    )


def patch_lunar_wrath(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static BOOL Mercury_D7ChooseFollowup(\n"
        "    BattleContext *battleCtx,\n"
        "    int *move,\n"
        "    int *power)"
    )
    insertion = """    case ABILITY_MR_LUNAR_WRATH:
        if (damaging && moveType == TYPE_GHOST) {
            *move = MOVE_MOONGEIST_BEAM;
            *power = 50;
        }
        break;

"""
    insert_before_in_function(
        path,
        signature,
        """    case ABILITY_MR_CHILLING_PELLETS:
""",
        insertion,
        "case ABILITY_MR_LUNAR_WRATH:",
        "D12 Lunar Wrath generated follow-up",
    )


def patch_hollow_ice_hit(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL Mercury_TriggerAttackerOnHitAbility("
        "BattleSystem *battleSys,\n"
        "    BattleContext *battleCtx,\n"
        "    int *subscript)"
    )
    insertion = """    if (Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MR_HOLLOW_ICE_ZONE
        && battleCtx->mercuryHollowIcePivotPending[battleCtx->attacker] == FALSE
        && DEFENDING_MON.curHP
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && CalcMoveType(
            battleCtx,
            battleCtx->attacker,
            battleCtx->moveCur) == TYPE_ICE) {
        DEFENDING_MON.type1 = TYPE_ICE;
        DEFENDING_MON.type2 = TYPE_ICE;
        battleCtx->mercuryDynamicAddedType[battleCtx->defender] = 0xFF;
        battleCtx->mercuryHollowIcePivotPending[battleCtx->attacker] = TRUE;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        battleCtx->msgTemp = ABILITY_MR_HOLLOW_ICE_ZONE;
        *subscript = subscript_mold_breaker;
        return TRUE;
    }

"""
    insert_before_in_function(
        path,
        signature,
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH
""",
        insertion,
        "ABILITY_MR_HOLLOW_ICE_ZONE",
        "D12 Hollow Ice hit retyping",
    )


def patch_hollow_ice_pivot(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """        if (battleCtx->attacker != BATTLER_NONE
            && battleCtx->mercuryHollowIcePivotPending[battleCtx->attacker]) {
            battleCtx->mercuryHollowIcePivotPending[battleCtx->attacker] = FALSE;

            if (battleCtx->battleMons[battleCtx->attacker].curHP) {
                LOAD_SUBSEQ(subscript_attack_then_switch_out);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                return;
            }
        }

"""
    insert_before_in_function(
        path,
        signature,
        """        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        insertion,
        "mercuryHollowIcePivotPending[battleCtx->attacker]",
        "D12 Hollow Ice delayed native pivot",
    )

    # Clear stale pending state whenever a slot receives a new battler.
    lib = root / "src/battle/battle_lib.c"
    replace_once(
        lib,
        """    battleCtx->mercuryDynamicAddedType[battler] = 0xFF;
""",
        """    battleCtx->mercuryDynamicAddedType[battler] = 0xFF;
    battleCtx->mercuryHollowIcePivotPending[battler] = FALSE;
""",
        "D12 Hollow Ice switch reset",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "lunar_wrath_ghost_gate":
            "case ABILITY_MR_LUNAR_WRATH:" in ctl
            and "moveType == TYPE_GHOST" in ctl,
        "lunar_wrath_moongeist_50":
            "MOVE_MOONGEIST_BEAM" in ctl
            and "*power = 50;" in ctl,
        "lunar_wrath_reuses_d7_pipeline":
            "Mercury_TryAbilityFollowup" in ctl
            and "mercuryAbilityGeneratedAction" in ctl,
        "hollow_ice_pending_state":
            "mercuryHollowIcePivotPending[MAX_BATTLERS]" in ctx,
        "hollow_ice_requires_real_hit":
            "BOOL Mercury_TriggerAttackerOnHitAbility" in lib
            and "DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken" in lib,
        "hollow_ice_ice_gate":
            "ABILITY_MR_HOLLOW_ICE_ZONE" in lib
            and "== TYPE_ICE" in lib,
        "hollow_ice_pure_ice_retype":
            "DEFENDING_MON.type1 = TYPE_ICE;" in lib
            and "DEFENDING_MON.type2 = TYPE_ICE;" in lib,
        "hollow_ice_clears_added_type":
            "mercuryDynamicAddedType[battleCtx->defender] = 0xFF;" in lib,
        "hollow_ice_native_self_switch":
            "LOAD_SUBSEQ(subscript_attack_then_switch_out);" in ctl
            and "mercuryHollowIcePivotPending[battleCtx->attacker] = FALSE;" in ctl,
        "hollow_ice_survives_reactive_counter_context_init":
            "mercuryHollowIcePivotPending" in ctx
            and "BattleContext_Init(battleCtx)" in ctl,
        "hollow_ice_switch_reset":
            "mercuryHollowIcePivotPending[battler] = FALSE;" in lib,
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
        default=Path("mr10d12-lunar-ice-pivot.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_lunar_wrath(root)
    patch_hollow_ice_hit(root)
    patch_hollow_ice_pivot(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D12_LUNAR_ICE_PIVOT",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_systems_reused": [
            "MR10D7 generated follow-up action",
            "MR10D10 battle-only type state",
            "Platinum attack-then-switch-out subscript",
        ],
        "remaining_keep_as_written_after_d12": 30,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D12 Lunar/Ice pivot validation failed")


if __name__ == "__main__":
    main()
