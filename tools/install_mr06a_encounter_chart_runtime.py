#!/usr/bin/env python3
"""MR06A — install the DS-native Encounter Chart runtime/browser foundation.

This phase deliberately separates *data access* from *presentation*.

MR05M already exports the complete player-facing chart. MR06A makes the same
sealed runtime encounter data queryable from native DS code without creating a
second hand-maintained encounter database.

Installed API:
- enumerate all 158 standard player-facing encounter resources;
- resolve the current map to its canonical encounter resource;
- load any browsable area's live WildEncounters member;
- query Morning/Day/Evening/Night land slots;
- query Surf / Old Rod / Good Rod / Super Rod slots;
- expose encounter rates, exact slot odds, level ranges, and map-label IDs.

Honey Trees and Great Marsh lookout metadata remain separate special-resource
views. The 25 MR05L orphan encounter members remain excluded.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

UNKNOWN_NAMES = {f"encounters_unknown_{n}" for n in range(533, 558)}
HONEY = "encounters_honey_tree"
LOOKOUT = "encounters_great_marsh_lookout"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def parse_resource_headers(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    block_re = re.compile(r"\[(MAP_HEADER_[A-Z0-9_]+)\]\s*=\s*\{(.*?)\n    \},", re.S)

    for match in block_re.finditer(text):
        header = match.group(1)
        block = match.group(2)
        wild = re.search(r"\.wildEncountersArchiveID\s*=\s*(encounters_[A-Za-z0-9_]+),", block)
        if not wild:
            continue
        resource = wild.group(1)
        result.setdefault(resource, [])
        if header not in result[resource]:
            result[resource].append(header)

    return result


TURNBACK_RUNTIME_LINKS = {
    "MAP_HEADER_TURNBACK_CAVE_ENTRANCE": "encounters_turnback_cave_entrance",
    "MAP_HEADER_TURNBACK_CAVE_PILLAR_ROOM": "encounters_turnback_cave_pillar_room",
    "MAP_HEADER_TURNBACK_CAVE_PILLAR_3_ROOM_6": "encounters_turnback_cave_pillar_3_room_6",
}

NO_RANDOM_BROWSABLE_HEADERS = {
    "encounters_turnback_cave_giratina_room": "MAP_HEADER_TURNBACK_CAVE_GIRATINA_ROOM",
}


def patch_turnback_runtime_links(root: Path) -> None:
    """Activate the three authored Turnback resources Platinum left disconnected.

    MR05E deliberately authored Entrance, generic Pillar Room, and Pillar 3
    Room 6 as ordinary maze ecology. Vanilla Platinum leaves those three map
    headers at ENCOUNTERS_NONE even though matching encounter NARC members
    exist. Giratina's terminal room intentionally remains ENCOUNTERS_NONE.
    """

    path = root / "include/data/map_headers.h"
    text = path.read_text()

    for header, encounter in TURNBACK_RUNTIME_LINKS.items():
        marker = f"[{header}] = {{"
        start = text.find(marker)
        if start < 0:
            raise SystemExit(f"MR06A missing Turnback map header {header}")
        end = text.find("\n    },", start)
        if end < 0:
            raise SystemExit(f"MR06A unterminated Turnback map header {header}")

        block = text[start:end + 7]
        old = ".wildEncountersArchiveID = ENCOUNTERS_NONE,"
        new = f".wildEncountersArchiveID = {encounter},"
        if old not in block:
            if new in block:
                continue
            raise SystemExit(f"{header}: expected ENCOUNTERS_NONE before MR06A link repair")

        block = block.replace(old, new, 1)
        text = text[:start] + block + text[end + 7:]

    # Terminal Giratina room must remain no-random by sealed MR05E policy.
    marker = "[MAP_HEADER_TURNBACK_CAVE_GIRATINA_ROOM] = {"
    start = text.find(marker)
    end = text.find("\n    },", start)
    terminal = text[start:end + 7]
    if ".wildEncountersArchiveID = ENCOUNTERS_NONE," not in terminal:
        raise SystemExit("MR06A must preserve Giratina terminal room as no-random")

    path.write_text(text)


def build_area_header(root: Path, manifest: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != 1 or manifest.get("area_count") != 185:
        raise SystemExit("MR06A requires the final 185-resource encounter manifest")
    if audit.get("status") != "PASS" or audit.get("runtime_active_unknown_resources") != 0:
        raise SystemExit("MR06A requires a passing MR05L orphan-resource audit")

    areas = manifest.get("areas")
    if not isinstance(areas, dict) or len(areas) != 185:
        raise SystemExit("MR06A manifest areas object is incomplete")

    standard_resources = []
    for name, data in areas.items():
        if name in UNKNOWN_NAMES or name in (HONEY, LOOKOUT):
            continue
        if isinstance(data, dict) and "land_encounters" in data:
            standard_resources.append(name)

    if len(standard_resources) != 158:
        raise SystemExit(f"MR06A expected 158 standard browsable resources, found {len(standard_resources)}")

    map_headers_path = root / "include/data/map_headers.h"
    resource_headers = parse_resource_headers(map_headers_path.read_text())

    resolved: list[tuple[str, str]] = []
    unresolved = []
    alternate_header_count = 0

    for resource in sorted(standard_resources):
        headers = resource_headers.get(resource, [])
        if not headers:
            fallback = NO_RANDOM_BROWSABLE_HEADERS.get(resource)
            if fallback is None:
                unresolved.append(resource)
                continue
            headers = [fallback]
        alternate_header_count += max(0, len(headers) - 1)
        resolved.append((resource, headers[0]))

    if unresolved:
        raise SystemExit("MR06A could not resolve map headers for: " + ", ".join(unresolved))
    if len(resolved) != 158:
        raise SystemExit("MR06A resolved resource count mismatch")

    header_path = root / "include/mercury_encounter_chart_areas.h"
    lines = [
        "#ifndef POKEPLATINUM_MERCURY_ENCOUNTER_CHART_AREAS_H",
        "#define POKEPLATINUM_MERCURY_ENCOUNTER_CHART_AREAS_H",
        "",
        '#include "generated/map_headers.h"',
        "",
        f"#define MERCURY_ENCOUNTER_CHART_AREA_COUNT {len(resolved)}",
        "",
        "static const enum MapHeaderID gMercuryEncounterChartMapHeaders[MERCURY_ENCOUNTER_CHART_AREA_COUNT] = {",
    ]
    for resource, header in resolved:
        lines.append(f"    {header}, // {resource}")
    lines.extend([
        "};",
        "",
        "#endif // POKEPLATINUM_MERCURY_ENCOUNTER_CHART_AREAS_H",
        "",
    ])
    header_path.write_text("\n".join(lines))

    return {
        "standard_resource_count": len(standard_resources),
        "resolved_resource_count": len(resolved),
        "alternate_header_count": alternate_header_count,
        "generated_area_header": str(header_path.relative_to(root)),
    }


def patch_runtime_header(root: Path) -> None:
    path = root / "include/overlay006/wild_encounters.h"

    type_anchor = """} WildEncounters;

