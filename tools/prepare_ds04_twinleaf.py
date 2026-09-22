#!/usr/bin/env python3
"""Prepare the DS04 static Twinleaf shell inside a pinned pokeheartgold checkout.

This tool is intentionally build-time only:
- reads public-source Platinum assets from a pinned pokeplatinum checkout;
- converts the six Twinleaf land-data members;
- appends Twinleaf visual resources to existing HGSS NARCs;
- adds six 1x1 matrices, seven empty event banks, and two empty script banks;
- extends HGSS map IDs/map headers append-only;
- redirects the DS04 feature build's start room to Platinum Player House 2F.

It never reads or writes a commercial ROM image.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args: str | Path) -> None:
    subprocess.run([str(x) for x in args], check=True)


def matrix_1x1(name: str, land_data_id: int) -> bytes:
    encoded = name.encode("ascii")
    if len(encoded) > 255:
        raise ValueError("Matrix name is too long")
    if not 0 <= land_data_id <= 0xFFFF:
        raise ValueError("Land-data ID does not fit u16")
    return bytes((1, 1, 0, 0, len(encoded))) + encoded + struct.pack("<H", land_data_id)


def append_members(
    nitroarc: Path,
    archive: Path,
    expected_count: int,
    additions: dict[int, tuple[bytes, str]],
) -> None:
    expected_ids = list(range(expected_count, expected_count + len(additions)))
    if sorted(additions) != expected_ids:
        raise ValueError(
            f"{archive}: additions must be contiguous from {expected_count}, got {sorted(additions)}"
        )

    with tempfile.TemporaryDirectory(prefix="ds04-narc-") as tmp_name:
        tmp = Path(tmp_name)
        extract = tmp / "members"
        run(nitroarc, "-xf", archive, extract)

        existing = sorted(p for p in extract.iterdir() if p.is_file())
        if len(existing) != expected_count:
            raise ValueError(
                f"{archive}: expected {expected_count} members before append, found {len(existing)}"
            )

        for member_id, (payload, ext) in additions.items():
            out = extract / f"{member_id:05d}.{ext}"
            if out.exists():
                raise ValueError(f"Refusing to overwrite extracted member {out}")
            out.write_bytes(payload)

        members = sorted(
            (p for p in extract.iterdir() if p.is_file()),
            key=lambda p: int(p.name.split(".", 1)[0]),
        )
        if len(members) != expected_count + len(additions):
            raise ValueError(f"{archive}: unexpected member count after append")

        for index, p in enumerate(members):
            numeric = int(p.name.split(".", 1)[0])
            if numeric != index:
                raise ValueError(
                    f"{archive}: extracted member numbering is not contiguous at {p.name}"
                )

        order = tmp / "order.txt"
        order.write_text("\n".join(p.name for p in members) + "\n", encoding="utf-8")
        rebuilt = tmp / "rebuilt.narc"
        run(nitroarc, "-cf", rebuilt, "-T", order, extract)
        shutil.copyfile(rebuilt, archive)


def insert_before(text: str, marker: str, payload: str) -> str:
    if payload.strip() in text:
        return text
    idx = text.rfind(marker)
    if idx < 0:
        raise ValueError(f"Marker not found: {marker!r}")
    return text[:idx] + payload + text[idx:]


def patch_maps_h(path: Path, maps: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    old = "#define MAP_ID_MAX                                        540"
    if old not in text and "#define MAP_ID_MAX                                        547" not in text:
        raise ValueError("Unexpected MAP_ID_MAX in constants/maps.h")

    lines = ["\n/* DS04: append-only Sinnoh/Twinleaf proof maps. */"]
    for item in maps:
        lines.append(f"#define {item['name']:<52} {item['id']}")
    lines.append("")
    block = "\n".join(lines)

    if "MAP_SINNOH_TWINLEAF_TOWN" not in text:
        text = text.replace(old, block + "\n#define MAP_ID_MAX                                        547")
    path.write_text(text, encoding="utf-8")


def map_header_entry(item: dict) -> str:
    exterior = item["kind"] == "exterior"
    area = 106 if exterior else 107
    matrix_const = "NARC_map_matrix_" + item["matrix_file"].replace(".", "_")
    event_const = "NARC_zone_event_" + item["event_file"].replace(".", "_")

    return f"""    [{item['name']}] = {{
                        .wildEncounterBank = ENCDATA_NA,
                        .areaDataBank = {area},
                        .moveModelBank = 15,
                        .worldMapX = 21,
                        .worldMapY = 12,
                        .matrixId = {matrix_const},
                        .scriptsBank = NARC_scr_seq_scr_seq_0965_SINNOH_TWINLEAF_EMPTY_bin,
                        .scriptHeaderBank = NARC_scr_seq_scr_seq_0966_SINNOH_TWINLEAF_EMPTY_hdr_bin,
                        .msgBank = NARC_msg_msg_0003_EVERYWHERE_bin,
                        .dayMusicId = SEQ_GS_T_WAKABA,
                        .nightMusicId = SEQ_GS_T_WAKABA,
                        .eventsBank = {event_const},
                        .mapsec = MAPSEC_NEW_BARK_TOWN,
                        .areaIcon = {2 if exterior else 9},
                        .momCallIntroParam = 0,
                        .regionNo = MAP_REGION_JOHTO,
                        .weather = 0,
                        .mapType = {'MAP_TYPE_CITY_TOWN' if exterior else 'MAP_TYPE_INTERIOR'},
                        .cameraType = {0 if exterior else 4},
                        .followMode = {'MAP_FOLLOWMODE_ALLOW' if exterior else 'MAP_FOLLOWMODE_HEIGHT_RESTRICT'},
                        .battleBg = {'BATTLE_BG_GENERAL' if exterior else 'BATTLE_BG_BUILDING_1'},
                        .bikeAllowed = {'TRUE' if exterior else 'FALSE'},
                        .runningAllowed_Unused = {'TRUE' if exterior else 'FALSE'},
                        .escapeRopeAllowed = FALSE,
                        .flyAllowed = FALSE,
                        .outgoingCalls = FALSE,
                        .incomingCalls = FALSE,
                        .radioSignal = FALSE,
                        }},
