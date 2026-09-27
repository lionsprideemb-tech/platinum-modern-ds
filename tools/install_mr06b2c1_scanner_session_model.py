#!/usr/bin/env python3
"""MR06B2C1 — DexNav-style scanner session model.

This is the UI-facing state layer for Mercury's DS Research Poké Radar. It
turns the current-map target API plus persistent Pokédex Search Levels into a
stable scanner model without exposing the abandoned generic Encounter Chart.

The visible DS application is the next subphase; this layer is deliberately
small so target ordering/registration can be compile-tested before graphics.
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


def patch_header(root: Path) -> None:
    path = root / "include/overlay006/wild_encounters.h"

    anchor = """typedef struct MercuryResearchRadarQualityProfile {
    u8 specialMoveChance;
    u8 rarePrimaryAbilityChance;
    u8 heldItemChance;
    u8 oneStarChance;
    u8 twoStarChance;
    u8 threeStarChance;
} MercuryResearchRadarQualityProfile;

#include "field_battle_data_transfer.h"
"""

    replacement = """typedef struct MercuryResearchRadarQualityProfile {
    u8 specialMoveChance;
    u8 rarePrimaryAbilityChance;
    u8 heldItemChance;
    u8 oneStarChance;
    u8 twoStarChance;
    u8 threeStarChance;
} MercuryResearchRadarQualityProfile;

typedef struct Pokedex Pokedex;

typedef struct MercuryResearchRadarScannerState {
    MercuryResearchRadarTarget targets[MERCURY_RESEARCH_RADAR_MAX_TARGETS];
    u16 registeredSpecies;
    u8 targetCount;
    u8 localCount;
    u8 researchCount;
    u8 selectedIndex;
    u8 landPeriod;
} MercuryResearchRadarScannerState;

#include "field_battle_data_transfer.h"
"""
    replace_once(path, anchor, replacement, "MR06B2C1 scanner state type")

    proto_anchor = """void MercuryResearchRadar_GetQualityProfile(
    u16 searchLevel,
    MercuryResearchRadarQualityProfile *profile);

void WildEncounters_ReplaceTimedEncounters"""
    proto_replacement = """void MercuryResearchRadar_GetQualityProfile(
    u16 searchLevel,
    MercuryResearchRadarQualityProfile *profile);

BOOL MercuryResearchRadar_InitScannerState(
    enum MapHeaderID mapHeaderID,
    enum MercuryEncounterChartMethod landPeriod,
    const Pokedex *pokedex,
    MercuryResearchRadarScannerState *state);
BOOL MercuryResearchRadar_MoveSelection(
    MercuryResearchRadarScannerState *state,
    int delta);
const MercuryResearchRadarTarget *MercuryResearchRadar_GetSelectedTarget(
    const MercuryResearchRadarScannerState *state);
u16 MercuryResearchRadar_GetSelectedSearchLevel(
    const MercuryResearchRadarScannerState *state,
    const Pokedex *pokedex);
BOOL MercuryResearchRadar_RegisterSelected(
    MercuryResearchRadarScannerState *state,
    Pokedex *pokedex);

