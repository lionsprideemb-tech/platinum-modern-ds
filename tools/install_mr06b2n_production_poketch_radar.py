#!/usr/bin/env python3
"""MR06B2N — production Pokétch Research Radar + instant encounter.

Promotes the approved MR06B2K/M Pokétch visuals into the actual player ROM.

Production behavior:
- Adds a dedicated Research Radar Pokétch app (ID 25) on Platinum's unused
  poketch_unused_4 overlay; Pokémon History remains untouched.
- Area page lists all currently accessible wild species for the map:
  current-time LAND + SURF + owned fishing rods + legacy/fixed RESEARCH slots.
  Duplicate species merge their method flags and authored level ranges.
- Up to 12 icons per page, with touch paging.
- Touch a Pokémon for the polished native Pokétch hunter detail page.
- Detail page clearly separates authored battle Lv. range from Search Lv.
- SEARCH requests an immediate normal wild battle. No patch, chain, battery,
  walking, or "couldn't find it" roll.
- Encounter level stays inside the authored area range AND is hard-clamped to
  the next Gym Leader's current ace level, loaded dynamically from trainer data.
- Search Level is research progression only and never raises battle level.
- Potential stars are generated from Search Level and applied as unique 31 IVs.
- Surf/fishing availability respects progression (Surf badge; owned rods).

The older full-screen scanner code remains compiled only for compatibility
during this transition, but ITEM_POKE_RADAR no longer launches it from the Bag.
The player-facing hunter UI is the Pokétch app.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


APP_MAIN = r'''#include <nitro.h>
#include <nitro/sinit.h>

#include "applications/poketch/poketch_system.h"
#include "applications/poketch/unused/4/graphics.h"

#include "bag.h"
#include "generated/items.h"
#include "generated/moves.h"
#include "generated/species.h"
#include "heap.h"
#include "map_header_data.h"
#include "mercury_research_radar_shared.h"
#include "overlay006/wild_encounters.h"
#include "party.h"
#include "pokedex.h"
#include "poketch.h"
#include "rtc.h"
#include "savedata.h"
#include "sys_task.h"
#include "sys_task_manager.h"
#include "system.h"
#include "trainer_info.h"

#define RADAR_PAGE_SIZE 12

typedef struct PoketchResearchRadar {
    u8 state;
    u8 subState;
    u8 shouldExit;
    u8 detailActive;
    u8 page;
    u8 selectedIndex;
    u16 padding;
    ResearchRadarData data;
    ResearchRadarGraphics *graphics;
    PoketchSystem *poketchSys;
} PoketchResearchRadar;

typedef BOOL (*StateFunc)(PoketchResearchRadar *);

enum ResearchRadarState {
    STATE_LOAD_APP = 0,
    STATE_UPDATE_LOOP,
    STATE_SHUTDOWN,
};

static void NitroStaticInit(void);
static BOOL New(void **appData, PoketchSystem *poketchSys, BgConfig *bgConfig, u32 appID);
static BOOL Init(PoketchResearchRadar *appData, PoketchSystem *poketchSys, BgConfig *bgConfig, u32 appID);
static void Free(PoketchResearchRadar *appData);
static void Exit(void *appData);
static void Task_Main(SysTask *task, void *appData);
static void ChangeState(PoketchResearchRadar *appData, enum ResearchRadarState newState);
static BOOL State_LoadApp(PoketchResearchRadar *appData);
static BOOL State_UpdateApp(PoketchResearchRadar *appData);
static BOOL State_UnloadApp(PoketchResearchRadar *appData);
static void BuildCurrentAreaTargets(PoketchResearchRadar *appData);
static void AddTarget(
    ResearchRadarData *data,
    u16 species,
    u8 minLevel,
    u8 maxLevel,
    u8 methodFlags);
static int CurrentMercuryLandPeriod(void);
static void GetLandSlot(
    const WildEncounters *encounters,
    int period,
    int slotIndex,
    u16 *species,
    u8 *minLevel,
    u8 *maxLevel);
static void EnterDetail(PoketchResearchRadar *appData, int absoluteIndex);
static void RequestSelectedEncounter(PoketchResearchRadar *appData);
static BOOL TapAreaGrid(PoketchResearchRadar *appData, u32 x, u32 y);
static BOOL TapAreaPager(PoketchResearchRadar *appData, u32 x, u32 y);
static BOOL TapDetail(PoketchResearchRadar *appData, u32 x, u32 y);

static void NitroStaticInit(void)
{
    PoketchSystem_SetAppFunctions(New, Exit);
}

static BOOL New(void **appData, PoketchSystem *poketchSys, BgConfig *bgConfig, u32 appID)
{
    PoketchResearchRadar *radar = Heap_Alloc(
        HEAP_ID_POKETCH_APP,
        sizeof(PoketchResearchRadar));

    if (radar != NULL) {
        MI_CpuClear8(radar, sizeof(PoketchResearchRadar));

        if (Init(radar, poketchSys, bgConfig, appID)
            && SysTask_Start(Task_Main, radar, 1) != NULL) {
            *appData = radar;
            return TRUE;
        }

        Heap_Free(radar);
    }

    return FALSE;
}

static BOOL Init(PoketchResearchRadar *appData, PoketchSystem *poketchSys, BgConfig *bgConfig, u32 appID)
{
    appData->poketchSys = poketchSys;
    appData->state = STATE_LOAD_APP;
    appData->subState = 0;
    appData->shouldExit = FALSE;
    appData->detailActive = FALSE;
    appData->page = 0;
    appData->selectedIndex = 0;

    BuildCurrentAreaTargets(appData);

    if (!ResearchRadarGraphics_New(
            &appData->graphics,
            &appData->data,
            bgConfig)) {
        return FALSE;
    }

    return TRUE;
}

static void Free(PoketchResearchRadar *appData)
{
    ResearchRadarGraphics_Free(appData->graphics);
    Heap_Free(appData);
}

static void Task_Main(SysTask *task, void *appData)
{
    static const StateFunc stateFuncs[] = {
        State_LoadApp,
        State_UpdateApp,
        State_UnloadApp
    };

    PoketchResearchRadar *radar = appData;

    if (radar->state < NELEMS(stateFuncs)
        && stateFuncs[radar->state](radar)) {
        PoketchSystem *poketchSys = radar->poketchSys;

        Free(radar);
        SysTask_Done(task);
        PoketchSystem_NotifyAppUnloaded(poketchSys);
    }
}

static void Exit(void *appData)
{
    ((PoketchResearchRadar *)appData)->shouldExit = TRUE;
}

static void ChangeState(PoketchResearchRadar *appData, enum ResearchRadarState newState)
{
    appData->state = appData->shouldExit ? STATE_SHUTDOWN : newState;
    appData->subState = 0;
}

static BOOL State_LoadApp(PoketchResearchRadar *appData)
{
    switch (appData->subState) {
    case 0:
        ResearchRadarGraphics_StartTask(
            appData->graphics,
            RESEARCH_RADAR_GRAPHICS_INIT);
        appData->subState++;
        break;

    case 1:
        if (ResearchRadarGraphics_TaskIsNotActive(
                appData->graphics,
                RESEARCH_RADAR_GRAPHICS_INIT)) {
            PoketchSystem_NotifyAppLoaded(appData->poketchSys);
            ChangeState(appData, STATE_UPDATE_LOOP);
        }
        break;
    }

    return FALSE;
}

static BOOL State_UpdateApp(PoketchResearchRadar *appData)
{
    if (appData->shouldExit) {
        ChangeState(appData, STATE_SHUTDOWN);
        return FALSE;
    }

    if (JOY_NEW(PAD_BUTTON_B) && appData->detailActive) {
        appData->detailActive = FALSE;
        ResearchRadarGraphics_ShowArea(
            appData->graphics,
            appData->page);
        return FALSE;
    }

    u32 x, y;
    if (!PoketchSystem_GetDisplayTappedCoords(&x, &y)) {
        return FALSE;
    }

    if (appData->detailActive) {
        TapDetail(appData, x, y);
    } else if (!TapAreaPager(appData, x, y)) {
        TapAreaGrid(appData, x, y);
    }

    return FALSE;
}

static BOOL State_UnloadApp(PoketchResearchRadar *appData)
{
    switch (appData->subState) {
    case 0:
        ResearchRadarGraphics_StartTask(
            appData->graphics,
            RESEARCH_RADAR_GRAPHICS_FREE);
        appData->subState++;
        break;

    case 1:
        if (ResearchRadarGraphics_NoActiveTasks(appData->graphics)) {
            return TRUE;
        }
        break;
    }

    return FALSE;
}

static int CurrentMercuryLandPeriod(void)
{
    RTCTime time;
    RTC_GetCurrentTime(&time);

    if (time.hour >= 5 && time.hour < 10) {
        return 0;
    }

    if (time.hour >= 10 && time.hour < 17) {
        return 1;
    }

    if (time.hour >= 17 && time.hour < 21) {
        return 2;
    }

    return 3;
}

static void GetLandSlot(
    const WildEncounters *encounters,
    int period,
    int slotIndex,
    u16 *species,
    u8 *minLevel,
    u8 *maxLevel)
{
    if (encounters->mercuryTimedGrassMagic == MERCURY_TIMED_GRASS_MAGIC) {
        const MercuryGrassEncounter *slot =
            &encounters->mercuryTimedGrass[period][slotIndex];

        *species = slot->species;
        *minLevel = slot->minLevel;
        *maxLevel = slot->maxLevel;
    } else {
        const GrassEncounter *slot =
            &encounters->grassEncounters.encounters[slotIndex];

        *species = slot->species;
        *minLevel = slot->level;
        *maxLevel = slot->level;
    }
}

static void AddTarget(
    ResearchRadarData *data,
    u16 species,
    u8 minLevel,
    u8 maxLevel,
    u8 methodFlags)
{
    if (species == SPECIES_NONE || minLevel == 0 || maxLevel == 0) {
        return;
    }

    for (int i = 0; i < data->count; i++) {
        if (data->targets[i].species != species) {
            continue;
        }

        if (minLevel < data->targets[i].minLevel) {
            data->targets[i].minLevel = minLevel;
        }

        if (maxLevel > data->targets[i].maxLevel) {
            data->targets[i].maxLevel = maxLevel;
        }

        data->targets[i].methodFlags |= methodFlags;
        return;
    }

    if (data->count >= RESEARCH_RADAR_MAX_TARGETS) {
        return;
    }

    ResearchRadarTarget *target = &data->targets[data->count++];
    target->species = species;
    target->minLevel = minLevel;
    target->maxLevel = maxLevel;
    target->methodFlags = methodFlags;
    target->searchLevel = 0;
    target->potentialStars = 0;
}

static void BuildCurrentAreaTargets(PoketchResearchRadar *appData)
{
    FieldSystem *fieldSystem = PoketchSystem_GetFieldSystem(appData->poketchSys);
    SaveData *saveData = PoketchSystem_GetSaveData(appData->poketchSys);
    const WildEncounters *encounters = MapHeaderData_GetWildEncounters(fieldSystem);

    MI_CpuClear8(&appData->data, sizeof(appData->data));

    if (encounters == NULL) {
        return;
    }

    int period = CurrentMercuryLandPeriod();

    if (encounters->grassEncounters.encounterRate > 0) {
        for (int i = 0; i < MAX_GRASS_ENCOUNTERS; i++) {
            u16 species;
            u8 minLevel, maxLevel;
            GetLandSlot(
                encounters,
                period,
                i,
                &species,
                &minLevel,
                &maxLevel);
            AddTarget(
                &appData->data,
                species,
                minLevel,
                maxLevel,
                RESEARCH_RADAR_METHOD_LAND);
        }
    }

    TrainerInfo *trainerInfo = SaveData_GetTrainerInfo(saveData);
    BOOL surfUnlocked = TrainerInfo_HasBadge(trainerInfo, 3);

    if (surfUnlocked && encounters->surfEncounters.encounterRate > 0) {
        for (int i = 0; i < MAX_WATER_ENCOUNTERS; i++) {
            const WaterEncounter *slot =
                &encounters->surfEncounters.encounters[i];

            AddTarget(
                &appData->data,
                slot->species,
                slot->minLevel,
                slot->maxLevel,
                RESEARCH_RADAR_METHOD_SURF);
        }
    }

    Bag *bag = SaveData_GetBag(saveData);

    static const struct {
        u16 item;
        const WaterEncounters *dummy;
        u8 method;
    } access[] = {
        { ITEM_OLD_ROD, NULL, RESEARCH_RADAR_METHOD_OLD_ROD },
        { ITEM_GOOD_ROD, NULL, RESEARCH_RADAR_METHOD_GOOD_ROD },
        { ITEM_SUPER_ROD, NULL, RESEARCH_RADAR_METHOD_SUPER_ROD },
    };

    for (int rod = 0; rod < 3; rod++) {
        if (Bag_GetItemQuantity(
                bag,
                access[rod].item,
                HEAP_ID_POKETCH_APP) == 0) {
            continue;
        }

        const WaterEncounters *rodEncounters = NULL;

        switch (rod) {
        case 0:
            rodEncounters = &encounters->oldRodEncounters;
            break;
        case 1:
            rodEncounters = &encounters->goodRodEncounters;
            break;
        default:
            rodEncounters = &encounters->superRodEncounters;
            break;
        }

        if (rodEncounters->encounterRate == 0) {
            continue;
        }

        for (int i = 0; i < MAX_WATER_ENCOUNTERS; i++) {
            const WaterEncounter *slot = &rodEncounters->encounters[i];

            AddTarget(
                &appData->data,
                slot->species,
                slot->minLevel,
                slot->maxLevel,
                access[rod].method);
        }
    }

    if (encounters->grassEncounters.encounterRate > 0) {
        static const u8 radarLandSlots[MAX_RADAR_ENCOUNTERS] = {
            4, 5, 10, 11
        };

        for (int i = 0; i < MAX_RADAR_ENCOUNTERS; i++) {
            u16 species = encounters->radarEncounters[i];
            u16 landSpecies;
            u8 minLevel, maxLevel;

            GetLandSlot(
                encounters,
                period,
                radarLandSlots[i],
                &landSpecies,
                &minLevel,
                &maxLevel);

            AddTarget(
                &appData->data,
                species,
                minLevel,
                maxLevel,
                RESEARCH_RADAR_METHOD_RESEARCH);
        }
    }

    Pokedex *pokedex = SaveData_GetPokedex(saveData);
    u8 levelCap = MercuryResearchRadar_GetCurrentGymAceCap(saveData);

    for (int i = 0; i < appData->data.count; i++) {
        ResearchRadarTarget *target = &appData->data.targets[i];

        target->searchLevel =
            Pokedex_MercuryRadar_GetSearchLevel(
                pokedex,
                target->species);

        if (target->minLevel > levelCap) {
            target->minLevel = levelCap;
        }

        if (target->maxLevel > levelCap) {
            target->maxLevel = levelCap;
        }

        if (target->minLevel > target->maxLevel) {
            target->minLevel = target->maxLevel;
        }
    }
}

static void EnterDetail(PoketchResearchRadar *appData, int absoluteIndex)
{
    if (absoluteIndex < 0 || absoluteIndex >= appData->data.count) {
        return;
    }

    ResearchRadarTarget *target = &appData->data.targets[absoluteIndex];

    if (target->potentialStars == 0) {
        target->potentialStars =
            MercuryResearchRadar_GeneratePotentialStars(
                target->searchLevel);
    }

    appData->selectedIndex = absoluteIndex;
    appData->detailActive = TRUE;

    ResearchRadarGraphics_ShowDetail(
        appData->graphics,
        absoluteIndex);
    PoketchSystem_PlayCry(target->species, 0);
}

static void RequestSelectedEncounter(PoketchResearchRadar *appData)
{
    if (appData->selectedIndex >= appData->data.count) {
        return;
    }

    FieldSystem *fieldSystem = PoketchSystem_GetFieldSystem(appData->poketchSys);
    ResearchRadarTarget *target =
        &appData->data.targets[appData->selectedIndex];

    MercuryResearchRadar_RequestInstantEncounter(
        fieldSystem,
        target->species,
        target->minLevel,
        target->maxLevel,
        target->methodFlags,
        target->potentialStars);
}

static BOOL TapAreaGrid(PoketchResearchRadar *appData, u32 x, u32 y)
{
    if (x < 12 || x >= 200 || y < 30 || y >= 158) {
        return FALSE;
    }

    int col = (x - 14) / 46;
    int row = (y - 34) / 42;

    if (col < 0 || col >= 4 || row < 0 || row >= 3) {
        return FALSE;
    }

    int slot = row * 4 + col;
    int absoluteIndex = appData->page * RADAR_PAGE_SIZE + slot;

    if (absoluteIndex >= appData->data.count) {
        return FALSE;
    }

    EnterDetail(appData, absoluteIndex);
    return TRUE;
}

static BOOL TapAreaPager(PoketchResearchRadar *appData, u32 x, u32 y)
{
    if (y < 160 || y >= 191) {
        return FALSE;
    }

    int pageCount =
        (appData->data.count + RADAR_PAGE_SIZE - 1)
        / RADAR_PAGE_SIZE;

    if (pageCount <= 1) {
        return FALSE;
    }

    if (x < 72 && appData->page > 0) {
        appData->page--;
        ResearchRadarGraphics_ShowArea(
            appData->graphics,
            appData->page);
        return TRUE;
    }

    if (x > 128 && appData->page + 1 < pageCount) {
        appData->page++;
        ResearchRadarGraphics_ShowArea(
            appData->graphics,
            appData->page);
        return TRUE;
    }

    return FALSE;
}

static BOOL TapDetail(PoketchResearchRadar *appData, u32 x, u32 y)
{
    // Small upper-left return target, visually represented by the header icon.
    if (x < 38 && y < 32) {
        appData->detailActive = FALSE;
        ResearchRadarGraphics_ShowArea(
            appData->graphics,
            appData->page);
        return TRUE;
    }

    if (x >= 10 && x <= 190 && y >= 132 && y <= 178) {
        RequestSelectedEncounter(appData);
        return TRUE;
    }

    return FALSE;
}
'''


GRAPHICS_H = r'''#ifndef POKEPLATINUM_POKETCH_UNUSED_4_GRAPHICS_H
#define POKEPLATINUM_POKETCH_UNUSED_4_GRAPHICS_H

#include "applications/poketch/poketch_animation.h"
#include "applications/poketch/poketch_task.h"

#include "bg_window.h"

#define RESEARCH_RADAR_MAX_TARGETS 40
#define RESEARCH_RADAR_PAGE_SIZE   12
#define RESEARCH_RADAR_TASK_SLOTS  4

#include "mercury_research_radar_shared.h"

typedef struct ResearchRadarTarget {
    u16 species;
    u16 searchLevel;
    u8 minLevel;
    u8 maxLevel;
    u8 methodFlags;
    u8 potentialStars;
} ResearchRadarTarget;

typedef struct ResearchRadarData {
    ResearchRadarTarget targets[RESEARCH_RADAR_MAX_TARGETS];
    u8 count;
    u8 padding[3];
} ResearchRadarData;

typedef struct ResearchRadarGraphics {
    const ResearchRadarData *data;
    BgConfig *bgConfig;
    u32 activeTasks[POKETCH_TASK_SLOT_BASE + RESEARCH_RADAR_TASK_SLOTS];
    PoketchAnimation_AnimationManager *animMan;
    PoketchAnimation_AnimatedSpriteData *sprites[RESEARCH_RADAR_PAGE_SIZE];
    PoketchAnimation_SpriteData spriteData;
    u32 iconIndices[RESEARCH_RADAR_PAGE_SIZE];
    u8 page;
    BOOL spriteDataLoaded;
} ResearchRadarGraphics;

enum ResearchRadarGraphicsTask {
    RESEARCH_RADAR_GRAPHICS_INIT = 0,
    RESEARCH_RADAR_GRAPHICS_FREE,
};

BOOL ResearchRadarGraphics_New(
    ResearchRadarGraphics **dest,
    const ResearchRadarData *data,
    BgConfig *bgConfig);
void ResearchRadarGraphics_Free(ResearchRadarGraphics *graphics);
void ResearchRadarGraphics_StartTask(
    ResearchRadarGraphics *graphics,
    enum ResearchRadarGraphicsTask taskID);
BOOL ResearchRadarGraphics_TaskIsNotActive(
    ResearchRadarGraphics *graphics,
    enum ResearchRadarGraphicsTask taskID);
BOOL ResearchRadarGraphics_NoActiveTasks(
    ResearchRadarGraphics *graphics);
void ResearchRadarGraphics_ShowArea(
    ResearchRadarGraphics *graphics,
    int page);
void ResearchRadarGraphics_ShowDetail(
    ResearchRadarGraphics *graphics,
    int absoluteIndex);

#endif
'''


GRAPHICS_C = r'''#include "applications/poketch/unused/4/graphics.h"

#include <nitro.h>

#include "applications/poketch/poketch_animation.h"
#include "applications/poketch/poketch_graphics.h"
#include "applications/poketch/poketch_task.h"

#include "constants/charcode.h"

#include "font.h"
#include "heap.h"
#include "message_util.h"
#include "pokemon_icon.h"
#include "string_gf.h"
#include "sys_task_manager.h"
#include "text.h"

#include "res/graphics/poketch/poketch.naix"

#define GRID_X(c) (36 + 44 * (c))
#define GRID_Y(r) (52 + 42 * (r))

#define MON_ANIM_DATA(r, c)                                     \
    {                                                           \
        .translation = { FX32_CONST(GRID_X(c)),                 \
            FX32_CONST(GRID_Y(r)) },                            \
        .animIdx = 4,                                           \
        .flip = NNS_G2D_RENDERERFLIP_NONE,                      \
        .oamPriority = 2,                                       \
        .priority = (r) * 4 + (c),                              \
        .hasAffineTransform = TRUE,                             \
    }

static void EndTask(PoketchTaskManager *taskMan);
static void Task_DrawBackground(SysTask *task, void *taskMan);
static void Task_FreeBackground(SysTask *task, void *taskMan);
static void RemovePageSprites(ResearchRadarGraphics *graphics);
static void LoadPageSprites(ResearchRadarGraphics *graphics, int page);
static void DrawAreaSurface(ResearchRadarGraphics *graphics, int page);
static void DrawDetailSurface(ResearchRadarGraphics *graphics, int absoluteIndex);
static void PrintAscii(Window *window, const char *ascii, int x, int y);
static void PrintNumber(Window *window, int value, int digits, int x, int y);
static void PrintPotential(Window *window, u8 stars, int x, int y);
static const char *MethodLabel(u8 flags);
static charcode_t AsciiToCharCode(char c);

BOOL ResearchRadarGraphics_New(
    ResearchRadarGraphics **dest,
    const ResearchRadarData *data,
    BgConfig *bgConfig)
{
    ResearchRadarGraphics *graphics = Heap_Alloc(
        HEAP_ID_POKETCH_APP,
        sizeof(ResearchRadarGraphics));

    if (graphics == NULL) {
        return FALSE;
    }

    MI_CpuClear8(graphics, sizeof(ResearchRadarGraphics));
    PoketchTask_InitActiveTaskList(
        graphics->activeTasks,
        RESEARCH_RADAR_TASK_SLOTS);

    graphics->data = data;
    graphics->bgConfig = PoketchGraphics_GetBgConfig();
    graphics->animMan = PoketchGraphics_GetAnimationManager();
    graphics->page = 0;
    *dest = graphics;

    return TRUE;
}

void ResearchRadarGraphics_Free(ResearchRadarGraphics *graphics)
{
    if (graphics != NULL) {
        Heap_Free(graphics);
    }
}

static const PoketchTask sResearchRadarTasks[] = {
    { RESEARCH_RADAR_GRAPHICS_INIT, Task_DrawBackground, 0 },
    { RESEARCH_RADAR_GRAPHICS_FREE, Task_FreeBackground, 0 },
    { 0 }
};

void ResearchRadarGraphics_StartTask(
    ResearchRadarGraphics *graphics,
    enum ResearchRadarGraphicsTask taskID)
{
    PoketchTask_Start(
        sResearchRadarTasks,
        taskID,
        graphics,
        graphics->data,
        graphics->activeTasks,
        2,
        HEAP_ID_POKETCH_APP);
}

BOOL ResearchRadarGraphics_TaskIsNotActive(
    ResearchRadarGraphics *graphics,
    enum ResearchRadarGraphicsTask taskID)
{
    return PoketchTask_TaskIsNotActive(
        graphics->activeTasks,
        taskID);
}

BOOL ResearchRadarGraphics_NoActiveTasks(
    ResearchRadarGraphics *graphics)
{
    return PoketchTask_NoActiveTasks(graphics->activeTasks);
}

static void EndTask(PoketchTaskManager *taskMan)
{
    ResearchRadarGraphics *graphics =
        PoketchTask_GetTaskData(taskMan);

    PoketchTask_EndTask(
        graphics->activeTasks,
        taskMan);
}

static void Task_DrawBackground(SysTask *task, void *taskMan)
{
    static const BgTemplate bgTemplate = {
        .x = 0,
        .y = 0,
        .bufferSize = 0x800,
        .baseTile = 0,
        .screenSize = BG_SCREEN_SIZE_256x256,
        .colorMode = GX_BG_COLORMODE_16,
        .screenBase = GX_BG_SCRBASE_0x7000,
        .charBase = GX_BG_CHARBASE_0x00000,
        .bgExtPltt = GX_BG_EXTPLTT_01,
        .priority = 2,
        .areaOver = 0,
        .mosaic = FALSE,
    };

    ResearchRadarGraphics *graphics =
        PoketchTask_GetTaskData(taskMan);

    Bg_InitFromTemplate(
        graphics->bgConfig,
        BG_LAYER_SUB_2,
        &bgTemplate,
        BG_TYPE_STATIC);
    Bg_FillTilesRange(
        graphics->bgConfig,
        BG_LAYER_SUB_2,
        4,
        1,
        0);
    Bg_FillTilemapRect(
        graphics->bgConfig,
        BG_LAYER_SUB_2,
        0,
        0,
        0,
        POKETCH_WIDTH_TILES,
        POKETCH_HEIGHT_TILES,
        0);

    PoketchGraphics_LoadActivePalette(0, 0);
    PoketchTask_LoadPokemonIconLuminancePalette(0);

    PoketchAnimation_LoadSpriteFromNARC(
        &graphics->spriteData,
        NARC_INDEX_GRAPHIC__POKETCH,
        poke_icon_cell_NCER_lz,
        poke_icon_anim_NANR_lz,
        HEAP_ID_POKETCH_APP);
    graphics->spriteDataLoaded = TRUE;

    DrawAreaSurface(graphics, 0);

    GXSDispCnt dispCnt = GXS_GetDispCnt();
    GXS_SetVisiblePlane(
        dispCnt.visiblePlane | GX_PLANEMASK_BG2);

    EndTask(taskMan);
}

static void Task_FreeBackground(SysTask *task, void *taskMan)
{
    ResearchRadarGraphics *graphics =
        PoketchTask_GetTaskData(taskMan);

    RemovePageSprites(graphics);

    if (graphics->spriteDataLoaded) {
        PoketchAnimation_FreeSpriteData(
            &graphics->spriteData);
        graphics->spriteDataLoaded = FALSE;
    }

    Bg_FreeTilemapBuffer(
        graphics->bgConfig,
        BG_LAYER_SUB_2);
    EndTask(taskMan);
}

static void RemovePageSprites(ResearchRadarGraphics *graphics)
{
    for (int i = 0; i < RESEARCH_RADAR_PAGE_SIZE; i++) {
        if (graphics->sprites[i] != NULL) {
            PoketchAnimation_RemoveAnimatedSprite(
                graphics->animMan,
                graphics->sprites[i]);
            graphics->sprites[i] = NULL;
        }
    }
}

static void LoadPageSprites(ResearchRadarGraphics *graphics, int page)
{
    static const PoketchAnimation_AnimationData animData[] = {
        MON_ANIM_DATA(0, 0),
        MON_ANIM_DATA(0, 1),
        MON_ANIM_DATA(0, 2),
        MON_ANIM_DATA(0, 3),
        MON_ANIM_DATA(1, 0),
        MON_ANIM_DATA(1, 1),
        MON_ANIM_DATA(1, 2),
        MON_ANIM_DATA(1, 3),
        MON_ANIM_DATA(2, 0),
        MON_ANIM_DATA(2, 1),
        MON_ANIM_DATA(2, 2),
        MON_ANIM_DATA(2, 3),
    };

    RemovePageSprites(graphics);

    int first = page * RESEARCH_RADAR_PAGE_SIZE;
    int count = graphics->data->count - first;

    if (count > RESEARCH_RADAR_PAGE_SIZE) {
        count = RESEARCH_RADAR_PAGE_SIZE;
    }

    if (count < 0) {
        count = 0;
    }

    for (int i = 0; i < count; i++) {
        const ResearchRadarTarget *target =
            &graphics->data->targets[first + i];

        graphics->iconIndices[i] =
            PokeIconSpriteIndex(
                target->species,
                FALSE,
                0);

        graphics->sprites[i] =
            PoketchAnimation_SetupNewAnimatedSprite(
                graphics->animMan,
                &animData[i],
                &graphics->spriteData);

        PoketchAnimation_SetSpriteCharNo(
            graphics->sprites[i],
            i * 16);
        PoketchAnimation_SetCParam(
            graphics->sprites[i],
            PokeIconPaletteIndex(
                target->species,
                0,
                FALSE));
    }

    for (int i = count; i < RESEARCH_RADAR_PAGE_SIZE; i++) {
        graphics->sprites[i] = NULL;
    }

    if (count > 0) {
        PoketchTask_LoadPokemonIcons(
            0,
            graphics->iconIndices,
            count,
            FALSE);
    }
}

static void DrawAreaSurface(ResearchRadarGraphics *graphics, int page)
{
    Bg_FillTilemapRect(
        graphics->bgConfig,
        BG_LAYER_SUB_2,
        0,
        0,
        0,
        POKETCH_WIDTH_TILES,
        POKETCH_HEIGHT_TILES,
        0);

    Window header;
    Window_Add(
        graphics->bgConfig,
        &header,
        BG_LAYER_SUB_2,
        2,
        1,
        24,
        3,
        0,
        1);
    Window_FillTilemap(&header, 4);
    Window_PutToTilemap(&header);

    PrintAscii(&header, "RESEARCH RADAR", 0, 3);
    PrintAscii(&header, "ALL", 152, 3);

    Window_FillRectWithColor(
        &header,
        8,
        0,
        23,
        192,
        1);

    Window_LoadTiles(&header);
    Window_Remove(&header);

    int pageCount =
        (graphics->data->count + RESEARCH_RADAR_PAGE_SIZE - 1)
        / RESEARCH_RADAR_PAGE_SIZE;

    if (pageCount > 1) {
        Window pager;
        Window_Add(
            graphics->bgConfig,
            &pager,
            BG_LAYER_SUB_2,
            2,
            20,
            24,
            3,
            0,
            80);
        Window_FillTilemap(&pager, 4);
        Window_PutToTilemap(&pager);

        if (page > 0) {
            PrintAscii(&pager, "<", 0, 1);
        }

        PrintNumber(&pager, page + 1, 1, 82, 1);
        PrintAscii(&pager, "/", 92, 1);
        PrintNumber(&pager, pageCount, 1, 102, 1);

        if (page + 1 < pageCount) {
            PrintAscii(&pager, ">", 176, 1);
        }

        Window_LoadTiles(&pager);
        Window_Remove(&pager);
    }

    graphics->page = page;
    LoadPageSprites(graphics, page);
    Bg_CopyTilemapBufferToVRAM(
        graphics->bgConfig,
        BG_LAYER_SUB_2);
}

void ResearchRadarGraphics_ShowArea(
    ResearchRadarGraphics *graphics,
    int page)
{
    if (graphics == NULL) {
        return;
    }

    DrawAreaSurface(graphics, page);
}

static const char *MethodLabel(u8 flags)
{
    int categories = 0;

    if (flags & RESEARCH_RADAR_METHOD_LAND) {
        categories++;
    }

    if (flags & RESEARCH_RADAR_METHOD_SURF) {
        categories++;
    }

    if (flags & (RESEARCH_RADAR_METHOD_OLD_ROD
        | RESEARCH_RADAR_METHOD_GOOD_ROD
        | RESEARCH_RADAR_METHOD_SUPER_ROD)) {
        categories++;
    }

    if (flags & RESEARCH_RADAR_METHOD_RESEARCH) {
        categories++;
    }

    if (categories > 1) {
        return "MULTI";
    }

    if (flags & RESEARCH_RADAR_METHOD_RESEARCH) {
        return "RESEARCH";
    }

    if (flags & RESEARCH_RADAR_METHOD_SURF) {
        return "SURF";
    }

    if (flags & (RESEARCH_RADAR_METHOD_OLD_ROD
        | RESEARCH_RADAR_METHOD_GOOD_ROD
        | RESEARCH_RADAR_METHOD_SUPER_ROD)) {
        return "FISH";
    }

    return "LAND";
}

static void DrawDetailSurface(
    ResearchRadarGraphics *graphics,
    int absoluteIndex)
{
    if (absoluteIndex < 0
        || absoluteIndex >= graphics->data->count) {
        return;
    }

    const ResearchRadarTarget *target =
        &graphics->data->targets[absoluteIndex];

    int page = absoluteIndex / RESEARCH_RADAR_PAGE_SIZE;
    int slot = absoluteIndex % RESEARCH_RADAR_PAGE_SIZE;

    if (graphics->page != page) {
        LoadPageSprites(graphics, page);
        graphics->page = page;
    }

    Bg_FillTilemapRect(
        graphics->bgConfig,
        BG_LAYER_SUB_2,
        0,
        0,
        0,
        POKETCH_WIDTH_TILES,
        POKETCH_HEIGHT_TILES,
        0);

    for (int i = 0; i < RESEARCH_RADAR_PAGE_SIZE; i++) {
        if (graphics->sprites[i] == NULL) {
            continue;
        }

        PoketchAnimation_HideSprite(
            graphics->sprites[i],
            i != slot);
    }

    if (graphics->sprites[slot] != NULL) {
        PoketchAnimation_SetSpritePosition(
            graphics->sprites[slot],
            FX32_CONST(62),
            FX32_CONST(86));
    }

    Window detail;
    Window_Add(
        graphics->bgConfig,
        &detail,
        BG_LAYER_SUB_2,
        2,
        1,
        24,
        21,
        0,
        1);
    Window_FillTilemap(&detail, 4);
    Window_PutToTilemap(&detail);

    // Small return glyph: touch here or press B to return to the area grid.
    PrintAscii(&detail, "<", 0, 3);

    String *speciesName =
        MessageUtil_SpeciesName(
            target->species,
            HEAP_ID_POKETCH_APP);

    if (speciesName != NULL) {
        Text_AddPrinterWithParamsAndColor(
            &detail,
            FONT_SYSTEM,
            speciesName,
            22,
            3,
            TEXT_SPEED_NO_TRANSFER,
            TEXT_COLOR(1, 8, 4),
            NULL);
        String_Free(speciesName);
    }

    const char *method = MethodLabel(target->methodFlags);
    PrintAscii(&detail, method, 132, 3);

    // Header divider.
    Window_FillRectWithColor(
        &detail,
        8,
        0,
        21,
        192,
        1);

    // Pokétch-native scanner reticle around the native monochrome icon.
    Window_FillRectWithColor(&detail, 8, 12, 40, 18, 2);
    Window_FillRectWithColor(&detail, 8, 12, 40, 2, 18);
    Window_FillRectWithColor(&detail, 8, 66, 40, 18, 2);
    Window_FillRectWithColor(&detail, 8, 82, 40, 2, 18);
    Window_FillRectWithColor(&detail, 8, 12, 94, 18, 2);
    Window_FillRectWithColor(&detail, 8, 12, 78, 2, 18);
    Window_FillRectWithColor(&detail, 8, 66, 94, 18, 2);
    Window_FillRectWithColor(&detail, 8, 82, 78, 2, 18);
    Window_FillRectWithColor(&detail, 8, 46, 34, 4, 2);
    Window_FillRectWithColor(&detail, 8, 46, 100, 4, 2);
    Window_FillRectWithColor(&detail, 8, 6, 66, 4, 2);
    Window_FillRectWithColor(&detail, 8, 88, 66, 4, 2);

    // Real battle level is deliberately separate from Search Level.
    PrintAscii(&detail, "LV", 2, 111);
    PrintNumber(&detail, target->minLevel, 2, 24, 111);
    PrintAscii(&detail, "-", 42, 111);
    PrintNumber(&detail, target->maxLevel, 2, 50, 111);

    PrintAscii(&detail, "SEARCH", 102, 39);
    PrintNumber(&detail, target->searchLevel, 3, 154, 39);

    PrintAscii(&detail, "POTENTIAL", 102, 66);
    PrintPotential(&detail, target->potentialStars, 120, 85);

    // One large hunt action; no redundant move/ability/item fields.
    Window_FillRectWithColor(
        &detail,
        8,
        8,
        132,
        176,
        2);
    Window_FillRectWithColor(
        &detail,
        8,
        8,
        160,
        176,
        2);
    Window_FillRectWithColor(
        &detail,
        8,
        8,
        132,
        2,
        30);
    Window_FillRectWithColor(
        &detail,
        8,
        182,
        132,
        2,
        30);
    PrintAscii(&detail, "SEARCH", 70, 139);

    Window_LoadTiles(&detail);
    Window_Remove(&detail);

    Bg_CopyTilemapBufferToVRAM(
        graphics->bgConfig,
        BG_LAYER_SUB_2);
}

void ResearchRadarGraphics_ShowDetail(
    ResearchRadarGraphics *graphics,
    int absoluteIndex)
{
    if (graphics == NULL) {
        return;
    }

    DrawDetailSurface(
        graphics,
        absoluteIndex);
}

static void PrintAscii(
    Window *window,
    const char *ascii,
    int x,
    int y)
{
    String *string =
        String_Init(32, HEAP_ID_POKETCH_APP);

    for (int i = 0; ascii[i] != '\0'; i++) {
        String_AppendChar(
            string,
            AsciiToCharCode(ascii[i]));
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

static void PrintNumber(
    Window *window,
    int value,
    int digits,
    int x,
    int y)
{
    String *string =
        String_Init(8, HEAP_ID_POKETCH_APP);

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

static void PrintPotential(
    Window *window,
    u8 stars,
    int x,
    int y)
{
    String *string =
        String_Init(4, HEAP_ID_POKETCH_APP);

    for (int i = 0; i < 3; i++) {
        String_AppendChar(
            string,
            i < stars ? CHAR_STAR : CHAR_MINUS);
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

static charcode_t AsciiToCharCode(char c)
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
    case '/':
        return CHAR_SLASH;
    case '<':
        return CHAR_ARROW_LEFT;
    case '>':
        return CHAR_ARROW_RIGHT;
    default:
        return CHAR_SPACE;
    }
}
'''


SHARED_H = r'''#ifndef POKEPLATINUM_MERCURY_RESEARCH_RADAR_SHARED_H
#define POKEPLATINUM_MERCURY_RESEARCH_RADAR_SHARED_H

#include "field/field_system_decl.h"
#include "savedata.h"

enum MercuryResearchRadarMethodFlags {
    RESEARCH_RADAR_METHOD_LAND       = (1 << 0),
    RESEARCH_RADAR_METHOD_SURF       = (1 << 1),
    RESEARCH_RADAR_METHOD_OLD_ROD    = (1 << 2),
    RESEARCH_RADAR_METHOD_GOOD_ROD   = (1 << 3),
    RESEARCH_RADAR_METHOD_SUPER_ROD  = (1 << 4),
    RESEARCH_RADAR_METHOD_RESEARCH   = (1 << 5),
};

typedef struct MercuryResearchRadarEncounterRequest {
    u16 species;
    u8 minLevel;
    u8 maxLevel;
    u8 methodFlags;
    u8 potentialStars;
    BOOL pending;
} MercuryResearchRadarEncounterRequest;

void MercuryResearchRadar_RequestInstantEncounter(
    FieldSystem *fieldSystem,
    u16 species,
    u8 minLevel,
    u8 maxLevel,
    u8 methodFlags,
    u8 potentialStars);
BOOL MercuryResearchRadar_TakeInstantEncounterRequest(
    MercuryResearchRadarEncounterRequest *request);
u8 MercuryResearchRadar_GetCurrentGymAceCap(
    SaveData *saveData);
u8 MercuryResearchRadar_GeneratePotentialStars(
    u16 searchLevel);

#endif
'''


SHARED_C = r'''#include "mercury_research_radar_shared.h"

#include <nitro.h>

#include "generated/trainers.h"

#include "party.h"
#include "pokedex.h"
#include "system.h"
#include "trainer_data.h"
#include "trainer_info.h"

#include "struct_defs/trainer.h"
#include "struct_defs/trainer_data.h"

static MercuryResearchRadarEncounterRequest sMercuryRadarRequest;

void MercuryResearchRadar_RequestInstantEncounter(
    FieldSystem *fieldSystem,
    u16 species,
    u8 minLevel,
    u8 maxLevel,
    u8 methodFlags,
    u8 potentialStars)
{
    if (fieldSystem == NULL
        || species == 0
        || minLevel == 0
        || maxLevel < minLevel) {
        return;
    }

    sMercuryRadarRequest.species = species;
    sMercuryRadarRequest.minLevel = minLevel;
    sMercuryRadarRequest.maxLevel = maxLevel;
    sMercuryRadarRequest.methodFlags = methodFlags;
    sMercuryRadarRequest.potentialStars = potentialStars;
    sMercuryRadarRequest.pending = TRUE;
}

BOOL MercuryResearchRadar_TakeInstantEncounterRequest(
    MercuryResearchRadarEncounterRequest *request)
{
    if (!sMercuryRadarRequest.pending || request == NULL) {
        return FALSE;
    }

    *request = sMercuryRadarRequest;
    MI_CpuClear8(
        &sMercuryRadarRequest,
        sizeof(sMercuryRadarRequest));
    return TRUE;
}

static u16 TrainerPartyLevel(
    const void *partyData,
    u8 dataType,
    int index)
{
    switch (dataType) {
    case TRDATATYPE_BASE:
        return ((const TrainerMonBase *)partyData)[index].level;

    case TRDATATYPE_WITH_MOVES:
        return ((const TrainerMonWithMoves *)partyData)[index].level;

    case TRDATATYPE_WITH_ITEM:
        return ((const TrainerMonWithItem *)partyData)[index].level;

    case TRDATATYPE_WITH_MOVES_AND_ITEM:
        return ((const TrainerMonWithMovesAndItem *)partyData)[index].level;

    default:
        return 1;
    }
}

u8 MercuryResearchRadar_GetCurrentGymAceCap(
    SaveData *saveData)
{
    static const u16 sGymLeaders[] = {
        TRAINER_LEADER_ROARK,
        TRAINER_LEADER_GARDENIA,
        TRAINER_LEADER_FANTINA,
        TRAINER_LEADER_MAYLENE,
        TRAINER_LEADER_WAKE,
        TRAINER_LEADER_BYRON,
        TRAINER_LEADER_CANDICE,
        TRAINER_LEADER_VOLKNER,
    };

    if (saveData == NULL) {
        return 100;
    }

    TrainerInfo *trainerInfo =
        SaveData_GetTrainerInfo(saveData);
    int badgeCount =
        TrainerInfo_BadgeCount(trainerInfo);

    if (badgeCount >= 8) {
        // All Gym ceilings have been cleared. League-specific scaling can
        // layer on later without allowing any pre-Gym Radar bypass.
        return 100;
    }

    Trainer trainer;
    Trainer_Load(
        sGymLeaders[badgeCount],
        &trainer);

    u8 partyData[
        sizeof(TrainerMonWithMovesAndItem)
        * MAX_PARTY_SIZE];

    MI_CpuClear8(
        partyData,
        sizeof(partyData));

    Trainer_LoadParty(
        sGymLeaders[badgeCount],
        partyData);

    u16 aceLevel = 1;

    for (int i = 0; i < trainer.header.partySize; i++) {
        u16 level = TrainerPartyLevel(
            partyData,
            trainer.header.monDataType,
            i);

        if (level > aceLevel) {
            aceLevel = level;
        }
    }

    if (aceLevel > 100) {
        aceLevel = 100;
    }

    return (u8)aceLevel;
}

u8 MercuryResearchRadar_GeneratePotentialStars(
    u16 searchLevel)
{
    u8 oneStar;
    u8 twoStar;
    u8 threeStar;

    if (searchLevel < 5) {
        oneStar = 0;
        twoStar = 0;
        threeStar = 0;
    } else if (searchLevel < 10) {
        oneStar = 14;
        twoStar = 1;
        threeStar = 0;
    } else if (searchLevel < 25) {
        oneStar = 17;
        twoStar = 9;
        threeStar = 1;
    } else if (searchLevel < 50) {
        oneStar = 17;
        twoStar = 16;
        threeStar = 7;
    } else if (searchLevel < 100) {
        oneStar = 15;
        twoStar = 17;
        threeStar = 6;
    } else {
        oneStar = 8;
        twoStar = 24;
        threeStar = 12;
    }

    u32 roll = LCRNG_RandMod(100);

    if (roll < oneStar) {
        return 1;
    }

    roll -= oneStar;

    if (roll < twoStar) {
        return 2;
    }

    roll -= twoStar;

    if (roll < threeStar) {
        return 3;
    }

    return 0;
}
'''


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def patch_app_id(root: Path) -> None:
    path = root / "generated/poketch_apps.txt"
    text = path.read_text()

    if "POKETCH_APPID_RESEARCHRADAR" not in text:
        replace_once(
            path,
            "POKETCH_APPID_MAX\n",
            "POKETCH_APPID_RESEARCHRADAR\n"
            "POKETCH_APPID_MAX\n",
            "MR06B2N Poketch app ID",
        )


def patch_app_overlay_table(root: Path) -> None:
    path = root / "src/applications/poketch/poketch_system.c"

    replace_once(
        path,
        """    { POKETCH_APPID_TRAINERCOUNTER, FS_OVERLAY_ID(poketch_trainer_counter) },
    { POKETCH_APPID_POKEMONHISTORY, FS_OVERLAY_ID(poketch_pokemon_history) }
};""",
        """    { POKETCH_APPID_TRAINERCOUNTER, FS_OVERLAY_ID(poketch_trainer_counter) },
    { POKETCH_APPID_POKEMONHISTORY, FS_OVERLAY_ID(poketch_pokemon_history) },
    { POKETCH_APPID_RESEARCHRADAR, FS_OVERLAY_ID(poketch_unused_4) }
};""",
        "MR06B2N Poketch overlay map",
    )


def install_app_sources(root: Path) -> None:
    (root / "src/applications/poketch/unused/4/main.c").write_text(APP_MAIN)
    (root / "src/applications/poketch/unused/4/graphics.c").write_text(GRAPHICS_C)
    (root / "include/applications/poketch/unused/4/graphics.h").write_text(GRAPHICS_H)


def install_shared_runtime(root: Path) -> None:
    (root / "include/mercury_research_radar_shared.h").write_text(SHARED_H)
    (root / "src/mercury_research_radar_shared.c").write_text(SHARED_C)

    meson = root / "src/meson.build"
    text = meson.read_text()

    if "'mercury_research_radar_shared.c'," not in text:
        replace_once(
            meson,
            "    'map_header_data.c',\n",
            "    'map_header_data.c',\n"
            "    'mercury_research_radar_shared.c',\n",
            "MR06B2N shared runtime meson",
        )


def patch_field_instant_encounter(root: Path) -> None:
    path = root / "src/overlay005/field_control.c"

    replace_once(
        path,
        '#include "map_header_data.h"\n',
        '#include "map_header_data.h"\n'
        '#include "mercury_research_radar_shared.h"\n',
        "MR06B2N shared request include",
    )

    replace_once(
        path,
        '#include "trainer_info.h"\n',
        '#include "trainer_info.h"\n'
        '#include "field_battle_data_transfer.h"\n',
        "MR06B2N battle DTO include",
    )

    helper_anchor = """static int Field_CheckTrainerInfo(void);

