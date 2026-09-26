#!/usr/bin/env python3
"""Extend MR05B authored encounters with Iron Island and Mt. Coronet.

This pass is a translator, not a new ecology-design pass. It consumes the
sealed Mercury encounter registries already stored in data/encounters and maps
those authored pools onto Platinum's real encounter resources.

Covered here:
- all 7 Iron Island encounter resources (outside + six mine floors);
- all 12 Mt. Coronet resources beyond the already-authored 1F south resource;
- preservation of the Regi ruins as no-random-encounter static/story spaces.

Important project rules preserved:
- Riolu remains Riley's special gift on Iron Island, not a random encounter;
- Mt. Coronet floors keep distinct authored identities;
- the snowy mountainside uses four full time-of-day tables;
- Feebas is a permanent normal fishing target in B1F while Platinum's
  elusive-rod metadata remains present for compatibility/reference;
- Regirock/Regice/Registeel/Regigigas are reserved for the later static/script
  pass and are never inserted into ordinary random encounter tables here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

LAND_SLOT_WEIGHTS = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
PERIODS = ("morning", "day", "evening", "night")

IRON_ISLAND_FILES = (
    "encounters_iron_island",
    "encounters_iron_island_1f",
    "encounters_iron_island_b1f_left_room",
    "encounters_iron_island_b1f_right_room",
    "encounters_iron_island_b2f_left_room",
    "encounters_iron_island_b2f_right_room",
    "encounters_iron_island_b3f",
)

MT_CORONET_FILES = (
    "encounters_mt_coronet_2f",
    "encounters_mt_coronet_3f",
    "encounters_mt_coronet_outside_north",
    "encounters_mt_coronet_outside_south",
    "encounters_mt_coronet_4f_rooms_1_and_2",
    "encounters_mt_coronet_4f_room_3",
    "encounters_mt_coronet_5f",
    "encounters_mt_coronet_6f",
    "encounters_mt_coronet_1f_tunnel_room",
    "encounters_mt_coronet_1f_north_room_2",
    "encounters_mt_coronet_1f_north_room_1",
    "encounters_mt_coronet_b1f",
)

IRON_FLOOR_MAP = {
    "encounters_iron_island_1f": "1F",
    "encounters_iron_island_b1f_left_room": "B1F_LEFT_ORE_VEIN",
    "encounters_iron_island_b1f_right_room": "B1F_RIGHT_TRAINING_GALLERY",
    "encounters_iron_island_b2f_left_room": "B2F_LEFT_RILEY_SECTION",
    "encounters_iron_island_b2f_right_room": "B2F_RIGHT_IRON_CHAMBER",
    "encounters_iron_island_b3f": "B3F_FINAL_MINE",
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
    if not entries:
        raise ValueError("weighted encounter source is empty")
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


def weighted_five(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cutpoints = (0.15, 0.50, 0.82, 0.94, 0.995)
    out = []
    for point in cutpoints:
        chosen = weighted_pick(entries, point)
        out.append({
            "level_max": int(chosen["max_level"]),
            "level_min": int(chosen["min_level"]),
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


def timed_species(slots: list[dict[str, Any]]) -> list[str]:
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


def standard_land_patch(
    entries: list[dict[str, Any]],
    *,
    land_rate: int,
) -> dict[str, Any]:
    slots = weighted_land(entries)
    return {
        "land_rate": land_rate,
        "land_encounters": midpoint_land(slots),
        "day": timed_species(slots),
        "night": timed_species(slots),
        "mercury_tod_land": {period: slots for period in PERIODS},
    }


def tod_land_patch(
    source: dict[str, list[dict[str, Any]]],
    *,
    land_rate: int,
) -> dict[str, Any]:
    tables = {
        "morning": weighted_land(source["Morning"]),
        "day": weighted_land(source["Day"]),
        "evening": weighted_land(source["Evening"]),
        "night": weighted_land(source["Night"]),
    }
    return {
        "land_rate": land_rate,
        "land_encounters": midpoint_land(tables["day"]),
        "day": timed_species(tables["day"]),
        "night": timed_species(tables["night"]),
        "mercury_tod_land": tables,
    }


def blend_entries(*groups: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Blend authored 100-weight pools without inventing species or levels.

    Concatenating full authored pools gives each source identity equal total
    influence in the deterministic DS-slot translation.
    """
    out: list[dict[str, Any]] = []
    for group in groups:
        out.extend(dict(entry) for entry in group)
    return out


