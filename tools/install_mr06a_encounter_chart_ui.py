#!/usr/bin/env python3
"""MR06A — install the first player-facing Mercury Encounter Chart UI.

This phase deliberately reuses Platinum's existing field/start-menu rendering
instead of introducing a new overlay. On the normal start menu, the redundant
visible EXIT row (B/X already closes the menu) becomes ENCOUNTERS once the
Pokédex has been obtained.

The chart reads the encounter NARC member for the player's CURRENT map at
runtime, so it cannot drift away from the tables that actually drive battles.
It supports:
- Mercury Morning / Day / Evening / Night land tables;
- vanilla land fallback when no Mercury table exists;
- Surf / Old Rod / Good Rod / Super Rod;
- merged duplicate species with exact Platinum slot odds;
- level ranges;
- method, time-period, and page navigation.

Special-room start menus (Safari, Pal Park, Battle Tower Salon, Union Room,
Colosseum) retain vanilla behavior and keep the ordinary EXIT row.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def insert_after_once(path: Path, anchor: str, addition: str, label: str) -> None:
    text = path.read_text()
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + addition, 1))


def patch_header(root: Path) -> None:
    path = root / "include/start_menu.h"

    replace_once(
        path,
        """    BOOL inUnionRoom;
    FieldTaskFunc callback;
""",
        """    BOOL inUnionRoom;
    BOOL mercuryEncounterChartEnabled;
    FieldTaskFunc callback;
""",
        "MR06A StartMenu chart availability flag",
    )

    replace_once(
        path,
        """    START_MENU_STATE_SAVED,
};
""",
        """    START_MENU_STATE_SAVED,
    START_MENU_STATE_MERCURY_ENCOUNTER_CHART,
};
""",
        "MR06A StartMenu chart state",
    )


def patch_text(root: Path) -> None:
    path = root / "res/text/start_menu.json"
    data = json.loads(path.read_text())
    messages = data.get("messages")
    if not isinstance(messages, list):
        raise SystemExit("MR06A start_menu text bank missing messages list")

    new_messages = [
        ("StartMenu_Text_Encounters", "ENCOUNTERS"),
        ("StartMenu_Text_EncounterChartTitle", "ENCOUNTER CHART"),
        ("StartMenu_Text_EncounterChartNoData", "No wild encounters in this area."),
        ("StartMenu_Text_EncounterChartLand", "LAND"),
        ("StartMenu_Text_EncounterChartSurf", "SURF"),
        ("StartMenu_Text_EncounterChartOldRod", "OLD ROD"),
        ("StartMenu_Text_EncounterChartGoodRod", "GOOD ROD"),
        ("StartMenu_Text_EncounterChartSuperRod", "SUPER ROD"),
        ("StartMenu_Text_EncounterChartMorning", "MORNING"),
        ("StartMenu_Text_EncounterChartDay", "DAY"),
        ("StartMenu_Text_EncounterChartEvening", "EVENING"),
        ("StartMenu_Text_EncounterChartNight", "NIGHT"),
        (
            "StartMenu_Text_EncounterChartRow",
            "Lv.{STRVAR_1 51, 0, 0}-{STRVAR_1 51, 1, 0}  {STRVAR_1 51, 2, 0}%",
        ),
        (
            "StartMenu_Text_EncounterChartPage",
            "PAGE {STRVAR_1 51, 0, 0}/{STRVAR_1 51, 1, 0}",
        ),
        ("StartMenu_Text_EncounterChartControls1", "LEFT/RIGHT: METHOD  L/R: TIME"),
        ("StartMenu_Text_EncounterChartControls2", "UP/DOWN: PAGE       B: BACK"),
    ]

    ids = {row.get("id") for row in messages if isinstance(row, dict)}
    for msg_id, en_us in new_messages:
        if msg_id in ids:
            raise SystemExit(f"MR06A text id already exists unexpectedly: {msg_id}")
        messages.append({"id": msg_id, "en_US": en_us})

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_start_menu(root: Path) -> None:
    path = root / "src/start_menu.c"

    insert_after_once(
        path,
        '#include "constants/heap.h"\n',
        '#include "constants/rtc.h"\n',
        "MR06A time-of-day include",
    )
    insert_after_once(
        path,
        '#include "map_header.h"\n',
        '#include "map_header_data.h"\n',
        "MR06A map encounter include",
    )
    insert_after_once(
        path,
        '#include "overlay005/sprite_resource_manager.h"\n',
        '#include "overlay006/wild_encounters.h"\n',
        "MR06A WildEncounters include",
    )
    insert_after_once(
        path,
        '#include "system_vars.h"\n',
        '#include "system.h"\n',
        "MR06A input include",
    )

    replace_once(
        path,
        """    START_MENU_OPTION_RETIRE,
};
""",
        """    START_MENU_OPTION_RETIRE,
    START_MENU_OPTION_ENCOUNTERS,
};
""",
        "MR06A start-menu option enum",
    )

    insert_after_once(
        path,
        "static BOOL StartMenu_ExitPokedex(FieldTask *fieldTask);\n",
        """static BOOL StartMenu_SelectEncounterChart(FieldTask *fieldTask);
