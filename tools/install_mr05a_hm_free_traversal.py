#!/usr/bin/env python3
"""MR05A — HM-free traversal foundation.

Reuses Mercury's universal Move Learner compatibility data so field traversal
requires a compatible party Pokemon, not an occupied move slot. Vanilla badge,
map, partner, and story restrictions remain in place.

Phase A covers field-interaction traversal (Cut, Rock Smash, Strength, Surf,
Rock Climb, Waterfall, and the dormant direct Defog path). The completed
MR05A pass also exposes Fly, Defog, and Flash from the party menu whenever
the selected Pokemon is compatible, without requiring the move to be learned.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1))


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1))


def patch_compatibility_backend(root: Path) -> None:
    header = root / "include/move_reminder_data.h"
    source = root / "src/move_reminder_data.c"

    insert_after_once(
        header,
        "u8 MoveReminderData_GetMoveSource(Pokemon *mon, u16 move);\n",
        "BOOL MoveReminderData_IsMoveCompatible(Pokemon *mon, u16 move, enum HeapID heapID);\n",
        "MR05A compatibility declaration",
    )

    helper = r'''
BOOL MoveReminderData_IsMoveCompatible(Pokemon *mon, u16 move, enum HeapID heapID)
{
    u16 species = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);
    u8 form = Pokemon_GetValue(mon, MON_DATA_FORM, NULL);

    if (Pokemon_GetValue(mon, MON_DATA_IS_EGG, NULL) != FALSE) {
        return FALSE;
    }

    SpeciesLearnsetEntry *levelUpMoves = Heap_Alloc(heapID, sizeof(SpeciesLearnset));
    Pokemon_LoadLevelUpMovesOf(species, form, levelUpMoves);

    for (u16 i = 0; i < MAX_LEARNSET_ENTRIES + 1; i++) {
        if (LEARNSET_ENTRY_IS_SENTINEL(levelUpMoves[i])) {
            break;
        }

        if (levelUpMoves[i].move == move) {
            Heap_Free(levelUpMoves);
            return TRUE;
        }
    }

    Heap_Free(levelUpMoves);

    if (species > SPECIES_NONE && species <= MERCURY_MOVE_LEARNER_SPECIES_MAX) {
        u32 begin = sMercuryMoveLearnerExtraOffsets[species];
        u32 finish = sMercuryMoveLearnerExtraOffsets[species + 1];

        for (u32 i = begin; i < finish; i++) {
            if ((sMercuryMoveLearnerExtraMoves[i] & MERCURY_MOVE_LEARNER_MOVE_MASK) == move) {
                return TRUE;
            }
        }
    }

    return FALSE;
}

'''

    insert_before_once(
        source,
        "u8 MoveReminderData_GetMoveSource(Pokemon *mon, u16 move)\n",
        helper,
        "MR05A compatibility helper",
    )


def patch_script_command(root: Path) -> None:
    party_header = root / "include/scrcmd_party.h"
    party_source = root / "src/scrcmd_party.c"
    command_table = root / "include/data/scripts/scrcmd.h"
    scrcmd_source = root / "src/scrcmd.c"
    macros = root / "asm/macros/scrcmd.inc"

    insert_after_once(
        party_header,
        "BOOL ScrCmd_FindPartySlotWithMove(ScriptContext *ctx);\n",
        "BOOL ScrCmd_FindPartySlotCompatibleWithMove(ScriptContext *ctx);\n",
        "MR05A script command declaration",
    )

    insert_after_once(
        party_source,
        '#include "map_header.h"\n',
        '#include "move_reminder_data.h"\n',
        "MR05A compatibility include",
    )

    command = r'''
BOOL ScrCmd_FindPartySlotCompatibleWithMove(ScriptContext *ctx)
{
    FieldSystem *fieldSystem = ctx->fieldSystem;
    u16 *destVar = ScriptContext_GetVarPointer(ctx);
    u16 move = ScriptContext_GetVar(ctx);
    Party *party = SaveData_GetParty(fieldSystem->saveData);
    u8 partyCount = Party_GetCurrentCount(party);

    *destVar = MAX_PARTY_SIZE;

    for (u8 slot = 0; slot < partyCount; slot++) {
        Pokemon *mon = Party_GetPokemonBySlotIndex(party, slot);

        if (MoveReminderData_IsMoveCompatible(mon, move, HEAP_ID_FIELD2)) {
            *destVar = slot;
            break;
        }
    }

    return FALSE;
}

'''

    insert_before_once(
        party_source,
        "BOOL ScrCmd_SurvivePoison(ScriptContext *ctx)\n",
        command,
        "MR05A compatible party slot command",
    )

    replace_once(
        command_table,
        "ScriptCommand(SCRCMD_UNUSED_09C,                                           ScrCmd_Unused_09C)",
        "ScriptCommand(SCRCMD_UNUSED_09C,                                           ScrCmd_FindPartySlotCompatibleWithMove)",
        "MR05A command table slot",
    )

    replace_once(
        scrcmd_source,
        "static BOOL ScrCmd_Unused_09C(ScriptContext *ctx);\n",
        "",
        "MR05A remove unused 09C declaration",
    )

    replace_once(
        scrcmd_source,
        """static BOOL ScrCmd_Unused_09C(ScriptContext *ctx)
{
    return FALSE;
}