#include "field_battle_data_transfer.h"
"""
    type_block = """} WildEncounters;

enum MercuryEncounterChartMethod {
    MERCURY_ENCOUNTER_METHOD_LAND_MORNING = 0,
    MERCURY_ENCOUNTER_METHOD_LAND_DAY,
    MERCURY_ENCOUNTER_METHOD_LAND_EVENING,
    MERCURY_ENCOUNTER_METHOD_LAND_NIGHT,
    MERCURY_ENCOUNTER_METHOD_SURF,
    MERCURY_ENCOUNTER_METHOD_OLD_ROD,
    MERCURY_ENCOUNTER_METHOD_GOOD_ROD,
    MERCURY_ENCOUNTER_METHOD_SUPER_ROD,
    MERCURY_ENCOUNTER_METHOD_MAX
};

typedef struct MercuryEncounterChartSlot {
    int species;
    u8 minLevel;
    u8 maxLevel;
    u8 chancePercent;
    u8 padding;
} MercuryEncounterChartSlot;

#include "field_battle_data_transfer.h"
"""
    replace_once(path, type_anchor, type_block, "MR06A chart types")

    proto_anchor = """void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *param1, int *param2);
"""
    proto_block = """int MercuryEncounterChart_GetAreaCount(void);
enum MapHeaderID MercuryEncounterChart_GetAreaMapHeader(int areaIndex);
u32 MercuryEncounterChart_GetAreaLabelTextID(int areaIndex);
int MercuryEncounterChart_FindAreaByMapHeader(enum MapHeaderID mapHeaderID);
void MercuryEncounterChart_LoadArea(int areaIndex, WildEncounters *encounterData);
enum MercuryEncounterChartMethod MercuryEncounterChart_GetCurrentLandMethod(void);
BOOL MercuryEncounterChart_HasMethod(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method);
int MercuryEncounterChart_GetEncounterRate(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method);
int MercuryEncounterChart_GetSlotCount(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method);
BOOL MercuryEncounterChart_GetSlot(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method, int slotIndex, MercuryEncounterChartSlot *slot);

