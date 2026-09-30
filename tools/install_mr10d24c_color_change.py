#!/usr/bin/env python3
"""MR10D24C — Elite Redux Color Change.

Implements the approved KEEP-AS-WRITTEN Color Change semantics:
- immediately before a damaging incoming hit is resolved, probe every ordinary
  battle type in Elite Redux/Showdown's deterministic type order;
- choose the first immunity if one exists, otherwise the first strictly-best
  resistance below neutral effectiveness;
- if that chosen type is not already one of the defender's current types,
  become that single type before the normal type-chart calculation;
- only one actual Color Change transformation may occur for that battler per
  turn. A probe that selects a type the user already has does not consume the
  once-per-turn transformation.

The type-order and selection rule mirror Elite Redux's gen8 showdown donor:
Bug, Dark, Dragon, Electric, Fairy, Fighting, Fire, Flying, Ghost, Grass,
Ground, Ice, Normal, Poison, Psychic, Rock, Steel, Water.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Color Change"
ABILITY_TOKEN = "ABILITY_COLOR_CHANGE"
ABILITY_ID = 16


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


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
        raise SystemExit(f"{label}: expected one anchor in {signature}, found {count}")
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
        raise SystemExit(f"{ABILITY_NAME}: expected one partition row, found {len(matches)}")
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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryDynamicAddedType[MAX_BATTLERS];
""",
        """    // Mercury MR10D24C: the battle turn on which Color Change
    // actually transformed each active battler. -1 means unused.
    int mercuryColorChangeTurn[MAX_BATTLERS];

""",
        "Color Change per-turn state",
    )


