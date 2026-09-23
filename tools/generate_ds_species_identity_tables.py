#!/usr/bin/env python3
"""Generate Mercury DS canonical species identity lookup tables.

Production Mercury DS keeps Platinum/HG-Engine internal IDs stable:
- 0: NONE
- 1..493: Gen I-IV canonical species
- 494: Egg
- 495: Bad Egg
- 496..543: legacy/reserved DS slots
- 544..1075: National Dex 494..1025

The runtime must therefore translate between internal species IDs and canonical
National Dex numbers instead of assuming both numbers are identical.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_ds_species_id_map import (
    BAD_EGG_INTERNAL_ID,
    CANONICAL_SPECIES_COUNT,
    EGG_INTERNAL_ID,
    FIRST_MODERN_INTERNAL_ID,
    LEGACY_RESERVED_FIRST,
    LEGACY_RESERVED_LAST,
    build_map,
    load_species,
)

LAST_CANONICAL_INTERNAL_ID = 1075


def build_tables(mapping: dict) -> tuple[list[int], list[int]]:
    internal_to_natdex = [0] * (LAST_CANONICAL_INTERNAL_ID + 1)
    natdex_to_internal = [0] * (CANONICAL_SPECIES_COUNT + 1)

    for entry in mapping["species"]:
        dex = entry["national_dex"]
        internal = entry["internal_species_id"]

        if internal_to_natdex[internal] != 0:
            raise SystemExit(f"duplicate internal ID in lookup table: {internal}")
        if natdex_to_internal[dex] != 0:
            raise SystemExit(f"duplicate National Dex number in lookup table: {dex}")

        internal_to_natdex[internal] = dex
        natdex_to_internal[dex] = internal

    # These are not canonical Pokemon identities and must never alias a NatDex.
    for reserved in [
        EGG_INTERNAL_ID,
        BAD_EGG_INTERNAL_ID,
        *range(LEGACY_RESERVED_FIRST, LEGACY_RESERVED_LAST + 1),
    ]:
        if internal_to_natdex[reserved] != 0:
            raise SystemExit(f"reserved internal ID {reserved} maps to a National Dex entry")

    for dex in range(1, CANONICAL_SPECIES_COUNT + 1):
        internal = natdex_to_internal[dex]
        if internal == 0:
            raise SystemExit(f"missing internal ID for National Dex {dex}")
        if internal_to_natdex[internal] != dex:
            raise SystemExit(
                f"round-trip failure: NatDex {dex} -> internal {internal} -> "
                f"NatDex {internal_to_natdex[internal]}"
            )

    return internal_to_natdex, natdex_to_internal


def format_array(values: list[int], per_line: int = 12) -> str:
    rows = []
    for i in range(0, len(values), per_line):
        rows.append("    " + ", ".join(str(v) for v in values[i : i + per_line]) + ",")
    return "\n".join(rows)


def emit_header(path: Path) -> None:
    path.write_text(
        """#ifndef MERCURY_DS_GENERATED_SPECIES_IDENTITY_H
#define MERCURY_DS_GENERATED_SPECIES_IDENTITY_H

#include <nitro.h>

#define MERCURY_CANONICAL_SPECIES_COUNT 1025
#define MERCURY_EGG_INTERNAL_ID 494
#define MERCURY_BAD_EGG_INTERNAL_ID 495
#define MERCURY_LEGACY_RESERVED_FIRST 496
#define MERCURY_LEGACY_RESERVED_LAST 543
#define MERCURY_FIRST_MODERN_INTERNAL_ID 544
#define MERCURY_LAST_CANONICAL_INTERNAL_ID 1075

extern const u16 gMercuryInternalSpeciesToNationalDex[
    MERCURY_LAST_CANONICAL_INTERNAL_ID + 1];
extern const u16 gMercuryNationalDexToInternalSpecies[
    MERCURY_CANONICAL_SPECIES_COUNT + 1];

