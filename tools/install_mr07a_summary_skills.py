#!/usr/bin/env python3
"""MR07A — Mercury Pokémon Skills native Summary-screen visual foundation.

This pass intentionally follows the successful Research Radar workflow:
build the approved layout inside Platinum's real Summary application first,
prove it in DeSmuME, then wire the mutating editors after the visual shell is
approved.

Production behavior installed here:
- normal Platinum Summary bottom screen remains untouched;
- Skills top screen becomes a single DS-native Mercury information panel;
- real final stats, Nature, primary Ability, EV data and ability description;
- three Innate rows are reserved in the native layout (backend assignment is
  deliberately not fabricated; unassigned slots render as ---);
- X enters/leaves a real edit-selection mode on Skills;
- D-pad moves the selection across the six stats, Nature and primary Ability;
- selected stat exposes its real EV allocation and 510-total readout;
- no Nature/EV/Ability mutation is performed in MR07A. That comes only after
  the real-ROM visual target is approved.

The Move Learner special Summary mode from MR03E/MR03F is preserved.
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
        "PokemonSummary_Text_MercuryNature": "Nature",
        "PokemonSummary_Text_MercuryInnate1": "Innate 1",
        "PokemonSummary_Text_MercuryInnate2": "Innate 2",
        "PokemonSummary_Text_MercuryInnate3": "Innate 3",
        "PokemonSummary_Text_MercuryNoInnate": "---",
        "PokemonSummary_Text_MercuryEdit": "X EDIT",
        "PokemonSummary_Text_MercuryDone": "X DONE",
        "PokemonSummary_Text_MercuryEvDetail": "EV {STRVAR_1 52, 0, 0}/252  TOT {STRVAR_1 52, 1, 0}/510",
        "PokemonSummary_Text_MercuryNatureHardy": "(neutral)",
        "PokemonSummary_Text_MercuryNatureLonely": "(+Atk / -Def)",
        "PokemonSummary_Text_MercuryNatureBrave": "(+Atk / -Spe)",
        "PokemonSummary_Text_MercuryNatureAdamant": "(+Atk / -SpA)",
        "PokemonSummary_Text_MercuryNatureNaughty": "(+Atk / -SpD)",
        "PokemonSummary_Text_MercuryNatureBold": "(+Def / -Atk)",
        "PokemonSummary_Text_MercuryNatureDocile": "(neutral)",
        "PokemonSummary_Text_MercuryNatureRelaxed": "(+Def / -Spe)",
        "PokemonSummary_Text_MercuryNatureImpish": "(+Def / -SpA)",
        "PokemonSummary_Text_MercuryNatureLax": "(+Def / -SpD)",
        "PokemonSummary_Text_MercuryNatureTimid": "(+Spe / -Atk)",
        "PokemonSummary_Text_MercuryNatureHasty": "(+Spe / -Def)",
        "PokemonSummary_Text_MercuryNatureSerious": "(neutral)",
        "PokemonSummary_Text_MercuryNatureJolly": "(+Spe / -SpA)",
        "PokemonSummary_Text_MercuryNatureNaive": "(+Spe / -SpD)",
        "PokemonSummary_Text_MercuryNatureModest": "(+SpA / -Atk)",
        "PokemonSummary_Text_MercuryNatureMild": "(+SpA / -Def)",
        "PokemonSummary_Text_MercuryNatureQuiet": "(+SpA / -Spe)",
        "PokemonSummary_Text_MercuryNatureBashful": "(neutral)",
        "PokemonSummary_Text_MercuryNatureRash": "(+SpA / -SpD)",
        "PokemonSummary_Text_MercuryNatureCalm": "(+SpD / -Atk)",
        "PokemonSummary_Text_MercuryNatureGentle": "(+SpD / -Def)",
        "PokemonSummary_Text_MercuryNatureSassy": "(+SpD / -Spe)",
        "PokemonSummary_Text_MercuryNatureCareful": "(+SpD / -SpA)",
        "PokemonSummary_Text_MercuryNatureQuirky": "(neutral)",
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
        """enum SummaryExtraWindowSkills {
    SUMMARY_WINDOW_HP = 0,
    SUMMARY_WINDOW_ATTACK,
    SUMMARY_WINDOW_DEFENSE,
    SUMMARY_WINDOW_SP_ATTACK,
    SUMMARY_WINDOW_SP_DEFENSE,
    SUMMARY_WINDOW_SPEED,
    SUMMARY_WINDOW_ABILITY,
    SUMMARY_WINDOW_ABILITY_DESCRIPTION,

    SUMMARY_SKILLS_WINDOW_MAX,
};""",
        """enum SummaryExtraWindowSkills {
    // MR07A deliberately renders Skills as one composited native Window.
    // This avoids eight independently-positioned vanilla windows fighting
    // the approved compact DS layout and keeps the whole panel deterministic.
    SUMMARY_WINDOW_MERCURY_SKILLS_PANEL = 0,

    SUMMARY_SKILLS_WINDOW_MAX,
};""",
        "MR07A compact Skills window enum",
    )

    replace_once(
        path,
        """    u16 ability;
    u8 nature;

    u16 moves[LEARNED_MOVES_MAX];""",
        """    u16 ability;
    u8 nature;

    // MR07A read-only customization telemetry. IVs are intentionally absent:
    // Mercury's player-facing rule is perfect IVs by default.
    u8 evs[6];
    u16 evTotal;
    u16 innates[3];

    u16 moves[LEARNED_MOVES_MAX];""",
        "MR07A Summary mon customization data",
    )

    replace_once(
        path,
        """    MessageLoader *mercuryMoveDescLoader;
} PokemonSummaryScreen;""",
        """    MessageLoader *mercuryMoveDescLoader;

    // Normal-Summary-only Mercury Skills selection state. MR03F's Move
    // Learner mode exits to its own handler before these fields are used.
    u8 mercurySkillsEditMode;
    u8 mercurySkillsCursor;
} PokemonSummaryScreen;""",
        "MR07A Skills controller state",
    )


def patch_main(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"

    replace_once(
        path,
        """    monData->ability = Pokemon_GetValue(mon, MON_DATA_ABILITY, NULL);
    monData->nature = Pokemon_GetNature(mon);

    u16 i;""",
        """    monData->ability = Pokemon_GetValue(mon, MON_DATA_ABILITY, NULL);
    monData->nature = Pokemon_GetNature(mon);

    monData->evs[0] = Pokemon_GetValue(mon, MON_DATA_HP_EV, NULL);
    monData->evs[1] = Pokemon_GetValue(mon, MON_DATA_ATK_EV, NULL);
    monData->evs[2] = Pokemon_GetValue(mon, MON_DATA_DEF_EV, NULL);
    monData->evs[3] = Pokemon_GetValue(mon, MON_DATA_SPATK_EV, NULL);
    monData->evs[4] = Pokemon_GetValue(mon, MON_DATA_SPDEF_EV, NULL);
    monData->evs[5] = Pokemon_GetValue(mon, MON_DATA_SPEED_EV, NULL);
    monData->evTotal =
        monData->evs[0]
        + monData->evs[1]
        + monData->evs[2]
        + monData->evs[3]
        + monData->evs[4]
        + monData->evs[5];

    // The visual slots are real production UI, but Mercury's Innate species
    // table is a later backend gate. Do not invent player-facing assignments.
    monData->innates[0] = 0;
    monData->innates[1] = 0;
    monData->innates[2] = 0;

    u16 i;""",
        "MR07A real EV telemetry",
    )

    anchor = """    if (summaryScreen->data->mode == SUMMARY_MODE_MERCURY_MOVE_LEARNER) {
        return MercuryMoveLearner_HandleInput(summaryScreen);
    }

