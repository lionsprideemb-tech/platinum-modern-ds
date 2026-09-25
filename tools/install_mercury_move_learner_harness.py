#!/usr/bin/env python3
"""Install a CI-only direct boot into Mercury's DS Move Learner.

The production game is not changed by this harness.  It creates a normal
Garchomp through native engine APIs, verifies the universal learner has moves,
and opens the real Move Reminder/Move Learner application for emulator capture.
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


def insert_include_once(path: Path, anchor: str, include_line: str, label: str) -> None:
    text = path.read_text()
    if include_line in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one include anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + include_line, 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mercury-move-learner-harness.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    field_map_change_c = root / "src/field_map_change.c"

    for path in (main_c, game_start_c, field_map_change_c):
        if not path.is_file():
            raise SystemExit(f"missing pinned pokeplatinum source file: {path}")

    # Skip opening/Rowan only inside CI, using Platinum's normal new-save app.
    replace_once(
        main_c,
        "EnqueueApplication(FS_OVERLAY_ID(game_opening), &gOpeningCutsceneAppTemplate);",
        "EnqueueApplication(FS_OVERLAY_ID(game_start), &gGameStartNewSaveAppTemplate);",
        "direct-new-save boot hook",
    )

    insert_include_once(
        game_start_c,
        '#include "constants/game_options.h"\n',
        '#include "constants/charcode.h"\n',
        "CI trainer-name constants include",
    )
    replace_once(
        game_start_c,
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    StartNewSave(HEAP_ID_GAME_START, saveData);\n"
        "    static const charcode_t mercuryTrainerName[] = { CHAR_M, CHAR_E, CHAR_R, CHAR_C, CHAR_U, CHAR_R, CHAR_Y, CHAR_EOS };\n"
        "    TrainerInfo *trainerInfo = SaveData_GetTrainerInfo(saveData);\n"
        "    TrainerInfo_SetName(trainerInfo, mercuryTrainerName);\n"
        "    TrainerInfo_SetGender(trainerInfo, 0);\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "blank-save initializer hook",
    )

    insert_include_once(
        field_map_change_c,
        '#include "constants/overworld_weather.h"\n',
        '#include "constants/items.h"\n\n#include "generated/species.h"\n',
        "Garchomp/constants includes",
    )
    insert_include_once(
        field_map_change_c,
        '#include "message.h"\n',
        '#include "move_reminder_data.h"\n',
        "Move Learner include",
    )
    insert_include_once(
        field_map_change_c,
        '#include "player_avatar.h"\n',
        '#include "pokedex.h"\n#include "party.h"\n',
        "party/Pokedex includes",
    )
    insert_include_once(
        field_map_change_c,
        '#include "unk_0203D1B8.h"\n',
        '#include "unk_02054884.h"\n',
        "give-mon include",
    )

    old_case0 = """        FieldMapChange_UpdateGameData(fieldSystem, 0);
        FieldMapChange_CreateObjects(fieldSystem);
        (*state)++;
        break;"""
    new_case0 = """        FieldMapChange_UpdateGameData(fieldSystem, 0);
        FieldMapChange_CreateObjects(fieldSystem);

        // CI-only Move Learner proof: use Platinum's normal gift-mon path.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_GARCHOMP,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));

        GF_ASSERT(Party_HasSpecies(
            SaveData_GetParty(fieldSystem->saveData),
            SPECIES_GARCHOMP));
        GF_ASSERT(Pokedex_HasSeenSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_GARCHOMP));

        (*state)++;
        break;"""
    replace_once(field_map_change_c, old_case0, new_case0, "Garchomp insertion")

    old_cases = """    case 1:
        FieldTransition_StartMapAndFadeIn(task);
        (*state)++;
        break;
    case 2:
        return TRUE;
    }

    return FALSE;
}

void FieldSystem_SetLoadNewGameSpawnTask"""

    new_cases = """    case 1:
        FieldTransition_StartMapAndFadeIn(task);
        (*state)++;
        break;
    case 2: {
        // Launch the production Move Learner application directly so CI can
        // capture its real DS rendering without walking through the story.
        Pokemon *mon = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData), 0);
        u16 *moves = MoveReminderData_GetMoves(mon, HEAP_ID_FIELD3);
        GF_ASSERT(MoveReminderData_HasMoves(moves));

        MoveReminderData *learner = MoveReminderData_Alloc(HEAP_ID_FIELD3);
        learner->mon = mon;
        learner->trainerInfo = SaveData_GetTrainerInfo(fieldSystem->saveData);
        learner->options = SaveData_GetOptions(fieldSystem->saveData);
        learner->moves = moves;
        learner->isMoveTutor = TRUE;

        // The harness intentionally keeps learner/moves alive for the entire
        // capture. Production script ownership remains unchanged.
        FieldSystem_OpenMoveReminderMenu(fieldSystem, learner);
        (*state)++;
        break;
    }
    case 3:
        if (!FieldSystem_IsRunningApplication(fieldSystem)) {
            return TRUE;
        }
        break;
    }

    return FALSE;
}

void FieldSystem_SetLoadNewGameSpawnTask"""
    replace_once(field_map_change_c, old_cases, new_cases, "Move Learner launch hook")

    report = {
        "gate": "MERCURY_DS_MOVE_LEARNER_RUNTIME_HARNESS",
        "scope": "CI workspace only; production game flow unchanged",
        "boot_path": "direct native new-save initializer",
        "species": "SPECIES_GARCHOMP",
        "level": 50,
        "native_entrypoint": "FieldSystem_OpenMoveReminderMenu",
        "backend_entrypoint": "MoveReminderData_GetMoves",
        "expected_label": "MOVE LEARNER",
        "expected_screen": "native Platinum DS Move Reminder shell with Mercury universal move pool",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
