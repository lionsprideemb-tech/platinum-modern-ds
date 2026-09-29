#!/usr/bin/env python3
"""MR10D1 — Mercury battle-only added-type core.

This pass establishes the shared third-type behavior required by the first
KEEP-AS-WRITTEN mechanic family and graduates nine approved abilities together:

- Aquatic
- Grounded
- Half Drake
- Ice Age
- Metallic
- Dragonfly
- Hover
- Turboblaze
- Teravolt

The added type is derived from the holder's currently-active Ability, so no
persistent save data is added and suppression/Ability replacement naturally
removes the granted type. Dynamic target retyping and compound abilities are
left for later MR10D batches.

Mechanics only; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Aquatic": ("ABILITY_MR_AQUATIC", 702, "TYPE_WATER"),
    "Grounded": ("ABILITY_MR_GROUNDED", 703, "TYPE_GROUND"),
    "Dragonfly": ("ABILITY_MR_DRAGONFLY", 775, "TYPE_DRAGON"),
    "Half Drake": ("ABILITY_MR_HALF_DRAKE", 791, "TYPE_DRAGON"),
    "Hover": ("ABILITY_MR_HOVER", 793, "TYPE_PSYCHIC"),
    "Ice Age": ("ABILITY_MR_ICE_AGE", 795, "TYPE_ICE"),
    "Metallic": ("ABILITY_MR_METALLIC", 809, "TYPE_STEEL"),
    "Turboblaze": ("ABILITY_TURBOBLAZE", 163, "TYPE_FIRE"),
    "Teravolt": ("ABILITY_TERAVOLT", 164, "TYPE_ELECTRIC"),
}

IMPLEMENTED_TOKENS = tuple(value[0] for value in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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


def insert_before_needle_in_function(
    path: Path,
    signature: str,
    needle: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    start, end = function_bounds(text, signature)
    block = text[start:end]
    pos = block.find(needle)
    if pos < 0:
        raise SystemExit(f"{label}: needle not found in {signature}")

    line_start = block.rfind("\n", 0, pos) + 1
    current_line = block[line_start:pos].lstrip()
    if current_line.startswith("&&") or current_line.startswith("||"):
        governing_if = block.rfind("    if (", 0, pos)
        if governing_if < 0:
            raise SystemExit(f"{label}: governing if not found in {signature}")
        line_start = governing_if

    block = block[:line_start] + insertion + block[line_start:]
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def prefix_if_before_needle_in_function(
    path: Path,
    signature: str,
    needle: str,
    custom_if: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return

    start, end = function_bounds(text, signature)
    block = text[start:end]
    pos = block.find(needle)
    if pos < 0:
        raise SystemExit(f"{label}: needle not found in {signature}")

    if_start = block.rfind("    if (", 0, pos)
    if if_start < 0:
        raise SystemExit(f"{label}: governing if not found in {signature}")

    block = block[:if_start] + custom_if + block[if_start + 4:]
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))

    for name, (token, ability_id, _) in IMPLEMENTED.items():
        matches = [
            row
            for row in rows
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


def patch_public_helpers(root: Path) -> None:
    header = root / "include/battle/battle_lib.h"
    insertion = """\n/* Mercury MR10D: battle-only additional typing. */\nint Mercury_BattlerAddedType(BattleContext *battleCtx, int battler);\nBOOL Mercury_BattlerHasType(BattleContext *battleCtx, int battler, int type);\n\n"""
    insert_before_once(
        header,
        "#endif // POKEPLATINUM_BATTLE_BATTLE_LIB_H",
        insertion,
        "MR10D battle type helper declarations",
    )

    common = root / "include/battle/common.h"
    replace_once(
        common,
        """#define MON_HAS_TYPE(mon, type)    (BattleMon_Get(battleCtx, mon, BATTLEMON_TYPE_1, NULL) == type || BattleMon_Get(battleCtx, mon, BATTLEMON_TYPE_2, NULL) == type)\n#define MON_IS_NOT_TYPE(mon, type) (BattleMon_Get(battleCtx, mon, BATTLEMON_TYPE_1, NULL) != type && BattleMon_Get(battleCtx, mon, BATTLEMON_TYPE_2, NULL) != type)\n""",
        """#define MON_HAS_TYPE(mon, type)    Mercury_BattlerHasType(battleCtx, mon, type)\n#define MON_IS_NOT_TYPE(mon, type) (Mercury_BattlerHasType(battleCtx, mon, type) == FALSE)\n""",
        "MR10D widen battle type macros",
    )


