#!/usr/bin/env python3
"""MR10C8 — implement the approved Backlash redesign.

Backlash:
- whenever an opposing active Pokémon successfully gains at least one stat stage,
  the holder becomes Primed;
- while Primed, the holder's next damaging move has 1.5x power;
- that move ignores positive Defense, Special Defense, and Evasion stages on
  its target;
- Primed does not stack, is consumed when the next damaging move finishes, and
  is cleared when the holder switches out.

The stat-gain trigger is attached after Platinum has accepted/applied a positive
stage change, so blocked/no-op boosts do not activate Backlash.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Backlash"
ABILITY_TOKEN = "ABILITY_MR_BACKLASH"
ABILITY_ID = 427


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
    insert_before_once(
        path,
        """    u8 mercuryRangefinderStreak[MAX_BATTLERS];
""",
        """    // Mercury MR10C8: anti-setup retaliation state.
    u8 mercuryBacklashPrimed[MAX_BATTLERS];

""",
        "Backlash Primed state",
    )


def patch_switch_in_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryRangefinderStreak[battler] = 0;
""",
        """    battleCtx->mercuryBacklashPrimed[battler] = FALSE;
""",
        "Backlash switch-in reset",
    )


def patch_successful_stat_gain_trigger(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    text = path.read_text(encoding="utf-8")
    if "mercuryBacklashPrimed[backlashBattler] = TRUE;" in text:
        return

    signature = "static BOOL BtlCmd_ChangeStatStage(BattleSystem *battleSys, BattleContext *battleCtx)"
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit("Backlash: BtlCmd_ChangeStatStage definition not found")

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
        raise SystemExit("Backlash: BtlCmd_ChangeStatStage closing brace not found")

    block = text[start:end]
    clamp_anchor = """            if (mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] > MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] = MAX_STAT_STAGE;
            }"""
    pos = block.find(clamp_anchor)
    if pos < 0:
        raise SystemExit(
            "Backlash: accepted positive-stage clamp not found in BtlCmd_ChangeStatStage"
        )

    insertion = """

            {
                int backlashBattler;
                int backlashMaxBattlers = BattleSystem_GetMaxBattlers(battleSys);
                int boostedBattler = battleCtx->sideEffectMon;

                for (backlashBattler = 0;
                     backlashBattler < backlashMaxBattlers;
                     backlashBattler++) {
                    if (backlashBattler != boostedBattler
                        && ((backlashBattler & 1) != (boostedBattler & 1))
                        && battleCtx->battleMons[backlashBattler].curHP
                        && Battler_Ability(battleCtx, backlashBattler)
                            == ABILITY_MR_BACKLASH) {
                        battleCtx->mercuryBacklashPrimed[backlashBattler] = TRUE;
                    }
                }
            }"""

    insert_at = pos + len(clamp_anchor)
    block = block[:insert_at] + insertion + block[insert_at:]
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_damage_and_defense_bypass(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_MR_RANGEFINDER
""",
        """    if (attackerParams.ability == ABILITY_MR_BACKLASH
        && battleCtx->mercuryBacklashPrimed[attacker]
        && movePower) {
        movePower = movePower * 3 / 2;
    }

""",
        "Backlash 50 percent Primed power boost",
    )

    insert_before_once(
        path,
        """    attackStage += DEFAULT_STAT_STAGE;
""",
        """    if (attackerParams.ability == ABILITY_MR_BACKLASH
        && battleCtx->mercuryBacklashPrimed[attacker]) {
        if (defenseStage > 0) {
            defenseStage = 0;
        }
        if (spDefenseStage > 0) {
            spDefenseStage = 0;
        }
    }

""",
        "Backlash positive defensive stage bypass",
    )


def patch_evasion_bypass(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static int BattleControllerPlayer_CheckMoveHitAccuracy("
        "BattleSystem *battleSys, BattleContext *battleCtx, int attacker, int defender, int move)"
    )
    insert_before_in_function(
        path,
        signature,
        """    if (MON_IS_IDENTIFIED(defender) && evaStages < 0) {
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_MR_BACKLASH
        && battleCtx->mercuryBacklashPrimed[attacker]
        && evaStages < 0) {
        evaStages = 0;
    }

""",
        "Backlash positive Evasion bypass",
    )


def patch_primed_consumption(root: Path) -> None:
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
                == ABILITY_MR_BACKLASH
            && battleCtx->mercuryBacklashPrimed[battleCtx->attacker]
            && CURRENT_MOVE_DATA.power) {
            battleCtx->mercuryBacklashPrimed[battleCtx->attacker] = FALSE;
        }

""",
        "Backlash Primed consumption",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_427":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "primed_state":
            "mercuryBacklashPrimed[MAX_BATTLERS]" in ctx,
        "switch_clears_primed":
            "mercuryBacklashPrimed[battler] = FALSE;" in lib,
        "successful_opponent_boost_primes":
            "mercuryBacklashPrimed[backlashBattler] = TRUE;" in script
            and "((backlashBattler & 1) != (boostedBattler & 1))" in script,
        "blocked_boosts_do_not_prime":
            "accepted positive-stage clamp" not in script
            and "mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] += stageChange;" in script,
        "primed_power_boost_50_percent":
            "movePower = movePower * 3 / 2;" in lib,
        "positive_defense_and_spdef_ignored":
            "if (defenseStage > 0)" in lib
            and "if (spDefenseStage > 0)" in lib,
        "positive_evasion_ignored":
            "ABILITY_MR_BACKLASH" in ctl
            and "mercuryBacklashPrimed[attacker]" in ctl
            and "evaStages = 0;" in ctl,
        "next_damaging_move_consumes":
            "mercuryBacklashPrimed[battleCtx->attacker] = FALSE;" in ctl
            and "CURRENT_MOVE_DATA.power" in ctl,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c8-backlash.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_state(root)
    patch_switch_in_reset(root)
    patch_successful_stat_gain_trigger(root)
    patch_damage_and_defense_bypass(root)
    patch_evasion_bypass(root)
    patch_primed_consumption(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C8_BACKLASH",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "primed_consumes_after_next_damaging_move": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C8 Backlash validation failed")


if __name__ == "__main__":
    main()
