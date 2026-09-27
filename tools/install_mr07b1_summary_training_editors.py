#!/usr/bin/env python3
"""MR07B1 — real EV and Primary Ability editors on Mercury Summary Skills.

Builds directly on the visually-proven MR07A Skills page.

Player flow:
  Skills -> X -> highlight a stat -> A -> EV editor on bottom screen
  Skills -> X -> highlight Ability -> A -> legal Primary Ability selector

The normal Platinum radial bottom Summary screen is restored when either editor
closes. Nature remains read-only in this gate so we do not mutate the PID; its
persistent override is deliberately deferred to MR07C.

IVs remain absent from this UI by the locked Mercury design.
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
    data = json.loads(path.read_text(encoding="utf-8"))

    additions = {
        "PokemonSummary_Text_MercuryEvEditorTitle": "EV TRAINING",
        "PokemonSummary_Text_MercuryAbilityEditorTitle": "PRIMARY ABILITY",
        "PokemonSummary_Text_MercuryEvEditorValue": "EV {STRVAR_1 52, 0, 0}/252",
        "PokemonSummary_Text_MercuryEvEditorTotal": "TOTAL {STRVAR_1 52, 0, 0}/510",
        "PokemonSummary_Text_MercuryEvEditorHelp1": "LEFT/RIGHT 1   L/R 4",
        "PokemonSummary_Text_MercuryEvEditorHelp2": "X MAX   Y 0   A/B DONE",
        "PokemonSummary_Text_MercuryAbilityEditorHelp1": "UP/DOWN SELECT",
        "PokemonSummary_Text_MercuryAbilityEditorHelp2": "A SET   B BACK",
        "PokemonSummary_Text_MercuryAbilityEditorSingle": "No alternate primary Ability.",
    }

    existing = {row.get("id") for row in data["messages"]}
    for msg_id, value in additions.items():
        if msg_id not in existing:
            data["messages"].append({"id": msg_id, "en_US": value})

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def patch_header(root: Path) -> None:
    path = root / "include/applications/pokemon_summary_screen/main.h"

    replace_once(
        path,
        """    u8 mercurySkillsEditMode;
    u8 mercurySkillsCursor;
} PokemonSummaryScreen;""",
        """    u8 mercurySkillsEditMode;
    u8 mercurySkillsCursor;

    // MR07B1 temporary bottom-screen editor state. These windows exist only
    // while the user is deliberately editing EVs or the Primary Ability.
    Window mercurySkillsEditorWindows[3];
    u8 mercurySkillsEditorMode;
    u8 mercurySkillsEditorCursor;
    u8 mercurySkillsAbilityCount;
    u16 mercurySkillsAbilityChoices[3];
} PokemonSummaryScreen;""",
        "MR07B1 editor controller state",
    )


def patch_main(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"

    # Helper declarations beside the rest of the Summary controller helpers.
    insert_after_once(
        path,
        "static int TryFeedPoffin(PokemonSummaryScreen *summaryScreen);\n",
        """static void MercurySkillsEditor_OpenEV(PokemonSummaryScreen *summaryScreen, u8 stat);
