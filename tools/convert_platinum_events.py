#!/usr/bin/env python3
"""Convert pokeplatinum event JSON into pokeheartgold-style zone-event JSON.

This tool converts structure, not game-specific IDs. Symbol remapping is supplied
through an optional mapping JSON so every non-identical sprite/flag/map/script
identifier remains explicit and auditable.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def mapped(value, table):
    if isinstance(value, str):
        return table.get(value, value)
    return value


def script_id(value, mappings):
    return mapped(value, mappings.get("scripts", {}))


def convert(src: dict, mappings: dict, header: str) -> dict:
    out = {"header": header}

    if src.get("bg_events"):
        out["bgs"] = []
        for e in src["bg_events"]:
            out["bgs"].append({
                "scriptId": script_id(e["script"], mappings),
                "type": e["type"],
                "x": e["x"],
                "z": e["z"],
                "y": e["y"],
                "dir": mapped(e["player_facing_dir"], mappings.get("bg_directions", {})),
            })

    if src.get("object_events"):
        out["objects"] = []
        for e in src["object_events"]:
            data = list(e.get("data", []))[:3]
            data += [0] * (3 - len(data))
            out["objects"].append({
                "id": mapped(e["id"], mappings.get("object_ids", {})),
                "spriteId": mapped(e["graphics_id"], mappings.get("sprites", {})),
                "movement": mapped(e["movement_type"], mappings.get("movement", {})),
                "type": mapped(e["trainer_type"], mappings.get("object_types", {})),
                "eventFlag": mapped(e["hidden_flag"], mappings.get("flags", {})),
                "scriptId": script_id(e["script"], mappings),
                "facingDirection": mapped(e["initial_dir"], mappings.get("directions", {})),
                "param0": data[0],
                "param1": data[1],
                "param2": data[2],
                "xRange": e["movement_range_x"],
                "yRange": e["movement_range_z"],
                "x": e["x"],
                "z": e["z"],
                "y": e["y"],
            })

    if src.get("warp_events"):
        out["warps"] = []
        for e in src["warp_events"]:
            out["warps"].append({
                "x": e["x"],
                "z": e["z"],
                "header": mapped(e["dest_header_id"], mappings.get("maps", {})),
                "anchor": e["dest_warp_id"],
                "y": 0,
            })

    if src.get("coord_events"):
        out["coords"] = []
        for e in src["coord_events"]:
            out["coords"].append({
                "scriptId": script_id(e["script"], mappings),
                "x": e["x"],
                "z": e["z"],
                "w": e["width"],
                "h": e["length"],
                "y": e["y"],
                "val": e["value"],
                "var": mapped(e["var"], mappings.get("vars", {})),
            })

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--mapping", type=Path)
    ap.add_argument("--header", required=True)
    args = ap.parse_args()

    src = json.loads(args.input.read_text(encoding="utf-8"))
    mappings = {}
    if args.mapping:
        mappings = json.loads(args.mapping.read_text(encoding="utf-8"))

    out = convert(src, mappings, args.header)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
