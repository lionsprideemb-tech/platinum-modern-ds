#!/usr/bin/env python3
"""MR07D4 — final Platinum typography/accent cleanup for Mercury Skills.

Applied after MR07D3. Visual-only.

- Lavender/purple stays in the native Platinum background cells.
- Player-facing text uses Platinum dark/blue text instead of purple.
- Selection arrows use the same blue family as other Summary accents.
- EV/Nature detail text uses dark blue for a cleaner vanilla read.
- No Summary behavior, data storage, or editing logic changes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_window(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/window.c"

    # MR07D3 changed the top-panel arrow to the lavender/purple end of the
    # native Skills palette. Keep the lavender backgrounds, but return cursor
    # ink to Platinum's blue family so the UI reads less custom.
    replace_once(
        path,
        """        ColoredArrow_SetColor(arrow, TEXT_COLOR(14, 13, 0));
""",
        """        ColoredArrow_SetColor(arrow, TEXT_COLOR(11, 10, 0));
""",
        "MR07D4 blue Skills cursor",
    )

    # The only deliberately purple player-facing text in MR07D3 is the detail
    # strip. Use the existing vanilla blue ink instead.
    replace_once(
        path,
        """    const TextColor mercuryBlue = TEXT_COLOR(11, 10, 0);
    const TextColor mercuryPurple = TEXT_COLOR(14, 13, 0);
""",
        """    const TextColor mercuryBlue = TEXT_COLOR(11, 10, 0);
""",
        "MR07D4 remove purple text token",
    )

    # Two uses: EV detail and selected-Nature detail.
    text = path.read_text()
    count = text.count("            mercuryPurple")
    if count != 2:
        raise SystemExit(
            f"MR07D4 detail ink: expected two mercuryPurple uses, found {count}"
        )
    path.write_text(
        text.replace("            mercuryPurple", "            mercuryBlue"),
        encoding="utf-8",
    )


def validate(root: Path) -> dict[str, bool]:
    window_c = (
        root / "src/applications/pokemon_summary_screen/window.c"
    ).read_text()

    checks = {
        "purple_backgrounds_retained":
            "Window_FillRectWithColor(panel, 13" in window_c
            and "Window_FillRectWithColor(panel, 12" in window_c,
        "no_purple_text_token":
            "mercuryPurple" not in window_c,
        "blue_selection_arrow":
            "ColoredArrow_SetColor(arrow, TEXT_COLOR(11, 10, 0));" in window_c,
        "blue_detail_text":
            window_c.count("            mercuryBlue") >= 3,
        "vanilla_palette_retained":
            ".palette = 8" in window_c,
        "logic_unchanged":
            "summaryScreen->mercurySkillsEditMode" in window_c
            and "summaryScreen->monData.evs" in window_c
            and "summaryScreen->monData.ability" in window_c,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr07d4-summary-typography-polish.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_window(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07D4_SUMMARY_TYPOGRAPHY_POLISH",
        "status": status,
        "scope": "top Skills typography/accent colors only",
        "purple_usage": "background/panel accents only",
        "text": "dark and native blue",
        "selection": "native blue menu arrow",
        "functionality_changed": False,
        "layout_changed": False,
        "innate_backend_added": False,
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07D4 validation failed")


if __name__ == "__main__":
    main()
