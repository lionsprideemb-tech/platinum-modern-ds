#!/usr/bin/env python3
"""MR07A2 — CI-only runtime proof harness for Mercury Summary Skills.

Applied only after the production Mercury player ROM has already been staged.

The harness fast-boots a clean new save, gives the player a real native
Empoleon with a deliberately visible 510-EV spread, opens Platinum's real
Summary application, and leaves all production Summary rendering/input code
untouched. DeSmuME drives the real page navigation and MR07A X edit-selection.
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
        default=Path("mr07a2-summary-skills-proof-harness.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    field_map_change_c = root / "src/field_map_change.c"
    summary_main_c = root / "src/applications/pokemon_summary_screen/main.c"
    summary_window_c = root / "src/applications/pokemon_summary_screen/window.c"

    for path in (
        main_c,
        game_start_c,
        field_map_change_c,
        summary_main_c,
        summary_window_c,
    ):
        if not path.is_file():
            raise SystemExit(f"MR07A2 missing required source: {path}")

    if "mercurySkillsEditMode" not in summary_main_c.read_text():
        raise SystemExit("MR07A2 requires MR07A Skills edit-selection")
    if "SUMMARY_WINDOW_MERCURY_SKILLS_PANEL" not in summary_window_c.read_text():
        raise SystemExit("MR07A2 requires MR07A native Skills renderer")

    # CI-only direct new-save boot. The player ROM has already been staged.
    replace_once(
        main_c,
        "EnqueueApplication(FS_OVERLAY_ID(game_opening), &gOpeningCutsceneAppTemplate);",
        "EnqueueApplication(FS_OVERLAY_ID(game_start), &gGameStartNewSaveAppTemplate);",
        "MR07A2 direct new-save boot",
    )

    insert_include_once(
        game_start_c,
        '#include "constants/game_options.h"\n',
        '#include "constants/charcode.h"\n',
        "MR07A2 trainer chars",
    )

    replace_once(
        game_start_c,
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    StartNewSave(HEAP_ID_GAME_START, saveData);\n"
        "    static const charcode_t summaryQaName[] = { CHAR_M, CHAR_E, CHAR_R, CHAR_C, CHAR_U, CHAR_R, CHAR_Y, CHAR_EOS };\n"
        "    TrainerInfo *trainerInfo = SaveData_GetTrainerInfo(saveData);\n"
        "    TrainerInfo_SetName(trainerInfo, summaryQaName);\n"
        "    TrainerInfo_SetGender(trainerInfo, 0);\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "MR07A2 proof save initialization",
    )

    insert_include_once(
        field_map_change_c,
        '#include "constants/overworld_weather.h"\n',
        '#include "constants/items.h"\n\n#include "generated/species.h"\n',
        "MR07A2 item/species includes",
    )
    insert_include_once(
        field_map_change_c,
        '#include "player_avatar.h"\n',
        '#include "party.h"\n#include "pokemon.h"\n',
        "MR07A2 party/Pokemon includes",
    )
    insert_include_once(
        field_map_change_c,
        '#include "unk_0203D1B8.h"\n',
        '#include "unk_02054884.h"\n',
        "MR07A2 give-mon include",
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

        // CI-only visual-proof mon. This uses the native gift path and native
        // boxed Pokemon storage; no fake Summary data is injected.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_EMPOLEON,
            50,
            ITEM_LEFTOVERS,
            fieldSystem->location->mapHeaderID,
            0));

        Pokemon *summaryQaMon = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);

        // Visible legal modern EV spread: 252 HP / 252 Sp.Atk / 6 Sp.Def.
        // MR07A reads these values through the production Pokemon getters.
        u8 ev252 = 252;
        u8 ev6 = 6;
        u8 ev0 = 0;
        Pokemon_SetValue(summaryQaMon, MON_DATA_HP_EV, &ev252);
        Pokemon_SetValue(summaryQaMon, MON_DATA_ATK_EV, &ev0);
        Pokemon_SetValue(summaryQaMon, MON_DATA_DEF_EV, &ev0);
        Pokemon_SetValue(summaryQaMon, MON_DATA_SPEED_EV, &ev0);
        Pokemon_SetValue(summaryQaMon, MON_DATA_SPATK_EV, &ev252);
        Pokemon_SetValue(summaryQaMon, MON_DATA_SPDEF_EV, &ev6);
        Pokemon_CalcLevelAndStats(summaryQaMon);

        (*state)++;
        break;
"""
    replace_once(
        field_map_change_c,
        old_case0,
        new_case0,
        "MR07A2 proof Pokemon insertion",
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
        // Open Platinum's real normal Summary application on the real party
        // Pokemon. DeSmuME will use Right, Right to reach Skills, then X and
        // D-pad navigation to prove MR07A's player-facing interaction.
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
        "MR07A2 Summary launch",
    )

    checks = {
        "direct_boot": "gGameStartNewSaveAppTemplate" in main_c.read_text(),
        "real_empoleon": "SPECIES_EMPOLEON" in field_map_change_c.read_text(),
        "native_gift_path": "Pokemon_GiveMonFromScript" in field_map_change_c.read_text(),
        "legal_510_ev_spread":
            "MON_DATA_HP_EV" in field_map_change_c.read_text()
            and "MON_DATA_SPATK_EV" in field_map_change_c.read_text()
            and "MON_DATA_SPDEF_EV" in field_map_change_c.read_text(),
        "native_summary_launch":
            "FieldSystem_GetPartyMenuMonSummary(0, fieldSystem, 0)"
            in field_map_change_c.read_text(),
        "production_x_edit_code_untouched":
            "PAD_BUTTON_X" in summary_main_c.read_text()
            and "mercurySkillsCursor = 7" in summary_main_c.read_text(),
        "production_renderer_untouched":
            "SUMMARY_WINDOW_MERCURY_SKILLS_PANEL" in summary_window_c.read_text()
            and "PokemonSummary_Text_MercuryInnate3" in summary_window_c.read_text(),
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR07A2 validation failed: " + ", ".join(failed))

    report = {
        "gate": "MERCURY_MR07A2_NATIVE_SUMMARY_SKILLS_RUNTIME_PROOF_HARNESS",
        "status": "PASS",
        "scope": "CI-only; production player ROM staged before harness",
        "pokemon": {
            "species": "Empoleon",
            "level": 50,
            "held_item": "Leftovers",
            "evs": {
                "hp": 252,
                "attack": 0,
                "defense": 0,
                "special_attack": 252,
                "special_defense": 6,
                "speed": 0,
                "total": 510,
            },
        },
        "application": "Platinum native Pokemon Summary Screen",
        "production_summary_code_modified_by_harness": False,
        "expected_emulator_flow": [
            "normal Summary Info page",
            "Right x2 -> Mercury Skills",
            "X -> edit-selection with primary Ability highlighted",
            "Up x4 -> Sp.Atk selected, EV 252 / total 510 visible",
        ],
        "player_rom_modified": False,
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
