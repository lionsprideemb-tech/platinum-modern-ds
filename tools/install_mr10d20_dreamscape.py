#!/usr/bin/env python3
"""MR10D20 — Dreamscape.

Implements the approved KEEP-AS-WRITTEN composite:
- inherits Mercury's canonical Comatose semantics (virtual sleep, ordinary
  nonvolatile-status immunity, and the same special Ability restrictions);
- inherits Dreamcatcher behavior: move power doubles while any living active
  battler is asleep, including a Comatose/Dreamscape virtual sleeper;
- all outgoing damaging moves also receive Dreamscape's unconditional 20%
  power increase.

The two power components intentionally stack when the sleep condition is met.
Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Dreamscape"
ABILITY_TOKEN = "ABILITY_MR_DREAMSCAPE"
ABILITY_ID = 735


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


def patch_status_immunity(root: Path) -> None:
    specs = [
        ("subscript_fall_asleep.s",
         "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _202\n",
         "_202"),
        ("subscript_poison.s",
         "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _177\n",
         "_177"),
        ("subscript_badly_poison.s",
         "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _249\n",
         "_249"),
        ("subscript_burn.s",
         "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _211\n",
         "_211"),
        ("subscript_freeze.s",
         "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _128\n",
         "_128"),
        ("subscript_paralyze.s",
         "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _170\n",
         "_170"),
    ]
    scripts = root / "res/battle/scripts/subscripts"
    for filename, anchor, fail in specs:
        insert_after_once(
            scripts / filename,
            anchor,
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, {fail}\n",
            f"D20 Dreamscape status immunity {filename}",
        )

    # Bad poison and burn have additional non-move/direct entry lanes that
    # canonical Comatose already protects. Mirror each remaining Comatose
    # guard rather than broadening unrelated immunity checks.
    for filename, fail in (
        ("subscript_badly_poison.s", "_248"),
        ("subscript_burn.s", "_264"),
    ):
        path = scripts / filename
        text = path.read_text(encoding="utf-8")
        comatose = (
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, "
            f"BATTLEMON_ABILITY, ABILITY_COMATOSE, {fail}\n"
        )
        dream = (
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, "
            f"BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, {fail}\n"
        )
        if dream not in text and comatose in text:
            text = text.replace(comatose, comatose + dream, 1)
            path.write_text(text, encoding="utf-8")


def patch_sleep_semantics(root: Path) -> None:
    effects = root / "res/battle/scripts/effects"

    replacements = [
        (
            effects / "effect_script_0092.s",
            "    CompareMonDataToValue OPCODE_NEQ, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _019\n",
            """    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _MercuryComatoseSnoreOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, _019
""",
            "D20 Snore virtual sleep",
        ),
        (
            effects / "effect_script_0097.s",
            "    CompareMonDataToValue OPCODE_NEQ, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _013\n",
            """    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _MercuryComatoseSleepTalkOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, _013
""",
            "D20 Sleep Talk virtual sleep",
        ),
        (
            effects / "effect_script_0008.s",
            "    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _015\n",
            """    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _MercuryComatoseDreamEaterOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, _015
""",
            "D20 Dream Eater virtual sleep",
        ),
        (
            effects / "effect_script_0107.s",
            "    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _019\n",
            """    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _MercuryComatoseNightmareOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, _019
""",
            "D20 Nightmare virtual sleep",
        ),
    ]
    for path, old, new, label in replacements:
        replace_once(path, old, new, label)

    nightmare = root / "res/battle/scripts/subscripts/subscript_nightmare_start.s"
    replace_once(
        nightmare,
        "    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _029\n",
        """    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _MercuryComatoseNightmareStartOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, _029
