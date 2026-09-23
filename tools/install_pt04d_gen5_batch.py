#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import struct
from pathlib import Path

from audit_pt04d_species_batch import (
    donor_dirname,
    extract_braced_block,
    load_generated_constants,
    load_registry,
    pair,
    parse_base_exp,
    scalar,
    subblock,
)

GEN5_START = 494
GEN5_END = 649

GENDER_RATIO = {
    0: "GENDER_RATIO_MALE_ONLY",
    31: "GENDER_RATIO_FEMALE_12_5",
    63: "GENDER_RATIO_FEMALE_25",
    127: "GENDER_RATIO_FEMALE_50",
    191: "GENDER_RATIO_FEMALE_75",
    223: "GENDER_RATIO_FEMALE_87_5",
    254: "GENDER_RATIO_FEMALE_ONLY",
    255: "GENDER_RATIO_NO_GENDER",
}

ITEM_ALIASES = {
    "ITEM_BLACK_GLASSES": "ITEM_BLACKGLASSES",
    "ITEM_DEEP_SEA_TOOTH": "ITEM_DEEPSEATOOTH",
    "ITEM_NEVER_MELT_ICE": "ITEM_NEVERMELTICE",
    "ITEM_SILVER_POWDER": "ITEM_SILVERPOWDER",
    "ITEM_TINY_MUSHROOM": "ITEM_TINYMUSHROOM",
}

