#!/usr/bin/env python3
"""MR08S11 — canonical Illusion battle presentation pass.

Implements current-mainline Illusion without altering the disguised battler's
real battle stats, typing, moves, HP, item, or Ability:
- on entry, an Illusion user copies the last conscious non-Egg party member's
  visible species/form/gender/shininess/personality/nickname;
- battle send-out, sprite-refresh, HP-gauge gender, encounter, and nickname-tag
  presentation use that apparent party member while Illusion is active;
- direct damaging hits break Illusion, but hits absorbed by Substitute do not;
- Neutralizing Gas, Gastro Acid, Worry Seed, or other Ability loss breaks the
  active presentation;
- Transform/Imposter cannot copy a target while its Illusion is active;
- switching out resets the state and a later entry selects a fresh disguise;
- Trace, Role Play, Skill Swap, Receiver and Power of Alchemy cannot acquire
  Illusion. Illusion itself remains suppressible, matching current mechanics.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_ILLUSION",)
EXPECTED_IDS = {"ABILITY_ILLUSION": 149}


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
        """    // Mercury MR08S11: apparent party slot used by Illusion.
    u8 mercuryIllusionActive[MAX_BATTLERS];
    u8 mercuryIllusionPartySlot[MAX_BATTLERS];

""",
        "Illusion state",
    )


def patch_subscript_and_text(root: Path) -> None:
    text_path = root / "res/text/battle_strings.json"
    data = json.loads(text_path.read_text(encoding="utf-8"))
    messages = data["messages"]
    if not any(m.get("id") == "BattleStrings_Text_MercuryIllusionWoreOff" for m in messages):
        messages.append({
            "id": "BattleStrings_Text_MercuryIllusionWoreOff",
            "en_US": [
                "{STRVAR_1 1, 0, 0}’s Illusion\n",
                "wore off!"
            ],
        })
        text_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_illusion_faded.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    SetMosaic BTLSCR_MSG_TEMP, 8, 1
    Wait
    RefreshSprite BTLSCR_MSG_TEMP
    SetMosaic BTLSCR_MSG_TEMP, 0, 1
    Wait
    PrintMessage BattleStrings_Text_MercuryIllusionWoreOff, TAG_NICKNAME, BTLSCR_MSG_TEMP
    Wait
    WaitButtonABTime 30
    End
""",
        encoding="utf-8",
    )

    insert_before_once(
        scripts / "sub_seq.order",
        "subscript_giratina_form_change\n",
        "subscript_mercury_illusion_faded\n",
        "Illusion subscript order",
    )
    insert_before_once(
        scripts / "meson.build",
        "    'subscript_giratina_form_change.s',\n",
        "    'subscript_mercury_illusion_faded.s',\n",
        "Illusion subscript build list",
    )


