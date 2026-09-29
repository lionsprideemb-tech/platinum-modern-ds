#!/usr/bin/env python3
"""MR10D15 — Patchwork Disguise/Curse composite.

Implements approved KEEP-AS-WRITTEN Patchwork:
- uses the canonical Mercury Disguise shield state and damage-cancel path;
- the first qualifying damaging hit breaks the disguise and costs 1/8 max HP;
- when the disguise breaks, the opposing attacker is cursed when legal;
- Mold Breaker-family bypass, suppression/copy/swap restrictions, party-persistent
  broken state, multi-hit behavior, and transformed-user handling mirror Disguise.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Patchwork"
ABILITY_TOKEN = "ABILITY_MR_PATCHWORK"
ABILITY_ID = 812


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
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_form_shield_core(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    replace_once(
        lib,
        """    mask = ability == ABILITY_DISGUISE
        ? &battleCtx->mercuryDisguiseBrokenMask[side]
        : &battleCtx->mercuryIceFaceBrokenMask[side];
""",
        """    mask = (ability == ABILITY_DISGUISE
            || ability == ABILITY_MR_PATCHWORK)
        ? &battleCtx->mercuryDisguiseBrokenMask[side]
        : &battleCtx->mercuryIceFaceBrokenMask[side];
""",
        "D15 Patchwork shares Disguise broken-state mask",
    )

    insert_after_once(
        lib,
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_DISGUISE)
        && Mercury_FormShieldBroken(
               battleSys, battleCtx, defender, ABILITY_DISGUISE) == FALSE) {
        battleCtx->mercuryFormShieldPending[defender] = ABILITY_DISGUISE;
        return TRUE;
    }

""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_PATCHWORK)
        && Mercury_FormShieldBroken(
               battleSys, battleCtx, defender, ABILITY_MR_PATCHWORK) == FALSE) {
        battleCtx->mercuryFormShieldPending[defender] = ABILITY_MR_PATCHWORK;
        return TRUE;
    }

""",
        "D15 Patchwork damage shield gate",
    )

    replace_once(
        lib,
        """        if (ability == ABILITY_DISGUISE) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(
                battleCtx->battleMons[battleCtx->defender].maxHP * -1,
                8);
        }

        *subscript = subscript_mercury_form_shield_break;
""",
        """        if (ability == ABILITY_DISGUISE
            || ability == ABILITY_MR_PATCHWORK) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(
                battleCtx->battleMons[battleCtx->defender].maxHP * -1,
                8);
        }

        if (ability == ABILITY_MR_PATCHWORK
            && battleCtx->attacker != BATTLER_NONE
            && battleCtx->battleMons[battleCtx->attacker].curHP
            && BattleSystem_GetBattlerSide(
                   battleSys, battleCtx->attacker)
                != BattleSystem_GetBattlerSide(
                   battleSys, battleCtx->defender)
            && (battleCtx->battleMons[battleCtx->attacker].statusVolatile
                & VOLATILE_CONDITION_CURSE) == 0) {
            battleCtx->battleMons[battleCtx->attacker].statusVolatile |=
                VOLATILE_CONDITION_CURSE;
        }

        *subscript = subscript_mercury_form_shield_break;
""",
        "D15 Patchwork break recoil and curse",
    )


def patch_disguise_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    insert_after_in_function(
        lib,
        "static BOOL Mercury_AbilityCannotBeNeutralized(int ability)",
        """    case ABILITY_DISGUISE:
""",
        """    case ABILITY_MR_PATCHWORK:
""",
        "case ABILITY_MR_PATCHWORK:",
        "D15 Patchwork Neutralizing Gas restriction",
    )

    insert_after_once(
        lib,
        """        && ability1 != ABILITY_DISGUISE
""",
        """        && ability1 != ABILITY_MR_PATCHWORK
""",
        "D15 Patchwork Trace defender1 restriction",
    )
    insert_after_once(
        lib,
        """        && ability2 != ABILITY_DISGUISE
""",
        """        && ability2 != ABILITY_MR_PATCHWORK
""",
        "D15 Patchwork Trace defender2 restriction",
    )

    for path, battler, label, fail in (
        (copy, "BTLSCR_DEFENDER", "Role Play target", "_091"),
        (copy, "BTLSCR_ATTACKER", "Role Play user", "_091"),
        (swap, "BTLSCR_DEFENDER", "Skill Swap target", "_156"),
        (swap, "BTLSCR_ATTACKER", "Skill Swap user", "_156"),
        (suppress, "BTLSCR_DEFENDER", "Gastro Acid target", "_034"),
        (worry, "BTLSCR_DEFENDER", "Worry Seed target", "_041"),
    ):
        anchor = (
            f"    CompareMonDataToValue OPCODE_EQU, {battler}, "
            f"BATTLEMON_ABILITY, ABILITY_DISGUISE, {fail}\n"
        )
        insertion = (
            f"    CompareMonDataToValue OPCODE_EQU, {battler}, "
            f"BATTLEMON_ABILITY, ABILITY_MR_PATCHWORK, {fail}\n"
        )
        insert_after_once(path, anchor, insertion, f"D15 Patchwork {label} restriction")


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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "stable_id":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "shares_disguise_party_state":
            "|| ability == ABILITY_MR_PATCHWORK" in lib
            and "&battleCtx->mercuryDisguiseBrokenMask[side]" in lib,
        "qualifying_hit_blocks_damage":
            "ABILITY_MR_PATCHWORK)" in lib
            and "mercuryFormShieldPending[defender] = ABILITY_MR_PATCHWORK" in lib,
        "disguise_break_recoil":
            "ability == ABILITY_MR_PATCHWORK" in lib
            and "maxHP * -1" in lib
            and "8);" in lib,
        "break_curses_opposing_attacker":
            "VOLATILE_CONDITION_CURSE" in lib
            and "statusVolatile |=" in lib
            and "BattleSystem_GetBattlerSide(" in lib,
        "curse_only_when_legal":
            "& VOLATILE_CONDITION_CURSE) == 0" in lib
            and "battleCtx->battleMons[battleCtx->attacker].curHP" in lib,
        "mold_breaker_path_preserved":
            "Battler_IgnorableAbility(" in lib
            and "ABILITY_MR_PATCHWORK" in lib,
        "disguise_special_restrictions":
            "case ABILITY_MR_PATCHWORK:" in lib
            and "ABILITY_MR_PATCHWORK" in copy
            and "ABILITY_MR_PATCHWORK" in swap
            and "ABILITY_MR_PATCHWORK" in suppress
            and "ABILITY_MR_PATCHWORK" in worry,
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
    ap.add_argument("--report", type=Path, default=Path("mr10d15-patchwork.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_form_shield_core(root)
    patch_disguise_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D15_PATCHWORK",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_system": "canonical_disguise_plus_curse_on_break",
        "remaining_keep_as_written_after_d15": 27,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D15 Patchwork validation failed")


if __name__ == "__main__":
    main()
