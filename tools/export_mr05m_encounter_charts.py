#!/usr/bin/env python3
"""MR05M — compile the final Mercury encounter tables into player-facing charts.

This is a presentation/indexing pass over the already-installed encounter
manifest. It does not modify encounter balance. It produces one structured
location chart, one reverse species-to-locations index, one readable Markdown
chart, and one machine-checkable report.

The 25 orphan encounters_unknown_533 through encounters_unknown_557 members
proven unreachable by MR05L are deliberately excluded from the player chart.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

PERIODS = ("morning", "day", "evening", "night")
LAND_WEIGHTS = (20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1)
UNKNOWN_NAMES = {f"encounters_unknown_{n}" for n in range(533, 558)}
LOOKOUT = "encounters_great_marsh_lookout"
HONEY = "encounters_honey_tree"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def humanize_resource(name: str) -> str:
    value = name.removeprefix("encounters_")
    words = value.split("_")
    out = []
    for word in words:
        low = word.lower()
        if re.fullmatch(r"\d+f", low):
            out.append(low[:-1] + "F")
        elif re.fullmatch(r"b\d+f", low):
            out.append("B" + low[1:-1] + "F")
        elif low == "mt":
            out.append("Mt.")
        elif low == "pokemon":
            out.append("Pokémon")
        else:
            out.append(word.capitalize())
    return " ".join(out)


def species_name(token: str) -> str:
    if not token.startswith("SPECIES_"):
        return token
    return token.removeprefix("SPECIES_").replace("_", " ").title()


def normalize_slot(slot: Any) -> dict[str, Any] | None:
    if isinstance(slot, str):
        if slot.startswith("SPECIES_") and slot != "SPECIES_NONE":
            return {"species": slot}
        return None
    if not isinstance(slot, dict):
        return None
    species = slot.get("species")
    if not isinstance(species, str) or not species.startswith("SPECIES_") or species == "SPECIES_NONE":
        return None
    out: dict[str, Any] = {"species": species}
    if isinstance(slot.get("level"), int):
        out["level_min"] = slot["level"]
        out["level_max"] = slot["level"]
    else:
        low = slot.get("level_min")
        high = slot.get("level_max")
        if isinstance(low, int):
            out["level_min"] = low
        if isinstance(high, int):
            out["level_max"] = high
    return out


def map_resource_metadata(text: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = defaultdict(lambda: {"map_headers": [], "map_labels": []})
    block_re = re.compile(r"\[(MAP_HEADER_[A-Z0-9_]+)\]\s*=\s*\{(.*?)\n    \},", re.S)
    for match in block_re.finditer(text):
        header = match.group(1)
        block = match.group(2)
        wild = re.search(r"\.wildEncountersArchiveID\s*=\s*(encounters_[A-Za-z0-9_]+),", block)
        if not wild:
            continue
        resource = wild.group(1)
        label = re.search(r"\.mapLabelTextID\s*=\s*([^,]+),", block)
        row = result[resource]
        if header not in row["map_headers"]:
            row["map_headers"].append(header)
        if label:
            token = label.group(1).strip()
            if token not in row["map_labels"]:
                row["map_labels"].append(token)
    return dict(result)


def append_method(methods: list[dict[str, Any]], label: str, slots: Any, **meta: Any) -> None:
    if not isinstance(slots, list):
        return
    normalized = [s for raw in slots if (s := normalize_slot(raw)) is not None]
    if not normalized:
        return
    entry = {"method": label, "slots": normalized}
    entry.update(meta)
    methods.append(entry)


def build_methods(name: str, area: dict[str, Any]) -> list[dict[str, Any]]:
    methods: list[dict[str, Any]] = []

    if name == HONEY:
        for tier in ("common", "uncommon", "rare"):
            append_method(methods, f"Honey Tree — {tier.title()}", area.get(tier), tier=tier)
        return methods

    if name == LOOKOUT:
        append_method(methods, "Great Marsh Binoculars — Before National Dex", area.get("before_national_dex"), informational=True)
        append_method(methods, "Great Marsh Binoculars — After National Dex", area.get("after_national_dex"), informational=True)
        return methods

    tod = area.get("mercury_tod_land")
    if isinstance(tod, dict):
        for period in PERIODS:
            slots = tod.get(period)
            if not isinstance(slots, list):
                continue
            normalized = []
            for i, raw in enumerate(slots):
                slot = normalize_slot(raw)
                if slot is None:
                    continue
                if i < len(LAND_WEIGHTS):
                    slot["slot_weight_percent"] = LAND_WEIGHTS[i]
                normalized.append(slot)
            if normalized:
                methods.append({
                    "method": f"Land — {period.title()}",
                    "period": period,
                    "slots": normalized,
                })
    elif int(area.get("land_rate", 0) or 0) > 0:
        slots = area.get("land_encounters")
        if isinstance(slots, list):
            normalized = []
            for i, raw in enumerate(slots):
                slot = normalize_slot(raw)
                if slot is None:
                    continue
                if i < len(LAND_WEIGHTS):
                    slot["slot_weight_percent"] = LAND_WEIGHTS[i]
                normalized.append(slot)
            if normalized:
                methods.append({"method": "Land", "slots": normalized})

    for label, rate_key, slots_key in (
        ("Surf", "surf_rate", "surf_encounters"),
        ("Old Rod", "old_rod_rate", "old_rod_encounters"),
        ("Good Rod", "good_rod_rate", "good_rod_encounters"),
        ("Super Rod", "super_rod_rate", "super_rod_encounters"),
    ):
        rate = int(area.get(rate_key, 0) or 0)
        if rate > 0:
            append_method(methods, label, area.get(slots_key), encounter_rate=rate)

    elusive = area.get("elusive_rod_encounter")
    if isinstance(elusive, dict):
        slot = normalize_slot(elusive)
        if slot:
            methods.append({"method": "Special Fishing", "slots": [slot], "special": True})

    return methods


def add_reverse_index(reverse, resource: str, display_name: str, methods: list[dict[str, Any]]) -> None:
    seen = set()
    for method in methods:
        for slot in method["slots"]:
            species = slot["species"]
            key = (species, resource, method["method"], slot.get("level_min"), slot.get("level_max"))
            if key in seen:
                continue
            seen.add(key)
            reverse[species].append({
                "resource": resource,
                "area": display_name,
                "method": method["method"],
                "level_min": slot.get("level_min"),
                "level_max": slot.get("level_max"),
            })


def compact_species(method: dict[str, Any]) -> str:
    parts = []
    seen = set()
    for slot in method["slots"]:
        species = slot["species"]
        low = slot.get("level_min")
        high = slot.get("level_max")
        key = (species, low, high)
        if key in seen:
            continue
        seen.add(key)
        label = species_name(species)
        if isinstance(low, int) and isinstance(high, int):
            label += f" Lv{low}" if low == high else f" Lv{low}-{high}"
        parts.append(label)
    return ", ".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("mr05l_audit", type=Path)
    ap.add_argument("--output-dir", type=Path, default=Path("encounter-chart"))
    ap.add_argument("--report", type=Path, default=Path("mr05m-encounter-chart-report.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    manifest = load_json(args.manifest)
    audit = load_json(args.mr05l_audit)

    if manifest.get("schema") != 1 or manifest.get("area_count") != 185:
        raise SystemExit("MR05M requires the final 185-resource encounter manifest")
    if audit.get("status") != "PASS" or audit.get("runtime_active_unknown_resources") != 0:
        raise SystemExit("MR05M requires a passing MR05L orphan-resource audit")

    areas = manifest.get("areas")
    if not isinstance(areas, dict) or len(areas) != 185:
        raise SystemExit("MR05M encounter manifest areas object is incomplete")

    map_meta = map_resource_metadata((root / "include/data/map_headers.h").read_text())
    active_names = sorted(set(areas) - UNKNOWN_NAMES)
    if len(active_names) != 160:
        raise SystemExit(f"Expected 160 player-facing/informational resources, found {len(active_names)}")

    output_rows = []
    reverse = defaultdict(list)
    full_tod_count = 0
    full_tod_slots = 0
    route_numbers = set()
    great_marsh_biomes = set()

    for name in active_names:
        area = areas[name]
        if "mercury_tod_land" in area:
            full_tod_count += 1
            full_tod_slots += sum(len(area["mercury_tod_land"].get(period, [])) for period in PERIODS)

        match = re.match(r"encounters_route_(\d+)", name)
        if match:
            route_numbers.add(int(match.group(1)))
        if re.match(r"encounters_great_marsh_\d+$", name):
            great_marsh_biomes.add(name)

        methods = build_methods(name, area)
        meta = map_meta.get(name, {"map_headers": [], "map_labels": []})
        display = humanize_resource(name)
        row = {
            "resource": name,
            "display_name": display,
            "map_headers": meta["map_headers"],
            "map_labels": meta["map_labels"],
            "informational_only": name == LOOKOUT,
            "methods": methods,
        }
        if name == HONEY:
            row["mercury_mechanics"] = {
                "honey_cost": 1,
                "instant_encounter": True,
                "cooldown": False,
                "special_tree_lottery": False,
                "tier_distribution_percent": {
                    "common": 70,
                    "uncommon": 20,
                    "rare": 10,
                },
            }
        output_rows.append(row)
        add_reverse_index(reverse, name, display, methods)

    if full_tod_count != 144 or full_tod_slots != 6912:
        raise SystemExit(f"Runtime chart mismatch: {full_tod_count} TOD areas / {full_tod_slots} slots")
    if route_numbers != set(range(201, 231)):
        missing = sorted(set(range(201, 231)) - route_numbers)
        raise SystemExit("Route 201-230 coverage incomplete: " + ", ".join(map(str, missing)))
    if len(great_marsh_biomes) != 6:
        raise SystemExit(f"Expected 6 Great Marsh biomes, found {len(great_marsh_biomes)}")

    honey = areas.get(HONEY)
    if not isinstance(honey, dict):
        raise SystemExit("Honey Tree resource missing")
    honey_species = {
        species
        for tier in ("common", "uncommon", "rare")
        for species in honey.get(tier, [])
        if isinstance(species, str)
    }
    if "SPECIES_BURMY" in honey_species:
        raise SystemExit("Burmy reappeared in Mercury Honey Tree pools")

    chart = {
        "schema": 1,
        "project": "Pokemon Mercury Redux",
        "phase": "MR05M",
        "source_manifest_sha256": manifest.get("dataset_sha256"),
        "resource_count": len(output_rows),
        "full_tod_area_count": full_tod_count,
        "full_tod_slot_count": full_tod_slots,
        "orphan_resources_excluded": sorted(UNKNOWN_NAMES),
        "areas": output_rows,
    }
    index = {
        "schema": 1,
        "project": "Pokemon Mercury Redux",
        "phase": "MR05M",
        "species_count": len(reverse),
        "species": {
            species: {
                "display_name": species_name(species),
                "locations": sorted(locations, key=lambda x: (x["area"], x["method"], x.get("level_min") or 0)),
            }
            for species, locations in sorted(reverse.items())
        },
    }

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "mercury_encounter_chart.json").write_text(json.dumps(chart, indent=2) + "\n")
    (out / "mercury_species_location_index.json").write_text(json.dumps(index, indent=2) + "\n")

    md = [
        "# Pokémon Mercury Redux — Encounter Chart",
        "",
        f"Generated from the final MR05M manifest. **{len(output_rows)}** player-facing/informational resources; "
        f"**{full_tod_count}** full four-period land areas; **{full_tod_slots:,}** Morning/Day/Evening/Night slots.",
        "",
        "The 25 encounters_unknown_533 through encounters_unknown_557 archive remnants are omitted because MR05L proved they are not runtime-addressable.",
        "",
    ]
    for row in output_rows:
        if not row["methods"]:
            continue
        md.append(f"## {row['display_name']}")
        if row["informational_only"]:
            md.append("_Informational resource; it does not gate encounter availability._")
        for method in row["methods"]:
            compact = compact_species(method)
            if compact:
                md.append(f"- **{method['method']}**: {compact}")
        md.append("")
    (out / "mercury_encounter_chart.md").write_text("\n".join(md) + "\n")

    report = {
        "gate": "MERCURY_MR05M_ENCOUNTER_CHART_EXPORT",
        "status": "PASS",
        "manifest_area_count": len(areas),
        "chart_resource_count": len(output_rows),
        "orphan_resources_excluded_count": len(UNKNOWN_NAMES),
        "full_tod_area_count": full_tod_count,
        "full_tod_slot_count": full_tod_slots,
        "route_number_count_201_230": len(route_numbers),
        "routes_201_230_complete": route_numbers == set(range(201, 231)),
        "great_marsh_biome_count": len(great_marsh_biomes),
        "great_marsh_all_six_biomes_present": len(great_marsh_biomes) == 6,
        "honey_tree_present": HONEY in areas,
        "honey_tree_burmy_removed": "SPECIES_BURMY" not in honey_species,
        "great_marsh_lookout_informational": LOOKOUT in active_names,
        "species_location_index_count": len(reverse),
        "player_chart_json": str(out / "mercury_encounter_chart.json"),
        "species_location_index_json": str(out / "mercury_species_location_index.json"),
        "player_chart_markdown": str(out / "mercury_encounter_chart.md"),
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
