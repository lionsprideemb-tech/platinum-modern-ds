#!/usr/bin/env python3
"""MR06B2L — CI-only Pokétch Research Radar Pokémon-detail visual proof.

Runs after MR06B2K in the same QA workspace. It keeps the approved native
Pokétch shell/area grid and adds the second page:
- selected Pokémon icon + species name;
- level range;
- Search Level;
- Potential stars;
- encounter method;
- large SEARCH touch target.

Touching any area-grid Pokémon opens its detail page. For deterministic CI
screenshots, the first Route 202 target (Bidoof) auto-opens after a short delay.
Production player ROM remains untouched; this is still a visual approval pass.
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


def patch_graphics_header(root: Path) -> None:
    path = root / "include/applications/poketch/pokemon_history/graphics.h"

    replace_once(
        path,
        """    struct {
        int species;
        u32 form;
        int icon;
    } mons[MAX_HISTORY_SIZE];
""",
        """    struct {
        int species;
        u32 form;
        int icon;
        u16 searchLevel;
        u8 minLevel;
        u8 maxLevel;
        u8 potentialStars;
        u8 method;
    } mons[MAX_HISTORY_SIZE];
""",
        "MR06B2L per-target detail metadata",
    )

    replace_once(
        path,
        """BOOL PoketchPokemonHistoryGraphics_NoActiveTasks(PokemonHistoryGraphics *graphics);

#endif // POKEPLATINUM_POKETCH_POKEMON_HISTORY_GRAPHICS_H
""",
        """BOOL PoketchPokemonHistoryGraphics_NoActiveTasks(PokemonHistoryGraphics *graphics);
void PoketchPokemonHistoryGraphics_ShowDetail(PokemonHistoryGraphics *graphics, int monIdx);

#endif // POKEPLATINUM_POKETCH_POKEMON_HISTORY_GRAPHICS_H
""",
        "MR06B2L detail graphics API",
    )


def patch_main(root: Path) -> None:
    path = root / "src/applications/poketch/pokemon_history/main.c"

    replace_once(
        path,
        """    u32 buttonState;
    u32 pressedIdx;
} PoketchPokemonHistory;
""",
        """    u32 buttonState;
    u32 pressedIdx;
    u16 detailProofFrames;
    u8 detailActive;
    u8 selectedIdx;
} PoketchPokemonHistory;
""",
        "MR06B2L app detail state",
    )

    old_loop = """    for (int i = 0; i < MAX_HISTORY_SIZE; i++) {
        appData->history.mons[i].species = radarProofSpecies[i];
        appData->history.mons[i].icon = 0;
        appData->history.mons[i].form = 0;
    }
"""
    new_loop = """    static const u8 radarProofMinLevel[MAX_HISTORY_SIZE] = {
        3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5,
    };
    static const u8 radarProofMaxLevel[MAX_HISTORY_SIZE] = {
        4, 4, 5, 4, 5, 4, 4, 5, 5, 5, 5, 5,
    };

    for (int i = 0; i < MAX_HISTORY_SIZE; i++) {
        appData->history.mons[i].species = radarProofSpecies[i];
        appData->history.mons[i].icon = 0;
        appData->history.mons[i].form = 0;
        appData->history.mons[i].minLevel = radarProofMinLevel[i];
        appData->history.mons[i].maxLevel = radarProofMaxLevel[i];
        appData->history.mons[i].searchLevel = 0;
        appData->history.mons[i].potentialStars = 0;
        appData->history.mons[i].method = 0;
    }

    // Visual-proof values make the second page demonstrate the final hierarchy
    // instead of looking empty. Production Search Level/Potential are supplied
    // by the Radar runtime, not hardcoded.
    appData->history.mons[0].searchLevel = 27;
    appData->history.mons[0].potentialStars = 2;
"""
    replace_once(path, old_loop, new_loop, "MR06B2L Route 202 detail proof metadata")

    replace_once(
        path,
        """        appData->pressedIdx = 0;
        appData->poketchSys = poketchSys;

        return TRUE;
