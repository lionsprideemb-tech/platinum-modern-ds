#!/usr/bin/env python3
"""MR06B — install the first player-facing native DS Encounter Chart browser.

Access:
- Open the normal Platinum Start Menu.
- Press Y to open Encounter Chart.
- Up/Down: browse areas.
- Left/Right: browse available encounter methods.
- A: next page of species.
- B: return to the normal Start Menu.

The browser consumes MR06A's live encounter runtime API. It does not maintain a
second encounter table. Standard-area pages show merged species odds and level
ranges. Dedicated Honey Tree / Great Marsh special-resource pages remain a
follow-up adapter pass.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

UNKNOWN_NAMES = {f"encounters_unknown_{n}" for n in range(533, 558)}
HONEY = "encounters_honey_tree"
LOOKOUT = "encounters_great_marsh_lookout"

FIXED_MESSAGES = [
    ("StartMenu_Text_EncounterChart", "ENCOUNTER CHART"),
    ("StartMenu_Text_EncounterMorning", "MORNING"),
    ("StartMenu_Text_EncounterDay", "DAY"),
    ("StartMenu_Text_EncounterEvening", "EVENING"),
    ("StartMenu_Text_EncounterNight", "NIGHT"),
    ("StartMenu_Text_EncounterSurf", "SURF"),
    ("StartMenu_Text_EncounterOldRod", "OLD ROD"),
    ("StartMenu_Text_EncounterGoodRod", "GOOD ROD"),
    ("StartMenu_Text_EncounterSuperRod", "SUPER ROD"),
    ("StartMenu_Text_EncounterPokemon", "POKéMON"),
    ("StartMenu_Text_EncounterLevel", "LEVEL"),
    ("StartMenu_Text_EncounterOdds", "ODDS"),
    ("StartMenu_Text_EncounterRate", "RATE"),
    ("StartMenu_Text_EncounterNoRandom", "NO RANDOM ENCOUNTERS"),
    ("StartMenu_Text_EncounterControls1", "UP/DOWN AREA   L/R METHOD"),
    ("StartMenu_Text_EncounterControls2", "A PAGE        B BACK"),
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def standard_resources(manifest: dict[str, Any]) -> list[str]:
    areas = manifest.get("areas")
    if not isinstance(areas, dict):
        raise SystemExit("MR06B manifest missing areas")

    resources = []
    for name, data in areas.items():
        if name in UNKNOWN_NAMES or name in (HONEY, LOOKOUT):
            continue
        if isinstance(data, dict) and "land_encounters" in data:
            resources.append(name)

    resources.sort()
    if len(resources) != 158:
        raise SystemExit(f"MR06B expected 158 standard resources, found {len(resources)}")
    return resources


def humanize(name: str) -> str:
    value = name.removeprefix("encounters_")

    exact = {
        "pokemon_league": "Pokémon League",
        "trophy_garden": "Trophy Garden",
        "sendoff_spring": "Sendoff Spring",
        "resort_area": "Resort Area",
        "valley_windworks_outside": "Valley Windworks",
        "fuego_ironworks_outside": "Fuego Ironworks",
        "ravaged_path": "Ravaged Path",
        "eterna_forest": "Eterna Forest",
        "valor_lakefront": "Valor Lakefront",
        "acuity_lakefront": "Acuity Lakefront",
        "lake_acuity": "Lake Acuity",
        "lake_valor": "Lake Valor",
        "lake_verity": "Lake Verity",
        "lake_verity_low_water": "Lake Verity - Low Water",
        "canalave_city": "Canalave City",
        "celestic_town": "Celestic Town",
        "eterna_city": "Eterna City",
        "pastoria_city": "Pastoria City",
        "sunyshore_city": "Sunyshore City",
        "twinleaf_town": "Twinleaf Town",
        "stark_mountain_outside": "Stark Mountain - Outside",
        "stark_mountain_room_1": "Stark Mountain - Room 1",
        "stark_mountain_room_2": "Stark Mountain - Room 2",
    }
    if value in exact:
        return exact[value]

    value = value.replace("mt_coronet", "Mt. Coronet")
    value = value.replace("old_chateau", "Old Chateau")
    value = value.replace("snowpoint_temple", "Snowpoint Temple")
    value = value.replace("iron_island", "Iron Island")
    value = value.replace("victory_road", "Victory Road")
    value = value.replace("turnback_cave", "Turnback Cave")
    value = value.replace("solaceon_ruins", "Solaceon Ruins")
    value = value.replace("wayward_cave", "Wayward Cave")
    value = value.replace("oreburgh_gate", "Oreburgh Gate")
    value = value.replace("oreburgh_mine", "Oreburgh Mine")
    value = value.replace("ruin_maniac_cave", "Ruin Maniac Cave")
    value = value.replace("great_marsh", "Great Marsh")
    value = value.replace("_", " ")

    # Keep common floor notation compact and readable on the DS.
    value = re.sub(r"\bb(\d+)f\b", lambda m: f"B{m.group(1)}F", value, flags=re.I)
    value = re.sub(r"\b(\d+)f\b", lambda m: f"{m.group(1)}F", value, flags=re.I)
    value = re.sub(r"\bpillar (\d+) room (\d+)\b", r"Pillar \1 Room \2", value, flags=re.I)
    value = re.sub(r"\broom (\d+)\b", r"Room \1", value, flags=re.I)
    value = re.sub(r"\bdead end\b", "Dead End", value, flags=re.I)
    value = " ".join(word if word in ("Mt.",) or re.fullmatch(r"[BP]\d+F", word) else word.capitalize() for word in value.split())
    return value[:42]


def patch_text(root: Path, resources: list[str]) -> None:
    path = root / "res/text/start_menu.json"
    data = load_json(path)
    messages = data.get("messages")
    if not isinstance(messages, list):
        raise SystemExit("start_menu text bank missing messages")

    ids = {entry.get("id") for entry in messages}
    for msg_id, text in FIXED_MESSAGES:
        if msg_id not in ids:
            messages.append({"id": msg_id, "en_US": text})
            ids.add(msg_id)

    for i, resource in enumerate(resources):
        msg_id = f"StartMenu_Text_EncounterArea_{i:03d}"
        if msg_id not in ids:
            messages.append({"id": msg_id, "en_US": humanize(resource)})
            ids.add(msg_id)

    data["messages"] = messages
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_header(root: Path) -> None:
    path = root / "include/start_menu.h"

    replace_once(
        path,
        """    Window primaryWindow;
    Window secondaryWindow;
    Menu *menu;
