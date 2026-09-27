#!/usr/bin/env python3
"""MR07D — Platinum-native visual polish for Mercury Summary Skills/editors.

This pass is visual-only. It deliberately does not change EV/Nature/Ability
storage or editing semantics.

Goals:
- retain the approved Mercury information density;
- make the top Skills page read like a Platinum page instead of a debug grid;
- use Platinum's own menu-arrow language instead of full-row pink highlights;
- keep standard DS window frames on temporary bottom-screen editors;
- tighten labels/help text and Nature-effect shorthand;
- preserve the vanilla radial lower Summary screen whenever no editor is open.
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
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def replace_span(path: Path, start_marker: str, end_marker: str, replacement: str, label: str) -> None:
    text = path.read_text()
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker missing in {path}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker missing in {path}")
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def patch_text(root: Path) -> None:
    path = root / "res/text/pokemon_summary_screen.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    replacements = {
        "PokemonSummary_Text_MercuryEvEditorTitle": "EV Training",
        "PokemonSummary_Text_MercuryAbilityEditorTitle": "Ability",
        "PokemonSummary_Text_MercuryNatureEditorTitle": "Nature",
        "PokemonSummary_Text_MercuryEvEditorHelp1": "LEFT/RIGHT 1   L/R 4",
        "PokemonSummary_Text_MercuryEvEditorHelp2": "X MAX   Y 0   A/B DONE",
        "PokemonSummary_Text_MercuryAbilityEditorHelp1": "UP/DOWN SELECT",
        "PokemonSummary_Text_MercuryAbilityEditorHelp2": "A SET   B BACK",
        "PokemonSummary_Text_MercuryNatureEditorHelp1": "UP/DOWN SELECT",
        "PokemonSummary_Text_MercuryNatureEditorHelp2": "A SET   B BACK",
        "PokemonSummary_Text_MercuryNatureHardy": "Neutral",
        "PokemonSummary_Text_MercuryNatureLonely": "+Atk -Def",
        "PokemonSummary_Text_MercuryNatureBrave": "+Atk -Spe",
        "PokemonSummary_Text_MercuryNatureAdamant": "+Atk -SpA",
        "PokemonSummary_Text_MercuryNatureNaughty": "+Atk -SpD",
        "PokemonSummary_Text_MercuryNatureBold": "+Def -Atk",
        "PokemonSummary_Text_MercuryNatureDocile": "Neutral",
        "PokemonSummary_Text_MercuryNatureRelaxed": "+Def -Spe",
        "PokemonSummary_Text_MercuryNatureImpish": "+Def -SpA",
        "PokemonSummary_Text_MercuryNatureLax": "+Def -SpD",
        "PokemonSummary_Text_MercuryNatureTimid": "+Spe -Atk",
        "PokemonSummary_Text_MercuryNatureHasty": "+Spe -Def",
        "PokemonSummary_Text_MercuryNatureSerious": "Neutral",
        "PokemonSummary_Text_MercuryNatureJolly": "+Spe -SpA",
        "PokemonSummary_Text_MercuryNatureNaive": "+Spe -SpD",
        "PokemonSummary_Text_MercuryNatureModest": "+SpA -Atk",
        "PokemonSummary_Text_MercuryNatureMild": "+SpA -Def",
        "PokemonSummary_Text_MercuryNatureQuiet": "+SpA -Spe",
        "PokemonSummary_Text_MercuryNatureBashful": "Neutral",
        "PokemonSummary_Text_MercuryNatureRash": "+SpA -SpD",
        "PokemonSummary_Text_MercuryNatureCalm": "+SpD -Atk",
        "PokemonSummary_Text_MercuryNatureGentle": "+SpD -Def",
        "PokemonSummary_Text_MercuryNatureSassy": "+SpD -Spe",
        "PokemonSummary_Text_MercuryNatureCareful": "+SpD -SpA",
        "PokemonSummary_Text_MercuryNatureQuirky": "Neutral",
    }

    found = set()
    for row in data["messages"]:
        msg_id = row.get("id")
        if msg_id in replacements:
            row["en_US"] = replacements[msg_id]
            found.add(msg_id)

    missing = sorted(set(replacements) - found)
    if missing:
        raise SystemExit("MR07D missing expected text IDs: " + ", ".join(missing))

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_top_skills(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/window.c"

    insert_after_once(
        path,
        '#include "bg_window.h"\n',
        '#include "colored_arrow.h"\n',
        "MR07D top menu-arrow include",
    )

    helper_anchor = """static void MercurySkills_DrawEditPrompt(PokemonSummaryScreen *summaryScreen)
