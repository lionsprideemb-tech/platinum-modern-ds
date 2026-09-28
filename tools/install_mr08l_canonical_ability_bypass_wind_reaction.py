#!/usr/bin/env python3
"""MR08L — canonical Ability accelerated bypass/wind/reaction pass.

Adds five distinct official/current-mainline Ability mechanics after MR08K:

- Infiltrator
- Wind Rider
- Wind Power
- Opportunist
- Poison Puppeteer

This pass deliberately avoids overlapping the 25-Ability MR08K registry.
Mechanics only; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_INFILTRATOR",
    "ABILITY_WIND_RIDER",
    "ABILITY_WIND_POWER",
    "ABILITY_OPPORTUNIST",
    "ABILITY_POISON_PUPPETEER",
)

EXPECTED_IDS = {
    "ABILITY_INFILTRATOR": 151,
    "ABILITY_WIND_RIDER": 274,
    "ABILITY_WIND_POWER": 277,
    "ABILITY_OPPORTUNIST": 290,
    "ABILITY_POISON_PUPPETEER": 310,
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


def patch_wind_family(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    script = root / "src/battle/battle_script.c"

    insert_before_once(
        lib,
        """static BOOL Mercury_MoveIsPulse(int move)
""",
        """static BOOL Mercury_MoveIsWind(int move)
{
    switch (move) {
    case MOVE_AEROBLAST:
    case MOVE_AIR_CUTTER:
    case MOVE_BLEAKWIND_STORM:
    case MOVE_BLIZZARD:
    case MOVE_FAIRY_WIND:
    case MOVE_GUST:
    case MOVE_HEAT_WAVE:
    case MOVE_HURRICANE:
    case MOVE_ICY_WIND:
    case MOVE_PETAL_BLIZZARD:
    case MOVE_SANDSEAR_STORM:
    case MOVE_SANDSTORM:
    case MOVE_SPRINGTIDE_STORM:
    case MOVE_TAILWIND:
    case MOVE_TWISTER:
    case MOVE_WHIRLWIND:
    case MOVE_WILDBOLT_STORM:
        return TRUE;
    default:
        return FALSE;
    }
}

""",
        "wind move classifier",
    )

    insert_before_once(
        lib,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOUNDPROOF) == TRUE) {
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_WIND_RIDER) == TRUE
        && attacker != defender
        && Mercury_MoveIsWind(battleCtx->moveCur)) {
        if (battleCtx->battleMons[defender].statBoosts[BATTLE_STAT_ATTACK]
            < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = defender;
            subscript = subscript_update_stat_stage;
        } else {
            battleCtx->msgBattlerTemp = defender;
            battleCtx->msgTemp = ABILITY_WIND_RIDER;
            subscript = subscript_mold_breaker;
        }
    }

""",
        "Wind Rider wind immunity/Attack boost",
    )

    insert_before_once(
        lib,
        """    case ABILITY_ELECTROMORPHOSIS:
""",
        """    case ABILITY_WIND_POWER:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_WIND_POWER) == TRUE
            && battleCtx->attacker != battleCtx->defender
            && Mercury_MoveIsWind(battleCtx->moveCur)
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            DEFENDING_MON.moveEffectsMask |= MOVE_EFFECT_CHARGE;
            DEFENDING_MON.moveEffectsData.chargedTurns = 2;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            battleCtx->msgTemp = ABILITY_WIND_POWER;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

""",
        "Wind Power wind-hit Charge",
    )

    replace_once(
        script,
        """    default:
        GF_ASSERT(FALSE);
        break;
    }

    return FALSE;
}

static inline BOOL AbilityBlocksSpecificStatReduction
""",
        """    default:
        GF_ASSERT(FALSE);
        break;
    }

    if (op == OPCODE_FLAG_ON
        && dstVar == BTLVAR_SIDE_CONDITIONS_ATTACKER
        && srcVal == SIDE_CONDITION_TAILWIND) {
        int i;
        int attackerSide = BattleSystem_GetBattlerSide(
            battleSys, battleCtx->attacker);
        int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

        for (i = 0; i < maxBattlers; i++) {
            if (battleCtx->battleMons[i].curHP
                && BattleSystem_GetBattlerSide(battleSys, i) == attackerSide) {
                if (Battler_Ability(battleCtx, i) == ABILITY_WIND_POWER) {
                    battleCtx->battleMons[i].moveEffectsMask |= MOVE_EFFECT_CHARGE;
                    battleCtx->battleMons[i].moveEffectsData.chargedTurns = 2;
                } else if (Battler_Ability(battleCtx, i) == ABILITY_WIND_RIDER
                    && battleCtx->battleMons[i].statBoosts[BATTLE_STAT_ATTACK]
                        < MAX_STAT_STAGE) {
                    battleCtx->battleMons[i].statBoosts[BATTLE_STAT_ATTACK]++;
                }
            }
        }
    }

    return FALSE;
}

static inline BOOL AbilityBlocksSpecificStatReduction
""",
        "Tailwind activates Wind Power/Wind Rider",
    )


