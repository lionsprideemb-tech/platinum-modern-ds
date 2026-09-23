#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

GEN5_START = 494
GEN5_END = 649

EXP_RATE_MAP = {
    "GROWTH_MEDIUM_FAST": "EXP_RATE_MEDIUM_FAST",
    "GROWTH_ERRATIC": "EXP_RATE_ERRATIC",
    "GROWTH_FLUCTUATING": "EXP_RATE_FLUCTUATING",
    "GROWTH_MEDIUM_SLOW": "EXP_RATE_MEDIUM_SLOW",
    "GROWTH_FAST": "EXP_RATE_FAST",
    "GROWTH_SLOW": "EXP_RATE_SLOW",
}


def load_lines(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text(errors="replace").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def load_registry(path: Path) -> list[str]:
    entries = [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(entries) != 1025:
        raise SystemExit(f"expected 1025 canonical species, found {len(entries)}")
    return entries


def extract_c_block(text: str, token: str) -> str:
    marker = f"[{token}] = {{"
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"missing {token}")
    brace = text.find("{", start)
    depth = 0
    for pos in range(brace, len(text)):
        ch = text[pos]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:pos + 1]
    raise ValueError(f"unterminated block for {token}")


def capture_pair(block: str, field: str, prefix: str) -> list[str]:
    m = re.search(
        rf"\.{re.escape(field)}\s*=\s*\{{\s*({prefix}[A-Z0-9_]+)\s*,\s*({prefix}[A-Z0-9_]+)",
        block,
    )
    return list(m.groups()) if m else []


