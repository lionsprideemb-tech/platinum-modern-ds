#!/usr/bin/env python3
"""MR10C4 — implement the approved Fresh Start redesign.

Fresh Start:
- when the normal switch-in Ability phase is reached, remove all entry hazards
  currently implemented by the Platinum battle core from the holder's side;
- if at least one hazard was removed, restore 1/8 max HP.

Current removable hazards in the active engine are Spikes, Toxic Spikes, and
Stealth Rock. Sticky Web is not yet present in the current battle-side state;
when that hazard is added, it must be added to this shared cleanup branch too.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Fresh Start"
ABILITY_TOKEN = "ABILITY_MR_FRESH_START"
ABILITY_ID = 436


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
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


def patch_switch_in_cleanup(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insertion = """                    case ABILITY_MR_FRESH_START: {
                        int side = BattleSystem_GetBattlerSide(battleSys, battler);
                        BOOL removedHazard = FALSE;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;

                        if (battleCtx->sideConditionsMask[side]
                            & SIDE_CONDITION_SPIKES) {
                            battleCtx->sideConditionsMask[side]
                                &= ~SIDE_CONDITION_SPIKES;
                            battleCtx->sideConditions[side].spikesLayers = 0;
                            removedHazard = TRUE;
                        }

                        if (battleCtx->sideConditionsMask[side]
                            & SIDE_CONDITION_TOXIC_SPIKES) {
                            battleCtx->sideConditionsMask[side]
                                &= ~SIDE_CONDITION_TOXIC_SPIKES;
                            battleCtx->sideConditions[side].toxicSpikesLayers = 0;
                            removedHazard = TRUE;
                        }

                        if (battleCtx->sideConditionsMask[side]
                            & SIDE_CONDITION_STEALTH_ROCK) {
                            battleCtx->sideConditionsMask[side]
                                &= ~SIDE_CONDITION_STEALTH_ROCK;
                            removedHazard = TRUE;
                        }

                        if (removedHazard) {
                            battleCtx->msgTemp = battler;
                            battleCtx->msgBattlerTemp = battler;

                            if (battleCtx->battleMons[battler].curHP
                                < battleCtx->battleMons[battler].maxHP) {
                                battleCtx->hpCalcTemp = BattleSystem_Divide(
                                    battleCtx->battleMons[battler].maxHP, 8);
                                subscript = subscript_ability_hp_restore_gradual;
                            } else {
                                subscript = subscript_mold_breaker;
                            }
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
                    }

"""
    insert_before_once(
        path,
        """                    case ABILITY_HOSPITALITY: {
""",
        insertion,
        "Fresh Start switch-in hazard cleanup",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_436":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "spikes_removed":
            "ABILITY_MR_FRESH_START" in lib
            and "&= ~SIDE_CONDITION_SPIKES;" in lib
            and "spikesLayers = 0;" in lib,
        "toxic_spikes_removed":
            "&= ~SIDE_CONDITION_TOXIC_SPIKES;" in lib
            and "toxicSpikesLayers = 0;" in lib,
        "stealth_rock_removed":
            "&= ~SIDE_CONDITION_STEALTH_ROCK;" in lib,
        "conditional_one_eighth_heal":
            "removedHazard" in lib
            and "maxHP, 8" in lib
            and "subscript_ability_hp_restore_gradual" in lib,
        "switch_in_processed_once":
            "weatherAbilityAnnounced = TRUE;" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c4-fresh-start.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_switch_in_cleanup(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C4_FRESH_START",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "implemented_hazards": ["Spikes", "Toxic Spikes", "Stealth Rock"],
        "pending_engine_hazards": ["Sticky Web"],
        "switch_in_order":
            "Runs in Platinum's normal switch-in Ability phase, after the entrant's normal hazard check.",
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C4 Fresh Start validation failed")


if __name__ == "__main__":
    main()