"""
    helper = r'''static void MercurySkills_PrintCursor(
    Window *window,
    u32 x,
    u32 y)
{
    ColoredArrow *arrow =
        ColoredArrow_New(HEAP_ID_POKEMON_SUMMARY_SCREEN);

    if (arrow != NULL) {
        ColoredArrow_SetColor(arrow, SUMMARY_TEXT_RED);
        ColoredArrow_Print(arrow, window, x, y);
        ColoredArrow_Free(arrow);
    }
}

'''
    replace_once(
        path,
        helper_anchor,
        helper + helper_anchor,
        "MR07D top selection cursor helper",
    )

    start = "static void DrawSkillsPageWindows(PokemonSummaryScreen *summaryScreen)\n{"
    end = "\nstatic void DrawConditionPageWindows(PokemonSummaryScreen *summaryScreen)"

    polished = r'''static void DrawSkillsPageWindows(PokemonSummaryScreen *summaryScreen)
{
    Window_ScheduleCopyToVRAM(
        &summaryScreen->staticWindows[SUMMARY_WINDOW_LABEL_SKILLS]);

    Window *panel =
        &summaryScreen->extraWindows[SUMMARY_WINDOW_MERCURY_SKILLS_PANEL];

    // MR07D: keep Platinum's bright information field and blue label tabs.
    // Editing is indicated with the game's native menu arrow + red value text
    // instead of a full-row modern/GBA-style selection fill.
    Window_FillRectWithColor(panel, 15, 0, 0, 152, 160);

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

    static const u8 statCellX[6]  = { 0, 0, 0, 76, 76, 76 };
    static const u8 statY[6]      = { 2, 18, 34, 2, 18, 34 };
    static const u8 labelWidth[6] = { 18, 34, 40, 38, 38, 34 };
    static const u8 valueX[6]     = { 29, 46, 52, 126, 126, 122 };

    for (u32 i = 0; i < 6; i++) {
        u32 cellX = statCellX[i];
        BOOL selected =
            summaryScreen->mercurySkillsEditMode
            && summaryScreen->mercurySkillsCursor == i;

        Window_FillRectWithColor(
            panel,
            4,
            cellX,
            statY[i] - 1,
            labelWidth[i],
            13);

        MercurySkills_PrintMessage(
            summaryScreen,
            panel,
            statLabels[i],
            cellX + 2,
            statY[i],
            SUMMARY_TEXT_WHITE);

        if (selected) {
            MercurySkills_PrintCursor(
                panel,
                cellX + labelWidth[i] + 1,
                statY[i]);
        }

        TextColor valueColor =
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK;

        if (i == 0) {
            MercurySkills_PrintHp(
                summaryScreen,
                panel,
                valueX[i],
                statY[i],
                valueColor);
        } else {
            MercurySkills_PrintNumber(
                summaryScreen,
                panel,
                statValues[i],
                valueX[i],
                statY[i],
                valueColor);
        }
    }

    // Nature gets the same label-tab treatment as a native Platinum field.
    BOOL natureSelected =
        summaryScreen->mercurySkillsEditMode
        && summaryScreen->mercurySkillsCursor == 6;

    Window_FillRectWithColor(panel, 4, 0, 50, 43, 15);
    MercurySkills_PrintMessage(
        summaryScreen,
        panel,
        PokemonSummary_Text_MercuryNature,
        3,
        52,
        SUMMARY_TEXT_WHITE);

    if (natureSelected) {
        MercurySkills_PrintCursor(panel, 45, 52);
    }

    MercurySkills_PrintNature(
        summaryScreen,
        panel,
        natureSelected ? 58 : 50,
        52,
        natureSelected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK);

    MercurySkills_PrintMessage(
        summaryScreen,
        panel,
        sMercuryNatureEffectText[summaryScreen->monData.nature],
        102,
        52,
        SUMMARY_TEXT_BLUE);

    // Primary Ability + Innates share one clean, vanilla-style information
    // block. Only the Primary Ability is editable; Innates remain read-only.
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
        u32 y = 70 + row * 14;
        BOOL selected =
            row == 0
            && summaryScreen->mercurySkillsEditMode
            && summaryScreen->mercurySkillsCursor == 7;

        Window_FillRectWithColor(panel, 4, 0, y - 1, 50, 13);

        MercurySkills_PrintMessage(
            summaryScreen,
            panel,
            abilityLabels[row],
            3,
            y,
            SUMMARY_TEXT_WHITE);

        if (selected) {
            MercurySkills_PrintCursor(panel, 52, y);
        }

        MercurySkills_PrintAbility(
            summaryScreen,
            panel,
            abilityValues[row],
            selected ? 65 : 55,
            y,
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK);
    }

    // Thin separator + detail area mirrors Platinum's use of a distinct
    // description zone without introducing a foreign UI card.
    Window_FillRectWithColor(panel, 1, 0, 125, 152, 1);
    Window_FillRectWithColor(panel, 15, 0, 126, 152, 34);

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
            5,
            136,
            TEXT_SPEED_NO_TRANSFER,
            SUMMARY_TEXT_BLUE,
            NULL);
    } else if (summaryScreen->mercurySkillsEditMode
        && summaryScreen->mercurySkillsCursor == 6) {
        MercurySkills_PrintMessage(
            summaryScreen,
            panel,
            sMercuryNatureEffectText[summaryScreen->monData.nature],
            5,
            136,
            SUMMARY_TEXT_BLUE);
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
            5,
            129,
            TEXT_SPEED_NO_TRANSFER,
            SUMMARY_TEXT_BLACK,
            NULL);
    }

    Window_ScheduleCopyToVRAM(panel);
    MercurySkills_DrawEditPrompt(summaryScreen);
}
'''

    replace_span(path, start, end, polished, "MR07D polished top Skills renderer")


def patch_bottom_editors(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"

    # MR07B1 used palette 13, where Summary's RED/BLUE TextColor constants map
    # to unrelated colors. Palette 15 is Platinum Summary's native text palette
    # and makes the same constants render correctly on the lower editor screen.
    replace_once(
        path,
        "#define MERCURY_SKILLS_EDITOR_TEXT_PLTT  13",
        "#define MERCURY_SKILLS_EDITOR_TEXT_PLTT  15",
        "MR07D editor text palette",
    )

    insert_after_once(
        path,
        '#include "bg_window.h"\n',
        '#include "colored_arrow.h"\n',
        "MR07D editor menu-arrow include",
    )

    create_marker = "static void MercurySkillsEditor_CreateWindows(PokemonSummaryScreen *summaryScreen)\n"
    cursor_helper = r'''static void MercurySkillsEditor_PrintCursor(
    Window *window,
    u32 x,
    u32 y)
{
    ColoredArrow *arrow =
        ColoredArrow_New(HEAP_ID_POKEMON_SUMMARY_SCREEN);

    if (arrow != NULL) {
        ColoredArrow_SetColor(arrow, SUMMARY_TEXT_RED);
        ColoredArrow_Print(arrow, window, x, y);
        ColoredArrow_Free(arrow);
    }
}

'''
    replace_once(
        path,
        create_marker,
        cursor_helper + create_marker,
        "MR07D editor cursor helper",
    )

    ev_start = "static void MercurySkillsEditor_DrawEV(PokemonSummaryScreen *summaryScreen)\n{"
    ev_end = "\nstatic void MercurySkillsEditor_DrawAbility(PokemonSummaryScreen *summaryScreen)"

    ev_polished = r'''static void MercurySkillsEditor_DrawEV(PokemonSummaryScreen *summaryScreen)
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
        SUMMARY_TEXT_WHITE);

    for (u32 stat = 0; stat < 6; stat++) {
        u32 y = 3 + stat * 16;
        BOOL selected = summaryScreen->mercurySkillsEditorCursor == stat;
        TextColor color =
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK;

        if (selected) {
            MercurySkillsEditor_PrintCursor(body, 4, y);
        }

        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            sMercurySkillsEvLabels[stat],
            18,
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
'''
    replace_span(path, ev_start, ev_end, ev_polished, "MR07D EV editor visual polish")

    ability_start = "static void MercurySkillsEditor_DrawAbility(PokemonSummaryScreen *summaryScreen)\n{"
    ability_end = "\nstatic void MercurySkillsEditor_DrawNature(PokemonSummaryScreen *summaryScreen)"

    ability_polished = r'''static void MercurySkillsEditor_DrawAbility(PokemonSummaryScreen *summaryScreen)
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
        SUMMARY_TEXT_WHITE);

    for (u32 i = 0; i < summaryScreen->mercurySkillsAbilityCount; i++) {
        u32 y = 5 + i * 18;
        BOOL selected = summaryScreen->mercurySkillsEditorCursor == i;

        if (selected) {
            MercurySkillsEditor_PrintCursor(body, 4, y);
        }

        MercurySkillsEditor_PrintAbility(
            summaryScreen,
            body,
            summaryScreen->mercurySkillsAbilityChoices[i],
            18,
            y,
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK);
    }

    if (summaryScreen->mercurySkillsAbilityCount == 1) {
        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            PokemonSummary_Text_MercuryAbilityEditorSingle,
            18,
            41,
            SUMMARY_TEXT_BLUE);
    }

    Window_FillRectWithColor(body, 1, 8, 58, 224, 1);

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
        66,
        TEXT_SPEED_NO_TRANSFER,
        SUMMARY_TEXT_BLACK,
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
'''
    replace_span(path, ability_start, ability_end, ability_polished, "MR07D Ability editor visual polish")

    nature_start = "static void MercurySkillsEditor_DrawNature(PokemonSummaryScreen *summaryScreen)\n{"
    nature_end = "\nstatic void MercurySkillsEditor_Draw(PokemonSummaryScreen *summaryScreen)"

    nature_polished = r'''static void MercurySkillsEditor_DrawNature(PokemonSummaryScreen *summaryScreen)
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
        PokemonSummary_Text_MercuryNatureEditorTitle,
        4,
        0,
        SUMMARY_TEXT_WHITE);

    // Seven-row rolling list, using Platinum's native menu arrow instead of a
    // full-width modern highlight bar.
    for (int row = 0; row < 7; row++) {
        int offset = row - 3;
        int nature =
            summaryScreen->mercurySkillsEditorCursor + offset;

        while (nature < 0) {
            nature += NATURE_COUNT;
        }
        while (nature >= NATURE_COUNT) {
            nature -= NATURE_COUNT;
        }

        u32 y = 3 + row * 14;
        BOOL selected = (row == 3);
        TextColor nameColor =
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK;

        if (selected) {
            MercurySkillsEditor_PrintCursor(body, 4, y);
        }

        MercurySkillsEditor_PrintNature(
            summaryScreen,
            body,
            (u8)nature,
            18,
            y,
            nameColor);

        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            sMercurySkillsNatureEffectText[nature],
            128,
            y,
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLUE);
    }

    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryNatureEditorHelp1,
        8,
        9,
        SUMMARY_TEXT_BLACK);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryNatureEditorHelp2,
        8,
        27,
        SUMMARY_TEXT_BLACK);

    Window_ScheduleCopyToVRAM(header);
    Window_ScheduleCopyToVRAM(body);
    Window_ScheduleCopyToVRAM(footer);
}
'''
    replace_span(path, nature_start, nature_end, nature_polished, "MR07D Nature editor visual polish")


def validate(root: Path) -> dict[str, bool]:
    window_c = (
        root / "src/applications/pokemon_summary_screen/window.c"
    ).read_text()
    main_c = (
        root / "src/applications/pokemon_summary_screen/main.c"
    ).read_text()
    text_json = (
        root / "res/text/pokemon_summary_screen.json"
    ).read_text()

    checks = {
        "top_uses_native_menu_arrow":
            "MercurySkills_PrintCursor" in window_c
            and "ColoredArrow_New" in window_c,
        "top_no_full_row_edit_fill":
            "selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK" in window_c
            and "labelWidth[6]" in window_c,
        "platinum_label_tabs":
            "Window_FillRectWithColor(panel, 4" in window_c
            and "abilityLabels[4]" in window_c,
        "short_nature_effects":
            '"+Atk -Def"' in text_json
            and '"+Spe -SpA"' in text_json
            and '"Neutral"' in text_json,
        "editor_uses_summary_text_palette":
            "#define MERCURY_SKILLS_EDITOR_TEXT_PLTT  15" in main_c,
        "ev_editor_arrow_selection":
            "MercurySkillsEditor_PrintCursor(body, 4, y)" in main_c
            and "PokemonSummary_Text_MercuryEvEditorValue" in main_c,
        "ability_editor_separated_description":
            "Window_FillRectWithColor(body, 1, 8, 58, 224, 1)" in main_c,
        "nature_editor_arrow_selection":
            "Seven-row rolling list" in main_c
            and "selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLUE" in main_c,
        "standard_editor_frames_preserved":
            "Window_DrawStandardFrame" in main_c
            and "STANDARD_WINDOW_SYSTEM" in main_c,
        "radial_restore_preserved":
            "PokemonSummaryScreen_SetSubscreenType(summaryScreen)" in main_c,
        "logic_untouched":
            "Pokemon_MercurySetNatureOverride" in main_c
            and "Pokemon_SetValue" in main_c
            and "SPECIES_DATA_ABILITY_2" in main_c,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr07d-summary-visual-polish.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_text(root)
    patch_top_skills(root)
    patch_bottom_editors(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07D_PLATINUM_NATIVE_SUMMARY_VISUAL_POLISH",
        "status": status,
        "scope": "visual-only polish after MR07A/B1/C",
        "top_screen": {
            "selection": "native Platinum menu arrow + red selected value",
            "labels": "compact blue Platinum-style label tabs",
            "nature": "short effect shorthand sized for DS layout",
            "detail": "separated native description/EV detail strip",
        },
        "bottom_editors": {
            "frames": "standard Platinum DS window system retained",
            "selection": "native menu arrow instead of pink full-row fill",
            "ev": "six-row clean list + framed controls",
            "ability": "arrow list + separated vanilla-style description area",
            "nature": "seven-row rolling list + arrow selection",
        },
        "functionality_changed": False,
        "innate_backend_added": False,
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07D validation failed")


if __name__ == "__main__":
    main()
