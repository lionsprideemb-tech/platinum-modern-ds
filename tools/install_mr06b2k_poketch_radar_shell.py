#!/usr/bin/env python3
"""MR06B2K — CI-only Pokétch-native Research Radar area-page visual proof.

This is intentionally a visual prototype, not the production scanner rewrite.
It reuses Platinum's real Pokémon History Pokétch app renderer because that app
already provides the exact ingredients we want to validate first:
- untouched overworld on the top screen;
- real Pokétch shell / palette / side buttons on the bottom screen;
- 3x4 touchable Pokémon icon grid inside the LCD.

For the QA ROM only, Pokémon History is temporarily fed current-area Mercury
Research Radar targets and retitled RESEARCH RADAR. If this visual foundation
looks right, the next production phase gets its own app identity and detail page.
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


def patch_history_main(root: Path) -> None:
    path = root / "src/applications/poketch/pokemon_history/main.c"

    replace_once(
        path,
        '#include "bg_window.h"\n',
        '#include "bg_window.h"\n'
        '#include "generated/species.h"\n',
        "MR06B2K species constants include",
    )

    old = """    Poketch *poketch = PoketchSystem_GetPoketchData(poketchSys);
    appData->history.count = Poketch_PokemonHistorySize(poketch);

    for (int i = 0; i < appData->history.count; i++) {
        Poketch_PokemonHistorySpeciesAndIcon(poketch, i, &appData->history.mons[i].species, &appData->history.mons[i].icon);
        appData->history.mons[i].form = Poketch_PokemonHistoryForm(poketch, i);
    }
"""
    new = """    // CI-only visual proof set, sourced directly from Mercury's authored
    // Route 202 Morning table. Hardcoding here avoids illegal cross-overlay
    // calls from the Pokétch app into overlay006; production wiring will use a
    // main-memory handoff owned by the field/Radar runtime.
    static const u16 radarProofSpecies[MAX_HISTORY_SIZE] = {
        SPECIES_BIDOOF,
        SPECIES_STARLY,
        SPECIES_SHINX,
        SPECIES_KRICKETOT,
        SPECIES_BUDEW,
        SPECIES_FLETCHLING,
        SPECIES_LILLIPUP,
        SPECIES_PAWMI,
        SPECIES_BUNEARY,
        SPECIES_GRUBBIN,
        SPECIES_RALTS,
        SPECIES_ROCKRUFF,
    };

    MI_CpuClear8(&appData->history, sizeof(appData->history));
    appData->history.count = MAX_HISTORY_SIZE;

    for (int i = 0; i < MAX_HISTORY_SIZE; i++) {
        appData->history.mons[i].species = radarProofSpecies[i];
        appData->history.mons[i].icon = 0;
        appData->history.mons[i].form = 0;
    }
