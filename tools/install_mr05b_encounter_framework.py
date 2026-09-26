#!/usr/bin/env python3
"""MR05B — centralized Mercury encounter-table framework.

Reads every Platinum encounter JSON as one logical dataset, validates the
schema, optionally applies centralized per-area overrides, and emits a single
canonical manifest/report for later Mercury encounter editing and randomizer
work.

Overrides are keyed by encounter file stem without the .json extension.
Object values deep-merge. Array values may be replaced as a whole or patched
by index using an object such as {"0": {"species": "SPECIES_GIBLE"}}.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

EXPECTED_LIST_LENGTHS = {
    "land_encounters": 12,
    "swarms": 2,
    "day": 2,
    "night": 2,
    "radar": 4,
    "ruby": 2,
    "sapphire": 2,
    "emerald": 2,
    "firered": 2,
    "leafgreen": 2,
    "surf_encounters": 5,
    "old_rod_encounters": 5,
    "good_rod_encounters": 5,
    "super_rod_encounters": 5,
}

RATE_FIELDS = (
    "land_rate",
    "surf_rate",
    "old_rod_rate",
    "good_rod_rate",
    "super_rod_rate",
)

WATER_LISTS = (
    "surf_encounters",
    "old_rod_encounters",
    "good_rod_encounters",
    "super_rod_encounters",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def validate_species(value: Any, where: str) -> None:
    if not isinstance(value, str) or not value.startswith("SPECIES_"):
        raise SystemExit(f"{where}: invalid species token {value!r}")


def validate_standard_area(key: str, data: dict[str, Any]) -> None:
    for field, expected in EXPECTED_LIST_LENGTHS.items():
        if field not in data:
            raise SystemExit(f"{key}: missing {field}")
        if not isinstance(data[field], list) or len(data[field]) != expected:
            raise SystemExit(
                f"{key}: {field} must contain {expected} entries, found "
                f"{len(data[field]) if isinstance(data[field], list) else 'non-list'}"
            )

    for field in RATE_FIELDS:
        rate = data.get(field)
        if not isinstance(rate, int) or not 0 <= rate <= 100:
            raise SystemExit(f"{key}: {field} must be an integer from 0 to 100")

    for i, slot in enumerate(data["land_encounters"]):
        if not isinstance(slot, dict):
            raise SystemExit(f"{key}: land slot {i} is not an object")
        level = slot.get("level")
        if not isinstance(level, int) or not 0 <= level <= 100:
            raise SystemExit(f"{key}: land slot {i} invalid level {level!r}")
        validate_species(slot.get("species"), f"{key} land slot {i}")

    for field in ("swarms", "day", "night", "radar", "ruby", "sapphire", "emerald", "firered", "leafgreen"):
        for i, species in enumerate(data[field]):
            validate_species(species, f"{key} {field}[{i}]")

    for field in WATER_LISTS:
        for i, slot in enumerate(data[field]):
            if not isinstance(slot, dict):
                raise SystemExit(f"{key}: {field}[{i}] is not an object")
            low = slot.get("level_min")
            high = slot.get("level_max")
            if not isinstance(low, int) or not isinstance(high, int):
                raise SystemExit(f"{key}: {field}[{i}] levels must be integers")
            if not 0 <= low <= 100 or not 0 <= high <= 100 or high < low:
                raise SystemExit(f"{key}: {field}[{i}] invalid level range {low}-{high}")
            validate_species(slot.get("species"), f"{key} {field}[{i}]")

    category = data.get("map_category")
    if not isinstance(category, dict):
        raise SystemExit(f"{key}: missing map_category object")
    if category.get("map_type") not in ("field", "dungeon"):
        raise SystemExit(f"{key}: unexpected map_type {category.get('map_type')!r}")
    if not isinstance(category.get("map_number"), int):
        raise SystemExit(f"{key}: map_number must be an integer")

    if "mercury_tod_land" in data:
        tables = data["mercury_tod_land"]
        if not isinstance(tables, dict):
            raise SystemExit(f"{key}: mercury_tod_land must be an object")
        for period in ("morning", "day", "evening", "night"):
            slots = tables.get(period)
            if not isinstance(slots, list) or len(slots) != 12:
                raise SystemExit(f"{key}: mercury_tod_land.{period} must contain 12 slots")
            for i, slot in enumerate(slots):
                if not isinstance(slot, dict):
                    raise SystemExit(f"{key}: mercury_tod_land.{period}[{i}] is not an object")
                low = slot.get("level_min")
                high = slot.get("level_max")
                if not isinstance(low, int) or not isinstance(high, int) or not 1 <= low <= high <= 100:
                    raise SystemExit(f"{key}: mercury_tod_land.{period}[{i}] invalid level range")
                validate_species(slot.get("species"), f"{key} mercury_tod_land.{period}[{i}]")

    if "daily_encounters" in data:
        daily = data["daily_encounters"]
        if not isinstance(daily, list) or len(daily) != 16:
            raise SystemExit(f"{key}: daily_encounters must contain 16 species")
        for i, species in enumerate(daily):
            validate_species(species, f"{key} daily_encounters[{i}]")

    if "elusive_rod_encounter" in data:
        elusive = data["elusive_rod_encounter"]
        if not isinstance(elusive, dict):
            raise SystemExit(f"{key}: elusive_rod_encounter must be an object")
        validate_species(elusive.get("species"), f"{key} elusive rod")
        dims = elusive.get("map_dimensions")
        if (
            not isinstance(dims, list)
            or len(dims) != 2
            or not all(isinstance(v, int) and v > 0 for v in dims)
        ):
            raise SystemExit(f"{key}: elusive rod map_dimensions must contain two positive integers")
        tiles = elusive.get("tiles")
        if not isinstance(tiles, list) or not tiles or not all(isinstance(v, int) and v >= 0 for v in tiles):
            raise SystemExit(f"{key}: elusive rod tiles must be a non-empty integer list")


def validate_honey_tree(key: str, data: dict[str, Any]) -> None:
    for field in ("common", "uncommon", "rare"):
        values = data.get(field)
        if not isinstance(values, list) or len(values) != 6:
            raise SystemExit(f"{key}: {field} must contain 6 species")
        for i, species in enumerate(values):
            validate_species(species, f"{key} {field}[{i}]")


def validate_great_marsh_lookout(key: str, data: dict[str, Any]) -> None:
    for field in ("before_national_dex", "after_national_dex"):
        values = data.get(field)
        if not isinstance(values, list) or len(values) != 32:
            raise SystemExit(f"{key}: {field} must contain 32 species")
        for i, species in enumerate(values):
            validate_species(species, f"{key} {field}[{i}]")

    coords = data.get("binocular_coords")
    if not isinstance(coords, list) or len(coords) != 36:
        raise SystemExit(f"{key}: binocular_coords must contain 36 coordinates")
    for i, coord in enumerate(coords):
        if (
            not isinstance(coord, dict)
            or not isinstance(coord.get("x"), int)
            or not isinstance(coord.get("y"), int)
        ):
            raise SystemExit(f"{key}: binocular_coords[{i}] must contain integer x/y")


def encounter_resource_type(key: str, data: dict[str, Any]) -> str:
    if "land_encounters" in data:
        return "standard"
    if set(("common", "uncommon", "rare")).issubset(data):
        return "honey_tree"
    if set(("before_national_dex", "after_national_dex", "binocular_coords")).issubset(data):
        return "great_marsh_lookout"
    raise SystemExit(f"{key}: unrecognized encounter resource schema")


def validate_area(key: str, data: dict[str, Any]) -> None:
    resource_type = encounter_resource_type(key, data)
    if resource_type == "standard":
        validate_standard_area(key, data)
    elif resource_type == "honey_tree":
        validate_honey_tree(key, data)
    elif resource_type == "great_marsh_lookout":
        validate_great_marsh_lookout(key, data)



def merge_patch(base: Any, patch: Any, where: str) -> Any:
    if isinstance(base, dict) and isinstance(patch, dict):
        out = deepcopy(base)
        for key, value in patch.items():
            if key not in out:
                if key.startswith("mercury_"):
                    out[key] = deepcopy(value)
                    continue
                raise SystemExit(f"{where}: unknown field {key!r}")
            out[key] = merge_patch(out[key], value, f"{where}.{key}")
        return out

    if isinstance(base, list) and isinstance(patch, dict):
        out = deepcopy(base)
        for raw_index, value in patch.items():
            try:
                index = int(raw_index)
            except (TypeError, ValueError):
                raise SystemExit(f"{where}: array patch index {raw_index!r} is not an integer")
            if index < 0 or index >= len(out):
                raise SystemExit(f"{where}: array patch index {index} out of range")
            out[index] = merge_patch(out[index], value, f"{where}[{index}]")
        return out

    return deepcopy(patch)


def load_dataset(encounter_dir: Path) -> dict[str, dict[str, Any]]:
    files = sorted(encounter_dir.glob("encounters_*.json"))
    if not files:
        raise SystemExit(f"No encounter tables found in {encounter_dir}")

    dataset: dict[str, dict[str, Any]] = {}
    for path in files:
        key = path.stem
        data = json.loads(path.read_text())
        validate_area(key, data)
        dataset[key] = data
    return dataset


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("config", type=Path)
    ap.add_argument("--manifest", type=Path, default=Path("mr05b-encounter-manifest.json"))
    ap.add_argument("--report", type=Path, default=Path("mr05b-encounter-framework.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    encounter_dir = root / "res/field/encounters"
    cfg = json.loads(args.config.read_text())

    if cfg.get("schema") != 1:
        raise SystemExit("MR05B encounter config schema must be 1")
    overrides = cfg.get("areas")
    if not isinstance(overrides, dict):
        raise SystemExit("MR05B encounter config areas must be an object")

    before = load_dataset(encounter_dir)
    before_digest = digest(before)

    after = deepcopy(before)
    changed = []

    for key, patch in overrides.items():
        if key not in after:
            raise SystemExit(f"MR05B override references unknown encounter area {key!r}")
        if not isinstance(patch, dict):
            raise SystemExit(f"MR05B override for {key} must be an object")
        patched = merge_patch(after[key], patch, key)
        validate_area(key, patched)
        if patched != after[key]:
            after[key] = patched
            changed.append(key)

    for key in sorted(after):
        path = encounter_dir / f"{key}.json"
        path.write_text(json.dumps(after[key], indent=4, ensure_ascii=False) + "\n")

    reloaded = load_dataset(encounter_dir)
    if reloaded != after:
        raise SystemExit("MR05B encounter write/read round-trip mismatch")

    after_digest = digest(after)

    manifest = {
        "schema": 1,
        "source": "Mercury Redux encounter framework",
        "area_count": len(after),
        "dataset_sha256": after_digest,
        "areas": after,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    resource_types = {
        "standard": sum(encounter_resource_type(k, v) == "standard" for k, v in after.items()),
        "honey_tree": sum(encounter_resource_type(k, v) == "honey_tree" for k, v in after.items()),
        "great_marsh_lookout": sum(encounter_resource_type(k, v) == "great_marsh_lookout" for k, v in after.items()),
    }

    report = {
        "gate": "MERCURY_MR05B_ENCOUNTER_TABLE_FRAMEWORK",
        "status": "PASS",
        "area_count": len(after),
        "resource_types": resource_types,
        "changed_area_count": len(changed),
        "changed_areas": changed,
        "baseline_sha256": before_digest,
        "output_sha256": after_digest,
        "baseline_preserved": before_digest == after_digest,
        "central_config": str(args.config),
        "supports": [
            "land",
            "swarm",
            "day",
            "night",
            "Poke Radar",
            "GBA dual-slot",
            "Surf",
            "Old Rod",
            "Good Rod",
            "Super Rod",
            "Honey Trees",
            "Trophy Garden daily encounters",
            "Great Marsh daily/binocular resources",
            "Mt. Coronet elusive-rod encounter",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
