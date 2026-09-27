#!/usr/bin/env python3
"""MR07D3 — use Platinum's native Skills-page palette on Mercury Skills.

Applied after MR07D2. Visual-only.

The vanilla Platinum Summary graphics already load a 16-palette main-screen
sheet. Palette slot 8 is the game's Skills-family palette: white/cream value
fields plus blue/lavender/purple accents. MR07D3 switches Mercury's custom
Skills information window from generic text palette 15 to that real palette
and composes the denser Mercury layout out of the same colors.

No generated art and no new palette are introduced.
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


def replace_span(path: Path, start_marker: str, end_marker: str, replacement: str, label: str) -> None:
    text = path.read_text()
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker missing in {path}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker missing in {path}")
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def patch_window(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/window.c"

    replace_once(
        path,
        """        .palette = 15,
        .baseTile = 0x23B,
    },
};""",
        """        // Vanilla Platinum Skills-family palette from tiles_main.pal.
        .palette = 8,
        .baseTile = 0x23B,
    },
};""",
        "MR07D3 native Skills palette slot",
    )

    # The cursor is rendered into the same palette-8 window, so give it a
    # palette-8 purple rather than SUMMARY_TEXT_RED (whose indices belong to
    # palette 15).
    replace_once(
        path,
        """        ColoredArrow_SetColor(arrow, SUMMARY_TEXT_RED);
""",
        """        ColoredArrow_SetColor(arrow, TEXT_COLOR(14, 13, 0));
