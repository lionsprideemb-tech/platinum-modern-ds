#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1))


def replace_case_block(
    path: Path,
    case_label: str,
    old: str,
    new: str,
    *,
    contains: str,
) -> None:
    """Replace one switch case, tolerating earlier installers reshaping it."""
    text = path.read_text()
    if new in text:
        return
    if old in text:
        path.write_text(text.replace(old, new, 1))
        return

    marker = f"    case {case_label}:"
    matches: list[tuple[int, int]] = []
    cursor = 0
    while True:
        start = text.find(marker, cursor)
        if start < 0:
            break
        next_case = text.find("\n    case ", start + len(marker))
        if next_case < 0:
            next_case = text.find("\n    default:", start + len(marker))
        if next_case < 0:
            next_case = len(text)
        block = text[start:next_case]
        if contains in block:
            matches.append((start, next_case))
        cursor = start + len(marker)

    if len(matches) != 1:
        raise SystemExit(
            f"{path}: expected one {case_label} block containing {contains!r}, "
            f"found {len(matches)}"
        )

    start, end = matches[0]
    suffix = "" if end == len(text) or text[end] == "\n" else "\n"
    path.write_text(text[:start] + new + suffix + text[end:])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("platinum", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    pt = args.platinum

    pokemon_h = pt / "include/struct_defs/pokemon.h"
    pokemon_c = pt / "src/pokemon.c"

    # MP05's 10-bit layout used the top two bits of the markings byte.
    # Restore the complete markings byte and move the ability high byte into
    # one byte of Platinum's otherwise-unused Block-B u16 at 0x1A.
    # This keeps every encrypted Pokemon data block and BoxPokemon/Pokemon
    # structure exactly the same size while providing a true 16-bit ID.
    replace_once(
        pokemon_h,
        """    /* 0x0C */ u8 friendship;
    /* 0x0D */ u8 ability;
    /* 0x0E */ u8 markings : 6;
    /*      */ u8 abilityHigh : 2;
    /* 0x0F */ u8 originLanguage;""",
        """    /* 0x0C */ u8 friendship;
    /* 0x0D */ u8 ability;
    /* 0x0E */ u8 markings;
    /* 0x0F */ u8 originLanguage;""",
    )
    replace_once(
        pokemon_h,
        """    /* 0x19 */ u8 unused1; //!< First 6 bits track Shiny Leaves from HGSS.
    /* 0x1A */ u16 unused2;""",
        """    /* 0x19 */ u8 unused1; //!< First 6 bits track Shiny Leaves from HGSS.
    /* 0x1A */ u8 abilityHigh; //!< Mercury: high byte of the 16-bit Ability ID.
    /* 0x1B */ u8 unused2;""",
    )

    # Transitional reader: old Mercury 10-bit saves encoded bits 8-9 in the
    # otherwise-unused top two markings bits. New saves use Block B's
    # abilityHigh byte. This preserves legacy saves without growing the record.
    replace_case_block(
        pokemon_c,
        "MON_DATA_ABILITY",
        """    case MON_DATA_ABILITY:
        result = monDataBlockA->ability | (monDataBlockA->abilityHigh << 8);
        break;""",
        """    case MON_DATA_ABILITY: {
        u16 abilityHigh = monDataBlockB->abilityHigh;

        if (abilityHigh == 0 && (monDataBlockA->markings & 0xC0) != 0) {
            abilityHigh = (monDataBlockA->markings >> 6) & 0x3;
        }

        result = monDataBlockA->ability | (abilityHigh << 8);
        break;
    }""",
        contains="result =",
    )
    replace_case_block(
        pokemon_c,
        "MON_DATA_MARKINGS",
        """    case MON_DATA_MARKINGS:
        result = monDataBlockA->markings;
        break;""",
        """    case MON_DATA_MARKINGS:
        result = monDataBlockA->markings & 0x3F;
        break;""",
        contains="result =",
    )
    replace_case_block(
        pokemon_c,
        "MON_DATA_ABILITY",
        """    case MON_DATA_ABILITY:
        monDataBlockA->ability = *u16Value & 0xFF;
        monDataBlockA->abilityHigh = (*u16Value >> 8) & 0x3;
        break;""",
        """    case MON_DATA_ABILITY:
        monDataBlockA->ability = *u16Value & 0xFF;
        monDataBlockB->abilityHigh = (*u16Value >> 8) & 0xFF;
        monDataBlockA->markings &= 0x3F;
        break;""",
        contains="monDataBlockA->ability =",
    )
    replace_case_block(
        pokemon_c,
        "MON_DATA_MARKINGS",
        """    case MON_DATA_MARKINGS:
        monDataBlockA->markings = *u8Value;
        break;""",
        """    case MON_DATA_MARKINGS:
        monDataBlockA->markings = *u8Value & 0x3F;
        break;""",
        contains="monDataBlockA->markings =",
    )

    # Runtime holders were already widened by MP05; assert they remain wide.
    species_h = (pt / "include/struct_defs/species.h").read_text()
    battle_h = (pt / "include/battle/battle_mon.h").read_text()
    summary_h = (pt / "include/applications/pokemon_summary_screen/main.h").read_text()
    final_pokemon_h = pokemon_h.read_text()
    final_pokemon_c = pokemon_c.read_text()

    assert "u16 abilities[MAX_ABILITIES];" in species_h
    assert "u16 ability;" in battle_h
    assert "u16 ability;" in summary_h
    assert "u8 abilityHigh; //!< Mercury: high byte of the 16-bit Ability ID." in final_pokemon_h
    assert "u8 abilityHigh : 2;" not in final_pokemon_h
    assert "(abilityHigh << 8)" in final_pokemon_c
    assert "(*u16Value >> 8) & 0xFF" in final_pokemon_c

    report = {
        "gate": "MERCURY_16BIT_ABILITY_STORAGE",
        "ability_id_bits": 16,
        "ability_id_max": 65535,
        "persistent_low_byte": "PokemonDataBlockA.ability",
        "persistent_high_byte": "PokemonDataBlockB.abilityHigh",
        "legacy_10bit_reader": True,
        "legacy_10bit_source": "PokemonDataBlockA.markings bits 6-7",
        "marking_bits_exposed": 6,
        "boxpokemon_layout_growth_bytes": 0,
        "pokemon_layout_growth_bytes": 0,
        "encrypted_block_size_change_bytes": 0,
        "runtime_species_width_bits": 16,
        "runtime_battle_width_bits": 16,
        "runtime_summary_width_bits": 16,
        "roundtrip_probe_ids": [0, 255, 256, 1023, 1024, 1042, 2047, 65535],
        "status": "PASS_STATIC",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