static void MercurySkillsEditor_OpenAbility(PokemonSummaryScreen *summaryScreen);
static void MercurySkillsEditor_Close(PokemonSummaryScreen *summaryScreen);
static void MercurySkillsEditor_Draw(PokemonSummaryScreen *summaryScreen);
static int MercurySkillsEditor_HandleInput(PokemonSummaryScreen *summaryScreen);
static void MercurySkillsEditor_ChangeEV(PokemonSummaryScreen *summaryScreen, int delta);
static void MercurySkillsEditor_SetCurrentEV(PokemonSummaryScreen *summaryScreen, u8 value);
static void MercurySkillsEditor_SetAbility(PokemonSummaryScreen *summaryScreen, u16 ability);
""",
        "MR07B1 helper declarations",
    )

    # Replace MR07A's deliberate A no-op with the real editor entrypoints.
    replace_once(
        path,
        """            // A is intentionally not bound in the visual-approval gate. Once
            // this real-ROM layout is approved, A will enter the EV, Nature or
            // primary-Ability editor for the highlighted field.
            return SUMMARY_STATE_HANDLE_INPUT;""",
        """            if (JOY_NEW(PAD_BUTTON_A)) {
                Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);

                if (summaryScreen->mercurySkillsCursor < 6) {
                    MercurySkillsEditor_OpenEV(
                        summaryScreen,
                        summaryScreen->mercurySkillsCursor);
                } else if (summaryScreen->mercurySkillsCursor == 7) {
                    MercurySkillsEditor_OpenAbility(summaryScreen);
                }

                // Nature intentionally remains read-only until MR07C installs
                // a persistent non-PID effective-Nature override.
                return SUMMARY_STATE_HANDLE_INPUT;
            }

            return SUMMARY_STATE_HANDLE_INPUT;""",
        "MR07B1 bind A to Skills editors",
    )

    # Editor input must own the controls before X edit-selection sees them.
    anchor = """    // MR07A: X owns edit-selection only on the normal Skills page. The lower
    // screen remains Platinum's native radial Summary navigator.
"""
    insert = """    if (summaryScreen->mercurySkillsEditorMode != 0) {
        return MercurySkillsEditor_HandleInput(summaryScreen);
    }

