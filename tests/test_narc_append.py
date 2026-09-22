#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import struct
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "narc_append.py"
spec = importlib.util.spec_from_file_location("narcmod", MODULE)
narcmod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(narcmod)

def synthetic(members):
    base = narcmod.Narc(
        header=b"NARC" + bytes.fromhex("feff0001") + b"\0\0\0\0" + struct.pack("<HH", 0x10, 3),
        fat_magic=b"BTAF",
        fat_reserved=b"\0\0",
        btnf=b"BTNF" + struct.pack("<I", 16) + bytes.fromhex("0400000000000100"),
        members=list(members),
    )
    return narcmod.build(base)

source_members = [b"abc", b"12345678", b"x"]
raw = synthetic(source_members)
parsed = narcmod.parse(raw)
assert parsed.members == source_members

out = narcmod.append_members(raw, [b"new", b"member-2"])
parsed2 = narcmod.parse(out)
assert parsed2.members[:3] == source_members
assert parsed2.members[3:] == [b"new", b"member-2"]
assert len(parsed2.members) == 5
assert struct.unpack_from("<I", out, 8)[0] == len(out)

print("DS04 NARC append synthetic regression: PASS")
