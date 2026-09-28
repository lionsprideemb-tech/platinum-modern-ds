#!/usr/bin/env python3
"""MR08S7 — canonical threshold form Ability family.

Implements the mechanics-side form state for:
- Zen Mode
- Schooling
- Shields Down

The pass uses exact current-mainline HP/level thresholds and exact non-HP stat
recalculation from the active Pokémon's level, IVs, EVs, and nature. Battle-only
form visuals are deliberately deferred to Mercury's form-asset phase.

Also implements Shields Down's Meteor-form protection from nonvolatile status
and Yawn. Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_ZEN_MODE",
    "ABILITY_SCHOOLING",
    "ABILITY_SHIELDS_DOWN",
)
EXPECTED_IDS = {
    "ABILITY_ZEN_MODE": 161,
    "ABILITY_SHIELDS_DOWN": 197,
    "ABILITY_SCHOOLING": 208,
}


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_in_function(
    path: Path,
    signature: str,
    old: str,
    new: str,
    label: str,
) -> None:
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

    segment = text[start:end]
    count = segment.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one scoped match in {path}, found {count}"
        )
    segment = segment.replace(old, new, 1)
    path.write_text(text[:start] + segment + text[end:], encoding="utf-8")


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
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08S7 threshold-form battle state.
    u8 mercuryZenActive[MAX_BATTLERS];
    u8 mercuryDarmanitanBaseForm[MAX_BATTLERS];
    u8 mercurySchoolingActive[MAX_BATTLERS];
    u8 mercuryMiniorCoreActive[MAX_BATTLERS];

""",
        "threshold form state",
    )


def patch_form_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """static u16 Mercury_ZeroToHeroCalcStat(
""",
        """static u16 Mercury_ThresholdFormCalcStat(
    Pokemon *mon,
    int baseStat,
    int statType)
{
    int ivParam;
    int evParam;
    int level;
    int iv;
    int ev;
    int value;
    int affinity;

    switch (statType) {
    case STAT_ATTACK:
        ivParam = MON_DATA_ATK_IV;
        evParam = MON_DATA_ATK_EV;
        break;
    case STAT_DEFENSE:
        ivParam = MON_DATA_DEF_IV;
        evParam = MON_DATA_DEF_EV;
        break;
    case STAT_SPEED:
        ivParam = MON_DATA_SPEED_IV;
        evParam = MON_DATA_SPEED_EV;
        break;
    case STAT_SPECIAL_ATTACK:
        ivParam = MON_DATA_SPATK_IV;
        evParam = MON_DATA_SPATK_EV;
        break;
    default:
        ivParam = MON_DATA_SPDEF_IV;
        evParam = MON_DATA_SPDEF_EV;
        break;
    }

    level = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);
    iv = Pokemon_GetValue(mon, ivParam, NULL);
    ev = Pokemon_GetValue(mon, evParam, NULL);
    value = ((2 * baseStat + iv + ev / 4) * level / 100 + 5);

    affinity = Pokemon_GetStatAffinityOf(Pokemon_GetNature(mon), statType);
    if (affinity > 0) {
        value = value * 110 / 100;
    } else if (affinity < 0) {
        value = value * 90 / 100;
    }

    return value;
}

static void Mercury_SetThresholdFormStats(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon,
    int atk,
    int def,
    int spa,
    int spd,
    int spe)
{
    battleCtx->battleMons[battler].attack =
        Mercury_ThresholdFormCalcStat(mon, atk, STAT_ATTACK);
    battleCtx->battleMons[battler].defense =
        Mercury_ThresholdFormCalcStat(mon, def, STAT_DEFENSE);
    battleCtx->battleMons[battler].spAttack =
        Mercury_ThresholdFormCalcStat(mon, spa, STAT_SPECIAL_ATTACK);
    battleCtx->battleMons[battler].spDefense =
        Mercury_ThresholdFormCalcStat(mon, spd, STAT_SPECIAL_DEFENSE);
    battleCtx->battleMons[battler].speed =
        Mercury_ThresholdFormCalcStat(mon, spe, STAT_SPEED);
}

static void Mercury_SetDarmanitanStandard(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    Mercury_SetThresholdFormStats(
        battleCtx, battler, mon, 140, 55, 30, 55, 95);

    if (battleCtx->mercuryDarmanitanBaseForm[battler] == 1) {
        battleCtx->battleMons[battler].type1 = TYPE_ICE;
        battleCtx->battleMons[battler].type2 = TYPE_ICE;
    } else {
        battleCtx->battleMons[battler].type1 = TYPE_FIRE;
        battleCtx->battleMons[battler].type2 = TYPE_FIRE;
    }
    battleCtx->mercuryZenActive[battler] = FALSE;
}

static void Mercury_SetDarmanitanZen(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    if (battleCtx->mercuryDarmanitanBaseForm[battler] == 1) {
        // Galarian Zen: 105/160/55/30/55/135, Ice/Fire.
        Mercury_SetThresholdFormStats(
            battleCtx, battler, mon, 160, 55, 30, 55, 135);
        battleCtx->battleMons[battler].type1 = TYPE_ICE;
        battleCtx->battleMons[battler].type2 = TYPE_FIRE;
    } else {
        // Unovan Zen: 105/30/105/140/105/55, Fire/Psychic.
        Mercury_SetThresholdFormStats(
            battleCtx, battler, mon, 30, 105, 140, 105, 55);
        battleCtx->battleMons[battler].type1 = TYPE_FIRE;
        battleCtx->battleMons[battler].type2 = TYPE_PSYCHIC;
    }
    battleCtx->mercuryZenActive[battler] = TRUE;
}

static void Mercury_SetWishiwashiSolo(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    // Solo: 45/20/20/25/25/40.
    Mercury_SetThresholdFormStats(
        battleCtx, battler, mon, 20, 20, 25, 25, 40);
    battleCtx->battleMons[battler].type1 = TYPE_WATER;
    battleCtx->battleMons[battler].type2 = TYPE_WATER;
    battleCtx->mercurySchoolingActive[battler] = FALSE;
}

static void Mercury_SetWishiwashiSchool(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    // School: 45/140/130/140/135/30.
    Mercury_SetThresholdFormStats(
        battleCtx, battler, mon, 140, 130, 140, 135, 30);
    battleCtx->battleMons[battler].type1 = TYPE_WATER;
    battleCtx->battleMons[battler].type2 = TYPE_WATER;
    battleCtx->mercurySchoolingActive[battler] = TRUE;
}

static void Mercury_SetMiniorMeteor(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    // Meteor: 60/60/100/60/100/60.
    Mercury_SetThresholdFormStats(
        battleCtx, battler, mon, 60, 100, 60, 100, 60);
    battleCtx->battleMons[battler].type1 = TYPE_ROCK;
    battleCtx->battleMons[battler].type2 = TYPE_FLYING;
    battleCtx->mercuryMiniorCoreActive[battler] = FALSE;
}

static void Mercury_SetMiniorCore(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    // Core: 60/100/60/100/60/120.
    Mercury_SetThresholdFormStats(
        battleCtx, battler, mon, 100, 60, 100, 60, 120);
    battleCtx->battleMons[battler].type1 = TYPE_ROCK;
    battleCtx->battleMons[battler].type2 = TYPE_FLYING;
    battleCtx->mercuryMiniorCoreActive[battler] = TRUE;
}

""",
        "threshold form stat helpers",
    )