def patch_battle_lib(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    header = root / "include/battle/battle_lib.h"

    insert_before_once(
        header,
        """int BattleSystem_NicknameTag(BattleContext *battleSys, int battler);
""",
        """BOOL Mercury_TryBreakIllusionByAbilityLoss(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);

""",
        "Illusion public helper",
    )

    insert_before_once(
        path,
        """void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)
""",
        """static int Mercury_FindIllusionPartySlot(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int partySlot)
{
    int partyCount = BattleSystem_GetPartyCount(battleSys, battler);
    int chosen = partySlot;
    int i;

    for (i = 0; i < partyCount; i++) {
        Pokemon *candidate;

        if (i == partySlot) {
            continue;
        }

        candidate = BattleSystem_GetPartyPokemon(battleSys, battler, i);
        if (Pokemon_GetValue(candidate, MON_DATA_SPECIES_OR_EGG, NULL)
                != SPECIES_NONE
            && Pokemon_GetValue(candidate, MON_DATA_SPECIES_OR_EGG, NULL)
                != SPECIES_EGG
            && Pokemon_GetValue(candidate, MON_DATA_IS_EGG, NULL) == FALSE
            && Pokemon_GetValue(candidate, MON_DATA_HP, NULL) != 0) {
            chosen = i;
        }
    }

    return chosen;
}

BOOL Mercury_TryBreakIllusionByAbilityLoss(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int *subscript)
{
    int battler;

    for (battler = 0; battler < BattleSystem_GetMaxBattlers(battleSys); battler++) {
        if (battleCtx->mercuryIllusionActive[battler]
            && Battler_Ability(battleCtx, battler) != ABILITY_ILLUSION) {
            battleCtx->mercuryIllusionActive[battler] = FALSE;
            battleCtx->mercuryIllusionPartySlot[battler] = MAX_PARTY_SIZE;
            battleCtx->msgBattlerTemp = battler;
            *subscript = subscript_mercury_illusion_faded;
            return TRUE;
        }
    }

    return FALSE;
}

""",
        "Illusion battle helpers",
    )

    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    battleCtx->mercuryGulpMissileForm[battler] = 0;
""",
        """    battleCtx->mercuryIllusionActive[battler] = FALSE;
    battleCtx->mercuryIllusionPartySlot[battler] = MAX_PARTY_SIZE;

    if (Battler_Ability(battleCtx, battler) == ABILITY_ILLUSION
        && (battleCtx->battleMons[battler].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
        int illusionSlot = Mercury_FindIllusionPartySlot(
            battleSys, battleCtx, battler, partySlot);

        if (illusionSlot != partySlot) {
            battleCtx->mercuryIllusionActive[battler] = TRUE;
            battleCtx->mercuryIllusionPartySlot[battler] = illusionSlot;
        }
    }

    battleCtx->mercuryGulpMissileForm[battler] = 0;
""",
        "Illusion entry setup",
    )

    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)",
        """    switch (Battler_Ability(battleCtx, battleCtx->defender)) {
""",
        """    if (battleCtx->mercuryIllusionActive[battleCtx->defender]
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
        battleCtx->mercuryIllusionActive[battleCtx->defender] = FALSE;
        battleCtx->mercuryIllusionPartySlot[battleCtx->defender] =
            MAX_PARTY_SIZE;
        battleCtx->msgBattlerTemp = battleCtx->defender;
        *subscript = subscript_mercury_illusion_faded;
        return TRUE;
    }

    switch (Battler_Ability(battleCtx, battleCtx->defender)) {
""",
        "Illusion damaging-hit break",
    )

    replace_once(
        path,
        """int BattleSystem_NicknameTag(BattleContext *battleSys, int battler)
{
    return battler | (battleSys->selectedPartySlot[battler] << 8);
}
""",
        """int BattleSystem_NicknameTag(BattleContext *battleSys, int battler)
{
    int partySlot = battleSys->selectedPartySlot[battler];

    if (battleSys->mercuryIllusionActive[battler]
        && Battler_Ability(battleSys, battler) == ABILITY_ILLUSION
        && battleSys->mercuryIllusionPartySlot[battler] < MAX_PARTY_SIZE) {
        partySlot = battleSys->mercuryIllusionPartySlot[battler];
    }

    return battler | (partySlot << 8);
}
""",
        "Illusion nickname tags",
    )

    # Trace cannot select an Illusion user.
    replace_once(
        path,
        """        && ability1 != ABILITY_RKS_SYSTEM;
""",
        """        && ability1 != ABILITY_RKS_SYSTEM
        && ability1 != ABILITY_ILLUSION;
""",
        "Illusion Trace defender1",
    )
    replace_once(
        path,
        """        && ability2 != ABILITY_RKS_SYSTEM;
""",
        """        && ability2 != ABILITY_RKS_SYSTEM
        && ability2 != ABILITY_ILLUSION;
""",
        "Illusion Trace defender2",
    )

    # Imposter also cannot copy a target while Illusion is active.
    replace_once(
        path,
        """                    || battleCtx->battleMons[target].ability
                        == ABILITY_GULP_MISSILE) {
""",
        """                    || battleCtx->battleMons[target].ability
                        == ABILITY_GULP_MISSILE
                    || battleCtx->mercuryIllusionActive[target]) {
""",
        "Illusion Imposter target lock",
    )


def patch_controller_presentation(root: Path) -> None:
    path = root / "src/battle/battle_controller.c"

    helper = """static Pokemon *Mercury_IllusionDisplayMon(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int slot;

    if (battler < 0 || battler >= BattleSystem_GetMaxBattlers(battleSys)
        || battleCtx->mercuryIllusionActive[battler] == FALSE
        || Battler_Ability(battleCtx, battler) != ABILITY_ILLUSION) {
        return NULL;
    }

    slot = battleCtx->mercuryIllusionPartySlot[battler];
    if (slot >= BattleSystem_GetPartyCount(battleSys, battler)) {
        return NULL;
    }

    return BattleSystem_GetPartyPokemon(battleSys, battler, slot);
}

"""
    insert_before_once(
        path,
        """void BattleController_EmitSetEncounter(BattleSystem *battleSys, int battler)
""",
        helper,
        "Illusion controller display helper",
    )

    for signature in (
        "void BattleController_EmitSetEncounter(BattleSystem *battleSys, int battler)",
        "void BattleController_EmitShowEncounter(BattleSystem *battleSys, int battler)",
    ):
        replace_in_function(
            path,
            signature,
            """    int i;

""",
            """    int i;
    Pokemon *illusion = Mercury_IllusionDisplayMon(
        battleSys, battleSys->battleCtx, battler);

""",
            f"{signature} Illusion local",
        )
        replace_in_function(
            path,
            signature,
            """    message.gender = battleSys->battleCtx->battleMons[battler].gender;
    message.isShiny = battleSys->battleCtx->battleMons[battler].isShiny;
    message.species = battleSys->battleCtx->battleMons[battler].species;
    message.personality = battleSys->battleCtx->battleMons[battler].personality;
""",
            """    message.gender = illusion
        ? Pokemon_GetGender(illusion)
        : battleSys->battleCtx->battleMons[battler].gender;
    message.isShiny = illusion
        ? Pokemon_IsShiny(illusion)
        : battleSys->battleCtx->battleMons[battler].isShiny;
    message.species = illusion
        ? Pokemon_GetValue(illusion, MON_DATA_SPECIES, NULL)
        : battleSys->battleCtx->battleMons[battler].species;
    message.personality = illusion
        ? Pokemon_GetValue(illusion, MON_DATA_PERSONALITY, NULL)
        : battleSys->battleCtx->battleMons[battler].personality;
""",
            f"{signature} Illusion identity",
        )
        replace_in_function(
            path,
            signature,
            """    message.formNum = battleSys->battleCtx->battleMons[battler].formNum;
""",
            """    message.formNum = illusion
        ? Pokemon_GetValue(illusion, MON_DATA_FORM, NULL)
        : battleSys->battleCtx->battleMons[battler].formNum;
""",
            f"{signature} Illusion form",
        )
        replace_in_function(
            path,
            signature,
            """    BattleMon_Get(battleSys->battleCtx, battler, BATTLEMON_NICKNAME, &message.nickname);
""",
            """    if (illusion) {
        Pokemon_GetValue(illusion, MON_DATA_NICKNAME, &message.nickname);
    } else {
        BattleMon_Get(
            battleSys->battleCtx, battler, BATTLEMON_NICKNAME,
            &message.nickname);
    }
""",
            f"{signature} Illusion nickname",
        )

    signature = "void BattleController_EmitShowPokemon(BattleSystem *battleSys, int battler, int capturedBall, int quickSendOut)"
    replace_in_function(
        path, signature,
        """    int i;

    message.command = BATTLE_COMMAND_SHOW_POKEMON;
""",
        """    int i;
    Pokemon *illusion = Mercury_IllusionDisplayMon(
        battleSys, battleSys->battleCtx, battler);

    message.command = BATTLE_COMMAND_SHOW_POKEMON;
""",
        "ShowPokemon Illusion local",
    )
    replace_in_function(
        path, signature,
        """    if (battleSys->battleCtx->battleMons[battler].statusVolatile & VOLATILE_CONDITION_TRANSFORM) {
""",
        """    if (illusion) {
        message.gender = Pokemon_GetGender(illusion);
        message.personality =
            Pokemon_GetValue(illusion, MON_DATA_PERSONALITY, NULL);
    } else if (battleSys->battleCtx->battleMons[battler].statusVolatile & VOLATILE_CONDITION_TRANSFORM) {
""",
        "ShowPokemon Illusion identity branch",
    )
    replace_in_function(
        path, signature,
        """    message.isShiny = battleSys->battleCtx->battleMons[battler].isShiny;
    message.species = battleSys->battleCtx->battleMons[battler].species;
""",
        """    message.isShiny = illusion
        ? Pokemon_IsShiny(illusion)
        : battleSys->battleCtx->battleMons[battler].isShiny;
    message.species = illusion
        ? Pokemon_GetValue(illusion, MON_DATA_SPECIES, NULL)
        : battleSys->battleCtx->battleMons[battler].species;
""",
        "ShowPokemon Illusion species",
    )
    replace_in_function(
        path, signature,
        """    message.formNum = battleSys->battleCtx->battleMons[battler].formNum;
""",
        """    message.formNum = illusion
        ? Pokemon_GetValue(illusion, MON_DATA_FORM, NULL)
        : battleSys->battleCtx->battleMons[battler].formNum;
""",
        "ShowPokemon Illusion form",
    )
    replace_in_function(
        path, signature,
        """    BattleMon_Get(battleSys->battleCtx, battler, BATTLEMON_NICKNAME, &message.nickname);
""",
        """    if (illusion) {
        Pokemon_GetValue(illusion, MON_DATA_NICKNAME, &message.nickname);
    } else {
        BattleMon_Get(
            battleSys->battleCtx, battler, BATTLEMON_NICKNAME,
            &message.nickname);
    }
""",
        "ShowPokemon Illusion nickname",
    )
    replace_in_function(
        path, signature,
        """        message.battleMonSpecies[i] = battleSys->battleCtx->battleMons[i].species;
        message.battleMonIsShiny[i] = battleSys->battleCtx->battleMons[i].isShiny;
        message.battleMonFormNums[i] = battleSys->battleCtx->battleMons[i].formNum;
""",
        """        Pokemon *shown = Mercury_IllusionDisplayMon(
            battleSys, battleSys->battleCtx, i);
        message.battleMonSpecies[i] = shown
            ? Pokemon_GetValue(shown, MON_DATA_SPECIES, NULL)
            : battleSys->battleCtx->battleMons[i].species;
        message.battleMonIsShiny[i] = shown
            ? Pokemon_IsShiny(shown)
            : battleSys->battleCtx->battleMons[i].isShiny;
        message.battleMonFormNums[i] = shown
            ? Pokemon_GetValue(shown, MON_DATA_FORM, NULL)
            : battleSys->battleCtx->battleMons[i].formNum;
""",
        "ShowPokemon Illusion battle array",
    )
    replace_in_function(
        path, signature,
        """        if (battleSys->battleCtx->battleMons[i].statusVolatile & VOLATILE_CONDITION_TRANSFORM) {
""",
        """        if (shown) {
            message.battleMonGenders[i] = Pokemon_GetGender(shown);
            message.battleMonPersonalities[i] =
                Pokemon_GetValue(shown, MON_DATA_PERSONALITY, NULL);
        } else if (battleSys->battleCtx->battleMons[i].statusVolatile & VOLATILE_CONDITION_TRANSFORM) {
""",
        "ShowPokemon Illusion battle identity array",
    )

    signature = "void BattleController_EmitRefreshSprite(BattleSystem *battleSys, BattleContext *battleCtx, int battler)"
    replace_in_function(
        path, signature,
        """        animation.species[i] = battleCtx->battleMons[i].species;
        animation.isShiny[i] = battleCtx->battleMons[i].isShiny;
        animation.formNums[i] = battleCtx->battleMons[i].formNum;

        if (battleCtx->battleMons[i].statusVolatile & VOLATILE_CONDITION_TRANSFORM) {
""",
        """        Pokemon *shown = Mercury_IllusionDisplayMon(
            battleSys, battleCtx, i);
        animation.species[i] = shown
            ? Pokemon_GetValue(shown, MON_DATA_SPECIES, NULL)
            : battleCtx->battleMons[i].species;
        animation.isShiny[i] = shown
            ? Pokemon_IsShiny(shown)
            : battleCtx->battleMons[i].isShiny;
        animation.formNums[i] = shown
            ? Pokemon_GetValue(shown, MON_DATA_FORM, NULL)
            : battleCtx->battleMons[i].formNum;

        if (shown) {
            animation.genders[i] = Pokemon_GetGender(shown);
            animation.personalities[i] =
                Pokemon_GetValue(shown, MON_DATA_PERSONALITY, NULL);
        } else if (battleCtx->battleMons[i].statusVolatile & VOLATILE_CONDITION_TRANSFORM) {
""",
        "RefreshSprite Illusion apparent identity",
    )

    signature = "void BattleController_EmitSendOutMessage(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)"
    replace_in_function(
        path, signature,
        """    message.partySlot = partySlot;
""",
        """    message.partySlot =
        (battleCtx->mercuryIllusionActive[battler]
            && Battler_Ability(battleCtx, battler) == ABILITY_ILLUSION
            && battleCtx->mercuryIllusionPartySlot[battler] < MAX_PARTY_SIZE)
        ? battleCtx->mercuryIllusionPartySlot[battler]
        : partySlot;
""",
        "SendOutMessage Illusion nickname slot",
    )

    signature = "void BattleController_EmitLeadMonMessage(BattleSystem *battleSys, BattleContext *battleCtx, int battler)"
    replace_in_function(
        path, signature,
        """        message.partySlot[i] = battleCtx->selectedPartySlot[i];
""",
        """        message.partySlot[i] =
            (battleCtx->mercuryIllusionActive[i]
                && Battler_Ability(battleCtx, i) == ABILITY_ILLUSION
                && battleCtx->mercuryIllusionPartySlot[i] < MAX_PARTY_SIZE)
            ? battleCtx->mercuryIllusionPartySlot[i]
            : battleCtx->selectedPartySlot[i];
""",
        "LeadMonMessage Illusion nickname slot",
    )


def patch_controller_break_check(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    replace_in_function(
        path,
        "static void BattleControllerPlayer_AfterMoveEffects(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    default:
        Mercury_TryLoadGulpMissile(battleSys, battleCtx);
        break;
""",
        """    default: {
        int illusionSeq;

        if (Mercury_TryBreakIllusionByAbilityLoss(
                battleSys, battleCtx, &illusionSeq)) {
            LOAD_SUBSEQ(illusionSeq);
            battleCtx->commandNext = battleCtx->command;
            battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
            return;
        }

        Mercury_TryLoadGulpMissile(battleSys, battleCtx);
        break;
    }
""",
        "Illusion suppression/loss break",
    )


def patch_transform_and_special_rules(root: Path) -> None:
    script = root / "src/battle/battle_script.c"
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"

    replace_in_function(
        script,
        "static BOOL BtlCmd_Transform(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    BattleScript_Iter(battleCtx, 1);

    ATTACKING_MON.statusVolatile |= VOLATILE_CONDITION_TRANSFORM;
""",
        """    BattleScript_Iter(battleCtx, 1);

    if (battleCtx->mercuryIllusionActive[battleCtx->defender]
        && Battler_Ability(battleCtx, battleCtx->defender)
            == ABILITY_ILLUSION) {
        battleCtx->moveStatusFlags |= MOVE_STATUS_FAILED;
        return FALSE;
    }

    ATTACKING_MON.statusVolatile |= VOLATILE_CONDITION_TRANSFORM;
""",
        "Transform active Illusion failure",
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _091\n",
        "Illusion Role Play target",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _091\n",
        "Illusion Role Play user",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _156\n",
        "Illusion Skill Swap target",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _156\n",
        "Illusion Skill Swap user",
    )

    # Receiver exclusion already exists in the MR08K helper. Keep Illusion
    # suppressible: do not add it to the cantsuppress helper or Worry/Gastro
    # failure scripts.
    if "case ABILITY_ILLUSION:" not in lib[lib.index("static BOOL Mercury_AbilityCanBeReceived"):lib.index("static int Mercury_CountFaintedPartyMons")]:
        raise SystemExit("Illusion Receiver exclusion unexpectedly missing")


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
    ctl = (root / "src/battle/battle_controller.c").read_text(encoding="utf-8")
    player = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
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
        "illusion_state":
            "mercuryIllusionActive[MAX_BATTLERS]" in ctx
            and "mercuryIllusionPartySlot[MAX_BATTLERS]" in ctx,
        "last_conscious_party_selection":
            "Mercury_FindIllusionPartySlot" in lib
            and "MON_DATA_IS_EGG" in lib
            and "MON_DATA_HP" in lib,
        "presentation_only":
            "Mercury_IllusionDisplayMon" in ctl
            and "MON_DATA_SPECIES" in ctl
            and "MON_DATA_NICKNAME" in ctl,
        "nickname_tags":
            "mercuryIllusionPartySlot[battler]" in lib
            and "int BattleSystem_NicknameTag" in lib,
        "damaging_hit_break":
            "mercuryIllusionActive[battleCtx->defender]" in lib
            and "physicalDamageTaken" in lib
            and "subscript_mercury_illusion_faded" in lib,
        "substitute_does_not_break":
            "Battler_SubstituteWasHit" in lib,
        "suppression_break":
            "Mercury_TryBreakIllusionByAbilityLoss" in player,
        "transform_imposter_block":
            "mercuryIllusionActive[battleCtx->defender]" in script
            and "mercuryIllusionActive[target]" in lib,
        "suppressible":
            "ABILITY_ILLUSION" not in cannot
            and "ABILITY_ILLUSION" not in suppress
            and "ABILITY_ILLUSION" not in worry,
        "trace_blocked":
            "ability1 != ABILITY_ILLUSION" in lib
            and "ability2 != ABILITY_ILLUSION" in lib,
        "roleplay_skillswap_blocked":
            "ABILITY_ILLUSION" in copy
            and "ABILITY_ILLUSION" in swap,
        "receiver_blocked":
            "ABILITY_ILLUSION" in receiver,
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
        default=Path("mr08s11-canonical-ability-illusion.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_subscript_and_text(root)
    patch_battle_lib(root)
    patch_controller_presentation(root)
    patch_controller_break_check(root)
    patch_transform_and_special_rules(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S11_CANONICAL_ABILITY_ILLUSION",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 184,
        "remaining_modern_canonical_mechanics": 3,
        "policy": "Current-mainline Illusion apparent-party presentation, damaging-hit break, suppressibility, and special copy restrictions.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S11 validation failed")


if __name__ == "__main__":
    main()
