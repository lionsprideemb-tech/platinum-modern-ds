#!/usr/bin/env python3
"""Build the Mercury DS National-Dex -> internal-species ID map.

Gen-IV DS resources reserve IDs after Arceus for Egg/Bad Egg and legacy
form/icon slots.  Canonical post-Gen-IV Pokemon therefore begin at internal
ID 544 while retaining their real National Dex numbers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VANILLA_NATDEX_MAX = 493
EGG_INTERNAL_ID = 494
BAD_EGG_INTERNAL_ID = 495
LEGACY_RESERVED_FIRST = 496
LEGACY_RESERVED_LAST = 543
MODERN_INTERNAL_OFFSET = 50
FIRST_MODERN_INTERNAL_ID = 544
CANONICAL_SPECIES_COUNT = 1025


def load_species(path: Path) -> list[str]:
    species = [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(species) != CANONICAL_SPECIES_COUNT:
        raise SystemExit(
            f"expected {CANONICAL_SPECIES_COUNT} canonical species, found {len(species)}"
        )
    return species


def internal_id_for_national_dex(national_dex: int) -> int:
    if not 1 <= national_dex <= CANONICAL_SPECIES_COUNT:
        raise ValueError(f"National Dex out of range: {national_dex}")
    if national_dex <= VANILLA_NATDEX_MAX:
        return national_dex
    return national_dex + MODERN_INTERNAL_OFFSET


def build_map(species: list[str]) -> dict:
    entries = []
    used_internal_ids: set[int] = {0, EGG_INTERNAL_ID, BAD_EGG_INTERNAL_ID}
    used_internal_ids.update(range(LEGACY_RESERVED_FIRST, LEGACY_RESERVED_LAST + 1))

    for national_dex, species_const in enumerate(species, start=1):
        internal_id = internal_id_for_national_dex(national_dex)
        if internal_id in used_internal_ids:
            raise SystemExit(
                f"internal-ID collision: NatDex {national_dex} {species_const} -> {internal_id}"
            )
        used_internal_ids.add(internal_id)
        entries.append(
            {
                "national_dex": national_dex,
                "internal_species_id": internal_id,
                "species": species_const,
            }
        )

    by_name = {entry["species"]: entry for entry in entries}
    checks = {
        "arceus": by_name["SPECIES_ARCEUS"],
        "victini": by_name["SPECIES_VICTINI"],
        "pecharunt": by_name["SPECIES_PECHARUNT"],
    }

    assert checks["arceus"]["national_dex"] == 493
    assert checks["arceus"]["internal_species_id"] == 493
    assert checks["victini"]["national_dex"] == 494
    assert checks["victini"]["internal_species_id"] == 544
    assert checks["pecharunt"]["national_dex"] == 1025
    assert checks["pecharunt"]["internal_species_id"] == 1075

    return {
        "schema": "mercury-ds-species-id-map-v1",
        "canonical_species_count": CANONICAL_SPECIES_COUNT,
        "vanilla_canonical_range": {"national_dex": [1, 493], "internal_ids": [1, 493]},
        "sentinels": {
            "SPECIES_NONE": 0,
            "SPECIES_EGG": EGG_INTERNAL_ID,
            "SPECIES_BAD_EGG": BAD_EGG_INTERNAL_ID,
        },
        "legacy_reserved_internal_ids": [LEGACY_RESERVED_FIRST, LEGACY_RESERVED_LAST],
        "modern_rule": {
            "national_dex_range": [494, 1025],
            "formula": "internal_species_id = national_dex + 50",
            "internal_id_range": [FIRST_MODERN_INTERNAL_ID, 1075],
        },
        "proof_points": checks,
        "species": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--species",
        type=Path,
        default=Path("data/canonical_species_1025.txt"),
        help="canonical National Dex registry",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/ds_species_id_map.json"),
        help="generated JSON mapping",
    )
    args = parser.parse_args()

    result = build_map(load_species(args.species))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")

    print(
        "Mercury DS species-ID map: "
        f"{result['canonical_species_count']} canonical species; "
        "Victini NatDex 494 -> internal 544; "
        "Pecharunt NatDex 1025 -> internal 1075"
    )


if __name__ == "__main__":
    main()
