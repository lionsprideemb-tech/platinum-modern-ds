#!/usr/bin/env python3
"""MR07B2 — CI-only runtime proof harness for the real Summary editors.

Applied after production MR07A + MR07B1 are installed and after the player ROM
has been staged. The harness gives a real Lv.50 Machamp, seeds a partial EV
spread, opens the native Summary on Skills, and verifies after the application
closes that the UI really committed both:
- HP EV -> 252, making the total exactly 510
- Primary Ability -> the species' second legal Ability

Production save flow is restored after the proof.
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
        default=Path("mr07b2-summary-editor-proof-harness.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    field_map_change_c = root / "src/field_map_change.c"
    summary_main_c = root / "src/applications/pokemon_summary_screen/main.c"
    summary_header = root / "include/applications/pokemon_summary_screen/main.h"

    for path in (
        main_c,
        game_start_c,
        field_map_change_c,
        summary_main_c,
        summary_header,
    ):
        if not path.is_file():
            raise SystemExit(f"MR07B2 missing required source: {path}")

    if "MERCURY_SKILLS_EDITOR_EV" not in summary_main_c.read_text():
        raise SystemExit("MR07B2 requires production MR07B1 EV editor")
    if "MERCURY_SKILLS_EDITOR_ABILITY" not in summary_main_c.read_text():
        raise SystemExit("MR07B2 requires production MR07B1 Ability editor")

    replace_once(
        main_c,
        "EnqueueApplication(FS_OVERLAY_ID(game_opening), &gOpeningCutsceneAppTemplate);",
        "EnqueueApplication(FS_OVERLAY_ID(game_start), &gGameStartNewSaveAppTemplate);",
        "MR07B2 direct new-save boot",
    )

    insert_include_once(
        game_start_c,
        '#include "constants/game_options.h"\n',
        '#include "constants/charcode.h"\n',
        "MR07B2 trainer chars",
    )

    replace_once(
        game_start_c,
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "    SaveData *saveData = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;\n"
        "    StartNewSave(HEAP_ID_GAME_START, saveData);\n"
        "    static const charcode_t editorQaName[] = { CHAR_E, CHAR_D, CHAR_I, CHAR_T, CHAR_O, CHAR_R, CHAR_EOS };\n"
        "    TrainerInfo *trainerInfo = SaveData_GetTrainerInfo(saveData);\n"
        "    TrainerInfo_SetName(trainerInfo, editorQaName);\n"
        "    TrainerInfo_SetGender(trainerInfo, 0);\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "MR07B2 proof save initialization",
    )

    insert_include_once(
        field_map_change_c,
        '#include "constants/overworld_weather.h"\n',
        '#include "constants/items.h"\n\n#include "generated/species.h"\n',
        "MR07B2 species/item constants",
    )
    insert_include_once(
        field_map_change_c,
        '#include "player_avatar.h"\n',
        '#include "party.h"\n#include "pokemon.h"\n',
        "MR07B2 Pokemon APIs",
    )
    insert_include_once(
        field_map_change_c,
        '#include "unk_0203D1B8.h"\n',
        '#include "unk_02054884.h"\n',
        "MR07B2 gift-mon API",
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

        // Machamp has two distinct native primary Abilities (Guts / No Guard),
        // making it a deterministic proof target for the real selector.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_MACHAMP,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));

        Pokemon *qaMon = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);

        u8 ev0 = 0;
        u8 ev6 = 6;
        u8 ev252 = 252;
        Pokemon_SetValue(qaMon, MON_DATA_HP_EV, &ev0);
        Pokemon_SetValue(qaMon, MON_DATA_ATK_EV, &ev252);
        Pokemon_SetValue(qaMon, MON_DATA_DEF_EV, &ev0);
        Pokemon_SetValue(qaMon, MON_DATA_SPEED_EV, &ev0);
        Pokemon_SetValue(qaMon, MON_DATA_SPATK_EV, &ev0);
        Pokemon_SetValue(qaMon, MON_DATA_SPDEF_EV, &ev6);

        u16 ability1 = (u16)SpeciesData_GetSpeciesValue(
            SPECIES_MACHAMP,
            SPECIES_DATA_ABILITY_1);
        u16 ability2 = (u16)SpeciesData_GetSpeciesValue(
            SPECIES_MACHAMP,
            SPECIES_DATA_ABILITY_2);
        GF_ASSERT(ability1 != 0);
        GF_ASSERT(ability2 != 0);
        GF_ASSERT(ability1 != ability2);
        Pokemon_SetValue(qaMon, MON_DATA_ABILITY, &ability1);
        Pokemon_CalcLevelAndStats(qaMon);

        (*state)++;
        break;
"""
    replace_once(
        field_map_change_c,
        old_case0,
        new_case0,
        "MR07B2 proof Machamp setup",
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
        FieldSystem_GetPartyMenuMonSummary(0, fieldSystem, 0);
        (*state)++;
        break;
    case 3:
        if (!FieldSystem_IsRunningApplication(fieldSystem)) {
            Pokemon *qaMon = Party_GetPokemonBySlotIndex(
                SaveData_GetParty(fieldSystem->saveData),
                0);
            u16 ability2 = (u16)SpeciesData_GetSpeciesValue(
                SPECIES_MACHAMP,
                SPECIES_DATA_ABILITY_2);

            // End-to-end commit assertions: these are reached only after the
            // DeSmuME script closes the real Summary application.
            GF_ASSERT(Pokemon_GetValue(
                qaMon,
                MON_DATA_HP_EV,
                NULL) == 252);
            GF_ASSERT(Pokemon_GetValue(
                qaMon,
                MON_DATA_ABILITY,
                NULL) == ability2);
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
        "MR07B2 Summary launch and commit assertions",
    )

    # CI-only convenience: production Summary still starts on Info.
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
        "MR07B2 proof initial Skills page",
    )

    checks = {
        "real_machamp": "SPECIES_MACHAMP" in field_map_change_c.read_text(),
        "two_ability_assertion":
            "SPECIES_DATA_ABILITY_1" in field_map_change_c.read_text()
            and "SPECIES_DATA_ABILITY_2" in field_map_change_c.read_text()
            and "GF_ASSERT(ability1 != ability2)" in field_map_change_c.read_text(),
        "partial_ev_seed":
            "MON_DATA_ATK_EV" in field_map_change_c.read_text()
            and "MON_DATA_SPDEF_EV" in field_map_change_c.read_text(),
        "commit_hp_ev_252":
            "MON_DATA_HP_EV" in field_map_change_c.read_text()
            and "== 252" in field_map_change_c.read_text(),
        "commit_second_ability":
            "MON_DATA_ABILITY" in field_map_change_c.read_text()
            and "== ability2" in field_map_change_c.read_text(),
        "native_summary": "FieldSystem_GetPartyMenuMonSummary" in field_map_change_c.read_text(),
        "production_editors_present":
            "MercurySkillsEditor_OpenEV" in summary_main_c.read_text()
            and "MercurySkillsEditor_OpenAbility" in summary_main_c.read_text(),
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR07B2 validation failed: " + ", ".join(failed))

    report = {
        "gate": "MERCURY_MR07B2_SUMMARY_EDITOR_RUNTIME_PROOF_HARNESS",
        "status": "PASS",
        "scope": "CI-only QA ROM; production player ROM staged before harness",
        "pokemon": "Machamp Lv50",
        "initial_primary_ability": "species Ability 1",
        "target_primary_ability": "species Ability 2",
        "initial_evs": {
            "hp": 0,
            "attack": 252,
            "defense": 0,
            "sp_attack": 0,
            "sp_defense": 6,
            "speed": 0,
            "total": 258,
        },
        "expected_final_evs": {
            "hp": 252,
            "attack": 252,
            "defense": 0,
            "sp_attack": 0,
            "sp_defense": 6,
            "speed": 0,
            "total": 510,
        },
        "initial_page": "SUMMARY_PAGE_SKILLS",
        "post_close_assertions": [
            "MON_DATA_HP_EV == 252",
            "MON_DATA_ABILITY == SPECIES_DATA_ABILITY_2",
        ],
        "player_rom_modified": False,
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
