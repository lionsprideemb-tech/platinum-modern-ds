#!/usr/bin/env python3
"""MR10C1 — implement the approved Spectral Body redesign.

Spectral Body:
- reduces damage from contact moves by 25%;
- prevents the holder from being trapped by moves, Abilities, and trapping
  effects.

This installer runs after the MR10 custom Ability namespace is materialized.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Spectral Body"
ABILITY_TOKEN = "ABILITY_MR_SPECTRAL_BODY"
ABILITY_ID = 549


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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


def validate_partition(partition: Path) -> None:
    plan = json.loads(partition.read_text(encoding="utf-8"))
    rows = [x for x in plan["abilities"] if x.get("id") == ABILITY_ID]
    if len(rows) != 1:
        raise SystemExit(f"{ABILITY_NAME}: expected one partition row at ID {ABILITY_ID}")
    row = rows[0]
    expected = {
        "display_name": ABILITY_NAME,
        "token": ABILITY_TOKEN,
        "approval_state": "owner_approved_redesign",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )


def patch_contact_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_BIG_PECKS
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_SPECTRAL_BODY) == TRUE
        && Mercury_MoveMakesContact(battleCtx, attacker, move)
        && movePower) {
        movePower = movePower * 3 / 4;
    }

""",
        "Spectral Body 25 percent contact reduction",
    )


def patch_trap_immunity(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    old = """    if (itemEffect == HOLD_EFFECT_FLEE
        || (battleType & BATTLE_TYPE_NO_EXPERIENCE)
        || Battler_Ability(battleCtx, battler) == ABILITY_RUN_AWAY) {
        return FALSE;
    }
"""
    new = """    if (itemEffect == HOLD_EFFECT_FLEE
        || (battleType & BATTLE_TYPE_NO_EXPERIENCE)
        || Battler_Ability(battleCtx, battler) == ABILITY_RUN_AWAY
        || Battler_Ability(battleCtx, battler) == ABILITY_MR_SPECTRAL_BODY) {
        return FALSE;
    }
"""
    replace_once(path, old, new, "Spectral Body trap immunity")


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
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_549": len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "contact_reduction_25_percent":
            "ABILITY_MR_SPECTRAL_BODY" in lib
            and "movePower = movePower * 3 / 4;" in lib
            and "Mercury_MoveMakesContact(battleCtx, attacker, move)" in lib,
        "trap_immunity":
            "Battler_Ability(battleCtx, battler) == ABILITY_MR_SPECTRAL_BODY" in lib
            and "BOOL Battler_IsTrappedMsg" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_touched": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c1-spectral-body.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_contact_damage(root)
    patch_trap_immunity(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C1_SPECTRAL_BODY",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C1 Spectral Body validation failed")


if __name__ == "__main__":
    main()
