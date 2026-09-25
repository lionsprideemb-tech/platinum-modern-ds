#!/usr/bin/env python3
"""Validate Mercury Redux's permanent 16-bit move-ID namespace contract.

The encoding is u16, but active Nintendo DS move IDs are intentionally kept
compact because Platinum uses move IDs as direct indexes and sizes some runtime
buffers from MAX_MOVES.
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
    soft_ceiling = int(cfg["runtime_soft_ceiling"])

    if move_none != 0:
        raise SystemExit(f"MOVE_NONE must remain ID 0, got {move_none}")
    if sentinel != U16_MAX:
        raise SystemExit(f"learnset sentinel must remain 65535, got {sentinel}")
    if usable_max != U16_MAX - 1:
        raise SystemExit(f"usable_id_max must remain 65534, got {usable_max}")
    if not (floor < soft_ceiling < sentinel):
        raise SystemExit(
            f"invalid floor/soft ceiling: floor={floor}, soft_ceiling={soft_ceiling}"
        )

    ranges = cfg.get("ranges", [])
    if not ranges:
        raise SystemExit("namespace has no ranges")

    expected_start = 1
    names = set()
    active_ends = []
    inactive_starts = []

    for lane in ranges:
        name = lane["name"]
        start = int(lane["start"])
        end = int(lane["end"])
        active = bool(lane.get("active", False))

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

        if active:
            active_ends.append(end)
            if end > soft_ceiling:
                raise SystemExit(
                    f"active lane {name} exceeds runtime soft ceiling "
                    f"{soft_ceiling}: ends at {end}"
                )
        else:
            inactive_starts.append(start)
            if start <= soft_ceiling:
                raise SystemExit(
                    f"inactive lane {name} begins inside active budget "
                    f"{soft_ceiling}: starts at {start}"
                )

        expected_start = end + 1

    if expected_start != sentinel:
        raise SystemExit(
            f"namespace must describe every usable nonzero u16 ID through "
            f"{usable_max}; stopped at {expected_start - 1}"
        )

    if not active_ends or max(active_ends) != soft_ceiling:
        raise SystemExit(
            f"highest active lane must end exactly at runtime_soft_ceiling "
            f"{soft_ceiling}"
        )
    if not inactive_starts or min(inactive_starts) != soft_ceiling + 1:
        raise SystemExit(
            "inactive future space must begin immediately above the active ceiling"
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
                "gate": "MERCURY_MOVE_ID_NAMESPACE_V2",
                "architecture": "u16",
                "canonical_floor": floor,
                "official_capacity": int(official["end"]),
                "future_official_slots": int(official["end"]) - floor,
                "runtime_soft_ceiling": soft_ceiling,
                "usable_id_max": usable_max,
                "sentinel": sentinel,
                "lanes": [
                    {
                        "name": x["name"],
                        "start": int(x["start"]),
                        "end": int(x["end"]),
                        "active": bool(x.get("active", False)),
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
