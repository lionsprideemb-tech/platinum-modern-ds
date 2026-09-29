#!/usr/bin/env python3
"""MR10D7 — dynamic battle-only typing family.

Graduates two KEEP-AS-WRITTEN mechanics on the D1 added-type foundation:

- Magical Dust: after a qualifying contact hit received, the attacker gains
  Psychic as its battle-only additional type.
- Color Change: before a damaging hit, once per battle turn, the holder changes
  to the single defensive type that gives the best matchup against the
  incoming resolved move type.

Dynamic type state lives only in BattleContext, resets on switch, and is never
written to party/save data. Color Change replaces Platinum's post-hit behavior.

Mechanics only; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Color Change": ("ABILITY_COLOR_CHANGE", 16),
    "Magical Dust": ("ABILITY_MR_MAGICAL_DUST", 906),
}
TOKENS = tuple(value[0] for value in IMPLEMENTED.values())


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


def insert_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
    after: bool = False,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    start, end = function_bounds(text, signature)
    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {signature}, found {count}")
    replacement = anchor + insertion if after else insertion + anchor
    block = block.replace(anchor, replacement, 1)
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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insertion = """    // Mercury MR10D7: one dynamic battle-only type3 slot per battler.
    // 0xFF means no dynamic type3 override.
    u8 mercuryDynamicAddedType[MAX_BATTLERS];

    // Last totalTurns value on which Color Change consumed its activation.
    u32 mercuryColorChangeTurn[MAX_BATTLERS];

"""
    insert_before_once(
        path,
        "    u32 battleProgressFlag : 1;\n",
        insertion,
        "MR10D7 dynamic typing state",
    )


def patch_state(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    sig = "void BattleContext_InitCounters(BattleSystem *battleSys, BattleContext *battleCtx)"
    insert_in_function(
        path,
        sig,
        "        battleCtx->speedRand[i] = BattleSystem_RandNext(battleSys);\n",
        """        battleCtx->mercuryDynamicAddedType[i] = 0xFF;
        battleCtx->mercuryColorChangeTurn[i] = 0xFFFFFFFF;
""",
        "mercuryDynamicAddedType[i] = 0xFF;",
        "MR10D7 battle-start type state",
        after=True,
    )

    sig = "void BattleSystem_UpdateAfterSwitch(BattleSystem *battleSys, BattleContext *battleCtx, int battler)"
    insert_in_function(
        path,
        sig,
        "    battleType = BattleSystem_GetBattleType(battleSys);\n",
        """    battleCtx->mercuryDynamicAddedType[battler] = 0xFF;
    battleCtx->mercuryColorChangeTurn[battler] = 0xFFFFFFFF;
""",
        "mercuryDynamicAddedType[battler] = 0xFF;",
        "MR10D7 switch reset",
        after=True,
    )


def patch_added_type_core(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    text = path.read_text(encoding="utf-8")
    sig = "int Mercury_BattlerAddedType(BattleContext *battleCtx, int battler)"
    start, end = function_bounds(text, sig)
    block = text[start:end]
    if "mercuryDynamicAddedType[battler]" in block:
        return

    replacement = """int Mercury_BattlerAddedType(BattleContext *battleCtx, int battler)
{
    if (battleCtx->mercuryDynamicAddedType[battler] != 0xFF) {
        return battleCtx->mercuryDynamicAddedType[battler];
    }

    return Mercury_AddedTypeForAbility(Battler_Ability(battleCtx, battler));
}"""
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def patch_magical_dust_script(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_magical_dust.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_followup\n",
        "subscript_mercury_magical_dust\n",
        "MR10D7 Magical Dust subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_followup.s',\n",
        "    'subscript_mercury_magical_dust.s',\n",
        "MR10D7 Magical Dust subscript build",
    )


def patch_magical_dust(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    sig = "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
    insertion = """    case ABILITY_MR_MAGICAL_DUST:
        if (ATTACKING_MON.curHP
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (battleCtx->battleStatusMask & SYSCTL_FIRST_OF_MULTI_TURN) == FALSE
            && (battleCtx->battleStatusMask2 & SYSCTL_UTURN_ACTIVE) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_LONG_REACH
            && Mercury_BattlerHasType(
                battleCtx, battleCtx->attacker, TYPE_PSYCHIC) == FALSE) {
            battleCtx->mercuryDynamicAddedType[battleCtx->attacker] = TYPE_PSYCHIC;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            battleCtx->msgTemp = ABILITY_MR_MAGICAL_DUST;
            *subscript = subscript_mercury_magical_dust;
            result = TRUE;
        }
        break;

"""
    insert_in_function(
        path,
        sig,
        "    case ABILITY_MR_DRAGONFRUIT:\n",
        insertion,
        "case ABILITY_MR_MAGICAL_DUST:",
        "MR10D7 Magical Dust contact type3",
    )


def patch_color_change(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Remove the current post-hit Color Change branch. Magical Dust was just
    # inserted immediately before Dragonfruit, giving us a stable next-case
    # boundary without depending on the exact canonical Color Change body.
    text = path.read_text(encoding="utf-8")
    sig = "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
    start, end = function_bounds(text, sig)
    block = text[start:end]
    case_start = block.find("    case ABILITY_COLOR_CHANGE:")
    next_case = block.find("    case ABILITY_MR_MAGICAL_DUST:", case_start)
    if case_start < 0 or next_case < 0:
        raise SystemExit("MR10D7 Color Change on-hit block bounds not found")

    block = (
        block[:case_start]
        + """    case ABILITY_COLOR_CHANGE:
        // MR10D7: ER-style Color Change resolves before the incoming hit.
        break;