def capture_single(block: str, field: str, prefix: str) -> str | None:
    m = re.search(
        rf"\.{re.escape(field)}\s*=\s*({prefix}[A-Z0-9_]+)",
        block,
    )
    return m.group(1) if m else None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit Gen V donor identifiers against the pinned Platinum engine."
    )
    parser.add_argument("hg_engine_root", type=Path)
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/canonical_species_1025.txt"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("pt05b-gen5-compatibility.json"),
    )
    args = parser.parse_args()

    hg = args.hg_engine_root.resolve()
    pt = args.pokeplatinum_root.resolve()
    registry = load_registry(args.registry)
    species = registry[GEN5_START - 1:GEN5_END]
    if species[0] != "SPECIES_VICTINI" or species[-1] != "SPECIES_GENESECT":
        raise SystemExit("canonical Gen V boundaries are not Victini..Genesect")

    species_text = (hg / "data/Species.c").read_text(errors="replace")
    hidden_text = (hg / "data/HiddenAbilityTable.c").read_text(errors="replace")
    base_exp_text = (hg / "data/BaseExperienceTable.c").read_text(errors="replace")
    learnsets = json.loads((hg / "data/learnsets/learnsets.json").read_text())

    pt_abilities = load_lines(pt / "generated/abilities.txt")
    pt_moves = load_lines(pt / "generated/moves.txt")
    pt_types = load_lines(pt / "generated/pokemon_types.txt")
    pt_items = load_lines(pt / "generated/items.txt")
    pt_egg_groups = load_lines(pt / "generated/egg_groups.txt")
    pt_exp_rates = load_lines(pt / "generated/exp_rates.txt")

    primary_abilities: set[str] = set()
    hidden_abilities: set[str] = set()
    types: set[str] = set()
    items: set[str] = set()
    egg_groups: set[str] = set()
    growth_rates: set[str] = set()
    moves: set[str] = set()

    parse_failures = []
    learnset_missing = []
    base_exp_overflow = []
    species_summary = []

    for dex, token in enumerate(species, start=GEN5_START):
        try:
            block = extract_c_block(species_text, token)
        except ValueError as exc:
            parse_failures.append({"species": token, "error": str(exc)})
            continue

        ability_pair = capture_pair(block, "abilities", "ABILITY_")
        type_pair = capture_pair(block, "types", "TYPE_")
        egg_pair = capture_pair(block, "eggGroups", "EGG_GROUP_")
        common_item = capture_single(block, "common", "ITEM_")
        rare_item = capture_single(block, "rare", "ITEM_")
        growth = capture_single(block, "expRate", "GROWTH_")

        if len(ability_pair) != 2:
            parse_failures.append({"species": token, "error": "abilities pair not parsed"})
        if len(type_pair) != 2:
            parse_failures.append({"species": token, "error": "types pair not parsed"})
        if len(egg_pair) != 2:
            parse_failures.append({"species": token, "error": "eggGroups pair not parsed"})
        if growth is None:
            parse_failures.append({"species": token, "error": "expRate not parsed"})

        primary_abilities.update(ability_pair)
        types.update(type_pair)
        egg_groups.update(egg_pair)
        if common_item:
            items.add(common_item)
        if rare_item:
            items.add(rare_item)
        if growth:
            growth_rates.add(growth)

        hidden_match = re.search(
            rf"\[{re.escape(token)}\s*\]\s*=\s*(ABILITY_[A-Z0-9_]+)",
            hidden_text,
        )
        if hidden_match:
            hidden_abilities.add(hidden_match.group(1))
        else:
            parse_failures.append({"species": token, "error": "hidden ability not parsed"})

        exp_match = re.search(
            rf"\[{re.escape(token)}\s*\]\s*=\s*(\d+)",
            base_exp_text,
        )
        exp_value = int(exp_match.group(1)) if exp_match else None
        if exp_value is None:
            parse_failures.append({"species": token, "error": "base experience not parsed"})
        elif exp_value > 255:
            base_exp_overflow.append({
                "national_dex": dex,
                "species": token,
                "base_experience": exp_value,
            })

        learn = learnsets.get(token)
        if learn is None:
            learnset_missing.append(token)
            species_moves = set()
        else:
            species_moves = set()

            def walk(value):
                if isinstance(value, dict):
                    for v in value.values():
                        walk(v)
                elif isinstance(value, list):
                    for v in value:
                        walk(v)
                elif isinstance(value, str) and value.startswith("MOVE_"):
                    species_moves.add(value)

            walk(learn)
            moves.update(species_moves)

        species_summary.append({
            "national_dex": dex,
            "species": token,
            "primary_abilities": ability_pair,
            "hidden_ability": hidden_match.group(1) if hidden_match else None,
            "types": type_pair,
            "held_items": [common_item, rare_item],
            "growth_rate": growth,
            "base_experience": exp_value,
            "referenced_move_count": len(species_moves),
        })

    mapped_exp_rates = {EXP_RATE_MAP.get(x) for x in growth_rates}
    unmapped_growth_rates = sorted(x for x in growth_rates if x not in EXP_RATE_MAP)
    unsupported_mapped_exp_rates = sorted(
        x for x in mapped_exp_rates if x is not None and x not in pt_exp_rates
    )

    all_abilities = primary_abilities | hidden_abilities

    report = {
        "gate": "PT05B_GEN5_COMPATIBILITY_AUDIT",
        "national_dex_range": [GEN5_START, GEN5_END],
        "species_count": len(species),
        "parse_failures": parse_failures,
        "learnset_missing": learnset_missing,
        "identifier_counts": {
            "abilities_total": len(all_abilities),
            "primary_abilities": len(primary_abilities),
            "hidden_abilities": len(hidden_abilities),
            "moves": len(moves),
            "types": len(types),
            "held_items": len(items),
            "egg_groups": len(egg_groups),
            "growth_rates": len(growth_rates),
        },
        "unsupported_in_platinum": {
            "abilities": sorted(all_abilities - pt_abilities),
            "moves": sorted(moves - pt_moves),
            "types": sorted(types - pt_types),
            "held_items": sorted(items - pt_items),
            "egg_groups": sorted(egg_groups - pt_egg_groups),
            "growth_rates_unmapped": unmapped_growth_rates,
            "mapped_exp_rates_missing_in_platinum": unsupported_mapped_exp_rates,
        },
        "platinum_byte_width_constraints": {
            "base_experience_over_255_count": len(base_exp_overflow),
            "base_experience_over_255": base_exp_overflow,
        },
        "species": species_summary,
        "ready_for_mapping_plan": not parse_failures and not learnset_missing,
        "next_gate": "PT05B_COMPATIBILITY_MAP_IMPLEMENTATION",
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")

    concise = dict(report)
    concise["species"] = f"{len(species_summary)} parsed rows"
    print(json.dumps(concise, indent=2))

    if parse_failures or learnset_missing:
        raise SystemExit(
            f"Gen V donor parse incomplete: {len(parse_failures)} parse failures, "
            f"{len(learnset_missing)} missing learnsets"
        )


if __name__ == "__main__":
    main()
