#!/usr/bin/env python3
"""MR07D2 — final selection/text polish for Platinum-native Summary screens.

Applied after MR07D. Visual-only:
- native menu arrow becomes the sole selection indicator;
- selected values remain normal Platinum text instead of turning red/green;
- control hints use compact DS-style "BUTTON: ACTION" wording;
- X prompt is clarified as "X: EDIT" / "X: DONE";
- no EV/Nature/Ability/Innate behavior is changed.
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


def patch_text(root: Path) -> None:
    path = root / "res/text/pokemon_summary_screen.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    replacements = {
        "PokemonSummary_Text_MercuryEdit": "X: EDIT",
        "PokemonSummary_Text_MercuryDone": "X: DONE",
        "PokemonSummary_Text_MercuryEvEditorHelp1": "LEFT/RIGHT: 1   L/R: 4",
        "PokemonSummary_Text_MercuryEvEditorHelp2": "X: MAX   Y: 0   A/B: DONE",
        "PokemonSummary_Text_MercuryAbilityEditorHelp1": "UP/DOWN: SELECT",
        "PokemonSummary_Text_MercuryAbilityEditorHelp2": "A: SET   B: BACK",
        "PokemonSummary_Text_MercuryNatureEditorHelp1": "UP/DOWN: SELECT",
        "PokemonSummary_Text_MercuryNatureEditorHelp2": "A: SET   B: BACK",
    }

    found = set()
    for row in data["messages"]:
        msg_id = row.get("id")
        if msg_id in replacements:
            row["en_US"] = replacements[msg_id]
            found.add(msg_id)

    missing = sorted(set(replacements) - found)
    if missing:
        raise SystemExit("MR07D2 missing text IDs: " + ", ".join(missing))

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_top(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/window.c"

    replace_once(
        path,
        """        TextColor valueColor =
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK;
""",
        """        // Platinum's menus use the cursor as the selection cue; avoid
        // recoloring the value itself into a modern-looking active state.
        TextColor valueColor = SUMMARY_TEXT_BLACK;
""",
        "MR07D2 normal selected stat text",
    )

    replace_once(
        path,
        """        natureSelected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK);
""",
        """        SUMMARY_TEXT_BLACK);
""",
        "MR07D2 normal selected Nature text",
    )

    replace_once(
        path,
        """            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK);
""",
        """            SUMMARY_TEXT_BLACK);
""",
        "MR07D2 normal selected Ability text",
    )


def patch_editors(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"

    replace_once(
        path,
        """        TextColor color =
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK;
""",
        """        TextColor color = SUMMARY_TEXT_BLACK;
""",
        "MR07D2 EV cursor-only selection",
    )

    replace_once(
        path,
        """            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK);
""",
        """            SUMMARY_TEXT_BLACK);
""",
        "MR07D2 Ability cursor-only selection",
    )

    replace_once(
        path,
        """        TextColor nameColor =
            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLACK;
""",
        """        TextColor nameColor = SUMMARY_TEXT_BLACK;
""",
        "MR07D2 Nature cursor-only name selection",
    )

    replace_once(
        path,
        """            selected ? SUMMARY_TEXT_RED : SUMMARY_TEXT_BLUE);
""",
        """            SUMMARY_TEXT_BLUE);
""",
        "MR07D2 Nature effect stable color",
    )


def validate(root: Path) -> dict[str, bool]:
    window_c = (
        root / "src/applications/pokemon_summary_screen/window.c"
    ).read_text()
    main_c = (
        root / "src/applications/pokemon_summary_screen/main.c"
    ).read_text()
    text_json = (
        root / "res/text/pokemon_summary_screen.json"
    ).read_text()

    checks = {
        "clear_x_prompt":
            '"X: EDIT"' in text_json and '"X: DONE"' in text_json,
        "compact_button_help":
            '"A: SET   B: BACK"' in text_json
            and '"X: MAX   Y: 0   A/B: DONE"' in text_json,
        "top_cursor_only":
            "TextColor valueColor = SUMMARY_TEXT_BLACK;" in window_c
            and "MercurySkills_PrintCursor" in window_c,
        "ev_cursor_only":
            "TextColor color = SUMMARY_TEXT_BLACK;" in main_c,
        "ability_cursor_only":
            "MercurySkillsEditor_PrintCursor(body, 4, y)" in main_c,
        "nature_cursor_only":
            "TextColor nameColor = SUMMARY_TEXT_BLACK;" in main_c,
        "native_arrow_preserved":
            "ColoredArrow_New" in main_c
            and "ColoredArrow_New" in window_c,
        "logic_preserved":
            "Pokemon_MercurySetNatureOverride" in main_c
            and "MercurySkillsEditor_SetCurrentEV" in main_c
            and "MercurySkillsEditor_SetAbility" in main_c,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr07d2-summary-selection-polish.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_text(root)
    patch_top(root)
    patch_editors(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07D2_SUMMARY_SELECTION_TEXT_POLISH",
        "status": status,
        "scope": "visual-only final polish after MR07D",
        "selection_language": "native menu arrow only; values retain normal Platinum text",
        "control_language": "compact BUTTON: ACTION footer prompts",
        "functionality_changed": False,
        "innate_backend_added": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07D2 validation failed")


if __name__ == "__main__":
    main()
