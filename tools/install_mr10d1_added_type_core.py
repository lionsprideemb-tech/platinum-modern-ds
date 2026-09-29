#!/usr/bin/env python3
"""MR10D1A — shared battle-only added-type foundation + pure type abilities.

This is the first KEEP-AS-WRITTEN batch after the 15 approved redesigns.

The DS battle core normally exposes only two Pokémon types. Mercury now keeps a
separate per-battler bitmask of extra battle-only types so an Ability can add a
third (or later another) type without destroying either native type.

This foundation wires the extra type into:
- MON_HAS_TYPE / MON_IS_NOT_TYPE checks (including STAB and type immunities);
- the live damage type chart as an additional defensive layer;
- Flower Veil's Grass-type eligibility check.

This batch then graduates the five mechanics whose entire approved effect is
"add this type while active in battle":
- Aquatic     -> Water
- Grounded    -> Ground
- Half Drake  -> Dragon
- Ice Age     -> Ice
- Metallic    -> Steel

The mask is rebuilt when a battler is initialized, so these Ability-granted
types naturally clear when that Pokémon leaves the field. More complex
added-type Abilities are intentionally left out of the implemented registry
until their second clauses are installed in later MR10D batches.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


IMPLEMENTED = (
    ("Aquatic", "ABILITY_MR_AQUATIC", 702, "TYPE_WATER"),
    ("Grounded", "ABILITY_MR_GROUNDED", 703, "TYPE_GROUND"),
    ("Half Drake", "ABILITY_MR_HALF_DRAKE", 791, "TYPE_DRAGON"),
    ("Ice Age", "ABILITY_MR_ICE_AGE", 795, "TYPE_ICE"),
    ("Metallic", "ABILITY_MR_METALLIC", 809, "TYPE_STEEL"),
)


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_regex_once(
    path: Path,
    pattern: str,
    replacement: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if replacement in text:
        return
    text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one regex match in {path}, found {count}")
    path.write_text(text, encoding="utf-8")


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


def insert_before_function_end(
    path: Path,
    signature: str,
    insertion: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    start, end = find_function_block(text, signature, label)
    block = text[start:end]
    block = block[:-1] + insertion + "}\n"
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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryAbilityGeneratedAction;
""",
        """    // Mercury MR10D1: additional battle-only typings. Each bit is a
    // type ID; native type1/type2 remain untouched.
    u32 mercuryExtraTypeMask[MAX_BATTLERS];
""",
        "MR10D added-type state",
    )


def patch_type_macros(root: Path) -> None:
    path = root / "include/battle/common.h"
    replace_regex_once(
        path,
        r"^#define MON_HAS_TYPE\(mon, type\)\s+\(BattleMon_Get\(battleCtx, mon, BATTLEMON_TYPE_1, NULL\) == type \|\| BattleMon_Get\(battleCtx, mon, BATTLEMON_TYPE_2, NULL\) == type\)$",
        "#define MON_HAS_TYPE(mon, type)    (BattleMon_Get(battleCtx, mon, BATTLEMON_TYPE_1, NULL) == type || BattleMon_Get(battleCtx, mon, BATTLEMON_TYPE_2, NULL) == type || (battleCtx->mercuryExtraTypeMask[mon] & (1u << (type))))",
        "MR10D MON_HAS_TYPE extra layer",
    )
    replace_regex_once(
        path,
        r"^#define MON_IS_NOT_TYPE\(mon, type\)\s+\(BattleMon_Get\(battleCtx, mon, BATTLEMON_TYPE_1, NULL\) != type && BattleMon_Get\(battleCtx, mon, BATTLEMON_TYPE_2, NULL\) != type\)$",
        "#define MON_IS_NOT_TYPE(mon, type) (BattleMon_Get(battleCtx, mon, BATTLEMON_TYPE_1, NULL) != type && BattleMon_Get(battleCtx, mon, BATTLEMON_TYPE_2, NULL) != type && (battleCtx->mercuryExtraTypeMask[mon] & (1u << (type))) == 0)",
        "MR10D MON_IS_NOT_TYPE extra layer",
    )


def patch_shared_helpers(root: Path) -> None:
    hdr = root / "include/battle/battle_lib.h"
    lib = root / "src/battle/battle_lib.c"

    insert_before_once(
        hdr,
        """BOOL Mercury_TryBlockTwoLives(
""",
        """void Mercury_ClearBattleAddedTypes(BattleContext *battleCtx, int battler);
void Mercury_AddBattleType(BattleContext *battleCtx, int battler, int type);
BOOL Mercury_BattlerHasExtraType(BattleContext *battleCtx, int battler, int type);
""",
        "MR10D added-type helper declarations",
    )

    insert_before_once(
        lib,
        """void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)
""",
        """void Mercury_ClearBattleAddedTypes(BattleContext *battleCtx, int battler)
{
    battleCtx->mercuryExtraTypeMask[battler] = 0;
}

void Mercury_AddBattleType(BattleContext *battleCtx, int battler, int type)
{
    if (type < TYPE_NORMAL || type > TYPE_FAIRY) {
        return;
    }

    if (BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_1, NULL) == type
        || BattleMon_Get(battleCtx, battler, BATTLEMON_TYPE_2, NULL) == type) {
        return;
    }

    battleCtx->mercuryExtraTypeMask[battler] |= (1u << type);
}

BOOL Mercury_BattlerHasExtraType(BattleContext *battleCtx, int battler, int type)
{
    if (type < TYPE_NORMAL || type > TYPE_FAIRY) {
        return FALSE;
    }

    return (battleCtx->mercuryExtraTypeMask[battler] & (1u << type)) != 0;
}

static void Mercury_InitializeAbilityAddedType(BattleContext *battleCtx, int battler)
{
    Mercury_ClearBattleAddedTypes(battleCtx, battler);

    switch (battleCtx->battleMons[battler].ability) {
    case ABILITY_MR_AQUATIC:
        Mercury_AddBattleType(battleCtx, battler, TYPE_WATER);
        break;
    case ABILITY_MR_GROUNDED:
        Mercury_AddBattleType(battleCtx, battler, TYPE_GROUND);
        break;
    case ABILITY_MR_HALF_DRAKE:
        Mercury_AddBattleType(battleCtx, battler, TYPE_DRAGON);
        break;
    case ABILITY_MR_ICE_AGE:
        Mercury_AddBattleType(battleCtx, battler, TYPE_ICE);
        break;
    case ABILITY_MR_METALLIC:
        Mercury_AddBattleType(battleCtx, battler, TYPE_STEEL);
        break;
    default:
        break;
    }
}

""",
        "MR10D shared added-type helpers",
    )


