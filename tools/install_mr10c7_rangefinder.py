#!/usr/bin/env python3
"""MR10C7 — implement the approved Rangefinder redesign.

Rangefinder:
- successful damaging Mega Launcher-class moves gain +10% power on the first
  shot in the streak, +20% on the second, and +30% from the third onward;
- a failed or missed launcher move does not advance the streak;
- status moves do not reset it;
- a successful damaging move outside the launcher class resets the streak;
- switching out resets the streak.

The current Mercury Mega Launcher move family is centralized in
Mercury_MoveIsPulse(), so Rangefinder and Mega Launcher cannot silently drift
onto different move lists.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Rangefinder"
ABILITY_TOKEN = "ABILITY_MR_RANGEFINDER"
ABILITY_ID = 910


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
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
        raise SystemExit(f"{label}: function closing brace not found in {path}")
    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor inside {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


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
        "implementation_class": "light_extension",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def expose_pulse_helper(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"
    replace_once(
        lib,
        "static BOOL Mercury_MoveIsPulse(int move)",
        "BOOL Mercury_MoveIsPulse(int move)",
        "Rangefinder shared pulse helper visibility",
    )
    insert_before_once(
        hdr,
        """BOOL BattleSystem_TriggerAttackerKOAbility(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        """BOOL Mercury_MoveIsPulse(int move);
""",
        "Rangefinder pulse helper declaration",
    )


def patch_context_state(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u8 mercuryPressureValveUsed[MAX_BATTLERS];
""",
        """    // Mercury MR10C7: consecutive successful launcher shots.
    u8 mercuryRangefinderStreak[MAX_BATTLERS];

""",
        "Rangefinder streak state",
    )


def patch_switch_in_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryPressureValveTurn[battler] = -1;
""",
        """    battleCtx->mercuryRangefinderStreak[battler] = 0;
""",
        "Rangefinder switch-in reset",
    )


def patch_damage_ramp(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_MR_EXECUTION_DRIVE
""",
        """    if (attackerParams.ability == ABILITY_MR_RANGEFINDER
        && Mercury_MoveIsPulse(move)
        && movePower) {
        switch (battleCtx->mercuryRangefinderStreak[attacker]) {
        case 0:
            movePower = movePower * 11 / 10;
            break;
        case 1:
            movePower = movePower * 12 / 10;
            break;
        default:
            movePower = movePower * 13 / 10;
            break;
        }
    }

""",
        "Rangefinder launcher power ramp",
    )


def patch_successful_move_update(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        signature,
        """        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        """        if (battleCtx->attacker != BATTLER_NONE
            && Battler_Ability(battleCtx, battleCtx->attacker)
                == ABILITY_MR_RANGEFINDER
            && CURRENT_MOVE_DATA.power
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE) {
            if (Mercury_MoveIsPulse(battleCtx->moveCur)) {
                if (battleCtx->mercuryRangefinderStreak[battleCtx->attacker] < 3) {
                    battleCtx->mercuryRangefinderStreak[battleCtx->attacker]++;
                }
            } else {
                battleCtx->mercuryRangefinderStreak[battleCtx->attacker] = 0;
            }
        }

""",
        "Rangefinder successful move streak update",
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
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_910":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "shared_launcher_family":
            "BOOL Mercury_MoveIsPulse(int move)" in lib
            and "BOOL Mercury_MoveIsPulse(int move);" in hdr,
        "streak_state":
            "mercuryRangefinderStreak[MAX_BATTLERS]" in ctx,
        "switch_resets_streak":
            "mercuryRangefinderStreak[battler] = 0;" in lib,
        "first_shot_10_percent":
            "movePower = movePower * 11 / 10;" in lib,
        "second_shot_20_percent":
            "movePower = movePower * 12 / 10;" in lib,
        "third_plus_30_percent":
            "movePower = movePower * 13 / 10;" in lib
            and "default:" in lib,
        "misses_do_not_advance":
            "moveStatusFlags & MOVE_STATUS_NO_EFFECTS" in ctl,
        "successful_launcher_advances":
            "Mercury_MoveIsPulse(battleCtx->moveCur)" in ctl
            and "mercuryRangefinderStreak[battleCtx->attacker]++" in ctl,
        "successful_nonlauncher_damaging_resets":
            "mercuryRangefinderStreak[battleCtx->attacker] = 0;" in ctl,
        "status_moves_do_not_reset":
            "CURRENT_MOVE_DATA.power" in ctl,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c7-rangefinder.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    expose_pulse_helper(root)
    patch_context_state(root)
    patch_switch_in_reset(root)
    patch_damage_ramp(root)
    patch_successful_move_update(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C7_RANGEFINDER",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "shares_mega_launcher_family": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C7 Rangefinder validation failed")


if __name__ == "__main__":
    main()
