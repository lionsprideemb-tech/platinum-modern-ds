#!/usr/bin/env python3
"""Inventory pinned pokeheartgold world-resource capacity.

Run against a local pokeheartgold checkout. This is read-only.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def numeric_prefixes(path: Path, pattern: str) -> list[int]:
    rx = re.compile(pattern)
    vals: list[int] = []
    for entry in path.iterdir():
        m = rx.match(entry.name)
        if m:
            vals.append(int(m.group(1)))
    return sorted(set(vals))


def parse_narc_file_count(path: Path) -> int:
    """Read NARC FATB/BTAF entry count without external libraries."""
    data = path.read_bytes()
    if len(data) < 0x20 or data[:4] != b"NARC":
        raise ValueError(f"{path} is not a NARC archive")
    # Nintendo NARC section is normally BTAF; some tooling displays reversed tags.
    for tag in (b"BTAF", b"FATB"):
        pos = data.find(tag)
        if pos >= 0:
            if pos + 12 > len(data):
                raise ValueError("Truncated FAT section")
            return int.from_bytes(data[pos + 8:pos + 10], "little")
    raise ValueError("Could not locate NARC FAT section")


def parse_map_id_max(maps_h: str) -> tuple[int, int]:
    max_match = re.search(r"^#define\s+MAP_ID_MAX\s+(\d+)\s*$", maps_h, re.M)
    if not max_match:
        raise ValueError("MAP_ID_MAX not found")
    vals = [
        int(value)
        for name, value in re.findall(
            r"^#define\s+(MAP_[A-Z0-9_]+)\s+(\d+)\b",
            maps_h,
            re.M,
        )
        if name != "MAP_ID_MAX"
    ]
    return max(vals), int(max_match.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pokeheartgold", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("audits/ds03_world_capacity.json"))
    args = ap.parse_args()
    root = args.pokeheartgold.resolve()

    maps_h = (root / "include/constants/maps.h").read_text(encoding="utf-8")
    max_map_define, map_id_max = parse_map_id_max(maps_h)

    matrices = numeric_prefixes(
        root / "files/fielddata/mapmatrix/map_matrix",
        r"map_matrix_(\d{4})(?:_|\.)",
    )
    events = numeric_prefixes(
        root / "files/fielddata/eventdata/zone_event",
        r"(\d{3})_.*\.json$",
    )
    scripts = numeric_prefixes(
        root / "files/fielddata/script/scr_seq",
        r"scr_seq_(\d{4})(?:_|\.)",
    )
    messages = numeric_prefixes(
        root / "files/msgdata/msg",
        r"msg_(\d{4})\.gmm$",
    )

    land_narc = root / "files/a/0/6/5"
    land_count = parse_narc_file_count(land_narc)

    result = {
        "schema": 1,
        "source": "pret/pokeheartgold",
        "map_headers": {
            "largest_defined_id": max_map_define,
            "map_id_max_exclusive": map_id_max,
            "next_append_id": map_id_max,
        },
        "matrices": {
            "count": len(matrices),
            "highest_source_id": max(matrices),
            "next_append_id": max(matrices) + 1,
        },
        "zone_events": {
            "count": len(events),
            "highest_source_id": max(events),
            "next_append_id": max(events) + 1,
        },
        "scripts": {
            "count_of_named_source_ids": len(scripts),
            "highest_source_id": max(scripts),
            "next_append_id": max(scripts) + 1,
        },
        "messages": {
            "count": len(messages),
            "highest_source_id": max(messages),
            "next_append_id": max(messages) + 1,
        },
        "land_data_narc": {
            "path": "files/a/0/6/5",
            "member_count": land_count,
            "highest_member_id": land_count - 1,
            "next_append_id": land_count,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
