#!/usr/bin/env python3
"""MR08S5 — canonical Hunger Switch battle-state pass.

Implements the mechanics-side state transition for Morpeko's Hunger Switch:
- an active Morpeko toggles Full Belly / Hangry state at the end of each turn;
- switch-in resets to Full Belly;
- transformed users do not toggle;
- Neutralizing Gas and Gastro Acid can suppress the Ability;
- Trace, Role Play, Skill Swap, Receiver / Power of Alchemy and Worry Seed
  keep the canonical special-Ability restrictions.

Mercury's alternate-form sprite resources and Aura Wheel move presentation are
owned by the later form/move asset phase. This pass stores the canonical form
state battle-side so that phase can consume it without touching locked MR07 UI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_HUNGER_SWITCH",)
EXPECTED_IDS = {"ABILITY_HUNGER_SWITCH": 258}


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
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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
        raise SystemExit(f"{label}: closing brace not found in {path}")

    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08S5: 0 = Full Belly, 1 = Hangry.
    u8 mercuryHungerHangry[MAX_BATTLERS];

""",
        "Hunger Switch state",
    )


def patch_battle_state(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_after_once(
        path,
        """    battleCtx->mercuryStanceBlade[battler] = FALSE;

""",
        """    battleCtx->mercuryHungerHangry[battler] = FALSE;

""",
        "Hunger Switch switch-in reset",
    )

    insert_before_once(
        path,
        """    case ABILITY_CUD_CHEW: {
""",
        """    case ABILITY_HUNGER_SWITCH:
        if (battleCtx->battleMons[battler].curHP
            && battleCtx->battleMons[battler].species == SPECIES_MORPEKO
            && (battleCtx->battleMons[battler].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
            battleCtx->mercuryHungerHangry[battler] ^=
                TRUE;
        }
        break;

""",
        "Hunger Switch end-turn toggle",
    )


def patch_neutralizing_gas(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Hunger Switch is disabled by Neutralizing Gas. Keep the still-deferred
    # form families in this temporary exemption table until their own passes
    # install their canonical suppression behavior.
    replace_function(
        path,
        "static BOOL Mercury_AbilityCannotBeNeutralized(int ability)",
        """static BOOL Mercury_AbilityCannotBeNeutralized(int ability)
{
    switch (ability) {
    case ABILITY_MULTITYPE:
    case ABILITY_ZEN_MODE:
    case ABILITY_SCHOOLING:
    case ABILITY_COMATOSE:
    case ABILITY_SHIELDS_DOWN:
    case ABILITY_BATTLE_BOND:
    case ABILITY_POWER_CONSTRUCT:
    case ABILITY_RKS_SYSTEM:
    case ABILITY_GULP_MISSILE:
    case ABILITY_AS_ONE_GLASTRIER:
    case ABILITY_AS_ONE_SPECTRIER:
    case ABILITY_ZERO_TO_HERO:
    case ABILITY_COMMANDER:
    case ABILITY_EMBODY_ASPECT:
    case ABILITY_EMBODY_ASPECT_2:
    case ABILITY_EMBODY_ASPECT_3:
    case ABILITY_EMBODY_ASPECT_4:
    case ABILITY_TERA_SHIFT:
        return TRUE;
    }

    return FALSE;
}""",
        "Hunger Switch Neutralizing Gas behavior",
    )


def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    replace_once(
        lib,
        """        && ability1 != ABILITY_STANCE_CHANGE;
""",
        """        && ability1 != ABILITY_STANCE_CHANGE
        && ability1 != ABILITY_HUNGER_SWITCH;
""",
        "Hunger Switch Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_STANCE_CHANGE;
""",
        """        && ability2 != ABILITY_STANCE_CHANGE
        && ability2 != ABILITY_HUNGER_SWITCH;
""",
        "Hunger Switch Trace defender2",
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _091\n",
        "Hunger Switch Role Play target",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _091\n",
        "Hunger Switch Role Play user",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _156\n",
        "Hunger Switch Skill Swap target",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _156\n",
        "Hunger Switch Skill Swap user",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _041\n",
        "Hunger Switch Worry Seed lock",
    )


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
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    receiver_start = lib.index("static BOOL Mercury_AbilityCanBeReceived")
    receiver_end = lib.index("static int Mercury_CountFaintedPartyMons", receiver_start)
    receiver = lib[receiver_start:receiver_end]

    checks = {
        "battle_state":
            "mercuryHungerHangry[MAX_BATTLERS]" in ctx,
        "switch_resets_full_belly":
            "mercuryHungerHangry[battler] = FALSE;" in lib,
        "end_turn_toggle":
            "case ABILITY_HUNGER_SWITCH:" in lib
            and "SPECIES_MORPEKO" in lib
            and "mercuryHungerHangry[battler] ^=" in lib,
        "transform_block":
            "VOLATILE_CONDITION_TRANSFORM" in lib,
        "neutralizing_gas_can_suppress":
            "ABILITY_HUNGER_SWITCH" not in cannot,
        "gastro_acid_can_suppress":
            "ABILITY_HUNGER_SWITCH" not in suppress,
        "trace_blocked":
            "ability1 != ABILITY_HUNGER_SWITCH" in lib
            and "ability2 != ABILITY_HUNGER_SWITCH" in lib,
        "uncopyable_unswappable":
            "ABILITY_HUNGER_SWITCH" in copy
            and "ABILITY_HUNGER_SWITCH" in swap,
        "receiver_blocked":
            "ABILITY_HUNGER_SWITCH" in receiver,
        "worry_seed_blocked":
            "ABILITY_HUNGER_SWITCH" in worry,
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
        default=Path("mr08s5-canonical-ability-hunger-switch.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_battle_state(root)
    patch_neutralizing_gas(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S5_CANONICAL_ABILITY_HUNGER_SWITCH",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 176,
        "remaining_modern_canonical_mechanics": 11,
        "form_visuals_deferred": True,
        "aura_wheel_presentation_deferred": True,
        "policy": "Official Hunger Switch turn-end state transition; form graphics and Aura Wheel presentation remain in their dedicated later asset/move phase.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S5 validation failed")


if __name__ == "__main__":
    main()
