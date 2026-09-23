#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def insert_include_once(path: Path, anchor: str, include_line: str, label: str) -> None:
    text = path.read_text()
    if include_line in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one include anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + include_line, 1))


def replace_block(path: Path, start_marker: str, end_marker: str, replacement: str, label: str) -> None:
    text = path.read_text()
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker missing in {path}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker missing in {path}")
    end += len(end_marker)
    if text.find(start_marker, start + 1) >= 0:
        raise SystemExit(f"{label}: duplicate start marker in {path}")
    path.write_text(text[:start] + replacement + text[end:])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04c-battle-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    insert_include_once(
        field_map_change_c,
        '#include "constants/heap.h"\n',
        '#include "constants/battle.h"\n',
        "battle constants include",
    )
    insert_include_once(
        field_map_change_c,
        '#include "overlay006/hm_cut_in.h"\n',
        '#include "overlay006/wild_encounters.h"\n',
        "scripted wild encounter include",
    )
    insert_include_once(
        field_map_change_c,
        '#include "field_bgm.h"\n',
        '#include "field_battle_data_transfer.h"\n',
        "battle DTO include",
    )

    start_marker = "        // PT04C PC-storage phase: store the proven Victini into the native"
    end_marker = "        FieldSystem_OpenPokemonStorage(fieldSystem, storageSession);"
    replacement = """        // PT04C battle control: use a native species but drive the real battle
        // application directly after finishing the field map. This bypasses
        // only the synthetic new-save encounter-effect transition, letting us
        // distinguish transition issues from battle/species issues.
        Party *controlParty = SaveData_GetParty(fieldSystem->saveData);
        GF_ASSERT(Party_HasSpecies(controlParty, SPECIES_VICTINI));
        GF_ASSERT(Party_RemovePokemonBySlotIndex(controlParty, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_MEW,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));
        GF_ASSERT(Party_HasSpecies(controlParty, SPECIES_MEW));

        FieldTransition_FinishMap(task);"""

    replace_block(
        field_map_change_c,
        start_marker,
        end_marker,
        replacement,
        "battle entry hook",
    )

    post_pc_case = """    case 3:
        if (!FieldSystem_IsRunningApplication(fieldSystem)) {
            return TRUE;
        }
        break;"""
    direct_battle_cases = """    case 3:
        // The map process is now finished. Build a normal wild-battle DTO,
        // including a copy of the player's actual party, then launch Platinum's
        // native battle overlay directly.
        FieldBattleDTO *dto = FieldBattleDTO_New(HEAP_ID_FIELD2, BATTLE_TYPE_WILD_MON);
        FieldBattleDTO_Init(dto, fieldSystem);
        CreateWildMon_Scripted(fieldSystem, SPECIES_BIDOOF, 5, dto);
        FieldSystem_StartBattleProcess(fieldSystem, dto);
        (*state)++;
        break;
    case 4:
        if (FieldSystem_IsRunningApplication(fieldSystem)) {
            break;
        }
        return TRUE;"""
    text = field_map_change_c.read_text()
    count = text.count(post_pc_case)
    if count != 1:
        raise SystemExit(f"direct battle state hook: expected one match, found {count}")
    field_map_change_c.write_text(text.replace(post_pc_case, direct_battle_cases, 1))

    report = {
        "gate": "PT04C_VICTINI_NATIVE_BATTLE_ENTRY_HARNESS_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "prerequisite": "PT04C native PC storage checkpoint Run #13",
        "player_species": "SPECIES_MEW_CONTROL",
        "player_species_id": 151,
        "opponent_species": "SPECIES_BIDOOF",
        "opponent_level": 5,
        "native_entrypoint": "FieldSystem_StartBattleProcess",
        "native_checks": [
            "Party_HasSpecies(SPECIES_MEW)",
            "native FieldBattleDTO initialized with player party + scripted Bidoof",
            "battle application must remain alive for visual proof",
        ],
        "next_if_passed": "visually verify native Mew control; then restore Victini and isolate species-494 battle-only fault",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