void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *param1, int *param2);
"""
    replace_once(path, proto_anchor, proto_block, "MR06A chart prototypes")


def patch_runtime_c(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"

    include_anchor = """#include "map_header_data.h"
#include "map_tile_behavior.h"
"""
    include_block = """#include "map_header_data.h"
#include "mercury_encounter_chart_areas.h"
#include "map_tile_behavior.h"
"""
    replace_once(path, include_anchor, include_block, "MR06A area header include")

    func_anchor = """void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *timedSlot1, int *timedSlot2)
{
"""
    helpers = """static const u8 sMercuryEncounterChartLandWeights[MAX_GRASS_ENCOUNTERS] = {
    20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1
};

static const u8 sMercuryEncounterChartWaterWeights[MAX_WATER_ENCOUNTERS] = {
    60, 30, 5, 4, 1
};

int MercuryEncounterChart_GetAreaCount(void)
{
    return MERCURY_ENCOUNTER_CHART_AREA_COUNT;
}

enum MapHeaderID MercuryEncounterChart_GetAreaMapHeader(int areaIndex)
{
    if (areaIndex < 0 || areaIndex >= MERCURY_ENCOUNTER_CHART_AREA_COUNT) {
        return MAP_HEADER_MYSTERY_ZONE;
    }

    return gMercuryEncounterChartMapHeaders[areaIndex];
}

u32 MercuryEncounterChart_GetAreaLabelTextID(int areaIndex)
{
    enum MapHeaderID mapHeaderID = MercuryEncounterChart_GetAreaMapHeader(areaIndex);
    return MapHeader_GetMapLabelTextID(mapHeaderID);
}

int MercuryEncounterChart_FindAreaByMapHeader(enum MapHeaderID mapHeaderID)
{
    // Exact header matching comes first so intentionally encounter-free areas
    // such as Giratina's terminal room can still display "No random encounters."
    for (int i = 0; i < MERCURY_ENCOUNTER_CHART_AREA_COUNT; i++) {
        if (gMercuryEncounterChartMapHeaders[i] == mapHeaderID) {
            return i;
        }
    }

    if (!MapHeader_HasWildEncounters(mapHeaderID)) {
        return -1;
    }

    u32 encounterArchiveID = MapHeader_GetWildEncountersArchiveID(mapHeaderID);

    for (int i = 0; i < MERCURY_ENCOUNTER_CHART_AREA_COUNT; i++) {
        enum MapHeaderID candidate = gMercuryEncounterChartMapHeaders[i];

        if (MapHeader_HasWildEncounters(candidate)
            && MapHeader_GetWildEncountersArchiveID(candidate) == encounterArchiveID) {
            return i;
        }
    }

    return -1;
}

void MercuryEncounterChart_LoadArea(int areaIndex, WildEncounters *encounterData)
{
    enum MapHeaderID mapHeaderID = MercuryEncounterChart_GetAreaMapHeader(areaIndex);
    MapHeaderData_LoadWildEncounters(encounterData, mapHeaderID);
}

enum MercuryEncounterChartMethod MercuryEncounterChart_GetCurrentLandMethod(void)
{
    // Keep the chart selector on the exact same Mercury RTC windows used by
    // MR05O's authored encounter runtime, including the 04:00 and 20:00
    // boundary corrections.
    RTCTime mercuryTime;
    RTC_GetCurrentTime(&mercuryTime);

    if (mercuryTime.hour >= 5 && mercuryTime.hour < 10) {
        return MERCURY_ENCOUNTER_METHOD_LAND_MORNING;
    }

    if (mercuryTime.hour >= 10 && mercuryTime.hour < 17) {
        return MERCURY_ENCOUNTER_METHOD_LAND_DAY;
    }

    if (mercuryTime.hour >= 17 && mercuryTime.hour < 21) {
        return MERCURY_ENCOUNTER_METHOD_LAND_EVENING;
    }

    return MERCURY_ENCOUNTER_METHOD_LAND_NIGHT;
}

BOOL MercuryEncounterChart_HasMethod(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method)
{
    if (encounterData == NULL) {
        return FALSE;
    }

    switch (method) {
    case MERCURY_ENCOUNTER_METHOD_LAND_MORNING:
    case MERCURY_ENCOUNTER_METHOD_LAND_DAY:
    case MERCURY_ENCOUNTER_METHOD_LAND_EVENING:
    case MERCURY_ENCOUNTER_METHOD_LAND_NIGHT:
        return encounterData->grassEncounters.encounterRate > 0;

    case MERCURY_ENCOUNTER_METHOD_SURF:
        return encounterData->surfEncounters.encounterRate > 0;

    case MERCURY_ENCOUNTER_METHOD_OLD_ROD:
        return encounterData->oldRodEncounters.encounterRate > 0;

    case MERCURY_ENCOUNTER_METHOD_GOOD_ROD:
        return encounterData->goodRodEncounters.encounterRate > 0;

    case MERCURY_ENCOUNTER_METHOD_SUPER_ROD:
        return encounterData->superRodEncounters.encounterRate > 0;

    default:
        return FALSE;
    }
}

int MercuryEncounterChart_GetEncounterRate(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method)
{
    if (!MercuryEncounterChart_HasMethod(encounterData, method)) {
        return 0;
    }

    switch (method) {
    case MERCURY_ENCOUNTER_METHOD_LAND_MORNING:
    case MERCURY_ENCOUNTER_METHOD_LAND_DAY:
    case MERCURY_ENCOUNTER_METHOD_LAND_EVENING:
    case MERCURY_ENCOUNTER_METHOD_LAND_NIGHT:
        return encounterData->grassEncounters.encounterRate;

    case MERCURY_ENCOUNTER_METHOD_SURF:
        return encounterData->surfEncounters.encounterRate;

    case MERCURY_ENCOUNTER_METHOD_OLD_ROD:
        return encounterData->oldRodEncounters.encounterRate;

    case MERCURY_ENCOUNTER_METHOD_GOOD_ROD:
        return encounterData->goodRodEncounters.encounterRate;

    case MERCURY_ENCOUNTER_METHOD_SUPER_ROD:
        return encounterData->superRodEncounters.encounterRate;

    default:
        return 0;
    }
}

int MercuryEncounterChart_GetSlotCount(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method)
{
    if (!MercuryEncounterChart_HasMethod(encounterData, method)) {
        return 0;
    }

    if (method <= MERCURY_ENCOUNTER_METHOD_LAND_NIGHT) {
        return MAX_GRASS_ENCOUNTERS;
    }

    return MAX_WATER_ENCOUNTERS;
}

BOOL MercuryEncounterChart_GetSlot(const WildEncounters *encounterData, enum MercuryEncounterChartMethod method, int slotIndex, MercuryEncounterChartSlot *slot)
{
    if (slot == NULL || !MercuryEncounterChart_HasMethod(encounterData, method)) {
        return FALSE;
    }

    if (method <= MERCURY_ENCOUNTER_METHOD_LAND_NIGHT) {
        if (slotIndex < 0 || slotIndex >= MAX_GRASS_ENCOUNTERS) {
            return FALSE;
        }

        if (encounterData->mercuryTimedGrassMagic == MERCURY_TIMED_GRASS_MAGIC) {
            const MercuryGrassEncounter *source = &encounterData->mercuryTimedGrass[method][slotIndex];
            slot->species = source->species;
            slot->minLevel = source->minLevel;
            slot->maxLevel = source->maxLevel;
        } else {
            const GrassEncounter *source = &encounterData->grassEncounters.encounters[slotIndex];
            slot->species = source->species;
            slot->minLevel = source->level;
            slot->maxLevel = source->level;
        }

        slot->chancePercent = sMercuryEncounterChartLandWeights[slotIndex];
        slot->padding = 0;
        return TRUE;
    }

    if (slotIndex < 0 || slotIndex >= MAX_WATER_ENCOUNTERS) {
        return FALSE;
    }

    const WaterEncounter *source = NULL;

    switch (method) {
    case MERCURY_ENCOUNTER_METHOD_SURF:
        source = &encounterData->surfEncounters.encounters[slotIndex];
        break;
    case MERCURY_ENCOUNTER_METHOD_OLD_ROD:
        source = &encounterData->oldRodEncounters.encounters[slotIndex];
        break;
    case MERCURY_ENCOUNTER_METHOD_GOOD_ROD:
        source = &encounterData->goodRodEncounters.encounters[slotIndex];
        break;
    case MERCURY_ENCOUNTER_METHOD_SUPER_ROD:
        source = &encounterData->superRodEncounters.encounters[slotIndex];
        break;
    default:
        return FALSE;
    }

    slot->species = source->species;
    slot->minLevel = source->minLevel;
    slot->maxLevel = source->maxLevel;
    slot->chancePercent = sMercuryEncounterChartWaterWeights[slotIndex];
    slot->padding = 0;
    return TRUE;
}

void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *timedSlot1, int *timedSlot2)
{
"""
    replace_once(path, func_anchor, helpers, "MR06A chart runtime helpers")


def validate(root: Path) -> None:
    header = (root / "include/overlay006/wild_encounters.h").read_text()
    runtime = (root / "src/overlay006/wild_encounters.c").read_text()
    areas = (root / "include/mercury_encounter_chart_areas.h").read_text()

    required_header = (
        "enum MercuryEncounterChartMethod",
        "MercuryEncounterChartSlot",
        "MercuryEncounterChart_GetAreaCount",
        "MercuryEncounterChart_GetSlot",
    )
    for token in required_header:
        if token not in header:
            raise SystemExit(f"MR06A header missing {token}")

    required_runtime = (
        "gMercuryEncounterChartMapHeaders",
        "MercuryEncounterChart_FindAreaByMapHeader",
        "MercuryEncounterChart_GetCurrentLandMethod",
        "MERCURY_TIMED_GRASS_MAGIC",
        "sMercuryEncounterChartLandWeights",
        "sMercuryEncounterChartWaterWeights",
    )
    for token in required_runtime:
        if token not in runtime:
            raise SystemExit(f"MR06A runtime missing {token}")

    if "#define MERCURY_ENCOUNTER_CHART_AREA_COUNT 158" not in areas:
        raise SystemExit("MR06A generated area count is not 158")

    map_headers = (root / "include/data/map_headers.h").read_text()
    for header, encounter in TURNBACK_RUNTIME_LINKS.items():
        marker = f"[{header}] = {{"
        start = map_headers.index(marker)
        end = map_headers.index("\n    },", start)
        block = map_headers[start:end]
        if f".wildEncountersArchiveID = {encounter}," not in block:
            raise SystemExit(f"MR06A Turnback runtime link missing: {header} -> {encounter}")

    terminal_start = map_headers.index("[MAP_HEADER_TURNBACK_CAVE_GIRATINA_ROOM] = {")
    terminal_end = map_headers.index("\n    },", terminal_start)
    if ".wildEncountersArchiveID = ENCOUNTERS_NONE," not in map_headers[terminal_start:terminal_end]:
        raise SystemExit("MR06A Giratina terminal no-random policy regressed")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("mr05l_audit", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06a-encounter-chart-runtime.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    manifest = load_json(args.manifest)
    audit = load_json(args.mr05l_audit)

    patch_turnback_runtime_links(root)
    area_info = build_area_header(root, manifest, audit)
    patch_runtime_header(root)
    patch_runtime_c(root)
    validate(root)

    full_tod = sum(
        1
        for name, data in manifest["areas"].items()
        if name not in UNKNOWN_NAMES
        and isinstance(data, dict)
        and "mercury_tod_land" in data
    )

    report = {
        "gate": "MERCURY_MR06A_ENCOUNTER_CHART_RUNTIME",
        "status": "PASS",
        "standard_browsable_resource_count": area_info["standard_resource_count"],
        "resolved_resource_count": area_info["resolved_resource_count"],
        "alternate_map_header_count": area_info["alternate_header_count"],
        "generated_area_header": area_info["generated_area_header"],
        "full_tod_resource_count": full_tod,
        "turnback_runtime_links_repaired": len(TURNBACK_RUNTIME_LINKS),
        "turnback_giratina_terminal_no_random_preserved": True,
        "supported_land_periods": ["morning", "day", "evening", "night"],
        "period_windows": {
            "morning": "05:00-09:59",
            "day": "10:00-16:59",
            "evening": "17:00-20:59",
            "night": "21:00-04:59",
        },
        "period_selector_matches_mr05o_exact_rtc_windows": True,
        "supported_methods": [
            "land_morning",
            "land_day",
            "land_evening",
            "land_night",
            "surf",
            "old_rod",
            "good_rod",
            "super_rod",
        ],
        "land_slot_weights_percent": [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1],
        "water_slot_weights_percent": [60, 30, 5, 4, 1],
        "honey_tree_special_resource_deferred_to_ui_adapter": True,
        "great_marsh_lookout_informational_resource_deferred_to_ui_adapter": True,
        "orphan_unknown_resources_excluded": len(UNKNOWN_NAMES),
        "runtime_uses_installed_encounter_narc": True,
        "second_hand_authored_encounter_database_created": False,
        "ready_for_native_ds_browser_ui": True,
    }
    if full_tod != 144:
        raise SystemExit(f"MR06A expected 144 TOD resources, found {full_tod}")

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
