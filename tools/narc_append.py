#!/usr/bin/env python3
"""Minimal append-only Nintendo DS NARC reader/writer.

Designed for project staging: preserves existing members byte-for-byte and
appends new members with 4-byte alignment. The original BTNF filename-table
section is preserved unchanged because runtime access is by numeric member ID.
"""

from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path

ALIGN = 4


@dataclass
class Narc:
    header: bytes
    fat_magic: bytes
    fat_reserved: bytes
    btnf: bytes
    members: list[bytes]


def align_up(value: int, alignment: int = ALIGN) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def parse(data: bytes) -> Narc:
    if len(data) < 0x10 or data[:4] != b"NARC":
        raise ValueError("Not a NARC archive")
    if struct.unpack_from("<H", data, 12)[0] != 0x10:
        raise ValueError("Unexpected NARC header size")
    if struct.unpack_from("<H", data, 14)[0] != 3:
        raise ValueError("Expected three NARC sections")

    fat_off = 0x10
    fat_magic = data[fat_off:fat_off + 4]
    if fat_magic not in (b"BTAF", b"FATB"):
        raise ValueError(f"Unexpected FAT magic: {fat_magic!r}")
    fat_size = struct.unpack_from("<I", data, fat_off + 4)[0]
    count = struct.unpack_from("<H", data, fat_off + 8)[0]
    expected_fat = 12 + count * 8
    if fat_size != expected_fat:
        raise ValueError(f"Unexpected FAT size {fat_size}; expected {expected_fat}")
    fat_reserved = data[fat_off + 10:fat_off + 12]

    btnf_off = fat_off + fat_size
    if data[btnf_off:btnf_off + 4] not in (b"BTNF", b"FNTB"):
        raise ValueError("Missing BTNF/FNTB section")
    btnf_size = struct.unpack_from("<I", data, btnf_off + 4)[0]
    btnf = data[btnf_off:btnf_off + btnf_size]

    fimg_off = btnf_off + btnf_size
    if data[fimg_off:fimg_off + 4] not in (b"GMIF", b"FIMG"):
        raise ValueError("Missing GMIF/FIMG section")
    fimg_size = struct.unpack_from("<I", data, fimg_off + 4)[0]
    fimg_data = data[fimg_off + 8:fimg_off + fimg_size]

    members = []
    for i in range(count):
        start, end = struct.unpack_from("<II", data, fat_off + 12 + i * 8)
        if start > end or end > len(fimg_data):
            raise ValueError(f"Invalid member {i} range {start}:{end}")
        members.append(bytes(fimg_data[start:end]))

    return Narc(
        header=bytes(data[:0x10]),
        fat_magic=fat_magic,
        fat_reserved=fat_reserved,
        btnf=bytes(btnf),
        members=members,
    )


def build(narc: Narc, members: list[bytes] | None = None) -> bytes:
    members = list(narc.members if members is None else members)
    if len(members) > 0xFFFF:
        raise ValueError("NARC member count exceeds u16")

    image = bytearray()
    entries: list[tuple[int, int]] = []
    for member in members:
        while len(image) % ALIGN:
            image.append(0xFF)
        start = len(image)
        image.extend(member)
        end = len(image)
        entries.append((start, end))

    while len(image) % ALIGN:
        image.append(0xFF)

    fat = bytearray()
    fat.extend(narc.fat_magic)
    fat.extend(struct.pack("<I", 12 + len(entries) * 8))
    fat.extend(struct.pack("<H", len(entries)))
    fat.extend(narc.fat_reserved)
    for start, end in entries:
        fat.extend(struct.pack("<II", start, end))

    fimg_magic = b"GMIF"
    fimg = fimg_magic + struct.pack("<I", 8 + len(image)) + bytes(image)

    header = bytearray(narc.header)
    total = len(header) + len(fat) + len(narc.btnf) + len(fimg)
    struct.pack_into("<I", header, 8, total)

    output = bytes(header) + bytes(fat) + narc.btnf + fimg
    if len(output) != total:
        raise AssertionError("NARC size accounting failure")
    return output


def append_members(data: bytes, new_members: list[bytes]) -> bytes:
    narc = parse(data)
    return build(narc, narc.members + [bytes(x) for x in new_members])


def append_files(archive: Path, paths: list[Path]) -> tuple[int, int]:
    before = parse(archive.read_bytes())
    payloads = [p.read_bytes() for p in paths]
    archive.write_bytes(build(before, before.members + payloads))
    after = parse(archive.read_bytes())
    return len(before.members), len(after.members)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    ap.add_argument("members", nargs="+", type=Path)
    args = ap.parse_args()

    before, after = append_files(args.archive, args.members)
    print(f"archive={args.archive}")
    print(f"before={before}")
    print(f"appended={after - before}")
    print(f"after={after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