""",
        """        appData->pressedIdx = 0;
        appData->poketchSys = poketchSys;
        appData->detailProofFrames = 0;
        appData->detailActive = FALSE;
        appData->selectedIdx = 0;

        return TRUE;
""",
        "MR06B2L initialize detail state",
    )

    old_update = """    if (appData->buttonState == BUTTON_MANAGER_STATE_TOUCH) {
        int monIdx = MAX_HISTORY_SIZE - 1 - appData->pressedIdx;

        if (monIdx < appData->history.count) {
            PoketchSystem_PlayCry(appData->history.mons[monIdx].species, appData->history.mons[monIdx].form);
        }

        appData->buttonState = BUTTON_MANAGER_STATE_NULL;
    }

    return FALSE;
}
"""
    new_update = """    if (appData->buttonState == BUTTON_MANAGER_STATE_TOUCH) {
        int monIdx = MAX_HISTORY_SIZE - 1 - appData->pressedIdx;

        if (!appData->detailActive && monIdx < appData->history.count) {
            appData->selectedIdx = monIdx;
            appData->detailActive = TRUE;
            PoketchPokemonHistoryGraphics_ShowDetail(appData->graphics, monIdx);
            PoketchSystem_PlayCry(
                appData->history.mons[monIdx].species,
                appData->history.mons[monIdx].form);
        }

        appData->buttonState = BUTTON_MANAGER_STATE_NULL;
    }

    // CI-only deterministic detail-page proof. The real interaction above is
    // already touch-driven; this simply guarantees a stable screenshot without
    // depending on emulator touch-coordinate scripting.
    if (!appData->detailActive) {
        appData->detailProofFrames++;

        if (appData->detailProofFrames == 90) {
            appData->selectedIdx = 0;
            appData->detailActive = TRUE;
            PoketchPokemonHistoryGraphics_ShowDetail(appData->graphics, 0);
        }
    }

    return FALSE;
}
"""
    replace_once(path, old_update, new_update, "MR06B2L touch-select detail page")


def patch_graphics(root: Path) -> None:
    path = root / "src/applications/poketch/pokemon_history/graphics.c"

    replace_once(
        path,
        '#include "applications/poketch/poketch_task.h"\n\n',
        '#include "applications/poketch/poketch_task.h"\n\n'
        '#include "constants/charcode.h"\n\n',
        "MR06B2L charcode include",
    )

    replace_once(
        path,
        '#include "message.h"\n',
        '#include "message.h"\n'
        '#include "message_util.h"\n',
        "MR06B2L species-name include",
    )

    decl_anchor = """static void SetupSprites(PokemonHistoryGraphics *graphics, const HistoryData *history);
static void UnloadSprites(PokemonHistoryGraphics *graphics);
"""
    decl_replacement = """static void SetupSprites(PokemonHistoryGraphics *graphics, const HistoryData *history);
static void UnloadSprites(PokemonHistoryGraphics *graphics);
static void DrawDetailSurface(PokemonHistoryGraphics *graphics, int monIdx);
static void DetailPrintAscii(Window *window, const char *ascii, int x, int y);
static void DetailPrintNumber(Window *window, int value, int digits, int x, int y);
static void DetailPrintPotential(Window *window, u8 stars, int x, int y);
static charcode_t DetailAsciiToCharCode(char c);
"""
    replace_once(path, decl_anchor, decl_replacement, "MR06B2L detail helper declarations")

    public_anchor = """BOOL PoketchPokemonHistoryGraphics_NoActiveTasks(PokemonHistoryGraphics *graphics)
{
    return PoketchTask_NoActiveTasks(graphics->activeTasks);
}
"""
    public_replacement = """BOOL PoketchPokemonHistoryGraphics_NoActiveTasks(PokemonHistoryGraphics *graphics)
{
    return PoketchTask_NoActiveTasks(graphics->activeTasks);
}

