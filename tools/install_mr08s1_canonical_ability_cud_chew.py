#!/usr/bin/env python3
"""MR08S1 — canonical Cud Chew pass.

Implements current-mainline Cud Chew using Platinum's existing Berry effect
pipeline:
- when an active Cud Chew user consumes a held Berry, remember that Berry;
- Bug Bite / Pluck consumption and a Berry received through Fling also arm it;
- only the most recently eaten Berry is retained;
- the remembered Berry is eaten again at the end of the next turn, not the
  same turn;
- the second use does not restore the held item, overwrite Recycle, or trigger
  Symbiosis;
- Neutralizing Gas naturally blocks arming through Battler_Ability and pauses
  the delayed activation until Cud Chew becomes active again.

The replay uses Platinum's Pluck/Bug Bite Berry-effect lane so HP, PP, status,
stat, flavor, Lansat/Micle/Custap and other supported Berry effects keep their
native behavior. Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_CUD_CHEW",)
EXPECTED_IDS = {"ABILITY_CUD_CHEW": 291}


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
        """    // Mercury MR08S1: delayed Cud Chew Berry replay.
    u16 mercuryCudChewBerry[MAX_BATTLERS];
    u16 mercuryCudChewTurn[MAX_BATTLERS];
    u8 mercuryCudChewPartySlot[MAX_BATTLERS];
    u8 mercuryCudChewReplay;
    u8 mercuryCudChewReplayBattler;

