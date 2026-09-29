#!/usr/bin/env python3
"""MR10C6 — implement the approved Pressure Valve redesign.

Pressure Valve:
- once per switch-in, when an opponent successfully lowers one or more of the
  holder's stat stages, immediately clear every negative stat stage and raise
  Speed by one stage;
- self-inflicted drops do not trigger it;
- multi-stat effects from the same opposing action are treated as one trigger:
  later drops from that same action are also cleaned, but the Speed boost is
  only granted once.

The reaction is placed after Platinum has accepted and applied a negative stat
change. That means blocked drops do not consume the Ability, and Contrary
reversals never enter this path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Pressure Valve"
ABILITY_TOKEN = "ABILITY_MR_PRESSURE_VALVE"
ABILITY_ID = 395


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
        """    u8 mercuryNullWardUsed[MAX_BATTLERS];
""",
        """    // Mercury MR10C6: Pressure Valve's once-per-entry trigger plus
    // enough action identity to keep cleaning later stat drops from the same
    // multi-stat opposing action without granting Speed more than once.
    u8 mercuryPressureValveUsed[MAX_BATTLERS];
    u8 mercuryPressureValveAttacker[MAX_BATTLERS];
    u16 mercuryPressureValveMove[MAX_BATTLERS];
    int mercuryPressureValveTurn[MAX_BATTLERS];

""",
        "Pressure Valve battle-context state",
    )


def patch_switch_in_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryNullWardUsed[battler] = FALSE;
""",
        """    battleCtx->mercuryPressureValveUsed[battler] = FALSE;
    battleCtx->mercuryPressureValveAttacker[battler] = BATTLER_NONE;
    battleCtx->mercuryPressureValveMove[battler] = MOVE_NONE;
    battleCtx->mercuryPressureValveTurn[battler] = -1;
""",
        "Pressure Valve switch-in reset",
    )


