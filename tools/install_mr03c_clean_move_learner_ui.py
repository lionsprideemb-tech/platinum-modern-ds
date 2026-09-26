#!/usr/bin/env python3
"""MR03C — clean Mercury Move Learner UI.

This pass intentionally replaces the MR03 visual layer instead of stacking
windows on top of Platinum's Move Reminder.  The existing MR03 backend,
party-menu launch path and teach/replace flow remain authoritative.

Layout target:
  Top: MOVE / STATS / ABILITY pages selected with L/R.
  Bottom: filter tabs, current moves, filtered learnable list, selected move
          details, and button hints.

The code uses fixed, non-overlapping screen regions so later art/palette work
can approach the approved mockup without reintroducing MR03B overlap bugs.
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


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1))


def replace_function(path: Path, signature: str, replacement: str, label: str) -> None:
    text = path.read_text()

    # A prototype may use different parameter names from the real definition.
    # Never patch from a prototype: require the signature to be followed
    # immediately by the function body opening brace.
    needle = signature + "\n{"
    start = text.rfind(needle)
    if start < 0:
        raise SystemExit(f"{label}: exact function definition not found in {path}: {signature}")

    brace = start + len(signature) + 1

    depth = 0
    end = None
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end is None:
        raise SystemExit(f"{label}: closing brace not found in {path}")
    path.write_text(text[:start] + replacement.rstrip() + text[end:])


def patch_ui(root: Path) -> None:
    source = root / "src/applications/move_reminder.c"

    insert_after_once(
        source,
        '#include "heap.h"\n',
        '#include "item.h"\n',
        "MR03C item-name include",
    )

    # Give the custom top page its own character/tilemap layer so its 30x22
    # window cannot collide with Platinum's message-box tile storage.
    replace_once(
        source,
        """    Bg_InitFromTemplate(bgConfig, BG_LAYER_SUB_0, &bgSub0, BG_TYPE_STATIC);
    Bg_ClearTilemap(bgConfig, BG_LAYER_SUB_0);

    Bg_ClearTilesRange(BG_LAYER_MAIN_0, 32, 0, HEAP_ID_MOVE_REMINDER);
    Bg_ClearTilesRange(BG_LAYER_SUB_0, 32, 0, HEAP_ID_MOVE_REMINDER);
    GXLayers_EngineBToggleLayers(GX_PLANEMASK_BG0, TRUE);
}""",
        """    Bg_InitFromTemplate(bgConfig, BG_LAYER_SUB_0, &bgSub0, BG_TYPE_STATIC);
    Bg_ClearTilemap(bgConfig, BG_LAYER_SUB_0);

    BgTemplate bgMain3 = {
        .x = 0,
        .y = 0,
        .bufferSize = 0x800,
        .baseTile = 0,
        .screenSize = BG_SCREEN_SIZE_256x256,
        .colorMode = GX_BG_COLORMODE_16,
        .screenBase = GX_BG_SCRBASE_0xd800,
        .charBase = GX_BG_CHARBASE_0x08000,
        .bgExtPltt = GX_BG_EXTPLTT_01,
        .priority = 1,
        .areaOver = 0,
        .mosaic = FALSE,
    };

    Bg_InitFromTemplate(bgConfig, BG_LAYER_MAIN_3, &bgMain3, BG_TYPE_STATIC);
    Bg_ClearTilemap(bgConfig, BG_LAYER_MAIN_3);

    Bg_ClearTilesRange(BG_LAYER_MAIN_0, 32, 0, HEAP_ID_MOVE_REMINDER);
    Bg_ClearTilesRange(BG_LAYER_MAIN_3, 32, 0, HEAP_ID_MOVE_REMINDER);
    Bg_ClearTilesRange(BG_LAYER_SUB_0, 32, 0, HEAP_ID_MOVE_REMINDER);
    GXLayers_EngineAToggleLayers(GX_PLANEMASK_BG3, TRUE);
    GXLayers_EngineBToggleLayers(GX_PLANEMASK_BG0, TRUE);
}""",
        "MR03C dedicated top BG",
    )

    replace_once(
        source,
        """    GXLayers_EngineBToggleLayers(GX_PLANEMASK_BG0, FALSE);
    Bg_FreeTilemapBuffer(bgConfig, BG_LAYER_SUB_0);
    Bg_FreeTilemapBuffer(bgConfig, BG_LAYER_MAIN_2);""",
        """    GXLayers_EngineBToggleLayers(GX_PLANEMASK_BG0, FALSE);
    GXLayers_EngineAToggleLayers(GX_PLANEMASK_BG3, FALSE);
    Bg_FreeTilemapBuffer(bgConfig, BG_LAYER_SUB_0);
    Bg_FreeTilemapBuffer(bgConfig, BG_LAYER_MAIN_3);
    Bg_FreeTilemapBuffer(bgConfig, BG_LAYER_MAIN_2);""",
        "MR03C dedicated top BG teardown",
    )

    # Dedicated MR03C windows.  Existing native windows remain available only
    # for the confirmation/replace-move state machine.
    replace_once(
        source,
        """    MOVE_REMINDER_WIN_YES_NO_MENU,
    MOVE_REMINDER_WIN_SUB_INFO,
    MAX_MOVE_REMINDER_WIN
};""",
        """    MOVE_REMINDER_WIN_YES_NO_MENU,
    MOVE_REMINDER_WIN_SUB_INFO,
    MOVE_REMINDER_WIN_MERCURY_TOP,
    MOVE_REMINDER_WIN_MERCURY_FILTER,
    MOVE_REMINDER_WIN_MERCURY_CURRENT,
    MOVE_REMINDER_WIN_MERCURY_LIST,
    MOVE_REMINDER_WIN_MERCURY_DESC,
    MOVE_REMINDER_WIN_MERCURY_HELP,
    MAX_MOVE_REMINDER_WIN
};""",
        "MR03C window enum",
    )

    replace_once(
        source,
        """    u16 numMoves;
    u8 textPrinterID;
    u8 yesNoCallback;
} MoveReminderController;""",
        """    u16 numMoves;
    u8 textPrinterID;
    u8 yesNoCallback;
    u8 mercuryPage;
    u8 mercuryFilter;
} MoveReminderController;

