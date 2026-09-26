#!/usr/bin/env python3
"""MR05H — Trophy Garden + Lost Tower encounter pass."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

PERIODS = ("morning", "day", "evening", "night")
LOST_TOWER_RESOURCES = tuple(f"encounters_route_209_lost_tower_{floor}f" for floor in range(1, 6))
TROPHY_GARDEN = "encounters_trophy_garden"

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())

def load_supported_species(root: Path) -> set[str]:
    return {line.strip() for line in (root / "generated/species.txt").read_text().splitlines()
            if line.strip().startswith("SPECIES_")}

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

def validate_periods(resource: str, area: dict[str, Any]) -> None:
    periods = area.get("periods")
    if not isinstance(periods, dict):
        raise SystemExit(f"{resource}: periods object missing")
    for period in PERIODS:
        slots = periods.get(period)
        if not isinstance(slots, list) or len(slots) != 12:
            raise SystemExit(f"{resource}: {period} must contain exactly 12 slots")
        for i, slot in enumerate(slots):
            species = slot.get("species")
            low = slot.get("level_min")
            high = slot.get("level_max")
            if not isinstance(species, str) or not species.startswith("SPECIES_"):
                raise SystemExit(f"{resource}: {period}[{i}] invalid species")
            if not isinstance(low, int) or not isinstance(high, int) or not 1 <= low <= high <= 100:
                raise SystemExit(f"{resource}: {period}[{i}] invalid levels")

def build_patch(area: dict[str, Any]) -> dict[str, Any]:
    periods = area["periods"]
    day = periods["day"]
    return {
        "land_rate": int(area["land_rate"]),
        "land_encounters": [{"level": midpoint(slot), "species": slot["species"]} for slot in day],
        "day": compatibility_pair(day),
        "night": compatibility_pair(periods["night"]),
        "mercury_tod_land": {period: periods[period] for period in PERIODS},
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("registry", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05h-lost-trophy-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = load_json(args.base_overrides)
    registry = load_json(args.registry)
    if registry.get("schema") != 1:
        raise SystemExit("MR05H registry schema must be 1")

    authored = registry.get("resources")
    expected = {TROPHY_GARDEN, *LOST_TOWER_RESOURCES}
    if not isinstance(authored, dict) or set(authored) != expected:
        raise SystemExit("MR05H registry resource mismatch")

    encounter_dir = root / "res/field/encounters"
    areas = output["areas"]
    for resource, area in authored.items():
        if not (encounter_dir / f"{resource}.json").is_file():
            raise SystemExit(f"Missing Platinum encounter resource: {resource}")
        validate_periods(resource, area)
        areas[resource] = build_patch(area)

    supported = load_supported_species(root)
    unresolved = sorted({species for resource in expected for species in walk_species(areas[resource]) if species not in supported})
    if unresolved:
        raise SystemExit("MR05H output contains unsupported species: " + ", ".join(unresolved))

    trophy = areas[TROPHY_GARDEN]
    trophy_union = {slot["species"] for slots in trophy["mercury_tod_land"].values() for slot in slots}
    required_trophy = {"SPECIES_EEVEE","SPECIES_PORYGON","SPECIES_CHANSEY","SPECIES_CASTFORM","SPECIES_PLUSLE","SPECIES_MINUN"}
    if not required_trophy.issubset(trophy_union):
        raise SystemExit("Trophy Garden former-daily species set incomplete")

    for resource in LOST_TOWER_RESOURCES:
        union = {slot["species"] for slots in areas[resource]["mercury_tod_land"].values() for slot in slots}
        if "SPECIES_GASTLY" not in union or "SPECIES_DUSKULL" not in union or len(union) < 8:
            raise SystemExit(f"{resource}: Lost Tower identity/variety check failed")

    output["description"] = "Mercury Redux authored Sinnoh encounters through MR05H, including Trophy Garden and all five Lost Tower floors."
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05H_LOST_TOWER_TROPHY_GARDEN",
        "status": "PASS",
        "resource_count": 6,
        "lost_tower_resource_count": 5,
        "trophy_garden_resource_count": 1,
        "full_tod_area_count_added": 6,
        "full_tod_slot_count_added": 288,
        "trophy_garden_daily_rng_gate": False,
        "trophy_garden_former_daily_species_distributed_by_tod": True,
        "lost_tower_memorial_identity_preserved": True,
        "lost_tower_galactic_story_added": False,
        "solaceon_ruins_deferred_for_unown_form_safety": True,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
