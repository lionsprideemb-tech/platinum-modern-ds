#!/usr/bin/env python3
"""MR06B2C2 — compile the real DS dual-screen Research Poké Radar application.

This phase creates the visible DexNav-style scanner application:
- top screen dossier for the highlighted target;
- bottom screen 4x4 Pokémon icon grid;
- D-pad and touch selection;
- R-button registration;
- LOCAL/RESEARCH source awareness.

For safety, ITEM_POKE_RADAR is still not rebound in this phase. The application
must compile cleanly first; item binding and targeted-patch SEARCH are installed
atomically in the next phase.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HEADER = r'''#ifndef POKEPLATINUM_APPLICATIONS_MERCURY_RESEARCH_RADAR_H
#define POKEPLATINUM_APPLICATIONS_MERCURY_RESEARCH_RADAR_H

#include "overlay006/wild_encounters.h"
#include "overlay_manager.h"
#include "savedata.h"

enum MercuryResearchRadarAppAction {
    MERCURY_RESEARCH_RADAR_APP_CANCEL = 0,
    MERCURY_RESEARCH_RADAR_APP_SEARCH,
};

typedef struct MercuryResearchRadarAppArgs {
    SaveData *saveData;
    MercuryResearchRadarScannerState scanner;
    int mapHeaderID;
    u16 selectedSpecies;
    u8 action;
    u8 padding;
} MercuryResearchRadarAppArgs;

extern const ApplicationManagerTemplate gMercuryResearchRadarAppTemplate;

MercuryResearchRadarAppArgs *MercuryResearchRadar_OpenScanner(void *fieldSystem);

#endif // POKEPLATINUM_APPLICATIONS_MERCURY_RESEARCH_RADAR_H
'''


SOURCE = r'''#include "applications/mercury_research_radar.h"

#include <nitro.h>
#include <string.h>

#include "constants/charcode.h"
#include "constants/graphics.h"
#include "constants/heap.h"
#include "constants/narc.h"
#include "constants/species.h"

#include "field/field_system.h"

#include "bg_window.h"
#include "field_system.h"
#include "font.h"
#include "graphics.h"
#include "gx_layers.h"
#include "heap.h"
#include "message_util.h"
#include "overlay006/wild_encounters.h"
#include "palette.h"
#include "pokedex.h"
#include "pokemon_icon.h"
#include "screen_fade.h"
#include "string_gf.h"
#include "system.h"
#include "text.h"

#define RADAR_GRID_COLUMNS 4
#define RADAR_GRID_ROWS 4
#define RADAR_ICON_TILES 16
#define RADAR_ICON_TILE_BYTES (RADAR_ICON_TILES * TILE_SIZE_4BPP)

typedef struct MercuryResearchRadarApp {
    MercuryResearchRadarAppArgs *args;
    BgConfig *bgConfig;
    Window mainWindow;
    Window subWindow;
} MercuryResearchRadarApp;

static BOOL MercuryResearchRadarApp_Init(ApplicationManager *appMan, int *state);
static int MercuryResearchRadarApp_Main(ApplicationManager *appMan, int *state);
static BOOL MercuryResearchRadarApp_Exit(ApplicationManager *appMan, int *state);
static void MercuryResearchRadarApp_VBlank(void *data);
static void MercuryResearchRadarApp_InitBgs(MercuryResearchRadarApp *app);
static void MercuryResearchRadarApp_FreeBgs(MercuryResearchRadarApp *app);
static void MercuryResearchRadarApp_InitWindows(MercuryResearchRadarApp *app);
static void MercuryResearchRadarApp_FreeWindows(MercuryResearchRadarApp *app);
static void MercuryResearchRadarApp_LoadIconPalettes(MercuryResearchRadarApp *app);
static void MercuryResearchRadarApp_LoadBottomIcons(MercuryResearchRadarApp *app);
static void MercuryResearchRadarApp_DrawSelection(MercuryResearchRadarApp *app);
static void MercuryResearchRadarApp_DrawDossier(MercuryResearchRadarApp *app);
static void MercuryResearchRadarApp_DrawBottomText(MercuryResearchRadarApp *app);
static BOOL MercuryResearchRadarApp_HandleTouch(MercuryResearchRadarApp *app);
static BOOL MercuryResearchRadarApp_MoveSelection(MercuryResearchRadarApp *app, int delta);
static void MercuryResearchRadarApp_PrintAscii(Window *window, const char *ascii, int x, int y);
static void MercuryResearchRadarApp_PrintNumber(Window *window, int value, int digits, int x, int y);
static void MercuryResearchRadarApp_PrintSpecies(Window *window, int species, int x, int y);
static void MercuryResearchRadarApp_LoadIconToBg(MercuryResearchRadarApp *app, int bgLayer, int species, int tileStart, int x, int y);
static charcode_t MercuryResearchRadarApp_AsciiToCharCode(char c);

const ApplicationManagerTemplate gMercuryResearchRadarAppTemplate = {
    .init = MercuryResearchRadarApp_Init,
    .main = MercuryResearchRadarApp_Main,
    .exit = MercuryResearchRadarApp_Exit,
    .overlayID = FS_OVERLAY_ID_NONE,
};

MercuryResearchRadarAppArgs *MercuryResearchRadar_OpenScanner(void *fieldSystemArg)
{
    FieldSystem *fieldSystem = fieldSystemArg;
    MercuryResearchRadarAppArgs *args = Heap_Alloc(HEAP_ID_FIELD2, sizeof(MercuryResearchRadarAppArgs));

    MI_CpuClear8(args, sizeof(MercuryResearchRadarAppArgs));

    args->saveData = fieldSystem->saveData;
    args->mapHeaderID = fieldSystem->location->mapHeaderID;
    args->action = MERCURY_RESEARCH_RADAR_APP_CANCEL;
    args->selectedSpecies = SPECIES_NONE;

    MercuryResearchRadar_InitScannerState(
        (enum MapHeaderID)args->mapHeaderID,
        MercuryEncounterChart_GetCurrentLandMethod(),
        SaveData_GetPokedex(args->saveData),
        &args->scanner);

    FieldSystem_StartChildProcess(fieldSystem, &gMercuryResearchRadarAppTemplate, args);
    return args;
}

static BOOL MercuryResearchRadarApp_Init(ApplicationManager *appMan, int *state)
{
    MercuryResearchRadarApp *app = ApplicationManager_NewData(
        appMan,
        sizeof(MercuryResearchRadarApp),
        HEAP_ID_FIELD2);

    MI_CpuClear8(app, sizeof(MercuryResearchRadarApp));
    app->args = ApplicationManager_Args(appMan);

    SetScreenColorBrightness(DS_SCREEN_MAIN, COLOR_BLACK);
    SetScreenColorBrightness(DS_SCREEN_SUB, COLOR_BLACK);
    SetVBlankCallback(NULL, NULL);
    SetHBlankCallback(NULL, NULL);

    GXLayers_DisableEngineALayers();
    GXLayers_DisableEngineBLayers();
    GX_SetVisiblePlane(0);
    GXS_SetVisiblePlane(0);

    SetAutorepeat(4, 8);

    MercuryResearchRadarApp_InitBgs(app);
    MercuryResearchRadarApp_InitWindows(app);
    MercuryResearchRadarApp_LoadIconPalettes(app);
    MercuryResearchRadarApp_LoadBottomIcons(app);
    MercuryResearchRadarApp_DrawSelection(app);
    MercuryResearchRadarApp_DrawDossier(app);
    MercuryResearchRadarApp_DrawBottomText(app);

    SetVBlankCallback(MercuryResearchRadarApp_VBlank, app);
    GXLayers_TurnBothDispOn();

    return TRUE;
}

static int MercuryResearchRadarApp_Main(ApplicationManager *appMan, int *state)
{
    MercuryResearchRadarApp *app = ApplicationManager_Data(appMan);

    switch (*state) {
    case 0:
        StartScreenFade(
            FADE_BOTH_SCREENS,
            FADE_TYPE_BRIGHTNESS_IN,
            FADE_TYPE_BRIGHTNESS_IN,
            COLOR_BLACK,
            6,
            1,
            HEAP_ID_FIELD2);
        *state = 1;
        break;

    case 1:
        if (IsScreenFadeDone()) {
            *state = 2;
        }
        break;

    case 2: {
        BOOL changed = FALSE;

        if (JOY_REPEAT(PAD_KEY_LEFT)) {
            changed = MercuryResearchRadarApp_MoveSelection(app, -1);
        } else if (JOY_REPEAT(PAD_KEY_RIGHT)) {
            changed = MercuryResearchRadarApp_MoveSelection(app, 1);
        } else if (JOY_REPEAT(PAD_KEY_UP)) {
            changed = MercuryResearchRadarApp_MoveSelection(app, -RADAR_GRID_COLUMNS);
        } else if (JOY_REPEAT(PAD_KEY_DOWN)) {
            changed = MercuryResearchRadarApp_MoveSelection(app, RADAR_GRID_COLUMNS);
        } else if (gSystem.touchPressed) {
            changed = MercuryResearchRadarApp_HandleTouch(app);
        }

        if (changed) {
            MercuryResearchRadarApp_DrawSelection(app);
            MercuryResearchRadarApp_DrawDossier(app);
        }

        if (JOY_NEW(PAD_BUTTON_R)) {
            Pokedex *pokedex = SaveData_GetPokedex(app->args->saveData);

            if (MercuryResearchRadar_RegisterSelected(&app->args->scanner, pokedex)) {
                MercuryResearchRadarApp_DrawDossier(app);
                MercuryResearchRadarApp_DrawBottomText(app);
            }
        }

        if (JOY_NEW(PAD_BUTTON_B)) {
            const MercuryResearchRadarTarget *target =
                MercuryResearchRadar_GetSelectedTarget(&app->args->scanner);

            app->args->action = MERCURY_RESEARCH_RADAR_APP_CANCEL;
            app->args->selectedSpecies = target != NULL ? target->species : SPECIES_NONE;

            StartScreenFade(
                FADE_BOTH_SCREENS,
                FADE_TYPE_BRIGHTNESS_OUT,
                FADE_TYPE_BRIGHTNESS_OUT,
                COLOR_BLACK,
                6,
                1,
                HEAP_ID_FIELD2);
            *state = 3;
        }
        break;
    }

    case 3:
        if (IsScreenFadeDone()) {
            return TRUE;
        }
        break;
    }

    return FALSE;
}

static BOOL MercuryResearchRadarApp_Exit(ApplicationManager *appMan, int *state)
{
    MercuryResearchRadarApp *app = ApplicationManager_Data(appMan);

    MercuryResearchRadarApp_FreeWindows(app);
    MercuryResearchRadarApp_FreeBgs(app);

    SetVBlankCallback(NULL, NULL);
    ApplicationManager_FreeData(appMan);

    return TRUE;
}

static void MercuryResearchRadarApp_VBlank(void *data)
{
    MercuryResearchRadarApp *app = data;
    Bg_RunScheduledUpdates(app->bgConfig);
}

static void MercuryResearchRadarApp_InitBgs(MercuryResearchRadarApp *app)
{
    GXBanks banks = {
        GX_VRAM_BG_128_B,
        GX_VRAM_BGEXTPLTT_NONE,
        GX_VRAM_SUB_BG_128_C,
        GX_VRAM_SUB_BGEXTPLTT_NONE,
        GX_VRAM_OBJ_NONE,
        GX_VRAM_OBJEXTPLTT_NONE,
        GX_VRAM_SUB_OBJ_NONE,
        GX_VRAM_SUB_OBJEXTPLTT_NONE,
        GX_VRAM_TEX_NONE,
        GX_VRAM_TEXPLTT_NONE,
    };

    GXLayers_SetBanks(&banks);

    app->bgConfig = BgConfig_New(HEAP_ID_FIELD2);

    GraphicsModes graphicsModes = {
        .displayMode = GX_DISPMODE_GRAPHICS,
        .mainBgMode = GX_BGMODE_0,
        .subBgMode = GX_BGMODE_0,
        .bg0As2DOr3D = GX_BG0_AS_2D,
    };

    SetAllGraphicsModes(&graphicsModes);

    BgTemplate template = {
        .x = 0,
        .y = 0,
        .bufferSize = 0x800,
        .baseTile = 0,
        .screenSize = BG_SCREEN_SIZE_256x256,
        .colorMode = GX_BG_COLORMODE_16,
        .screenBase = GX_BG_SCRBASE_0x0000,
        .charBase = GX_BG_CHARBASE_0x10000,
        .bgExtPltt = GX_BG_EXTPLTT_01,
        .priority = 0,
        .areaOver = 0,
        .mosaic = FALSE,
    };

    Bg_InitFromTemplate(app->bgConfig, BG_LAYER_MAIN_0, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(app->bgConfig, BG_LAYER_MAIN_0);

    template.screenBase = GX_BG_SCRBASE_0x1000;
    template.charBase = GX_BG_CHARBASE_0x00000;
    template.priority = 1;
    Bg_InitFromTemplate(app->bgConfig, BG_LAYER_MAIN_1, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(app->bgConfig, BG_LAYER_MAIN_1);

    template.screenBase = GX_BG_SCRBASE_0x0000;
    template.charBase = GX_BG_CHARBASE_0x10000;
    template.priority = 0;
    Bg_InitFromTemplate(app->bgConfig, BG_LAYER_SUB_0, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(app->bgConfig, BG_LAYER_SUB_0);

    template.screenBase = GX_BG_SCRBASE_0x1000;
    template.charBase = GX_BG_CHARBASE_0x00000;
    template.priority = 1;
    Bg_InitFromTemplate(app->bgConfig, BG_LAYER_SUB_1, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(app->bgConfig, BG_LAYER_SUB_1);

    template.screenBase = GX_BG_SCRBASE_0x2000;
    template.charBase = GX_BG_CHARBASE_0x08000;
    template.priority = 2;
    Bg_InitFromTemplate(app->bgConfig, BG_LAYER_SUB_2, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(app->bgConfig, BG_LAYER_SUB_2);

    Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_2, 1, 1, 1);

    Bg_ToggleLayer(BG_LAYER_MAIN_0, TRUE);
    Bg_ToggleLayer(BG_LAYER_MAIN_1, TRUE);
    Bg_ToggleLayer(BG_LAYER_SUB_0, TRUE);
    Bg_ToggleLayer(BG_LAYER_SUB_1, TRUE);
    Bg_ToggleLayer(BG_LAYER_SUB_2, TRUE);
}

static void MercuryResearchRadarApp_FreeBgs(MercuryResearchRadarApp *app)
{
    Bg_ToggleLayer(BG_LAYER_MAIN_0, FALSE);
    Bg_ToggleLayer(BG_LAYER_MAIN_1, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_0, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_1, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_2, FALSE);

    Bg_FreeTilemapBuffer(app->bgConfig, BG_LAYER_MAIN_0);
    Bg_FreeTilemapBuffer(app->bgConfig, BG_LAYER_MAIN_1);
    Bg_FreeTilemapBuffer(app->bgConfig, BG_LAYER_SUB_0);
    Bg_FreeTilemapBuffer(app->bgConfig, BG_LAYER_SUB_1);
    Bg_FreeTilemapBuffer(app->bgConfig, BG_LAYER_SUB_2);
    Heap_Free(app->bgConfig);
}

static void MercuryResearchRadarApp_InitWindows(MercuryResearchRadarApp *app)
{
    Text_ResetAllPrinters();

    Window_Add(
        app->bgConfig,
        &app->mainWindow,
        BG_LAYER_MAIN_0,
        0,
        0,
        32,
        24,
        15,
        1);

    Window_Add(
        app->bgConfig,
        &app->subWindow,
        BG_LAYER_SUB_0,
        0,
        0,
        32,
        24,
        15,
        1);

    Window_FillTilemap(&app->mainWindow, 0);
    Window_FillTilemap(&app->subWindow, 0);

    Font_LoadTextPalette(PAL_LOAD_MAIN_BG, PLTT_OFFSET(15), HEAP_ID_FIELD2);
    Font_LoadTextPalette(PAL_LOAD_SUB_BG, PLTT_OFFSET(15), HEAP_ID_FIELD2);
}

static void MercuryResearchRadarApp_FreeWindows(MercuryResearchRadarApp *app)
{
    Window_Remove(&app->subWindow);
    Window_Remove(&app->mainWindow);
}

static void MercuryResearchRadarApp_LoadIconPalettes(MercuryResearchRadarApp *app)
{
    Graphics_LoadPalette(
        NARC_INDEX_POKETOOL__ICONGRA__PL_POKE_ICON,
        PokeIconPalettesFileIndex(),
        PAL_LOAD_MAIN_BG,
        PLTT_OFFSET(0),
        PALETTE_SIZE_BYTES * 3,
        HEAP_ID_FIELD2);

    Graphics_LoadPalette(
        NARC_INDEX_POKETOOL__ICONGRA__PL_POKE_ICON,
        PokeIconPalettesFileIndex(),
        PAL_LOAD_SUB_BG,
        PLTT_OFFSET(0),
        PALETTE_SIZE_BYTES * 3,
        HEAP_ID_FIELD2);
}

static void MercuryResearchRadarApp_LoadIconToBg(
    MercuryResearchRadarApp *app,
    int bgLayer,
    int species,
    int tileStart,
    int x,
    int y)
{
    NNSG2dCharacterData *charData = NULL;
    void *buffer = Graphics_GetCharData(
        NARC_INDEX_POKETOOL__ICONGRA__PL_POKE_ICON,
        PokeIconSpriteIndex(species, FALSE, 0),
        FALSE,
        &charData,
        HEAP_ID_FIELD2);

    if (buffer == NULL || charData == NULL) {
        if (buffer != NULL) {
            Heap_Free(buffer);
        }
        return;
    }

    Bg_LoadTiles(
        app->bgConfig,
        bgLayer,
        charData->pRawData,
        RADAR_ICON_TILE_BYTES,
        tileStart);

    int palette = PokeIconPaletteIndex(species, 0, FALSE);

    for (int tileY = 0; tileY < 4; tileY++) {
        for (int tileX = 0; tileX < 4; tileX++) {
            Bg_FillTilemapRect(
                app->bgConfig,
                bgLayer,
                tileStart + tileY * 4 + tileX,
                x + tileX,
                y + tileY,
                1,
                1,
                palette);
        }
    }

    Heap_Free(buffer);
}

static void MercuryResearchRadarApp_LoadBottomIcons(MercuryResearchRadarApp *app)
{
    static const u8 sGridX[RADAR_GRID_COLUMNS] = { 2, 9, 16, 23 };
    static const u8 sGridY[RADAR_GRID_ROWS] = { 4, 9, 14, 19 };

    Bg_ClearTilemap(app->bgConfig, BG_LAYER_SUB_1);

    for (int i = 0; i < app->args->scanner.targetCount; i++) {
        int col = i % RADAR_GRID_COLUMNS;
        int row = i / RADAR_GRID_COLUMNS;
        int tileStart = 1 + i * RADAR_ICON_TILES;

        MercuryResearchRadarApp_LoadIconToBg(
            app,
            BG_LAYER_SUB_1,
            app->args->scanner.targets[i].species,
            tileStart,
            sGridX[col],
            sGridY[row]);
    }

    Bg_CopyTilemapBufferToVRAM(app->bgConfig, BG_LAYER_SUB_1);
}

static void MercuryResearchRadarApp_DrawSelection(MercuryResearchRadarApp *app)
{
    static const u8 sGridX[RADAR_GRID_COLUMNS] = { 2, 9, 16, 23 };
    static const u8 sGridY[RADAR_GRID_ROWS] = { 4, 9, 14, 19 };

    Bg_ClearTilemap(app->bgConfig, BG_LAYER_SUB_2);

    if (app->args->scanner.targetCount > 0) {
        int selected = app->args->scanner.selectedIndex;
        int col = selected % RADAR_GRID_COLUMNS;
        int row = selected / RADAR_GRID_COLUMNS;
        int x = sGridX[col];
        int y = sGridY[row];

        Bg_FillTilemapRect(
            app->bgConfig,
            BG_LAYER_SUB_2,
            1,
            x - 1,
            y - 1,
            6,
            6,
            15);
    }

    Bg_CopyTilemapBufferToVRAM(app->bgConfig, BG_LAYER_SUB_2);
}

static void MercuryResearchRadarApp_DrawDossier(MercuryResearchRadarApp *app)
{
    Window_FillTilemap(&app->mainWindow, 0);
    Bg_ClearTilemap(app->bgConfig, BG_LAYER_MAIN_1);

    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "RESEARCH POKE RADAR", 72, 8);

    const MercuryResearchRadarTarget *target =
        MercuryResearchRadar_GetSelectedTarget(&app->args->scanner);

    if (target == NULL) {
        MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "NO LAND TARGETS", 72, 48);
        Window_CopyToVRAM(&app->mainWindow);
        Bg_CopyTilemapBufferToVRAM(app->bgConfig, BG_LAYER_MAIN_1);
        return;
    }

    MercuryResearchRadarApp_LoadIconToBg(
        app,
        BG_LAYER_MAIN_1,
        target->species,
        1,
        2,
        4);

    MercuryResearchRadarApp_PrintSpecies(&app->mainWindow, target->species, 72, 32);

    BOOL isLocal = (target->sourceFlags & MERCURY_RESEARCH_RADAR_SOURCE_NORMAL) != 0;
    MercuryResearchRadarApp_PrintAscii(
        &app->mainWindow,
        isLocal ? "LOCAL" : "RESEARCH",
        72,
        52);

    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "LEVEL", 72, 72);
    MercuryResearchRadarApp_PrintNumber(&app->mainWindow, target->minLevel, 3, 120, 72);
    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "-", 146, 72);
    MercuryResearchRadarApp_PrintNumber(&app->mainWindow, target->maxLevel, 3, 156, 72);

    Pokedex *pokedex = SaveData_GetPokedex(app->args->saveData);
    u16 searchLevel = MercuryResearchRadar_GetSelectedSearchLevel(
        &app->args->scanner,
        pokedex);

    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "SEARCH LV", 72, 92);
    MercuryResearchRadarApp_PrintNumber(&app->mainWindow, searchLevel, 3, 154, 92);

    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "CAUGHT", 72, 112);
    MercuryResearchRadarApp_PrintAscii(
        &app->mainWindow,
        Pokedex_HasCaughtSpecies(pokedex, target->species) ? "YES" : "NO",
        136,
        112);

    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "POTENTIAL", 72, 132);
    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "---", 154, 132);

    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "ABILITY MOVE ITEM", 72, 152);
    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "REVEALED BY SEARCH", 72, 168);

    MercuryResearchRadarApp_PrintAscii(&app->mainWindow, "REGISTERED", 8, 184);
    MercuryResearchRadarApp_PrintAscii(
        &app->mainWindow,
        app->args->scanner.registeredSpecies == target->species ? "YES" : "NO",
        104,
        184);

    Window_CopyToVRAM(&app->mainWindow);
    Bg_CopyTilemapBufferToVRAM(app->bgConfig, BG_LAYER_MAIN_1);
}

static void MercuryResearchRadarApp_DrawBottomText(MercuryResearchRadarApp *app)
{
    Window_FillTilemap(&app->subWindow, 0);

    MercuryResearchRadarApp_PrintAscii(&app->subWindow, "LOCAL", 8, 4);
    MercuryResearchRadarApp_PrintNumber(
        &app->subWindow,
        app->args->scanner.localCount,
        2,
        54,
        4);

    MercuryResearchRadarApp_PrintAscii(&app->subWindow, "RESEARCH", 104, 4);
    MercuryResearchRadarApp_PrintNumber(
        &app->subWindow,
        app->args->scanner.researchCount,
        2,
        176,
        4);

    MercuryResearchRadarApp_PrintAscii(
        &app->subWindow,
        "D-PAD TOUCH SELECT   R REGISTER   B BACK",
        4,
        184);

    Window_CopyToVRAM(&app->subWindow);
}

static BOOL MercuryResearchRadarApp_MoveSelection(
    MercuryResearchRadarApp *app,
    int delta)
{
    return MercuryResearchRadar_MoveSelection(&app->args->scanner, delta);
}

static BOOL MercuryResearchRadarApp_HandleTouch(MercuryResearchRadarApp *app)
{
    static const int sGridX[RADAR_GRID_COLUMNS] = { 16, 72, 128, 184 };
    static const int sGridY[RADAR_GRID_ROWS] = { 32, 72, 112, 152 };

    for (int row = 0; row < RADAR_GRID_ROWS; row++) {
        for (int col = 0; col < RADAR_GRID_COLUMNS; col++) {
            int index = row * RADAR_GRID_COLUMNS + col;

            if (index >= app->args->scanner.targetCount) {
                continue;
            }

            if (gSystem.touchX >= sGridX[col]
                && gSystem.touchX < sGridX[col] + 32
                && gSystem.touchY >= sGridY[row]
                && gSystem.touchY < sGridY[row] + 32) {
                if (app->args->scanner.selectedIndex != index) {
                    app->args->scanner.selectedIndex = index;
                    return TRUE;
                }

                return FALSE;
            }
        }
    }

    return FALSE;
}

static charcode_t MercuryResearchRadarApp_AsciiToCharCode(char c)
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

static void MercuryResearchRadarApp_PrintAscii(
    Window *window,
    const char *ascii,
    int x,
    int y)
{
    String *string = String_Init(96, HEAP_ID_FIELD2);

    for (int i = 0; ascii[i] != '\0'; i++) {
        String_AppendChar(string, MercuryResearchRadarApp_AsciiToCharCode(ascii[i]));
    }

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 2, 0),
        NULL);

    String_Free(string);
}

static void MercuryResearchRadarApp_PrintNumber(
    Window *window,
    int value,
    int digits,
    int x,
    int y)
{
    String *number = String_Init(8, HEAP_ID_FIELD2);

    String_FormatInt(number, value, digits, PADDING_MODE_NONE, CHARSET_MODE_EN);

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        number,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 2, 0),
        NULL);

    String_Free(number);
}

static void MercuryResearchRadarApp_PrintSpecies(
    Window *window,
    int species,
    int x,
    int y)
{
    String *name = MessageUtil_SpeciesName(species, HEAP_ID_FIELD2);

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        name,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 2, 0),
        NULL);

    String_Free(name);
}
'''


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def install_files(root: Path) -> None:
    header = root / "include/applications/mercury_research_radar.h"
    source = root / "src/applications/mercury_research_radar.c"

    header.parent.mkdir(parents=True, exist_ok=True)
    source.parent.mkdir(parents=True, exist_ok=True)

    header.write_text(HEADER)
    source.write_text(SOURCE)

    meson = root / "src/meson.build"
    replace_once(
        meson,
        "    'applications/town_map/context.c',\n",
        "    'applications/town_map/context.c',\n"
        "    'applications/mercury_research_radar.c',\n",
        "MR06B2C2 meson source",
    )


def validate(root: Path) -> None:
    header = (root / "include/applications/mercury_research_radar.h").read_text()
    source = (root / "src/applications/mercury_research_radar.c").read_text()
    meson = (root / "src/meson.build").read_text()
    item_use = (root / "src/item_use_functions.c").read_text()
    start_menu = (root / "src/start_menu.c").read_text()

    required = (
        "MercuryResearchRadarAppArgs",
        "gMercuryResearchRadarAppTemplate",
        "MercuryResearchRadar_OpenScanner",
        "MercuryResearchRadarApp_LoadBottomIcons",
        "PokeIconSpriteIndex",
        "PokeIconPaletteIndex",
        "gSystem.touchPressed",
        "PAD_BUTTON_R",
        "MercuryResearchRadar_RegisterSelected",
        "MercuryResearchRadar_GetSelectedSearchLevel",
    )
    combined = header + source
    for token in required:
        if token not in combined:
            raise SystemExit(f"MR06B2C2 missing {token}")

    if "'applications/mercury_research_radar.c'," not in meson:
        raise SystemExit("MR06B2C2 scanner source is not in src/meson.build")

    # Preserve the safety boundary: the real item is rebound only after this
    # visible application has proven it compiles.
    if "MercuryResearchRadar_OpenScanner" in item_use:
        raise SystemExit("MR06B2C2 rebound ITEM_POKE_RADAR too early")

    if "START_MENU_OPTION_ENCOUNTERS" in start_menu:
        raise SystemExit("MR06B2C2 standalone encounter menu regression")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06b2c2-dual-screen-scanner.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    wild_header = (root / "include/overlay006/wild_encounters.h").read_text()
    pokedex_header = (root / "include/pokedex.h").read_text()

    if "MercuryResearchRadarScannerState" not in wild_header:
        raise SystemExit("MR06B2C2 requires MR06B2C1 scanner session model")
    if "Pokedex_MercuryRadar_GetSearchLevel" not in pokedex_header:
        raise SystemExit("MR06B2C2 requires MR06B2B Search Level storage")

    install_files(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2C2_DUAL_SCREEN_DEXNAV_SCANNER",
        "status": "PASS",
        "top_screen": {
            "selected_species_icon": True,
            "species_name": True,
            "source_badge": ["LOCAL", "RESEARCH"],
            "level_range": True,
            "search_level": True,
            "caught_status": True,
            "potential_placeholder": True,
            "registered_status": True,
        },
        "bottom_screen": {
            "pokemon_icon_grid": "4x4",
            "max_visible_targets": 16,
            "dpad_selection": True,
            "touch_selection": True,
            "selection_cursor": True,
            "local_research_counts": True,
            "r_button_registration": True,
        },
        "standalone_encounter_menu": False,
        "poke_radar_item_rebound": False,
        "search_action_enabled": False,
        "normal_encounter_tables_modified": False,
        "next": "bind ITEM_POKE_RADAR only after this application compiles, then add guaranteed nearby target patch SEARCH",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
