#!/usr/bin/env python3
"""MR06B2D — apply Elite Redux-style DexNav quality rolls to Radar targets.

This phase turns Search Level into battle-visible rewards while keeping the
normal encounter tables untouched.

Quality is generated when SEARCH creates the rustling patch, so the result can
be shown by the overworld search HUD in the following UI pass:
- Potential: 0-3 stars; each star guarantees one unique 31 IV.
- Special move: random species Egg Move using the Search-Level probability.
- Primary Ability: Ability 1 normally; Ability 2 becomes the rarer Radar roll.
- Held item: DexNav-style common/rare item selection that improves with Search
  Level and plateaus at Search Lv. 100+.

Mercury Innates are not read or modified here.
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


def patch_radar_header(root: Path) -> None:
    path = root / "include/pokeradar.h"

    anchor = """typedef struct RadarChain RadarChain;

#define NUM_GRASS_PATCHES"""
    replacement = """typedef struct RadarChain RadarChain;

typedef struct MercuryRadarTargetQuality {
    u16 searchLevel;
    u16 specialMove;
    u16 heldItem;
    u8 primaryAbility;
    u8 potentialStars;
} MercuryRadarTargetQuality;

#define NUM_GRASS_PATCHES"""
    replace_once(path, anchor, replacement, "MR06B2D quality struct")

    anchor = """BOOL MercuryRadar_HasTarget(const RadarChain *chain);
void MercuryRadar_GetTarget(const RadarChain *chain, int *species, int *level);
void MercuryRadar_ClearTarget(RadarChain *chain);

const BOOL sub_02069798"""
    replacement = """BOOL MercuryRadar_HasTarget(const RadarChain *chain);
void MercuryRadar_GetTarget(const RadarChain *chain, int *species, int *level);
void MercuryRadar_GetTargetQuality(
    const RadarChain *chain,
    MercuryRadarTargetQuality *quality);
void MercuryRadar_ClearTarget(RadarChain *chain);

const BOOL sub_02069798"""
    replace_once(path, anchor, replacement, "MR06B2D quality API")