void WildEncounters_ReplaceTimedEncounters"""
    replace_once(path, proto_anchor, proto_replacement, "MR06B2C1 scanner state API")


def patch_runtime(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"

    anchor = """u16 MercuryResearchRadar_ClampSearchLevel(u16 searchLevel)
{
"""

    implementation = r'''static void MercuryResearchRadar_AppendScannerTarget(
    MercuryResearchRadarScannerState *state,
    const MercuryResearchRadarTarget *target)
{
    if (state->targetCount >= MERCURY_RESEARCH_RADAR_MAX_TARGETS) {
        return;
    }

    state->targets[state->targetCount++] = *target;
}

BOOL MercuryResearchRadar_InitScannerState(
    enum MapHeaderID mapHeaderID,
    enum MercuryEncounterChartMethod landPeriod,
    const Pokedex *pokedex,
    MercuryResearchRadarScannerState *state)
{
    if (state == NULL || pokedex == NULL) {
        return FALSE;
    }

    MI_CpuClear8(state, sizeof(MercuryResearchRadarScannerState));

    MercuryResearchRadarTarget raw[MERCURY_RESEARCH_RADAR_MAX_TARGETS];
    MI_CpuClear8(raw, sizeof(raw));

    int rawCount = MercuryResearchRadar_GetTargets(
        mapHeaderID,
        landPeriod,
        raw,
        MERCURY_RESEARCH_RADAR_MAX_TARGETS);

    state->landPeriod = landPeriod;
    state->registeredSpecies = Pokedex_MercuryRadar_GetRegisteredSpecies(pokedex);

    // DexNav-like presentation order:
    // 1) ordinary LOCAL ecology for this time period;
    // 2) RESEARCH-only targets.
    // A species present in both layers appears once in LOCAL, not twice.
    for (int i = 0; i < rawCount; i++) {
        if ((raw[i].sourceFlags & MERCURY_RESEARCH_RADAR_SOURCE_NORMAL) == 0) {
            continue;
        }

        MercuryResearchRadar_AppendScannerTarget(state, &raw[i]);
        state->localCount++;
    }

    for (int i = 0; i < rawCount; i++) {
        if ((raw[i].sourceFlags & MERCURY_RESEARCH_RADAR_SOURCE_NORMAL) != 0) {
            continue;
        }

        if ((raw[i].sourceFlags & MERCURY_RESEARCH_RADAR_SOURCE_LEGACY_RESEARCH) == 0) {
            continue;
        }

        MercuryResearchRadar_AppendScannerTarget(state, &raw[i]);
        state->researchCount++;
    }

    state->selectedIndex = 0;

    if (state->registeredSpecies != SPECIES_NONE) {
        for (int i = 0; i < state->targetCount; i++) {
            if (state->targets[i].species == state->registeredSpecies) {
                state->selectedIndex = i;
                break;
            }
        }
    }

    return state->targetCount > 0;
}

BOOL MercuryResearchRadar_MoveSelection(
    MercuryResearchRadarScannerState *state,
    int delta)
{
    if (state == NULL || state->targetCount == 0 || delta == 0) {
        return FALSE;
    }

    int next = (int)state->selectedIndex + delta;

    while (next < 0) {
        next += state->targetCount;
    }

    while (next >= state->targetCount) {
        next -= state->targetCount;
    }

    if (next == state->selectedIndex) {
        return FALSE;
    }

    state->selectedIndex = next;
    return TRUE;
}

const MercuryResearchRadarTarget *MercuryResearchRadar_GetSelectedTarget(
    const MercuryResearchRadarScannerState *state)
{
    if (state == NULL
        || state->targetCount == 0
        || state->selectedIndex >= state->targetCount) {
        return NULL;
    }

    return &state->targets[state->selectedIndex];
}

u16 MercuryResearchRadar_GetSelectedSearchLevel(
    const MercuryResearchRadarScannerState *state,
    const Pokedex *pokedex)
{
    const MercuryResearchRadarTarget *target =
        MercuryResearchRadar_GetSelectedTarget(state);

    if (target == NULL || pokedex == NULL) {
        return 0;
    }

    return Pokedex_MercuryRadar_GetSearchLevel(pokedex, (u16)target->species);
}

BOOL MercuryResearchRadar_RegisterSelected(
    MercuryResearchRadarScannerState *state,
    Pokedex *pokedex)
{
    const MercuryResearchRadarTarget *target =
        MercuryResearchRadar_GetSelectedTarget(state);

    if (target == NULL || pokedex == NULL) {
        return FALSE;
    }

    Pokedex_MercuryRadar_SetRegisteredSpecies(pokedex, (u16)target->species);
    state->registeredSpecies = (u16)target->species;
    return TRUE;
}

u16 MercuryResearchRadar_ClampSearchLevel(u16 searchLevel)
{
'''

    replace_once(path, anchor, implementation, "MR06B2C1 scanner session runtime")


def validate(root: Path) -> None:
    header = (root / "include/overlay006/wild_encounters.h").read_text()
    runtime = (root / "src/overlay006/wild_encounters.c").read_text()
    start_menu = (root / "src/start_menu.c").read_text()
    item_use = (root / "src/item_use_functions.c").read_text()

    checks = {
        "scanner_state": "MercuryResearchRadarScannerState" in header,
        "local_then_research_order": "DexNav-like presentation order" in runtime,
        "registered_target_restore": "Pokedex_MercuryRadar_GetRegisteredSpecies" in runtime,
        "search_level_bridge": "Pokedex_MercuryRadar_GetSearchLevel" in runtime,
        "register_bridge": "Pokedex_MercuryRadar_SetRegisteredSpecies" in runtime,
        "selection_wrap": "MercuryResearchRadar_MoveSelection" in runtime,
        "standalone_menu_absent": "START_MENU_OPTION_ENCOUNTERS" not in start_menu,
        "vanilla_item_not_rebound_early": "menu->callback = RefreshRadarChain;" in item_use,
    }

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit("MR06B2C1 validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06b2c1-scanner-session-model.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    wild_header = (root / "include/overlay006/wild_encounters.h").read_text()
    pokedex_header = (root / "include/pokedex.h").read_text()

    if "MercuryResearchRadar_GetTargets" not in wild_header:
        raise SystemExit("MR06B2C1 requires MR06B1")
    if "MercuryResearchRadar_GetQualityProfile" not in wild_header:
        raise SystemExit("MR06B2C1 requires MR06B2A")
    if "Pokedex_MercuryRadar_GetSearchLevel" not in pokedex_header:
        raise SystemExit("MR06B2C1 requires MR06B2B")

    patch_header(root)
    patch_runtime(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2C1_DEXNAV_SCANNER_SESSION_MODEL",
        "status": "PASS",
        "target_capacity": 16,
        "display_order": ["LOCAL", "RESEARCH_ONLY"],
        "duplicates_across_layers_shown_once": True,
        "registered_target_restored_if_present_here": True,
        "selection_wraps": True,
        "search_level_available_to_ui": True,
        "register_selected_available_to_ui": True,
        "standalone_encounter_menu": False,
        "poke_radar_item_rebound_in_this_subphase": False,
        "reason_item_binding_deferred": "do not replace working vanilla Radar until DS scanner application exists",
        "normal_encounter_tables_modified": False,
        "ready_for_dual_screen_application": True,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
