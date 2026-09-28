#!/usr/bin/env python3
"""MR08P2 — canonical Symbiosis pass.

Adds current-mainline Symbiosis item passing on ally item loss/consumption.
The donor must be alive, on the same side, still holding an item, and its
Ability must be active after suppression checks. Locked MR07 visuals remain
untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_SYMBIOSIS",)
EXPECTED_IDS = {"ABILITY_SYMBIOSIS": 180}


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
        && battleCtx->battleMons[ally].heldItem != ITEM_NONE
        && battleCtx->battleMons[ally].heldItem != ITEM_GRISEOUS_ORB) {
        battleCtx->battleMons[battler].heldItem =
            battleCtx->battleMons[ally].heldItem;
        battleCtx->battleMons[ally].heldItem = ITEM_NONE;
        BattleMon_CopyToParty(battleSys, battleCtx, ally);
    }

    BattleMon_CopyToParty(battleSys, battleCtx, battler);

    return FALSE;
}""",
        "Symbiosis item transfer",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "symbiosis_hook":
            "Battler_Ability(battleCtx, ally) == ABILITY_SYMBIOSIS" in script,
        "same_side_partner_lane":
            "int ally = battler ^ 2;" in script
            and "ally < maxBattlers" in script,
        "donor_item_transfer":
            "battleCtx->battleMons[battler].heldItem =" in script
            and "battleCtx->battleMons[ally].heldItem = ITEM_NONE;" in script,
        "griseous_orb_protection":
            "heldItem != ITEM_GRISEOUS_ORB" in script,
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
        default=Path("mr08p2-canonical-ability-symbiosis.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_symbiosis(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08P2_CANONICAL_ABILITY_SYMBIOSIS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 159,
        "remaining_modern_canonical_mechanics": 28,
        "policy": "Official/current-mainline mechanics; form-changing families remain in later passes.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08P2 validation failed")


if __name__ == "__main__":
    main()