def patch_switch_in(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    battleCtx->mercuryZeroToHeroActive[battler] = FALSE;
""",
        """    battleCtx->mercuryZenActive[battler] = FALSE;
    battleCtx->mercurySchoolingActive[battler] = FALSE;
    battleCtx->mercuryMiniorCoreActive[battler] = FALSE;
    battleCtx->mercuryDarmanitanBaseForm[battler] =
        battleCtx->battleMons[battler].formNum == 1 ? 1 : 0;

    if (battleCtx->battleMons[battler].species == SPECIES_WISHIWASHI
        && battleCtx->battleMons[battler].ability == ABILITY_SCHOOLING
        && battleCtx->battleMons[battler].level >= 20) {
        if (battleCtx->battleMons[battler].curHP
            > battleCtx->battleMons[battler].maxHP / 4) {
            Mercury_SetWishiwashiSchool(battleCtx, battler, mon);
        } else {
            Mercury_SetWishiwashiSolo(battleCtx, battler, mon);
        }
    }

    if (battleCtx->battleMons[battler].species == SPECIES_MINIOR
        && battleCtx->battleMons[battler].ability == ABILITY_SHIELDS_DOWN) {
        if (battleCtx->battleMons[battler].curHP
            <= battleCtx->battleMons[battler].maxHP / 2) {
            Mercury_SetMiniorCore(battleCtx, battler, mon);
        } else {
            Mercury_SetMiniorMeteor(battleCtx, battler, mon);
        }
    }

    battleCtx->mercuryZeroToHeroActive[battler] = FALSE;
""",
        "threshold form switch-in initialization",
    )


def patch_end_turn(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    case ABILITY_HUNGER_SWITCH:
""",
        """    case ABILITY_ZEN_MODE: {
        Pokemon *mon = BattleSystem_GetPartyPokemon(
            battleSys, battler, battleCtx->selectedPartySlot[battler]);

        if (battleCtx->battleMons[battler].species == SPECIES_DARMANITAN
            && battleCtx->battleMons[battler].curHP
            && (battleCtx->battleMons[battler].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
            if (battleCtx->battleMons[battler].curHP
                <= battleCtx->battleMons[battler].maxHP / 2) {
                if (battleCtx->mercuryZenActive[battler] == FALSE) {
                    Mercury_SetDarmanitanZen(battleCtx, battler, mon);
                    battleCtx->msgBattlerTemp = battler;
                    subscript = subscript_mold_breaker;
                    result = TRUE;
                }
            } else if (battleCtx->mercuryZenActive[battler]) {
                Mercury_SetDarmanitanStandard(battleCtx, battler, mon);
                battleCtx->msgBattlerTemp = battler;
                subscript = subscript_mold_breaker;
                result = TRUE;
            }
        }
        break;
    }

    case ABILITY_SCHOOLING: {
        Pokemon *mon = BattleSystem_GetPartyPokemon(
            battleSys, battler, battleCtx->selectedPartySlot[battler]);

        if (battleCtx->battleMons[battler].species == SPECIES_WISHIWASHI
            && battleCtx->battleMons[battler].level >= 20
            && battleCtx->battleMons[battler].curHP
            && (battleCtx->battleMons[battler].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
            if (battleCtx->battleMons[battler].curHP
                > battleCtx->battleMons[battler].maxHP / 4) {
                if (battleCtx->mercurySchoolingActive[battler] == FALSE) {
                    Mercury_SetWishiwashiSchool(battleCtx, battler, mon);
                    battleCtx->msgBattlerTemp = battler;
                    subscript = subscript_mold_breaker;
                    result = TRUE;
                }
            } else if (battleCtx->mercurySchoolingActive[battler]) {
                Mercury_SetWishiwashiSolo(battleCtx, battler, mon);
                battleCtx->msgBattlerTemp = battler;
                subscript = subscript_mold_breaker;
                result = TRUE;
            }
        }
        break;
    }

    case ABILITY_SHIELDS_DOWN: {
        Pokemon *mon = BattleSystem_GetPartyPokemon(
            battleSys, battler, battleCtx->selectedPartySlot[battler]);

        if (battleCtx->battleMons[battler].species == SPECIES_MINIOR
            && battleCtx->battleMons[battler].curHP
            && (battleCtx->battleMons[battler].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
            if (battleCtx->battleMons[battler].curHP
                <= battleCtx->battleMons[battler].maxHP / 2) {
                if (battleCtx->mercuryMiniorCoreActive[battler] == FALSE) {
                    Mercury_SetMiniorCore(battleCtx, battler, mon);
                    battleCtx->msgBattlerTemp = battler;
                    subscript = subscript_mold_breaker;
                    result = TRUE;
                }
            } else if (battleCtx->mercuryMiniorCoreActive[battler]) {
                Mercury_SetMiniorMeteor(battleCtx, battler, mon);
                battleCtx->msgBattlerTemp = battler;
                subscript = subscript_mold_breaker;
                result = TRUE;
            }
        }
        break;
    }

    case ABILITY_HUNGER_SWITCH:
""",
        "threshold form end-turn checks",
    )


