#!/usr/bin/env python3
"""MR06B2I — place new Radar code in the correct Nitro linker regions.

pret/pokeplatinum does not infer Nitro overlay placement from src/meson.build.
Every new C object must also be assigned in platinum.us/main.lsf. The scanner
and HUD previously compiled, but their unassigned functions could resolve to
zero/unrelated overlay addresses at runtime.

This pass:
- places the scanner application in Static main;
- places the overworld HUD in overlay5;
- removes scanner-time calls into overlay6 after the field process is unloaded.

The only overlay6 call retained by the scanner path is
MercuryResearchRadar_InitScannerState(), which executes before the child
application starts while the field/overlay6 is still live.
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


def patch_linker_spec(root: Path) -> None:
    path = root / "platinum.us/main.lsf"

    replace_once(
        path,
        "\tObject main.nef.p/src_applications_town_map_context.c.o\n"
        "\tObject main.nef.p/src_unk_0206B9D8.c.o\n",
        "\tObject main.nef.p/src_applications_town_map_context.c.o\n"
        "\tObject main.nef.p/src_applications_mercury_research_radar.c.o\n"
        "\tObject main.nef.p/src_unk_0206B9D8.c.o\n",
        "MR06B2I scanner Static-main placement",
    )

    replace_once(
        path,
        "\tObject main.nef.p/src_overlay005_map_name_popup.c.o\n"
        "\tObject main.nef.p/src_overlay005_enable_poketch_task.c.o\n",
        "\tObject main.nef.p/src_overlay005_map_name_popup.c.o\n"
        "\tObject main.nef.p/src_overlay005_mercury_radar_hud.c.o\n"
        "\tObject main.nef.p/src_overlay005_enable_poketch_task.c.o\n",
        "MR06B2I HUD overlay5 placement",
    )


def patch_scanner_overlay_boundary(root: Path) -> None:
    path = root / "src/applications/mercury_research_radar.c"
    text = path.read_text()

    # Scanner navigation executes after FieldSystem_StartChildProcess has caused
    # the field map and overlay6 to unload. Keep all child-app state operations
    # in Static main instead of jumping back into overlay6.
    count = text.count(
        "MercuryResearchRadar_GetSelectedTarget(&app->args->scanner)"
    )
    if count < 2:
        raise SystemExit(
            "MR06B2I expected scanner selected-target calls, "
            f"found {count}"
        )
    text = text.replace(
        "MercuryResearchRadar_GetSelectedTarget(&app->args->scanner)",
        "MercuryResearchRadarApp_GetSelectedTarget(app)",
    )

    count = text.count(
        "MercuryResearchRadar_RegisterSelected(&app->args->scanner, pokedex)"
    )
    if count != 1:
        raise SystemExit(
            "MR06B2I expected one scanner registration call, "
            f"found {count}"
        )
    text = text.replace(
        "MercuryResearchRadar_RegisterSelected(&app->args->scanner, pokedex)",
        "MercuryResearchRadarApp_RegisterSelected(app, pokedex)",
        1,
    )

    old_search_level = """    u16 searchLevel = MercuryResearchRadar_GetSelectedSearchLevel(
        &app->args->scanner,
        pokedex);
"""
    new_search_level = """    u16 searchLevel = Pokedex_MercuryRadar_GetSearchLevel(
        pokedex,
        (u16)target->species);
"""
    if text.count(old_search_level) != 1:
        raise SystemExit("MR06B2I scanner Search-Level bridge anchor missing")
    text = text.replace(old_search_level, new_search_level, 1)

    decl_anchor = """static BOOL MercuryResearchRadarApp_HandleTouch(MercuryResearchRadarApp *app);
static BOOL MercuryResearchRadarApp_MoveSelection(MercuryResearchRadarApp *app, int delta);
static void MercuryResearchRadarApp_PrintAscii"""
    decl_replacement = """static BOOL MercuryResearchRadarApp_HandleTouch(MercuryResearchRadarApp *app);
static BOOL MercuryResearchRadarApp_MoveSelection(MercuryResearchRadarApp *app, int delta);
static const MercuryResearchRadarTarget *MercuryResearchRadarApp_GetSelectedTarget(
    const MercuryResearchRadarApp *app);
static BOOL MercuryResearchRadarApp_RegisterSelected(
    MercuryResearchRadarApp *app,
    Pokedex *pokedex);
