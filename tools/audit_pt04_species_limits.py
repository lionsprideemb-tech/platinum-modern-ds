#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TARGET_NATIONAL_DEX_COUNT = 1025
TARGET_MAX_SPECIES = TARGET_NATIONAL_DEX_COUNT + 2
TARGET_DEX_WORDS = (TARGET_NATIONAL_DEX_COUNT - 1) // 32 + 1


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"PT04 audit failed: {label}: missing {needle!r}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: audit_pt04_species_limits.py <pokeplatinum-root>")

    root = Path(sys.argv[1]).resolve()
    species_h = (root / "include/constants/species.h").read_text()
    mon_h = (root / "include/struct_defs/pokemon.h").read_text()
    pokedex_h = (root / "include/pokedex.h").read_text()
    save_table_c = (root / "src/savedata/save_table.c").read_text()
    species_meson = (root / "res/pokemon/meson.build").read_text()
    species_txt = (root / "generated/species.txt").read_text().splitlines()

    require(mon_h, "u16 species;", "BoxPokemon species width")
    require(mon_h, "u8 form : 5;", "persistent form width")
    require(species_h, "#define MAX_SPECIES        SPECIES_BAD_EGG", "MAX_SPECIES derivation")
    require(species_h, "#define NATIONAL_DEX_COUNT (MAX_SPECIES - 2)", "National Dex derivation")
    require(
        pokedex_h,
        "#define DEX_SIZE_U32 ((int)((NATIONAL_DEX_COUNT - 1) / 32) + 1)",
        "dynamic Pokédex bitset sizing",
    )
    require(
        save_table_c,
        "(SaveEntrySizeFunc)Pokedex_SaveSize",
        "dynamic Pokédex save-table sizing",
    )
    require(
        species_meson,
        "species_consts = fs.read(species_txt).splitlines()",
        "species registry drives asset build",
    )
    require(
        species_meson,
        "foreach species : species_dirnames",
        "species directory walk",
    )

    expected_tail = ["SPECIES_ARCEUS", "SPECIES_EGG", "SPECIES_BAD_EGG"]
    if species_txt[-3:] != expected_tail:
        raise SystemExit(
            "PT04 audit failed: unexpected vanilla species registry tail: "
            + repr(species_txt[-3:])
        )

    current_national = len(species_txt) - 3  # NONE + base species + EGG + BAD_EGG
    if current_national != 493:
        raise SystemExit(f"PT04 audit failed: expected vanilla count 493, got {current_national}")

    report = {
        "gate": "PT04A_POKEDEX_EXPANSION_CAPACITY",
        "upstream_current_national_dex_count": current_national,
        "target_national_dex_count": TARGET_NATIONAL_DEX_COUNT,
        "target_max_species_sentinel": TARGET_MAX_SPECIES,
        "species_storage_bits": 16,
        "species_storage_target_safe": TARGET_MAX_SPECIES <= 0xFFFF,
        "persistent_form_bits": 5,
        "persistent_form_max": 31,
        "extended_form_architecture_required": True,
        "current_dex_words": (current_national - 1) // 32 + 1,
        "target_dex_words": TARGET_DEX_WORDS,
        "pokedex_bitsets_dynamic": True,
        "pokedex_save_entry_dynamic_size": True,
        "species_registry_drives_archives": True,
        "next_gate": "PT04B_REGISTRY_EXPANSION_HARNESS",
    }

    Path("pt04-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
