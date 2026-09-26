#!/usr/bin/env python3
"""MR05G — translate the pre-League core-area encounter registry.

This pass fills a set of untouched Platinum encounter resources that matter
during the main adventure, while keeping story/static encounters separate from
ordinary wild tables.

Resources covered:
- Oreburgh Gate 1F / B1F
- Oreburgh Mine B1F / B2F
- Eterna Forest
- Wayward Cave 1F / B1F
- Valley Windworks exterior
- Fuego Ironworks exterior
- Ruin Maniac short cave / long cave / completed tunnel

Water/fishing tables are deliberately preserved from Platinum in this phase;
only land ecology is authored here. This keeps the batch small and avoids
inventing water distributions where Mercury has not authored replacements yet.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

LAND_SLOT_WEIGHTS = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
PERIODS = ("Morning", "Day", "Evening", "Night")
OUTPUT_PERIODS = ("morning", "day", "evening", "night")


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


def weighted_pick(entries: list[dict[str, Any]], point: float) -> dict[str, Any]:
    weighted = [(entry, max(1, int(entry.get("weight", 1)))) for entry in entries]
    if not weighted:
        raise ValueError("empty weighted encounter pool")

    total = sum(weight for _, weight in weighted)
    target = point * total
    running = 0
    for entry, weight in weighted:
        running += weight
        if running >= target:
            return entry
    return weighted[-1][0]


def weighted_land(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = sum(LAND_SLOT_WEIGHTS)
    out: list[dict[str, Any]] = []
    cumulative = 0
    for slot_weight in LAND_SLOT_WEIGHTS:
        point = (cumulative + slot_weight / 2) / total
        chosen = weighted_pick(entries, point)
        out.append(
            {
                "level_min": int(chosen["min_level"]),
                "level_max": int(chosen["max_level"]),
                "species": chosen["species"],
            }
        )
        cumulative += slot_weight
    return out


def midpoint_land(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "level": (int(slot["level_min"]) + int(slot["level_max"]) + 1) // 2,
            "species": slot["species"],
        }
        for slot in slots
    ]


def two_species(slots: list[dict[str, Any]]) -> list[str]:
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


def tod_patch(area: dict[str, Any]) -> dict[str, Any]:
    src = area["time_of_day"]
    tables = {
        output_period: weighted_land(src[source_period])
        for source_period, output_period in zip(PERIODS, OUTPUT_PERIODS)
    }

    return {
        "land_rate": int(area["land_rate"]),
        "land_encounters": midpoint_land(tables["day"]),
        "day": two_species(tables["day"]),
        "night": two_species(tables["night"]),
        "mercury_tod_land": tables,
    }


def assert_priority_route203(areas: dict[str, Any]) -> None:
    route = areas.get("encounters_route_203", {})
    tables = route.get("mercury_tod_land")
    if not isinstance(tables, dict):
        raise SystemExit("Route 203 full-TOD table missing before MR05G")

    for period in ("morning", "day", "evening", "night"):
        slots = tables.get(period)
        if not isinstance(slots, list) or len(slots) != 12:
            raise SystemExit(f"Route 203 {period} table malformed")
        species = [slot.get("species") for slot in slots]
        if "SPECIES_GIBLE" not in species:
            raise SystemExit(f"Route 203 {period}: early Gible priority slot missing")
        if "SPECIES_RIOLU" not in species:
            raise SystemExit(f"Route 203 {period}: early Riolu priority slot missing")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("registry", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05g-preleague-core-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = load_json(args.base_overrides)
    registry = load_json(args.registry)

    if registry.get("schema") != 1:
        raise SystemExit("MR05G registry schema must be 1")

    areas = output["areas"]
    authored = registry.get("areas")
    if not isinstance(authored, dict) or not authored:
        raise SystemExit("MR05G registry areas object missing/empty")

    encounter_dir = root / "res/field/encounters"

    for resource, area in authored.items():
        source_path = encounter_dir / f"{resource}.json"
        if not source_path.is_file():
            raise SystemExit(f"Missing Platinum encounter resource: {resource}")
        if "time_of_day" not in area:
            raise SystemExit(f"{resource}: time_of_day registry missing")
        for period in PERIODS:
            entries = area["time_of_day"].get(period)
            if not isinstance(entries, list) or not entries:
                raise SystemExit(f"{resource}: {period} pool missing/empty")

        # preserve_water_fishing is an explicit contract marker. By applying
        # only the land patch, the framework deep-merges the untouched
        # Platinum Surf/Rod tables from the underlying resource.
        if area.get("preserve_water_fishing") is not True:
            raise SystemExit(f"{resource}: preserve_water_fishing must be true in MR05G")

        areas[resource] = tod_patch(area)

    assert_priority_route203(areas)

    # Story/static separation guards.
    valley_species = set(walk_species(areas["encounters_valley_windworks_outside"]))
    if "SPECIES_DRIFLOON" in valley_species or "SPECIES_DRIFLOON_DELTA" in valley_species:
        raise SystemExit("Valley Windworks random table absorbed a Drifloon static/story encounter")

    fuego_species = set(walk_species(areas["encounters_fuego_ironworks_outside"]))
    if "SPECIES_MELTAN" in fuego_species:
        raise SystemExit("Fuego random table absorbed the stationary Meltan quest encounter")

    forest_species = set(walk_species(areas["encounters_eterna_forest"]))
    if "SPECIES_CELEBI" in forest_species:
        raise SystemExit("Eterna Forest random table absorbed the future Celebi shrine static")

    # Wayward B1F should be a genuine Gible den, not another microscopic roll.
    # One standard slot here is the leading 20% slot, so requiring Gible to
    # survive into that slot preserves a substantial catch rate.
    wayward_b1f = areas["encounters_wayward_cave_b1f"]["mercury_tod_land"]
    for period, slots in wayward_b1f.items():
        gible_slots = sum(slot["species"] == "SPECIES_GIBLE" for slot in slots)
        if gible_slots < 1 or slots[0]["species"] != "SPECIES_GIBLE":
            raise SystemExit(f"Wayward B1F {period}: Gible-den identity too weak after translation")

    supported = load_supported_species(root)
    unresolved = sorted(
        {
            species
            for resource in authored
            for species in walk_species(areas[resource])
            if species not in supported
        }
    )
    if unresolved:
        raise SystemExit(
            "MR05G output contains unsupported species: " + ", ".join(unresolved)
        )

    full_tod = [
        resource
        for resource in authored
        if "mercury_tod_land" in areas[resource]
    ]
    if len(full_tod) != len(authored):
        raise SystemExit("MR05G did not emit full-TOD tables for every authored resource")

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides through MR05G: "
        "Routes 201-230, Honey Trees, Great Marsh, special areas, Iron Island, "
        "Mt. Coronet, Victory Road, Sendoff Spring, Turnback Cave, and twelve "
        "additional pre-League core locations."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05G_PRELEAGUE_CORE_AREAS",
        "status": "PASS",
        "resource_count": len(authored),
        "resources": list(authored),
        "full_tod_area_count_added": len(full_tod),
        "full_tod_slot_count_added": len(full_tod) * 48,
        "route203_gible_priority_access": True,
        "route203_riolu_priority_access": True,
        "wayward_b1f_gible_den_preserved": True,
        "valley_normal_drifloon_randomized": False,
        "valley_delta_drifloon_randomized": False,
        "fuego_meltan_randomized": False,
        "eterna_celebi_randomized": False,
        "platinum_water_fishing_preserved": True,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
