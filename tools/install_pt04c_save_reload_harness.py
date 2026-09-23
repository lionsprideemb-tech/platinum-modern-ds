#!/usr/bin/env python3
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04c-save-reload-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    replace_once(
        field_map_change_c,
        '#include "location.h"\n',
        '#include "location.h"\n#include "main.h"\n',
        "reset constants include",
    )

    battle_block = """        // PT04C battle-entry phase: keep the already-proven native Victini
        // in party slot 0 and start Platinum's real scripted wild encounter
        // path. The opponent is deliberately native/low-risk so this gate
        // isolates player-side species-494 loading into the battle engine.
        GF_ASSERT(Party_HasSpecies(
            SaveData_GetParty(fieldSystem->saveData),
            SPECIES_VICTINI));

        int *battleResult = Heap_Alloc(HEAP_ID_FIELD2, sizeof(int));
        *battleResult = 0;

        Encounter_NewVsSpeciesAtLevel(
            task,
            SPECIES_BIDOOF,
            5,
            battleResult,
            FALSE);"""

    save_reset_block = """        // PT04C final gate: persist species #494 through Platinum's real
        // save writer, then reboot through the native load-save recovery path.
        // RESET_ERROR is intentional here: NitroMain routes it directly through
        // gGameStartLoadSaveAppTemplate, which calls SaveData_Load.
        GF_ASSERT(Party_HasSpecies(
            SaveData_GetParty(fieldSystem->saveData),
            SPECIES_VICTINI));
        GF_ASSERT(Pokedex_HasSeenSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_VICTINI));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_VICTINI));
        GF_ASSERT(FieldSystem_Save(fieldSystem));

        OS_ResetSystem(RESET_ERROR);"""

    replace_once(
        field_map_change_c,
        battle_block,
        save_reset_block,
        "save/reset replacement",
    )

    saved_case = """    case 3:
        return TRUE;
    case 4:
        if (!FieldSystem_IsRunningApplication(fieldSystem)) {
            *state = 1;
        }
        break;"""

    reload_case = """    case 3:
        // We reached this state only after gGameStartLoadSaveAppTemplate loaded
        // the cartridge save and the saved map was reconstructed. Prove that
        // species #494 and its capture flags survived serialization/reload.
        GF_ASSERT(Party_HasSpecies(
            SaveData_GetParty(fieldSystem->saveData),
            SPECIES_VICTINI));
        GF_ASSERT(Pokedex_HasSeenSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_VICTINI));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_VICTINI));

        Pokemon *reloadedVictini = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);
        GF_ASSERT(Pokemon_GetValue(reloadedVictini, MON_DATA_SPECIES, NULL) == SPECIES_VICTINI);
        GF_ASSERT(Pokemon_GetValue(reloadedVictini, MON_DATA_LEVEL, NULL) == 50);

        FieldSystem_OpenPartyMenu_SelectPokemon(0, fieldSystem);
        *state = 5;
        break;
    case 4:
        if (!FieldSystem_IsRunningApplication(fieldSystem)) {
            *state = 1;
        }
        break;
    case 5:
        if (!FieldSystem_IsRunningApplication(fieldSystem)) {
            return TRUE;
        }
        break;"""

    replace_once(
        field_map_change_c,
        saved_case,
        reload_case,
        "post-reload verification hook",
    )

    report = {
        "gate": "PT04C_VICTINI_SAVE_RELOAD_RUNTIME_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "prerequisite": "PT04C native Battle checkpoint Run #28",
        "species": "SPECIES_VICTINI",
        "species_id": 494,
        "level": 50,
        "save_entrypoint": "FieldSystem_Save",
        "reload_entrypoint": "gGameStartLoadSaveAppTemplate -> SaveData_Load",
        "reset_mode": "RESET_ERROR",
        "post_reload_checks": [
            "Party_HasSpecies(SPECIES_VICTINI)",
            "Pokedex_HasSeenSpecies(SPECIES_VICTINI)",
            "Pokedex_HasCaughtSpecies(SPECIES_VICTINI)",
            "party slot 0 species == SPECIES_VICTINI",
            "party slot 0 level == 50",
            "native Party application reopened after reload",
        ],
        "next_if_passed": "seal PT04C and begin bulk post-Gen-IV roster expansion",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
