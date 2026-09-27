#!/usr/bin/env python3
"""MR06B2J — clear uninitialized scanner BG tiles.

MR06B2I made the scanner runtime-addressable, exposing a separate visual bug:
all five scanner BG layers referenced tile 0 for unused space, but tile 0's
character data was never initialized. On hardware/DeSmuME this appears as
repeating green/striped VRAM garbage behind otherwise-correct text and icons.

Zero the blank tile on every scanner BG character base. This changes no target
logic, encounter data, or Radar behavior.
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


def patch_scanner(root: Path) -> None:
    path = root / "src/applications/mercury_research_radar.c"

    anchor = """    Bg_InitFromTemplate(app->bgConfig, BG_LAYER_SUB_2, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(app->bgConfig, BG_LAYER_SUB_2);

    Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_2, 1, 1, 1);

    Bg_ToggleLayer(BG_LAYER_MAIN_0, TRUE);
"""
    replacement = """    Bg_InitFromTemplate(app->bgConfig, BG_LAYER_SUB_2, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(app->bgConfig, BG_LAYER_SUB_2);

    // Every empty tilemap cell points at character tile 0. Nitro VRAM is not
    // guaranteed to begin zeroed, so initialize tile 0 on each distinct BG
    // character base before the transparent text/icon layers are shown.
    Bg_FillTilesRange(app->bgConfig, BG_LAYER_MAIN_0, 0, 1, 0);
    Bg_FillTilesRange(app->bgConfig, BG_LAYER_MAIN_1, 0, 1, 0);
    Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_0, 0, 1, 0);
    Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_1, 0, 1, 0);
    Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_2, 0, 1, 0);

    // Tile 1 on SUB_2 is the selection highlight behind the Pokémon icon.
    Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_2, 1, 1, 1);

    Bg_ToggleLayer(BG_LAYER_MAIN_0, TRUE);
"""
    replace_once(path, anchor, replacement, "MR06B2J scanner blank-tile init")


def validate(root: Path) -> None:
    source = (root / "src/applications/mercury_research_radar.c").read_text()
    lsf = (root / "platinum.us/main.lsf").read_text()
    start_menu = (root / "src/start_menu.c").read_text()

    required = (
        "Bg_FillTilesRange(app->bgConfig, BG_LAYER_MAIN_0, 0, 1, 0);",
        "Bg_FillTilesRange(app->bgConfig, BG_LAYER_MAIN_1, 0, 1, 0);",
        "Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_0, 0, 1, 0);",
        "Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_1, 0, 1, 0);",
        "Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_2, 0, 1, 0);",
    )
    for token in required:
        if token not in source:
            raise SystemExit(f"MR06B2J scanner missing {token}")

    checks = {
        "scanner_linked_static":
            "Object main.nef.p/src_applications_mercury_research_radar.c.o" in lsf,
        "selection_highlight_retained":
            "Bg_FillTilesRange(app->bgConfig, BG_LAYER_SUB_2, 1, 1, 1);" in source,
        "standalone_encounter_menu_absent":
            "START_MENU_OPTION_ENCOUNTERS" not in start_menu,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2J validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2j-scanner-vram-cleanup.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    scanner = root / "src/applications/mercury_research_radar.c"
    if not scanner.exists():
        raise SystemExit("MR06B2J requires MR06B2C2 scanner application")

    patch_scanner(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2J_SCANNER_VRAM_CLEANUP",
        "status": "PASS",
        "root_cause": "scanner BG tile 0 character data was uninitialized VRAM",
        "blank_tile_initialized_layers": [
            "MAIN_0",
            "MAIN_1",
            "SUB_0",
            "SUB_1",
            "SUB_2",
        ],
        "selection_highlight_retained": True,
        "target_logic_modified": False,
        "normal_encounter_tables_modified": False,
        "standalone_encounter_menu": False,
        "ready_for_visual_retest": True,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
