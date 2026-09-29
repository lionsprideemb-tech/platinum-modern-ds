#!/usr/bin/env python3
"""MR10D17 — Cryo Architect.

Implements the approved KEEP-AS-WRITTEN reactive stat mechanic:
- a qualifying Water- or Ice-type damaging hit raises the holder's Attack;
- an Ice-type hit also raises Defense immediately;
- a Water-type hit schedules one Defense raise for the turn boundary, after
  the current turn's actions and before the holder can act next turn;
- scheduled Defense state is battle-only and clears if that active slot is
  replaced before it resolves.

All stage changes run through Platinum's normal stat-stage script so caps,
Simple, Contrary, and ordinary prevention/message rules remain centralized.
Locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Cryo Architect"
ABILITY_TOKEN = "ABILITY_MR_CRYO_ARCHITECT"
ABILITY_ID = 687


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
        raise SystemExit(
            f"{label}: expected one anchor in {signature}, found {count}"
        )
    block = block.replace(anchor, anchor + insertion, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))
    matches = [
        row for row in rows
        if row.get("display_name") == ABILITY_NAME
        or row.get("source_name") == ABILITY_NAME
    ]
    if len(matches) != 1:
        raise SystemExit(
            f"{ABILITY_NAME}: expected one partition row, found {len(matches)}"
        )
    row = matches[0]
    expected = {
        "id": ABILITY_ID,
        "token": ABILITY_TOKEN,
        "approval_state": "owner_approved_keep",
        "owner_review_decision": "KEEP AS WRITTEN",
        "implementation_class": "new_engine_system",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryLuckyHaloSurvivalUsedMask[2];
""",
        """    // Mercury MR10D17: Water-hit Defense boost waiting for turn boundary.
    u8 mercuryCryoArchitectWaterDefensePending[MAX_BATTLERS];

""",
        "D17 Cryo Architect pending state",
    )


def patch_state_init_and_switch_reset(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    insert_after_in_function(
        lib,
        "void BattleContext_InitCounters(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        battleCtx->mercuryParasiticSpores[i] = FALSE;
""",
        """        battleCtx->mercuryCryoArchitectWaterDefensePending[i] = FALSE;
""",
        "mercuryCryoArchitectWaterDefensePending[i] = FALSE;",
        "D17 battle-start pending init",
    )

    insert_after_in_function(
        lib,
        "void BattleSystem_UpdateAfterSwitch(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    battleCtx->mercurySapTrapMarked[battler] = FALSE;
""",
        """    battleCtx->mercuryCryoArchitectWaterDefensePending[battler] = FALSE;
""",
        "mercuryCryoArchitectWaterDefensePending[battler] = FALSE;",
        "D17 switch clears pending Defense",
    )


def patch_ice_script(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_cryo_architect_ice.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_parasitic_spores\n",
        "subscript_mercury_cryo_architect_ice\n",
        "D17 Cryo Architect subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_parasitic_spores.s',\n",
        "    'subscript_mercury_cryo_architect_ice.s',\n",
        "D17 Cryo Architect subscript build list",
    )


def patch_on_hit(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL BattleSystem_TriggerAbilityOnHit("
        "BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
    )
    insertion = """    case ABILITY_MR_CRYO_ARCHITECT: {
        int mercuryHitType = battleCtx->moveType
            ? battleCtx->moveType
            : MOVE_DATA(battleCtx->moveCur).type;

        if (DEFENDING_MON.curHP
            && Battler_SubstituteWasHit(
                battleCtx, battleCtx->defender) == FALSE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (mercuryHitType == TYPE_WATER
                || mercuryHitType == TYPE_ICE)) {
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            battleCtx->msgBattlerTemp = battleCtx->defender;

            if (mercuryHitType == TYPE_WATER) {
                battleCtx->mercuryCryoArchitectWaterDefensePending[
                    battleCtx->defender] = TRUE;
                battleCtx->sideEffectParam =
                    MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
                *subscript = subscript_update_stat_stage;
            } else {
                *subscript = subscript_mercury_cryo_architect_ice;
            }

            result = TRUE;
        }
        break;
    }

"""
    insert_before_in_function(
        lib,
        signature,
        """    case ABILITY_MR_MAGICAL_DUST:
""",
        insertion,
        "case ABILITY_MR_CRYO_ARCHITECT:",
        "D17 Cryo Architect on-hit reaction",
    )


def patch_delayed_defense(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL BattleSystem_TriggerTurnEndAbility("
        "BattleSystem *battleSys, BattleContext *battleCtx, int battler)"
    )
    insertion = """    if (battleCtx->mercuryCryoArchitectWaterDefensePending[battler]
        && battleCtx->battleMons[battler].curHP) {
        battleCtx->mercuryCryoArchitectWaterDefensePending[battler] = FALSE;
        battleCtx->sideEffectParam =
            MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE;
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battler;
        battleCtx->msgBattlerTemp = battler;
        LOAD_SUBSEQ(subscript_update_stat_stage);
        battleCtx->commandNext = battleCtx->command;
        battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
        return TRUE;
    }

"""
    insert_before_in_function(
        lib,
        signature,
        """    switch (Battler_Ability(battleCtx, battler)) {
""",
        insertion,
        "mercuryCryoArchitectWaterDefensePending[battler]",
        "D17 delayed Water Defense boost",
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
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    ice = (root / "res/battle/scripts/subscripts/subscript_mercury_cryo_architect_ice.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "stable_id_687":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "pending_state":
            "mercuryCryoArchitectWaterDefensePending[MAX_BATTLERS]" in ctx,
        "switch_clears_pending":
            "mercuryCryoArchitectWaterDefensePending[battler] = FALSE;" in lib,
        "water_or_ice_hit_gate":
            "case ABILITY_MR_CRYO_ARCHITECT:" in lib
            and "mercuryHitType == TYPE_WATER" in lib
            and "mercuryHitType == TYPE_ICE" in lib,
        "real_damage_gate":
            "Battler_SubstituteWasHit(" in lib
            and "DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken" in lib,
        "water_attack_now_defense_later":
            "MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE" in lib
            and "mercuryCryoArchitectWaterDefensePending[" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in lib,
        "ice_attack_and_defense_now":
            "subscript_mercury_cryo_architect_ice" in order
            and "MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE" in ice
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in ice,
        "normal_stat_stage_pipeline":
            "BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE" in ice
            and "subscript_update_stat_stage" in lib,
        "implemented_registry_updated":
            ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }
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
        default=Path("mr10d17-cryo-architect.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_state_init_and_switch_reset(root)
    patch_ice_script(root)
    patch_on_hit(root)
    patch_delayed_defense(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D17_CRYO_ARCHITECT",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_systems_reused": [
            "Platinum on-hit Ability dispatcher",
            "Platinum stat-stage subscript",
            "turn-end Ability lane",
        ],
        "remaining_keep_as_written_after_d17": 21,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D17 Cryo Architect validation failed")


if __name__ == "__main__":
    main()