"""
    replace_once(path, old, new, "MR06B2K authored Route 202 proof grid")


def patch_history_title(root: Path) -> None:
    path = root / "res/text/poketch_pokemon_history.json"
    data = json.loads(path.read_text())
    messages = data.get("messages", [])
    if len(messages) != 1:
        raise SystemExit("MR06B2K expected one Pokémon History title message")
    messages[0]["en_US"] = "RESEARCH RADAR"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def patch_history_graphics(root: Path) -> None:
    path = root / "include/applications/poketch/pokemon_history/graphics.h"
    text = path.read_text()
    # Keep the canonical 12-target count, but give the icons more breathing room
    # than the old acquisition-history layout.
    text = text.replace("#define HISTORY_ICON_STEP_X 40", "#define HISTORY_ICON_STEP_X 44")
    text = text.replace("#define HISTORY_ICON_STEP_Y 48", "#define HISTORY_ICON_STEP_Y 44")
    path.write_text(text)

    path = root / "src/applications/poketch/pokemon_history/graphics.c"
    text = path.read_text()
    text = text.replace(
        ".translation = { FX32_CONST(48 + HISTORY_ICON_STEP_X * c), \\\n"
        "            FX32_CONST(48 + HISTORY_ICON_STEP_Y * r) },",
        ".translation = { FX32_CONST(36 + HISTORY_ICON_STEP_X * c), \\\n"
        "            FX32_CONST(54 + HISTORY_ICON_STEP_Y * r) },",
    )
    path.write_text(text)


def patch_qa_boot(root: Path) -> None:
    game_start = root / "src/game_start.c"
    field_map = root / "src/field_map_change.c"

    game_text = game_start.read_text()
    if '#include "poketch.h"\n' not in game_text:
        anchor = '#include "play_time_manager.h"\n'
        if game_text.count(anchor) != 1:
            raise SystemExit("MR06B2K missing game_start Pokétch include anchor")
        game_start.write_text(
            game_text.replace(anchor, anchor + '#include "poketch.h"\n', 1)
        )

    replace_once(
        game_start,
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "    Poketch *mr06b2kPoketch = SaveData_GetPoketch(saveData);\n"
        "    Poketch_Enable(mr06b2kPoketch);\n"
        "    Poketch_RegisterApp(mr06b2kPoketch, POKETCH_APPID_POKEMONHISTORY);\n"
        "    mr06b2kPoketch->appIndex = POKETCH_APPID_POKEMONHISTORY;\n"
        "    InitializeNewSave(HEAP_ID_GAME_START, saveData, 1);",
        "MR06B2K force Radar prototype Pokétch app",
    )

    # MR06B2H normally opens the old full-screen scanner after the Route 202
    # field settles. For this visual proof we deliberately suppress that call:
    # the top screen must stay in the live overworld while the real Pokétch
    # renders the Radar area page on the bottom.
    old_tail = """    case 1:
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

    new_tail = """    case 1:
        FieldTransition_StartMapAndFadeIn(task);
        (*state)++;
        break;
    case 2:
        // MR06B2K visual proof: leave the live field running. The Research
        // Radar is being judged as a native Pokétch app, not a full-screen
        // child application.
        return TRUE;
    }

    return FALSE;
}
"""

    replace_once(
        field_map,
        old_tail,
        new_tail,
        "MR06B2K suppress old scanner for Pokétch visual proof",
    )

    if "MAP_HEADER_ROUTE_202" not in field_map.read_text():
        raise SystemExit("MR06B2K expects MR06B2H Route 202 QA spawn")


def validate(root: Path) -> None:
    main = (root / "src/applications/poketch/pokemon_history/main.c").read_text()
    gfx = (root / "src/applications/poketch/pokemon_history/graphics.c").read_text()
    title = (root / "res/text/poketch_pokemon_history.json").read_text()
    game_start = (root / "src/game_start.c").read_text()

    checks = {
        "real_poketch_app_renderer": "PoketchPokemonHistoryGraphics_New" in main,
        "authored_route202_targets": "SPECIES_ROCKRUFF" in main and "SPECIES_PAWMI" in main,
        "twelve_target_grid": "MAX_HISTORY_SIZE" in main,
        "native_icon_loader": "PoketchTask_LoadPokemonIcons" in gfx,
        "native_luminance_palette": "PoketchTask_LoadPokemonIconLuminancePalette" in gfx,
        "research_radar_title": "RESEARCH RADAR" in title,
        "qa_forces_poketch_enabled": "Poketch_Enable(mr06b2kPoketch)" in game_start,
        "qa_forces_radar_visual_app": "POKETCH_APPID_POKEMONHISTORY" in game_start,
        "top_screen_left_as_overworld": "MercuryResearchRadar_FieldTask" not in (root / "src/field_map_change.c").read_text(),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2K validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2k-poketch-radar-shell.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

        patch_history_main(root)
    patch_history_title(root)
    patch_history_graphics(root)
    patch_qa_boot(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2K_POKETCH_RADAR_VISUAL_SHELL",
        "status": "PASS",
        "scope": "CI-only visual prototype; production scanner untouched",
        "top_screen": "normal live Platinum overworld",
        "bottom_screen": "real Platinum Poketch shell",
        "app_surface": "Poketch LCD",
        "area_page": {
            "layout": "3x4 icon grid",
            "visible_targets": 12,
            "source": "Mercury authored Route 202 Morning proof set; production runtime handoff comes after visual approval",
            "palette": "native Poketch active luminance palette",
            "icons": "native Pokemon icon resources rendered through Poketch animation system",
            "title": "RESEARCH RADAR",
        },
        "purpose": "approve the visual foundation before production interaction/detail-page wiring",
        "old_fullscreen_scanner_suppressed_in_qa": True,
        "production_player_rom_modified": False,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
