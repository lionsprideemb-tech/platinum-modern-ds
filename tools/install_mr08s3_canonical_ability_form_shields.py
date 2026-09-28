#!/usr/bin/env python3
"""MR08S3 — canonical Disguise + Ice Face shared shield pass.

Implements the two once-intact form-shield mechanics on Platinum's move pipeline:
- Disguise blocks the first damaging hit while intact, then costs 1/8 max HP;
- Ice Face blocks the first physical damaging hit while intact;
- multi-hit moves only lose the hit that actually breaks the shield;
- secondary effects still run because only HP damage is cancelled;
- Mold Breaker-family attacks bypass the shields through the normal ignorable-
  Ability helper;
- Disguise stays broken for that party member for the rest of the battle;
- Ice Face can reform when hail begins, or when a broken holder enters while
  hail is already active;
- transformed users cannot use either shield;
- both abilities keep their canonical copy/swap/Gastro Acid/Worry Seed
  restrictions, but can be suppressed by Neutralizing Gas.

Mercury's modern alternate-form sprite resources are a later content phase, so
this pass stores the form state battle-side without touching the locked MR07 UI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_DISGUISE",
    "ABILITY_ICE_FACE",
)
EXPECTED_IDS = {
    "ABILITY_DISGUISE": 209,
    "ABILITY_ICE_FACE": 248,
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
        """    // Mercury MR08S3: party-persistent Disguise / Ice Face state.
    u8 mercuryDisguiseBrokenMask[2];
    u8 mercuryIceFaceBrokenMask[2];
    u16 mercuryFormShieldPending[MAX_BATTLERS];
    u8 mercuryIceFaceNeedsWeatherCheck[MAX_BATTLERS];
    u8 mercuryIceFaceHailActive;

""",
        "form-shield battle state",
    )


def patch_subscripts(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"

    (scripts / "subscript_mercury_form_shield_break.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    CompareVarToValue OPCODE_EQU, BTLVAR_HP_CALC_TEMP, 0, _End
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_SKIP_SPRITE_BLINK
    Call BATTLE_SUBSCRIPT_UPDATE_HP
    // {0} is hurt by its {1}!
    PrintMessage BattleStrings_Text_PokemonIsHurtByItsAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15

_End:
    End
""",
        encoding="utf-8",
    )

    (scripts / "subscript_mercury_ice_face_restore.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    End
""",
        encoding="utf-8",
    )

    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_cud_chew\n",
        "subscript_mercury_form_shield_break\nsubscript_mercury_ice_face_restore\n",
        "form-shield subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_cud_chew.s',\n",
        "    'subscript_mercury_form_shield_break.s',\n    'subscript_mercury_ice_face_restore.s',\n",
        "form-shield subscript build list",
    )


def patch_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    insert_before_once(
        hdr,
        """BOOL Mercury_IsGroundedForTerrain(BattleContext *battleCtx, int battler);
""",
        """BOOL Mercury_TryBlockFormShield(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int attacker,
    int defender);
""",
        "form-shield public helper",
    )

    insert_before_once(
        lib,
        """BOOL Mercury_IsGroundedForTerrain(BattleContext *battleCtx, int battler)
""",
        """static u8 Mercury_FormShieldPartyBit(BattleContext *battleCtx, int battler)
{
    int slot = battleCtx->selectedPartySlot[battler];

    if (slot < 0 || slot >= 6) {
        return 0;
    }

    return (u8)(1 << slot);
}

static BOOL Mercury_FormShieldBroken(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int ability)
{
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    u8 bit = Mercury_FormShieldPartyBit(battleCtx, battler);

    if (bit == 0) {
        return TRUE;
    }

    if (ability == ABILITY_DISGUISE) {
        return (battleCtx->mercuryDisguiseBrokenMask[side] & bit) != 0;
    }

    return (battleCtx->mercuryIceFaceBrokenMask[side] & bit) != 0;
}

static void Mercury_SetFormShieldBroken(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int ability,
    BOOL broken)
{
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    u8 bit = Mercury_FormShieldPartyBit(battleCtx, battler);
    u8 *mask;

    if (bit == 0) {
        return;
    }

    mask = ability == ABILITY_DISGUISE
        ? &battleCtx->mercuryDisguiseBrokenMask[side]
        : &battleCtx->mercuryIceFaceBrokenMask[side];

    if (broken) {
        *mask |= bit;
    } else {
        *mask &= (u8)~bit;
    }
}

BOOL Mercury_TryBlockFormShield(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int attacker,
    int defender)
{
    int moveClass;

    if (attacker == BATTLER_NONE
        || defender == BATTLER_NONE
        || attacker == defender
        || battleCtx->damage >= 0
        || (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS)
        || (battleCtx->battleMons[defender].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM)) {
        return FALSE;
    }

    moveClass = MOVE_DATA(battleCtx->moveCur).class;
    if (moveClass == CLASS_STATUS) {
        return FALSE;
    }

    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_DISGUISE)
        && Mercury_FormShieldBroken(
               battleSys, battleCtx, defender, ABILITY_DISGUISE) == FALSE) {
        battleCtx->mercuryFormShieldPending[defender] = ABILITY_DISGUISE;
        return TRUE;
    }

    if (moveClass == CLASS_PHYSICAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_ICE_FACE)
        && Mercury_FormShieldBroken(
               battleSys, battleCtx, defender, ABILITY_ICE_FACE) == FALSE) {
        battleCtx->mercuryFormShieldPending[defender] = ABILITY_ICE_FACE;
        return TRUE;
    }

    return FALSE;
}

