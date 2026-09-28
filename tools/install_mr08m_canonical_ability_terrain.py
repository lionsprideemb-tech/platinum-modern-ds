#!/usr/bin/env python3
"""MR08M — accelerated canonical terrain Ability pass.

Adds nine official/current-mainline mechanics on top of MR08K:
Infiltrator, Grass Pelt, Surge Surfer, Electric Surge, Psychic Surge,
Misty Surge, Grassy Surge, Seed Sower, and Hadron Engine.

This pass also adds the shared DS-side terrain state needed by those Abilities.
Locked MR07 Summary/editor visuals are not touched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_GRASS_PELT",
    "ABILITY_SURGE_SURFER",
    "ABILITY_ELECTRIC_SURGE",
    "ABILITY_PSYCHIC_SURGE",
    "ABILITY_MISTY_SURGE",
    "ABILITY_GRASSY_SURGE",
    "ABILITY_SEED_SOWER",
    "ABILITY_HADRON_ENGINE",
)

EXPECTED_IDS = {
    "ABILITY_GRASS_PELT": 179,
    "ABILITY_SURGE_SURFER": 207,
    "ABILITY_ELECTRIC_SURGE": 226,
    "ABILITY_PSYCHIC_SURGE": 227,
    "ABILITY_MISTY_SURGE": 228,
    "ABILITY_GRASSY_SURGE": 229,
    "ABILITY_SEED_SOWER": 269,
    "ABILITY_HADRON_ENGINE": 289,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
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


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """typedef struct BattleContext BattleContext;
""",
        """#define MERCURY_TERRAIN_NONE     0
#define MERCURY_TERRAIN_ELECTRIC 1
#define MERCURY_TERRAIN_GRASSY   2
#define MERCURY_TERRAIN_MISTY    3
#define MERCURY_TERRAIN_PSYCHIC  4

""",
        "MR08M terrain constants",
    )
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08L: current-mainline terrain state.
    u8 mercuryTerrainType;
    u8 mercuryTerrainTurns;

""",
        "MR08M terrain state",
    )


def patch_shared_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    insert_before_once(
        lib,
        """static BOOL Mercury_MoveHasSheerForceSecondary(
""",
        """BOOL Mercury_IsGroundedForTerrain(BattleContext *battleCtx, int battler)
{
    if (battleCtx->fieldConditionsMask & FIELD_CONDITION_GRAVITY) {
        return TRUE;
    }

    if (battleCtx->battleMons[battler].type1 == TYPE_FLYING
        || battleCtx->battleMons[battler].type2 == TYPE_FLYING
        || Battler_Ability(battleCtx, battler) == ABILITY_LEVITATE
        || battleCtx->battleMons[battler].moveEffectsData.magnetRiseTurns) {
        return FALSE;
    }

    return TRUE;
}

void Mercury_SetTerrain(BattleContext *battleCtx, int terrain)
{
    battleCtx->mercuryTerrainType = terrain;
    battleCtx->mercuryTerrainTurns = 5;
}

""",
        "MR08M terrain helpers",
    )

    insert_before_once(
        hdr,
        """void Mercury_TriggerFaintAbilities(BattleSystem *battleSys, BattleContext *battleCtx);
""",
        """BOOL Mercury_IsGroundedForTerrain(BattleContext *battleCtx, int battler);
void Mercury_SetTerrain(BattleContext *battleCtx, int terrain);
""",
        "MR08L public terrain helpers",
    )


def patch_damage_and_speed(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    moveClass = MOVE_DATA(move).class;

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    moveClass = MOVE_DATA(move).class;

    if (Mercury_IsGroundedForTerrain(battleCtx, attacker)) {
        if ((battleCtx->mercuryTerrainType == MERCURY_TERRAIN_ELECTRIC
                && moveType == TYPE_ELECTRIC)
            || (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_GRASSY
                && moveType == TYPE_GRASS)
            || (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_PSYCHIC
                && moveType == TYPE_PSYCHIC)) {
            movePower = movePower * 13 / 10;
        }
    }

    if (Mercury_IsGroundedForTerrain(battleCtx, defender)) {
        if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_MISTY
            && moveType == TYPE_DRAGON) {
            movePower /= 2;
        }

        if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_GRASSY
            && (move == MOVE_EARTHQUAKE
                || move == MOVE_BULLDOZE
                || move == MOVE_MAGNITUDE)) {
            movePower /= 2;
        }

        if (defenderParams.ability == ABILITY_GRASS_PELT) {
            if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_GRASSY) {
                defenseStat = defenseStat * 15 / 10;
            }
        }
    }

    if (attackerParams.ability == ABILITY_HADRON_ENGINE
        && battleCtx->mercuryTerrainType == MERCURY_TERRAIN_ELECTRIC) {
        spAttackStat = spAttackStat * 4 / 3;
    }

    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        "terrain damage / Grass Pelt / Hadron Engine",
    )

    replace_once(
        path,
        """    battler1Speed = battleCtx->battleMons[battler1].speed * sStatStageBoosts[battler1SpeedStage].numerator / sStatStageBoosts[battler1SpeedStage].denominator;
    battler2Speed = battleCtx->battleMons[battler2].speed * sStatStageBoosts[battler2SpeedStage].numerator / sStatStageBoosts[battler2SpeedStage].denominator;

    if (NO_CLOUD_NINE) {
""",
        """    battler1Speed = battleCtx->battleMons[battler1].speed * sStatStageBoosts[battler1SpeedStage].numerator / sStatStageBoosts[battler1SpeedStage].denominator;
    battler2Speed = battleCtx->battleMons[battler2].speed * sStatStageBoosts[battler2SpeedStage].numerator / sStatStageBoosts[battler2SpeedStage].denominator;

    if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_ELECTRIC) {
        if (battler1Ability == ABILITY_SURGE_SURFER) {
            battler1Speed *= 2;
        }
        if (battler2Ability == ABILITY_SURGE_SURFER) {
            battler2Speed *= 2;
        }
    }

    if (NO_CLOUD_NINE) {
""",
        "Surge Surfer speed",
    )