def patch_radar_runtime(root: Path) -> None:
    path = root / "src/pokeradar.c"

    replace_once(
        path,
        '#include "constants/battle.h"\n',
        '#include "constants/battle.h"\n'
        '#include "constants/daycare.h"\n'
        '#include "generated/abilities.h"\n'
        '#include "generated/items.h"\n'
        '#include "generated/moves.h"\n'
        '#include "generated/species_data_params.h"\n',
        "MR06B2D Radar quality includes",
    )

    replace_once(
        path,
        '#include "map_object.h"\n',
        '#include "map_object.h"\n'
        '#include "overlay006/wild_encounters.h"\n'
        '#include "pokedex.h"\n'
        '#include "pokemon.h"\n',
        "MR06B2D Radar quality runtime includes",
    )

    replace_once(
        path,
        '#include "terrain_collision_manager.h"\n',
        '#include "terrain_collision_manager.h"\n\n'
        '#include "res/pokemon/species_egg_moves.h"\n',
        "MR06B2D egg move table include",
    )

    struct_anchor = """    int mercuryTargetSpecies;
    int mercuryTargetLevel;
    BOOL mercuryTargetActive;
} RadarChain;
"""
    struct_replacement = """    int mercuryTargetSpecies;
    int mercuryTargetLevel;
    BOOL mercuryTargetActive;
    MercuryRadarTargetQuality mercuryTargetQuality;
} RadarChain;
"""
    replace_once(path, struct_anchor, struct_replacement, "MR06B2D target quality state")

    decl_anchor = """static BOOL CheckPatchShiny(const int param0);
static void IncWithCap(int *param0);
"""
    decl_replacement = """static BOOL CheckPatchShiny(const int param0);
static void IncWithCap(int *param0);
static u8 MercuryRadar_GeneratePotential(
    const MercuryResearchRadarQualityProfile *profile);
static u16 MercuryRadar_GenerateSpecialMove(
    u16 species,
    const MercuryResearchRadarQualityProfile *profile);
static u8 MercuryRadar_GeneratePrimaryAbility(
    u16 species,
    const MercuryResearchRadarQualityProfile *profile);
static u16 MercuryRadar_GenerateHeldItem(u16 species, u16 searchLevel);
static void MercuryRadar_GenerateTargetQuality(
    FieldSystem *fieldSystem,
    u16 species,
    MercuryRadarTargetQuality *quality);
"""
    replace_once(path, decl_anchor, decl_replacement, "MR06B2D helper declarations")

    clear_anchor = """    chain->mercuryTargetSpecies = 0;
    chain->mercuryTargetLevel = 0;
    chain->mercuryTargetActive = FALSE;
    MI_CpuClear8(chain->patch, sizeof(GrassPatch) * NUM_GRASS_PATCHES);
"""
    clear_replacement = """    chain->mercuryTargetSpecies = 0;
    chain->mercuryTargetLevel = 0;
    chain->mercuryTargetActive = FALSE;
    MI_CpuClear8(&chain->mercuryTargetQuality, sizeof(MercuryRadarTargetQuality));
    MI_CpuClear8(chain->patch, sizeof(GrassPatch) * NUM_GRASS_PATCHES);
"""
    replace_once(path, clear_anchor, clear_replacement, "MR06B2D clear quality state")

    spawn_anchor = """    chain->mercuryTargetSpecies = species;
    chain->mercuryTargetLevel = minLevel + LCRNG_RandMod(levelRange);
    chain->mercuryTargetActive = TRUE;
    chain->active = TRUE;

    FieldSystem_CreateShakingRadarPatches(fieldSystem, chain);
"""
    spawn_replacement = """    chain->mercuryTargetSpecies = species;
    chain->mercuryTargetLevel = minLevel + LCRNG_RandMod(levelRange);
    chain->mercuryTargetActive = TRUE;
    MercuryRadar_GenerateTargetQuality(
        fieldSystem,
        species,
        &chain->mercuryTargetQuality);
    chain->active = TRUE;

    FieldSystem_CreateShakingRadarPatches(fieldSystem, chain);
"""
    replace_once(path, spawn_anchor, spawn_replacement, "MR06B2D generate quality on SEARCH")

    api_anchor = """void MercuryRadar_ClearTarget(RadarChain *chain)
{
    chain->mercuryTargetSpecies = 0;
    chain->mercuryTargetLevel = 0;
    chain->mercuryTargetActive = FALSE;
}

const BOOL sub_02069798"""
    api_replacement = r'''void MercuryRadar_GetTargetQuality(
    const RadarChain *chain,
    MercuryRadarTargetQuality *quality)
{
    if (quality == NULL) {
        return;
    }

    if (chain == NULL || !chain->mercuryTargetActive) {
        MI_CpuClear8(quality, sizeof(MercuryRadarTargetQuality));
        return;
    }

    *quality = chain->mercuryTargetQuality;
}

void MercuryRadar_ClearTarget(RadarChain *chain)
{
    chain->mercuryTargetSpecies = 0;
    chain->mercuryTargetLevel = 0;
    chain->mercuryTargetActive = FALSE;
    MI_CpuClear8(&chain->mercuryTargetQuality, sizeof(MercuryRadarTargetQuality));
}

static u8 MercuryRadar_GeneratePotential(
    const MercuryResearchRadarQualityProfile *profile)
{
    u32 roll = LCRNG_RandMod(100);

    if (roll < profile->oneStarChance) {
        return 1;
    }

    roll -= profile->oneStarChance;

    if (roll < profile->twoStarChance) {
        return 2;
    }

    roll -= profile->twoStarChance;

    if (roll < profile->threeStarChance) {
        return 3;
    }

    return 0;
}

static u16 MercuryRadar_GenerateSpecialMove(
    u16 species,
    const MercuryResearchRadarQualityProfile *profile)
{
    if (profile->specialMoveChance == 0
        || LCRNG_RandMod(100) >= profile->specialMoveChance) {
        return MOVE_NONE;
    }

    int eggMoveOffset = -1;

    for (int i = 0; i < NELEMS(sEggMoves) - 1; i++) {
        if (sEggMoves[i] == EGG_MOVES_SPECIES_OFFSET + species) {
            eggMoveOffset = i + 1;
            break;
        }
    }

    if (eggMoveOffset < 0) {
        return MOVE_NONE;
    }

    u16 eggMoves[MAX_EGG_MOVES];
    int eggMoveCount = 0;

    for (int i = 0; i < MAX_EGG_MOVES; i++) {
        u16 move = sEggMoves[eggMoveOffset + i];

        if (move > EGG_MOVES_SPECIES_OFFSET
            || move == EGG_MOVES_TERMINATOR) {
            break;
        }

        eggMoves[eggMoveCount++] = move;
    }

    if (eggMoveCount == 0) {
        return MOVE_NONE;
    }

    return eggMoves[LCRNG_RandMod(eggMoveCount)];
}

static u8 MercuryRadar_GeneratePrimaryAbility(
    u16 species,
    const MercuryResearchRadarQualityProfile *profile)
{
    u8 ability1 = SpeciesData_GetSpeciesValue(
        species,
        SPECIES_DATA_ABILITY_1);
    u8 ability2 = SpeciesData_GetSpeciesValue(
        species,
        SPECIES_DATA_ABILITY_2);

    if (ability2 != ABILITY_NONE
        && ability2 != ability1
        && profile->rarePrimaryAbilityChance > 0
        && LCRNG_RandMod(100) < profile->rarePrimaryAbilityChance) {
        return ability2;
    }

    return ability1;
}

static u16 MercuryRadar_GenerateHeldItem(u16 species, u16 searchLevel)
{
    u16 commonItem = SpeciesData_GetSpeciesValue(
        species,
        SPECIES_DATA_HELD_ITEM_COMMON);
    u16 rareItem = SpeciesData_GetSpeciesValue(
        species,
        SPECIES_DATA_HELD_ITEM_RARE);

    if (commonItem == rareItem) {
        return commonItem;
    }

    if (commonItem == ITEM_NONE && rareItem == ITEM_NONE) {
        return ITEM_NONE;
    }

    // Elite Redux's DexNav item algorithm grows through Search Lv. 100.
    // Mercury caps the influence there so Search Lv. 101-999 remains stable.
    u16 cappedSearch = searchLevel > 100 ? 100 : searchLevel;
    u16 influence = cappedSearch >> 1;
    u16 roll = LCRNG_RandMod(100);

    if (rareItem != ITEM_NONE && roll < 5 + influence) {
        return rareItem;
    }

    if (commonItem == ITEM_NONE) {
        return ITEM_NONE;
    }

    if (rareItem == ITEM_NONE) {
        return roll < 50 ? commonItem : ITEM_NONE;
    }

    u16 totalItemChance = 55 + influence + cappedSearch;
    if (totalItemChance > 100) {
        totalItemChance = 100;
    }

    if (roll < totalItemChance) {
        return commonItem;
    }

    return ITEM_NONE;
}

static void MercuryRadar_GenerateTargetQuality(
    FieldSystem *fieldSystem,
    u16 species,
    MercuryRadarTargetQuality *quality)
{
    MI_CpuClear8(quality, sizeof(MercuryRadarTargetQuality));

    Pokedex *pokedex = SaveData_GetPokedex(fieldSystem->saveData);
    quality->searchLevel = Pokedex_MercuryRadar_GetSearchLevel(
        pokedex,
        species);

    MercuryResearchRadarQualityProfile profile;
    MercuryResearchRadar_GetQualityProfile(
        quality->searchLevel,
        &profile);

    quality->potentialStars = MercuryRadar_GeneratePotential(&profile);
    quality->specialMove = MercuryRadar_GenerateSpecialMove(species, &profile);
    quality->primaryAbility = MercuryRadar_GeneratePrimaryAbility(species, &profile);
    quality->heldItem = MercuryRadar_GenerateHeldItem(
        species,
        quality->searchLevel);
}

const BOOL sub_02069798'''
    replace_once(path, api_anchor, api_replacement, "MR06B2D quality generation runtime")