""",
        """    Window primaryWindow;
    Window secondaryWindow;
    Menu *menu;
""",
        "MR06B StartMenu window anchor",
    )

    replace_once(
        path,
        """    void *taskData;
    void *additionalTaskContext;
} StartMenu;
""",
        """    void *taskData;
    void *additionalTaskContext;
    u16 encounterChartArea;
    u8 encounterChartMethod;
    u8 encounterChartPage;
} StartMenu;
""",
        "MR06B StartMenu chart state",
    )

    replace_once(
        path,
        """    START_MENU_STATE_REINIT_WAIT_FOR_FADE,
    START_MENU_STATE_SAVED,
};
""",
        """    START_MENU_STATE_REINIT_WAIT_FOR_FADE,
    START_MENU_STATE_MERCURY_ENCOUNTER_CHART,
    START_MENU_STATE_SAVED,
};
""",
        "MR06B StartMenu state enum",
    )


def patch_source(root: Path) -> None:
    path = root / "src/start_menu.c"

    replace_once(
        path,
        """#include "message.h"
""",
        """#include "message.h"
#include "message_util.h"
""",
        "MR06B message util include",
    )

    # start_menu.c already uses many overlay005 helpers, so the overlay006
    # encounter API is safe in the field runtime and is linked in the same NEF.
    replace_once(
        path,
        """#include "overlay005/save_info_window.h"
#include "overlay005/sprite_resource_manager.h"
""",
        """#include "overlay005/save_info_window.h"
#include "overlay005/sprite_resource_manager.h"
#include "overlay006/wild_encounters.h"
""",
        "MR06B wild encounter include",
    )

    replace_once(
        path,
        """#include "system_flags.h"
#include "system_vars.h"
""",
        """#include "system.h"
#include "system_flags.h"
#include "system_vars.h"
""",
        "MR06B system input include",
    )

    proto_anchor = """static BOOL StartMenu_Select(FieldTask *fieldTask);
static u32 StartMenu_MakeOptionList(StartMenu *menu, u8 *listOut);
"""
    proto_new = """static BOOL StartMenu_Select(FieldTask *fieldTask);