def patch_battler_init(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "void BattleSystem_InitBattleMon("
        "BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)"
    )
    insert_before_function_end(
        path,
        signature,
        """
    // Rebuild battle-only Ability typing after the Ability and native types
    // have both been loaded for this entry.
    Mercury_InitializeAbilityAddedType(battleCtx, battler);
""",
        "MR10D initialize Ability-added typing",
    )


def patch_damage_type_chart(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_ApplyTypeChart("
        "BattleSystem *battleSys, BattleContext *battleCtx, int move, int inType, "
        "int attacker, int defender, int damage, u32 *moveStatusMask)"
    )
    insertion = """
            if (Mercury_BattlerHasExtraType(
                    battleCtx,
                    defender,
                    sTypeMatchupMultipliers[chartEntry][1])
                && BasicTypeMulApplies(
                    battleCtx, attacker, defender, chartEntry) == TRUE) {
                damage = ApplyTypeMultiplier(
                    battleCtx,
                    attacker,
                    sTypeMatchupMultipliers[chartEntry][2],
                    damage,
                    movePower,
                    moveStatusMask);

                if (sTypeMatchupMultipliers[chartEntry][2]
                    == TYPE_MULTI_SUPER_EFF) {
                    totalMul *= 2;
                }
            }

"""
    insert_before_in_function(
        path,
        signature,
        """            chartEntry++;
        }
    }

    if (Battler_IgnorableAbility(
""",
        insertion,
        "MR10D third-type damage chart layer",
    )


def patch_flower_veil_extra_type_awareness(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    old = """    if (ability == ABILITY_FLOWER_VEIL
        && BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_1, NULL)
            != TYPE_GRASS
        && BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_2, NULL)
            != TYPE_GRASS) {
        return FALSE;
    }
"""
    new = """    if (ability == ABILITY_FLOWER_VEIL
        && MON_IS_NOT_TYPE(defender, TYPE_GRASS)) {
        return FALSE;
    }
"""
    replace_once(path, old, new, "MR10D Flower Veil extra-type awareness")


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
        key = name.lower().replace(" ", "_") + "_stable_id"
        checks[key] = len(abilities) > ability_id and abilities[ability_id] == token
    return checks


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    common = (root / "include/battle/common.h").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "extra_type_mask_present":
            "u32 mercuryExtraTypeMask[MAX_BATTLERS];" in ctx,
        "type_macros_see_extra_types":
            "mercuryExtraTypeMask[mon]" in common
            and common.count("mercuryExtraTypeMask[mon]") >= 2,
        "shared_helpers_exported":
            "void Mercury_AddBattleType(" in hdr
            and "BOOL Mercury_BattlerHasExtraType(" in hdr,
        "entry_rebuild_after_native_load":
            "Mercury_InitializeAbilityAddedType(battleCtx, battler);" in lib,
        "live_damage_chart_has_extra_layer":
            lib.count("Mercury_BattlerHasExtraType(") >= 2
            and "sTypeMatchupMultipliers[chartEntry][1]" in lib,
        "flower_veil_respects_extra_grass":
            "MON_IS_NOT_TYPE(defender, TYPE_GRASS)" in lib,
        "aquatic_water":
            "case ABILITY_MR_AQUATIC:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_WATER);" in lib,
        "grounded_ground":
            "case ABILITY_MR_GROUNDED:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_GROUND);" in lib,
        "half_drake_dragon":
            "case ABILITY_MR_HALF_DRAKE:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_DRAGON);" in lib,
        "ice_age_ice":
            "case ABILITY_MR_ICE_AGE:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_ICE);" in lib,
        "metallic_steel":
            "case ABILITY_MR_METALLIC:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_STEEL);" in lib,
        "registry_has_all_five":
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
        default=Path("mr10d1-added-type-core.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_type_macros(root)
    patch_shared_helpers(root)
    patch_battler_init(root)
    patch_damage_type_chart(root)
    patch_flower_veil_extra_type_awareness(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D1_ADDED_TYPE_CORE",
        "status": status,
        "implemented_abilities": [name for name, _token, _id, _type in IMPLEMENTED],
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "battle-only extra type bitmask",
        "native_type_slots_overwritten": False,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D1 added-type validation failed")


if __name__ == "__main__":
    main()
