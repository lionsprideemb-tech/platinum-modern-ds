#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import struct
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "convert_platinum_landdata.py"
spec = importlib.util.spec_from_file_location("landconv", MODULE)
landconv = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(landconv)

permissions = bytes([0x11, 0x00]) * 1024
buildings = bytes(48)
nsbmd = b"BMD0" + bytes(60)
bdhc = b"BDHC" + bytes(28)
header = struct.pack("<4I", len(permissions), len(buildings), len(nsbmd), len(bdhc))
source = header + permissions + buildings + nsbmd + bdhc

landconv.validate_dppt(source)
converted = landconv.convert(source)
info = landconv.validate_hgss(converted)

assert converted[:0x10] == source[:0x10]
assert converted[0x10:0x14] == landconv.BLANK_HGSS_BGS
assert converted[0x14:] == source[0x10:]
assert info["permissions_offset"] == 0x14
assert converted[info["nsbmd_offset"]:info["nsbmd_offset"]+4] == b"BMD0"
assert len(converted) == len(source) + 4

print("DS03 land-data converter synthetic test: PASS")
