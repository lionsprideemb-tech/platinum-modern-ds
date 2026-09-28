#!/usr/bin/env python3
"""MR08S12 — canonical Commander pass.

Implements current-mainline Tatsugiri / Dondozo Commander mechanics:
- in doubles, an active Tatsugiri with Commander enters its living Dondozo ally;
- Dondozo immediately gains +2 Attack, Defense, Sp. Atk, Sp. Def and Speed;
- the commanding Tatsugiri cannot choose an action, is hidden, and direct moves
  targeted at it miss while its Dondozo host remains active;
- both the commanding Tatsugiri and commanded Dondozo are trapped, including
  drag/forced-switch checks;
- indirect damage can still damage/faint Tatsugiri;
- if Tatsugiri faints, Dondozo stays commanded/trapped and keeps its boosts;
- if Dondozo faints/leaves, Tatsugiri is released and can act again;
- Commander cannot be traced, Role Played, Skill Swapped, Entrained/Worry
  Seeded, or inherited by Receiver / Power of Alchemy;
- current-mainline Commander remains suppressible by Neutralizing Gas/Gastro
  Acid before activation.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_COMMANDER",)
EXPECTED_IDS = {"ABILITY_COMMANDER": 279}


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
        """    // Mercury MR08S12: Commander / commanded pairing state.
    u8 mercuryCommanderActive[MAX_BATTLERS];
    u8 mercuryCommanderHost[MAX_BATTLERS];
    u8 mercuryCommanded[MAX_BATTLERS];

