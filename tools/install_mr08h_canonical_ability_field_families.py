#!/usr/bin/env python3
"""MR08H — canonical Ability fast pass, field/shared families.

Adds fifteen more official/current-mainline Ability mechanics using shared
Platinum battle hooks:

- Sap Sipper
- Victory Star
- Turboblaze
- Teravolt
- Dark Aura
- Fairy Aura
- Aura Break
- Slush Rush
- Long Reach
- Transistor
- Dragon's Maw
- Vessel of Ruin
- Sword of Ruin
- Tablets of Ruin
- Beads of Ruin

This pass changes battle mechanics only. Locked MR07 Summary/editor visuals
remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_SAP_SIPPER",
    "ABILITY_VICTORY_STAR",
    "ABILITY_TURBOBLAZE",
    "ABILITY_TERAVOLT",
    "ABILITY_DARK_AURA",
    "ABILITY_FAIRY_AURA",
    "ABILITY_AURA_BREAK",
    "ABILITY_SLUSH_RUSH",
    "ABILITY_LONG_REACH",
    "ABILITY_TRANSISTOR",
    "ABILITY_DRAGONS_MAW",
    "ABILITY_VESSEL_OF_RUIN",
    "ABILITY_SWORD_OF_RUIN",
    "ABILITY_TABLETS_OF_RUIN",
    "ABILITY_BEADS_OF_RUIN",
)

EXPECTED_IDS = {
    "ABILITY_SAP_SIPPER": 157,
    "ABILITY_VICTORY_STAR": 162,
    "ABILITY_TURBOBLAZE": 163,
    "ABILITY_TERAVOLT": 164,
    "ABILITY_DARK_AURA": 186,
    "ABILITY_FAIRY_AURA": 187,
    "ABILITY_AURA_BREAK": 188,
    "ABILITY_SLUSH_RUSH": 202,
    "ABILITY_LONG_REACH": 203,
    "ABILITY_TRANSISTOR": 262,
    "ABILITY_DRAGONS_MAW": 263,
    "ABILITY_VESSEL_OF_RUIN": 284,
    "ABILITY_SWORD_OF_RUIN": 285,
    "ABILITY_TABLETS_OF_RUIN": 286,
    "ABILITY_BEADS_OF_RUIN": 287,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all_required(
    path: Path,
    old: str,
    new: str,
    minimum: int,
    label: str,
) -> int:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count < minimum:
        raise SystemExit(
            f"{label}: expected at least {minimum} matches in {path}, found {count}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")
    return count


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


def patch_battle_lib(root: Path) -> int:
    path = root / "src/battle/battle_lib.c"

    # Turboblaze and Teravolt are canonical Mold Breaker family members. Convert
    # Platinum's direct Mold Breaker tests before installing the shared helper.
    replace_all_required(
        path,
        "Battler_Ability(battleCtx, attacker) == ABILITY_MOLD_BREAKER",
        "Mercury_IsMoldBreakerAbility(Battler_Ability(battleCtx, attacker))",
        1,
        "Turboblaze/Teravolt direct attacker equality",
    )
    replace_all_required(
        path,
        "Battler_Ability(battleCtx, attacker) != ABILITY_MOLD_BREAKER",
        "!Mercury_IsMoldBreakerAbility(Battler_Ability(battleCtx, attacker))",
        1,
        "Turboblaze/Teravolt direct attacker inequality",
    )
    replace_all_required(
        path,
        "attackerAbility != ABILITY_MOLD_BREAKER",
        "!Mercury_IsMoldBreakerAbility(attackerAbility)",
        2,
        "Turboblaze/Teravolt effectiveness aliases",
    )
    replace_all_required(
        path,
        "Battler_Ability(battleCtx, battler) == ABILITY_MOLD_BREAKER",
        "Mercury_IsMoldBreakerAbility(Battler_Ability(battleCtx, battler))",
        1,
        "Turboblaze/Teravolt switch-in alias",
    )

    # Long Reach makes otherwise-contacting moves non-contact for all of the
    # shared contact-reaction lanes in battle_lib.c.
    contact_replacements = replace_all_required(
        path,
        "(CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)",
        "Mercury_MoveMakesContact(battleCtx, battleCtx->attacker, battleCtx->moveCur)",
        5,
        "Long Reach contact family",
    )

    insert_before_once(
        path,
        """static BOOL Mercury_MoveIsSlicing(int move)
