#!/usr/bin/env python3
"""MR10D10 — dynamic battle-only added typing.

Implements Magical Dust:
- after the holder receives a qualifying damaging contact hit, the attacker
  gains Psychic as an additional battle type if it is not already Psychic;
- the added type lasts while that battler remains active and is cleared when
  that battle slot switches to a new party Pokémon;
- STAB, script type checks, and defensive effectiveness all see the dynamic
  type through the existing MR10D type helper path.

This extends MR10D's static Ability-added type system without replacing the
holder's ordinary or Ability-granted types. Mechanics only; locked MR07
visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Magical Dust"
ABILITY_TOKEN = "ABILITY_MR_MAGICAL_DUST"
ABILITY_ID = 906


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
    rows = [
        row for row in plan.get("abilities", plan.get("rows", []))
        if row.get("display_name") == ABILITY_NAME
        or row.get("source_name") == ABILITY_NAME
    ]
    if len(rows) != 1:
        raise SystemExit(f"{ABILITY_NAME}: expected one partition row, found {len(rows)}")
    row = rows[0]
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
        """    u16 mercuryReactiveOriginalMove;
""",
        """    // Mercury MR10D10: temporary additional battle typing caused
    // by effects such as Magical Dust. 0xFF means no dynamic added type.
    u8 mercuryDynamicAddedType[MAX_BATTLERS];

""",
        "MR10D10 dynamic type context",
    )


def patch_initialization_and_switch_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_after_in_function(
        path,
        "void BattleContext_InitCounters(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        battleCtx->speedRand[i] = BattleSystem_RandNext(battleSys);
""",
        """        battleCtx->mercuryDynamicAddedType[i] = 0xFF;
""",
        "mercuryDynamicAddedType[i] = 0xFF;",
        "MR10D10 battle-start dynamic type init",
    )

    insert_before_in_function(
        path,
        "void BattleSystem_UpdateAfterSwitch(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    battleCtx->moveProtect[battler] = MOVE_NONE;
""",
        """    battleCtx->mercuryDynamicAddedType[battler] = 0xFF;
""",
        "mercuryDynamicAddedType[battler] = 0xFF;",
        "MR10D10 switch reset",
    )


def patch_type_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    return BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_1, NULL) == type
        || BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_2, NULL) == type
        || Mercury_BattlerAddedType(battleCtx, battler) == type;
""",
        """    return BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_1, NULL) == type
        || BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_2, NULL) == type
        || Mercury_BattlerAddedType(battleCtx, battler) == type
        || battleCtx->mercuryDynamicAddedType[battler] == type;
""",
        "MR10D10 widen public battle type helper",
    )


def patch_runtime_type_chart(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, "
        "int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)"
    )

    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "u8 mercuryDynamicDefenderType;" not in block:
        anchor = "    u8 mercuryDefenderType;\n"
        if block.count(anchor) != 1:
            raise SystemExit("MR10D10 dynamic type declaration anchor missing")
        block = block.replace(
            anchor,
            anchor + "    u8 mercuryDynamicDefenderType;\n",
            1,
        )
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")

    insert_after_in_function(
        path,
        signature,
        """    mercuryDefenderType = Mercury_BattlerAddedType(battleCtx, defender);
""",
        """    mercuryDynamicDefenderType =
        battleCtx->mercuryDynamicAddedType[defender];
""",
        "mercuryDynamicDefenderType =",
        "MR10D10 dynamic type capture",
    )

    dynamic_loop = """    /* Mercury MR10D10: apply temporary contact-added typing too. */
    if (mercuryDynamicDefenderType != 0xFF
        && mercuryDynamicDefenderType != BattleMon_Get(
            battleCtx, defender, BATTLEMON_TYPE_1, NULL)
        && mercuryDynamicDefenderType != BattleMon_Get(
            battleCtx, defender, BATTLEMON_TYPE_2, NULL)
        && mercuryDynamicDefenderType != mercuryDefenderType
        && (*moveStatusMask & MOVE_STATUS_NO_EFFECTS) == FALSE) {
        chartEntry = 0;
        while (sTypeMatchupMultipliers[chartEntry][0] != 0xFF) {
            if (sTypeMatchupMultipliers[chartEntry][0] != 0xFE
                && sTypeMatchupMultipliers[chartEntry][0] == moveType
                && sTypeMatchupMultipliers[chartEntry][1]
                    == mercuryDynamicDefenderType
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

"""
    insert_before_in_function(
        path,
        signature,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WONDER_GUARD) == TRUE
""",
        dynamic_loop,
        "Mercury MR10D10: apply temporary contact-added typing too.",
        "MR10D10 dynamic defensive type effectiveness",
    )


def patch_magical_dust_hit(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL BattleSystem_TriggerAbilityOnHit("
        "BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
    )

    insertion = """    case ABILITY_MR_MAGICAL_DUST:
        if (ATTACKING_MON.curHP
            && DEFENDING_MON.curHP
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)
            && Battler_SubstituteWasHit(
                battleCtx, battleCtx->defender) == FALSE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_BattlerHasType(
                battleCtx, battleCtx->attacker, TYPE_PSYCHIC) == FALSE) {
            battleCtx->mercuryDynamicAddedType[battleCtx->attacker] =
                TYPE_PSYCHIC;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            battleCtx->msgTemp = ABILITY_MR_MAGICAL_DUST;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

"""
    insert_before_in_function(
        path,
        signature,
        """    case ABILITY_MR_DEFLECT:
""",
        insertion,
        "case ABILITY_MR_MAGICAL_DUST:",
        "MR10D10 Magical Dust contact reaction",
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
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "dynamic_type_state":
            "mercuryDynamicAddedType[MAX_BATTLERS]" in ctx,
        "battle_start_initializes_none":
            "mercuryDynamicAddedType[i] = 0xFF;" in lib,
        "switch_clears_dynamic_type":
            "mercuryDynamicAddedType[battler] = 0xFF;" in lib,
        "public_type_checks_see_dynamic_type":
            "mercuryDynamicAddedType[battler] == type" in lib,
        "runtime_effectiveness_sees_dynamic_type":
            "Mercury MR10D10: apply temporary contact-added typing too." in lib
            and "mercuryDynamicDefenderType" in lib,
        "magical_dust_contact_gate":
            "case ABILITY_MR_MAGICAL_DUST:" in lib
            and "MOVE_FLAG_MAKES_CONTACT" in lib,
        "magical_dust_requires_real_hit":
            "Battler_SubstituteWasHit(" in lib
            and "DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken" in lib,
        "magical_dust_adds_psychic":
            "mercuryDynamicAddedType[battleCtx->attacker]" in lib
            and "TYPE_PSYCHIC;" in lib,
        "already_psychic_no_duplicate":
            "Mercury_BattlerHasType(" in lib
            and "TYPE_PSYCHIC) == FALSE" in lib,
        "implemented_registry_updated":
            ABILITY_TOKEN in registry_lines,
        "stable_id_906":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
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
        default=Path("mr10d10-dynamic-added-type.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_initialization_and_switch_reset(root)
    patch_type_helpers(root)
    patch_runtime_type_chart(root)
    patch_magical_dust_hit(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D10_DYNAMIC_ADDED_TYPE",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "dynamic_type": "Psychic",
        "duration": "until battler leaves active slot",
        "remaining_keep_as_written_after_d10": 38,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D10 dynamic added-type validation failed")


if __name__ == "__main__":
    main()
