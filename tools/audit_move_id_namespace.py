#!/usr/bin/env python3
"""Validate Mercury Redux's permanent 16-bit move-ID namespace contract.

This is intentionally data-driven. Runtime code only needs u16 move IDs; this
file prevents generators/importers from quietly colliding with official,
community, Mercury-custom, or sentinel IDs as the project grows.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


U16_MAX = 0xFFFF


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--namespace",
        type=Path,
        default=Path("data/move_id_namespace.json"),
        help="Namespace JSON to validate",
    )
    args = ap.parse_args()

    cfg = json.loads(args.namespace.read_text())
    if cfg.get("architecture") != "u16":
        raise SystemExit("move namespace must use u16 architecture")

    move_none = int(cfg["move_none_id"])
    sentinel = int(cfg["sentinel_id"])
    usable_max = int(cfg["usable_id_max"])
    floor = int(cfg["canonical_floor"])

    if move_none != 0:
        raise SystemExit(f"MOVE_NONE must remain ID 0, got {move_none}")
    if sentinel != U16_MAX:
        raise SystemExit(f"learnset sentinel must remain 65535, got {sentinel}")
    if usable_max != U16_MAX - 1:
        raise SystemExit(f"usable_id_max must remain 65534, got {usable_max}")

    ranges = cfg.get("ranges", [])
    if not ranges:
        raise SystemExit("namespace has no ranges")

    expected_start = 1
    names = set()
    for lane in ranges:
        name = lane["name"]
        start = int(lane["start"])
        end = int(lane["end"])

        if name in names:
            raise SystemExit(f"duplicate lane name: {name}")
        names.add(name)

        if start != expected_start:
            raise SystemExit(
                f"namespace gap/overlap before {name}: expected start "
                f"{expected_start}, got {start}"
            )
        if end < start:
            raise SystemExit(f"invalid range for {name}: {start}..{end}")
        if end >= sentinel:
            raise SystemExit(f"{name} collides with sentinel {sentinel}")

        expected_start = end + 1

    if expected_start != sentinel:
        raise SystemExit(
            f"namespace must cover every usable nonzero u16 ID through "
            f"{usable_max}; stopped at {expected_start - 1}"
        )

    official = next((x for x in ranges if x["name"] == "official_canonical"), None)
    if official is None:
        raise SystemExit("official_canonical lane is missing")
    if not (int(official["start"]) <= floor <= int(official["end"])):
        raise SystemExit(
            f"canonical floor {floor} is outside official_canonical "
            f"{official['start']}..{official['end']}"
        )

    print(
        json.dumps(
            {
                "gate": "MERCURY_MOVE_ID_NAMESPACE_V1",
                "architecture": "u16",
                "canonical_floor": floor,
                "official_capacity": int(official["end"]),
                "usable_ids": usable_max,
                "sentinel": sentinel,
                "lanes": [
                    {
                        "name": x["name"],
                        "start": int(x["start"]),
                        "end": int(x["end"]),
                        "capacity": int(x["end"]) - int(x["start"]) + 1,
                    }
                    for x in ranges
                ],
                "status": "PASS",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