def patch_wild_encounters(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"

    decl_anchor = """static BOOL CreateWildMon_FromRadarKeepChain(const int species, const int level, const int partyDest, const BOOL isShiny, const u32 trainerId, const WildEncounters_FieldParams *fieldParams, Pokemon *mon, FieldBattleDTO *battleParams);
static u8 ModifyEncounterRateWithFieldParams"""
    decl_replacement = """static BOOL CreateWildMon_FromRadarKeepChain(const int species, const int level, const int partyDest, const BOOL isShiny, const u32 trainerId, const WildEncounters_FieldParams *fieldParams, Pokemon *mon, FieldBattleDTO *battleParams);
static void MercuryResearchRadar_ApplyTargetQuality(
    Pokemon *mon,
    const MercuryRadarTargetQuality *quality);
static u8 ModifyEncounterRateWithFieldParams"""
    replace_once(path, decl_anchor, decl_replacement, "MR06B2D quality apply declaration")

    target_anchor = """            encounterSuccess = CreateWildMon_FromRadarKeepChain(
                species,
                level,
                1,
                FALSE,
                TrainerInfo_ID(trainerInfo),
                encounterFieldParams,
                firstPartyMon,
                battleParams);

            if (encounterSuccess) {
                Pokedex_MercuryRadar_IncrementSearchLevel(
                    SaveData_GetPokedex(fieldSystem->saveData),
                    (u16)species);
            }

            RadarChain_Clear(fieldSystem->chain);
            return encounterSuccess;
"""
    target_replacement = """            MercuryRadarTargetQuality targetQuality;
            MercuryRadar_GetTargetQuality(
                fieldSystem->chain,
                &targetQuality);

            encounterSuccess = CreateWildMon_FromRadarKeepChain(
                species,
                level,
                1,
                FALSE,
                TrainerInfo_ID(trainerInfo),
                encounterFieldParams,
                firstPartyMon,
                battleParams);

            if (encounterSuccess) {
                Pokemon *targetMon = Party_GetPokemonBySlotIndex(
                    battleParams->parties[BATTLER_ENEMY_1],
                    0);

                MercuryResearchRadar_ApplyTargetQuality(
                    targetMon,
                    &targetQuality);

                Pokedex_MercuryRadar_IncrementSearchLevel(
                    SaveData_GetPokedex(fieldSystem->saveData),
                    (u16)species);
            }

            RadarChain_Clear(fieldSystem->chain);
            return encounterSuccess;
"""
    replace_once(path, target_anchor, target_replacement, "MR06B2D apply quality to selected mon")

    function_anchor = """// Generates new encounter slot, so may or may not break the chain.
static BOOL CreateWildMon_FromRadarNoChain"""
    helper = r'''static void MercuryResearchRadar_ApplyTargetQuality(
    Pokemon *mon,
    const MercuryRadarTargetQuality *quality)
{
    if (mon == NULL || quality == NULL) {
        return;
    }

    if (quality->primaryAbility != ABILITY_NONE) {
        u8 ability = quality->primaryAbility;
        Pokemon_SetValue(mon, MON_DATA_ABILITY, &ability);
    }

    // The target's item is predetermined when the rustling patch is created.
    // Override vanilla wild-item generation even when the result is ITEM_NONE.
    u16 heldItem = quality->heldItem;
    Pokemon_SetValue(mon, MON_DATA_HELD_ITEM, &heldItem);

    if (quality->specialMove != MOVE_NONE) {
        Pokemon_SetMoveSlot(mon, quality->specialMove, 0);
    }

    u8 perfectIV = 31;
    u8 chosenStats[3] = { 0xFF, 0xFF, 0xFF };

    for (int star = 0; star < quality->potentialStars && star < 3; star++) {
        u8 stat;

        do {
            stat = LCRNG_RandMod(6);
        } while ((star > 0 && stat == chosenStats[0])
            || (star > 1 && stat == chosenStats[1]));

        chosenStats[star] = stat;
        Pokemon_SetValue(mon, MON_DATA_HP_IV + stat, &perfectIV);
    }

    Pokemon_CalcLevelAndStats(mon);
}

// Generates new encounter slot, so may or may not break the chain.
static BOOL CreateWildMon_FromRadarNoChain'''
    replace_once(path, function_anchor, helper, "MR06B2D quality apply helper")


def validate(root: Path) -> None:
    radar_h = (root / "include/pokeradar.h").read_text()
    radar_c = (root / "src/pokeradar.c").read_text()
    wild = (root / "src/overlay006/wild_encounters.c").read_text()
    start_menu = (root / "src/start_menu.c").read_text()

    checks = {
        "quality_struct": "MercuryRadarTargetQuality" in radar_h,
        "quality_pre_generated": "MercuryRadar_GenerateTargetQuality" in radar_c,
        "potential_uses_profile": "MercuryRadar_GeneratePotential" in radar_c,
        "egg_move_table": "species_egg_moves.h" in radar_c and "sEggMoves" in radar_c,
        "rare_primary_ability": "SPECIES_DATA_ABILITY_2" in radar_c,
        "held_item_slots": "SPECIES_DATA_HELD_ITEM_COMMON" in radar_c and "SPECIES_DATA_HELD_ITEM_RARE" in radar_c,
        "iv_application": "MON_DATA_HP_IV + stat" in wild,
        "move_application": "Pokemon_SetMoveSlot(mon, quality->specialMove, 0)" in wild,
        "ability_application": "MON_DATA_ABILITY" in wild,
        "held_item_application": "MON_DATA_HELD_ITEM" in wild,
        "stat_recalc": "Pokemon_CalcLevelAndStats(mon)" in wild,
        "search_increment_preserved": "Pokedex_MercuryRadar_IncrementSearchLevel" in wild,
        "general_encounter_menu_absent": "START_MENU_OPTION_ENCOUNTERS" not in start_menu,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2D validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06b2d-dexnav-quality-rolls.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    if "MercuryRadar_SpawnTargetPatch" not in (root / "include/pokeradar.h").read_text():
        raise SystemExit("MR06B2D requires MR06B2C3 target-patch runtime")
    if "MercuryResearchRadar_GetQualityProfile" not in (root / "include/overlay006/wild_encounters.h").read_text():
        raise SystemExit("MR06B2D requires MR06B2A quality profile")

    patch_radar_header(root)
    patch_radar_runtime(root)
    patch_wild_encounters(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2D_DEXNAV_QUALITY_ROLLS",
        "status": "PASS",
        "quality_generated_when_patch_spawns": True,
        "potential": {
            "stars": "0-3",
            "guaranteed_perfect_ivs_per_star": 1,
            "unique_stats": True,
        },
        "special_move": {
            "source": "species Egg Move table",
            "replaces_move_slot": 1,
            "chance_source": "MR06B2A Search Level profile",
        },
        "primary_ability": {
            "normal": "ability slot 1",
            "rare_radar_roll": "ability slot 2 when distinct and available",
            "chance_source": "MR06B2A Search Level profile",
            "innates_modified": False,
        },
        "held_item": {
            "source": "species common/rare held-item slots",
            "model": "Elite Redux-style Search Level influence",
            "search_level_influence_cap": 100,
        },
        "quality_applied_before_battle": True,
        "search_level_increments_after_target_generation": True,
        "normal_encounter_tables_modified": False,
        "chain_required": False,
        "battery_required": False,
        "ready_for_overworld_search_hud": True,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
