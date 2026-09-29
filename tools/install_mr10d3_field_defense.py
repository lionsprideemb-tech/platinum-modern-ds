#!/usr/bin/env python3
"""MR10D3 — timed defense + Fey Flight KEEP-AS-WRITTEN batch.

Graduates three reviewed mechanics on top of the green MR10D2 stack:

- Prismatic Pelt — 3-turn Prismatic Veil, 25% SE damage reduction, first
  qualifying hit raises the matching defense by one stage.
- Soothsayer — first entry only, for three turns damaging attacks that are not
  otherwise immune are treated as resisted (exactly 0.5x type effectiveness).
- Fey Flight — adds Fairy battle typing, sets Misty Terrain on entry, and
  grants Levitate behavior.

This pass is mechanics-only and does not touch locked MR07 visuals.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Prismatic Pelt": ("ABILITY_PRISMATIC_PELT", 316),
    "Soothsayer": ("ABILITY_MR_SOOTHSAYER", 423),
    "Fey Flight": ("ABILITY_MR_FEY_FLIGHT", 528),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


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


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
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


def patch_context_and_entry_state(root: Path) -> None:
    ctx = root / "include/battle/battle_context.h"
    insert_after_once(
        ctx,
        """    u8 mercuryAbilityGeneratedAction;
""",
        """    // Mercury MR10D3: timed entry defenses.
    int mercuryPrismaticUntilTurn[MAX_BATTLERS];
    u8 mercuryPrismaticBoostUsed[MAX_BATTLERS];
    int mercurySoothsayerUntilTurn[MAX_BATTLERS];
    u8 mercurySoothsayerUsedMask[2];

""",
        "MR10D3 timed-defense context state",
    )

    lib = root / "src/battle/battle_lib.c"
    insertion = """    battleCtx->mercuryPrismaticUntilTurn[battler] = -1;
    battleCtx->mercuryPrismaticBoostUsed[battler] = FALSE;
    battleCtx->mercurySoothsayerUntilTurn[battler] = -1;

    if (Battler_Ability(battleCtx, battler) == ABILITY_PRISMATIC_PELT) {
        battleCtx->mercuryPrismaticUntilTurn[battler] =
            battleCtx->totalTurns + 3;
    }

    if (Battler_Ability(battleCtx, battler) == ABILITY_MR_SOOTHSAYER) {
        int mercurySoothsayerSide =
            BattleSystem_GetBattlerSide(battleSys, battler);
        int mercurySoothsayerSlot = battleCtx->selectedPartySlot[battler];

        if (mercurySoothsayerSlot >= 0 && mercurySoothsayerSlot < 6) {
            u8 mercurySoothsayerBit = (u8)(1 << mercurySoothsayerSlot);

            if ((battleCtx->mercurySoothsayerUsedMask[mercurySoothsayerSide]
                    & mercurySoothsayerBit) == 0) {
                battleCtx->mercurySoothsayerUsedMask[mercurySoothsayerSide]
                    |= mercurySoothsayerBit;
                battleCtx->mercurySoothsayerUntilTurn[battler] =
                    battleCtx->totalTurns + 3;
            }
        }
    }
"""
    insert_after_once(
        lib,
        """    battleCtx->mercuryPatternTarget[battler] = 0;
""",
        insertion,
        "MR10D3 entry-state initialization",
    )


def patch_fey_flight(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    # Extend MR10D's static Ability-added type map.
    signature = "static u8 Mercury_AddedTypeForAbility(int ability)"
    text = lib.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "case ABILITY_MR_FEY_FLIGHT:" not in block:
        anchor = """    default:
        return 0xFF;
"""
        if block.count(anchor) != 1:
            raise SystemExit("Fey Flight: added-type map default anchor missing")
        block = block.replace(
            anchor,
            """    case ABILITY_MR_FEY_FLIGHT:
        return TYPE_FAIRY;
