#!/usr/bin/env python3
"""MR08B — fast-pass unchanged canonical Ability mechanics.

This gate ports a larger family of official Gen 5-8 Ability mechanics whose
core behavior is unchanged in the pinned Elite Redux source. hg-engine is used
as the DS-native mechanics reference; Mercury keeps the official/canonical
effect, not a Redux rebalance.

This batch deliberately targets low-risk shared hooks so many Abilities can be
certified together:
- Heavy Metal
- Light Metal
- Multiscale
- Sand Force
- Fur Coat
- Gale Wings
- Tough Claws
- Water Bubble
- Fluffy
- Neuroforce
- Ice Scales
- Power Spot

The locked MR07 Summary/Skills visuals are not touched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_HEAVY_METAL",
    "ABILITY_LIGHT_METAL",
    "ABILITY_MULTISCALE",
    "ABILITY_SAND_FORCE",
    "ABILITY_FUR_COAT",
    "ABILITY_GALE_WINGS",
    "ABILITY_TOUGH_CLAWS",
    "ABILITY_WATER_BUBBLE",
    "ABILITY_FLUFFY",
    "ABILITY_NEUROFORCE",
    "ABILITY_ICE_SCALES",
    "ABILITY_POWER_SPOT",
)

EXPECTED_IDS = {
    "ABILITY_HEAVY_METAL": 134,
    "ABILITY_LIGHT_METAL": 135,
    "ABILITY_MULTISCALE": 136,
    "ABILITY_SAND_FORCE": 159,
    "ABILITY_FUR_COAT": 169,
    "ABILITY_GALE_WINGS": 177,
    "ABILITY_TOUGH_CLAWS": 181,
    "ABILITY_WATER_BUBBLE": 199,
    "ABILITY_FLUFFY": 218,
    "ABILITY_NEUROFORCE": 233,
    "ABILITY_ICE_SCALES": 246,
    "ABILITY_POWER_SPOT": 249,
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


def patch_battle_lib(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Power Spot affects allies, never the holder's own attacks.
    insert_before_once(
        path,
        "int BattleSystem_CountAbility(BattleSystem *battleSys, BattleContext *battleCtx, enum CountAbilityMode mode, int battler, int ability)\n",
        """static BOOL Mercury_AllyHasAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int ability)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    for (i = 0; i < maxBattlers; i++) {
        if (i != battler
            && BattleSystem_GetBattlerSide(battleSys, i) == BattleSystem_GetBattlerSide(battleSys, battler)
            && battleCtx->battleMons[i].curHP
            && Battler_Ability(battleCtx, i) == ability) {
            return TRUE;
        }
    }

    return FALSE;
}

""",
        "Power Spot ally helper",
    )

    # Gale Wings: current mainline behavior is +1 priority for Flying moves
    # while the user is at full HP.
    replace_once(
        path,
        """        battler1Priority = MOVE_DATA(battler1Move).priority;
        battler2Priority = MOVE_DATA(battler2Move).priority;
""",
        """        battler1Priority = MOVE_DATA(battler1Move).priority;
        battler2Priority = MOVE_DATA(battler2Move).priority;

        if (battler1Move
            && battler1Ability == ABILITY_GALE_WINGS
            && battleCtx->battleMons[battler1].curHP == battleCtx->battleMons[battler1].maxHP
            && MOVE_DATA(battler1Move).type == TYPE_FLYING) {
            battler1Priority++;
        }

        if (battler2Move
            && battler2Ability == ABILITY_GALE_WINGS
            && battleCtx->battleMons[battler2].curHP == battleCtx->battleMons[battler2].maxHP
            && MOVE_DATA(battler2Move).type == TYPE_FLYING) {
            battler2Priority++;
        }
""",
        "Gale Wings priority",
    )

    # Base-power family: these all share the normal damage-calculation path.
    replace_once(
        path,
        """    moveClass = MOVE_DATA(move).class;

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    moveClass = MOVE_DATA(move).class;

    if (attackerParams.ability == ABILITY_SAND_FORCE
        && (fieldConditions & FIELD_CONDITION_SANDSTORM)
        && (moveType == TYPE_ROCK || moveType == TYPE_GROUND || moveType == TYPE_STEEL)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_TOUGH_CLAWS
        && (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_WATER_BUBBLE
        && moveType == TYPE_WATER) {
        movePower *= 2;
    }

    if (Mercury_AllyHasAbility(battleSys, battleCtx, attacker, ABILITY_POWER_SPOT)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        "unchanged Ability base-power family",
    )

    # Fur Coat modifies Defense itself, so it remains active through criticals
    # and stat-stage handling just like the DS donor implementation.
    replace_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MARVEL_SCALE) == TRUE
        && defenderParams.statusMask) {
        defenseStat = defenseStat * 150 / 100;
    }

    if (attackerParams.ability == ABILITY_PLUS
""",
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MARVEL_SCALE) == TRUE
        && defenderParams.statusMask) {
        defenseStat = defenseStat * 150 / 100;
    }

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FUR_COAT) == TRUE
        && moveClass == CLASS_PHYSICAL) {
        defenseStat *= 2;
    }

    if (attackerParams.ability == ABILITY_PLUS
""",
        "Fur Coat defense modifier",
    )

    # Final-damage family. Fluffy's two modifiers intentionally stack, so a
    # contact Fire move is net neutral, matching canonical behavior.
    replace_once(
        path,
        """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
""",
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MULTISCALE) == TRUE
        && defenderParams.curHP == defenderParams.maxHP) {
        damage /= 2;
    }

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FLUFFY) == TRUE) {
        if (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT) {
            damage /= 2;
        }
        if (moveType == TYPE_FIRE) {
            damage *= 2;
        }
    }

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_ICE_SCALES) == TRUE
        && moveClass == CLASS_SPECIAL) {
        damage /= 2;
    }

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WATER_BUBBLE) == TRUE
        && moveType == TYPE_FIRE) {
        damage /= 2;
    }

    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
