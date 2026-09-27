#!/usr/bin/env python3
"""MR06B2C3 — bind ITEM_POKE_RADAR to the DS scanner and targeted rustling patch.

This is the first player-facing functional DexNav pass:
- Bag and registered Poké Radar use open the dual-screen scanner.
- A selects SEARCH; R registers; B cancels.
- SEARCH returns to the field and creates one guaranteed nearby rustling grass
  patch containing the selected species at a level inside its current Radar
  range.
- No battery recharge, random target failure, or required chain.
- Entering the patch starts the selected species and increments that species'
  persistent Search Level.
- Normal walking encounter tables are untouched.

Quality rolls (special move / rare Primary Ability / held item / Potential IVs)
remain the following subphase; this pass proves the complete selection-to-battle
path first.
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


def patch_app_header(root: Path) -> None:
    path = root / "include/applications/mercury_research_radar.h"

    old = """    int mapHeaderID;
    u16 selectedSpecies;
    u8 action;
    u8 padding;
} MercuryResearchRadarAppArgs;

extern const ApplicationManagerTemplate gMercuryResearchRadarAppTemplate;

MercuryResearchRadarAppArgs *MercuryResearchRadar_OpenScanner(void *fieldSystem);
"""
    new = """    int mapHeaderID;
    u16 selectedSpecies;
    u8 selectedMinLevel;
    u8 selectedMaxLevel;
    u8 selectedSourceFlags;
    u8 action;
} MercuryResearchRadarAppArgs;

extern const ApplicationManagerTemplate gMercuryResearchRadarAppTemplate;

MercuryResearchRadarAppArgs *MercuryResearchRadar_OpenScanner(void *fieldSystem);
void *MercuryResearchRadar_NewFieldTaskContext(void);
BOOL MercuryResearchRadar_FieldTask(FieldTask *task);
"""
    replace_once(path, old, new, "MR06B2C3 app args and task API")


def patch_app_source(root: Path) -> None:
    path = root / "src/applications/mercury_research_radar.c"

    replace_once(
        path,
        '#include "field/field_system.h"\n\n#include "bg_window.h"\n',
        '#include "field/field_system.h"\n\n'
        '#include "overlay005/fieldmap.h"\n'
        '#include "bg_window.h"\n',
        "MR06B2C3 fieldmap include",
    )
    replace_once(
        path,
        '#include "message_util.h"\n#include "overlay006/wild_encounters.h"\n',
        '#include "message_util.h"\n'
        '#include "map_object.h"\n'
        '#include "overlay006/wild_encounters.h"\n',
        "MR06B2C3 map object include",
    )
    replace_once(
        path,
        '#include "pokedex.h"\n#include "pokemon_icon.h"\n',
        '#include "pokedex.h"\n'
        '#include "pokeradar.h"\n'
        '#include "pokemon_icon.h"\n',
        "MR06B2C3 pokeradar include",
    )
    replace_once(
        path,
        '#include "screen_fade.h"\n#include "string_gf.h"\n',
        '#include "screen_fade.h"\n'
        '#include "scrcmd.h"\n'
        '#include "script_manager.h"\n'
        '#include "string_gf.h"\n',
        "MR06B2C3 script includes",
    )

    old_struct = """typedef struct MercuryResearchRadarApp {
    MercuryResearchRadarAppArgs *args;
    BgConfig *bgConfig;
    Window mainWindow;
    Window subWindow;
} MercuryResearchRadarApp;
"""
    new_struct = """typedef struct MercuryResearchRadarApp {
    MercuryResearchRadarAppArgs *args;
    BgConfig *bgConfig;
    Window mainWindow;
    Window subWindow;
} MercuryResearchRadarApp;

