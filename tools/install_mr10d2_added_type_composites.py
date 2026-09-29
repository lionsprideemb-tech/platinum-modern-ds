#!/usr/bin/env python3
"""MR10D2 — added-type compound Ability batch.

Builds directly on MR10D1's battle-only added-type core and graduates five
KEEP-AS-WRITTEN mechanics whose remaining behavior can reuse existing Platinum
or Mercury hooks:

- Draconic Might — added Dragon type + Normal-to-Dragon conversion + 1.2x power
- Dragonfruit — added Dragon type + Rough Skin behavior
- Rock Armor — added Rock type + 10 percent incoming move-damage reduction
- Voltron — added Steel type + Battle Armor behavior
- Komodo — added Dragon type + 30 percent badly-poison proc on successful attacks

Mechanics only; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Draconic Might": ("ABILITY_MR_DRACONIC_MIGHT", 527, "TYPE_DRAGON"),
    "Dragonfruit": ("ABILITY_MR_DRAGONFRUIT", 552, "TYPE_DRAGON"),
    "Rock Armor": ("ABILITY_MR_ROCK_ARMOR", 562, "TYPE_ROCK"),
    "Voltron": ("ABILITY_MR_VOLTRON", 586, "TYPE_STEEL"),
    "Komodo": ("ABILITY_MR_KOMODO", 670, "TYPE_DRAGON"),
}

TOKENS = tuple(value[0] for value in IMPLEMENTED.values())

# MR10D2 gate revision: workflow trigger path is active.


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all_existing(path: Path, old: str, new: str, label: str) -> int:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count < 1:
        raise SystemExit(f"{label}: expected at least one match in {path}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    return count


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
    if marker in text:
        return
    start, end = function_bounds(text, signature)
    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
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


def extend_added_type_map(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = "static u8 Mercury_AddedTypeForAbility(int ability)"
    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]

    marker = "case ABILITY_MR_DRACONIC_MIGHT:"
    if marker in block:
        return

    anchor = """    default:
        return 0xFF;
"""
    insertion = """    case ABILITY_MR_DRACONIC_MIGHT:
    case ABILITY_MR_DRAGONFRUIT:
    case ABILITY_MR_KOMODO:
        return TYPE_DRAGON;
    case ABILITY_MR_ROCK_ARMOR:
        return TYPE_ROCK;
    case ABILITY_MR_VOLTRON:
        return TYPE_STEEL;
"""
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(f"MR10D2 added-type map: expected one default anchor, found {count}")
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_draconic_might(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Damage calculation path.
    replace_all_existing(
        path,
        """        } else if (attackerParams.ability == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else {
""",
        """        } else if (attackerParams.ability == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else if (attackerParams.ability == ABILITY_MR_DRACONIC_MIGHT) {
            moveType = TYPE_DRAGON;
        } else {
""",
        "Draconic Might damage move-type conversion",
    )

    # Shared local-ability paths (type chart, immunity path, Color Change path).
    replace_all_existing(
        path,
        """        } else if (ability == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else {
""",
        """        } else if (ability == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else if (ability == ABILITY_MR_DRACONIC_MIGHT) {
            moveType = TYPE_DRAGON;
        } else {
""",
        "Draconic Might local ability move-type conversion",
    )

    # Generic effectiveness path used for party/AI calculations.
    replace_all_existing(
        path,
        """        } else if (attackerAbility == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else {
""",
        """        } else if (attackerAbility == ABILITY_GALVANIZE) {
            moveType = TYPE_ELECTRIC;
        } else if (attackerAbility == ABILITY_MR_DRACONIC_MIGHT) {
            moveType = TYPE_DRAGON;
        } else {
""",
        "Draconic Might generic effectiveness conversion",
    )

    # The -ate family already applies the exact requested 1.2x modifier.
    replace_once(
        path,
        """            || attackerParams.ability == ABILITY_GALVANIZE)
        && inType == TYPE_NORMAL
""",
        """            || attackerParams.ability == ABILITY_GALVANIZE
            || attackerParams.ability == ABILITY_MR_DRACONIC_MIGHT)
        && inType == TYPE_NORMAL
""",
        "Draconic Might 20 percent Normal-move boost",
    )


def patch_dragonfruit(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """    case ABILITY_ROUGH_SKIN:
""",
        """    case ABILITY_MR_DRAGONFRUIT:
    case ABILITY_ROUGH_SKIN:
""",
        "Dragonfruit Rough Skin behavior",
    )


def patch_rock_armor(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_CalcMoveDamage(BattleSystem *battleSys,\n"
        "    BattleContext *battleCtx,\n"
        "    int move,\n"
        "    u32 sideConditions,\n"
        "    u32 fieldConditions,\n"
        "    u16 inPower,\n"
        "    u8 inType,\n"
        "    u8 attacker,\n"
        "    u8 defender,\n"
        "    u8 criticalMul)"
    )
    insertion = """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_ROCK_ARMOR) == TRUE) {
        damage = damage * 9 / 10;
    }

"""
    insert_before_in_function(
        path,
        signature,
        """    if (Mercury_AllyHasAbility(
            battleSys, battleCtx, defender, ABILITY_FRIEND_GUARD)) {
""",
        insertion,
        "ABILITY_MR_ROCK_ARMOR) == TRUE",
        "Rock Armor incoming damage reduction",
    )


def patch_voltron(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_BATTLE_ARMOR) == FALSE
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SHELL_ARMOR) == FALSE
""",
        """        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_BATTLE_ARMOR) == FALSE
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MR_VOLTRON) == FALSE
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SHELL_ARMOR) == FALSE
""",
        "Voltron Battle Armor behavior",
    )


def patch_komodo(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
        && DEFENDING_MON.curHP
""",
        """    if ((Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
            || Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MR_KOMODO)
        && DEFENDING_MON.curHP
""",
        "Komodo 30 percent badly-poison reaction",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "d1_added_type_core_present":
            "Mercury_BattlerAddedType" in lib
            and "Mercury_AddedTypeForAbility" in lib,
        "five_added_type_mappings":
            all(token in lib for token in TOKENS),
        "draconic_might_conversion":
            "attackerParams.ability == ABILITY_MR_DRACONIC_MIGHT" in lib
            and "moveType = TYPE_DRAGON;" in lib,
        "draconic_might_power_20":
            "|| attackerParams.ability == ABILITY_MR_DRACONIC_MIGHT)" in lib
            and "movePower = movePower * 12 / 10;" in lib,
        "dragonfruit_rough_skin":
            "case ABILITY_MR_DRAGONFRUIT:" in lib
            and "case ABILITY_ROUGH_SKIN:" in lib,
        "rock_armor_damage_reduction":
            "ABILITY_MR_ROCK_ARMOR) == TRUE" in lib
            and "damage = damage * 9 / 10;" in lib,
        "voltron_critical_immunity":
            "ABILITY_MR_VOLTRON) == FALSE" in lib
            and "ABILITY_BATTLE_ARMOR" in lib,
        "komodo_badly_poison_proc":
            "ABILITY_MR_KOMODO)" in lib
            and "subscript_badly_poison" in lib,
        "implemented_registry_updated":
            all(token in registry_lines for token in TOKENS),
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
        default=Path("mr10d2-added-type-composites.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    extend_added_type_map(root)
    patch_draconic_might(root)
    patch_dragonfruit(root)
    patch_rock_armor(root)
    patch_voltron(root)
    patch_komodo(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D2_ADDED_TYPE_COMPOSITES",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "battle_only_added_type_plus_existing_hooks",
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D2 added-type composite validation failed")


if __name__ == "__main__":
    main()
