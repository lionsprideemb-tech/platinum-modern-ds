#!/usr/bin/env python3
"""MR08S4 — canonical Stance Change pass.

Implements the battle-state portion of Aegislash's Stance Change:
- starts each switch-in in Shield stance;
- using King's Shield returns the holder to Shield stance;
- using a damaging move changes the holder to Blade stance before the move;
- Attack/Defense and Sp. Atk/Sp. Def are swapped with the stance, preserving
  stat-stage state and current HP;
- status moves other than King's Shield do not change stance;
- transformed users do not trigger Stance Change;
- Neutralizing Gas can suppress activation, while Gastro Acid/Worry Seed,
  Trace, Role Play, Skill Swap, Receiver and Power of Alchemy keep the
  canonical restrictions.

Alternate-form sprite presentation is deferred to Mercury's form-asset phase;
this pass installs the actual battle-stat state transition without touching the
locked MR07 Summary/editor visuals.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_STANCE_CHANGE",)
EXPECTED_IDS = {"ABILITY_STANCE_CHANGE": 176}


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
        """    // Mercury MR08S4: 0 = Shield stance, 1 = Blade stance.
    u8 mercuryStanceBlade[MAX_BATTLERS];

""",
        "Stance Change state",
    )


def patch_switch_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryIceFaceNeedsWeatherCheck[battler] = TRUE;

""",
        """    battleCtx->mercuryStanceBlade[battler] = FALSE;

""",
        "Stance Change switch-in reset",
    )


def patch_before_move(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        path,
        """static void BattleControllerPlayer_BeforeMove(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        """static void Mercury_TryStanceChange(BattleContext *battleCtx)
{
    int battler = battleCtx->attacker;
    BOOL wantBlade;
    BOOL wantShield;
    u16 temp;

    if (battler == BATTLER_NONE
        || battleCtx->battleMons[battler].curHP == 0
        || Battler_Ability(battleCtx, battler) != ABILITY_STANCE_CHANGE
        || (battleCtx->battleMons[battler].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM)) {
        return;
    }

    wantShield = battleCtx->moveCur == MOVE_KINGS_SHIELD;
    wantBlade = MOVE_DATA(battleCtx->moveCur).class != CLASS_STATUS;

    if (wantShield && battleCtx->mercuryStanceBlade[battler]) {
        temp = battleCtx->battleMons[battler].attack;
        battleCtx->battleMons[battler].attack =
            battleCtx->battleMons[battler].defense;
        battleCtx->battleMons[battler].defense = temp;

        temp = battleCtx->battleMons[battler].spAttack;
        battleCtx->battleMons[battler].spAttack =
            battleCtx->battleMons[battler].spDefense;
        battleCtx->battleMons[battler].spDefense = temp;

        battleCtx->mercuryStanceBlade[battler] = FALSE;
    } else if (wantBlade && battleCtx->mercuryStanceBlade[battler] == FALSE) {
        temp = battleCtx->battleMons[battler].attack;
        battleCtx->battleMons[battler].attack =
            battleCtx->battleMons[battler].defense;
        battleCtx->battleMons[battler].defense = temp;

        temp = battleCtx->battleMons[battler].spAttack;
        battleCtx->battleMons[battler].spAttack =
            battleCtx->battleMons[battler].spDefense;
        battleCtx->battleMons[battler].spDefense = temp;

        battleCtx->mercuryStanceBlade[battler] = TRUE;
    }
}

""",
        "Stance Change before-move helper",
    )

    insert_before_once(
        path,
        """    if (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) {
""",
        """    Mercury_TryStanceChange(battleCtx);

""",
        "Stance Change before-move hook",
    )


def patch_neutralizing_gas(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """    case ABILITY_ZEN_MODE:
    case ABILITY_STANCE_CHANGE:
    case ABILITY_SCHOOLING:
""",
        """    case ABILITY_ZEN_MODE:
    case ABILITY_SCHOOLING:
""",
        "Stance Change Neutralizing Gas suppression",
    )


def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    replace_once(
        lib,
        """        && ability1 != ABILITY_ICE_FACE;
""",
        """        && ability1 != ABILITY_ICE_FACE
        && ability1 != ABILITY_STANCE_CHANGE;
""",
        "Stance Change Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_ICE_FACE;
""",
        """        && ability2 != ABILITY_ICE_FACE
        && ability2 != ABILITY_STANCE_CHANGE;
""",
        "Stance Change Trace defender2",
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _091\n",
        "Stance Change Role Play target",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _091\n",
        "Stance Change Role Play user",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _156\n",
        "Stance Change Skill Swap target",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _156\n",
        "Stance Change Skill Swap user",
    )
    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _034\n",
        "Stance Change Gastro Acid lock",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _041\n",
        "Stance Change Worry Seed lock",
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
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    checks = {
        "stance_state":
            "mercuryStanceBlade[MAX_BATTLERS]" in ctx,
        "switch_resets_shield":
            "mercuryStanceBlade[battler] = FALSE;" in lib,
        "kings_shield_returns_shield":
            "battleCtx->moveCur == MOVE_KINGS_SHIELD" in controller
            and "wantShield" in controller,
        "damaging_move_enters_blade":
            "MOVE_DATA(battleCtx->moveCur).class != CLASS_STATUS" in controller
            and "wantBlade" in controller,
        "battle_stats_swap":
            "battleMons[battler].attack =" in controller
            and "battleMons[battler].defense =" in controller
            and "battleMons[battler].spAttack =" in controller
            and "battleMons[battler].spDefense =" in controller,
        "transform_block":
            "VOLATILE_CONDITION_TRANSFORM" in controller,
        "neutralizing_gas_can_suppress":
            "ABILITY_STANCE_CHANGE" not in cannot,
        "trace_blocked":
            "ability1 != ABILITY_STANCE_CHANGE" in lib
            and "ability2 != ABILITY_STANCE_CHANGE" in lib,
        "uncopyable_unswappable":
            "ABILITY_STANCE_CHANGE" in copy
            and "ABILITY_STANCE_CHANGE" in swap,
        "move_suppression_blocked":
            "ABILITY_STANCE_CHANGE" in suppress,
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
        default=Path("mr08s4-canonical-ability-stance-change.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_switch_reset(root)
    patch_before_move(root)
    patch_neutralizing_gas(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S4_CANONICAL_ABILITY_STANCE_CHANGE",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 175,
        "remaining_modern_canonical_mechanics": 12,
        "form_visuals_deferred": True,
        "policy": "Official Stance Change battle-state stat transition; alternate-form sprite presentation is deferred to the form-asset phase.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S4 validation failed")


if __name__ == "__main__":
    main()