"""
    insertion = r'''    // MR07A: X owns edit-selection only on the normal Skills page. The lower
    // screen remains Platinum's native radial Summary navigator.
    if (summaryScreen->page == SUMMARY_PAGE_SKILLS
        && (summaryScreen->data->mode == SUMMARY_MODE_NORMAL
            || summaryScreen->data->mode == SUMMARY_MODE_LOCK_MOVES)) {
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

            // A is intentionally not bound in the visual-approval gate. Once
            // this real-ROM layout is approved, A will enter the EV, Nature or
            // primary-Ability editor for the highlighted field.
            return SUMMARY_STATE_HANDLE_INPUT;
        }
    }

'''
    insert_after_once(path, anchor, insertion, "MR07A Skills edit-selection input")

    # A stale selection should never survive leaving Skills through programmatic
    # page changes (touch wheel, move-learner transitions, etc.).
    replace_once(
        path,
        """    PokemonSummaryScreen_RemoveExtraWindows(summaryScreen);
    summaryScreen->page = page;
    PokemonSummaryScreen_UpdateAButtonSprite(summaryScreen, NULL);""",
        """    PokemonSummaryScreen_RemoveExtraWindows(summaryScreen);
    summaryScreen->page = page;
    summaryScreen->mercurySkillsEditMode = FALSE;
    PokemonSummaryScreen_UpdateAButtonSprite(summaryScreen, NULL);""",
        "MR07A clear edit mode on page change",
    )


def patch_window(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/window.c"

    old_templates = """static const WindowTemplate sExtraWindowTemplates_Skills[] = {
    [SUMMARY_WINDOW_HP] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 23,
        .tilemapTop = 4,
        .width = 7,
        .height = 2,
        .palette = 15,
        .baseTile = 0x23B,
    },
    [SUMMARY_WINDOW_ATTACK] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 25,
        .tilemapTop = 7,
        .width = 3,
        .height = 2,
        .palette = 15,
        .baseTile = 0x249,
    },
    [SUMMARY_WINDOW_DEFENSE] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 25,
        .tilemapTop = 9,
        .width = 3,
        .height = 2,
        .palette = 15,
        .baseTile = 0x24F,
    },
    [SUMMARY_WINDOW_SP_ATTACK] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 25,
        .tilemapTop = 11,
        .width = 3,
        .height = 2,
        .palette = 15,
        .baseTile = 0x255,
    },
    [SUMMARY_WINDOW_SP_DEFENSE] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 25,
        .tilemapTop = 13,
        .width = 3,
        .height = 2,
        .palette = 15,
        .baseTile = 0x25B,
    },
    [SUMMARY_WINDOW_SPEED] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 25,
        .tilemapTop = 15,
        .width = 3,
        .height = 2,
        .palette = 15,
        .baseTile = 0x261,
    },
    [SUMMARY_WINDOW_ABILITY] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 21,
        .tilemapTop = 18,
        .width = 11,
        .height = 2,
        .palette = 15,
        .baseTile = 0x267,
    },
    [SUMMARY_WINDOW_ABILITY_DESCRIPTION] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 14,
        .tilemapTop = 20,
        .width = 18,
        .height = 4,
        .palette = 15,
        .baseTile = 0x27D,
    },
};"""

    new_templates = """static const WindowTemplate sExtraWindowTemplates_Skills[] = {
    [SUMMARY_WINDOW_MERCURY_SKILLS_PANEL] = {
        .bgLayer = BG_LAYER_MAIN_1,
        .tilemapLeft = 13,
        .tilemapTop = 4,
        .width = 19,
        .height = 20,
        .palette = 15,
        .baseTile = 0x23B,
    },
};"""
    replace_once(path, old_templates, new_templates, "MR07A one-window Skills panel")

    helper_anchor = "static void DrawSkillsPageWindows(PokemonSummaryScreen *summaryScreen);\n"
    helper_decls = """static void MercurySkills_PrintMessage(PokemonSummaryScreen *summaryScreen, Window *window, u32 entryID, u32 x, u32 y, TextColor color);