static void StartMenu_OpenEncounterChart(FieldTask *fieldTask);
static void StartMenu_UpdateEncounterChart(FieldTask *fieldTask);
static void StartMenu_DrawEncounterChart(FieldTask *fieldTask);
static u32 StartMenu_MakeOptionList(StartMenu *menu, u8 *listOut);
"""
    replace_once(path, proto_anchor, proto_new, "MR06B prototypes")

    replace_once(
        path,
        """    menu->state = START_MENU_STATE_INIT;
    menu->cursorPos = 0;
    menu->taskData = NULL;

    return menu;
}
""",
        """    menu->state = START_MENU_STATE_INIT;
    menu->cursorPos = 0;
    menu->taskData = NULL;
    menu->encounterChartArea = 0;
    menu->encounterChartMethod = MERCURY_ENCOUNTER_METHOD_MAX;
    menu->encounterChartPage = 0;

    return menu;
}
""",
        "MR06B init chart state",
    )

    replace_once(
        path,
        """    case START_MENU_STATE_REINIT_WAIT_FOR_FADE:
        if (IsScreenFadeDone()) {
            menu->state = START_MENU_STATE_SELECT;
        }
        break;
    }
""",
        """    case START_MENU_STATE_REINIT_WAIT_FOR_FADE:
        if (IsScreenFadeDone()) {
            menu->state = START_MENU_STATE_SELECT;
        }
        break;
    case START_MENU_STATE_MERCURY_ENCOUNTER_CHART:
        StartMenu_UpdateEncounterChart(fieldTask);
        break;
    }
