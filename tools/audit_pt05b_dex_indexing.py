#!/usr/bin/env python3
"""Audit pokeplatinum locations that couple National Dex and internal species IDs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


RULES = {
    "species_constants_coupled": {
        "path": "include/constants/species.h",
        "patterns": [
            r"#define\s+MAX_SPECIES\s+SPECIES_BAD_EGG",
            r"#define\s+NATIONAL_DEX_COUNT\s+\(MAX_SPECIES\s*-\s*2\)",
        ],
        "severity": "blocker",
        "fix": "define canonical Dex count separately from the internal species ceiling",
    },
    "pokedex_rejects_internal_ids": {
        "path": "src/pokedex.c",
        "patterns": [
            r"species\s*>\s*NATIONAL_DEX_COUNT",
        ],
        "severity": "blocker",
        "fix": "validate canonical identity through internal->NatDex translation",
    },
    "pokedex_bits_use_internal_id": {
        "path": "src/pokedex.c",
        "patterns": [
            r"ActivateBit_2Forms\([^\n]*species\)",
            r"ReadBit_2Forms\([^\n]*species\)",
        ],
        "severity": "blocker",
        "fix": "translate internal species ID to National Dex before bit access",
    },
    "pokedex_loops_treat_natdex_as_species": {
        "path": "src/pokedex.c",
        "patterns": [
            r"for \(species = 1; species <= NATIONAL_DEX_COUNT; species\+\+\)",
        ],
        "severity": "blocker",
        "fix": "iterate National Dex numbers and translate each to internal species ID",
    },
    "speciesproc_uses_egg_as_dex_ceiling": {
        "path": "tools/dataproc/src/speciesproc.c",
        "patterns": [
            r"#define\s+NATIONAL_DEX_MAX\s+SPECIES_EGG",
            r"if \(i >= SPECIES_EGG\) return \(SpeciesDexData\)",
            r"if \(i >= SPECIES_EGG\) return;",
        ],
        "severity": "blocker",
        "fix": "drive canonical Dex emission through identity mapping, not sentinel position",
    },
    "personal_data_bounds_use_natdex_count": {
        "path": "src/pokemon.c",
        "patterns": [
            r"GF_ASSERT\(NATIONAL_DEX_COUNT \+ 1 > species\)",
        ],
        "severity": "blocker",
        "fix": "bound personal-data lookup by internal species archive capacity",
    },
    "height_weight_arrays_index_internal_species": {
        "path": "src/pokedex_heightweight.c",
        "patterns": [
            r"HWData->height\[species\]",
            r"HWData->weight\[species\]",
            r"HWData->trainerPos\[species\]",
            r"HWData->pokemonPos\[species\]",
            r"HWData->trainerScale\[species\]",
            r"HWData->pokemonScale\[species\]",
        ],
        "severity": "blocker",
        "fix": "translate internal species IDs to canonical Dex indices for Dex-sized arrays",
    },
}


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_rule(root: Path, rule: dict) -> list[dict]:
    path = root / rule["path"]
    if not path.is_file():
        raise SystemExit(f"missing pinned pokeplatinum file: {path}")

    text = path.read_text()
    matches: list[dict] = []
    for pattern in rule["patterns"]:
        regex = re.compile(pattern)
        found = list(regex.finditer(text))
        for match in found:
            line = line_number(text, match.start())
            source_line = text.splitlines()[line - 1].strip()
            matches.append(
                {
                    "pattern": pattern,
                    "line": line,
                    "source": source_line,
                }
            )
    return matches


def scan_global_references(root: Path, token: str) -> list[dict]:
    results = []
    allowed_suffixes = {".c", ".h", ".cpp", ".py", ".build"}
    roots = ["src", "include", "tools", "res"]

    for dirname in roots:
        base = root / dirname
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in allowed_suffixes:
                continue
            try:
                lines = path.read_text().splitlines()
            except UnicodeDecodeError:
                continue
            for index, line in enumerate(lines, start=1):
                if token in line:
                    results.append(
                        {
                            "path": str(path.relative_to(root)),
                            "line": index,
                            "source": line.strip(),
                        }
                    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("build/pt05b/pt05b-dex-indexing-audit.json"),
    )
    args = parser.parse_args()
    root = args.pokeplatinum_root.resolve()

    findings = {}
    total_blocker_matches = 0
    for name, rule in RULES.items():
        matches = scan_rule(root, rule)
        if not matches:
            raise SystemExit(f"PT05B audit expected coupling not found: {name}")
        findings[name] = {
            "path": rule["path"],
            "severity": rule["severity"],
            "recommended_fix": rule["fix"],
            "matches": matches,
        }
        total_blocker_matches += len(matches)

    national_refs = scan_global_references(root, "NATIONAL_DEX_COUNT")
    egg_refs = scan_global_references(root, "SPECIES_EGG")
    max_species_refs = scan_global_references(root, "MAX_SPECIES")

    report = {
        "gate": "PT05B_DEX_INTERNAL_ID_COUPLING_AUDIT",
        "production_identity_contract": {
            "canonical_species_count": 1025,
            "egg_internal_id": 494,
            "bad_egg_internal_id": 495,
            "legacy_reserved_internal_ids": [496, 543],
            "victini": {"national_dex": 494, "internal_species_id": 544},
            "pecharunt": {"national_dex": 1025, "internal_species_id": 1075},
        },
        "confirmed_blocker_categories": len(findings),
        "confirmed_blocker_matches": total_blocker_matches,
        "findings": findings,
        "global_reference_counts": {
            "NATIONAL_DEX_COUNT": len(national_refs),
            "SPECIES_EGG": len(egg_refs),
            "MAX_SPECIES": len(max_species_refs),
        },
        "global_references": {
            "NATIONAL_DEX_COUNT": national_refs,
            "SPECIES_EGG": egg_refs,
            "MAX_SPECIES": max_species_refs,
        },
        "patch_order": [
            "generated species identity runtime tables",
            "species constants: separate canonical count and internal ceiling",
            "Pokedex validation/bit access/count loops",
            "Pokedex height-weight canonical indexing",
            "personal-data internal bounds",
            "species dataproc canonical-vs-internal archive emission",
            "remaining global references from audit report",
        ],
        "next_gate": "PT05B_IDENTITY_TRANSLATION_ENGINE_PATCH",
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "gate": report["gate"],
                "confirmed_blocker_categories": report["confirmed_blocker_categories"],
                "confirmed_blocker_matches": report["confirmed_blocker_matches"],
                "global_reference_counts": report["global_reference_counts"],
                "next_gate": report["next_gate"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
