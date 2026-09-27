#!/usr/bin/env python3
"""MR07D5 — Platinum-native colored lower-screen Summary editors.

Applied after MR07D4. Visual-only.

This pass removes the remaining flat-white feel from the temporary EV,
Primary Ability, and Nature editors. It uses the vanilla Platinum Summary
lower-screen palette that is already loaded from tiles_sub.NCLR, palette 0:

- warm cream/tan information fields;
- native dark-blue title bar and selection arrow;
- blue separators/accent strips;
- standard Platinum window frames retained;
- the radial Summary screen still returns immediately when an editor closes.

No new graphics or palette files are added and no EV/Nature/Ability behavior
is changed.
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


def patch_editor_palette(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"
    text = path.read_text()

    old = ".palette = MERCURY_SKILLS_EDITOR_TEXT_PLTT,"
    count = text.count(old)
    if count != 3:
        raise SystemExit(
            f"MR07D5 editor palette: expected three window template palettes, found {count}"
        )
    text = text.replace(
        old,
        ".palette = 0, // vanilla tiles_sub.NCLR warm/blue Summary palette",
    )
    path.write_text(text, encoding="utf-8")

    replace_once(
        path,
        """        ColoredArrow_SetColor(arrow, SUMMARY_TEXT_RED);
""",
        """        ColoredArrow_SetColor(arrow, TEXT_COLOR(15, 14, 0));
