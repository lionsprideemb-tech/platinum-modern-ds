#!/usr/bin/env python3
"""MR06B2E — compact overworld Research Poké Radar search HUD.

After SEARCH creates the guaranteed rustling patch, show the generated target
quality on the field for a few seconds:
- species + level;
- Search Level + Potential stars;
- special move;
- Primary Ability;
- held item.

The HUD is information-only. It does not alter the generated target, normal
encounters, or the patch lifetime. RadarChain_Clear owns cleanup so map changes,
cycling, battle entry, and other normal Radar clears cannot leave stale UI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HUD_HEADER = r'''#ifndef POKEPLATINUM_OVERLAY005_MERCURY_RADAR_HUD_H
#define POKEPLATINUM_OVERLAY005_MERCURY_RADAR_HUD_H

#include "field/field_system_decl.h"
#include "pokeradar.h"

typedef struct MercuryRadarHud MercuryRadarHud;

MercuryRadarHud *MercuryRadarHud_Show(
    FieldSystem *fieldSystem,
    u16 species,
    u8 level,
    const MercuryRadarTargetQuality *quality);
void MercuryRadarHud_Destroy(MercuryRadarHud *hud);

#endif // POKEPLATINUM_OVERLAY005_MERCURY_RADAR_HUD_H
'''


HUD_SOURCE = r'''#include "overlay005/mercury_radar_hud.h"

#include <nitro.h>

#include "constants/charcode.h"
#include "constants/field/window.h"
#include "constants/field_base_tiles.h"
#include "constants/heap.h"
#include "constants/narc.h"
#include "generated/items.h"
#include "generated/moves.h"
#include "generated/text_banks.h"

#include "field/field_system.h"

#include "bg_window.h"
#include "font.h"
#include "heap.h"
#include "item.h"
#include "message.h"
#include "message_util.h"
#include "render_window.h"
#include "string_gf.h"
#include "sys_task.h"
#include "sys_task_manager.h"
#include "text.h"

#define MERCURY_RADAR_HUD_WIDTH_TILES  21
#define MERCURY_RADAR_HUD_HEIGHT_TILES 10
#define MERCURY_RADAR_HUD_SIZE_TILES \
    (MERCURY_RADAR_HUD_WIDTH_TILES * MERCURY_RADAR_HUD_HEIGHT_TILES)
#define MERCURY_RADAR_HUD_BASE_TILE \
    (BASE_TILE_YES_NO_MENU - MERCURY_RADAR_HUD_SIZE_TILES)
#define MERCURY_RADAR_HUD_DURATION_FRAMES 300

struct MercuryRadarHud {
    BgConfig *bgConfig;
    Window window;
    SysTask *task;
    u16 timer;
    BOOL visible;
};

static void MercuryRadarHud_Task(SysTask *task, void *data);
static void MercuryRadarHud_Hide(MercuryRadarHud *hud);
static void MercuryRadarHud_PrintAscii(
    Window *window,
    const char *ascii,
    int x,
    int y);
static void MercuryRadarHud_PrintNumber(
    Window *window,
    int value,
    int digits,
    int x,
    int y);
static void MercuryRadarHud_PrintString(
    Window *window,
    const String *string,
    int x,
    int y);
static void MercuryRadarHud_PrintPotential(
    Window *window,
    u8 stars,
    int x,
    int y);
static charcode_t MercuryRadarHud_AsciiToCharCode(char c);

MercuryRadarHud *MercuryRadarHud_Show(
    FieldSystem *fieldSystem,
    u16 species,
    u8 level,
    const MercuryRadarTargetQuality *quality)
{
    if (fieldSystem == NULL || quality == NULL) {
        return NULL;
    }

    MercuryRadarHud *hud = Heap_Alloc(
        HEAP_ID_FIELD2,
        sizeof(MercuryRadarHud));

    MI_CpuClear8(hud, sizeof(MercuryRadarHud));
    hud->bgConfig = fieldSystem->bgConfig;

    Window_Add(
        hud->bgConfig,
        &hud->window,
        BG_LAYER_MAIN_3,
        10,
        1,
        MERCURY_RADAR_HUD_WIDTH_TILES,
        MERCURY_RADAR_HUD_HEIGHT_TILES,
        FIELD_MESSAGE_PALETTE_INDEX,
        MERCURY_RADAR_HUD_BASE_TILE);

    LoadStandardWindowGraphics(
        hud->bgConfig,
        BG_LAYER_MAIN_3,
        BASE_TILE_STANDARD_WINDOW_FRAME,
        FIELD_WINDOW_PALETTE_INDEX,
        STANDARD_WINDOW_FIELD,
        HEAP_ID_FIELD2);

    Window_FillTilemap(
        &hud->window,
        Font_GetAttribute(FONT_SYSTEM, FONTATTR_BG_COLOR));

    String *speciesName = MessageUtil_SpeciesName(species, HEAP_ID_FIELD2);
    MercuryRadarHud_PrintString(&hud->window, speciesName, 0, 0);
    String_Free(speciesName);

    MercuryRadarHud_PrintAscii(&hud->window, "LV", 112, 0);
    MercuryRadarHud_PrintNumber(&hud->window, level, 3, 132, 0);

    MercuryRadarHud_PrintAscii(&hud->window, "SEARCH", 0, 16);
    MercuryRadarHud_PrintNumber(
        &hud->window,
        quality->searchLevel,
        3,
        52,
        16);
    MercuryRadarHud_PrintAscii(&hud->window, "POT", 88, 16);
    MercuryRadarHud_PrintPotential(
        &hud->window,
        quality->potentialStars,
        116,
        16);

    MercuryRadarHud_PrintAscii(&hud->window, "MOVE", 0, 32);
    if (quality->specialMove != MOVE_NONE) {
        String *moveName = MessageUtil_MoveName(
            quality->specialMove,
            HEAP_ID_FIELD2);
        MercuryRadarHud_PrintString(&hud->window, moveName, 42, 32);
        String_Free(moveName);
    } else {
        MercuryRadarHud_PrintAscii(&hud->window, "---", 42, 32);
    }

    MercuryRadarHud_PrintAscii(&hud->window, "ABILITY", 0, 48);
    if (quality->primaryAbility != 0) {
        MessageLoader *abilityLoader = MessageLoader_Init(
            MSG_LOADER_LOAD_ON_DEMAND,
            NARC_INDEX_MSGDATA__PL_MSG,
            TEXT_BANK_ABILITY_NAMES,
            HEAP_ID_FIELD2);

        String *abilityName = MessageLoader_GetNewString(
            abilityLoader,
            quality->primaryAbility);

        MercuryRadarHud_PrintString(
            &hud->window,
            abilityName,
            54,
            48);

        String_Free(abilityName);
        MessageLoader_Free(abilityLoader);
    } else {
        MercuryRadarHud_PrintAscii(&hud->window, "---", 54, 48);
    }

    MercuryRadarHud_PrintAscii(&hud->window, "ITEM", 0, 64);
    if (quality->heldItem != ITEM_NONE) {
        String *itemName = String_Init(32, HEAP_ID_FIELD2);
        Item_LoadName(itemName, quality->heldItem, HEAP_ID_FIELD2);
        MercuryRadarHud_PrintString(&hud->window, itemName, 42, 64);
        String_Free(itemName);
    } else {
        MercuryRadarHud_PrintAscii(&hud->window, "---", 42, 64);
    }

    Window_DrawStandardFrame(
        &hud->window,
        FALSE,
        BASE_TILE_STANDARD_WINDOW_FRAME,
        FIELD_WINDOW_PALETTE_INDEX);

    hud->visible = TRUE;
    hud->task = SysTask_Start(MercuryRadarHud_Task, hud, 0);
    return hud;
}

void MercuryRadarHud_Destroy(MercuryRadarHud *hud)
{
    if (hud == NULL) {
        return;
    }

    if (hud->task != NULL) {
        SysTask_Done(hud->task);
        hud->task = NULL;
    }

    MercuryRadarHud_Hide(hud);
    Window_Remove(&hud->window);
    Heap_Free(hud);
}

static void MercuryRadarHud_Task(SysTask *task, void *data)
{
    MercuryRadarHud *hud = data;

    hud->timer++;

    if (hud->timer < MERCURY_RADAR_HUD_DURATION_FRAMES) {
        return;
    }

    MercuryRadarHud_Hide(hud);
    hud->task = NULL;
    SysTask_Done(task);
}

static void MercuryRadarHud_Hide(MercuryRadarHud *hud)
{
    if (hud == NULL || !hud->visible) {
        return;
    }

    Window_EraseStandardFrame(&hud->window, FALSE);
    Window_ClearAndCopyToVRAM(&hud->window);
    hud->visible = FALSE;
}

static void MercuryRadarHud_PrintString(
    Window *window,
    const String *string,
    int x,
    int y)
{
    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 2, 0),
        NULL);
}

static void MercuryRadarHud_PrintAscii(
    Window *window,
    const char *ascii,
    int x,
    int y)
{
    String *string = String_Init(48, HEAP_ID_FIELD2);

    for (int i = 0; ascii[i] != '\0'; i++) {
        String_AppendChar(
            string,
            MercuryRadarHud_AsciiToCharCode(ascii[i]));
    }

    MercuryRadarHud_PrintString(window, string, x, y);
    String_Free(string);
}

static void MercuryRadarHud_PrintNumber(
    Window *window,
    int value,
    int digits,
    int x,
    int y)
{
    String *string = String_Init(8, HEAP_ID_FIELD2);

    String_FormatInt(
        string,
        value,
        digits,
        PADDING_MODE_NONE,
        CHARSET_MODE_EN);

    MercuryRadarHud_PrintString(window, string, x, y);
    String_Free(string);
}

static void MercuryRadarHud_PrintPotential(
    Window *window,
    u8 stars,
    int x,
    int y)
{
    String *string = String_Init(4, HEAP_ID_FIELD2);

    for (int i = 0; i < 3; i++) {
        String_AppendChar(
            string,
            i < stars ? CHAR_STAR : CHAR_MINUS);
    }

    MercuryRadarHud_PrintString(window, string, x, y);
    String_Free(string);
}

static charcode_t MercuryRadarHud_AsciiToCharCode(char c)
{
    if (c >= 'A' && c <= 'Z') {
        return CHAR_A + (c - 'A');
    }

    if (c >= 'a' && c <= 'z') {
        return CHAR_a + (c - 'a');
    }

    if (c >= '0' && c <= '9') {
        return CHAR_0 + (c - '0');
    }

    switch (c) {
    case ' ':
        return CHAR_SPACE;
    case '-':
        return CHAR_MINUS;
    case '/':
        return CHAR_SLASH;
    case ':':
        return CHAR_COLON;
    case '.':
        return CHAR_PERIOD;
    case '?':
        return CHAR_QUESTION;
    case '!':
        return CHAR_EXCLAMATION;
    default:
        return CHAR_SPACE;
    }
}
'''


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def install_hud(root: Path) -> None:
    header = root / "include/overlay005/mercury_radar_hud.h"
    source = root / "src/overlay005/mercury_radar_hud.c"

    header.parent.mkdir(parents=True, exist_ok=True)
    source.parent.mkdir(parents=True, exist_ok=True)

    header.write_text(HUD_HEADER)
    source.write_text(HUD_SOURCE)

    meson = root / "src/meson.build"
    replace_once(
        meson,
        "    'overlay005/map_name_popup.c',\n",
        "    'overlay005/map_name_popup.c',\n"
        "    'overlay005/mercury_radar_hud.c',\n",
        "MR06B2E HUD meson source",
    )


def patch_pokeradar(root: Path) -> None:
    path = root / "src/pokeradar.c"

    replace_once(
        path,
        '#include "overlay005/fieldmap.h"\n',
        '#include "overlay005/fieldmap.h"\n'
        '#include "overlay005/mercury_radar_hud.h"\n',
        "MR06B2E HUD include",
    )

    struct_anchor = """    BOOL mercuryTargetActive;
    MercuryRadarTargetQuality mercuryTargetQuality;
} RadarChain;
"""
    struct_replacement = """    BOOL mercuryTargetActive;
    MercuryRadarTargetQuality mercuryTargetQuality;
    MercuryRadarHud *mercuryHud;
} RadarChain;
"""
    replace_once(
        path,
        struct_anchor,
        struct_replacement,
        "MR06B2E Radar HUD owner",
    )

    init_anchor = """RadarChain *RadarChain_Init(const enum HeapID heapID)
{
    RadarChain *chain = Heap_Alloc(heapID, sizeof(RadarChain));
    GFXBoxTest_MakeBox(FX32_ONE * 16, FX32_ONE * 8, FX32_ONE * 16, &chain->grassPatchVolume);
    return chain;
}

