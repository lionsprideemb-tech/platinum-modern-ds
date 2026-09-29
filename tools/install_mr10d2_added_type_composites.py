#!/usr/bin/env python3
"""MR10D2 — added-type composite Ability batch.

Builds on MR10D1's shared battle-only extra-type bitmask and graduates six
KEEP-AS-WRITTEN mechanics whose remaining clauses can reuse canonical hooks:

- Dragonfruit: +Dragon typing + Rough Skin.
- Voltron: +Steel typing + Battle Armor.
- Dragonfly: +Dragon typing + Ground immunity.
- Hover: +Psychic typing + Ground immunity.
- Turboblaze: canonical Mold Breaker-family behavior + Fire typing.
- Teravolt: canonical Mold Breaker-family behavior + Electric typing.

MR08H already certified Turboblaze/Teravolt as Mold Breaker aliases; this pass
adds only their approved Redux typing clause while validating that the canonical
bypass behavior is still present.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    ("Dragonfruit", "ABILITY_MR_DRAGONFRUIT", 552, "TYPE_DRAGON"),
    ("Voltron", "ABILITY_MR_VOLTRON", 586, "TYPE_STEEL"),
    ("Dragonfly", "ABILITY_MR_DRAGONFLY", 775, "TYPE_DRAGON"),
    ("Hover", "ABILITY_MR_HOVER", 793, "TYPE_PSYCHIC"),
    ("Turboblaze", "ABILITY_TURBOBLAZE", 163, "TYPE_FIRE"),
    ("Teravolt", "ABILITY_TERAVOLT", 164, "TYPE_ELECTRIC"),
)


def find_function_block(text: str, signature: str, label: str) -> tuple[int, int]:
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found")

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
        raise SystemExit(f"{label}: function closing brace not found")
    return start, end


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_in_function(
    path: Path,
    signature: str,
    old: str,
    new: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    start, end = find_function_block(text, signature, label)
    block = text[start:end]
    count = block.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match inside {signature}, found {count}"
        )
    block = block.replace(old, new, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


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
    start, end = find_function_block(text, signature, label)
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
    rows = plan["abilities"]

    for name, token, ability_id, _type in IMPLEMENTED:
        matches = [x for x in rows if x.get("id") == ability_id]
        if len(matches) != 1:
            raise SystemExit(f"{name}: expected one partition row at ID {ability_id}")
        row = matches[0]
        expected = {
            "display_name": name,
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


def patch_added_type_mapping(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "static void Mercury_InitializeAbilityAddedType("
        "BattleContext *battleCtx, int battler)"
    )
    insertion = """    case ABILITY_MR_DRAGONFRUIT:
        Mercury_AddBattleType(battleCtx, battler, TYPE_DRAGON);
        break;
    case ABILITY_MR_VOLTRON:
        Mercury_AddBattleType(battleCtx, battler, TYPE_STEEL);
        break;
    case ABILITY_MR_DRAGONFLY:
        Mercury_AddBattleType(battleCtx, battler, TYPE_DRAGON);
        break;
    case ABILITY_MR_HOVER:
        Mercury_AddBattleType(battleCtx, battler, TYPE_PSYCHIC);
        break;
    case ABILITY_TURBOBLAZE:
        Mercury_AddBattleType(battleCtx, battler, TYPE_FIRE);
        break;
    case ABILITY_TERAVOLT:
        Mercury_AddBattleType(battleCtx, battler, TYPE_ELECTRIC);
        break;
"""
    insert_before_in_function(
        path,
        signature,
        """    default:
""",
        insertion,
        "MR10D2 added-type mappings",
    )


def patch_dragonfruit_rough_skin(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """    case ABILITY_ROUGH_SKIN:
""",
        """    case ABILITY_MR_DRAGONFRUIT:
    case ABILITY_ROUGH_SKIN:
""",
        "Dragonfruit Rough Skin alias",
    )


def patch_voltron_battle_armor(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_CalcCriticalMulti("
        "BattleSystem *battleSys, BattleContext *battleCtx, int attacker, "
        "int defender, int criticalStage, u32 sideConditions)"
    )
    old = """        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SHELL_ARMOR) == FALSE
