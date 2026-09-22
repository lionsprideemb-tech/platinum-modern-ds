#!/usr/bin/env python3
"""Convert pokeplatinum AreaData JSON to HGSS AreaData bytes.

Platinum (8 bytes):
  u16 mapPropSet
  u16 mapTextureSet
  u16 dummy
  u16 lightingSet

HGSS (8 bytes):
  u16 buildingsTileset
  u16 mapTileset
  u16 dynamicTextureType
  u8  areaType      (0 indoor, 1 outdoor)
  u8  lightType

The Platinum 'dummy' field is NOT copied into HGSS dynamicTextureType because
the fields have different semantics. By default dynamic textures are disabled
with 0xFFFF for the first compatibility build.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path

HGSS_AREA_INDOOR = 0
HGSS_AREA_OUTDOOR = 1
HGSS_DYNAMIC_TEXTURES_DISABLED = 0xFFFF


def numeric_suffix(value: str, field: str) -> int:
    m = re.search(r"_(\d+)$", value)
    if not m:
        raise ValueError(f"{field} has no numeric suffix: {value!r}")
    return int(m.group(1))


def source_values(data: dict) -> dict[str, int]:
    return {
        "platinum_prop_set": numeric_suffix(data["mapPropSet"], "mapPropSet"),
        "platinum_map_texture_set": numeric_suffix(
            data["mapTextureSet"], "mapTextureSet"
        ),
        "platinum_lighting_set": numeric_suffix(data["lightingSet"], "lightingSet"),
        "platinum_dummy": int(data.get("dummy", 0)),
    }


def convert(
    data: dict,
    *,
    building_tileset: int,
    map_tileset: int,
    area_type: int,
    dynamic_texture_type: int = HGSS_DYNAMIC_TEXTURES_DISABLED,
    light_type: int | None = None,
) -> tuple[bytes, dict[str, int]]:
    src = source_values(data)
    if light_type is None:
        light_type = src["platinum_lighting_set"]

    for name, value in {
        "building_tileset": building_tileset,
        "map_tileset": map_tileset,
        "dynamic_texture_type": dynamic_texture_type,
    }.items():
        if not 0 <= value <= 0xFFFF:
            raise ValueError(f"{name} out of u16 range: {value}")

    if area_type not in (HGSS_AREA_INDOOR, HGSS_AREA_OUTDOOR):
        raise ValueError("area_type must be 0 (indoor) or 1 (outdoor)")
    if not 0 <= light_type <= 0xFF:
        raise ValueError(f"light_type out of u8 range: {light_type}")

    result = struct.pack(
        "<HHHBB",
        building_tileset,
        map_tileset,
        dynamic_texture_type,
        area_type,
        light_type,
    )
    assert len(result) == 8

    metadata = {
        **src,
        "hgss_building_tileset": building_tileset,
        "hgss_map_tileset": map_tileset,
        "hgss_dynamic_texture_type": dynamic_texture_type,
        "hgss_area_type": area_type,
        "hgss_light_type": light_type,
    }
    return result, metadata


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="pokeplatinum area_data_XXX.json")
    ap.add_argument("output", type=Path, help="8-byte HGSS AreaData member")
    ap.add_argument("--building-tileset", required=True, type=int)
    ap.add_argument("--map-tileset", required=True, type=int)
    ap.add_argument("--area-type", required=True, choices=("indoor", "outdoor"))
    ap.add_argument("--dynamic-texture-type", type=lambda x: int(x, 0), default=0xFFFF)
    ap.add_argument("--light-type", type=int)
    ap.add_argument("--metadata", type=Path)
    args = ap.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    area_type = HGSS_AREA_INDOOR if args.area_type == "indoor" else HGSS_AREA_OUTDOOR
    payload, metadata = convert(
        data,
        building_tileset=args.building_tileset,
        map_tileset=args.map_tileset,
        area_type=area_type,
        dynamic_texture_type=args.dynamic_texture_type,
        light_type=args.light_type,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)

    if args.metadata:
        args.metadata.parent.mkdir(parents=True, exist_ok=True)
        args.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