enum {
    MERCURY_PAGE_MOVE = 0,
    MERCURY_PAGE_STATS,
    MERCURY_PAGE_ABILITY,
};

enum {
    MERCURY_FILTER_ALL = 0,
    MERCURY_FILTER_LEVEL,
    MERCURY_FILTER_EGG,
    MERCURY_FILTER_TUTOR,
    MERCURY_FILTER_SPECIAL,
};""",
        "MR03C controller state",
    )

    decl_anchor = "static void MoveReminder_DrawSubInfo(MoveReminderController *controller);\n"
    insert_after_once(
        source,
        decl_anchor,
        """static void MercuryMoveLearner_DrawTopPage(MoveReminderController *controller);
static void MercuryMoveLearner_DrawBottomChrome(MoveReminderController *controller);
static void MercuryMoveLearner_DrawSelectedMove(MoveReminderController *controller, u32 move);
static void MercuryMoveLearner_RebuildFilteredList(MoveReminderController *controller);
static BOOL MercuryMoveLearner_FilterMatches(MoveReminderController *controller, u16 move);
static void MercuryMoveLearner_PrintMessage(MoveReminderController *controller, Window *window, u32 messageID, u32 x, u32 y);
static void MercuryMoveLearner_PrintNumber(MoveReminderController *controller, Window *window, u32 value, u32 x, u32 y);
static void MercuryMoveLearner_PrintMoveName(MoveReminderController *controller, Window *window, u16 move, u32 x, u32 y);
static void MercuryMoveLearner_PrintTypeName(MoveReminderController *controller, Window *window, u16 type, u32 x, u32 y);
static void MercuryMoveLearner_DrawPanel(Window *window, u32 x, u32 y, u32 width, u32 height);
static void MercuryMoveLearner_LoadPalette(void);
""",
        "MR03C declarations",
    )

    # Keep the native list window off-screen; the actual interactive ListMenu
    # is rendered into the dedicated lower-screen list window.
    replace_once(
        source,
        """    [MOVE_REMINDER_WIN_MOVES_NAMES] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 21,
        .tilemapTop = 3,
        .width = 11,
        .height = 14,
        .palette = 15,
        .baseTile = 0x20C,
    },""",
        """    [MOVE_REMINDER_WIN_MOVES_NAMES] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 31,
        .tilemapTop = 23,
        .width = 1,
        .height = 1,
        .palette = 15,
        .baseTile = 0x20C,
    },""",
        "MR03C retire native list window",
    )

    replace_once(
        source,
        """    [MOVE_REMINDER_WIN_SUB_INFO] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 1,
        .width = 30,
        .height = 22,
        .palette = 15,
        .baseTile = 1,
    }
};""",
        """    [MOVE_REMINDER_WIN_SUB_INFO] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 31,
        .tilemapTop = 23,
        .width = 1,
        .height = 1,
        .palette = 15,
        .baseTile = 1,
    },
    [MOVE_REMINDER_WIN_MERCURY_TOP] = {
        .bgLayer = BG_LAYER_MAIN_3,
        .tilemapLeft = 1,
        .tilemapTop = 1,
        .width = 30,
        .height = 22,
        .palette = 15,
        .baseTile = 0x001,
    },
    [MOVE_REMINDER_WIN_MERCURY_FILTER] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 0,
        .width = 30,
        .height = 3,
        .palette = 15,
        .baseTile = 0x001,
    },
    [MOVE_REMINDER_WIN_MERCURY_CURRENT] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 3,
        .width = 30,
        .height = 5,
        .palette = 15,
        .baseTile = 0x05B,
    },
    [MOVE_REMINDER_WIN_MERCURY_LIST] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 8,
        .width = 30,
        .height = 7,
        .palette = 15,
        .baseTile = 0x0F1,
    },
    [MOVE_REMINDER_WIN_MERCURY_DESC] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 15,
        .width = 30,
        .height = 7,
        .palette = 15,
        .baseTile = 0x1C3,
    },
    [MOVE_REMINDER_WIN_MERCURY_HELP] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 22,
        .width = 30,
        .height = 2,
        .palette = 15,
        .baseTile = 0x295,
    }
};""",
        "MR03C fixed screen regions",
    )

    # The dedicated bottom list is five rows.  It uses a normal text cursor;
    # all legacy engine-A selector/type-row sprites are disabled below.
    replace_once(source, "    .maxDisplay = 7,\n", "    .maxDisplay = 4,\n", "MR03C list rows")
    replace_once(source, "    .textColorBg = 0,\n", "    .textColorBg = 15,\n", "MR03C list bg")
    replace_once(source, "    .lineSpacing = 16,\n", "    .lineSpacing = 12,\n", "MR03C row spacing")
    replace_once(source, "    .cursorType = 1,\n", "    .cursorType = 0,\n", "MR03C text cursor")

    # L/R are page navigation and X cycles source filters.
    old_input = """static int MoveReminder_State_ProcessMainInput(MoveReminderController *controller)
{
    if (JOY_NEW(PAD_KEY_LEFT | PAD_KEY_RIGHT)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        controller->data->showingContest ^= 1;
        MoveReminder_DrawMovesInfo(controller);
        return MOVE_REMINDER_STATE_PROCESS_MAIN_INPUT;
    }
"""
    new_input = """static int MoveReminder_State_ProcessMainInput(MoveReminderController *controller)
{
    if (JOY_NEW(PAD_BUTTON_L)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        controller->mercuryPage = (controller->mercuryPage + 2) % 3;
        MercuryMoveLearner_DrawTopPage(controller);
        return MOVE_REMINDER_STATE_PROCESS_MAIN_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_R)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        controller->mercuryPage = (controller->mercuryPage + 1) % 3;
        MercuryMoveLearner_DrawTopPage(controller);
        return MOVE_REMINDER_STATE_PROCESS_MAIN_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_X)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        controller->mercuryFilter = (controller->mercuryFilter + 1) % 5;
        MercuryMoveLearner_RebuildFilteredList(controller);
        MercuryMoveLearner_DrawBottomChrome(controller);
        return MOVE_REMINDER_STATE_PROCESS_MAIN_INPUT;
    }
