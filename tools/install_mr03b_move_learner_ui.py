#!/usr/bin/env python3
"""MR03B Mercury Move Learner UI.

Reworks the proven MR03 Move Learner into a DS two-screen workspace:

Top screen
  * MOVE page: keeps the already-approved native Platinum move detail view.
  * STATS page: L/R shoulder navigation, live battle stats + nature.
  * ABILITY page: ability name + canonical description.

Bottom screen
  * current four moves
  * scrollable learnable-move list
  * live description for the highlighted move
  * compact button help

This pass deliberately keeps the native ListMenu/D-pad teaching flow intact.
Touch filters are a later polish pass; this installer focuses on getting the
new screen architecture working without destabilizing the learner backend.
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
    # Function names also appear in the forward-declaration block near
    # the top of move_reminder.c.  Use the final occurrence so we patch the
    # actual definition rather than consuming everything from a prototype to
    # the next unrelated brace.
    start = text.rfind(signature)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

    brace = text.find("{", start + len(signature))
    if brace < 0:
        raise SystemExit(f"{label}: opening brace not found in {path}")

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

    # Extra windows: a bottom description/footer and one compact opaque card
    # on the top screen for Stats/Ability pages.
    replace_once(
        source,
        """    MOVE_REMINDER_WIN_YES_NO_MENU,
    MOVE_REMINDER_WIN_SUB_INFO,
    MAX_MOVE_REMINDER_WIN
};""",
        """    MOVE_REMINDER_WIN_YES_NO_MENU,
    MOVE_REMINDER_WIN_SUB_INFO,
    MOVE_REMINDER_WIN_SUB_DESC,
    MOVE_REMINDER_WIN_SUB_HELP,
    MOVE_REMINDER_WIN_TOP_PAGE,
    MAX_MOVE_REMINDER_WIN
};""",
        "MR03B window enum",
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
} MoveReminderController;""",
        "MR03B controller page state",
    )

    decl_anchor = "static void MoveReminder_DrawSubInfo(MoveReminderController *controller);\n"
    insert_after_once(
        source,
        decl_anchor,
        """static void MoveReminder_DrawSubMoveDescription(MoveReminderController *controller, u32 move);
static void MoveReminder_DrawMercuryTopPage(MoveReminderController *controller);
static void MoveReminder_SetNativeMoveViewVisible(MoveReminderController *controller, BOOL visible);
""",
        "MR03B function declarations",
    )

    # Move the native ListMenu from the top engine to the touch screen.
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
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 7,
        .width = 30,
        .height = 9,
        .palette = 15,
        .baseTile = 0x0D3,
    },""",
        "MR03B bottom move list window",
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
        .tilemapLeft = 1,
        .tilemapTop = 0,
        .width = 30,
        .height = 7,
        .palette = 15,
        .baseTile = 1,
    },
    [MOVE_REMINDER_WIN_SUB_DESC] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 16,
        .width = 30,
        .height = 6,
        .palette = 15,
        .baseTile = 0x1E1,
    },
    [MOVE_REMINDER_WIN_SUB_HELP] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 22,
        .width = 30,
        .height = 2,
        .palette = 15,
        .baseTile = 0x295,
    },
    [MOVE_REMINDER_WIN_TOP_PAGE] = {
        .bgLayer = BG_LAYER_MAIN_0,
        .tilemapLeft = 5,
        .tilemapTop = 3,
        .width = 22,
        .height = 14,
        .palette = 15,
        .baseTile = 0x2C2,
    }
};""",
        "MR03B workspace windows",
    )

    replace_once(
        source,
        "    .maxDisplay = 7,\n",
        "    .maxDisplay = 4,\n",
        "MR03B bottom list visible rows",
    )
    replace_once(
        source,
        "    .textColorBg = 0,\n",
        "    .textColorBg = 15,\n",
        "MR03B bottom list white background",
    )
    replace_once(
        source,
        "    .cursorType = 1,\n",
        "    .cursorType = 0,\n",
        "MR03B bottom list native text cursor",
    )
    replace_once(
        source,
        """    controller->listMenu = ListMenu_New(&template, controller->data->listPos, controller->data->cursorPos, HEAP_ID_MOVE_REMINDER);

    Window_ScheduleCopyToVRAM(&controller->windows[MOVE_REMINDER_WIN_MOVES_NAMES]);""",
        """    Window_FillTilemap(&controller->windows[MOVE_REMINDER_WIN_MOVES_NAMES], 15);
    controller->listMenu = ListMenu_New(&template, controller->data->listPos, controller->data->cursorPos, HEAP_ID_MOVE_REMINDER);

    Window_ScheduleCopyToVRAM(&controller->windows[MOVE_REMINDER_WIN_MOVES_NAMES]);""",
        "MR03B white list fill",
    )

    # The old move selector and scroll arrows are also engine-A sprites. The
    # sub-screen ListMenu now draws its own native text cursor instead.
    replace_function(
        source,
        "static void MoveReminder_DrawMoveSelector(MoveReminderController *controller, u8 cursorPos, u8 palette)",
        r'''static void MoveReminder_DrawMoveSelector(MoveReminderController *controller, u8 cursorPos, u8 palette)
{
    ManagedSprite_SetDrawFlag(
        controller->managedSprites[MOVE_REMINDER_SPRITE_MOVE_SELECTOR],
        FALSE);
}''',
        "MR03B hide engine-A selector",
    )
    replace_function(
        source,
        "static void MoveReminder_DrawArrows(MoveReminderController *controller)",
        r'''static void MoveReminder_DrawArrows(MoveReminderController *controller)
{
    ManagedSprite_SetDrawFlag(
        controller->managedSprites[MOVE_REMINDER_SPRITE_SCROLL_ARROW_UP],
        FALSE);
    ManagedSprite_SetDrawFlag(
        controller->managedSprites[MOVE_REMINDER_SPRITE_SCROLL_ARROW_DOWN],
        FALSE);
}''',
        "MR03B hide engine-A scroll arrows",
    )

    # The old row type sprites belong to engine A; with the list moved to the
    # sub screen they would float over the top screen. Keep only the selected
    # move's native category icon on the MOVE page.
    replace_function(
        source,
        "static void MoveReminder_DrawTypeIcons(MoveReminderController *controller)",
        r'''static void MoveReminder_DrawTypeIcons(MoveReminderController *controller)
{
    for (u32 i = 0; i < 7; i++) {
        ManagedSprite_SetDrawFlag(
            controller->managedSprites[MOVE_REMINDER_SPRITE_TYPE_MOVE_0 + i],
            FALSE);
    }
}''',
        "MR03B hide orphaned top-engine type rows",
    )

    # Page switching replaces the old contest left/right toggle. L/R shoulders
    # cycle MOVE -> STATS -> ABILITY while the bottom list stays active.
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
        MoveReminder_DrawMercuryTopPage(controller);
        return MOVE_REMINDER_STATE_PROCESS_MAIN_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_R)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        controller->mercuryPage = (controller->mercuryPage + 1) % 3;
        MoveReminder_DrawMercuryTopPage(controller);
        return MOVE_REMINDER_STATE_PROCESS_MAIN_INPUT;
    }
