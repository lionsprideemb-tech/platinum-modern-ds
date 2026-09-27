#!/usr/bin/env python3
"""MR06B2B — persist Research Poké Radar Search Level per species.

Search Level belongs with Pokédex knowledge, so Mercury stores it in the
expanded Mercury Pokedex save block rather than creating a parallel encounter
save table or reusing an unrelated online record.

The Mercury build already expands NATIONAL_DEX_COUNT through 1025. This phase
adds one u16 Search Level entry for every canonical species plus a registered
quick-search target. New-game initialization is automatic because Pokedex_Init
clears the complete structure before setting its normal sentinels.

No normal encounter table, Radar probability, chain logic, or UI is changed
here.
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
    path = root / "include/pokedex.h"

    struct_anchor = """    u8 shayminFormsSeen;
    u8 giratinaFormsSeen;
    // u8 padding[2]; // implicit padding in vanilla
} Pokedex;
"""
    struct_replacement = """    u8 shayminFormsSeen;
    u8 giratinaFormsSeen;

    // Mercury Research Poké Radar progression. Index 0 is SPECIES_NONE;
    // canonical species use their native 1..NATIONAL_DEX_COUNT IDs.
    u16 mercuryRadarSearchLevel[NATIONAL_DEX_COUNT + 1];
    u16 mercuryRadarRegisteredSpecies;
} Pokedex;
"""
    replace_once(path, struct_anchor, struct_replacement, "MR06B2B Pokedex storage")

    proto_anchor = """BOOL Pokedex_HasCaughtSpecies(const Pokedex *pokedex, u16 species);
BOOL Pokedex_HasSeenSpecies(const Pokedex *pokedex, u16 species);
u32 Pokedex_GetForm_Spinda"""
    proto_replacement = """BOOL Pokedex_HasCaughtSpecies(const Pokedex *pokedex, u16 species);
BOOL Pokedex_HasSeenSpecies(const Pokedex *pokedex, u16 species);

#define POKEDEX_MERCURY_RADAR_SEARCH_LEVEL_CAP 999

u16 Pokedex_MercuryRadar_GetSearchLevel(const Pokedex *pokedex, u16 species);
void Pokedex_MercuryRadar_SetSearchLevel(Pokedex *pokedex, u16 species, u16 searchLevel);
u16 Pokedex_MercuryRadar_IncrementSearchLevel(Pokedex *pokedex, u16 species);
u16 Pokedex_MercuryRadar_GetRegisteredSpecies(const Pokedex *pokedex);
void Pokedex_MercuryRadar_SetRegisteredSpecies(Pokedex *pokedex, u16 species);

u32 Pokedex_GetForm_Spinda"""
    replace_once(path, proto_anchor, proto_replacement, "MR06B2B Pokedex API")


def patch_runtime(root: Path) -> None:
    path = root / "src/pokedex.c"

    anchor = """BOOL Pokedex_HasSeenSpecies(const Pokedex *pokedex, u16 species)
{
    CheckPokedexIntegrity(pokedex);

    if (SpeciesInvalid(species)) {
        return FALSE;
    }

    return SpeciesSeen(pokedex, species);
}

u32 Pokedex_GetForm_Spinda"""
    replacement = """BOOL Pokedex_HasSeenSpecies(const Pokedex *pokedex, u16 species)
{
    CheckPokedexIntegrity(pokedex);

    if (SpeciesInvalid(species)) {
        return FALSE;
    }

    return SpeciesSeen(pokedex, species);
}

u16 Pokedex_MercuryRadar_GetSearchLevel(const Pokedex *pokedex, u16 species)
{
    CheckPokedexIntegrity(pokedex);

    if (SpeciesInvalid(species)) {
        return 0;
    }

    u16 searchLevel = pokedex->mercuryRadarSearchLevel[species];
    if (searchLevel > POKEDEX_MERCURY_RADAR_SEARCH_LEVEL_CAP) {
        return POKEDEX_MERCURY_RADAR_SEARCH_LEVEL_CAP;
    }

    return searchLevel;
}

void Pokedex_MercuryRadar_SetSearchLevel(Pokedex *pokedex, u16 species, u16 searchLevel)
{
    CheckPokedexIntegrity(pokedex);

    if (SpeciesInvalid(species)) {
        return;
    }

    if (searchLevel > POKEDEX_MERCURY_RADAR_SEARCH_LEVEL_CAP) {
        searchLevel = POKEDEX_MERCURY_RADAR_SEARCH_LEVEL_CAP;
    }

    pokedex->mercuryRadarSearchLevel[species] = searchLevel;
}