""",
        """static BOOL Mercury_IsMoldBreakerAbility(int ability)
{
    return ability == ABILITY_MOLD_BREAKER
        || ability == ABILITY_TURBOBLAZE
        || ability == ABILITY_TERAVOLT;
}

static BOOL Mercury_MoveMakesContact(
    BattleContext *battleCtx,
    int attacker,
    int move)
{
    return (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT)
        && Battler_Ability(battleCtx, attacker) != ABILITY_LONG_REACH;
}

""",
        "MR08H shared Mold Breaker/contact helpers",
    )

    # Slush Rush uses Platinum's hail field condition as Mercury's Gen-9
    # snow-equivalent weather representation.
    replace_once(
        path,
        """        if ((battler1Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler1Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler1Ability == ABILITY_SAND_RUSH && WEATHER_IS_SAND)) {
            battler1Speed *= 2;
        }
""",
        """        if ((battler1Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler1Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler1Ability == ABILITY_SAND_RUSH && WEATHER_IS_SAND)
            || (battler1Ability == ABILITY_SLUSH_RUSH && WEATHER_IS_HAIL)) {
            battler1Speed *= 2;
        }
""",
        "Slush Rush battler1",
    )
    replace_once(
        path,
        """        if ((battler2Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler2Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler2Ability == ABILITY_SAND_RUSH && WEATHER_IS_SAND)) {
            battler2Speed *= 2;
        }
""",
        """        if ((battler2Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler2Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler2Ability == ABILITY_SAND_RUSH && WEATHER_IS_SAND)
            || (battler2Ability == ABILITY_SLUSH_RUSH && WEATHER_IS_HAIL)) {
            battler2Speed *= 2;
        }
""",
        "Slush Rush battler2",
    )

    # Sap Sipper blocks opposing Grass moves and raises Attack by one stage.
    # It shares the pre-move immunity lane, so status and damaging Grass moves
    # are both stopped before their normal effect.
    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_EARTH_EATER) == TRUE
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_SAP_SIPPER) == TRUE
        && moveType == TYPE_GRASS
        && attacker != defender) {
        battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = defender;
        return subscript_update_stat_stage;
    }

""",
        "Sap Sipper immunity/Attack hook",
    )

    # The four Ruin Abilities are field effects and do not affect their own
    # holder. Same-name copies do not stack, so each family is applied once if
    # any other living holder exists.
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_DEFEATIST
""",
        """    if (moveClass == CLASS_PHYSICAL
        && BattleSystem_CountAbility(
            battleSys,
            battleCtx,
            COUNT_ALIVE_BATTLERS_EXCEPT_ME,
            attacker,
            ABILITY_TABLETS_OF_RUIN)) {
        attackStat = attackStat * 3 / 4;
    }

    if (moveClass == CLASS_SPECIAL
        && BattleSystem_CountAbility(
            battleSys,
            battleCtx,
            COUNT_ALIVE_BATTLERS_EXCEPT_ME,
            attacker,
            ABILITY_VESSEL_OF_RUIN)) {
        spAttackStat = spAttackStat * 3 / 4;
    }

    if (moveClass == CLASS_PHYSICAL
        && BattleSystem_CountAbility(
            battleSys,
            battleCtx,
            COUNT_ALIVE_BATTLERS_EXCEPT_ME,
            defender,
            ABILITY_SWORD_OF_RUIN)) {
        defenseStat = defenseStat * 3 / 4;
    }

    if (moveClass == CLASS_SPECIAL
        && BattleSystem_CountAbility(
            battleSys,
            battleCtx,
            COUNT_ALIVE_BATTLERS_EXCEPT_ME,
            defender,
            ABILITY_BEADS_OF_RUIN)) {
        spDefenseStat = spDefenseStat * 3 / 4;
    }

