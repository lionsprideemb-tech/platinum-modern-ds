#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

GEN5_START = 494
GEN5_END = 649
GEN5_COUNT = GEN5_END - GEN5_START + 1

SUPPORT_TABLES = {
    "height": "data/HeightTable.c",
    "hidden_ability": "data/HiddenAbilityTable.c",
    "icon_palette": "data/IconPaletteTable.c",
    "base_experience": "data/BaseExperienceTable.c",
    "baby_species": "data/BabyMons.c",
    "pokedex_sort": "data/PokedexSort.c",
    "female_overworld_form": "data/SpeciesToOWFormFemale.c",
    "follower_properties": "data/FollowerProperties.c",
}

LARGE_DONOR_FILES = {
    "species_data": "data/Species.c",
    "learnsets": "data/learnsets/learnsets.json",
    "sprite_offsets": "data/SpriteOffsets.c",
}


def load_registry(path: Path) -> list[str]:
    entries = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith("SPECIES_"):
            raise SystemExit(f"invalid canonical species entry: {line!r}")
        entries.append(line)
    return entries


def nonempty(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def choose_battle_sprite_dir(root: Path, dirname: str) -> tuple[str | None, dict]:
    species_dir = root / "data/graphics/sprites" / dirname
    candidates = {}
    for sex in ("male", "female"):
        front = species_dir / sex / "front.png"
        back = species_dir / sex / "back.png"
        front_key = species_dir / sex / "front.png.key"
        back_key = species_dir / sex / "back.png.key"
        candidates[sex] = {
            "front": nonempty(front),
            "back": nonempty(back),
            "front_key": nonempty(front_key),
            "back_key": nonempty(back_key),
        }

    for sex in ("male", "female"):
        values = candidates[sex]
        if all(values.values()):
            return sex, candidates
    return None, candidates


def table_token_coverage(root: Path, species: list[str]) -> dict:
    result = {}
    for label, rel in SUPPORT_TABLES.items():
        path = root / rel
        if not nonempty(path):
            result[label] = {
                "path": rel,
                "file_present": False,
                "covered": 0,
                "missing": species,
            }
            continue

        text = path.read_text(errors="replace")
        missing = [token for token in species if token not in text]
        result[label] = {
            "path": rel,
            "file_present": True,
            "covered": len(species) - len(missing),
            "missing": missing,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit pinned HG-Engine donor coverage for the Mercury DS Gen V bulk import."
    )
    parser.add_argument("hg_engine_root", type=Path)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/canonical_species_1025.txt"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("pt05a-gen5-donor-coverage.json"),
    )
    args = parser.parse_args()

    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)
    if len(registry) != 1025:
        raise SystemExit(f"expected 1025 canonical species, found {len(registry)}")

    species = registry[GEN5_START - 1:GEN5_END]
    if len(species) != GEN5_COUNT:
        raise SystemExit(f"expected {GEN5_COUNT} Gen V species, found {len(species)}")
    if species[0] != "SPECIES_VICTINI" or species[-1] != "SPECIES_GENESECT":
        raise SystemExit(
            f"unexpected Gen V boundaries: first={species[0]} last={species[-1]}"
        )

    graphics = []
    missing_graphics = []
    female_fallbacks = []

    for dex, token in enumerate(species, start=GEN5_START):
        dirname = token.removeprefix("SPECIES_").lower()
        species_dir = hg / "data/graphics/sprites" / dirname
        chosen_sex, candidates = choose_battle_sprite_dir(hg, dirname)
        icon = nonempty(species_dir / "icon.png")
        overworld = nonempty(species_dir / "overworld.png")
        overworld_meta = nonempty(species_dir / "overworld.json")
        complete = chosen_sex is not None and icon

        row = {
            "national_dex": dex,
            "species": token,
            "donor_dir": dirname,
            "battle_sprite_source": chosen_sex,
            "icon": icon,
            "overworld": overworld,
            "overworld_metadata": overworld_meta,
            "complete_battle_graphics": complete,
        }
        graphics.append(row)

        if not complete:
            missing_graphics.append({
                **row,
                "candidates": candidates,
            })
        elif chosen_sex == "female":
            female_fallbacks.append({
                "national_dex": dex,
                "species": token,
                "reason": "male battle sprite files are empty/missing; female donor is complete",
            })

    table_coverage = table_token_coverage(hg, species)
    incomplete_tables = {
        label: data
        for label, data in table_coverage.items()
        if not data["file_present"] or data["missing"]
    }

    large_files = {}
    for label, rel in LARGE_DONOR_FILES.items():
        path = hg / rel
        large_files[label] = {
            "path": rel,
            "present": nonempty(path),
            "bytes": path.stat().st_size if path.is_file() else 0,
        }

    report = {
        "gate": "PT05A_GEN5_DONOR_COVERAGE",
        "national_dex_range": [GEN5_START, GEN5_END],
        "expected_species": GEN5_COUNT,
        "first_species": species[0],
        "last_species": species[-1],
        "battle_graphics": {
            "complete": len(graphics) - len(missing_graphics),
            "missing": len(missing_graphics),
            "female_fallback_count": len(female_fallbacks),
            "female_fallbacks": female_fallbacks,
            "missing_entries": missing_graphics,
        },
        "support_tables": table_coverage,
        "large_donor_files": large_files,
        "all_battle_graphics_present": not missing_graphics,
        "all_support_table_tokens_present": not incomplete_tables,
        "all_large_donor_files_present": all(x["present"] for x in large_files.values()),
        "next_gate": "PT05B_GEN5_COMPATIBILITY_MAPPING_AND_BULK_IMPORTER",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if missing_graphics:
        raise SystemExit(
            f"Gen V donor graphics incomplete for {len(missing_graphics)} species"
        )
    if incomplete_tables:
        raise SystemExit(
            "Gen V donor support-table coverage incomplete: "
            + ", ".join(sorted(incomplete_tables))
        )
    if not report["all_large_donor_files_present"]:
        raise SystemExit("one or more large Gen V donor data sources are missing")


if __name__ == "__main__":
    main()
