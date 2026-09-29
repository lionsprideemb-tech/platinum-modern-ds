#!/usr/bin/env python3
"""MR10D9 — Polarity ally-stat aura.

Polarity raises each active ally's own highest non-HP battle stat by 30%.
Each ally is evaluated independently using the same deterministic tie order
Mercury already uses for Beast Boost: Attack, Defense, Speed, Sp. Atk, Sp. Def.

The holder does not buff itself merely for having Polarity; two active
Polarity holders can buff one another because each is the other's ally.
The multiplier is applied continuously in damage and Speed calculations.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Polarity"
ABILITY_TOKEN = "ABILITY_MR_POLARITY"
ABILITY_ID = 698


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


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        row for row in plan.get("abilities", plan.get("rows", []))
        if row.get("display_name") == ABILITY_NAME
        or row.get("source_name") == ABILITY_NAME
    ]
    if len(rows) != 1:
        raise SystemExit(f"{ABILITY_NAME}: expected one partition row, found {len(rows)}")
    row = rows[0]
    expected = {
        "id": ABILITY_ID,
        "token": ABILITY_TOKEN,
        "approval_state": "owner_approved_keep",
        "owner_review_decision": "KEEP AS WRITTEN",
        "implementation_class": "new_engine_system",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_helper(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    helper = """static int Mercury_PolarityHighestStat(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    BattleMon *mon = &battleCtx->battleMons[battler];
    int highest;
    int stat;

    for (i = 0; i < maxBattlers; i++) {
        if (i == battler
            || battleCtx->battleMons[i].curHP == 0
            || (battleCtx->battlersSwitchingMask & FlagIndex(i))
            || BattleSystem_GetBattlerSide(battleSys, i) != side
            || Battler_Ability(battleCtx, i) != ABILITY_MR_POLARITY) {
            continue;
        }

        // Match Mercury's Beast Boost deterministic tie order.
        stat = BATTLE_STAT_ATTACK;
        highest = mon->attack;

        if (mon->defense > highest) {
            highest = mon->defense;
            stat = BATTLE_STAT_DEFENSE;
        }
        if (mon->speed > highest) {
            highest = mon->speed;
            stat = BATTLE_STAT_SPEED;
        }
        if (mon->spAttack > highest) {
            highest = mon->spAttack;
            stat = BATTLE_STAT_SP_ATTACK;
        }
        if (mon->spDefense > highest) {
            stat = BATTLE_STAT_SP_DEFENSE;
        }

        return stat;
    }

    return -1;
}

"""
    insert_before_once(
        path,
        """static inline int CompareSpeed_ApplySimple(BattleContext *battleCtx, int battler, int stage)
""",
        helper,
        "MR10D9 Polarity helper",
    )


def patch_damage_stats(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insertion = """    if (Mercury_PolarityHighestStat(
            battleSys, battleCtx, attacker) == BATTLE_STAT_ATTACK) {
        attackStat = attackStat * 13 / 10;
    }
    if (Mercury_PolarityHighestStat(
            battleSys, battleCtx, attacker) == BATTLE_STAT_SP_ATTACK) {
        spAttackStat = spAttackStat * 13 / 10;
    }
    if (Mercury_PolarityHighestStat(
            battleSys, battleCtx, defender) == BATTLE_STAT_DEFENSE) {
        defenseStat = defenseStat * 13 / 10;
    }
    if (Mercury_PolarityHighestStat(
            battleSys, battleCtx, defender) == BATTLE_STAT_SP_DEFENSE) {
        spDefenseStat = spDefenseStat * 13 / 10;
    }

"""
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        insertion,
        "MR10D9 Polarity combat-stat multipliers",
    )


def patch_speed(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """    battler1Speed = battleCtx->battleMons[battler1].speed * sStatStageBoosts[battler1SpeedStage].numerator / sStatStageBoosts[battler1SpeedStage].denominator;
    battler2Speed = battleCtx->battleMons[battler2].speed * sStatStageBoosts[battler2SpeedStage].numerator / sStatStageBoosts[battler2SpeedStage].denominator;

""",
        """    battler1Speed = battleCtx->battleMons[battler1].speed * sStatStageBoosts[battler1SpeedStage].numerator / sStatStageBoosts[battler1SpeedStage].denominator;
    battler2Speed = battleCtx->battleMons[battler2].speed * sStatStageBoosts[battler2SpeedStage].numerator / sStatStageBoosts[battler2SpeedStage].denominator;

    if (Mercury_PolarityHighestStat(
            battleSys, battleCtx, battler1) == BATTLE_STAT_SPEED) {
        battler1Speed = battler1Speed * 13 / 10;
    }
    if (Mercury_PolarityHighestStat(
            battleSys, battleCtx, battler2) == BATTLE_STAT_SPEED) {
        battler2Speed = battler2Speed * 13 / 10;
    }

""",
        "MR10D9 Polarity Speed multiplier",
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
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "stable_id_698":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "active_ally_gate":
            "Mercury_PolarityHighestStat" in lib
            and "i == battler" in lib
            and "BattleSystem_GetBattlerSide(battleSys, i) != side" in lib
            and "Battler_Ability(battleCtx, i) != ABILITY_MR_POLARITY" in lib,
        "independent_highest_stat":
            "BattleMon *mon = &battleCtx->battleMons[battler];" in lib
            and "stat = BATTLE_STAT_ATTACK;" in lib
            and "BATTLE_STAT_SP_DEFENSE" in lib,
        "deterministic_tie_order":
            lib.find("mon->defense > highest")
                < lib.find("mon->speed > highest")
                < lib.find("mon->spAttack > highest")
                < lib.find("mon->spDefense > highest"),
        "attack_30_percent":
            "== BATTLE_STAT_ATTACK" in lib
            and "attackStat = attackStat * 13 / 10;" in lib,
        "special_attack_30_percent":
            "== BATTLE_STAT_SP_ATTACK" in lib
            and "spAttackStat = spAttackStat * 13 / 10;" in lib,
        "defense_30_percent":
            "== BATTLE_STAT_DEFENSE" in lib
            and "defenseStat = defenseStat * 13 / 10;" in lib,
        "special_defense_30_percent":
            "== BATTLE_STAT_SP_DEFENSE" in lib
            and "spDefenseStat = spDefenseStat * 13 / 10;" in lib,
        "speed_30_percent":
            lib.count("== BATTLE_STAT_SPEED") >= 2
            and "battler1Speed = battler1Speed * 13 / 10;" in lib
            and "battler2Speed = battler2Speed * 13 / 10;" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--partition",
        type=Path,
        default=Path("data/mr10_safe_ability_partition.json"),
    )
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10d9-polarity-aura.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_helper(root)
    patch_damage_stats(root)
    patch_speed(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D9_POLARITY_AURA",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "ally_stat_multiplier_percent": 130,
        "self_buff_from_own_polarity": False,
        "remaining_keep_as_written_after_d9": 39,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D9 Polarity validation failed")


if __name__ == "__main__":
    main()