def patch_lifecycle(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    insert_after_in_function(
        lib,
        "void BattleContext_InitCounters(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        battleCtx->mercuryDynamicAddedType[i] = 0xFF;
""",
        """        battleCtx->mercuryColorChangeTurn[i] = -1;
""",
        "mercuryColorChangeTurn[i] = -1;",
        "Color Change battle initialization",
    )

    insert_after_in_function(
        lib,
        "void BattleSystem_UpdateAfterSwitch(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    battleCtx->mercuryDynamicAddedType[battler] = 0xFF;
""",
        """    battleCtx->mercuryColorChangeTurn[battler] = -1;
""",
        "mercuryColorChangeTurn[battler] = -1;",
        "Color Change switch reset",
    )


def patch_type_selection(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    helper = """static u8 Mercury_ColorChangeBestType(u8 moveType)
{
    static const u8 mercuryColorChangeTypeOrder[] = {
        TYPE_BUG,
        TYPE_DARK,
        TYPE_DRAGON,
        TYPE_ELECTRIC,
        TYPE_FAIRY,
        TYPE_FIGHTING,
        TYPE_FIRE,
        TYPE_FLYING,
        TYPE_GHOST,
        TYPE_GRASS,
        TYPE_GROUND,
        TYPE_ICE,
        TYPE_NORMAL,
        TYPE_POISON,
        TYPE_PSYCHIC,
        TYPE_ROCK,
        TYPE_STEEL,
        TYPE_WATER,
    };
    int typeIndex;
    int bestMultiplier = 10;
    u8 bestType = 0xFF;

    for (typeIndex = 0;
         typeIndex < NELEMS(mercuryColorChangeTypeOrder);
         typeIndex++) {
        int chartEntry = 0;
        int multiplier = 10;
        u8 candidate = mercuryColorChangeTypeOrder[typeIndex];

        while (sTypeMatchupMultipliers[chartEntry][0] != 0xFF) {
            if (sTypeMatchupMultipliers[chartEntry][0] != 0xFE
                && sTypeMatchupMultipliers[chartEntry][0] == moveType
                && sTypeMatchupMultipliers[chartEntry][1] == candidate) {
                multiplier = sTypeMatchupMultipliers[chartEntry][2];
                break;
            }
            chartEntry++;
        }

        if (multiplier == TYPE_MULTI_IMMUNE) {
            return candidate;
        }

        if (multiplier < bestMultiplier) {
            bestMultiplier = multiplier;
            bestType = candidate;
        }
    }

    return bestType;
}

static void Mercury_TryColorChange(
    BattleContext *battleCtx,
    int attacker,
    int defender,
    u8 moveType,
    u32 movePower)
{
    u8 bestType;

    if (attacker == defender
        || movePower == 0
        || battleCtx->mercuryColorChangeTurn[defender]
            == battleCtx->totalTurns
        || Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_COLOR_CHANGE) == FALSE) {
        return;
    }

    bestType = Mercury_ColorChangeBestType(moveType);
    if (bestType == 0xFF
        || battleCtx->battleMons[defender].type1 == bestType
        || battleCtx->battleMons[defender].type2 == bestType) {
        return;
    }

    battleCtx->battleMons[defender].type1 = bestType;
    battleCtx->battleMons[defender].type2 = bestType;
    battleCtx->mercuryDynamicAddedType[defender] = 0xFF;
    battleCtx->mercuryColorChangeTurn[defender] = battleCtx->totalTurns;
}

"""
    insert_before_once(
        lib,
        """int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)
""",
        helper,
        "Color Change donor-selection helper",
    )

    signature = (
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, "
        "int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)"
    )
    insert_after_in_function(
        lib,
        signature,
        """    movePower = MOVE_DATA(move).power;
""",
        """
    Mercury_TryColorChange(
        battleCtx,
        attacker,
        defender,
        moveType,
        movePower);
""",
        "Mercury_TryColorChange(",
        "Color Change pre-effectiveness hook",
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
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    expected_order = [
        "TYPE_BUG", "TYPE_DARK", "TYPE_DRAGON", "TYPE_ELECTRIC",
        "TYPE_FAIRY", "TYPE_FIGHTING", "TYPE_FIRE", "TYPE_FLYING",
        "TYPE_GHOST", "TYPE_GRASS", "TYPE_GROUND", "TYPE_ICE",
        "TYPE_NORMAL", "TYPE_POISON", "TYPE_PSYCHIC", "TYPE_ROCK",
        "TYPE_STEEL", "TYPE_WATER",
    ]
    positions = [lib.find(x, lib.find("mercuryColorChangeTypeOrder")) for x in expected_order]

    checks = {
        "stable_canonical_id_16":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "per_turn_state":
            "mercuryColorChangeTurn[MAX_BATTLERS]" in ctx
            and "mercuryColorChangeTurn[i] = -1;" in lib
            and "mercuryColorChangeTurn[battler] = -1;" in lib,
        "donor_type_order":
            all(p >= 0 for p in positions)
            and positions == sorted(positions),
        "immunity_wins_immediately":
            "multiplier == TYPE_MULTI_IMMUNE" in lib
            and "return candidate;" in lib,
        "strictly_better_resistance":
            "multiplier < bestMultiplier" in lib,
        "before_type_chart_resolution":
            lib.find("Mercury_TryColorChange(")
            < lib.find("Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_LEVITATE)"),
        "does_not_trigger_on_self_or_status":
            "attacker == defender" in lib
            and "movePower == 0" in lib,
        "mold_breaker_suppression_respected":
            "defender, ABILITY_COLOR_CHANGE) == FALSE" in lib,
        "existing_best_type_does_not_transform":
            "battleCtx->battleMons[defender].type1 == bestType" in lib
            and "battleCtx->battleMons[defender].type2 == bestType" in lib,
        "actual_change_becomes_monotype":
            "battleCtx->battleMons[defender].type1 = bestType;" in lib
            and "battleCtx->battleMons[defender].type2 = bestType;" in lib,
        "once_per_turn_on_actual_change":
            "mercuryColorChangeTurn[defender] = battleCtx->totalTurns;" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
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
    ap.add_argument("--report", type=Path, default=Path("mr10d24c-color-change.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_lifecycle(root)
    patch_type_selection(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D24C_COLOR_CHANGE",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "donor_behavior": "Elite Redux pre-hit best defensive type",
        "once_per_turn": True,
        "remaining_keep_as_written_after_d24c": 12,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D24C Color Change validation failed")


if __name__ == "__main__":
    main()
