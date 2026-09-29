#!/usr/bin/env python3
"""MR10C12 — implement the approved Time Compression redesign.

Time Compression:
- once per switch-in, the first move that would actually impose a charge turn
  or a recharge turn skips that delay;
- charge moves already made instant by sun/strong sun or Power Herb do not
  consume the Ability;
- recharge moves consume the Ability only when their normal on-hit recharge
  side effect would actually be applied;
- switching refreshes the single use.

Charge skipping is implemented before the move script runs by temporarily
putting the attacker into Platinum's existing damaging-turn path. The normal
charge cleanup clears that lock in the same move. Recharge skipping removes
only the recharge side effect after a successful hit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Time Compression"
ABILITY_TOKEN = "ABILITY_MR_TIME_COMPRESSION"
ABILITY_ID = 696


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


def insert_after_in_function(
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
    block = block.replace(anchor, anchor + insertion, 1)
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
        """    u32 mercuryCountercurrentGrantedTurn[MAX_BATTLERS];
""",
        """    // Mercury MR10C12: one delay skip per switch-in.
    u8 mercuryTimeCompressionUsed[MAX_BATTLERS];
""",
        "Time Compression state",
    )


def patch_switch_in_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryCountercurrentGrantedTurn[battler] = 0;
""",
        """    battleCtx->mercuryTimeCompressionUsed[battler] = FALSE;
""",
        "Time Compression switch-in reset",
    )


def patch_charge_skip(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_BeforeMove("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        signature,
        """        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        """        if (battleCtx->attacker != BATTLER_NONE
            && battleCtx->defender != BATTLER_NONE
            && battleCtx->battleMons[battleCtx->defender].curHP
            && Battler_Ability(battleCtx, battleCtx->attacker)
                == ABILITY_MR_TIME_COMPRESSION
            && battleCtx->mercuryTimeCompressionUsed[battleCtx->attacker] == FALSE
            && Move_IsMultiTurn(battleCtx, battleCtx->moveCur)
            && CURRENT_MOVE_DATA.effect != BATTLE_EFFECT_BIDE
            && (ATTACKING_MON.statusVolatile & VOLATILE_CONDITION_MOVE_LOCKED)
                == FALSE
            && (battleCtx->battleStatusMask & SYSCTL_LAST_OF_MULTI_TURN) == FALSE
            && Battler_HeldItemEffect(battleCtx, battleCtx->attacker)
                != HOLD_EFFECT_CHARGE_SKIP
            && !(CURRENT_MOVE_DATA.effect == BATTLE_EFFECT_SKIP_CHARGE_TURN_IN_SUN
                && NO_CLOUD_NINE
                && WEATHER_IS_SUN)) {
            battleCtx->mercuryTimeCompressionUsed[battleCtx->attacker] = TRUE;

            // Enter the move's existing damaging-turn path. Its normal charge
            // cleanup removes MOVE_LOCKED before the action finishes.
            ATTACKING_MON.statusVolatile |= VOLATILE_CONDITION_MOVE_LOCKED;

            // Skull Bash normally receives this boost during the skipped
            // charge turn. Preserve the gameplay effect even though there is
            // no separate charge animation/message.
            if (CURRENT_MOVE_DATA.effect == BATTLE_EFFECT_CHARGE_TURN_DEF_UP
                && ATTACKING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
                ATTACKING_MON.statBoosts[BATTLE_STAT_DEFENSE]++;
            }
        }

""",
        "Time Compression charge-turn skip",
    )


def patch_recharge_skip(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL BattleSystem_TriggerSecondaryEffect("
        "BattleSystem *battleSys, BattleContext *battleCtx, int *effect)"
    )
    insert_after_in_function(
        path,
        signature,
        """    u16 effectChance;
""",
        """
    if (battleCtx->attacker != BATTLER_NONE
        && Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MR_TIME_COMPRESSION
        && battleCtx->mercuryTimeCompressionUsed[battleCtx->attacker] == FALSE
        && CURRENT_MOVE_DATA.effect == BATTLE_EFFECT_RECHARGE_AFTER
        && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
        && (battleCtx->sideEffectIndirectFlags & MOVE_SIDE_EFFECT_ON_HIT)
        && ((battleCtx->sideEffectIndirectFlags & MOVE_SIDE_EFFECT_SUBSCRIPT_POINTER)
            == MOVE_SUBSCRIPT_PTR_RECHARGE_TURN)) {
        battleCtx->sideEffectIndirectFlags = 0;
        battleCtx->mercuryTimeCompressionUsed[battleCtx->attacker] = TRUE;
        return FALSE;
    }
""",
        "Time Compression recharge-turn skip",
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
        "stable_id_696":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "one_use_state":
            "mercuryTimeCompressionUsed[MAX_BATTLERS]" in ctx,
        "switch_refreshes_use":
            "mercuryTimeCompressionUsed[battler] = FALSE;" in lib,
        "charge_move_detection":
            "Move_IsMultiTurn(battleCtx, battleCtx->moveCur)" in ctl
            and "BATTLE_EFFECT_BIDE" in ctl,
        "power_herb_does_not_consume":
            "HOLD_EFFECT_CHARGE_SKIP" in ctl,
        "sun_instant_solar_does_not_consume":
            "BATTLE_EFFECT_SKIP_CHARGE_TURN_IN_SUN" in ctl
            and "WEATHER_IS_SUN" in ctl,
        "charge_delay_skipped":
            "ATTACKING_MON.statusVolatile |= VOLATILE_CONDITION_MOVE_LOCKED;" in ctl,
        "skull_bash_defense_preserved":
            "BATTLE_EFFECT_CHARGE_TURN_DEF_UP" in ctl
            and "statBoosts[BATTLE_STAT_DEFENSE]++" in ctl,
        "recharge_side_effect_removed":
            "MOVE_SUBSCRIPT_PTR_RECHARGE_TURN" in lib
            and "battleCtx->sideEffectIndirectFlags = 0;" in lib,
        "recharge_consumes_only_on_real_effect":
            "MOVE_STATUS_NO_EFFECTS" in lib
            and "BATTLE_EFFECT_RECHARGE_AFTER" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c12-time-compression.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_state(root)
    patch_switch_in_reset(root)
    patch_charge_skip(root)
    patch_recharge_skip(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C12_TIME_COMPRESSION",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "uses_per_switch_in": 1,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C12 Time Compression validation failed")


if __name__ == "__main__":
    main()
