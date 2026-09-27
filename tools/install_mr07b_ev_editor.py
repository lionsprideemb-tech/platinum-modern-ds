#!/usr/bin/env python3
"""MR07B — production Mercury EV editor inside the Platinum Summary screen.

Applied after MR07A.

Player flow:
- Skills -> X enters field-selection mode.
- Highlight any of the six stats -> A opens the EV editor on the lower screen.
- D-pad Up/Down or touch selects a stat.
- Left/Right changes by 4 EV.
- L sets the selected stat to 0.
- R sets the selected stat to the highest legal value.
- Y clears all EVs.
- B returns to field-selection mode; X exits editing entirely.

The editor writes the real Pokemon/BoxPokemon EV fields, enforces Mercury's
modern 252-per-stat / 510-total rule, recalculates party stats immediately,
and keeps Platinum's normal lower Summary wheel intact whenever the editor is
closed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1))


def replace_span(path: Path, start_marker: str, end_marker: str, replacement: str, label: str) -> None:
    text = path.read_text()
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker missing in {path}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker missing in {path}")
    path.write_text(text[:start] + replacement + text[end:])


def patch_text(root: Path) -> None:
    path = root / "res/text/pokemon_summary_screen.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    additions = {
        "PokemonSummary_Text_MercuryEvTraining": "EV TRAINING",
        "PokemonSummary_Text_MercuryEvValue": "{STRVAR_1 52, 0, 0}/252",
        "PokemonSummary_Text_MercuryEvTotal": "TOTAL {STRVAR_1 52, 0, 0}/510",
        "PokemonSummary_Text_MercuryEvMinus": "-4",
        "PokemonSummary_Text_MercuryEvPlus": "+4",
        "PokemonSummary_Text_MercuryEvZero": "0",
        "PokemonSummary_Text_MercuryEvMax": "MAX",
        "PokemonSummary_Text_MercuryEvClear": "Y CLEAR ALL",
        "PokemonSummary_Text_MercuryEvBack": "B BACK",
    }

    existing = {row.get("id") for row in data["messages"]}
    for msg_id, value in additions.items():
        if msg_id not in existing:
            data["messages"].append({"id": msg_id, "en_US": value})

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_header(root: Path) -> None:
    path = root / "include/applications/pokemon_summary_screen/main.h"
    replace_once(
        path,
        """    u8 mercurySkillsEditMode;
    u8 mercurySkillsCursor;
} PokemonSummaryScreen;""",
        """    u8 mercurySkillsEditMode;
    u8 mercurySkillsCursor;

    // MR07B temporary lower-screen editor. The normal Platinum radial wheel is
    // restored as soon as the editor closes.
    u8 mercurySkillsEditorMode;
    u8 mercurySkillsEditorWindowActive;
    Window mercurySkillsEditorWindow;
} PokemonSummaryScreen;""",
        "MR07B editor state",
    )


def patch_main(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"

    insert_after_once(
        path,
        '#include "touch_pad.h"\n',
        '#include "touch_screen.h"\n',
        "MR07B touch-screen include",
    )

    insert_after_once(
        path,
        """enum SummaryPageState {
    PAGE_STATE_INITIAL = 0,
    PAGE_STATE_SCROLLING,
    PAGE_STATE_SCROLL_FINISHED,
};
""",
        """
enum MercurySkillsEditorMode {
    MERCURY_SKILLS_EDITOR_NONE = 0,
    MERCURY_SKILLS_EDITOR_EV,
};

enum MercuryEvTouchTarget {
    MERCURY_EV_TOUCH_HP = 0,
    MERCURY_EV_TOUCH_ATK,
    MERCURY_EV_TOUCH_DEF,
    MERCURY_EV_TOUCH_SPATK,
    MERCURY_EV_TOUCH_SPDEF,
    MERCURY_EV_TOUCH_SPEED,
    MERCURY_EV_TOUCH_MINUS,
    MERCURY_EV_TOUCH_PLUS,
    MERCURY_EV_TOUCH_ZERO,
    MERCURY_EV_TOUCH_MAX,
    MERCURY_EV_TOUCH_CLEAR,
    MERCURY_EV_TOUCH_BACK,
};

