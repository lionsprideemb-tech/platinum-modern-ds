#!/usr/bin/env python3
"""Audit canonical National Dex coverage in a local HG-Engine checkout.

This tool is read-only. It does not edit HG-Engine.

It treats data/PokedexSort.c's National Dex array as the canonical #001-1025
ordering and checks whether each species is represented across the major data
surfaces we care about before doing any Platinum-world integration.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


REQUIRED_SURFACES = (
    "species_data",
    "base_experience",
    "hidden_ability_entry",
    "icon_palette",
    "learnset",
    "battle_graphics",
    "follower_properties",
)

INFORMATIONAL_SURFACES = (
    "evolution_entry",
)


def read_text(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        raise FileNotFoundError(f"Required HG-Engine file missing: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def extract_national_dex(pokedex_sort: str) -> list[str]:
    match = re.search(
        r"static\s+const\s+u16\s+sPokedexSort_NationalNum\[\]\s*=\s*\{(.*?)\};",
        pokedex_sort,
        flags=re.S,
    )
    if not match:
        raise RuntimeError("Could not locate sPokedexSort_NationalNum in data/PokedexSort.c")
    return re.findall(r"\bSPECIES_[A-Z0-9_]+\b", match.group(1))


def extract_numeric_species_ids(species_h: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for name, value in re.findall(
        r"^#define\s+(SPECIES_[A-Z0-9_]+)\s+(\d+)\s*(?:/\*.*?\*/)?\s*$",
        species_h,
        flags=re.M,
    ):
        result[name] = int(value)
    return result


def has_indexed_entry(text: str, species: str) -> bool:
    return re.search(r"\[\s*" + re.escape(species) + r"\s*\]", text) is not None


def has_json_key(text: str, species: str) -> bool:
    return f'"{species}"' in text


def has_token(text: str, species: str) -> bool:
    return re.search(r"\b" + re.escape(species) + r"\b", text) is not None


def audit(root: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    species_h = read_text(root, "include/constants/species.h")
    pokedex_sort = read_text(root, "data/PokedexSort.c")

    national = extract_national_dex(pokedex_sort)
    engine_ids = extract_numeric_species_ids(species_h)

    if len(national) != 1025:
        raise RuntimeError(
            f"Expected 1025 National Dex entries, found {len(national)}. "
            "Audit assumptions need review before continuing."
        )
    if national[0] != "SPECIES_BULBASAUR" or national[-1] != "SPECIES_PECHARUNT":
        raise RuntimeError(
            "National Dex boundary mismatch: expected Bulbasaur first and Pecharunt last."
        )

    surfaces = {
        "species_data": read_text(root, "data/Species.c"),
        "base_experience": read_text(root, "data/BaseExperienceTable.c"),
        "hidden_ability_entry": read_text(root, "data/HiddenAbilityTable.c"),
        "icon_palette": read_text(root, "data/IconPaletteTable.c"),
        "learnset": read_text(root, "data/learnsets/learnsets.json"),
        "battle_graphics": read_text(root, "data/graphics/pokegra.mk"),
        "follower_properties": read_text(root, "data/FollowerProperties.c"),
        "evolution_entry": read_text(root, "data/Evolutions.c"),
    }

    rows: list[dict[str, object]] = []
    missing_counts = {name: 0 for name in REQUIRED_SURFACES}
    complete_count = 0

    for dex_number, species in enumerate(national, start=1):
        checks = {
            "species_data": has_indexed_entry(surfaces["species_data"], species),
            "base_experience": has_indexed_entry(surfaces["base_experience"], species),
            "hidden_ability_entry": has_indexed_entry(
                surfaces["hidden_ability_entry"], species
            ),
            "icon_palette": has_indexed_entry(surfaces["icon_palette"], species),
            "learnset": has_json_key(surfaces["learnset"], species),
            "battle_graphics": has_token(surfaces["battle_graphics"], species),
            "follower_properties": has_indexed_entry(
                surfaces["follower_properties"], species
            ),
            "evolution_entry": has_indexed_entry(surfaces["evolution_entry"], species),
        }

        for key in REQUIRED_SURFACES:
            if not checks[key]:
                missing_counts[key] += 1

        minimum_complete = all(checks[key] for key in REQUIRED_SURFACES)
        if minimum_complete:
            complete_count += 1

        rows.append(
            {
                "national_dex": dex_number,
                "species": species,
                "engine_species_id": engine_ids.get(species, ""),
                **checks,
                "minimum_complete": minimum_complete,
                "needs_review": not minimum_complete,
            }
        )

    summary = {
        "canonical_species_count": len(national),
        "first_species": national[0],
        "last_species": national[-1],
        "minimum_complete_count": complete_count,
        "needs_review_count": len(national) - complete_count,
        "missing_by_surface": missing_counts,
        "required_surfaces": list(REQUIRED_SURFACES),
        "informational_surfaces": list(INFORMATIONAL_SURFACES),
        "notes": [
            "evolution_entry is informational because many valid species have no evolution record.",
            "minimum_complete is a coverage signal, not proof that every special battle/form mechanic is implemented.",
            "special mechanics require a separate DS02 behavior audit.",
        ],
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hg-engine",
        type=Path,
        default=Path("vendor/hg-engine"),
        help="Path to a local HG-Engine checkout.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("audits/pokedex_1025.csv"),
        help="CSV output path.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("audits/pokedex_1025_summary.json"),
        help="JSON summary output path.",
    )
    args = parser.parse_args()

    rows, summary = audit(args.hg_engine.resolve())

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "national_dex",
        "species",
        "engine_species_id",
        *REQUIRED_SURFACES,
        *INFORMATIONAL_SURFACES,
        "minimum_complete",
        "needs_review",
    ]
    with args.csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
