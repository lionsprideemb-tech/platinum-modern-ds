#!/usr/bin/env python3
"""MR08N — canonical Ability strong-weather/suppression shell pass.

Adds five official/current-mainline Ability mechanics after MR08M:
Primordial Sea, Desolate Land, Delta Stream, Neutralizing Gas, and Tera Shell.

This pass adds dynamic strong-weather state, central Neutralizing Gas
suppression, Delta Stream's Flying weakness removal, and Tera Shell's
full-HP not-very-effective override. Locked MR07 Summary/editor visuals are
not touched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_PRIMORDIAL_SEA",
    "ABILITY_DESOLATE_LAND",
    "ABILITY_DELTA_STREAM",
    "ABILITY_NEUTRALIZING_GAS",
    "ABILITY_TERA_SHELL",
)

EXPECTED_IDS = {
    "ABILITY_PRIMORDIAL_SEA": 189,
    "ABILITY_DESOLATE_LAND": 190,
    "ABILITY_DELTA_STREAM": 191,
    "ABILITY_NEUTRALIZING_GAS": 256,
    "ABILITY_TERA_SHELL": 308,
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


def replace_function(path: Path, signature: str, replacement: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

    open_brace = start + len(signature) + 1
    depth = 0
    end = -1
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end < 0:
        raise SystemExit(f"{label}: closing brace not found in {path}")

    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected
        and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_context_and_weather_macros(root: Path) -> None:
    ctx = root / "include/battle/battle_context.h"
    insert_before_once(
        ctx,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08N: source-tracked strong weather. The state is
    // intentionally separate from Platinum's timed/permanent weather flags so
    // ordinary weather cannot silently overwrite a primal weather.
    u32 mercuryStrongWeatherType;
    u32 mercuryStrongWeatherSource;

""",
        "MR08N strong-weather context state",
    )

    common = root / "include/battle/common.h"
    insert_before_once(
        common,
        """#define NO_CLOUD_NINE""",
        """#define MERCURY_STRONG_WEATHER_NONE  0
#define MERCURY_STRONG_WEATHER_RAIN  1
#define MERCURY_STRONG_WEATHER_SUN   2
#define MERCURY_STRONG_WEATHER_DELTA 3

#define MERCURY_STRONG_WEATHER_ACTIVE \
    (Mercury_StrongWeatherType(battleCtx) != MERCURY_STRONG_WEATHER_NONE)

""",
        "MR08N strong-weather constants",
    )

    replace_once(
        common,
        """#define NO_WEATHER ((battleCtx->fieldConditionsMask & FIELD_CONDITION_WEATHER) == FALSE             \\
    || BattleSystem_CountAbility(battleSys, battleCtx, COUNT_ALIVE_BATTLERS, 0, ABILITY_CLOUD_NINE) \\
    || BattleSystem_CountAbility(battleSys, battleCtx, COUNT_ALIVE_BATTLERS, 0, ABILITY_AIR_LOCK))
#define WEATHER_IS_RAIN (battleCtx->fieldConditionsMask & FIELD_CONDITION_RAINING)
#define WEATHER_IS_SAND (battleCtx->fieldConditionsMask & FIELD_CONDITION_SANDSTORM)
#define WEATHER_IS_SUN  (battleCtx->fieldConditionsMask & FIELD_CONDITION_SUNNY)
""",
        """#define NO_WEATHER ((((battleCtx->fieldConditionsMask & FIELD_CONDITION_WEATHER) == FALSE) \\
        && !MERCURY_STRONG_WEATHER_ACTIVE) \\
    || BattleSystem_CountAbility(battleSys, battleCtx, COUNT_ALIVE_BATTLERS, 0, ABILITY_CLOUD_NINE) \\
    || BattleSystem_CountAbility(battleSys, battleCtx, COUNT_ALIVE_BATTLERS, 0, ABILITY_AIR_LOCK))
#define WEATHER_IS_RAIN ((battleCtx->fieldConditionsMask & FIELD_CONDITION_RAINING) \\
    || Mercury_StrongWeatherType(battleCtx) == MERCURY_STRONG_WEATHER_RAIN)
#define WEATHER_IS_SAND (battleCtx->fieldConditionsMask & FIELD_CONDITION_SANDSTORM)
#define WEATHER_IS_SUN  ((battleCtx->fieldConditionsMask & FIELD_CONDITION_SUNNY) \\
    || Mercury_StrongWeatherType(battleCtx) == MERCURY_STRONG_WEATHER_SUN)
""",
        "MR08N strong-weather common macros",
    )


