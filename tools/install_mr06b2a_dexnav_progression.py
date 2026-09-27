#!/usr/bin/env python3
"""MR06B2A — Elite Redux-style Research Poké Radar progression model.

This phase adds the data model the DS scanner UI and targeted encounter
generator consume. It deliberately does NOT alter normal wild encounter tables,
start-menu layout, Honey Trees, Surf/fishing, or Great Marsh behavior.

The milestone bands and quality probabilities are adapted from Elite Redux's
DexNav design:
0-4, 5-9, 10-24, 25-49, 50-99, 100+.

Mercury differences:
- Search Level is planned per species and capped at 999.
- Chaining is never required.
- Radar quality affects the Pokémon's Primary Ability only; species Innates are
  controlled by Mercury's global Innate Abilities toggle.
- Shiny tuning is kept out of this phase until the targeted-battle generator is
  installed, so it can be balanced against Mercury's final shiny system.
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

    anchor = """typedef struct MercuryResearchRadarTarget {
    int species;
    u8 minLevel;
    u8 maxLevel;
    u8 sourceFlags;
    u8 padding;
} MercuryResearchRadarTarget;

#include "field_battle_data_transfer.h"
"""

    replacement = """typedef struct MercuryResearchRadarTarget {
    int species;
    u8 minLevel;
    u8 maxLevel;
    u8 sourceFlags;
    u8 padding;
} MercuryResearchRadarTarget;

#define MERCURY_RESEARCH_RADAR_SEARCH_LEVEL_CAP 999

typedef struct MercuryResearchRadarQualityProfile {
    u8 specialMoveChance;
    u8 rarePrimaryAbilityChance;
    u8 heldItemChance;
    u8 oneStarChance;
    u8 twoStarChance;
    u8 threeStarChance;
} MercuryResearchRadarQualityProfile;

#include "field_battle_data_transfer.h"
"""
    replace_once(path, anchor, replacement, "MR06B2A quality profile type")

    proto_anchor = """int MercuryResearchRadar_GetTargets(
    enum MapHeaderID mapHeaderID,
    enum MercuryEncounterChartMethod landPeriod,
    MercuryResearchRadarTarget *targets,
    int maxTargets);

void WildEncounters_ReplaceTimedEncounters"""
    proto_replacement = """int MercuryResearchRadar_GetTargets(
    enum MapHeaderID mapHeaderID,
    enum MercuryEncounterChartMethod landPeriod,
    MercuryResearchRadarTarget *targets,
    int maxTargets);

u16 MercuryResearchRadar_ClampSearchLevel(u16 searchLevel);
u8 MercuryResearchRadar_GetSearchTier(u16 searchLevel);
void MercuryResearchRadar_GetQualityProfile(
    u16 searchLevel,
    MercuryResearchRadarQualityProfile *profile);