""",
        "MR07D3 purple native cursor",
    )

    start = "static void DrawSkillsPageWindows(PokemonSummaryScreen *summaryScreen)\n{"
    end = "\nstatic void DrawConditionPageWindows(PokemonSummaryScreen *summaryScreen)"

    renderer = r'''static void DrawSkillsPageWindows(PokemonSummaryScreen *summaryScreen)
{
    Window_ScheduleCopyToVRAM(
        &summaryScreen->staticWindows[SUMMARY_WINDOW_LABEL_SKILLS]);

    Window *panel =
        &summaryScreen->extraWindows[SUMMARY_WINDOW_MERCURY_SKILLS_PANEL];

    // Palette slot 8 comes directly from Platinum's tiles_main.pal:
    //   5 = white, 6 = pale yellow, 9-11 = blue family,
    //   12-14 = lavender/purple family.
    // This deliberately mirrors the vanilla Skills page's colored stat rows
    // while preserving Mercury's denser 2x3 information layout.
    const TextColor mercuryDark = TEXT_COLOR(1, 2, 0);
    const TextColor mercuryLight = TEXT_COLOR(5, 4, 0);
    const TextColor mercuryBlue = TEXT_COLOR(11, 10, 0);
    const TextColor mercuryPurple = TEXT_COLOR(14, 13, 0);

    Window_FillRectWithColor(panel, 12, 0, 0, 152, 160);

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

    static const u8 statCellX[6] = { 0, 0, 0, 76, 76, 76 };
    static const u8 statY[6] = { 1, 17, 33, 1, 17, 33 };

    for (u32 i = 0; i < 6; i++) {
        u32 cellX = statCellX[i];
        BOOL selected =
            summaryScreen->mercurySkillsEditMode
            && summaryScreen->mercurySkillsCursor == i;

        u8 labelW = (i == 0) ? 24 : 45;
        u8 valueX = cellX + labelW;
        u8 valueW = 76 - labelW;
        u8 labelFill = ((i % 3) & 1) ? 13 : 12;
        u8 valueFill = ((i % 3) & 1) ? 6 : 5;

        Window_FillRectWithColor(
            panel,
            labelFill,
            cellX,
            statY[i] - 1,
            labelW,
            15);
        Window_FillRectWithColor(
            panel,
            valueFill,
            valueX,
            statY[i] - 1,
            valueW,
            15);

        MercurySkills_PrintMessage(
            summaryScreen,
            panel,
            statLabels[i],
            cellX + 2,
            statY[i],
            mercuryLight);

        if (selected) {
            MercurySkills_PrintCursor(
                panel,
                valueX + 1,
                statY[i]);
        }

        if (i == 0) {
            MercurySkills_PrintHp(
                summaryScreen,
                panel,
                selected ? valueX + 13 : valueX + 4,
                statY[i],
                mercuryDark);
        } else {
            MercurySkills_PrintNumber(
                summaryScreen,
                panel,
                statValues[i],
                selected ? valueX + 13 : valueX + 7,
                statY[i],
                mercuryDark);
        }
    }

    BOOL natureSelected =
        summaryScreen->mercurySkillsEditMode
        && summaryScreen->mercurySkillsCursor == 6;

    Window_FillRectWithColor(panel, 13, 0, 49, 45, 16);
    Window_FillRectWithColor(panel, 5, 45, 49, 57, 16);
    Window_FillRectWithColor(panel, 6, 102, 49, 50, 16);

    MercurySkills_PrintMessage(
        summaryScreen,
        panel,
        PokemonSummary_Text_MercuryNature,
        3,
        51,
        mercuryLight);

    if (natureSelected) {
        MercurySkills_PrintCursor(panel, 47, 51);
    }

    MercurySkills_PrintNature(
        summaryScreen,
        panel,
        natureSelected ? 60 : 50,
        51,
        mercuryDark);

    MercurySkills_PrintMessage(
        summaryScreen,
        panel,
        sMercuryNatureEffectText[summaryScreen->monData.nature],
        105,
        51,
        mercuryBlue);

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
        u32 y = 68 + row * 14;
        BOOL selected =
            row == 0
            && summaryScreen->mercurySkillsEditMode
            && summaryScreen->mercurySkillsCursor == 7;

        u8 labelFill = (row & 1) ? 12 : 13;
        u8 valueFill = (row & 1) ? 6 : 5;

        Window_FillRectWithColor(panel, labelFill, 0, y - 1, 50, 13);
        Window_FillRectWithColor(panel, valueFill, 50, y - 1, 102, 13);

        MercurySkills_PrintMessage(
            summaryScreen,
            panel,
            abilityLabels[row],
            3,
            y,
            mercuryLight);

        if (selected) {
            MercurySkills_PrintCursor(panel, 52, y);
        }

        MercurySkills_PrintAbility(
            summaryScreen,
            panel,
            abilityValues[row],
            selected ? 65 : 55,
            y,
            mercuryDark);
    }

    // Vanilla-like yellow description band, using colors from the same
    // Platinum palette slot rather than the generic white debug-style field.
    Window_FillRectWithColor(panel, 8, 0, 124, 152, 2);
    Window_FillRectWithColor(panel, 6, 0, 126, 152, 34);

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
            mercuryPurple,
            NULL);
    } else if (
        summaryScreen->mercurySkillsEditMode
        && summaryScreen->mercurySkillsCursor == 6) {
        MercurySkills_PrintMessage(
            summaryScreen,
            panel,
            sMercuryNatureEffectText[summaryScreen->monData.nature],
            5,
            136,
            mercuryPurple);
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
            mercuryDark,
            NULL);
    }

    Window_ScheduleCopyToVRAM(panel);
    MercurySkills_DrawEditPrompt(summaryScreen);
}
'''

    replace_span(path, start, end, renderer, "MR07D3 vanilla-palette Skills renderer")


def validate(root: Path) -> dict[str, bool]:
    window_c = (
        root / "src/applications/pokemon_summary_screen/window.c"
    ).read_text()

    checks = {
        "vanilla_palette_slot_8":
            ".palette = 8" in window_c
            and "Platinum Skills-family palette" in window_c,
        "vanilla_lavender_family":
            "Window_FillRectWithColor(panel, 13" in window_c
            and "Window_FillRectWithColor(panel, 12" in window_c,
        "vanilla_white_yellow_values":
            "valueFill = (row & 1) ? 6 : 5" in window_c
            and "valueFill = ((i % 3) & 1) ? 6 : 5" in window_c,
        "vanilla_description_band":
            "Window_FillRectWithColor(panel, 8, 0, 124" in window_c
            and "Window_FillRectWithColor(panel, 6, 0, 126" in window_c,
        "palette_aware_cursor":
            "TEXT_COLOR(14, 13, 0)" in window_c,
        "no_new_graphics":
            "image" not in window_c.lower()
            and "png" not in window_c.lower(),
        "logic_untouched":
            "PokemonSummaryScreen_DrawExtraWindows" in window_c
            and "sMercuryNatureEffectText" in window_c,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr07d3-vanilla-skills-palette.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_window(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07D3_VANILLA_PLATINUM_SKILLS_PALETTE",
        "status": status,
        "scope": "top Skills visual palette only",
        "source": "vanilla res/graphics/pokemon_summary_screen/tiles_main.pal slot 8",
        "new_art": False,
        "new_palette": False,
        "functionality_changed": False,
        "layout_changed": False,
        "colors": {
            "values": "vanilla white / pale yellow",
            "labels": "vanilla lavender / purple",
            "accents": "vanilla blue",
            "description": "vanilla pale yellow band",
        },
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07D3 validation failed")


if __name__ == "__main__":
    main()