static const TouchScreenRect sMercuryEvTouchRects[] = {
    { 24, 39,   0, 255 },
    { 40, 55,   0, 255 },
    { 56, 71,   0, 255 },
    { 72, 87,   0, 255 },
    { 88, 103,  0, 255 },
    { 104, 119, 0, 255 },
    { 140, 166, 0,  63 },
    { 140, 166, 64, 127 },
    { 140, 166, 128, 191 },
    { 140, 166, 192, 255 },
    { 168, 191, 0,  127 },
    { 168, 191, 128, 255 },
    { 255, 0, 0, 0 },
};
""",
        "MR07B editor enums/touch zones",
    )

    prototype_anchor = "static int HandleInput_Main(PokemonSummaryScreen *summaryScreen);\n"
    prototypes = """static void MercurySkills_OpenEvEditor(PokemonSummaryScreen *summaryScreen);
static void MercurySkills_CloseEvEditor(PokemonSummaryScreen *summaryScreen);
static void MercurySkills_DrawEvEditor(PokemonSummaryScreen *summaryScreen);
static void MercurySkills_ApplyEvDelta(PokemonSummaryScreen *summaryScreen, s16 delta);
static void MercurySkills_SetSelectedEv(PokemonSummaryScreen *summaryScreen, u8 value);
static void MercurySkills_ClearAllEvs(PokemonSummaryScreen *summaryScreen);
static void MercurySkills_RefreshAfterEvWrite(PokemonSummaryScreen *summaryScreen);
static int MercurySkills_HandleEvEditorInput(PokemonSummaryScreen *summaryScreen);
"""
    insert_after_once(path, prototype_anchor, prototypes, "MR07B editor prototypes")

    function_marker = "static int HandleInput_Main(PokemonSummaryScreen *summaryScreen)\n{"
    idx = path.read_text().find(function_marker)
    if idx < 0:
        raise SystemExit("MR07B HandleInput_Main definition missing")

    helpers = r'''static const u32 sMercuryEvDataParams[6] = {
    MON_DATA_HP_EV,
    MON_DATA_ATK_EV,
    MON_DATA_DEF_EV,
    MON_DATA_SPATK_EV,
    MON_DATA_SPDEF_EV,
    MON_DATA_SPEED_EV,
};

static const u32 sMercuryEvLabelText[6] = {
    PokemonSummary_Text_LabelHp,
    PokemonSummary_Text_LabelAttack,
    PokemonSummary_Text_LabelDefense,
    PokemonSummary_Text_LabelSpAttack,
    PokemonSummary_Text_LabelSpDefense,
    PokemonSummary_Text_LabelSpeed,
};

static void MercurySkills_PrintEditorMessage(
    PokemonSummaryScreen *summaryScreen,
    u32 entryID,
    u32 x,
    u32 y,
    TextColor color)
{
    MessageLoader_GetString(summaryScreen->msgLoader, entryID, summaryScreen->string);
    Text_AddPrinterWithParamsAndColor(
        &summaryScreen->mercurySkillsEditorWindow,
        FONT_SYSTEM,
        summaryScreen->string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        color,
        NULL);
}

static void MercurySkills_PrintEditorNumber(
    PokemonSummaryScreen *summaryScreen,
    u32 entryID,
    u32 value,
    u32 x,
    u32 y,
    TextColor color)
{
    String *fmt = MessageLoader_GetNewString(summaryScreen->msgLoader, entryID);
    StringTemplate_SetNumber(
        summaryScreen->strFormatter,
        0,
        value,
        3,
        PADDING_MODE_NONE,
        CHARSET_MODE_EN);
    StringTemplate_Format(
        summaryScreen->strFormatter,
        summaryScreen->string,
        fmt);
    String_Free(fmt);

    Text_AddPrinterWithParamsAndColor(
        &summaryScreen->mercurySkillsEditorWindow,
        FONT_SYSTEM,
        summaryScreen->string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        color,
        NULL);
}

static void MercurySkills_OpenEvEditor(PokemonSummaryScreen *summaryScreen)
{
    if (summaryScreen->mercurySkillsEditorWindowActive) {
        return;
    }

    summaryScreen->mercurySkillsEditorMode = MERCURY_SKILLS_EDITOR_EV;
    summaryScreen->subscreenType = SUMMARY_SUBSCREEN_TYPE_NO_BUTTONS;

    Window_Init(&summaryScreen->mercurySkillsEditorWindow);
    Window_Add(
        summaryScreen->bgConfig,
        &summaryScreen->mercurySkillsEditorWindow,
        BG_LAYER_SUB_0,
        0,
        0,
        32,
        24,
        15,
        0x20);
    summaryScreen->mercurySkillsEditorWindowActive = TRUE;

    MercurySkills_DrawEvEditor(summaryScreen);
}

static void MercurySkills_CloseEvEditor(PokemonSummaryScreen *summaryScreen)
{
    if (!summaryScreen->mercurySkillsEditorWindowActive) {
        summaryScreen->mercurySkillsEditorMode = MERCURY_SKILLS_EDITOR_NONE;
        return;
    }

    Window_Remove(&summaryScreen->mercurySkillsEditorWindow);
    summaryScreen->mercurySkillsEditorWindowActive = FALSE;
    summaryScreen->mercurySkillsEditorMode = MERCURY_SKILLS_EDITOR_NONE;

    // The full-screen editor temporarily reuses SUB_0 character memory, so
    // reload Platinum's real radial-button graphics before restoring the wheel.
    Graphics_LoadTilesToBgLayer(
        NARC_INDEX_GRAPHIC__PL_PST_GRA,
        sub_buttons_NCGR,
        summaryScreen->bgConfig,
        BG_LAYER_SUB_0,
        0,
        0,
        FALSE,
        HEAP_ID_POKEMON_SUMMARY_SCREEN);
    Bg_ClearTilemap(summaryScreen->bgConfig, BG_LAYER_SUB_0);
    PokemonSummaryScreen_SetSubscreenType(summaryScreen);
}

static void MercurySkills_DrawEvEditor(PokemonSummaryScreen *summaryScreen)
{
    Window *window = &summaryScreen->mercurySkillsEditorWindow;
    Window_FillTilemap(window, 15);

    // Header.
    Window_FillRectWithColor(window, 4, 0, 0, 256, 22);
    MercurySkills_PrintEditorMessage(
        summaryScreen,
        PokemonSummary_Text_MercuryEvTraining,
        8,
        4,
        SUMMARY_TEXT_WHITE);

    // Six real EV rows.
    for (u32 i = 0; i < 6; i++) {
        u32 y = 24 + i * 16;
        BOOL selected = summaryScreen->mercurySkillsCursor == i;

        if (selected) {
            Window_FillRectWithColor(window, 4, 6, y, 244, 15);
        }

        TextColor color = selected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLACK;
        MercurySkills_PrintEditorMessage(
            summaryScreen,
            sMercuryEvLabelText[i],
            12,
            y + 1,
            color);
        MercurySkills_PrintEditorNumber(
            summaryScreen,
            PokemonSummary_Text_MercuryEvValue,
            summaryScreen->monData.evs[i],
            176,
            y + 1,
            color);
    }

    // Total budget.
    MercurySkills_PrintEditorNumber(
        summaryScreen,
        PokemonSummary_Text_MercuryEvTotal,
        summaryScreen->monData.evTotal,
        74,
        122,
        SUMMARY_TEXT_BLACK);

    // Touch/button controls.
    Window_FillRectWithColor(window, 4, 0, 140, 63, 27);
    Window_FillRectWithColor(window, 4, 64, 140, 63, 27);
    Window_FillRectWithColor(window, 4, 128, 140, 63, 27);
    Window_FillRectWithColor(window, 4, 192, 140, 64, 27);
    MercurySkills_PrintEditorMessage(summaryScreen, PokemonSummary_Text_MercuryEvMinus, 24, 146, SUMMARY_TEXT_WHITE);
    MercurySkills_PrintEditorMessage(summaryScreen, PokemonSummary_Text_MercuryEvPlus, 88, 146, SUMMARY_TEXT_WHITE);
    MercurySkills_PrintEditorMessage(summaryScreen, PokemonSummary_Text_MercuryEvZero, 154, 146, SUMMARY_TEXT_WHITE);
    MercurySkills_PrintEditorMessage(summaryScreen, PokemonSummary_Text_MercuryEvMax, 211, 146, SUMMARY_TEXT_WHITE);

    Window_FillRectWithColor(window, 4, 0, 168, 127, 24);
    Window_FillRectWithColor(window, 4, 128, 168, 128, 24);
    MercurySkills_PrintEditorMessage(summaryScreen, PokemonSummary_Text_MercuryEvClear, 24, 174, SUMMARY_TEXT_WHITE);
    MercurySkills_PrintEditorMessage(summaryScreen, PokemonSummary_Text_MercuryEvBack, 170, 174, SUMMARY_TEXT_WHITE);

    Window_CopyToVRAM(window);
}

static void MercurySkills_RefreshAfterEvWrite(PokemonSummaryScreen *summaryScreen)
{
    SetMonData(summaryScreen);
    DrawHealthBar(summaryScreen);
    PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
    MercurySkills_DrawEvEditor(summaryScreen);
}

static void MercurySkills_SetSelectedEv(PokemonSummaryScreen *summaryScreen, u8 value)
{
    u8 stat = summaryScreen->mercurySkillsCursor;
    if (stat >= 6) {
        return;
    }

    u32 current = summaryScreen->monData.evs[stat];
    u32 totalWithoutCurrent = summaryScreen->monData.evTotal - current;
    u32 legalMax = 510 - totalWithoutCurrent;

    if (legalMax > 252) {
        legalMax = 252;
    }
    if (value > legalMax) {
        value = legalMax;
    }

    void *monData = PokemonSummaryScreen_MonData(summaryScreen);

    if (summaryScreen->data->dataType == SUMMARY_DATA_BOX_MON) {
        BoxPokemon_SetValue(
            (BoxPokemon *)monData,
            sMercuryEvDataParams[stat],
            &value);
    } else {
        Pokemon *mon = (Pokemon *)monData;
        Pokemon_SetValue(mon, sMercuryEvDataParams[stat], &value);
        Pokemon_CalcLevelAndStats(mon);
    }

    MercurySkills_RefreshAfterEvWrite(summaryScreen);
}

static void MercurySkills_ApplyEvDelta(PokemonSummaryScreen *summaryScreen, s16 delta)
{
    u8 stat = summaryScreen->mercurySkillsCursor;
    if (stat >= 6) {
        return;
    }

    s32 value = summaryScreen->monData.evs[stat];

    if (delta < 0) {
        value += delta;
        if (value < 0) {
            value = 0;
        }
    } else {
        s32 remaining = 510 - summaryScreen->monData.evTotal;
        if (remaining <= 0 || value >= 252) {
            return;
        }

        s32 allowed = delta;
        if (allowed > remaining) {
            allowed = remaining;
        }
        if (value + allowed > 252) {
            allowed = 252 - value;
        }
        value += allowed;
    }

    MercurySkills_SetSelectedEv(summaryScreen, (u8)value);
}

static void MercurySkills_ClearAllEvs(PokemonSummaryScreen *summaryScreen)
{
    void *monData = PokemonSummaryScreen_MonData(summaryScreen);
    u8 zero = 0;

    if (summaryScreen->data->dataType == SUMMARY_DATA_BOX_MON) {
        BoxPokemon *boxMon = (BoxPokemon *)monData;
        for (u32 i = 0; i < 6; i++) {
            BoxPokemon_SetValue(boxMon, sMercuryEvDataParams[i], &zero);
        }
    } else {
        Pokemon *mon = (Pokemon *)monData;
        for (u32 i = 0; i < 6; i++) {
            Pokemon_SetValue(mon, sMercuryEvDataParams[i], &zero);
        }
        Pokemon_CalcLevelAndStats(mon);
    }

    MercurySkills_RefreshAfterEvWrite(summaryScreen);
}

static int MercurySkills_HandleEvEditorInput(PokemonSummaryScreen *summaryScreen)
{
    if (JOY_NEW(PAD_BUTTON_X)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        MercurySkills_CloseEvEditor(summaryScreen);
        summaryScreen->mercurySkillsEditMode = FALSE;
        PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_B)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        MercurySkills_CloseEvEditor(summaryScreen);
        PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_REPEAT(PAD_KEY_UP)) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
        if (summaryScreen->mercurySkillsCursor == 0) {
            summaryScreen->mercurySkillsCursor = 5;
        } else {
            summaryScreen->mercurySkillsCursor--;
        }
        PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
        MercurySkills_DrawEvEditor(summaryScreen);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_REPEAT(PAD_KEY_DOWN)) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
        summaryScreen->mercurySkillsCursor++;
        if (summaryScreen->mercurySkillsCursor > 5) {
            summaryScreen->mercurySkillsCursor = 0;
        }
        PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
        MercurySkills_DrawEvEditor(summaryScreen);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_REPEAT(PAD_KEY_LEFT)) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
        MercurySkills_ApplyEvDelta(summaryScreen, -4);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_REPEAT(PAD_KEY_RIGHT)) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
        MercurySkills_ApplyEvDelta(summaryScreen, 4);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_L)) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
        MercurySkills_SetSelectedEv(summaryScreen, 0);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_R)) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
        MercurySkills_SetSelectedEv(summaryScreen, 252);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (JOY_NEW(PAD_BUTTON_Y)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        MercurySkills_ClearAllEvs(summaryScreen);
        return SUMMARY_STATE_HANDLE_INPUT;
    }

    int touch = TouchScreen_CheckRectanglePressed(sMercuryEvTouchRects);
    if (touch != TOUCHSCREEN_INPUT_NONE) {
        Sound_PlayEffect(SE_CONFIRM_sseq_3);

        if (touch >= MERCURY_EV_TOUCH_HP && touch <= MERCURY_EV_TOUCH_SPEED) {
            summaryScreen->mercurySkillsCursor = touch;
            PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
            MercurySkills_DrawEvEditor(summaryScreen);
        } else if (touch == MERCURY_EV_TOUCH_MINUS) {
            MercurySkills_ApplyEvDelta(summaryScreen, -4);
        } else if (touch == MERCURY_EV_TOUCH_PLUS) {
            MercurySkills_ApplyEvDelta(summaryScreen, 4);
        } else if (touch == MERCURY_EV_TOUCH_ZERO) {
            MercurySkills_SetSelectedEv(summaryScreen, 0);
        } else if (touch == MERCURY_EV_TOUCH_MAX) {
            MercurySkills_SetSelectedEv(summaryScreen, 252);
        } else if (touch == MERCURY_EV_TOUCH_CLEAR) {
            MercurySkills_ClearAllEvs(summaryScreen);
        } else if (touch == MERCURY_EV_TOUCH_BACK) {
            MercurySkills_CloseEvEditor(summaryScreen);
            PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
        }

        return SUMMARY_STATE_HANDLE_INPUT;
    }

    return SUMMARY_STATE_HANDLE_INPUT;
}

'''
    text = path.read_text()
    path.write_text(text[:idx] + helpers + text[idx:], encoding="utf-8")

    start_marker = "    // MR07A: X owns edit-selection only on the normal Skills page."
    end_marker = "    if (summaryScreen->subscreenExit == TRUE) {"
    replacement = r'''    // MR07B: MR07A's field-selection mode now opens the production EV
    // editor for any highlighted stat. Nature and primary Ability remain the
    // next editor gates; they are not faked here.
    if (summaryScreen->page == SUMMARY_PAGE_SKILLS
        && (summaryScreen->data->mode == SUMMARY_MODE_NORMAL
            || summaryScreen->data->mode == SUMMARY_MODE_LOCK_MOVES)) {
        if (summaryScreen->mercurySkillsEditorMode == MERCURY_SKILLS_EDITOR_EV) {
            return MercurySkills_HandleEvEditorInput(summaryScreen);
        }

        if (JOY_NEW(PAD_BUTTON_X)) {
            Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
            summaryScreen->mercurySkillsEditMode =
                !summaryScreen->mercurySkillsEditMode;
            if (summaryScreen->mercurySkillsEditMode) {
                summaryScreen->mercurySkillsCursor = 7; // primary Ability
            }
            PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (summaryScreen->mercurySkillsEditMode) {
            if (JOY_NEW(PAD_BUTTON_B)) {
                Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
                summaryScreen->mercurySkillsEditMode = FALSE;
                PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
                return SUMMARY_STATE_HANDLE_INPUT;
            }

            if (JOY_NEW(PAD_BUTTON_A)
                && summaryScreen->mercurySkillsCursor < 6) {
                Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
                MercurySkills_OpenEvEditor(summaryScreen);
                return SUMMARY_STATE_HANDLE_INPUT;
            }

            if (JOY_REPEAT(PAD_KEY_UP)) {
                Sound_PlayEffect(SE_CONFIRM_sseq_3);
                if (summaryScreen->mercurySkillsCursor == 0) {
                    summaryScreen->mercurySkillsCursor = 7;
                } else {
                    summaryScreen->mercurySkillsCursor--;
                }
                PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
                return SUMMARY_STATE_HANDLE_INPUT;
            }

            if (JOY_REPEAT(PAD_KEY_DOWN)) {
                Sound_PlayEffect(SE_CONFIRM_sseq_3);
                summaryScreen->mercurySkillsCursor++;
                if (summaryScreen->mercurySkillsCursor > 7) {
                    summaryScreen->mercurySkillsCursor = 0;
                }
                PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
                return SUMMARY_STATE_HANDLE_INPUT;
            }

            if (JOY_REPEAT(PAD_KEY_LEFT)
                && summaryScreen->mercurySkillsCursor >= 3
                && summaryScreen->mercurySkillsCursor <= 5) {
                Sound_PlayEffect(SE_CONFIRM_sseq_3);
                summaryScreen->mercurySkillsCursor -= 3;
                PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
                return SUMMARY_STATE_HANDLE_INPUT;
            }

            if (JOY_REPEAT(PAD_KEY_RIGHT)
                && summaryScreen->mercurySkillsCursor <= 2) {
                Sound_PlayEffect(SE_CONFIRM_sseq_3);
                summaryScreen->mercurySkillsCursor += 3;
                PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
                return SUMMARY_STATE_HANDLE_INPUT;
            }

            return SUMMARY_STATE_HANDLE_INPUT;
        }
    }

'''
    replace_span(path, start_marker, end_marker, replacement, "MR07B Skills input replacement")


def validate(root: Path) -> dict[str, bool]:
    main_h = (root / "include/applications/pokemon_summary_screen/main.h").read_text()
    main_c = (root / "src/applications/pokemon_summary_screen/main.c").read_text()
    text_json = (root / "res/text/pokemon_summary_screen.json").read_text()

    checks = {
        "production_ev_editor_state":
            "mercurySkillsEditorMode" in main_h
            and "mercurySkillsEditorWindow" in main_h,
        "a_opens_ev_editor":
            "JOY_NEW(PAD_BUTTON_A)" in main_c
            and "MercurySkills_OpenEvEditor(summaryScreen)" in main_c,
        "real_party_ev_write":
            "Pokemon_SetValue(mon, sMercuryEvDataParams[stat], &value)" in main_c,
        "real_box_ev_write":
            "BoxPokemon_SetValue(" in main_c
            and "sMercuryEvDataParams[stat]" in main_c,
        "modern_ev_caps":
            "510 - summaryScreen->monData.evTotal" in main_c
            and "legalMax > 252" in main_c,
        "live_stat_recalc":
            "Pokemon_CalcLevelAndStats(mon)" in main_c
            and "SetMonData(summaryScreen)" in main_c,
        "bottom_screen_editor":
            "BG_LAYER_SUB_0" in main_c
            and "PokemonSummary_Text_MercuryEvTraining" in text_json,
        "touch_controls":
            "TouchScreen_CheckRectanglePressed(sMercuryEvTouchRects)" in main_c,
        "radial_restore":
            "sub_buttons_NCGR" in main_c
            and "PokemonSummaryScreen_SetSubscreenType(summaryScreen)" in main_c,
        "clear_all":
            "MercurySkills_ClearAllEvs" in main_c
            and "PAD_BUTTON_Y" in main_c,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr07b-ev-editor.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_text(root)
    patch_header(root)
    patch_main(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07B_SUMMARY_EV_EDITOR",
        "status": status,
        "requires": "MR07A native Summary Skills visual foundation",
        "controls": {
            "enter_edit_selection": "X",
            "open_selected_stat": "A",
            "editor_stat": "D-pad Up/Down or touch stat row",
            "ev_minus_plus_4": "D-pad Left/Right or touch -4/+4",
            "selected_zero": "L or touch 0",
            "selected_max": "R or touch MAX",
            "clear_all": "Y or touch CLEAR ALL",
            "back_to_selection": "B or touch BACK",
            "finish_all_editing": "X",
        },
        "limits": {
            "per_stat": 252,
            "total": 510,
            "ivs_visible": False,
        },
        "storage": "real Pokemon/BoxPokemon EV fields",
        "recalculation": "party/full Pokemon recalculated immediately",
        "bottom_screen": "temporary native EV editor; Platinum radial wheel restored on close",
        "nature_editor": "not yet wired",
        "primary_ability_editor": "not yet wired",
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07B validation failed")


if __name__ == "__main__":
    main()
