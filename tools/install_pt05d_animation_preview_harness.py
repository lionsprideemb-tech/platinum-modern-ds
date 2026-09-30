#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def insert_include_once(path: Path, anchor: str, include_line: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if include_line in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + include_line, 1), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("--move", required=True)
    parser.add_argument("--preview-id", required=True)
    parser.add_argument("--report", type=Path, default=Path("pt05d-animation-preview-harness.json"))
    args = parser.parse_args()

    move = args.move.strip()
    if not re.fullmatch(r"MOVE_[A-Z0-9_]+", move):
        raise SystemExit(f"invalid move constant: {move}")

    root = args.pokeplatinum_root.resolve()
    moves_txt = root / "generated" / "moves.txt"
    field = root / "src" / "field_map_change.c"
    if not moves_txt.is_file() or not field.is_file():
        raise SystemExit("expected pinned pokeplatinum tree is incomplete")

    available = {line.strip() for line in moves_txt.read_text(encoding="utf-8").splitlines()}
    if move not in available:
        raise SystemExit(f"{move} is not present in generated/moves.txt")

    text = field.read_text(encoding="utf-8")

    # Reuse the already-proven PT04C direct-new-save -> native battle harness,
    # but keep this proof fully vanilla-resource-safe by using Bidoof as the
    # player Pokemon instead of the Gen-V Victini sentinel.
    if "SPECIES_VICTINI" not in text:
        raise SystemExit("PT04C harness chain was not installed before PT05D finalization")
    text = text.replace("SPECIES_VICTINI", "SPECIES_BIDOOF")
    field.write_text(text, encoding="utf-8")

    insert_include_once(
        field,
        '#include "constants/overworld_weather.h"\n',
        '#include "constants/moves.h"\n',
        "move constants include",
    )
    insert_include_once(
        field,
        '#include "party.h"\n',
        '#include "pokemon.h"\n',
        "Pokemon API include",
    )

    text = field.read_text(encoding="utf-8")
    anchor = (
        "        GF_ASSERT(Pokedex_HasCaughtSpecies(SaveData_GetPokedex(fieldSystem->saveData), SPECIES_BIDOOF));\n\n"
        "        (*state)++;"
    )
    if text.count(anchor) != 1:
        raise SystemExit("could not locate the proven party-insertion anchor")

    replacement = (
        "        GF_ASSERT(Pokedex_HasCaughtSpecies(SaveData_GetPokedex(fieldSystem->saveData), SPECIES_BIDOOF));\n\n"
        "        // PT05D native-Platinum animation proof: force the requested move\n"
        "        // into slot 1 and blank the remaining slots so the emulator can\n"
        "        // select it deterministically with Fight -> A.\n"
        "        Pokemon *previewMon = Party_GetPokemonBySlotIndex(\n"
        "            SaveData_GetParty(fieldSystem->saveData), 0);\n"
        f"        Pokemon_SetMoveSlot(previewMon, {move}, 0);\n"
        "        Pokemon_SetMoveSlot(previewMon, MOVE_NONE, 1);\n"
        "        Pokemon_SetMoveSlot(previewMon, MOVE_NONE, 2);\n"
        "        Pokemon_SetMoveSlot(previewMon, MOVE_NONE, 3);\n\n"
        "        (*state)++;"
    )
    field.write_text(text.replace(anchor, replacement, 1), encoding="utf-8")

    report = {
        "gate": "PT05D_NATIVE_PLATINUM_ANIMATION_PREVIEW_HARNESS",
        "runtime": "pokeplatinum",
        "preview_id": args.preview_id,
        "move_constant": move,
        "player_species": "SPECIES_BIDOOF",
        "player_level": 50,
        "opponent_species": "SPECIES_BIDOOF",
        "opponent_level": 5,
        "move_slot": 0,
        "selection": "native battle UI; Fight then first move",
        "scope": "CI workspace only; no gameplay harness is committed into platinum-overlay",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
