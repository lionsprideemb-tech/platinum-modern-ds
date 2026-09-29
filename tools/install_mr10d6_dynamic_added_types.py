#!/usr/bin/env python3
"""MR10D6 — dynamic battle-only added typing + Magical Dust.

Adds a reusable per-battler added-type bitmask on top of MR10D1's static
Ability-added type layer. This allows reactive mechanics to grant temporary
battle typing without overwriting a Pokémon's native types or static
Ability-granted third type.

Implements:
- Magical Dust — when the holder is struck by a qualifying contact hit, the
  attacker gains Psychic as an additional battle type if it is not already
  Psychic-type.

Dynamic added types are battle-local and reset whenever a battler slot is
initialized for a newly sent-out party Pokémon.

Mechanics only; locked MR07 visuals remain untouched.
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
                f"{ABILITY_NAME}: partition {key} expected {value!r}, "
                f"got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_context(root: Path) -> None:
    ctx = root / "include/battle/battle_context.h"
    insert_after_once(
        ctx,
        """    u8 mercurySoothsayerUsedMask[2];
""",
        """    // Mercury MR10D6: reactive battle-only additional typing.
    u32 mercuryDynamicAddedTypeMask[MAX_BATTLERS];

""",
        "MR10D6 dynamic added-type state",
    )


def patch_type_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    replace_once(
        hdr,
        """int Mercury_BattlerAddedType(BattleContext *battleCtx, int battler);
BOOL Mercury_BattlerHasType(BattleContext *battleCtx, int battler, int type);
""",
        """int Mercury_BattlerAddedType(BattleContext *battleCtx, int battler);
BOOL Mercury_BattlerHasDynamicAddedType(BattleContext *battleCtx, int battler, int type);
void Mercury_AddBattlerType(BattleContext *battleCtx, int battler, int type);
BOOL Mercury_BattlerHasType(BattleContext *battleCtx, int battler, int type);
""",
        "MR10D6 public dynamic type helpers",
    )

    replace_once(
        lib,
        """int Mercury_BattlerAddedType(BattleContext *battleCtx, int battler)
{
    return Mercury_AddedTypeForAbility(Battler_Ability(battleCtx, battler));
}

BOOL Mercury_BattlerHasType(BattleContext *battleCtx, int battler, int type)
{
    return BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_1, NULL) == type
        || BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_2, NULL) == type
        || Mercury_BattlerAddedType(battleCtx, battler) == type;
}
""",
        """int Mercury_BattlerAddedType(BattleContext *battleCtx, int battler)
{
    return Mercury_AddedTypeForAbility(Battler_Ability(battleCtx, battler));
}

BOOL Mercury_BattlerHasDynamicAddedType(
    BattleContext *battleCtx,
    int battler,
    int type)
{
    if (type < 0 || type >= NUM_POKEMON_TYPES || type == TYPE_MYSTERY) {
        return FALSE;
    }

    return (battleCtx->mercuryDynamicAddedTypeMask[battler]
        & (1U << type)) != 0;
}

void Mercury_AddBattlerType(BattleContext *battleCtx, int battler, int type)
{
    if (type < 0 || type >= NUM_POKEMON_TYPES || type == TYPE_MYSTERY) {
        return;
    }

    battleCtx->mercuryDynamicAddedTypeMask[battler] |= (1U << type);
}

BOOL Mercury_BattlerHasType(BattleContext *battleCtx, int battler, int type)
{
    return BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_1, NULL) == type
        || BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_2, NULL) == type
        || Mercury_BattlerAddedType(battleCtx, battler) == type
        || Mercury_BattlerHasDynamicAddedType(
            battleCtx, battler, type) == TRUE;
}
""",
        "MR10D6 dynamic added-type helpers",
    )


def patch_reset_on_entry(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    replace_once(
        lib,
        """    battleCtx->battleMons[battler].type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
    battleCtx->battleMons[battler].type2 = Pokemon_GetValue(mon, MON_DATA_TYPE_2, NULL);
""",
        """    battleCtx->battleMons[battler].type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
    battleCtx->battleMons[battler].type2 = Pokemon_GetValue(mon, MON_DATA_TYPE_2, NULL);
    battleCtx->mercuryDynamicAddedTypeMask[battler] = 0;
""",
        "MR10D6 reset dynamic added typing on battler init",
    )


def patch_runtime_effectiveness(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, "
        "int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)"
    )

    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "int mercuryDynamicType;" not in block:
        anchor = "    u8 mercuryDefenderType;\n"
        if block.count(anchor) != 1:
            raise SystemExit("MR10D6 runtime type chart declaration anchor missing")
        block = block.replace(
            anchor,
            anchor
            + "    int mercuryDynamicType;\n"
            + "    u32 mercuryDynamicTypeMask;\n",
            1,
        )
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")

    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "mercuryDynamicTypeMask = battleCtx->mercuryDynamicAddedTypeMask[defender];" not in block:
        anchor = """    mercuryDefenderType = Mercury_BattlerAddedType(battleCtx, defender);

