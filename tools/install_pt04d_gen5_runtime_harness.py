#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPRESENTATIVES = [
    ("SPECIES_GENESECT", 649, "upper Gen V / >511 boundary"),
    ("SPECIES_VICTINI", 494, "first post-Gen-IV species"),
    ("SPECIES_SNIVY", 495, "ordinary Gen V starter"),
    ("SPECIES_COTTONEE", 546, "Fairy-enabled modern typing"),
    ("SPECIES_DEERLING", 585, "dual-gender donor resources"),
    ("SPECIES_MANDIBUZZ", 630, "female-only donor resources"),
]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04d-gen5-runtime-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    text = field_map_change_c.read_text()
    victini_count = text.count("SPECIES_VICTINI")
    if victini_count < 4:
        raise SystemExit(
            "PT04D runtime harness expects the completed PT04C save/reload harness "
            f"before patching; found only {victini_count} SPECIES_VICTINI references"
        )

    # Reuse the sealed PT04C persistence harness, but put the upper Gen V
    # boundary in slot 0 so every save/reload species assertion crosses 511.
    text = text.replace("SPECIES_VICTINI", "SPECIES_GENESECT")
    text = text.replace("reloadedVictini", "reloadedGenesect")
    field_map_change_c.write_text(text)

    genesect_give = """        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_GENESECT,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));"""

    six_party = genesect_give + """

        // PT04D representative roster. These additional species exercise the
        // beginning, middle, Fairy-typed, dual-gender, and female-only parts of
        // the Gen V batch while Genesect remains slot 0 for the >511 boundary.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_VICTINI, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_SNIVY, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_COTTONEE, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_DEERLING, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_MANDIBUZZ, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));

        GF_ASSERT(Party_GetCurrentCount(SaveData_GetParty(fieldSystem->saveData)) == 6);"""

    replace_once(
        field_map_change_c,
        genesect_give,
        six_party,
        "six-species Gen V party injection",
    )

    reload_anchor = """        Pokemon *reloadedGenesect = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);
        GF_ASSERT(Pokemon_GetValue(reloadedGenesect, MON_DATA_SPECIES, NULL) == SPECIES_GENESECT);
        GF_ASSERT(Pokemon_GetValue(reloadedGenesect, MON_DATA_LEVEL, NULL) == 50);"""

    reload_checks = reload_anchor + """

        Party *reloadedParty = SaveData_GetParty(fieldSystem->saveData);
        GF_ASSERT(Party_GetCurrentCount(reloadedParty) == 6);
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_VICTINI));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_SNIVY));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_COTTONEE));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_DEERLING));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_MANDIBUZZ));

        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_COTTONEE));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_MANDIBUZZ));"""

    replace_once(
        field_map_change_c,
        reload_anchor,
        reload_checks,
        "post-reload Gen V representative assertions",
    )

    report = {
        "gate": "PT04D_GEN5_SAVE_RELOAD_RUNTIME_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "base_harness": "sealed PT04C native save/reload path",
        "primary_boundary": {
            "species": "SPECIES_GENESECT",
            "species_id": 649,
            "party_slot": 0,
            "level": 50,
            "reason": "crosses the 511/512 species-ID boundary not exercised by Victini #494",
        },
        "representative_party": [
            {"species": species, "national_dex": dex, "purpose": purpose}
            for species, dex, purpose in REPRESENTATIVES
        ],
        "post_reload_checks": [
            "party count == 6",
            "slot 0 species == SPECIES_GENESECT",
            "slot 0 level == 50",
            "all six representative species remain in party",
            "Genesect seen/caught flags survive reload",
            "Cottonee and Mandibuzz caught flags survive reload",
            "native Party application reopened after reload",
        ],
        "next_if_passed": "visually review post-reload six-slot Party screen, then test Genesect battle rendering",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