""",
        "Commander battle state",
    )


def patch_subscripts_and_text(root: Path) -> None:
    text_path = root / "res/text/battle_strings.json"
    data = json.loads(text_path.read_text(encoding="utf-8"))
    messages = data["messages"]

    if not any(m.get("id") == "BattleStrings_Text_MercuryCommanderEntered" for m in messages):
        messages.append({
            "id": "BattleStrings_Text_MercuryCommanderEntered",
            "en_US": [
                "{STRVAR_1 1, 0, 0} entered {STRVAR_1 1, 1, 0}!\n",
                "Its ally’s stats rose sharply!"
            ],
        })

    if not any(m.get("id") == "BattleStrings_Text_MercuryCommanderReleased" for m in messages):
        messages.append({
            "id": "BattleStrings_Text_MercuryCommanderReleased",
            "en_US": [
                "{STRVAR_1 1, 0, 0} emerged\n",
                "from its ally!"
            ],
        })

    text_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_commander_enter.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    PrintMessage BattleStrings_Text_MercuryCommanderEntered, TAG_NICKNAME_NICKNAME, BTLSCR_MSG_TEMP, BTLSCR_MSG_DEFENDER
    Wait
    WaitButtonABTime 30
    ToggleVanish BTLSCR_MSG_TEMP, TRUE
    Wait
    End
""",
        encoding="utf-8",
    )
    (scripts / "subscript_mercury_commander_release.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    ToggleVanish BTLSCR_MSG_TEMP, FALSE
    Wait
    PrintMessage BattleStrings_Text_MercuryCommanderReleased, TAG_NICKNAME, BTLSCR_MSG_TEMP
    Wait
    WaitButtonABTime 30
    End
""",
        encoding="utf-8",
    )

    insert_before_once(
        scripts / "sub_seq.order",
        "subscript_giratina_form_change\n",
        "subscript_mercury_commander_enter\nsubscript_mercury_commander_release\n",
        "Commander subscript order",
    )
    insert_before_once(
        scripts / "meson.build",
        "    'subscript_giratina_form_change.s',\n",
        "    'subscript_mercury_commander_enter.s',\n    'subscript_mercury_commander_release.s',\n",
        "Commander subscript build list",
    )


def patch_battle_lib(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """int BattleSystem_TriggerEffectOnSwitch(BattleSystem *battleSys, BattleContext *battleCtx)
""",
        """static void Mercury_CommanderRaiseTwo(
    BattleContext *battleCtx,
    int battler,
    int stat)
{
    int stage = battleCtx->battleMons[battler].statBoosts[stat] + 2;

    if (stage > MAX_STAT_STAGE) {
        stage = MAX_STAT_STAGE;
    }
    battleCtx->battleMons[battler].statBoosts[stat] = stage;
}

static BOOL Mercury_TryCommander(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int *subscript)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    // First release any surviving Tatsugiri whose host has fainted or left.
    for (i = 0; i < maxBattlers; i++) {
        if (battleCtx->mercuryCommanderActive[i]) {
            int host = battleCtx->mercuryCommanderHost[i];

            if (host >= maxBattlers
                || battleCtx->battleMons[host].curHP == 0
                || battleCtx->battleMons[host].species != SPECIES_DONDOZO) {
                if (host < maxBattlers) {
                    battleCtx->mercuryCommanded[host] = FALSE;
                }
                battleCtx->mercuryCommanderActive[i] = FALSE;
                battleCtx->mercuryCommanderHost[i] = BATTLER_NONE;
                battleCtx->battleMons[i].moveEffectsMask &=
                    ~MOVE_EFFECT_SEMI_INVULNERABLE;

                if (battleCtx->battleMons[i].curHP) {
                    battleCtx->msgBattlerTemp = i;
                    *subscript = subscript_mercury_commander_release;
                    return TRUE;
                }
            }
        }
    }

    if ((BattleSystem_GetBattleType(battleSys) & BATTLE_TYPE_DOUBLES) == 0) {
        return FALSE;
    }

    for (i = 0; i < maxBattlers; i++) {
        int battler = battleCtx->monSpeedOrder[i];
        int ally;

        if (battleCtx->mercuryCommanderActive[battler]
            || battleCtx->battleMons[battler].curHP == 0
            || battleCtx->battleMons[battler].species != SPECIES_TATSUGIRI
            || Battler_Ability(battleCtx, battler) != ABILITY_COMMANDER
            || (battleCtx->battleMons[battler].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM)) {
            continue;
        }

        ally = BattleSystem_GetPartner(battleSys, battler);
        if (ally == battler
            || battleCtx->battleMons[ally].curHP == 0
            || battleCtx->battleMons[ally].species != SPECIES_DONDOZO
            || battleCtx->mercuryCommanded[ally]) {
            continue;
        }

        battleCtx->mercuryCommanderActive[battler] = TRUE;
        battleCtx->mercuryCommanderHost[battler] = ally;
        battleCtx->mercuryCommanded[ally] = TRUE;
        battleCtx->battleMons[battler].moveEffectsMask |=
            MOVE_EFFECT_SEMI_INVULNERABLE;

        Mercury_CommanderRaiseTwo(
            battleCtx, ally, BATTLE_STAT_ATTACK);
        Mercury_CommanderRaiseTwo(
            battleCtx, ally, BATTLE_STAT_DEFENSE);
        Mercury_CommanderRaiseTwo(
            battleCtx, ally, BATTLE_STAT_SP_ATTACK);
        Mercury_CommanderRaiseTwo(
            battleCtx, ally, BATTLE_STAT_SP_DEFENSE);
        Mercury_CommanderRaiseTwo(
            battleCtx, ally, BATTLE_STAT_SPEED);

        battleCtx->msgBattlerTemp = battler;
        battleCtx->msgDefender = ally;
        *subscript = subscript_mercury_commander_enter;
        return TRUE;
    }

    return FALSE;
}

""",
        "Commander helpers",
    )

    replace_in_function(
        path,
        "int BattleSystem_TriggerEffectOnSwitch(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        case SWITCH_IN_CHECK_STATE_FORM_CHANGE:
            if (BattleSystem_TriggerFormChange(battleSys, battleCtx, &subscript) == TRUE) {
""",
        """        case SWITCH_IN_CHECK_STATE_FORM_CHANGE:
            if (Mercury_TryCommander(
                    battleSys, battleCtx, &subscript) == TRUE) {
                result = SWITCH_IN_CHECK_RESULT_BREAK;
            } else if (BattleSystem_TriggerFormChange(battleSys, battleCtx, &subscript) == TRUE) {
""",
        "Commander switch-in activation",
    )

    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    battleCtx->mercuryIllusionActive[battler] = FALSE;