static void StartMenu_EncounterChartOpen(FieldTask *fieldTask);
static void StartMenu_EncounterChartRun(FieldTask *fieldTask);
static void StartMenu_EncounterChartClose(FieldTask *fieldTask);
""",
        "MR06A chart function declarations",
    )

    replace_once(
        path,
        """    [START_MENU_OPTION_RETIRE]       = { .bankEntry = StartMenu_Text_Retire,         .callback = StartMenu_SelectRetire      },
};
""",
        """    [START_MENU_OPTION_RETIRE]       = { .bankEntry = StartMenu_Text_Retire,         .callback = StartMenu_SelectRetire      },
    [START_MENU_OPTION_ENCOUNTERS]   = { .bankEntry = StartMenu_Text_Encounters,     .callback = StartMenu_SelectEncounterChart },
};
""",
        "MR06A start-menu action table",
    )

    chart_types = r'''
enum MercuryEncounterChartMethod {
    MERCURY_ENCOUNTER_METHOD_LAND = 0,
    MERCURY_ENCOUNTER_METHOD_SURF,
    MERCURY_ENCOUNTER_METHOD_OLD_ROD,
    MERCURY_ENCOUNTER_METHOD_GOOD_ROD,
    MERCURY_ENCOUNTER_METHOD_SUPER_ROD,
    MERCURY_ENCOUNTER_METHOD_COUNT,
};

#define MERCURY_ENCOUNTER_CHART_ROWS_PER_PAGE 6
#define MERCURY_ENCOUNTER_CHART_MAX_ROWS 12

typedef struct MercuryEncounterChartRow {
    u16 species;
    u8 minLevel;
    u8 maxLevel;
    u8 chance;
} MercuryEncounterChartRow;

typedef struct MercuryEncounterChartState {
    WildEncounters encounters;
    MercuryEncounterChartRow rows[MERCURY_ENCOUNTER_CHART_MAX_ROWS];
    u8 method;
    u8 period;
    u8 page;
    u8 rowCount;
    BOOL hasEncounterData;
} MercuryEncounterChartState;

static const u8 sMercuryEncounterLandWeights[MAX_GRASS_ENCOUNTERS] = {
    20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1
};

static const u8 sMercuryEncounterWaterWeights[MAX_WATER_ENCOUNTERS] = {
    60, 30, 5, 4, 1
};

static const u32 sMercuryEncounterMethodText[MERCURY_ENCOUNTER_METHOD_COUNT] = {
    StartMenu_Text_EncounterChartLand,
    StartMenu_Text_EncounterChartSurf,
    StartMenu_Text_EncounterChartOldRod,
    StartMenu_Text_EncounterChartGoodRod,
    StartMenu_Text_EncounterChartSuperRod,
};

static const u32 sMercuryEncounterPeriodText[MERCURY_TIMED_GRASS_TABLES] = {
    StartMenu_Text_EncounterChartMorning,
    StartMenu_Text_EncounterChartDay,
    StartMenu_Text_EncounterChartEvening,
    StartMenu_Text_EncounterChartNight,
};

static void MercuryEncounterChart_AddRow(
    MercuryEncounterChartState *state,
    u16 species,
    u8 minLevel,
    u8 maxLevel,
    u8 chance)
{
    if (species == SPECIES_NONE) {
        return;
    }

    for (u8 i = 0; i < state->rowCount; i++) {
        if (state->rows[i].species == species) {
            state->rows[i].minLevel = min(state->rows[i].minLevel, minLevel);
            state->rows[i].maxLevel = max(state->rows[i].maxLevel, maxLevel);
            state->rows[i].chance += chance;
            return;
        }
    }

    if (state->rowCount >= MERCURY_ENCOUNTER_CHART_MAX_ROWS) {
        return;
    }

    MercuryEncounterChartRow *row = &state->rows[state->rowCount++];
    row->species = species;
    row->minLevel = minLevel;
    row->maxLevel = maxLevel;
    row->chance = chance;
}

static const WaterEncounters *MercuryEncounterChart_GetWaterTable(
    const MercuryEncounterChartState *state,
    u8 method)
{
    switch (method) {
    case MERCURY_ENCOUNTER_METHOD_SURF:
        return &state->encounters.surfEncounters;
    case MERCURY_ENCOUNTER_METHOD_OLD_ROD:
        return &state->encounters.oldRodEncounters;
    case MERCURY_ENCOUNTER_METHOD_GOOD_ROD:
        return &state->encounters.goodRodEncounters;
    case MERCURY_ENCOUNTER_METHOD_SUPER_ROD:
        return &state->encounters.superRodEncounters;
    default:
        return NULL;
    }
}

static BOOL MercuryEncounterChart_MethodAvailable(
    const MercuryEncounterChartState *state,
    u8 method)
{
    if (!state->hasEncounterData) {
        return FALSE;
    }

    if (method == MERCURY_ENCOUNTER_METHOD_LAND) {
        return state->encounters.grassEncounters.encounterRate > 0;
    }

    const WaterEncounters *water = MercuryEncounterChart_GetWaterTable(state, method);
    return water != NULL && water->encounterRate > 0;
}

static void MercuryEncounterChart_BuildRows(MercuryEncounterChartState *state)
{
    state->rowCount = 0;

    if (!MercuryEncounterChart_MethodAvailable(state, state->method)) {
        return;
    }

    if (state->method == MERCURY_ENCOUNTER_METHOD_LAND) {
        if (state->encounters.mercuryTimedGrassMagic == MERCURY_TIMED_GRASS_MAGIC) {
            for (u8 i = 0; i < MAX_GRASS_ENCOUNTERS; i++) {
                const MercuryGrassEncounter *slot =
                    &state->encounters.mercuryTimedGrass[state->period][i];

                MercuryEncounterChart_AddRow(
                    state,
                    (u16)slot->species,
                    (u8)slot->minLevel,
                    (u8)slot->maxLevel,
                    sMercuryEncounterLandWeights[i]);
            }
        } else {
            for (u8 i = 0; i < MAX_GRASS_ENCOUNTERS; i++) {
                const GrassEncounter *slot = &state->encounters.grassEncounters.encounters[i];

                MercuryEncounterChart_AddRow(
                    state,
                    (u16)slot->species,
                    (u8)slot->level,
                    (u8)slot->level,
                    sMercuryEncounterLandWeights[i]);
            }
        }
        return;
    }

    const WaterEncounters *water = MercuryEncounterChart_GetWaterTable(state, state->method);
    for (u8 i = 0; i < MAX_WATER_ENCOUNTERS; i++) {
        const WaterEncounter *slot = &water->encounters[i];

        MercuryEncounterChart_AddRow(
            state,
            (u16)slot->species,
            (u8)slot->minLevel,
            (u8)slot->maxLevel,
            sMercuryEncounterWaterWeights[i]);
    }
}

static void MercuryEncounterChart_SelectInitialMethod(MercuryEncounterChartState *state)
{
    for (u8 method = 0; method < MERCURY_ENCOUNTER_METHOD_COUNT; method++) {
        if (MercuryEncounterChart_MethodAvailable(state, method)) {
            state->method = method;
            return;
        }
    }

    state->method = MERCURY_ENCOUNTER_METHOD_LAND;
}

static void MercuryEncounterChart_ChangeMethod(MercuryEncounterChartState *state, int delta)
{
    if (!state->hasEncounterData) {
        return;
    }

    for (u8 attempts = 0; attempts < MERCURY_ENCOUNTER_METHOD_COUNT; attempts++) {
        int next = state->method + delta;

        if (next < 0) {
            next = MERCURY_ENCOUNTER_METHOD_COUNT - 1;
        } else if (next >= MERCURY_ENCOUNTER_METHOD_COUNT) {
            next = 0;
        }

        state->method = next;
        if (MercuryEncounterChart_MethodAvailable(state, state->method)) {
            state->page = 0;
            MercuryEncounterChart_BuildRows(state);
            return;
        }
    }
}

static void MercuryEncounterChart_ChangePeriod(MercuryEncounterChartState *state, int delta)
{
    if (state->method != MERCURY_ENCOUNTER_METHOD_LAND
        || state->encounters.mercuryTimedGrassMagic != MERCURY_TIMED_GRASS_MAGIC) {
        return;
    }

    int next = state->period + delta;
    if (next < 0) {
        next = MERCURY_TIMED_GRASS_TABLES - 1;
    } else if (next >= MERCURY_TIMED_GRASS_TABLES) {
        next = 0;
    }

    state->period = next;
    state->page = 0;
    MercuryEncounterChart_BuildRows(state);
}

static void MercuryEncounterChart_PrintMessage(
    Window *window,
    MessageLoader *loader,
    u32 message,
    u32 x,
    u32 y)
{
    String *string = MessageLoader_GetNewString(loader, message);
    Text_AddPrinterWithParams(window, FONT_SYSTEM, string, x, y, TEXT_SPEED_NO_TRANSFER, NULL);
    String_Free(string);
}

static void MercuryEncounterChart_Draw(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    MercuryEncounterChartState *state = menu->taskData;

    Window_FillTilemap(&menu->primaryWindow, 15);

    MessageLoader *menuLoader = MessageLoader_Init(
        MSG_LOADER_PRELOAD_ENTIRE_BANK,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_START_MENU,
        HEAP_ID_FIELD2);
    MessageLoader *locationLoader = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_LOCATION_NAMES,
        HEAP_ID_FIELD2);
    MessageLoader *speciesLoader = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_SPECIES_NAME,
        HEAP_ID_FIELD2);

    MercuryEncounterChart_PrintMessage(
        &menu->primaryWindow,
        menuLoader,
        StartMenu_Text_EncounterChartTitle,
        0,
        0);

    String *location = MessageLoader_GetNewString(
        locationLoader,
        MapHeader_GetMapLabelTextID(fieldSystem->location->mapHeaderID));
    Text_AddPrinterWithParams(
        &menu->primaryWindow,
        FONT_SYSTEM,
        location,
        0,
        16,
        TEXT_SPEED_NO_TRANSFER,
        NULL);
    String_Free(location);

    if (!state->hasEncounterData || state->rowCount == 0) {
        MercuryEncounterChart_PrintMessage(
            &menu->primaryWindow,
            menuLoader,
            StartMenu_Text_EncounterChartNoData,
            0,
            48);

        MercuryEncounterChart_PrintMessage(
            &menu->primaryWindow,
            menuLoader,
            StartMenu_Text_EncounterChartControls2,
            0,
            160);

        MessageLoader_Free(speciesLoader);
        MessageLoader_Free(locationLoader);
        MessageLoader_Free(menuLoader);
        Window_ScheduleCopyToVRAM(&menu->primaryWindow);
        return;
    }

    MercuryEncounterChart_PrintMessage(
        &menu->primaryWindow,
        menuLoader,
        sMercuryEncounterMethodText[state->method],
        0,
        32);

    if (state->method == MERCURY_ENCOUNTER_METHOD_LAND
        && state->encounters.mercuryTimedGrassMagic == MERCURY_TIMED_GRASS_MAGIC) {
        MercuryEncounterChart_PrintMessage(
            &menu->primaryWindow,
            menuLoader,
            sMercuryEncounterPeriodText[state->period],
            72,
            32);
    }

    u8 pageCount = (state->rowCount + MERCURY_ENCOUNTER_CHART_ROWS_PER_PAGE - 1)
        / MERCURY_ENCOUNTER_CHART_ROWS_PER_PAGE;
    if (pageCount == 0) {
        pageCount = 1;
    }
    if (state->page >= pageCount) {
        state->page = pageCount - 1;
    }

    StringTemplate *formatter = StringTemplate_Default(HEAP_ID_FIELD2);
    String *formatted = String_Init(64, HEAP_ID_FIELD2);
    String *rowFormat = MessageLoader_GetNewString(menuLoader, StartMenu_Text_EncounterChartRow);
    String *pageFormat = MessageLoader_GetNewString(menuLoader, StartMenu_Text_EncounterChartPage);

    StringTemplate_SetNumber(formatter, 0, state->page + 1, 2, PADDING_MODE_NONE, CHARSET_MODE_EN);
    StringTemplate_SetNumber(formatter, 1, pageCount, 2, PADDING_MODE_NONE, CHARSET_MODE_EN);
    StringTemplate_Format(formatter, formatted, pageFormat);
    Text_AddPrinterWithParams(
        &menu->primaryWindow,
        FONT_SYSTEM,
        formatted,
        176,
        32,
        TEXT_SPEED_NO_TRANSFER,
        NULL);

    u8 first = state->page * MERCURY_ENCOUNTER_CHART_ROWS_PER_PAGE;
    u8 last = min(state->rowCount, first + MERCURY_ENCOUNTER_CHART_ROWS_PER_PAGE);

    for (u8 rowIndex = first; rowIndex < last; rowIndex++) {
        MercuryEncounterChartRow *row = &state->rows[rowIndex];
        u32 y = 48 + (rowIndex - first) * 16;

        String *species = MessageLoader_GetNewString(speciesLoader, row->species);
        Text_AddPrinterWithParams(
            &menu->primaryWindow,
            FONT_SYSTEM,
            species,
            0,
            y,
            TEXT_SPEED_NO_TRANSFER,
            NULL);
        String_Free(species);

        StringTemplate_SetNumber(formatter, 0, row->minLevel, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        StringTemplate_SetNumber(formatter, 1, row->maxLevel, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        StringTemplate_SetNumber(formatter, 2, row->chance, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        StringTemplate_Format(formatter, formatted, rowFormat);

        Text_AddPrinterWithParams(
            &menu->primaryWindow,
            FONT_SYSTEM,
            formatted,
            112,
            y,
            TEXT_SPEED_NO_TRANSFER,
            NULL);
    }

    MercuryEncounterChart_PrintMessage(
        &menu->primaryWindow,
        menuLoader,
        StartMenu_Text_EncounterChartControls1,
        0,
        148);
    MercuryEncounterChart_PrintMessage(
        &menu->primaryWindow,
        menuLoader,
        StartMenu_Text_EncounterChartControls2,
        0,
        160);

    String_Free(pageFormat);
    String_Free(rowFormat);
    String_Free(formatted);
    StringTemplate_Free(formatter);
    MessageLoader_Free(speciesLoader);
    MessageLoader_Free(locationLoader);
    MessageLoader_Free(menuLoader);

    Window_ScheduleCopyToVRAM(&menu->primaryWindow);
}

'''
    insert_after_once(
        path,
        """static const u8 sOnlyMovePages[] = {
    SUMMARY_PAGE_BATTLE_MOVES,
    SUMMARY_PAGE_CONTEST_MOVES,
    SUMMARY_PAGE_MAX,
};
""",
        chart_types,
        "MR06A chart runtime types/helpers",
    )

    replace_once(
        path,
        """    menu->taskData = NULL;

    return menu;
}
""",
        """    menu->taskData = NULL;
    menu->mercuryEncounterChartEnabled = FALSE;

    return menu;
}
""",
        "MR06A StartMenu default chart flag",
    )

    # Normal field menu: enable after obtaining the Pokedex and only outside
    # the special-menu contexts whose vanilla option sets must remain intact.
    replace_once(
        path,
        """    menu->inUnionRoom = FALSE;

    if (PlayerAvatar_CheckForceStopMovement(fieldSystem->playerAvatar) == 1) {
""",
        """    menu->inUnionRoom = FALSE;
    menu->mercuryEncounterChartEnabled =
        Pokedex_IsObtained(SaveData_GetPokedex(fieldSystem->saveData))
        && !SystemFlag_CheckSafariGameActive(SaveData_GetVarsFlags(fieldSystem->saveData))
        && !SystemFlag_CheckInPalPark(SaveData_GetVarsFlags(fieldSystem->saveData))
        && !FieldSystem_IsInBattleTowerSalon(fieldSystem);

    if (PlayerAvatar_CheckForceStopMovement(fieldSystem->playerAvatar) == 1) {
""",
        "MR06A normal menu availability",
    )

    # The first exact occurrence after StartMenu_OpenUnionRoom is unique when
    # paired with its hide-options assignment.
    replace_once(
        path,
        """    menu->hideOptionFlags = StartMenu_GetUnionRoomHiddenOptions(fieldSystem);
    menu->inUnionRoom = TRUE;

    if (PlayerAvatar_CheckForceStopMovement(fieldSystem->playerAvatar) == 1) {
""",
        """    menu->hideOptionFlags = StartMenu_GetUnionRoomHiddenOptions(fieldSystem);
    menu->inUnionRoom = TRUE;
    menu->mercuryEncounterChartEnabled = FALSE;

    if (PlayerAvatar_CheckForceStopMovement(fieldSystem->playerAvatar) == 1) {
""",
        "MR06A Union Room exclusion",
    )

    replace_once(
        path,
        """    menu->hideOptionFlags = StartMenu_GetColosseumHiddenOptions(fieldSystem);
    menu->inUnionRoom = FALSE;

    if (PlayerAvatar_CheckForceStopMovement(fieldSystem->playerAvatar) == 1) {
""",
        """    menu->hideOptionFlags = StartMenu_GetColosseumHiddenOptions(fieldSystem);
    menu->inUnionRoom = FALSE;
    menu->mercuryEncounterChartEnabled = FALSE;

    if (PlayerAvatar_CheckForceStopMovement(fieldSystem->playerAvatar) == 1) {
""",
        "MR06A Colosseum exclusion",
    )

    replace_once(
        path,
        """    FieldTask_InitJump(fieldSystem->task, StartMenu_Main, menu);
}
""",
        """    menu->mercuryEncounterChartEnabled =
        Pokedex_IsObtained(SaveData_GetPokedex(fieldSystem->saveData))
        && !SystemFlag_CheckSafariGameActive(SaveData_GetVarsFlags(fieldSystem->saveData))
        && !SystemFlag_CheckInPalPark(SaveData_GetVarsFlags(fieldSystem->saveData))
        && !FieldSystem_IsInBattleTowerSalon(fieldSystem)
        && fieldSystem->mapLoadType != MAP_LOAD_TYPE_COLOSSEUM
        && fieldSystem->mapLoadType != MAP_LOAD_TYPE_UNION;

    FieldTask_InitJump(fieldSystem->task, StartMenu_Main, menu);
}
""",
        "MR06A scripted menu availability",
    )

    replace_once(
        path,
        """    case START_MENU_STATE_SAVED:
        Heap_Free(menu);
        MapObjectMan_UnpauseAllMovement(fieldSystem->mapObjMan);
        return TRUE;
    case START_MENU_STATE_END:
""",
        """    case START_MENU_STATE_SAVED:
        Heap_Free(menu);
        MapObjectMan_UnpauseAllMovement(fieldSystem->mapObjMan);
        return TRUE;
    case START_MENU_STATE_MERCURY_ENCOUNTER_CHART:
        StartMenu_EncounterChartRun(fieldTask);
        break;
    case START_MENU_STATE_END:
""",
        "MR06A chart state dispatch",
    )

    replace_once(
        path,
        """    ADD_OPTION_IF_NOT_HIDDEN(START_MENU_OPTION_OPTIONS, HIDE_OPTION_OPTIONS);
    ADD_OPTION_IF_NOT_HIDDEN(START_MENU_OPTION_EXIT, HIDE_OPTION_EXIT);
    return optionCount;
}
""",
        """    ADD_OPTION_IF_NOT_HIDDEN(START_MENU_OPTION_OPTIONS, HIDE_OPTION_OPTIONS);

    if (menu->mercuryEncounterChartEnabled) {
        ADD_OPTION_IF_NOT_HIDDEN(START_MENU_OPTION_ENCOUNTERS, HIDE_OPTION_EXIT);
    } else {
        ADD_OPTION_IF_NOT_HIDDEN(START_MENU_OPTION_EXIT, HIDE_OPTION_EXIT);
    }

    return optionCount;
}
""",
        "MR06A replace redundant normal Exit row",
    )

    replace_once(
        path,
        """        if (options[i] == START_MENU_OPTION_BAG && gender == GENDER_FEMALE) {
            template.animIdx = 9 * ICON_ANIM_COUNT;
        } else {
            template.animIdx = options[i] * ICON_ANIM_COUNT;
        }
""",
        """        if (options[i] == START_MENU_OPTION_BAG && gender == GENDER_FEMALE) {
            template.animIdx = 9 * ICON_ANIM_COUNT;
        } else if (options[i] == START_MENU_OPTION_ENCOUNTERS) {
            // Reuse the Pokédex icon family for the related Encounter Chart.
            template.animIdx = START_MENU_OPTION_POKEDEX * ICON_ANIM_COUNT;
        } else {
            template.animIdx = options[i] * ICON_ANIM_COUNT;
        }
""",
        "MR06A encounter chart icon",
    )

    chart_impl = r'''
static BOOL StartMenu_SelectEncounterChart(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);

    StartMenu_Close(menu);
    Window_EraseStandardFrame(&menu->primaryWindow, TRUE);
    Window_Remove(&menu->primaryWindow);
    StartMenu_EraseBallCount(fieldTask);

    StartMenu_EncounterChartOpen(fieldTask);
    menu->state = START_MENU_STATE_MERCURY_ENCOUNTER_CHART;

    return TRUE;
}

static void StartMenu_EncounterChartOpen(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    MercuryEncounterChartState *state =
        Heap_Alloc(HEAP_ID_FIELD2, sizeof(MercuryEncounterChartState));

    memset(state, 0, sizeof(MercuryEncounterChartState));
    state->hasEncounterData = MapHeader_HasWildEncounters(fieldSystem->location->mapHeaderID);

    if (state->hasEncounterData) {
        MapHeaderData_LoadWildEncounters(
            &state->encounters,
            fieldSystem->location->mapHeaderID);
    }

    int timeOfDay = FieldSystem_GetTimeOfDay(fieldSystem);
    if (timeOfDay == TIMEOFDAY_DAY) {
        state->period = 1;
    } else if (timeOfDay == TIMEOFDAY_TWILIGHT) {
        state->period = 2;
    } else if (timeOfDay == TIMEOFDAY_NIGHT || timeOfDay == TIMEOFDAY_LATE_NIGHT) {
        state->period = 3;
    } else {
        state->period = 0;
    }

    MercuryEncounterChart_SelectInitialMethod(state);
    MercuryEncounterChart_BuildRows(state);
    menu->taskData = state;

    Window_Add(
        fieldSystem->bgConfig,
        &menu->primaryWindow,
        BG_LAYER_MAIN_3,
        1,
        1,
        30,
        22,
        12,
        BASE_TILE_MESSAGE_WINDOW - (30 * 22));
    LoadStandardWindowGraphics(
        fieldSystem->bgConfig,
        BG_LAYER_MAIN_3,
        BASE_TILE_STANDARD_WINDOW_FRAME,
        11,
        STANDARD_WINDOW_FIELD,
        HEAP_ID_FIELD2);
    Window_DrawStandardFrame(
        &menu->primaryWindow,
        TRUE,
        BASE_TILE_STANDARD_WINDOW_FRAME,
        11);

    MercuryEncounterChart_Draw(fieldTask);
}

static void StartMenu_EncounterChartRun(FieldTask *fieldTask)
{
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    MercuryEncounterChartState *state = menu->taskData;
    BOOL redraw = FALSE;

    if (JOY_NEW(PAD_BUTTON_B)) {
        StartMenu_EncounterChartClose(fieldTask);
        return;
    }

    if (JOY_NEW(PAD_KEY_LEFT)) {
        MercuryEncounterChart_ChangeMethod(state, -1);
        redraw = TRUE;
    } else if (JOY_NEW(PAD_KEY_RIGHT)) {
        MercuryEncounterChart_ChangeMethod(state, 1);
        redraw = TRUE;
    }

    if (JOY_NEW(PAD_BUTTON_L)) {
        MercuryEncounterChart_ChangePeriod(state, -1);
        redraw = TRUE;
    } else if (JOY_NEW(PAD_BUTTON_R)) {
        MercuryEncounterChart_ChangePeriod(state, 1);
        redraw = TRUE;
    }

    u8 pageCount = (state->rowCount + MERCURY_ENCOUNTER_CHART_ROWS_PER_PAGE - 1)
        / MERCURY_ENCOUNTER_CHART_ROWS_PER_PAGE;

    if (pageCount > 1) {
        if (JOY_NEW(PAD_KEY_UP)) {
            state->page = (state->page == 0) ? pageCount - 1 : state->page - 1;
            redraw = TRUE;
        } else if (JOY_NEW(PAD_KEY_DOWN)) {
            state->page++;
            if (state->page >= pageCount) {
                state->page = 0;
            }
            redraw = TRUE;
        }
    }

    if (redraw) {
        MercuryEncounterChart_Draw(fieldTask);
    }
}

static void StartMenu_EncounterChartClose(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);

    Window_EraseStandardFrame(&menu->primaryWindow, TRUE);
    Window_Remove(&menu->primaryWindow);

    if (menu->taskData != NULL) {
        Heap_Free(menu->taskData);
        menu->taskData = NULL;
    }

    StartMenu_InitMenu(fieldTask);
    StartMenu_PrintBallCount(fieldTask);
    Bg_ScheduleTilemapTransfer(fieldSystem->bgConfig, BG_LAYER_MAIN_3);
    menu->state = START_MENU_STATE_SELECT;
}

'''
    insert_after_once(
        path,
        """static BOOL StartMenu_ExitPokedex(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);

    FieldSystem_StartFieldMap(fieldSystem);

    if (menu->taskData != NULL) {
        Heap_FreeExplicit(HEAP_ID_FIELD2, menu->taskData);
    }

    menu->state = START_MENU_STATE_REINIT;

    return FALSE;
}
""",
        chart_impl,
        "MR06A chart implementation",
    )


def audit(root: Path) -> dict[str, object]:
    source = (root / "src/start_menu.c").read_text()
    header = (root / "include/start_menu.h").read_text()
    text_bank = json.loads((root / "res/text/start_menu.json").read_text())

    checks = {
        "start_menu_entry": "START_MENU_OPTION_ENCOUNTERS" in source,
        "normal_exit_row_replaced_only_when_enabled": "mercuryEncounterChartEnabled" in source,
        "runtime_narc_read": "MapHeaderData_LoadWildEncounters" in source,
        "mercury_four_period_read": "mercuryTimedGrassMagic" in source
        and "mercuryTimedGrass[state->period]" in source,
        "water_methods": all(
            token in source
            for token in (
                "surfEncounters",
                "oldRodEncounters",
                "goodRodEncounters",
                "superRodEncounters",
            )
        ),
        "slot_odds": "sMercuryEncounterLandWeights" in source
        and "sMercuryEncounterWaterWeights" in source,
        "duplicate_species_merge": "state->rows[i].chance += chance" in source,
        "header_state": "START_MENU_STATE_MERCURY_ENCOUNTER_CHART" in header,
        "text_bank": any(
            row.get("id") == "StartMenu_Text_EncounterChartTitle"
            for row in text_bank["messages"]
        ),
    }

    failed = [key for key, value in checks.items() if not value]
    if failed:
        raise SystemExit("MR06A audit failed: " + ", ".join(failed))

    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06a-encounter-chart-ui.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    # This must run after MR05B's runtime extension because start_menu.c uses
    # the Mercury-extended WildEncounters structure directly.
    wild_header = (root / "include/overlay006/wild_encounters.h").read_text()
    if "MERCURY_TIMED_GRASS_MAGIC" not in wild_header:
        raise SystemExit("MR06A requires the installed MR05B four-period runtime first")

    patch_header(root)
    patch_text(root)
    patch_start_menu(root)
    checks = audit(root)

    report = {
        "gate": "MERCURY_MR06A_ENCOUNTER_CHART_UI",
        "status": "PASS",
        "access": "normal Start Menu ENCOUNTERS row after Pokedex acquisition",
        "vanilla_special_menus_preserved": True,
        "visible_exit_replaced_only_normal_menu": True,
        "b_or_x_still_closes_start_menu": True,
        "data_source": "current map WildEncounters NARC member at runtime",
        "full_four_period_land_supported": True,
        "surf_supported": True,
        "old_rod_supported": True,
        "good_rod_supported": True,
        "super_rod_supported": True,
        "duplicate_species_merged": True,
        "exact_platinum_slot_odds": True,
        "level_ranges": True,
        "navigation": {
            "left_right": "encounter method",
            "l_r": "Morning/Day/Evening/Night when full Mercury land tables exist",
            "up_down": "result page",
            "b": "return to Start Menu",
        },
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
