#!/usr/bin/env python3
"""MR08S10 — canonical Gulp Missile battle-state pass.

Implements current-mainline Cramorant / Gulp Missile mechanics:
- successful Surf damage arms Gulping (> 50% HP) or Gorging (<= 50%);
- the successful first turn of Dive arms the same state immediately;
- a damaging hit on an armed Cramorant fires the prey even if Cramorant faints;
- no projectile fires while Cramorant itself is still semi-invulnerable;
- the attacker loses 1/4 max HP unless protected by Magic Guard;
- Gulping lowers the surviving attacker's Defense by one stage;
- Gorging attempts to paralyze the surviving attacker;
- Cramorant returns to normal after firing and when it switches out;
- transformed users can possess Gulp Missile but cannot arm its prey state;
- current Gen IX rules allow Role Play, Trace, Skill Swap, Wandering Spirit
  and Receiver to acquire Gulp Missile;
- Gastro Acid and Worry Seed fail, Mummy/Lingering Aroma cannot overwrite it,
  and Neutralizing Gas cannot suppress it.

Gulping / Gorging sprite presentation is deferred to Mercury's later form-asset
phase. Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_GULP_MISSILE",)
EXPECTED_IDS = {"ABILITY_GULP_MISSILE": 241}


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
        """    // Mercury MR08S10: 0 normal, 1 Gulping/Arrokuda, 2 Gorging/Pikachu.
    u8 mercuryGulpMissileState[MAX_BATTLERS];

""",
        "Gulp Missile battle state",
    )


def patch_subscript(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"

    (scripts / "subscript_mercury_gulp_missile.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_DEFENDER, BTLSCR_DEFENDER
    Wait
    WaitButtonABTime 15

    // Magic Guard leaves HP_CALC_TEMP at zero; the secondary effect still runs.
    CompareVarToValue OPCODE_EQU, BTLVAR_HP_CALC_TEMP, 0, _Survived
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_SKIP_SPRITE_BLINK
    Call BATTLE_SUBSCRIPT_UPDATE_HP

    // Showdown/current-mainline behavior applies the secondary only if the
    // attacker survived the projectile.
    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_CUR_HP, 0, _End

_Survived:
    Call BATTLE_SUBSCRIPT_PUSH_ATTACKER_AND_DEFENDER
    // Attribute the stat/status effect to Cramorant rather than to the attacker.
    UpdateVarFromVar OPCODE_SET, BTLVAR_ATTACKER, BTLVAR_DEFENDER
    CompareVarToValue OPCODE_EQU, BTLVAR_CALC_TEMP, 1, _Arrokuda

    // Pikachu: Electric types cannot be paralyzed in modern mechanics.
    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_1, TYPE_ELECTRIC, _Restore
    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_TYPE_2, TYPE_ELECTRIC, _Restore
    Call BATTLE_SUBSCRIPT_PARALYZE
    GoTo _Restore

_Arrokuda:
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE

_Restore:
    Call BATTLE_SUBSCRIPT_POP_ATTACKER_AND_DEFENDER

_End:
    End
""",
        encoding="utf-8",
    )

    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_ice_face_restore\n",
        "subscript_mercury_gulp_missile\n",
        "Gulp Missile subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_ice_face_restore.s',\n",
        "    'subscript_mercury_gulp_missile.s',\n",
        "Gulp Missile subscript build list",
    )


