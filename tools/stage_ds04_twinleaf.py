#!/usr/bin/env python3
"""Stage the certified DS04 Twinleaf proof into a clean pokeheartgold checkout.

This is intentionally append-only. It converts the certified Platinum source
assets, appends them at the reserved HGSS member IDs, generates isolated 1x1
matrices, installs project-owned no-op script banks, expands the HGSS map
header table, and optionally redirects the test player-room location to the
imported Platinum room.

No commercial ROM is read or written by this tool.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_hgss_prop_set as propset
import convert_platinum_areadata as areaconv
import convert_platinum_landdata as landconv
import narc_append

EXPECTED_COUNTS = {
    "land_data": ("files/a/0/6/5", 676),
    "area_data": ("files/a/0/4/2", 106),
    "prop_sets": ("files/a/0/4/3", 104),
    "map_textures": ("files/a/0/4/4", 106),
    "prop_textures": ("files/a/0/7/0", 104),
    "exterior_models": ("files/a/0/4/0", 340),
    "interior_models": ("files/a/1/4/8", 222),
}

LAND_ORDER = [
    ("000", 676, "exterior"),
    ("180", 677, "interior"),
    ("184", 678, "interior"),
    ("185", 679, "interior"),
    ("186", 680, "interior"),
    ("187", 681, "interior"),
]

MATRICES = [
    (288, "SINNOH_TWINLEAF", "s_twin_", 676),
    (289, "SINNOH_TWINLEAF_GENERIC_HOUSE", "s_gen_", 677),
    (290, "SINNOH_TWINLEAF_RIVAL_1F", "s_riv1_", 678),
    (291, "SINNOH_TWINLEAF_RIVAL_2F", "s_riv2_", 679),
    (292, "SINNOH_TWINLEAF_PLAYER_1F", "s_plr1_", 680),
    (293, "SINNOH_TWINLEAF_PLAYER_2F", "s_plr2_", 681),
]

MAP_DEFINES = [
    ("MAP_SINNOH_TWINLEAF_TOWN", 540),
    ("MAP_SINNOH_TWINLEAF_RIVAL_HOUSE_1F", 541),
    ("MAP_SINNOH_TWINLEAF_RIVAL_HOUSE_2F", 542),
    ("MAP_SINNOH_TWINLEAF_PLAYER_HOUSE_1F", 543),
    ("MAP_SINNOH_TWINLEAF_PLAYER_HOUSE_2F", 544),
    ("MAP_SINNOH_TWINLEAF_NORTHEAST_HOUSE", 545),
    ("MAP_SINNOH_TWINLEAF_SOUTHWEST_HOUSE", 546),
]

NOOP_SCRIPT_ID = 965
NOOP_HEADER_ID = 966


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def model_map(path: Path) -> dict[int, int]:
    return {int(k): int(v) for k, v in load_json(path).items()}


def check_archive_count(root: Path, key: str) -> None:
    rel, expected = EXPECTED_COUNTS[key]
    archive = root / rel
    count = len(narc_append.parse(archive.read_bytes()).members)
    if count != expected:
        raise RuntimeError(
            f"{key} archive member count changed: expected {expected}, found {count} "
            f"at {archive}"
        )


def append_checked(root: Path, key: str, members: list[bytes]) -> None:
    rel, expected = EXPECTED_COUNTS[key]
    archive = root / rel
    parsed = narc_append.parse(archive.read_bytes())
    if len(parsed.members) != expected:
        raise RuntimeError(
            f"Refusing append to {key}: expected base count {expected}, "
            f"found {len(parsed.members)}"
        )
    archive.write_bytes(narc_append.build(parsed, parsed.members + members))
    after = narc_append.parse(archive.read_bytes())
    if len(after.members) != expected + len(members):
        raise RuntimeError(f"{key} append count verification failed")


def build_matrix(name: str, land_data_id: int) -> bytes:
    encoded = name.encode("ascii")
    if len(encoded) > 0xFF:
        raise ValueError("Matrix internal name is too long")
    if not 0 <= land_data_id <= 0xFFFF:
        raise ValueError("land_data_id out of u16 range")
    # width, height, has-headers, has-altitudes, name-length, name, land member ID
    return bytes((1, 1, 0, 0, len(encoded))) + encoded + struct.pack(
        "<H", land_data_id
    )


def stage_matrices(hg: Path) -> None:
    dest = hg / "files/fielddata/mapmatrix/map_matrix"
    for matrix_id, suffix, internal, land_id in MATRICES:
        path = dest / f"map_matrix_{matrix_id:04d}_{suffix}.bin"
        if path.exists():
            raise RuntimeError(f"Refusing to overwrite existing matrix: {path}")
        path.write_bytes(build_matrix(internal, land_id))


def stage_noop_scripts(hg: Path) -> None:
    dest = hg / "files/fielddata/script/scr_seq"
    main = dest / "scr_seq_0965_SINNOH_TWINLEAF_EMPTY.s"
    hdr = dest / "scr_seq_0966_SINNOH_TWINLEAF_EMPTY_hdr.s"
    if main.exists() or hdr.exists():
        raise RuntimeError("DS04 no-op script IDs are already occupied")

    main.write_text(
        '#include "constants/scrcmd.h"\n'
        '\t.include "asm/macros/script.inc"\n\n'
        '\t.rodata\n\n'
        '\tScrDefEnd\n\n'
        '\t.balign 4, 0\n',
        encoding="utf-8",
    )
    hdr.write_text(
        '#include "constants/scrcmd.h"\n'
        '#include "constants/init_script_types.h"\n'
        '\t.include "asm/macros/script.inc"\n\n'
        '\t.rodata\n'
        '\t.option alignment off\n\n'
        '\tInitScriptEntryEnd\n\n'
        '\tInitScriptEnd\n',
        encoding="utf-8",
    )


def patch_map_constants(hg: Path) -> None:
    path = hg / "include/constants/maps.h"
    text = path.read_text(encoding="utf-8")
    if "MAP_SINNOH_TWINLEAF_TOWN" in text:
        raise RuntimeError("Twinleaf map constants already staged")
    if "#define MAP_ID_MAX                                        540" not in text:
        raise RuntimeError("Pinned HGSS MAP_ID_MAX is not 540")

    additions = "\n".join(
        f"#define {name:<55} {value}" for name, value in MAP_DEFINES
    )
    text = text.replace(
        "#define MAP_ID_MAX                                        540",
        additions + "\n#define MAP_ID_MAX                                        547",
    )
    path.write_text(text, encoding="utf-8")


def header_entry(
    name: str,
    matrix_const: str,
    area_data: int,
    *,
    exterior: bool,
) -> str:
    if exterior:
        map_type = "MAP_TYPE_CITY_TOWN"
        camera = 0
        follow = "MAP_FOLLOWMODE_ALLOW"
        battle = "BATTLE_BG_GENERAL"
        area_icon = 6
        bike = "TRUE"
    else:
        map_type = "MAP_TYPE_INTERIOR"
        camera = 4
        follow = "MAP_FOLLOWMODE_HEIGHT_RESTRICT"
        battle = "BATTLE_BG_BUILDING_1"
        area_icon = 9
        bike = "FALSE"

    return f"""    [{name}] = {{
                        .wildEncounterBank = ENCDATA_NA,
                        .areaDataBank = {area_data},
                        .moveModelBank = 15,
                        .worldMapX = 0,
                        .worldMapY = 0,
                        .matrixId = {matrix_const},
                        .scriptsBank = NARC_scr_seq_scr_seq_0965_SINNOH_TWINLEAF_EMPTY_bin,
                        .scriptHeaderBank = NARC_scr_seq_scr_seq_0966_SINNOH_TWINLEAF_EMPTY_hdr_bin,
                        .msgBank = NARC_msg_msg_0003_EVERYWHERE_bin,
                        .dayMusicId = SEQ_GS_T_WAKABA,
                        .nightMusicId = SEQ_GS_T_WAKABA,
                        .eventsBank = NARC_zone_event_000_DUMMY_bin,
                        .mapsec = MAPSEC_MYSTERY_ZONE,
                        .areaIcon = {area_icon},
                        .momCallIntroParam = 10,
                        .regionNo = MAP_REGION_JOHTO,
                        .weather = 0,
                        .mapType = {map_type},
                        .cameraType = {camera},
                        .followMode = {follow},
                        .battleBg = {battle},
                        .bikeAllowed = {bike},
                        .runningAllowed_Unused = TRUE,
                        .escapeRopeAllowed = FALSE,
                        .flyAllowed = FALSE,
                        .outgoingCalls = FALSE,
                        .incomingCalls = FALSE,
                        .radioSignal = FALSE,
                        }},
