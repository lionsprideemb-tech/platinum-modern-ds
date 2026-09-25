#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import struct
from pathlib import Path

from audit_pt04d_species_batch import (
    extract_braced_block,
    load_generated_constants,
    load_registry,
    parse_base_exp,
    parse_species_entry,
    scalar,
    translated_body_color,
    translated_growth,
)

GENDER_MAP = {
    0: "GENDER_RATIO_MALE_ONLY",
    31: "GENDER_RATIO_FEMALE_12_5",
    63: "GENDER_RATIO_FEMALE_25",
    127: "GENDER_RATIO_FEMALE_50",
    190: "GENDER_RATIO_FEMALE_75",
    191: "GENDER_RATIO_FEMALE_75",
    222: "GENDER_RATIO_FEMALE_87_5",
    223: "GENDER_RATIO_FEMALE_87_5",
    254: "GENDER_RATIO_FEMALE_ONLY",
    255: "GENDER_RATIO_NO_GENDER",
}

BODY_SHAPE_MAP = {
    "DEX_SEARCH_BODYTYPE_QUADRUPED": "SHAPE_QUADRUPED",
    "DEX_SEARCH_BODYTYPE_BIPEDAL_TAILLESS": "SHAPE_BIPEDAL_TAILLESS",
    "DEX_SEARCH_BODYTYPE_BIPEDAL_TAIL": "SHAPE_BIPEDAL_TAILED",
    "DEX_SEARCH_BODYTYPE_SERPENTINE": "SHAPE_SERPENTINE",
    "DEX_SEARCH_BODYTYPE_MULTIWING": "SHAPE_MULTI_WINGED",
    "DEX_SEARCH_BODYTYPE_BIWING": "SHAPE_WINGED",
    "DEX_SEARCH_BODYTYPE_INSECTOID": "SHAPE_INSECTOID",
    "DEX_SEARCH_BODYTYPE_HEAD_TORSO": "SHAPE_HEAD_BASE",
    "DEX_SEARCH_BODYTYPE_HEAD_ARMS": "SHAPE_HEAD_ARMS",
    "DEX_SEARCH_BODYTYPE_HEAD_LEGS": "SHAPE_HEAD_LEGS",
    "DEX_SEARCH_BODYTYPE_TENTACLES": "SHAPE_TENTACLES",
    "DEX_SEARCH_BODYTYPE_FINS": "SHAPE_FINS",
    "DEX_SEARCH_BODYTYPE_HEAD_ONLY": "SHAPE_HEAD",
    "DEX_SEARCH_BODYTYPE_MULTIBODY": "SHAPE_MULTI_BODY",
}

ITEM_ALIASES = {
    "ITEM_BLACK_GLASSES": "ITEM_BLACKGLASSES",
    "ITEM_DEEP_SEA_TOOTH": "ITEM_DEEPSEATOOTH",
    "ITEM_NEVER_MELT_ICE": "ITEM_NEVERMELTICE",
    "ITEM_SILVER_POWDER": "ITEM_SILVERPOWDER",
    "ITEM_TINY_MUSHROOM": "ITEM_TINYMUSHROOM",
}

SHADOW_MAP = {
    0: "SHADOW_SIZE_NONE",
    1: "SHADOW_SIZE_SMALL",
    2: "SHADOW_SIZE_MEDIUM",
    3: "SHADOW_SIZE_LARGE",
}


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
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))