def patch_switch_reset_and_reaction(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    battleCtx->mercuryPowerConstructActive[battler] = FALSE;
""",
        """    battleCtx->mercuryGulpMissileState[battler] = 0;
    battleCtx->mercuryPowerConstructActive[battler] = FALSE;
""",
        "Gulp Missile switch reset",
    )

    # Surf must actually hit/damage a target. This is intentionally before the
    # defender-substitute early return: damage to a target's Substitute still
    # counts as a successful Surf for Cramorant's form change.
    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)",
        """    if (Battler_SubstituteWasHit(battleCtx, battleCtx->defender) == TRUE) {
        return result;
    }

""",
        """    if (battleCtx->moveCur == MOVE_SURF
        && ATTACKING_MON.species == SPECIES_CRAMORANT
        && Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_GULP_MISSILE
        && battleCtx->mercuryGulpMissileState[battleCtx->attacker] == 0
        && (ATTACKING_MON.statusVolatile
            & VOLATILE_CONDITION_TRANSFORM) == FALSE
        && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
        && ((DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            || Battler_SubstituteWasHit(
                battleCtx, battleCtx->defender) == TRUE)) {
        battleCtx->mercuryGulpMissileState[battleCtx->attacker] =
            ATTACKING_MON.curHP <= ATTACKING_MON.maxHP / 2 ? 2 : 1;
    }

    if (Battler_SubstituteWasHit(battleCtx, battleCtx->defender) == TRUE) {
        return result;
    }

""",
        "Gulp Missile Surf arm",
    )

    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)",
        """    switch (Battler_Ability(battleCtx, battleCtx->defender)) {
    case ABILITY_STATIC:
""",
        """    switch (Battler_Ability(battleCtx, battleCtx->defender)) {
    case ABILITY_GULP_MISSILE: {
        int gulpState =
            battleCtx->mercuryGulpMissileState[battleCtx->defender];

        if (DEFENDING_MON.species == SPECIES_CRAMORANT
            && gulpState
            && ATTACKING_MON.curHP
            && (DEFENDING_MON.moveEffectsMask
                & MOVE_EFFECT_SEMI_INVULNERABLE) == FALSE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            // Spitting the prey always returns Cramorant to its base state,
            // including when the incoming hit also knocked Cramorant out.
            battleCtx->mercuryGulpMissileState[battleCtx->defender] = 0;
            battleCtx->calcTemp = gulpState;
            battleCtx->msgBattlerTemp = battleCtx->attacker;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;

            if (gulpState == 1) {
                battleCtx->sideEffectParam =
                    MOVE_SUBSCRIPT_PTR_DEFENSE_DOWN_1_STAGE;
            }

            if (Battler_Ability(
                    battleCtx, battleCtx->attacker) == ABILITY_MAGIC_GUARD) {
                battleCtx->hpCalcTemp = 0;
            } else {
                battleCtx->hpCalcTemp =
                    BattleSystem_Divide(ATTACKING_MON.maxHP * -1, 4);
            }

            *subscript = subscript_mercury_gulp_missile;
            result = TRUE;
        }
        break;
    }

    case ABILITY_STATIC:
""",
        "Gulp Missile retaliation",
    )


def patch_dive_arm_and_substitute_rule(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_in_function(
        path,
        "static BOOL BtlCmd_UpdateMonData(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    BattleMon_Set(battleCtx, battler, paramID, &monData);
    BattleMon_CopyToParty(battleSys, battleCtx, battler);

""",
        """    BattleMon_Set(battleCtx, battler, paramID, &monData);

    // Dive catches prey on the successful first turn as soon as the
    // underwater state is installed. This also covers charge-skipping items.
    if (op == OPCODE_FLAG_ON
        && paramID == BATTLEMON_MOVE_EFFECTS_MASK
        && (srcVal & MOVE_EFFECT_UNDERWATER)
        && battler == battleCtx->attacker
        && battleCtx->moveCur == MOVE_DIVE
        && battleCtx->battleMons[battler].species == SPECIES_CRAMORANT
        && Battler_Ability(battleCtx, battler) == ABILITY_GULP_MISSILE
        && battleCtx->mercuryGulpMissileState[battler] == 0
        && (battleCtx->battleMons[battler].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
        battleCtx->mercuryGulpMissileState[battler] =
            battleCtx->battleMons[battler].curHP
                <= battleCtx->battleMons[battler].maxHP / 2
            ? 2
            : 1;
    }

    BattleMon_CopyToParty(battleSys, battleCtx, battler);

""",
        "Gulp Missile Dive arm",
    )

    # The projectile bypasses the attacker's Substitute. Preserve normal
    # Substitute behavior for every other Ability/stat-stage source.
    replace_in_function(
        path,
        "static BOOL BtlCmd_ChangeStatStage(BattleSystem *battleSys, BattleContext *battleCtx)",
        """                } else if (battleCtx->battleMons[battleCtx->sideEffectMon].statusVolatile & VOLATILE_CONDITION_SUBSTITUTE) {
                    result = 2;
                }
""",
        """                } else if ((battleCtx->battleMons[battleCtx->sideEffectMon].statusVolatile
                        & VOLATILE_CONDITION_SUBSTITUTE)
                    && !(battleCtx->sideEffectType == SIDE_EFFECT_TYPE_ABILITY
                        && Battler_Ability(
                            battleCtx, battleCtx->attacker)
                            == ABILITY_GULP_MISSILE
                        && battleCtx->sideEffectParam
                            == MOVE_SUBSCRIPT_PTR_DEFENSE_DOWN_1_STAGE)) {
                    result = 2;
                }
""",
        "Gulp Missile projectile bypasses attacker Substitute",
    )


def patch_gen9_interactions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    # Scarlet/Violet 3.0+: Receiver and Wandering Spirit can acquire/swap Gulp
    # Missile. Mummy and Lingering Aroma remain blocked by their older helper.
    replace_in_function(
        lib,
        "static BOOL Mercury_AbilityCanBeReceived(int ability)",
        """    case ABILITY_GULP_MISSILE:
""",
        "",
        "Gulp Missile Receiver Gen IX allowance",
    )

    insert_before_once(
        lib,
        """static int Mercury_CountFaintedPartyMons(
""",
        """static BOOL Mercury_AbilityCanSwapWithWanderingSpirit(int ability)
{
    if (ability == ABILITY_GULP_MISSILE) {
        return TRUE;
    }

    return Mercury_AbilityCanBeOverwrittenByMummy(ability);
}

""",
        "Gulp Missile Wandering Spirit helper",
    )

    replace_once(
        lib,
        """            && Mercury_AbilityCanBeOverwrittenByMummy(
                Battler_Ability(battleCtx, battleCtx->attacker))
            && Mercury_AbilityCanBeOverwrittenByMummy(
                Battler_Ability(battleCtx, battleCtx->defender))) {
""",
        """            && Mercury_AbilityCanSwapWithWanderingSpirit(
                Battler_Ability(battleCtx, battleCtx->attacker))
            && Mercury_AbilityCanSwapWithWanderingSpirit(
                Battler_Ability(battleCtx, battleCtx->defender))) {
""",
        "Gulp Missile Wandering Spirit Gen IX allowance",
    )

    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_GULP_MISSILE, _034\n",
        "Gulp Missile Gastro Acid lock",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_GULP_MISSILE, _041\n",
        "Gulp Missile Worry Seed lock",
    )

    # Deliberately do not add Gulp Missile to Trace or Skill Swap exclusions.
    _ = swap


def update_registry(path: Path) -> None:
    rows = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    sub = (root / "res/battle/scripts/subscripts/subscript_mercury_gulp_missile.s").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    receiver_start = lib.index("static BOOL Mercury_AbilityCanBeReceived")
    receiver_end = lib.index("static BOOL Mercury_AbilityCanSwapWithWanderingSpirit", receiver_start)
    receiver = lib[receiver_start:receiver_end]

    mummy_start = lib.index("static BOOL Mercury_AbilityCanBeOverwrittenByMummy")
    mummy_end = lib.index("static BOOL Mercury_AbilityCanSwapWithWanderingSpirit", mummy_start)
    mummy = lib[mummy_start:mummy_end]

    checks = {
        "battle_state":
            "mercuryGulpMissileState[MAX_BATTLERS]" in ctx,
        "switch_resets_state":
            "mercuryGulpMissileState[battler] = 0;" in lib,
        "surf_requires_successful_hit":
            "battleCtx->moveCur == MOVE_SURF" in lib
            and "DEFENDER_SELF_TURN_FLAGS.specialDamageTaken" in lib
            and "Battler_SubstituteWasHit" in lib,
        "dive_first_turn_arm":
            "battleCtx->moveCur == MOVE_DIVE" in script
            and "MOVE_EFFECT_UNDERWATER" in script
            and "mercuryGulpMissileState[battler]" in script,
        "half_hp_form_selection":
            "<= battleCtx->battleMons[battler].maxHP / 2" in script
            and "ATTACKING_MON.curHP <= ATTACKING_MON.maxHP / 2" in lib,
        "semi_invulnerable_does_not_spit":
            "DEFENDING_MON.moveEffectsMask" in lib
            and "MOVE_EFFECT_SEMI_INVULNERABLE" in lib,
        "quarter_hp_retaliation":
            "ATTACKING_MON.maxHP * -1, 4" in lib
            and "subscript_mercury_gulp_missile" in lib,
        "magic_guard_damage_immunity":
            "ABILITY_MAGIC_GUARD" in lib
            and "battleCtx->hpCalcTemp = 0;" in lib,
        "gulping_defense_drop":
            "MOVE_SUBSCRIPT_PTR_DEFENSE_DOWN_1_STAGE" in lib
            and "BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE" in sub,
        "gorging_paralysis":
            "BATTLE_SUBSCRIPT_PARALYZE" in sub
            and sub.count("TYPE_ELECTRIC") >= 2,
        "projectile_bypasses_attacker_substitute":
            "ABILITY_GULP_MISSILE" in script
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_DOWN_1_STAGE" in script,
        "transformed_user_cannot_arm":
            "VOLATILE_CONDITION_TRANSFORM" in lib
            and "VOLATILE_CONDITION_TRANSFORM" in script,
        "subscript_registered":
            "subscript_mercury_gulp_missile" in order,
        "neutralizing_gas_cannot_suppress":
            "ABILITY_GULP_MISSILE" in cannot,
        "gastro_and_worry_seed_fail":
            "ABILITY_GULP_MISSILE" in suppress
            and "ABILITY_GULP_MISSILE" in worry,
        "role_play_allowed_gen9":
            "ABILITY_GULP_MISSILE" not in
                (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8"),
        "trace_allowed_gen9":
            "ability1 != ABILITY_GULP_MISSILE" not in lib
            and "ability2 != ABILITY_GULP_MISSILE" not in lib,
        "skill_swap_allowed_gen9":
            "ABILITY_GULP_MISSILE" not in swap,
        "receiver_allowed_gen9":
            "ABILITY_GULP_MISSILE" not in receiver,
        "wandering_spirit_allowed_gen9":
            "Mercury_AbilityCanSwapWithWanderingSpirit" in lib
            and "ability == ABILITY_GULP_MISSILE" in lib,
        "mummy_lingering_aroma_blocked":
            "ABILITY_GULP_MISSILE" in mummy,
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
        default=Path("mr08s10-canonical-ability-gulp-missile.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_subscript(root)
    patch_switch_reset_and_reaction(root)
    patch_dive_arm_and_substitute_rule(root)
    patch_gen9_interactions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S10_CANONICAL_ABILITY_GULP_MISSILE",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 183,
        "remaining_modern_canonical_mechanics": 4,
        "form_visuals_deferred": True,
        "policy": "Current Gen IX Gulp Missile: successful Surf / first-turn Dive prey state, quarter-max-HP retaliation, Arrokuda Defense drop / Pikachu paralysis, plus post-3.0 Role Play/Trace/Skill Swap/Receiver rules.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S10 validation failed")


if __name__ == "__main__":
    main()
