#!/usr/bin/env python3
"""MR06B2O — CI-only proof harness for the production Pokétch Research Radar.

Applied only after the production MR06B2N ROM has already been staged.

Unlike the obsolete MR06B2H/K/L/M proofs, this harness does not launch the old
full-screen scanner and does not rewrite Pokémon History. It boots a clean new
save on Route 202 with the actual production Research Radar Pokétch app selected.
DeSmuME then exercises the real touch targets: area icon -> detail -> SEARCH.
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
        raise SystemExit(f"{label}: include anchor count {count}")
    path.write_text(text.replace(anchor, anchor + include_line, 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2o-production-poketch-proof-harness.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    field_map_change_c = root / "src/field_map_change.c"
    radar_main_c = root / "src/applications/poketch/unused/4/main.c"
    history_c = root / "src/applications/poketch/pokemon_history/main.c"

    for path in (main_c, game_start_c, field_map_change_c, radar_main_c, history_c):
        if not path.is_file():
            raise SystemExit(f"MR06B2O missing required source: {path}")

    if "POKETCH_APPID_RESEARCHRADAR" not in (
        root / "generated/poketch_apps.txt"
    ).read_text():
        raise SystemExit("MR06B2O requires production MR06B2N app ID")

    if "MercuryResearchRadar_RequestInstantEncounter" not in radar_main_c.read_text():
        raise SystemExit("MR06B2O requires production instant-search Pokétch app")

    # CI-only fast boot. The production ROM is staged before this harness.
    replace_once(
        main_c,
        "EnqueueApplication(FS_OVERLAY_ID(game_opening), &gOpeningCutsceneAppTemplate);",
        "EnqueueApplication(FS_OVERLAY_ID(game_start), &gGameStartNewSaveAppTemplate);",
        "MR06B2O direct new-save boot",
    )

    insert_include_once(
        game_start_c,
        '#include "constants/game_options.h"\n',
        '#include "constants/charcode.h"\n',
        "MR06B2O trainer chars",
    )
    insert_include_once(
        game_start_c,
        '#include "constants/charcode.h"\n',
        '#include "generated/species.h"\n',
        "MR06B2O species include",
    )
    insert_include_once(
        game_start_c,
        '#include "generated/species.h"\n',
        '#include "pokedex.h"\n',
        "MR06B2O Pokedex include",
    )
    insert_include_once(
        game_start_c,
        '#include "pokedex.h"\n',
        '#include "poketch.h"\n',
        "MR06B2O Poketch include",
    )

    replace_once(
        game_start_c,
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    StartNewSave(HEAP_ID_GAME_START, saveData);\n"
        "    static const charcode_t radarQaName[] = { CHAR_R, CHAR_A, CHAR_D, CHAR_A, CHAR_R, CHAR_EOS };\n"
        "    TrainerInfo *trainerInfo = SaveData_GetTrainerInfo(saveData);\n"
        "    TrainerInfo_SetName(trainerInfo, radarQaName);\n"
        "    TrainerInfo_SetGender(trainerInfo, 0);\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);\n"
        "\n"
        "    // CI-only proof state: make the actual production Pokétch app the\n"
        "    // selected lower-screen app. No Pokémon History substitution.\n"
        "    Poketch *poketch = SaveData_GetPoketch(saveData);\n"
        "    Poketch_Enable(poketch);\n"
        "    Poketch_RegisterApp(poketch, POKETCH_APPID_RESEARCHRADAR);\n"
        "    poketch->appIndex = POKETCH_APPID_RESEARCHRADAR;\n"
        "\n"
        "    // Give the detail screen a nonzero real Search Level so its visual\n"
        "    // separation from battle level is exercised in the proof only.\n"
        "    Pokedex_MercuryRadar_SetSearchLevel(\n"
        "        SaveData_GetPokedex(saveData),\n"
        "        SPECIES_BIDOOF,\n"
        "        27);",
        "MR06B2O proof save initialization",
    )

    old_case0 = """    case 0:
        FieldMapChange_SetNewLocation(fieldSystem, fieldSystem->location);
        FieldMapChange_InitTerrainCollisionManager(fieldSystem);
        FieldMapChange_UpdateGameData(fieldSystem, 0);
        FieldMapChange_CreateObjects(fieldSystem);
        (*state)++;
        break;
"""
    new_case0 = """    case 0:
        // CI-only proof location. Route 202 has a compact early-game encounter
        // table and leaves the top screen as a normal live Platinum overworld.
        Location_Set(
            fieldSystem->location,
            MAP_HEADER_ROUTE_202,
            WARP_ID_NONE,
            180,
            827,
            FACE_LEFT);

        FieldMapChange_SetNewLocation(fieldSystem, fieldSystem->location);
        FieldMapChange_InitTerrainCollisionManager(fieldSystem);
        FieldMapChange_UpdateGameData(fieldSystem, 0);
        FieldMapChange_CreateObjects(fieldSystem);
        (*state)++;
        break;
"""
    replace_once(
        field_map_change_c,
        old_case0,
        new_case0,
        "MR06B2O Route 202 proof spawn",
    )

    checks = {
        "direct_boot": "gGameStartNewSaveAppTemplate" in main_c.read_text(),
        "route_202": "MAP_HEADER_ROUTE_202" in field_map_change_c.read_text(),
        "production_app_selected": "POKETCH_APPID_RESEARCHRADAR" in game_start_c.read_text(),
        "poketch_enabled": "Poketch_Enable(poketch)" in game_start_c.read_text(),
        "search_level_27": "SPECIES_BIDOOF" in game_start_c.read_text()
            and "27);" in game_start_c.read_text(),
        "real_area_app": "BuildCurrentAreaTargets" in radar_main_c.read_text(),
        "real_instant_search": "MercuryResearchRadar_RequestInstantEncounter" in radar_main_c.read_text(),
        "pokemon_history_untouched": "RESEARCH RADAR" not in history_c.read_text(),
        "old_scanner_not_forced": "MercuryResearchRadar_FieldTask" not in field_map_change_c.read_text(),
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2O validation failed: " + ", ".join(failed))

    report = {
        "gate": "MERCURY_MR06B2O_PRODUCTION_POKETCH_PROOF_HARNESS",
        "status": "PASS",
        "scope": "CI-only; production player ROM already staged before this harness",
        "proof_map": "MAP_HEADER_ROUTE_202",
        "proof_position": {"x": 180, "z": 827, "facing": "left"},
        "selected_app": "POKETCH_APPID_RESEARCHRADAR",
        "top_screen": "normal live Platinum overworld",
        "bottom_screen": "actual production MR06B2N Research Radar app",
        "pokemon_history_modified": False,
        "old_fullscreen_scanner_launched": False,
        "qa_search_level": {"species": "Bidoof", "value": 27},
        "emulator_inputs": [
            "touch first current-area Pokemon icon",
            "touch SEARCH on detail page",
        ],
        "expected_flow": [
            "production Poketch area grid",
            "production Poketch detail page",
            "immediate normal wild battle transition",
        ],
        "player_rom_modified": False,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