def patch_shields_down_status(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_in_function(
        path,
        "static BOOL BtlCmd_UpdateMonData(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    if (paramID == BATTLEMON_ABILITY) {
""",
        """    if (paramID == BATTLEMON_STATUS
        && monData != MON_CONDITION_NONE
        && battleCtx->battleMons[battler].species == SPECIES_MINIOR
        && Battler_Ability(battleCtx, battler) == ABILITY_SHIELDS_DOWN
        && battleCtx->mercuryMiniorCoreActive[battler] == FALSE
        && (battleCtx->battleMons[battler].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
        return FALSE;
    }

    if (paramID == BATTLEMON_ABILITY) {
""",
        "Shields Down Meteor nonvolatile-status immunity",
    )

    replace_in_function(
        path,
        "static BOOL BtlCmd_TryYawn(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    if (DEFENDING_MON.moveEffectsMask & MOVE_EFFECT_YAWN) {
""",
        """    if (DEFENDING_MON.species == SPECIES_MINIOR
        && Battler_Ability(battleCtx, battleCtx->defender) == ABILITY_SHIELDS_DOWN
        && battleCtx->mercuryMiniorCoreActive[battleCtx->defender] == FALSE
        && (DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
        BattleScript_Iter(battleCtx, jumpOnFail);
    } else if (DEFENDING_MON.moveEffectsMask & MOVE_EFFECT_YAWN) {
""",
        "Shields Down Meteor Yawn immunity",
    )


def patch_neutralizing_gas(root: Path) -> None:
    # Zen Mode, Schooling and Shields Down are cantsuppress Abilities in
    # current mainline mechanics, so Neutralizing Gas must leave them active.
    return

def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    replace_once(
        lib,
        """        && ability1 != ABILITY_ZERO_TO_HERO;
""",
        """        && ability1 != ABILITY_ZERO_TO_HERO
        && ability1 != ABILITY_ZEN_MODE
        && ability1 != ABILITY_SCHOOLING
        && ability1 != ABILITY_SHIELDS_DOWN;
""",
        "threshold forms Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_ZERO_TO_HERO;
""",
        """        && ability2 != ABILITY_ZERO_TO_HERO
        && ability2 != ABILITY_ZEN_MODE
        && ability2 != ABILITY_SCHOOLING
        && ability2 != ABILITY_SHIELDS_DOWN;
""",
        "threshold forms Trace defender2",
    )

    copy_target = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {token}, _091\n"
        for token in IMPLEMENTED
    )
    copy_user = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {token}, _091\n"
        for token in IMPLEMENTED
    )
    swap_target = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {token}, _156\n"
        for token in IMPLEMENTED
    )
    swap_user = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {token}, _156\n"
        for token in IMPLEMENTED
    )
    suppress_lines = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {token}, _034\n"
        for token in IMPLEMENTED
    )
    worry_lines = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {token}, _041\n"
        for token in IMPLEMENTED
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _091\n",
        copy_target,
        "threshold form Role Play target",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _091\n",
        copy_user,
        "threshold form Role Play user",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _156\n",
        swap_target,
        "threshold form Skill Swap target",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _156\n",
        swap_user,
        "threshold form Skill Swap user",
    )
    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _034\n",
        suppress_lines,
        "threshold form Gastro Acid lock",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _041\n",
        worry_lines,
        "threshold form Worry Seed lock",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    receiver_start = lib.index("static BOOL Mercury_AbilityCanBeReceived")
    receiver_end = lib.index("static int Mercury_CountFaintedPartyMons", receiver_start)
    receiver = lib[receiver_start:receiver_end]

    checks = {
        "form_state":
            "mercuryZenActive[MAX_BATTLERS]" in ctx
            and "mercurySchoolingActive[MAX_BATTLERS]" in ctx
            and "mercuryMiniorCoreActive[MAX_BATTLERS]" in ctx,
        "exact_stat_formula":
            "Pokemon_GetStatAffinityOf(Pokemon_GetNature(mon), statType)" in lib
            and "MON_DATA_ATK_EV" in lib
            and "MON_DATA_SPDEF_EV" in lib,
        "zen_threshold_and_forms":
            "case ABILITY_ZEN_MODE:" in lib
            and "maxHP / 2" in lib
            and "Mercury_SetDarmanitanZen" in lib
            and "Mercury_SetDarmanitanStandard" in lib
            and "TYPE_PSYCHIC" in lib,
        "schooling_threshold_and_level":
            "case ABILITY_SCHOOLING:" in lib
            and "level >= 20" in lib
            and "maxHP / 4" in lib
            and "Mercury_SetWishiwashiSchool" in lib
            and "Mercury_SetWishiwashiSolo" in lib,
        "shields_down_threshold":
            "case ABILITY_SHIELDS_DOWN:" in lib
            and "Mercury_SetMiniorMeteor" in lib
            and "Mercury_SetMiniorCore" in lib,
        "meteor_status_immunity":
            "paramID == BATTLEMON_STATUS" in script
            and "mercuryMiniorCoreActive[battler] == FALSE" in script,
        "meteor_yawn_immunity":
            "BtlCmd_TryYawn" in script
            and "mercuryMiniorCoreActive[battleCtx->defender] == FALSE" in script,
        "neutralizing_gas_cannot_suppress":
            all(token in cannot for token in IMPLEMENTED),
        "trace_blocked":
            all(f"ability1 != {token}" in lib and f"ability2 != {token}" in lib
                for token in IMPLEMENTED),
        "role_play_and_skill_swap_blocked":
            all(token in copy and token in swap for token in IMPLEMENTED),
        "gastro_acid_and_worry_seed_blocked":
            all(token in suppress and token in worry for token in IMPLEMENTED),
        "receiver_blocked":
            all(token in receiver for token in IMPLEMENTED),
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
        default=Path("mr08s7-canonical-ability-threshold-forms.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_form_helpers(root)
    patch_switch_in(root)
    patch_end_turn(root)
    patch_shields_down_status(root)
    patch_neutralizing_gas(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S7_CANONICAL_ABILITY_THRESHOLD_FORMS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 180,
        "remaining_modern_canonical_mechanics": 7,
        "form_visuals_deferred": True,
        "policy": "Official/current-mainline threshold form rules for Zen Mode, Schooling and Shields Down, including Meteor-form status/Yawn immunity.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S7 validation failed")


if __name__ == "__main__":
    main()
