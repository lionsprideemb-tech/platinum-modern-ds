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


def insert_include_once(path: Path, anchor: str, include_line: str, label: str) -> None:
    text = path.read_text()
    if include_line in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one include anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + include_line, 1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04c-pc-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    insert_include_once(
        field_map_change_c,
        '#include "constants/overworld_weather.h"\n',
        '#include "applications/pc_boxes/pokemon_storage_session.h"\n',
        "PC storage session include",
    )
    insert_include_once(
        field_map_change_c,
        '#include "pokedex.h"\n',
        '#include "pc_boxes.h"\n#include "pokemon.h"\n',
        "PC box/Pokemon includes",
    )
    insert_include_once(
        field_map_change_c,
        '#include "savedata.h"\n',
        '#include "savedata/save_table.h"\n',
        "save-table include",
    )

    old = """        // PT04C summary phase: reuse the already-proven native party/save state,
        // but launch Platinum's real Summary application directly for slot 0.
        // This remains CI-only and never changes the approved normal game flow.
        FieldSystem_GetPartyMenuMonSummary(0, fieldSystem, 0);"""
    new = """        // PT04C PC-storage phase: store the proven Victini into the native
        // PCBoxes save block, assert that species 494 survives the boxed format,
        // then open Platinum's real PC storage application for visual proof.
        Party *party = SaveData_GetParty(fieldSystem->saveData);
        Pokemon *victini = Party_GetPokemonBySlotIndex(party, 0);
        PCBoxes *pcBoxes = SaveData_GetPCBoxes(fieldSystem->saveData);

        GF_ASSERT(PCBoxes_TryStoreBoxMonAt(
            pcBoxes,
            0,
            0,
            Pokemon_GetBoxPokemon(victini)));

        BoxPokemon *boxedVictini = PCBoxes_GetBoxMonAt(pcBoxes, 0, 0);
        GF_ASSERT(BoxPokemon_GetValue(boxedVictini, MON_DATA_SPECIES, NULL) == SPECIES_VICTINI);
        GF_ASSERT(PCBoxes_CountAllBoxMons(pcBoxes) == 1);

        PokemonStorageSession *storageSession = Heap_Alloc(
            HEAP_ID_FIELD2,
            sizeof(PokemonStorageSession));
        storageSession->saveData = fieldSystem->saveData;
        storageSession->boxMode = PC_MODE_MOVE_MONS;
        storageSession->recordBoxUseInJournal = FALSE;

        FieldSystem_OpenPokemonStorage(fieldSystem, storageSession);"""
    replace_once(field_map_change_c, old, new, "PC storage UI launch hook")

    report = {
        "gate": "PT04C_VICTINI_NATIVE_PC_STORAGE_HARNESS_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "prerequisite": "PT04C native Summary checkpoint Run #12",
        "species": "SPECIES_VICTINI",
        "species_id": 494,
        "box_id": 0,
        "box_slot": 0,
        "party_copy_retained": True,
        "native_checks": [
            "PCBoxes_TryStoreBoxMonAt returned TRUE",
            "PCBoxes_GetBoxMonAt(0,0) species == SPECIES_VICTINI",
            "PCBoxes_CountAllBoxMons == 1",
            "Platinum native PC storage application launched",
        ],
        "next_if_passed": "checkpoint PC storage proof, then add isolated battle-entry proof",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