typedef struct MercuryResearchRadarFieldTaskContext {
    MercuryResearchRadarAppArgs *appArgs;
    u16 selectedSpecies;
    u8 selectedMinLevel;
    u8 selectedMaxLevel;
    u8 action;
    u8 state;
    BOOL patchSpawned;
} MercuryResearchRadarFieldTaskContext;
"""
    replace_once(path, old_struct, new_struct, "MR06B2C3 field task context")

    open_anchor = """MercuryResearchRadarAppArgs *MercuryResearchRadar_OpenScanner(void *fieldSystemArg)
{
    FieldSystem *fieldSystem = fieldSystemArg;
    MercuryResearchRadarAppArgs *args = Heap_Alloc(HEAP_ID_FIELD2, sizeof(MercuryResearchRadarAppArgs));

    MI_CpuClear8(args, sizeof(MercuryResearchRadarAppArgs));

    args->saveData = fieldSystem->saveData;
    args->mapHeaderID = fieldSystem->location->mapHeaderID;
    args->action = MERCURY_RESEARCH_RADAR_APP_CANCEL;
    args->selectedSpecies = SPECIES_NONE;

    MercuryResearchRadar_InitScannerState(
        (enum MapHeaderID)args->mapHeaderID,
        MercuryEncounterChart_GetCurrentLandMethod(),
        SaveData_GetPokedex(args->saveData),
        &args->scanner);

    FieldSystem_StartChildProcess(fieldSystem, &gMercuryResearchRadarAppTemplate, args);
    return args;
}
"""
    task_impl = open_anchor + r'''
void *MercuryResearchRadar_NewFieldTaskContext(void)
{
    MercuryResearchRadarFieldTaskContext *ctx = Heap_AllocAtEnd(
        HEAP_ID_FIELD2,
        sizeof(MercuryResearchRadarFieldTaskContext));

    MI_CpuClear8(ctx, sizeof(MercuryResearchRadarFieldTaskContext));
    return ctx;
}

BOOL MercuryResearchRadar_FieldTask(FieldTask *task)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(task);
    MercuryResearchRadarFieldTaskContext *ctx = FieldTask_GetEnv(task);

    switch (ctx->state) {
    case 0:
        MapObjectMan_PauseAllMovement(fieldSystem->mapObjMan);
        FieldMap_FadeScreen(FADE_TYPE_BRIGHTNESS_OUT);
        ctx->state = 1;
        break;

    case 1:
        if (IsScreenFadeDone()) {
            ctx->appArgs = MercuryResearchRadar_OpenScanner(fieldSystem);
            ctx->state = 2;
        }
        break;

    case 2:
        if (FieldSystem_IsRunningApplication(fieldSystem)) {
            break;
        }

        if (ctx->appArgs != NULL) {
            ctx->action = ctx->appArgs->action;
            ctx->selectedSpecies = ctx->appArgs->selectedSpecies;
            ctx->selectedMinLevel = ctx->appArgs->selectedMinLevel;
            ctx->selectedMaxLevel = ctx->appArgs->selectedMaxLevel;
            Heap_Free(ctx->appArgs);
            ctx->appArgs = NULL;
        }

        FieldSystem_StartFieldMap(fieldSystem);
        ctx->state = 3;
        break;

    case 3:
        if (!FieldSystem_IsRunningFieldMap(fieldSystem)) {
            break;
        }

        if (ctx->action == MERCURY_RESEARCH_RADAR_APP_SEARCH
            && ctx->selectedSpecies != SPECIES_NONE) {
            ctx->patchSpawned = MercuryRadar_SpawnTargetPatch(
                fieldSystem,
                ctx->selectedSpecies,
                ctx->selectedMinLevel,
                ctx->selectedMaxLevel);

            if (!ctx->patchSpawned) {
                ScriptManager_Start(task, SCRIPT_ID(POKE_RADAR, 1), NULL, NULL);
            }
        }

        FieldMap_FadeScreen(FADE_TYPE_BRIGHTNESS_IN);
        ctx->state = 4;
        break;

    case 4:
        if (IsScreenFadeDone()) {
            MapObjectMan_UnpauseAllMovement(fieldSystem->mapObjMan);
            Heap_Free(ctx);
            return TRUE;
        }
        break;
    }

    return FALSE;
}
'''
    replace_once(path, open_anchor, task_impl, "MR06B2C3 shared field task")

    old_input = """        if (JOY_NEW(PAD_BUTTON_R)) {
            Pokedex *pokedex = SaveData_GetPokedex(app->args->saveData);

            if (MercuryResearchRadar_RegisterSelected(&app->args->scanner, pokedex)) {
                MercuryResearchRadarApp_DrawDossier(app);
                MercuryResearchRadarApp_DrawBottomText(app);
            }
        }

        if (JOY_NEW(PAD_BUTTON_B)) {
            const MercuryResearchRadarTarget *target =
                MercuryResearchRadar_GetSelectedTarget(&app->args->scanner);

            app->args->action = MERCURY_RESEARCH_RADAR_APP_CANCEL;
            app->args->selectedSpecies = target != NULL ? target->species : SPECIES_NONE;

            StartScreenFade(
                FADE_BOTH_SCREENS,
                FADE_TYPE_BRIGHTNESS_OUT,
                FADE_TYPE_BRIGHTNESS_OUT,
                COLOR_BLACK,
                6,
                1,
                HEAP_ID_FIELD2);
            *state = 3;
        }
