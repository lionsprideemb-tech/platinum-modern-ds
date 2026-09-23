#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

TARGET_NATIONAL_DEX_COUNT = 1025
VANILLA_NATIONAL_DEX_COUNT = 493

GENERATION_ENDS = {
    1: (151, "SPECIES_MEW"),
    2: (251, "SPECIES_CELEBI"),
    3: (386, "SPECIES_DEOXYS"),
    4: (493, "SPECIES_ARCEUS"),
    5: (649, "SPECIES_GENESECT"),
    6: (721, "SPECIES_VOLCANION"),
    7: (809, "SPECIES_MELMETAL"),
    8: (905, "SPECIES_ENAMORUS"),
    9: (1025, "SPECIES_PECHARUNT"),
}


def load_registry(path: Path) -> list[str]:
    entries = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith("SPECIES_"):
            raise SystemExit(f"invalid species registry entry: {line!r}")
        entries.append(line)
    return entries


def load_vanilla_species(path: Path) -> list[str]:
    entries = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    expected_tail = ["SPECIES_EGG", "SPECIES_BAD_EGG"]
    if entries[-2:] != expected_tail:
        raise SystemExit(f"unexpected upstream species sentinels: {entries[-2:]!r}")
    if entries[0] != "SPECIES_NONE":
        raise SystemExit(f"unexpected upstream zero species: {entries[0]!r}")
    return entries[1:-2]


def validate_registry(registry: list[str], vanilla: list[str]) -> dict:
    if len(registry) != TARGET_NATIONAL_DEX_COUNT:
        raise SystemExit(
            f"canonical registry must contain {TARGET_NATIONAL_DEX_COUNT} base species; "
            f"found {len(registry)}"
        )

    if len(set(registry)) != len(registry):
        seen = set()
        dupes = []
        for species in registry:
            if species in seen:
                dupes.append(species)
            seen.add(species)
        raise SystemExit(f"duplicate canonical species entries: {sorted(set(dupes))}")

    if len(vanilla) != VANILLA_NATIONAL_DEX_COUNT:
        raise SystemExit(
            f"expected pinned Platinum to expose {VANILLA_NATIONAL_DEX_COUNT} base species; "
            f"found {len(vanilla)}"
        )

    if registry[:VANILLA_NATIONAL_DEX_COUNT] != vanilla:
        for i, (expected, actual) in enumerate(
            zip(vanilla, registry[:VANILLA_NATIONAL_DEX_COUNT]), start=1
        ):
            if expected != actual:
                raise SystemExit(
                    f"canonical registry diverges from Platinum at National Dex #{i}: "
                    f"upstream={expected}, registry={actual}"
                )
        raise SystemExit("canonical registry differs from Platinum in the Gen I-IV prefix")

    boundary_report = {}
    for generation, (dex_num, expected_species) in GENERATION_ENDS.items():
        actual = registry[dex_num - 1]
        if actual != expected_species:
            raise SystemExit(
                f"generation {generation} boundary mismatch at #{dex_num}: "
                f"expected {expected_species}, got {actual}"
            )
        boundary_report[str(generation)] = {
            "national_dex_end": dex_num,
            "species": actual,
        }

    return boundary_report


def emit_species_txt(registry: list[str], through: int, output: Path) -> None:
    if through < 1 or through > TARGET_NATIONAL_DEX_COUNT:
        raise SystemExit(
            f"--through must be between 1 and {TARGET_NATIONAL_DEX_COUNT}, got {through}"
        )

    lines = ["SPECIES_NONE", *registry[:through], "SPECIES_EGG", "SPECIES_BAD_EGG"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and emit Mercury DS canonical base-species registries."
    )
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/canonical_species_1025.txt"),
    )
    parser.add_argument(
        "--through",
        type=int,
        default=TARGET_NATIONAL_DEX_COUNT,
        help="emit base species through this National Dex number",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("pt04-generated-species.txt"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("pt04-registry-report.json"),
    )
    args = parser.parse_args()

    registry = load_registry(args.registry)
    vanilla = load_vanilla_species(
        args.pokeplatinum_root / "generated/species.txt"
    )
    boundaries = validate_registry(registry, vanilla)
    emit_species_txt(registry, args.through, args.output)

    report = {
        "gate": "PT04B_CANONICAL_SPECIES_REGISTRY",
        "canonical_base_species_count": len(registry),
        "requested_through": args.through,
        "candidate_registry_line_count": args.through + 3,
        "first_species": registry[0],
        "vanilla_last_species": registry[VANILLA_NATIONAL_DEX_COUNT - 1],
        "first_post_gen4_species": registry[VANILLA_NATIONAL_DEX_COUNT],
        "last_species": registry[-1],
        "sentinels": ["SPECIES_NONE", "SPECIES_EGG", "SPECIES_BAD_EGG"],
        "vanilla_prefix_exact_match": True,
        "generation_boundaries": boundaries,
        "next_gate": "PT04C_FIRST_POST_GEN4_RUNTIME_BATCH",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
