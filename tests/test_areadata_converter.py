#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "convert_platinum_areadata.py"
spec = importlib.util.spec_from_file_location("areaconv", MODULE)
areaconv = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(areaconv)

exterior = {
    "mapPropSet": "prop_model_set_000",
    "mapTextureSet": "map_texture_set_006",
    "lightingSet": "lighting_set_000",
    "dummy": 0,
}
payload, meta = areaconv.convert(
    exterior,
    building_tileset=123,
    map_tileset=45,
    area_type=areaconv.HGSS_AREA_OUTDOOR,
)
assert len(payload) == 8
assert payload == bytes.fromhex("7b002d00ffff0101")
assert meta["platinum_dummy"] == 0
assert meta["hgss_dynamic_texture_type"] == 0xFFFF
assert meta["hgss_area_type"] == 1
assert meta["hgss_light_type"] == 1

interior = {
    "mapPropSet": "prop_model_set_016",
    "mapTextureSet": "map_texture_set_020",
    "lightingSet": "lighting_set_001",
    "dummy": 3,
}
payload, meta = areaconv.convert(
    interior,
    building_tileset=124,
    map_tileset=46,
    area_type=areaconv.HGSS_AREA_INDOOR,
)
assert len(payload) == 8
assert payload == bytes.fromhex("7c002e00ffff0000")
assert meta["platinum_dummy"] == 3
assert meta["hgss_dynamic_texture_type"] == 0xFFFF
assert meta["hgss_area_type"] == 0
assert meta["hgss_light_type"] == 0

print("DS03 area-data converter regression: PASS")

# Lighting archive 2 has no proven direct HGSS mapping.
unsupported = {
    "mapPropSet": "prop_model_set_001",
    "mapTextureSet": "map_texture_set_001",
    "lightingSet": "lighting_set_002",
    "dummy": 0,
}
try:
    areaconv.convert(
        unsupported,
        building_tileset=1,
        map_tileset=1,
        area_type=areaconv.HGSS_AREA_OUTDOOR,
    )
except ValueError:
    pass
else:
    raise AssertionError("Unproven lighting archive 2 should require an explicit mapping")