"""


def patch_map_headers(hg: Path) -> None:
    path = hg / "src/data/map_headers.h"
    text = path.read_text(encoding="utf-8")
    if "[MAP_SINNOH_TWINLEAF_TOWN]" in text:
        raise RuntimeError("Twinleaf map headers already staged")

    entries = [
        header_entry(
            "MAP_SINNOH_TWINLEAF_TOWN",
            "NARC_map_matrix_map_matrix_0288_SINNOH_TWINLEAF_bin",
            106,
            exterior=True,
        ),
        header_entry(
            "MAP_SINNOH_TWINLEAF_RIVAL_HOUSE_1F",
            "NARC_map_matrix_map_matrix_0290_SINNOH_TWINLEAF_RIVAL_1F_bin",
            107,
            exterior=False,
        ),
        header_entry(
            "MAP_SINNOH_TWINLEAF_RIVAL_HOUSE_2F",
            "NARC_map_matrix_map_matrix_0291_SINNOH_TWINLEAF_RIVAL_2F_bin",
            107,
            exterior=False,
        ),
        header_entry(
            "MAP_SINNOH_TWINLEAF_PLAYER_HOUSE_1F",
            "NARC_map_matrix_map_matrix_0292_SINNOH_TWINLEAF_PLAYER_1F_bin",
            107,
            exterior=False,
        ),
        header_entry(
            "MAP_SINNOH_TWINLEAF_PLAYER_HOUSE_2F",
            "NARC_map_matrix_map_matrix_0293_SINNOH_TWINLEAF_PLAYER_2F_bin",
            107,
            exterior=False,
        ),
        header_entry(
            "MAP_SINNOH_TWINLEAF_NORTHEAST_HOUSE",
            "NARC_map_matrix_map_matrix_0289_SINNOH_TWINLEAF_GENERIC_HOUSE_bin",
            107,
            exterior=False,
        ),
        header_entry(
            "MAP_SINNOH_TWINLEAF_SOUTHWEST_HOUSE",
            "NARC_map_matrix_map_matrix_0289_SINNOH_TWINLEAF_GENERIC_HOUSE_bin",
            107,
            exterior=False,
        ),
    ]

    marker = "};\n\n#endif"
    pos = text.rfind(marker)
    if pos < 0:
        raise RuntimeError("Could not locate map-header array terminator")
    text = text[:pos] + "".join(entries) + text[pos:]
    path.write_text(text, encoding="utf-8")


def patch_runtime_unused_header(hg: Path) -> None:
    """Temporarily repurpose MAP_UNUSED for HG-Engine runtime compatibility.

    This keeps the map-header array length unchanged so the base ARM9 layout is
    much closer to vanilla HeartGold while we certify the imported room.
    """
    path = hg / "src/data/map_headers.h"
    text = path.read_text(encoding="utf-8")
    rx = re.compile(
        r"    \[MAP_UNUSED\] = \{\n.*?^                        \},\n",
        re.S | re.M,
    )
    m = rx.search(text)
    if not m:
        raise RuntimeError("Could not locate MAP_UNUSED header entry")
    replacement = header_entry(
        "MAP_UNUSED",
        "NARC_map_matrix_map_matrix_0293_SINNOH_TWINLEAF_PLAYER_2F_bin",
        107,
        exterior=False,
    )
    text = text[:m.start()] + replacement + text[m.end():]
    path.write_text(text, encoding="utf-8")


def patch_test_start(hg: Path, *, runtime_compat_slot: bool = False) -> None:
    path = hg / "src/location_backup.c"
    text = path.read_text(encoding="utf-8")
    rx = re.compile(
        r"(static const Location sLocation_PlayerRoom = \{\n)"
        r"(.*?)(\n\};)",
        re.S,
    )
    m = rx.search(text)
    if not m:
        raise RuntimeError("Could not locate sLocation_PlayerRoom")
    body = m.group(2)
    body = re.sub(
        r"\.mapId\s*=\s*[^,]+,",
        ".mapId = MAP_UNUSED," if runtime_compat_slot
        else ".mapId = MAP_SINNOH_TWINLEAF_PLAYER_HOUSE_2F,",
        body,
        count=1,
    )
    body = re.sub(r"\.x\s*=\s*[^,]+,", ".x = 4,", body, count=1)
    body = re.sub(r"\.y\s*=\s*[^,]+,", ".y = 6,", body, count=1)
    body = re.sub(r"\.direction\s*=\s*[^,]+,", ".direction = 0,", body, count=1)
    text = text[:m.start()] + m.group(1) + body + m.group(3) + text[m.end():]
    path.write_text(text, encoding="utf-8")


def stage_visual_and_land_resources(hg: Path, pt: Path) -> dict:
    visual = load_json(ROOT / "platinum_port/twinleaf/visual_resources.json")
    exterior_map = model_map(ROOT / "platinum_port/twinleaf/model_map_exterior.json")
    interior_map = model_map(ROOT / "platinum_port/twinleaf/model_map_interior.json")

    # Convert six real Platinum land members in target member order.
    land_members = []
    for source_id, target_id, env in LAND_ORDER:
        source = (
            pt / f"res/field/maps/data/map_data_{source_id}.bin"
        ).read_bytes()
        mapping = exterior_map if env == "exterior" else interior_map
        converted = landconv.convert(source, model_map=mapping)
        landconv.validate_hgss(converted)
        land_members.append(converted)
    append_checked(hg, "land_data", land_members)

    # Convert the two AreaData members.
    area_members = []
    for env_name in ("exterior", "interior"):
        env = visual["environments"][env_name]
        source_json = load_json(pt / env["source_area_data"])
        payload, meta = areaconv.convert(
            source_json,
            building_tileset=env["target_prop_set"]["id"],
            map_tileset=env["target_map_texture"]["id"],
            area_type=env["area_type"],
            dynamic_texture_type=env["dynamic_texture_type"],
            light_type=env["hgss_light_type"],
        )
        if len(payload) != 8:
            raise RuntimeError(f"Unexpected AreaData size for {env_name}")
        area_members.append(payload)
    append_checked(hg, "area_data", area_members)

    # Build compact prop-set members containing only the models used by Twinleaf.
    exterior_ids = sorted(exterior_map.values())
    interior_ids = sorted(interior_map.values())
    append_checked(
        hg,
        "prop_sets",
        [propset.build(exterior_ids), propset.build(interior_ids)],
    )

    # Texture packs are native Nitro NSBTX and can be copied byte-for-byte.
    append_checked(
        hg,
        "map_textures",
        [
            (pt / visual["environments"]["exterior"]["source_map_texture"]).read_bytes(),
            (pt / visual["environments"]["interior"]["source_map_texture"]).read_bytes(),
        ],
    )
    append_checked(
        hg,
        "prop_textures",
        [
            (pt / visual["environments"]["exterior"]["source_prop_texture"]).read_bytes(),
            (pt / visual["environments"]["interior"]["source_prop_texture"]).read_bytes(),
        ],
    )

    # HGSS separates exterior and interior prop-model archives.
    ext_models = sorted(
        visual["environments"]["exterior"]["models"], key=lambda row: row["target_id"]
    )
    int_models = sorted(
        visual["environments"]["interior"]["models"], key=lambda row: row["target_id"]
    )
    append_checked(
        hg,
        "exterior_models",
        [(pt / row["source_path"]).read_bytes() for row in ext_models],
    )
    append_checked(
        hg,
        "interior_models",
        [(pt / row["source_path"]).read_bytes() for row in int_models],
    )

    return {
        key: {
            "path": rel,
            "members": len(narc_append.parse((hg / rel).read_bytes()).members),
        }
        for key, (rel, _) in EXPECTED_COUNTS.items()
    }


def verify_staged(hg: Path, *, runtime_compat_slot: bool = False) -> None:
    expected_after = {
        "land_data": 682,
        "area_data": 108,
        "prop_sets": 106,
        "map_textures": 108,
        "prop_textures": 106,
        "exterior_models": 344,
        "interior_models": 244,
    }
    for key, count in expected_after.items():
        rel, _ = EXPECTED_COUNTS[key]
        actual = len(narc_append.parse((hg / rel).read_bytes()).members)
        if actual != count:
            raise RuntimeError(f"{key}: expected staged count {count}, found {actual}")

    maps_h = (hg / "include/constants/maps.h").read_text(encoding="utf-8")
    headers_h = (hg / "src/data/map_headers.h").read_text(encoding="utf-8")
    if runtime_compat_slot:
        if "#define MAP_ID_MAX                                        540" not in maps_h:
            raise RuntimeError("Runtime compatibility mode must preserve MAP_ID_MAX 540")
        unused_pos = headers_h.find("[MAP_UNUSED]")
        if unused_pos < 0:
            raise RuntimeError("MAP_UNUSED header missing")
        unused_block = headers_h[unused_pos:unused_pos + 1800]
        if "map_matrix_0293_SINNOH_TWINLEAF_PLAYER_2F" not in unused_block:
            raise RuntimeError("MAP_UNUSED was not redirected to Twinleaf Player House 2F")
        if ".areaDataBank = 107" not in unused_block:
            raise RuntimeError("MAP_UNUSED did not receive Twinleaf interior AreaData")
    else:
        if "#define MAP_ID_MAX                                        547" not in maps_h:
            raise RuntimeError("MAP_ID_MAX staging verification failed")
        for name, _ in MAP_DEFINES:
            if f"[{name}]" not in headers_h:
                raise RuntimeError(f"Missing staged map header: {name}")

    matrix_dir = hg / "files/fielddata/mapmatrix/map_matrix"
    for matrix_id, suffix, internal, land_id in MATRICES:
        data = (matrix_dir / f"map_matrix_{matrix_id:04d}_{suffix}.bin").read_bytes()
        if data != build_matrix(internal, land_id):
            raise RuntimeError(f"Matrix {matrix_id} verification failed")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pokeheartgold", type=Path, required=True)
    ap.add_argument("--pokeplatinum", type=Path, required=True)
    ap.add_argument(
        "--test-start",
        action="store_true",
        help="Redirect HGSS player-room fallback/start to imported Platinum room",
    )
    ap.add_argument(
        "--runtime-compat-slot",
        action="store_true",
        help=(
            "Use existing MAP_UNUSED as the temporary Twinleaf Player House 2F "
            "header so the HGSS map-header array does not grow before HG-Engine."
        ),
    )
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()

    hg = args.pokeheartgold.resolve()
    pt = args.pokeplatinum.resolve()

    for key in EXPECTED_COUNTS:
        check_archive_count(hg, key)

    report = {
        "schema": 1,
        "strategy": "APPEND_ONLY",
        "archives": stage_visual_and_land_resources(hg, pt),
        "matrices": [row[0] for row in MATRICES],
        "map_headers": (
            [538] if args.runtime_compat_slot
            else [value for _, value in MAP_DEFINES]
        ),
        "scripts": [NOOP_SCRIPT_ID, NOOP_HEADER_ID],
        "runtime_compat_slot": bool(args.runtime_compat_slot),
        "test_start": bool(args.test_start),
        "test_start_map": (
            538 if args.test_start and args.runtime_compat_slot
            else 544 if args.test_start
            else None
        ),
        "test_start_x": 4 if args.test_start else None,
        "test_start_y": 6 if args.test_start else None,
        "test_start_direction": 0 if args.test_start else None,
    }

    stage_matrices(hg)
    stage_noop_scripts(hg)
    if args.runtime_compat_slot:
        patch_runtime_unused_header(hg)
    else:
        patch_map_constants(hg)
        patch_map_headers(hg)
    if args.test_start:
        patch_test_start(hg, runtime_compat_slot=args.runtime_compat_slot)
    verify_staged(hg, runtime_compat_slot=args.runtime_compat_slot)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