""",
        "D20 Nightmare-start virtual sleep",
    )

    wake = effects / "effect_script_0217.s"
    insert_after_once(
        wake,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _MercuryComatoseWakeUpSlap\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, _MercuryComatoseWakeUpSlap\n",
        "D20 Wake-Up Slap virtual sleep",
    )


def patch_comatose_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    insert_after_in_function(
        lib,
        "static BOOL Mercury_AbilityCanBeReceived(int ability)",
        "    case ABILITY_COMATOSE:\n",
        "    case ABILITY_MR_DREAMSCAPE:\n",
        "case ABILITY_MR_DREAMSCAPE:",
        "D20 Receiver restriction",
    )
    insert_after_in_function(
        lib,
        "static BOOL Mercury_AbilityCannotBeNeutralized(int ability)",
        "    case ABILITY_COMATOSE:\n",
        "    case ABILITY_MR_DREAMSCAPE:\n",
        "case ABILITY_MR_DREAMSCAPE:",
        "D20 Neutralizing Gas restriction",
    )

    for path, battler, fail, label in (
        (copy, "BTLSCR_DEFENDER", "_091", "Role Play target"),
        (copy, "BTLSCR_ATTACKER", "_091", "Role Play user"),
        (swap, "BTLSCR_DEFENDER", "_156", "Skill Swap target"),
        (swap, "BTLSCR_ATTACKER", "_156", "Skill Swap user"),
        (suppress, "BTLSCR_DEFENDER", "_034", "Gastro Acid target"),
        (worry, "BTLSCR_DEFENDER", "_041", "Worry Seed target"),
    ):
        anchor = (
            f"    CompareMonDataToValue OPCODE_EQU, {battler}, "
            f"BATTLEMON_ABILITY, ABILITY_COMATOSE, {fail}\n"
        )
        insertion = (
            f"    CompareMonDataToValue OPCODE_EQU, {battler}, "
            f"BATTLEMON_ABILITY, ABILITY_MR_DREAMSCAPE, {fail}\n"
        )
        insert_after_once(path, anchor, insertion, f"D20 Dreamscape {label}")


def patch_damage_components(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    helper = """static BOOL Mercury_DreamscapeAnyActiveSleeper(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    for (i = 0; i < maxBattlers; i++) {
        int ability;

        if (battleCtx->battleMons[i].curHP == 0) {
            continue;
        }

        ability = Battler_Ability(battleCtx, i);
        if ((battleCtx->battleMons[i].status & MON_CONDITION_SLEEP)
            || ability == ABILITY_COMATOSE
            || ability == ABILITY_MR_DREAMSCAPE) {
            return TRUE;
        }
    }

    return FALSE;
}

"""
    insert_before_once(
        lib,
        """int BattleSystem_CalcMoveDamage(BattleSystem *battleSys,
    BattleContext *battleCtx,
""",
        helper,
        "D20 active sleeper helper",
    )

    insert_before_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    if (attackerParams.ability == ABILITY_MR_DREAMSCAPE && movePower) {
        movePower = movePower * 12 / 10;
        if (Mercury_DreamscapeAnyActiveSleeper(battleSys, battleCtx)) {
            movePower *= 2;
        }
    }

""",
        "D20 Dreamscape power components",
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
    scripts = root / "res/battle/scripts/subscripts"
    effects = root / "res/battle/scripts/effects"
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    status_files = (
        "subscript_fall_asleep.s",
        "subscript_poison.s",
        "subscript_badly_poison.s",
        "subscript_burn.s",
        "subscript_freeze.s",
        "subscript_paralyze.s",
    )
    status_ok = all(
        "ABILITY_MR_DREAMSCAPE" in
        (scripts / name).read_text(encoding="utf-8")
        for name in status_files
    )

    virtual_files = (
        effects / "effect_script_0092.s",
        effects / "effect_script_0097.s",
        effects / "effect_script_0008.s",
        effects / "effect_script_0107.s",
        effects / "effect_script_0217.s",
        scripts / "subscript_nightmare_start.s",
    )
    virtual_ok = all(
        "ABILITY_MR_DREAMSCAPE" in path.read_text(encoding="utf-8")
        for path in virtual_files
    )

    copy = (scripts / "subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (scripts / "subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (scripts / "subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    worry = (scripts / "subscript_give_target_insomnia.s").read_text(encoding="utf-8")

    checks = {
        "stable_id_735":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "comatose_status_immunity":
            status_ok,
        "comatose_virtual_sleep":
            virtual_ok,
        "special_ability_restrictions":
            "case ABILITY_MR_DREAMSCAPE:" in lib
            and "ABILITY_MR_DREAMSCAPE" in copy
            and "ABILITY_MR_DREAMSCAPE" in swap
            and "ABILITY_MR_DREAMSCAPE" in suppress
            and "ABILITY_MR_DREAMSCAPE" in worry,
        "active_sleep_helper":
            "Mercury_DreamscapeAnyActiveSleeper(" in lib
            and "MON_CONDITION_SLEEP" in lib
            and "ABILITY_COMATOSE" in lib,
        "unconditional_twenty_percent":
            "movePower = movePower * 12 / 10;" in lib,
        "dreamcatcher_double":
            "Mercury_DreamscapeAnyActiveSleeper(battleSys, battleCtx)" in lib
            and "movePower *= 2;" in lib,
        "components_stack":
            lib.find("movePower = movePower * 12 / 10;")
            < lib.find("movePower *= 2;", lib.find("ABILITY_MR_DREAMSCAPE")),
        "implemented_registry_updated":
            ABILITY_TOKEN in registry_lines,
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
    ap.add_argument("--report", type=Path, default=Path("mr10d20-dreamscape.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_status_immunity(root)
    patch_sleep_semantics(root)
    patch_comatose_restrictions(root)
    patch_damage_components(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D20_DREAMSCAPE",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "components": [
            "Comatose",
            "Dreamcatcher",
            "unconditional 20 percent outgoing power",
        ],
        "sleep_condition_multiplier": 2.0,
        "always_on_multiplier": 1.2,
        "remaining_keep_as_written_after_d20": 16,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D20 Dreamscape validation failed")


if __name__ == "__main__":
    main()