""",
        "MR07D5 native dark-blue lower-screen cursor",
    )


def patch_ev(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"
    start = "static void MercurySkillsEditor_DrawEV(PokemonSummaryScreen *summaryScreen)\n{"
    end = "\nstatic void MercurySkillsEditor_DrawAbility(PokemonSummaryScreen *summaryScreen)"

    replacement = r'''static void MercurySkillsEditor_DrawEV(PokemonSummaryScreen *summaryScreen)
{
    Window *header =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_HEADER];
    Window *body =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_BODY];
    Window *footer =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_FOOTER];

    // Palette 0 is vanilla tiles_sub.NCLR:
    // 0 warm gray, 4-8 cream/gold, 12-15 blue family, 9 black.
    const TextColor editorDark = TEXT_COLOR(9, 1, 0);
    const TextColor editorBlue = TEXT_COLOR(15, 14, 0);
    const TextColor editorLight = TEXT_COLOR(4, 5, 0);

    // Strong Platinum-style title band.
    Window_FillTilemap(header, 15);
    Window_FillRectWithColor(header, 14, 0, 14, 240, 2);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        header,
        PokemonSummary_Text_MercuryEvEditorTitle,
        8,
        1,
        editorLight);

    // Warm alternating rows replace the old flat white sheet.
    Window_FillTilemap(body, 0);
    for (u32 stat = 0; stat < 6; stat++) {
        u32 y = 2 + stat * 16;
        BOOL selected = summaryScreen->mercurySkillsEditorCursor == stat;
        u8 rowFill = (stat & 1) ? 5 : 4;

        Window_FillRectWithColor(body, rowFill, 4, y - 1, 232, 15);

        if (selected) {
            Window_FillRectWithColor(body, 12, 4, y - 1, 3, 15);
            MercurySkillsEditor_PrintCursor(body, 9, y);
        }

        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            sMercurySkillsEvLabels[stat],
            selected ? 23 : 18,
            y,
            editorDark);
        MercurySkillsEditor_PrintNumberMessage(
            summaryScreen,
            body,
            PokemonSummary_Text_MercuryEvEditorValue,
            summaryScreen->monData.evs[stat],
            132,
            y,
            editorDark);
    }

    // Total + help live in a cream control panel with a native blue divider.
    Window_FillTilemap(footer, 4);
    Window_FillRectWithColor(footer, 12, 0, 0, 240, 2);
    MercurySkillsEditor_PrintNumberMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryEvEditorTotal,
        summaryScreen->monData.evTotal,
        8,
        4,
        editorBlue);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryEvEditorHelp1,
        8,
        19,
        editorDark);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryEvEditorHelp2,
        8,
        34,
        editorDark);

    Window_ScheduleCopyToVRAM(header);
    Window_ScheduleCopyToVRAM(body);
    Window_ScheduleCopyToVRAM(footer);
}
'''
    replace_span(path, start, end, replacement, "MR07D5 EV editor color treatment")


def patch_ability(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"
    start = "static void MercurySkillsEditor_DrawAbility(PokemonSummaryScreen *summaryScreen)\n{"
    end = "\nstatic void MercurySkillsEditor_DrawNature(PokemonSummaryScreen *summaryScreen)"

    replacement = r'''static void MercurySkillsEditor_DrawAbility(PokemonSummaryScreen *summaryScreen)
{
    Window *header =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_HEADER];
    Window *body =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_BODY];
    Window *footer =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_FOOTER];

    const TextColor editorDark = TEXT_COLOR(9, 1, 0);
    const TextColor editorBlue = TEXT_COLOR(15, 14, 0);
    const TextColor editorLight = TEXT_COLOR(4, 5, 0);

    Window_FillTilemap(header, 15);
    Window_FillRectWithColor(header, 14, 0, 14, 240, 2);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        header,
        PokemonSummary_Text_MercuryAbilityEditorTitle,
        8,
        1,
        editorLight);

    Window_FillTilemap(body, 4);

    // Legal primary Abilities occupy compact cream rows at the top.
    for (u32 i = 0; i < summaryScreen->mercurySkillsAbilityCount; i++) {
        u32 y = 5 + i * 18;
        BOOL selected = summaryScreen->mercurySkillsEditorCursor == i;
        u8 rowFill = (i & 1) ? 5 : 4;

        Window_FillRectWithColor(body, rowFill, 4, y - 2, 232, 16);

        if (selected) {
            Window_FillRectWithColor(body, 12, 4, y - 2, 3, 16);
            MercurySkillsEditor_PrintCursor(body, 9, y);
        }

        MercurySkillsEditor_PrintAbility(
            summaryScreen,
            body,
            summaryScreen->mercurySkillsAbilityChoices[i],
            selected ? 23 : 18,
            y,
            editorDark);
    }

    if (summaryScreen->mercurySkillsAbilityCount == 1) {
        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            PokemonSummary_Text_MercuryAbilityEditorSingle,
            18,
            41,
            editorBlue);
    }

    // Ability description gets its own pale-gold information panel.
    Window_FillRectWithColor(body, 12, 8, 58, 224, 2);
    Window_FillRectWithColor(body, 5, 8, 60, 224, 46);

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
        editorDark,
        NULL);

    Window_FillTilemap(footer, 4);
    Window_FillRectWithColor(footer, 12, 0, 0, 240, 2);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryAbilityEditorHelp1,
        8,
        11,
        editorDark);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryAbilityEditorHelp2,
        8,
        29,
        editorDark);

    Window_ScheduleCopyToVRAM(header);
    Window_ScheduleCopyToVRAM(body);
    Window_ScheduleCopyToVRAM(footer);
}
'''
    replace_span(path, start, end, replacement, "MR07D5 Ability editor color treatment")


def patch_nature(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"
    start = "static void MercurySkillsEditor_DrawNature(PokemonSummaryScreen *summaryScreen)\n{"
    end = "\nstatic void MercurySkillsEditor_Draw(PokemonSummaryScreen *summaryScreen)"

    replacement = r'''static void MercurySkillsEditor_DrawNature(PokemonSummaryScreen *summaryScreen)
{
    Window *header =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_HEADER];
    Window *body =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_BODY];
    Window *footer =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_FOOTER];

    const TextColor editorDark = TEXT_COLOR(9, 1, 0);
    const TextColor editorBlue = TEXT_COLOR(15, 14, 0);
    const TextColor editorLight = TEXT_COLOR(4, 5, 0);

    Window_FillTilemap(header, 15);
    Window_FillRectWithColor(header, 14, 0, 14, 240, 2);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        header,
        PokemonSummary_Text_MercuryNatureEditorTitle,
        8,
        1,
        editorLight);

    Window_FillTilemap(body, 0);

    // Seven-row rolling list with the same warm alternating fields used by
    // Platinum's lower-screen palette. The native arrow remains the sole
    // selection symbol.
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
        u8 rowFill = (row & 1) ? 5 : 4;

        Window_FillRectWithColor(body, rowFill, 4, y - 1, 232, 13);

        if (selected) {
            Window_FillRectWithColor(body, 12, 4, y - 1, 3, 13);
            MercurySkillsEditor_PrintCursor(body, 9, y);
        }

        MercurySkillsEditor_PrintNature(
            summaryScreen,
            body,
            (u8)nature,
            selected ? 23 : 18,
            y,
            editorDark);

        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            sMercurySkillsNatureEffectText[nature],
            128,
            y,
            selected ? editorBlue : editorDark);
    }

    Window_FillTilemap(footer, 4);
    Window_FillRectWithColor(footer, 12, 0, 0, 240, 2);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryNatureEditorHelp1,
        8,
        11,
        editorDark);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryNatureEditorHelp2,
        8,
        29,
        editorDark);

    Window_ScheduleCopyToVRAM(header);
    Window_ScheduleCopyToVRAM(body);
    Window_ScheduleCopyToVRAM(footer);
}
'''
    replace_span(path, start, end, replacement, "MR07D5 Nature editor color treatment")


def validate(root: Path) -> dict[str, bool]:
    main_c = (
        root / "src/applications/pokemon_summary_screen/main.c"
    ).read_text()

    checks = {
        "native_sub_palette_zero":
            main_c.count(
                ".palette = 0, // vanilla tiles_sub.NCLR warm/blue Summary palette"
            ) == 3,
        "dark_blue_title_bands":
            main_c.count("Window_FillTilemap(header, 15);") == 3,
        "cream_bodies":
            "Window_FillTilemap(body, 4);" in main_c
            and "u8 rowFill = (stat & 1) ? 5 : 4;" in main_c
            and "u8 rowFill = (row & 1) ? 5 : 4;" in main_c,
        "blue_accents":
            main_c.count(
                "const TextColor editorBlue = TEXT_COLOR(15, 14, 0);"
            ) == 3,
        "native_blue_cursors":
            "ColoredArrow_SetColor(arrow, TEXT_COLOR(15, 14, 0));" in main_c,
        "standard_frames_retained":
            "Window_DrawStandardFrame" in main_c
            and "STANDARD_WINDOW_SYSTEM" in main_c,
        "ability_description_panel":
            "Window_FillRectWithColor(body, 5, 8, 60, 224, 46);" in main_c,
        "radial_restore_retained":
            "PokemonSummaryScreen_SetSubscreenType(summaryScreen)" in main_c,
        "logic_untouched":
            "MercurySkillsEditor_SetCurrentEV" in main_c
            and "MercurySkillsEditor_SetAbility" in main_c
            and "Pokemon_MercurySetNatureOverride" in main_c,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr07d5-summary-editor-color-polish.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_editor_palette(root)
    patch_ev(root)
    patch_ability(root)
    patch_nature(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07D5_PLATINUM_COLORED_SUMMARY_EDITORS",
        "status": status,
        "scope": "lower Summary EV / Ability / Nature visual treatment only",
        "palette_source": "vanilla pokemon_summary_screen/tiles_sub.NCLR palette 0",
        "new_art": False,
        "new_palette": False,
        "functionality_changed": False,
        "innate_backend_added": False,
        "visuals": {
            "header": "native dark-blue title band",
            "body": "warm cream/tan alternating information fields",
            "selection": "native dark-blue menu arrow + slim blue marker",
            "footer": "cream control panel with blue divider",
            "frames": "standard Platinum window frames",
        },
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07D5 validation failed")


if __name__ == "__main__":
    main()
