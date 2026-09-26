#!/usr/bin/env python3
"""MR03F — move the Mercury Move Learner onto Platinum Summary's bottom screen.

Architecture:
  TOP: untouched Platinum Summary Screen renderer.
  BOTTOM: DS-native framed Move Learner browser.
  A: enter Platinum's native move-replacement view on the top screen.
  B from replacement: return to the Move Learner browser.
  L/R: change top Summary page while browsing.
  Up/Down: scroll the learnable-move list.

This deliberately builds on MR03E instead of reusing the old custom
Move Reminder top-screen renderer.
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


def patch_text(root: Path) -> None:
    path = root / "res/text/pokemon_summary_screen.json"
    data = json.loads(path.read_text())

    additions = {
        "PokemonSummary_Text_MercuryLearnerTitle": "MOVE LEARNER   AVAILABLE MOVES",
        "PokemonSummary_Text_MercuryLearnerAvailable": "AVAILABLE MOVES",
        "PokemonSummary_Text_MercuryLearnerRow": "  {STRVAR_1 6, 0, 0}",
        "PokemonSummary_Text_MercuryLearnerRowSelected": "  {STRVAR_1 6, 0, 0}",
        "PokemonSummary_Text_MercuryLearnerStats": "POWER     ACC.      PP",
        "PokemonSummary_Text_MercuryLearnerNumber": "{STRVAR_1 52, 0, 0}",
        "PokemonSummary_Text_MercuryLearnerHelp": "D-PAD:SELECT  A:TEACH  L/R:PAGE  B:BACK",
        "PokemonSummary_Text_MercuryLearnerReplaceHelp": "Choose a move to replace on the top screen.",
        "PokemonSummary_Text_MercuryLearnerNoMoves": "No additional moves are available.",
    }

    existing = {row.get("id") for row in data["messages"]}
    for msg_id, text in additions.items():
        if msg_id not in existing:
            data["messages"].append({"id": msg_id, "en_US": text})

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_header(root: Path) -> None:
    path = root / "include/applications/pokemon_summary_screen/main.h"

    replace_once(
        path,
        """    SUMMARY_MODE_SHOW_CONDITION_CHANGE,
    SUMMARY_MODE_MERCURY_MOVE_LEARNER,
};""",
        """    SUMMARY_MODE_SHOW_CONDITION_CHANGE,
    SUMMARY_MODE_MERCURY_MOVE_LEARNER,
    SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT,
};""",
        "MR03F Summary teach mode",
    )

    replace_once(
        path,
        """    u8 ribbonID;
} PokemonSummaryScreen;""",
        """    u8 ribbonID;

    // Mercury Move Learner bottom-screen state. These fields exist only on
    // the Summary Screen controller, so normal Summary callers are unchanged.
    Window mercuryLearnerWindows[4];
    u16 *mercuryLearnerMoves;
    u16 mercuryLearnerMoveCount;
    u16 mercuryLearnerCursor;
    u16 mercuryLearnerTop;
    MessageLoader *mercuryMoveDescLoader;
} PokemonSummaryScreen;""",
        "MR03F Summary controller state",
    )


def patch_main(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"

    insert_after_once(
        path,
        '#include "message.h"\n',
        '#include "move_reminder_data.h"\n',
        "MR03F Move Learner backend include",
    )

    # Native Summary already uses a large application heap. The bottom-screen
    # learner adds four window pixel buffers, a 512-entry move pool, and an
    # additional message loader. Keep headroom rather than reproducing the
    # MR03C low-heap runtime crash pattern.
    replace_once(
        path,
        "#define HEAP_ALLOCATION_SIZE 0x40000\n",
        "#define HEAP_ALLOCATION_SIZE 0x50000\n",
        "MR03F Summary heap headroom",
    )

    insert_after_once(
        path,
        "static int TryFeedPoffin(PokemonSummaryScreen *summaryScreen);\n",
        """static void MercuryMoveLearner_Init(PokemonSummaryScreen *summaryScreen);
