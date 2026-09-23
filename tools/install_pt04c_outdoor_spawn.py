#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04c-outdoor-spawn-install.json"))
    args = parser.parse_args()

    path = args.pokeplatinum_root.resolve() / "src/game_start.c"
    text = path.read_text()

    old = """    StartNewSave(HEAP_ID_GAME_START, saveData);
    static const charcode_t pt04cTrainerName[]"""
    new = """    StartNewSave(HEAP_ID_GAME_START, saveData);
    // PT04C diagnostic: move the synthetic new-game boot to Platinum's
    // known-good Twinleaf Town exterior respawn before the field system loads.
    SetPlayerFirstRespawnLocation(
        FieldOverworldState_GetPlayerLocation(SaveData_GetFieldOverworldState(saveData)));
    static const charcode_t pt04cTrainerName[]"""

    count = text.count(old)
    if count != 1:
        raise SystemExit(f"outdoor spawn hook: expected one match, found {count}")
    path.write_text(text.replace(old, new, 1))

    report = {
        "gate": "PT04C_NATIVE_OUTDOOR_BATTLE_CONTROL",
        "scope": "diagnostic CI branch only",
        "spawn": "Twinleaf Town exterior / first respawn",
        "player_species": "SPECIES_MEW",
        "opponent_species": "SPECIES_BIDOOF",
        "purpose": "separate bedroom map/terrain transition from battle-engine initialization",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
