#!/usr/bin/env python3
"""MR06B2F — DS-native visual polish for the overworld Radar HUD.

Turn the compact text HUD into a Platinum-like two-panel scan card:
- left: native DS Pokémon preview sprite in a framed panel;
- right: compact target dossier;
- star markers identify premium move / Primary Ability / held-item rolls.

This remains information-only and reuses Platinum's existing preview renderer
instead of introducing external GBA-style DexNav graphics.
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


def patch_hud(root: Path) -> None:
    path = root / "src/overlay005/mercury_radar_hud.c"

    replace_once(
        path,
        '#include "generated/items.h"\n#include "generated/moves.h"\n',
        '#include "generated/genders.h"\n'
        '#include "generated/items.h"\n'
        '#include "generated/moves.h"\n'
        '#include "generated/species_data_params.h"\n',
        "MR06B2F preview/trait generated includes",
    )

    replace_once(
        path,
        '#include "message_util.h"\n#include "render_window.h"\n',
        '#include "message_util.h"\n'
        '#include "pokemon.h"\n'
        '#include "render_window.h"\n',
        "MR06B2F Pokemon runtime include",
    )

    old_struct = """struct MercuryRadarHud {
    BgConfig *bgConfig;
    Window window;
    SysTask *task;
    u16 timer;
    BOOL visible;
};
"""
    new_struct = """struct MercuryRadarHud {
    BgConfig *bgConfig;
    Window window;
    SysTask *task;
    u8 *previewState;
    u16 timer;
    BOOL visible;
};
"""
    replace_once(path, old_struct, new_struct, "MR06B2F preview ownership")

    decl_anchor = """static void MercuryRadarHud_PrintPotential(
    Window *window,
    u8 stars,
    int x,
    int y);
static charcode_t MercuryRadarHud_AsciiToCharCode(char c);
"""
    decl_replacement = """static void MercuryRadarHud_PrintPotential(
    Window *window,
    u8 stars,
    int x,
    int y);
static void MercuryRadarHud_PrintTraitMarker(
    Window *window,
    BOOL premium,
    int x,
    int y);
static BOOL MercuryRadarHud_IsRarePrimaryAbility(
    u16 species,
    const MercuryRadarTargetQuality *quality);
static BOOL MercuryRadarHud_IsRareHeldItem(
    u16 species,
    const MercuryRadarTargetQuality *quality);
static charcode_t MercuryRadarHud_AsciiToCharCode(char c);
"""
    replace_once(path, decl_anchor, decl_replacement, "MR06B2F trait declarations")

    window_anchor = """        BG_LAYER_MAIN_3,
        10,
        1,
        MERCURY_RADAR_HUD_WIDTH_TILES,
        MERCURY_RADAR_HUD_HEIGHT_TILES,
"""
    window_replacement = """        BG_LAYER_MAIN_3,
        13,
        1,
        18,
        MERCURY_RADAR_HUD_HEIGHT_TILES,
"""
    replace_once(path, window_anchor, window_replacement, "MR06B2F right dossier geometry")

    frame_anchor = """    Window_FillTilemap(
        &hud->window,
        Font_GetAttribute(FONT_SYSTEM, FONTATTR_BG_COLOR));

    String *speciesName = MessageUtil_SpeciesName(species, HEAP_ID_FIELD2);
"""
    frame_replacement = """    Window_FillTilemap(
        &hud->window,
        Font_GetAttribute(FONT_SYSTEM, FONTATTR_BG_COLOR));

    // Platinum already ships a polished field-safe Pokémon preview renderer.
    // Use it as the left half of the Radar trace instead of copying GBA art.
    hud->previewState = DrawPokemonPreview(
        hud->bgConfig,
        BG_LAYER_MAIN_3,
        1,
        1,
        FIELD_WINDOW_PALETTE_INDEX,
        BASE_TILE_STANDARD_WINDOW_FRAME,
        species,
        GENDER_MALE,
        HEAP_ID_FIELD2);

    String *speciesName = MessageUtil_SpeciesName(species, HEAP_ID_FIELD2);