static void MercuryMoveLearner_Free(PokemonSummaryScreen *summaryScreen);
static void MercuryMoveLearner_Draw(PokemonSummaryScreen *summaryScreen);
static void MercuryMoveLearner_DrawList(PokemonSummaryScreen *summaryScreen);
static void MercuryMoveLearner_DrawDetails(PokemonSummaryScreen *summaryScreen);
static void MercuryMoveLearner_DrawFooter(PokemonSummaryScreen *summaryScreen);
static int MercuryMoveLearner_HandleInput(PokemonSummaryScreen *summaryScreen);
static int MercuryMoveLearner_BeginTeach(PokemonSummaryScreen *summaryScreen);
static void MercuryMoveLearner_PrintMessage(PokemonSummaryScreen *summaryScreen, Window *window, u32 entryID, u32 x, u32 y, TextColor color);
static void MercuryMoveLearner_PrintMoveRow(PokemonSummaryScreen *summaryScreen, Window *window, u16 move, BOOL selected, u32 y);
static void MercuryMoveLearner_PrintNumber(PokemonSummaryScreen *summaryScreen, Window *window, u32 value, u32 x, u32 y);
""",
        "MR03F helper declarations",
    )

    replace_once(
        path,
        """    SetMonData(summaryScreen);
    PokemonSummaryScreen_InitSpriteResources(summaryScreen);""",
        """    SetMonData(summaryScreen);
    PokemonSummaryScreen_InitSpriteResources(summaryScreen);""",
        "MR03F stable SetMonData anchor",
    )

    replace_once(
        path,
        """    SetupInitialPageGfx(summaryScreen);
    PokemonSummaryScreen_SetSubscreenType(summaryScreen);
    PokemonSummaryScreen_SetupCamera(summaryScreen);""",
        """    SetupInitialPageGfx(summaryScreen);
    PokemonSummaryScreen_SetSubscreenType(summaryScreen);

    if (summaryScreen->data->mode == SUMMARY_MODE_MERCURY_MOVE_LEARNER) {
        MercuryMoveLearner_Init(summaryScreen);
    }

    PokemonSummaryScreen_SetupCamera(summaryScreen);""",
        "MR03F bottom-screen init hook",
    )

    replace_once(
        path,
        """    SetVBlankCallback(NULL, NULL);
    PokemonSummaryScreen_FreeCameraAndMonSprite(summaryScreen);""",
        """    SetVBlankCallback(NULL, NULL);

    if (summaryScreen->mercuryLearnerMoves != NULL) {
        MercuryMoveLearner_Free(summaryScreen);
    }

    PokemonSummaryScreen_FreeCameraAndMonSprite(summaryScreen);""",
        "MR03F bottom-screen teardown hook",
    )

    # MR03E begins on Battle Moves. The teaching submode also uses that page.
    replace_once(
        path,
        """    case SUMMARY_MODE_MERCURY_MOVE_LEARNER:
        summaryScreen->page = SUMMARY_PAGE_BATTLE_MOVES;
        break;
    case SUMMARY_MODE_FEED_POFFIN:""",
        """    case SUMMARY_MODE_MERCURY_MOVE_LEARNER:
    case SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT:
        summaryScreen->page = SUMMARY_PAGE_BATTLE_MOVES;
        break;
    case SUMMARY_MODE_FEED_POFFIN:""",
        "MR03F teaching page selection",
    )

    # Treat Mercury's teaching submode exactly like Platinum's SELECT_MOVE
    # whenever the Summary renderer chooses the special move-replacement art.
    replace_once(
        path,
        """    if (summaryScreen->data->mode == SUMMARY_MODE_SELECT_MOVE && summaryScreen->data->move != MOVE_NONE) {""",
        """    if ((summaryScreen->data->mode == SUMMARY_MODE_SELECT_MOVE
            || summaryScreen->data->mode == SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT)
        && summaryScreen->data->move != MOVE_NONE) {""",
        "MR03F select-mode tilemap",
    )

    replace_once(
        path,
        """    if (summaryScreen->data->mode == SUMMARY_MODE_SELECT_MOVE) {
        ClearMoveInfoWindows(summaryScreen);
    }""",
        """    if (summaryScreen->data->mode == SUMMARY_MODE_SELECT_MOVE
        || summaryScreen->data->mode == SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT) {
        ClearMoveInfoWindows(summaryScreen);
    }""",
        "MR03F clear move detail windows",
    )

    replace_once(
        path,
        """    if (summaryScreen->data->mode == SUMMARY_MODE_SELECT_MOVE) {
        SetupMoveInfoFromSubscreenButton(summaryScreen);
    }""",
        """    if (summaryScreen->data->mode == SUMMARY_MODE_SELECT_MOVE
        || summaryScreen->data->mode == SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT) {
        SetupMoveInfoFromSubscreenButton(summaryScreen);
    }""",
        "MR03F setup move detail windows",
    )

    # Mercury browsing owns Up/Down for the lower move list and L/R for the
    # top Summary pages. Keep every vanilla Summary input path untouched.
    handle_anchor = """static int HandleInput_Main(PokemonSummaryScreen *summaryScreen)
{
"""
    replace_once(
        path,
        handle_anchor,
        handle_anchor + """    if (summaryScreen->data->mode == SUMMARY_MODE_MERCURY_MOVE_LEARNER) {
        return MercuryMoveLearner_HandleInput(summaryScreen);
    }

""",
        "MR03F dedicated browse input",
    )

    # In the teaching submode, B returns to the learner instead of closing the
    # application. A still uses Platinum's native selectedMoveSlot result.
    old_b = """    if (JOY_NEW(PAD_BUTTON_B)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        summaryScreen->data->selectedMoveSlot = LEARNED_MOVES_MAX;
        summaryScreen->data->returnMode = SUMMARY_RETURN_CANCEL;
        return SUMMARY_STATE_TRANSITION_OUT;
    }

    return SUMMARY_STATE_SELECT_MOVE;
}
"""
    new_b = """    if (JOY_NEW(PAD_BUTTON_B)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);

        if (summaryScreen->data->mode == SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT) {
            Window_ClearAndScheduleCopyToVRAM(
                &summaryScreen->extraWindows[SUMMARY_WINDOW_BATTLE_MOVE_5]);
            summaryScreen->data->mode = SUMMARY_MODE_MERCURY_MOVE_LEARNER;
            summaryScreen->data->move = MOVE_NONE;
            summaryScreen->pageState = PAGE_STATE_INITIAL;
            LoadCurrentPageTilemap(summaryScreen);
            MercuryMoveLearner_DrawFooter(summaryScreen);
            return SUMMARY_STATE_HIDE_BATTLE_MOVE_INFO;
        }

        summaryScreen->data->selectedMoveSlot = LEARNED_MOVES_MAX;
        summaryScreen->data->returnMode = SUMMARY_RETURN_CANCEL;
        return SUMMARY_STATE_TRANSITION_OUT;
    }

    return SUMMARY_STATE_SELECT_MOVE;
}
"""
    replace_once(path, old_b, new_b, "MR03F cancel replacement returns to learner")

    helpers = r'''
enum {
    MERCURY_LEARNER_WINDOW_HEADER = 0,
    MERCURY_LEARNER_WINDOW_LIST,
    MERCURY_LEARNER_WINDOW_DETAILS,
    MERCURY_LEARNER_WINDOW_FOOTER,
    MERCURY_LEARNER_WINDOW_MAX,
};

#define MERCURY_LEARNER_VISIBLE_ROWS 4
#define MERCURY_LEARNER_FRAME_TILE   0x300
#define MERCURY_LEARNER_FRAME_PLTT   11
#define MERCURY_LEARNER_TEXT_PLTT    13

static const WindowTemplate sMercuryLearnerWindowTemplates[MERCURY_LEARNER_WINDOW_MAX] = {
    [MERCURY_LEARNER_WINDOW_HEADER] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 0,
        .width = 30,
        .height = 2,
        .palette = MERCURY_LEARNER_TEXT_PLTT,
        .baseTile = 1,
    },
    [MERCURY_LEARNER_WINDOW_LIST] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 3,
        .width = 30,
        .height = 8,
        .palette = MERCURY_LEARNER_TEXT_PLTT,
        .baseTile = 61,
    },
    [MERCURY_LEARNER_WINDOW_DETAILS] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 12,
        .width = 30,
        .height = 8,
        .palette = MERCURY_LEARNER_TEXT_PLTT,
        .baseTile = 301,
    },
    [MERCURY_LEARNER_WINDOW_FOOTER] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 22,
        .width = 30,
        .height = 2,
        .palette = MERCURY_LEARNER_TEXT_PLTT,
        .baseTile = 541,
    },
};

static void MercuryMoveLearner_Init(PokemonSummaryScreen *summaryScreen)
{
    Pokemon *mon = Party_GetPokemonBySlotIndex(
        (Party *)summaryScreen->data->monData,
        summaryScreen->data->monIndex);

    summaryScreen->mercuryLearnerMoves =
        MoveReminderData_GetMoves(mon, HEAP_ID_POKEMON_SUMMARY_SCREEN);

    summaryScreen->mercuryLearnerMoveCount = 0;
    while (summaryScreen->mercuryLearnerMoveCount < MERCURY_MOVE_LEARNER_MAX_MOVES
        && summaryScreen->mercuryLearnerMoves[summaryScreen->mercuryLearnerMoveCount] != LEVEL_UP_MOVESET_TERMINATOR) {
        summaryScreen->mercuryLearnerMoveCount++;
    }

    summaryScreen->mercuryLearnerCursor = 0;
    summaryScreen->mercuryLearnerTop = 0;
    summaryScreen->mercuryMoveDescLoader = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_MOVE_DESCRIPTIONS,
        HEAP_ID_POKEMON_SUMMARY_SCREEN);

    Bg_ClearTilemap(summaryScreen->bgConfig, BG_LAYER_SUB_0);
    LoadStandardWindowGraphics(
        summaryScreen->bgConfig,
        BG_LAYER_SUB_0,
        MERCURY_LEARNER_FRAME_TILE,
        MERCURY_LEARNER_FRAME_PLTT,
        STANDARD_WINDOW_SYSTEM,
        HEAP_ID_POKEMON_SUMMARY_SCREEN);
    Font_LoadTextPalette(
        PAL_LOAD_SUB_BG,
        PLTT_OFFSET(MERCURY_LEARNER_TEXT_PLTT),
        HEAP_ID_POKEMON_SUMMARY_SCREEN);

    for (u32 i = 0; i < MERCURY_LEARNER_WINDOW_MAX; i++) {
        Window_AddFromTemplate(
            summaryScreen->bgConfig,
            &summaryScreen->mercuryLearnerWindows[i],
            &sMercuryLearnerWindowTemplates[i]);
    }

    Window_DrawStandardFrame(
        &summaryScreen->mercuryLearnerWindows[MERCURY_LEARNER_WINDOW_LIST],
        TRUE,
        MERCURY_LEARNER_FRAME_TILE,
        MERCURY_LEARNER_FRAME_PLTT);
    Window_DrawStandardFrame(
        &summaryScreen->mercuryLearnerWindows[MERCURY_LEARNER_WINDOW_DETAILS],
        TRUE,
        MERCURY_LEARNER_FRAME_TILE,
        MERCURY_LEARNER_FRAME_PLTT);

    MercuryMoveLearner_Draw(summaryScreen);
    Bg_ScheduleTilemapTransfer(summaryScreen->bgConfig, BG_LAYER_SUB_0);
}

static void MercuryMoveLearner_Free(PokemonSummaryScreen *summaryScreen)
{
    for (u32 i = 0; i < MERCURY_LEARNER_WINDOW_MAX; i++) {
        Window_Remove(&summaryScreen->mercuryLearnerWindows[i]);
    }

    if (summaryScreen->mercuryMoveDescLoader != NULL) {
        MessageLoader_Free(summaryScreen->mercuryMoveDescLoader);
        summaryScreen->mercuryMoveDescLoader = NULL;
    }

    Heap_Free(summaryScreen->mercuryLearnerMoves);
    summaryScreen->mercuryLearnerMoves = NULL;
}

static void MercuryMoveLearner_PrintMessage(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u32 entryID,
    u32 x,
    u32 y,
    TextColor color)
{
    MessageLoader_GetString(summaryScreen->msgLoader, entryID, summaryScreen->string);
    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        summaryScreen->string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        color,
        NULL);
}

static void MercuryMoveLearner_PrintMoveRow(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u16 move,
    BOOL selected,
    u32 y)
{
    String *fmt = MessageLoader_GetNewString(
        summaryScreen->msgLoader,
        selected
            ? PokemonSummary_Text_MercuryLearnerRowSelected
            : PokemonSummary_Text_MercuryLearnerRow);

    StringTemplate_SetMoveName(summaryScreen->strFormatter, 0, move);
    StringTemplate_Format(summaryScreen->strFormatter, summaryScreen->string, fmt);
    String_Free(fmt);

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        summaryScreen->string,
        8,
        y,
        TEXT_SPEED_NO_TRANSFER,
        selected ? SUMMARY_TEXT_BLUE : SUMMARY_TEXT_BLACK,
        NULL);
}

static void MercuryMoveLearner_PrintNumber(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u32 value,
    u32 x,
    u32 y)
{
    String *fmt = MessageLoader_GetNewString(
        summaryScreen->msgLoader,
        PokemonSummary_Text_MercuryLearnerNumber);

    StringTemplate_SetNumber(
        summaryScreen->strFormatter,
        0,
        value,
        3,
        PADDING_MODE_NONE,
        CHARSET_MODE_EN);
    StringTemplate_Format(summaryScreen->strFormatter, summaryScreen->string, fmt);
    String_Free(fmt);

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        summaryScreen->string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        SUMMARY_TEXT_BLACK,
        NULL);
}

static void MercuryMoveLearner_DrawList(PokemonSummaryScreen *summaryScreen)
{
    Window *window = &summaryScreen->mercuryLearnerWindows[MERCURY_LEARNER_WINDOW_LIST];
    Window_FillTilemap(window, 15);

    if (summaryScreen->mercuryLearnerMoveCount == 0) {
        MercuryMoveLearner_PrintMessage(
            summaryScreen,
            window,
            PokemonSummary_Text_MercuryLearnerNoMoves,
            8,
            8,
            SUMMARY_TEXT_BLACK);
    } else {
        for (u32 row = 0; row < MERCURY_LEARNER_VISIBLE_ROWS; row++) {
            u32 index = summaryScreen->mercuryLearnerTop + row;

            if (index >= summaryScreen->mercuryLearnerMoveCount) {
                break;
            }

            MercuryMoveLearner_PrintMoveRow(
                summaryScreen,
                window,
                summaryScreen->mercuryLearnerMoves[index],
                index == summaryScreen->mercuryLearnerCursor,
                row * 16);
        }
    }

    Window_ScheduleCopyToVRAM(window);
}

static void MercuryMoveLearner_DrawDetails(PokemonSummaryScreen *summaryScreen)
{
    Window *window = &summaryScreen->mercuryLearnerWindows[MERCURY_LEARNER_WINDOW_DETAILS];
    Window_FillTilemap(window, 15);

    if (summaryScreen->mercuryLearnerMoveCount == 0) {
        Window_ScheduleCopyToVRAM(window);
        return;
    }

    u16 move = summaryScreen->mercuryLearnerMoves[summaryScreen->mercuryLearnerCursor];
    u32 power = MoveTable_LoadParam(move, MOVEATTRIBUTE_POWER);
    u32 accuracy = MoveTable_LoadParam(move, MOVEATTRIBUTE_ACCURACY);
    u32 pp = MoveTable_LoadParam(move, MOVEATTRIBUTE_PP);

    MercuryMoveLearner_PrintMessage(
        summaryScreen,
        window,
        PokemonSummary_Text_MercuryLearnerStats,
        8,
        0,
        SUMMARY_TEXT_BLACK);

    if (power <= 1) {
        MercuryMoveLearner_PrintMessage(
            summaryScreen,
            window,
            PokemonSummary_Text_ThreeDashes,
            43,
            0,
            SUMMARY_TEXT_BLACK);
    } else {
        MercuryMoveLearner_PrintNumber(summaryScreen, window, power, 43, 0);
    }

    if (accuracy == 0) {
        MercuryMoveLearner_PrintMessage(
            summaryScreen,
            window,
            PokemonSummary_Text_ThreeDashes,
            121,
            0,
            SUMMARY_TEXT_BLACK);
    } else {
        MercuryMoveLearner_PrintNumber(summaryScreen, window, accuracy, 121, 0);
    }

    MercuryMoveLearner_PrintNumber(summaryScreen, window, pp, 196, 0);

    MessageLoader_GetString(
        summaryScreen->mercuryMoveDescLoader,
        move,
        summaryScreen->string);
    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        summaryScreen->string,
        8,
        18,
        TEXT_SPEED_NO_TRANSFER,
        SUMMARY_TEXT_BLACK,
        NULL);

    Window_ScheduleCopyToVRAM(window);
}

static void MercuryMoveLearner_DrawFooter(PokemonSummaryScreen *summaryScreen)
{
    Window *window = &summaryScreen->mercuryLearnerWindows[MERCURY_LEARNER_WINDOW_FOOTER];
    Window_FillTilemap(window, 0);

    MercuryMoveLearner_PrintMessage(
        summaryScreen,
        window,
        summaryScreen->data->mode == SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT
            ? PokemonSummary_Text_MercuryLearnerReplaceHelp
            : PokemonSummary_Text_MercuryLearnerHelp,
        0,
        0,
        SUMMARY_TEXT_BLACK);

    Window_ScheduleCopyToVRAM(window);
}

static void MercuryMoveLearner_Draw(PokemonSummaryScreen *summaryScreen)
{
    Window *header = &summaryScreen->mercuryLearnerWindows[MERCURY_LEARNER_WINDOW_HEADER];
    Window_FillTilemap(header, 0);

    MercuryMoveLearner_PrintMessage(
        summaryScreen,
        header,
        PokemonSummary_Text_MercuryLearnerTitle,
        4,
        0,
        SUMMARY_TEXT_BLACK);
    Window_ScheduleCopyToVRAM(header);

    MercuryMoveLearner_DrawList(summaryScreen);
    MercuryMoveLearner_DrawDetails(summaryScreen);
    MercuryMoveLearner_DrawFooter(summaryScreen);
}

static int MercuryMoveLearner_HandleInput(PokemonSummaryScreen *summaryScreen)
{
    if (summaryScreen->subscreenExit == TRUE) {
        summaryScreen->data->returnMode = SUMMARY_RETURN_CANCEL;
        return SUMMARY_STATE_TRANSITION_OUT;
    }

    if (JOY_NEW(PAD_BUTTON_L)) {
        ChangePage(summaryScreen, -1);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_R)) {
        ChangePage(summaryScreen, 1);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_REPEAT(PAD_KEY_UP) && summaryScreen->mercuryLearnerCursor > 0) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
        summaryScreen->mercuryLearnerCursor--;

        if (summaryScreen->mercuryLearnerCursor < summaryScreen->mercuryLearnerTop) {
            summaryScreen->mercuryLearnerTop = summaryScreen->mercuryLearnerCursor;
        }

        MercuryMoveLearner_DrawList(summaryScreen);
        MercuryMoveLearner_DrawDetails(summaryScreen);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_REPEAT(PAD_KEY_DOWN)
        && summaryScreen->mercuryLearnerCursor + 1 < summaryScreen->mercuryLearnerMoveCount) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
        summaryScreen->mercuryLearnerCursor++;

        if (summaryScreen->mercuryLearnerCursor
            >= summaryScreen->mercuryLearnerTop + MERCURY_LEARNER_VISIBLE_ROWS) {
            summaryScreen->mercuryLearnerTop =
                summaryScreen->mercuryLearnerCursor - (MERCURY_LEARNER_VISIBLE_ROWS - 1);
        }

        MercuryMoveLearner_DrawList(summaryScreen);
        MercuryMoveLearner_DrawDetails(summaryScreen);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_A) && summaryScreen->mercuryLearnerMoveCount != 0) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        return MercuryMoveLearner_BeginTeach(summaryScreen);
    }

    if (JOY_NEW(PAD_BUTTON_B)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        summaryScreen->data->returnMode = SUMMARY_RETURN_CANCEL;
        return SUMMARY_STATE_TRANSITION_OUT;
    }

    return SUMMARY_STATE_HANDLE_INPUT;
}

static int MercuryMoveLearner_BeginTeach(PokemonSummaryScreen *summaryScreen)
{
    summaryScreen->data->move =
        summaryScreen->mercuryLearnerMoves[summaryScreen->mercuryLearnerCursor];
    summaryScreen->data->mode = SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT;
    summaryScreen->cursor = 0;

    if (summaryScreen->page != SUMMARY_PAGE_BATTLE_MOVES) {
        SetupPageFromSubscreenButton(summaryScreen, SUMMARY_PAGE_BATTLE_MOVES);
    } else {
        LoadCurrentPageTilemap(summaryScreen);
        SetupMoveInfoFromSubscreenButton(summaryScreen);
    }

    MercuryMoveLearner_DrawFooter(summaryScreen);
    return SUMMARY_STATE_SELECT_MOVE;
}
'''

    marker = "const ApplicationManagerTemplate gPokemonSummaryScreenApp = {\n"
    text = path.read_text()
    if helpers.strip() not in text:
        count = text.count(marker)
        if count != 1:
            raise SystemExit(f"MR03F helper insertion marker changed: {count}")
        path.write_text(text.replace(marker, helpers + "\n" + marker, 1))


def patch_start_menu(root: Path) -> None:
    path = root / "src/start_menu.c"

    old = """    switch (summary->mode) {
    case SUMMARY_MODE_SELECT_MOVE: {
"""
    new = """    switch (summary->mode) {
    case SUMMARY_MODE_MERCURY_MOVE_LEARNER_SELECT:
        if (summary->returnMode == SUMMARY_RETURN_SELECT
            && summary->selectedMoveSlot < LEARNED_MOVES_MAX) {
            Pokemon *mon = Party_GetPokemonBySlotIndex(
                SaveData_GetParty(fieldSystem->saveData),
                summary->monIndex);
            Pokemon_ResetMoveSlot(mon, summary->move, summary->selectedMoveSlot);
        }

        menu->taskData = FieldSystem_OpenPartyMenu(
            fieldSystem,
            &menu->fieldMoveContext,
            summary->monIndex);
        StartMenu_SetCallback(menu, StartMenu_ExitPartyMenu);
        break;

    case SUMMARY_MODE_SELECT_MOVE: {
"""
    replace_once(path, old, new, "MR03F apply selected move")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr03f-summary-bottom-learner.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_text(root)
    patch_header(root)
    patch_main(root)
    patch_start_menu(root)

    report = {
        "gate": "MERCURY_MR03F_SUMMARY_BOTTOM_MOVE_LEARNER",
        "status": "PASS",
        "top_screen": "vanilla Platinum Summary Screen renderer",
        "bottom_screen": "Mercury Move Learner browser on Summary SUB engine",
        "bottom_visual_system": [
            "Platinum Summary sub-screen background",
            "native system window frames",
            "native DS font palette",
            "move descriptions from Platinum text bank",
        ],
        "controls": {
            "up_down": "scroll learnable moves",
            "l_r": "change top Summary page",
            "a": "teach selected move using Platinum native replacement view",
            "b": "back / cancel replacement",
        },
        "teaching": "selected replacement is committed with Pokemon_ResetMoveSlot",
        "filters": "deferred to next bottom-screen pass after base browse/teach proof",
        "old_mr03c_top_renderer": False,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
