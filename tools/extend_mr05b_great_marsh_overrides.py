#!/usr/bin/env python3
"""Extend MR05B authored overrides with the six Mercury Great Marsh biomes.

Source: recovered cumulative Mercury GBA runtime tables. Each Great Marsh area
has four complete 12-slot land tables plus time-invariant Surf/fishing pools.
The Mercury TOD runtime bypasses Platinum's daily Great Marsh replacement for
areas carrying mercury_tod_land, so daily RNG no longer gates availability.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

AREA_TO_FILE = {
    1: "encounters_great_marsh_1",
    2: "encounters_great_marsh_2",
    3: "encounters_great_marsh_3",
    4: "encounters_great_marsh_4",
    5: "encounters_great_marsh_5",
    6: "encounters_great_marsh_6",
}

PERIOD_MAP = {
    "Morning": "morning",
    "Day": "day",
    "Evening": "evening",
    "Night": "night",
}

FORM_FALLBACKS = {
    "SPECIES_GRIMER_ALOLA": "SPECIES_GRIMER",
    "SPECIES_ORICORIO_PAU": "SPECIES_ORICORIO",
    "SPECIES_SHELLOS_EAST": "SPECIES_SHELLOS",
    "SPECIES_SLOWPOKE_GALAR": "SPECIES_SLOWPOKE",
    "SPECIES_STUNFISK_GALAR": "SPECIES_STUNFISK",
    "SPECIES_WOOPER_PALDEA": "SPECIES_WOOPER",
}

OLD_ROD_WEIGHTS = [70, 30]
GOOD_ROD_WEIGHTS = [60, 20, 20]


def load_supported_species(root: Path) -> set[str]:
    path = root / "generated/species.txt"
    if not path.exists():
        raise SystemExit(f"Expected generated species registry at {path}")
    return {
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip().startswith("SPECIES_")
    }


def project_species(token: str, fallbacks: list[dict[str, str]]) -> str:
    out = FORM_FALLBACKS.get(token, token)
    if out != token:
        pair = {"source": token, "runtime": out}
        if pair not in fallbacks:
            fallbacks.append(pair)
    return out


def midpoint(entry: dict[str, Any]) -> int:
    lo = int(entry["min_level"])
    hi = int(entry["max_level"])
    return (lo + hi + 1) // 2


def slot(entry: dict[str, Any], fallbacks: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "level_max": int(entry["max_level"]),
        "level_min": int(entry["min_level"]),
        "species": project_species(entry["species"], fallbacks),
    }


def expand_to_five(
    entries: list[dict[str, Any]],
    weights: list[int],
    fallbacks: list[dict[str, str]],
) -> list[dict[str, Any]]:
    if len(entries) == 5:
        return [slot(e, fallbacks) for e in entries]
    if len(entries) != len(weights):
        raise SystemExit(f"Expected {len(weights)} fishing entries, found {len(entries)}")

    weighted = list(zip(entries, weights))
    total = sum(weights)
    cutpoints = (0.15, 0.50, 0.82, 0.94, 0.995)
    out = []
    for point in cutpoints:
        target = point * total
        running = 0
        chosen = entries[-1]
        for entry, weight in weighted:
            running += weight
            if running >= target:
                chosen = entry
                break
        out.append(slot(chosen, fallbacks))
    return out


def timed_species(
    period: list[dict[str, Any]],
    morning: list[dict[str, Any]],
    fallbacks: list[dict[str, str]],
) -> list[str]:
    morning_species = {project_species(e["species"], fallbacks) for e in morning}
    chosen: list[str] = []
    for entry in period:
        species = project_species(entry["species"], fallbacks)
        if species not in morning_species and species not in chosen:
            chosen.append(species)
        if len(chosen) == 2:
            return chosen
    for entry in period:
        species = project_species(entry["species"], fallbacks)
        if species not in chosen:
            chosen.append(species)
        if len(chosen) == 2:
            break
    while len(chosen) < 2:
        chosen.append(project_species(morning[len(chosen)]["species"], fallbacks))
    return chosen[:2]


def walk_species(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_species(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_species(child)
    elif isinstance(value, str) and value.startswith("SPECIES_"):
        yield value


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("legacy_runtime", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05b-great-marsh-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    source = json.loads(args.legacy_runtime.read_text())
    output = json.loads(args.base_overrides.read_text())

    if output.get("schema") != 1 or not isinstance(output.get("areas"), dict):
        raise SystemExit("Base MR05B overrides must use schema 1 with an areas object")

    records = {}
    pattern = re.compile(r"^gGreatMarshArea([1-6])_(Morning|Day|Evening|Night)$")
    for encounter in source.get("encounters", []):
        match = pattern.match(encounter.get("base_label", ""))
        if not match:
            continue
        area = int(match.group(1))
        period = match.group(2)
        records[(area, period)] = encounter

    expected = {(a, p) for a in AREA_TO_FILE for p in PERIOD_MAP}
    missing = sorted(expected - set(records))
    if missing:
        raise SystemExit(f"Missing recovered Great Marsh tables: {missing}")

    supported = load_supported_species(root)
    fallbacks: list[dict[str, str]] = []
    added = []

    for area, file_key in AREA_TO_FILE.items():
        periods = {p: records[(area, p)] for p in PERIOD_MAP}
        morning = periods["Morning"]["land_mons"]["mons"]
        if len(morning) != 12:
            raise SystemExit(f"Great Marsh area {area} morning table is not 12 slots")

        patch: dict[str, Any] = {
            "land_rate": int(periods["Morning"]["land_mons"].get("encounter_rate", 25)),
            "land_encounters": [
                {
                    "level": midpoint(entry),
                    "species": project_species(entry["species"], fallbacks),
                }
                for entry in morning
            ],
            "day": timed_species(periods["Day"]["land_mons"]["mons"], morning, fallbacks),
            "night": timed_species(periods["Night"]["land_mons"]["mons"], morning, fallbacks),
            "mercury_tod_land": {},
        }

        for source_period, runtime_period in PERIOD_MAP.items():
            land = periods[source_period]["land_mons"]["mons"]
            if len(land) != 12:
                raise SystemExit(f"Great Marsh area {area} {source_period} table is not 12 slots")
            patch["mercury_tod_land"][runtime_period] = [slot(e, fallbacks) for e in land]

        surf = periods["Morning"]["water_mons"]["mons"]
        if len(surf) != 5:
            raise SystemExit(f"Great Marsh area {area} Surf table must contain 5 entries")
        patch["surf_rate"] = int(periods["Morning"]["water_mons"].get("encounter_rate", 10))
        patch["surf_encounters"] = [slot(e, fallbacks) for e in surf]

        fishing = periods["Morning"]["fishing_mons"]["mons"]
        if len(fishing) != 10:
            raise SystemExit(f"Great Marsh area {area} fishing table must contain 10 entries")
        patch["old_rod_rate"] = int(periods["Morning"]["fishing_mons"].get("encounter_rate", 35))
        patch["good_rod_rate"] = patch["old_rod_rate"]
        patch["super_rod_rate"] = patch["old_rod_rate"]
        patch["old_rod_encounters"] = expand_to_five(fishing[0:2], OLD_ROD_WEIGHTS, fallbacks)
        patch["good_rod_encounters"] = expand_to_five(fishing[2:5], GOOD_ROD_WEIGHTS, fallbacks)
        patch["super_rod_encounters"] = expand_to_five(fishing[5:10], [40, 40, 15, 4, 1], fallbacks)

        output["areas"][file_key] = patch
        added.append(file_key)

    unresolved = sorted({
        species
        for key in added
        for species in walk_species(output["areas"][key])
        if species not in supported
    })
    if unresolved:
        raise SystemExit(
            "Great Marsh runtime output contains unsupported species: " + ", ".join(unresolved)
        )

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides: Routes 201-230, "
        "Honey Trees, and six Great Marsh biomes."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05B_GREAT_MARSH",
        "status": "PASS",
        "area_count": 6,
        "areas": added,
        "full_tod_table_count": 24,
        "full_tod_slot_count": 288,
        "surf_table_count": 6,
        "fishing_table_count": 18,
        "daily_rng_gate": False,
        "binoculars_role": "informational preview only",
        "runtime_form_fallbacks": fallbacks,
        "runtime_species_registry_validation": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
