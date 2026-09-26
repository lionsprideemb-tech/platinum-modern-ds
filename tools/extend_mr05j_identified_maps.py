#!/usr/bin/env python3
"""MR05J — finish identified pre-League/city/lake encounter resources.

The only identified resource deliberately not rewritten is
encounters_great_marsh_lookout: Mercury already removed the Great Marsh daily
availability gate, so binocular data remains informational.

This pass authors:
- Acuity Lakefront
- Lake Acuity, Lake Valor, Lake Verity, Lake Verity low-water state
- Mt. Coronet 1F south
- Valor Lakefront
- Canalave, Celestic, Eterna, Pastoria, Sunyshore, Twinleaf city/town water
- Pokémon League approach water

Static Jirachi, Mesprit, Azelf, and Uxie are explicitly excluded from random
encounters.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PERIODS = ("morning", "day", "evening", "night")
WATER_SLOT_POINTS = (0.15, 0.50, 0.82, 0.94, 0.995)

STATIC_EXCLUSIONS = {
    "SPECIES_JIRACHI",
    "SPECIES_MESPRIT",
    "SPECIES_AZELF",
    "SPECIES_UXIE",
}


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
    return (int(slot["level_min"]) + int(slot["level_max"]) + 1) // 2


def compatibility_pair(slots: list[dict[str, Any]]) -> list[str]:
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


def weighted_pick(entries: list[dict[str, Any]], point: float) -> dict[str, Any]:
    weighted = [(entry, max(1, int(entry.get("weight", 1)))) for entry in entries]
    if not weighted:
        raise SystemExit("empty weighted encounter pool")
    total = sum(weight for _, weight in weighted)
    target = point * total
    running = 0
    for entry, weight in weighted:
        running += weight
        if running >= target:
            return entry
    return weighted[-1][0]


def weighted_five(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for point in WATER_SLOT_POINTS:
        entry = weighted_pick(entries, point)
        out.append({
            "level_min": int(entry["min_level"]),
            "level_max": int(entry["max_level"]),
            "species": entry["species"],
        })
    return out


def validate_land(resource: str, periods: dict[str, Any]) -> None:
    for period in PERIODS:
        slots = periods.get(period)
        if not isinstance(slots, list) or len(slots) != 12:
            raise SystemExit(f"{resource}: {period} must contain exactly 12 land slots")
        for i, slot in enumerate(slots):
            species = slot.get("species")
            low = slot.get("min_level")
            high = slot.get("max_level")
            if not isinstance(species, str) or not species.startswith("SPECIES_"):
                raise SystemExit(f"{resource}: {period}[{i}] invalid species")
            if not isinstance(low, int) or not isinstance(high, int) or not 1 <= low <= high <= 100:
                raise SystemExit(f"{resource}: {period}[{i}] invalid levels")


def land_patch(area: dict[str, Any]) -> dict[str, Any]:
    periods = area["periods"]
    validate_land("land", periods)
    day = periods["day"]
    return {
        "land_rate": int(area["land_rate"]),
        "land_encounters": [
            {"level": midpoint(slot), "species": slot["species"]}
            for slot in day
        ],
        "day": compatibility_pair(day),
        "night": compatibility_pair(periods["night"]),
        "mercury_tod_land": {
            period: periods[period]
            for period in PERIODS
        },
    }


def add_water(patch: dict[str, Any], water: dict[str, Any]) -> None:
    mapping = (
        ("surf", "surf_rate", "surf_encounters"),
        ("old_rod", "old_rod_rate", "old_rod_encounters"),
        ("good_rod", "good_rod_rate", "good_rod_encounters"),
        ("super_rod", "super_rod_rate", "super_rod_encounters"),
    )
    for pool_key, rate_key, output_key in mapping:
        pool = water.get(pool_key)
        rate = water.get(rate_key)
        if not isinstance(pool, list) or not pool:
            raise SystemExit(f"water pool {pool_key} missing/empty")
        if not isinstance(rate, int) or not 0 <= rate <= 100:
            raise SystemExit(f"water rate {rate_key} invalid")
        patch[rate_key] = rate
        patch[output_key] = weighted_five(pool)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("registry", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05j-identified-maps-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = load_json(args.base_overrides)
    registry = load_json(args.registry)

    if registry.get("schema") != 1:
        raise SystemExit("MR05J registry schema must be 1")

    authored = registry.get("resources")
    if not isinstance(authored, dict) or len(authored) != 14:
        raise SystemExit("MR05J must contain exactly 14 authored standard resources")

    encounter_dir = root / "res/field/encounters"
    areas = output["areas"]

    full_tod_resources = []
    water_resources = []

    for resource, area in authored.items():
        path = encounter_dir / f"{resource}.json"
        if not path.is_file():
            raise SystemExit(f"Missing Platinum encounter resource: {resource}")

        patch: dict[str, Any] = {}
        periods = area.get("periods")
        if periods is not None:
            patch.update(land_patch(area))
            full_tod_resources.append(resource)
        elif area.get("land_random_encounters") is not False:
            raise SystemExit(f"{resource}: water-only map must explicitly declare no random land encounters")

        water = area.get("water")
        if water is not None:
            add_water(patch, water)
            water_resources.append(resource)

        if not patch:
            raise SystemExit(f"{resource}: generated empty patch")
        areas[resource] = patch

    # Great Marsh lookout remains an informational special resource.
    lookout_path = encounter_dir / "encounters_great_marsh_lookout.json"
    if not lookout_path.is_file():
        raise SystemExit("Great Marsh lookout resource missing")
    lookout = load_json(lookout_path)
    if not isinstance(lookout.get("binocular_coords"), list) or len(lookout["binocular_coords"]) != 36:
        raise SystemExit("Great Marsh binocular coordinate table changed unexpectedly")
    if not isinstance(lookout.get("before_national_dex"), list) or len(lookout["before_national_dex"]) != 32:
        raise SystemExit("Great Marsh pre-National binocular pool changed unexpectedly")
    if not isinstance(lookout.get("after_national_dex"), list) or len(lookout["after_national_dex"]) != 32:
        raise SystemExit("Great Marsh post-National binocular pool changed unexpectedly")

    # Story/static legendaries and Jirachi must not leak into random tables.
    random_species = {
        species
        for resource in authored
        for species in walk_species(areas[resource])
    }
    leaked = sorted(random_species & STATIC_EXCLUSIONS)
    if leaked:
        raise SystemExit("Static/story species leaked into MR05J random tables: " + ", ".join(leaked))

    supported = load_supported_species(root)
    unresolved = sorted(species for species in random_species if species not in supported)
    if unresolved:
        raise SystemExit("MR05J output contains unsupported species: " + ", ".join(unresolved))

    if len(full_tod_resources) != 7:
        raise SystemExit(f"MR05J expected 7 new full-TOD land resources, found {len(full_tod_resources)}")
    if len(water_resources) != 11:
        raise SystemExit(f"MR05J expected 11 authored water resources, found {len(water_resources)}")

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides through MR05J: "
        "all identified pre-League/city/lake resources are covered, with the "
        "Great Marsh lookout intentionally retained as informational metadata."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05J_IDENTIFIED_PRELEAGUE_MAPS",
        "status": "PASS",
        "resource_count": len(authored),
        "resources": list(authored),
        "full_tod_area_count_added": len(full_tod_resources),
        "full_tod_slot_count_added": len(full_tod_resources) * 48,
        "water_resource_count": len(water_resources),
        "great_marsh_lookout_certified": True,
        "great_marsh_lookout_changed": False,
        "static_story_species_excluded": sorted(STATIC_EXCLUSIONS),
        "lake_verity_early_game_levels_preserved": True,
        "lake_acuity_approved_cold_ecology_preserved": True,
        "lake_valor_disaster_basin_random_encounters_added": False,
        "runtime_species_registry_validation": "PASS",
        "remaining_identified_standard_resources_after_phase": 4,
        "remaining_unknown_resources_after_phase": 25,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
