#!/usr/bin/env python3
"""MR08D — unchanged canonical Ability fast pass, shared battle hooks.

Adds ten more official/mainline Ability mechanics that match the pinned
Elite Redux behavior and can share existing Platinum battle hooks:

- Iron Barbs
- Wonder Skin
- Analytic
- Bulletproof
- Queenly Majesty
- Battery
- Dazzling
- Tangling Hair
- Shadow Shield
- Prism Armor

hg-engine remains the DS-native implementation reference. This pass changes
battle mechanics only and leaves the locked MR07 Summary/editor visuals alone.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_IRON_BARBS",
    "ABILITY_WONDER_SKIN",
    "ABILITY_ANALYTIC",
    "ABILITY_BULLETPROOF",
    "ABILITY_QUEENLY_MAJESTY",
    "ABILITY_BATTERY",
    "ABILITY_DAZZLING",
    "ABILITY_TANGLING_HAIR",
    "ABILITY_SHADOW_SHIELD",
    "ABILITY_PRISM_ARMOR",
)

EXPECTED_IDS = {
    "ABILITY_WONDER_SKIN": 147,
    "ABILITY_ANALYTIC": 148,
    "ABILITY_IRON_BARBS": 160,
    "ABILITY_BULLETPROOF": 171,
    "ABILITY_QUEENLY_MAJESTY": 214,
    "ABILITY_BATTERY": 217,
    "ABILITY_DAZZLING": 219,
    "ABILITY_TANGLING_HAIR": 221,
    "ABILITY_SHADOW_SHIELD": 231,
    "ABILITY_PRISM_ARMOR": 232,
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

    # Bulletproof's canonical projectile list, mirrored from the pinned
    # hg-engine BallAndBombMoveList. Modern move constants are installed later
    # in the same Mercury integration workflow before compilation.
    insert_before_once(
        path,
        """int BattleSystem_TriggerImmunityAbility(BattleContext *battleCtx, int attacker, int defender)
""",
        """static BOOL Mercury_MoveIsBallOrBomb(int move)
{
    switch (move) {
    case MOVE_ACID_SPRAY:
    case MOVE_AURA_SPHERE:
    case MOVE_BARRAGE:
    case MOVE_BEAK_BLAST:
    case MOVE_BULLET_SEED:
    case MOVE_EGG_BOMB:
    case MOVE_ELECTRO_BALL:
    case MOVE_ENERGY_BALL:
    case MOVE_FOCUS_BLAST:
    case MOVE_GYRO_BALL:
    case MOVE_ICE_BALL:
    case MOVE_MAGNET_BOMB:
    case MOVE_MIST_BALL:
    case MOVE_MUD_BOMB:
    case MOVE_OCTAZOOKA:
    case MOVE_POLLEN_PUFF:
    case MOVE_PYRO_BALL:
    case MOVE_ROCK_BLAST:
    case MOVE_ROCK_WRECKER:
    case MOVE_SEARING_SHOT:
    case MOVE_SEED_BOMB:
    case MOVE_SHADOW_BALL:
    case MOVE_SLUDGE_BOMB:
    case MOVE_SYRUP_BOMB:
    case MOVE_WEATHER_BALL:
    case MOVE_ZAP_CANNON:
        return TRUE;
    }

    return FALSE;
}

static int Mercury_CurrentMovePriority(BattleContext *battleCtx, int attacker)
{
    int priority = CURRENT_MOVE_DATA.priority;
    int moveType;

    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (battleCtx->moveType) {
        moveType = battleCtx->moveType;
    } else {
        moveType = CURRENT_MOVE_DATA.type;
    }

    if (Battler_Ability(battleCtx, attacker) == ABILITY_PRANKSTER
        && CURRENT_MOVE_DATA.class == CLASS_STATUS) {
        priority++;
    }

    if (Battler_Ability(battleCtx, attacker) == ABILITY_GALE_WINGS
        && battleCtx->battleMons[attacker].curHP
            == battleCtx->battleMons[attacker].maxHP
        && moveType == TYPE_FLYING) {
        priority++;
    }

    return priority;
}

static BOOL Mercury_PriorityBlockerActive(
    BattleContext *battleCtx,
    int attacker,
    int defender)
{
    int partner = defender ^ 2;

    if ((attacker & 1) == (defender & 1)
        || Mercury_CurrentMovePriority(battleCtx, attacker) <= 0) {
        return FALSE;
    }

    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_QUEENLY_MAJESTY)
        || Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_DAZZLING)) {
        return TRUE;
    }

    if (battleCtx->battleMons[partner].curHP
        && (Battler_IgnorableAbility(
                battleCtx, attacker, partner, ABILITY_QUEENLY_MAJESTY)
            || Battler_IgnorableAbility(
                battleCtx, attacker, partner, ABILITY_DAZZLING))) {
        return TRUE;
    }

    return FALSE;
}

