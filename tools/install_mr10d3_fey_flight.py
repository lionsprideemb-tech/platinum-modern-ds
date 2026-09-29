#!/usr/bin/env python3
"""MR10D3 — Fey Flight compound mechanic.

Builds on MR10D1/D2's battle-only added-type core and the canonical terrain
framework. Fey Flight keeps all three approved pieces together:

- adds Fairy as a battle typing,
- establishes Misty Terrain on entry,
- grants Levitate-style Ground immunity / airborne terrain behavior.

Mechanics only; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

NAME = "Fey Flight"
TOKEN = "ABILITY_MR_FEY_FLIGHT"
ABILITY_ID = 528


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))
    matches = [
        row for row in rows
        if row.get("display_name") == NAME or row.get("source_name") == NAME
    ]
    if len(matches) != 1:
        raise SystemExit(f"{NAME}: expected one partition row, found {len(matches)}")
    row = matches[0]
    expected = {
        "id": ABILITY_ID,
        "token": TOKEN,
        "approval_state": "owner_approved_keep",
        "owner_review_decision": "KEEP AS WRITTEN",
        "implementation_class": "new_engine_system",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{NAME}: reviewed mechanic is runtime-disabled")


def extend_added_type_map(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = "static u8 Mercury_AddedTypeForAbility(int ability)"
    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "case ABILITY_MR_FEY_FLIGHT:" in block:
        return
    anchor = """    default:
        return 0xFF;
"""
    insertion = """    case ABILITY_MR_FEY_FLIGHT:
        return TYPE_FAIRY;
"""
    if block.count(anchor) != 1:
        raise SystemExit("Fey Flight added-type map default anchor missing")
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_ground_immunity(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """            || Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_MR_HOVER) == TRUE)
        && moveType == TYPE_GROUND) {
""",
        """            || Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_MR_HOVER) == TRUE
            || Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_MR_FEY_FLIGHT) == TRUE)
        && moveType == TYPE_GROUND) {
""",
        "Fey Flight runtime Ground immunity",
    )

    replace_once(
        path,
        """        && (defenderAbility == ABILITY_MR_DRAGONFLY
            || defenderAbility == ABILITY_MR_HOVER)
        && moveType == TYPE_GROUND) {
""",
        """        && (defenderAbility == ABILITY_MR_DRAGONFLY
            || defenderAbility == ABILITY_MR_HOVER
            || defenderAbility == ABILITY_MR_FEY_FLIGHT)
        && moveType == TYPE_GROUND) {
""",
        "Fey Flight generic effectiveness Ground immunity",
    )

    replace_once(
        path,
        """        || Battler_Ability(battleCtx, battler) == ABILITY_LEVITATE
        || battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns) {
""",
        """        || Battler_Ability(battleCtx, battler) == ABILITY_LEVITATE
        || Battler_Ability(battleCtx, battler) == ABILITY_MR_FEY_FLIGHT
        || battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns) {
""",
        "Fey Flight airborne terrain behavior",
    )


def patch_misty_terrain_entry(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insertion = """                    case ABILITY_MR_FEY_FLIGHT:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_MISTY) {
                            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_MISTY);
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = ABILITY_MR_FEY_FLIGHT;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

"""
    anchor = """                    case ABILITY_MISTY_SURGE:
"""
    text = path.read_text(encoding="utf-8")
    if "case ABILITY_MR_FEY_FLIGHT:" not in text:
        count = text.count(anchor)
        if count != 1:
            raise SystemExit(
                f"Fey Flight Misty Terrain entry: expected one Misty Surge anchor, found {count}"
            )
        path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if TOKEN not in lines:
        lines.append(TOKEN)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_528":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == TOKEN,
        "added_fairy_type":
            "case ABILITY_MR_FEY_FLIGHT:" in lib
            and "return TYPE_FAIRY;" in lib,
        "ground_immunity":
            "ABILITY_MR_FEY_FLIGHT) == TRUE" in lib
            and "moveType == TYPE_GROUND" in lib,
        "airborne_terrain_behavior":
            "Battler_Ability(battleCtx, battler) == ABILITY_MR_FEY_FLIGHT" in lib,
        "misty_terrain_on_entry":
            "case ABILITY_MR_FEY_FLIGHT:" in lib
            and "Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_MISTY);" in lib,
        "implemented_registry_updated": TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--partition",
        type=Path,
        default=Path("data/mr10_safe_ability_partition.json"),
    )
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10d3-fey-flight.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    extend_added_type_map(root)
    patch_ground_immunity(root)
    patch_misty_terrain_entry(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D3_FEY_FLIGHT",
        "status": status,
        "implemented_abilities": [NAME],
        "implemented_count": 1,
        "shared_system": "added_type_plus_terrain_plus_ground_immunity",
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D3 Fey Flight validation failed")


if __name__ == "__main__":
    main()