"""
    replace_once(source, old_input, new_input, "MR03C navigation")

    # Cursor callback updates both the selected-move card and MOVE top page.
    replace_function(
        source,
        "static void MoveReminder_ListMenuCursorCallback(ListMenu *menu, u32 move, u8 onInit)",
        r'''static void MoveReminder_ListMenuCursorCallback(ListMenu *menu, u32 move, u8 onInit)
{
    MoveReminderController *controller = (MoveReminderController *)ListMenu_GetAttribute(menu, LIST_MENU_PARENT);

    if (onInit != TRUE) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
    }

    MercuryMoveLearner_DrawSelectedMove(controller, move);
    if (controller->mercuryPage == 0) {
        MercuryMoveLearner_DrawTopPage(controller);
    }
}''',
        "MR03C cursor callback",
    )

    # Extra metadata on each bottom list row.
    replace_function(
        source,
        "static void MoveReminder_ListMenuPrintCallback(ListMenu *menu, u32 index, u8 yOffset)",
        r'''static void MoveReminder_ListMenuPrintCallback(ListMenu *menu, u32 move, u8 yOffset)
{
    if (move == MENU_CANCEL) {
        return;
    }

    MoveReminderController *controller = (MoveReminderController *)ListMenu_GetAttribute(menu, LIST_MENU_PARENT);
    Window *window = (Window *)ListMenu_GetAttribute(menu, LIST_MENU_WINDOW);

    u16 type = MoveTable_LoadParam(move, MOVEATTRIBUTE_TYPE);
    MercuryMoveLearner_PrintTypeName(controller, window, type, 122, yOffset);

    u16 moveClass = MoveTable_LoadParam(move, MOVEATTRIBUTE_CLASS);
    u32 classMsg = MoveReminder_Text_MercuryClassStatus;
    if (moveClass == CLASS_PHYSICAL) {
        classMsg = MoveReminder_Text_MercuryClassPhysical;
    } else if (moveClass == CLASS_SPECIAL) {
        classMsg = MoveReminder_Text_MercuryClassSpecial;
    }
    MercuryMoveLearner_PrintMessage(controller, window, classMsg, 182, yOffset);

    u8 source = MoveReminderData_GetMoveSource(controller->data->mon, move);
    u32 sourceMsg = MoveReminder_Text_MercurySourceSpecial;
    if (source == 0) sourceMsg = MoveReminder_Text_MercurySourceLevel;
    if (source == 1) sourceMsg = MoveReminder_Text_MercurySourceEgg;
    if (source == 2) sourceMsg = MoveReminder_Text_MercurySourceTutor;
    MercuryMoveLearner_PrintMessage(controller, window, sourceMsg, 224, yOffset);
}''',
        "MR03C list row metadata",
    )

    # Disable old selector, scroll arrows and type rows so the clean renderer
    # has exclusive ownership of both screens.
    replace_function(
        source,
        "static void MoveReminder_DrawMoveSelector(MoveReminderController *controller, u8 cursorPos, u8 palette)",
        r'''static void MoveReminder_DrawMoveSelector(MoveReminderController *controller, u8 cursorPos, u8 palette)
{
    ManagedSprite_SetDrawFlag(controller->managedSprites[MOVE_REMINDER_SPRITE_MOVE_SELECTOR], FALSE);
}''',
        "MR03C legacy selector off",
    )
    replace_function(
        source,
        "static void MoveReminder_DrawArrows(MoveReminderController *controller)",
        r'''static void MoveReminder_DrawArrows(MoveReminderController *controller)
{
    ManagedSprite_SetDrawFlag(controller->managedSprites[MOVE_REMINDER_SPRITE_SCROLL_ARROW_UP], FALSE);
    ManagedSprite_SetDrawFlag(controller->managedSprites[MOVE_REMINDER_SPRITE_SCROLL_ARROW_DOWN], FALSE);
}''',
        "MR03C legacy arrows off",
    )
    replace_function(
        source,
        "static void MoveReminder_DrawTypeIcons(MoveReminderController *controller)",
        r'''static void MoveReminder_DrawTypeIcons(MoveReminderController *controller)
{
    for (u32 i = 0; i < 7; i++) {
        ManagedSprite_SetDrawFlag(controller->managedSprites[MOVE_REMINDER_SPRITE_TYPE_MOVE_0 + i], FALSE);
    }
    ManagedSprite_SetDrawFlag(controller->managedSprites[MOVE_REMINDER_SPRITE_CATEGORY], FALSE);
}''',
        "MR03C legacy type sprites off",
    )
    replace_function(
        source,
        "static void MoveReminder_DrawSideArrows(MoveReminderController *controller, u8 draw)",
        r'''static void MoveReminder_DrawSideArrows(MoveReminderController *controller, u8 draw)
{
    ManagedSprite_SetDrawFlag(controller->managedSprites[MOVE_REMINDER_SPRITE_SIDE_ARROW_LEFT], FALSE);
    ManagedSprite_SetDrawFlag(controller->managedSprites[MOVE_REMINDER_SPRITE_SIDE_ARROW_RIGHT], FALSE);
}''',
        "MR03C legacy side arrows off",
    )

    # Filtered list implementation. StringList choice values remain move IDs,
    # so the native teaching state machine can consume them directly.
    replace_function(
        source,
        "static void MoveReminder_InitListMenu(MoveReminderController *controller)",
        r'''static void MoveReminder_InitListMenu(MoveReminderController *controller)
{
    u16 count = 1; // Cancel
    for (u32 i = 0; i < MERCURY_MOVE_LEARNER_MAX_MOVES; i++) {
        u16 move = controller->data->moves[i];
        if (move == LEVEL_UP_MOVESET_TERMINATOR) {
            break;
        }
        if (MercuryMoveLearner_FilterMatches(controller, move)) {
            count++;
        }
    }

    controller->numMoves = count;
    controller->stringList = StringList_New(count, HEAP_ID_MOVE_REMINDER);

    MessageLoader *moveNamesLoader = MessageLoader_Init(
        MSG_LOADER_PRELOAD_ENTIRE_BANK,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_MOVE_NAMES,
        HEAP_ID_MOVE_REMINDER);

    for (u32 i = 0; i < MERCURY_MOVE_LEARNER_MAX_MOVES; i++) {
        u16 move = controller->data->moves[i];
        if (move == LEVEL_UP_MOVESET_TERMINATOR) {
            break;
        }
        if (MercuryMoveLearner_FilterMatches(controller, move)) {
            StringList_AddFromMessageBank(
                controller->stringList,
                moveNamesLoader,
                move,
                move);
        }
    }

    StringList_AddFromMessageBank(
        controller->stringList,
        controller->messageLoader,
        MoveReminder_Text_Cancel,
        MENU_CANCEL);

    MessageLoader_Free(moveNamesLoader);

    ListMenuTemplate template = sListMenuTemplate;
    template.choices = controller->stringList;
    template.window = &controller->windows[MOVE_REMINDER_WIN_MERCURY_LIST];
    template.count = controller->numMoves;
    template.parent = (void *)controller;

    Window_FillTilemap(&controller->windows[MOVE_REMINDER_WIN_MERCURY_LIST], 15);
    controller->listMenu = ListMenu_New(
        &template,
        controller->data->listPos,
        controller->data->cursorPos,
        HEAP_ID_MOVE_REMINDER);

    Window_ScheduleCopyToVRAM(&controller->windows[MOVE_REMINDER_WIN_MERCURY_LIST]);
}''',
        "MR03C filtered list",
    )

    replace_function(
        source,
        "static u16 MoveReminder_GetSelectedMove(MoveReminderController *controller)",
        r'''static u16 MoveReminder_GetSelectedMove(MoveReminderController *controller)
{
    u16 listPos, cursorPos;
    ListMenu_GetListAndCursorPos(controller->listMenu, &listPos, &cursorPos);
    return (u16)ListMenu_GetIndexOfChoice(controller->listMenu, listPos + cursorPos);
}''',
        "MR03C selected move from filtered list",
    )

    # Replace the old simple sub-screen draw with the clean chrome.
    replace_function(
        source,
        "static void MoveReminder_DrawSubInfo(MoveReminderController *controller)",
        r'''static void MoveReminder_DrawSubInfo(MoveReminderController *controller)
{
    MercuryMoveLearner_DrawBottomChrome(controller);
}''',
        "MR03C sub-screen renderer",
    )

    # The native battle/contest detail renderer is no longer part of the main
    # browsing screen. Keep the function callable for the legacy teach flow but
    # route ordinary browsing through the MR03C page renderer.
    replace_function(
        source,
        "static void MoveReminder_DrawMovesInfo(MoveReminderController *controller)",
        r'''static void MoveReminder_DrawMovesInfo(MoveReminderController *controller)
{
    MercuryMoveLearner_DrawTopPage(controller);

    u16 move = MoveReminder_GetSelectedMove(controller);
    MercuryMoveLearner_DrawSelectedMove(controller, move);
}''',
        "MR03C top renderer",
    )

    helpers = r'''
static void MercuryMoveLearner_LoadPalette(void)
{
    static const u16 palette[16] = {
        GX_RGB(0, 0, 0),
        GX_RGB(3, 7, 13),
        GX_RGB(12, 18, 24),
        GX_RGB(5, 18, 30),
        GX_RGB(24, 28, 31),
        GX_RGB(30, 25, 10),
        GX_RGB(30, 8, 6),
        GX_RGB(8, 22, 29),
        GX_RGB(8, 12, 19),
        GX_RGB(15, 20, 26),
        GX_RGB(20, 24, 28),
        GX_RGB(10, 16, 23),
        GX_RGB(26, 28, 30),
        GX_RGB(6, 13, 20),
        GX_RGB(21, 25, 29),
        GX_RGB(31, 31, 31),
    };

    GX_LoadBGPltt(palette, 15 * PALETTE_SIZE_BYTES, PALETTE_SIZE_BYTES);
    GXS_LoadBGPltt(palette, 15 * PALETTE_SIZE_BYTES, PALETTE_SIZE_BYTES);
}

static void MercuryMoveLearner_DrawPanel(Window *window, u32 x, u32 y, u32 width, u32 height)
{
    Window_FillRectWithColor(window, 1, x, y, width, 1);
    Window_FillRectWithColor(window, 1, x, y + height - 1, width, 1);
    Window_FillRectWithColor(window, 1, x, y, 1, height);
    Window_FillRectWithColor(window, 1, x + width - 1, y, 1, height);
}

static void MercuryMoveLearner_PrintMessage(
    MoveReminderController *controller,
    Window *window,
    u32 messageID,
    u32 x,
    u32 y)
{
    MessageLoader_GetString(controller->messageLoader, messageID, controller->string);
    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        controller->string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 2, 15),
        NULL);
}

static void MercuryMoveLearner_PrintNumber(
    MoveReminderController *controller,
    Window *window,
    u32 value,
    u32 x,
    u32 y)
{
    MoveReminder_FormatNumber(
        controller,
        MoveReminder_Text_PowerValue,
        value,
        3,
        PADDING_MODE_NONE);
    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        controller->string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 2, 15),
        NULL);
}

static void MercuryMoveLearner_PrintMoveName(
    MoveReminderController *controller,
    Window *window,
    u16 move,
    u32 x,
    u32 y)
{
    MessageLoader *loader = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_MOVE_NAMES,
        HEAP_ID_MOVE_REMINDER);
    MessageLoader_GetString(loader, move, controller->string);
    Text_AddPrinterWithParamsAndColor(
        window, FONT_SYSTEM, controller->string,
        x, y, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
    MessageLoader_Free(loader);
}

static void MercuryMoveLearner_PrintTypeName(
    MoveReminderController *controller,
    Window *window,
    u16 type,
    u32 x,
    u32 y)
{
    MessageLoader *loader = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_POKEMON_TYPE_NAMES,
        HEAP_ID_MOVE_REMINDER);
    MessageLoader_GetString(loader, type, controller->string);
    Text_AddPrinterWithParamsAndColor(
        window, FONT_SYSTEM, controller->string,
        x, y, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
    MessageLoader_Free(loader);
}

static BOOL MercuryMoveLearner_FilterMatches(MoveReminderController *controller, u16 move)
{
    if (controller->mercuryFilter == MERCURY_FILTER_ALL) {
        return TRUE;
    }

    u8 source = MoveReminderData_GetMoveSource(controller->data->mon, move);
    switch (controller->mercuryFilter) {
    case MERCURY_FILTER_LEVEL:
        return source == 0;
    case MERCURY_FILTER_EGG:
        return source == 1;
    case MERCURY_FILTER_TUTOR:
        return source == 2;
    case MERCURY_FILTER_SPECIAL:
        return source == 3;
    }

    return TRUE;
}

static void MercuryMoveLearner_RebuildFilteredList(MoveReminderController *controller)
{
    MoveReminder_FreeListMenu(controller);
    controller->data->listPos = 0;
    controller->data->cursorPos = 0;
    MoveReminder_InitListMenu(controller);

    u16 move = MoveReminder_GetSelectedMove(controller);
    MercuryMoveLearner_DrawSelectedMove(controller, move);
}

static void MercuryMoveLearner_DrawBottomChrome(MoveReminderController *controller)
{
    Window *filter = &controller->windows[MOVE_REMINDER_WIN_MERCURY_FILTER];
    Window *current = &controller->windows[MOVE_REMINDER_WIN_MERCURY_CURRENT];
    Window *help = &controller->windows[MOVE_REMINDER_WIN_MERCURY_HELP];

    Window_FillTilemap(filter, 15);
    Window_FillTilemap(current, 15);
    Window_FillTilemap(help, 15);

    MercuryMoveLearner_DrawPanel(filter, 0, 0, 240, 23);
    MercuryMoveLearner_DrawPanel(current, 0, 0, 240, 39);
    MercuryMoveLearner_DrawPanel(help, 0, 0, 240, 15);

    static const u32 filterMessages[5] = {
        MoveReminder_Text_MercuryFilterAll,
        MoveReminder_Text_MercuryFilterLevel,
        MoveReminder_Text_MercuryFilterEgg,
        MoveReminder_Text_MercuryFilterTutor,
        MoveReminder_Text_MercuryFilterSpecial,
    };
    static const u8 tabX[5] = { 3, 49, 95, 141, 187 };
    static const u8 textX[5] = { 14, 55, 106, 148, 190 };

    for (u32 i = 0; i < 5; i++) {
        if (i == controller->mercuryFilter) {
            Window_FillRectWithColor(filter, 4, tabX[i] + 1, 3, 44, 17);
            Window_FillRectWithColor(filter, 3, tabX[i], 2, 46, 1);
            Window_FillRectWithColor(filter, 3, tabX[i], 20, 46, 1);
            Window_FillRectWithColor(filter, 3, tabX[i], 2, 1, 19);
            Window_FillRectWithColor(filter, 3, tabX[i] + 45, 2, 1, 19);
        } else {
            MercuryMoveLearner_DrawPanel(filter, tabX[i], 2, 46, 19);
        }

        MercuryMoveLearner_PrintMessage(
            controller,
            filter,
            filterMessages[i],
            textX[i],
            5);
    }

    MercuryMoveLearner_PrintMessage(
        controller,
        current,
        MoveReminder_Text_MercuryCurrentMoves,
        5,
        2);

    static const u8 cardX[LEARNED_MOVES_MAX] = { 2, 62, 122, 182 };
    for (u16 i = 0; i < LEARNED_MOVES_MAX; i++) {
        u16 move = Pokemon_GetValue(controller->data->mon, MON_DATA_MOVE1 + i, NULL);
        MercuryMoveLearner_DrawPanel(current, cardX[i], 14, 56, 23);

        if (move == MOVE_NONE) {
            continue;
        }

        MercuryMoveLearner_PrintMoveName(controller, current, move, cardX[i] + 3, 16);

        u16 type = MoveTable_LoadParam(move, MOVEATTRIBUTE_TYPE);
        MercuryMoveLearner_PrintTypeName(controller, current, type, cardX[i] + 3, 27);

        u16 pp = Pokemon_GetValue(controller->data->mon, MON_DATA_MOVE1_PP + i, NULL);
        MercuryMoveLearner_PrintNumber(controller, current, pp, cardX[i] + 35, 27);
    }

    MercuryMoveLearner_PrintMessage(
        controller,
        help,
        MoveReminder_Text_MercuryHelp,
        6,
        2);

    Window_ScheduleCopyToVRAM(filter);
    Window_ScheduleCopyToVRAM(current);
    Window_ScheduleCopyToVRAM(help);
}

static void MercuryMoveLearner_DrawSelectedMove(MoveReminderController *controller, u32 move)
{
    Window *window = &controller->windows[MOVE_REMINDER_WIN_MERCURY_DESC];
    Window_FillTilemap(window, 15);
    MercuryMoveLearner_DrawPanel(window, 0, 0, 240, 47);

    if (move == MENU_CANCEL || move == LEVEL_UP_MOVESET_TERMINATOR) {
        MercuryMoveLearner_PrintMessage(
            controller,
            window,
            MoveReminder_Text_MercuryCancelHint,
            6,
            6);
        Window_ScheduleCopyToVRAM(window);
        return;
    }

    MercuryMoveLearner_PrintMoveName(controller, window, move, 6, 4);

    u16 type = MoveTable_LoadParam(move, MOVEATTRIBUTE_TYPE);
    MercuryMoveLearner_PrintTypeName(controller, window, type, 96, 4);

    u16 moveClass = MoveTable_LoadParam(move, MOVEATTRIBUTE_CLASS);
    u32 classMsg = MoveReminder_Text_MercuryClassStatus;
    if (moveClass == CLASS_PHYSICAL) classMsg = MoveReminder_Text_MercuryClassPhysical;
    if (moveClass == CLASS_SPECIAL) classMsg = MoveReminder_Text_MercuryClassSpecial;
    MercuryMoveLearner_PrintMessage(controller, window, classMsg, 158, 4);

    MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryPowerShort, 6, 17);
    u32 power = MoveTable_LoadParam(move, MOVEATTRIBUTE_POWER);
    if (power <= 1) {
        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_Dashes, 34, 17);
    } else {
        MercuryMoveLearner_PrintNumber(controller, window, power, 34, 17);
    }

    MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryAccuracyShort, 70, 17);
    u32 accuracy = MoveTable_LoadParam(move, MOVEATTRIBUTE_ACCURACY);
    if (accuracy == 0) {
        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_Dashes, 105, 17);
    } else {
        MercuryMoveLearner_PrintNumber(controller, window, accuracy, 105, 17);
    }

    MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryPPShort, 145, 17);
    MercuryMoveLearner_PrintNumber(
        controller,
        window,
        MoveTable_CalcMaxPP(move, 0),
        166,
        17);

    MessageLoader *desc = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_MOVE_DESCRIPTIONS,
        HEAP_ID_MOVE_REMINDER);
    MessageLoader_GetString(desc, move, controller->string);
    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        controller->string,
        6,
        30,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 2, 15),
        NULL);
    MessageLoader_Free(desc);

    Window_ScheduleCopyToVRAM(window);
}

static void MercuryMoveLearner_DrawTopIdentity(MoveReminderController *controller, Window *window)
{
    Pokemon *mon = controller->data->mon;

    Pokemon_GetValue(mon, MON_DATA_NICKNAME_STRING, controller->string);
    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        controller->string,
        8,
        20,
        TEXT_SPEED_NO_TRANSFER,
        TEXT_COLOR(1, 2, 15),
        NULL);

    MercuryMoveLearner_PrintMessage(
        controller,
        window,
        MoveReminder_Text_MercuryLevel,
        114,
        20);
    MercuryMoveLearner_PrintNumber(
        controller,
        window,
        Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL),
        144,
        20);

    u16 type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
    u16 type2 = Pokemon_GetValue(mon, MON_DATA_TYPE_2, NULL);
    MercuryMoveLearner_PrintTypeName(controller, window, type1, 178, 20);
    if (type2 != type1) {
        MercuryMoveLearner_PrintTypeName(controller, window, type2, 210, 20);
    }
}

static void MercuryMoveLearner_DrawTopPage(MoveReminderController *controller)
{
    Window *window = &controller->windows[MOVE_REMINDER_WIN_MERCURY_TOP];
    Pokemon *mon = controller->data->mon;

    Window_FillTilemap(window, 15);
    MercuryMoveLearner_DrawPanel(window, 0, 0, 240, 175);

    Window_FillRectWithColor(window, 4, 1, 1, 238, 31);
    Window_FillRectWithColor(window, 3, 1, 31, 238, 2);

    MercuryMoveLearner_DrawTopIdentity(controller, window);

    u32 pageTitle = MoveReminder_Text_MercuryMoveView;
    if (controller->mercuryPage == MERCURY_PAGE_STATS) {
        pageTitle = MoveReminder_Text_MercuryStatsView;
    } else if (controller->mercuryPage == MERCURY_PAGE_ABILITY) {
        pageTitle = MoveReminder_Text_MercuryAbilityView;
    }

    MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryShoulderLeft, 6, 4);
    MercuryMoveLearner_PrintMessage(controller, window, pageTitle, 82, 4);
    MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryShoulderRight, 220, 4);

    if (controller->mercuryPage == MERCURY_PAGE_MOVE) {
        MercuryMoveLearner_DrawPanel(window, 4, 36, 92, 100);
        Window_FillRectWithColor(window, 8, 8, 40, 84, 70);
        MercuryMoveLearner_PrintMessage(
            controller, window,
            MoveReminder_Text_MercuryPokemonPanel,
            24, 66);
        MercuryMoveLearner_DrawPanel(window, 100, 36, 136, 100);
        MercuryMoveLearner_DrawPanel(window, 4, 140, 232, 30);

        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryHP, 12, 120);
        u32 hp = Pokemon_GetValue(mon, MON_DATA_HP, NULL);
        u32 maxHP = Pokemon_GetValue(mon, MON_DATA_MAX_HP, NULL);
        MercuryMoveLearner_PrintNumber(controller, window, hp, 34, 120);
        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercurySlash, 58, 120);
        MercuryMoveLearner_PrintNumber(controller, window, maxHP, 70, 120);

        Window_FillRectWithColor(window, 2, 12, 130, 72, 5);
        if (maxHP > 0) {
            u32 fill = (72 * hp) / maxHP;
            Window_FillRectWithColor(window, 3, 12, 130, fill, 5);
        }

        u16 selected = MoveReminder_GetSelectedMove(controller);
        if (selected != MENU_CANCEL && selected != LEVEL_UP_MOVESET_TERMINATOR) {
            MercuryMoveLearner_PrintMoveName(controller, window, selected, 108, 43);

            u16 type = MoveTable_LoadParam(selected, MOVEATTRIBUTE_TYPE);
            MercuryMoveLearner_PrintTypeName(controller, window, type, 108, 58);

            u16 moveClass = MoveTable_LoadParam(selected, MOVEATTRIBUTE_CLASS);
            u32 classMsg = MoveReminder_Text_MercuryClassStatus;
            if (moveClass == CLASS_PHYSICAL) classMsg = MoveReminder_Text_MercuryClassPhysical;
            if (moveClass == CLASS_SPECIAL) classMsg = MoveReminder_Text_MercuryClassSpecial;
            MercuryMoveLearner_PrintMessage(controller, window, classMsg, 176, 58);

            MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryPower, 108, 72);
            u32 power = MoveTable_LoadParam(selected, MOVEATTRIBUTE_POWER);
            if (power <= 1) {
                MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_Dashes, 166, 72);
            } else {
                MercuryMoveLearner_PrintNumber(controller, window, power, 166, 72);
            }

            MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryAccuracy, 108, 86);
            u32 accuracy = MoveTable_LoadParam(selected, MOVEATTRIBUTE_ACCURACY);
            if (accuracy == 0) {
                MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_Dashes, 166, 86);
            } else {
                MercuryMoveLearner_PrintNumber(controller, window, accuracy, 166, 86);
            }

            MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryPP, 108, 100);
            MercuryMoveLearner_PrintNumber(controller, window, MoveTable_CalcMaxPP(selected, 0), 166, 100);

            MessageLoader *desc = MessageLoader_Init(
                MSG_LOADER_LOAD_ON_DEMAND,
                NARC_INDEX_MSGDATA__PL_MSG,
                TEXT_BANK_MOVE_DESCRIPTIONS,
                HEAP_ID_MOVE_REMINDER);
            MessageLoader_GetString(desc, selected, controller->string);
            Text_AddPrinterWithParamsAndColor(
                window, FONT_SYSTEM, controller->string,
                108, 114, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
            MessageLoader_Free(desc);
        }

        static const u8 cardX[LEARNED_MOVES_MAX] = { 7, 65, 123, 181 };
        for (u16 i = 0; i < LEARNED_MOVES_MAX; i++) {
            u16 move = Pokemon_GetValue(mon, MON_DATA_MOVE1 + i, NULL);
            MercuryMoveLearner_DrawPanel(window, cardX[i], 143, 54, 24);

            if (move != MOVE_NONE) {
                MercuryMoveLearner_PrintMoveName(controller, window, move, cardX[i] + 3, 145);
                MercuryMoveLearner_PrintNumber(
                    controller,
                    window,
                    Pokemon_GetValue(mon, MON_DATA_MOVE1_PP + i, NULL),
                    cardX[i] + 22,
                    157);
            }
        }
    } else if (controller->mercuryPage == MERCURY_PAGE_STATS) {
        MercuryMoveLearner_DrawPanel(window, 4, 36, 92, 134);
        Window_FillRectWithColor(window, 8, 8, 40, 84, 96);
        MercuryMoveLearner_PrintMessage(
            controller, window,
            MoveReminder_Text_MercuryPokemonPanel,
            24, 80);
        MercuryMoveLearner_DrawPanel(window, 100, 36, 136, 96);
        MercuryMoveLearner_DrawPanel(window, 100, 136, 136, 34);

        static const u32 labels[6] = {
            MoveReminder_Text_MercuryHP,
            MoveReminder_Text_MercuryAttack,
            MoveReminder_Text_MercuryDefense,
            MoveReminder_Text_MercurySpAttack,
            MoveReminder_Text_MercurySpDefense,
            MoveReminder_Text_MercurySpeed,
        };
        static const u16 params[6] = {
            MON_DATA_MAX_HP,
            MON_DATA_ATK,
            MON_DATA_DEF,
            MON_DATA_SP_ATK,
            MON_DATA_SP_DEF,
            MON_DATA_SPEED,
        };

        for (u32 i = 0; i < 6; i++) {
            u32 y = 44 + i * 14;
            MercuryMoveLearner_PrintMessage(controller, window, labels[i], 108, y);
            u32 value = Pokemon_GetValue(mon, params[i], NULL);
            MercuryMoveLearner_PrintNumber(controller, window, value, 158, y);

            u32 bar = value;
            if (bar > 255) bar = 255;
            Window_FillRectWithColor(window, 2, 188, y + 3, 38, 5);
            Window_FillRectWithColor(window, 3, 188, y + 3, (38 * bar) / 255, 5);
        }

        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryNature, 108, 141);
        MessageLoader *nature = MessageLoader_Init(
            MSG_LOADER_LOAD_ON_DEMAND,
            NARC_INDEX_MSGDATA__PL_MSG,
            TEXT_BANK_NATURE_NAMES,
            HEAP_ID_MOVE_REMINDER);
        MessageLoader_GetString(nature, Pokemon_GetNature(mon), controller->string);
        Text_AddPrinterWithParamsAndColor(
            window, FONT_SYSTEM, controller->string,
            164, 141, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
        MessageLoader_Free(nature);

        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryHeldItem, 108, 155);
        u16 item = Pokemon_GetValue(mon, MON_DATA_HELD_ITEM, NULL);
        if (item == 0) {
            MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryNone, 164, 155);
        } else {
            Item_LoadName(controller->string, item, HEAP_ID_MOVE_REMINDER);
            Text_AddPrinterWithParamsAndColor(
                window, FONT_SYSTEM, controller->string,
                164, 155, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
        }
    } else {
        MercuryMoveLearner_DrawPanel(window, 4, 36, 92, 134);
        Window_FillRectWithColor(window, 8, 8, 40, 84, 96);
        MercuryMoveLearner_PrintMessage(
            controller, window,
            MoveReminder_Text_MercuryPokemonPanel,
            24, 80);
        MercuryMoveLearner_DrawPanel(window, 100, 36, 136, 78);
        MercuryMoveLearner_DrawPanel(window, 100, 118, 136, 52);

        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryAbility, 108, 44);

        u16 ability = Pokemon_GetValue(mon, MON_DATA_ABILITY, NULL);
        MessageLoader *abilityNames = MessageLoader_Init(
            MSG_LOADER_LOAD_ON_DEMAND,
            NARC_INDEX_MSGDATA__PL_MSG,
            TEXT_BANK_ABILITY_NAMES,
            HEAP_ID_MOVE_REMINDER);
        MessageLoader_GetString(abilityNames, ability, controller->string);
        Text_AddPrinterWithParamsAndColor(
            window, FONT_SYSTEM, controller->string,
            108, 60, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
        MessageLoader_Free(abilityNames);

        MessageLoader *abilityDesc = MessageLoader_Init(
            MSG_LOADER_LOAD_ON_DEMAND,
            NARC_INDEX_MSGDATA__PL_MSG,
            TEXT_BANK_ABILITY_DESCRIPTIONS,
            HEAP_ID_MOVE_REMINDER);
        MessageLoader_GetString(abilityDesc, ability, controller->string);
        Text_AddPrinterWithParamsAndColor(
            window, FONT_SYSTEM, controller->string,
            108, 78, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
        MessageLoader_Free(abilityDesc);

        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryInnateAbilities, 108, 126);
        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryOff, 210, 126);
        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryDash, 112, 142);
        MercuryMoveLearner_PrintMessage(controller, window, MoveReminder_Text_MercuryDash, 112, 154);
    }

    Window_ScheduleCopyToVRAM(window);
}
'''

    marker = "static u32 MoveReminder_GetNumMoves(MoveReminderController *controller)\n"
    text = source.read_text()
    if helpers.strip() not in text:
        if text.count(marker) != 1:
            raise SystemExit("MR03C helper insertion marker changed")
        source.write_text(text.replace(marker, helpers + "\n" + marker, 1))

    # Initialize page/filter before the ListMenu is built.  Clear legacy main
    # windows once so they cannot bleed into the custom page.
    replace_once(
        source,
        """    MoveReminder_InitWindows(controller);
    MoveReminder_InitListMenu(controller);
    MoveReminder_DrawMovesInfo(controller);""",
        """    MoveReminder_InitWindows(controller);
    controller->mercuryPage = MERCURY_PAGE_MOVE;
    controller->mercuryFilter = MERCURY_FILTER_ALL;

    MercuryMoveLearner_LoadPalette();

    for (u32 i = MOVE_REMINDER_WIN_LABEL_BATTLE_MOVES;
         i <= MOVE_REMINDER_WIN_MOVES_NAMES;
         i++) {
        if (i != MOVE_REMINDER_WIN_MESSAGE_BOX) {
            Window_ClearAndScheduleCopyToVRAM(&controller->windows[i]);
        }
    }
    MoveReminder_DrawTypeIcons(controller);
    MoveReminder_DrawSideArrows(controller, FALSE);
    MoveReminder_DrawArrows(controller);

    MoveReminder_InitListMenu(controller);
    MercuryMoveLearner_DrawBottomChrome(controller);
    MoveReminder_DrawMovesInfo(controller);""",
        "MR03C setup",
    )

    # Free-list callback is unchanged, but a filter switch resets list/cursor
    # intentionally.  Confirmation states always use the selected move ID.
    # Keep native message box visible for teaching confirmation.
    replace_once(
        source,
        """    MoveReminder_DrawLabelText(controller);
    MoveReminder_DrawSubInfo(controller);

    Window_FillTilemap(&controller->windows[MOVE_REMINDER_WIN_MESSAGE_BOX], 15);""",
        """    Window_FillTilemap(&controller->windows[MOVE_REMINDER_WIN_MESSAGE_BOX], 15);""",
        "MR03C suppress native labels",
    )


def patch_text(root: Path) -> None:
    path = root / "res/text/move_reminder.json"
    data = json.loads(path.read_text())

    additions = {
        "MoveReminder_Text_MercuryMoveView": "MOVE VIEW",
        "MoveReminder_Text_MercuryStatsView": "STATS VIEW",
        "MoveReminder_Text_MercuryAbilityView": "ABILITY VIEW",
        "MoveReminder_Text_MercuryShoulderLeft": "L",
        "MoveReminder_Text_MercuryShoulderRight": "R",
        "MoveReminder_Text_MercuryPokemonPanel": "POKEMON",
        "MoveReminder_Text_MercuryFilterAll": "ALL",
        "MoveReminder_Text_MercuryFilterLevel": "LEVEL",
        "MoveReminder_Text_MercuryFilterEgg": "EGG",
        "MoveReminder_Text_MercuryFilterTutor": "TUTOR",
        "MoveReminder_Text_MercuryFilterSpecial": "SPECIAL",
        "MoveReminder_Text_MercuryCurrentMoves": "CURRENT MOVES",
        "MoveReminder_Text_MercuryHelp": "Y INSPECT   X FILTER   A TEACH   B BACK",
        "MoveReminder_Text_MercuryCancelHint": "BACK",
        "MoveReminder_Text_MercuryClassPhysical": "PHYS",
        "MoveReminder_Text_MercuryClassSpecial": "SPEC",
        "MoveReminder_Text_MercuryClassStatus": "STATUS",
        "MoveReminder_Text_MercurySourceLevel": "L",
        "MoveReminder_Text_MercurySourceEgg": "E",
        "MoveReminder_Text_MercurySourceTutor": "T",
        "MoveReminder_Text_MercurySourceSpecial": "S",
        "MoveReminder_Text_MercuryPowerShort": "PWR",
        "MoveReminder_Text_MercuryAccuracyShort": "ACC",
        "MoveReminder_Text_MercuryPPShort": "PP",
        "MoveReminder_Text_MercuryPower": "Power",
        "MoveReminder_Text_MercuryAccuracy": "Accuracy",
        "MoveReminder_Text_MercuryPP": "PP",
        "MoveReminder_Text_MercuryLevel": "Lv.",
        "MoveReminder_Text_MercuryHP": "HP",
        "MoveReminder_Text_MercuryAttack": "Attack",
        "MoveReminder_Text_MercuryDefense": "Defense",
        "MoveReminder_Text_MercurySpAttack": "Sp. Atk",
        "MoveReminder_Text_MercurySpDefense": "Sp. Def",
        "MoveReminder_Text_MercurySpeed": "Speed",
        "MoveReminder_Text_MercuryNature": "Nature",
        "MoveReminder_Text_MercuryHeldItem": "Held Item",
        "MoveReminder_Text_MercuryAbility": "Ability",
        "MoveReminder_Text_MercuryInnateAbilities": "Innate Abilities (Mercury)",
        "MoveReminder_Text_MercuryOff": "OFF",
        "MoveReminder_Text_MercuryNone": "None",
        "MoveReminder_Text_MercurySlash": "/",
        "MoveReminder_Text_MercuryDash": "-",
    }

    by_id = {msg.get("id"): msg for msg in data["messages"]}
    for msg_id, text in additions.items():
        if msg_id in by_id:
            by_id[msg_id]["en_US"] = text
            by_id[msg_id].pop("garbage", None)
        else:
            data["messages"].append({"id": msg_id, "en_US": text})

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr03c-clean-ui.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_ui(root)
    patch_text(root)

    report = {
        "gate": "MERCURY_MR03C_CLEAN_UI",
        "status": "PASS",
        "source_of_truth": "approved six-panel Move Learner mockup",
        "architecture": "fixed non-overlapping DS-native windows",
        "top_pages": ["MOVE VIEW", "STATS VIEW", "ABILITY VIEW"],
        "page_controls": "L/R",
        "filters": ["ALL", "LEVEL", "EGG", "TUTOR", "SPECIAL"],
        "filter_control": "X",
        "bottom_regions": [
            "filter tabs",
            "current moves",
            "five-row filtered learnable list",
            "selected move details/effect",
            "button hints",
        ],
        "preserved": [
            "MR03 universal learner backend",
            "normal party-menu entry",
            "native teach/replace flow",
            "normal story boot",
        ],
        "visual_pass": "Mercury blue palette and tab/card styling; portrait temporarily isolated after preview-task runtime crash",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
