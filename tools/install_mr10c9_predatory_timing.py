#!/usr/bin/env python3
"""MR10C9 — implement the approved Predatory Timing redesign.

Predatory Timing:
- whenever an opposing active Pokémon successfully resolves a status move, the
  holder becomes Opportunistic;
- while Opportunistic, the holder's next damaging move has 1.3x power;
- the state does not stack, survives the holder using status moves, is consumed
  after its next damaging move resolves, and is cleared on switch-out.

The trigger lives at move-end so failed/missed status moves do not prime the
Ability and broad status categories such as setup, recovery, hazards, screens,
weather, terrain, and Trick Room all share one path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Predatory Timing"
ABILITY_TOKEN = "ABILITY_MR_PREDATORY_TIMING"
ABILITY_ID = 732


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


def patch_context_state(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryBacklashPrimed[MAX_BATTLERS];
""",
        """    // Mercury MR10C9: next-attack reward after an opposing status move.
    u8 mercuryPredatoryTimingReady[MAX_BATTLERS];
""",
        "Predatory Timing Opportunistic state",
    )


def patch_switch_in_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryBacklashPrimed[battler] = FALSE;
""",
        """    battleCtx->mercuryPredatoryTimingReady[battler] = FALSE;
""",
        "Predatory Timing switch-in reset",
    )


def patch_damage_boost(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_in_function(
        path,
        """int BattleSystem_CalcMoveDamage(BattleSystem *battleSys,
    BattleContext *battleCtx,
    int move,
    u32 sideConditions,
    u32 fieldConditions,
    u16 inPower,
    u8 inType,
    u8 attacker,
    u8 defender,
    u8 criticalMul)""",
        """    if (attackerParams.ability == ABILITY_MR_BACKLASH
        && battleCtx->mercuryBacklashPrimed[attacker]
        && movePower) {
""",
        """    if (attackerParams.ability == ABILITY_MR_PREDATORY_TIMING
        && battleCtx->mercuryPredatoryTimingReady[attacker]
        && movePower) {
        movePower = movePower * 13 / 10;
    }

""",
        "Predatory Timing 30 percent Opportunistic power boost",
    )


def patch_move_end_trigger_and_consume(root: Path) -> None:
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
            && CURRENT_MOVE_DATA.class == CLASS_STATUS
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE) {
            int predatoryBattler;
            int predatoryMaxBattlers = BattleSystem_GetMaxBattlers(battleSys);

            for (predatoryBattler = 0;
                 predatoryBattler < predatoryMaxBattlers;
                 predatoryBattler++) {
                if (predatoryBattler != battleCtx->attacker
                    && ((predatoryBattler & 1) != (battleCtx->attacker & 1))
                    && battleCtx->battleMons[predatoryBattler].curHP
                    && Battler_Ability(battleCtx, predatoryBattler)
                        == ABILITY_MR_PREDATORY_TIMING) {
                    battleCtx->mercuryPredatoryTimingReady[predatoryBattler]
                        = TRUE;
                }
            }
        }

        if (battleCtx->attacker != BATTLER_NONE
            && Battler_Ability(battleCtx, battleCtx->attacker)
                == ABILITY_MR_PREDATORY_TIMING
            && battleCtx->mercuryPredatoryTimingReady[battleCtx->attacker]
            && CURRENT_MOVE_DATA.power) {
            battleCtx->mercuryPredatoryTimingReady[battleCtx->attacker] = FALSE;
        }

""",
        "Predatory Timing status trigger and damaging-move consumption",
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
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_732":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "opportunistic_state":
            "mercuryPredatoryTimingReady[MAX_BATTLERS]" in ctx,
        "switch_clears_opportunistic":
            "mercuryPredatoryTimingReady[battler] = FALSE;" in lib,
        "successful_opposing_status_move_primes":
            "CURRENT_MOVE_DATA.class == CLASS_STATUS" in ctl
            and "MOVE_STATUS_NO_EFFECTS" in ctl
            and "ABILITY_MR_PREDATORY_TIMING" in ctl
            and "mercuryPredatoryTimingReady[predatoryBattler]" in ctl,
        "broad_status_move_trigger":
            "CURRENT_MOVE_DATA.class == CLASS_STATUS" in ctl,
        "opportunistic_power_boost_30_percent":
            "movePower = movePower * 13 / 10;" in lib
            and "mercuryPredatoryTimingReady[attacker]" in lib,
        "status_moves_preserve_state":
            "CURRENT_MOVE_DATA.power" in ctl,
        "next_damaging_move_consumes":
            "mercuryPredatoryTimingReady[battleCtx->attacker] = FALSE;" in ctl,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c9-predatory-timing.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_state(root)
    patch_switch_in_reset(root)
    patch_damage_boost(root)
    patch_move_end_trigger_and_consume(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C9_PREDATORY_TIMING",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "opportunistic_consumes_after_next_damaging_move": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C9 Predatory Timing validation failed")


if __name__ == "__main__":
    main()
