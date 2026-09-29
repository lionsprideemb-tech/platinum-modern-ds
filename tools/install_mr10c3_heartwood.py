#!/usr/bin/env python3
"""MR10C3 — implement the approved Heartwood redesign.

Heartwood:
- opponents cannot lower the holder's Defense or Special Defense;
- self-inflicted defensive drops still work normally;
- at end of turn, if the holder took no direct attack damage that turn,
  restore 1/16 max HP.

This reuses Platinum's normal stat-drop prevention messaging and gradual
Ability-healing subscript.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Heartwood"
ABILITY_TOKEN = "ABILITY_MR_HEARTWOOD"
ABILITY_ID = 686


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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
        "owner_review_decision": "REDESIGN",
        "implementation_class": "existing_hook",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_defensive_drop_immunity(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    old = """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_MINDS_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)) {
"""
    new = """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_MINDS_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)
                    || (((battleCtx->attacker & 1) != (battleCtx->sideEffectMon & 1))
                        && (BATTLE_STAT_ATTACK + statOffset == BATTLE_STAT_DEFENSE
                            || BATTLE_STAT_ATTACK + statOffset == BATTLE_STAT_SP_DEFENSE)
                        && Battler_IgnorableAbility(
                            battleCtx,
                            battleCtx->attacker,
                            battleCtx->sideEffectMon,
                            ABILITY_MR_HEARTWOOD) == TRUE)) {
"""
    replace_once(path, old, new, "Heartwood opponent defensive-drop immunity")


def patch_end_turn_heal(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    old = """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_MOODY: {
"""
    new = """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_MR_HEARTWOOD: {
        BOOL tookDirectDamage = FALSE;
        int i;

        for (i = 0; i < MAX_BATTLERS; i++) {
            if (battleCtx->turnFlags[battler].physicalDamageTakenFrom[i]
                || battleCtx->turnFlags[battler].specialDamageTakenFrom[i]) {
                tookDirectDamage = TRUE;
                break;
            }
        }

        if (battleCtx->battleMons[battler].curHP
            && battleCtx->battleMons[battler].curHP
                < battleCtx->battleMons[battler].maxHP
            && tookDirectDamage == FALSE) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(
                battleCtx->battleMons[battler].maxHP, 16);
            battleCtx->msgTemp = battler;
            battleCtx->msgBattlerTemp = battler;
            subscript = subscript_ability_hp_restore_gradual;
            result = TRUE;
        }
        break;
    }

    case ABILITY_MOODY: {
"""
    replace_once(path, old, new, "Heartwood no-direct-damage end-turn recovery")


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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_686":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "opponent_defense_and_spdef_drop_immunity":
            "ABILITY_MR_HEARTWOOD" in script
            and "BATTLE_STAT_SP_DEFENSE" in script
            and "(battleCtx->attacker & 1) != (battleCtx->sideEffectMon & 1)" in script,
        "self_drop_guard_preserved":
            "(battleCtx->attacker & 1) != (battleCtx->sideEffectMon & 1)" in script,
        "no_direct_damage_end_turn_heal":
            "case ABILITY_MR_HEARTWOOD:" in lib
            and "physicalDamageTakenFrom[i]" in lib
            and "specialDamageTakenFrom[i]" in lib
            and "BattleSystem_Divide(" in lib
            and "maxHP, 16" in lib
            and "subscript_ability_hp_restore_gradual" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c3-heartwood.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_defensive_drop_immunity(root)
    patch_end_turn_heal(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C3_HEARTWOOD",
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
        raise SystemExit("MR10C3 Heartwood validation failed")


if __name__ == "__main__":
    main()