""",
        "Ruin Ability stat family",
    )

    # Current-mainline Transistor is 1.3x; Dragon's Maw is 1.5x. Dark/Fairy
    # Aura apply a field-wide 4/3 modifier, reversed to 3/4 by Aura Break.
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_ROCKY_PAYLOAD
""",
        """    if (attackerParams.ability == ABILITY_TRANSISTOR
        && moveType == TYPE_ELECTRIC) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_DRAGONS_MAW
        && moveType == TYPE_DRAGON) {
        movePower = movePower * 15 / 10;
    }

    if (moveType == TYPE_DARK
        && BattleSystem_CountAbility(
            battleSys, battleCtx, COUNT_ALIVE_BATTLERS, 0, ABILITY_DARK_AURA)) {
        if (BattleSystem_CountAbility(
                battleSys,
                battleCtx,
                COUNT_ALIVE_BATTLERS,
                0,
                ABILITY_AURA_BREAK)) {
            movePower = movePower * 3 / 4;
        } else {
            movePower = movePower * 4 / 3;
        }
    }

    if (moveType == TYPE_FAIRY
        && BattleSystem_CountAbility(
            battleSys, battleCtx, COUNT_ALIVE_BATTLERS, 0, ABILITY_FAIRY_AURA)) {
        if (BattleSystem_CountAbility(
                battleSys,
                battleCtx,
                COUNT_ALIVE_BATTLERS,
                0,
                ABILITY_AURA_BREAK)) {
            movePower = movePower * 3 / 4;
        } else {
            movePower = movePower * 4 / 3;
        }
    }

""",
        "Transistor / Dragon's Maw / Aura power family",
    )

    return contact_replacements


def patch_victory_star(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        path,
        """    if (NO_CLOUD_NINE) {
""",
        """    {
        int victoryStars = BattleSystem_CountAbility(
            battleSys,
            battleCtx,
            COUNT_ALIVE_BATTLERS_OUR_SIDE,
            attacker,
            ABILITY_VICTORY_STAR);

        while (victoryStars-- > 0) {
            hitRate = hitRate * 110 / 100;
        }
    }

""",
        "Victory Star accuracy family",
    )


def patch_mold_breaker_ai(root: Path) -> None:
    path = root / "src/battle/trainer_ai/script.s"

    replace_once(
        path,
        """    IfLoadedEqualTo ABILITY_MOLD_BREAKER, Basic_NoImmunityAbility
""",
        """    IfLoadedEqualTo ABILITY_MOLD_BREAKER, Basic_NoImmunityAbility
    IfLoadedEqualTo ABILITY_TURBOBLAZE, Basic_NoImmunityAbility
    IfLoadedEqualTo ABILITY_TERAVOLT, Basic_NoImmunityAbility
""",
        "Trainer AI Turboblaze/Teravolt immunity handling",
    )

    replace_once(
        path,
        """    IfLoadedEqualTo ABILITY_MOLD_BREAKER, Basic_ScoreMoveEffect
""",
        """    IfLoadedEqualTo ABILITY_MOLD_BREAKER, Basic_ScoreMoveEffect
    IfLoadedEqualTo ABILITY_TURBOBLAZE, Basic_ScoreMoveEffect
    IfLoadedEqualTo ABILITY_TERAVOLT, Basic_ScoreMoveEffect
""",
        "Trainer AI Turboblaze/Teravolt move scoring",
    )