static void FieldInput_Clear(FieldInput *input)
"""
    helper = r'''static int Field_CheckTrainerInfo(void);

static BOOL MercuryResearchRadar_StartPendingEncounter(
    FieldSystem *fieldSystem)
{
    MercuryResearchRadarEncounterRequest request;

    if (!MercuryResearchRadar_TakeInstantEncounterRequest(
            &request)) {
        return FALSE;
    }

    u8 levelCap =
        MercuryResearchRadar_GetCurrentGymAceCap(
            fieldSystem->saveData);

    u8 minLevel = request.minLevel;
    u8 maxLevel = request.maxLevel;

    if (minLevel > levelCap) {
        minLevel = levelCap;
    }

    if (maxLevel > levelCap) {
        maxLevel = levelCap;
    }

    if (minLevel > maxLevel) {
        minLevel = maxLevel;
    }

    u8 level = minLevel;

    if (maxLevel > minLevel) {
        level += LCRNG_RandMod(
            maxLevel - minLevel + 1);
    }

    FieldBattleDTO *dto =
        FieldBattleDTO_New(
            HEAP_ID_FIELD2,
            BATTLE_TYPE_WILD_MON);
    FieldBattleDTO_Init(
        dto,
        fieldSystem);

    CreateWildMon_Scripted(
        fieldSystem,
        request.species,
        level,
        dto);

    // If a species is available only through water/fishing, keep the battle
    // presentation appropriate. Species also available on land use land.
    if (!(request.methodFlags & RESEARCH_RADAR_METHOD_LAND)
        && !(request.methodFlags & RESEARCH_RADAR_METHOD_RESEARCH)
        && (request.methodFlags & (
            RESEARCH_RADAR_METHOD_SURF
            | RESEARCH_RADAR_METHOD_OLD_ROD
            | RESEARCH_RADAR_METHOD_GOOD_ROD
            | RESEARCH_RADAR_METHOD_SUPER_ROD))) {
        FieldBattleDTO_SetWaterTerrain(dto);
    }

    Pokemon *targetMon =
        Party_GetPokemonBySlotIndex(
            dto->parties[BATTLER_ENEMY_1],
            0);

    u8 perfectIV = 31;
    u8 chosenStats[3] = {
        0xFF, 0xFF, 0xFF
    };

    for (int star = 0;
         star < request.potentialStars && star < 3;
         star++) {
        u8 stat;

        do {
            stat = LCRNG_RandMod(6);
        } while ((star > 0 && stat == chosenStats[0])
            || (star > 1 && stat == chosenStats[1]));

        chosenStats[star] = stat;
        Pokemon_SetValue(
            targetMon,
            MON_DATA_HP_IV + stat,
            &perfectIV);
    }

    Pokemon_CalcLevelAndStats(targetMon);

    Pokedex_MercuryRadar_IncrementSearchLevel(
        SaveData_GetPokedex(fieldSystem->saveData),
        request.species);

    Encounter_NewVsWild(
        fieldSystem,
        dto);
    return TRUE;
}

static void FieldInput_Clear(FieldInput *input)
'''
    replace_once(
        path,
        helper_anchor,
        helper,
        "MR06B2N instant encounter helper",
    )

    replace_once(
        path,
        """BOOL FieldInput_Process(const FieldInput *input, FieldSystem *fieldSystem)
{
    if (input->dummy5 == FALSE""",
        """BOOL FieldInput_Process(const FieldInput *input, FieldSystem *fieldSystem)
{
    if (MercuryResearchRadar_StartPendingEncounter(fieldSystem)) {
        return TRUE;
    }

    if (input->dummy5 == FALSE""",
        "MR06B2N field request consumption",
    )


def patch_registration(root: Path) -> None:
    jubilife = root / "res/field/scripts/scripts_jubilife_city.s"
    text = jubilife.read_text()

    anchor = "    RegisterPoketchApp POKETCH_APPID_PARTYSTATUS\n"
    if "RegisterPoketchApp POKETCH_APPID_RESEARCHRADAR" not in text:
        count = text.count(anchor)
        if count < 1:
            raise SystemExit("MR06B2N Jubilife Poketch registration anchor missing")
        text = text.replace(
            anchor,
            anchor
            + "    RegisterPoketchApp POKETCH_APPID_RESEARCHRADAR\n",
            1,
        )
        jubilife.write_text(text)

    sandgem = root / "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s"
    text = sandgem.read_text()

    if "RegisterPoketchApp POKETCH_APPID_RESEARCHRADAR" not in text:
        anchor = """    SetVar VAR_0x8005, 1
    Common_GiveItemQuantity
    Message SandgemTownLab_Text_ThatsThePokemonRadar
"""
        count = text.count(anchor)
        if count != 2:
            raise SystemExit(
                f"MR06B2N expected two Rowan Radar grant anchors, found {count}"
            )

        text = text.replace(
            anchor,
            """    SetVar VAR_0x8005, 1
    Common_GiveItemQuantity
    RegisterPoketchApp POKETCH_APPID_RESEARCHRADAR
    Message SandgemTownLab_Text_ThatsThePokemonRadar
""",
        )
        sandgem.write_text(text)


def patch_item_description(root: Path) -> None:
    path = root / "res/items/data/poke_radar.json"
    data = json.loads(path.read_text())
    data["description"] = [
        "A research tool installed in the\\n",
        "Pokétch. It lists huntable Pokémon\\n",
        "and starts a selected encounter."
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def patch_old_item_frontend(root: Path) -> None:
    """Bag use should return to field with the Pokétch Radar selected.

    Field/registered use only selects the app for the next Pokétch reload;
    it intentionally does not reopen the obsolete full-screen scanner.
    """
    path = root / "src/item_use_functions.c"
    text = path.read_text()

    if '#include "poketch.h"\n' not in text:
        replace_once(
            path,
            '#include "pokedex.h"\n',
            '#include "pokedex.h"\n'
            '#include "poketch.h"\n',
            "MR06B2N Poketch item include",
        )

    old = """static void UsePokeRadarFromMenu(ItemMenuUseContext *usageContext, const ItemUseContext *additionalContext)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(usageContext->fieldTask);
    StartMenu *menu = FieldTask_GetEnv(usageContext->fieldTask);

    FieldSystem_StartFieldMap(fieldSystem);

    menu->callback = MercuryResearchRadar_FieldTask;
    menu->taskData = MercuryResearchRadar_NewFieldTaskContext();
    menu->state = START_MENU_STATE_NEW_TASK;
}

static BOOL UsePokeRadarInField(ItemFieldUseContext *usageContext)
{
    FieldSystem_CreateTask(
        usageContext->fieldSystem,
        MercuryResearchRadar_FieldTask,
        MercuryResearchRadar_NewFieldTaskContext());

    return FALSE;
}
"""

    new = """static void UsePokeRadarFromMenu(ItemMenuUseContext *usageContext, const ItemUseContext *additionalContext)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(usageContext->fieldTask);
    StartMenu *menu = FieldTask_GetEnv(usageContext->fieldTask);
    Poketch *poketch = SaveData_GetPoketch(fieldSystem->saveData);

    Poketch_RegisterApp(poketch, POKETCH_APPID_RESEARCHRADAR);
    poketch->appIndex = POKETCH_APPID_RESEARCHRADAR;

    // Returning from the Bag rebuilds the field/Pokétch and therefore loads
    // Research Radar directly as the selected native app.
    FieldSystem_StartFieldMap(fieldSystem);
    menu->state = START_MENU_STATE_END;
}

static BOOL UsePokeRadarInField(ItemFieldUseContext *usageContext)
{
    Poketch *poketch =
        SaveData_GetPoketch(usageContext->fieldSystem->saveData);

    Poketch_RegisterApp(poketch, POKETCH_APPID_RESEARCHRADAR);
    poketch->appIndex = POKETCH_APPID_RESEARCHRADAR;

    // Do not launch the superseded full-screen scanner. The selected app is
    // persistent and will be shown on the next normal Pokétch reload/cycle.
    return FALSE;
}
"""

    if old not in text:
        raise SystemExit("MR06B2N old Radar item frontend anchor missing")

    path.write_text(text.replace(old, new, 1))


def validate(root: Path) -> None:
    app_ids = (root / "generated/poketch_apps.txt").read_text()
    system = (root / "src/applications/poketch/poketch_system.c").read_text()
    app = (root / "src/applications/poketch/unused/4/main.c").read_text()
    gfx = (root / "src/applications/poketch/unused/4/graphics.c").read_text()
    shared = (root / "src/mercury_research_radar_shared.c").read_text()
    field = (root / "src/overlay005/field_control.c").read_text()
    item = (root / "src/item_use_functions.c").read_text()
    history = (root / "src/applications/poketch/pokemon_history/main.c").read_text()

    checks = {
        "dedicated_app_id": "POKETCH_APPID_RESEARCHRADAR" in app_ids,
        "unused_overlay_repurposed": "POKETCH_APPID_RESEARCHRADAR, FS_OVERLAY_ID(poketch_unused_4)" in system,
        "pokemon_history_preserved": "Poketch_PokemonHistorySize" in history,
        "all_method_land": "RESEARCH_RADAR_METHOD_LAND" in app,
        "all_method_surf": "RESEARCH_RADAR_METHOD_SURF" in app,
        "all_method_rods": "ITEM_OLD_ROD" in app and "ITEM_SUPER_ROD" in app,
        "research_slots": "radarEncounters" in app,
        "pagination": "RADAR_PAGE_SIZE" in app and "TapAreaPager" in app,
        "detail_search_level": '"SEARCH"' in gfx,
        "detail_potential": '"POTENTIAL"' in gfx,
        "detail_level": '"LV"' in gfx,
        "instant_request": "MercuryResearchRadar_RequestInstantEncounter" in app,
        "instant_battle": "Encounter_NewVsWild" in field,
        "dynamic_gym_cap": "Trainer_LoadParty" in shared and "sGymLeaders" in shared,
        "potential_iv_apply": "MON_DATA_HP_IV + stat" in field,
        "search_level_increment": "Pokedex_MercuryRadar_IncrementSearchLevel" in field,
        "old_fullscreen_item_not_launched": "MercuryResearchRadar_FieldTask" not in item[item.find("static void UsePokeRadarFromMenu"):item.find("static void UseSprayDuckFromMenu")],
        "pokemon_history_not_overwritten": "RESEARCH RADAR" not in history,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MR06B2N validation failed: "
            + ", ".join(failed)
        )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2n-production-poketch-radar.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    header = root / "include/overlay006/wild_encounters.h"
    header_text = header.read_text()

    for token in (
        "MERCURY_TIMED_GRASS_MAGIC",
        "MercuryGrassEncounter",
        "mercuryTimedGrass",
    ):
        if token not in header_text:
            raise SystemExit(
                f"MR06B2N requires installed Mercury TOD encounter runtime: missing {token}"
            )

    if "Pokedex_MercuryRadar_GetSearchLevel" not in (
        root / "include/pokedex.h"
    ).read_text():
        raise SystemExit("MR06B2N requires MR06B2B Search Level storage")

    patch_app_id(root)
    patch_app_overlay_table(root)
    install_app_sources(root)
    install_shared_runtime(root)
    patch_field_instant_encounter(root)
    patch_registration(root)
    patch_item_description(root)
    patch_old_item_frontend(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2N_PRODUCTION_POKETCH_RADAR",
        "status": "PASS",
        "player_facing_ui": "dedicated native Poketch Research Radar app",
        "app_id": 25,
        "overlay": "poketch_unused_4 repurposed",
        "pokemon_history_preserved": True,
        "top_screen": "normal live Platinum overworld",
        "area_page": {
            "page_size": 12,
            "pagination": True,
            "methods": [
                "current-time land",
                "Surf when progression permits",
                "Old Rod when owned",
                "Good Rod when owned",
                "Super Rod when owned",
                "Research Radar slots",
            ],
            "duplicates_merged": True,
        },
        "detail_page": {
            "battle_level_range": True,
            "search_level": True,
            "potential_stars": True,
            "encounter_method": True,
            "moves_shown": False,
            "abilities_shown": False,
            "held_items_shown": False,
            "wide_search_control": True,
        },
        "search": {
            "instant_encounter": True,
            "rustling_patch": False,
            "chain_required": False,
            "battery_required": False,
            "random_search_failure": False,
        },
        "level_safety": {
            "search_level_changes_battle_level": False,
            "authored_area_range_respected": True,
            "pre_eight_badges_cap": "next Gym Leader current ace loaded dynamically from trainer data",
            "eight_badges": "Gym ceiling released; League-specific cap can layer later",
        },
        "potential": "0-3 stars; each star guarantees one unique 31 IV",
        "search_level_increments_on_instant_encounter": True,
        "old_fullscreen_scanner_launched_by_poke_radar_item": False,
        "research_habitat_layer": "uses currently installed Research/radar slots; MR06B3 fixed foreign habitat import remains separate",
        "honey_tree_species_folded_into_radar": False,
    }

    args.report.write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