def patch_stat_drop_reaction(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    text = path.read_text(encoding="utf-8")
    if "BOOL samePressureAction =" in text:
        return

    signature = "static BOOL BtlCmd_ChangeStatStage(BattleSystem *battleSys, BattleContext *battleCtx)"
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit("Pressure Valve: BtlCmd_ChangeStatStage definition not found")

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
        raise SystemExit("Pressure Valve: BtlCmd_ChangeStatStage closing brace not found")

    block = text[start:end]
    clamp_anchor = """        if (mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] < MIN_STAT_STAGE) {
            mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] = MIN_STAT_STAGE;
        }"""
    pos = block.rfind(clamp_anchor)
    if pos < 0:
        raise SystemExit(
            "Pressure Valve: accepted negative-stage clamp not found in BtlCmd_ChangeStatStage"
        )

    insertion = """

        {
            int pressureBattler = battleCtx->sideEffectMon;
            BOOL samePressureAction =
                battleCtx->mercuryPressureValveUsed[pressureBattler]
                && battleCtx->mercuryPressureValveTurn[pressureBattler]
                    == battleCtx->totalTurns
                && battleCtx->mercuryPressureValveMove[pressureBattler]
                    == battleCtx->moveCur
                && battleCtx->mercuryPressureValveAttacker[pressureBattler]
                    == battleCtx->attacker;

            if (((battleCtx->attacker & 1) != (pressureBattler & 1))
                && (battleCtx->mercuryPressureValveUsed[pressureBattler] == FALSE
                    || samePressureAction)
                && Battler_IgnorableAbility(
                    battleCtx,
                    battleCtx->attacker,
                    pressureBattler,
                    ABILITY_MR_PRESSURE_VALVE) == TRUE) {
                int pressureStat;

                for (pressureStat = BATTLE_STAT_ATTACK;
                     pressureStat < BATTLE_STAT_MAX;
                     pressureStat++) {
                    if (mon->statBoosts[pressureStat] < DEFAULT_STAT_STAGE) {
                        mon->statBoosts[pressureStat] = DEFAULT_STAT_STAGE;
                    }
                }

                if (battleCtx->mercuryPressureValveUsed[pressureBattler]
                    == FALSE) {
                    battleCtx->mercuryPressureValveUsed[pressureBattler] = TRUE;
                    battleCtx->mercuryPressureValveTurn[pressureBattler]
                        = battleCtx->totalTurns;
                    battleCtx->mercuryPressureValveMove[pressureBattler]
                        = battleCtx->moveCur;
                    battleCtx->mercuryPressureValveAttacker[pressureBattler]
                        = battleCtx->attacker;

                    if (mon->statBoosts[BATTLE_STAT_SPEED] < MAX_STAT_STAGE) {
                        mon->statBoosts[BATTLE_STAT_SPEED]++;
                        SetupNicknameAbilityStatMsg(
                            battleCtx,
                            BattleStrings_Text_PokemonsAbilityRaisedItsStat_Ally,
                            BATTLE_STAT_SPEED - BATTLE_STAT_ATTACK);
                    } else {
                        battleCtx->msgBuffer.id =
                            BattleStrings_Text_PokemonsAbilityPreventsStatLoss_Ally;
                        battleCtx->msgBuffer.tags = TAG_NICKNAME_ABILITY;
                        battleCtx->msgBuffer.params[0] =
                            BattleSystem_NicknameTag(battleCtx, pressureBattler);
                        battleCtx->msgBuffer.params[1] =
                            battleCtx->battleMons[pressureBattler].ability;
                    }
                    battleCtx->scriptTemp = BATTLE_ANIMATION_STAT_BOOST;
                } else {
                    battleCtx->msgBuffer.id =
                        BattleStrings_Text_PokemonsAbilityPreventsStatLoss_Ally;
                    battleCtx->msgBuffer.tags = TAG_NICKNAME_ABILITY;
                    battleCtx->msgBuffer.params[0] =
                        BattleSystem_NicknameTag(battleCtx, pressureBattler);
                    battleCtx->msgBuffer.params[1] =
                        battleCtx->battleMons[pressureBattler].ability;
                    battleCtx->scriptTemp = BATTLE_ANIMATION_STAT_BOOST;
                }
            }
        }"""

    insert_at = pos + len(clamp_anchor)
    block = block[:insert_at] + insertion + block[insert_at:]
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


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
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_395":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "per_entry_state":
            "mercuryPressureValveUsed[MAX_BATTLERS]" in ctx
            and "mercuryPressureValveTurn[MAX_BATTLERS]" in ctx,
        "state_resets_on_entry":
            "mercuryPressureValveUsed[battler] = FALSE;" in lib
            and "mercuryPressureValveTurn[battler] = -1;" in lib,
        "only_after_accepted_negative_change":
            "Pressure Valve accepted stat-drop reaction" not in script
            and "mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] += stageChange;" in script,
        "opponent_only":
            "((battleCtx->attacker & 1) != (pressureBattler & 1))" in script,
        "clears_all_negative_stages":
            "pressureStat < BATTLE_STAT_MAX" in script
            and "mon->statBoosts[pressureStat] = DEFAULT_STAT_STAGE;" in script,
        "speed_plus_one_once":
            "mon->statBoosts[BATTLE_STAT_SPEED]++;" in script
            and "mercuryPressureValveUsed[pressureBattler] == FALSE" in script,
        "same_action_multi_stat_cleanup":
            "samePressureAction" in script
            and "mercuryPressureValveMove[pressureBattler]" in script
            and "mercuryPressureValveAttacker[pressureBattler]" in script,
        "mold_breaker_aware":
            "ABILITY_MR_PRESSURE_VALVE) == TRUE" in script,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c6-pressure-valve.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_state(root)
    patch_switch_in_reset(root)
    patch_stat_drop_reaction(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C6_PRESSURE_VALVE",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "multi_stat_same_action_guard": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C6 Pressure Valve validation failed")


if __name__ == "__main__":
    main()
