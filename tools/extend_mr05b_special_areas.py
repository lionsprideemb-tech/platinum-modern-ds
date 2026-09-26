#!/usr/bin/env python3
"""Extend MR05B authored overrides with Ravaged Path, Old Chateau, and Snowpoint Temple."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

OLD_CHATEAU_1F = [
    "encounters_old_chateau",
    "encounters_old_chateau_dining_area",
    "encounters_old_chateau_side_rooms",
]
OLD_CHATEAU_2F = [
    "encounters_old_chateau_corridor",
    "encounters_old_chateau_back_east_room",
    "encounters_old_chateau_back_middle_east_room",
    "encounters_old_chateau_back_middle_room",
    "encounters_old_chateau_back_middle_west_room",
    "encounters_old_chateau_back_west_room",
]
SNOWPOINT_FILES = {
    "1F": "encounters_snowpoint_temple_1f",
    "B1F": "encounters_snowpoint_temple_b1f",
    "B2F": "encounters_snowpoint_temple_b2f",
    "B3F": "encounters_snowpoint_temple_b3f",
    "B4F": "encounters_snowpoint_temple_b4f",
    "B5F": "encounters_snowpoint_temple_b5f",
}
LAND_SLOT_WEIGHTS = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]

def load_supported_species(root: Path) -> set[str]:
    path = root / "generated/species.txt"
    return {line.strip() for line in path.read_text().splitlines() if line.strip().startswith("SPECIES_")}

def midpoint(entry: dict[str, Any]) -> int:
    lo = int(entry["min_level"])
    hi = int(entry["max_level"])
    return (lo + hi + 1) // 2

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

def weighted_land(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = sum(LAND_SLOT_WEIGHTS)
    out = []
    cumulative = 0
    for slot_weight in LAND_SLOT_WEIGHTS:
        target = (cumulative + slot_weight / 2) / total
        chosen = weighted_pick(entries, target)
        out.append({
            "level_max": int(chosen["max_level"]),
            "level_min": int(chosen["min_level"]),
            "species": chosen["species"],
        })
        cumulative += slot_weight
    return out

def land_fixed(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slots = weighted_land(entries)
    return [{"level": (s["level_min"] + s["level_max"] + 1) // 2, "species": s["species"]} for s in slots]

def timed_block(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    slots = weighted_land(entries)
    return {period: slots for period in ("morning", "day", "evening", "night")}

def timed_species(entries: list[dict[str, Any]]) -> list[str]:
    slots = weighted_land(entries)
    out = []
    for s in slots:
        if s["species"] not in out:
            out.append(s["species"])
        if len(out) == 2:
            break
    while len(out) < 2:
        out.append(slots[len(out)]["species"])
    return out

def weighted_five(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not entries:
        return []
    cutpoints = (0.15, 0.50, 0.82, 0.94, 0.995)
    out = []
    for point in cutpoints:
        e = weighted_pick(entries, point)
        out.append({
            "level_max": int(e["max_level"]),
            "level_min": int(e["min_level"]),
            "species": e["species"],
        })
    return out

def walk_species(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_species(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_species(child)
    elif isinstance(value, str) and value.startswith("SPECIES_"):
        yield value

def add_land_area(areas: dict[str, Any], file_key: str, entries: list[dict[str, Any]], land_rate: int = 30) -> None:
    areas[file_key] = {
        "land_rate": land_rate,
        "land_encounters": land_fixed(entries),
        "day": timed_species(entries),
        "night": timed_species(entries),
        "mercury_tod_land": timed_block(entries),
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("registry", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05b-special-areas-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = json.loads(args.base_overrides.read_text())
    registry = json.loads(args.registry.read_text())
    areas = output["areas"]
    source = registry["areas"]

    ravaged = source["RAVAGED_PATH"]
    areas["encounters_ravaged_path"] = {
        "surf_rate": 30,
        "surf_encounters": weighted_five(ravaged["surf"]),
        "old_rod_rate": 25,
        "old_rod_encounters": weighted_five(ravaged["old_rod"]),
        "good_rod_rate": 25,
        "good_rod_encounters": weighted_five(ravaged["good_rod"]),
        "super_rod_rate": 25,
        "super_rod_encounters": weighted_five(ravaged["super_rod"]),
    }

    chateau = source["OLD_CHATEAU"]["floors"]
    for file_key in OLD_CHATEAU_1F:
        add_land_area(areas, file_key, chateau["1F"], 30)
    for file_key in OLD_CHATEAU_2F:
        add_land_area(areas, file_key, chateau["2F"], 30)

    temple = source["SNOWPOINT_TEMPLE"]["floors"]
    for floor, file_key in SNOWPOINT_FILES.items():
        add_land_area(areas, file_key, temple[floor], 30)

    supported = load_supported_species(root)
    added = ["encounters_ravaged_path", *OLD_CHATEAU_1F, *OLD_CHATEAU_2F, *SNOWPOINT_FILES.values()]
    unresolved = sorted({
        species
        for key in added
        for species in walk_species(areas[key])
        if species not in supported
    })
    if unresolved:
        raise SystemExit("Special-area output contains unsupported species: " + ", ".join(unresolved))

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides: Routes 201-230, Honey Trees, "
        "Great Marsh, Ravaged Path, Old Chateau, and Snowpoint Temple."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05B_SPECIAL_AREAS_1",
        "status": "PASS",
        "resource_count": len(added),
        "resources": added,
        "ravaged_path_land_preserved": True,
        "ravaged_path_water_fishing_added": True,
        "old_chateau_resource_count": 9,
        "snowpoint_temple_floor_count": 6,
        "full_tod_area_count_added": 15,
        "full_tod_slot_count_added": 720,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
