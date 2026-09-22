#!/usr/bin/env python3
"""Convert a Gen IV DPPt land-data member to HGSS layout.

DPPt:
    0x00 u32 permissions size
    0x04 u32 buildings size
    0x08 u32 NSBMD size
    0x0C u32 BDHC size
    0x10 permissions...

HGSS:
    same 16-byte size header
    0x10 BGS block
    permissions...
    
For ordinary imported maps we use HGSS's blank BGS block:
    34 12 00 00
(signature 0x1234, payload length 0)
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

BLANK_HGSS_BGS = bytes((0x34, 0x12, 0x00, 0x00))
HEADER_SIZE = 0x10
PERMISSIONS_SIZE = 0x800
BUILDING_RECORD_SIZE = 48


def parse_sizes(data: bytes) -> tuple[int, int, int, int]:
    if len(data) < HEADER_SIZE:
        raise ValueError("Land-data member is shorter than the 16-byte DPPt header")
    return struct.unpack_from("<4I", data, 0)


def validate_dppt(data: bytes) -> tuple[int, int, int, int]:
    permissions, buildings, nsbmd, bdhc = parse_sizes(data)
    if permissions != PERMISSIONS_SIZE:
        raise ValueError(
            f"Unexpected permissions size 0x{permissions:X}; expected 0x{PERMISSIONS_SIZE:X}"
        )
    expected = HEADER_SIZE + permissions + buildings + nsbmd + bdhc
    if len(data) != expected:
        raise ValueError(
            f"Land-data size mismatch: header says {expected} bytes, file has {len(data)}"
        )

    nsbmd_offset = HEADER_SIZE + permissions + buildings
    if nsbmd < 4 or data[nsbmd_offset:nsbmd_offset + 4] != b"BMD0":
        raise ValueError("Map-model section does not begin with Nintendo DS BMD0 signature")

    return permissions, buildings, nsbmd, bdhc


def building_model_ids_dppt(data: bytes) -> list[int]:
    permissions, buildings, _, _ = validate_dppt(data)
    if buildings % BUILDING_RECORD_SIZE != 0:
        raise ValueError(
            f"Building section size {buildings} is not divisible by {BUILDING_RECORD_SIZE}"
        )
    offset = HEADER_SIZE + permissions
    return [
        struct.unpack_from("<I", data, offset + i * BUILDING_RECORD_SIZE)[0]
        for i in range(buildings // BUILDING_RECORD_SIZE)
    ]


def remap_building_models_dppt(
    data: bytes,
    model_map: dict[int, int],
    *,
    require_all: bool = True,
) -> bytes:
    permissions, buildings, _, _ = validate_dppt(data)
    if buildings % BUILDING_RECORD_SIZE != 0:
        raise ValueError(
            f"Building section size {buildings} is not divisible by {BUILDING_RECORD_SIZE}"
        )

    out = bytearray(data)
    offset = HEADER_SIZE + permissions
    for i in range(buildings // BUILDING_RECORD_SIZE):
        rec = offset + i * BUILDING_RECORD_SIZE
        source_id = struct.unpack_from("<I", out, rec)[0]
        if source_id not in model_map:
            if require_all:
                raise ValueError(f"No HGSS model mapping for Platinum model ID {source_id}")
            continue
        target_id = int(model_map[source_id])
        if not 0 <= target_id <= 0xFFFFFFFF:
            raise ValueError(f"Target model ID out of u32 range: {target_id}")
        struct.pack_into("<I", out, rec, target_id)
    return bytes(out)


def convert(
    data: bytes,
    bgs: bytes = BLANK_HGSS_BGS,
    model_map: dict[int, int] | None = None,
) -> bytes:
    validate_dppt(data)
    if model_map is not None:
        data = remap_building_models_dppt(data, model_map)
    if len(bgs) < 4:
        raise ValueError("HGSS BGS block must include at least signature and size fields")
    if bgs[:2] != bytes((0x34, 0x12)):
        raise ValueError("HGSS BGS block must begin with signature 0x1234 (little-endian)")
    payload_len = int.from_bytes(bgs[2:4], "little")
    if len(bgs) != payload_len + 4:
        raise ValueError(
            f"HGSS BGS block length mismatch: declares {payload_len} payload bytes, "
            f"contains {len(bgs) - 4}"
        )
    return data[:HEADER_SIZE] + bgs + data[HEADER_SIZE:]


def validate_hgss(converted: bytes) -> dict[str, int]:
    permissions, buildings, nsbmd, bdhc = parse_sizes(converted)
    if converted[HEADER_SIZE:HEADER_SIZE + 2] != bytes((0x34, 0x12)):
        raise ValueError("Converted HGSS map is missing BGS signature at offset 0x10")
    bgs_payload = int.from_bytes(converted[HEADER_SIZE + 2:HEADER_SIZE + 4], "little")
    bgs_size = bgs_payload + 4
    permissions_offset = HEADER_SIZE + bgs_size
    model_offset = permissions_offset + permissions + buildings
    if converted[model_offset:model_offset + 4] != b"BMD0":
        raise ValueError("Converted HGSS NSBMD section is not aligned correctly")
    expected = HEADER_SIZE + bgs_size + permissions + buildings + nsbmd + bdhc
    if len(converted) != expected:
        raise ValueError("Converted HGSS land-data length does not match section sizes")
    return {
        "bgs_size": bgs_size,
        "permissions_offset": permissions_offset,
        "buildings_offset": permissions_offset + permissions,
        "nsbmd_offset": model_offset,
        "bdhc_offset": model_offset + nsbmd,
        "total_size": expected,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument(
        "--model-map",
        type=Path,
        help="JSON object mapping Platinum building model IDs to HGSS model IDs",
    )
    args = ap.parse_args()

    src = args.input.read_bytes()
    model_map = None
    if args.model_map:
        raw = json.loads(args.model_map.read_text(encoding="utf-8"))
        model_map = {int(k): int(v) for k, v in raw.items()}

    source_models = building_model_ids_dppt(src)
    converted = convert(src, model_map=model_map)
    info = validate_hgss(converted)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(converted)

    print(f"converted {args.input} -> {args.output}")
    print("source_building_models=" + ",".join(map(str, source_models)))
    if model_map is not None:
        print(
            "target_building_models="
            + ",".join(str(model_map[m]) for m in source_models)
        )
    for key, value in info.items():
        print(f"{key}=0x{value:X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
