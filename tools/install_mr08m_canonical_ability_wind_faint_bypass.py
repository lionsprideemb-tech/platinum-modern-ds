#!/usr/bin/env python3
"""MR08M — canonical Ability fast pass, wind/faint/bypass family.

Adds six official/current-mainline Ability mechanics:

- Infiltrator
- Soul-Heart
- Wind Rider
- Wind Power
- Mycelium Might
- Supersweet Syrup

Mechanics-only pass; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_INFILTRATOR",
    "ABILITY_SOUL_HEART",
    "ABILITY_WIND_RIDER",
    "ABILITY_WIND_POWER",
    "ABILITY_MYCELIUM_MIGHT",
    "ABILITY_SUPERSWEET_SYRUP",
)

EXPECTED_IDS = {
    "ABILITY_INFILTRATOR": 151,
    "ABILITY_SOUL_HEART": 220,
    "ABILITY_WIND_RIDER": 274,
    "ABILITY_WIND_POWER": 277,
    "ABILITY_MYCELIUM_MIGHT": 298,
    "ABILITY_SUPERSWEET_SYRUP": 306,
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
        "wind-move classifier",
    )

    insert_before_once(
        lib,
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_BULLETPROOF) == TRUE
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
            return subscript_update_stat_stage;
        }

        battleCtx->msgBattlerTemp = defender;
        battleCtx->msgTemp = ABILITY_WIND_RIDER;
        return subscript_mold_breaker;
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
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE) {
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


def patch_myc​​elium_might(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    if (battler1Priority == battler2Priority) {
""",
        """    if (battler1Move
        && battler1Ability == ABILITY_MYCELIUM_MIGHT
        && MOVE_DATA(battler1Move).class == CLASS_STATUS) {
        battler1LaggingTail = 1;
    }

    if (battler2Move
        && battler2Ability == ABILITY_MYCELIUM_MIGHT
        && MOVE_DATA(battler2Move).class == CLASS_STATUS) {
        battler2LaggingTail = 1;
    }

""",
        "Mycelium Might status moves act last",
    )

    replace_once(
        path,
        """BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)
{
    BOOL result = FALSE;

    if (Battler_Ability(battleCtx, attacker) != ABILITY_MOLD_BREAKER) {
""",
        """BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)
{
    BOOL result = FALSE;

    if (attacker != defender
        && Battler_Ability(battleCtx, attacker) == ABILITY_MYCELIUM_MIGHT
        && CURRENT_MOVE_DATA.class == CLASS_STATUS) {
        return FALSE;
    }

    if (Battler_Ability(battleCtx, attacker) != ABILITY_MOLD_BREAKER) {
""",
        "Mycelium Might status-move Ability bypass",
    )


def patch_soul_heart(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        path,
        """static BOOL BattleControllerPlayer_AnyFainted(BattleContext *battleCtx, int nextCmd, int nextCmdNoFainted, BOOL onlyFaint)
""",
        """static void Mercury_TriggerSoulHeart(BattleContext *battleCtx, int fainted)
{
    int i;

    for (i = 0; i < MAX_BATTLERS; i++) {
        if (i != fainted
            && battleCtx->battleMons[i].curHP
            && Battler_Ability(battleCtx, i) == ABILITY_SOUL_HEART
            && battleCtx->battleMons[i].statBoosts[BATTLE_STAT_SP_ATTACK]
                < MAX_STAT_STAGE) {
            battleCtx->battleMons[i].statBoosts[BATTLE_STAT_SP_ATTACK]++;
        }
    }
}

""",
        "Soul-Heart faint helper",
    )

    replace_once(
        path,
        """        battleCtx->faintedMon = LowestBit(battlerBit >> SYSCTL_MON_FAINTED_SHIFT);

        if (onlyFaint == TRUE) {
""",
        """        battleCtx->faintedMon = LowestBit(battlerBit >> SYSCTL_MON_FAINTED_SHIFT);
        Mercury_TriggerSoulHeart(battleCtx, battleCtx->faintedMon);

        if (onlyFaint == TRUE) {
""",
        "Soul-Heart standard faint trigger",
    )

    replace_once(
        path,
        """        battleCtx->faintedMon = LowestBit((battleCtx->battleStatusMask & SYSCTL_MON_SELFDESTRUCTED) >> SYSCTL_MON_SELFDESTRUCTED_SHIFT);
        battleCtx->battleStatusMask &= ~SYSCTL_MON_SELFDESTRUCTED;

        LOAD_SUBSEQ(subscript_after_selfdestruct);
""",
        """        battleCtx->faintedMon = LowestBit((battleCtx->battleStatusMask & SYSCTL_MON_SELFDESTRUCTED) >> SYSCTL_MON_SELFDESTRUCTED_SHIFT);
        battleCtx->battleStatusMask &= ~SYSCTL_MON_SELFDESTRUCTED;
        Mercury_TriggerSoulHeart(battleCtx, battleCtx->faintedMon);

        LOAD_SUBSEQ(subscript_after_selfdestruct);
""",
        "Soul-Heart selfdestruct faint trigger",
    )