def assert_source_rules(
    iron: dict[str, Any],
    coronet: dict[str, Any],
    regi: dict[str, Any],
) -> None:
    if iron.get("riley", {}).get("gift_species") != "SPECIES_RIOLU":
        raise SystemExit("Iron Island registry no longer identifies Riolu as Riley's gift")
    if iron.get("iron_ruins", {}).get("random_encounters") is not False:
        raise SystemExit("Iron Ruins must remain a no-random-encounter special area")
    if coronet.get("areas", {}).get("SPEAR_PILLAR", {}).get("random_wild_encounters") is not False:
        raise SystemExit("Spear Pillar must remain a no-random-encounter special area")
    for key in ("ROCK_PEAK_RUINS", "ICEBERG_RUINS", "IRON_RUINS"):
        if regi.get("ruins", {}).get(key, {}).get("random_encounters") is not False:
            raise SystemExit(f"{key} must remain a no-random-encounter static ruin")
    if regi.get("regigigas", {}).get("random_encounters") is not False:
        raise SystemExit("Regigigas must remain a scripted/static encounter")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("iron_island_registry", type=Path)
    ap.add_argument("route211_coronet_registry", type=Path)
    ap.add_argument("post_candice_coronet_registry", type=Path)
    ap.add_argument("regi_registry", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05b-iron-coronet-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = load_json(args.base_overrides)
    areas = output["areas"]

    iron = load_json(args.iron_island_registry)
    route211 = load_json(args.route211_coronet_registry)
    coronet = load_json(args.post_candice_coronet_registry)
    regi = load_json(args.regi_registry)
    assert_source_rules(iron, coronet, regi)

    encounter_dir = root / "res/field/encounters"
    for key in (*IRON_ISLAND_FILES, *MT_CORONET_FILES):
        if not (encounter_dir / f"{key}.json").is_file():
            raise SystemExit(f"Missing Platinum encounter resource: {key}")

    # ------------------------------------------------------------------
    # Iron Island — direct translation of the sealed Iron Island registry.
    # ------------------------------------------------------------------
    outside = iron["outside"]
    areas["encounters_iron_island"] = {
        "surf_rate": 20,
        "surf_encounters": weighted_five(outside["surf"]),
        "old_rod_rate": 25,
        "old_rod_encounters": weighted_five(outside["fishing"]["old_rod"]),
        "good_rod_rate": 50,
        "good_rod_encounters": weighted_five(outside["fishing"]["good_rod"]),
        "super_rod_rate": 75,
        "super_rod_encounters": weighted_five(outside["fishing"]["super_rod"]),
    }

    for resource, floor_key in IRON_FLOOR_MAP.items():
        areas[resource] = standard_land_patch(
            iron["floors"][floor_key]["encounters"],
            land_rate=10,
        )

    # Guard the project decision that Riolu is Riley's story gift, not a
    # random Iron Island catch.
    iron_random_species = {
        species
        for key in IRON_FLOOR_MAP
        for species in walk_species(areas[key])
    }
    if "SPECIES_RIOLU" in iron_random_species:
        raise SystemExit("Riolu leaked into random Iron Island encounters")

    # ------------------------------------------------------------------
    # Mt. Coronet — translate the existing route-side and post-Candice
    # registries onto Platinum's twelve remaining encounter resources.
    # ------------------------------------------------------------------
    c_areas = coronet["areas"]

    # Route 211-facing north room: directly authored in the earlier Route 211
    # registry.
    areas["encounters_mt_coronet_1f_north_room_1"] = standard_land_patch(
        route211["mt_coronet_route211_entrance"]["land_encounters"],
        land_rate=10,
    )

    # Route 216/Iceberg-Ruins-facing north room: the deeper Route 211-side
    # authored cavern pool.
    areas["encounters_mt_coronet_1f_north_room_2"] = standard_land_patch(
        route211["mt_coronet_route211_lower_cavern"]["land_encounters"],
        land_rate=10,
    )

    # Tunnel between the Route 211-side cavern and snowy ascent: blend the two
    # already-authored neighboring identities rather than inventing a third
    # ecology list.
    tunnel_entries = blend_entries(
        route211["mt_coronet_route211_lower_cavern"]["land_encounters"],
        c_areas["MT_CORONET_ASCENT_2F"]["land"],
    )
    areas["encounters_mt_coronet_1f_tunnel_room"] = standard_land_patch(
        tunnel_entries,
        land_rate=10,
    )

    # B1F Feebas lake: full authored land + water + fishing. The upstream
    # elusive-rod field is deliberately untouched by this patch.
    b1f = c_areas["MT_CORONET_B1F_FEEBAS_LAKE"]
    areas["encounters_mt_coronet_b1f"] = standard_land_patch(
        b1f["land"],
        land_rate=10,
    )
    areas["encounters_mt_coronet_b1f"].update({
        "surf_rate": 20,
        "surf_encounters": weighted_five(b1f["surf"]),
        "old_rod_rate": 25,
        "old_rod_encounters": weighted_five(b1f["fishing"]["Old Rod"]),
        "good_rod_rate": 50,
        "good_rod_encounters": weighted_five(b1f["fishing"]["Good Rod"]),
        "super_rod_rate": 75,
        "super_rod_encounters": weighted_five(b1f["fishing"]["Super Rod"]),
    })

    # Main ascent.
    areas["encounters_mt_coronet_2f"] = standard_land_patch(
        c_areas["MT_CORONET_ASCENT_2F"]["land"],
        land_rate=10,
    )
    areas["encounters_mt_coronet_3f"] = standard_land_patch(
        c_areas["MT_CORONET_ASCENT_3F"]["land"],
        land_rate=10,
    )

    mountainside = c_areas["MT_CORONET_MOUNTAINSIDE"]["time_of_day_land"]
    for key in ("encounters_mt_coronet_outside_north", "encounters_mt_coronet_outside_south"):
        areas[key] = tod_land_patch(mountainside, land_rate=10)

    # Platinum shares one encounter resource across 4F rooms 1 and 2. Preserve
    # both authored identities by blending their land pools 50/50.
    room1 = c_areas["MT_CORONET_4F_ROOM1_CRYSTAL_GALLERY"]
    room2 = c_areas["MT_CORONET_4F_ROOM2_WATERFALL_SHRINE"]
    areas["encounters_mt_coronet_4f_rooms_1_and_2"] = standard_land_patch(
        blend_entries(room1["land"], room2["land"]),
        land_rate=10,
    )
    # The authored Waterfall Shrine supplies a dedicated water pool; map that
    # to Surf while leaving Platinum's rod tables intact rather than inventing
    # rod-specific distributions the registry did not define.
    areas["encounters_mt_coronet_4f_rooms_1_and_2"].update({
        "surf_rate": 20,
        "surf_encounters": weighted_five(room2["waterfall_pool"]),
    })

    areas["encounters_mt_coronet_4f_room_3"] = standard_land_patch(
        c_areas["MT_CORONET_4F_ROOM3_GALACTIC_TUNNEL"]["land"],
        land_rate=15,
    )
    areas["encounters_mt_coronet_5f"] = standard_land_patch(
        c_areas["MT_CORONET_5F_CELESTIAL_CHAMBER"]["land"],
        land_rate=15,
    )
    areas["encounters_mt_coronet_6f"] = standard_land_patch(
        c_areas["MT_CORONET_6F_SUMMIT_GATE"]["land"],
        land_rate=15,
    )

    # Prove Feebas is now a normal fishing target while the original special
    # metadata remains untouched in the underlying Platinum encounter JSON.
    b1f_source = load_json(encounter_dir / "encounters_mt_coronet_b1f.json")
    elusive = b1f_source.get("elusive_rod_encounter")
    elusive_preserved = (
        isinstance(elusive, dict)
        and elusive.get("species") == "SPECIES_FEEBAS"
        and "elusive_rod_encounter" not in areas["encounters_mt_coronet_b1f"]
    )
    if not elusive_preserved:
        raise SystemExit("Mt. Coronet B1F elusive-rod metadata preservation check failed")

    regular_feebas = any(
        slot.get("species") == "SPECIES_FEEBAS"
        for field in ("good_rod_encounters", "super_rod_encounters")
        for slot in areas["encounters_mt_coronet_b1f"][field]
    )
    if not regular_feebas:
        raise SystemExit("Feebas did not survive normal B1F fishing translation")

    # Validate every emitted species against Mercury's canonical 1025-species
    # runtime registry.
    supported = load_supported_species(root)
    changed = [*IRON_ISLAND_FILES, *MT_CORONET_FILES]
    unresolved = sorted({
        species
        for key in changed
        for species in walk_species(areas[key])
        if species not in supported
    })
    if unresolved:
        raise SystemExit(
            "Iron Island / Mt. Coronet output contains unsupported species: "
            + ", ".join(unresolved)
        )

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides: Routes 201-230, Honey Trees, "
        "Great Marsh, Ravaged Path, Old Chateau, Snowpoint Temple, Iron Island, and Mt. Coronet."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05B_IRON_CORONET_2",
        "status": "PASS",
        "resource_count": len(changed),
        "resources": changed,
        "source_mode": "sealed_registry_translation",
        "iron_island_resource_count": len(IRON_ISLAND_FILES),
        "iron_island_land_resource_count": len(IRON_FLOOR_MAP),
        "iron_island_riolu_random_encounter": False,
        "iron_island_riley_gift_preserved": True,
        "mt_coronet_resource_count": len(MT_CORONET_FILES),
        "mt_coronet_1f_south_intentionally_not_reauthored": True,
        "mt_coronet_tunnel_uses_authored_transition_blend": True,
        "mt_coronet_4f_shared_resource_blends_rooms_1_and_2": True,
        "full_tod_area_count_added": len(IRON_FLOOR_MAP) + len(MT_CORONET_FILES),
        "full_tod_slot_count_added": (len(IRON_FLOOR_MAP) + len(MT_CORONET_FILES)) * 48,
        "mt_coronet_feebas_regular_fishing": regular_feebas,
        "mt_coronet_elusive_rod_metadata_preserved": elusive_preserved,
        "regi_ruins_random_encounters_added": False,
        "registeel_iron_ruins_static_reserved": True,
        "regice_iceberg_ruins_static_reserved": True,
        "regirock_rock_peak_ruins_static_reserved": True,
        "regigigas_static_reserved": True,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