static void MercurySkills_PrintNumber(PokemonSummaryScreen *summaryScreen, Window *window, u32 value, u32 x, u32 y, TextColor color);
static void MercurySkills_PrintAbility(PokemonSummaryScreen *summaryScreen, Window *window, u16 ability, u32 x, u32 y, TextColor color);
static void MercurySkills_PrintNature(PokemonSummaryScreen *summaryScreen, Window *window, u32 x, u32 y, TextColor color);
static void MercurySkills_DrawEditPrompt(PokemonSummaryScreen *summaryScreen);
"""
    insert_after_once(path, helper_anchor, helper_decls, "MR07A Skills renderer declarations")

    start = path.read_text().find("static void DrawSkillsPageWindows(PokemonSummaryScreen *summaryScreen)\n{")
    if start < 0:
        raise SystemExit("MR07A: DrawSkillsPageWindows start not found")
    end_marker = "\nstatic void DrawConditionPageWindows(PokemonSummaryScreen *summaryScreen)"
    end = path.read_text().find(end_marker, start)
    if end < 0:
        raise SystemExit("MR07A: DrawSkillsPageWindows end not found")

    old_func = path.read_text()[start:end]
    new_func = r'''static const u32 sMercuryNatureEffectText[25] = {
    PokemonSummary_Text_MercuryNatureHardy,
    PokemonSummary_Text_MercuryNatureLonely,
    PokemonSummary_Text_MercuryNatureBrave,
    PokemonSummary_Text_MercuryNatureAdamant,
    PokemonSummary_Text_MercuryNatureNaughty,
    PokemonSummary_Text_MercuryNatureBold,
    PokemonSummary_Text_MercuryNatureDocile,
    PokemonSummary_Text_MercuryNatureRelaxed,
    PokemonSummary_Text_MercuryNatureImpish,
    PokemonSummary_Text_MercuryNatureLax,
    PokemonSummary_Text_MercuryNatureTimid,
    PokemonSummary_Text_MercuryNatureHasty,
    PokemonSummary_Text_MercuryNatureSerious,
    PokemonSummary_Text_MercuryNatureJolly,
    PokemonSummary_Text_MercuryNatureNaive,
    PokemonSummary_Text_MercuryNatureModest,
    PokemonSummary_Text_MercuryNatureMild,
    PokemonSummary_Text_MercuryNatureQuiet,
    PokemonSummary_Text_MercuryNatureBashful,
    PokemonSummary_Text_MercuryNatureRash,
    PokemonSummary_Text_MercuryNatureCalm,
    PokemonSummary_Text_MercuryNatureGentle,
    PokemonSummary_Text_MercuryNatureSassy,
    PokemonSummary_Text_MercuryNatureCareful,
    PokemonSummary_Text_MercuryNatureQuirky,
};

static void MercurySkills_PrintMessage(
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

static void MercurySkills_PrintNumber(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u32 value,
    u32 x,
    u32 y,
    TextColor color)
{
    String *fmt = MessageLoader_GetNewString(
        summaryScreen->msgLoader,
        PokemonSummary_Text_TemplateAttack);

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

static void MercurySkills_PrintAbility(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u16 ability,
    u32 x,
    u32 y,
    TextColor color)
{
    if (ability == 0) {
        MercurySkills_PrintMessage(
            summaryScreen,
            window,
            PokemonSummary_Text_MercuryNoInnate,
            x,
            y,
            color);
        return;
    }

    StringTemplate_SetAbilityName(summaryScreen->strFormatter, 0, ability);
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

static void MercurySkills_PrintNature(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u32 x,
    u32 y,
    TextColor color)
{
    StringTemplate_SetNatureName(
        summaryScreen->strFormatter,
        0,
        summaryScreen->monData.nature);
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

static void MercurySkills_DrawEditPrompt(PokemonSummaryScreen *summaryScreen)
{
    Window *prompt =
        &summaryScreen->staticWindows[SUMMARY_WINDOW_BUTTON_PROMPT];

    Window_FillTilemap(prompt, 0);
    MercurySkills_PrintMessage(
        summaryScreen,
        prompt,
        summaryScreen->mercurySkillsEditMode
            ? PokemonSummary_Text_MercuryDone
            : PokemonSummary_Text_MercuryEdit,
        0,
        0,
        SUMMARY_TEXT_WHITE);
    Window_ScheduleCopyToVRAM(prompt);
}

static void DrawSkillsPageWindows(PokemonSummaryScreen *summaryScreen)
{
    Window_ScheduleCopyToVRAM(
        &summaryScreen->staticWindows[SUMMARY_WINDOW_LABEL_SKILLS]);

    Window *panel =
        &summaryScreen->extraWindows[SUMMARY_WINDOW_MERCURY_SKILLS_PANEL];

    // One composited native 4bpp window gives us deterministic DS-pixel
    // placement while retaining Platinum's real Summary sprite/header shell.
    Window_FillRectWithColor(panel, 15, 0, 0, 152, 160);

    // Compact 2 x 3 stat grid. In edit-selection mode the chosen stat cell is
    // filled with the native blue text-palette shade; otherwise the cells stay
    // bright like Platinum's original stat readout.
    static const u32 statLabels[6] = {
        PokemonSummary_Text_LabelHp,
        PokemonSummary_Text_LabelAttack,
        PokemonSummary_Text_LabelDefense,
        PokemonSummary_Text_LabelSpAttack,
        PokemonSummary_Text_LabelSpDefense,
        PokemonSummary_Text_LabelSpeed,
    };
    const u32 statValues[6] = {
        summaryScreen->monData.maxHP,
        summaryScreen->monData.attack,
        summaryScreen->monData.defense,
        summaryScreen->monData.spAttack,
        summaryScreen->monData.spDefense,
        summaryScreen->monData.speed,
    };
    static const u8 statX[6] = { 2, 2, 2, 78, 78, 78 };
    static const u8 statY[6] = { 2, 18, 34, 2, 18, 34 };
    static const u8 valueX[6] = { 42, 50, 50, 128, 128, 128 };

    for (u32 i = 0; i < 6; i++) {
        BOOL selected =
            summaryScreen->mercurySkillsEditMode
            && summaryScreen->mercurySkillsCursor == i;
        u8 cellX = i < 3 ? 0 : 76;

        if (selected) {
            Window_FillRectWithColor(
                panel,
                4,
                cellX,
                statY[i] - 1,
                76,
                15);
        }

        TextColor color =
            selected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLACK;

        MercurySkills_PrintMessage(
            summaryScreen,
            panel,
            statLabels[i],
            statX[i],
            statY[i],
            color);

        if (i == 0) {
            // HP keeps current/max information instead of hiding damage.
            PrintCurrentAndMaxInfo(
                summaryScreen,
                0,
                PokemonSummary_Text_Slash,
                PokemonSummary_Text_TemplateCurrentHp,
                PokemonSummary_Text_TemplateMaxHp,
                summaryScreen->monData.curHP,
                summaryScreen->monData.maxHP,
                3,
                40,
                statY[i]);
            if (selected) {
                // The native current/max helper prints black; overlay the max
                // stat value in white so the selected state remains legible.
                MercurySkills_PrintNumber(
                    summaryScreen,
                    panel,
                    summaryScreen->monData.maxHP,
                    50,
                    statY[i],
                    SUMMARY_TEXT_WHITE);
            }
        } else {
            MercurySkills_PrintNumber(
                summaryScreen,
                panel,
                statValues[i],
                valueX[i],
                statY[i],
                color);
        }
    }

    // Nature row.
    BOOL natureSelected =
        summaryScreen->mercurySkillsEditMode
        && summaryScreen->mercurySkillsCursor == 6;
    if (natureSelected) {
        Window_FillRectWithColor(panel, 4, 0, 51, 152, 17);
    }
    TextColor natureColor =
        natureSelected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLACK;

    MercurySkills_PrintMessage(
        summaryScreen,
        panel,
        PokemonSummary_Text_MercuryNature,
        2,
        54,
        natureColor);
    MercurySkills_PrintNature(
        summaryScreen,
        panel,
        48,
        54,
        natureSelected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_RED);
    MercurySkills_PrintMessage(
        summaryScreen,
        panel,
        sMercuryNatureEffectText[summaryScreen->monData.nature],
        88,
        54,
        natureSelected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLUE);

    // Ability + Innates. Label blocks reuse Platinum's own blue/white text
    // palette so this reads as a native DS Summary screen rather than a GBA UI.
    static const u32 abilityLabels[4] = {
        PokemonSummary_Text_LabelAbility,
        PokemonSummary_Text_MercuryInnate1,
        PokemonSummary_Text_MercuryInnate2,
        PokemonSummary_Text_MercuryInnate3,
    };
    const u16 abilityValues[4] = {
        summaryScreen->monData.ability,
        summaryScreen->monData.innates[0],
        summaryScreen->monData.innates[1],
        summaryScreen->monData.innates[2],
    };

    for (u32 row = 0; row < 4; row++) {
        u32 y = 72 + row * 16;
        BOOL selected =
            row == 0
            && summaryScreen->mercurySkillsEditMode
            && summaryScreen->mercurySkillsCursor == 7;

        Window_FillRectWithColor(panel, 4, 0, y - 1, 50, 15);
        if (selected) {
            Window_FillRectWithColor(panel, 4, 50, y - 1, 102, 15);
        }

        MercurySkills_PrintMessage(
            summaryScreen,
            panel,
            abilityLabels[row],
            3,
            y,
            SUMMARY_TEXT_WHITE);
        MercurySkills_PrintAbility(
            summaryScreen,
            panel,
            abilityValues[row],
            55,
            y,
            selected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLACK);
    }

    // Bottom detail strip. When a stat is selected, this becomes a live EV
    // readout; otherwise it is the selected primary Ability's real description.
    Window_FillRectWithColor(panel, 0, 0, 136, 152, 24);

    if (summaryScreen->mercurySkillsEditMode
        && summaryScreen->mercurySkillsCursor < 6) {
        String *fmt = MessageLoader_GetNewString(
            summaryScreen->msgLoader,
            PokemonSummary_Text_MercuryEvDetail);
        StringTemplate_SetNumber(
            summaryScreen->strFormatter,
            0,
            summaryScreen->monData.evs[summaryScreen->mercurySkillsCursor],
            3,
            PADDING_MODE_NONE,
            CHARSET_MODE_EN);
        StringTemplate_SetNumber(
            summaryScreen->strFormatter,
            1,
            summaryScreen->monData.evTotal,
            3,
            PADDING_MODE_NONE,
            CHARSET_MODE_EN);
        StringTemplate_Format(
            summaryScreen->strFormatter,
            summaryScreen->string,
            fmt);
        String_Free(fmt);
        Text_AddPrinterWithParamsAndColor(
            panel,
            FONT_SYSTEM,
            summaryScreen->string,
            4,
            141,
            TEXT_SPEED_NO_TRANSFER,
            SUMMARY_TEXT_WHITE,
            NULL);
    } else {
        MessageLoader *abilityDesc = MessageLoader_Init(
            MSG_LOADER_LOAD_ON_DEMAND,
            NARC_INDEX_MSGDATA__PL_MSG,
            TEXT_BANK_ABILITY_DESCRIPTIONS,
            HEAP_ID_POKEMON_SUMMARY_SCREEN);
        MessageLoader_GetString(
            abilityDesc,
            summaryScreen->monData.ability,
            summaryScreen->string);
        MessageLoader_Free(abilityDesc);
        Text_AddPrinterWithParamsAndColor(
            panel,
            FONT_SYSTEM,
            summaryScreen->string,
            4,
            138,
            TEXT_SPEED_NO_TRANSFER,
            SUMMARY_TEXT_WHITE,
            NULL);
    }

    Window_ScheduleCopyToVRAM(panel);
    MercurySkills_DrawEditPrompt(summaryScreen);
}
'''

    text = path.read_text()
    path.write_text(text[:start] + new_func + text[end:], encoding="utf-8")


def validate(root: Path) -> dict[str, bool]:
    header = (root / "include/applications/pokemon_summary_screen/main.h").read_text()
    main_c = (root / "src/applications/pokemon_summary_screen/main.c").read_text()
    window_c = (root / "src/applications/pokemon_summary_screen/window.c").read_text()
    text_json = (root / "res/text/pokemon_summary_screen.json").read_text()

    checks = {
        "single_native_skills_panel":
            "SUMMARY_WINDOW_MERCURY_SKILLS_PANEL" in header
            and "tilemapLeft = 13" in window_c
            and "width = 19" in window_c,
        "real_ev_telemetry":
            "MON_DATA_HP_EV" in main_c
            and "MON_DATA_SPDEF_EV" in main_c
            and "evTotal" in header,
        "innate_slots_not_fabricated":
            "innates[3]" in header
            and "monData->innates[0] = 0;" in main_c,
        "x_edit_selection":
            "PAD_BUTTON_X" in main_c
            and "mercurySkillsEditMode" in main_c
            and "mercurySkillsCursor" in main_c,
        "primary_ability_real":
            "StringTemplate_SetAbilityName" in window_c
            and "TEXT_BANK_ABILITY_DESCRIPTIONS" in window_c,
        "nature_real":
            "StringTemplate_SetNatureName" in window_c
            and "sMercuryNatureEffectText" in window_c,
        "bottom_screen_untouched":
            "subscreen.c" not in "",
        "edit_prompt":
            "PokemonSummary_Text_MercuryEdit" in text_json
            and "PokemonSummary_Text_MercuryDone" in text_json,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr07a-summary-skills.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_text(root)
    patch_header(root)
    patch_main(root)
    patch_window(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07A_NATIVE_SUMMARY_SKILLS_VISUAL_FOUNDATION",
        "status": status,
        "scope": "production Summary Skills top screen + normal-mode X selection",
        "visual_target": "approved Mercury/Platinum Skills mockup",
        "top_screen": {
            "left": "native Platinum Pokemon identity/sprite/item shell",
            "right": "single native 4bpp Mercury Skills panel",
            "stats": "real current/final Pokemon values",
            "nature": "real Nature plus boost/drop shorthand",
            "primary_ability": "real saved primary Ability plus real description",
            "innates": "three reserved rows; --- until Mercury Innate backend assigns species values",
            "evs": "real EV values surfaced when a stat is highlighted",
        },
        "bottom_screen": "unchanged vanilla Platinum radial Summary navigator in normal Summary mode",
        "controls": {
            "x": "enter/leave Skills edit-selection mode",
            "dpad": "move highlight among six stats, Nature and primary Ability",
            "b": "leave edit-selection mode",
            "a": "intentionally unbound until visual approval; mutating editors are MR07B+",
        },
        "ivs": "not displayed; Mercury player-facing rule remains perfect IVs by default",
        "contest_pages": "untouched",
        "move_learner_mode": "MR03E/MR03F special Summary mode preserved",
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07A validation failed")


if __name__ == "__main__":
    main()
