#!/usr/bin/env python3
"""MR08D — unchanged canonical Ability fast pass, reaction/power family.

Adds another large batch of official/current-mainline Ability mechanics while
preserving the locked MR07 Summary/Skills visuals.

Implemented:
- Analytic
- Bulletproof
- Stamina
- Water Compaction
- Steelworker
- Queenly Majesty
- Dazzling
- Tangling Hair
- Shadow Shield
- Prism Armor
- Perish Body

The mechanics are ported into Platinum-native shared battle hooks with the
pinned hg-engine implementation used as the DS reference.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_ANALYTIC",
    "ABILITY_BULLETPROOF",
    "ABILITY_STAMINA",
    "ABILITY_WATER_COMPACTION",
    "ABILITY_STEELWORKER",
    "ABILITY_QUEENLY_MAJESTY",
    "ABILITY_DAZZLING",
    "ABILITY_TANGLING_HAIR",
    "ABILITY_SHADOW_SHIELD",
    "ABILITY_PRISM_ARMOR",
    "ABILITY_PERISH_BODY",
)

EXPECTED_IDS = {
    "ABILITY_ANALYTIC": 148,
    "ABILITY_BULLETPROOF": 171,
    "ABILITY_STAMINA": 192,
    "ABILITY_WATER_COMPACTION": 195,
    "ABILITY_STEELWORKER": 200,
    "ABILITY_QUEENLY_MAJESTY": 214,
    "ABILITY_DAZZLING": 219,
    "ABILITY_TANGLING_HAIR": 221,
    "ABILITY_SHADOW_SHIELD": 231,
    "ABILITY_PRISM_ARMOR": 232,
    "ABILITY_PERISH_BODY": 253,
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


def patch_power_and_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Analytic: 1.3x if the user is the final battler with an unfinished action.
    # waitingBattlers is recomputed by the Platinum action dispatcher before
    # each action and therefore naturally includes switches and other actions.
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    if (attackerParams.ability == ABILITY_ANALYTIC
        && battleCtx->waitingBattlers == 1
        && MOVE_DATA(move).effect != BATTLE_EFFECT_HIT_IN_3_TURNS) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_STEELWORKER
        && moveType == TYPE_STEEL) {
        movePower = movePower * 15 / 10;
    }

""",
        "Analytic / Steelworker power modifiers",
    )

    # Shadow Shield is Multiscale's unignorable counterpart.
    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_MULTISCALE) == TRUE
""",
        """    if (Battler_Ability(battleCtx, defender) == ABILITY_SHADOW_SHIELD
        && defenderParams.curHP == defenderParams.maxHP) {
        damage /= 2;
    }

""",
        "Shadow Shield final damage",
    )

    # Prism Armor is the unignorable counterpart to Filter / Solid Rock.
    replace_once(
        path,
        """        if ((*moveStatusMask & MOVE_STATUS_SUPER_EFFECTIVE) && movePower) {
            if (Battler_Ability(battleCtx, attacker) == ABILITY_NEUROFORCE) {
                damage = damage * 125 / 100;
            }

            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOLID_ROCK) == TRUE) {
                damage = BattleSystem_Divide(damage * 3, 4);
            }
""",
        """        if ((*moveStatusMask & MOVE_STATUS_SUPER_EFFECTIVE) && movePower) {
            if (Battler_Ability(battleCtx, attacker) == ABILITY_NEUROFORCE) {
                damage = damage * 125 / 100;
            }

            if (Battler_Ability(battleCtx, defender) == ABILITY_PRISM_ARMOR) {
                damage = BattleSystem_Divide(damage * 3, 4);
            } else if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOLID_ROCK) == TRUE) {
                damage = BattleSystem_Divide(damage * 3, 4);
            }
""",
        "Prism Armor super-effective reduction",
    )


def patch_immunities(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """int BattleSystem_TriggerImmunityAbility(BattleContext *battleCtx, int attacker, int defender)
""",
        """static BOOL Mercury_IsBallOrBombMove(int move)
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
    default:
        return FALSE;
    }
}

static int Mercury_EffectiveMovePriority(BattleContext *battleCtx, int attacker)
{
    int priority = CURRENT_MOVE_DATA.priority;
    int ability = Battler_Ability(battleCtx, attacker);

    if (ability == ABILITY_PRANKSTER && CURRENT_MOVE_DATA.class == CLASS_STATUS) {
        priority++;
    }

    if (ability == ABILITY_GALE_WINGS
        && battleCtx->battleMons[attacker].curHP == battleCtx->battleMons[attacker].maxHP
        && CURRENT_MOVE_DATA.type == TYPE_FLYING) {
        priority++;
    }

    return priority;
}

""",
        "Bulletproof / priority-block helpers",
    )

    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_VOLT_ABSORB) == TRUE
""",
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_BULLETPROOF) == TRUE
        && Mercury_IsBallOrBombMove(battleCtx->moveCur)) {
        return subscript_blocked_by_soundproof;
    }

    if (attacker != defender
        && BattleSystem_GetBattlerSide(NULL, attacker) != BattleSystem_GetBattlerSide(NULL, defender)) {
        // placeholder: side check replaced below by parity-safe DS battler layout
    }

    if (attacker != defender
        && ((attacker & 1) != (defender & 1))
        && Battler_Ability(battleCtx, attacker) != ABILITY_MOLD_BREAKER
        && Mercury_EffectiveMovePriority(battleCtx, attacker) > 0
        && (Battler_Ability(battleCtx, defender) == ABILITY_QUEENLY_MAJESTY
            || Battler_Ability(battleCtx, defender) == ABILITY_DAZZLING
            || Mercury_AllyHasAbility(NULL, battleCtx, defender, ABILITY_QUEENLY_MAJESTY)
            || Mercury_AllyHasAbility(NULL, battleCtx, defender, ABILITY_DAZZLING))) {
        return subscript_blocked_by_soundproof;
    }

