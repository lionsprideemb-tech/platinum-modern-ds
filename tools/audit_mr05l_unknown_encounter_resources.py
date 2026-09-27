#!/usr/bin/env python3
"""MR05L — prove encounters_unknown_533..557 are not active encounter maps.

Platinum contains 25 encounter JSON/NARC members named encounters_unknown_533
through encounters_unknown_557. Their similarly numbered map headers are
Turnback Cave cave headers, but those headers explicitly use ENCOUNTERS_NONE.
The normal field loader only reads a wild-encounter NARC member when the map
header says it has wild encounters, so these files are not runtime-addressable
through those map headers.

This is an audit-only phase. It deliberately does NOT attach orphaned tables to
live headers or invent additional encounter maps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def header_block(text: str, header: str) -> str:
    marker = f"[{header}] = {{"
    start = text.find(marker)
    if start < 0:
        raise SystemExit(f"Missing map header block: {header}")
    end = text.find("\n    },", start)
    if end < 0:
        raise SystemExit(f"Unterminated map header block: {header}")
    return text[start:end + 7]


def field(block: str, name: str) -> str:
    match = re.search(rf"\.{re.escape(name)}\s*=\s*([^,]+),", block)
    if not match:
        raise SystemExit(f"Missing .{name} in map header block")
    return match.group(1).strip()


def stable_digest(value: Any) -> str:
    packed = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(packed).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("registry", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05l-unknown-resource-audit.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = load_json(args.registry)
    if registry.get("schema") != 1:
        raise SystemExit("MR05L registry schema must be 1")

    expected = registry["expected_range"]
    first = int(expected["first"])
    last = int(expected["last"])
    numbers = list(range(first, last + 1))
    if len(numbers) != int(expected["count"]) or len(numbers) != 25:
        raise SystemExit("MR05L expected exactly 25 unknown resources")

    map_headers_path = root / "include/data/map_headers.h"
    map_header_c_path = root / "src/map_header.c"
    loader_path = root / "src/map_header_data.c"
    encounter_dir = root / "res/field/encounters"
    encounter_order_path = encounter_dir / "encounters.order"

    headers_text = map_headers_path.read_text()
    map_header_c = map_header_c_path.read_text()
    loader_text = loader_path.read_text()
    encounter_order = encounter_order_path.read_text().splitlines()

    # Prove the normal field path only loads a NARC member when the header
    # advertises wild encounters, and ENCOUNTERS_NONE is the no-data sentinel.
    required_loader_fragments = (
        "if (MapHeader_HasWildEncounters(mapHeaderID))",
        "MapHeader_GetWildEncountersArchiveID(mapHeaderID)",
        "NARC_ReadWholeMemberByIndexPair",
    )
    for fragment in required_loader_fragments:
        if fragment not in loader_text:
            raise SystemExit(f"Wild encounter loader contract changed: missing {fragment!r}")

    if "wildEncountersArchiveID != 65535" not in map_header_c:
        raise SystemExit("MapHeader_HasWildEncounters sentinel contract changed")

    header_rows = []
    file_rows = []
    direct_header_refs = []
    digests = set()

    for n in numbers:
        header_name = f"MAP_HEADER_UNKNOWN_{n}"
        encounter_name = f"encounters_unknown_{n}"
        block = header_block(headers_text, header_name)

        wild = field(block, "wildEncountersArchiveID")
        label = field(block, "mapLabelTextID")
        map_type = field(block, "mapType")
        matrix = field(block, "mapMatrixID")
        events = field(block, "eventsArchiveID")

        if wild != registry["expected_header_properties"]["wildEncountersArchiveID"]:
            raise SystemExit(f"{header_name}: expected ENCOUNTERS_NONE, found {wild}")
        if label != registry["expected_header_properties"]["mapLabelTextID"]:
            raise SystemExit(f"{header_name}: expected Turnback Cave label, found {label}")
        if map_type != registry["expected_header_properties"]["mapType"]:
            raise SystemExit(f"{header_name}: expected cave map type, found {map_type}")

        if f".wildEncountersArchiveID = {encounter_name}," in headers_text:
            direct_header_refs.append(encounter_name)

        path = encounter_dir / f"{encounter_name}.json"
        if not path.is_file():
            raise SystemExit(f"Missing orphan encounter member file: {path.name}")
        data = load_json(path)
        cat = data.get("map_category")
        if not isinstance(cat, dict):
            raise SystemExit(f"{path.name}: missing map_category")
        if cat.get("map_type") != registry["expected_encounter_file_properties"]["map_type"]:
            raise SystemExit(f"{path.name}: unexpected map_category.map_type")
        if int(cat.get("map_number", -1)) != int(registry["expected_encounter_file_properties"]["map_number"]):
            raise SystemExit(f"{path.name}: unexpected map_category.map_number")

        if encounter_name not in encounter_order:
            raise SystemExit(f"{encounter_name}: missing from encounters.order")

        digests.add(stable_digest(data))
        header_rows.append({
            "header": header_name,
            "wild_encounters_archive_id": wild,
            "map_label": label,
            "map_type": map_type,
            "matrix": matrix,
            "events": events,
        })
        file_rows.append({
            "resource": encounter_name,
            "file": path.name,
            "map_category": cat,
        })

    if direct_header_refs:
        raise SystemExit(
            "Unknown encounter members unexpectedly became runtime-addressable: "
            + ", ".join(direct_header_refs)
        )

    # Also guard against references from any *other* map header.
    for n in numbers:
        encounter_name = f"encounters_unknown_{n}"
        refs = headers_text.count(f".wildEncountersArchiveID = {encounter_name},")
        if refs != 0:
            raise SystemExit(f"{encounter_name}: found {refs} live map-header references")

    report = {
        "gate": "MERCURY_MR05L_UNKNOWN_RESOURCE_CLASSIFICATION",
        "status": "PASS",
        "unknown_resource_count": len(numbers),
        "unknown_header_count": len(header_rows),
        "headers_with_encounters_none": sum(
            row["wild_encounters_archive_id"] == "ENCOUNTERS_NONE" for row in header_rows
        ),
        "turnback_cave_labeled_headers": sum(
            row["map_label"] == "LocationNames_Text_TurnbackCave" for row in header_rows
        ),
        "direct_runtime_header_references": 0,
        "runtime_active_unknown_resources": 0,
        "orphaned_encounter_members": len(file_rows),
        "encounter_member_unique_content_digests": len(digests),
        "normal_loader_contract_verified": True,
        "no_table_rewrite_required": True,
        "active_standard_encounter_sweep_complete": True,
        "classification": registry["classification"],
        "headers": header_rows,
        "resources": file_rows,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