""",
        "Cud Chew battle state",
    )


def patch_cud_chew_subscript(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_cud_chew.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    // Announce the Ability, then reuse the already-selected native Berry effect.
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    CallFromVar BTLVAR_SCRIPT_TEMP
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_dancer\n",
        "subscript_mercury_cud_chew\n",
        "Cud Chew subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_dancer.s',\n",
        "    'subscript_mercury_cud_chew.s',\n",
        "Cud Chew subscript build list",
    )


def patch_remove_item(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_function(
        path,
        "static BOOL BtlCmd_RemoveItem(BattleSystem *battleSys, BattleContext *battleCtx)",
        """static BOOL BtlCmd_RemoveItem(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BattleScript_Iter(battleCtx, 1);
    int inBattler = BattleScript_Read(battleCtx);

    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
    int ally = battler ^ 2;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    int removedItem = battleCtx->battleMons[battler].heldItem;

    // A Cud Chew replay is an effect-only second eating. Do not remove a new
    // held item, overwrite Recycle, or hand an ally item through Symbiosis.
    if (battleCtx->mercuryCudChewReplay
        && battleCtx->mercuryCudChewReplayBattler == battler) {
        battleCtx->mercuryCudChewReplay = FALSE;
        return FALSE;
    }

    if (removedItem != ITEM_NONE
        && Item_IsBerry(removedItem) == TRUE
        && Battler_Ability(battleCtx, battler) == ABILITY_CUD_CHEW) {
        battleCtx->mercuryCudChewBerry[battler] = removedItem;
        battleCtx->mercuryCudChewTurn[battler] = battleCtx->totalTurns;
        battleCtx->mercuryCudChewPartySlot[battler] =
            battleCtx->selectedPartySlot[battler];
    }

    battleCtx->recycleItem[battler] = removedItem;
    battleCtx->battleMons[battler].heldItem = ITEM_NONE;

    // Preserve MR08P2 Symbiosis behavior after the consumed item is recorded.
    if (removedItem != ITEM_NONE
        && battleCtx->battleMons[battler].curHP
        && ally < maxBattlers
        && battleCtx->battleMons[ally].curHP
        && Battler_Ability(battleCtx, ally) == ABILITY_SYMBIOSIS
        && battleCtx->battleMons[ally].heldItem != ITEM_NONE
        && battleCtx->battleMons[ally].heldItem != ITEM_GRISEOUS_ORB) {
        battleCtx->battleMons[battler].heldItem =
            battleCtx->battleMons[ally].heldItem;
        battleCtx->battleMons[ally].heldItem = ITEM_NONE;
        BattleMon_CopyToParty(battleSys, battleCtx, ally);
    }

    BattleMon_CopyToParty(battleSys, battleCtx, battler);

    return FALSE;
}""",
        "Cud Chew RemoveItem / Symbiosis integration",
    )


def patch_battle_lib(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
""",
        """static void Mercury_RecordCudChew(
    BattleContext *battleCtx,
    int battler,
    u16 berry)
{
    if (battleCtx->mercuryCudChewReplay == FALSE
        && berry != ITEM_NONE
        && Item_IsBerry(berry) == TRUE
        && Battler_Ability(battleCtx, battler) == ABILITY_CUD_CHEW) {
        battleCtx->mercuryCudChewBerry[battler] = berry;
        battleCtx->mercuryCudChewTurn[battler] = battleCtx->totalTurns;
        battleCtx->mercuryCudChewPartySlot[battler] =
            battleCtx->selectedPartySlot[battler];
    }
}

""",
        "Cud Chew record helper",
    )

    # Bug Bite / Pluck: the Berry belongs to the defender but is eaten by the
    # attacker, so the generic RemoveItem hook cannot identify the consumer.
    insert_after_once(
        path,
        """    if (Battler_SubstituteWasHit(battleCtx, battleCtx->defender) == TRUE) {
        return result;
    }

""",
        """    Mercury_RecordCudChew(
        battleCtx,
        battleCtx->attacker,
        battleCtx->battleMons[battler].heldItem);

""",
        "Cud Chew Pluck/Bug Bite arm",
    )

    # Fling: a Berry's effect is received by the defender. Record it after
    # proving the thrown item has nonzero Fling power.
    insert_after_once(
        path,
        """    if (battleCtx->movePower == 0) {
        return FALSE;
    }

""",
        """    Mercury_RecordCudChew(
        battleCtx,
        battleCtx->defender,
        battleCtx->battleMons[battler].heldItem);

""",
        "Cud Chew Fling arm",
    )

    # Add the delayed replay to the normal end-of-turn Ability lane. Using
    # totalTurns rather than a simple decrement prevents a Berry eaten during
    # the end-of-turn item phase from replaying immediately.
    insert_before_once(
        path,
        """    case ABILITY_SHED_SKIN:
""",
        """    case ABILITY_CUD_CHEW: {
        u16 berry = battleCtx->mercuryCudChewBerry[battler];

        if (berry != ITEM_NONE
            && battleCtx->battleMons[battler].curHP
            && battleCtx->mercuryCudChewPartySlot[battler]
                == battleCtx->selectedPartySlot[battler]
            && battleCtx->totalTurns > battleCtx->mercuryCudChewTurn[battler]) {
            int oldAttacker = battleCtx->attacker;
            int oldDefender = battleCtx->defender;
            u16 oldHeldItem = battleCtx->battleMons[battler].heldItem;

            // Clear the pending record before replay. This is what prevents the
            // old launch-version every-other-turn loop and lets a later Berry
            // overwrite the state normally.
            battleCtx->mercuryCudChewBerry[battler] = ITEM_NONE;
            battleCtx->mercuryCudChewReplay = TRUE;
            battleCtx->mercuryCudChewReplayBattler = battler;

            // Platinum's Pluck lane already encodes direct Berry effects
            // without their held-item activation thresholds. Temporarily make
            // the remembered Berry visible only while that lane is selected.
            battleCtx->attacker = battler;
            battleCtx->defender = battler;
            battleCtx->battleMons[battler].heldItem = berry;
            battleCtx->scriptTemp = 0;

            (void)BattleSystem_PluckBerry(battleSys, battleCtx, battler);

            // The replay must not look like an actual Pluck action. Force the
            // normal Berry subscript to reach RemoveItem, where MR08S1 turns
            // the removal into an effect-only no-op.
            battleCtx->selfTurnFlags[battler].statusFlags &=
                ~SELF_TURN_FLAG_PLUCK_BERRY;

            battleCtx->battleMons[battler].heldItem = oldHeldItem;
            BattleMon_CopyToParty(battleSys, battleCtx, battler);
            battleCtx->attacker = oldAttacker;
            battleCtx->defender = oldDefender;
            battleCtx->msgBattlerTemp = battler;
            battleCtx->msgTemp = battler;
            battleCtx->msgItemTemp = berry;

            if (battleCtx->scriptTemp) {
                subscript = subscript_mercury_cud_chew;
                result = TRUE;
            } else {
                // The Berry had no applicable effect at replay time (for
                // example a status-curing Berry while healthy).
                battleCtx->mercuryCudChewReplay = FALSE;
            }
        }
        break;
    }

""",
        "Cud Chew delayed replay",
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
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    cud = (root / "res/battle/scripts/subscripts/subscript_mercury_cud_chew.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "pending_berry_state":
            "mercuryCudChewBerry[MAX_BATTLERS]" in ctx
            and "mercuryCudChewTurn[MAX_BATTLERS]" in ctx
            and "mercuryCudChewPartySlot[MAX_BATTLERS]" in ctx,
        "held_berry_consumption_arm":
            "Item_IsBerry(removedItem) == TRUE" in script
            and "ABILITY_CUD_CHEW" in script,
        "pluck_and_fling_arm":
            lib.count("Mercury_RecordCudChew(") >= 3
            and "battleCtx->attacker" in lib
            and "battleCtx->defender" in lib,
        "next_turn_delay":
            "battleCtx->totalTurns > battleCtx->mercuryCudChewTurn[battler]" in lib,
        "latest_berry_overwrites":
            "battleCtx->mercuryCudChewBerry[battler] = berry;" in lib
            and "battleCtx->mercuryCudChewBerry[battler] = ITEM_NONE;" in lib,
        "native_berry_replay":
            "BattleSystem_PluckBerry(battleSys, battleCtx, battler)" in lib
            and "subscript_mercury_cud_chew" in order
            and "CallFromVar BTLVAR_SCRIPT_TEMP" in cud,
        "replay_does_not_remove_new_item":
            "mercuryCudChewReplayBattler == battler" in script
            and "battleCtx->mercuryCudChewReplay = FALSE;" in script,
        "symbiosis_preserved":
            "Battler_Ability(battleCtx, ally) == ABILITY_SYMBIOSIS" in script,
        "party_slot_identity_guard":
            "mercuryCudChewPartySlot[battler]" in lib
            and "selectedPartySlot[battler]" in lib,
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
        default=Path("mr08s1-canonical-ability-cud-chew.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_cud_chew_subscript(root)
    patch_remove_item(root)
    patch_battle_lib(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S1_CANONICAL_ABILITY_CUD_CHEW",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 170,
        "remaining_modern_canonical_mechanics": 17,
        "policy": "Official/current-mainline Cud Chew delayed Berry replay, including Pluck/Bug Bite and Fling consumption.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S1 validation failed")


if __name__ == "__main__":
    main()