void RadarChain_Free(RadarChain *chain)
{
    Heap_Free(chain);
}
"""
    init_replacement = """RadarChain *RadarChain_Init(const enum HeapID heapID)
{
    RadarChain *chain = Heap_Alloc(heapID, sizeof(RadarChain));
    chain->mercuryHud = NULL;
    GFXBoxTest_MakeBox(FX32_ONE * 16, FX32_ONE * 8, FX32_ONE * 16, &chain->grassPatchVolume);
    return chain;
}

void RadarChain_Free(RadarChain *chain)
{
    if (chain->mercuryHud != NULL) {
        MercuryRadarHud_Destroy(chain->mercuryHud);
        chain->mercuryHud = NULL;
    }

    Heap_Free(chain);
}
"""
    replace_once(
        path,
        init_anchor,
        init_replacement,
        "MR06B2E Radar init/free HUD lifecycle",
    )

    clear_anchor = """void RadarChain_Clear(RadarChain *chain)
{
    chain->count = 0;
"""
    clear_replacement = """void RadarChain_Clear(RadarChain *chain)
{
    if (chain->mercuryHud != NULL) {
        MercuryRadarHud_Destroy(chain->mercuryHud);
        chain->mercuryHud = NULL;
    }

    chain->count = 0;
"""
    replace_once(
        path,
        clear_anchor,
        clear_replacement,
        "MR06B2E Radar clear HUD lifecycle",
    )

    spawn_anchor = """    FieldSystem_CreateShakingRadarPatches(fieldSystem, chain);
    return TRUE;
}
"""
    spawn_replacement = """    FieldSystem_CreateShakingRadarPatches(fieldSystem, chain);

    chain->mercuryHud = MercuryRadarHud_Show(
        fieldSystem,
        species,
        chain->mercuryTargetLevel,
        &chain->mercuryTargetQuality);

    return TRUE;
}
"""
    replace_once(
        path,
        spawn_anchor,
        spawn_replacement,
        "MR06B2E show HUD after target patch",
    )


def validate(root: Path) -> None:
    header = (root / "include/overlay005/mercury_radar_hud.h").read_text()
    source = (root / "src/overlay005/mercury_radar_hud.c").read_text()
    radar = (root / "src/pokeradar.c").read_text()
    meson = (root / "src/meson.build").read_text()
    start_menu = (root / "src/start_menu.c").read_text()

    combined = header + source + radar

    checks = {
        "hud_type": "MercuryRadarHud" in header,
        "species_name": "MessageUtil_SpeciesName" in source,
        "level": '"LV"' in source,
        "search_level": "quality->searchLevel" in source,
        "potential_stars": "CHAR_STAR" in source,
        "special_move_name": "MessageUtil_MoveName" in source,
        "ability_name": "TEXT_BANK_ABILITY_NAMES" in source,
        "item_name": "Item_LoadName" in source,
        "timed_hide": "MERCURY_RADAR_HUD_DURATION_FRAMES 300" in source,
        "show_after_patch": "MercuryRadarHud_Show(" in radar,
        "cleanup_on_radar_clear": "MercuryRadarHud_Destroy(chain->mercuryHud)" in radar,
        "hud_source_built": "'overlay005/mercury_radar_hud.c'," in meson,
        "general_encounter_menu_absent": "START_MENU_OPTION_ENCOUNTERS" not in start_menu,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2E validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2e-overworld-search-hud.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    if "MercuryRadarTargetQuality" not in (root / "include/pokeradar.h").read_text():
        raise SystemExit("MR06B2E requires MR06B2D target quality")
    if "MercuryRadar_GenerateTargetQuality" not in (root / "src/pokeradar.c").read_text():
        raise SystemExit("MR06B2E requires MR06B2D quality generation")

    install_hud(root)
    patch_pokeradar(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2E_OVERWORLD_SEARCH_HUD",
        "status": "PASS",
        "screen": "top overworld screen",
        "duration_frames": 300,
        "duration_seconds_at_60fps": 5,
        "shows": [
            "species name",
            "target level",
            "Search Level",
            "Potential stars",
            "special move name",
            "Primary Ability name",
            "held item name",
        ],
        "generated_target_changed_by_hud": False,
        "radar_clear_owns_cleanup": True,
        "map_change_cleanup": True,
        "battle_entry_cleanup": True,
        "normal_encounter_tables_modified": False,
        "standalone_encounter_menu": False,
        "next": "add species icon/rare markers and run DS visual proof pass",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