void WildEncounters_ReplaceTimedEncounters"""
    replace_once(path, proto_anchor, proto_replacement, "MR06B2A quality profile API")


def patch_runtime(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"

    anchor = """void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *timedSlot1, int *timedSlot2)
{
"""

    helpers = r'''u16 MercuryResearchRadar_ClampSearchLevel(u16 searchLevel)
{
    if (searchLevel > MERCURY_RESEARCH_RADAR_SEARCH_LEVEL_CAP) {
        return MERCURY_RESEARCH_RADAR_SEARCH_LEVEL_CAP;
    }

    return searchLevel;
}

u8 MercuryResearchRadar_GetSearchTier(u16 searchLevel)
{
    searchLevel = MercuryResearchRadar_ClampSearchLevel(searchLevel);

    if (searchLevel < 5) {
        return 0;
    }

    if (searchLevel < 10) {
        return 1;
    }

    if (searchLevel < 25) {
        return 2;
    }

    if (searchLevel < 50) {
        return 3;
    }

    if (searchLevel < 100) {
        return 4;
    }

    return 5;
}

void MercuryResearchRadar_GetQualityProfile(
    u16 searchLevel,
    MercuryResearchRadarQualityProfile *profile)
{
    static const MercuryResearchRadarQualityProfile sProfiles[] = {
        // special move, rare Primary Ability, held item, 1-star, 2-star, 3-star
        {  0,  0,  0,  0,  0,  0 }, // Search Lv. 0-4
        { 21,  0,  0, 14,  1,  0 }, // Search Lv. 5-9
        { 46,  5,  1, 17,  9,  1 }, // Search Lv. 10-24
        { 58, 15,  7, 17, 16,  7 }, // Search Lv. 25-49
        { 63, 20,  6, 15, 17,  6 }, // Search Lv. 50-99
        { 83, 23, 12,  8, 24, 12 }, // Search Lv. 100+
    };

    if (profile == NULL) {
        return;
    }

    *profile = sProfiles[MercuryResearchRadar_GetSearchTier(searchLevel)];
}

void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *timedSlot1, int *timedSlot2)
{
'''
    replace_once(path, anchor, helpers, "MR06B2A quality profile runtime")


def validate(root: Path) -> None:
    header = (root / "include/overlay006/wild_encounters.h").read_text()
    runtime = (root / "src/overlay006/wild_encounters.c").read_text()
    start_menu = (root / "src/start_menu.c").read_text()

    required = (
        "MERCURY_RESEARCH_RADAR_SEARCH_LEVEL_CAP 999",
        "MercuryResearchRadarQualityProfile",
        "MercuryResearchRadar_GetSearchTier",
        "MercuryResearchRadar_GetQualityProfile",
        "{ 21,  0,  0, 14,  1,  0 }",
        "{ 83, 23, 12,  8, 24, 12 }",
    )
    combined = header + runtime
    for token in required:
        if token not in combined:
            raise SystemExit(f"MR06B2A missing {token}")

    if "START_MENU_OPTION_ENCOUNTERS" in start_menu:
        raise SystemExit("MR06B2A standalone encounter menu regression")

    # No player-visible target source other than land / research may leak in.
    if "MERCURY_RESEARCH_RADAR_SOURCE_SURF" in combined:
        raise SystemExit("MR06B2A Surf targeting regression")
    if "MERCURY_RESEARCH_RADAR_SOURCE_FISHING" in combined:
        raise SystemExit("MR06B2A fishing targeting regression")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06b2a-dexnav-progression.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    header = (root / "include/overlay006/wild_encounters.h").read_text()

    if "MercuryResearchRadar_GetTargets" not in header:
        raise SystemExit("MR06B2A requires MR06B1 Research Radar foundation")

    patch_header(root)
    patch_runtime(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2A_DEXNAV_PROGRESSION_MODEL",
        "status": "PASS",
        "inspiration": "Elite Redux DexNav search-quality milestone model",
        "search_level_cap": 999,
        "per_species_persistence": "next save-data subphase",
        "tiers": [
            {"range": "0-4", "special_move": 0, "rare_primary_ability": 0, "held_item": 0, "stars": [0, 0, 0]},
            {"range": "5-9", "special_move": 21, "rare_primary_ability": 0, "held_item": 0, "stars": [14, 1, 0]},
            {"range": "10-24", "special_move": 46, "rare_primary_ability": 5, "held_item": 1, "stars": [17, 9, 1]},
            {"range": "25-49", "special_move": 58, "rare_primary_ability": 15, "held_item": 7, "stars": [17, 16, 7]},
            {"range": "50-99", "special_move": 63, "rare_primary_ability": 20, "held_item": 6, "stars": [15, 17, 6]},
            {"range": "100+", "special_move": 83, "rare_primary_ability": 23, "held_item": 12, "stars": [8, 24, 12]},
        ],
        "primary_ability_only": True,
        "innates_unchanged": True,
        "chain_required": False,
        "battery_recharge_required": False,
        "normal_encounter_tables_modified": False,
        "surf_targets": False,
        "fishing_targets": False,
        "shiny_bonus": "deferred to targeted-battle generator for final balancing",
        "ready_for_scanner_ui": True,
        "ready_for_search_level_save_storage": True,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
