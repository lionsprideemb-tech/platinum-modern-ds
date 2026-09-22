#!/usr/bin/env python3
"""Build an HGSS prop-model-set member: u16 count followed by u16 model IDs."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


def build(ids: list[int]) -> bytes:
    if len(ids) > 0xFFFF:
        raise ValueError("Too many prop model IDs")
    for model_id in ids:
        if not 0 <= model_id <= 0xFFFF:
            raise ValueError(f"Model ID out of u16 range: {model_id}")
    return struct.pack("<H", len(ids)) + b"".join(
        struct.pack("<H", model_id) for model_id in ids
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model_map", type=Path, help="JSON source->target model map")
    ap.add_argument("output", type=Path)
    args = ap.parse_args()

    mapping = json.loads(args.model_map.read_text(encoding="utf-8"))
    target_ids = sorted({int(v) for v in mapping.values()})
    payload = build(target_ids)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)

    print(f"count={len(target_ids)}")
    print("target_ids=" + ",".join(map(str, target_ids)))
    print(f"bytes={len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