""",
        "MR06B main state",
    )

    select_anchor = """static BOOL StartMenu_Select(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    u16 prevPos = Menu_GetCursorPos(menu->menu);

    menu->input = Menu_ProcessInputWithSound(menu->menu, SEQ_SE_DP_SELECT78_sseq);
"""
    select_new = """static BOOL StartMenu_Select(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    u16 prevPos = Menu_GetCursorPos(menu->menu);

    if (JOY_NEW(PAD_BUTTON_Y)) {
        StartMenu_OpenEncounterChart(fieldTask);
        return FALSE;
    }

    menu->input = Menu_ProcessInputWithSound(menu->menu, SEQ_SE_DP_SELECT78_sseq);
"""
    replace_once(path, select_anchor, select_new, "MR06B Y shortcut")

    insert_anchor = """#define ADD_OPTION_IF_NOT_HIDDEN(__menuOption, __hideFlag) \\
"""
    browser_code = r'''
typedef struct MercuryEncounterChartDisplayRow {
    int species;
    u8 minLevel;
    u8 maxLevel;
    u8 chancePercent;
} MercuryEncounterChartDisplayRow;

static u32 StartMenu_EncounterMethodText(enum MercuryEncounterChartMethod method)
{
    switch (method) {
    case MERCURY_ENCOUNTER_METHOD_LAND_MORNING:
        return StartMenu_Text_EncounterMorning;
    case MERCURY_ENCOUNTER_METHOD_LAND_DAY:
        return StartMenu_Text_EncounterDay;
    case MERCURY_ENCOUNTER_METHOD_LAND_EVENING:
        return StartMenu_Text_EncounterEvening;
    case MERCURY_ENCOUNTER_METHOD_LAND_NIGHT:
        return StartMenu_Text_EncounterNight;
    case MERCURY_ENCOUNTER_METHOD_SURF:
        return StartMenu_Text_EncounterSurf;
    case MERCURY_ENCOUNTER_METHOD_OLD_ROD:
        return StartMenu_Text_EncounterOldRod;
    case MERCURY_ENCOUNTER_METHOD_GOOD_ROD:
        return StartMenu_Text_EncounterGoodRod;
    case MERCURY_ENCOUNTER_METHOD_SUPER_ROD:
        return StartMenu_Text_EncounterSuperRod;
    default:
        return StartMenu_Text_EncounterNoRandom;
    }
}

static void StartMenu_EncounterPrintMessage(Window *window, MessageLoader *loader, u32 entry, int x, int y)
{
    String *string = MessageLoader_GetNewString(loader, entry);
    Text_AddPrinterWithParams(window, FONT_SYSTEM, string, x, y, TEXT_SPEED_NO_TRANSFER, NULL);
    String_Free(string);
}

static void StartMenu_EncounterPrintNumber(Window *window, int number, int digits, int x, int y)
{
    String *string = String_Init(8, HEAP_ID_FIELD2);
    String_FormatInt(string, number, digits, PADDING_MODE_NONE, CHARSET_MODE_EN);
    Text_AddPrinterWithParams(window, FONT_SYSTEM, string, x, y, TEXT_SPEED_NO_TRANSFER, NULL);
    String_Free(string);
}

static int StartMenu_EncounterBuildRows(const WildEncounters *encounters, enum MercuryEncounterChartMethod method, MercuryEncounterChartDisplayRow *rows)
{
    int rowCount = 0;
    int slotCount = MercuryEncounterChart_GetSlotCount(encounters, method);

    for (int i = 0; i < slotCount; i++) {
        MercuryEncounterChartSlot slot;

        if (!MercuryEncounterChart_GetSlot(encounters, method, i, &slot) || slot.species == SPECIES_NONE) {
            continue;
        }

        int found = -1;
        for (int row = 0; row < rowCount; row++) {
            if (rows[row].species == slot.species) {
                found = row;
                break;
            }
        }

        if (found < 0) {
            found = rowCount++;
            rows[found].species = slot.species;
            rows[found].minLevel = slot.minLevel;
            rows[found].maxLevel = slot.maxLevel;
            rows[found].chancePercent = 0;
        } else {
            rows[found].minLevel = MIN(rows[found].minLevel, slot.minLevel);
            rows[found].maxLevel = MAX(rows[found].maxLevel, slot.maxLevel);
        }

        rows[found].chancePercent += slot.chancePercent;
    }

    return rowCount;
}

static enum MercuryEncounterChartMethod StartMenu_EncounterFirstMethod(const WildEncounters *encounters)
{
    enum MercuryEncounterChartMethod current = MercuryEncounterChart_GetCurrentLandMethod();

    if (MercuryEncounterChart_HasMethod(encounters, current)) {
        return current;
    }

    for (int method = 0; method < MERCURY_ENCOUNTER_METHOD_MAX; method++) {
        if (MercuryEncounterChart_HasMethod(encounters, method)) {
            return (enum MercuryEncounterChartMethod)method;
        }
    }

    return MERCURY_ENCOUNTER_METHOD_MAX;
}

static enum MercuryEncounterChartMethod StartMenu_EncounterCycleMethod(const WildEncounters *encounters, enum MercuryEncounterChartMethod method, int direction)
{
    int value = method;

    if (value < 0 || value >= MERCURY_ENCOUNTER_METHOD_MAX) {
        value = MercuryEncounterChart_GetCurrentLandMethod();
    }

    for (int i = 0; i < MERCURY_ENCOUNTER_METHOD_MAX; i++) {
        value += direction;

        if (value < 0) {
            value = MERCURY_ENCOUNTER_METHOD_MAX - 1;
        } else if (value >= MERCURY_ENCOUNTER_METHOD_MAX) {
            value = 0;
        }

        if (MercuryEncounterChart_HasMethod(encounters, (enum MercuryEncounterChartMethod)value)) {
            return (enum MercuryEncounterChartMethod)value;
        }
    }

    return MERCURY_ENCOUNTER_METHOD_MAX;
}

static void StartMenu_OpenEncounterChart(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);

    Sound_PlayEffect(SEQ_SE_DP_WIN_OPEN_sseq);

    int area = MercuryEncounterChart_FindAreaByMapHeader(fieldSystem->location->mapHeaderID);
    if (area < 0) {
        area = 0;
    }

    StartMenu_Close(menu);
    Window_EraseStandardFrame(&menu->primaryWindow, TRUE);
    Window_Remove(&menu->primaryWindow);
    StartMenu_EraseBallCount(fieldTask);

    // 28x19 = 532 content tiles. Base tile 1 stays below Platinum's
    // reserved field-message/window graphics while fitting cleanly on-screen.
    Window_Add(fieldSystem->bgConfig, &menu->primaryWindow, BG_LAYER_MAIN_3, 2, 2, 28, 19, 12, 1);
    LoadStandardWindowGraphics(fieldSystem->bgConfig, BG_LAYER_MAIN_3, BASE_TILE_STANDARD_WINDOW_FRAME, 11, STANDARD_WINDOW_FIELD, HEAP_ID_FIELD2);
    Window_DrawStandardFrame(&menu->primaryWindow, TRUE, BASE_TILE_STANDARD_WINDOW_FRAME, 11);

    menu->encounterChartArea = area;
    menu->encounterChartPage = 0;

    WildEncounters encounters;
    MercuryEncounterChart_LoadArea(area, &encounters);
    menu->encounterChartMethod = StartMenu_EncounterFirstMethod(&encounters);

    menu->state = START_MENU_STATE_MERCURY_ENCOUNTER_CHART;
    StartMenu_DrawEncounterChart(fieldTask);
}

static void StartMenu_DrawEncounterChart(FieldTask *fieldTask)
{
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    Window *window = &menu->primaryWindow;
    WildEncounters encounters;
    MercuryEncounterChartDisplayRow rows[MAX_GRASS_ENCOUNTERS];

    MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);

    Window_FillTilemap(window, 15);

    MessageLoader *loader = MessageLoader_Init(
        MSG_LOADER_PRELOAD_ENTIRE_BANK,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_START_MENU,
        HEAP_ID_FIELD2
    );

    StartMenu_EncounterPrintMessage(
        window,
        loader,
        StartMenu_Text_EncounterArea_000 + menu->encounterChartArea,
        0,
        0
    );

    enum MercuryEncounterChartMethod method = (enum MercuryEncounterChartMethod)menu->encounterChartMethod;

    if (method >= MERCURY_ENCOUNTER_METHOD_MAX || !MercuryEncounterChart_HasMethod(&encounters, method)) {
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterNoRandom, 0, 20);
        menu->encounterChartPage = 0;
    } else {
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_EncounterMethodText(method), 0, 20);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterRate, 156, 20);
        StartMenu_EncounterPrintNumber(
            window,
            MercuryEncounterChart_GetEncounterRate(&encounters, method),
            3,
            194,
            20
        );

        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterPokemon, 0, 38);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterLevel, 112, 38);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterOdds, 180, 38);

        int rowCount = StartMenu_EncounterBuildRows(&encounters, method, rows);
        int pages = MAX(1, (rowCount + 3) / 4);
        if (menu->encounterChartPage >= pages) {
            menu->encounterChartPage = 0;
        }

        int start = menu->encounterChartPage * 4;
        int end = MIN(start + 4, rowCount);

        for (int rowIndex = start; rowIndex < end; rowIndex++) {
            int line = rowIndex - start;
            int y = 56 + line * 16;
            MercuryEncounterChartDisplayRow *row = &rows[rowIndex];

            String *species = MessageUtil_SpeciesName(row->species, HEAP_ID_FIELD2);
            Text_AddPrinterWithParams(window, FONT_SYSTEM, species, 0, y, TEXT_SPEED_NO_TRANSFER, NULL);
            String_Free(species);

            StartMenu_EncounterPrintNumber(window, row->minLevel, 3, 112, y);
            if (row->maxLevel != row->minLevel) {
                StartMenu_EncounterPrintNumber(window, row->maxLevel, 3, 142, y);
            }
            StartMenu_EncounterPrintNumber(window, row->chancePercent, 3, 184, y);
        }
    }

    StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterControls1, 0, 124);
    StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterControls2, 0, 140);

    MessageLoader_Free(loader);
    Window_ScheduleCopyToVRAM(window);
}

static void StartMenu_UpdateEncounterChart(FieldTask *fieldTask)
{
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    BOOL redraw = FALSE;

    if (JOY_NEW(PAD_BUTTON_B)) {
        Sound_PlayEffect(SEQ_SE_DP_WIN_CLOSE_sseq);
        Window_EraseStandardFrame(&menu->primaryWindow, TRUE);
        Window_Remove(&menu->primaryWindow);
        menu->state = START_MENU_STATE_INIT;
        return;
    }

    int areaCount = MercuryEncounterChart_GetAreaCount();

    if (JOY_REPEAT(PAD_KEY_UP)) {
        menu->encounterChartArea = (menu->encounterChartArea + areaCount - 1) % areaCount;
        redraw = TRUE;
    } else if (JOY_REPEAT(PAD_KEY_DOWN)) {
        menu->encounterChartArea = (menu->encounterChartArea + 1) % areaCount;
        redraw = TRUE;
    }

    if (redraw) {
        WildEncounters encounters;
        MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);
        menu->encounterChartMethod = StartMenu_EncounterFirstMethod(&encounters);
        menu->encounterChartPage = 0;
        Sound_PlayEffect(SEQ_SE_DP_SELECT78_sseq);
        StartMenu_DrawEncounterChart(fieldTask);
        return;
    }

    WildEncounters encounters;
    MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);

    if (JOY_NEW(PAD_KEY_LEFT)) {
        menu->encounterChartMethod = StartMenu_EncounterCycleMethod(
            &encounters,
            (enum MercuryEncounterChartMethod)menu->encounterChartMethod,
            -1
        );
        menu->encounterChartPage = 0;
        redraw = TRUE;
    } else if (JOY_NEW(PAD_KEY_RIGHT)) {
        menu->encounterChartMethod = StartMenu_EncounterCycleMethod(
            &encounters,
            (enum MercuryEncounterChartMethod)menu->encounterChartMethod,
            1
        );
        menu->encounterChartPage = 0;
        redraw = TRUE;
    } else if (JOY_NEW(PAD_BUTTON_A)) {
        MercuryEncounterChartDisplayRow rows[MAX_GRASS_ENCOUNTERS];
        enum MercuryEncounterChartMethod method = (enum MercuryEncounterChartMethod)menu->encounterChartMethod;
        int rowCount = StartMenu_EncounterBuildRows(&encounters, method, rows);
        int pages = MAX(1, (rowCount + 3) / 4);

        if (pages > 1) {
            menu->encounterChartPage = (menu->encounterChartPage + 1) % pages;
            redraw = TRUE;
        }
    }

    if (redraw) {
        Sound_PlayEffect(SEQ_SE_DP_SELECT78_sseq);
        StartMenu_DrawEncounterChart(fieldTask);
    }
}

'''
    if insert_anchor not in path.read_text():
        raise SystemExit("MR06B browser insertion anchor missing")
    text = path.read_text()
    path.write_text(text.replace(insert_anchor, browser_code + "\n" + insert_anchor, 1))


def validate(root: Path, resources: list[str]) -> None:
    source = (root / "src/start_menu.c").read_text()
    header = (root / "include/start_menu.h").read_text()
    bank = load_json(root / "res/text/start_menu.json")

    required_source = (
        "PAD_BUTTON_Y",
        "START_MENU_STATE_MERCURY_ENCOUNTER_CHART",
        "MercuryEncounterChart_FindAreaByMapHeader",
        "MercuryEncounterChart_LoadArea",
        "MercuryEncounterChart_GetSlot",
        "StartMenu_EncounterBuildRows",
        "StartMenu_Text_EncounterArea_000",
        "UP/DOWN",
    )
    # UP/DOWN lives in the text bank, not source.
    for token in required_source[:-1]:
        if token not in source:
            raise SystemExit(f"MR06B source missing {token}")

    if "encounterChartArea" not in header or "START_MENU_STATE_MERCURY_ENCOUNTER_CHART" not in header:
        raise SystemExit("MR06B StartMenu header state missing")

    ids = [m.get("id") for m in bank.get("messages", [])]
    if "StartMenu_Text_EncounterChart" not in ids:
        raise SystemExit("MR06B fixed UI text missing")
    area_ids = [x for x in ids if isinstance(x, str) and x.startswith("StartMenu_Text_EncounterArea_")]
    if len(area_ids) != len(resources):
        raise SystemExit(f"MR06B expected {len(resources)} area labels, found {len(area_ids)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06b-encounter-chart-ui.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    manifest = load_json(args.manifest)
    resources = standard_resources(manifest)

    patch_text(root, resources)
    patch_header(root)
    patch_source(root)
    validate(root, resources)

    report = {
        "gate": "MERCURY_MR06B_ENCOUNTER_CHART_UI",
        "status": "PASS",
        "entry_point": "Start Menu + Y",
        "standard_area_count": len(resources),
        "area_navigation": "Up/Down",
        "method_navigation": "Left/Right",
        "page_navigation": "A",
        "exit_button": "B",
        "shows_level_ranges": True,
        "shows_merged_species_odds": True,
        "shows_encounter_rate": True,
        "supported_methods": [
            "Morning",
            "Day",
            "Evening",
            "Night",
            "Surf",
            "Old Rod",
            "Good Rod",
            "Super Rod",
        ],
        "current_area_auto_selected": True,
        "uses_mr06a_live_runtime_api": True,
        "duplicate_encounter_database_created": False,
        "honey_tree_adapter_deferred": True,
        "great_marsh_lookout_adapter_deferred": True,
        "top_screen_browser_foundation": True,
        "dual_screen_polish_deferred": True,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
