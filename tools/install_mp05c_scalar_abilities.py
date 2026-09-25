#!/usr/bin/env python3
"""Port the first exact modern ability family into Platinum.

MP05C intentionally starts with stateless scalar abilities that fit existing
Platinum damage-calculation hooks.  No new battle state, switching logic,
terrain, form logic, or approximation is introduced here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITIES = [
    "ABILITY_TOXIC_BOOST",
    "ABILITY_FLARE_BOOST",
    "ABILITY_FUR_COAT",
    "ABILITY_STEELWORKER",
    "ABILITY_TRANSISTOR",
    "ABILITY_DRAGONS_MAW",
    "ABILITY_ROCKY_PAYLOAD",
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
        help="MP05 implemented-ability registry to extend after mechanics are installed.",
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mp05c-scalar-abilities.json"),
    )
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    battle_lib = pt / "src/battle/battle_lib.c"

    canonical = load_registry(pt / "generated/abilities.txt")
    implemented = load_registry(args.implemented_registry)

    if len(canonical) != 311:
        raise SystemExit(f"expected canonical ability namespace 0..310, got {len(canonical)} entries")
    if canonical[310] != "ABILITY_POISON_PUPPETEER":
        raise SystemExit(f"unexpected canonical ability tail: {canonical[310]}")
    if len(implemented) != 124 or implemented[-1] != "ABILITY_BAD_DREAMS":
        raise SystemExit("MP05C must start from the native implemented registry 0..123")

    missing = [ability for ability in ABILITIES if ability not in canonical]
    if missing:
        raise SystemExit(f"canonical registry is missing MP05C abilities: {missing}")

    anchor = """    moveClass = MOVE_DATA(move).class;

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
"""
    replacement = """    moveClass = MOVE_DATA(move).class;

    // MP05C: exact stateless modern ability family. These modifiers use the
    // same existing offensive/defensive stat path as Platinum's Guts,
    // Marvel Scale, Huge Power, and item modifiers.
    if (attackerParams.ability == ABILITY_TOXIC_BOOST
        && moveClass == CLASS_PHYSICAL
        && (attackerParams.statusMask & MON_CONDITION_ANY_POISON)) {
        attackStat = attackStat * 150 / 100;
    }

    if (attackerParams.ability == ABILITY_FLARE_BOOST
        && moveClass == CLASS_SPECIAL
        && (attackerParams.statusMask & MON_CONDITION_BURN)) {
        spAttackStat = spAttackStat * 150 / 100;
    }

    if (attackerParams.ability == ABILITY_STEELWORKER && moveType == TYPE_STEEL) {
        if (moveClass == CLASS_PHYSICAL) {
            attackStat = attackStat * 150 / 100;
        } else if (moveClass == CLASS_SPECIAL) {
            spAttackStat = spAttackStat * 150 / 100;
        }
    }

    if (attackerParams.ability == ABILITY_DRAGONS_MAW && moveType == TYPE_DRAGON) {
        if (moveClass == CLASS_PHYSICAL) {
            attackStat = attackStat * 150 / 100;
        } else if (moveClass == CLASS_SPECIAL) {
            spAttackStat = spAttackStat * 150 / 100;
        }
    }

    // Transistor uses its current Gen IX 1.3x modifier.
    if (attackerParams.ability == ABILITY_TRANSISTOR && moveType == TYPE_ELECTRIC) {
        if (moveClass == CLASS_PHYSICAL) {
            attackStat = attackStat * 130 / 100;
        } else if (moveClass == CLASS_SPECIAL) {
            spAttackStat = spAttackStat * 130 / 100;
        }
    }

    if (attackerParams.ability == ABILITY_ROCKY_PAYLOAD && moveType == TYPE_ROCK) {
        if (moveClass == CLASS_PHYSICAL) {
            attackStat = attackStat * 150 / 100;
        } else if (moveClass == CLASS_SPECIAL) {
            spAttackStat = spAttackStat * 150 / 100;
        }
    }

    if (moveClass == CLASS_PHYSICAL
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FUR_COAT) == TRUE) {
        defenseStat *= 2;
    }

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
"""
    replace_once(battle_lib, anchor, replacement, "damage scalar family")

    # Extend the live-ability registry only after all exact mechanics above
    # have been installed. Preserve canonical numeric order for deterministic
    # species imports and reports.
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
        "gate": "MP05C_STATELESS_SCALAR_ABILITIES",
        "abilities_added": ABILITIES,
        "abilities_added_count": len(ABILITIES),
        "implemented_ability_count": len(extended),
        "mechanics": {
            "ABILITY_TOXIC_BOOST": "1.5x physical Attack while poisoned or badly poisoned",
            "ABILITY_FLARE_BOOST": "1.5x Special Attack while burned",
            "ABILITY_FUR_COAT": "2x Defense against physical damage; Mold Breaker-ignorable",
            "ABILITY_STEELWORKER": "1.5x offensive stat for Steel-type attacks",
            "ABILITY_DRAGONS_MAW": "1.5x offensive stat for Dragon-type attacks",
            "ABILITY_TRANSISTOR": "1.3x offensive stat for Electric-type attacks (current Gen IX)",
            "ABILITY_ROCKY_PAYLOAD": "1.5x offensive stat for Rock-type attacks",
        },
        "new_battle_state": False,
        "new_switching_logic": False,
        "new_field_or_terrain_state": False,
        "approximate_mechanics": False,
        "result": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