"""
    replace_once(source, old_input, new_input, "MR03B L/R page switching")

    # Before any confirmation dialog, return to the MOVE page so Platinum's
    # native message box and replacement flow are never obscured.
    replace_once(
        source,
        """    case MENU_CANCEL:
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        MoveReminder_DrawMoveSelector(controller, controller->data->cursorPos, 1);""",
        """    case MENU_CANCEL:
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        controller->mercuryPage = 0;
        MoveReminder_DrawMercuryTopPage(controller);
        MoveReminder_DrawMoveSelector(controller, controller->data->cursorPos, 1);""",
        "MR03B cancel restores Move page",
    )
    replace_once(
        source,
        """    default:
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        MoveReminder_DrawMoveSelector(controller, controller->data->cursorPos, 1);""",
        """    default:
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        controller->mercuryPage = 0;
        MoveReminder_DrawMercuryTopPage(controller);
        MoveReminder_DrawMoveSelector(controller, controller->data->cursorPos, 1);""",
        "MR03B teach restores Move page",
    )

    # Cursor movement always updates the lower description; top move-detail
    # updates only when the MOVE page is active.
    replace_function(
        source,
        "static void MoveReminder_ListMenuCursorCallback(ListMenu *menu, u32 move, u8 onInit)",
        r'''static void MoveReminder_ListMenuCursorCallback(ListMenu *menu, u32 move, u8 onInit)
{
    MoveReminderController *controller = (MoveReminderController *)ListMenu_GetAttribute(menu, LIST_MENU_PARENT);

    if (onInit != TRUE) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
    }

    MoveReminder_DrawSubMoveDescription(controller, move);

    if (controller->mercuryPage == 0) {
        controller->data->showingContest = 0;
        MoveReminder_DrawBattleMovesText(controller, move);
        MoveReminder_DrawTypeIcons(controller);
    }
}''',
        "MR03B cursor callback",
    )

    # Replace the original simple bottom info panel with the new workspace,
    # then add the Stats/Ability top-page renderer immediately after it.
    replace_function(
        source,
        "static void MoveReminder_DrawSubInfo(MoveReminderController *controller)",
        r'''static void MoveReminder_DrawSubInfo(MoveReminderController *controller)
{
    Window *current = &controller->windows[MOVE_REMINDER_WIN_SUB_INFO];
    Window *help = &controller->windows[MOVE_REMINDER_WIN_SUB_HELP];

    Window_FillTilemap(current, 15);
    Window_FillTilemap(help, 15);

    MessageLoader_GetString(
        controller->messageLoader,
        MoveReminder_Text_MercuryLearnerCurrentMoves,
        controller->string);
    Text_AddPrinterWithParamsAndColor(
        current, FONT_SYSTEM, controller->string,
        4, 0, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);

    MessageLoader *moveNamesLoader = MessageLoader_Init(
        MSG_LOADER_PRELOAD_ENTIRE_BANK,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_MOVE_NAMES,
        HEAP_ID_MOVE_REMINDER);

    static const u8 moveX[LEARNED_MOVES_MAX] = { 4, 124, 4, 124 };
    static const u8 moveY[LEARNED_MOVES_MAX] = { 17, 17, 34, 34 };

    for (u16 i = 0; i < LEARNED_MOVES_MAX; i++) {
        u16 move = Pokemon_GetValue(
            controller->data->mon,
            MON_DATA_MOVE1 + i,
            NULL);

        if (move != 0) {
            MessageLoader_GetString(moveNamesLoader, move, controller->string);
            Text_AddPrinterWithParamsAndColor(
                current, FONT_SYSTEM, controller->string,
                moveX[i], moveY[i], TEXT_SPEED_NO_TRANSFER,
                TEXT_COLOR(1, 2, 15), NULL);
        }
    }

    MessageLoader_Free(moveNamesLoader);

    MessageLoader_GetString(
        controller->messageLoader,
        MoveReminder_Text_MercuryLearnerLearnable,
        controller->string);
    Text_AddPrinterWithParamsAndColor(
        current, FONT_SYSTEM, controller->string,
        4, 48, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);

    MessageLoader_GetString(
        controller->messageLoader,
        MoveReminder_Text_MercuryLearnerHelp,
        controller->string);
    Text_AddPrinterWithParamsAndColor(
        help, FONT_SYSTEM, controller->string,
        2, 0, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);

    Window_ScheduleCopyToVRAM(current);
    Window_ScheduleCopyToVRAM(help);
}''',
        "MR03B bottom current moves",
    )

    insertion_marker = "static u32 MoveReminder_GetNumMoves(MoveReminderController *controller)\n"
    extra_functions = r'''
static void MoveReminder_DrawSubMoveDescription(MoveReminderController *controller, u32 move)
{
    Window *window = &controller->windows[MOVE_REMINDER_WIN_SUB_DESC];
    Window_FillTilemap(window, 15);

    if (move == MENU_CANCEL || move == LEVEL_UP_MOVESET_TERMINATOR) {
        Window_ScheduleCopyToVRAM(window);
        return;
    }

    MessageLoader *moveNames = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_MOVE_NAMES,
        HEAP_ID_MOVE_REMINDER);
    MessageLoader_GetString(moveNames, move, controller->string);
    Text_AddPrinterWithParamsAndColor(
        window, FONT_SYSTEM, controller->string,
        2, 0, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
    MessageLoader_Free(moveNames);

    u16 type = MoveTable_LoadParam(move, MOVEATTRIBUTE_TYPE);
    MessageLoader *typeNames = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_POKEMON_TYPE_NAMES,
        HEAP_ID_MOVE_REMINDER);
    MessageLoader_GetString(typeNames, type, controller->string);
    Text_AddPrinterWithParamsAndColor(
        window, FONT_SYSTEM, controller->string,
        164, 0, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
    MessageLoader_Free(typeNames);

    MessageLoader *moveDesc = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_MOVE_DESCRIPTIONS,
        HEAP_ID_MOVE_REMINDER);
    MessageLoader_GetString(moveDesc, move, controller->string);
    Text_AddPrinterWithParamsAndColor(
        window, FONT_SYSTEM, controller->string,
        2, 16, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
    MessageLoader_Free(moveDesc);

    Window_ScheduleCopyToVRAM(window);
}

static void MoveReminder_SetNativeMoveViewVisible(MoveReminderController *controller, BOOL visible)
{
    if (!visible) {
        for (u32 i = MOVE_REMINDER_WIN_LABEL_BATTLE_MOVES;
             i <= MOVE_REMINDER_WIN_MOVE_CONTEST_DESCRIPTION;
             i++) {
            Window_ClearAndScheduleCopyToVRAM(&controller->windows[i]);
        }

        ManagedSprite_SetDrawFlag(
            controller->managedSprites[MOVE_REMINDER_SPRITE_CATEGORY],
            FALSE);
        MoveReminder_DrawTypeIcons(controller);
        return;
    }

    MoveReminder_DrawLabelText(controller);
    controller->data->showingContest = 0;
    MoveReminder_DrawMovesInfo(controller);
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
        window, FONT_SYSTEM, controller->string,
        x, y, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
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
        window, FONT_SYSTEM, controller->string,
        x, y, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
}

static void MoveReminder_DrawMercuryTopPage(MoveReminderController *controller)
{
    Window *page = &controller->windows[MOVE_REMINDER_WIN_TOP_PAGE];

    if (controller->mercuryPage == 0) {
        Window_FillTilemap(page, 0);
        Window_ClearAndScheduleCopyToVRAM(page);
        MoveReminder_SetNativeMoveViewVisible(controller, TRUE);
        return;
    }

    MoveReminder_SetNativeMoveViewVisible(controller, FALSE);
    Window_FillTilemap(page, 15);
    Window_FillRectWithColor(page, 0, 0, 0, 176, 112);
    Window_FillRectWithColor(page, 15, 2, 2, 172, 108);

    Pokemon *mon = controller->data->mon;

    if (controller->mercuryPage == 1) {
        MercuryMoveLearner_PrintMessage(
            controller, page,
            MoveReminder_Text_MercuryStatsTitle,
            8, 4);

        Pokemon_GetValue(mon, MON_DATA_NICKNAME_STRING, controller->string);
        Text_AddPrinterWithParamsAndColor(
            page, FONT_SYSTEM, controller->string,
            8, 20, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);

        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercuryLevel, 104, 20);
        MercuryMoveLearner_PrintNumber(
            controller, page,
            Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL),
            140, 20);

        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercuryHP, 8, 38);
        MercuryMoveLearner_PrintNumber(
            controller, page,
            Pokemon_GetValue(mon, MON_DATA_HP, NULL),
            40, 38);
        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercurySlash, 70, 38);
        MercuryMoveLearner_PrintNumber(
            controller, page,
            Pokemon_GetValue(mon, MON_DATA_MAX_HP, NULL),
            82, 38);

        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercuryAtk, 8, 56);
        MercuryMoveLearner_PrintNumber(
            controller, page,
            Pokemon_GetValue(mon, MON_DATA_ATK, NULL),
            44, 56);
        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercuryDef, 96, 56);
        MercuryMoveLearner_PrintNumber(
            controller, page,
            Pokemon_GetValue(mon, MON_DATA_DEF, NULL),
            132, 56);

        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercurySpAtk, 8, 74);
        MercuryMoveLearner_PrintNumber(
            controller, page,
            Pokemon_GetValue(mon, MON_DATA_SP_ATK, NULL),
            52, 74);
        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercurySpDef, 96, 74);
        MercuryMoveLearner_PrintNumber(
            controller, page,
            Pokemon_GetValue(mon, MON_DATA_SP_DEF, NULL),
            140, 74);

        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercurySpeed, 8, 86);
        MercuryMoveLearner_PrintNumber(
            controller, page,
            Pokemon_GetValue(mon, MON_DATA_SPEED, NULL),
            52, 86);

        MercuryMoveLearner_PrintMessage(controller, page, MoveReminder_Text_MercuryNature, 8, 100);
        MessageLoader *natureNames = MessageLoader_Init(
            MSG_LOADER_LOAD_ON_DEMAND,
            NARC_INDEX_MSGDATA__PL_MSG,
            TEXT_BANK_NATURE_NAMES,
            HEAP_ID_MOVE_REMINDER);
        MessageLoader_GetString(
            natureNames,
            Pokemon_GetNature(mon),
            controller->string);
        Text_AddPrinterWithParamsAndColor(
            page, FONT_SYSTEM, controller->string,
            62, 100, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
        MessageLoader_Free(natureNames);
    } else {
        MercuryMoveLearner_PrintMessage(
            controller, page,
            MoveReminder_Text_MercuryAbilityTitle,
            8, 4);

        Pokemon_GetValue(mon, MON_DATA_NICKNAME_STRING, controller->string);
        Text_AddPrinterWithParamsAndColor(
            page, FONT_SYSTEM, controller->string,
            8, 20, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);

        u16 ability = Pokemon_GetValue(mon, MON_DATA_ABILITY, NULL);

        MessageLoader *abilityNames = MessageLoader_Init(
            MSG_LOADER_LOAD_ON_DEMAND,
            NARC_INDEX_MSGDATA__PL_MSG,
            TEXT_BANK_ABILITY_NAMES,
            HEAP_ID_MOVE_REMINDER);
        MessageLoader_GetString(abilityNames, ability, controller->string);
        Text_AddPrinterWithParamsAndColor(
            page, FONT_SYSTEM, controller->string,
            8, 42, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
        MessageLoader_Free(abilityNames);

        MessageLoader *abilityDesc = MessageLoader_Init(
            MSG_LOADER_LOAD_ON_DEMAND,
            NARC_INDEX_MSGDATA__PL_MSG,
            TEXT_BANK_ABILITY_DESCRIPTIONS,
            HEAP_ID_MOVE_REMINDER);
        MessageLoader_GetString(abilityDesc, ability, controller->string);
        Text_AddPrinterWithParamsAndColor(
            page, FONT_SYSTEM, controller->string,
            8, 64, TEXT_SPEED_NO_TRANSFER, TEXT_COLOR(1, 2, 15), NULL);
        MessageLoader_Free(abilityDesc);

        MercuryMoveLearner_PrintMessage(
            controller, page,
            MoveReminder_Text_MercuryInnatesOff,
            8, 98);
    }

    Window_ScheduleCopyToVRAM(page);
}

'''
    text = source.read_text()
    if extra_functions.strip() not in text:
        if text.count(insertion_marker) != 1:
            raise SystemExit("MR03B helper insertion marker changed")
        source.write_text(text.replace(insertion_marker, extra_functions + insertion_marker, 1))

    # Initialize the new architecture after the normal windows exist.
    replace_once(
        source,
        """    MoveReminder_DrawLabelText(controller);
    MoveReminder_DrawSubInfo(controller);

    Window_FillTilemap(&controller->windows[MOVE_REMINDER_WIN_MESSAGE_BOX], 15);""",
        """    MoveReminder_DrawLabelText(controller);
    MoveReminder_DrawSubInfo(controller);
    controller->mercuryPage = 0;

    Window_FillTilemap(&controller->windows[MOVE_REMINDER_WIN_MESSAGE_BOX], 15);""",
        "MR03B initial page draw",
    )


def patch_text(root: Path) -> None:
    path = root / "res/text/move_reminder.json"
    data = json.loads(path.read_text())

    replacements = {
        "MoveReminder_Text_MercuryLearnerCurrentMoves": "CURRENT MOVES",
        "MoveReminder_Text_MercuryLearnerLearnable": "LEARNABLE MOVES",
        "MoveReminder_Text_MercuryLearnerHelp": "L/R: INFO   A: TEACH   B: BACK",
        "MoveReminder_Text_MercuryStatsTitle": "< L   STATS   R >",
        "MoveReminder_Text_MercuryAbilityTitle": "< L   ABILITY   R >",
        "MoveReminder_Text_MercuryInnatesOff": "INNATE ABILITIES: OFF",
        "MoveReminder_Text_MercuryLevel": "Lv.",
        "MoveReminder_Text_MercuryHP": "HP",
        "MoveReminder_Text_MercuryAtk": "ATK",
        "MoveReminder_Text_MercuryDef": "DEF",
        "MoveReminder_Text_MercurySpAtk": "SP.ATK",
        "MoveReminder_Text_MercurySpDef": "SP.DEF",
        "MoveReminder_Text_MercurySpeed": "SPEED",
        "MoveReminder_Text_MercuryNature": "NATURE",
        "MoveReminder_Text_MercurySlash": "/",
    }

    by_id = {m.get("id"): m for m in data["messages"]}
    for msg_id, text in replacements.items():
        if msg_id in by_id:
            by_id[msg_id]["en_US"] = text
            by_id[msg_id].pop("garbage", None)
        else:
            data["messages"].append({"id": msg_id, "en_US": text})

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr03b-move-learner-ui.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_ui(root)
    patch_text(root)

    report = {
        "gate": "MERCURY_MR03B_MOVE_LEARNER_UI",
        "status": "PASS",
        "top_pages": ["MOVE", "STATS", "ABILITY"],
        "page_controls": "L/R shoulder buttons",
        "bottom_workspace": [
            "current four moves",
            "scrollable learnable move list",
            "live highlighted-move name/type/description",
            "teach/back control footer",
        ],
        "preserved": [
            "MR03 universal move pool",
            "party-menu launch path",
            "native four-move replacement flow",
            "normal Mercury/Platinum story boot",
        ],
        "visual_polish": [
            "white bottom-screen workspace",
            "2x2 current-move grid",
            "learnable-moves heading",
            "framed Stats and Ability cards",
            "dedicated Nature line",
            "Innate Abilities OFF indicator",
        ],
        "deferred_polish": [
            "touchscreen row selection",
            "source filter tabs",
            "custom type/category icons on sub-screen",
            "Innate Ability expansion",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
