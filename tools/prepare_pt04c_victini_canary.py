#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match for {old!r}, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: prepare_pt04c_victini_canary.py <pokeplatinum-root>")

    root = Path(sys.argv[1]).resolve()
    victini = root / "res/pokemon/victini"
    mew = root / "res/pokemon/mew"
    intro = root / "src/applications/rowan_intro/rowan_intro_app.c"

    required = [
        victini / "data.json",
        victini / "sprite_data.json",
        victini / "male_front.png",
        victini / "male_back.png",
        victini / "icon.png",
        victini / "normal.pal",
        victini / "shiny.pal",
        mew / "cry.txt",
        mew / "cry.wav",
        intro,
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("missing PT04C canary inputs:\n" + "\n".join(missing))

    # PT04C is a structural species-expansion canary. Until PT05 imports
    # modern cry tables, reuse Mew's valid Platinum-format cry assets so the
    # new species traverses the complete native archive build path.
    shutil.copy2(mew / "cry.txt", victini / "cry.txt")
    shutil.copy2(mew / "cry.wav", victini / "cry.wav")

    text = intro.read_text()
    text = replace_once(
        text,
        "        SPECIES_BUNEARY,\n        GENDER_MALE,",
        "        SPECIES_VICTINI,\n        GENDER_MALE,",
        "Rowan intro sprite species",
    )
    text = replace_once(
        text,
        "        Sound_PlayPokemonCry(SPECIES_BUNEARY, 0);",
        "        Sound_PlayPokemonCry(SPECIES_VICTINI, 0);",
        "Rowan intro cry species",
    )
    intro.write_text(text)

    print("PT04C Victini canary prepared")
    print("- National Dex #494 enabled")
    print("- real DS-format Victini battle sprites/icon installed")
    print("- Rowan intro temporarily loads SPECIES_VICTINI")
    print("- cry/ability/learnset/shiny data remain structural placeholders for PT05")


if __name__ == "__main__":
    main()
