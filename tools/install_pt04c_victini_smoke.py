#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import struct
from pathlib import Path

VICTINI_DEX = 494


def read_png_palette(path: Path) -> list[tuple[int, int, int]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"{path} is not a PNG")

    pos = 8
    palette: list[tuple[int, int, int]] = []
    while pos + 12 <= len(data):
        length = struct.unpack_from(">I", data, pos)[0]
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"PLTE":
            if len(payload) % 3:
                raise SystemExit(f"{path} has malformed PLTE data")
            palette = [
                (payload[i], payload[i + 1], payload[i + 2])
                for i in range(0, len(payload), 3)
            ]
            break

    if not palette:
        raise SystemExit(f"{path} has no indexed PLTE palette")

    palette = palette[:16]
    while len(palette) < 16:
        palette.append((0, 0, 0))
    return palette


def write_jasc_palette(path: Path, colors: list[tuple[int, int, int]]) -> None:
    lines = ["JASC-PAL", "0100", "16"]
    lines += [f"{r} {g} {b}" for r, g, b in colors[:16]]
    # nitrogfx's JASC reader requires DOS line endings even on Linux.
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))


def patch_victini_data(template: dict) -> dict:
    data = template
    data["base_stats"] = {
        "hp": 100,
        "attack": 100,
        "defense": 100,
        "speed": 100,
        "special_attack": 100,
        "special_defense": 100,
    }
    data["types"] = ["TYPE_PSYCHIC", "TYPE_FIRE"]
    data["catch_rate"] = 3
    # Platinum stores this field in one byte. PT05 must widen the data and
    # runtime readers before importing the intended modern reward of 300.
    data["base_exp_reward"] = 255
    data["ev_yields"] = {
        "hp": 3,
        "attack": 0,
        "defense": 0,
        "speed": 0,
        "special_attack": 0,
        "special_defense": 0,
    }
    data["held_items"] = {"common": "ITEM_NONE", "rare": "ITEM_NONE"}
    data["gender_ratio"] = "GENDER_RATIO_NO_GENDER"
    data["hatch_cycles"] = 120
    data["base_friendship"] = 100
    data["exp_rate"] = "EXP_RATE_MEDIUM_SLOW"
    data["egg_groups"] = ["EGG_GROUP_UNDISCOVERED", "EGG_GROUP_UNDISCOVERED"]

    # PT04 proves species-index expansion before PT05 expands the modern
    # move/ability tables. Victory Star and Victini's post-Gen-IV moves are
    # intentionally deferred; this compatibility ability/learnset is replaced
    # in PT05.
    data["abilities"] = ["ABILITY_SYNCHRONIZE", "ABILITY_NONE"]
    data["body_color"] = "MON_COLOR_YELLOW"
    data["learnset"] = {
        "by_level": [
            [1, "MOVE_CONFUSION"],
            [1, "MOVE_QUICK_ATTACK"],
            [9, "MOVE_ENDURE"],
            [17, "MOVE_HEADBUTT"],
            [25, "MOVE_ZEN_HEADBUTT"],
            [33, "MOVE_REVERSAL"],
        ],
        "by_tm": [],
        "by_tutor": [],
    }
    data["evolutions"] = []
    data["offspring"] = "SPECIES_VICTINI"
    data["footprint"] = {
        "has": False,
        "size": "FOOTPRINT_SMALL",
        "type": "FOOTPRINT_TYPE_CUTE",
    }

    dex = data["pokedex_data"]
    dex["height_inches"] = 16
    dex["weight_pounds"] = 8.8
    dex["body_shape"] = "SHAPE_BIPEDAL_TAILED"

    text = {
        "name": "VICTINI",
        "category": "Victory Pokémon",
        "entry_text": [
            "A post-Gen-IV species used to prove\n",
            "Mercury DS can safely expand\n",
            "the native species registry.",
        ],
    }
    for lang in ("en", "fr", "de", "it", "es", "jp"):
        dex[lang] = dict(text)

    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("hg_engine_root", type=Path)
    parser.add_argument("--report", type=Path, default=Path("pt04c-victini-install.json"))
    args = parser.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()

    species_lines = [
        line.strip()
        for line in (pt / "generated/species.txt").read_text().splitlines()
        if line.strip()
    ]
    try:
        victini_index = species_lines.index("SPECIES_VICTINI")
    except ValueError as exc:
        raise SystemExit("SPECIES_VICTINI is missing from generated/species.txt") from exc

    if victini_index != VICTINI_DEX:
        raise SystemExit(
            f"Victini must be species ID {VICTINI_DEX}, got {victini_index}"
        )

    donor = hg / "data/graphics/sprites/victini"
    donor_front = donor / "male/front.png"
    donor_back = donor / "male/back.png"
    donor_icon = donor / "icon.png"
    donor_front_key = donor / "male/front.png.key"
    donor_back_key = donor / "male/back.png.key"
    for path in (donor_front, donor_back, donor_icon, donor_front_key, donor_back_key):
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"missing pinned HG-Engine donor asset: {path}")

    dest = pt / "res/pokemon/victini"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    shutil.copy2(donor_front, dest / "male_front.png")
    shutil.copy2(donor_back, dest / "male_back.png")
    shutil.copy2(donor_front_key, dest / "male_front.png.key")
    shutil.copy2(donor_back_key, dest / "male_back.png.key")
    shutil.copy2(donor_icon, dest / "icon.png")
    # The footprint archive requires a member even for footprint.has == False.
    # Use the native NONE entry until Victini's footprint art is imported.
    shutil.copy2(pt / "res/pokemon/none/footprint.png", dest / "footprint.png")

    palette = read_png_palette(donor_front)
    write_jasc_palette(dest / "normal.pal", palette)
    # PT04C's target is ordinary runtime loading. The authentic shiny palette
    # is imported in the later bulk-art pass; keeping the same indexed palette
    # here preserves valid archive structure without inventing colors.
    write_jasc_palette(dest / "shiny.pal", palette)

    # The current Platinum build unconditionally expects one cry bank/wave pair
    # per registered base species. Authentic modern cries are a later audio
    # import; reuse a known-good native pair for this architecture smoke test.
    shutil.copy2(pt / "res/pokemon/mew/cry.txt", dest / "cry.txt")
    shutil.copy2(pt / "res/pokemon/mew/cry.wav", dest / "cry.wav")
    shutil.copy2(pt / "res/pokemon/mew/sprite_data.json", dest / "sprite_data.json")

    template = json.loads((pt / "res/pokemon/mew/data.json").read_text())
    victini = patch_victini_data(template)
    (dest / "data.json").write_text(
        json.dumps(victini, indent=4, ensure_ascii=False) + "\n"
    )

    (dest / "meson.build").write_text(
        "species_data_files += files('data.json', 'sprite_data.json')\n\n"
        "poke_icon_files += files('icon.png')\n\n"
        "pokegra_files += files('male_back.png')\n"
        "pokegra_files += files('male_front.png')\n"
        "\npokefoot_files += files('footprint.png')\n"
    )

    report = {
        "gate": "PT04C_VICTINI_BUILD_INSTALL",
        "species": "SPECIES_VICTINI",
        "national_dex": VICTINI_DEX,
        "donor_graphics": "pinned BluRosie/hg-engine",
        "front_sprite_bytes": (dest / "male_front.png").stat().st_size,
        "back_sprite_bytes": (dest / "male_back.png").stat().st_size,
        "icon_bytes": (dest / "icon.png").stat().st_size,
        "temporary_pt04_only": {
            "footprint": "native NONE entry with footprint.has false until authentic art import",
            "base_exp_reward": "255 until PT05 widens the field for the intended value 300",
            "ability": "ABILITY_SYNCHRONIZE until PT05 Victory Star import",
            "learnset": "Gen-IV-compatible smoke-test subset until PT05 move expansion",
            "cry": "native Mew cry placeholder until modern cry import",
            "shiny_palette": "normal palette mirror until bulk art import",
        },
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
