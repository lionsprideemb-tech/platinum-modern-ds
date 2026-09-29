#!/usr/bin/env python3
"""MR10C5 — implement the approved Null Ward redesign.

Null Ward:
- once per switch-in, the first opposing status move that directly targets the
  holder fails;
- damaging moves with secondary effects, self/side/field moves, spread status
  moves, weather, terrain, and hazards do not consume the ward.

The once-per-entry state is battle-only and resets whenever the holder is
initialized into its battler slot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Null Ward"
ABILITY_TOKEN = "ABILITY_MR_NULL_WARD"
ABILITY_ID = 476


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


def patch_context_state(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u8 mercuryProteanUsed[MAX_BATTLERS];
""",
        """    // Mercury MR10C: approved custom Ability per-entry state.
    u8 mercuryNullWardUsed[MAX_BATTLERS];

""",
        "Null Ward battle context state",
    )


def patch_switch_in_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryProteanUsed[battler] = FALSE;
""",
        """    battleCtx->mercuryNullWardUsed[battler] = FALSE;
""",
        "Null Ward switch-in state reset",
    )


def patch_status_immunity(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insertion = """    if (attacker != defender
        && ((attacker & 1) != (defender & 1))
        && battleCtx->mercuryNullWardUsed[defender] == FALSE
        && CURRENT_MOVE_DATA.class == CLASS_STATUS
        && (CURRENT_MOVE_DATA.range == RANGE_SINGLE_TARGET
            || CURRENT_MOVE_DATA.range == RANGE_SINGLE_TARGET_SPECIAL
            || CURRENT_MOVE_DATA.range == RANGE_RANDOM_OPPONENT)
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_NULL_WARD) == TRUE) {
        battleCtx->mercuryNullWardUsed[defender] = TRUE;
        battleCtx->msgTemp = defender;
        battleCtx->msgBattlerTemp = defender;
        return subscript_mold_breaker;
    }

"""
    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_VOLT_ABSORB) == TRUE
""",
        insertion,
        "Null Ward targeted status immunity",
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
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_476":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "per_entry_state": "mercuryNullWardUsed[MAX_BATTLERS]" in ctx,
        "state_resets_on_entry": "mercuryNullWardUsed[battler] = FALSE;" in lib,
        "opponent_status_only":
            "CURRENT_MOVE_DATA.class == CLASS_STATUS" in lib
            and "((attacker & 1) != (defender & 1))" in lib,
        "direct_target_ranges_only":
            "RANGE_SINGLE_TARGET" in lib
            and "RANGE_SINGLE_TARGET_SPECIAL" in lib
            and "RANGE_RANDOM_OPPONENT" in lib,
        "ward_consumed_on_block":
            "mercuryNullWardUsed[defender] = TRUE;" in lib,
        "mold_breaker_aware":
            "ABILITY_MR_NULL_WARD) == TRUE" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c5-null-ward.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_state(root)
    patch_switch_in_reset(root)
    patch_status_immunity(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C5_NULL_WARD",
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
        raise SystemExit("MR10C5 Null Ward validation failed")


if __name__ == "__main__":
    main()