""",
        "",
        "MR05A remove unused 09C implementation",
    )

    replace_once(
        macros,
        """    .macro ScrCmd_Unused_09C
    .short SCRCMD_UNUSED_09C
    .endm
""",
        """    .macro FindPartySlotCompatibleWithMove destVar, move
    .short SCRCMD_UNUSED_09C
    .short \\destVar
    .short \\move
    .endm
""",
        "MR05A compatibility macro",
    )


def patch_field_scripts(root: Path) -> None:
    scripts = root / "res/field/scripts/scripts_field_moves.s"
    text = scripts.read_text()

    expected = text.count("FindPartySlotWithMove")
    if expected < 8:
        raise SystemExit(f"MR05A expected field-move script checks, found only {expected}")

    text = text.replace("FindPartySlotWithMove", "FindPartySlotCompatibleWithMove")

    surf_old = """FieldMoves_Water:
    PlaySE SE_CONFIRM_sseq_3
    LockAll
    CheckHasPartner VAR_RESULT
"""
    surf_new = """FieldMoves_Water:
    PlaySE SE_CONFIRM_sseq_3
    LockAll
    FindPartySlotCompatibleWithMove VAR_RESULT, MOVE_SURF
    GoToIfEq VAR_RESULT, MAX_PARTY_SIZE, FieldMoves_CantUseSurfNoCompatible
    CheckBadgeAcquired BADGE_ID_FEN, VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, FieldMoves_CantUseSurfNoCompatible
    CheckHasPartner VAR_RESULT
"""
    if surf_old not in text:
        raise SystemExit("MR05A Surf field anchor changed")
    text = text.replace(surf_old, surf_new, 1)

    surf_error_anchor = """FieldMoves_CantUseSurf:
    Message FieldMoves_Text_NoSurfingWithPartner
"""
    surf_error = """FieldMoves_CantUseSurfNoCompatible:
    Message FieldMoves_Text_SurfNeedsCompatiblePokemon
    WaitButton
    CloseMessage
    GoTo FieldMoves_End2

"""
    if surf_error not in text:
        if surf_error_anchor not in text:
            raise SystemExit("MR05A Surf error anchor changed")
        text = text.replace(surf_error_anchor, surf_error + surf_error_anchor, 1)

    scripts.write_text(text)

    text_path = root / "res/text/field_moves.json"
    data = json.loads(text_path.read_text())
    msg_id = "FieldMoves_Text_SurfNeedsCompatiblePokemon"
    if not any(msg.get("id") == msg_id for msg in data["messages"]):
        data["messages"].append({
            "id": msg_id,
            "en_US": [
                "You need the Fen Badge and a compatible\\n",
                "Pokémon in your party to surf here."
            ],
        })
    text_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")



def patch_party_menu(root: Path) -> None:
    defs = root / "include/applications/party_menu/defs.h"
    main = root / "src/applications/party_menu/main.c"
    windows = root / "src/applications/party_menu/windows.c"

    replace_once(
        defs,
        """    PARTY_MENU_STR_MOVE0,
    PARTY_MENU_STR_MOVE1,
    PARTY_MENU_STR_MOVE2,
    PARTY_MENU_STR_MOVE3,

    NUM_PARTY_MENU_STRS,
""",
        """    PARTY_MENU_STR_MOVE0,
    PARTY_MENU_STR_MOVE1,
    PARTY_MENU_STR_MOVE2,
    PARTY_MENU_STR_MOVE3,
    PARTY_MENU_STR_MOVE4,
    PARTY_MENU_STR_MOVE5,
    PARTY_MENU_STR_MOVE6,

    NUM_PARTY_MENU_STRS,
""",
        "MR05A dynamic field-move string capacity",
    )

    insert_after_once(
        main,
        '#include "message.h"\n',
        '#include "move_reminder_data.h"\n',
        "MR05A party-menu compatibility include",
    )

    replace_once(
        main,
        "    v0 = Heap_Alloc(HEAP_ID_PARTY_MENU, 8);\n",
        "    v0 = Heap_Alloc(HEAP_ID_PARTY_MENU, 12);\n",
        "MR05A party context buffer capacity",
    )

    replace_once(
        main,
        """    for (v1 = 0; v1 < 20; v1++) {
        String_Free(v0->menuStrings[v1]);
    }
""",
        """    for (v1 = 0; v1 < NUM_PARTY_MENU_STRS; v1++) {
        String_Free(v0->menuStrings[v1]);
    }
