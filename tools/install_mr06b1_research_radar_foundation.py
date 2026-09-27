#!/usr/bin/env python3
"""MR06B1 — Research Poké Radar scanner data foundation.

Runs after the sealed MR06A encounter runtime. This phase does not add a
standalone Encounter Chart menu and does not change ordinary wild encounters.

It exposes a compact, land-only target list for the current map that the
Poké Radar UI can consume:
- Mercury Morning / Day / Evening / Night authored land species;
- the four existing Platinum radar-only slots as a compatibility layer;
- merged duplicate species and exact level ranges from the live encounter NARC.

Surf, fishing, Honey Trees, Great Marsh special presentation, statics, gifts,
and trades are deliberately outside this API.

The fixed Mercury Research habitat layer is added in MR06B3. Until then the
existing Platinum radar slots are tagged as LEGACY_RESEARCH so the scanner/UI
can distinguish them from normal land ecology without overwriting either.
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

    anchor = """typedef struct MercuryEncounterChartSlot {
    int species;
    u8 minLevel;
    u8 maxLevel;
    u8 chancePercent;
    u8 padding;
} MercuryEncounterChartSlot;

#include "field_battle_data_transfer.h"
"""

    replacement = """typedef struct MercuryEncounterChartSlot {
    int species;
    u8 minLevel;
    u8 maxLevel;
    u8 chancePercent;
    u8 padding;
} MercuryEncounterChartSlot;

#define MERCURY_RESEARCH_RADAR_MAX_TARGETS 16

enum MercuryResearchRadarTargetSource {
    MERCURY_RESEARCH_RADAR_SOURCE_NORMAL = (1 << 0),
    MERCURY_RESEARCH_RADAR_SOURCE_LEGACY_RESEARCH = (1 << 1),
};

typedef struct MercuryResearchRadarTarget {
    int species;
    u8 minLevel;
    u8 maxLevel;
    u8 sourceFlags;
    u8 padding;
} MercuryResearchRadarTarget;

#include "field_battle_data_transfer.h"
"""
    replace_once(path, anchor, replacement, "MR06B1 radar target types")

    proto_anchor = """BOOL MercuryEncounterChart_GetSlot(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method, int slotIndex, MercuryEncounterChartSlot *slot);

void WildEncounters_ReplaceTimedEncounters"""
    proto_replacement = """BOOL MercuryEncounterChart_GetSlot(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method, int slotIndex, MercuryEncounterChartSlot *slot);

int MercuryResearchRadar_GetTargets(
    enum MapHeaderID mapHeaderID,
    enum MercuryEncounterChartMethod landPeriod,
    MercuryResearchRadarTarget *targets,
    int maxTargets);

