#!/usr/bin/env python3
"""MR05K — finish the final four identified standard encounter resources."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

PERIODS = ("morning", "day", "evening", "night")
WATER_SLOT_POINTS = (0.15, 0.50, 0.82, 0.94, 0.995)
HEATRAN = "SPECIES_HEATRAN"

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())

def load_supported_species(root: Path) -> set[str]:
    return {
        line.strip()
        for line in (root / "generated/species.txt").read_text().splitlines()
        if line.strip().startswith("SPECIES_")
    }

def walk_species(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_species(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_species(child)
    elif isinstance(value, str) and value.startswith("SPECIES_"):
        yield value

def midpoint(slot: dict[str, Any]) -> int:
    return (int(slot["min_level"]) + int(slot["max_level"]) + 1) // 2

def normalize_land_slot(slot: dict[str, Any]) -> dict[str, Any]:
    return {
        "level_min": int(slot["min_level"]),
        "level_max": int(slot["max_level"]),
        "species": slot["species"],
    }

def pair(slots: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for slot in slots:
        species = slot["species"]
        if species not in out:
            out.append(species)
        if len(out) == 2:
            break
    while len(out) < 2:
        out.append(slots[len(out)]["species"])
    return out

def validate_land(resource: str, periods: dict[str, Any]) -> None:
    for period in PERIODS:
        slots = periods.get(period)
        if not isinstance(slots, list) or len(slots) != 12:
            raise SystemExit(f"{resource}: {period} must contain exactly 12 slots")
        for i, slot in enumerate(slots):
            species = slot.get("species")
            low = slot.get("min_level")
            high = slot.get("max_level")
            if not isinstance(species, str) or not species.startswith("SPECIES_"):
                raise SystemExit(f"{resource}: {period}[{i}] invalid species")
            if not isinstance(low, int) or not isinstance(high, int) or not 1 <= low <= high <= 100:
                raise SystemExit(f"{resource}: {period}[{i}] invalid levels")

def land_patch(resource: str, area: dict[str, Any]) -> dict[str, Any]:
    periods = area["periods"]
    validate_land(resource, periods)
    normalized = {
        period: [normalize_land_slot(slot) for slot in periods[period]]
        for period in PERIODS
    }
    day = periods["day"]
    return {
        "land_rate": int(area["land_rate"]),
        "land_encounters": [
            {"level": midpoint(slot), "species": slot["species"]}
            for slot in day
        ],
        "day": pair(day),
        "night": pair(periods["night"]),
        "mercury_tod_land": normalized,
    }

def weighted_pick(entries: list[dict[str, Any]], point: float) -> dict[str, Any]:
    weighted = [(entry, max(1, int(entry.get("weight", 1)))) for entry in entries]
    total = sum(weight for _, weight in weighted)
    target = point * total
    running = 0
    for entry, weight in weighted:
        running += weight
        if running >= target:
            return entry
    return weighted[-1][0]

def weighted_five(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not entries:
        raise SystemExit("empty water encounter pool")
    out = []
    for point in WATER_SLOT_POINTS:
        entry = weighted_pick(entries, point)
        out.append({
            "level_min": int(entry["min_level"]),
            "level_max": int(entry["max_level"]),
            "species": entry["species"],
        })
    return out

def add_water(patch: dict[str, Any], water: dict[str, Any]) -> None:
    mapping = (
        ("surf", "surf_rate", "surf_encounters"),
        ("old_rod", "old_rod_rate", "old_rod_encounters"),
        ("good_rod", "good_rod_rate", "good_rod_encounters"),
        ("super_rod", "super_rod_rate", "super_rod_encounters"),
    )
    for pool_key, rate_key, out_key in mapping:
        pool = water.get(pool_key)
        rate = water.get(rate_key)
        if not isinstance(pool, list) or not pool:
            raise SystemExit(f"{pool_key}: pool missing/empty")
        if not isinstance(rate, int) or not 0 <= rate <= 100:
            raise SystemExit(f"{rate_key}: invalid rate")
        patch[rate_key] = rate
        patch[out_key] = weighted_five(pool)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("registry", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05k-final-identified-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = load_json(args.base_overrides)
    registry = load_json(args.registry)

    if registry.get("schema") != 1:
        raise SystemExit("MR05K registry schema must be 1")

    authored = registry.get("resources")
    if not isinstance(authored, dict) or len(authored) != 4:
        raise SystemExit("MR05K registry must contain exactly 4 resources")

    expected = {
        "encounters_stark_mountain_outside",
        "encounters_stark_mountain_room_1",
        "encounters_stark_mountain_room_2",
        "encounters_resort_area",
    }
    if set(authored) != expected:
        raise SystemExit("MR05K resource set mismatch")

    encounter_dir = root / "res/field/encounters"
    areas = output["areas"]
    full_tod = []
    water = []

    for resource, area in authored.items():
        if not (encounter_dir / f"{resource}.json").is_file():
            raise SystemExit(f"Missing Platinum encounter resource: {resource}")

        patch: dict[str, Any] = {}
        if "periods" in area:
            patch.update(land_patch(resource, area))
            full_tod.append(resource)
        elif area.get("land_random_encounters") is not False:
            raise SystemExit(f"{resource}: water-only resource must declare no random land")

        if "water" in area:
            add_water(patch, area["water"])
            water.append(resource)

        areas[resource] = patch

    random_species = {
        species
        for resource in authored
        for species in walk_species(areas[resource])
    }
    if HEATRAN in random_species:
        raise SystemExit("Heatran leaked into Stark Mountain random encounters")

    supported = load_supported_species(root)
    unresolved = sorted(s for s in random_species if s not in supported)
    if unresolved:
        raise SystemExit("MR05K output contains unsupported species: " + ", ".join(unresolved))

    if len(full_tod) != 3:
        raise SystemExit(f"MR05K expected 3 new full-TOD resources, found {len(full_tod)}")
    if water != ["encounters_resort_area"]:
        raise SystemExit(f"MR05K expected only Resort Area water authoring, found {water!r}")

    super_rod = areas["encounters_resort_area"]["super_rod_encounters"]
    if not all(slot["species"] == "SPECIES_MAGIKARP" for slot in super_rod):
        raise SystemExit("Resort Area Super Rod Magikarp identity was lost")
    if not any(slot["level_max"] == 100 for slot in super_rod):
        raise SystemExit("Resort Area no longer has a Lv100-capable Magikarp roll")

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides through MR05K: "
        "all identified standard encounter resources are now covered; only "
        "the 25 unknown_533-557 resources remain for map/header tracing."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05K_FINAL_IDENTIFIED_RESOURCES",
        "status": "PASS",
        "resource_count": 4,
        "full_tod_area_count_added": 3,
        "full_tod_slot_count_added": 144,
        "resort_area_water_authored": True,
        "resort_super_rod_magikarp_only": True,
        "resort_lv100_magikarp_capability_preserved": True,
        "heatran_randomized": False,
        "all_identified_standard_resources_complete": True,
        "remaining_identified_standard_resources_after_phase": 0,
        "remaining_unknown_resources_after_phase": 25,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