static void MercuryResearchRadarApp_PrintAscii"""
    if text.count(decl_anchor) != 1:
        raise SystemExit("MR06B2I scanner local helper declaration anchor missing")
    text = text.replace(decl_anchor, decl_replacement, 1)

    move_anchor = """static BOOL MercuryResearchRadarApp_MoveSelection(
    MercuryResearchRadarApp *app,
    int delta)
{
    return MercuryResearchRadar_MoveSelection(&app->args->scanner, delta);
}
"""
    move_replacement = """static BOOL MercuryResearchRadarApp_MoveSelection(
    MercuryResearchRadarApp *app,
    int delta)
{
    MercuryResearchRadarScannerState *scanner = &app->args->scanner;

    if (scanner->targetCount == 0 || delta == 0) {
        return FALSE;
    }

    int next = (int)scanner->selectedIndex + delta;

    while (next < 0) {
        next += scanner->targetCount;
    }

    while (next >= scanner->targetCount) {
        next -= scanner->targetCount;
    }

    if (next == scanner->selectedIndex) {
        return FALSE;
    }

    scanner->selectedIndex = next;
    return TRUE;
}

static const MercuryResearchRadarTarget *MercuryResearchRadarApp_GetSelectedTarget(
    const MercuryResearchRadarApp *app)
{
    const MercuryResearchRadarScannerState *scanner = &app->args->scanner;

    if (scanner->targetCount == 0
        || scanner->selectedIndex >= scanner->targetCount) {
        return NULL;
    }

    return &scanner->targets[scanner->selectedIndex];
}

static BOOL MercuryResearchRadarApp_RegisterSelected(
    MercuryResearchRadarApp *app,
    Pokedex *pokedex)
{
    const MercuryResearchRadarTarget *target =
        MercuryResearchRadarApp_GetSelectedTarget(app);

    if (target == NULL || pokedex == NULL) {
        return FALSE;
    }

    Pokedex_MercuryRadar_SetRegisteredSpecies(
        pokedex,
        (u16)target->species);
    app->args->scanner.registeredSpecies = (u16)target->species;
    return TRUE;
}
"""
    if text.count(move_anchor) != 1:
        raise SystemExit("MR06B2I scanner MoveSelection implementation anchor missing")
    text = text.replace(move_anchor, move_replacement, 1)

    path.write_text(text)


def validate(root: Path) -> None:
    lsf = (root / "platinum.us/main.lsf").read_text()
    scanner = (root / "src/applications/mercury_research_radar.c").read_text()
    meson = (root / "src/meson.build").read_text()

    scanner_obj = "Object main.nef.p/src_applications_mercury_research_radar.c.o"
    hud_obj = "Object main.nef.p/src_overlay005_mercury_radar_hud.c.o"

    static_start = lsf.index("Static main")
    overlay5_start = lsf.index("Overlay overlay5")
    overlay6_start = lsf.index("Overlay overlay6")

    static_block = lsf[static_start:overlay5_start]
    overlay5_block = lsf[overlay5_start:overlay6_start]

    checks = {
        "scanner_compiled": "'applications/mercury_research_radar.c'," in meson,
        "hud_compiled": "'overlay005/mercury_radar_hud.c'," in meson,
        "scanner_in_static_main": scanner_obj in static_block,
        "scanner_not_overlay5": scanner_obj not in overlay5_block,
        "hud_in_overlay5": hud_obj in overlay5_block,
        "child_selection_main_safe":
            "MercuryResearchRadar_MoveSelection(&app->args->scanner" not in scanner,
        "child_selected_target_main_safe":
            "MercuryResearchRadar_GetSelectedTarget(&app->args->scanner" not in scanner,
        "child_registration_main_safe":
            "MercuryResearchRadar_RegisterSelected(&app->args->scanner" not in scanner,
        "child_search_level_main_safe":
            "MercuryResearchRadar_GetSelectedSearchLevel(" not in scanner,
        "pre_child_target_snapshot_retained":
            "MercuryResearchRadar_InitScannerState(" in scanner,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2I validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2i-radar-linker-placement.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    scanner = root / "src/applications/mercury_research_radar.c"
    hud = root / "src/overlay005/mercury_radar_hud.c"
    if not scanner.exists() or not hud.exists():
        raise SystemExit("MR06B2I requires MR06B2C2 and MR06B2E")

    patch_linker_spec(root)
    patch_scanner_overlay_boundary(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2I_RADAR_NITRO_LINKER_PLACEMENT",
        "status": "PASS",
        "root_cause_fixed": (
            "new C files were compiled by Meson but absent from platinum.us/main.lsf, "
            "leaving runtime function addresses unassigned"
        ),
        "scanner_object_region": "Static main",
        "hud_object_region": "overlay5",
        "scanner_child_overlay6_calls_removed": [
            "MoveSelection",
            "GetSelectedTarget",
            "RegisterSelected",
            "GetSelectedSearchLevel",
        ],
        "pre_child_overlay6_snapshot_call_retained": "MercuryResearchRadar_InitScannerState",
        "normal_encounter_tables_modified": False,
        "player_facing_design_modified": False,
        "ready_for_runtime_visual_retest": True,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