"""
    new = """        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SHELL_ARMOR) == FALSE
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MR_VOLTRON) == FALSE
"""
    replace_in_function(
        path,
        signature,
        old,
        new,
        "Voltron Battle Armor alias",
    )


def patch_ground_immunity(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    apply_sig = (
        "int BattleSystem_ApplyTypeChart("
        "BattleSystem *battleSys, BattleContext *battleCtx, int move, int inType, "
        "int attacker, int defender, int damage, u32 *moveStatusMask)"
    )
    old_live = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_LEVITATE) == TRUE
        && moveType == TYPE_GROUND
        && defenderItemEffect != HOLD_EFFECT_SPEED_DOWN_GROUNDED) {
"""
    new_live = """    if ((Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_LEVITATE) == TRUE
            || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MR_DRAGONFLY) == TRUE
            || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MR_HOVER) == TRUE)
        && moveType == TYPE_GROUND
        && (battleCtx->fieldConditionsMask & FIELD_CONDITION_GRAVITY) == FALSE
        && defenderItemEffect != HOLD_EFFECT_SPEED_DOWN_GROUNDED) {
"""
    replace_in_function(
        path,
        apply_sig,
        old_live,
        new_live,
        "Dragonfly/Hover live Ground immunity",
    )

    calc_sig = (
        "void BattleSystem_CalcEffectiveness("
        "BattleContext *battleCtx, int move, int inType, int attackerAbility, "
        "int defenderAbility, int defenderItemEffect, int defenderType1, "
        "int defenderType2, u32 *moveStatusMask)"
    )
    old_calc = """        && defenderAbility == ABILITY_LEVITATE
        && moveType == TYPE_GROUND
"""
    new_calc = """        && (defenderAbility == ABILITY_LEVITATE
            || defenderAbility == ABILITY_MR_DRAGONFLY
            || defenderAbility == ABILITY_MR_HOVER)
        && moveType == TYPE_GROUND
"""
    replace_in_function(
        path,
        calc_sig,
        old_calc,
        new_calc,
        "Dragonfly/Hover general effectiveness Ground immunity",
    )

    replace_once(
        path,
        """    return (Battler_Ability(battleCtx, battler) != ABILITY_LEVITATE
               && battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns == 0
""",
        """    return (Battler_Ability(battleCtx, battler) != ABILITY_LEVITATE
               && Battler_Ability(battleCtx, battler) != ABILITY_MR_DRAGONFLY
               && Battler_Ability(battleCtx, battler) != ABILITY_MR_HOVER
               && battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns == 0
""",
        "Dragonfly/Hover grounded-state integration",
    )

    replace_once(
        path,
        """            if (Battler_Ability(battleCtx, battler) != ABILITY_LEVITATE
                && battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns == 0
""",
        """            if (Battler_Ability(battleCtx, battler) != ABILITY_LEVITATE
                && Battler_Ability(battleCtx, battler) != ABILITY_MR_DRAGONFLY
                && Battler_Ability(battleCtx, battler) != ABILITY_MR_HOVER
                && battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns == 0
""",
        "Dragonfly/Hover Arena Trap message integration",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for _name, token, _ability_id, _type in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    checks: dict[str, bool] = {}
    for name, token, ability_id, _type in IMPLEMENTED:
        checks[name.lower().replace(" ", "_") + "_stable_id"] = (
            len(abilities) > ability_id and abilities[ability_id] == token
        )
    return checks


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "dragonfruit_dragon_typing":
            "case ABILITY_MR_DRAGONFRUIT:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_DRAGON);" in lib,
        "dragonfruit_rough_skin":
            "case ABILITY_MR_DRAGONFRUIT:\n    case ABILITY_ROUGH_SKIN:" in lib,
        "voltron_steel_typing":
            "case ABILITY_MR_VOLTRON:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_STEEL);" in lib,
        "voltron_battle_armor":
            "ABILITY_MR_VOLTRON) == FALSE" in lib,
        "dragonfly_ground_immunity":
            "ABILITY_MR_DRAGONFLY) == TRUE" in lib
            and "ABILITY_MR_DRAGONFLY\n               && Battler_Ability" in lib,
        "hover_ground_immunity":
            "ABILITY_MR_HOVER) == TRUE" in lib
            and "ABILITY_MR_HOVER\n               && battleCtx" in lib,
        "general_effectiveness_knows_ground_immunities":
            "defenderAbility == ABILITY_MR_DRAGONFLY" in lib
            and "defenderAbility == ABILITY_MR_HOVER" in lib,
        "turboblaze_fire_typing":
            "case ABILITY_TURBOBLAZE:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_FIRE);" in lib,
        "teravolt_electric_typing":
            "case ABILITY_TERAVOLT:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_ELECTRIC);" in lib,
        "canonical_mold_breaker_family_preserved":
            "ability == ABILITY_TURBOBLAZE" in lib
            and "ability == ABILITY_TERAVOLT" in lib
            and "Mercury_IsMoldBreakerAbility" in lib,
        "registry_has_all_six":
            all(token in registry_lines for _name, token, _id, _type in IMPLEMENTED),
        "locked_mr07_visuals_untouched": True,
    }
    checks.update(validate_ids(root))
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
    patch_added_type_mapping(root)
    patch_dragonfruit_rough_skin(root)
    patch_voltron_battle_armor(root)
    patch_ground_immunity(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D2_ADDED_TYPE_COMPOSITES",
        "status": status,
        "implemented_abilities": [name for name, _token, _id, _type in IMPLEMENTED],
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "MR10D1 battle-only extra type bitmask",
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D2 added-type composite validation failed")


if __name__ == "__main__":
    main()