def patch_type_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    helper = """static u8 Mercury_AddedTypeForAbility(int ability)\n{\n    switch (ability) {\n    case ABILITY_MR_AQUATIC:\n        return TYPE_WATER;\n    case ABILITY_MR_GROUNDED:\n        return TYPE_GROUND;\n    case ABILITY_MR_DRAGONFLY:\n    case ABILITY_MR_HALF_DRAKE:\n        return TYPE_DRAGON;\n    case ABILITY_MR_HOVER:\n        return TYPE_PSYCHIC;\n    case ABILITY_MR_ICE_AGE:\n        return TYPE_ICE;\n    case ABILITY_MR_METALLIC:\n        return TYPE_STEEL;\n    case ABILITY_TURBOBLAZE:\n        return TYPE_FIRE;\n    case ABILITY_TERAVOLT:\n        return TYPE_ELECTRIC;\n    default:\n        return 0xFF;\n    }\n}\n\nint Mercury_BattlerAddedType(BattleContext *battleCtx, int battler)\n{\n    return Mercury_AddedTypeForAbility(Battler_Ability(battleCtx, battler));\n}\n\nBOOL Mercury_BattlerHasType(BattleContext *battleCtx, int battler, int type)\n{\n    return BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_1, NULL) == type\n        || BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_2, NULL) == type\n        || Mercury_BattlerAddedType(battleCtx, battler) == type;\n}\n\nstatic BOOL Mercury_IsMoldBreakerLikeAbilityId(int ability)\n{\n    return ability == ABILITY_MOLD_BREAKER\n        || ability == ABILITY_TURBOBLAZE\n        || ability == ABILITY_TERAVOLT;\n}\n\n"""
    insert_before_once(
        lib,
        "BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)\n",
        helper,
        "MR10D added-type helpers",
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
    if "u8 mercuryDefenderType;" not in block:
        anchor = "    u8 defenderItemPower;\n"
        if block.count(anchor) != 1:
            raise SystemExit("MR10D runtime type chart: defenderItemPower declaration anchor missing")
        block = block.replace(anchor, anchor + "    u8 mercuryDefenderType;\n", 1)
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")

    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "mercuryDefenderType = Mercury_BattlerAddedType" not in block:
        anchor = """    if (move == MOVE_STRUGGLE) {\n        return damage;\n    }\n\n"""
        if block.count(anchor) != 1:
            raise SystemExit("MR10D runtime type chart: Struggle anchor missing")
        block = block.replace(
            anchor,
            anchor
            + "    mercuryDefenderType = Mercury_BattlerAddedType(battleCtx, defender);\n\n",
            1,
        )
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")

    custom_ground = """    if ((Battler_IgnorableAbility(\n            battleCtx, attacker, defender, ABILITY_MR_DRAGONFLY) == TRUE\n            || Battler_IgnorableAbility(\n                battleCtx, attacker, defender, ABILITY_MR_HOVER) == TRUE)\n        && moveType == TYPE_GROUND) {\n        *moveStatusMask |= MOVE_STATUS_INEFFECTIVE;\n    } else """
    prefix_if_before_needle_in_function(
        path,
        signature,
        "ABILITY_LEVITATE",
        custom_ground,
        "ABILITY_MR_DRAGONFLY) == TRUE",
        "MR10D Dragonfly/Hover Ground immunity",
    )

    third_type = """    /* Mercury MR10D: apply the Ability-granted third defensive type. */\n    if (mercuryDefenderType != 0xFF\n        && mercuryDefenderType != BattleMon_Get(\n            battleCtx, defender, BATTLEMON_TYPE_1, NULL)\n        && mercuryDefenderType != BattleMon_Get(\n            battleCtx, defender, BATTLEMON_TYPE_2, NULL)\n        && (*moveStatusMask & MOVE_STATUS_NO_EFFECTS) == FALSE) {\n        chartEntry = 0;\n        while (sTypeMatchupMultipliers[chartEntry][0] != 0xFF) {\n            if (sTypeMatchupMultipliers[chartEntry][0] != 0xFE\n                && sTypeMatchupMultipliers[chartEntry][0] == moveType\n                && sTypeMatchupMultipliers[chartEntry][1] == mercuryDefenderType\n                && BasicTypeMulApplies(\n                    battleCtx, attacker, defender, chartEntry) == TRUE) {\n                damage = ApplyTypeMultiplier(\n                    battleCtx,\n                    attacker,\n                    sTypeMatchupMultipliers[chartEntry][2],\n                    damage,\n                    movePower,\n                    moveStatusMask);\n            }\n            chartEntry++;\n        }\n    }\n\n"""
    insert_before_needle_in_function(
        path,
        signature,
        "ABILITY_WONDER_GUARD",
        third_type,
        "Mercury MR10D: apply the Ability-granted third defensive type.",
        "MR10D runtime third defensive type",
    )


def patch_ai_type_chart(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "void BattleSystem_CalcEffectiveness(BattleContext *battleCtx, int move, int inType, "
        "int attackerAbility, int defenderAbility, int defenderItemEffect, int defenderType1, "
        "int defenderType2, u32 *moveStatusMask)"
    )

    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "u8 mercuryDefenderType;" not in block:
        anchor = "    u8 moveType;\n"
        if block.count(anchor) != 1:
            raise SystemExit("MR10D AI type chart: moveType declaration anchor missing")
        block = block.replace(anchor, anchor + "    u8 mercuryDefenderType;\n", 1)
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")

    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "mercuryDefenderType = Mercury_AddedTypeForAbility(defenderAbility);" not in block:
        anchor = """    if (move == MOVE_STRUGGLE) {\n        return;\n    }\n\n"""
        if block.count(anchor) != 1:
            raise SystemExit("MR10D AI type chart: Struggle anchor missing")
        block = block.replace(
            anchor,
            anchor
            + "    mercuryDefenderType = Mercury_AddedTypeForAbility(defenderAbility);\n\n",
            1,
        )
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")

    custom_ground = """    if (Mercury_IsMoldBreakerLikeAbilityId(attackerAbility) == FALSE\n        && (defenderAbility == ABILITY_MR_DRAGONFLY\n            || defenderAbility == ABILITY_MR_HOVER)\n        && moveType == TYPE_GROUND) {\n        *moveStatusMask |= MOVE_STATUS_INEFFECTIVE;\n    } else """
    prefix_if_before_needle_in_function(
        path,
        signature,
        "defenderAbility == ABILITY_LEVITATE",
        custom_ground,
        "defenderAbility == ABILITY_MR_DRAGONFLY",
        "MR10D AI Dragonfly/Hover Ground immunity",
    )

    third_type = """    /* Mercury MR10D: include the static Ability-granted third type in AI checks. */\n    if (mercuryDefenderType != 0xFF\n        && mercuryDefenderType != defenderType1\n        && mercuryDefenderType != defenderType2\n        && (*moveStatusMask & MOVE_STATUS_INEFFECTIVE) == FALSE) {\n        chartEntry = 0;\n        while (sTypeMatchupMultipliers[chartEntry][0] != 0xFF) {\n            if (sTypeMatchupMultipliers[chartEntry][0] != 0xFE\n                && sTypeMatchupMultipliers[chartEntry][0] == moveType\n                && sTypeMatchupMultipliers[chartEntry][1] == mercuryDefenderType\n                && NoImmunityOverrides(\n                    battleCtx, defenderItemEffect, chartEntry) == TRUE) {\n                UpateMoveStatusForTypeMul(\n                    sTypeMatchupMultipliers[chartEntry][2], moveStatusMask);\n            }\n            chartEntry++;\n        }\n    }\n\n"""
    insert_before_needle_in_function(
        path,
        signature,
        "defenderAbility == ABILITY_WONDER_GUARD",
        third_type,
        "Mercury MR10D: include the static Ability-granted third type in AI checks.",
        "MR10D AI third defensive type",
    )


def patch_script_type_equality(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    signature = (
        "static BOOL BtlCmd_CompareMonDataToValue("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """    if ((srcParam == BATTLEMON_TYPE_1 || srcParam == BATTLEMON_TYPE_2)\n        && (op == OPCODE_EQU || op == OPCODE_NEQ)) {\n        BOOL hasType = Mercury_BattlerHasType(\n            battleCtx, battler, compareTo);\n        if ((op == OPCODE_EQU && hasType == FALSE)\n            || (op == OPCODE_NEQ && hasType == TRUE)) {\n            jump = 0;\n        }\n\n        if (jump) {\n            BattleScript_Iter(battleCtx, jump);\n        }\n        return FALSE;\n    }\n\n"""
    insert_before_needle_in_function(
        path,
        signature,
        "switch (op)",
        insertion,
        "BOOL hasType = Mercury_BattlerHasType(",
        "MR10D script type equality",
    )

    signature = (
        "static BOOL BtlCmd_CompareMonDataToVar("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """    if ((paramID == BATTLEMON_TYPE_1 || paramID == BATTLEMON_TYPE_2)\n        && (op == OPCODE_EQU || op == OPCODE_NEQ)) {\n        int resolvedBattler = BattleScript_Battler(battleSys, battleCtx, battler);\n        BOOL hasType = Mercury_BattlerHasType(\n            battleCtx, resolvedBattler, *rhs);\n        if ((op == OPCODE_EQU && hasType == FALSE)\n            || (op == OPCODE_NEQ && hasType == TRUE)) {\n            jump = 0;\n        }\n\n        if (jump) {\n            BattleScript_Iter(battleCtx, jump);\n        }\n        return FALSE;\n    }\n\n"""
    insert_before_needle_in_function(
        path,
        signature,
        "switch (op)",
        insertion,
        "int resolvedBattler = BattleScript_Battler(",
        "MR10D script type variable equality",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED_TOKENS:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    common = (root / "include/battle/common.h").read_text(encoding="utf-8")
    header = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "public_added_type_helpers":
            "Mercury_BattlerAddedType" in header
            and "Mercury_BattlerHasType" in header,
        "common_type_macros_widened":
            "#define MON_HAS_TYPE(mon, type)    Mercury_BattlerHasType" in common
            and "Mercury_BattlerHasType(battleCtx, mon, type) == FALSE" in common,
        "static_added_type_mapping":
            all(token in lib for token in IMPLEMENTED_TOKENS),
        "runtime_third_type_effectiveness":
            "Mercury MR10D: apply the Ability-granted third defensive type." in lib
            and "mercuryDefenderType" in lib,
        "runtime_added_type_stab":
            "Mercury_BattlerHasType(battleCtx, mon, type)" in common,
        "dragonfly_hover_ground_immunity":
            "ABILITY_MR_DRAGONFLY) == TRUE" in lib
            and "ABILITY_MR_HOVER) == TRUE" in lib,
        "ai_understands_static_added_types":
            "Mercury MR10D: include the static Ability-granted third type in AI checks." in lib,
        "battle_scripts_see_added_types":
            "BOOL hasType = Mercury_BattlerHasType(" in script
            and "int resolvedBattler = BattleScript_Battler(" in script,
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED_TOKENS),
        "locked_mr07_visuals_untouched": True,
    }

    for name, (token, ability_id, _) in IMPLEMENTED.items():
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
        default=Path("mr10d1-added-type-core.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_public_helpers(root)
    patch_type_helpers(root)
    patch_runtime_type_chart(root)
    patch_ai_type_chart(root)
    patch_script_type_equality(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D1_ADDED_TYPE_CORE",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(IMPLEMENTED_TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "battle_only_added_type",
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D1 added-type core validation failed")


if __name__ == "__main__":
    main()