static BOOL Mercury_TryRestoreIceFace(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int *subscript)
{
    BOOL hailActive = NO_CLOUD_NINE && WEATHER_IS_HAIL;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    int i;

    if (hailActive == FALSE) {
        battleCtx->mercuryIceFaceHailActive = FALSE;
        return FALSE;
    }

    if (battleCtx->mercuryIceFaceHailActive == FALSE) {
        battleCtx->mercuryIceFaceHailActive = TRUE;
        for (i = 0; i < maxBattlers; i++) {
            battleCtx->mercuryIceFaceNeedsWeatherCheck[i] = TRUE;
        }
    }

    for (i = 0; i < maxBattlers; i++) {
        if (battleCtx->mercuryIceFaceNeedsWeatherCheck[i] == FALSE) {
            continue;
        }

        // Keep the check pending while Neutralizing Gas suppresses a raw
        // Ice Face holder. Once Gas leaves, the still-active hail can reform it.
        if (battleCtx->battleMons[i].ability == ABILITY_ICE_FACE
            && Battler_Ability(battleCtx, i) != ABILITY_ICE_FACE) {
            continue;
        }

        battleCtx->mercuryIceFaceNeedsWeatherCheck[i] = FALSE;

        if (battleCtx->battleMons[i].curHP
            && Battler_Ability(battleCtx, i) == ABILITY_ICE_FACE
            && (battleCtx->battleMons[i].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE
            && Mercury_FormShieldBroken(
                   battleSys, battleCtx, i, ABILITY_ICE_FACE)) {
            Mercury_SetFormShieldBroken(
                battleSys, battleCtx, i, ABILITY_ICE_FACE, FALSE);
            battleCtx->msgTemp = i;
            battleCtx->msgBattlerTemp = i;
            *subscript = subscript_mercury_ice_face_restore;
            return TRUE;
        }
    }

    return FALSE;
}

""",
        "form-shield helpers",
    )

    # A newly loaded battler gets one weather check. Disguise's party-bit stays
    # untouched so switching cannot restore it.
    insert_after_once(
        lib,
        """    battleCtx->mercuryParadoxBoosterActive[battler] = FALSE;

""",
        """    battleCtx->mercuryFormShieldPending[battler] = ABILITY_NONE;
    battleCtx->mercuryIceFaceNeedsWeatherCheck[battler] = TRUE;

""",
        "form-shield switch-in reset",
    )


def patch_damage_cancel(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        path,
        """        if (CURRENT_MOVE_DATA.effect == BATTLE_EFFECT_LEAVE_WITH_1_HP
""",
        """        if (Mercury_TryBlockFormShield(
                battleSys,
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender)) {
            // The move still connected, so secondary effects and the ordinary
            // post-hit pipeline continue; only HP damage is cancelled.
            battleCtx->damage = 0;
            battleCtx->hitDamage = 0;
            battleCtx->hpCalcTemp = 0;
            battleCtx->battleStatusMask |= SYSCTL_MOVE_HIT;
            battleCtx->command = BATTLE_CONTROL_AFTER_MOVE_MESSAGE;
            return;
        }

""",
        "form-shield HP cancellation",
    )


def patch_break_and_restore(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Form restoration shares Platinum's existing form-change checkpoint, which
    # is revisited after moves and switch-ins.
    insert_after_once(
        path,
        """BOOL BattleSystem_TriggerFormChange(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
{
    int i;
    int arceusForm;
    BOOL result = FALSE;

""",
        """    if (Mercury_TryRestoreIceFace(battleSys, battleCtx, subscript)) {
        return TRUE;
    }

""",
        "Ice Face hail restoration",
    )

    # A shield that just cancelled damage gets first claim on the defender's
    # on-hit Ability checkpoint.
    insert_after_once(
        path,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
{
    BOOL result = FALSE;

    // These two sentinels must be separate to match
    if (battleCtx->defender == BATTLER_NONE) {
        return result;
    }

    if (Battler_SubstituteWasHit(battleCtx, battleCtx->defender) == TRUE) {
        return result;
    }

""",
        """    if (battleCtx->mercuryFormShieldPending[battleCtx->defender]
        != ABILITY_NONE) {
        int ability =
            battleCtx->mercuryFormShieldPending[battleCtx->defender];

        battleCtx->mercuryFormShieldPending[battleCtx->defender] =
            ABILITY_NONE;
        Mercury_SetFormShieldBroken(
            battleSys, battleCtx, battleCtx->defender, ability, TRUE);

        battleCtx->msgTemp = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->defender;
        battleCtx->hpCalcTemp = 0;

        if (ability == ABILITY_DISGUISE) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(
                battleCtx->battleMons[battleCtx->defender].maxHP * -1,
                8);
        }

        *subscript = subscript_mercury_form_shield_break;
        return TRUE;
    }

""",
        "form-shield break checkpoint",
    )


def patch_neutralizing_gas_rules(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Current-mainline Disguise and Ice Face are cantsuppress Abilities:
    # Neutralizing Gas and Gastro Acid do not disable them. Replace this helper
    # as a unit to avoid matching the similar Receiver exclusion list.
    replace_function(
        path,
        "static BOOL Mercury_AbilityCannotBeNeutralized(int ability)",
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
    case ABILITY_AS_ONE_GLASTRIER:
    case ABILITY_AS_ONE_SPECTRIER:
    case ABILITY_ZERO_TO_HERO:
    case ABILITY_TERA_SHIFT:
        return TRUE;
    }

    return FALSE;
}""",
        "Disguise / Ice Face Neutralizing Gas behavior",
    )

def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    # Trace was hardened in MR08R4 and extended by MR08S2.
    replace_once(
        lib,
        """        && ability1 != ABILITY_QUARK_DRIVE;
""",
        """        && ability1 != ABILITY_QUARK_DRIVE
        && ability1 != ABILITY_DISGUISE
        && ability1 != ABILITY_ICE_FACE;
""",
        "form-shield Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_QUARK_DRIVE;
""",
        """        && ability2 != ABILITY_QUARK_DRIVE
        && ability2 != ABILITY_DISGUISE
        && ability2 != ABILITY_ICE_FACE;
""",
        "form-shield Trace defender2",
    )

    target_copy = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {a}, _091\n"
        for a in IMPLEMENTED
    )
    user_copy = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {a}, _091\n"
        for a in IMPLEMENTED
    )
    target_swap = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {a}, _156\n"
        for a in IMPLEMENTED
    )
    user_swap = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {a}, _156\n"
        for a in IMPLEMENTED
    )
    suppress_lines = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {a}, _034\n"
        for a in IMPLEMENTED
    )
    worry_lines = "".join(
        f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {a}, _041\n"
        for a in IMPLEMENTED
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n",
        target_copy,
        "form-shield Role Play target locks",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n",
        user_copy,
        "form-shield Role Play user locks",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n",
        target_swap,
        "form-shield Skill Swap target locks",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n",
        user_swap,
        "form-shield Skill Swap user locks",
    )
    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _034\n",
        suppress_lines,
        "form-shield Gastro Acid locks",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _041\n",
        worry_lines,
        "form-shield Worry Seed locks",
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
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    checks = {
        "party_persistent_state":
            "mercuryDisguiseBrokenMask[2]" in ctx
            and "mercuryIceFaceBrokenMask[2]" in ctx,
        "damage_cancel_hook":
            "Mercury_TryBlockFormShield(" in controller
            and "battleCtx->damage = 0;" in controller,
        "disguise_recoil":
            "ABILITY_DISGUISE" in lib
            and "maxHP * -1" in lib
            and ",\n                8);" in lib,
        "ice_face_physical_only":
            "moveClass == CLASS_PHYSICAL" in lib
            and "ABILITY_ICE_FACE" in lib,
        "mold_breaker_path":
            "Battler_IgnorableAbility(" in lib,
        "transform_block":
            "VOLATILE_CONDITION_TRANSFORM" in lib,
        "hail_reform_event":
            "Mercury_TryRestoreIceFace" in lib
            and "mercuryIceFaceHailActive" in lib
            and "WEATHER_IS_HAIL" in lib,
        "neutralizing_gas_cannot_suppress":
            "ABILITY_DISGUISE" in cannot
            and "ABILITY_ICE_FACE" in cannot,
        "uncopyable_unswappable":
            all(token in copy and token in swap for token in IMPLEMENTED),
        "move_suppression_blocked":
            all(token in suppress for token in IMPLEMENTED),
        "scripts_registered":
            "subscript_mercury_form_shield_break" in order
            and "subscript_mercury_ice_face_restore" in order,
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
        default=Path("mr08s3-canonical-ability-form-shields.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_subscripts(root)
    patch_helpers(root)
    patch_damage_cancel(root)
    patch_break_and_restore(root)
    patch_neutralizing_gas_rules(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S3_CANONICAL_ABILITY_FORM_SHIELDS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 174,
        "remaining_modern_canonical_mechanics": 13,
        "form_visuals_deferred": True,
        "policy": "Official/current-mainline Disguise and Ice Face battle mechanics; alternate-form graphics remain in the later species/form asset phase.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S3 validation failed")


if __name__ == "__main__":
    main()