"""
    insert_after_once(path, anchor, insert, "MR07B1 editor input priority")

    # Defensive teardown in case a caller closes the Summary externally.
    replace_once(
        path,
        """    if (summaryScreen->mercuryLearnerMoves != NULL) {
        MercuryMoveLearner_Free(summaryScreen);
    }

    PokemonSummaryScreen_FreeCameraAndMonSprite(summaryScreen);""",
        """    if (summaryScreen->mercuryLearnerMoves != NULL) {
        MercuryMoveLearner_Free(summaryScreen);
    }

    if (summaryScreen->mercurySkillsEditorMode != 0) {
        for (u32 i = 0; i < 3; i++) {
            Window_Remove(&summaryScreen->mercurySkillsEditorWindows[i]);
        }
        summaryScreen->mercurySkillsEditorMode = 0;
    }

    PokemonSummaryScreen_FreeCameraAndMonSprite(summaryScreen);""",
        "MR07B1 defensive editor teardown",
    )

    helpers = r'''
enum {
    MERCURY_SKILLS_EDITOR_NONE = 0,
    MERCURY_SKILLS_EDITOR_EV,
    MERCURY_SKILLS_EDITOR_ABILITY,
};

enum {
    MERCURY_SKILLS_EDITOR_WINDOW_HEADER = 0,
    MERCURY_SKILLS_EDITOR_WINDOW_BODY,
    MERCURY_SKILLS_EDITOR_WINDOW_FOOTER,
    MERCURY_SKILLS_EDITOR_WINDOW_MAX,
};

#define MERCURY_SKILLS_EDITOR_FRAME_TILE 0x300
#define MERCURY_SKILLS_EDITOR_FRAME_PLTT 11
#define MERCURY_SKILLS_EDITOR_TEXT_PLTT  13

static const WindowTemplate sMercurySkillsEditorWindowTemplates[MERCURY_SKILLS_EDITOR_WINDOW_MAX] = {
    [MERCURY_SKILLS_EDITOR_WINDOW_HEADER] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 0,
        .width = 30,
        .height = 2,
        .palette = MERCURY_SKILLS_EDITOR_TEXT_PLTT,
        .baseTile = 1,
    },
    [MERCURY_SKILLS_EDITOR_WINDOW_BODY] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 3,
        .width = 30,
        .height = 14,
        .palette = MERCURY_SKILLS_EDITOR_TEXT_PLTT,
        .baseTile = 61,
    },
    [MERCURY_SKILLS_EDITOR_WINDOW_FOOTER] = {
        .bgLayer = BG_LAYER_SUB_0,
        .tilemapLeft = 1,
        .tilemapTop = 18,
        .width = 30,
        .height = 6,
        .palette = MERCURY_SKILLS_EDITOR_TEXT_PLTT,
        .baseTile = 481,
    },
};

static const u32 sMercurySkillsEvParams[6] = {
    MON_DATA_HP_EV,
    MON_DATA_ATK_EV,
    MON_DATA_DEF_EV,
    MON_DATA_SPATK_EV,
    MON_DATA_SPDEF_EV,
    MON_DATA_SPEED_EV,
};

static const u32 sMercurySkillsEvLabels[6] = {
    PokemonSummary_Text_LabelHp,
    PokemonSummary_Text_LabelAttack,
    PokemonSummary_Text_LabelDefense,
    PokemonSummary_Text_LabelSpAttack,
    PokemonSummary_Text_LabelSpDefense,
    PokemonSummary_Text_LabelSpeed,
};

static void MercurySkillsEditor_PrintMessage(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u32 entryID,
    u32 x,
    u32 y,
    TextColor color)
{
    MessageLoader_GetString(
        summaryScreen->msgLoader,
        entryID,
        summaryScreen->string);
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

static void MercurySkillsEditor_PrintNumberMessage(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u32 entryID,
    u32 value,
    u32 x,
    u32 y,
    TextColor color)
{
    String *fmt = MessageLoader_GetNewString(
        summaryScreen->msgLoader,
        entryID);

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
        window,
        FONT_SYSTEM,
        summaryScreen->string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        color,
        NULL);
}

static void MercurySkillsEditor_PrintAbility(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u16 ability,
    u32 x,
    u32 y,
    TextColor color)
{
    StringTemplate_SetAbilityName(
        summaryScreen->strFormatter,
        0,
        ability);
    String *fmt = MessageLoader_GetNewString(
        summaryScreen->msgLoader,
        PokemonSummary_Text_TemplateAbility);
    StringTemplate_Format(
        summaryScreen->strFormatter,
        summaryScreen->string,
        fmt);
    String_Free(fmt);

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

static void MercurySkillsEditor_CreateWindows(PokemonSummaryScreen *summaryScreen)
{
    Bg_ClearTilemap(summaryScreen->bgConfig, BG_LAYER_SUB_0);

    LoadStandardWindowGraphics(
        summaryScreen->bgConfig,
        BG_LAYER_SUB_0,
        MERCURY_SKILLS_EDITOR_FRAME_TILE,
        MERCURY_SKILLS_EDITOR_FRAME_PLTT,
        STANDARD_WINDOW_SYSTEM,
        HEAP_ID_POKEMON_SUMMARY_SCREEN);
    Font_LoadTextPalette(
        PAL_LOAD_SUB_BG,
        PLTT_OFFSET(MERCURY_SKILLS_EDITOR_TEXT_PLTT),
        HEAP_ID_POKEMON_SUMMARY_SCREEN);

    for (u32 i = 0; i < MERCURY_SKILLS_EDITOR_WINDOW_MAX; i++) {
        Window_AddFromTemplate(
            summaryScreen->bgConfig,
            &summaryScreen->mercurySkillsEditorWindows[i],
            &sMercurySkillsEditorWindowTemplates[i]);
    }

    Window_DrawStandardFrame(
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_BODY],
        TRUE,
        MERCURY_SKILLS_EDITOR_FRAME_TILE,
        MERCURY_SKILLS_EDITOR_FRAME_PLTT);
    Window_DrawStandardFrame(
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_FOOTER],
        TRUE,
        MERCURY_SKILLS_EDITOR_FRAME_TILE,
        MERCURY_SKILLS_EDITOR_FRAME_PLTT);

    Bg_ScheduleTilemapTransfer(summaryScreen->bgConfig, BG_LAYER_SUB_0);
}

static void MercurySkillsEditor_RestoreSubscreen(PokemonSummaryScreen *summaryScreen)
{
    for (u32 i = 0; i < MERCURY_SKILLS_EDITOR_WINDOW_MAX; i++) {
        Window_Remove(&summaryScreen->mercurySkillsEditorWindows[i]);
    }

    Bg_ClearTilemap(summaryScreen->bgConfig, BG_LAYER_SUB_0);

    // Temporary editor windows write character tiles into SUB BG0. Reload the
    // real Platinum radial-button sheet before restoring its tilemap.
    NARC *narc = NARC_ctor(
        NARC_INDEX_GRAPHIC__PL_PST_GRA,
        HEAP_ID_POKEMON_SUMMARY_SCREEN);
    Graphics_LoadTilesToBgLayerFromOpenNARC(
        narc,
        sub_buttons_NCGR,
        summaryScreen->bgConfig,
        BG_LAYER_SUB_0,
        0,
        0,
        FALSE,
        HEAP_ID_POKEMON_SUMMARY_SCREEN);
    NARC_dtor(narc);

    summaryScreen->mercurySkillsEditorMode = MERCURY_SKILLS_EDITOR_NONE;
    PokemonSummaryScreen_SetSubscreenType(summaryScreen);
    Bg_ScheduleTilemapTransfer(summaryScreen->bgConfig, BG_LAYER_SUB_0);
}

static void MercurySkillsEditor_OpenEV(
    PokemonSummaryScreen *summaryScreen,
    u8 stat)
{
    summaryScreen->mercurySkillsEditorMode = MERCURY_SKILLS_EDITOR_EV;
    summaryScreen->mercurySkillsEditorCursor = stat;
    summaryScreen->mercurySkillsCursor = stat;
    MercurySkillsEditor_CreateWindows(summaryScreen);
    MercurySkillsEditor_Draw(summaryScreen);
}

static void MercurySkillsEditor_OpenAbility(PokemonSummaryScreen *summaryScreen)
{
    u16 ability1 = (u16)SpeciesData_GetSpeciesValue(
        summaryScreen->monData.species,
        SPECIES_DATA_ABILITY_1);
    u16 ability2 = (u16)SpeciesData_GetSpeciesValue(
        summaryScreen->monData.species,
        SPECIES_DATA_ABILITY_2);
    u16 current = summaryScreen->monData.ability;

    summaryScreen->mercurySkillsAbilityCount = 0;

    if (ability1 != 0) {
        summaryScreen->mercurySkillsAbilityChoices[
            summaryScreen->mercurySkillsAbilityCount++] = ability1;
    }

    if (ability2 != 0
        && ability2 != ability1
        && summaryScreen->mercurySkillsAbilityCount < 3) {
        summaryScreen->mercurySkillsAbilityChoices[
            summaryScreen->mercurySkillsAbilityCount++] = ability2;
    }

    // Preserve any already-assigned legal/custom primary Ability instead of
    // making the editor silently erase it if it is not one of the two native
    // species slots.
    BOOL foundCurrent = FALSE;
    for (u32 i = 0; i < summaryScreen->mercurySkillsAbilityCount; i++) {
        if (summaryScreen->mercurySkillsAbilityChoices[i] == current) {
            foundCurrent = TRUE;
            break;
        }
    }
    if (!foundCurrent
        && current != 0
        && summaryScreen->mercurySkillsAbilityCount < 3) {
        summaryScreen->mercurySkillsAbilityChoices[
            summaryScreen->mercurySkillsAbilityCount++] = current;
    }

    if (summaryScreen->mercurySkillsAbilityCount == 0) {
        return;
    }

    summaryScreen->mercurySkillsEditorCursor = 0;
    for (u32 i = 0; i < summaryScreen->mercurySkillsAbilityCount; i++) {
        if (summaryScreen->mercurySkillsAbilityChoices[i] == current) {
            summaryScreen->mercurySkillsEditorCursor = i;
            break;
        }
    }

    summaryScreen->mercurySkillsEditorMode = MERCURY_SKILLS_EDITOR_ABILITY;
    MercurySkillsEditor_CreateWindows(summaryScreen);
    MercurySkillsEditor_Draw(summaryScreen);
}

static void MercurySkillsEditor_Close(PokemonSummaryScreen *summaryScreen)
{
    if (summaryScreen->mercurySkillsEditorMode == MERCURY_SKILLS_EDITOR_NONE) {
        return;
    }

    MercurySkillsEditor_RestoreSubscreen(summaryScreen);
    PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
}

static void MercurySkillsEditor_DrawEV(PokemonSummaryScreen *summaryScreen)
{
    Window *header =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_HEADER];
    Window *body =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_BODY];
    Window *footer =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_FOOTER];

    Window_FillTilemap(header, 0);
    Window_FillTilemap(body, 15);
    Window_FillTilemap(footer, 15);

    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        header,
        PokemonSummary_Text_MercuryEvEditorTitle,
        4,
        0,
        SUMMARY_TEXT_BLACK);

    for (u32 stat = 0; stat < 6; stat++) {
        u32 y = 3 + stat * 16;
        BOOL selected = summaryScreen->mercurySkillsEditorCursor == stat;

        if (selected) {
            Window_FillRectWithColor(body, 4, 4, y - 2, 232, 15);
        }

        TextColor color =
            selected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLACK;

        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            sMercurySkillsEvLabels[stat],
            10,
            y,
            color);
        MercurySkillsEditor_PrintNumberMessage(
            summaryScreen,
            body,
            PokemonSummary_Text_MercuryEvEditorValue,
            summaryScreen->monData.evs[stat],
            132,
            y,
            color);
    }

    MercurySkillsEditor_PrintNumberMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryEvEditorTotal,
        summaryScreen->monData.evTotal,
        8,
        2,
        SUMMARY_TEXT_BLUE);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryEvEditorHelp1,
        8,
        17,
        SUMMARY_TEXT_BLACK);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryEvEditorHelp2,
        8,
        32,
        SUMMARY_TEXT_BLACK);

    Window_ScheduleCopyToVRAM(header);
    Window_ScheduleCopyToVRAM(body);
    Window_ScheduleCopyToVRAM(footer);
}

static void MercurySkillsEditor_DrawAbility(PokemonSummaryScreen *summaryScreen)
{
    Window *header =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_HEADER];
    Window *body =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_BODY];
    Window *footer =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_FOOTER];

    Window_FillTilemap(header, 0);
    Window_FillTilemap(body, 15);
    Window_FillTilemap(footer, 15);

    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        header,
        PokemonSummary_Text_MercuryAbilityEditorTitle,
        4,
        0,
        SUMMARY_TEXT_BLACK);

    for (u32 i = 0; i < summaryScreen->mercurySkillsAbilityCount; i++) {
        u32 y = 5 + i * 18;
        BOOL selected = summaryScreen->mercurySkillsEditorCursor == i;

        if (selected) {
            Window_FillRectWithColor(body, 4, 4, y - 2, 232, 16);
        }

        MercurySkillsEditor_PrintAbility(
            summaryScreen,
            body,
            summaryScreen->mercurySkillsAbilityChoices[i],
            12,
            y,
            selected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLACK);
    }

    if (summaryScreen->mercurySkillsAbilityCount == 1) {
        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            PokemonSummary_Text_MercuryAbilityEditorSingle,
            12,
            60,
            SUMMARY_TEXT_BLUE);
    }

    u16 ability =
        summaryScreen->mercurySkillsAbilityChoices[
            summaryScreen->mercurySkillsEditorCursor];
    MessageLoader *abilityDesc = MessageLoader_Init(
        MSG_LOADER_LOAD_ON_DEMAND,
        NARC_INDEX_MSGDATA__PL_MSG,
        TEXT_BANK_ABILITY_DESCRIPTIONS,
        HEAP_ID_POKEMON_SUMMARY_SCREEN);
    MessageLoader_GetString(
        abilityDesc,
        ability,
        summaryScreen->string);
    MessageLoader_Free(abilityDesc);

    Text_AddPrinterWithParamsAndColor(
        body,
        FONT_SYSTEM,
        summaryScreen->string,
        12,
        72,
        TEXT_SPEED_NO_TRANSFER,
        SUMMARY_TEXT_BLUE,
        NULL);

    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryAbilityEditorHelp1,
        8,
        9,
        SUMMARY_TEXT_BLACK);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryAbilityEditorHelp2,
        8,
        27,
        SUMMARY_TEXT_BLACK);

    Window_ScheduleCopyToVRAM(header);
    Window_ScheduleCopyToVRAM(body);
    Window_ScheduleCopyToVRAM(footer);
}

static void MercurySkillsEditor_Draw(PokemonSummaryScreen *summaryScreen)
{
    if (summaryScreen->mercurySkillsEditorMode == MERCURY_SKILLS_EDITOR_EV) {
        MercurySkillsEditor_DrawEV(summaryScreen);
    } else if (
        summaryScreen->mercurySkillsEditorMode
        == MERCURY_SKILLS_EDITOR_ABILITY) {
        MercurySkillsEditor_DrawAbility(summaryScreen);
    }
}

static void MercurySkillsEditor_SetCurrentEV(
    PokemonSummaryScreen *summaryScreen,
    u8 value)
{
    u8 stat = summaryScreen->mercurySkillsEditorCursor;
    void *monData = PokemonSummaryScreen_MonData(summaryScreen);

    if (summaryScreen->data->dataType == SUMMARY_DATA_BOX_MON) {
        BoxPokemon_SetValue(
            (BoxPokemon *)monData,
            sMercurySkillsEvParams[stat],
            &value);
    } else {
        Pokemon *mon = (Pokemon *)monData;
        Pokemon_SetValue(
            mon,
            sMercurySkillsEvParams[stat],
            &value);
        Pokemon_CalcLevelAndStats(mon);
    }

    SetMonData(summaryScreen);
    summaryScreen->mercurySkillsCursor = stat;
    PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
    MercurySkillsEditor_Draw(summaryScreen);
}

static void MercurySkillsEditor_ChangeEV(
    PokemonSummaryScreen *summaryScreen,
    int delta)
{
    u8 stat = summaryScreen->mercurySkillsEditorCursor;
    int current = summaryScreen->monData.evs[stat];
    int total = summaryScreen->monData.evTotal;
    int target = current;

    if (delta > 0) {
        int statRoom = 252 - current;
        int totalRoom = 510 - total;
        int amount = delta;

        if (amount > statRoom) amount = statRoom;
        if (amount > totalRoom) amount = totalRoom;
        target += amount;
    } else if (delta < 0) {
        int amount = -delta;
        if (amount > current) amount = current;
        target -= amount;
    }

    if (target != current) {
        MercurySkillsEditor_SetCurrentEV(
            summaryScreen,
            (u8)target);
        Sound_PlayEffect(SE_CONFIRM_sseq_3);
    }
}

static void MercurySkillsEditor_SetAbility(
    PokemonSummaryScreen *summaryScreen,
    u16 ability)
{
    void *monData = PokemonSummaryScreen_MonData(summaryScreen);

    if (summaryScreen->data->dataType == SUMMARY_DATA_BOX_MON) {
        BoxPokemon_SetValue(
            (BoxPokemon *)monData,
            MON_DATA_ABILITY,
            &ability);
    } else {
        Pokemon_SetValue(
            (Pokemon *)monData,
            MON_DATA_ABILITY,
            &ability);
    }

    SetMonData(summaryScreen);
    PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
}

static int MercurySkillsEditor_HandleInput(PokemonSummaryScreen *summaryScreen)
{
    if (summaryScreen->mercurySkillsEditorMode == MERCURY_SKILLS_EDITOR_EV) {
        if (JOY_REPEAT(PAD_KEY_UP)) {
            if (summaryScreen->mercurySkillsEditorCursor == 0) {
                summaryScreen->mercurySkillsEditorCursor = 5;
            } else {
                summaryScreen->mercurySkillsEditorCursor--;
            }
            summaryScreen->mercurySkillsCursor =
                summaryScreen->mercurySkillsEditorCursor;
            Sound_PlayEffect(SE_CONFIRM_sseq_3);
            PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
            MercurySkillsEditor_Draw(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_REPEAT(PAD_KEY_DOWN)) {
            summaryScreen->mercurySkillsEditorCursor++;
            if (summaryScreen->mercurySkillsEditorCursor > 5) {
                summaryScreen->mercurySkillsEditorCursor = 0;
            }
            summaryScreen->mercurySkillsCursor =
                summaryScreen->mercurySkillsEditorCursor;
            Sound_PlayEffect(SE_CONFIRM_sseq_3);
            PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
            MercurySkillsEditor_Draw(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_REPEAT(PAD_KEY_LEFT)) {
            MercurySkillsEditor_ChangeEV(summaryScreen, -1);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_REPEAT(PAD_KEY_RIGHT)) {
            MercurySkillsEditor_ChangeEV(summaryScreen, 1);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_REPEAT(PAD_BUTTON_L)) {
            MercurySkillsEditor_ChangeEV(summaryScreen, -4);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_REPEAT(PAD_BUTTON_R)) {
            MercurySkillsEditor_ChangeEV(summaryScreen, 4);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_NEW(PAD_BUTTON_X)) {
            int current =
                summaryScreen->monData.evs[
                    summaryScreen->mercurySkillsEditorCursor];
            int target = current + (510 - summaryScreen->monData.evTotal);
            if (target > 252) target = 252;
            MercurySkillsEditor_SetCurrentEV(summaryScreen, (u8)target);
            Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_NEW(PAD_BUTTON_Y)) {
            MercurySkillsEditor_SetCurrentEV(summaryScreen, 0);
            Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_NEW(PAD_BUTTON_A) || JOY_NEW(PAD_BUTTON_B)) {
            Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
            MercurySkillsEditor_Close(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        return SUMMARY_STATE_HANDLE_INPUT;
    }

    if (summaryScreen->mercurySkillsEditorMode
        == MERCURY_SKILLS_EDITOR_ABILITY) {
        if (JOY_REPEAT(PAD_KEY_UP)) {
            if (summaryScreen->mercurySkillsEditorCursor == 0) {
                summaryScreen->mercurySkillsEditorCursor =
                    summaryScreen->mercurySkillsAbilityCount - 1;
            } else {
                summaryScreen->mercurySkillsEditorCursor--;
            }
            Sound_PlayEffect(SE_CONFIRM_sseq_3);
            MercurySkillsEditor_Draw(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_REPEAT(PAD_KEY_DOWN)) {
            summaryScreen->mercurySkillsEditorCursor++;
            if (summaryScreen->mercurySkillsEditorCursor
                >= summaryScreen->mercurySkillsAbilityCount) {
                summaryScreen->mercurySkillsEditorCursor = 0;
            }
            Sound_PlayEffect(SE_CONFIRM_sseq_3);
            MercurySkillsEditor_Draw(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_NEW(PAD_BUTTON_A)) {
            u16 ability =
                summaryScreen->mercurySkillsAbilityChoices[
                    summaryScreen->mercurySkillsEditorCursor];
            MercurySkillsEditor_SetAbility(summaryScreen, ability);
            Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
            MercurySkillsEditor_Close(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_NEW(PAD_BUTTON_B)) {
            Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
            MercurySkillsEditor_Close(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        return SUMMARY_STATE_HANDLE_INPUT;
    }

    return SUMMARY_STATE_HANDLE_INPUT;
}
'''

    marker = "const ApplicationManagerTemplate gPokemonSummaryScreenApp = {\n"
    text = path.read_text()
    if "MERCURY_SKILLS_EDITOR_NONE" not in text:
        count = text.count(marker)
        if count != 1:
            raise SystemExit(
                f"MR07B1 helper insertion marker changed: {count}"
            )
        path.write_text(
            text.replace(marker, helpers + "\n" + marker, 1),
            encoding="utf-8",
        )


def validate(root: Path) -> dict[str, bool]:
    header = (
        root / "include/applications/pokemon_summary_screen/main.h"
    ).read_text()
    main_c = (
        root / "src/applications/pokemon_summary_screen/main.c"
    ).read_text()
    text_json = (
        root / "res/text/pokemon_summary_screen.json"
    ).read_text()

    checks = {
        "ev_editor":
            "MERCURY_SKILLS_EDITOR_EV" in main_c
            and "MercurySkillsEditor_ChangeEV" in main_c,
        "modern_ev_caps":
            "252 - current" in main_c
            and "510 - total" in main_c,
        "live_stat_recalc":
            "Pokemon_CalcLevelAndStats(mon);" in main_c
            and "SetMonData(summaryScreen);" in main_c,
        "party_and_box_ev_write":
            "BoxPokemon_SetValue" in main_c
            and "Pokemon_SetValue" in main_c,
        "ability_selector":
            "SPECIES_DATA_ABILITY_1" in main_c
            and "SPECIES_DATA_ABILITY_2" in main_c
            and "MercurySkillsEditor_SetAbility" in main_c,
        "primary_only":
            "mercurySkillsAbilityChoices[3]" in header,
        "bottom_radial_restore":
            "sub_buttons_NCGR" in main_c
            and "PokemonSummaryScreen_SetSubscreenType(summaryScreen);" in main_c,
        "nature_not_pid_mutated":
            "MON_DATA_PERSONALITY" not in main_c,
        "editor_messages":
            "PokemonSummary_Text_MercuryEvEditorTitle" in text_json
            and "PokemonSummary_Text_MercuryAbilityEditorTitle" in text_json,
        "ivs_still_not_exposed":
            "MON_DATA_HP_IV" not in main_c
            and "MON_DATA_SPEED_IV" not in main_c,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr07b1-summary-training-editors.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_text(root)
    patch_header(root)
    patch_main(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07B1_SUMMARY_TRAINING_EDITORS",
        "status": status,
        "requires": "MR07A polished native Skills screen",
        "controls": {
            "skills_x": "enter/leave field selection",
            "skills_a_stat": "open EV editor for highlighted stat",
            "skills_a_ability": "open Primary Ability selector",
            "ev_up_down": "choose stat",
            "ev_left_right": "-/+ 1",
            "ev_l_r": "-/+ 4",
            "ev_x": "MAX selected stat subject to 252/510 caps",
            "ev_y": "ZERO selected stat",
            "ev_a_b": "done and restore Platinum radial bottom screen",
            "ability_up_down": "choose legal primary Ability",
            "ability_a": "commit",
            "ability_b": "cancel",
        },
        "ev_limits": {
            "per_stat": 252,
            "total": 510,
            "writes_real_pokemon_data": True,
            "recalculates_party_stats_live": True,
        },
        "ability_source": [
            "SPECIES_DATA_ABILITY_1",
            "SPECIES_DATA_ABILITY_2",
            "currently assigned primary Ability if distinct",
        ],
        "innates_editable": False,
        "nature_editor": "deferred to MR07C persistent override; PID remains untouched",
        "iv_editor": False,
        "bottom_screen": "temporary native window editor, then restored Platinum radial navigator",
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07B1 validation failed")


if __name__ == "__main__":
    main()