""" + anchor,
            1,
        )
        lib.write_text(text[:start] + block + text[end:], encoding="utf-8")

    # Ground immunity in live type chart.
    replace_once(
        lib,
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
        "Fey Flight live Ground immunity",
    )

    # AI effectiveness mirror for the static Levitate behavior.
    replace_once(
        lib,
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

    # Terrain grounding helper must treat Fey Flight exactly like Levitate.
    replace_once(
        lib,
        """        || Battler_Ability(battleCtx, battler) == ABILITY_LEVITATE
        || battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns) {
""",
        """        || Battler_Ability(battleCtx, battler) == ABILITY_LEVITATE
        || Battler_Ability(battleCtx, battler) == ABILITY_MR_FEY_FLIGHT
        || battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns) {
""",
        "Fey Flight terrain grounding",
    )

    # Reuse the canonical Misty Surge entry lane.
    replace_once(
        lib,
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


def patch_timed_damage_rules(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, "
        "int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)"
    )

    # Keep the post-STAB/pre-effectiveness value so Soothsayer can force an
    # exact resisted result rather than stacking another arbitrary multiplier.
    text = lib.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "int mercuryDamageBeforeEffectiveness;" not in block:
        anchor = "    int totalMul;\n"
        if block.count(anchor) != 1:
            raise SystemExit("Soothsayer: declaration anchor missing")
        block = block.replace(
            anchor,
            anchor + "    int mercuryDamageBeforeEffectiveness;\n",
            1,
        )
        lib.write_text(text[:start] + block + text[end:], encoding="utf-8")

    insert_before_in_function(
        lib,
        signature,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_LEVITATE) == TRUE
""",
        """    mercuryDamageBeforeEffectiveness = damage;

""",
        "mercuryDamageBeforeEffectiveness = damage;",
        "Soothsayer pre-effectiveness damage capture",
    )

    insertion = """    if (battleCtx->mercurySoothsayerUntilTurn[defender]
            > battleCtx->totalTurns
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_SOOTHSAYER) == TRUE
        && movePower
        && (*moveStatusMask & MOVE_STATUS_NO_EFFECTS) == FALSE) {
        damage = mercuryDamageBeforeEffectiveness / 2;
        *moveStatusMask &= ~MOVE_STATUS_SUPER_EFFECTIVE;
        *moveStatusMask &= ~MOVE_STATUS_NOT_VERY_EFFECTIVE;
        *moveStatusMask |= MOVE_STATUS_NOT_VERY_EFFECTIVE;
    }

    if (battleCtx->mercuryPrismaticUntilTurn[defender]
            > battleCtx->totalTurns
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_PRISMATIC_PELT) == TRUE
        && movePower
        && (*moveStatusMask & MOVE_STATUS_SUPER_EFFECTIVE)) {
        damage = damage * 75 / 100;
    }

"""
    insert_before_in_function(
        lib,
        signature,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WONDER_GUARD) == TRUE
""",
        insertion,
        "mercurySoothsayerUntilTurn[defender]",
        "Prismatic Pelt / Soothsayer effectiveness override",
    )


def patch_prismatic_reaction(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    insertion = """    case ABILITY_PRISMATIC_PELT:
        if (DEFENDING_MON.curHP
            && battleCtx->mercuryPrismaticUntilTurn[battleCtx->defender]
                > battleCtx->totalTurns
            && battleCtx->mercuryPrismaticBoostUsed[battleCtx->defender] == FALSE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_SUPER_EFFECTIVE)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            battleCtx->mercuryPrismaticBoostUsed[battleCtx->defender] = TRUE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;

            if (MOVE_DATA(battleCtx->moveCur).class == CLASS_PHYSICAL) {
                battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE;
            } else {
                battleCtx->sideEffectParam =
                    MOVE_SUBSCRIPT_PTR_SP_DEFENSE_UP_1_STAGE;
            }

            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;

"""
    insert_before_once(
        lib,
        """    case ABILITY_AFTERMATH:
""",
        insertion,
        "Prismatic Pelt first SE-hit defense adaptation",
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
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "timed_defense_state":
            "mercuryPrismaticUntilTurn[MAX_BATTLERS]" in ctx
            and "mercurySoothsayerUsedMask[2]" in ctx,
        "prismatic_three_turn_entry":
            "ABILITY_PRISMATIC_PELT" in lib
            and "battleCtx->totalTurns + 3" in lib,
        "prismatic_se_reduction":
            "ABILITY_PRISMATIC_PELT) == TRUE" in lib
            and "damage = damage * 75 / 100;" in lib,
        "prismatic_first_hit_adaptation":
            "case ABILITY_PRISMATIC_PELT:" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in lib
            and "MOVE_SUBSCRIPT_PTR_SP_DEFENSE_UP_1_STAGE" in lib,
        "soothsayer_first_entry_mask":
            "mercurySoothsayerUsedMask" in lib
            and "mercurySoothsayerBit" in lib,
        "soothsayer_exact_resist":
            "mercuryDamageBeforeEffectiveness / 2" in lib
            and "ABILITY_MR_SOOTHSAYER) == TRUE" in lib,
        "fey_flight_added_fairy":
            "case ABILITY_MR_FEY_FLIGHT:" in lib
            and "return TYPE_FAIRY;" in lib,
        "fey_flight_ground_immunity":
            "ABILITY_MR_FEY_FLIGHT) == TRUE" in lib
            and "defenderAbility == ABILITY_MR_FEY_FLIGHT" in lib,
        "fey_flight_misty_terrain":
            "case ABILITY_MR_FEY_FLIGHT:" in lib
            and "MERCURY_TERRAIN_MISTY" in lib,
        "fey_flight_not_grounded":
            "Battler_Ability(battleCtx, battler) == ABILITY_MR_FEY_FLIGHT" in lib,
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
        default=Path("mr10d3-field-defense.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_and_entry_state(root)
    patch_fey_flight(root)
    patch_timed_damage_rules(root)
    patch_prismatic_reaction(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D3_FIELD_DEFENSE",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "remaining_keep_as_written_after_d3": 58,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D3 field-defense validation failed")


if __name__ == "__main__":
    main()