""",
        "Bulletproof / Queenly Majesty / Dazzling immunity hooks",
    )

    # BattleSystem_TriggerImmunityAbility historically lacks BattleSystem*.
    # Replace the two helper calls above with parity-based ally lookup that
    # remains valid for Platinum's fixed 0/2 and 1/3 side layout.
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        """    if (attacker != defender
        && BattleSystem_GetBattlerSide(NULL, attacker) != BattleSystem_GetBattlerSide(NULL, defender)) {
        // placeholder: side check replaced below by parity-safe DS battler layout
    }

""",
        "",
    )
    text = text.replace(
        """            || Mercury_AllyHasAbility(NULL, battleCtx, defender, ABILITY_QUEENLY_MAJESTY)
            || Mercury_AllyHasAbility(NULL, battleCtx, defender, ABILITY_DAZZLING))) {
""",
        """            || ((defender ^ 2) < MAX_BATTLERS
                && battleCtx->battleMons[defender ^ 2].curHP
                && (Battler_Ability(battleCtx, defender ^ 2) == ABILITY_QUEENLY_MAJESTY
                    || Battler_Ability(battleCtx, defender ^ 2) == ABILITY_DAZZLING)))) {
""",
    )
    path.write_text(text, encoding="utf-8")


def patch_on_hit(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Tangling Hair is mechanically identical to Gooey.
    replace_once(
        path,
        """    case ABILITY_GOOEY:
        if (ATTACKING_MON.curHP
""",
        """    case ABILITY_GOOEY:
    case ABILITY_TANGLING_HAIR:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                Battler_Ability(battleCtx, battleCtx->defender)) == TRUE
            && ATTACKING_MON.curHP
""",
        "Tangling Hair / Gooey shared hook",
    )

    insert_before_once(
        path,
        """    case ABILITY_BERSERK: {
""",
        """    case ABILITY_STAMINA:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_STAMINA) == TRUE
            && DEFENDING_MON.curHP
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

        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_WATER_COMPACTION) == TRUE
            && DEFENDING_MON.curHP
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

    case ABILITY_PERISH_BODY:
        if ((DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)
            && (((ATTACKING_MON.moveEffectsMask & MOVE_EFFECT_PERISH_SONG) == FALSE)
                || ((DEFENDING_MON.moveEffectsMask & MOVE_EFFECT_PERISH_SONG) == FALSE))) {
            if ((ATTACKING_MON.moveEffectsMask & MOVE_EFFECT_PERISH_SONG) == FALSE) {
                ATTACKING_MON.moveEffectsMask |= MOVE_EFFECT_PERISH_SONG;
                ATTACKING_MON.moveEffectsData.perishSongTurns = 3;
            }

            if ((DEFENDING_MON.moveEffectsMask & MOVE_EFFECT_PERISH_SONG) == FALSE) {
                DEFENDING_MON.moveEffectsMask |= MOVE_EFFECT_PERISH_SONG;
                DEFENDING_MON.moveEffectsData.perishSongTurns = 3;
            }

            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

""",
        "Stamina / Water Compaction / Perish Body on-hit hooks",
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
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "analytic_hook":
            "ABILITY_ANALYTIC" in battle_lib
            and "battleCtx->waitingBattlers == 1" in battle_lib,
        "bulletproof_hook":
            "Mercury_IsBallOrBombMove" in battle_lib
            and "ABILITY_BULLETPROOF" in battle_lib,
        "stamina_hook":
            "case ABILITY_STAMINA:" in battle_lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in battle_lib,
        "water_compaction_hook":
            "case ABILITY_WATER_COMPACTION:" in battle_lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_2_STAGES" in battle_lib,
        "steelworker_hook":
            "attackerParams.ability == ABILITY_STEELWORKER" in battle_lib,
        "priority_block_hook":
            "Mercury_EffectiveMovePriority" in battle_lib
            and "ABILITY_QUEENLY_MAJESTY" in battle_lib
            and "ABILITY_DAZZLING" in battle_lib,
        "tangling_hair_hook":
            "case ABILITY_TANGLING_HAIR:" in battle_lib,
        "shadow_shield_hook":
            "ABILITY_SHADOW_SHIELD" in battle_lib
            and "defenderParams.curHP == defenderParams.maxHP" in battle_lib,
        "prism_armor_hook":
            "Battler_Ability(battleCtx, defender) == ABILITY_PRISM_ARMOR"
            in battle_lib,
        "perish_body_hook":
            "case ABILITY_PERISH_BODY:" in battle_lib
            and "perishSongTurns = 3" in battle_lib,
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
        default=Path("mr08d-unchanged-ability-reactions.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_power_and_damage(root)
    patch_immunities(root)
    patch_on_hit(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08D_UNCHANGED_ABILITY_REACTIONS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 36,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08D validation failed")


if __name__ == "__main__":
    main()
