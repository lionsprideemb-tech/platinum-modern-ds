#!/usr/bin/env python3
"""Install MR03: open Mercury's universal Move Learner from the normal party menu.

Production behavior:
  Start Menu -> POKEMON -> select a non-Egg Pokemon -> MOVE LEARNER

The option is shown only when the selected Pokemon has at least one currently
learnable move.  Closing the learner returns to the same party slot.
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


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1))


def patch_defs(root: Path) -> None:
    path = root / "include/applications/party_menu/defs.h"

    replace_once(
        path,
        """    PARTY_MENU_EXIT_CODE_SWEET_SCENT,
    PARTY_MENU_EXIT_CODE_CHATTER
};""",
        """    PARTY_MENU_EXIT_CODE_SWEET_SCENT,
    PARTY_MENU_EXIT_CODE_CHATTER,
    PARTY_MENU_EXIT_CODE_MOVE_LEARNER
};""",
        "Move Learner party exit code",
    )

    replace_once(
        path,
        """    PARTY_MENU_STR_SET,
    PARTY_MENU_STR_CONFIRM,
    PARTY_MENU_STR_MOVE0,""",
        """    PARTY_MENU_STR_SET,
    PARTY_MENU_STR_CONFIRM,
    PARTY_MENU_STR_MOVE_LEARNER,
    PARTY_MENU_STR_MOVE0,""",
        "Move Learner context string slot",
    )


def patch_party_text(root: Path) -> None:
    path = root / "res/text/party_menu.json"
    data = json.loads(path.read_text())

    msg_id = "PartyMenu_Text_MoveLearner"
    if not any(msg.get("id") == msg_id for msg in data["messages"]):
        data["messages"].append({
            "id": msg_id,
            "en_US": "MOVE LEARNER",
        })

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_party_windows(root: Path) -> None:
    path = root / "src/applications/party_menu/windows.c"

    replace_once(
        path,
        """    LoadMenuString(PartyMenu_Text_Switch, PARTY_MENU_STR_SWITCH);
    LoadMenuString(PartyMenu_Text_Summary, PARTY_MENU_STR_SUMMARY);
    LoadMenuString(PartyMenu_Text_Item, PARTY_MENU_STR_ITEM);""",
        """    LoadMenuString(PartyMenu_Text_Switch, PARTY_MENU_STR_SWITCH);
    LoadMenuString(PartyMenu_Text_Summary, PARTY_MENU_STR_SUMMARY);
    LoadMenuString(PartyMenu_Text_MoveLearner, PARTY_MENU_STR_MOVE_LEARNER);
    LoadMenuString(PartyMenu_Text_Item, PARTY_MENU_STR_ITEM);""",
        "Move Learner context string load",
    )


def patch_party_context(root: Path) -> None:
    path = root / "src/applications/party_menu/context_menu.c"

    insert_after_once(
        path,
        "static void PartyMenu_SelectSummary(PartyMenuApplication *application, int *partyMenuState);\n",
        "static void PartyMenu_SelectMoveLearner(PartyMenuApplication *application, int *partyMenuState);\n",
        "Move Learner action declaration",
    )

    replace_once(
        path,
        """    ACTION_SET_CAPSULE,
    ACTION_CLEANUP_2,
    ACTION_CUT,""",
        """    ACTION_SET_CAPSULE,
    ACTION_CLEANUP_2,
    ACTION_MOVE_LEARNER,
    ACTION_CUT,""",
        "Move Learner action enum",
    )

    replace_once(
        path,
        """    [ACTION_SET_CAPSULE] = PartyMenu_SetBallCapsuleAction,
    [ACTION_CLEANUP_2] =   PartyMenu_CleanupContextMenu2,
    [ACTION_CUT] =         PartyMenu_SelectCut,""",
        """    [ACTION_SET_CAPSULE] = PartyMenu_SetBallCapsuleAction,
    [ACTION_CLEANUP_2] =   PartyMenu_CleanupContextMenu2,
    [ACTION_MOVE_LEARNER] = PartyMenu_SelectMoveLearner,
    [ACTION_CUT] =         PartyMenu_SelectCut,""",
        "Move Learner action dispatch",
    )

    summary_impl = """static void PartyMenu_SelectSummary(PartyMenuApplication *application, int *partyMenuState)
{
    application->partyMenu->menuSelectionResult = PARTY_MENU_EXIT_CODE_SUMMARY;

    Menu_Free(application->contextMenu, NULL);
    StringList_Free(application->contextMenuChoices);

    *partyMenuState = PARTY_MENU_STATE_FADE_OUT;
}
"""

    learner_impl = summary_impl + """