def patch_ability_suppression_and_weather_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    insert_before_once(
        hdr,
        """BOOL Mercury_IsGroundedForTerrain(BattleContext *battleCtx, int battler);
""",
        """int Mercury_StrongWeatherType(BattleContext *battleCtx);
""",
        "MR08N strong-weather public helper",
    )

    insert_before_once(
        lib,
        """u16 Battler_Ability(BattleContext *battleCtx, int battler)
""",
        """static BOOL Mercury_AbilityCannotBeNeutralized(int ability)
{
    switch (ability) {
    case ABILITY_MULTITYPE:
    case ABILITY_ZEN_MODE:
    case ABILITY_STANCE_CHANGE:
    case ABILITY_SCHOOLING:
    case ABILITY_COMATOSE:
    case ABILITY_SHIELDS_DOWN:
    case ABILITY_DISGUISE:
    case ABILITY_BATTLE_BOND:
    case ABILITY_POWER_CONSTRUCT:
    case ABILITY_RKS_SYSTEM:
    case ABILITY_GULP_MISSILE:
    case ABILITY_ICE_FACE:
    case ABILITY_HUNGER_SWITCH:
    case ABILITY_AS_ONE_GLASTRIER:
    case ABILITY_AS_ONE_SPECTRIER:
    case ABILITY_ZERO_TO_HERO:
    case ABILITY_COMMANDER:
    case ABILITY_EMBODY_ASPECT:
    case ABILITY_EMBODY_ASPECT_2:
    case ABILITY_EMBODY_ASPECT_3:
    case ABILITY_EMBODY_ASPECT_4:
    case ABILITY_TERA_SHIFT:
        return TRUE;
    }

    return FALSE;
}

static BOOL Mercury_NeutralizingGasRawActive(
    BattleContext *battleCtx,
    int ignoredBattler)
{
    int i;

    for (i = 0; i < MAX_BATTLERS; i++) {
        if (i != ignoredBattler
            && battleCtx->battleMons[i].curHP
            && battleCtx->battleMons[i].ability == ABILITY_NEUTRALIZING_GAS
            && (battleCtx->battleMons[i].moveEffectsMask
                & MOVE_EFFECT_ABILITY_SUPPRESSED) == FALSE) {
            return TRUE;
        }
    }

    return FALSE;
}

int Mercury_StrongWeatherType(BattleContext *battleCtx)
{
    int source = battleCtx->mercuryStrongWeatherSource;
    int type = battleCtx->mercuryStrongWeatherType;
    int expectedAbility = ABILITY_NONE;
    int i;

    switch (type) {
    case MERCURY_STRONG_WEATHER_RAIN:
        expectedAbility = ABILITY_PRIMORDIAL_SEA;
        break;
    case MERCURY_STRONG_WEATHER_SUN:
        expectedAbility = ABILITY_DESOLATE_LAND;
        break;
    case MERCURY_STRONG_WEATHER_DELTA:
        expectedAbility = ABILITY_DELTA_STREAM;
        break;
    default:
        return MERCURY_STRONG_WEATHER_NONE;
    }

    if (source < MAX_BATTLERS
        && battleCtx->battleMons[source].curHP
        && Battler_Ability(battleCtx, source) == expectedAbility) {
        return type;
    }

    // If the active source left but another user of the *same* primal
    // Ability remains active, ownership transfers instead of clearing.
    for (i = 0; i < MAX_BATTLERS; i++) {
        if (battleCtx->battleMons[i].curHP
            && Battler_Ability(battleCtx, i) == expectedAbility) {
            battleCtx->mercuryStrongWeatherSource = i;
            return type;
        }
    }

    battleCtx->mercuryStrongWeatherType = MERCURY_STRONG_WEATHER_NONE;
    battleCtx->mercuryStrongWeatherSource = BATTLER_NONE;
    return MERCURY_STRONG_WEATHER_NONE;
}

""",
        "MR08N suppression/strong-weather helpers",
    )

    replace_function(
        lib,
        "u16 Battler_Ability(BattleContext *battleCtx, int battler)",
        """u16 Battler_Ability(BattleContext *battleCtx, int battler)
{
    u16 ability = battleCtx->battleMons[battler].ability;

    if ((battleCtx->battleMons[battler].moveEffectsMask
            & MOVE_EFFECT_ABILITY_SUPPRESSED)
        && ability != ABILITY_MULTITYPE) {
        return ABILITY_NONE;
    }

    if ((battleCtx->fieldConditionsMask & FIELD_CONDITION_GRAVITY)
        && ability == ABILITY_LEVITATE) {
        return ABILITY_NONE;
    }

    if ((battleCtx->battleMons[battler].moveEffectsMask & MOVE_EFFECT_INGRAIN)
        && ability == ABILITY_LEVITATE) {
        return ABILITY_NONE;
    }

    if (ability != ABILITY_NEUTRALIZING_GAS
        && Mercury_AbilityCannotBeNeutralized(ability) == FALSE
        && Mercury_NeutralizingGasRawActive(battleCtx, battler)) {
        return ABILITY_NONE;
    }

    return ability;
}""",
        "MR08N Neutralizing Gas central suppression",
    )