"""
    replace_once(path, frame_anchor, frame_replacement, "MR06B2F native DS preview")

    replace_once(
        path,
        'MercuryRadarHud_PrintAscii(&hud->window, "LV", 112, 0);\n'
        '    MercuryRadarHud_PrintNumber(&hud->window, level, 3, 132, 0);',
        'MercuryRadarHud_PrintAscii(&hud->window, "LV", 96, 0);\n'
        '    MercuryRadarHud_PrintNumber(&hud->window, level, 3, 114, 0);',
        "MR06B2F level geometry",
    )

    replace_once(
        path,
        """    MercuryRadarHud_PrintAscii(&hud->window, "SEARCH", 0, 16);
    MercuryRadarHud_PrintNumber(
        &hud->window,
        quality->searchLevel,
        3,
        52,
        16);
    MercuryRadarHud_PrintAscii(&hud->window, "POT", 88, 16);
    MercuryRadarHud_PrintPotential(
        &hud->window,
        quality->potentialStars,
        116,
        16);
""",
        """    MercuryRadarHud_PrintAscii(&hud->window, "SEARCH", 0, 16);
    MercuryRadarHud_PrintNumber(
        &hud->window,
        quality->searchLevel,
        3,
        50,
        16);
    MercuryRadarHud_PrintAscii(&hud->window, "POT", 82, 16);
    MercuryRadarHud_PrintPotential(
        &hud->window,
        quality->potentialStars,
        106,
        16);
""",
        "MR06B2F search/potential geometry",
    )

    move_anchor = """    MercuryRadarHud_PrintAscii(&hud->window, "MOVE", 0, 32);
    if (quality->specialMove != MOVE_NONE) {
        String *moveName = MessageUtil_MoveName(
            quality->specialMove,
            HEAP_ID_FIELD2);
        MercuryRadarHud_PrintString(&hud->window, moveName, 42, 32);
        String_Free(moveName);
    } else {
        MercuryRadarHud_PrintAscii(&hud->window, "---", 42, 32);
    }

    MercuryRadarHud_PrintAscii(&hud->window, "ABILITY", 0, 48);
"""
    move_replacement = """    MercuryRadarHud_PrintTraitMarker(
        &hud->window,
        quality->specialMove != MOVE_NONE,
        0,
        32);
    MercuryRadarHud_PrintAscii(&hud->window, "MOVE", 12, 32);
    if (quality->specialMove != MOVE_NONE) {
        String *moveName = MessageUtil_MoveName(
            quality->specialMove,
            HEAP_ID_FIELD2);
        MercuryRadarHud_PrintString(&hud->window, moveName, 48, 32);
        String_Free(moveName);
    } else {
        MercuryRadarHud_PrintAscii(&hud->window, "---", 48, 32);
    }

    MercuryRadarHud_PrintTraitMarker(
        &hud->window,
        MercuryRadarHud_IsRarePrimaryAbility(species, quality),
        0,
        48);
    MercuryRadarHud_PrintAscii(&hud->window, "ABILITY", 12, 48);
"""
    replace_once(path, move_anchor, move_replacement, "MR06B2F premium move/ability markers")

    replace_once(
        path,
        """        MercuryRadarHud_PrintString(
            &hud->window,
            abilityName,
            54,
            48);
""",
        """        MercuryRadarHud_PrintString(
            &hud->window,
            abilityName,
            68,
            48);
""",
        "MR06B2F ability name geometry",
    )
    replace_once(
        path,
        'MercuryRadarHud_PrintAscii(&hud->window, "---", 54, 48);',
        'MercuryRadarHud_PrintAscii(&hud->window, "---", 68, 48);',
        "MR06B2F blank ability geometry",
    )

    item_anchor = """    MercuryRadarHud_PrintAscii(&hud->window, "ITEM", 0, 64);
    if (quality->heldItem != ITEM_NONE) {
        String *itemName = String_Init(32, HEAP_ID_FIELD2);
        Item_LoadName(itemName, quality->heldItem, HEAP_ID_FIELD2);
        MercuryRadarHud_PrintString(&hud->window, itemName, 42, 64);
        String_Free(itemName);
    } else {
        MercuryRadarHud_PrintAscii(&hud->window, "---", 42, 64);
    }
"""
    item_replacement = """    MercuryRadarHud_PrintTraitMarker(
        &hud->window,
        MercuryRadarHud_IsRareHeldItem(species, quality),
        0,
        64);
    MercuryRadarHud_PrintAscii(&hud->window, "ITEM", 12, 64);
    if (quality->heldItem != ITEM_NONE) {
        String *itemName = String_Init(32, HEAP_ID_FIELD2);
        Item_LoadName(itemName, quality->heldItem, HEAP_ID_FIELD2);
        MercuryRadarHud_PrintString(&hud->window, itemName, 48, 64);
        String_Free(itemName);
    } else {
        MercuryRadarHud_PrintAscii(&hud->window, "---", 48, 64);
    }
