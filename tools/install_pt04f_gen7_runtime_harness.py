#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPRESENTATIVES = [
    ("SPECIES_MELMETAL", 809, "upper Gen VII canonical boundary"),
    ("SPECIES_ROWLET", 722, "first Gen VII species / starter"),
    ("SPECIES_ORICORIO", 741, "multi-form species base resource path"),
    ("SPECIES_SALAZZLE", 758, "female-only species resource path"),
    ("SPECIES_SILVALLY", 773, "type/form-sensitive species data"),
    ("SPECIES_MIMIKYU", 778, "form-heavy species base resource path"),
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
    parser.add_argument("--report", type=Path, default=Path("pt04f-gen7-runtime-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    text = field_map_change_c.read_text()
    victini_count = text.count("SPECIES_VICTINI")
    if victini_count < 4:
        raise SystemExit(
            "PT04F runtime harness expects the completed PT04C save/reload harness "
            f"before patching; found only {victini_count} SPECIES_VICTINI references"
        )

    text = text.replace("SPECIES_VICTINI", "SPECIES_MELMETAL")
    text = text.replace("reloadedVictini", "reloadedMelmetal")
    field_map_change_c.write_text(text)

    melmetal_give = """        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3,
            fieldSystem->saveData,
            SPECIES_MELMETAL,
            50,
            ITEM_NONE,
            fieldSystem->location->mapHeaderID,
            0));"""

    six_party = melmetal_give + """

        // PT04F representative Gen VII roster. Melmetal remains slot 0 so all
        // primary save/reload assertions exercise native species ID #809.
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_ROWLET, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_ORICORIO, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_SALAZZLE, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_SILVALLY, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));
        GF_ASSERT(Pokemon_GiveMonFromScript(
            HEAP_ID_FIELD3, fieldSystem->saveData, SPECIES_MIMIKYU, 50,
            ITEM_NONE, fieldSystem->location->mapHeaderID, 0));

        GF_ASSERT(Party_GetCurrentCount(SaveData_GetParty(fieldSystem->saveData)) == 6);"""

    replace_once(
        field_map_change_c,
        melmetal_give,
        six_party,
        "six-species Gen VII party injection",
    )

    reload_anchor = """        Pokemon *reloadedMelmetal = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            0);
        GF_ASSERT(Pokemon_GetValue(reloadedMelmetal, MON_DATA_SPECIES, NULL) == SPECIES_MELMETAL);
        GF_ASSERT(Pokemon_GetValue(reloadedMelmetal, MON_DATA_LEVEL, NULL) == 50);"""

    reload_checks = reload_anchor + """

        Party *reloadedParty = SaveData_GetParty(fieldSystem->saveData);
        GF_ASSERT(Party_GetCurrentCount(reloadedParty) == 6);
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_ROWLET));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_ORICORIO));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_SALAZZLE));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_SILVALLY));
        GF_ASSERT(Party_HasSpecies(reloadedParty, SPECIES_MIMIKYU));

        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_ORICORIO));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_SALAZZLE));
        GF_ASSERT(Pokedex_HasCaughtSpecies(
            SaveData_GetPokedex(fieldSystem->saveData),
            SPECIES_MIMIKYU));"""

    replace_once(
        field_map_change_c,
        reload_anchor,
        reload_checks,
        "post-reload Gen VII representative assertions",
    )

    report = {
        "gate": "PT04F_GEN7_SAVE_RELOAD_RUNTIME_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "base_harness": "sealed PT04C native save/reload path",
        "primary_boundary": {
            "species": "SPECIES_MELMETAL",
            "species_id": 809,
            "party_slot": 0,
            "level": 50,
            "reason": "proves persistence at the canonical Gen VII upper boundary",
        },
        "representative_party": [
            {"species": species, "national_dex": dex, "purpose": purpose}
            for species, dex, purpose in REPRESENTATIVES
        ],
        "post_reload_checks": [
            "party count == 6",
            "slot 0 species == SPECIES_MELMETAL",
            "slot 0 level == 50",
            "all six representative species remain in party",
            "Melmetal seen/caught flags survive reload",
            "Oricorio, Salazzle, and Mimikyu caught flags survive reload",
            "native Party application reopened after reload",
        ],
        "next_if_passed": "visually review post-reload six-slot Party screen, then test Melmetal battle rendering",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