u16 Pokedex_MercuryRadar_IncrementSearchLevel(Pokedex *pokedex, u16 species)
{
    u16 searchLevel = Pokedex_MercuryRadar_GetSearchLevel(pokedex, species);

    if (SpeciesInvalid(species)) {
        return 0;
    }

    if (searchLevel < POKEDEX_MERCURY_RADAR_SEARCH_LEVEL_CAP) {
        searchLevel++;
        pokedex->mercuryRadarSearchLevel[species] = searchLevel;
    }

    return searchLevel;
}

u16 Pokedex_MercuryRadar_GetRegisteredSpecies(const Pokedex *pokedex)
{
    CheckPokedexIntegrity(pokedex);

    if (SpeciesInvalid(pokedex->mercuryRadarRegisteredSpecies)) {
        return SPECIES_NONE;
    }

    return pokedex->mercuryRadarRegisteredSpecies;
}

void Pokedex_MercuryRadar_SetRegisteredSpecies(Pokedex *pokedex, u16 species)
{
    CheckPokedexIntegrity(pokedex);

    if (species == SPECIES_NONE) {
        pokedex->mercuryRadarRegisteredSpecies = SPECIES_NONE;
        return;
    }

    if (SpeciesInvalid(species)) {
        return;
    }

    pokedex->mercuryRadarRegisteredSpecies = species;
}

u32 Pokedex_GetForm_Spinda"""
    replace_once(path, anchor, replacement, "MR06B2B Pokedex runtime")


def validate(root: Path) -> None:
    header = (root / "include/pokedex.h").read_text()
    runtime = (root / "src/pokedex.c").read_text()
    save_table = (root / "src/savedata/save_table.c").read_text()

    required_header = (
        "mercuryRadarSearchLevel[NATIONAL_DEX_COUNT + 1]",
        "mercuryRadarRegisteredSpecies",
        "POKEDEX_MERCURY_RADAR_SEARCH_LEVEL_CAP 999",
        "Pokedex_MercuryRadar_GetSearchLevel",
        "Pokedex_MercuryRadar_IncrementSearchLevel",
        "Pokedex_MercuryRadar_SetRegisteredSpecies",
    )
    for token in required_header:
        if token not in header:
            raise SystemExit(f"MR06B2B header missing {token}")

    required_runtime = (
        "pokedex->mercuryRadarSearchLevel[species]",
        "POKEDEX_MERCURY_RADAR_SEARCH_LEVEL_CAP",
        "pokedex->mercuryRadarRegisteredSpecies",
    )
    for token in required_runtime:
        if token not in runtime:
            raise SystemExit(f"MR06B2B runtime missing {token}")

    # Search progression extends the existing Pokedex entry. It must not add
    # or reorder save-table IDs, which would be a much larger save-layout risk.
    if save_table.count("SAVE_TABLE_ENTRY_POKEDEX") != 1:
        raise SystemExit("MR06B2B unexpected Pokedex save-table layout")
    if "SAVE_TABLE_ENTRY_MERCURY_RADAR" in save_table:
        raise SystemExit("MR06B2B must not create a parallel Radar save-table entry")

    # Pokedex_Init already clears sizeof(Pokedex), therefore both the full
    # Search Level array and registered target initialize to zero.
    if "memset(pokedexData, 0, sizeof(Pokedex));" not in runtime:
        raise SystemExit("MR06B2B requires whole-Pokedex zero initialization")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06b2b-radar-save-storage.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    generated_species = root / "generated/species.txt"
    species = [line.strip() for line in generated_species.read_text().splitlines() if line.strip()]
    canonical_count = len(species) - 3  # NONE + EGG + BAD_EGG
    if canonical_count != 1025:
        raise SystemExit(f"MR06B2B expected 1025 canonical species, found {canonical_count}")

    patch_header(root)
    patch_runtime(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2B_RADAR_SEARCH_LEVEL_SAVE_STORAGE",
        "status": "PASS",
        "canonical_species_count": canonical_count,
        "storage_owner": "expanded Mercury Pokedex save block",
        "search_level_storage": "u16 per species, indexed by native species ID",
        "search_level_entries": canonical_count + 1,
        "search_level_cap": 999,
        "registered_quick_search_species_persisted": True,
        "new_game_initial_search_level": 0,
        "new_game_registered_species": "SPECIES_NONE",
        "separate_save_table_entry_added": False,
        "save_table_ids_reordered": False,
        "normal_encounter_tables_modified": False,
        "chain_state_added": False,
        "battery_state_added": False,
        "ready_for_item_scanner_ui": True,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
