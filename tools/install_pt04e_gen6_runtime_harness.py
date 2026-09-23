#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPRESENTATIVES = [
    ("SPECIES_VOLCANION", 721, "upper Gen VI canonical boundary"),
    ("SPECIES_CHESPIN", 650, "first Gen VI species / starter"),
    ("SPECIES_FLABEBE", 669, "female-only base-species resource path"),
    ("SPECIES_MEOWSTIC", 678, "gender/form-sensitive species data"),
    ("SPECIES_AEGISLASH", 681, "form-heavy species base resource path"),
    ("SPECIES_SYLVEON", 700, "Fairy-type representative"),
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
    parser.add_argument("--report", type=Path, default=Path("pt04e-gen6-runtime-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    text = field_map_change_c.read_text()
    victini_count = text.count("SPECIES_VICTINI")
    if victini_count < 4:
        raise SystemExit(
            "PT04E runtime harness expects the completed PT04C save/reload harness "
            f"before patching; found only {victini_count} SPECIES_VICTINI references"
        )

    # Reuse the sealed PT04C persistence machinery but move the primary
    # serialization boundary to Volcanion #721.
    text = text.replace("SPECIES_VICTINI", "SPECIES_VOLCANION")
    text = text.replace("reloadedVictini", "reloadedVolcanion")
    field_map_change_c.write_text(text)

    volcanion_give = """        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_VOLCANION,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));"""

    six_party = volcanion_give + """

        // PT04E representative Gen VI roster. Volcanion remains slot 0 so all
        // primary save/reload assertions exercise native species ID #721.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_CHESPIN, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_FLABEBE, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_MEOWSTIC, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_AEGISLASH, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_SYLVEON, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));

        GF_ASSERT(Party_GetCurrentCount(SaveData_GetParty(fieldSystem->saveData)) == 6);"""

    replace_once(
        field_map_change_c,
        volcanion_give,
        six_party,
        "six-species Gen VI party injection",
    )

    reload_anchor = """        Pokemon *reloadedVolcanion = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);
        GF_ASSERT(Pokemon_GetValue(reloadedVolcanion, MON_DATA_SPECIES, NULL) == SPECIES_VOLCANION);
        GF_ASSERT(Pokemon_GetValue(reloadedVolcanion, MON_DATA_LEVEL, NULL) == 50);"""

    reload_checks = reload_anchor + """

        Party *reloadedParty = SaveData_GetParty(fieldSystem->saveData);
        GF_ASSERT(Party_GetCurrentCount(reloadedParty) == 6);
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_CHESPIN));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_FLABEBE));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_MEOWSTIC));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_AEGISLASH));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_SYLVEON));

        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_FLABEBE));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_AEGISLASH));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_SYLVEON));"""

    replace_once(
        field_map_change_c,
        reload_anchor,
        reload_checks,
        "post-reload Gen VI representative assertions",
    )

    report = {
        "gate": "PT04E_GEN6_SAVE_RELOAD_RUNTIME_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "base_harness": "sealed PT04C native save/reload path",
        "primary_boundary": {
            "species": "SPECIES_VOLCANION",
            "species_id": 721,
            "party_slot": 0,
            "level": 50,
            "reason": "proves persistence at the canonical Gen VI upper boundary",
        },
        "representative_party": [
            {"species": species, "national_dex": dex, "purpose": purpose}
            for species, dex, purpose in REPRESENTATIVES
        ],
        "post_reload_checks": [
            "party count == 6",
            "slot 0 species == SPECIES_VOLCANION",
            "slot 0 level == 50",
            "all six representative species remain in party",
            "Volcanion seen/caught flags survive reload",
            "Flabebe, Aegislash, and Sylveon caught flags survive reload",
            "native Party application reopened after reload",
        ],
        "next_if_passed": "visually review post-reload six-slot Party screen, then test Volcanion battle rendering",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
