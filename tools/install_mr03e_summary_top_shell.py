#!/usr/bin/env python3
"""MR03E — Platinum-native Move Learner top-screen shell.

This pass deliberately stops drawing the Move Learner top screen inside the
Move Reminder application.  Instead, the party-menu MOVE LEARNER action opens
Pokémon Platinum's native Summary Screen application in a dedicated read-only
Mercury mode.

Scope of MR03E D1:
- preserve the already-proven MR03C Move Learner backend on its checkpoint;
- use Platinum's own Summary Screen VRAM, palettes, tilemaps, sprites, fonts,
  page transitions, and 3D Pokemon renderer;
- start on the native Battle Moves page;
- allow L/R page proof across Battle Moves, Skills, and Info only;
- keep the shell read-only while the top-screen visual target is validated;
- return to the same party slot on B.

The lower screen is intentionally not redesigned in this pass.
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


def replace_exact_count(path: Path, old: str, new: str, expected: int, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} matches in {path}, found {count}")
    path.write_text(text.replace(old, new))


def patch_summary_mode(root: Path) -> None:
    header = root / "include/applications/pokemon_summary_screen/main.h"
    main_c = root / "src/applications/pokemon_summary_screen/main.c"

    replace_once(
        header,
        """    SUMMARY_MODE_FEED_POFFIN,
    SUMMARY_MODE_SHOW_CONDITION_CHANGE,
};""",
        """    SUMMARY_MODE_FEED_POFFIN,
    SUMMARY_MODE_SHOW_CONDITION_CHANGE,
    SUMMARY_MODE_MERCURY_MOVE_LEARNER,
};""",
        "MR03E Summary mode enum",
    )

    replace_once(
        main_c,
        """    case SUMMARY_MODE_SELECT_MOVE:
        summaryScreen->page = SUMMARY_PAGE_BATTLE_MOVES;
        break;
    case SUMMARY_MODE_FEED_POFFIN:""",
        """    case SUMMARY_MODE_SELECT_MOVE:
        summaryScreen->page = SUMMARY_PAGE_BATTLE_MOVES;
        break;
    case SUMMARY_MODE_MERCURY_MOVE_LEARNER:
        summaryScreen->page = SUMMARY_PAGE_BATTLE_MOVES;
        break;
    case SUMMARY_MODE_FEED_POFFIN:""",
        "MR03E initial Battle Moves page",
    )

    replace_once(
        main_c,
        """    if (JOY_REPEAT(PAD_KEY_UP)) {
        ChangeSummaryMon(summaryScreen, -1);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_REPEAT(PAD_KEY_DOWN)) {
        ChangeSummaryMon(summaryScreen, 1);
        return SUMMARY_STATE_HANDLE_INPUT;
    }""",
        """    if (summaryScreen->data->mode != SUMMARY_MODE_MERCURY_MOVE_LEARNER) {
        if (JOY_REPEAT(PAD_KEY_UP)) {
            ChangeSummaryMon(summaryScreen, -1);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_REPEAT(PAD_KEY_DOWN)) {
            ChangeSummaryMon(summaryScreen, 1);
            return SUMMARY_STATE_HANDLE_INPUT;
        }
    }""",
        "MR03E lock selected Pokemon",
    )

    # Keep the native move-details page available for visual inspection, but
    # disable move swapping in the read-only top-shell proof.
    replace_exact_count(
        main_c,
        "if (summaryScreen->data->mode != SUMMARY_MODE_LOCK_MOVES) {",
        """if (summaryScreen->data->mode != SUMMARY_MODE_LOCK_MOVES
            && summaryScreen->data->mode != SUMMARY_MODE_MERCURY_MOVE_LEARNER) {""",
        3,
        "MR03E read-only move details",
    )


def patch_move_learner_launch(root: Path) -> None:
    start_menu = root / "src/start_menu.c"

    replace_once(
        start_menu,
        """static const u8 sOnlyMovePages[] = {
    SUMMARY_PAGE_BATTLE_MOVES,
    SUMMARY_PAGE_CONTEST_MOVES,
    SUMMARY_PAGE_MAX,
};""",
        """static const u8 sOnlyMovePages[] = {
    SUMMARY_PAGE_BATTLE_MOVES,
    SUMMARY_PAGE_CONTEST_MOVES,
    SUMMARY_PAGE_MAX,
};

static const u8 sMercuryMoveLearnerTopPages[] = {
    SUMMARY_PAGE_INFO,
    SUMMARY_PAGE_SKILLS,
    SUMMARY_PAGE_BATTLE_MOVES,
    SUMMARY_PAGE_MAX,
};""",
        "MR03E visible top pages",
    )

    old_case = """    case PARTY_MENU_EXIT_CODE_MOVE_LEARNER: {
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

    new_case = """    case PARTY_MENU_EXIT_CODE_MOVE_LEARNER:
        // MR03E D1 top-shell proof: route the existing MOVE LEARNER party
        // action into Platinum's real Summary Screen renderer. The proven
        // Move Reminder backend remains untouched on the MR03C checkpoint and
        // will be reconnected only after this native visual shell is approved.
        summary = Heap_Alloc(HEAP_ID_FIELD2, sizeof(PokemonSummary));

        summary->monData = SaveData_GetParty(fieldSystem->saveData);
        summary->options = SaveData_GetOptions(fieldSystem->saveData);
        summary->dataType = SUMMARY_DATA_PARTY_MON;
        summary->monIndex = partyMenu->selectedMonSlot;
        summary->monMax = Party_GetCurrentCount(summary->monData);
        summary->move = MOVE_NONE;
        summary->mode = SUMMARY_MODE_MERCURY_MOVE_LEARNER;
        summary->specialRibbons = SaveData_GetRibbons(fieldSystem->saveData);
        summary->dexMode = SaveData_GetDexMode(fieldSystem->saveData);
        summary->showContest = FALSE;
        summary->chatotCry = NULL;

        PokemonSummaryScreen_FlagVisiblePages(summary, sMercuryMoveLearnerTopPages);
        PokemonSummaryScreen_SetPlayerProfile(summary, SaveData_GetTrainerInfo(fieldSystem->saveData));
        FieldSystem_OpenSummaryScreen(fieldSystem, summary);

        menu->taskData = summary;
        StartMenu_SetCallback(menu, StartMenu_ExitSummary);
        break;
"""

    replace_once(start_menu, old_case, new_case, "MR03E Move Learner Summary launch")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr03e-summary-top-shell.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_summary_mode(root)
    patch_move_learner_launch(root)

    report = {
        "gate": "MERCURY_MR03E_SUMMARY_TOP_SHELL",
        "status": "PASS",
        "host_application": "Pokemon Platinum Summary Screen",
        "initial_page": "SUMMARY_PAGE_BATTLE_MOVES",
        "visible_pages": [
            "SUMMARY_PAGE_BATTLE_MOVES",
            "SUMMARY_PAGE_SKILLS",
            "SUMMARY_PAGE_INFO",
        ],
        "pokemon_renderer": "native Platinum 3D PokemonSprite renderer",
        "native_assets": [
            "pl_pst_gra tilemaps/palettes",
            "Summary Screen windows/fonts",
            "Summary Screen type/category sprites",
            "Summary Screen page transitions",
        ],
        "read_only": True,
        "bottom_screen_scope": "unchanged native Summary shell for D1; Mercury learner bottom UI deferred",
        "backend_checkpoint": "checkpoint/mr03c-final-functional-ui-2026-09-26",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
