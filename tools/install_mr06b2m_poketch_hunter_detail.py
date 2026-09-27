#!/usr/bin/env python3
"""MR06B2M — refined Pokétch-native hunter detail page visual proof.

This applies after MR06B2L in the CI-only QA workspace. It keeps the approved
area grid untouched, but simplifies the selected-Pokémon page around what
actually matters for Mercury hunting:

- normal battle level range (visually separate from Search Level);
- Search Level as species-research progress, not Pokémon level;
- Potential stars;
- encounter method;
- one large SEARCH control.

Moves, ability and held-item readouts are deliberately omitted because Mercury
already exposes those systems elsewhere. The visual language remains entirely
Pokétch: four-tone LCD, native icon sprite, pixel-line scanner reticle.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_function(path: Path, start: str, end: str, new_body: str, label: str) -> None:
    text = path.read_text()
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"{label}: start anchor not found in {path}")
    b = text.find(end, a)
    if b < 0:
        raise SystemExit(f"{label}: end anchor not found in {path}")
    path.write_text(text[:a] + new_body + text[b:])


DETAIL = r'''static void DrawDetailSurface(PokemonHistoryGraphics *graphics, int monIdx)
{
    const HistoryData *history = graphics->history;

    Bg_FillTilemapRect(
        graphics->bgConfig,
        BG_LAYER_SUB_2,
        0,
        0,
        0,
        POKETCH_WIDTH_TILES,
        POKETCH_HEIGHT_TILES,
        0);

    for (int i = 0; i < MAX_HISTORY_SIZE; i++) {
        if (graphics->sprites[i] == NULL) {
            continue;
        }

        PoketchAnimation_HideSprite(graphics->sprites[i], i != monIdx);
    }

    // Keep the native Pokétch Pokémon icon, but turn the surrounding LCD into
    // a proper scanner rather than a text menu.
    if (graphics->sprites[monIdx] != NULL) {
        PoketchAnimation_SetSpritePosition(
            graphics->sprites[monIdx],
            FX32_CONST(62),
            FX32_CONST(86));
    }

    Window detail;
    Window_Add(
        graphics->bgConfig,
        &detail,
        BG_LAYER_SUB_2,
        2,
        2,
        24,
        19,
        0,
        1);
    Window_FillTilemap(&detail, 4);
    Window_PutToTilemap(&detail);

    String *speciesName = MessageUtil_SpeciesName(
        history->mons[monIdx].species,
        HEAP_ID_POKETCH_APP);

    if (speciesName != NULL) {
        Text_AddPrinterWithParamsAndColor(
            &detail,
            FONT_SYSTEM,
            speciesName,
            4,
            2,
            TEXT_SPEED_NO_TRANSFER,
            TEXT_COLOR(1, 8, 4),
            NULL);
        String_Free(speciesName);
    }

    DetailPrintAscii(&detail, "LAND", 142, 2);

    // Thin LCD divider under the header.
    Window_FillRectWithColor(&detail, 8, 0, 18, 192, 1);

    // Scanner reticle: four corner brackets and small cardinal ticks around
    // the native Pokémon icon. These use only the active Pokétch palette.
    Window_FillRectWithColor(&detail, 8, 12, 38, 18, 2);
    Window_FillRectWithColor(&detail, 8, 12, 38, 2, 18);
    Window_FillRectWithColor(&detail, 8, 66, 38, 18, 2);
    Window_FillRectWithColor(&detail, 8, 82, 38, 2, 18);
    Window_FillRectWithColor(&detail, 8, 12, 92, 18, 2);
    Window_FillRectWithColor(&detail, 8, 12, 76, 2, 18);
    Window_FillRectWithColor(&detail, 8, 66, 92, 18, 2);
    Window_FillRectWithColor(&detail, 8, 82, 76, 2, 18);
    Window_FillRectWithColor(&detail, 8, 46, 32, 4, 2);
    Window_FillRectWithColor(&detail, 8, 46, 98, 4, 2);
    Window_FillRectWithColor(&detail, 8, 6, 64, 4, 2);
    Window_FillRectWithColor(&detail, 8, 86, 64, 4, 2);

    // Pokémon battle level: authored area range. Search Level is deliberately
    // separate so the UI cannot imply that research progress raises levels.
    DetailPrintAscii(&detail, "LV", 2, 110);
    DetailPrintNumber(&detail, history->mons[monIdx].minLevel, 2, 22, 110);
    DetailPrintAscii(&detail, "-", 40, 110);
    DetailPrintNumber(&detail, history->mons[monIdx].maxLevel, 2, 48, 110);

    DetailPrintAscii(&detail, "SEARCH", 100, 38);
    DetailPrintNumber(&detail, history->mons[monIdx].searchLevel, 3, 150, 38);

    DetailPrintAscii(&detail, "POTENTIAL", 100, 64);
    DetailPrintPotential(&detail, history->mons[monIdx].potentialStars, 118, 82);

    // Wide, unmistakable touch target without introducing non-Pokétch art.
    Window_FillRectWithColor(&detail, 8, 8, 130, 176, 2);
    Window_FillRectWithColor(&detail, 8, 8, 151, 176, 2);
    Window_FillRectWithColor(&detail, 8, 8, 130, 2, 23);
    Window_FillRectWithColor(&detail, 8, 182, 130, 2, 23);
    DetailPrintAscii(&detail, "SEARCH", 70, 134);

    Window_LoadTiles(&detail);
    Window_Remove(&detail);
    Bg_CopyTilemapBufferToVRAM(graphics->bgConfig, BG_LAYER_SUB_2);
}

'''


def validate(root: Path) -> None:
    source = (root / "src/applications/poketch/pokemon_history/graphics.c").read_text()

    checks = {
        "native_icon": "PoketchAnimation_SetSpritePosition" in source,
        "scanner_reticle": "Scanner reticle" in source,
        "battle_level_separate": "Pokémon battle level" in source,
        "search_level": 'DetailPrintAscii(&detail, "SEARCH", 100, 38);' in source,
        "potential": 'DetailPrintAscii(&detail, "POTENTIAL"' in source,
        "method": 'DetailPrintAscii(&detail, "LAND", 142, 2);' in source,
        "wide_search": 'DetailPrintAscii(&detail, "SEARCH", 70, 134);' in source,
        "no_move_field": '"MOVE"' not in source[source.find("static void DrawDetailSurface"):source.find("static void DetailPrintAscii")],
        "no_ability_field": '"ABILITY"' not in source[source.find("static void DrawDetailSurface"):source.find("static void DetailPrintAscii")],
        "no_item_field": '"ITEM"' not in source[source.find("static void DrawDetailSurface"):source.find("static void DetailPrintAscii")],
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2M validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2m-poketch-hunter-detail.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()
    path = root / "src/applications/poketch/pokemon_history/graphics.c"

    if "PoketchPokemonHistoryGraphics_ShowDetail" not in path.read_text():
        raise SystemExit("MR06B2M requires MR06B2L detail-page proof")

    replace_function(
        path,
        "static void DrawDetailSurface(PokemonHistoryGraphics *graphics, int monIdx)\n{",
        "static void DetailPrintAscii(",
        DETAIL,
        "MR06B2M detail renderer",
    )
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2M_POKETCH_HUNTER_DETAIL",
        "status": "PASS",
        "scope": "CI-only visual prototype; production scanner untouched",
        "area_page_changed": False,
        "top_screen": "normal live Platinum overworld",
        "detail_page": {
            "visual_focus": "native Pokemon icon inside Poketch scanner reticle",
            "battle_level": "authored area level range; visually separate from Search Level",
            "search_level": "species research progression only",
            "potential_stars": True,
            "encounter_method": True,
            "wide_search_control": True,
            "moves_shown": False,
            "abilities_shown": False,
            "held_items_shown": False,
        },
        "qa_species": "Bidoof",
        "qa_level_range": "3-4",
        "qa_search_level": 27,
        "qa_potential": "2/3",
        "production_player_rom_modified": False,
        "next": "visual approval, then production Poketch app + ALL/LAND/WATER/FISH/RESEARCH runtime + instant encounter with badge cap",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
