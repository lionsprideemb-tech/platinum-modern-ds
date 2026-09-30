#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("platinum", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    pt = args.platinum

    pokemon_h = pt / "include/struct_defs/pokemon.h"
    pokemon_c = pt / "src/pokemon.c"
    recording_h = pt / "include/struct_defs/struct_02078B40.h"

    # MP05 stores ability bits 8-9 in the top two marking bits. MR10 keeps the
    # visible six marking bits exactly where they are and uses one byte from
    # Platinum's otherwise-unused Block-B u16 for the complete high ability
    # byte. Every encrypted Pokemon block remains exactly the same size.
    pokemon_h_text = pokemon_h.read_text(encoding="utf-8")
    legacy_bitfield = """    /* 0x0C */ u8 friendship;
    /* 0x0D */ u8 ability;
    /* 0x0E */ u8 markings : 6;
    /*      */ u8 abilityHigh : 2;
    /* 0x0F */ u8 originLanguage;"""
    plain_markings = """    /* 0x0C */ u8 friendship;
    /* 0x0D */ u8 ability;
    /* 0x0E */ u8 markings;
    /* 0x0F */ u8 originLanguage;"""
    if legacy_bitfield in pokemon_h_text:
        replace_once(
            pokemon_h,
            legacy_bitfield,
            plain_markings,
            "legacy 10-bit Block-A layout",
        )
    elif plain_markings not in pokemon_h_text:
        raise SystemExit("PokemonDataBlockA markings/ability layout is unknown")

    replace_once(
        pokemon_h,
        """    /* 0x19 */ u8 unused1; //!< First 6 bits track Shiny Leaves from HGSS.
    /* 0x1A */ u16 unused2;""",
        """    /* 0x19 */ u8 unused1; //!< First 6 bits track Shiny Leaves from HGSS.
    /* 0x1A */ u8 abilityHigh; //!< Mercury: high byte of the 16-bit Ability ID.
    /* 0x1B */ u8 unused2;""",
        "Block-B high ability byte",
    )

    # MP05 getter -> full 16-bit getter. If a save predates MR10 and Block B's
    # new byte is still zero, recover bits 8-9 from the old marking-bit lane.
    replace_once(
        pokemon_c,
        """    case MON_DATA_ABILITY:
        result = monDataBlockA->ability
            | ((monDataBlockA->markings & MERCURY_ABILITY_HIGH_MASK) << 2);
        break;""",
        """    case MON_DATA_ABILITY: {
        u16 abilityHigh = monDataBlockB->abilityHigh;

        if (abilityHigh == 0 && (monDataBlockA->markings & MERCURY_ABILITY_HIGH_MASK) != 0) {
            abilityHigh = (monDataBlockA->markings & MERCURY_ABILITY_HIGH_MASK) >> 6;
        }

        result = monDataBlockA->ability | (abilityHigh << 8);
        break;
    }""",
        "16-bit Ability getter",
    )

    # Support the short-lived intermediate implementation too, so this
    # installer stays replay-safe across Mercury checkpoints.
    old_intermediate_getter = """    case MON_DATA_ABILITY:
        result = monDataBlockA->ability | (monDataBlockA->abilityHigh << 8);
        break;"""
    text = pokemon_c.read_text(encoding="utf-8")
    final_getter = """    case MON_DATA_ABILITY: {
        u16 abilityHigh = monDataBlockB->abilityHigh;

        if (abilityHigh == 0 && (monDataBlockA->markings & MERCURY_ABILITY_HIGH_MASK) != 0) {
            abilityHigh = (monDataBlockA->markings & MERCURY_ABILITY_HIGH_MASK) >> 6;
        }

        result = monDataBlockA->ability | (abilityHigh << 8);
        break;
    }"""
    if final_getter not in text and old_intermediate_getter in text:
        replace_once(
            pokemon_c,
            old_intermediate_getter,
            final_getter,
            "intermediate 10-bit Ability getter",
        )

    replace_once(
        pokemon_c,
        """    case MON_DATA_ABILITY: {
        u16 ability = *u16Value;
        GF_ASSERT(ability <= 1023);
        monDataBlockA->ability = ability & 0xFF;
        monDataBlockA->markings = (monDataBlockA->markings & ~MERCURY_ABILITY_HIGH_MASK)
            | ((ability >> 2) & MERCURY_ABILITY_HIGH_MASK);
        break;
    }""",
        """    case MON_DATA_ABILITY: {
        u16 ability = *u16Value;
        monDataBlockA->ability = ability & 0xFF;
        monDataBlockB->abilityHigh = (ability >> 8) & 0xFF;
        monDataBlockA->markings &= MERCURY_VISIBLE_MARKINGS_MASK;
        break;
    }""",
        "16-bit Ability setter",
    )

    old_intermediate_setter = """    case MON_DATA_ABILITY:
        monDataBlockA->ability = *u16Value & 0xFF;
        monDataBlockA->abilityHigh = (*u16Value >> 8) & 0x3;
        break;"""
    final_setter = """    case MON_DATA_ABILITY: {
        u16 ability = *u16Value;
        monDataBlockA->ability = ability & 0xFF;
        monDataBlockB->abilityHigh = (ability >> 8) & 0xFF;
        monDataBlockA->markings &= MERCURY_VISIBLE_MARKINGS_MASK;
        break;
    }"""
    text = pokemon_c.read_text(encoding="utf-8")
    if final_setter not in text and old_intermediate_setter in text:
        replace_once(
            pokemon_c,
            old_intermediate_setter,
            final_setter,
            "intermediate 10-bit Ability setter",
        )

    # Battle-recording metadata had two high bits in MP05. Expand that field
    # into eight of the already-spare flag bits without changing structure size.
    replace_once(
        recording_h,
        """    u16 partyDecrypted : 1;
    u16 boxDecrypted : 1;
    u16 checksumFailed : 1;
    u16 abilityHigh : 2;
    u16 : 11;""",
        """    u16 partyDecrypted : 1;
    u16 boxDecrypted : 1;
    u16 checksumFailed : 1;
    u16 abilityHigh : 8;
    u16 : 5;""",
        "battle-recording Ability high byte",
    )

    replace_once(
        pokemon_c,
        """    param1->ability = monDataBlockA->ability;
    param1->abilityHigh = (monDataBlockA->markings & MERCURY_ABILITY_HIGH_MASK) >> 6;""",
        """    param1->ability = monDataBlockA->ability;
    param1->abilityHigh = monDataBlockB->abilityHigh;""",
        "battle-recording Ability export",
    )
    replace_once(
        pokemon_c,
        """    monDataBlockA->ability = param0->ability;
    monDataBlockA->markings = (monDataBlockA->markings & ~MERCURY_ABILITY_HIGH_MASK)
        | ((param0->abilityHigh << 6) & MERCURY_ABILITY_HIGH_MASK);""",
        """    monDataBlockA->ability = param0->ability;
    monDataBlockB->abilityHigh = param0->abilityHigh;
    monDataBlockA->markings &= MERCURY_VISIBLE_MARKINGS_MASK;""",
        "battle-recording Ability import",
    )

    species_h = (pt / "include/struct_defs/species.h").read_text(encoding="utf-8")
    battle_h = (pt / "include/battle/battle_mon.h").read_text(encoding="utf-8")
    summary_h = (pt / "include/applications/pokemon_summary_screen/main.h").read_text(encoding="utf-8")
    final_pokemon_h = pokemon_h.read_text(encoding="utf-8")
    final_pokemon_c = pokemon_c.read_text(encoding="utf-8")
    final_recording_h = recording_h.read_text(encoding="utf-8")

    checks = {
        "species_runtime_u16": "u16 abilities[MAX_ABILITIES];" in species_h,
        "battle_runtime_u16": "u16 ability;" in battle_h,
        "summary_runtime_u16": "u16 ability;" in summary_h,
        "persistent_high_byte":
            "u8 abilityHigh; //!< Mercury: high byte of the 16-bit Ability ID."
            in final_pokemon_h,
        "no_block_a_ability_bitfield": "u8 abilityHigh : 2;" not in final_pokemon_h,
        "getter_uses_block_b": "u16 abilityHigh = monDataBlockB->abilityHigh;" in final_pokemon_c,
        "legacy_10bit_fallback": "MERCURY_ABILITY_HIGH_MASK) >> 6" in final_pokemon_c,
        "setter_writes_full_high_byte": "monDataBlockB->abilityHigh = (ability >> 8) & 0xFF;" in final_pokemon_c,
        "recording_high_byte": "u16 abilityHigh : 8;" in final_recording_h,
        "recording_export_full": "param1->abilityHigh = monDataBlockB->abilityHigh;" in final_pokemon_c,
        "recording_import_full": "monDataBlockB->abilityHigh = param0->abilityHigh;" in final_pokemon_c,
    }
    if not all(checks.values()):
        raise SystemExit(f"16-bit Ability storage validation failed: {checks}")

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
        "battle_recording_layout_growth_bytes": 0,
        "runtime_species_width_bits": 16,
        "runtime_battle_width_bits": 16,
        "runtime_summary_width_bits": 16,
        "roundtrip_probe_ids": [0, 255, 256, 1023, 1024, 1042, 2047, 65535],
        "checks": checks,
        "status": "PASS_STATIC",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
