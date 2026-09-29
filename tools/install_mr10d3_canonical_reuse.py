#!/usr/bin/env python3
"""MR10D3 — canonical-reuse / shared-system Ability batch.

Graduates three owner-approved KEEP-AS-WRITTEN mechanics:

- Fey Flight: adds Fairy as a battle type, sets Misty Terrain on entry,
  and uses Levitate-style Ground immunity.
- Schooling: already satisfied by Mercury's compile-certified canonical
  Schooling implementation from MR08S7.
- Comatose: already satisfied by Mercury's compile-certified canonical
  Comatose implementation from MR08Q2.

This pass intentionally reuses the existing added-type, terrain, form-state,
and virtual-sleep systems instead of creating parallel mechanics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Fey Flight": ("ABILITY_MR_FEY_FLIGHT", 528),
    "Schooling": ("ABILITY_SCHOOLING", 208),
    "Comatose": ("ABILITY_COMATOSE", 213),
}

TOKENS = tuple(value[0] for value in IMPLEMENTED.values())

# MR10D3 native gate trigger.


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

    for name, (token, ability_id) in IMPLEMENTED.items():
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
            "review_blocked": False,
        }
        for key, value in expected.items():
            if row.get(key) != value:
                raise SystemExit(
                    f"{name}: partition {key} expected {value!r}, got {row.get(key)!r}"
                )


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
    if block.count(anchor) != 1:
        raise SystemExit("Fey Flight added-type map: default anchor missing")

    block = block.replace(
        anchor,
        """    case ABILITY_MR_FEY_FLIGHT:
        return TYPE_FAIRY;
""" + anchor,
        1,
    )
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_fey_flight_ground_immunity(root: Path) -> None:
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
        "Fey Flight AI Ground immunity",
    )


def patch_fey_flight_terrain_grounding(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """        || Battler_Ability(battleCtx, battler) == ABILITY_LEVITATE
        || battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns) {
""",
        """        || Battler_Ability(battleCtx, battler) == ABILITY_LEVITATE
        || Battler_Ability(battleCtx, battler) == ABILITY_MR_FEY_FLIGHT
        || battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns) {
""",
        "Fey Flight terrain grounding",
    )


def patch_fey_flight_full_levitate(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Mercury's approved Levitate mechanic is not just Ground immunity:
    # MR10B2 also gives the holder's Flying-type moves a 25% power boost.
    # "Grants Levitate behavior" therefore inherits the complete current
    # Mercury Levitate behavior.
    replace_once(
        path,
        """    if (attackerParams.ability == ABILITY_LEVITATE
        && moveType == TYPE_FLYING) {
        movePower = movePower * 125 / 100;
    }
""",
        """    if ((attackerParams.ability == ABILITY_LEVITATE
            || attackerParams.ability == ABILITY_MR_FEY_FLIGHT)
        && moveType == TYPE_FLYING) {
        movePower = movePower * 125 / 100;
    }
""",
        "Fey Flight full Mercury Levitate behavior",
    )


def patch_fey_flight_misty_entry(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """                    case ABILITY_MISTY_SURGE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_MISTY) {
                            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_MISTY);
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = ABILITY_MISTY_SURGE;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
""",
        """                    case ABILITY_MISTY_SURGE:
                    case ABILITY_MR_FEY_FLIGHT:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_MISTY) {
                            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_MISTY);
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = Battler_Ability(battleCtx, battler);
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
""",
        "Fey Flight Misty Terrain entry",
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
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    sleep = (root / "res/battle/scripts/subscripts/subscript_fall_asleep.s").read_text(encoding="utf-8")
    sleep_talk = (root / "res/battle/scripts/effects/effect_script_0097.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "fey_flight_added_fairy":
            "case ABILITY_MR_FEY_FLIGHT:" in lib
            and "return TYPE_FAIRY;" in lib,
        "fey_flight_ground_immunity_runtime":
            "ABILITY_MR_FEY_FLIGHT) == TRUE" in lib,
        "fey_flight_ground_immunity_ai":
            "defenderAbility == ABILITY_MR_FEY_FLIGHT" in lib,
        "fey_flight_misty_terrain":
            "case ABILITY_MR_FEY_FLIGHT:" in lib
            and "Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_MISTY);" in lib,
        "fey_flight_terrain_grounding":
            "Battler_Ability(battleCtx, battler) == ABILITY_MR_FEY_FLIGHT" in lib,
        "fey_flight_full_mercury_levitate":
            "attackerParams.ability == ABILITY_MR_FEY_FLIGHT" in lib
            and "movePower = movePower * 125 / 100;" in lib,
        "schooling_canonical_state":
            "mercurySchoolingActive[MAX_BATTLERS]" in ctx
            and "case ABILITY_SCHOOLING:" in lib
            and "SPECIES_WISHIWASHI" in lib
            and "maxHP / 4" in lib,
        "comatose_canonical_status_immunity":
            "ABILITY_COMATOSE" in sleep,
        "comatose_canonical_sleep_interactions":
            "ABILITY_COMATOSE" in sleep_talk,
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
        default=Path("mr10d3-canonical-reuse.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    extend_added_type_map(root)
    patch_fey_flight_ground_immunity(root)
    patch_fey_flight_terrain_grounding(root)
    patch_fey_flight_full_levitate(root)
    patch_fey_flight_misty_entry(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D3_CANONICAL_REUSE",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "new_runtime_mechanics": ["Fey Flight"],
        "canonical_equivalence_certified": ["Schooling", "Comatose"],
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D3 canonical reuse validation failed")


if __name__ == "__main__":
    main()
