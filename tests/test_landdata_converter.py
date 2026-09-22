#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import struct

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "convert_platinum_landdata.py"
spec = importlib.util.spec_from_file_location("landconv", MODULE)
landconv = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(landconv)

permissions = bytes([0x11, 0x00]) * 1024
buildings = bytearray(96)
struct.pack_into("<I", buildings, 0, 10)
struct.pack_into("<I", buildings, 48, 20)
nsbmd = b"BMD0" + bytes(60)
bdhc = b"BDHC" + bytes(28)
header = struct.pack("<4I", len(permissions), len(buildings), len(nsbmd), len(bdhc))
source = header + permissions + bytes(buildings) + nsbmd + bdhc

landconv.validate_dppt(source)
assert landconv.building_model_ids_dppt(source) == [10, 20]

converted = landconv.convert(source, model_map={10: 100, 20: 200})
info = landconv.validate_hgss(converted)

assert converted[:0x10] == source[:0x10]
assert converted[0x10:0x14] == landconv.BLANK_HGSS_BGS
assert info["permissions_offset"] == 0x14
assert converted[info["nsbmd_offset"]:info["nsbmd_offset"]+4] == b"BMD0"
assert len(converted) == len(source) + 4

b = info["buildings_offset"]
assert struct.unpack_from("<I", converted, b)[0] == 100
assert struct.unpack_from("<I", converted, b + 48)[0] == 200

try:
    landconv.convert(source, model_map={10: 100})
except ValueError:
    pass
else:
    raise AssertionError("Missing model mapping should fail closed")

print("DS03 land-data converter synthetic test: PASS")
