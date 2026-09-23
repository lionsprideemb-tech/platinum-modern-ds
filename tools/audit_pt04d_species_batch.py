#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

GEN5_START = 494
GEN5_END = 649


def load_registry(path: Path) -> list[str]:
    entries = [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(entries) != 1025:
        raise SystemExit(f"expected 1025 canonical species, found {len(entries)}")
    return entries


def extract_braced_block(text: str, marker: str) -> str:
    start = text.find(marker)
    if start < 0:
        raise KeyError(marker)
    brace = text.find("{", start)
    if brace < 0:
        raise ValueError(f"opening brace missing for {marker}")
    depth = 0
    in_string = False
    escaped = False
    for i in range(brace, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError(f"unterminated block for {marker}")


def subblock(block: str, field: str) -> str:
    return extract_braced_block(block, f".{field} = ")


def scalar(block: str, field: str) -> str:
    match = re.search(rf"\.{re.escape(field)}\s*=\s*([^,\n]+)", block)
    if not match:
        raise ValueError(f"missing scalar .{field}")
    return match.group(1).strip()


def pair(block: str, field: str) -> list[str]:
    match = re.search(
        rf"\.{re.escape(field)}\s*=\s*\{{\s*([^,}}]+)\s*,\s*([^}}]+)\}}",
        block,
    )
    if not match:
        raise ValueError(f"missing pair .{field}")
    return [match.group(1).strip(), match.group(2).strip()]


def parse_base_exp(path: Path) -> dict[str, int]:
    text = path.read_text()
    return {
        species: int(value)
        for species, value in re.findall(
            r"\[\s*(SPECIES_[A-Z0-9_]+)\s*\]\s*=\s*(\d+)\s*,",
            text,
        )
    }


def load_generated_constants(path: Path) -> set[str]:
    if not path.is_file():
        raise SystemExit(f"missing Platinum generated constants file: {path}")
    values = set()
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        values.add(line.split("=", 1)[0].strip())
    return values


def translated_growth(name: str) -> str:
    if name.startswith("GROWTH_"):
        return "EXP_RATE_" + name.removeprefix("GROWTH_")
    return name


def translated_body_color(name: str) -> str:
    if name.startswith("BODY_COLOR_"):
        return "MON_COLOR_" + name.removeprefix("BODY_COLOR_")
    return name


def donor_dirname(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


def find_gender_sprite(root: Path, gender: str, stem: str) -> Path | None:
    path = root / gender / f"{stem}.png"
    return path if path.is_file() and path.stat().st_size else None


def parse_species_entry(species_text: str, species_const: str, base_exp: dict[str, int]) -> dict:
    block = extract_braced_block(species_text, f"[{species_const}] = ")
    data = subblock(block, "speciesData")
    stats = subblock(data, "baseStats")
    evs = subblock(data, "evYields")
    items = subblock(data, "wildHeldItems")
    metrics = subblock(block, "metricsData")
    text_data = subblock(block, "textData")

    return {
        "species": species_const,
        "base_stats": {
            "hp": int(scalar(stats, "hp")),
            "attack": int(scalar(stats, "attack")),
            "defense": int(scalar(stats, "defense")),
            "speed": int(scalar(stats, "speed")),
            "special_attack": int(scalar(stats, "spAttack")),
            "special_defense": int(scalar(stats, "spDefense")),
        },
        "types": pair(data, "types"),
        "catch_rate": int(scalar(data, "catchRate")),
        "base_exp_padding": int(scalar(data, "baseExpRewardPadding")),
        "base_exp_modern": base_exp.get(species_const),
        "ev_yields": {
            "hp": int(scalar(evs, "hp")),
            "attack": int(scalar(evs, "attack")),
            "defense": int(scalar(evs, "defense")),
            "speed": int(scalar(evs, "speed")),
            "special_attack": int(scalar(evs, "spAttack")),
            "special_defense": int(scalar(evs, "spDefense")),
        },
        "held_items": {
            "common": scalar(items, "common"),
            "rare": scalar(items, "rare"),
        },
        "gender_ratio_raw": int(scalar(data, "genderRatio")),
        "hatch_cycles": int(scalar(data, "hatchCycles")),
        "base_friendship": int(scalar(data, "baseFriendship")),
        "exp_rate": scalar(data, "expRate"),
        "egg_groups": pair(data, "eggGroups"),
        "abilities": pair(data, "abilities"),
        "safari_flee_rate": int(scalar(data, "safariFleeRate")),
        "body_color": scalar(data, "bodyColor"),
        "flip_sprite": int(scalar(data, "flipSprite")),
        "metrics": {
            "height_dm": int(scalar(metrics, "heightDecimetres")),
            "weight_hg": int(scalar(metrics, "weightHectograms")),
            "body_type": scalar(metrics, "bodyType"),
            "trainer_scale_f": int(scalar(metrics, "femaleTrainerScale")),
            "pokemon_scale_f": int(scalar(metrics, "femalePokemonScale")),
            "trainer_scale_m": int(scalar(metrics, "maleTrainerScale")),
            "pokemon_scale_m": int(scalar(metrics, "malePokemonScale")),
            "trainer_pos_f": int(scalar(metrics, "femaleTrainerYOffset")),
            "pokemon_pos_f": int(scalar(metrics, "femalePokemonYOffset")),
            "trainer_pos_m": int(scalar(metrics, "maleTrainerYOffset")),
            "pokemon_pos_m": int(scalar(metrics, "malePokemonYOffset")),
        },
        "text": {
            "name": scalar(text_data, "name").strip('"'),
            "category": scalar(text_data, "classification").strip('"'),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("hg_engine_root", type=Path)
    parser.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    parser.add_argument("--start-dex", type=int, default=GEN5_START)
    parser.add_argument("--end-dex", type=int, default=GEN5_END)
    parser.add_argument("--report", type=Path, default=Path("pt04d-gen5-donor-audit.json"))
    parser.add_argument(
        "--gate",
        default="PT04D_GEN5_DONOR_AUDIT",
        help="report gate name for the current canonical batch",
    )
    args = parser.parse_args()

    if not (494 <= args.start_dex <= args.end_dex <= 1025):
        raise SystemExit("PT04D batch must stay within canonical post-Gen-IV range 494..1025")

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)
    target = registry[args.start_dex - 1:args.end_dex]

    species_c = hg / "data/Species.c"
    base_exp_c = hg / "data/BaseExperienceTable.c"
    if not species_c.is_file():
        raise SystemExit(f"missing pinned HG donor species table: {species_c}")
    if not base_exp_c.is_file():
        raise SystemExit(f"missing pinned HG donor base EXP table: {base_exp_c}")

    species_text = species_c.read_text()
    base_exp = parse_base_exp(base_exp_c)

    platinum_constants = {
        "types": load_generated_constants(pt / "generated/pokemon_types.txt"),
        "abilities": load_generated_constants(pt / "generated/abilities.txt"),
        "held_items": load_generated_constants(pt / "generated/items.txt"),
        "growth_rates": load_generated_constants(pt / "generated/exp_rates.txt"),
        "egg_groups": load_generated_constants(pt / "generated/egg_groups.txt"),
        "body_colors": load_generated_constants(pt / "generated/pokemon_colors.txt"),
    }

    parsed = []
    missing_entries = []
    missing_assets = []
    donor_abilities = set()
    donor_items = set()
    donor_growth = set()
    donor_egg_groups = set()
    donor_types = set()
    exp_overflow = []

    for dex, species_const in enumerate(target, start=args.start_dex):
        try:
            entry = parse_species_entry(species_text, species_const, base_exp)
        except (KeyError, ValueError) as exc:
            missing_entries.append({"national_dex": dex, "species": species_const, "error": str(exc)})
            continue

        sprite_root = hg / "data/graphics/sprites" / donor_dirname(species_const)
        male_front = find_gender_sprite(sprite_root, "male", "front")
        female_front = find_gender_sprite(sprite_root, "female", "front")
        male_back = find_gender_sprite(sprite_root, "male", "back")
        female_back = find_gender_sprite(sprite_root, "female", "back")
        icon = sprite_root / "icon.png"

        asset_state = {
            "front": bool(male_front or female_front),
            "back": bool(male_back or female_back),
            "icon": icon.is_file() and icon.stat().st_size > 0,
        }
        if not all(asset_state.values()):
            missing_assets.append({
                "national_dex": dex,
                "species": species_const,
                "directory": str(sprite_root),
                "assets": asset_state,
            })

        donor_abilities.update(entry["abilities"])
        donor_items.update(entry["held_items"].values())
        donor_growth.add(entry["exp_rate"])
        donor_egg_groups.update(entry["egg_groups"])
        donor_types.update(entry["types"])
        if entry["base_exp_modern"] is not None and entry["base_exp_modern"] > 255:
            exp_overflow.append({
                "national_dex": dex,
                "species": species_const,
                "modern_base_exp": entry["base_exp_modern"],
            })

        parsed.append({
            "national_dex": dex,
            **entry,
            "donor_assets": asset_state,
        })

    compatibility = {
        "unsupported_types": sorted(donor_types - platinum_constants["types"]),
        "unsupported_abilities": sorted(donor_abilities - platinum_constants["abilities"]),
        "unsupported_held_items": sorted(donor_items - platinum_constants["held_items"]),
        "unsupported_growth_rates_after_translation": sorted(
            {
                translated_growth(value)
                for value in donor_growth
                if translated_growth(value) not in platinum_constants["growth_rates"]
            }
        ),
        "unsupported_egg_groups": sorted(donor_egg_groups - platinum_constants["egg_groups"]),
        "translation_rules": {
            "growth_rate": "GROWTH_X -> EXP_RATE_X",
            "body_color": "BODY_COLOR_X -> MON_COLOR_X",
            "species_ids": "map by canonical species constant/National Dex, never HG numeric ID",
        },
    }

    report = {
        "gate": args.gate,
        "range": [args.start_dex, args.end_dex],
        "expected_species": len(target),
        "parsed_species": len(parsed),
        "missing_entries": missing_entries,
        "missing_required_assets": missing_assets,
        "distinct_constants": {
            "types": sorted(donor_types),
            "abilities": sorted(donor_abilities),
            "held_items": sorted(donor_items),
            "growth_rates": sorted(donor_growth),
            "egg_groups": sorted(donor_egg_groups),
        },
        "base_exp_over_255": exp_overflow,
        "compatibility": compatibility,
        "proof_points": {
            "first": parsed[0] if parsed else None,
            "last": parsed[-1] if parsed else None,
        },
        "status": "PASS" if len(parsed) == len(target) and not missing_entries and not missing_assets else "FAIL",
        "next_if_passed": "translate donor constants and generate Platinum-compatible resource directories for this canonical batch",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps({
        "gate": report["gate"],
        "range": report["range"],
        "expected_species": report["expected_species"],
        "parsed_species": report["parsed_species"],
        "missing_entries": len(missing_entries),
        "missing_required_assets": len(missing_assets),
        "base_exp_over_255": len(exp_overflow),
        "unsupported_types": len(compatibility["unsupported_types"]),
        "unsupported_abilities": len(compatibility["unsupported_abilities"]),
        "unsupported_held_items": len(compatibility["unsupported_held_items"]),
        "status": report["status"],
    }, indent=2))

    if report["status"] != "PASS":
        raise SystemExit("PT04D donor audit failed; see report")


if __name__ == "__main__":
    main()
