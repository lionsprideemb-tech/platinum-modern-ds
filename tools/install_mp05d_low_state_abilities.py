#!/usr/bin/env python3
"""Port a second exact, low-state modern ability family into Platinum.

MP05D extends the successful MP05C scalar pass with abilities that can be
implemented entirely through existing Platinum speed, move-flag, critical-hit,
and final-damage hooks. No new persistent battle state, switching framework,
terrain system, or form engine is introduced.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITIES = [
    "ABILITY_SAND_RUSH",
    "ABILITY_TOUGH_CLAWS",
    "ABILITY_MERCILESS",
    "ABILITY_SLUSH_RUSH",
    "ABILITY_FLUFFY",
    "ABILITY_ICE_SCALES",
]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one {label} anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def load_registry(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--implemented-registry",
        type=Path,
        required=True,
        help="Implemented-ability registry after MP05C.",
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mp05d-low-state-abilities.json"),
    )
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    battle_lib = pt / "src/battle/battle_lib.c"

    canonical = load_registry(pt / "generated/abilities.txt")
    implemented = load_registry(args.implemented_registry)

    if len(canonical) != 311:
        raise SystemExit(
            f"expected canonical ability namespace 0..310, got {len(canonical)} entries"
        )
    if canonical[310] != "ABILITY_POISON_PUPPETEER":
        raise SystemExit(f"unexpected canonical ability tail: {canonical[310]}")
    if len(implemented) != 131:
        raise SystemExit(
            f"MP05D must start from MP05C's 131 implemented abilities, got {len(implemented)}"
        )

    missing = [ability for ability in ABILITIES if ability not in canonical]
    if missing:
        raise SystemExit(f"canonical registry is missing MP05D abilities: {missing}")
    already = [ability for ability in ABILITIES if ability in implemented]
    if already:
        raise SystemExit(f"MP05D abilities unexpectedly already implemented: {already}")

    # Sand Rush and Slush Rush reuse Platinum's existing weather-speed hook.
    speed_anchor = """        if ((battler1Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler1Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)) {
            battler1Speed *= 2;
        }

        if ((battler2Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler2Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)) {
            battler2Speed *= 2;
        }
"""
    speed_replacement = """        if ((battler1Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler1Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler1Ability == ABILITY_SAND_RUSH && WEATHER_IS_SANDSTORM)
            || (battler1Ability == ABILITY_SLUSH_RUSH && WEATHER_IS_HAIL)) {
            battler1Speed *= 2;
        }

        if ((battler2Ability == ABILITY_SWIFT_SWIM && WEATHER_IS_RAIN)
            || (battler2Ability == ABILITY_CHLOROPHYLL && WEATHER_IS_SUN)
            || (battler2Ability == ABILITY_SAND_RUSH && WEATHER_IS_SANDSTORM)
            || (battler2Ability == ABILITY_SLUSH_RUSH && WEATHER_IS_HAIL)) {
            battler2Speed *= 2;
        }
"""
    replace_once(battle_lib, speed_anchor, speed_replacement, "weather speed family")

    # Tough Claws is a base-power modifier for contact moves.
    claws_anchor = """    for (i = 0; i < NELEMS(sPunchingMoves); i++) {
        if (sPunchingMoves[i] == move && attackerParams.ability == ABILITY_IRON_FIST) {
            movePower = movePower * 12 / 10;
            break;
        }
    }
"""
    claws_replacement = """    if (attackerParams.ability == ABILITY_TOUGH_CLAWS
        && (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT)) {
        movePower = movePower * 13 / 10;
    }

    for (i = 0; i < NELEMS(sPunchingMoves); i++) {
        if (sPunchingMoves[i] == move && attackerParams.ability == ABILITY_IRON_FIST) {
            movePower = movePower * 12 / 10;
            break;
        }
    }
"""
    replace_once(battle_lib, claws_anchor, claws_replacement, "Tough Claws contact modifier")

    # Merciless guarantees a critical hit against poisoned targets while still
    # respecting Battle Armor/Shell Armor, Lucky Chant, and no-critical effects.
    crit_anchor = """    if (BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_BATTLE_ARMOR) == FALSE
"""
    crit_replacement = """    if (((attackerAbility == ABILITY_MERCILESS
                && (battleCtx->battleMons[defender].status & MON_CONDITION_ANY_POISON))
            || BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0)
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_BATTLE_ARMOR) == FALSE
"""
    replace_once(battle_lib, crit_anchor, crit_replacement, "Merciless critical-hit hook")

    # Ice Scales and Fluffy are final-damage modifiers. Converting the original
    # return into an explicit +2 then modifier sequence leaves every unaffected
    # move bit-for-bit equivalent to Platinum.
    damage_anchor = """    if (BattleMon_Get(battleCtx, attacker, BATTLEMON_FLASH_FIRE, NULL) && moveType == TYPE_FIRE) {
        damage = damage * 15 / 10;
    }

    return damage + 2;
}
"""
    damage_replacement = """    if (BattleMon_Get(battleCtx, attacker, BATTLEMON_FLASH_FIRE, NULL) && moveType == TYPE_FIRE) {
        damage = damage * 15 / 10;
    }

    damage += 2;

    if (moveClass == CLASS_SPECIAL
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_ICE_SCALES) == TRUE) {
        damage /= 2;
    }

    // Fluffy halves contact damage and doubles Fire damage. A contact Fire move
    // receives both modifiers, which cancel to 1x.
    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FLUFFY) == TRUE) {
        if ((MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT) && moveType != TYPE_FIRE) {
            damage /= 2;
        } else if ((MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT) == 0 && moveType == TYPE_FIRE) {
            damage *= 2;
        }
    }

    return damage;
}
"""
    replace_once(battle_lib, damage_anchor, damage_replacement, "final damage modifier family")

    live = set(implemented)
    live.update(ABILITIES)
    extended = [token for token in canonical if token in live]
    if len(extended) != len(implemented) + len(ABILITIES):
        raise SystemExit("implemented registry extension count mismatch")
    args.implemented_registry.write_text(
        "\n".join(extended) + "\n",
        encoding="utf-8",
    )

    report = {
        "gate": "MP05D_LOW_STATE_MODERN_ABILITIES",
        "abilities_added": ABILITIES,
        "abilities_added_count": len(ABILITIES),
        "implemented_ability_count": len(extended),
        "mechanics": {
            "ABILITY_SAND_RUSH": "2x Speed in sand while weather is active",
            "ABILITY_SLUSH_RUSH": "2x Speed in hail while weather is active",
            "ABILITY_TOUGH_CLAWS": "1.3x base power for contact moves",
            "ABILITY_MERCILESS": "guaranteed critical hit against poisoned targets, subject to anti-critical protections",
            "ABILITY_FLUFFY": "0.5x contact damage and 2x Fire damage; contact Fire cancels to 1x",
            "ABILITY_ICE_SCALES": "0.5x final damage from special-category moves",
        },
        "new_persistent_battle_state": False,
        "new_switching_logic": False,
        "new_terrain_state": False,
        "approximate_mechanics": False,
        "result": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