def patch_strong_weather_switch_in(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    insert_before_once(
        lib,
        """                    case ABILITY_DRIZZLE:
""",
        """                    case ABILITY_PRIMORDIAL_SEA:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->mercuryStrongWeatherType =
                            MERCURY_STRONG_WEATHER_RAIN;
                        battleCtx->mercuryStrongWeatherSource = battler;
                        battleCtx->fieldConditionsMask &= ~FIELD_CONDITION_WEATHER;
                        battleCtx->msgTemp = ABILITY_PRIMORDIAL_SEA;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;

                    case ABILITY_DESOLATE_LAND:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->mercuryStrongWeatherType =
                            MERCURY_STRONG_WEATHER_SUN;
                        battleCtx->mercuryStrongWeatherSource = battler;
                        battleCtx->fieldConditionsMask &= ~FIELD_CONDITION_WEATHER;
                        battleCtx->msgTemp = ABILITY_DESOLATE_LAND;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;

                    case ABILITY_DELTA_STREAM:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->mercuryStrongWeatherType =
                            MERCURY_STRONG_WEATHER_DELTA;
                        battleCtx->mercuryStrongWeatherSource = battler;
                        battleCtx->fieldConditionsMask &= ~FIELD_CONDITION_WEATHER;
                        battleCtx->msgTemp = ABILITY_DELTA_STREAM;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;

                    case ABILITY_NEUTRALIZING_GAS:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->msgTemp = ABILITY_NEUTRALIZING_GAS;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;

""",
        "MR08N strong weather / gas switch-in cases",
    )


def patch_weather_change_lock(root: Path) -> None:
    script = root / "src/battle/battle_script.c"

    replace_once(
        script,
        """    int *var = BattleScript_VarAddress(battleSys, battleCtx, dstVar);
    u32 mask;

    switch (op) {
""",
        """    int *var = BattleScript_VarAddress(battleSys, battleCtx, dstVar);
    u32 mask;

    // Primal weather and Delta Stream cannot be replaced by ordinary weather
    // moves or ordinary weather-setting Abilities. Strong-weather Abilities
    // themselves update the Mercury state directly in the switch-in pass.
    if (dstVar == BTLVAR_FIELD_CONDITIONS
        && Mercury_StrongWeatherType(battleCtx) != MERCURY_STRONG_WEATHER_NONE
        && (srcVal & FIELD_CONDITION_WEATHER)
        && (op == OPCODE_SET
            || op == OPCODE_FLAG_ON
            || op == OPCODE_FLAG_OFF)) {
        return FALSE;
    }

    switch (op) {
""",
        "MR08N ordinary-weather replacement lock",
    )


def patch_type_chart(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    replace_once(
        lib,
        """    u8 defenderItemPower;

    totalMul = 1;
""",
        """    u8 defenderItemPower;
    int preTypeDamage;
    int typeMul;

    totalMul = 1;
""",
        "MR08N type-chart locals",
    )

    replace_once(
        lib,
        """    movePower = MOVE_DATA(move).power;

    if ((battleCtx->battleStatusMask & SYSCTL_IGNORE_TYPE_CHECKS) == FALSE && MON_HAS_TYPE(attacker, moveType)) {
""",
        """    movePower = MOVE_DATA(move).power;

    // Primordial Sea and Desolate Land make damaging moves of the opposing
    // element fail completely while their strong weather is active.
    if (NO_CLOUD_NINE && movePower) {
        if ((Mercury_StrongWeatherType(battleCtx)
                == MERCURY_STRONG_WEATHER_RAIN
                && moveType == TYPE_FIRE)
            || (Mercury_StrongWeatherType(battleCtx)
                == MERCURY_STRONG_WEATHER_SUN
                && moveType == TYPE_WATER)) {
            *moveStatusMask |= MOVE_STATUS_INEFFECTIVE;
            return 0;
        }
    }

    if ((battleCtx->battleStatusMask & SYSCTL_IGNORE_TYPE_CHECKS) == FALSE && MON_HAS_TYPE(attacker, moveType)) {
""",
        "MR08N primal weather move failure",
    )

    replace_once(
        lib,
        """        } else {
            damage = damage * 15 / 10;
        }
    }

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_LEVITATE) == TRUE
""",
        """        } else {
            damage = damage * 15 / 10;
        }
    }

    preTypeDamage = damage;

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_LEVITATE) == TRUE
""",
        "MR08N pre-type damage capture",
    )

    old = """                    damage = ApplyTypeMultiplier(battleCtx, attacker, sTypeMatchupMultipliers[chartEntry][2], damage, movePower, moveStatusMask);

                    if (sTypeMatchupMultipliers[chartEntry][2] == TYPE_MULTI_SUPER_EFF) {
                        totalMul *= 2;
                    }
"""
    new = """                    typeMul = sTypeMatchupMultipliers[chartEntry][2];
                    if (NO_CLOUD_NINE
                        && Mercury_StrongWeatherType(battleCtx)
                            == MERCURY_STRONG_WEATHER_DELTA
                        && sTypeMatchupMultipliers[chartEntry][1] == TYPE_FLYING
                        && typeMul == TYPE_MULTI_SUPER_EFF) {
                        typeMul = 10;
                    }

                    damage = ApplyTypeMultiplier(
                        battleCtx,
                        attacker,
                        typeMul,
                        damage,
                        movePower,
                        moveStatusMask);

                    if (typeMul == TYPE_MULTI_SUPER_EFF) {
                        totalMul *= 2;
                    }
"""
    text = lib.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 2:
        raise SystemExit(
            f"MR08N Delta Stream type multipliers: expected 2 matches, found {count}"
        )
    lib.write_text(text.replace(old, new), encoding="utf-8")

    insert_before_once(
        lib,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WONDER_GUARD) == TRUE
""",
        """    // At full HP Tera Shell forces any otherwise damaging,
    // non-immune hit to exactly one not-very-effective multiplier. Rebuild
    // from the post-STAB/pre-type value so dual weaknesses do not leak through.
    if (movePower
        && DEFENDING_MON.curHP == DEFENDING_MON.maxHP
        && (*moveStatusMask & MOVE_STATUS_IMMUNE) == FALSE
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_TERA_SHELL) == TRUE) {
        damage = BattleSystem_Divide(
            preTypeDamage * TYPE_MULTI_NOT_VERY_EFF, 10);
        *moveStatusMask &= ~MOVE_STATUS_SUPER_EFFECTIVE;
        *moveStatusMask &= ~MOVE_STATUS_INEFFECTIVE;
        *moveStatusMask |= MOVE_STATUS_NOT_VERY_EFFECTIVE;
    }

""",
        "MR08N Tera Shell effectiveness override",
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
    common = (root / "include/battle/common.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "strong_weather_state":
            "mercuryStrongWeatherType" in ctx
            and "mercuryStrongWeatherSource" in ctx,
        "strong_weather_macros":
            "MERCURY_STRONG_WEATHER_RAIN" in common
            and "Mercury_StrongWeatherType(battleCtx)" in common,
        "primordial_sea_hook":
            "case ABILITY_PRIMORDIAL_SEA:" in lib
            and "moveType == TYPE_FIRE" in lib,
        "desolate_land_hook":
            "case ABILITY_DESOLATE_LAND:" in lib
            and "moveType == TYPE_WATER" in lib,
        "delta_stream_hook":
            "case ABILITY_DELTA_STREAM:" in lib
            and "sTypeMatchupMultipliers[chartEntry][1] == TYPE_FLYING" in lib,
        "neutralizing_gas_hook":
            "Mercury_NeutralizingGasRawActive" in lib
            and "ABILITY_NEUTRALIZING_GAS" in lib
            and "Mercury_AbilityCannotBeNeutralized" in lib,
        "ordinary_weather_lock":
            "Primal weather and Delta Stream cannot be replaced" in script,
        "tera_shell_hook":
            "ABILITY_TERA_SHELL" in lib
            and "preTypeDamage * TYPE_MULTI_NOT_VERY_EFF" in lib,
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
        default=Path("mr08n-canonical-ability-weather-suppression-shell.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context_and_weather_macros(root)
    patch_ability_suppression_and_weather_helpers(root)
    patch_strong_weather_switch_in(root)
    patch_weather_change_lock(root)
    patch_type_chart(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08N_CANONICAL_ABILITY_WEATHER_SUPPRESSION_SHELL",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 153,
        "remaining_modern_canonical_mechanics": 34,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08N validation failed")


if __name__ == "__main__":
    main()