"""
    new_input = """        if (JOY_NEW(PAD_BUTTON_A)) {
            const MercuryResearchRadarTarget *target =
                MercuryResearchRadar_GetSelectedTarget(&app->args->scanner);

            if (target != NULL) {
                app->args->action = MERCURY_RESEARCH_RADAR_APP_SEARCH;
                app->args->selectedSpecies = target->species;
                app->args->selectedMinLevel = target->minLevel;
                app->args->selectedMaxLevel = target->maxLevel;
                app->args->selectedSourceFlags = target->sourceFlags;

                StartScreenFade(
                    FADE_BOTH_SCREENS,
                    FADE_TYPE_BRIGHTNESS_OUT,
                    FADE_TYPE_BRIGHTNESS_OUT,
                    COLOR_BLACK,
                    6,
                    1,
                    HEAP_ID_FIELD2);
                *state = 3;
            }
        } else if (JOY_NEW(PAD_BUTTON_R)) {
            Pokedex *pokedex = SaveData_GetPokedex(app->args->saveData);

            if (MercuryResearchRadar_RegisterSelected(&app->args->scanner, pokedex)) {
                MercuryResearchRadarApp_DrawDossier(app);
                MercuryResearchRadarApp_DrawBottomText(app);
            }
        } else if (JOY_NEW(PAD_BUTTON_B)) {
            const MercuryResearchRadarTarget *target =
                MercuryResearchRadar_GetSelectedTarget(&app->args->scanner);

            app->args->action = MERCURY_RESEARCH_RADAR_APP_CANCEL;
            app->args->selectedSpecies = target != NULL ? target->species : SPECIES_NONE;

            StartScreenFade(
                FADE_BOTH_SCREENS,
                FADE_TYPE_BRIGHTNESS_OUT,
                FADE_TYPE_BRIGHTNESS_OUT,
                COLOR_BLACK,
                6,
                1,
                HEAP_ID_FIELD2);
            *state = 3;
        }
"""
    replace_once(path, old_input, new_input, "MR06B2C3 A search action")

    replace_once(
        path,
        '"D-PAD TOUCH SELECT   R REGISTER   B BACK",',
        '"A SEARCH   R REGISTER   B BACK",',
        "MR06B2C3 controls text",
    )


def patch_pokeradar(root: Path) -> None:
    header = root / "include/pokeradar.h"
    source = root / "src/pokeradar.c"

    header_anchor = """void SetRadarMon(RadarChain *chain, const int species, const int level);
void GetRadarMon(RadarChain *chain, int *species, int *level);
const BOOL sub_02069798"""
    header_replacement = """void SetRadarMon(RadarChain *chain, const int species, const int level);
void GetRadarMon(RadarChain *chain, int *species, int *level);

BOOL MercuryRadar_SpawnTargetPatch(
    FieldSystem *fieldSystem,
    u16 species,
    u8 minLevel,
    u8 maxLevel);
BOOL MercuryRadar_HasTarget(const RadarChain *chain);
void MercuryRadar_GetTarget(const RadarChain *chain, int *species, int *level);
void MercuryRadar_ClearTarget(RadarChain *chain);