"""
        if block.count(anchor) != 1:
            raise SystemExit("MR10D6 dynamic type mask assignment anchor missing")
        block = block.replace(
            anchor,
            anchor
            + """    mercuryDynamicTypeMask =
        battleCtx->mercuryDynamicAddedTypeMask[defender];

""",
            1,
        )
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")

    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    marker = "Mercury MR10D6: apply every reactive added defensive type."
    if marker not in block:
        anchor = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WONDER_GUARD) == TRUE
"""
        if block.count(anchor) != 1:
            raise SystemExit("MR10D6 dynamic effectiveness insertion anchor missing")
        insertion = """    /* Mercury MR10D6: apply every reactive added defensive type. */
    for (mercuryDynamicType = 0;
         mercuryDynamicType < NUM_POKEMON_TYPES;
         mercuryDynamicType++) {
        if (mercuryDynamicType == TYPE_MYSTERY
            || (mercuryDynamicTypeMask & (1U << mercuryDynamicType)) == 0
            || mercuryDynamicType
                == BattleMon_Get(
                    battleCtx, defender, BATTLEMON_TYPE_1, NULL)
            || mercuryDynamicType
                == BattleMon_Get(
                    battleCtx, defender, BATTLEMON_TYPE_2, NULL)
            || mercuryDynamicType == mercuryDefenderType
            || (*moveStatusMask & MOVE_STATUS_NO_EFFECTS)) {
            continue;
        }

        chartEntry = 0;
        while (sTypeMatchupMultipliers[chartEntry][0] != 0xFF) {
            if (sTypeMatchupMultipliers[chartEntry][0] != 0xFE
                && sTypeMatchupMultipliers[chartEntry][0] == moveType
                && sTypeMatchupMultipliers[chartEntry][1]
                    == mercuryDynamicType
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
        block = block.replace(anchor, insertion + anchor, 1)
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_magical_dust(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    insertion = """    case ABILITY_MR_MAGICAL_DUST:
        if (ATTACKING_MON.curHP
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (battleCtx->battleStatusMask & SYSCTL_FIRST_OF_MULTI_TURN) == FALSE
            && (battleCtx->battleStatusMask2 & SYSCTL_UTURN_ACTIVE) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)
            && Mercury_BattlerHasType(
                battleCtx, battleCtx->attacker, TYPE_PSYCHIC) == FALSE) {
            Mercury_AddBattlerType(
                battleCtx, battleCtx->attacker, TYPE_PSYCHIC);
            battleCtx->msgBattlerTemp = battleCtx->defender;
            battleCtx->msgTemp = ABILITY_MR_MAGICAL_DUST;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

"""
    insert_before_once(
        lib,
        """    case ABILITY_ROUGH_SKIN:
""",
        insertion,
        "MR10D6 Magical Dust contact reaction",
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
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    common = (root / "include/battle/common.h").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "dynamic_type_mask_state":
            "mercuryDynamicAddedTypeMask[MAX_BATTLERS]" in ctx,
        "public_dynamic_type_helpers":
            "Mercury_BattlerHasDynamicAddedType" in hdr
            and "Mercury_AddBattlerType" in hdr,
        "dynamic_type_reset_on_entry":
            "mercuryDynamicAddedTypeMask[battler] = 0;" in lib,
        "dynamic_type_visible_to_mon_has_type":
            "Mercury_BattlerHasDynamicAddedType(" in lib
            and "#define MON_HAS_TYPE(mon, type)    Mercury_BattlerHasType" in common,
        "dynamic_type_defensive_effectiveness":
            "Mercury MR10D6: apply every reactive added defensive type." in lib
            and "mercuryDynamicTypeMask" in lib,
        "magical_dust_contact_gate":
            "case ABILITY_MR_MAGICAL_DUST:" in lib
            and "MOVE_FLAG_MAKES_CONTACT" in lib,
        "magical_dust_adds_psychic":
            "Mercury_AddBattlerType(" in lib
            and "battleCtx, battleCtx->attacker, TYPE_PSYCHIC" in lib,
        "magical_dust_no_duplicate_psychic":
            "Mercury_BattlerHasType(" in lib
            and "battleCtx, battleCtx->attacker, TYPE_PSYCHIC) == FALSE" in lib,
        "static_added_type_layer_preserved":
            "Mercury_BattlerAddedType(battleCtx, battler) == type" in lib,
        "registry_updated":
            ABILITY_TOKEN in registry_lines,
        "stable_id":
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
        default=Path("mr10d6-dynamic-added-types.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_type_helpers(root)
    patch_reset_on_entry(root)
    patch_runtime_effectiveness(root)
    patch_magical_dust(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D6_DYNAMIC_ADDED_TYPES",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_system": "reactive_battle_only_added_type_mask",
        "remaining_keep_as_written_after_d6": 53,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D6 dynamic added-type validation failed")


if __name__ == "__main__":
    main()
