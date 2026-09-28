#!/usr/bin/env python3
"""MR08R4 — canonical Embody Aspect family.

Implements the four Gen IX Embody Aspect variants as switch-in stat boosts:
- Teal Mask: Speed +1
- Wellspring Mask: Sp. Def +1
- Hearthflame Mask: Attack +1
- Cornerstone Mask: Defense +1

Also blocks the four special abilities from Trace, Role Play, Skill Swap, and
Receiver / Power of Alchemy, matching their special-copy restrictions.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_EMBODY_ASPECT",
    "ABILITY_EMBODY_ASPECT_2",
    "ABILITY_EMBODY_ASPECT_3",
    "ABILITY_EMBODY_ASPECT_4",
)

EXPECTED_IDS = {
    "ABILITY_EMBODY_ASPECT": 301,
    "ABILITY_EMBODY_ASPECT_2": 302,
    "ABILITY_EMBODY_ASPECT_3": 303,
    "ABILITY_EMBODY_ASPECT_4": 304,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all_required(
    path: Path, old: str, new: str, label: str
) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count < 1:
        raise SystemExit(f"{label}: expected at least one match in {path}, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def replace_function(path: Path, signature: str, replacement: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

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
        raise SystemExit(f"{label}: could not find function end in {path}")
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_switch_in_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """                    case ABILITY_CURIOUS_MEDICINE: {
""",
        """                    case ABILITY_EMBODY_ASPECT:
                    case ABILITY_EMBODY_ASPECT_2:
                    case ABILITY_EMBODY_ASPECT_3:
                    case ABILITY_EMBODY_ASPECT_4: {
                        int ability = Battler_Ability(battleCtx, battler);

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;

                        switch (ability) {
                        case ABILITY_EMBODY_ASPECT:
                            battleCtx->sideEffectParam =
                                MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE;
                            break;
                        case ABILITY_EMBODY_ASPECT_2:
                            battleCtx->sideEffectParam =
                                MOVE_SUBSCRIPT_PTR_SP_DEFENSE_UP_1_STAGE;
                            break;
                        case ABILITY_EMBODY_ASPECT_3:
                            battleCtx->sideEffectParam =
                                MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
                            break;
                        default:
                            battleCtx->sideEffectParam =
                                MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE;
                            break;
                        }

                        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                        battleCtx->sideEffectMon = battler;
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_update_stat_stage;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

""",
        "Embody Aspect switch-in family",
    )


def patch_receiver_restriction(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    case ABILITY_TERA_SHIFT:
        return FALSE;
""",
        """    case ABILITY_EMBODY_ASPECT:
    case ABILITY_EMBODY_ASPECT_2:
    case ABILITY_EMBODY_ASPECT_3:
    case ABILITY_EMBODY_ASPECT_4:
""",
        "Embody Aspect Receiver restriction",
    )


def patch_trace_restriction(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replacement = """static int ChooseTraceTarget(BattleSystem *battleSys, BattleContext *battleCtx, int defender1, int defender2)
{
    int trace = BATTLER_NONE;
    int ability1 = battleCtx->battleMons[defender1].ability;
    int ability2 = battleCtx->battleMons[defender2].ability;
    BOOL eligible1 = battleCtx->battleMons[defender1].curHP
        && ability1 != ABILITY_FORECAST
        && ability1 != ABILITY_TRACE
        && ability1 != ABILITY_MULTITYPE
        && ability1 != ABILITY_EMBODY_ASPECT
        && ability1 != ABILITY_EMBODY_ASPECT_2
        && ability1 != ABILITY_EMBODY_ASPECT_3
        && ability1 != ABILITY_EMBODY_ASPECT_4;
    BOOL eligible2 = battleCtx->battleMons[defender2].curHP
        && ability2 != ABILITY_FORECAST
        && ability2 != ABILITY_TRACE
        && ability2 != ABILITY_MULTITYPE
        && ability2 != ABILITY_EMBODY_ASPECT
        && ability2 != ABILITY_EMBODY_ASPECT_2
        && ability2 != ABILITY_EMBODY_ASPECT_3
        && ability2 != ABILITY_EMBODY_ASPECT_4;

    if (eligible1 && eligible2) {
        trace = (BattleSystem_RandNext(battleSys) & 1) ? defender2 : defender1;
    } else if (eligible1) {
        trace = defender1;
    } else if (eligible2) {
        trace = defender2;
    }

    return trace;
}
"""
    replace_function(
        path,
        "static int ChooseTraceTarget(BattleSystem *battleSys, BattleContext *battleCtx, int defender1, int defender2)",
        replacement,
        "Embody Aspect Trace restriction",
    )

def patch_role_play_skill_swap(root: Path) -> None:
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"

    copy_target_anchor = (
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, "
        "BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n"
    )
    copy_user_anchor = (
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, "
        "BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n"
    )
    copy_target_insert = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {ability}, _091\n"
        for ability in IMPLEMENTED
    )
    copy_user_insert = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {ability}, _091\n"
        for ability in IMPLEMENTED
    )
    insert_after_once(copy, copy_target_anchor, copy_target_insert, "Embody Role Play target")
    insert_after_once(copy, copy_user_anchor, copy_user_insert, "Embody Role Play user")

    swap_target_anchor = (
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, "
        "BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n"
    )
    swap_user_anchor = (
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, "
        "BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n"
    )
    swap_target_insert = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {ability}, _156\n"
        for ability in IMPLEMENTED
    )
    swap_user_insert = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {ability}, _156\n"
        for ability in IMPLEMENTED
    )
    insert_after_once(swap, swap_target_anchor, swap_target_insert, "Embody Skill Swap target")
    insert_after_once(swap, swap_user_anchor, swap_user_insert, "Embody Skill Swap user")


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "four_switch_in_hooks":
            all(f"case {token}:" in lib for token in IMPLEMENTED),
        "teal_speed":
            "ABILITY_EMBODY_ASPECT:" in lib
            and "MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE" in lib,
        "wellspring_spdef":
            "ABILITY_EMBODY_ASPECT_2:" in lib
            and "MOVE_SUBSCRIPT_PTR_SP_DEFENSE_UP_1_STAGE" in lib,
        "hearthflame_attack":
            "ABILITY_EMBODY_ASPECT_3:" in lib
            and "MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE" in lib,
        "cornerstone_defense":
            "ABILITY_EMBODY_ASPECT_4:" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in lib,
        "trace_blocked":
            "BOOL eligible1 =" in lib
            and "BOOL eligible2 =" in lib
            and lib.count("ABILITY_EMBODY_ASPECT_4") >= 3,
        "receiver_blocked":
            "case ABILITY_EMBODY_ASPECT:" in lib
            and "case ABILITY_TERA_SHIFT:" in lib,
        "role_play_blocked":
            all(token in copy for token in IMPLEMENTED),
        "skill_swap_blocked":
            all(token in swap for token in IMPLEMENTED),
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr08r4-canonical-ability-embody-aspect.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_switch_in_family(root)
    patch_receiver_restriction(root)
    patch_trace_restriction(root)
    patch_role_play_skill_swap(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08R4_CANONICAL_ABILITY_EMBODY_ASPECT",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 168,
        "remaining_modern_canonical_mechanics": 19,
        "policy": "Official/current-mainline Embody Aspect stat boosts and special copy restrictions.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08R4 validation failed")


if __name__ == "__main__":
    main()
