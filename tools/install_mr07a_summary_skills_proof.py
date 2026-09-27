#!/usr/bin/env python3
"""MR07A — CI-only real-ROM proof harness for the Mercury Skills screen.

Applied only after the production player ROM has already been staged.

The harness:
- fast-boots a clean new save;
- gives a real Lv.50 Garchomp through Platinum's normal gift path;
- assigns a legal 510-EV test spread through real Pokemon data setters;
- opens the normal Platinum Summary application directly;
- forces the QA ROM to begin on SUMMARY_PAGE_SKILLS;
- leaves the production bottom Summary screen untouched.

No production save flow or player ROM is modified by this harness.
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
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr07a-summary-skills-proof-harness.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    field_map_change_c = root / "src/field_map_change.c"
    summary_main_c = root / "src/applications/pokemon_summary_screen/main.c"
    summary_window_c = root / "src/applications/pokemon_summary_screen/window.c"

    for path in (main_c, game_start_c, field_map_change_c, summary_main_c, summary_window_c):
        if not path.is_file():
            raise SystemExit(f"MR07A proof missing required source: {path}")

    if "SUMMARY_WINDOW_MERCURY_SKILLS_PANEL" not in (
        root / "include/applications/pokemon_summary_screen/main.h"
    ).read_text():
        raise SystemExit("MR07A proof requires the production Mercury Skills renderer")

    # CI-only fast boot. The production ROM is staged before this harness.
    replace_once(
        main_c,
        "EnqueueApplication(FS_OVERLAY_ID(game_opening), &gOpeningCutsceneAppTemplate);",
        "EnqueueApplication(FS_OVERLAY_ID(game_start), &gGameStartNewSaveAppTemplate);",
        "MR07A direct new-save boot",
    )

    insert_include_once(
        game_start_c,
        '#include "constants/game_options.h"\n',
        '#include "constants/charcode.h"\n',
        "MR07A trainer-name chars",
    )

    replace_once(
        game_start_c,
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    StartNewSave(HEAP_ID_GAME_START, saveData);\n"
        "    static const charcode_t skillsQaName[] = { CHAR_S, CHAR_K, CHAR_I, CHAR_L, CHAR_L, CHAR_S, CHAR_EOS };\n"
        "    TrainerInfo *trainerInfo = SaveData_GetTrainerInfo(saveData);\n"
        "    TrainerInfo_SetName(trainerInfo, skillsQaName);\n"
        "    TrainerInfo_SetGender(trainerInfo, 0);\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "MR07A proof save initialization",
    )

    insert_include_once(
        field_map_change_c,
        '#include "constants/overworld_weather.h"\n',
        '#include "constants/items.h"\n\n#include "generated/species.h"\n',
        "MR07A proof species/item constants",
    )
    insert_include_once(
        field_map_change_c,
        '#include "player_avatar.h"\n',
        '#include "party.h"\n#include "pokemon.h"\n',
        "MR07A proof Pokemon APIs",
    )
    insert_include_once(
        field_map_change_c,
        '#include "unk_0203D1B8.h"\n',
        '#include "unk_02054884.h"\n',
        "MR07A proof gift-mon API",
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
        FieldMapChange_SetNewLocation(fieldSystem, fieldSystem->location);
        FieldMapChange_InitTerrainCollisionManager(fieldSystem);
        FieldMapChange_UpdateGameData(fieldSystem, 0);
        FieldMapChange_CreateObjects(fieldSystem);

        // Real Pokemon data, real Summary application. Garchomp gives the
        // compact stat panel enough width pressure to expose spacing issues.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_GARCHOMP,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));

        Pokemon *qaMon = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);
        u8 evHp = 6;
        u8 evAtk = 252;
        u8 evSpeed = 252;
        Pokemon_SetValue(qaMon, MON_DATA_HP_EV, &evHp);
        Pokemon_SetValue(qaMon, MON_DATA_ATK_EV, &evAtk);
        Pokemon_SetValue(qaMon, MON_DATA_SPEED_EV, &evSpeed);
        Pokemon_CalcLevelAndStats(qaMon);

        (*state)++;
        break;
"""
    replace_once(
        field_map_change_c,
        old_case0,
        new_case0,
        "MR07A proof Garchomp/EV setup",
    )

    old_cases = """    case 1:
        FieldTransition_StartMapAndFadeIn(task);
        (*state)++;
        break;
    case 2:
        return TRUE;
    }

    return FALSE;
}
"""
    new_cases = """    case 1:
        FieldTransition_StartMapAndFadeIn(task);
        (*state)++;
        break;
    case 2:
        // Open Platinum's normal Summary application. The proof-only initial
        // page override below starts it on Mercury's Skills page.
        FieldSystem_GetPartyMenuMonSummary(0, fieldSystem, 0);
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
"""
    replace_once(
        field_map_change_c,
        old_cases,
        new_cases,
        "MR07A proof Summary launch",
    )

    # QA ROM only: normal production Summary still starts on Info.
    replace_once(
        summary_main_c,
        """    case SUMMARY_MODE_NORMAL:
    case SUMMARY_MODE_LOCK_MOVES:
        if (summaryScreen->monData.isEgg == FALSE) {
            summaryScreen->page = SUMMARY_PAGE_INFO;
        } else {
            summaryScreen->page = SUMMARY_PAGE_MEMO;
        }
        break;""",
        """    case SUMMARY_MODE_NORMAL:
    case SUMMARY_MODE_LOCK_MOVES:
        if (summaryScreen->monData.isEgg == FALSE) {
            summaryScreen->page = SUMMARY_PAGE_SKILLS;
        } else {
            summaryScreen->page = SUMMARY_PAGE_MEMO;
        }
        break;""",
        "MR07A proof initial Skills page",
    )

    checks = {
        "direct_boot": "gGameStartNewSaveAppTemplate" in main_c.read_text(),
        "real_garchomp": "SPECIES_GARCHOMP" in field_map_change_c.read_text(),
        "real_ev_setters":
            "MON_DATA_ATK_EV" in field_map_change_c.read_text()
            and "MON_DATA_SPEED_EV" in field_map_change_c.read_text(),
        "real_summary_entrypoint":
            "FieldSystem_GetPartyMenuMonSummary" in field_map_change_c.read_text(),
        "skills_initial_page":
            "summaryScreen->page = SUMMARY_PAGE_SKILLS;" in summary_main_c.read_text(),
        "x_edit_mode":
            "PAD_BUTTON_X" in summary_main_c.read_text()
            and "mercurySkillsEditMode" in summary_main_c.read_text(),
        "native_panel":
            "Window_FillRectWithColor(panel" in summary_window_c.read_text(),
        "production_player_rom_modified": False,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR07A proof validation failed: " + ", ".join(failed))

    report = {
        "gate": "MERCURY_MR07A_SUMMARY_SKILLS_REAL_ROM_PROOF",
        "status": "PASS",
        "scope": "CI-only QA ROM; production player ROM already staged",
        "pokemon": {
            "species": "Garchomp",
            "level": 50,
            "evs": {
                "HP": 6,
                "Attack": 252,
                "Defense": 0,
                "SpAtk": 0,
                "SpDef": 0,
                "Speed": 252,
                "total": 510,
            },
        },
        "entrypoint": "FieldSystem_GetPartyMenuMonSummary",
        "initial_page": "SUMMARY_PAGE_SKILLS",
        "bottom_screen": "normal Platinum Summary radial navigator",
        "expected_proof_frames": [
            "normal Mercury Skills page",
            "X edit-selection with primary Ability highlighted",
            "D-pad moved to HP with live EV 6 / total 510 detail",
        ],
        "player_rom_modified": False,
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
