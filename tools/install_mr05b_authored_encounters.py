#!/usr/bin/env python3
"""MR05B authored Mercury encounter import.

Ports recovered Mercury Redux encounter content from the legacy Sinnoh-GBA
runtime snapshot into the real Platinum encounter JSONs.

This pass intentionally uses Platinum's native encounter structures as the
baseline representation:
- Morning is the 12-slot base grass table.
- Native Day/Night replacement slots are populated from recovered Mercury
  Day/Night tables.
- Surf is copied exactly when the recovered record has five water slots.
- Fishing preserves the recovered 10-slot species/level set across Platinum's
  three five-slot rod tables using deterministic duplication for the two- and
  three-slot legacy rods.

A follow-up MR05B runtime selector restores all 12 authored land slots for all
four Mercury periods. The recovered source remains authoritative.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TOD_MAP = {
    "gTwinleafTown": "encounters_twinleaf_town",
    "gRoute201": "encounters_route_201",
    "gRoute202": "encounters_route_202",
    "gLakeVerity": "encounters_lake_verity",
    "gRoute203": "encounters_route_203",
    "gRoute204South": "encounters_route_204_south",
    "gRoute204North": "encounters_route_204_north",
    "gValleyWindworksApproach": "encounters_valley_windworks_outside",
    "gRoute205South": "encounters_route_205_south",
    "gEternaForest": "encounters_eterna_forest",
    "gRoute206": "encounters_route_206",
    "gRoute207": "encounters_route_207",
    "gRoute208Shared": "encounters_route_208",
    "gRoute209": "encounters_route_209",
    "gRoute210SouthShared": "encounters_route_210_south",
    "gRoute212North": "encounters_route_212_north",
    "gRoute212South": "encounters_route_212_south",
    "gTrophyGarden": "encounters_trophy_garden",
    "gRoute213": "encounters_route_213",
    "gValorLakefront": "encounters_valor_lakefront",
    "gRoute214": "encounters_route_214",
    "gRoute215": "encounters_route_215",
    "gGreatMarshArea1": "encounters_great_marsh_1",
    "gGreatMarshArea2": "encounters_great_marsh_2",
    "gGreatMarshArea3": "encounters_great_marsh_3",
    "gGreatMarshArea4": "encounters_great_marsh_4",
    "gGreatMarshArea5": "encounters_great_marsh_5",
    "gGreatMarshArea6": "encounters_great_marsh_6",
}

STATIC_MAP = {
    "gOreburghGate": "encounters_oreburgh_gate_1f",
    "gOreburghMine_1": "encounters_oreburgh_mine_b1f",
    "gOreburghMine_3": "encounters_oreburgh_mine_b2f",
    "gMtCoronetFirstCrossing": "encounters_mt_coronet_1f_south",
    "gLostTower_1F": "encounters_route_209_lost_tower_1f",
    "gLostTower_2F": "encounters_route_209_lost_tower_2f",
    "gLostTower_3F": "encounters_route_209_lost_tower_3f",
    "gLostTower_4F": "encounters_route_209_lost_tower_4f",
    "gRuinManiacTunnel": "encounters_maniac_tunnel",
}

ADDITIVE_MAPS = {
    "gVerityLakefront": "MAP_HEADER_VERITY_LAKEFRONT",
    "gSandgemTown": "MAP_HEADER_SANDGEM_TOWN",
    "gFloaromaMeadow": "MAP_HEADER_FLOAROMA_MEADOW",
}

SPECIES_ALIASES = {
    # DS form plumbing is handled separately from the canonical 1025-species
    # registry. These aliases keep the encounter port compilable until the
    # custom/form registry is installed.
    "SPECIES_SHELLOS_WEST": "SPECIES_SHELLOS",
    "SPECIES_SHELLOS_EAST": "SPECIES_SHELLOS",
    "SPECIES_GASTRODON_WEST": "SPECIES_GASTRODON",
    "SPECIES_GASTRODON_EAST": "SPECIES_GASTRODON",
    "SPECIES_DEERLING_SPRING": "SPECIES_DEERLING",
    "SPECIES_DEERLING_SUMMER": "SPECIES_DEERLING",
    "SPECIES_DEERLING_AUTUMN": "SPECIES_DEERLING",
    "SPECIES_DEERLING_WINTER": "SPECIES_DEERLING",
    "SPECIES_ABRA_REDUX": "SPECIES_ABRA",
    "SPECIES_MACHOP_REDUX": "SPECIES_MACHOP",
    "SPECIES_LARVITAR_REDUX": "SPECIES_LARVITAR",
    "SPECIES_DARUMAKA_REDUX": "SPECIES_DARUMAKA",
}

OLD_ROD_EXPAND = (0, 1, 0, 0, 1)
GOOD_ROD_EXPAND = (2, 3, 4, 2, 4)
SUPER_ROD_INDEXES = (5, 6, 7, 8, 9)


def species(token: str) -> str:
    return SPECIES_ALIASES.get(token, token)


def fixed_level(mon: dict[str, Any]) -> int:
    lo = int(mon["min_level"])
    hi = int(mon["max_level"])
    return (lo + hi + 1) // 2


def land_slot(mon: dict[str, Any]) -> dict[str, Any]:
    return {"level": fixed_level(mon), "species": species(mon["species"])}


def water_slot(mon: dict[str, Any]) -> dict[str, Any]:
    return {
        "level_max": int(mon["max_level"]),
        "level_min": int(mon["min_level"]),
        "species": species(mon["species"]),
    }


def copy_water(dst: dict[str, Any], rec: dict[str, Any]) -> None:
    water = rec.get("water_mons")
    if not water:
        return
    mons = water.get("mons", [])
    if len(mons) != 5:
        raise SystemExit(f"{rec['base_label']}: expected 5 Surf slots, found {len(mons)}")
    dst["surf_rate"] = int(water.get("encounter_rate", dst.get("surf_rate", 0)))
    dst["surf_encounters"] = [water_slot(mon) for mon in mons]


def copy_fishing(dst: dict[str, Any], rec: dict[str, Any]) -> None:
    fishing = rec.get("fishing_mons")
    if not fishing:
        return
    mons = fishing.get("mons", [])
    if len(mons) != 10:
        raise SystemExit(f"{rec['base_label']}: expected 10 legacy fishing slots, found {len(mons)}")

    dst["old_rod_encounters"] = [water_slot(mons[i]) for i in OLD_ROD_EXPAND]
    dst["good_rod_encounters"] = [water_slot(mons[i]) for i in GOOD_ROD_EXPAND]
    dst["super_rod_encounters"] = [water_slot(mons[i]) for i in SUPER_ROD_INDEXES]

    rate = int(fishing.get("encounter_rate", 0))
    if rate:
        dst["old_rod_rate"] = rate
        dst["good_rod_rate"] = rate
        dst["super_rod_rate"] = rate


def records_by_label(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {rec["base_label"]: rec for rec in snapshot["records"]}


def update_tod_area(enc_dir: Path, stem: str, out_stem: str, records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    periods = {}
    for period in ("Morning", "Day", "Evening", "Night"):
        label = f"{stem}_{period}"
        if label not in records:
            raise SystemExit(f"Missing recovered Mercury record {label}")
        periods[period] = records[label]

    path = enc_dir / f"{out_stem}.json"
    if not path.exists():
        raise SystemExit(f"Missing Platinum encounter file {path}")

    before = json.loads(path.read_text())
    after = json.loads(path.read_text())

    morning_land = periods["Morning"].get("land_mons")
    if morning_land:
        mons = morning_land["mons"]
        if len(mons) != 12:
            raise SystemExit(f"{stem}: Morning must have 12 land slots")
        after["land_rate"] = int(morning_land["encounter_rate"])
        after["land_encounters"] = [land_slot(mon) for mon in mons]

        day_mons = periods["Day"]["land_mons"]["mons"]
        night_mons = periods["Night"]["land_mons"]["mons"]
        after["day"] = [species(day_mons[2]["species"]), species(day_mons[3]["species"])]
        after["night"] = [species(night_mons[2]["species"]), species(night_mons[3]["species"])]

        # Disable vanilla daily/cartridge replacement species from overriding
        # authored Mercury ecology. Dedicated Mercury Radar comes later.
        after["swarms"] = [after["land_encounters"][0]["species"], after["land_encounters"][1]["species"]]
        after["radar"] = [after["land_encounters"][8]["species"], after["land_encounters"][9]["species"], after["land_encounters"][10]["species"], after["land_encounters"][11]["species"]]
        for key in ("ruby", "sapphire", "emerald", "firered", "leafgreen"):
            after[key] = [after["land_encounters"][8]["species"], after["land_encounters"][9]["species"]]

    copy_water(after, periods["Day"])
    copy_fishing(after, periods["Day"])

    path.write_text(json.dumps(after, indent=4, ensure_ascii=False) + "\n")
    return {
        "area": out_stem,
        "source": stem,
        "changed": before != after,
        "morning_species": [x["species"] for x in after.get("land_encounters", [])],
    }


def update_static_area(enc_dir: Path, label: str, out_stem: str, records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rec = records.get(label)
    if rec is None:
        raise SystemExit(f"Missing recovered Mercury record {label}")
    path = enc_dir / f"{out_stem}.json"
    if not path.exists():
        raise SystemExit(f"Missing Platinum encounter file {path}")
    before = json.loads(path.read_text())
    after = json.loads(path.read_text())

    land = rec.get("land_mons")
    if land:
        mons = land["mons"]
        if len(mons) != 12:
            raise SystemExit(f"{label}: expected 12 land slots")
        after["land_rate"] = int(land["encounter_rate"])
        after["land_encounters"] = [land_slot(mon) for mon in mons]
        after["day"] = [after["land_encounters"][2]["species"], after["land_encounters"][3]["species"]]
        after["night"] = list(after["day"])

    copy_water(after, rec)
    copy_fishing(after, rec)
    path.write_text(json.dumps(after, indent=4, ensure_ascii=False) + "\n")
    return {"area": out_stem, "source": label, "changed": before != after}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("runtime_snapshot", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05b-authored-encounters.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    enc_dir = root / "res/field/encounters"
    snapshot = json.loads(args.runtime_snapshot.read_text())
    records = records_by_label(snapshot)

    results = []
    for stem, out_stem in TOD_MAP.items():
        results.append(update_tod_area(enc_dir, stem, out_stem, records))
    for label, out_stem in STATIC_MAP.items():
        results.append(update_static_area(enc_dir, label, out_stem, records))

    changed = [r["area"] for r in results if r["changed"]]
    report = {
        "gate": "MERCURY_MR05B_AUTHORED_ENCOUNTERS",
        "status": "PASS",
        "source_record_count": int(snapshot["record_count"]),
        "ported_area_count": len(results),
        "changed_area_count": len(changed),
        "changed_areas": changed,
        "additive_maps_pending_in_next_pass": ADDITIVE_MAPS,
        "full_four_period_runtime_selector_pending": True,
        "regional_honey_tree_runtime_pending": True,
        "species_aliases_used": SPECIES_ALIASES,
    }
    if not changed:
        raise SystemExit("MR05B authored encounter import changed zero areas")
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
