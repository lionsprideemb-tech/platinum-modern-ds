#!/usr/bin/env python3
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04c-summary-harness-install.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    field_map_change_c = root / "src/field_map_change.c"
    if not field_map_change_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {field_map_change_c}")

    old = """        // Open the real native party application and leave it on screen for the
        // emulator proof capture. The automation will close it in later PT04C
        // phases when summary/PC/battle/save-reload checks are added.
        FieldSystem_OpenPartyMenu_SelectPokemon(0, fieldSystem);"""
    new = """        // PT04C summary phase: reuse the already-proven native party/save state,
        // but launch Platinum's real Summary application directly for slot 0.
        // This remains CI-only and never changes the approved normal game flow.
        FieldSystem_GetPartyMenuMonSummary(0, fieldSystem, 0);"""
    replace_once(field_map_change_c, old, new, "summary UI launch hook")

    report = {
        "gate": "PT04C_VICTINI_NATIVE_SUMMARY_HARNESS_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "prerequisite": "PT04C native party checkpoint Run #8",
        "species": "SPECIES_VICTINI",
        "species_id": 494,
        "party_slot": 0,
        "native_entrypoint": "FieldSystem_GetPartyMenuMonSummary",
        "expected_screen": "Platinum native Pokemon Summary screen for Victini",
        "next_if_passed": "checkpoint Summary proof, then add isolated PC storage proof",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