def patch_infiltrator(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    controller = root / "src/battle/battle_controller_player.c"
    script = root / "src/battle/battle_script.c"

    replace_once(
        lib,
        """        if ((sideConditions & SIDE_CONDITION_REFLECT) != FALSE
            && criticalMul == 1
""",
        """        if ((sideConditions & SIDE_CONDITION_REFLECT) != FALSE
            && attackerParams.ability != ABILITY_INFILTRATOR
            && criticalMul == 1
""",
        "Infiltrator Reflect bypass",
    )
    replace_once(
        lib,
        """        if ((sideConditions & SIDE_CONDITION_LIGHT_SCREEN) != FALSE
            && criticalMul == 1
""",
        """        if ((sideConditions & SIDE_CONDITION_LIGHT_SCREEN) != FALSE
            && attackerParams.ability != ABILITY_INFILTRATOR
            && criticalMul == 1
""",
        "Infiltrator Light Screen bypass",
    )

    replace_once(
        controller,
        """        if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE) && battleCtx->damage < 0) {
""",
        """        if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE)
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_INFILTRATOR
            && battleCtx->damage < 0) {
""",
        "Infiltrator damaging Substitute bypass",
    )

    replace_once(
        script,
        """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
    if ((battleCtx->battleMons[battler].statusVolatile & VOLATILE_CONDITION_SUBSTITUTE)
        || (battleCtx->selfTurnFlags[battler].statusFlags & SELF_TURN_FLAG_SUBSTITUTE_HIT)) {
        BattleScript_Iter(battleCtx, jumpSubActive);
    }
""",
        """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
    if (((battleCtx->battleMons[battler].statusVolatile & VOLATILE_CONDITION_SUBSTITUTE)
            || (battleCtx->selfTurnFlags[battler].statusFlags
                & SELF_TURN_FLAG_SUBSTITUTE_HIT))
        && (battler == battleCtx->attacker
            || Battler_Ability(battleCtx, battleCtx->attacker)
                != ABILITY_INFILTRATOR)) {
        BattleScript_Iter(battleCtx, jumpSubActive);
    }
""",
        "Infiltrator scripted Substitute bypass",
    )


def patch_opportunist(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_once(
        path,
        """            if (mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] > MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] = MAX_STAT_STAGE;
            }
        }
    } else {
""",
        """            if (mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] > MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] = MAX_STAT_STAGE;
            }

            if (stageChange > 0) {
                int i;
                int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
                int boostedStat = BATTLE_STAT_ATTACK + statOffset;

                for (i = 0; i < maxBattlers; i++) {
                    if (i != battleCtx->sideEffectMon
                        && battleCtx->battleMons[i].curHP
                        && BattleSystem_GetBattlerSide(battleSys, i)
                            != BattleSystem_GetBattlerSide(
                                battleSys, battleCtx->sideEffectMon)
                        && Battler_Ability(battleCtx, i) == ABILITY_OPPORTUNIST
                        && battleCtx->battleMons[i].statBoosts[boostedStat]
                            < MAX_STAT_STAGE) {
                        battleCtx->battleMons[i].statBoosts[boostedStat] +=
                            stageChange;
                        if (battleCtx->battleMons[i].statBoosts[boostedStat]
                            > MAX_STAT_STAGE) {
                            battleCtx->battleMons[i].statBoosts[boostedStat] =
                                MAX_STAT_STAGE;
                        }
                    }
                }
            }
        }
    } else {
""",
        "Opportunist copies opponent stat raises",
    )


def patch_poison_puppeteer(root: Path) -> None:
    poison = root / "res/battle/scripts/subscripts/subscript_poison.s"
    toxic = root / "res/battle/scripts/subscripts/subscript_badly_poison.s"

    replace_once(
        poison,
        """_172:
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_TRY_SYNCHRONIZE_STATUS
    End 
""",
        """_172:
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_TRY_SYNCHRONIZE_STATUS

_MercuryPoisonPuppeteer:
    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_POISON_PUPPETEER, _MercuryPoisonPuppeteerApply
    End 

_MercuryPoisonPuppeteerApply:
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_ABILITY
    Call BATTLE_SUBSCRIPT_CONFUSE
    End 
""",
        "Poison Puppeteer regular poison confusion",
    )

    replace_once(
        poison,
        """    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_TRY_SYNCHRONIZE_STATUS
    End 
""",
        """    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_TRY_SYNCHRONIZE_STATUS
    GoTo _MercuryPoisonPuppeteer
""",
        "Poison Puppeteer regular poison first synchronize path",
    )

    replace_once(
        toxic,
        """_244:
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_TRY_SYNCHRONIZE_STATUS

_248:
    End 
""",
        """_244:
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_TRY_SYNCHRONIZE_STATUS

_248:
    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_POISON_PUPPETEER, _MercuryToxicPuppeteerApply
    End 

_MercuryToxicPuppeteerApply:
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_ABILITY
    Call BATTLE_SUBSCRIPT_CONFUSE
    End 
""",
        "Poison Puppeteer toxic confusion",
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
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    poison = (root / "res/battle/scripts/subscripts/subscript_poison.s").read_text(encoding="utf-8")
    toxic = (root / "res/battle/scripts/subscripts/subscript_badly_poison.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "infiltrator_hook":
            lib.count("ABILITY_INFILTRATOR") >= 2
            and "ABILITY_INFILTRATOR" in controller
            and "ABILITY_INFILTRATOR" in script,
        "wind_rider_hook":
            "ABILITY_WIND_RIDER" in lib
            and "Mercury_MoveIsWind" in lib
            and "ABILITY_WIND_RIDER" in script,
        "wind_power_hook":
            "case ABILITY_WIND_POWER:" in lib
            and "MOVE_EFFECT_CHARGE" in lib
            and "ABILITY_WIND_POWER" in script,
        "opportunist_hook":
            "ABILITY_OPPORTUNIST" in script
            and "stageChange > 0" in script,
        "poison_puppeteer_hook":
            "ABILITY_POISON_PUPPETEER" in poison
            and "BATTLE_SUBSCRIPT_CONFUSE" in poison
            and "ABILITY_POISON_PUPPETEER" in toxic
            and "BATTLE_SUBSCRIPT_CONFUSE" in toxic,
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
        default=Path("mr08l-canonical-ability-bypass-wind-reaction.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_wind_family(root)
    patch_infiltrator(root)
    patch_opportunist(root)
    patch_poison_puppeteer(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08L_CANONICAL_ABILITY_BYPASS_WIND_REACTION",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 140,
        "remaining_modern_canonical_mechanics": 47,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08L validation failed")


if __name__ == "__main__":
    main()
