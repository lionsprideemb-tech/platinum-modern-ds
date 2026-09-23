#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPRESENTATIVES = [
    ("SPECIES_PECHARUNT", 1025, "upper canonical National Dex boundary"),
    ("SPECIES_SPRIGATITO", 906, "first Gen IX species / starter"),
    ("SPECIES_PALAFIN", 964, "form-sensitive modern species base resource path"),
    ("SPECIES_KINGAMBIT", 983, "modern evolution-line / late-generation species path"),
    ("SPECIES_KORAIDON", 1007, "legendary / Paradox-era base resource path"),
    ("SPECIES_TERAPAGOS", 1024, "form-heavy penultimate canonical species"),
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
    parser.add_argument("--report", type=Path, default=Path("pt04h-gen9-runtime-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    text = field_map_change_c.read_text()
    victini_count = text.count("SPECIES_VICTINI")
    if victini_count < 4:
        raise SystemExit(
            "PT04H runtime harness expects the completed PT04C save/reload harness "
            f"before patching; found only {victini_count} SPECIES_VICTINI references"
        )

    text = text.replace("SPECIES_VICTINI", "SPECIES_PECHARUNT")
    text = text.replace("reloadedVictini", "reloadedPecharunt")
    field_map_change_c.write_text(text)

    pecharunt_give = """        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_PECHARUNT,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));"""

    six_party = pecharunt_give + """

        // PT04H representative Gen IX roster. Pecharunt remains slot 0 so all
        // primary save/reload assertions exercise native species ID #1025.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_SPRIGATITO, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_PALAFIN, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_KINGAMBIT, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_KORAIDON, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_TERAPAGOS, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));

        GF_ASSERT(Party_GetCurrentCount(SaveData_GetParty(fieldSystem->saveData)) == 6);"""

    replace_once(
        field_map_change_c,
        pecharunt_give,
        six_party,
        "six-species Gen IX party injection",
    )

    reload_anchor = """        Pokemon *reloadedPecharunt = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);
        GF_ASSERT(Pokemon_GetValue(reloadedPecharunt, MON_DATA_SPECIES, NULL) == SPECIES_PECHARUNT);
        GF_ASSERT(Pokemon_GetValue(reloadedPecharunt, MON_DATA_LEVEL, NULL) == 50);"""

    reload_checks = reload_anchor + """

        Party *reloadedParty = SaveData_GetParty(fieldSystem->saveData);
        GF_ASSERT(Party_GetCurrentCount(reloadedParty) == 6);
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_SPRIGATITO));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_PALAFIN));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_KINGAMBIT));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_KORAIDON));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_TERAPAGOS));

        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_PALAFIN));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_KINGAMBIT));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_TERAPAGOS));"""

    replace_once(
        field_map_change_c,
        reload_anchor,
        reload_checks,
        "post-reload Gen IX representative assertions",
    )

    report = {
        "gate": "PT04H_GEN9_SAVE_RELOAD_RUNTIME_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "base_harness": "sealed PT04C native save/reload path",
        "primary_boundary": {
            "species": "SPECIES_PECHARUNT",
            "species_id": 1025,
            "party_slot": 0,
            "level": 50,
            "reason": "proves persistence at the final canonical National Dex boundary",
        },
        "representative_party": [
            {"species": species, "national_dex": dex, "purpose": purpose}
            for species, dex, purpose in REPRESENTATIVES
        ],
        "post_reload_checks": [
            "party count == 6",
            "slot 0 species == SPECIES_PECHARUNT",
            "slot 0 level == 50",
            "all six representative species remain in party",
            "Pecharunt seen/caught flags survive reload",
            "Palafin, Kingambit, and Terapagos caught flags survive reload",
            "native Party application reopened after reload",
        ],
        "next_if_passed": "visually review post-reload six-slot Party screen, then test Pecharunt battle rendering",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