def donor_dirname(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


def existing_png(root: Path, gender: str, stem: str) -> Path | None:
    path = root / gender / f"{stem}.png"
    return path if path.is_file() and path.stat().st_size else None


def copy_sprite(src: Path, dest: Path) -> None:
    shutil.copy2(src, dest)
    key = src.with_name(src.name + ".key")
    if not key.is_file():
        raise SystemExit(f"missing donor sprite key: {key}")
    shutil.copy2(key, dest.with_name(dest.name + ".key"))


def parse_simple_index(path: Path) -> dict[str, int]:
    text = path.read_text()
    return {
        species: int(value)
        for species, value in re.findall(
            r"\[\s*(SPECIES_[A-Z0-9_]+)\s*\]\s*=\s*(-?\d+)\s*,",
            text,
        )
    }


def parse_height_table(path: Path) -> dict[str, tuple[int, int, int, int]]:
    text = path.read_text()
    result = {}
    pattern = re.compile(
        r"\[\s*(SPECIES_[A-Z0-9_]+)\s*\]\s*=\s*"
        r"\{\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\}\s*,"
    )
    for match in pattern.finditer(text):
        result[match.group(1)] = tuple(int(match.group(i)) for i in range(2, 6))
    return result


def parse_frame_array(block: str, field: str) -> list[dict]:
    frames = extract_braced_block(block, f".{field} = ")
    values = re.findall(
        r"\.frameNo\s*=\s*(-?\d+)\s*,\s*"
        r"\.duration\s*=\s*(\d+)\s*,\s*"
        r"\.horizontalShift\s*=\s*(-?\d+)\s*,\s*"
        r"\.verticalShift\s*=\s*(-?\d+)",
        frames,
    )
    if len(values) != 10:
        raise ValueError(f"{field}: expected 10 animation frames, got {len(values)}")
    return [
        {
            "sprite_frame": int(frame),
            "frame_delay": int(duration),
            "x_shift": int(x),
            "y_shift": int(y),
        }
        for frame, duration, x, y in values
    ]


def parse_sprite_metadata(text: str, species_const: str) -> dict:
    block = extract_braced_block(text, f"[{species_const}] = ")
    front_header = extract_braced_block(block, ".frontHeader = ")
    back_header = extract_braced_block(block, ".backHeader = ")
    return {
        "front": {
            "cry_delay": int(scalar(front_header, "cryDelay")),
            "animation": int(scalar(front_header, "animation")),
            "start_delay": int(scalar(front_header, "animationDelay")),
            "frames": parse_frame_array(block, "frontFrames"),
        },
        "back": {
            "cry_delay": int(scalar(back_header, "cryDelay")),
            "animation": int(scalar(back_header, "animation")),
            "start_delay": int(scalar(back_header, "animationDelay")),
            "frames": parse_frame_array(block, "backFrames"),
        },
        "sprite_y_offset": int(scalar(block, "spriteYOffset")),
        "shadow_x_offset": int(scalar(block, "shadowXOffset")),
        "shadow_size": int(scalar(block, "shadowSize")),
    }


def map_item(name: str, available: set[str]) -> tuple[str, str | None]:
    mapped = ITEM_ALIASES.get(name, name)
    if mapped in available:
        return mapped, None
    return "ITEM_NONE", name


def map_ability(name: str, available: set[str]) -> tuple[str, str | None]:
    if name in available:
        return name, None
    return "ABILITY_NONE", name


def u16(value: int) -> int:
    return value & 0xFFFF


def patch_data(
    template: dict,
    donor: dict,
    species_const: str,
    icon_palette: int,
    available_abilities: set[str],
    available_items: set[str],
    exceptions: dict,
) -> dict:
    data = copy.deepcopy(template)
    data["base_stats"] = donor["base_stats"]
    data["types"] = donor["types"]
    data["catch_rate"] = donor["catch_rate"]

    modern_exp = donor["base_exp_modern"]
    if modern_exp is None:
        modern_exp = 255
        exceptions["missing_base_exp"].append(species_const)
    if modern_exp > 255:
        exceptions["clamped_base_exp"].append(
            {"species": species_const, "modern": modern_exp, "stored": 255}
        )
    data["base_exp_reward"] = min(modern_exp, 255)

    data["ev_yields"] = donor["ev_yields"]

    mapped_items = {}
    for slot in ("common", "rare"):
        mapped, unsupported = map_item(donor["held_items"][slot], available_items)
        mapped_items[slot] = mapped
        if unsupported:
            exceptions["unsupported_items"].append(
                {"species": species_const, "slot": slot, "donor": unsupported, "stored": mapped}
            )
    data["held_items"] = mapped_items

    gender = GENDER_MAP.get(donor["gender_ratio_raw"])
    if gender is None:
        raise ValueError(
            f"{species_const}: unsupported gender ratio {donor['gender_ratio_raw']}"
        )
    data["gender_ratio"] = gender
    data["hatch_cycles"] = donor["hatch_cycles"]
    data["base_friendship"] = donor["base_friendship"]
    data["exp_rate"] = translated_growth(donor["exp_rate"])
    data["egg_groups"] = donor["egg_groups"]

    mapped_abilities = []
    for slot, ability in enumerate(donor["abilities"]):
        mapped, unsupported = map_ability(ability, available_abilities)
        mapped_abilities.append(mapped)
        if unsupported:
            exceptions["unsupported_abilities"].append(
                {"species": species_const, "slot": slot, "donor": unsupported, "stored": mapped}
            )
    data["abilities"] = mapped_abilities
    data["safari_flee_rate"] = donor["safari_flee_rate"]
    data["body_color"] = translated_body_color(donor["body_color"])
    data["flip_sprite"] = bool(donor["flip_sprite"])
    data["icon_palette"] = icon_palette

    # PT04D proves whole-generation species/resource capacity. Modern moves and
    # evolution methods are imported in their dedicated follow-up phase.
    data["learnset"] = {
        "by_level": [[1, "MOVE_TACKLE"]],
        "by_tm": [],
        "by_tutor": [],
    }
    data["evolutions"] = []
    data["offspring"] = species_const
    data["footprint"] = {
        "has": False,
        "size": "FOOTPRINT_SMALL",
        "type": "FOOTPRINT_TYPE_CUTE",
    }

    metrics = donor["metrics"]
    shape = BODY_SHAPE_MAP.get(metrics["body_type"])
    if shape is None:
        raise ValueError(f"{species_const}: unknown donor body shape {metrics['body_type']}")

    dex = data["pokedex_data"]
    dex["height_inches"] = round(metrics["height_dm"] * 3.937007874)
    dex["weight_pounds"] = round(metrics["weight_hg"] * 0.220462262, 1)
    dex["body_shape"] = shape
    dex["trainer_scale_f"] = metrics["trainer_scale_f"]
    dex["pokemon_scale_f"] = metrics["pokemon_scale_f"]
    dex["trainer_scale_m"] = metrics["trainer_scale_m"]
    dex["pokemon_scale_m"] = metrics["pokemon_scale_m"]
    dex["trainer_pos_f"] = u16(metrics["trainer_pos_f"])
    dex["pokemon_pos_f"] = u16(metrics["pokemon_pos_f"])
    dex["trainer_pos_m"] = u16(metrics["trainer_pos_m"])
    dex["pokemon_pos_m"] = u16(metrics["pokemon_pos_m"])

    display_name = donor["text"]["name"].upper()
    category = donor["text"]["category"]
    temp_text = {
        "name": display_name,
        "category": category,
        "entry_text": [
            f"{display_name} is registered in the\n",
            "Mercury DS expanded National Dex.\n",
            "Full localized Dex text follows later.",
        ],
    }
    for lang in ("en", "fr", "de", "it", "es", "jp"):
        dex[lang] = dict(temp_text)

    return data


def build_sprite_data(
    template: dict,
    meta: dict,
    heights: tuple[int, int, int, int],
    has_female: bool,
    has_male: bool,
) -> dict:
    result = copy.deepcopy(template)
    female_back, male_back, female_front, male_front = heights

    result["front"]["y_offset"]["female"] = female_front if has_female and female_front >= 0 else 0
    result["front"]["y_offset"]["male"] = male_front if has_male and male_front >= 0 else 0
    result["front"]["addl_y_offset"] = meta["sprite_y_offset"]
    result["front"]["animation"] = meta["front"]["animation"]
    result["front"]["cry_delay"] = meta["front"]["cry_delay"]
    result["front"]["start_delay"] = meta["front"]["start_delay"]
    result["front"]["frames"] = meta["front"]["frames"]

    result["back"]["y_offset"]["female"] = female_back if has_female and female_back >= 0 else 0
    result["back"]["y_offset"]["male"] = male_back if has_male and male_back >= 0 else 0
    result["back"]["animation"] = meta["back"]["animation"]
    result["back"]["cry_delay"] = meta["back"]["cry_delay"]
    result["back"]["start_delay"] = meta["back"]["start_delay"]
    result["back"]["frames"] = meta["back"]["frames"]

    if meta["shadow_size"] not in SHADOW_MAP:
        raise ValueError(f"unknown donor shadow size {meta['shadow_size']}")
    result["shadow"] = {
        "x_offset": meta["shadow_x_offset"],
        "size": SHADOW_MAP[meta["shadow_size"]],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("hg_engine_root", type=Path)
    parser.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    parser.add_argument("--start-dex", type=int, default=494)
    parser.add_argument("--end-dex", type=int, default=649)
    parser.add_argument("--report", type=Path, default=Path("pt04d-gen5-install.json"))
    parser.add_argument(
        "--gate",
        default="PT04D_GEN5_BATCH_INSTALL",
        help="report gate name for the current canonical batch",
    )
    parser.add_argument(
        "--implemented-abilities",
        type=Path,
        default=None,
        help="Optional ability registry used to keep not-yet-ported modern abilities out of live species data.",
    )
    args = parser.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)
    target = registry[args.start_dex - 1:args.end_dex]

    registered = [
        line.strip()
        for line in (pt / "generated/species.txt").read_text().splitlines()
        if line.strip()
    ]
    for dex, species_const in enumerate(target, start=args.start_dex):
        if dex >= len(registered) or registered[dex] != species_const:
            raise SystemExit(
                f"registry mismatch at native ID {dex}: expected {species_const}, "
                f"found {registered[dex] if dex < len(registered) else '<missing>'}"
            )

    species_text = (hg / "data/Species.c").read_text()
    base_exp = parse_base_exp(hg / "data/BaseExperienceTable.c")
    icon_palettes = parse_simple_index(hg / "data/IconPaletteTable.c")
    heights = parse_height_table(hg / "data/HeightTable.c")
    sprite_offsets_text = (hg / "data/SpriteOffsets.c").read_text()

    available_abilities = load_generated_constants(
        args.implemented_abilities
        if args.implemented_abilities is not None
        else pt / "generated/abilities.txt"
    )
    available_items = load_generated_constants(pt / "generated/items.txt")
    available_types = load_generated_constants(pt / "generated/pokemon_types.txt")
    available_growth = load_generated_constants(pt / "generated/exp_rates.txt")
    available_eggs = load_generated_constants(pt / "generated/egg_groups.txt")
    available_colors = load_generated_constants(pt / "generated/pokemon_colors.txt")

    template_data = json.loads((pt / "res/pokemon/mew/data.json").read_text())
    template_sprite = json.loads((pt / "res/pokemon/mew/sprite_data.json").read_text())

    exceptions = {
        "clamped_base_exp": [],
        "missing_base_exp": [],
        "unsupported_abilities": [],
        "unsupported_items": [],
        "deferred": {
            "learnsets": "temporary Tackle-only compatibility data until modern move import",
            "evolutions": "deferred to evolution-method import",
            "offspring": "temporarily self; breeding lineage import follows",
            "footprints": "native NONE footprint with footprint.has false",
            "cries": "native Mew cry placeholder until modern cry import",
            "localized_dex_text": "English compatibility text mirrored to all languages",
        },
    }
    installed = []

    for dex, species_const in enumerate(target, start=args.start_dex):
        donor = parse_species_entry(species_text, species_const, base_exp)

        for type_name in donor["types"]:
            if type_name not in available_types:
                raise SystemExit(f"{species_const}: unsupported type {type_name}")
        if translated_growth(donor["exp_rate"]) not in available_growth:
            raise SystemExit(f"{species_const}: unsupported growth rate {donor['exp_rate']}")
        for egg in donor["egg_groups"]:
            if egg not in available_eggs:
                raise SystemExit(f"{species_const}: unsupported egg group {egg}")
        color = translated_body_color(donor["body_color"])
        if color not in available_colors:
            raise SystemExit(f"{species_const}: unsupported body color {donor['body_color']}")

        if species_const not in icon_palettes:
            raise SystemExit(f"{species_const}: missing donor icon palette")
        if species_const not in heights:
            raise SystemExit(f"{species_const}: missing donor height offsets")

        sprite_root = hg / "data/graphics/sprites" / donor_dirname(species_const)
        male_front = existing_png(sprite_root, "male", "front")
        male_back = existing_png(sprite_root, "male", "back")
        female_front = existing_png(sprite_root, "female", "front")
        female_back = existing_png(sprite_root, "female", "back")
        has_male = bool(male_front and male_back)
        has_female = bool(female_front and female_back)
        if not has_male and not has_female:
            raise SystemExit(f"{species_const}: no complete donor gender sprite pair")

        icon = sprite_root / "icon.png"
        if not icon.is_file() or not icon.stat().st_size:
            raise SystemExit(f"{species_const}: missing donor icon")

        dest = pt / "res/pokemon" / donor_dirname(species_const)
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)

        if has_male:
            copy_sprite(male_front, dest / "male_front.png")
            copy_sprite(male_back, dest / "male_back.png")
        if has_female:
            copy_sprite(female_front, dest / "female_front.png")
            copy_sprite(female_back, dest / "female_back.png")
        shutil.copy2(icon, dest / "icon.png")
        shutil.copy2(pt / "res/pokemon/none/footprint.png", dest / "footprint.png")
        shutil.copy2(pt / "res/pokemon/mew/cry.txt", dest / "cry.txt")
        shutil.copy2(pt / "res/pokemon/mew/cry.wav", dest / "cry.wav")

        normal_source = male_front or female_front
        shiny_source = male_back or female_back
        write_jasc_palette(dest / "normal.pal", read_png_palette(normal_source))
        write_jasc_palette(dest / "shiny.pal", read_png_palette(shiny_source))

        data = patch_data(
            template_data,
            donor,
            species_const,
            icon_palettes[species_const],
            available_abilities,
            available_items,
            exceptions,
        )
        (dest / "data.json").write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")

        meta = parse_sprite_metadata(sprite_offsets_text, species_const)
        sprite_data = build_sprite_data(
            template_sprite,
            meta,
            heights[species_const],
            has_female,
            has_male,
        )
        (dest / "sprite_data.json").write_text(
            json.dumps(sprite_data, indent=4) + "\n"
        )

        meson = [
            "species_data_files += files('data.json', 'sprite_data.json')",
            "",
            "poke_icon_files += files('icon.png')",
            "",
        ]
        # Platinum's base sprite archive order is back sprites first
        # (female, male), then front sprites (female, male). Keep that exact
        # ordering for dual-gender species so each canonical slot resolves to
        # the correct native pl_pokegra members.
        if has_female:
            meson.append("pokegra_files += files('female_back.png')")
        if has_male:
            meson.append("pokegra_files += files('male_back.png')")
        if has_female:
            meson.append("pokegra_files += files('female_front.png')")
        if has_male:
            meson.append("pokegra_files += files('male_front.png')")
        meson += ["", "pokefoot_files += files('footprint.png')", ""]
        (dest / "meson.build").write_text("\n".join(meson))

        installed.append({
            "national_dex": dex,
            "species": species_const,
            "directory": str(dest),
            "male_sprites": has_male,
            "female_sprites": has_female,
            "icon_palette": icon_palettes[species_const],
            "types": donor["types"],
            "base_exp_modern": donor["base_exp_modern"],
            "base_exp_stored": data["base_exp_reward"],
            "abilities_donor": donor["abilities"],
            "abilities_stored": data["abilities"],
        })

    report = {
        "gate": args.gate,
        "range": [args.start_dex, args.end_dex],
        "installed_species": len(installed),
        "first": installed[0],
        "last": installed[-1],
        "exceptions": exceptions,
        "status": "PASS" if len(installed) == len(target) else "FAIL",
        "next_if_passed": "configure/build expanded Platinum and verify this batch's archive counts",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "gate": report["gate"],
        "range": report["range"],
        "installed_species": report["installed_species"],
        "base_exp_clamped": len(exceptions["clamped_base_exp"]),
        "ability_fallbacks": len(exceptions["unsupported_abilities"]),
        "item_fallbacks": len(exceptions["unsupported_items"]),
        "status": report["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