void WildEncounters_ReplaceTimedEncounters"""
    replace_once(path, proto_anchor, proto_replacement, "MR06B1 radar target prototype")


def patch_runtime(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"

    anchor = """void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *timedSlot1, int *timedSlot2)
{
"""

    helpers = r'''static void MercuryResearchRadar_AddTarget(
    MercuryResearchRadarTarget *targets,
    int *count,
    int maxTargets,
    int species,
    u8 minLevel,
    u8 maxLevel,
    u8 sourceFlags)
{
    if (species == SPECIES_NONE || targets == NULL || count == NULL || *count >= maxTargets) {
        return;
    }

    for (int i = 0; i < *count; i++) {
        if (targets[i].species == species) {
            targets[i].minLevel = min(targets[i].minLevel, minLevel);
            targets[i].maxLevel = max(targets[i].maxLevel, maxLevel);
            targets[i].sourceFlags |= sourceFlags;
            return;
        }
    }

    MercuryResearchRadarTarget *target = &targets[*count];
    target->species = species;
    target->minLevel = minLevel;
    target->maxLevel = maxLevel;
    target->sourceFlags = sourceFlags;
    target->padding = 0;
    (*count)++;
}

int MercuryResearchRadar_GetTargets(
    enum MapHeaderID mapHeaderID,
    enum MercuryEncounterChartMethod landPeriod,
    MercuryResearchRadarTarget *targets,
    int maxTargets)
{
    if (targets == NULL || maxTargets <= 0) {
        return 0;
    }

    if (maxTargets > MERCURY_RESEARCH_RADAR_MAX_TARGETS) {
        maxTargets = MERCURY_RESEARCH_RADAR_MAX_TARGETS;
    }

    if (landPeriod < MERCURY_ENCOUNTER_METHOD_LAND_MORNING
        || landPeriod > MERCURY_ENCOUNTER_METHOD_LAND_NIGHT) {
        landPeriod = MercuryEncounterChart_GetCurrentLandMethod();
    }

    int areaIndex = MercuryEncounterChart_FindAreaByMapHeader(mapHeaderID);
    if (areaIndex < 0) {
        return 0;
    }

    WildEncounters encounterData;
    MercuryEncounterChart_LoadArea(areaIndex, &encounterData);

    if (!MercuryEncounterChart_HasMethod(&encounterData, landPeriod)) {
        return 0;
    }

    int count = 0;
    u8 areaMinLevel = 100;
    u8 areaMaxLevel = 1;

    for (int slotIndex = 0; slotIndex < MAX_GRASS_ENCOUNTERS; slotIndex++) {
        MercuryEncounterChartSlot slot;

        if (!MercuryEncounterChart_GetSlot(&encounterData, landPeriod, slotIndex, &slot)) {
            continue;
        }

        areaMinLevel = min(areaMinLevel, slot.minLevel);
        areaMaxLevel = max(areaMaxLevel, slot.maxLevel);

        MercuryResearchRadar_AddTarget(
            targets,
            &count,
            maxTargets,
            slot.species,
            slot.minLevel,
            slot.maxLevel,
            MERCURY_RESEARCH_RADAR_SOURCE_NORMAL);
    }

    // Platinum stores four radar-only species in each WildEncounters member.
    // Keep them visible to the Research Radar as a compatibility layer for
    // MR06B1/2. MR06B3 replaces/extends this with Mercury's fixed authored
    // Research habitat table rather than a daily or chain-based lottery.
    if (areaMinLevel <= areaMaxLevel) {
        for (int i = 0; i < 4; i++) {
            MercuryResearchRadar_AddTarget(
                targets,
                &count,
                maxTargets,
                encounterData.radarEncounters[i],
                areaMinLevel,
                areaMaxLevel,
                MERCURY_RESEARCH_RADAR_SOURCE_LEGACY_RESEARCH);
        }
    }

    return count;
}

void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *timedSlot1, int *timedSlot2)
{
'''

    replace_once(path, anchor, helpers, "MR06B1 radar target runtime")


def validate(root: Path) -> None:
    header = (root / "include/overlay006/wild_encounters.h").read_text()
    runtime = (root / "src/overlay006/wild_encounters.c").read_text()
    start_menu = (root / "src/start_menu.c").read_text()

    required_header = (
        "MERCURY_RESEARCH_RADAR_MAX_TARGETS 16",
        "MercuryResearchRadarTarget",
        "MercuryResearchRadar_GetTargets",
    )
    for token in required_header:
        if token not in header:
            raise SystemExit(f"MR06B1 header missing {token}")

    required_runtime = (
        "MercuryResearchRadar_AddTarget",
        "MERCURY_RESEARCH_RADAR_SOURCE_NORMAL",
        "MERCURY_RESEARCH_RADAR_SOURCE_LEGACY_RESEARCH",
        "encounterData.radarEncounters[i]",
    )
    for token in required_runtime:
        if token not in runtime:
            raise SystemExit(f"MR06B1 runtime missing {token}")

    # Explicit regression guard: the rejected general Start Menu browser must
    # never leak into the production Research Radar branch.
    forbidden = (
        "START_MENU_OPTION_ENCOUNTERS",
        "StartMenu_Text_Encounters",
        "START_MENU_STATE_MERCURY_ENCOUNTER_CHART",
    )
    for token in forbidden:
        if token in start_menu:
            raise SystemExit(f"MR06B1 standalone encounter menu regression: {token}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06b1-research-radar-foundation.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    header = (root / "include/overlay006/wild_encounters.h").read_text()
    if "MercuryEncounterChart_GetAreaCount" not in header:
        raise SystemExit("MR06B1 requires the sealed MR06A encounter runtime")

    patch_header(root)
    patch_runtime(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B1_RESEARCH_RADAR_FOUNDATION",
        "status": "PASS",
        "standalone_encounter_menu": False,
        "player_facing_entrypoint": "ITEM_POKE_RADAR (UI binding follows in MR06B1B)",
        "normal_land_targets_from_live_runtime": True,
        "current_land_periods_supported": ["morning", "day", "evening", "night"],
        "legacy_platinum_radar_slots_exposed": 4,
        "legacy_slots_tagged_separately": True,
        "fixed_mercury_research_habitats": "deferred to MR06B3 authored import",
        "surf_targets": False,
        "fishing_targets": False,
        "honey_tree_targets": False,
        "great_marsh_special_view": False,
        "normal_encounter_tables_modified": False,
        "chain_behavior_modified": False,
        "battery_behavior_modified": False,
        "ready_for_item_scanner_ui": True,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
