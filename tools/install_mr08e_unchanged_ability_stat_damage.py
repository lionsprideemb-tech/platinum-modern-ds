#!/usr/bin/env python3
"""MR08E — unchanged canonical Ability fast pass, stat/damage family.

Adds ten more official/current-mainline Ability mechanics on shared Platinum
battle hooks:

- Defeatist
- Friend Guard
- Flare Boost
- Toxic Boost
- Sand Rush
- Stamina
- Water Compaction
- Merciless
- Steelworker
- Steely Spirit

This is mechanics-only; locked MR07 Summary/editor visuals are untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_DEFEATIST",
    "ABILITY_FRIEND_GUARD",
    "ABILITY_FLARE_BOOST",
    "ABILITY_TOXIC_BOOST",
    "ABILITY_SAND_RUSH",
    "ABILITY_STAMINA",
    "ABILITY_WATER_COMPACTION",
    "ABILITY_MERCILESS",
    "ABILITY_STEELWORKER",
    "ABILITY_STEELY_SPIRIT",
)

EXPECTED_IDS = {
    "ABILITY_DEFEATIST": 129,
    "ABILITY_FRIEND_GUARD": 132,
    "ABILITY_FLARE_BOOST": 138,
    "ABILITY_TOXIC_BOOST": 137,
    "ABILITY_SAND_RUSH": 146,
    "ABILITY_STAMINA": 192,
    "ABILITY_WATER_COMPACTION": 195,
    "ABILITY_MERCILESS": 196,
    "ABILITY_STEELWORKER": 200,
    "ABILITY_STEELY_SPIRIT": 252,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {count}"
        )
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    checks: dict[str, bool] = {}
    for token, expected in EXPECTED_IDS.items():
        checks[f"{token.lower()}_id"] = (
            len(abilities) > expected and abilities[expected] == token
        )
    return checks


def patch_speed(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """        if ((battler1Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler1Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)) {
            battler1Speed *= 2;
        }
""",
        """        if ((battler1Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler1Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler1Ability == ABILITY_SAND_RUSH && WEATHER_IS_SAND)) {
            battler1Speed *= 2;
        }
""",
        "Sand Rush battler1",
    )

    replace_once(
        path,
        """        if ((battler2Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler2Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)) {
            battler2Speed *= 2;
        }
""",
        """        if ((battler2Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler2Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler2Ability == ABILITY_SAND_RUSH && WEATHER_IS_SAND)) {
            battler2Speed *= 2;
        }
""",
        "Sand Rush battler2",
    )


def patch_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
""",
        """    if (attackerParams.ability == ABILITY_DEFEATIST
        && attackerParams.curHP <= attackerParams.maxHP / 2) {
        attackStat /= 2;
        spAttackStat /= 2;
    }

    if (attackerParams.ability == ABILITY_TOXIC_BOOST
        && (attackerParams.statusMask & MON_CONDITION_ANY_POISON)) {
        attackStat = attackStat * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_FLARE_BOOST
        && (attackerParams.statusMask & MON_CONDITION_BURN)) {
        spAttackStat = spAttackStat * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_STEELWORKER
        && moveType == TYPE_STEEL) {
        movePower = movePower * 15 / 10;
    }

    if (moveType == TYPE_STEEL
        && attackerParams.ability == ABILITY_STEELY_SPIRIT) {
        movePower = movePower * 15 / 10;
    }

    if (moveType == TYPE_STEEL
        && Mercury_AllyHasAbility(
            battleSys, battleCtx, attacker, ABILITY_STEELY_SPIRIT)) {
        movePower = movePower * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
""",
        "Defeatist / boosts / Steelworker / Steely Spirit",
    )

    insert_before_once(
        path,
        """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
""",
        """    if (Mercury_AllyHasAbility(
            battleSys, battleCtx, defender, ABILITY_FRIEND_GUARD)) {
        damage = damage * 75 / 100;
    }

""",
        "Friend Guard damage reduction",
    )


def patch_merciless(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    if (BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_BATTLE_ARMOR) == FALSE
""",
        """    if (((attackerAbility == ABILITY_MERCILESS
                && (battleCtx->battleMons[defender].status & MON_CONDITION_ANY_POISON))
            || BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0)
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_BATTLE_ARMOR) == FALSE
""",
        "Merciless guaranteed critical",
    )


def patch_on_hit(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    case ABILITY_AFTERMATH:
""",
        """    case ABILITY_STAMINA:
        if (DEFENDING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;

    case ABILITY_WATER_COMPACTION: {
        int moveType;

        if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NORMALIZE) {
            moveType = TYPE_NORMAL;
        } else if (battleCtx->moveType) {
            moveType = battleCtx->moveType;
        } else {
            moveType = CURRENT_MOVE_DATA.type;
        }

        if (DEFENDING_MON.curHP
            && moveType == TYPE_WATER
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_DEFENSE_UP_2_STAGES;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;
    }

""",
        "Stamina / Water Compaction on-hit",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "defeatist_hook":
            "attackerParams.ability == ABILITY_DEFEATIST" in lib,
        "friend_guard_hook":
            "ABILITY_FRIEND_GUARD" in lib
            and "damage = damage * 75 / 100;" in lib,
        "flare_boost_hook":
            "attackerParams.ability == ABILITY_FLARE_BOOST" in lib,
        "toxic_boost_hook":
            "attackerParams.ability == ABILITY_TOXIC_BOOST" in lib,
        "sand_rush_hook":
            lib.count("ABILITY_SAND_RUSH && WEATHER_IS_SAND") == 2,
        "stamina_hook":
            "case ABILITY_STAMINA:" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in lib,
        "water_compaction_hook":
            "case ABILITY_WATER_COMPACTION:" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_2_STAGES" in lib,
        "merciless_hook":
            "attackerAbility == ABILITY_MERCILESS" in lib
            and "MON_CONDITION_ANY_POISON" in lib,
        "steelworker_hook":
            "attackerParams.ability == ABILITY_STEELWORKER" in lib,
        "steely_spirit_hook":
            lib.count("ABILITY_STEELY_SPIRIT") >= 2,
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
        default=Path("mr08e-unchanged-ability-stat-damage.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_speed(root)
    patch_damage(root)
    patch_merciless(root)
    patch_on_hit(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08E_UNCHANGED_ABILITY_STAT_DAMAGE",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 45,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08E validation failed")


if __name__ == "__main__":
    main()