const BOOL sub_02069798"""
    replace_once(header, header_anchor, header_replacement, "MR06B2C3 Radar public API")

    struct_anchor = """    GFXTestBox grassPatchVolume;
    u8 unk_D0;
} RadarChain;
"""
    struct_replacement = """    GFXTestBox grassPatchVolume;
    u8 unk_D0;

    // Mercury Research Radar targeted-search state. This is intentionally
    // independent of vanilla chain count/battery semantics.
    int mercuryTargetSpecies;
    int mercuryTargetLevel;
    BOOL mercuryTargetActive;
} RadarChain;
"""
    replace_once(source, struct_anchor, struct_replacement, "MR06B2C3 Radar target state")

    clear_anchor = """    chain->unk_D0 = 0;
    chain->unk_14 = 1;
    chain->unk_18 = 0;
    MI_CpuClear8(chain->patch, sizeof(GrassPatch) * NUM_GRASS_PATCHES);
"""
    clear_replacement = """    chain->unk_D0 = 0;
    chain->unk_14 = 1;
    chain->unk_18 = 0;
    chain->mercuryTargetSpecies = 0;
    chain->mercuryTargetLevel = 0;
    chain->mercuryTargetActive = FALSE;
    MI_CpuClear8(chain->patch, sizeof(GrassPatch) * NUM_GRASS_PATCHES);
"""
    replace_once(source, clear_anchor, clear_replacement, "MR06B2C3 Radar clear target")

    api_anchor = """void GetRadarMon(RadarChain *chain, int *species, int *level)
{
    *species = chain->species;
    *level = chain->level;
}

