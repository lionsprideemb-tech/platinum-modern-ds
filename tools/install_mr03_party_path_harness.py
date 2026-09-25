#!/usr/bin/env python3
"""Install a CI-only normal-party-path harness for MR03.

This does NOT launch the Move Learner. It only skips the intro/name screens,
creates a normal new save, gives the player a Garchomp, and leaves control on
the field. Runtime automation must open Start Menu -> POKEMON -> context menu
-> MOVE LEARNER using ordinary player input.
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
    ap.add_argument("--report", type=Path, default=Path("mr03-party-path-harness.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    field_map_change_c = root / "src/field_map_change.c"

    for path in (main_c, game_start_c, field_map_change_c):
        if not path.is_file():
            raise SystemExit(f"missing pinned pokeplatinum source file: {path}")

    # Skip only the opening/name flow. The field, Start Menu, party menu,
    # context menu, and Move Learner path remain production code.
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
        '#include "player_avatar.h"\n',
        '#include "pokedex.h"\n#include "party.h"\n#include "system_vars.h"\n',
        "party/Pokedex/system-vars includes",
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

        // CI-only setup. From here onward the proof uses normal player input.
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

        // Make the normal Start Menu expose POKEMON. The production build
        // reaches this state through the ordinary starter flow.
        GF_ASSERT(SystemVars_SetPlayerStarter(
            SaveData_GetVarsFlags(fieldSystem->saveData),
            SPECIES_GARCHOMP));

        (*state)++;
        break;"""
    replace_once(field_map_change_c, old_case0, new_case0, "Garchomp insertion")

    # The direct-new-save harness enters Twinleaf 2F before the opening TV
    # script has completed. Suppress that one CI-only on-frame message so the
    # proof starts from genuine free-field control rather than mistaking a
    # story textbox for a usable overworld state.
    house_script = root / "res/field/scripts/scripts_twinleaf_town_player_house_2f.s"
    old_tv = """TwinleafTownPlayerHouse2F_OnFrame_ConcludeSpecialProgram:
    LockAll
    SetVar VAR_PLAYER_HOUSE_SPECIAL_PROGRAM_STATE, 1
    Message TwinleafTownPlayerHouse2F_Text_ConcludesSpecialProgram
    PlayFanfare SEQ_TV_END_sseq
    Message TwinleafTownPlayerHouse2F_Text_SeeYouNextWeek
    WaitFanfare
    CloseMessage
    PlayDefaultMusic
    ReleaseAll
    End
"""
    new_tv = """TwinleafTownPlayerHouse2F_OnFrame_ConcludeSpecialProgram:
    SetVar VAR_PLAYER_HOUSE_SPECIAL_PROGRAM_STATE, 1
    End
"""
    replace_once(house_script, old_tv, new_tv, "CI opening-TV suppression")

    report = {
        "gate": "MERCURY_MR03_PARTY_PATH_HARNESS",
        "scope": "CI workspace only; production player ROM remains normal boot",
        "boot_path": "direct native new-save initializer",
        "setup_only": True,
        "species": "SPECIES_GARCHOMP",
        "level": 50,
        "starter_menu_unlock": "SystemVars_SetPlayerStarter(SPECIES_GARCHOMP)",
        "opening_tv_script_suppressed": True,
        "direct_party_launch": False,
        "direct_move_learner_launch": False,
        "required_runtime_input_path": [
            "X: Start Menu",
            "A: POKEMON",
            "A: selected Garchomp",
            "DOWN: MOVE LEARNER",
            "A: open MOVE LEARNER",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
