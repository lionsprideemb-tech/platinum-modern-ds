#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPRESENTATIVES = [
    ("SPECIES_ENAMORUS", 905, "upper Gen VIII canonical boundary / female-only"),
    ("SPECIES_GROOKEY", 810, "first Gen VIII species / starter"),
    ("SPECIES_TOXTRICITY", 849, "form-sensitive species base resource path"),
    ("SPECIES_INDEEDEE", 876, "gender/form-sensitive species data"),
    ("SPECIES_MORPEKO", 877, "form-heavy species base resource path"),
    ("SPECIES_ZACIAN", 888, "item/form-sensitive legendary base data"),
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
    parser.add_argument("--report", type=Path, default=Path("pt04g-gen8-runtime-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    text = field_map_change_c.read_text()
    victini_count = text.count("SPECIES_VICTINI")
    if victini_count < 4:
        raise SystemExit(
            "PT04G runtime harness expects the completed PT04C save/reload harness "
            f"before patching; found only {victini_count} SPECIES_VICTINI references"
        )

    text = text.replace("SPECIES_VICTINI", "SPECIES_ENAMORUS")
    text = text.replace("reloadedVictini", "reloadedEnamorus")
    field_map_change_c.write_text(text)

    enamorus_give = """        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_ENAMORUS,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));"""

    six_party = enamorus_give + """

        // PT04G representative Gen VIII roster. Enamorus remains slot 0 so all
        // primary save/reload assertions exercise native species ID #905.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_GROOKEY, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_TOXTRICITY, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_INDEEDEE, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_MORPEKO, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_ZACIAN, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));

        GF_ASSERT(Party_GetCurrentCount(SaveData_GetParty(fieldSystem->saveData)) == 6);"""

    replace_once(
        field_map_change_c,
        enamorus_give,
        six_party,
        "six-species Gen VIII party injection",
    )

    reload_anchor = """        Pokemon *reloadedEnamorus = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);
        GF_ASSERT(Pokemon_GetValue(reloadedEnamorus, MON_DATA_SPECIES, NULL) == SPECIES_ENAMORUS);
        GF_ASSERT(Pokemon_GetValue(reloadedEnamorus, MON_DATA_LEVEL, NULL) == 50);"""

    reload_checks = reload_anchor + """

        Party *reloadedParty = SaveData_GetParty(fieldSystem->saveData);
        GF_ASSERT(Party_GetCurrentCount(reloadedParty) == 6);
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_GROOKEY));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_TOXTRICITY));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_INDEEDEE));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_MORPEKO));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_ZACIAN));

        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_TOXTRICITY));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_INDEEDEE));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_ZACIAN));"""

    replace_once(
        field_map_change_c,
        reload_anchor,
        reload_checks,
        "post-reload Gen VIII representative assertions",
    )

    report = {
        "gate": "PT04G_GEN8_SAVE_RELOAD_RUNTIME_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "base_harness": "sealed PT04C native save/reload path",
        "primary_boundary": {
            "species": "SPECIES_ENAMORUS",
            "species_id": 905,
            "party_slot": 0,
            "level": 50,
            "reason": "proves persistence at the canonical Gen VIII upper boundary",
        },
        "representative_party": [
            {"species": species, "national_dex": dex, "purpose": purpose}
            for species, dex, purpose in REPRESENTATIVES
        ],
        "post_reload_checks": [
            "party count == 6",
            "slot 0 species == SPECIES_ENAMORUS",
            "slot 0 level == 50",
            "all six representative species remain in party",
            "Enamorus seen/caught flags survive reload",
            "Toxtricity, Indeedee, and Zacian caught flags survive reload",
            "native Party application reopened after reload",
        ],
        "next_if_passed": "visually review post-reload six-slot Party screen, then test Enamorus battle rendering",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