""",
        "unchanged Ability final-damage family",
    )

    # Neuroforce applies only after type effectiveness has been established.
    replace_once(
        path,
        """        if ((*moveStatusMask & MOVE_STATUS_SUPER_EFFECTIVE) && movePower) {
            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
""",
        """        if ((*moveStatusMask & MOVE_STATUS_SUPER_EFFECTIVE) && movePower) {
            if (Battler_Ability(battleCtx, attacker) == ABILITY_NEUROFORCE) {
                damage = damage * 125 / 100;
            }

            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
""",
        "Neuroforce super-effective modifier",
    )


def patch_battle_script(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    # Heavy/Light Metal affect the target's effective weight and can be ignored
    # by Mold Breaker for weight-based attacks.
    replace_once(
        path,
        """    int i = 0;
    int monWeight = DEFENDING_MON.weight;

    for (; sWeightToPower[i][0] != 0xFFFF; i++) {
""",
        """    int i = 0;
    int monWeight = DEFENDING_MON.weight;

    if (Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battleCtx->defender,
            ABILITY_HEAVY_METAL) == TRUE) {
        monWeight *= 2;
    } else if (Battler_IgnorableAbility(
                   battleCtx,
                   battleCtx->attacker,
                   battleCtx->defender,
                   ABILITY_LIGHT_METAL) == TRUE) {
        monWeight /= 2;
        if (monWeight < 1) {
            monWeight = 1;
        }
    }

    for (; sWeightToPower[i][0] != 0xFFFF; i++) {
""",
        "Heavy Metal / Light Metal effective weight",
    )

    # Sand Force holders are immune to sandstorm chip damage.
    replace_once(
        path,
        """            && battleCtx->battleMons[battler].curHP
            && Battler_Ability(battleCtx, battler) != ABILITY_SAND_VEIL
            && (battleCtx->battleMons[battler].moveEffectsMask & MOVE_EFFECT_NO_WEATHER_DAMAGE) == FALSE) {
""",
        """            && battleCtx->battleMons[battler].curHP
            && Battler_Ability(battleCtx, battler) != ABILITY_SAND_VEIL
            && Battler_Ability(battleCtx, battler) != ABILITY_SAND_FORCE
            && (battleCtx->battleMons[battler].moveEffectsMask & MOVE_EFFECT_NO_WEATHER_DAMAGE) == FALSE) {
""",
        "Sand Force sandstorm immunity",
    )


def patch_water_bubble_burn_immunity(root: Path) -> None:
    path = root / "res/battle/scripts/subscripts/subscript_burn.s"

    replace_once(
        path,
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _211
    CheckIgnoreWeather _021
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _211
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _211
    CheckIgnoreWeather _021
""",
        "Water Bubble held-item/self burn immunity",
    )

    replace_once(
        path,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _264
    CheckIgnoreWeather _069
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _264
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _264
    CheckIgnoreWeather _069
""",
        "Water Bubble opposing-source burn immunity",
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
    battle_lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    battle_script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    burn_script = (
        root / "res/battle/scripts/subscripts/subscript_burn.s"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "heavy_metal_hook": "ABILITY_HEAVY_METAL) == TRUE" in battle_script,
        "light_metal_hook": "ABILITY_LIGHT_METAL) == TRUE" in battle_script,
        "multiscale_hook": "ABILITY_MULTISCALE) == TRUE" in battle_lib,
        "sand_force_power_hook":
            "attackerParams.ability == ABILITY_SAND_FORCE" in battle_lib,
        "sand_force_weather_immunity":
            "Battler_Ability(battleCtx, battler) != ABILITY_SAND_FORCE"
            in battle_script,
        "fur_coat_hook": "ABILITY_FUR_COAT) == TRUE" in battle_lib,
        "gale_wings_hook": battle_lib.count("ABILITY_GALE_WINGS") >= 2,
        "tough_claws_hook":
            "attackerParams.ability == ABILITY_TOUGH_CLAWS" in battle_lib,
        "water_bubble_power_hook":
            "attackerParams.ability == ABILITY_WATER_BUBBLE" in battle_lib,
        "water_bubble_fire_hook":
            "ABILITY_WATER_BUBBLE) == TRUE" in battle_lib,
        "water_bubble_burn_hook":
            burn_script.count("ABILITY_WATER_BUBBLE") == 2,
        "fluffy_hook": "ABILITY_FLUFFY) == TRUE" in battle_lib,
        "neuroforce_hook":
            "Battler_Ability(battleCtx, attacker) == ABILITY_NEUROFORCE"
            in battle_lib,
        "ice_scales_hook": "ABILITY_ICE_SCALES) == TRUE" in battle_lib,
        "power_spot_hook":
            "Mercury_AllyHasAbility(battleSys, battleCtx, attacker, ABILITY_POWER_SPOT)"
            in battle_lib,
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--implemented-registry",
        type=Path,
        required=True,
        help="Registry generated by install_mp05_ability_namespace.py",
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr08b-unchanged-ability-fastpass.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_battle_lib(root)
    patch_battle_script(root)
    patch_water_bubble_burn_immunity(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08B_UNCHANGED_CANONICAL_ABILITY_FASTPASS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "policy": "Official/canonical mechanics only; unchanged in pinned Elite Redux source.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "elite_redux_reference": "Elite-Redux/eliteredux pinned by upstream/LOCK.json",
        "checks": checks,
    }

    args.report.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08B validation failed")


if __name__ == "__main__":
    main()