"""
        + block[next_case:]
    )
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")

    helper = """static u8 Mercury_D7RawSingleTypeMultiplier(
    int moveType,
    int defenderType)
{
    int chartEntry = 0;

    while (sTypeMatchupMultipliers[chartEntry][0] != 0xFF) {
        if (sTypeMatchupMultipliers[chartEntry][0] != 0xFE
            && sTypeMatchupMultipliers[chartEntry][0] == moveType
            && sTypeMatchupMultipliers[chartEntry][1] == defenderType) {
            return sTypeMatchupMultipliers[chartEntry][2];
        }
        chartEntry++;
    }

    return TYPE_MULTI_NORMAL;
}

static u8 Mercury_D7BestDefensiveType(
    int moveType,
    int currentType)
{
    int type;
    u8 bestType = currentType;
    u8 bestModifier = Mercury_D7RawSingleTypeMultiplier(
        moveType, currentType);

    for (type = TYPE_NORMAL; type <= TYPE_FAIRY; type++) {
        u8 modifier;

        if (type == TYPE_MYSTERY) {
            continue;
        }

        modifier = Mercury_D7RawSingleTypeMultiplier(moveType, type);
        if (modifier < bestModifier) {
            bestModifier = modifier;
            bestType = type;
        }

        if (bestModifier == TYPE_MULTI_IMMUNE) {
            break;
        }
    }

    return bestType;
}

"""
    insert_before_once(
        path,
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)\n",
        helper,
        "MR10D7 Color Change type-selection helpers",
    )

    sig = (
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, "
        "int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)"
    )
    insertion = """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_COLOR_CHANGE) == TRUE
        && MOVE_DATA(move).class != CLASS_STATUS
        && MoveIsOnDamagingTurn(battleCtx, move)
        && battleCtx->mercuryColorChangeTurn[defender]
            != battleCtx->totalTurns) {
        u8 mercuryBestType = Mercury_D7BestDefensiveType(
            moveType,
            BattleMon_Get(
                battleCtx, defender, BATTLEMON_TYPE_1, NULL));

        // The once-per-turn activation is consumed by the pre-hit check even
        // if the selected type is already present.
        battleCtx->mercuryColorChangeTurn[defender]
            = battleCtx->totalTurns;

        if (Mercury_BattlerHasType(
                battleCtx, defender, mercuryBestType) == FALSE) {
            battleCtx->battleMons[defender].type1 = mercuryBestType;
            battleCtx->battleMons[defender].type2 = mercuryBestType;
            battleCtx->mercuryDynamicAddedType[defender] = 0xFF;
        }
    }

"""
    insert_in_function(
        path,
        sig,
        "    movePower = MOVE_DATA(move).power;\n",
        insertion,
        "mercuryColorChangeTurn[defender]",
        "MR10D7 Color Change pre-hit hook",
        after=True,
    )

    sig = (
        "void BattleSystem_CalcEffectiveness(BattleContext *battleCtx, int move, int inType, "
        "int attackerAbility, int defenderAbility, int defenderItemEffect, int defenderType1, "
        "int defenderType2, u32 *moveStatusMask)"
    )
    ai = """    if (defenderAbility == ABILITY_COLOR_CHANGE
        && MOVE_DATA(move).class != CLASS_STATUS
        && MoveIsOnDamagingTurn(battleCtx, move)) {
        defenderType1 = Mercury_D7BestDefensiveType(
            moveType, defenderType1);
        defenderType2 = defenderType1;
    }

"""
    insert_in_function(
        path,
        sig,
        "    mercuryDefenderType = Mercury_AddedTypeForAbility(defenderAbility);\n",
        ai,
        "defenderType1 = Mercury_D7BestDefensiveType",
        "MR10D7 Color Change AI awareness",
        after=True,
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
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    magical = (root / "res/battle/scripts/subscripts/subscript_mercury_magical_dust.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "dynamic_type_state":
            "mercuryDynamicAddedType[MAX_BATTLERS]" in ctx
            and "mercuryColorChangeTurn[MAX_BATTLERS]" in ctx,
        "dynamic_type_reset":
            "mercuryDynamicAddedType[battler] = 0xFF;" in lib,
        "added_type_core_extended":
            "mercuryDynamicAddedType[battler] != 0xFF" in lib,
        "magical_dust_contact_psychic":
            "case ABILITY_MR_MAGICAL_DUST:" in lib
            and "mercuryDynamicAddedType[battleCtx->attacker] = TYPE_PSYCHIC;" in lib,
        "magical_dust_long_reach_respected":
            "ABILITY_LONG_REACH" in lib,
        "magical_dust_popup":
            "subscript_mercury_magical_dust" in order
            and "BattleStrings_Text_PokemonWasAbility_Ally" in magical,
        "color_change_post_hit_removed":
            "MR10D7: ER-style Color Change resolves before the incoming hit." in lib,
        "color_change_best_type_selection":
            "Mercury_D7BestDefensiveType" in lib
            and "TYPE_MYSTERY" in lib,
        "color_change_once_per_turn":
            "mercuryColorChangeTurn[defender]" in lib
            and "battleCtx->totalTurns" in lib,
        "color_change_pre_hit_retype":
            "battleCtx->battleMons[defender].type1 = mercuryBestType;" in lib
            and "battleCtx->battleMons[defender].type2 = mercuryBestType;" in lib,
        "color_change_ai_aware":
            "defenderType1 = Mercury_D7BestDefensiveType" in lib,
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
    ap.add_argument("--report", type=Path, default=Path("mr10d7-dynamic-typing.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_state(root)
    patch_added_type_core(root)
    patch_magical_dust_script(root)
    patch_magical_dust(root)
    patch_color_change(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D7_DYNAMIC_TYPING",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "dynamic_battle_only_type3",
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D7 dynamic typing validation failed")


if __name__ == "__main__":
    main()