def patch_supersweet_syrup(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """#define MERCURY_ONCE_INTREPID_SWORD  (1 << 0)
#define MERCURY_ONCE_DAUNTLESS_SHIELD (1 << 1)
""",
        """#define MERCURY_ONCE_INTREPID_SWORD   (1 << 0)
#define MERCURY_ONCE_DAUNTLESS_SHIELD (1 << 1)
#define MERCURY_ONCE_SUPERSWEET_SYRUP  (1 << 2)
""",
        "Supersweet Syrup once-per-battle flag",
    )

    insert_before_once(
        path,
        """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && (Battler_Ability(battleCtx, battler) == ABILITY_INTREPID_SWORD
""",
        """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && Battler_Ability(battleCtx, battler) == ABILITY_SUPERSWEET_SYRUP) {
                    int slot = battleCtx->selectedPartySlot[battler];

                    battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                    if ((battleCtx->mercuryOnceAbilityFlags[battler][slot]
                            & MERCURY_ONCE_SUPERSWEET_SYRUP) == 0) {
                        int j;

                        battleCtx->mercuryOnceAbilityFlags[battler][slot] |=
                            MERCURY_ONCE_SUPERSWEET_SYRUP;

                        for (j = 0; j < maxBattlers; j++) {
                            if (battleCtx->battleMons[j].curHP == 0
                                || BattleSystem_GetBattlerSide(battleSys, j)
                                    == BattleSystem_GetBattlerSide(battleSys, battler)) {
                                continue;
                            }

                            if (Battler_IgnorableAbility(
                                    battleCtx,
                                    battler,
                                    j,
                                    ABILITY_CLEAR_BODY) == TRUE
                                || Battler_IgnorableAbility(
                                    battleCtx,
                                    battler,
                                    j,
                                    ABILITY_WHITE_SMOKE) == TRUE
                                || Battler_Ability(battleCtx, j)
                                    == ABILITY_FULL_METAL_BODY
                                || battleCtx->sideConditions[
                                    BattleSystem_GetBattlerSide(battleSys, j)
                                ].mistTurns) {
                                continue;
                            }

                            if (Battler_IgnorableAbility(
                                    battleCtx,
                                    battler,
                                    j,
                                    ABILITY_MIRROR_ARMOR) == TRUE) {
                                if (battleCtx->battleMons[battler].statBoosts[
                                        BATTLE_STAT_EVASION] > MIN_STAT_STAGE) {
                                    battleCtx->battleMons[battler].statBoosts[
                                        BATTLE_STAT_EVASION]--;
                                }
                                continue;
                            }

                            if (Battler_Ability(battleCtx, j) == ABILITY_CONTRARY) {
                                if (battleCtx->battleMons[j].statBoosts[
                                        BATTLE_STAT_EVASION] < MAX_STAT_STAGE) {
                                    battleCtx->battleMons[j].statBoosts[
                                        BATTLE_STAT_EVASION]++;
                                }
                            } else if (battleCtx->battleMons[j].statBoosts[
                                    BATTLE_STAT_EVASION] > MIN_STAT_STAGE) {
                                int drop = Battler_Ability(battleCtx, j)
                                        == ABILITY_SIMPLE
                                    ? 2
                                    : 1;

                                battleCtx->battleMons[j].statBoosts[
                                    BATTLE_STAT_EVASION] -= drop;
                                if (battleCtx->battleMons[j].statBoosts[
                                        BATTLE_STAT_EVASION] < MIN_STAT_STAGE) {
                                    battleCtx->battleMons[j].statBoosts[
                                        BATTLE_STAT_EVASION] = MIN_STAT_STAGE;
                                }
                            }
                        }

                        battleCtx->msgBattlerTemp = battler;
                        battleCtx->msgTemp = ABILITY_SUPERSWEET_SYRUP;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }
                }

""",
        "Supersweet Syrup entry evasion drop",
    )


def update_registry(path: Path) -> None:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "infiltrator_hook":
            lib.count("ABILITY_INFILTRATOR") >= 2
            and "ABILITY_INFILTRATOR" in controller
            and "ABILITY_INFILTRATOR" in script,
        "soul_heart_hook":
            "Mercury_TriggerSoulHeart" in controller
            and "ABILITY_SOUL_HEART" in controller,
        "wind_rider_hook":
            "ABILITY_WIND_RIDER" in lib
            and "Mercury_MoveIsWind" in lib
            and "ABILITY_WIND_RIDER" in script,
        "wind_power_hook":
            "case ABILITY_WIND_POWER:" in lib
            and "MOVE_EFFECT_CHARGE" in lib
            and "ABILITY_WIND_POWER" in script,
        "mycelium_might_hook":
            lib.count("ABILITY_MYCELIUM_MIGHT") >= 3
            and "CLASS_STATUS" in lib,
        "supersweet_syrup_hook":
            "ABILITY_SUPERSWEET_SYRUP" in lib
            and "MERCURY_ONCE_SUPERSWEET_SYRUP" in lib
            and "BATTLE_STAT_EVASION" in lib,
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
        default=Path("mr08m-canonical-ability-wind-faint-bypass.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_wind_family(root)
    patch_infiltrator(root)
    patch_myc​​elium_might(root)
    patch_soul_heart(root)
    patch_supersweet_syrup(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08M_CANONICAL_ABILITY_WIND_FAINT_BYPASS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 133,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08M validation failed")


if __name__ == "__main__":
    main()