BODY_TYPE_TO_SHAPE = {
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

SHADOW_SIZE = {
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


def c_string(block: str, field: str) -> str:
    match = re.search(
        rf"\.{re.escape(field)}\s*=\s*(\"(?:\\.|[^\"\\])*\")",
        block,
    )
    if not match:
        raise ValueError(f"missing C string .{field}")
    return ast.literal_eval(match.group(1))


def translated_growth(name: str) -> str:
    return "EXP_RATE_" + name.removeprefix("GROWTH_") if name.startswith("GROWTH_") else name


def translated_color(name: str) -> str:
    return "MON_COLOR_" + name.removeprefix("BODY_COLOR_") if name.startswith("BODY_COLOR_") else name


def parse_species(species_text: str, species_const: str, base_exp: dict[str, int]) -> dict:
    block = extract_braced_block(species_text, f"[{species_const}] = ")
    data = subblock(block, "speciesData")
    stats = subblock(data, "baseStats")
    evs = subblock(data, "evYields")
    items = subblock(data, "wildHeldItems")
    metrics = subblock(block, "metricsData")
    text = subblock(block, "textData")
    return {
        "base_stats": {
            "hp": int(scalar(stats, "hp")),
            "attack": int(scalar(stats, "attack")),
            "defense": int(scalar(stats, "defense")),
            "speed": int(scalar(stats, "speed")),
            "special_attack": int(scalar(stats, "spAttack")),
            "special_defense": int(scalar(stats, "spDefense")),
        },
        "types": pair(data, "types"),
        "catch_rate": int(scalar(data, "catchRate")),
        "base_exp": base_exp[species_const],
        "ev_yields": {
            "hp": int(scalar(evs, "hp")),
            "attack": int(scalar(evs, "attack")),
            "defense": int(scalar(evs, "defense")),
            "speed": int(scalar(evs, "speed")),
            "special_attack": int(scalar(evs, "spAttack")),
            "special_defense": int(scalar(evs, "spDefense")),
        },
        "held_items": {
            "common": scalar(items, "common"),
            "rare": scalar(items, "rare"),
        },
        "gender_ratio_raw": int(scalar(data, "genderRatio")),
        "hatch_cycles": int(scalar(data, "hatchCycles")),
        "base_friendship": int(scalar(data, "baseFriendship")),
        "exp_rate": scalar(data, "expRate"),
        "egg_groups": pair(data, "eggGroups"),
        "abilities": pair(data, "abilities"),
        "safari_flee_rate": int(scalar(data, "safariFleeRate")),
        "body_color": scalar(data, "bodyColor"),
        "flip_sprite": bool(int(scalar(data, "flipSprite"))),
        "metrics": {
            "height_dm": int(scalar(metrics, "heightDecimetres")),
            "weight_hg": int(scalar(metrics, "weightHectograms")),
            "body_type": scalar(metrics, "bodyType"),
            "trainer_scale_f": int(scalar(metrics, "femaleTrainerScale")),
            "pokemon_scale_f": int(scalar(metrics, "femalePokemonScale")),
            "trainer_scale_m": int(scalar(metrics, "maleTrainerScale")),
            "pokemon_scale_m": int(scalar(metrics, "malePokemonScale")),
            "trainer_pos_f": int(scalar(metrics, "femaleTrainerYOffset")),
            "pokemon_pos_f": int(scalar(metrics, "femalePokemonYOffset")),
            "trainer_pos_m": int(scalar(metrics, "maleTrainerYOffset")),
            "pokemon_pos_m": int(scalar(metrics, "malePokemonYOffset")),
        },
        "name": c_string(text, "name"),
        "category": c_string(text, "classification"),
        "entry": c_string(text, "pokedexEntry"),
    }


def parse_simple_table(text: str, species_const: str) -> list[int]:
    match = re.search(
        rf"\[\s*{re.escape(species_const)}\s*\]\s*=\s*\{{\s*([^}}]+)\}}",
        text,
    )
    if not match:
        raise ValueError(f"missing table entry for {species_const}")
    return [int(v.strip()) for v in match.group(1).split(",")]


def parse_icon_palette(text: str, species_const: str) -> int:
    match = re.search(
        rf"\[\s*{re.escape(species_const)}\s*\]\s*=\s*(\d+)\s*,",
        text,
    )
    if not match:
        raise ValueError(f"missing icon palette for {species_const}")
    return int(match.group(1))


def parse_sprite_data(text: str, species_const: str, height_values: list[int]) -> dict:
    block = extract_braced_block(text, f"[{species_const}] = ")
    front_header = subblock(block, "frontHeader")
    back_header = subblock(block, "backHeader")

    def frames(field: str) -> list[dict]:
        frames_block = subblock(block, field)
        rows = re.findall(
            r"\{\s*\.frameNo\s*=\s*(-?\d+)\s*,\s*\.duration\s*=\s*(\d+)\s*,"
            r"\s*\.horizontalShift\s*=\s*(-?\d+)\s*,\s*\.verticalShift\s*=\s*(-?\d+)\s*\}",
            frames_block,
        )
        if len(rows) != 10:
            raise ValueError(f"{species_const} {field}: expected 10 frames, found {len(rows)}")
        return [
            {
                "sprite_frame": int(frame),
                "frame_delay": int(duration),
                "x_shift": int(x),
                "y_shift": int(y),
            }
            for frame, duration, x, y in rows
        ]

    female_back, male_back, female_front, male_front = height_values
    extra_y = int(scalar(block, "spriteYOffset"))
    shadow_x = int(scalar(block, "shadowXOffset"))
    shadow_size = int(scalar(block, "shadowSize"))

    def safe_offset(value: int) -> int:
        return 0 if value < 0 else value

    return {
        "front": {
            "y_offset": {
                "female": safe_offset(female_front),
                "male": safe_offset(male_front),
            },
            "addl_y_offset": extra_y,
            "animation": int(scalar(front_header, "animation")),
            "cry_delay": int(scalar(front_header, "cryDelay")),
            "start_delay": int(scalar(front_header, "animationDelay")),
            "frames": frames("frontFrames"),
        },
        "back": {
            "y_offset": {
                "female": safe_offset(female_back),
                "male": safe_offset(male_back),
            },
            "animation": int(scalar(back_header, "animation")),
            "cry_delay": int(scalar(back_header, "cryDelay")),
            "start_delay": int(scalar(back_header, "animationDelay")),
            "frames": frames("backFrames"),
        },
        "shadow": {
            "x_offset": shadow_x,
            "size": SHADOW_SIZE.get(shadow_size, "SHADOW_SIZE_SMALL"),
        },
    }


def choose_sprite(root: Path, gender: str, side: str) -> Path | None:
    path = root / gender / f"{side}.png"
    return path if path.is_file() and path.stat().st_size else None


def copy_with_key(src: Path, dest: Path) -> None:
    shutil.copy2(src, dest)
    key = Path(str(src) + ".key")
    if key.is_file():
        shutil.copy2(key, Path(str(dest) + ".key"))


def dex_text(entry: str) -> list[str]:
    lines = entry.splitlines()
    if not lines:
        return ["No Pokédex entry is available yet."]
    return [line + ("\n" if i < len(lines) - 1 else "") for i, line in enumerate(lines)]


def make_meson(has_female: bool, has_male: bool) -> str:
    lines = [
        "species_data_files += files('data.json', 'sprite_data.json')",
        "",
        "poke_icon_files += files('icon.png')",
        "",
    ]
    if has_female:
        lines.append("pokegra_files += files('female_back.png')")
    if has_male:
        lines.append("pokegra_files += files('male_back.png')")
    if has_female:
        lines.append("pokegra_files += files('female_front.png')")
    if has_male:
        lines.append("pokegra_files += files('male_front.png')")
    lines += ["", "pokefoot_files += files('footprint.png')", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum_root", type=Path)
    parser.add_argument("hg_engine_root", type=Path)
    parser.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    parser.add_argument("--start-dex", type=int, default=GEN5_START)
    parser.add_argument("--end-dex", type=int, default=GEN5_END)
    parser.add_argument("--report", type=Path, default=Path("pt04d-gen5-install.json"))
    args = parser.parse_args()

    if not (494 <= args.start_dex <= args.end_dex <= 1025):
        raise SystemExit("PT04D batch must stay in canonical post-Gen-IV range")

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
        if len(registered) <= dex or registered[dex] != species_const:
            raise SystemExit(
                f"generated/species.txt mismatch at native ID {dex}: "
                f"expected {species_const}, got {registered[dex] if len(registered) > dex else 'EOF'}"
            )

    species_text = (hg / "data/Species.c").read_text()
    base_exp = parse_base_exp(hg / "data/BaseExperienceTable.c")
    icon_text = (hg / "data/IconPaletteTable.c").read_text()
    height_text = (hg / "data/HeightTable.c").read_text()
    sprite_text = (hg / "data/SpriteOffsets.c").read_text()

    constants = {
        "types": load_generated_constants(pt / "generated/pokemon_types.txt"),
        "abilities": load_generated_constants(pt / "generated/abilities.txt"),
        "items": load_generated_constants(pt / "generated/items.txt"),
        "growth": load_generated_constants(pt / "generated/exp_rates.txt"),
        "eggs": load_generated_constants(pt / "generated/egg_groups.txt"),
        "colors": load_generated_constants(pt / "generated/pokemon_colors.txt"),
        "shapes": load_generated_constants(pt / "generated/pokemon_body_shapes.txt"),
    }

    template = json.loads((pt / "res/pokemon/mew/data.json").read_text())
    fallback_footprint = pt / "res/pokemon/none/footprint.png"
    fallback_cry_txt = pt / "res/pokemon/mew/cry.txt"
    fallback_cry_wav = pt / "res/pokemon/mew/cry.wav"

    ability_subs = []
    item_subs = []
    exp_clamps = []
    installed = []

    for dex, species_const in enumerate(target, start=args.start_dex):
        parsed = parse_species(species_text, species_const, base_exp)
        dirname = donor_dirname(species_const)
        donor = hg / "data/graphics/sprites" / dirname
        dest = pt / "res/pokemon" / dirname
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)

        male_front = choose_sprite(donor, "male", "front")
        male_back = choose_sprite(donor, "male", "back")
        female_front = choose_sprite(donor, "female", "front")
        female_back = choose_sprite(donor, "female", "back")

        has_male = male_front is not None and male_back is not None
        has_female = female_front is not None and female_back is not None
        if not (has_male or has_female):
            raise SystemExit(f"{species_const}: no complete donor gender sprite pair")

        if has_male:
            copy_with_key(male_front, dest / "male_front.png")
            copy_with_key(male_back, dest / "male_back.png")
        if has_female:
            copy_with_key(female_front, dest / "female_front.png")
            copy_with_key(female_back, dest / "female_back.png")

        icon = donor / "icon.png"
        if not icon.is_file():
            raise SystemExit(f"{species_const}: missing icon")
        shutil.copy2(icon, dest / "icon.png")

        normal_source = male_front or female_front
        shiny_source = male_back or female_back
        write_jasc_palette(dest / "normal.pal", read_png_palette(normal_source))
        write_jasc_palette(dest / "shiny.pal", read_png_palette(shiny_source))

        shutil.copy2(fallback_footprint, dest / "footprint.png")
        shutil.copy2(fallback_cry_txt, dest / "cry.txt")
        shutil.copy2(fallback_cry_wav, dest / "cry.wav")

        abilities = []
        for slot, ability in enumerate(parsed["abilities"]):
            if ability in constants["abilities"]:
                abilities.append(ability)
            else:
                abilities.append("ABILITY_NONE")
                ability_subs.append({
                    "national_dex": dex,
                    "species": species_const,
                    "slot": slot,
                    "donor": ability,
                    "temporary": "ABILITY_NONE",
                })

        held_items = {}
        for slot, item in parsed["held_items"].items():
            mapped = ITEM_ALIASES.get(item, item)
            if mapped not in constants["items"]:
                item_subs.append({
                    "national_dex": dex,
                    "species": species_const,
                    "slot": slot,
                    "donor": item,
                    "temporary": "ITEM_NONE",
                })
                mapped = "ITEM_NONE"
            elif mapped != item:
                item_subs.append({
                    "national_dex": dex,
                    "species": species_const,
                    "slot": slot,
                    "donor": item,
                    "temporary": mapped,
                    "alias_only": True,
                })
            held_items[slot] = mapped

        base_exp_reward = parsed["base_exp"]
        if base_exp_reward > 255:
            exp_clamps.append({
                "national_dex": dex,
                "species": species_const,
                "donor": base_exp_reward,
                "temporary": 255,
            })
            base_exp_reward = 255

        growth = translated_growth(parsed["exp_rate"])
        color = translated_color(parsed["body_color"])
        shape = BODY_TYPE_TO_SHAPE.get(parsed["metrics"]["body_type"])
        gender = GENDER_RATIO.get(parsed["gender_ratio_raw"])
        if not gender:
            raise SystemExit(f"{species_const}: unsupported gender ratio {parsed['gender_ratio_raw']}")
        for kind, value, valid in (
            ("type1", parsed["types"][0], constants["types"]),
            ("type2", parsed["types"][1], constants["types"]),
            ("growth", growth, constants["growth"]),
            ("egg1", parsed["egg_groups"][0], constants["eggs"]),
            ("egg2", parsed["egg_groups"][1], constants["eggs"]),
            ("color", color, constants["colors"]),
            ("shape", shape, constants["shapes"]),
        ):
            if value not in valid:
                raise SystemExit(f"{species_const}: unsupported {kind} constant {value}")

        data = json.loads(json.dumps(template))
        data["base_stats"] = parsed["base_stats"]
        data["types"] = parsed["types"]
        data["catch_rate"] = parsed["catch_rate"]
        data["base_exp_reward"] = base_exp_reward
        data["ev_yields"] = parsed["ev_yields"]
        data["held_items"] = held_items
        data["gender_ratio"] = gender
        data["hatch_cycles"] = parsed["hatch_cycles"]
        data["base_friendship"] = parsed["base_friendship"]
        data["exp_rate"] = growth
        data["egg_groups"] = parsed["egg_groups"]
        data["abilities"] = abilities
        data["safari_flee_rate"] = parsed["safari_flee_rate"]
        data["body_color"] = color
        data["flip_sprite"] = parsed["flip_sprite"]
        data["icon_palette"] = parse_icon_palette(icon_text, species_const)
        data["learnset"] = {"by_level": [], "by_tm": [], "by_tutor": []}
        data["evolutions"] = []
        data["offspring"] = species_const
        data["footprint"] = {
            "has": False,
            "size": "FOOTPRINT_SMALL",
            "type": "FOOTPRINT_TYPE_CUTE",
        }

        metrics = parsed["metrics"]
        dexdata = data["pokedex_data"]
        dexdata["height_inches"] = round(metrics["height_dm"] * 3.937007874)
        dexdata["weight_pounds"] = round(metrics["weight_hg"] * 0.220462262, 1)
        dexdata["body_shape"] = shape
        dexdata["trainer_scale_f"] = metrics["trainer_scale_f"]
        dexdata["pokemon_scale_f"] = metrics["pokemon_scale_f"]
        dexdata["trainer_scale_m"] = metrics["trainer_scale_m"]
        dexdata["pokemon_scale_m"] = metrics["pokemon_scale_m"]
        dexdata["trainer_pos_f"] = metrics["trainer_pos_f"] & 0xFFFF
        dexdata["pokemon_pos_f"] = metrics["pokemon_pos_f"] & 0xFFFF
        dexdata["trainer_pos_m"] = metrics["trainer_pos_m"] & 0xFFFF
        dexdata["pokemon_pos_m"] = metrics["pokemon_pos_m"] & 0xFFFF

        lang_text = {
            "name": parsed["name"].upper(),
            "category": parsed["category"],
            "entry_text": dex_text(parsed["entry"]),
        }
        for lang in ("en", "fr", "de", "it", "es", "jp"):
            dexdata[lang] = dict(lang_text)

        (dest / "data.json").write_text(
            json.dumps(data, indent=4, ensure_ascii=False) + "\n"
        )

        height_values = parse_simple_table(height_text, species_const)
        if len(height_values) != 4:
            raise SystemExit(f"{species_const}: expected 4 height offsets")
        sprite_data = parse_sprite_data(sprite_text, species_const, height_values)
        (dest / "sprite_data.json").write_text(
            json.dumps(sprite_data, indent=4) + "\n"
        )
        (dest / "meson.build").write_text(make_meson(has_female, has_male))

        installed.append({
            "national_dex": dex,
            "species": species_const,
            "directory": dirname,
            "male_sprites": has_male,
            "female_sprites": has_female,
            "types": parsed["types"],
            "base_exp_reward": base_exp_reward,
            "icon_palette": data["icon_palette"],
        })

    report = {
        "gate": "PT04D_GEN5_RESOURCE_INSTALL",
        "range": [args.start_dex, args.end_dex],
        "installed_species": len(installed),
        "first": installed[0],
        "last": installed[-1],
        "compatibility_substitutions": {
            "abilities": ability_subs,
            "held_items": item_subs,
            "base_exp_clamps": exp_clamps,
            "learnsets": "deferred to PT05 move import; PT04D emits empty native learnsets",
            "evolutions": "deferred to PT05 evolution-method import; PT04D emits empty native evolution tables",
            "cries": "native Mew placeholder per species until modern cry import",
            "footprints": "native NONE placeholder with footprint.has false",
        },
        "authentic_donor_resources": [
            "base stats",
            "types",
            "catch rate",
            "EV yields",
            "gender",
            "hatch cycles",
            "friendship",
            "growth rate",
            "egg groups",
            "compatible abilities",
            "compatible/aliased held items",
            "body color/shape and Pokedex metrics",
            "front/back battle sprites by gender",
            "icon",
            "normal palette",
            "shiny palette",
            "sprite animation/frame/shadow metadata",
            "English donor name/category/entry text mirrored into all language slots for PT04D",
        ],
        "status": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "gate": report["gate"],
        "installed_species": len(installed),
        "ability_substitutions": len(ability_subs),
        "held_item_substitutions": len(item_subs),
        "base_exp_clamps": len(exp_clamps),
        "status": report["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
