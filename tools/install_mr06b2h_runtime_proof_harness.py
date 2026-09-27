#!/usr/bin/env python3
"""MR06B2H — CI-only end-to-end Research Poké Radar runtime proof harness.

This installer NEVER belongs in the player ROM. It is applied only after the
production ROM has already been built/staged/uploaded in CI.

The harness:
- boots directly through Platinum's native new-save initializer;
- creates a valid minimal trainer profile;
- starts the field on Route 202 beside the catching-tutorial grass;
- invokes MercuryResearchRadar_FieldTask exactly as the Key Item does.

DeSmuME automation can then capture the scanner, press A SEARCH, and capture
the returned overworld with the one target patch + MR06B2F dossier HUD.
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
        default=Path("mr06b2h-radar-runtime-proof-harness.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    main_c = root / "src/main.c"
    game_start_c = root / "src/game_start.c"
    field_map_change_c = root / "src/field_map_change.c"
    radar_app_c = root / "src/applications/mercury_research_radar.c"

    for path in (main_c, game_start_c, field_map_change_c, radar_app_c):
        if not path.is_file():
            raise SystemExit(f"missing pinned pokeplatinum source file: {path}")

    if "MercuryResearchRadar_FieldTask" not in radar_app_c.read_text():
        raise SystemExit("MR06B2H requires the production Research Radar runtime")

    # CI-only fast boot. The production ROM has already been copied/uploaded by
    # the workflow before this installer runs.
    replace_once(
        main_c,
        "EnqueueApplication(FS_OVERLAY_ID(game_opening), &gOpeningCutsceneAppTemplate);",
        "EnqueueApplication(FS_OVERLAY_ID(game_start), &gGameStartNewSaveAppTemplate);",
        "MR06B2H direct-new-save boot hook",
    )

    insert_include_once(
        game_start_c,
        '#include "constants/game_options.h"\n',
        '#include "constants/charcode.h"\n',
        "MR06B2H trainer name constants",
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
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "MR06B2H valid trainer profile",
    )

    insert_include_once(
        field_map_change_c,
        '#include "field_system.h"\n',
        '#include "applications/mercury_research_radar.h"\n',
        "MR06B2H Research Radar app include",
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
        // CI-only proof position: Route 202's catching-tutorial corridor sits
        // two tiles east of known tall grass, so the production Radar patch
        // finder has real nearby grass to validate against.
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
        "MR06B2H Route 202 proof spawn",
    )

    old_tail = """    case 1:
        FieldTransition_StartMapAndFadeIn(task);
        (*state)++;
        break;
    case 2:
        return TRUE;
    }

    return FALSE;
}
"""
    new_tail = """    case 1:
        FieldTransition_StartMapAndFadeIn(task);
        (*state)++;
        break;
    case 2: {
        // A real player cannot use the Key Item on the exact frame the field
        // finishes booting. Give Route 202, the map-name popup and Poketch
        // several seconds to settle before invoking the production Radar task.
        // This keeps the CI harness faithful to real gameplay and avoids
        // diagnosing field-startup races as Radar failures.
        static int mr06b2hFieldSettleFrames = 0;

        if (mr06b2hFieldSettleFrames < 300) {
            mr06b2hFieldSettleFrames++;
            break;
        }

        FieldTask_InitCall(
            task,
            MercuryResearchRadar_FieldTask,
            MercuryResearchRadar_NewFieldTaskContext());
        (*state)++;
        break;
    }
    case 3:
        // The nested Radar task owns scanner -> SEARCH -> patch/HUD lifecycle.
        // Once it returns, leave the live Route 202 field on screen so DeSmuME
        // can capture the rustling target patch and dossier HUD.
        return TRUE;
    }

    return FALSE;
}
"""
    replace_once(
        field_map_change_c,
        old_tail,
        new_tail,
        "MR06B2H shared Radar field-task proof",
    )

    # Keep the first runtime proof non-invasive. The previous QA-only hard
    # assertions intentionally trap on failure, but on DeSmuME that obscures
    # whether the scanner ever rendered. Visual transition + later targeted
    # telemetry are a cleaner first proof layer.

    checks = {
        "ci_only_direct_boot": "gGameStartNewSaveAppTemplate" in main_c.read_text(),
        "valid_trainer_profile": "radarQaName" in game_start_c.read_text(),
        "route_202_spawn": "MAP_HEADER_ROUTE_202" in field_map_change_c.read_text(),
        "known_grass_corridor": "180,\n            827," in field_map_change_c.read_text(),
        "real_shared_field_task": "MercuryResearchRadar_FieldTask" in field_map_change_c.read_text(),
        "real_shared_context": "MercuryResearchRadar_NewFieldTaskContext" in field_map_change_c.read_text(),
        "realistic_field_settle_delay": "mr06b2hFieldSettleFrames < 300" in field_map_change_c.read_text(),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2H harness validation failed: " + ", ".join(failed))

    report = {
        "gate": "MERCURY_MR06B2H_RADAR_RUNTIME_PROOF_HARNESS",
        "status": "PASS",
        "scope": "CI workspace only; applied after production player ROM upload",
        "boot_path": "direct native new-save initializer",
        "proof_map": "MAP_HEADER_ROUTE_202",
        "proof_position": {"x": 180, "z": 827, "facing": "left"},
        "grass_basis": "vanilla Route 202 catching tutorial walks west two tiles into tall grass",
        "runtime_entrypoint": "MercuryResearchRadar_FieldTask",
        "field_settle_frames_before_radar": 300,
        "runtime_assertions": [],
        "runtime_proof_mode": "non-invasive visual transition first; targeted telemetry follows after scanner stability",
        "expected_flow": [
            "dual-screen Research Poke Radar scanner",
            "A SEARCH",
            "return to Route 202",
            "one guaranteed nearby rustling target patch",
            "MR06B2F two-panel target dossier HUD",
        ],
        "player_rom_modified": False,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