"""


def patch_map_headers(path: Path, maps: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    if "MAP_SINNOH_TWINLEAF_TOWN] =" in text:
        return
    payload = "\n    /* DS04 static Twinleaf shell. */\n" + "".join(
        map_header_entry(item) for item in maps
    )
    marker = "};\n\n#endif"
    text = insert_before(text, marker, payload)
    path.write_text(text, encoding="utf-8")


def patch_start_location(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        ".mapId = MAP_NEW_BARK_PLAYER_HOUSE_2F,\n"
        "    .warpId = 0xFFFFFFFF,\n"
        "    .x = 0x00000006,\n"
        "    .y = 0x00000006,",
        ".mapId = MAP_SINNOH_TWINLEAF_PLAYER_HOUSE_2F,\n"
        "    .warpId = 0xFFFFFFFF,\n"
        "    .x = 0x00000004,\n"
        "    .y = 0x00000006,",
    )
    if "MAP_SINNOH_TWINLEAF_PLAYER_HOUSE_2F" not in text:
        raise ValueError("Could not apply DS04 start-location patch")
    path.write_text(text, encoding="utf-8")


def write_generated_source(phg: Path, config: dict) -> None:
    matrix_dir = phg / "files/fielddata/mapmatrix/map_matrix"
    event_dir = phg / "files/fielddata/eventdata/zone_event"
    script_dir = phg / "files/fielddata/script/scr_seq"

    matrix_payloads: dict[str, int] = {}
    for item in config["maps"]:
        matrix_payloads[item["matrix_file"]] = item["land_data_id"]
    for filename, land_id in matrix_payloads.items():
        (matrix_dir / filename).write_bytes(matrix_1x1("sinnoh", land_id))

    for item in config["maps"]:
        (event_dir / item["event_file"]).write_text(
            json.dumps(
                {"header": "fielddata/script/scr_seq/event_EVERYWHERE.h"},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    (script_dir / "scr_seq_0965_SINNOH_TWINLEAF_EMPTY.s").write_text(
        '#include "constants/scrcmd.h"\n'
        '\t.include "asm/macros/script.inc"\n\n'
        '\t.rodata\n\n'
        '\tScrDefEnd\n\n'
        '\t.balign 4, 0\n',
        encoding="utf-8",
    )
    (script_dir / "scr_seq_0966_SINNOH_TWINLEAF_EMPTY_hdr.s").write_text(
        '#include "constants/scrcmd.h"\n'
        '#include "constants/init_script_types.h"\n'
        '\t.include "asm/macros/script.inc"\n\n'
        '\t.rodata\n'
        '\t.option alignment off\n\n'
        '\tInitScriptEntryEnd\n\n'
        '\tInitScriptEnd\n',
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--pokeheartgold", type=Path, required=True)
    ap.add_argument("--pokeplatinum", type=Path, required=True)
    args = ap.parse_args()

    project = args.project_root.resolve()
    phg = args.pokeheartgold.resolve()
    ppt = args.pokeplatinum.resolve()

    config = json.loads(
        (project / "platinum_port/twinleaf/ds04_static_shell.json").read_text()
    )
    allocation = json.loads(
        (project / "platinum_port/twinleaf/target_allocation.json").read_text()
    )
    visuals = json.loads(
        (project / "platinum_port/twinleaf/visual_resources.json").read_text()
    )

    landconv = load_module(project / "tools/convert_platinum_landdata.py", "landconv")
    areaconv = load_module(project / "tools/convert_platinum_areadata.py", "areaconv")
    propset = load_module(project / "tools/build_hgss_prop_set.py", "propset")

    nitroarc = phg / "tools/nitroarc/nitroarc"
    if not nitroarc.is_file():
        raise FileNotFoundError(
            f"Build pokeheartgold/tools/nitroarc before running DS04 prep: {nitroarc}"
        )

    ext_map = {
        int(k): int(v)
        for k, v in json.loads(
            (project / "platinum_port/twinleaf/model_map_exterior.json").read_text()
        ).items()
    }
    int_map = {
        int(k): int(v)
        for k, v in json.loads(
            (project / "platinum_port/twinleaf/model_map_interior.json").read_text()
        ).items()
    }

    land_additions: dict[int, tuple[bytes, str]] = {}
    for item in allocation["twinleaf"]["land_data"]:
        src_num = int(item["source"].split("_")[1])
        src = ppt / f"res/field/maps/data/map_data_{src_num:03d}.bin"
        model_map = ext_map if src_num == 0 else int_map
        converted = landconv.convert(src.read_bytes(), model_map=model_map)
        landconv.validate_hgss(converted)
        land_additions[int(item["target_id"])] = (converted, "bin")

    ext_area, _ = areaconv.convert(
        json.loads(
            (ppt / visuals["environments"]["exterior"]["source_area_data"]).read_text()
        ),
        building_tileset=104,
        map_tileset=106,
        area_type=areaconv.HGSS_AREA_OUTDOOR,
    )
    int_area, _ = areaconv.convert(
        json.loads(
            (ppt / visuals["environments"]["interior"]["source_area_data"]).read_text()
        ),
        building_tileset=105,
        map_tileset=107,
        area_type=areaconv.HGSS_AREA_INDOOR,
    )

    archive_jobs: list[tuple[str, int, dict[int, tuple[bytes, str]]]] = [
        ("files/a/0/6/5", 676, land_additions),
        (
            "files/a/0/4/2",
            106,
            {106: (ext_area, "bin"), 107: (int_area, "bin")},
        ),
        (
            "files/a/0/4/3",
            104,
            {
                104: (propset.build(sorted(set(ext_map.values()))), "bin"),
                105: (propset.build(sorted(set(int_map.values()))), "bin"),
            },
        ),
        (
            "files/a/0/4/4",
            106,
            {
                106: (
                    (ppt / visuals["environments"]["exterior"]["source_map_texture"]).read_bytes(),
                    "nsbtx",
                ),
                107: (
                    (ppt / visuals["environments"]["interior"]["source_map_texture"]).read_bytes(),
                    "nsbtx",
                ),
            },
        ),
        (
            "files/a/0/7/0",
            104,
            {
                104: (
                    (ppt / visuals["environments"]["exterior"]["source_prop_texture"]).read_bytes(),
                    "nsbtx",
                ),
                105: (
                    (ppt / visuals["environments"]["interior"]["source_prop_texture"]).read_bytes(),
                    "nsbtx",
                ),
            },
        ),
    ]

    ext_models = {
        int(m["target_id"]): (
            (ppt / m["source_path"]).read_bytes(),
            "nsbmd",
        )
        for m in visuals["environments"]["exterior"]["models"]
    }
    int_models = {
        int(m["target_id"]): (
            (ppt / m["source_path"]).read_bytes(),
            "nsbmd",
        )
        for m in visuals["environments"]["interior"]["models"]
    }
    archive_jobs.extend(
        [
            ("files/a/0/4/0", 340, ext_models),
            ("files/a/1/4/8", 222, int_models),
        ]
    )

    for rel, expected, additions in archive_jobs:
        append_members(nitroarc, phg / rel, expected, additions)

    write_generated_source(phg, config)
    patch_maps_h(phg / "include/constants/maps.h", config["maps"])
    patch_map_headers(phg / "src/data/map_headers.h", config["maps"])
    patch_start_location(phg / "src/location_backup.c")

    print("DS04 Twinleaf static shell prepared successfully")
    print("test_start=MAP_SINNOH_TWINLEAF_PLAYER_HOUSE_2F@(4,6)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
