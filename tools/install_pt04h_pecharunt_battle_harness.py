#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04h-pecharunt-battle-harness.json"))
    args = parser.parse_args()

    root = args.pokeplatinum_root.resolve()
    path = root / "src/field_map_change.c"
    if not path.is_file():
        raise SystemExit(f"missing pinned pokeplatinum source file: {path}")

    text = path.read_text()
    if "Encounter_NewVsSpeciesAtLevel" not in text:
        raise SystemExit(
            "PT04H Pecharunt battle harness expects the completed PT04C battle-entry harness first"
        )

    victini_refs = text.count("SPECIES_VICTINI")
    if victini_refs < 2:
        raise SystemExit(
            f"expected PT04C Victini battle references before conversion, found {victini_refs}"
        )

    text = text.replace("SPECIES_VICTINI", "SPECIES_PECHARUNT")
    text = text.replace("Victini", "Pecharunt")
    path.write_text(text)

    report = {
        "gate": "PT04H_GEN9_PECHARUNT_BATTLE_RUNTIME_INSTALL",
        "scope": "CI workspace only; normal Mercury DS game flow unchanged",
        "base_harness": "sealed PT04C native battle-entry path",
        "player_species": "SPECIES_PECHARUNT",
        "species_id": 1025,
        "level": 50,
        "opponent": "SPECIES_BIDOOF",
        "opponent_level": 5,
        "native_entrypoint": "Encounter_NewVsSpeciesAtLevel",
        "expected_visual_proof": [
            "Pecharunt player-side back sprite",
            "PECHARUNT player name",
            "Lv.50 and sane HP",
            "native battle command UI",
            "stable render across multiple captures",
        ],
        "next_if_passed": "seal PT04H complete and begin playable-baseline certification branch",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