"""
    replace_once(path, item_anchor, item_replacement, "MR06B2F premium item marker")

    hide_anchor = """static void MercuryRadarHud_Hide(MercuryRadarHud *hud)
{
    if (hud == NULL || !hud->visible) {
        return;
    }

    Window_EraseStandardFrame(&hud->window, FALSE);
"""
    hide_replacement = """static void MercuryRadarHud_Hide(MercuryRadarHud *hud)
{
    if (hud == NULL || !hud->visible) {
        return;
    }

    if (hud->previewState != NULL) {
        *hud->previewState = PREVIEW_STATE_REMOVE;
        hud->previewState = NULL;
    }

    Window_EraseStandardFrame(&hud->window, FALSE);
"""
    replace_once(path, hide_anchor, hide_replacement, "MR06B2F preview cleanup")

    helper_anchor = """static charcode_t MercuryRadarHud_AsciiToCharCode(char c)
{
"""
    helper_impl = r'''static void MercuryRadarHud_PrintTraitMarker(
    Window *window,
    BOOL premium,
    int x,
    int y)
{
    String *string = String_Init(2, HEAP_ID_FIELD2);
    String_AppendChar(string, premium ? CHAR_STAR : CHAR_SPACE);
    MercuryRadarHud_PrintString(window, string, x, y);
    String_Free(string);
}

static BOOL MercuryRadarHud_IsRarePrimaryAbility(
    u16 species,
    const MercuryRadarTargetQuality *quality)
{
    u8 normalAbility = SpeciesData_GetSpeciesValue(
        species,
        SPECIES_DATA_ABILITY_1);

    return quality->primaryAbility != 0
        && quality->primaryAbility != normalAbility;
}

static BOOL MercuryRadarHud_IsRareHeldItem(
    u16 species,
    const MercuryRadarTargetQuality *quality)
{
    u16 commonItem = SpeciesData_GetSpeciesValue(
        species,
        SPECIES_DATA_HELD_ITEM_COMMON);
    u16 rareItem = SpeciesData_GetSpeciesValue(
        species,
        SPECIES_DATA_HELD_ITEM_RARE);

    return rareItem != ITEM_NONE
        && rareItem != commonItem
        && quality->heldItem == rareItem;
}

static charcode_t MercuryRadarHud_AsciiToCharCode(char c)
{
'''
    replace_once(path, helper_anchor, helper_impl, "MR06B2F premium trait helpers")


def validate(root: Path) -> None:
    source = (root / "src/overlay005/mercury_radar_hud.c").read_text()
    radar = (root / "src/pokeradar.c").read_text()
    start_menu = (root / "src/start_menu.c").read_text()

    checks = {
        "native_preview_renderer": "DrawPokemonPreview(" in source,
        "preview_cleanup": "PREVIEW_STATE_REMOVE" in source,
        "preview_panel_left": "BG_LAYER_MAIN_3,\n        1,\n        1," in source,
        "dossier_panel_right": "BG_LAYER_MAIN_3,\n        13,\n        1,\n        18," in source,
        "premium_move_marker": "quality->specialMove != MOVE_NONE" in source,
        "rare_primary_marker": "MercuryRadarHud_IsRarePrimaryAbility" in source,
        "rare_item_marker": "MercuryRadarHud_IsRareHeldItem" in source,
        "potential_stars_preserved": "MercuryRadarHud_PrintPotential" in source,
        "hud_still_radar_owned": "MercuryRadarHud_Destroy(chain->mercuryHud)" in radar,
        "standalone_encounter_menu_absent": "START_MENU_OPTION_ENCOUNTERS" not in start_menu,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2F validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2f-radar-visual-polish.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    source = root / "src/overlay005/mercury_radar_hud.c"

    if not source.exists():
        raise SystemExit("MR06B2F requires MR06B2E HUD")
    if "MercuryRadarHud_Show" not in source.read_text():
        raise SystemExit("MR06B2F requires MR06B2E HUD runtime")

    patch_hud(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2F_RADAR_VISUAL_POLISH",
        "status": "PASS",
        "presentation": "DS/Platinum-native two-panel Radar trace",
        "left_panel": "native Pokemon preview sprite",
        "right_panel": "target dossier",
        "premium_markers": {
            "special_move": True,
            "rare_primary_ability": True,
            "rare_held_item": True,
            "potential_stars": True,
        },
        "gba_graphics_copied": False,
        "preview_cleanup_with_hud": True,
        "normal_encounter_tables_modified": False,
        "standalone_encounter_menu": False,
        "next": "runtime visual proof of scanner -> SEARCH -> rustling patch -> polished HUD",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