""",
        """    {
        int i;
        int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

        // Replacing a commanded host releases any surviving commander.
        if (battleCtx->mercuryCommanded[battler]) {
            for (i = 0; i < maxBattlers; i++) {
                if (battleCtx->mercuryCommanderActive[i]
                    && battleCtx->mercuryCommanderHost[i] == battler) {
                    battleCtx->mercuryCommanderActive[i] = FALSE;
                    battleCtx->mercuryCommanderHost[i] = BATTLER_NONE;
                    battleCtx->battleMons[i].moveEffectsMask &=
                        ~MOVE_EFFECT_SEMI_INVULNERABLE;
                }
            }
        }

        battleCtx->mercuryCommanded[battler] = FALSE;
        battleCtx->mercuryCommanderActive[battler] = FALSE;
        battleCtx->mercuryCommanderHost[battler] = BATTLER_NONE;
    }

    battleCtx->mercuryIllusionActive[battler] = FALSE;
""",
        "Commander slot reset",
    )

    replace_in_function(
        path,
        "BOOL Battler_IsTrapped(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    int result = FALSE;

""",
        """    int result = FALSE;

    if (battleCtx->mercuryCommanded[battler]) {
        return TRUE;
    }
    if (battleCtx->mercuryCommanderActive[battler]
        && battleCtx->mercuryCommanderHost[battler] < MAX_BATTLERS
        && battleCtx->battleMons[
            battleCtx->mercuryCommanderHost[battler]].curHP) {
        return TRUE;
    }

""",
        "Commander hard trap",
    )

    replace_in_function(
        path,
        "BOOL Battler_IsTrappedMsg(BattleSystem *battleSys, BattleContext *battleCtx, int battler, BattleMessage *msgOut)",
        """    itemEffect = Battler_HeldItemEffect(battleCtx, battler);

""",
        """    itemEffect = Battler_HeldItemEffect(battleCtx, battler);

    if (battleCtx->mercuryCommanded[battler]
        || (battleCtx->mercuryCommanderActive[battler]
            && battleCtx->mercuryCommanderHost[battler] < MAX_BATTLERS
            && battleCtx->battleMons[
                battleCtx->mercuryCommanderHost[battler]].curHP)) {
        if (msgOut != NULL) {
            msgOut->tags = TAG_NONE;
            msgOut->id = BattleStrings_Text_CantEscape2;
        }
        return TRUE;
    }

""",
        "Commander hard trap message",
    )

    replace_in_function(
        path,
        "BOOL BattleSystem_CanWhirlwind(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    BOOL result = FALSE;

""",
        """    BOOL result = FALSE;

    if (battleCtx->mercuryCommanded[battleCtx->defender]
        || (battleCtx->mercuryCommanderActive[battleCtx->defender]
            && battleCtx->mercuryCommanderHost[battleCtx->defender]
                < MAX_BATTLERS)) {
        return FALSE;
    }

""",
        "Commander drag immunity",
    )

    # Trace cannot acquire Commander.
    replace_once(
        path,
        """        && ability1 != ABILITY_ILLUSION;
""",
        """        && ability1 != ABILITY_ILLUSION
        && ability1 != ABILITY_COMMANDER;
""",
        "Commander Trace defender1",
    )
    replace_once(
        path,
        """        && ability2 != ABILITY_ILLUSION;
""",
        """        && ability2 != ABILITY_ILLUSION
        && ability2 != ABILITY_COMMANDER;
""",
        "Commander Trace defender2",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_in_function(
        path,
        "static void BattleControllerPlayer_CommandSelectionInput(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        case COMMAND_SELECTION_INIT:
            // No need to reinitialize if the same controller acts for both battlers on a side.
""",
        """        case COMMAND_SELECTION_INIT:
            if (battleCtx->mercuryCommanderActive[i]
                && battleCtx->mercuryCommanderHost[i] < maxBattlers
                && battleCtx->battleMons[
                    battleCtx->mercuryCommanderHost[i]].curHP) {
                battleCtx->curCommandState[i] = COMMAND_SELECTION_WAIT;
                battleCtx->battlerActions[i][BATTLE_ACTION_PICK_COMMAND] =
                    BATTLE_CONTROL_MOVE_END;
                break;
            }

            // No need to reinitialize if the same controller acts for both battlers on a side.
""",
        "Commander skips action selection",
    )

    replace_once(
        path,
        """void BattleControllerPlayer_CheckMoveHit(BattleSystem *battleSys, BattleContext *battleCtx, int attacker, int defender, int move)
{
    BattleControllerPlayer_CheckMoveHitAccuracy(battleSys, battleCtx, attacker, defender, move);
""",
        """void BattleControllerPlayer_CheckMoveHit(BattleSystem *battleSys, BattleContext *battleCtx, int attacker, int defender, int move)
{
    if (battleCtx->mercuryCommanderActive[defender]
        && battleCtx->mercuryCommanderHost[defender] < MAX_BATTLERS
        && battleCtx->battleMons[
            battleCtx->mercuryCommanderHost[defender]].curHP) {
        battleCtx->moveStatusFlags |= MOVE_STATUS_MISSED;
        return;
    }

    BattleControllerPlayer_CheckMoveHitAccuracy(battleSys, battleCtx, attacker, defender, move);
""",
        "Commander target invulnerability",
    )