""",
        "MR05A dynamic string cleanup capacity",
    )

    insert_after_once(
        main,
        """static const u16 sFieldMoves[FIELD_MOVE_MAX] = {
    [FIELD_MOVE_CUT] = MOVE_CUT,
    [FIELD_MOVE_FLY] = MOVE_FLY,
    [FIELD_MOVE_SURF] = MOVE_SURF,
    [FIELD_MOVE_STRENGTH] = MOVE_STRENGTH,
    [FIELD_MOVE_DEFOG] = MOVE_DEFOG,
    [FIELD_MOVE_ROCK_SMASH] = MOVE_ROCK_SMASH,
    [FIELD_MOVE_WATERFALL] = MOVE_WATERFALL,
    [FIELD_MOVE_ROCK_CLIMB] = MOVE_ROCK_CLIMB,
    [FIELD_MOVE_FLASH] = MOVE_FLASH,
    [FIELD_MOVE_TELEPORT] = MOVE_TELEPORT,
    [FIELD_MOVE_DIG] = MOVE_DIG,
    [FIELD_MOVE_SWEET_SCENT] = MOVE_SWEET_SCENT,
    [FIELD_MOVE_CHATTER] = MOVE_CHATTER,
    [FIELD_MOVE_MILK_DRINK] = MOVE_MILK_DRINK,
    [FIELD_MOVE_SOFTBOILED] = MOVE_SOFTBOILED,
};
""",
        """
static const u16 sMercuryHmFreeMenuMoves[] = {
    MOVE_FLY,
    MOVE_DEFOG,
    MOVE_FLASH,
};
""",
        "MR05A party-menu compatibility moves",
    )

    old = """            for (i = 0; i < 4; i++) {
                move = (u16)Pokemon_GetValue(mon, MON_DATA_MOVE1 + i, NULL);

                if (move == 0) {
                    break;
                }

                fieldEffect = GetFieldMoveIndex(move);

                if (fieldEffect != 0xff) {
                    menuEntriesBuffer[count] = fieldEffect;
                    count++;
                    PartyMenu_SetKnownFieldMove(application, move, fieldMoveIndex);
                    fieldMoveIndex++;
                }
            }

            menuEntriesBuffer[count] = 0;
"""
    new = """            for (i = 0; i < 4; i++) {
                move = (u16)Pokemon_GetValue(mon, MON_DATA_MOVE1 + i, NULL);

                if (move == 0) {
                    break;
                }

                fieldEffect = GetFieldMoveIndex(move);

                if (fieldEffect != 0xff) {
                    menuEntriesBuffer[count] = fieldEffect;
                    count++;
                    PartyMenu_SetKnownFieldMove(application, move, fieldMoveIndex);
                    fieldMoveIndex++;
                }
            }

            for (i = 0; i < NELEMS(sMercuryHmFreeMenuMoves); i++) {
                u16 compatibleMove = sMercuryHmFreeMenuMoves[i];
                BOOL alreadyKnown = FALSE;

                for (u8 moveSlot = 0; moveSlot < LEARNED_MOVES_MAX; moveSlot++) {
                    if ((u16)Pokemon_GetValue(mon, MON_DATA_MOVE1 + moveSlot, NULL) == compatibleMove) {
                        alreadyKnown = TRUE;
                        break;
                    }
                }

                if (alreadyKnown == FALSE
                    && MoveReminderData_IsMoveCompatible(mon, compatibleMove, HEAP_ID_PARTY_MENU)) {
                    fieldEffect = GetFieldMoveIndex(compatibleMove);

                    if (fieldEffect != 0xff) {
                        menuEntriesBuffer[count] = fieldEffect;
                        count++;
                        PartyMenu_SetKnownFieldMove(application, compatibleMove, fieldMoveIndex);
                        fieldMoveIndex++;
                    }
                }
            }

            menuEntriesBuffer[count] = 0;
"""
    replace_once(main, old, new, "MR05A compatible party-menu actions")

    replace_once(
        windows,
        """    String *string = MessageLoader_GetNewString(application->messageLoader, PartyMenu_Text_FieldMove0 + menuEntry);
""",
        """    String *string = MessageLoader_GetNewString(application->messageLoader, PartyMenu_Text_FieldMove0);
""",
        "MR05A reusable field-move label template",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05a-hm-free-traversal.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_compatibility_backend(root)
    patch_script_command(root)
    patch_field_scripts(root)
    patch_party_menu(root)

    report = {
        "gate": "MERCURY_MR05A_HM_FREE_TRAVERSAL_FOUNDATION",
        "status": "PASS",
        "policy": {
            "badge_checks": "preserved",
            "story_and_map_checks": "preserved",
            "party_requirement": "compatible non-Egg Pokemon required",
            "move_slot_requirement": "removed for patched field interactions and Fly/Defog/Flash party-menu actions",
            "compatibility_source": "Mercury universal Move Learner legal learnset data",
        },
        "phase_a": [
            "Cut",
            "Rock Smash",
            "Strength",
            "Surf",
            "Rock Climb",
            "Waterfall",
            "direct Defog script path",
        ],
        "party_menu_hm_free": [
            "Fly",
            "Defog",
            "Flash",
        ],
        "dynamic_field_move_label_capacity": 7,
        "deferred_same_phase": [],
        "vanilla_find_party_slot_command_modified": False,
        "mercury_script_opcode": "SCRCMD_UNUSED_09C",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
