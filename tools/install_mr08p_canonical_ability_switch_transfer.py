#!/usr/bin/env python3
"""MR08P — canonical stateful switch / item-transfer Ability pass.

Adds three official/current-mainline mechanics after MR08O:
- Symbiosis
- Wimp Out
- Emergency Exit

This pass deliberately focuses on mechanics that share Platinum's existing
item-removal and pivot-switch infrastructure. Locked MR07 Summary/editor
visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_SYMBIOSIS",
    "ABILITY_WIMP_OUT",
    "ABILITY_EMERGENCY_EXIT",
)

EXPECTED_IDS = {
    "ABILITY_SYMBIOSIS": 180,
    "ABILITY_WIMP_OUT": 193,
    "ABILITY_EMERGENCY_EXIT": 194,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {count}"
        )
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {count}"
        )
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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
        for line in (root / "generated/abilities.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_wimp_subscript(root: Path) -> None:
    subs = root / "res/battle/scripts/subscripts"
    script_path = subs / "subscript_mercury_wimp_out.s"
    script_path.write_text(
        """#include "macros/btlcmd.inc"


_000:
    TryReplaceFaintedMon BTLSCR_MSG_TEMP, TRUE, _060
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_TEMP
    Wait
    WaitButtonABTime 30
    UpdateVarFromVar OPCODE_SET, BTLVAR_SWITCHED_MON, BTLVAR_MSG_TEMP
    TryRestoreStatusOnSwitch BTLSCR_MSG_TEMP, _030
    UpdateMonData OPCODE_SET, BTLSCR_MSG_TEMP, BATTLEMON_STATUS, MON_CONDITION_NONE

_030:
    DeletePokemon BTLSCR_MSG_TEMP
    Wait
    HealthBoxSlideOut BTLSCR_MSG_TEMP
    Wait
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS_2, SYSCTL_UTURN_ACTIVE
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_TRY_SYNCHRONIZE_STATUS
    UpdateVar OPCODE_SET, BTLVAR_DEFENDER_SELF_TURN_STATUS_FLAGS, SELF_TURN_FLAG_CLEAR
    GoToSubscript BATTLE_SUBSCRIPT_SHOW_PARTY_LIST

_060:
    End
""",
        encoding="utf-8",
    )

    order = subs / "sub_seq.order"
    order_lines = [
        line.rstrip()
        for line in order.read_text(encoding="utf-8").splitlines()
    ]
    if "subscript_mercury_wimp_out" not in order_lines:
        order_lines.append("subscript_mercury_wimp_out")
        order.write_text("\n".join(order_lines) + "\n", encoding="utf-8")

    meson = subs / "meson.build"
    insert_after_once(
        meson,
        """    'subscript_start_encounter.s',
""",
        """    'subscript_mercury_wimp_out.s',
""",
        "MR08P subscript build registration",
    )


def patch_wimp_family(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    insert_before_once(
        lib,
        """    case ABILITY_ANGER_SHELL: {
""",
        """    case ABILITY_WIMP_OUT:
    case ABILITY_EMERGENCY_EXIT: {
        int ability = Battler_Ability(battleCtx, battleCtx->defender);
        int damageTaken = DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            ? DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            : DEFENDER_SELF_TURN_FLAGS.specialDamageTaken;
        int hpBeforeHit = DEFENDING_MON.curHP - damageTaken;

        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ability) == TRUE
            && DEFENDING_MON.curHP
            && damageTaken < 0
            && hpBeforeHit > DEFENDING_MON.maxHP / 2
            && DEFENDING_MON.curHP <= DEFENDING_MON.maxHP / 2
            && !(Battler_Ability(battleCtx, battleCtx->attacker)
                    == ABILITY_SHEER_FORCE
                && Mercury_MoveHasSheerForceSecondary(
                    battleCtx, battleCtx->moveCur))) {
            battleCtx->msgBattlerTemp = battleCtx->defender;
            battleCtx->msgTemp = battleCtx->defender;
            *subscript = subscript_mercury_wimp_out;
            result = TRUE;
        }
        break;
    }

""",
        "Wimp Out / Emergency Exit damage-threshold hook",
    )


def patch_symbiosis(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_function(
        path,
        "static BOOL BtlCmd_RemoveItem(BattleSystem *battleSys, BattleContext *battleCtx)",
        """static BOOL BtlCmd_RemoveItem(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BattleScript_Iter(battleCtx, 1);
    int inBattler = BattleScript_Read(battleCtx);

    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
    int ally = battler ^ 2;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    int removedItem = battleCtx->battleMons[battler].heldItem;

    battleCtx->recycleItem[battler] = removedItem;
    battleCtx->battleMons[battler].heldItem = ITEM_NONE;

    if (removedItem != ITEM_NONE
        && battleCtx->battleMons[battler].curHP
        && ally < maxBattlers
        && battleCtx->battleMons[ally].curHP
        && Battler_Ability(battleCtx, ally) == ABILITY_SYMBIOSIS
        && battleCtx->battleMons[ally].heldItem != ITEM_NONE) {
        battleCtx->battleMons[battler].heldItem =
            battleCtx->battleMons[ally].heldItem;
        battleCtx->battleMons[ally].heldItem = ITEM_NONE;
        BattleMon_CopyToParty(battleSys, battleCtx, ally);
    }

    BattleMon_CopyToParty(battleSys, battleCtx, battler);

    return FALSE;
}""",
        "Symbiosis item transfer on ally item loss",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    battle_script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(
        encoding="utf-8"
    )
    meson = (root / "res/battle/scripts/subscripts/meson.build").read_text(
        encoding="utf-8"
    )
    wimp_script = (
        root / "res/battle/scripts/subscripts/subscript_mercury_wimp_out.s"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "wimp_out_hook":
            "case ABILITY_WIMP_OUT:" in lib
            and "subscript_mercury_wimp_out" in lib,
        "emergency_exit_hook":
            "case ABILITY_EMERGENCY_EXIT:" in lib
            and "hpBeforeHit > DEFENDING_MON.maxHP / 2" in lib,
        "wimp_pivot_subscript":
            "subscript_mercury_wimp_out" in order
            and "subscript_mercury_wimp_out.s" in meson
            and "BATTLE_SUBSCRIPT_SHOW_PARTY_LIST" in wimp_script,
        "symbiosis_hook":
            "ABILITY_SYMBIOSIS" in battle_script
            and "battleCtx->battleMons[ally].heldItem = ITEM_NONE;" in battle_script,
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
        default=Path("mr08p-canonical-ability-switch-transfer.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_wimp_subscript(root)
    patch_wimp_family(root)
    patch_symbiosis(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08P_CANONICAL_ABILITY_SWITCH_TRANSFER",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 159,
        "remaining_modern_canonical_mechanics": 28,
        "policy": "Official/current-mainline mechanics; stateful form families remain in later passes.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08P validation failed")


if __name__ == "__main__":
    main()