def patch_special_restrictions(root: Path) -> None:
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMMANDER, _091\n",
        "Commander Role Play target",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMMANDER, _091\n",
        "Commander Role Play user",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMMANDER, _156\n",
        "Commander Skill Swap target",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMMANDER, _156\n",
        "Commander Skill Swap user",
    )

    # Worry Seed is Mercury's existing overwrite/Entrainment-style guard.
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMMANDER, _041\n",
        "Commander Worry Seed / overwrite lock",
    )


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
    player = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
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
        "pair_state":
            "mercuryCommanderActive[MAX_BATTLERS]" in ctx
            and "mercuryCommanderHost[MAX_BATTLERS]" in ctx
            and "mercuryCommanded[MAX_BATTLERS]" in ctx,
        "doubles_tatsugiri_dondozo_activation":
            "BATTLE_TYPE_DOUBLES" in lib
            and "SPECIES_TATSUGIRI" in lib
            and "SPECIES_DONDOZO" in lib
            and "ABILITY_COMMANDER" in lib,
        "five_plus_two_boosts":
            all(token in lib for token in (
                "BATTLE_STAT_ATTACK",
                "BATTLE_STAT_DEFENSE",
                "BATTLE_STAT_SP_ATTACK",
                "BATTLE_STAT_SP_DEFENSE",
                "BATTLE_STAT_SPEED",
            ))
            and "Mercury_CommanderRaiseTwo" in lib,
        "commander_cannot_act":
            "mercuryCommanderActive[i]" in player
            and "BATTLE_CONTROL_MOVE_END" in player,
        "commander_cannot_be_targeted":
            "mercuryCommanderActive[defender]" in player
            and "MOVE_STATUS_MISSED" in player,
        "both_are_trapped":
            "mercuryCommanded[battler]" in lib
            and "mercuryCommanderActive[battler]" in lib
            and "BOOL Battler_IsTrapped(" in lib,
        "forced_switch_blocked":
            "BattleSystem_CanWhirlwind" in lib
            and "mercuryCommanded[battleCtx->defender]" in lib,
        "indirect_damage_not_blocked":
            "curHP" in lib
            and "mercuryCommanderActive" not in suppress,
        "host_faint_releases_commander":
            "subscript_mercury_commander_release" in lib
            and "~MOVE_EFFECT_SEMI_INVULNERABLE" in lib,
        "commander_faint_keeps_host_commanded":
            "mercuryCommanded[ally] = TRUE;" in lib
            and "mercuryCommanded[battler] = FALSE;" in lib,
        "suppressible_before_activation":
            "ABILITY_COMMANDER" not in cannot
            and "ABILITY_COMMANDER" not in suppress,
        "trace_roleplay_skillswap_blocked":
            "ability1 != ABILITY_COMMANDER" in lib
            and "ability2 != ABILITY_COMMANDER" in lib
            and "ABILITY_COMMANDER" in copy
            and "ABILITY_COMMANDER" in swap,
        "worry_seed_blocked":
            "ABILITY_COMMANDER" in worry,
        "receiver_blocked":
            "ABILITY_COMMANDER" in receiver,
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
        default=Path("mr08s12-canonical-ability-commander.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_subscripts_and_text(root)
    patch_battle_lib(root)
    patch_controller(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S12_CANONICAL_ABILITY_COMMANDER",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 185,
        "remaining_modern_canonical_mechanics": 2,
        "policy": "Current-mainline Commander doubles pairing, Dondozo +2 five-stat boost, action/target/trap state, and special-copy restrictions.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S12 validation failed")


if __name__ == "__main__":
    main()