void PoketchPokemonHistoryGraphics_ShowDetail(PokemonHistoryGraphics *graphics, int monIdx)
{
    if (graphics == NULL
        || monIdx < 0
        || monIdx >= (int)graphics->history->count) {
        return;
    }

    DrawDetailSurface(graphics, monIdx);
}
"""
    replace_once(path, public_anchor, public_replacement, "MR06B2L detail public function")

    helper_anchor = """static void UnloadSprites(PokemonHistoryGraphics *graphics)
{
"""
    helper_impl = r'''static void DrawDetailSurface(PokemonHistoryGraphics *graphics, int monIdx)
{
    const HistoryData *history = graphics->history;

    Bg_FillTilemapRect(
        graphics->bgConfig,
        BG_LAYER_SUB_2,
        0,
        0,
        0,
        POKETCH_WIDTH_TILES,
        POKETCH_HEIGHT_TILES,
        0);

    for (int i = 0; i < MAX_HISTORY_SIZE; i++) {
        if (graphics->sprites[i] == NULL) {
            continue;
        }

        PoketchAnimation_HideSprite(graphics->sprites[i], i != monIdx);
    }

    if (graphics->sprites[monIdx] != NULL) {
        PoketchAnimation_SetSpritePosition(
            graphics->sprites[monIdx],
            FX32_CONST(52),
            FX32_CONST(96));
    }

    Window title;
    Window_Add(
        graphics->bgConfig,
        &title,
        BG_LAYER_SUB_2,
        10,
        2,
        16,
        3,
        0,
        1);
    Window_FillTilemap(&title, 4);
    Window_PutToTilemap(&title);

    String *speciesName = MessageUtil_SpeciesName(
        history->mons[monIdx].species,
        HEAP_ID_POKETCH_APP);

    if (speciesName != NULL) {
        Text_AddPrinterWithParamsAndColor(
            &title,
            FONT_SYSTEM,
            speciesName,
            (128 - Font_CalcStringWidth(FONT_SYSTEM, speciesName, 0)) / 2,
            4,
            TEXT_SPEED_NO_TRANSFER,
            TEXT_COLOR(1, 8, 4),
            NULL);
        String_Free(speciesName);
    }

    Window_LoadTiles(&title);
    Window_Remove(&title);

    Window detail;
    Window_Add(
        graphics->bgConfig,
        &detail,
        BG_LAYER_SUB_2,
        10,
        5,
        16,
        15,
        0,
        64);
    Window_FillTilemap(&detail, 4);
    Window_PutToTilemap(&detail);

    DetailPrintAscii(&detail, "LV", 0, 4);
    DetailPrintNumber(&detail, history->mons[monIdx].minLevel, 2, 24, 4);
    DetailPrintAscii(&detail, "-", 42, 4);
    DetailPrintNumber(&detail, history->mons[monIdx].maxLevel, 2, 50, 4);

    DetailPrintAscii(&detail, "SEARCH", 0, 24);
    DetailPrintNumber(&detail, history->mons[monIdx].searchLevel, 3, 58, 24);

    DetailPrintAscii(&detail, "POT", 0, 44);
    DetailPrintPotential(&detail, history->mons[monIdx].potentialStars, 36, 44);

    DetailPrintAscii(&detail, "LAND", 0, 64);

    DetailPrintAscii(&detail, "> SEARCH <", 12, 94);

    Window_LoadTiles(&detail);
    Window_Remove(&detail);

    Bg_CopyTilemapBufferToVRAM(graphics->bgConfig, BG_LAYER_SUB_2);
}

static void DetailPrintAscii(Window *window, const char *ascii, int x, int y)
{
    String *string = String_Init(32, HEAP_ID_POKETCH_APP);

    for (int i = 0; ascii[i] != '\0'; i++) {
        String_AppendChar(string, DetailAsciiToCharCode(ascii[i]));
    }

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 8, 4),
        NULL);

    String_Free(string);
}

static void DetailPrintNumber(Window *window, int value, int digits, int x, int y)
{
    String *string = String_Init(8, HEAP_ID_POKETCH_APP);

    String_FormatInt(
        string,
        value,
        digits,
        PADDING_MODE_NONE,
        CHARSET_MODE_EN);

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 8, 4),
        NULL);

    String_Free(string);
}

static void DetailPrintPotential(Window *window, u8 stars, int x, int y)
{
    String *string = String_Init(4, HEAP_ID_POKETCH_APP);

    for (int i = 0; i < 3; i++) {
        String_AppendChar(string, i < stars ? CHAR_STAR : CHAR_MINUS);
    }

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 8, 4),
        NULL);

    String_Free(string);
}

static charcode_t DetailAsciiToCharCode(char c)
{
    if (c >= 'A' && c <= 'Z') {
        return CHAR_A + (c - 'A');
    }

    if (c >= '0' && c <= '9') {
        return CHAR_0 + (c - '0');
    }

    switch (c) {
    case ' ':
        return CHAR_SPACE;
    case '-':
        return CHAR_MINUS;
    case '>':
        return CHAR_RARROW;
    case '<':
        return CHAR_LARROW;
    default:
        return CHAR_SPACE;
    }
}

static void UnloadSprites(PokemonHistoryGraphics *graphics)
{
'''
    replace_once(path, helper_anchor, helper_impl, "MR06B2L detail page renderer")


def validate(root: Path) -> None:
    main = (root / "src/applications/poketch/pokemon_history/main.c").read_text()
    gfx = (root / "src/applications/poketch/pokemon_history/graphics.c").read_text()
    hdr = (root / "include/applications/poketch/pokemon_history/graphics.h").read_text()

    checks = {
        "touch_opens_detail": "PoketchPokemonHistoryGraphics_ShowDetail(appData->graphics, monIdx)" in main,
        "qa_auto_detail": "detailProofFrames == 90" in main,
        "dynamic_species_name": "MessageUtil_SpeciesName" in gfx,
        "level_range": 'DetailPrintAscii(&detail, "LV"' in gfx,
        "search_level": 'DetailPrintAscii(&detail, "SEARCH"' in gfx,
        "potential": "DetailPrintPotential" in gfx,
        "method_badge": 'DetailPrintAscii(&detail, "LAND"' in gfx,
        "search_touch_label": '"> SEARCH <"' in gfx,
        "native_icon_reused": "PoketchAnimation_SetSpritePosition" in gfx,
        "metadata_struct": "u16 searchLevel;" in hdr and "u8 potentialStars;" in hdr,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2L validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2l-poketch-radar-detail.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    if "RESEARCH RADAR" not in (
        root / "res/text/poketch_pokemon_history.json"
    ).read_text():
        raise SystemExit("MR06B2L requires MR06B2K Pokétch Radar shell")

    patch_graphics_header(root)
    patch_main(root)
    patch_graphics(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2L_POKETCH_RADAR_DETAIL_PAGE",
        "status": "PASS",
        "scope": "CI-only visual prototype; production scanner untouched",
        "top_screen": "normal live Platinum overworld",
        "bottom_screen": "same approved native Poketch shell",
        "interaction": "touching an area-grid Pokemon opens its detail page",
        "detail_page": {
            "species_name": True,
            "pokemon_icon": True,
            "level_range": True,
            "search_level": True,
            "potential_stars": True,
            "encounter_method": "LAND proof badge",
            "search_control": "> SEARCH <",
        },
        "qa_selected_species": "Bidoof",
        "qa_search_level": 27,
        "qa_potential_stars": 2,
        "production_player_rom_modified": False,
        "next": "approve detail-page visual, then create production Poketch Radar app identity and wire current-area ALL/LAND/WATER/FISH/RESEARCH data plus instant encounter",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
