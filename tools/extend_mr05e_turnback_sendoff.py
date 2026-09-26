#!/usr/bin/env python3
"""MR05E — Sendoff Spring + Turnback Cave authored encounter pass.

This stage translates the sealed Sinnoh special-area registry onto Platinum's
real encounter resources. It is deliberately limited to random encounters:

- Sendoff Spring: full Morning/Day/Evening/Night + Surf/fishing.
- Turnback Cave: all maze encounter resources receive the authored tiered
  Ghost/Psychic ecology.
- Giratina's terminal room is explicitly no-random-encounter.

Static legendary scripting (Giratina retry, lake guardians, Dialga/Palkia
portals, Fullmoon/Newmoon statics) remains a separate phase so random-encounter
work stays auditable and does not silently rewrite story events.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

LAND_SLOT_WEIGHTS = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]

FORM_SPECIES_NORMALIZATION = {
    # Mercury's canonical 1,025-species encounter namespace stores Hisuian
    # battle forms outside the National Dex species list. Keep the authored
    # species family without emitting an unsupported encounter constant.
    "SPECIES_ZOROARK_HISUI": "SPECIES_ZOROARK",
}

TURNBACK_TIER_1 = (
    "encounters_turnback_cave_entrance",
    *tuple(f"encounters_turnback_cave_pillar_1_room_{i}" for i in range(1, 7)),
)
TURNBACK_TIER_2 = tuple(
    f"encounters_turnback_cave_pillar_2_room_{i}" for i in range(1, 7)
)
TURNBACK_TIER_3 = (
    "encounters_turnback_cave_pillar_room",
    *tuple(f"encounters_turnback_cave_pillar_3_room_{i}" for i in range(1, 7)),
)
TURNBACK_TERMINAL = "encounters_turnback_cave_giratina_room"
SENDOFF = "encounters_sendoff_spring"

ALL_RESOURCES = (
    SENDOFF,
    *TURNBACK_TIER_1,
    *TURNBACK_TIER_2,
    *TURNBACK_TIER_3,
    TURNBACK_TERMINAL,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_supported_species(root: Path) -> set[str]:
    return {
        line.strip()
        for line in (root / "generated/species.txt").read_text().splitlines()
        if line.strip().startswith("SPECIES_")
    }


def normalize_species(species: str) -> str:
    return FORM_SPECIES_NORMALIZATION.get(species, species)


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
            "species": normalize_species(chosen["species"]),
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
            "species": normalize_species(chosen["species"]),
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


def tod_patch(
    src: dict[str, list[dict[str, Any]]],
    *,
    land_rate: int = 15,
) -> dict[str, Any]:
    tables = {
        "morning": weighted_land(src["Morning"]),
        "day": weighted_land(src["Day"]),
        "evening": weighted_land(src["Evening"]),
        "night": weighted_land(src["Night"]),
    }
    return {
        "land_rate": land_rate,
        "land_encounters": midpoint_land(tables["day"]),
        "day": two_species(tables["day"]),
        "night": two_species(tables["night"]),
        "mercury_tod_land": tables,
    }


def add_water(patch: dict[str, Any], authored: dict[str, Any]) -> None:
    patch.update({
        "surf_rate": 20,
        "surf_encounters": weighted_five(authored["surf"]),
        "old_rod_rate": 25,
        "old_rod_encounters": weighted_five(authored["old_rod"]),
        "good_rod_rate": 50,
        "good_rod_encounters": weighted_five(authored["good_rod"]),
        "super_rod_rate": 75,
        "super_rod_encounters": weighted_five(authored["super_rod"]),
    })


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("special_registry", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05e-turnback-sendoff-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = load_json(args.base_overrides)
    areas = output["areas"]
    registry = load_json(args.special_registry)
    authored = registry["areas"]

    encounter_dir = root / "res/field/encounters"
    for resource in ALL_RESOURCES:
        if not (encounter_dir / f"{resource}.json").is_file():
            raise SystemExit(f"Missing Platinum encounter resource: {resource}")

    # Sendoff Spring
    sendoff = authored["SENDOFF_SPRING"]
    areas[SENDOFF] = tod_patch(sendoff["time_of_day_land"], land_rate=10)
    add_water(areas[SENDOFF], sendoff)

    # Turnback Cave authored depth tiers.
    turnback = authored["TURNBACK_CAVE"]
    tiers = turnback["tiers"]

    tier_sources = (
        (
            TURNBACK_TIER_1,
            tiers["ENTRANCE_TO_FIRST_PILLAR"]["time_of_day"],
        ),
        (
            TURNBACK_TIER_2,
            tiers["FIRST_TO_SECOND_PILLAR"]["time_of_day"],
        ),
        (
            TURNBACK_TIER_3,
            tiers["SECOND_TO_THIRD_PILLAR"]["time_of_day"],
        ),
    )

    for resources, src in tier_sources:
        for resource in resources:
            areas[resource] = tod_patch(src, land_rate=15)

    # Registry policy: the Giratina terminal room itself has no random wilds.
    areas[TURNBACK_TERMINAL] = {
        "land_rate": 0,
        "surf_rate": 0,
        "old_rod_rate": 0,
        "good_rod_rate": 0,
        "super_rod_rate": 0,
    }

    supported = load_supported_species(root)
    unresolved = sorted({
        species
        for resource in ALL_RESOURCES
        for species in walk_species(areas[resource])
        if species not in supported
    })
    if unresolved:
        raise SystemExit(
            "Sendoff/Turnback output contains unsupported species: "
            + ", ".join(unresolved)
        )

    full_tod_resources = [
        resource
        for resource in ALL_RESOURCES
        if "mercury_tod_land" in areas[resource]
    ]
    if len(full_tod_resources) != 21:
        raise SystemExit(
            f"expected 21 full-TOD Sendoff/Turnback resources, found {len(full_tod_resources)}"
        )

    if areas[TURNBACK_TERMINAL]["land_rate"] != 0:
        raise SystemExit("Turnback Giratina terminal room unexpectedly has random land encounters")

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides through Turnback Cave: "
        "Routes 201-230, Honey Trees, Great Marsh, special areas, Iron Island, "
        "Mt. Coronet, Victory Road, Sendoff Spring, and the Turnback Cave maze."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05E_TURNBACK_SENDOFF",
        "status": "PASS",
        "resource_count": len(ALL_RESOURCES),
        "resources": list(ALL_RESOURCES),
        "sendoff_spring_resource_count": 1,
        "turnback_cave_resource_count": len(ALL_RESOURCES) - 1,
        "turnback_tier1_resource_count": len(TURNBACK_TIER_1),
        "turnback_tier2_resource_count": len(TURNBACK_TIER_2),
        "turnback_tier3_resource_count": len(TURNBACK_TIER_3),
        "turnback_terminal_no_random_encounters": True,
        "full_tod_area_count_added": len(full_tod_resources),
        "full_tod_slot_count_added": len(full_tod_resources) * 48,
        "sendoff_water_fishing_authored": True,
        "static_giratina_story_deferred": True,
        "lake_guardian_statics_deferred": True,
        "spear_pillar_portal_statics_deferred": True,
        "fullmoon_newmoon_random_encounters_added": False,
        "form_species_normalization": FORM_SPECIES_NORMALIZATION,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