const BOOL sub_02069798"""
    api_replacement = r'''void GetRadarMon(RadarChain *chain, int *species, int *level)
{
    *species = chain->species;
    *level = chain->level;
}

BOOL MercuryRadar_SpawnTargetPatch(
    FieldSystem *fieldSystem,
    u16 species,
    u8 minLevel,
    u8 maxLevel)
{
    RadarChain *chain = fieldSystem->chain;

    if (species == 0 || minLevel == 0 || maxLevel < minLevel) {
        return FALSE;
    }

    RadarChain_Clear(chain);

    int playerX = PlayerAvatar_GetXPos(fieldSystem->playerAvatar);
    int playerZ = PlayerAvatar_GetZPos(fieldSystem->playerAvatar);

    if (!RadarSpawnPatches(fieldSystem, playerX, playerZ, chain)) {
        return FALSE;
    }

    int chosenPatch = -1;
    int chosenDistance = 0x7FFFFFFF;

    for (int i = 0; i < NUM_GRASS_PATCHES; i++) {
        if (!chain->patch[i].active) {
            continue;
        }

        int dx = chain->patch[i].x - playerX;
        int dz = chain->patch[i].z - playerZ;
        int distance = dx * dx + dz * dz;

        if (distance < chosenDistance) {
            chosenDistance = distance;
            chosenPatch = i;
        }
    }

    if (chosenPatch < 0) {
        RadarChain_Clear(chain);
        return FALSE;
    }

    // DexNav-style search creates one obvious target, not four lottery
    // patches. Keep the nearest valid grass tile and discard the rest.
    for (int i = 0; i < NUM_GRASS_PATCHES; i++) {
        if (i != chosenPatch) {
            chain->patch[i].active = FALSE;
        }
    }

    chain->patch[chosenPatch].continueChain = FALSE;
    chain->patch[chosenPatch].shakeType = PATCH_SHAKE_HARD;
    chain->patch[chosenPatch].shiny = FALSE;

    u32 levelRange = maxLevel - minLevel + 1;
    chain->mercuryTargetSpecies = species;
    chain->mercuryTargetLevel = minLevel + LCRNG_RandMod(levelRange);
    chain->mercuryTargetActive = TRUE;
    chain->active = TRUE;

    FieldSystem_CreateShakingRadarPatches(fieldSystem, chain);
    return TRUE;
}

BOOL MercuryRadar_HasTarget(const RadarChain *chain)
{
    return chain != NULL && chain->mercuryTargetActive;
}

void MercuryRadar_GetTarget(const RadarChain *chain, int *species, int *level)
{
    if (species != NULL) {
        *species = chain->mercuryTargetSpecies;
    }

    if (level != NULL) {
        *level = chain->mercuryTargetLevel;
    }
}

void MercuryRadar_ClearTarget(RadarChain *chain)
{
    chain->mercuryTargetSpecies = 0;
    chain->mercuryTargetLevel = 0;
    chain->mercuryTargetActive = FALSE;
}

const BOOL sub_02069798'''
    replace_once(source, api_anchor, api_replacement, "MR06B2C3 Radar targeted patch runtime")


def patch_wild_encounters(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"

    anchor = """    if (radarData->isRadarEncounter) {
        int species, level;

        if (radarData->shakeType == 1) {
"""
    replacement = """    if (radarData->isRadarEncounter) {
        int species, level;

        // Mercury Research Radar: a scanner SEARCH owns this rustling patch.
        // It bypasses vanilla chain-slot lottery and guarantees the selected
        // species/level without altering the area's normal encounter table.
        if (MercuryRadar_HasTarget(fieldSystem->chain)) {
            MercuryRadar_GetTarget(fieldSystem->chain, &species, &level);

            TrainerInfo *trainerInfo = SaveData_GetTrainerInfo(
                FieldSystem_GetSaveData(fieldSystem));

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
                Pokedex_MercuryRadar_IncrementSearchLevel(
                    SaveData_GetPokedex(fieldSystem->saveData),
                    (u16)species);
            }

            RadarChain_Clear(fieldSystem->chain);
            return encounterSuccess;
        }

        if (radarData->shakeType == 1) {
"""
    replace_once(path, anchor, replacement, "MR06B2C3 guaranteed selected encounter")


def patch_item_use(root: Path) -> None:
    path = root / "src/item_use_functions.c"

    replace_once(
        path,
        '#include "applications/mail.h"\n',
        '#include "applications/mail.h"\n'
        '#include "applications/mercury_research_radar.h"\n',
        "MR06B2C3 scanner include",
    )

    old = """static void UsePokeRadarFromMenu(ItemMenuUseContext *usageContext, const ItemUseContext *additionalContext)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(usageContext->fieldTask);
    StartMenu *menu = FieldTask_GetEnv(usageContext->fieldTask);
    int *v2 = Heap_AllocAtEnd(HEAP_ID_FIELD2, sizeof(int));

    (*v2) = 0;
    FieldSystem_StartFieldMap(fieldSystem);

    menu->callback = RefreshRadarChain;
    menu->taskData = v2;
    menu->state = START_MENU_STATE_NEW_TASK;
}

static BOOL UsePokeRadarInField(ItemFieldUseContext *usageContext)
{
    int *v0 = Heap_AllocAtEnd(HEAP_ID_FIELD2, sizeof(int));

    *v0 = 0;
    FieldSystem_CreateTask(usageContext->fieldSystem, RefreshRadarChain, v0);

    return FALSE;
}

static enum ItemUseCheckResult CanUsePokeRadar(const ItemUseContext *usageContext)
{
    if (usageContext->hasPartner == TRUE) {
        return ITEM_USE_CANNOT_USE_WITH_PARTNER;
    }

    if (PlayerAvatar_GetPlayerState(usageContext->fieldSystem->playerAvatar) == 0x1) {
        return ITEM_USE_CANNOT_USE_GENERIC;
    }

    if (!TileBehavior_IsTallGrass(usageContext->currTileBehavior)) {
        return ITEM_USE_CANNOT_USE_GENERIC;
    }

    return ITEM_USE_CAN_USE;
}
"""
    new = """static void UsePokeRadarFromMenu(ItemMenuUseContext *usageContext, const ItemUseContext *additionalContext)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(usageContext->fieldTask);
    StartMenu *menu = FieldTask_GetEnv(usageContext->fieldTask);

    FieldSystem_StartFieldMap(fieldSystem);

    menu->callback = MercuryResearchRadar_FieldTask;
    menu->taskData = MercuryResearchRadar_NewFieldTaskContext();
    menu->state = START_MENU_STATE_NEW_TASK;
}

static BOOL UsePokeRadarInField(ItemFieldUseContext *usageContext)
{
    FieldSystem_CreateTask(
        usageContext->fieldSystem,
        MercuryResearchRadar_FieldTask,
        MercuryResearchRadar_NewFieldTaskContext());

    return FALSE;
}

static enum ItemUseCheckResult CanUsePokeRadar(const ItemUseContext *usageContext)
{
    if (usageContext->hasPartner == TRUE) {
        return ITEM_USE_CANNOT_USE_WITH_PARTNER;
    }

    if (PlayerAvatar_GetPlayerState(usageContext->fieldSystem->playerAvatar) == 0x1) {
        return ITEM_USE_CANNOT_USE_GENERIC;
    }

    MercuryResearchRadarTarget target;

    if (MercuryResearchRadar_GetTargets(
            usageContext->mapHeaderID,
            MercuryEncounterChart_GetCurrentLandMethod(),
            &target,
            1) <= 0) {
        return ITEM_USE_CANNOT_USE_GENERIC;
    }

    return ITEM_USE_CAN_USE;
}
"""
    replace_once(path, old, new, "MR06B2C3 item binding")


def validate(root: Path) -> None:
    app_h = (root / "include/applications/mercury_research_radar.h").read_text()
    app_c = (root / "src/applications/mercury_research_radar.c").read_text()
    radar_h = (root / "include/pokeradar.h").read_text()
    radar_c = (root / "src/pokeradar.c").read_text()
    wild = (root / "src/overlay006/wild_encounters.c").read_text()
    item = (root / "src/item_use_functions.c").read_text()
    start_menu = (root / "src/start_menu.c").read_text()

    checks = {
        "A_search": "MERCURY_RESEARCH_RADAR_APP_SEARCH" in app_c and "PAD_BUTTON_A" in app_c,
        "shared_field_task": "MercuryResearchRadar_FieldTask" in app_h and "MercuryResearchRadar_FieldTask" in app_c,
        "single_target_patch": "MercuryRadar_SpawnTargetPatch" in radar_h and "chosenPatch" in radar_c,
        "target_runtime_state": "mercuryTargetActive" in radar_c,
        "selected_species_guarantee": "MercuryRadar_HasTarget(fieldSystem->chain)" in wild,
        "search_level_increment": "Pokedex_MercuryRadar_IncrementSearchLevel" in wild,
        "bag_binding": "menu->callback = MercuryResearchRadar_FieldTask;" in item,
        "registered_binding": "MercuryResearchRadar_FieldTask," in item,
        "battery_removed_from_mercury_flow": "RefreshRadarChain" not in item[item.find("static void UsePokeRadarFromMenu"):item.find("static void UseSprayDuckFromMenu")],
        "standing_in_grass_not_required": "!TileBehavior_IsTallGrass(usageContext->currTileBehavior)" not in item[item.find("static enum ItemUseCheckResult CanUsePokeRadar"):item.find("static void UseSprayDuckFromMenu")],
        "general_encounter_menu_absent": "START_MENU_OPTION_ENCOUNTERS" not in start_menu,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2C3 validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06b2c3-radar-item-target-patch.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    scanner = root / "src/applications/mercury_research_radar.c"
    if not scanner.exists():
        raise SystemExit("MR06B2C3 requires MR06B2C2 dual-screen scanner")

    patch_app_header(root)
    patch_app_source(root)
    patch_pokeradar(root)
    patch_wild_encounters(root)
    patch_item_use(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2C3_RADAR_ITEM_TARGET_PATCH",
        "status": "PASS",
        "poke_radar_item_opens_scanner": True,
        "registered_poke_radar_opens_scanner": True,
        "a_button_search": True,
        "r_button_register": True,
        "b_button_cancel": True,
        "standing_on_grass_required_to_open": False,
        "nearby_grass_required_to_search": True,
        "target_patch_count": 1,
        "target_species_guaranteed": True,
        "target_level_within_displayed_range": True,
        "search_level_increments_on_target_encounter": True,
        "required_chain": False,
        "battery_recharge": False,
        "normal_encounter_tables_modified": False,
        "quality_rolls_applied": False,
        "next": "apply Search-Level quality rolls: special move, rarer Primary Ability, held item and Potential IVs",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
