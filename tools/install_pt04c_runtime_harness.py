#!/usr/bin/env python3
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
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04c-runtime-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    field_map_change_c = root / "src/field_map_change.c"

    for path in (main_c, game_start_c, field_map_change_c):
        if not path.is_file():
            raise SystemExit(f"missing pinned pokeplatinum source file: {path}")

    # Harness-only fast path: bypass opening/title/Rowan interaction and run the
    # native new-save initializer directly. This patch is applied only inside the
    # PT04C CI workspace; no source under platinum-overlay is modified.
    replace_once(
        main_c,
        "EnqueueApplication(FS_OVERLAY_ID(game_opening), &gOpeningCutsceneAppTemplate);",
        "EnqueueApplication(FS_OVERLAY_ID(game_start), &gGameStartNewSaveAppTemplate);",
        "direct-new-save boot hook",
    )

    # The normal game reaches GameStartNewSave only after Rowan intro has already
    # called StartNewSave. The harness skips that intro, so initialize the blank
    # save explicitly before the normal NewSave initialization.
    replace_once(
        game_start_c,
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    StartNewSave(HEAP_ID_GAME_START, saveData);\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "blank-save initializer hook",
    )

    # Add only the native APIs required by the PT04C runtime gate.
    insert_include_once(
        field_map_change_c,
        '#include "constants/overworld_weather.h"\n',
        '#include "constants/items.h"\n\n#include "generated/species.h"\n',
        "Victini/constants includes",
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

        // PT04C runtime harness: create #494 through Platinum's normal gift-mon
        // path so party insertion and capture-record/Pokedex updates use native
        // engine code rather than a fabricated save structure.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_VICTINI,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));

        GF_ASSERT(Party_HasSpecies(SaveData_GetParty(fieldSystem->saveData), SPECIES_VICTINI));
        GF_ASSERT(Pokedex_HasSeenSpecies(SaveData_GetPokedex(fieldSystem->saveData), SPECIES_VICTINI));
        GF_ASSERT(Pokedex_HasCaughtSpecies(SaveData_GetPokedex(fieldSystem->saveData), SPECIES_VICTINI));

        (*state)++;
        break;"""
    replace_once(field_map_change_c, old_case0, new_case0, "Victini party/catch insertion")

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
    case 2:
        // Open the real native party application and leave it on screen for the
        // emulator proof capture. The automation will close it in later PT04C
        // phases when summary/PC/battle/save-reload checks are added.
        FieldSystem_OpenPartyMenu_SelectPokemon(0, fieldSystem);
        (*state)++;
        break;
    case 3:
        if (!FieldSystem_IsRunningApplication(fieldSystem)) {
            return TRUE;
        }
        break;
    }

    return FALSE;
}

void FieldSystem_SetLoadNewGameSpawnTask"""
    replace_once(field_map_change_c, old_cases, new_cases, "party UI launch hook")

    report = {
        "gate": "PT04C_VICTINI_NATIVE_PARTY_HARNESS_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "boot_path": "direct native new-save initializer",
        "species": "SPECIES_VICTINI",
        "species_id": 494,
        "level": 50,
        "native_checks": [
            "Pokemon_GiveMonFromScript returned TRUE",
            "Party_HasSpecies(SPECIES_VICTINI)",
            "Pokedex_HasSeenSpecies(SPECIES_VICTINI)",
            "Pokedex_HasCaughtSpecies(SPECIES_VICTINI)",
            "native party application launched",
        ],
        "next_if_passed": "capture/review party UI, then add summary runtime proof",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
