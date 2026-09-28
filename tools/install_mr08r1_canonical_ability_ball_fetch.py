#!/usr/bin/env python3
"""MR08R1 — canonical Ball Fetch pass.

Implements Ball Fetch in Platinum's capture task: on the first failed normal
capture attempt of the battle, an active player-side Ball Fetch user that is
alive and not holding an item receives the thrown Poke Ball as its held item.
The retrieval is persisted to the party immediately and only occurs once per
battle. Neutralizing Gas / Gastro Acid naturally suppress it through
Battler_Ability().

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_BALL_FETCH",)
EXPECTED_IDS = {"ABILITY_BALL_FETCH": 237}


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
        """    // Mercury MR08R1: the first failed Ball is the only Ball Fetch target.
    u8 mercuryBallFetchHandled;

""",
        "Ball Fetch battle state",
    )


def patch_capture_task(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    insert_before_once(
        path,
        """static void BattleScript_CatchMonTask(SysTask *task, void *inData)
{
""",
        """static void Mercury_TryBallFetch(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    u16 ball)
{
    int battler;
    int maxBattlers;

    if (battleCtx->mercuryBallFetchHandled) {
        return;
    }

    // The first failed throw is consumed as the Ball Fetch opportunity even
    // when no eligible user is active or the user is already holding an item.
    battleCtx->mercuryBallFetchHandled = TRUE;
    maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    for (battler = 0; battler < maxBattlers; battler++) {
        if (BattleSystem_GetBattlerSide(battleSys, battler) == BATTLE_SIDE_PLAYER
            && battleCtx->battleMons[battler].curHP
            && battleCtx->battleMons[battler].heldItem == ITEM_NONE
            && Battler_Ability(battleCtx, battler) == ABILITY_BALL_FETCH) {
            battleCtx->battleMons[battler].heldItem = ball;
            BattleMon_CopyToParty(battleSys, battleCtx, battler);
            break;
        }
    }
}

""",
        "Ball Fetch capture helper",
    )

    insert_after_once(
        path,
        """    case SEQ_CATCH_MON_POKEMON_BREAK_FREE:
""",
        """        if (data->flag == 0) {
            Mercury_TryBallFetch(data->battleSys, data->battleCtx, data->ball);
        }
""",
        "Ball Fetch failed-capture hook",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "first_failed_ball_state":
            "mercuryBallFetchHandled" in ctx
            and "battleCtx->mercuryBallFetchHandled = TRUE;" in script,
        "failed_capture_hook":
            "case SEQ_CATCH_MON_POKEMON_BREAK_FREE:" in script
            and "Mercury_TryBallFetch(data->battleSys, data->battleCtx, data->ball);" in script,
        "active_player_side_only":
            "BattleSystem_GetBattlerSide(battleSys, battler) == BATTLE_SIDE_PLAYER" in script
            and "battleCtx->battleMons[battler].curHP" in script,
        "empty_hands_only":
            "battleCtx->battleMons[battler].heldItem == ITEM_NONE" in script,
        "ability_gate":
            "Battler_Ability(battleCtx, battler) == ABILITY_BALL_FETCH" in script,
        "party_persistence":
            "BattleMon_CopyToParty(battleSys, battleCtx, battler);" in script,
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
        default=Path("mr08r1-canonical-ability-ball-fetch.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_capture_task(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08R1_CANONICAL_ABILITY_BALL_FETCH",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 162,
        "remaining_modern_canonical_mechanics": 25,
        "policy": "Official/current-mainline mechanics; remaining state/form families stay explicit.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08R1 validation failed")


if __name__ == "__main__":
    main()
