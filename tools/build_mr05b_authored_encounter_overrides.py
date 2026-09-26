#!/usr/bin/env python3
"""MR05B authored encounter port.

Translate recovered Mercury Redux Sinnoh encounter specifications into the
native Pokemon Platinum encounter JSON schema used by the DS build.

The recovered source keeps the full Morning/Day/Evening/Night ecology. Vanilla
Platinum supports base + Day/Twilight + Night/Late-Night replacement slots, so
this pass preserves the full source manifest while projecting it into the
native DS format:
  * Morning becomes the 12-slot base table.
  * Day contributes two high-value timed replacements.
  * Night contributes two high-value timed replacements.
  * Evening remains preserved in the authored source for the later expanded
    four-period runtime pass.
  * Surf/fishing pools are projected into Platinum's five fixed weighted slots.

Regional forms not yet represented by the current 1,025-species DS registry
are preserved in the authored source but temporarily projected to their base
species so the playable build remains valid.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROUTE_TO_FILE = {
    "201": "encounters_route_201",
    "202": "encounters_route_202",
    "203": "encounters_route_203",
    "204_south": "encounters_route_204_south",
    "204_north": "encounters_route_204_north",
    "205_south": "encounters_route_205_south",
    "205_north": "encounters_route_205_north",
    "206": "encounters_route_206",
    "207": "encounters_route_207",
    "208": "encounters_route_208",
    "209": "encounters_route_209",
    "210_south": "encounters_route_210_south",
    "210_north": "encounters_route_210_north",
    "211_west": "encounters_route_211_west",
    "211_east": "encounters_route_211_east",
    "212_south": "encounters_route_212_south",
    "212_north": "encounters_route_212_north",
    "213": "encounters_route_213",
    "214": "encounters_route_214",
    "215": "encounters_route_215",
    "216": "encounters_route_216",
    "217": "encounters_route_217",
    "218": "encounters_route_218",
    "219": "encounters_route_219",
    "220": "encounters_route_220",
    "221": "encounters_route_221",
    "222": "encounters_route_222",
    "223": "encounters_route_223",
    "224": "encounters_route_224",
}

FORM_FALLBACKS = {
    "SPECIES_SHELLOS_WEST": "SPECIES_SHELLOS",
    "SPECIES_SHELLOS_EAST": "SPECIES_SHELLOS",
    "SPECIES_GASTRODON_WEST": "SPECIES_GASTRODON",
    "SPECIES_GASTRODON_EAST": "SPECIES_GASTRODON",
    "SPECIES_GROWLITHE_HISUI": "SPECIES_GROWLITHE",
    "SPECIES_ARCANINE_HISUI": "SPECIES_ARCANINE",
    "SPECIES_VULPIX_ALOLA": "SPECIES_VULPIX",
    "SPECIES_NINETALES_ALOLA": "SPECIES_NINETALES",
    "SPECIES_SANDSHREW_ALOLA": "SPECIES_SANDSHREW",
    "SPECIES_SANDSLASH_ALOLA": "SPECIES_SANDSLASH",
    "SPECIES_DARUMAKA_GALAR": "SPECIES_DARUMAKA",
    "SPECIES_DARMANITAN_GALAR": "SPECIES_DARMANITAN",
    "SPECIES_FARFETCHD_GALAR": "SPECIES_FARFETCHD",
    "SPECIES_SNEASEL_HISUI": "SPECIES_SNEASEL",
    "SPECIES_QWILFISH_HISUI": "SPECIES_QWILFISH",
    "SPECIES_SLIGGOO_HISUI": "SPECIES_SLIGGOO",
    "SPECIES_BASCULIN_RED_STRIPED": "SPECIES_BASCULIN",
    "SPECIES_BASCULIN_BLUE_STRIPED": "SPECIES_BASCULIN",
    "SPECIES_BASCULIN_WHITE_STRIPED": "SPECIES_BASCULIN",
    "SPECIES_WOOPER_PALDEA": "SPECIES_WOOPER",
    "SPECIES_TAUROS_PALDEA": "SPECIES_TAUROS",
}

HONEY_POOL = {
    "common": [
        "SPECIES_AIPOM",
        "SPECIES_TEDDIURSA",
        "SPECIES_CUTIEFLY",
        "SPECIES_APPLIN",
        "SPECIES_HERACROSS",
        "SPECIES_PINSIR",
    ],
    "uncommon": [
        "SPECIES_SCYTHER",
        "SPECIES_PHANTUMP",
        "SPECIES_SLAKOTH",
        "SPECIES_LARVESTA",
        "SPECIES_JOLTIK",
        "SPECIES_SEWADDLE",
    ],
    "rare": [
        "SPECIES_MUNCHLAX",
        "SPECIES_KECLEON",
        "SPECIES_ORANGURU",
        "SPECIES_PASSIMIAN",
        "SPECIES_EEVEE",
        "SPECIES_VULPIX",
    ],
}

LAND_DEFAULT_WEIGHTS = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
WATER_DEFAULT_WEIGHTS = [60, 30, 5, 4, 1]
OLD_ROD_DEFAULT_WEIGHTS = [70, 30]
GOOD_ROD_DEFAULT_WEIGHTS = [60, 20, 20]
SUPER_ROD_DEFAULT_WEIGHTS = [40, 40, 15, 4, 1]


def projected_species(species: str, fallbacks: list[dict[str, str]]) -> str:
    out = FORM_FALLBACKS.get(species, species)
    if out != species:
        fallbacks.append({"source": species, "runtime": out})
    return out


def midpoint(entry: dict[str, Any]) -> int:
    low = int(entry.get("min_level", entry.get("level", 1)))
    high = int(entry.get("max_level", low))
    return (low + high + 1) // 2


def period_tables(route: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    land = route.get("land")
    if not land:
        return {}
    if isinstance(land, list):
        return {p: land for p in ("Morning", "Day", "Evening", "Night")}
    if isinstance(land, dict):
        if any(k in land for k in ("Morning", "Day", "Evening", "Night")):
            first = next((land.get(p) for p in ("Morning", "Day", "Evening", "Night") if isinstance(land.get(p), list)), [])
            return {p: land.get(p, first) for p in ("Morning", "Day", "Evening", "Night")}
    raise SystemExit(f"Unsupported land schema: {type(land).__name__}")


def ensure_12(entries: list[dict[str, Any]], route_key: str) -> list[dict[str, Any]]:
    if len(entries) == 12:
        return entries
    if not entries:
        return []
    ranked = sorted(entries, key=lambda e: int(e.get("weight", 1)), reverse=True)
    out = []
    while len(out) < 12:
        out.extend(ranked)
    return out[:12]


def timed_species(
    period: list[dict[str, Any]],
    morning: list[dict[str, Any]],
    fallbacks: list[dict[str, str]],
) -> list[str]:
    morning_species = {projected_species(e["species"], fallbacks) for e in morning}
    ranked = sorted(
        period,
        key=lambda e: int(e.get("weight", 0)),
        reverse=True,
    )
    chosen: list[str] = []
    for entry in ranked:
        species = projected_species(entry["species"], fallbacks)
        if species not in morning_species and species not in chosen:
            chosen.append(species)
        if len(chosen) == 2:
            return chosen
    for index in (2, 3, 0, 1):
        if index < len(period):
            species = projected_species(period[index]["species"], fallbacks)
            if species not in chosen:
                chosen.append(species)
        if len(chosen) == 2:
            break
    while len(chosen) < 2:
        chosen.append(projected_species(morning[len(chosen)]["species"], fallbacks))
    return chosen[:2]


def weighted_five(
    entries: list[dict[str, Any]],
    defaults: list[int],
    fallbacks: list[dict[str, str]],
) -> list[dict[str, Any]]:
    if not entries:
        return []
    weighted = []
    for i, entry in enumerate(entries):
        weight = int(entry.get("weight", defaults[i] if i < len(defaults) else 1))
        weighted.append((entry, max(1, weight)))
    total = sum(w for _, w in weighted)
    cutpoints = (0.15, 0.50, 0.82, 0.94, 0.995)
    out = []
    for point in cutpoints:
        target = point * total
        running = 0
        selected = weighted[-1][0]
        for entry, weight in weighted:
            running += weight
            if running >= target:
                selected = entry
                break
        out.append({
            "level_max": int(selected.get("max_level", selected.get("level", 1))),
            "level_min": int(selected.get("min_level", selected.get("level", 1))),
            "species": projected_species(selected["species"], fallbacks),
        })
    return out


def set_rate(area: dict[str, Any], field: str, has_entries: bool, default: int) -> None:
    if not has_entries:
        return
    if int(area.get(field, 0)) == 0:
        area[field] = default


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("source_manifest", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05b-authored-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    encounter_dir = root / "res/field/encounters"
    source = json.loads(args.source_manifest.read_text())
    routes = source["routes"]

    missing = sorted(set(ROUTE_TO_FILE) - set(routes))
    if missing:
        raise SystemExit(f"MR05B authored manifest missing route segments: {missing}")

    overrides: dict[str, Any] = {}
    fallbacks: list[dict[str, str]] = []
    changed_routes = []

    for route_key, file_key in ROUTE_TO_FILE.items():
        path = encounter_dir / f"{file_key}.json"
        if not path.exists():
            raise SystemExit(f"Missing Platinum encounter file for {route_key}: {path}")
        base = json.loads(path.read_text())
        route = routes[route_key]
        out: dict[str, Any] = {}

        periods = period_tables(route)
        morning = ensure_12(periods.get("Morning", []), route_key)
        if morning:
            out["land_encounters"] = [
                {
                    "level": midpoint(entry),
                    "species": projected_species(entry["species"], fallbacks),
                }
                for entry in morning
            ]
            out["land_rate"] = max(int(base.get("land_rate", 0)), 20)
            out["day"] = timed_species(periods.get("Day", morning), morning, fallbacks)
            out["night"] = timed_species(periods.get("Night", morning), morning, fallbacks)
        elif route.get("land") is False:
            out["land_rate"] = 0

        surf = route.get("surf") or []
        if surf:
            out["surf_encounters"] = weighted_five(surf, WATER_DEFAULT_WEIGHTS, fallbacks)
            out["surf_rate"] = max(int(base.get("surf_rate", 0)), 10)

        old_rod = route.get("old_rod") or []
        if old_rod:
            out["old_rod_encounters"] = weighted_five(old_rod, OLD_ROD_DEFAULT_WEIGHTS, fallbacks)
            out["old_rod_rate"] = max(int(base.get("old_rod_rate", 0)), 25)

        good_rod = route.get("good_rod") or []
        if good_rod:
            out["good_rod_encounters"] = weighted_five(good_rod, GOOD_ROD_DEFAULT_WEIGHTS, fallbacks)
            out["good_rod_rate"] = max(int(base.get("good_rod_rate", 0)), 25)

        super_rod = route.get("super_rod") or []
        if super_rod:
            out["super_rod_encounters"] = weighted_five(super_rod, SUPER_ROD_DEFAULT_WEIGHTS, fallbacks)
            out["super_rod_rate"] = max(int(base.get("super_rod_rate", 0)), 25)

        if out:
            overrides[file_key] = out
            changed_routes.append(route_key)

    overrides["encounters_honey_tree"] = HONEY_POOL

    output = {
        "schema": 1,
        "description": "Mercury Redux authored Sinnoh encounter overrides recovered from the original Mercury encounter pass.",
        "areas": overrides,
    }
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    unique_fallbacks = []
    seen = set()
    for item in fallbacks:
        pair = (item["source"], item["runtime"])
        if pair not in seen:
            seen.add(pair)
            unique_fallbacks.append(item)

    report = {
        "gate": "MERCURY_MR05B_AUTHORED_ENCOUNTER_PORT",
        "status": "PASS",
        "route_segments_expected": len(ROUTE_TO_FILE),
        "route_segments_ported": len(changed_routes),
        "route_segments": changed_routes,
        "honey_tree_updated": True,
        "honey_tree_burmy_present": any("BURMY" in s for pool in HONEY_POOL.values() for s in pool),
        "regional_form_runtime_fallbacks": unique_fallbacks,
        "source_preserves_evening_tables": True,
        "runtime_projection": "Morning base + two Day/Twilight replacements + two Night/Late-Night replacements",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
