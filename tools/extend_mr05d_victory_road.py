#!/usr/bin/env python3
"""MR05D — translate sealed Victory Road / Marley encounter registries.

Uses Platinum's six real Victory Road encounter resources:
- main pre-League 1F / 2F / B1F;
- the three Marley / Route 224 branch rooms.

The Marley branch is also opened on the first pre-League Victory Road visit by
removing Platinum's Hall-of-Fame + National-Dex collector blockade. Route 224's
own already-authored Mercury encounter table is not rewritten by this pass.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

LAND_SLOT_WEIGHTS = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]

RESOURCE_MAP = {
    "encounters_victory_road_1f": ("main", "1F_ROCKY_GATE"),
    "encounters_victory_road_2f": ("main", "2F_MAGNETIC_GALLERY"),
    "encounters_victory_road_b1f": ("main", "B1F_UNDERGROUND_WATER"),
    "encounters_victory_road_1f_room_1": ("marley", "FOG_GALLERY"),
    "encounters_victory_road_1f_room_2": ("marley", "UNDERGROUND_LAKE"),
    "encounters_victory_road_1f_room_3": ("marley", "EXIT_PASSAGE"),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_supported_species(root: Path) -> set[str]:
    path = root / "generated/species.txt"
    return {
        line.strip()
        for line in path.read_text().splitlines()
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
        target = (cumulative + slot_weight / 2) / total
        chosen = weighted_pick(entries, target)
        out.append({
            "level_min": int(chosen["min_level"]),
            "level_max": int(chosen["max_level"]),
            "species": chosen["species"],
        })
        cumulative += slot_weight
    return out


def weighted_five(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for point in (0.15, 0.50, 0.82, 0.94, 0.995):
        chosen = weighted_pick(entries, point)
        out.append({
            "level_min": int(chosen["min_level"]),
            "level_max": int(chosen["max_level"]),
            "species": chosen["species"],
        })
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


def tod_patch(area: dict[str, Any], land_rate: int = 10) -> dict[str, Any]:
    src = area["time_of_day"]
    tables = {
        "morning": weighted_land(src["Morning"]),
        "day": weighted_land(src["Day"]),
        "evening": weighted_land(src["Evening"]),
        "night": weighted_land(src["Night"]),
    }
    out: dict[str, Any] = {
        "land_rate": land_rate,
        "land_encounters": midpoint_land(tables["day"]),
        "day": two_species(tables["day"]),
        "night": two_species(tables["night"]),
        "mercury_tod_land": tables,
    }
    if "surf" in area:
        out["surf_rate"] = 20
        out["surf_encounters"] = weighted_five(area["surf"])
    if "old_rod" in area:
        out["old_rod_rate"] = 25
        out["old_rod_encounters"] = weighted_five(area["old_rod"])
    if "good_rod" in area:
        out["good_rod_rate"] = 50
        out["good_rod_encounters"] = weighted_five(area["good_rod"])
    if "super_rod" in area:
        out["super_rod_rate"] = 75
        out["super_rod_encounters"] = weighted_five(area["super_rod"])
    return out


def open_marley_branch(root: Path) -> None:
    path = root / "res/field/scripts/scripts_victory_road_1f.s"
    text = path.read_text()
    old = """VictoryRoad_OnTransition:
    SetFlag FLAG_FIRST_ARRIVAL_VICTORY_ROAD
    GoToIfUnset FLAG_GAME_COMPLETED, VictoryRoad_DontHideCollector
    GetNationalDexEnabled VAR_MAP_LOCAL_0x00
    GoToIfEq VAR_MAP_LOCAL_0x00, FALSE, VictoryRoad_DontHideCollector
    SetFlag FLAG_HIDE_VICTORY_ROAD_1F_COLLECTOR
VictoryRoad_DontHideCollector:
    End
"""
    new = """VictoryRoad_OnTransition:
    SetFlag FLAG_FIRST_ARRIVAL_VICTORY_ROAD
    SetFlag FLAG_HIDE_VICTORY_ROAD_1F_COLLECTOR
    End
"""
    if text.count(old) != 1:
        raise SystemExit("Victory Road collector gate anchor changed")
    text = text.replace(old, new, 1)
    path.write_text(text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("victory_road_registry", type=Path)
    ap.add_argument("marley_registry", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05d-victory-road-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = load_json(args.base_overrides)
    areas = output["areas"]
    main_registry = load_json(args.victory_road_registry)
    marley_registry = load_json(args.marley_registry)

    main_areas = main_registry["victory_road"]["areas"]
    marley_areas = marley_registry["marley_victory_road_branch"]["areas"]

    encounter_dir = root / "res/field/encounters"
    for resource in RESOURCE_MAP:
        if not (encounter_dir / f"{resource}.json").is_file():
            raise SystemExit(f"Missing Platinum Victory Road resource: {resource}")

    for resource, (source, key) in RESOURCE_MAP.items():
        authored = main_areas[key] if source == "main" else marley_areas[key]
        areas[resource] = tod_patch(authored, land_rate=10)

    open_marley_branch(root)

    supported = load_supported_species(root)
    unresolved = sorted({
        species
        for resource in RESOURCE_MAP
        for species in walk_species(areas[resource])
        if species not in supported
    })
    if unresolved:
        raise SystemExit(
            "Victory Road output contains unsupported species: " + ", ".join(unresolved)
        )

    script = (root / "res/field/scripts/scripts_victory_road_1f.s").read_text()
    preleague_open = (
        "SetFlag FLAG_HIDE_VICTORY_ROAD_1F_COLLECTOR" in script
        and "GetNationalDexEnabled VAR_MAP_LOCAL_0x00" not in script
        and "GoToIfUnset FLAG_GAME_COMPLETED, VictoryRoad_DontHideCollector" not in script
    )
    if not preleague_open:
        raise SystemExit("Marley branch pre-League unlock proof failed")

    # Route 224 itself was already authored in the route-wide pass; this stage
    # must not silently duplicate/replace that work.
    route224_untouched = "encounters_route_224" not in RESOURCE_MAP
    if not route224_untouched:
        raise SystemExit("MR05D unexpectedly targets Route 224")

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides through Victory Road: "
        "Routes 201-230, Honey Trees, Great Marsh, special areas, Iron Island, "
        "Mt. Coronet, and all six Victory Road encounter resources."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05D_VICTORY_ROAD",
        "status": "PASS",
        "resource_count": len(RESOURCE_MAP),
        "resources": list(RESOURCE_MAP),
        "main_victory_road_resource_count": 3,
        "marley_branch_resource_count": 3,
        "full_tod_area_count_added": 6,
        "full_tod_slot_count_added": 288,
        "marley_branch_preleague_open": preleague_open,
        "national_dex_gate_removed": True,
        "hall_of_fame_gate_removed": True,
        "route_224_existing_authored_table_preserved": route224_untouched,
        "youngster_martin_team_untouched": True,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