""",
        "Bulletproof / priority-blocker helpers",
    )

    # Bulletproof and Queenly Majesty / Dazzling terminate the move in the
    # same pre-damage immunity lane used by Volt Absorb and Soundproof.
    replace_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_VOLT_ABSORB) == TRUE
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_BULLETPROOF) == TRUE
        && Mercury_MoveIsBallOrBomb(battleCtx->moveCur)) {
        return subscript_but_it_failed;
    }

    if (Mercury_PriorityBlockerActive(battleCtx, attacker, defender)) {
        return subscript_but_it_failed;
    }

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_VOLT_ABSORB) == TRUE
""",
        "Bulletproof / Queenly Majesty / Dazzling immunity hooks",
    )

    # Iron Barbs is canonically the same contact recoil as Rough Skin.
    replace_once(
        path,
        """    case ABILITY_ROUGH_SKIN:
        if (ATTACKING_MON.curHP
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_MAGIC_GUARD
""",
        """    case ABILITY_ROUGH_SKIN:
    case ABILITY_IRON_BARBS:
        if (ATTACKING_MON.curHP
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_MAGIC_GUARD
""",
        "Iron Barbs Rough Skin family",
    )

    # Tangling Hair is the canonical Gooey contact-Speed-drop mechanic.
    replace_once(
        path,
        """    case ABILITY_GOOEY:
        if (ATTACKING_MON.curHP
""",
        """    case ABILITY_GOOEY:
    case ABILITY_TANGLING_HAIR:
        if (ATTACKING_MON.curHP
""",
        "Tangling Hair Gooey family",
    )

    # Analytic and Battery share Platinum's existing move-power path.
    replace_once(
        path,
        """    if (Mercury_AllyHasAbility(battleSys, battleCtx, attacker, ABILITY_POWER_SPOT)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    if (Mercury_AllyHasAbility(battleSys, battleCtx, attacker, ABILITY_POWER_SPOT)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_ANALYTIC
        && Battler_MovedThisTurn(battleCtx, defender)
        && MOVE_DATA(move).effect != BATTLE_EFFECT_HIT_IN_3_TURNS) {
        movePower = movePower * 13 / 10;
    }

    if (moveClass == CLASS_SPECIAL
        && Mercury_AllyHasAbility(battleSys, battleCtx, attacker, ABILITY_BATTERY)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        "Analytic / Battery power hooks",
    )

    # Shadow Shield is the unignorable Multiscale family member.
    replace_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MULTISCALE) == TRUE
        && defenderParams.curHP == defenderParams.maxHP) {
        damage /= 2;
    }
""",
        """    if ((Battler_IgnorableAbility(
             battleCtx, attacker, defender, ABILITY_MULTISCALE) == TRUE
            || Battler_Ability(battleCtx, defender) == ABILITY_SHADOW_SHIELD)
        && defenderParams.curHP == defenderParams.maxHP) {
        damage /= 2;
    }
""",
        "Shadow Shield Multiscale family",
    )

    # Prism Armor is the unignorable Filter/Solid Rock family member.
    replace_once(
        path,
        """            if (Battler_Ability(battleCtx, attacker) == ABILITY_NEUROFORCE) {
                damage = damage * 125 / 100;
            }

            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
""",
        """            if (Battler_Ability(battleCtx, attacker) == ABILITY_NEUROFORCE) {
                damage = damage * 125 / 100;
            }

            if (Battler_Ability(battleCtx, defender) == ABILITY_PRISM_ARMOR) {
                damage = BattleSystem_Divide(damage * 3, 4);
            }

            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
""",
        "Prism Armor super-effective reduction",
    )


def patch_wonder_skin(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    # Wonder Skin sets opposing status-move base accuracy to at most 50 before
    # the normal accuracy/evasion stages and other accuracy modifiers apply.
    replace_once(
        path,
        """    u16 hitRate = MOVE_DATA(move).accuracy;
    if (hitRate == 0) {
        return 0;
    }

    // Charge-up moves don't consider accuracy on their first turn
""",
        """    u16 hitRate = MOVE_DATA(move).accuracy;
    if (hitRate == 0) {
        return 0;
    }

    if ((attacker & 1) != (defender & 1)
        && moveClass == CLASS_STATUS
        && hitRate > 50
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_WONDER_SKIN) == TRUE) {
        hitRate = 50;
    }

    // Charge-up moves don't consider accuracy on their first turn
""",
        "Wonder Skin accuracy hook",
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
    controller = (
        root / "src/battle/battle_controller_player.c"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "iron_barbs_hook":
            "case ABILITY_IRON_BARBS:" in battle_lib,
        "wonder_skin_hook":
            "ABILITY_WONDER_SKIN) == TRUE" in controller
            and "hitRate = 50;" in controller,
        "analytic_hook":
            "attackerParams.ability == ABILITY_ANALYTIC" in battle_lib
            and "Battler_MovedThisTurn(battleCtx, defender)" in battle_lib,
        "bulletproof_hook":
            "Mercury_MoveIsBallOrBomb" in battle_lib
            and "ABILITY_BULLETPROOF) == TRUE" in battle_lib
            and "MOVE_SYRUP_BOMB" in battle_lib,
        "queenly_majesty_hook":
            battle_lib.count("ABILITY_QUEENLY_MAJESTY") >= 2,
        "battery_hook":
            "ABILITY_BATTERY" in battle_lib
            and "moveClass == CLASS_SPECIAL" in battle_lib,
        "dazzling_hook":
            battle_lib.count("ABILITY_DAZZLING") >= 2,
        "tangling_hair_hook":
            "case ABILITY_TANGLING_HAIR:" in battle_lib,
        "shadow_shield_hook":
            "Battler_Ability(battleCtx, defender) == ABILITY_SHADOW_SHIELD"
            in battle_lib,
        "prism_armor_hook":
            "Battler_Ability(battleCtx, defender) == ABILITY_PRISM_ARMOR"
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
        default=Path("mr08d-unchanged-ability-shared-hooks.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_battle_lib(root)
    patch_wonder_skin(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08D_UNCHANGED_ABILITY_SHARED_HOOKS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 35,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "elite_redux_reference": "Elite-Redux/eliteredux pinned by upstream/LOCK.json",
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08D validation failed")


if __name__ == "__main__":
    main()
