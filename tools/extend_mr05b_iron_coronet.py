#!/usr/bin/env python3
"""Extend MR05B authored encounter overrides with Iron Island and Mt. Coronet.

This pass keeps Platinum's actual encounter-resource geography as the authority:
- all 7 Iron Island encounter resources;
- the 12 Mt. Coronet resources not already represented by the south 1F entry.

The ordinary encounter layer is expanded for Mercury Redux while preserving
special map mechanics that live in the upstream JSON, especially Mt. Coronet
B1F's elusive-rod/Feebas metadata.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

IRON_ISLAND_FILES = (
    "encounters_iron_island",
    "encounters_iron_island_1f",
    "encounters_iron_island_b1f_left_room",
    "encounters_iron_island_b1f_right_room",
    "encounters_iron_island_b2f_right_room",
    "encounters_iron_island_b2f_left_room",
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

PERIODS = ("morning", "day", "evening", "night")


def slot(species: str, lo: int, hi: int | None = None) -> dict[str, Any]:
    hi = lo if hi is None else hi
    return {"species": species, "level_min": lo, "level_max": hi}


def fixed(slots: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    out = list(slots)
    if len(out) != 12:
        raise ValueError(f"land table must contain 12 slots, found {len(out)}")
    return out


def midpoint_table(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "level": (int(entry["level_min"]) + int(entry["level_max"]) + 1) // 2,
            "species": entry["species"],
        }
        for entry in slots
    ]


def first_two_species(slots: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for entry in slots:
        species = entry["species"]
        if species not in out:
            out.append(species)
        if len(out) == 2:
            return out
    while len(out) < 2:
        out.append(slots[len(out)]["species"])
    return out


def land_patch(
    day_slots: list[dict[str, Any]],
    *,
    morning_slots: list[dict[str, Any]] | None = None,
    evening_slots: list[dict[str, Any]] | None = None,
    night_slots: list[dict[str, Any]] | None = None,
    land_rate: int = 10,
) -> dict[str, Any]:
    day_slots = fixed(day_slots)
    morning_slots = fixed(morning_slots or day_slots)
    evening_slots = fixed(evening_slots or day_slots)
    night_slots = fixed(night_slots or day_slots)
    return {
        "land_rate": land_rate,
        "land_encounters": midpoint_table(day_slots),
        "day": first_two_species(day_slots),
        "night": first_two_species(night_slots),
        "mercury_tod_land": {
            "morning": morning_slots,
            "day": day_slots,
            "evening": evening_slots,
            "night": night_slots,
        },
    }


def water_slot(species: str, lo: int, hi: int) -> dict[str, Any]:
    return {"species": species, "level_min": lo, "level_max": hi}


def walk_species(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_species(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_species(child)
    elif isinstance(value, str) and value.startswith("SPECIES_"):
        yield value


def load_supported_species(root: Path) -> set[str]:
    path = root / "generated/species.txt"
    return {
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip().startswith("SPECIES_")
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05b-iron-coronet-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = json.loads(args.base_overrides.read_text())
    areas = output["areas"]

    encounter_dir = root / "res/field/encounters"
    for key in (*IRON_ISLAND_FILES, *MT_CORONET_FILES):
        if not (encounter_dir / f"{key}.json").is_file():
            raise SystemExit(f"Missing Platinum encounter resource: {key}")

    # ------------------------------------------------------------------
    # Iron Island
    # ------------------------------------------------------------------
    # Outside/coast: no artificial land encounters. Preserve the island's
    # marine identity while widening the water/fishing pool.
    areas["encounters_iron_island"] = {
        "surf_rate": 20,
        "surf_encounters": [
            water_slot("SPECIES_WINGULL", 28, 34),
            water_slot("SPECIES_TENTACOOL", 28, 34),
            water_slot("SPECIES_PELIPPER", 31, 36),
            water_slot("SPECIES_FINIZEN", 30, 36),
            water_slot("SPECIES_MANTINE", 33, 38),
        ],
        "old_rod_rate": 25,
        "old_rod_encounters": [
            water_slot("SPECIES_MAGIKARP", 8, 14),
            water_slot("SPECIES_FINNEON", 10, 15),
            water_slot("SPECIES_MAGIKARP", 12, 18),
            water_slot("SPECIES_REMORAID", 12, 18),
            water_slot("SPECIES_FINNEON", 14, 20),
        ],
        "good_rod_rate": 50,
        "good_rod_encounters": [
            water_slot("SPECIES_FINNEON", 20, 28),
            water_slot("SPECIES_REMORAID", 21, 29),
            water_slot("SPECIES_CLAUNCHER", 22, 30),
            water_slot("SPECIES_QWILFISH", 24, 31),
            water_slot("SPECIES_MANTYKE", 24, 31),
        ],
        "super_rod_rate": 75,
        "super_rod_encounters": [
            water_slot("SPECIES_GYARADOS", 34, 45),
            water_slot("SPECIES_LUMINEON", 34, 44),
            water_slot("SPECIES_QWILFISH", 35, 45),
            water_slot("SPECIES_MANTINE", 36, 46),
            water_slot("SPECIES_WAILMER", 36, 46),
        ],
    }

    iron_tables = {
        "encounters_iron_island_1f": [
            slot("SPECIES_GEODUDE", 30, 32),
            slot("SPECIES_GRAVELER", 31, 33),
            slot("SPECIES_ZUBAT", 30, 32),
            slot("SPECIES_GOLBAT", 31, 33),
            slot("SPECIES_ONIX", 31, 33),
            slot("SPECIES_ARON", 30, 32),
            slot("SPECIES_DRILBUR", 31, 33),
            slot("SPECIES_MAWILE", 31, 33),
            slot("SPECIES_CARBINK", 31, 33),
            slot("SPECIES_TINKATINK", 31, 33),
            slot("SPECIES_BELDUM", 32, 33),
            slot("SPECIES_RIOLU", 32, 33),
        ],
        "encounters_iron_island_b1f_left_room": [
            slot("SPECIES_GRAVELER", 31, 33),
            slot("SPECIES_GRAVELER", 32, 34),
            slot("SPECIES_GOLBAT", 31, 33),
            slot("SPECIES_ONIX", 31, 34),
            slot("SPECIES_ARON", 31, 33),
            slot("SPECIES_DRILBUR", 31, 34),
            slot("SPECIES_MAWILE", 32, 34),
            slot("SPECIES_CARBINK", 32, 34),
            slot("SPECIES_TINKATINK", 32, 34),
            slot("SPECIES_VAROOM", 32, 34),
            slot("SPECIES_BELDUM", 33, 34),
            slot("SPECIES_RIOLU", 33, 34),
        ],
        "encounters_iron_island_b1f_right_room": [
            slot("SPECIES_GRAVELER", 31, 33),
            slot("SPECIES_GOLBAT", 31, 34),
            slot("SPECIES_ONIX", 32, 34),
            slot("SPECIES_ARON", 31, 34),
            slot("SPECIES_DRILBUR", 32, 34),
            slot("SPECIES_MAWILE", 32, 34),
            slot("SPECIES_VAROOM", 32, 34),
            slot("SPECIES_ORTHWORM", 33, 34),
            slot("SPECIES_CARBINK", 32, 34),
            slot("SPECIES_TINKATINK", 32, 34),
            slot("SPECIES_BELDUM", 33, 34),
            slot("SPECIES_RIOLU", 33, 34),
        ],
        "encounters_iron_island_b2f_right_room": [
            slot("SPECIES_ONIX", 32, 34),
            slot("SPECIES_GRAVELER", 32, 35),
            slot("SPECIES_GOLBAT", 32, 35),
            slot("SPECIES_STEELIX", 33, 35),
            slot("SPECIES_LAIRON", 33, 35),
            slot("SPECIES_DRILBUR", 32, 35),
            slot("SPECIES_MAWILE", 33, 35),
            slot("SPECIES_VAROOM", 33, 35),
            slot("SPECIES_ORTHWORM", 34, 35),
            slot("SPECIES_TINKATINK", 33, 35),
            slot("SPECIES_BELDUM", 34, 35),
            slot("SPECIES_RIOLU", 34, 35),
        ],
        "encounters_iron_island_b2f_left_room": [
            slot("SPECIES_ONIX", 32, 34),
            slot("SPECIES_GRAVELER", 32, 35),
            slot("SPECIES_GOLBAT", 32, 35),
            slot("SPECIES_STEELIX", 33, 35),
            slot("SPECIES_LAIRON", 33, 35),
            slot("SPECIES_DRILBUR", 32, 35),
            slot("SPECIES_CARBINK", 33, 35),
            slot("SPECIES_VAROOM", 33, 35),
            slot("SPECIES_ORTHWORM", 34, 35),
            slot("SPECIES_TINKATINK", 33, 35),
            slot("SPECIES_BELDUM", 34, 35),
            slot("SPECIES_RIOLU", 34, 35),
        ],
        "encounters_iron_island_b3f": [
            slot("SPECIES_STEELIX", 34, 36),
            slot("SPECIES_GRAVELER", 33, 36),
            slot("SPECIES_GOLBAT", 33, 36),
            slot("SPECIES_LAIRON", 34, 36),
            slot("SPECIES_EXCADRILL", 35, 36),
            slot("SPECIES_MAWILE", 34, 36),
            slot("SPECIES_CARBINK", 34, 36),
            slot("SPECIES_VAROOM", 34, 36),
            slot("SPECIES_ORTHWORM", 35, 36),
            slot("SPECIES_TINKATUFF", 35, 36),
            slot("SPECIES_BELDUM", 35, 36),
            slot("SPECIES_RIOLU", 35, 36),
        ],
    }
    for key, table in iron_tables.items():
        areas[key] = land_patch(table, land_rate=10)

    # ------------------------------------------------------------------
    # Mt. Coronet
    # ------------------------------------------------------------------
    # Keep the early north room early. Do not flatten Coronet's distinct
    # story-time level bands into one late-game table.
    coronet_land = {
        "encounters_mt_coronet_1f_north_room_1": [
            slot("SPECIES_BRONZOR", 14, 16),
            slot("SPECIES_GEODUDE", 14, 16),
            slot("SPECIES_MEDITITE", 14, 16),
            slot("SPECIES_CLEFFA", 13, 15),
            slot("SPECIES_MACHOP", 14, 16),
            slot("SPECIES_ZUBAT", 14, 16),
            slot("SPECIES_CHINGLING", 14, 16),
            slot("SPECIES_NOSEPASS", 14, 16),
            slot("SPECIES_ROLYCOLY", 14, 16),
            slot("SPECIES_NACLI", 14, 16),
            slot("SPECIES_ROGGENROLA", 15, 16),
            slot("SPECIES_CARBINK", 15, 16),
        ],
        "encounters_mt_coronet_1f_north_room_2": [
            slot("SPECIES_BRONZOR", 33, 35),
            slot("SPECIES_GRAVELER", 33, 35),
            slot("SPECIES_MEDITITE", 33, 35),
            slot("SPECIES_CLEFAIRY", 32, 35),
            slot("SPECIES_MACHOKE", 33, 35),
            slot("SPECIES_GOLBAT", 33, 35),
            slot("SPECIES_CHINGLING", 33, 35),
            slot("SPECIES_NOSEPASS", 33, 35),
            slot("SPECIES_BOLDORE", 33, 35),
            slot("SPECIES_NACLSTACK", 33, 35),
            slot("SPECIES_DRILBUR", 34, 35),
            slot("SPECIES_CARBINK", 34, 35),
        ],
        "encounters_mt_coronet_b1f": [
            slot("SPECIES_BRONZOR", 33, 35),
            slot("SPECIES_GRAVELER", 33, 35),
            slot("SPECIES_MEDITITE", 33, 35),
            slot("SPECIES_CLEFAIRY", 32, 35),
            slot("SPECIES_MACHOKE", 33, 35),
            slot("SPECIES_GOLBAT", 33, 35),
            slot("SPECIES_CHINGLING", 33, 35),
            slot("SPECIES_NOSEPASS", 33, 35),
            slot("SPECIES_BOLDORE", 33, 35),
            slot("SPECIES_NACLSTACK", 33, 35),
            slot("SPECIES_GLIMMET", 34, 35),
            slot("SPECIES_CARBINK", 34, 35),
        ],
        "encounters_mt_coronet_1f_tunnel_room": [
            slot("SPECIES_GRAVELER", 37, 39),
            slot("SPECIES_MEDICHAM", 37, 39),
            slot("SPECIES_CLEFAIRY", 36, 39),
            slot("SPECIES_MACHOKE", 37, 39),
            slot("SPECIES_GOLBAT", 37, 39),
            slot("SPECIES_CHINGLING", 37, 39),
            slot("SPECIES_NOSEPASS", 37, 39),
            slot("SPECIES_BOLDORE", 37, 39),
            slot("SPECIES_NACLSTACK", 37, 39),
            slot("SPECIES_DRILBUR", 38, 39),
            slot("SPECIES_GLIMMET", 38, 39),
            slot("SPECIES_CARBINK", 38, 39),
        ],
        "encounters_mt_coronet_2f": [
            slot("SPECIES_BRONZONG", 37, 39),
            slot("SPECIES_GRAVELER", 37, 39),
            slot("SPECIES_MEDICHAM", 37, 39),
            slot("SPECIES_CLEFAIRY", 36, 39),
            slot("SPECIES_MACHOKE", 38, 40),
            slot("SPECIES_GOLBAT", 37, 40),
            slot("SPECIES_CHINGLING", 37, 39),
            slot("SPECIES_NOSEPASS", 37, 39),
            slot("SPECIES_BOLDORE", 38, 40),
            slot("SPECIES_NACLSTACK", 38, 40),
            slot("SPECIES_GLIMMET", 39, 40),
            slot("SPECIES_CARBINK", 39, 40),
        ],
        "encounters_mt_coronet_3f": [
            slot("SPECIES_BRONZONG", 38, 40),
            slot("SPECIES_GRAVELER", 38, 40),
            slot("SPECIES_MEDICHAM", 38, 40),
            slot("SPECIES_CLEFAIRY", 37, 40),
            slot("SPECIES_MACHOKE", 39, 41),
            slot("SPECIES_GOLBAT", 38, 41),
            slot("SPECIES_CHINGLING", 38, 40),
            slot("SPECIES_NOSEPASS", 38, 40),
            slot("SPECIES_BOLDORE", 39, 41),
            slot("SPECIES_NACLSTACK", 39, 41),
            slot("SPECIES_GLIMMET", 40, 41),
            slot("SPECIES_CARBINK", 40, 41),
        ],
        "encounters_mt_coronet_4f_rooms_1_and_2": [
            slot("SPECIES_BRONZONG", 39, 41),
            slot("SPECIES_GRAVELER", 39, 41),
            slot("SPECIES_MEDICHAM", 39, 41),
            slot("SPECIES_CLEFAIRY", 38, 41),
            slot("SPECIES_MACHOKE", 40, 42),
            slot("SPECIES_GOLBAT", 39, 42),
            slot("SPECIES_CHINGLING", 39, 41),
            slot("SPECIES_NOSEPASS", 39, 41),
            slot("SPECIES_CARBINK", 40, 42),
            slot("SPECIES_GLIMMET", 40, 42),
            slot("SPECIES_LUNATONE", 41, 42),
            slot("SPECIES_SOLROCK", 41, 42),
        ],
        "encounters_mt_coronet_4f_room_3": [
            slot("SPECIES_BRONZONG", 39, 42),
            slot("SPECIES_GRAVELER", 39, 42),
            slot("SPECIES_MEDICHAM", 39, 42),
            slot("SPECIES_CLEFAIRY", 38, 42),
            slot("SPECIES_MACHOKE", 40, 42),
            slot("SPECIES_GOLBAT", 39, 42),
            slot("SPECIES_CHINGLING", 39, 42),
            slot("SPECIES_CHIMECHO", 40, 42),
            slot("SPECIES_CARBINK", 40, 42),
            slot("SPECIES_GLIMMET", 40, 42),
            slot("SPECIES_LUNATONE", 41, 42),
            slot("SPECIES_SOLROCK", 41, 42),
        ],
        "encounters_mt_coronet_5f": [
            slot("SPECIES_BRONZONG", 40, 43),
            slot("SPECIES_GRAVELER", 40, 43),
            slot("SPECIES_MEDICHAM", 40, 43),
            slot("SPECIES_CLEFAIRY", 39, 43),
            slot("SPECIES_MACHOKE", 41, 43),
            slot("SPECIES_GOLBAT", 40, 43),
            slot("SPECIES_CHIMECHO", 41, 43),
            slot("SPECIES_CARBINK", 41, 43),
            slot("SPECIES_GLIMMET", 41, 43),
            slot("SPECIES_SABLEYE", 42, 43),
            slot("SPECIES_LUNATONE", 42, 43),
            slot("SPECIES_SOLROCK", 42, 43),
        ],
        "encounters_mt_coronet_6f": [
            slot("SPECIES_BRONZONG", 41, 44),
            slot("SPECIES_GRAVELER", 41, 44),
            slot("SPECIES_MEDICHAM", 41, 44),
            slot("SPECIES_CLEFAIRY", 40, 44),
            slot("SPECIES_MACHOKE", 42, 44),
            slot("SPECIES_GOLBAT", 41, 44),
            slot("SPECIES_CHIMECHO", 42, 44),
            slot("SPECIES_CARBINK", 42, 44),
            slot("SPECIES_GLIMMET", 42, 44),
            slot("SPECIES_SABLEYE", 43, 44),
            slot("SPECIES_LUNATONE", 43, 44),
            slot("SPECIES_SOLROCK", 43, 44),
        ],
    }
    for key, table in coronet_land.items():
        areas[key] = land_patch(table, land_rate=15 if key in {
            "encounters_mt_coronet_4f_room_3",
            "encounters_mt_coronet_5f",
            "encounters_mt_coronet_6f",
        } else 10)

    # Mountainside sections are the only Coronet resources in this batch where
    # time of day should materially change the ecology.
    outside_day = [
        slot("SPECIES_SNOVER", 36, 39),
        slot("SPECIES_ABOMASNOW", 38, 40),
        slot("SPECIES_MEDICHAM", 38, 40),
        slot("SPECIES_MACHOKE", 39, 41),
        slot("SPECIES_CHINGLING", 37, 40),
        slot("SPECIES_NOSEPASS", 38, 40),
        slot("SPECIES_ABSOL", 39, 41),
        slot("SPECIES_SWINUB", 37, 40),
        slot("SPECIES_PILOSWINE", 39, 41),
        slot("SPECIES_BERGMITE", 38, 40),
        slot("SPECIES_CUBCHOO", 38, 40),
        slot("SPECIES_SNOM", 39, 40),
    ]
    outside_morning = [
        slot("SPECIES_SNOVER", 36, 39),
        slot("SPECIES_SNOVER", 37, 40),
        slot("SPECIES_MEDICHAM", 38, 40),
        slot("SPECIES_CHINGLING", 37, 40),
        slot("SPECIES_NOSEPASS", 38, 40),
        slot("SPECIES_SWINUB", 37, 40),
        slot("SPECIES_PILOSWINE", 39, 41),
        slot("SPECIES_BERGMITE", 38, 40),
        slot("SPECIES_CUBCHOO", 38, 40),
        slot("SPECIES_SNOM", 38, 40),
        slot("SPECIES_ABOMASNOW", 39, 41),
        slot("SPECIES_ABSOL", 40, 41),
    ]
    outside_evening = [
        slot("SPECIES_SNOVER", 36, 39),
        slot("SPECIES_ABOMASNOW", 38, 41),
        slot("SPECIES_MEDICHAM", 38, 40),
        slot("SPECIES_MACHOKE", 39, 41),
        slot("SPECIES_CHINGLING", 38, 40),
        slot("SPECIES_NOSEPASS", 38, 40),
        slot("SPECIES_ABSOL", 39, 41),
        slot("SPECIES_SWINUB", 38, 40),
        slot("SPECIES_PILOSWINE", 39, 41),
        slot("SPECIES_BERGMITE", 39, 40),
        slot("SPECIES_SNEASEL", 40, 41),
        slot("SPECIES_SNOM", 39, 41),
    ]
    outside_night = [
        slot("SPECIES_SNOVER", 37, 40),
        slot("SPECIES_ABOMASNOW", 39, 41),
        slot("SPECIES_GOLBAT", 38, 41),
        slot("SPECIES_NOCTOWL", 38, 41),
        slot("SPECIES_ABSOL", 39, 41),
        slot("SPECIES_SNEASEL", 39, 41),
        slot("SPECIES_SWINUB", 38, 40),
        slot("SPECIES_PILOSWINE", 39, 41),
        slot("SPECIES_BERGMITE", 39, 41),
        slot("SPECIES_CUBCHOO", 39, 41),
        slot("SPECIES_SNOM", 39, 41),
        slot("SPECIES_CHINGLING", 39, 41),
    ]
    for key in ("encounters_mt_coronet_outside_north", "encounters_mt_coronet_outside_south"):
        areas[key] = land_patch(
            outside_day,
            morning_slots=outside_morning,
            evening_slots=outside_evening,
            night_slots=outside_night,
            land_rate=10,
        )

    # 4F water preserves the Dragon/fishing identity but makes the pool useful
    # before postgame without depending on version or daily mechanics.
    areas["encounters_mt_coronet_4f_rooms_1_and_2"].update({
        "surf_rate": 20,
        "surf_encounters": [
            water_slot("SPECIES_ZUBAT", 30, 36),
            water_slot("SPECIES_GOLBAT", 32, 38),
            water_slot("SPECIES_BARBOACH", 31, 37),
            water_slot("SPECIES_WHISCASH", 34, 40),
            water_slot("SPECIES_DRATINI", 34, 40),
        ],
        "old_rod_rate": 25,
        "old_rod_encounters": [
            water_slot("SPECIES_MAGIKARP", 8, 15),
            water_slot("SPECIES_MAGIKARP", 10, 16),
            water_slot("SPECIES_BARBOACH", 12, 18),
            water_slot("SPECIES_BARBOACH", 14, 20),
            water_slot("SPECIES_DRATINI", 16, 22),
        ],
        "good_rod_rate": 50,
        "good_rod_encounters": [
            water_slot("SPECIES_MAGIKARP", 20, 28),
            water_slot("SPECIES_BARBOACH", 21, 29),
            water_slot("SPECIES_WHISCASH", 25, 32),
            water_slot("SPECIES_DRATINI", 25, 32),
            water_slot("SPECIES_FEEBAS", 26, 32),
        ],
        "super_rod_rate": 75,
        "super_rod_encounters": [
            water_slot("SPECIES_GYARADOS", 34, 44),
            water_slot("SPECIES_WHISCASH", 34, 44),
            water_slot("SPECIES_DRATINI", 32, 42),
            water_slot("SPECIES_DRAGONAIR", 37, 45),
            water_slot("SPECIES_FEEBAS", 35, 43),
        ],
    })

    # B1F retains its elusive-rod metadata in the upstream JSON because this
    # override does not touch that field. Feebas is also made available through
    # normal fishing so it is not dependent on the six-random-tile mechanic.
    areas["encounters_mt_coronet_b1f"].update({
        "surf_rate": 20,
        "surf_encounters": [
            water_slot("SPECIES_ZUBAT", 28, 34),
            water_slot("SPECIES_GOLBAT", 30, 36),
            water_slot("SPECIES_BARBOACH", 28, 35),
            water_slot("SPECIES_WHISCASH", 31, 37),
            water_slot("SPECIES_FEEBAS", 30, 36),
        ],
        "old_rod_rate": 25,
        "old_rod_encounters": [
            water_slot("SPECIES_MAGIKARP", 8, 15),
            water_slot("SPECIES_MAGIKARP", 10, 16),
            water_slot("SPECIES_BARBOACH", 12, 18),
            water_slot("SPECIES_BARBOACH", 14, 20),
            water_slot("SPECIES_FEEBAS", 16, 22),
        ],
        "good_rod_rate": 50,
        "good_rod_encounters": [
            water_slot("SPECIES_MAGIKARP", 20, 28),
            water_slot("SPECIES_BARBOACH", 21, 29),
            water_slot("SPECIES_WHISCASH", 25, 32),
            water_slot("SPECIES_FEEBAS", 25, 32),
            water_slot("SPECIES_FEEBAS", 27, 34),
        ],
        "super_rod_rate": 75,
        "super_rod_encounters": [
            water_slot("SPECIES_GYARADOS", 34, 44),
            water_slot("SPECIES_WHISCASH", 34, 44),
            water_slot("SPECIES_FEEBAS", 32, 42),
            water_slot("SPECIES_FEEBAS", 35, 44),
            water_slot("SPECIES_FEEBAS", 38, 46),
        ],
    })

    # Validate all species against Mercury's canonical 1025-species runtime.
    supported = load_supported_species(root)
    added = [*IRON_ISLAND_FILES, *MT_CORONET_FILES]
    unresolved = sorted({
        species
        for key in added
        for species in walk_species(areas[key])
        if species not in supported
    })
    if unresolved:
        raise SystemExit(
            "Iron Island / Mt. Coronet output contains unsupported species: "
            + ", ".join(unresolved)
        )

    # Prove the special B1F Feebas resource exists in the Platinum source and
    # that this patch does not replace/delete it.
    b1f_source = json.loads((encounter_dir / "encounters_mt_coronet_b1f.json").read_text())
    elusive = b1f_source.get("elusive_rod_encounter")
    elusive_preserved = (
        isinstance(elusive, dict)
        and elusive.get("species") == "SPECIES_FEEBAS"
        and "elusive_rod_encounter" not in areas["encounters_mt_coronet_b1f"]
    )
    if not elusive_preserved:
        raise SystemExit("Mt. Coronet B1F elusive-rod metadata preservation check failed")

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides: Routes 201-230, Honey Trees, "
        "Great Marsh, Ravaged Path, Old Chateau, Snowpoint Temple, Iron Island, and Mt. Coronet."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05B_IRON_CORONET_1",
        "status": "PASS",
        "resource_count": len(added),
        "resources": added,
        "iron_island_resource_count": len(IRON_ISLAND_FILES),
        "iron_island_land_resource_count": len(iron_tables),
        "mt_coronet_resource_count": len(MT_CORONET_FILES),
        "mt_coronet_1f_south_intentionally_not_reauthored": True,
        "full_tod_area_count_added": len(iron_tables) + len(MT_CORONET_FILES),
        "full_tod_slot_count_added": (len(iron_tables) + len(MT_CORONET_FILES)) * 48,
        "mt_coronet_feebas_regular_fishing": True,
        "mt_coronet_elusive_rod_metadata_preserved": elusive_preserved,
        "regi_ruins_random_encounters_added": False,
        "registeel_iron_ruins_static_reserved": True,
        "regice_iceberg_ruins_static_reserved": True,
        "regirock_rock_peak_ruins_static_reserved": True,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