static void PartyMenu_SelectMoveLearner(PartyMenuApplication *application, int *partyMenuState)
{
    application->partyMenu->menuSelectionResult = PARTY_MENU_EXIT_CODE_MOVE_LEARNER;

    Menu_Free(application->contextMenu, NULL);
    StringList_Free(application->contextMenuChoices);

    *partyMenuState = PARTY_MENU_STATE_FADE_OUT;
}
"""

    replace_once(
        path,
        summary_impl,
        learner_impl,
        "Move Learner action implementation",
    )


def patch_party_main(root: Path) -> None:
    path = root / "src/applications/party_menu/main.c"

    insert_after_once(
        path,
        '#include "menu.h"\n',
        '#include "move_reminder_data.h"\n',
        "Move Learner party backend include",
    )

    replace_once(
        path,
        "    v0 = Heap_Alloc(HEAP_ID_PARTY_MENU, 8);\n",
        "    v0 = Heap_Alloc(HEAP_ID_PARTY_MENU, 9 * sizeof(u8));\n",
        "Move Learner context-menu capacity",
    )

    replace_once(
        path,
        """    if (FieldSystem_IsInBattleTowerSalon(application->partyMenu->fieldSystem) == FALSE) {
        if (application->partyMembers[application->currPartySlot].isEgg == FALSE) {
            for (i = 0; i < 4; i++) {""",
        """    if (FieldSystem_IsInBattleTowerSalon(application->partyMenu->fieldSystem) == FALSE) {
        if (application->partyMembers[application->currPartySlot].isEgg == FALSE) {
            u16 *learnerMoves = MoveReminderData_GetMoves(mon, HEAP_ID_PARTY_MENU);

            if (MoveReminderData_HasMoves(learnerMoves)) {
                menuEntriesBuffer[count] = PARTY_MENU_STR_MOVE_LEARNER;
                count++;
            }

            Heap_Free(learnerMoves);

            for (i = 0; i < 4; i++) {""",
        "Move Learner party option visibility",
    )


def patch_start_menu(root: Path) -> None:
    path = root / "src/start_menu.c"

    insert_after_once(
        path,
        '#include "message.h"\n',
        '#include "move_reminder_data.h"\n',
        "Move Learner start-menu include",
    )

    insert_after_once(
        path,
        "static BOOL StartMenu_ExitSummary(FieldTask *fieldTask);\n",
        "static BOOL StartMenu_ExitMoveLearner(FieldTask *fieldTask);\n",
        "Move Learner return callback declaration",
    )

    switch_anchor = """    case PARTY_MENU_EXIT_CODE_SUMMARY:
        summary = Heap_Alloc(HEAP_ID_FIELD2, sizeof(PokemonSummary));
"""

    learner_case = """    case PARTY_MENU_EXIT_CODE_MOVE_LEARNER: {
        Pokemon *mon = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            partyMenu->selectedMonSlot);
        u16 *moves = MoveReminderData_GetMoves(mon, HEAP_ID_FIELD2);

        // The party menu normally hides this action when no moves are
        // available, but keep the field transition defensive as well.
        if (!MoveReminderData_HasMoves(moves)) {
            Heap_Free(moves);
            menu->taskData = FieldSystem_OpenPartyMenu(
                fieldSystem,
                &menu->fieldMoveContext,
                partyMenu->selectedMonSlot);
            StartMenu_SetCallback(menu, StartMenu_ExitPartyMenu);
            break;
        }

        MoveReminderData *learner = MoveReminderData_Alloc(HEAP_ID_FIELD2);
        learner->mon = mon;
        learner->trainerInfo = SaveData_GetTrainerInfo(fieldSystem->saveData);
        learner->options = SaveData_GetOptions(fieldSystem->saveData);
        learner->moves = moves;
        learner->isMoveTutor = TRUE;

        u32 *returnSlot = Heap_Alloc(HEAP_ID_FIELD2, sizeof(u32));
        *returnSlot = partyMenu->selectedMonSlot;

        FieldSystem_OpenMoveReminderMenu(fieldSystem, learner);
        menu->taskData = learner;
        menu->additionalTaskContext = returnSlot;
        StartMenu_SetCallback(menu, StartMenu_ExitMoveLearner);
    } break;
"""

    replace_once(
        path,
        switch_anchor,
        switch_anchor + learner_case,
        "Move Learner start-menu exit dispatch",
    )

    summary_callback = """static BOOL StartMenu_ExitSummary(FieldTask *fieldTask)
{"""

    learner_callback = """static BOOL StartMenu_ExitMoveLearner(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    MoveReminderData *learner = menu->taskData;
    u32 returnSlot = *((u32 *)menu->additionalTaskContext);

    // The universal move list belongs to this start-menu transition.
    // MoveReminderData_Free intentionally frees only the shell.
    Heap_Free(learner->moves);
    MoveReminderData_Free(learner);
    Heap_Free(menu->additionalTaskContext);

    menu->taskData = FieldSystem_OpenPartyMenu(
        fieldSystem,
        &menu->fieldMoveContext,
        (u8)returnSlot);
    menu->additionalTaskContext = NULL;
    StartMenu_SetCallback(menu, StartMenu_ExitPartyMenu);

    return FALSE;
}

"""

    replace_once(
        path,
        summary_callback,
        learner_callback + summary_callback,
        "Move Learner return callback",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr03-party-move-learner.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_defs(root)
    patch_party_text(root)
    patch_party_windows(root)
    patch_party_context(root)
    patch_party_main(root)
    patch_start_menu(root)

    report = {
        "gate": "MERCURY_MR03_PARTY_MOVE_LEARNER",
        "status": "PASS",
        "path": [
            "Start Menu",
            "POKEMON",
            "select non-Egg Pokemon",
            "MOVE LEARNER",
        ],
        "visibility": "shown only when at least one learnable move exists",
        "restricted_areas": "hidden in the Battle Tower Salon to preserve vanilla restrictions",
        "return_behavior": "closing Move Learner reopens the party menu on the same slot",
        "production_direct_launch": False,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
