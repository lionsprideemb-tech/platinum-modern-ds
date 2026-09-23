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
    parser.add_argument("--report", type=Path, default=Path("pt04c-cutin-bypass-install.json"))
    args = parser.parse_args()

    encounter_c = args.pokeplatinum_root.resolve() / "src/encounter.c"
    if not encounter_c.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {encounter_c}")

    old = """    case 0:
        MapObjectMan_PauseAllMovement(fieldSystem->mapObjMan);
        FieldTransition_StartEncounterEffect(task, encounter->introEffectID, encounter->battleBGM);
        (*state)++;
        break;"""
    new = """    case 0:
        // PT04C CI diagnostic: bypass only the field encounter cut-in.
        // The normal battle DTO, field shutdown, and battle child application
        // remain untouched so the persistent black screen can be isolated.
        MapObjectMan_PauseAllMovement(fieldSystem->mapObjMan);
        Sound_SetSceneAndPlayBGM(SOUND_SCENE_BATTLE, encounter->battleBGM, 1);
        (*state)++;
        break;"""

    replace_once(encounter_c, old, new, "FieldTask_Encounter cut-in bypass")

    report = {
        "gate": "PT04C_NATIVE_BATTLE_CUTIN_BYPASS_INSTALL",
        "scope": "diagnostic CI branch only",
        "player_control_species": "SPECIES_MEW",
        "opponent_species": "SPECIES_BIDOOF",
        "bypassed_component": "FieldTransition_StartEncounterEffect",
        "preserved_components": [
            "FieldBattleDTO",
            "FieldTransition_FinishMap",
            "FieldSystem_StartBattleProcess",
            "native battle overlay",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
