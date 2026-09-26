#!/usr/bin/env python3
"""MR05I — Solaceon Ruins Unown-form-safe encounter pass.

All 18 Solaceon Ruins encounter resources already have the correct Platinum
Unown form-table IDs. Mercury's four-period encounter runtime must not flatten
or replace that form-selection logic.

This pass therefore:
- preserves every room's vanilla 12-slot Unown level table;
- copies that same table into Mercury Morning/Day/Evening/Night slots;
- does not override rate_form0..rate_form4 or unown_table;
- verifies the pinned Platinum runtime still contains the dedicated Unown
  table-selection code;
- keeps the Ruins an Unown collection/puzzle location instead of injecting
  unrelated ordinary species.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PERIODS = ("morning", "day", "evening", "night")
SOLACEON_RESOURCES = (
    "encounters_solaceon_ruins_maniac_tunnel_room",
    "encounters_solaceon_ruins_room_2_northeast_dead_end",
    "encounters_solaceon_ruins_room_1_northwest_dead_end",
    "encounters_solaceon_ruins_room_2",
    "encounters_solaceon_ruins_room_1_southeast_dead_end",
    "encounters_solaceon_ruins_room_3",
    "encounters_solaceon_ruins_room_2_southeast_dead_end",
    "encounters_solaceon_ruins_room_6_southeast_dead_end",
    "encounters_solaceon_ruins_room_5_southwest_dead_end",
    "encounters_solaceon_ruins_room_3_northwest_dead_end",
    "encounters_solaceon_ruins_room_3_southwest_dead_end",
    "encounters_solaceon_ruins_room_4",
    "encounters_solaceon_ruins_room_6",
    "encounters_solaceon_ruins_room_5",
    "encounters_solaceon_ruins_room_7",
    "encounters_solaceon_ruins_room_4_southeast_dead_end",
    "encounters_solaceon_ruins_room_6_northwest_dead_end",
    "encounters_solaceon_ruins_room_5_southeast_deadend",
)

PROTECTED_FORM_FIELDS = (
    "rate_form0",
    "rate_form1",
    "rate_form2",
    "rate_form3",
    "rate_form4",
    "unown_table",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def to_mercury_slots(land: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(land) != 12:
        raise SystemExit(f"Solaceon source expected 12 land slots, found {len(land)}")
    out = []
    for i, slot in enumerate(land):
        if slot.get("species") != "SPECIES_UNOWN":
            raise SystemExit(f"Solaceon slot {i} is not Unown: {slot.get('species')!r}")
        level = slot.get("level")
        if not isinstance(level, int) or not 1 <= level <= 100:
            raise SystemExit(f"Solaceon slot {i} has invalid level {level!r}")
        out.append({
            "level_min": level,
            "level_max": level,
            "species": "SPECIES_UNOWN",
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("base_overrides", type=Path)
    ap.add_argument("output_overrides", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05i-solaceon-unown-port.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    output = load_json(args.base_overrides)
    areas = output["areas"]
    encounter_dir = root / "res/field/encounters"

    source_runtime = (root / "src/overlay006/wild_encounters.c").read_text()
    if "WildEncounters_UnownTables" not in source_runtime or "unownTableID" not in source_runtime:
        raise SystemExit("Pinned Platinum Unown form-selection runtime is missing")

    table_ids: dict[str, int] = {}
    protected_snapshots: dict[str, dict[str, int]] = {}

    for resource in SOLACEON_RESOURCES:
        path = encounter_dir / f"{resource}.json"
        if not path.is_file():
            raise SystemExit(f"Missing Solaceon encounter resource: {resource}")

        source = load_json(path)
        if source.get("land_rate") != 10:
            raise SystemExit(f"{resource}: unexpected land rate {source.get('land_rate')!r}")

        protected = {}
        for field in PROTECTED_FORM_FIELDS:
            value = source.get(field)
            if not isinstance(value, int):
                raise SystemExit(f"{resource}: protected field {field} missing/non-integer")
            protected[field] = value

        table_id = protected["unown_table"]
        if not 1 <= table_id <= 8:
            raise SystemExit(f"{resource}: unexpected Unown table ID {table_id}")
        table_ids[resource] = table_id
        protected_snapshots[resource] = protected

        slots = to_mercury_slots(source["land_encounters"])
        # Only add Mercury's extra runtime field. Do not put the protected form
        # fields into the override object at all, so framework deep-merge cannot
        # accidentally rewrite them.
        areas[resource] = {
            "mercury_tod_land": {
                period: slots
                for period in PERIODS
            }
        }

    # Coverage sanity: the correct-path F-R-I-E-N-D tables, generic dead-end
    # table, and secret ?/! table all need to remain represented.
    ids = set(table_ids.values())
    if not set(range(1, 9)).issubset(ids):
        raise SystemExit(
            "Solaceon Ruins source does not expose all expected Unown table IDs 1-8: "
            + ", ".join(str(v) for v in sorted(ids))
        )

    # Prove no protected field was inserted into the outgoing patch.
    for resource in SOLACEON_RESOURCES:
        leaked = sorted(set(areas[resource]) & set(PROTECTED_FORM_FIELDS))
        if leaked:
            raise SystemExit(f"{resource}: protected form fields leaked into override: {leaked}")

    output["description"] = (
        "Mercury Redux authored Sinnoh encounter overrides through MR05I, "
        "including all 18 Solaceon Ruins resources with Unown form-table "
        "selection preserved exactly."
    )
    args.output_overrides.write_text(json.dumps(output, indent=2) + "\n")

    report = {
        "gate": "MERCURY_MR05I_SOLACEON_UNOWN_FORM_SAFE",
        "status": "PASS",
        "resource_count": len(SOLACEON_RESOURCES),
        "resources": list(SOLACEON_RESOURCES),
        "full_tod_area_count_added": len(SOLACEON_RESOURCES),
        "full_tod_slot_count_added": len(SOLACEON_RESOURCES) * 48,
        "all_random_species_remain_unown": True,
        "unown_table_ids_preserved": table_ids,
        "unown_table_id_set": sorted(ids),
        "protected_form_fields_untouched": True,
        "vanilla_unown_runtime_detected": True,
        "time_of_day_changes_unown_form_pool": False,
        "solaceon_deep_chamber_lore_preserved_for_story_pass": True,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
