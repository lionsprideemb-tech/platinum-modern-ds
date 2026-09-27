#!/usr/bin/env python3
"""MR05O — align Mercury's four encounter periods to the approved clock windows.

Approved Mercury encounter periods:
- Morning: 05:00-09:59
- Day: 10:00-16:59
- Evening: 17:00-20:59
- Night: 21:00-04:59

Platinum's native TimeOfDayForHour differs at two boundary hours:
04:00 is native Morning and 20:00 is native Night. Mercury therefore reads
the RTC hour directly for authored four-period encounter tables while leaving
the rest of Platinum's day/night systems untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def patch_runtime(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"

    old = """        int period = 0;
        int timeOfDay = GetTimeOfDay();

        if (timeOfDay == TIMEOFDAY_DAY) {
            period = 1;
        } else if (timeOfDay == TIMEOFDAY_TWILIGHT) {
            period = 2;
        } else if (timeOfDay == TIMEOFDAY_NIGHT || timeOfDay == TIMEOFDAY_LATE_NIGHT) {
            period = 3;
        }
"""

    new = """        RTCTime mercuryTime;
        RTC_GetCurrentTime(&mercuryTime);

        int period;
        if (mercuryTime.hour >= 5 && mercuryTime.hour < 10) {
            period = 0; // Morning 05:00-09:59
        } else if (mercuryTime.hour >= 10 && mercuryTime.hour < 17) {
            period = 1; // Day 10:00-16:59
        } else if (mercuryTime.hour >= 17 && mercuryTime.hour < 21) {
            period = 2; // Evening 17:00-20:59
        } else {
            period = 3; // Night 21:00-04:59
        }
"""

    replace_once(path, old, new, "MR05O exact Mercury encounter periods")


def validate(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"
    text = path.read_text()

    start = text.index("static BOOL WildEncounters_PopulateGrassEncounterTable")
    end = text.index("\n}\n", start) + 3
    block = text[start:end]

    required = (
        "RTC_GetCurrentTime(&mercuryTime);",
        "mercuryTime.hour >= 5 && mercuryTime.hour < 10",
        "mercuryTime.hour >= 10 && mercuryTime.hour < 17",
        "mercuryTime.hour >= 17 && mercuryTime.hour < 21",
        "period = 3; // Night 21:00-04:59",
    )
    for fragment in required:
        if fragment not in block:
            raise SystemExit(f"MR05O runtime missing {fragment!r}")

    if "GetTimeOfDay()" in block:
        raise SystemExit("MR05O authored encounter selector still depends on Platinum TimeOfDay categories")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05o-exact-tod-periods.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_runtime(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR05O_EXACT_TOD_PERIODS",
        "status": "PASS",
        "clock_source": "RTC hour",
        "periods": {
            "morning": {"start": "05:00", "end": "09:59"},
            "day": {"start": "10:00", "end": "16:59"},
            "evening": {"start": "17:00", "end": "20:59"},
            "night": {"start": "21:00", "end": "04:59"},
        },
        "boundary_04_00": "night",
        "boundary_20_00": "evening",
        "platinum_global_time_system_changed": False,
        "mercury_authored_encounter_selector_changed": True,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