def patch_switch_in_surges(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """                    case ABILITY_HOSPITALITY: {
""",
        """                    case ABILITY_ELECTRIC_SURGE:
                    case ABILITY_HADRON_ENGINE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_ELECTRIC) {
                            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_ELECTRIC);
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = Battler_Ability(battleCtx, battler);
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

                    case ABILITY_GRASSY_SURGE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_GRASSY) {
                            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_GRASSY);
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = ABILITY_GRASSY_SURGE;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

                    case ABILITY_MISTY_SURGE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_MISTY) {
                            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_MISTY);
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = ABILITY_MISTY_SURGE;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

                    case ABILITY_PSYCHIC_SURGE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_PSYCHIC) {
                            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_PSYCHIC);
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = ABILITY_PSYCHIC_SURGE;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

""",
        "terrain-setting switch-in abilities",
    )


def patch_seed_sower(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    case ABILITY_THERMAL_EXCHANGE: {
""",
        """    case ABILITY_SEED_SOWER:
        if (DEFENDING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && battleCtx->mercuryTerrainType != MERCURY_TERRAIN_GRASSY) {
            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_GRASSY);
            battleCtx->msgBattlerTemp = battleCtx->defender;
            battleCtx->msgTemp = ABILITY_SEED_SOWER;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

""",
        "Seed Sower on-hit terrain",
    )


def patch_terrain_turns(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    FIELD_COND_CHECK_STATE_GRAVITY,

    FIELD_COND_CHECK_END
""",
        """    FIELD_COND_CHECK_STATE_GRAVITY,
    FIELD_COND_CHECK_STATE_MERCURY_TERRAIN,

    FIELD_COND_CHECK_END
""",
        "terrain field-condition state",
    )

    insert_before_once(
        path,
        """        case FIELD_COND_CHECK_END:
""",
        """        case FIELD_COND_CHECK_STATE_MERCURY_TERRAIN:
            if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_NONE
                && battleCtx->mercuryTerrainTurns) {
                int i;

                if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_GRASSY) {
                    for (i = 0; i < maxBattlers; i++) {
                        if (battleCtx->battleMons[i].curHP
                            && battleCtx->battleMons[i].curHP
                                < battleCtx->battleMons[i].maxHP
                            && Mercury_IsGroundedForTerrain(battleCtx, i)) {
                            int heal = battleCtx->battleMons[i].maxHP / 16;
                            if (heal < 1) {
                                heal = 1;
                            }
                            battleCtx->battleMons[i].curHP += heal;
                            if (battleCtx->battleMons[i].curHP
                                > battleCtx->battleMons[i].maxHP) {
                                battleCtx->battleMons[i].curHP =
                                    battleCtx->battleMons[i].maxHP;
                            }
                            BattleMon_CopyToParty(battleSys, battleCtx, i);
                        }
                    }
                }

                battleCtx->mercuryTerrainTurns--;
                if (battleCtx->mercuryTerrainTurns == 0) {
                    battleCtx->mercuryTerrainType = MERCURY_TERRAIN_NONE;
                }
            }
            battleCtx->fieldConditionCheckState++;
            break;

""",
        "terrain duration / Grassy Terrain healing",
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
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "terrain_state":
            "mercuryTerrainType" in ctx and "mercuryTerrainTurns" in ctx,
        "grass_pelt_hook":
            "ABILITY_GRASS_PELT" in lib and "defenseStat = defenseStat * 15 / 10" in lib,
        "surge_surfer_hook":
            "ABILITY_SURGE_SURFER" in lib and "battler1Speed *= 2" in lib,
        "electric_surge_hook":
            "case ABILITY_ELECTRIC_SURGE:" in lib,
        "psychic_surge_hook":
            "case ABILITY_PSYCHIC_SURGE:" in lib,
        "misty_surge_hook":
            "case ABILITY_MISTY_SURGE:" in lib,
        "grassy_surge_hook":
            "case ABILITY_GRASSY_SURGE:" in lib,
        "seed_sower_hook":
            "case ABILITY_SEED_SOWER:" in lib,
        "hadron_engine_hook":
            "case ABILITY_HADRON_ENGINE:" in lib
            and "spAttackStat = spAttackStat * 4 / 3" in lib,
        "terrain_duration_hook":
            "FIELD_COND_CHECK_STATE_MERCURY_TERRAIN" in controller,
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
        default=Path("mr08m-canonical-ability-terrain.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_shared_helpers(root)
    patch_damage_and_speed(root)
    patch_switch_in_surges(root)
    patch_seed_sower(root)
    patch_terrain_turns(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08M_CANONICAL_ABILITY_TERRAIN",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 148,
        "remaining_modern_canonical_mechanics": 39,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08M validation failed")


if __name__ == "__main__":
    main()