def patch_heal_bell_mold_breaker_family(root: Path) -> None:
    path = root / "src/battle/battle_io_command.c"

    replace_once(
        path,
        """        if (message->ability == ABILITY_MOLD_BREAKER) {
""",
        """        if (message->ability == ABILITY_MOLD_BREAKER
            || message->ability == ABILITY_TURBOBLAZE
            || message->ability == ABILITY_TERAVOLT) {
""",
        "Heal Bell Mold Breaker family",
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


def validate(
    root: Path,
    registry: Path,
    contact_replacements: int,
) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (
        root / "src/battle/battle_controller_player.c"
    ).read_text(encoding="utf-8")
    trainer_ai = (root / "src/battle/trainer_ai/script.s").read_text(
        encoding="utf-8"
    )
    battle_io = (root / "src/battle/battle_io_command.c").read_text(
        encoding="utf-8"
    )
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "sap_sipper_hook":
            "ABILITY_SAP_SIPPER) == TRUE" in lib
            and "MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE" in lib,
        "victory_star_hook":
            "ABILITY_VICTORY_STAR" in controller
            and "hitRate = hitRate * 110 / 100;" in controller,
        "turboblaze_hook":
            "ABILITY_TURBOBLAZE" in lib
            and "ABILITY_TURBOBLAZE, Basic_NoImmunityAbility" in trainer_ai
            and "message->ability == ABILITY_TURBOBLAZE" in battle_io,
        "teravolt_hook":
            "ABILITY_TERAVOLT" in lib
            and "ABILITY_TERAVOLT, Basic_NoImmunityAbility" in trainer_ai
            and "message->ability == ABILITY_TERAVOLT" in battle_io,
        "dark_aura_hook":
            "ABILITY_DARK_AURA" in lib
            and "moveType == TYPE_DARK" in lib,
        "fairy_aura_hook":
            "ABILITY_FAIRY_AURA" in lib
            and "moveType == TYPE_FAIRY" in lib,
        "aura_break_hook":
            lib.count("ABILITY_AURA_BREAK") >= 2
            and "movePower = movePower * 3 / 4;" in lib,
        "slush_rush_hook":
            lib.count("ABILITY_SLUSH_RUSH && WEATHER_IS_HAIL") == 2,
        "long_reach_hook":
            contact_replacements >= 5
            and "ABILITY_LONG_REACH" in lib
            and "(CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)" not in lib,
        "transistor_hook":
            "attackerParams.ability == ABILITY_TRANSISTOR" in lib
            and "movePower = movePower * 13 / 10;" in lib,
        "dragons_maw_hook":
            "attackerParams.ability == ABILITY_DRAGONS_MAW" in lib,
        "vessel_of_ruin_hook":
            "ABILITY_VESSEL_OF_RUIN" in lib
            and "spAttackStat = spAttackStat * 3 / 4;" in lib,
        "sword_of_ruin_hook":
            "ABILITY_SWORD_OF_RUIN" in lib
            and "defenseStat = defenseStat * 3 / 4;" in lib,
        "tablets_of_ruin_hook":
            "ABILITY_TABLETS_OF_RUIN" in lib
            and "attackStat = attackStat * 3 / 4;" in lib,
        "beads_of_ruin_hook":
            "ABILITY_BEADS_OF_RUIN" in lib
            and "spDefenseStat = spDefenseStat * 3 / 4;" in lib,
        "mold_breaker_family_shared":
            "Mercury_IsMoldBreakerAbility" in lib
            and "attackerAbility != ABILITY_MOLD_BREAKER" not in lib,
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
        default=Path("mr08h-canonical-ability-field-families.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    contact_replacements = patch_battle_lib(root)
    patch_victory_star(root)
    patch_mold_breaker_ai(root)
    patch_heal_bell_mold_breaker_family(root)
    update_registry(registry)

    checks = validate(root, registry, contact_replacements)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08H_CANONICAL_ABILITY_FIELD_FAMILIES",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 80,
        "long_reach_contact_sites_rewired": contact_replacements,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08H validation failed")


if __name__ == "__main__":
    main()