u16 MercurySpecies_ToNationalDex(u16 internalSpecies);
u16 MercurySpecies_FromNationalDex(u16 nationalDex);
BOOL MercurySpecies_IsCanonical(u16 internalSpecies);

#endif // MERCURY_DS_GENERATED_SPECIES_IDENTITY_H
"""
    )


def emit_source(path: Path, internal_to_natdex: list[int], natdex_to_internal: list[int]) -> None:
    path.write_text(
        """#include "generated/mercury_species_identity.h"

const u16 gMercuryInternalSpeciesToNationalDex[
    MERCURY_LAST_CANONICAL_INTERNAL_ID + 1] = {
"""
        + format_array(internal_to_natdex)
        + """
};

const u16 gMercuryNationalDexToInternalSpecies[
    MERCURY_CANONICAL_SPECIES_COUNT + 1] = {
"""
        + format_array(natdex_to_internal)
        + """
};

u16 MercurySpecies_ToNationalDex(u16 internalSpecies)
{
    if (internalSpecies > MERCURY_LAST_CANONICAL_INTERNAL_ID) {
        return 0;
    }

    return gMercuryInternalSpeciesToNationalDex[internalSpecies];
}

u16 MercurySpecies_FromNationalDex(u16 nationalDex)
{
    if (nationalDex == 0 || nationalDex > MERCURY_CANONICAL_SPECIES_COUNT) {
        return 0;
    }

    return gMercuryNationalDexToInternalSpecies[nationalDex];
}

BOOL MercurySpecies_IsCanonical(u16 internalSpecies)
{
    return MercurySpecies_ToNationalDex(internalSpecies) != 0;
}
"""
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--species",
        type=Path,
        default=Path("data/canonical_species_1025.txt"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("build/pt05a"),
    )
    args = parser.parse_args()

    species = load_species(args.species)
    mapping = build_map(species)
    internal_to_natdex, natdex_to_internal = build_tables(mapping)

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    header = out / "mercury_species_identity.h"
    source = out / "mercury_species_identity.c"
    mapping_path = out / "species_id_map.json"
    report_path = out / "pt05a-species-identity-report.json"

    emit_header(header)
    emit_source(source, internal_to_natdex, natdex_to_internal)
    mapping_path.write_text(json.dumps(mapping, indent=2) + "\n")

    proof = {
        "gate": "PT05A_SPECIES_IDENTITY_LAYER",
        "canonical_species_count": CANONICAL_SPECIES_COUNT,
        "internal_id_ceiling": LAST_CANONICAL_INTERNAL_ID,
        "sentinels": {
            "egg": EGG_INTERNAL_ID,
            "bad_egg": BAD_EGG_INTERNAL_ID,
        },
        "legacy_reserved_internal_ids": [
            LEGACY_RESERVED_FIRST,
            LEGACY_RESERVED_LAST,
        ],
        "proof_points": {
            "arceus": {
                "national_dex": 493,
                "internal_species_id": natdex_to_internal[493],
            },
            "victini": {
                "national_dex": 494,
                "internal_species_id": natdex_to_internal[494],
            },
            "genesect": {
                "national_dex": 649,
                "internal_species_id": natdex_to_internal[649],
            },
            "pecharunt": {
                "national_dex": 1025,
                "internal_species_id": natdex_to_internal[1025],
            },
        },
        "reserved_ids_map_to_natdex_zero": all(
            internal_to_natdex[i] == 0
            for i in range(EGG_INTERNAL_ID, FIRST_MODERN_INTERNAL_ID)
        ),
        "all_canonical_round_trips_pass": all(
            internal_to_natdex[natdex_to_internal[dex]] == dex
            for dex in range(1, CANONICAL_SPECIES_COUNT + 1)
        ),
        "generated_files": [
            header.name,
            source.name,
            mapping_path.name,
        ],
        "next_gate": "PT05B_DECOUPLE_POKEPLATINUM_DEX_AND_INTERNAL_SPECIES_INDEXING",
    }

    report_path.write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
