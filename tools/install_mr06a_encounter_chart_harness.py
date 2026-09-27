#!/usr/bin/env python3
"""Install a CI-only field harness for visual MR06A Encounter Chart proof.

Production behavior is not changed by this harness. It only:
- skips the opening/name flow into the native new-save initializer;
- starts the CI proof on Route 203, away from the rival trigger;
- marks the Pokédex as obtained so the normal Start Menu exposes ENCOUNTERS.

The proof still reaches the chart through ordinary controller input:
X -> move cursor to ENCOUNTERS -> A.
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
    ap.add_argument("--report", type=Path, default=Path("mr06a-encounter-chart-harness.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    location_c = root / "src/location.c"

    for path in (main_c, game_start_c, location_c):
        if not path.is_file():
            raise SystemExit(f"missing pinned pokeplatinum source file: {path}")

    replace_once(
        main_c,
        "EnqueueApplication(FS_OVERLAY_ID(game_opening), &gOpeningCutsceneAppTemplate);",
        "EnqueueApplication(FS_OVERLAY_ID(game_start), &gGameStartNewSaveAppTemplate);",
        "MR06A direct-new-save proof hook",
    )

    insert_include_once(
        game_start_c,
        '#include "constants/game_options.h"\n',
        '#include "constants/charcode.h"\n',
        "MR06A trainer-name constants include",
    )
    insert_include_once(
        game_start_c,
        '#include "savedata.h"\n',
        '#include "pokedex.h"\n',
        "MR06A Pokedex include",
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
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);\n"
        "    Pokedex_ObtainPokedex(SaveData_GetPokedex(saveData));",
        "MR06A new-save Pokedex proof setup",
    )

    replace_once(
        location_c,
        """static const Location sPlayerStartLocation = {
    .mapHeaderID = MAP_HEADER_TWINLEAF_TOWN_PLAYER_HOUSE_2F,
    .warpId = WARP_ID_NONE,
    .x = 4,
    .z = 6,
    .faceDirection = FACE_UP,
};""",
        """static const Location sPlayerStartLocation = {
    // CI-only MR06A proof point: Route 203, well east of the rival trigger.
    .mapHeaderID = MAP_HEADER_ROUTE_203,
    .warpId = WARP_ID_NONE,
    .x = 232,
    .z = 750,
    .faceDirection = FACE_DOWN,
};""",
        "MR06A Route 203 proof start",
    )

    report = {
        "gate": "MERCURY_MR06A_ENCOUNTER_CHART_HARNESS",
        "scope": "CI proof ROM only; clean player ROM staged before harness install",
        "boot_path": "direct native new-save initializer",
        "start_map": "MAP_HEADER_ROUTE_203",
        "start_x": 232,
        "start_z": 750,
        "pokedex_obtained": True,
        "direct_chart_launch": False,
        "required_runtime_input_path": [
            "X: Start Menu",
            "DOWN x5: ENCOUNTERS",
            "A: Encounter Chart",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
