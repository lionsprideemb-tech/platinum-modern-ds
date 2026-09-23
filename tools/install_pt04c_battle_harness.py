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
        '#include "field_bgm.h"\n',
        '#include "encounter.h"\n',
        "encounter include",
    )

    start_marker = "        // PT04C PC-storage phase: store the proven Victini into the native"
    end_marker = "        FieldSystem_OpenPokemonStorage(fieldSystem, storageSession);"
    replacement = """        // PT04C battle-entry phase: keep the already-proven native Victini
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

    replace_block(
        field_map_change_c,
        start_marker,
        end_marker,
        replacement,
        "battle entry hook",
    )

    report = {
        "gate": "PT04C_VICTINI_NATIVE_BATTLE_ENTRY_HARNESS_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "prerequisite": "PT04C native PC storage checkpoint Run #13",
        "player_species": "SPECIES_VICTINI",
        "player_species_id": 494,
        "opponent_species": "SPECIES_BIDOOF",
        "opponent_level": 5,
        "native_entrypoint": "Encounter_NewVsSpeciesAtLevel",
        "native_checks": [
            "Party_HasSpecies(SPECIES_VICTINI)",
            "real scripted wild encounter path launched",
            "battle application must remain alive for visual proof",
        ],
        "next_if_passed": "checkpoint battle entry proof, then add isolated save/reload proof",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
