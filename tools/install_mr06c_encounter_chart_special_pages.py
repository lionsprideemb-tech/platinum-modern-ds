#!/usr/bin/env python3
"""MR06C — complete the player-facing Encounter Chart special-resource pages.

Adds two virtual pages after MR06B's 158 standard encounter resources:
158: Honey Trees — live Common/Uncommon/Rare tables read from encdata_ex.narc.
159: Great Marsh Info — explicitly informational; no daily RNG availability gate.

The Honey page reads the same runtime NARC members used by HoneyTree_GetSpecies.
No duplicate encounter database is created.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HONEY = "encounters_honey_tree"
LOOKOUT = "encounters_great_marsh_lookout"

MESSAGES = [
    ("StartMenu_Text_EncounterArea_158", "Honey Trees"),
    ("StartMenu_Text_EncounterArea_159", "Great Marsh Info"),
    ("StartMenu_Text_EncounterHoneyCommon", "COMMON"),
    ("StartMenu_Text_EncounterHoneyUncommon", "UNCOMMON"),
    ("StartMenu_Text_EncounterHoneyRare", "RARE"),
    ("StartMenu_Text_EncounterHoneyRule", "1 HONEY = INSTANT ENCOUNTER"),
    ("StartMenu_Text_EncounterMarshInfo1", "BINOCULARS: INFORMATION ONLY"),
    ("StartMenu_Text_EncounterMarshInfo2", "ALL 6 MARSH AREAS STAY LIVE"),
    ("StartMenu_Text_EncounterMarshInfo3", "NO DAILY RNG GATE"),
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def patch_text(root: Path) -> None:
    path = root / "res/text/start_menu.json"
    data = load_json(path)
    messages = data.get("messages")
    if not isinstance(messages, list):
        raise SystemExit("MR06C start-menu text bank missing messages")

    ids = {row.get("id") for row in messages}
    for msg_id, text in MESSAGES:
        if msg_id not in ids:
            messages.append({"id": msg_id, "en_US": text})
            ids.add(msg_id)

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_source(root: Path) -> None:
    path = root / "src/start_menu.c"

    replace_once(
        path,
        '#include "constants/heap.h"\n',
        '#include "constants/heap.h"\n#include "constants/narc.h"\n',
        "MR06C NARC include",
    )

    struct_anchor = """typedef struct MercuryEncounterChartDisplayRow {
    int species;
    u8 minLevel;
    u8 maxLevel;
    u8 chancePercent;
} MercuryEncounterChartDisplayRow;
"""
    struct_insert = struct_anchor + """
#define MERCURY_ENCOUNTER_CHART_STANDARD_AREAS 158
#define MERCURY_ENCOUNTER_CHART_HONEY_AREA 158
#define MERCURY_ENCOUNTER_CHART_MARSH_INFO_AREA 159
#define MERCURY_ENCOUNTER_CHART_TOTAL_AREAS 160
#define MERCURY_HONEY_TIER_COUNT 3
#define MERCURY_HONEY_SLOT_COUNT 6

static const u8 sMercuryHoneyTierNarcMembers[MERCURY_HONEY_TIER_COUNT] = { 2, 3, 4 };
static const u8 sMercuryHoneyTierOdds[MERCURY_HONEY_TIER_COUNT] = { 70, 20, 10 };
static const u8 sMercuryHoneySlotOdds[MERCURY_HONEY_SLOT_COUNT] = { 40, 20, 20, 10, 5, 5 };

static u32 StartMenu_EncounterHoneyTierText(int tier)
{
    if (tier == 0) {
        return StartMenu_Text_EncounterHoneyCommon;
    }
    if (tier == 1) {
        return StartMenu_Text_EncounterHoneyUncommon;
    }
    return StartMenu_Text_EncounterHoneyRare;
}
"""
    replace_once(path, struct_anchor, struct_insert, "MR06C special-page constants")

    build_anchor = """    return rowCount;
}

static enum MercuryEncounterChartMethod StartMenu_EncounterFirstMethod"""
    build_helper = """    return rowCount;
}

static int StartMenu_EncounterBuildHoneyRows(int tier, MercuryEncounterChartDisplayRow *rows)
{
    tier %= MERCURY_HONEY_TIER_COUNT;

    int *speciesTable = NARC_AllocAtEndAndReadWholeMemberByIndexPair(
        NARC_INDEX_ARC__ENCDATA_EX,
        sMercuryHoneyTierNarcMembers[tier],
        HEAP_ID_FIELD2
    );
    int rowCount = 0;

    for (int i = 0; i < MERCURY_HONEY_SLOT_COUNT; i++) {
        int species = speciesTable[i];
        int found = -1;

        if (species == SPECIES_NONE) {
            continue;
        }

        for (int row = 0; row < rowCount; row++) {
            if (rows[row].species == species) {
                found = row;
                break;
            }
        }

        if (found < 0) {
            found = rowCount++;
            rows[found].species = species;
            rows[found].minLevel = 5;
            rows[found].maxLevel = 15;
            rows[found].chancePercent = 0;
        }

        rows[found].chancePercent += sMercuryHoneySlotOdds[i];
    }

    Heap_Free(speciesTable);
    return rowCount;
}

static enum MercuryEncounterChartMethod StartMenu_EncounterFirstMethod"""
    replace_once(path, build_anchor, build_helper, "MR06C Honey row builder")

    replace_once(
        path,
        """    MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);

    Window_FillTilemap(window, 15);
""",
        """    if (menu->encounterChartArea < MERCURY_ENCOUNTER_CHART_STANDARD_AREAS) {
        MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);
    }

    Window_FillTilemap(window, 15);
""",
        "MR06C special-page safe load",
    )

    draw_anchor = """    enum MercuryEncounterChartMethod method = (enum MercuryEncounterChartMethod)menu->encounterChartMethod;

    if (method >= MERCURY_ENCOUNTER_METHOD_MAX || !MercuryEncounterChart_HasMethod(&encounters, method)) {
"""
    draw_special = """    if (menu->encounterChartArea == MERCURY_ENCOUNTER_CHART_HONEY_AREA) {
        int tier = menu->encounterChartMethod % MERCURY_HONEY_TIER_COUNT;
        menu->encounterChartMethod = tier;

        StartMenu_EncounterPrintMessage(window, loader, StartMenu_EncounterHoneyTierText(tier), 0, 20);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterRate, 156, 20);
        StartMenu_EncounterPrintNumber(window, sMercuryHoneyTierOdds[tier], 3, 194, 20);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterPokemon, 0, 38);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterLevel, 112, 38);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterOdds, 180, 38);

        int rowCount = StartMenu_EncounterBuildHoneyRows(tier, rows);
        int pages = (rowCount + 3) / 4;
        if (pages < 1) {
            pages = 1;
        }
        if (menu->encounterChartPage >= pages) {
            menu->encounterChartPage = 0;
        }

        int start = menu->encounterChartPage * 4;
        int end = start + 4;
        if (end > rowCount) {
            end = rowCount;
        }

        for (int rowIndex = start; rowIndex < end; rowIndex++) {
            int line = rowIndex - start;
            int y = 56 + line * 16;
            MercuryEncounterChartDisplayRow *row = &rows[rowIndex];

            String *species = MessageUtil_SpeciesName(row->species, HEAP_ID_FIELD2);
            Text_AddPrinterWithParams(window, FONT_SYSTEM, species, 0, y, TEXT_SPEED_NO_TRANSFER, NULL);
            String_Free(species);
            StartMenu_EncounterPrintNumber(window, row->minLevel, 3, 112, y);
            StartMenu_EncounterPrintNumber(window, row->maxLevel, 3, 142, y);
            StartMenu_EncounterPrintNumber(window, row->chancePercent, 3, 184, y);
        }

        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterHoneyRule, 0, 108);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterControls1, 0, 124);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterControls2, 0, 140);
        MessageLoader_Free(loader);
        Window_ScheduleCopyToVRAM(window);
        return;
    }

    if (menu->encounterChartArea == MERCURY_ENCOUNTER_CHART_MARSH_INFO_AREA) {
        menu->encounterChartMethod = 0;
        menu->encounterChartPage = 0;
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterMarshInfo1, 0, 28);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterMarshInfo2, 0, 52);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterMarshInfo3, 0, 76);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterControls1, 0, 124);
        StartMenu_EncounterPrintMessage(window, loader, StartMenu_Text_EncounterControls2, 0, 140);
        MessageLoader_Free(loader);
        Window_ScheduleCopyToVRAM(window);
        return;
    }

    enum MercuryEncounterChartMethod method = (enum MercuryEncounterChartMethod)menu->encounterChartMethod;

    if (method >= MERCURY_ENCOUNTER_METHOD_MAX || !MercuryEncounterChart_HasMethod(&encounters, method)) {
"""
    replace_once(path, draw_anchor, draw_special, "MR06C special-page drawing")

    replace_once(
        path,
        "    int areaCount = MercuryEncounterChart_GetAreaCount();\n",
        "    int areaCount = MERCURY_ENCOUNTER_CHART_TOTAL_AREAS;\n",
        "MR06C area count",
    )

    redraw_anchor = """    if (redraw) {
        WildEncounters encounters;
        MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);
        menu->encounterChartMethod = StartMenu_EncounterFirstMethod(&encounters);
        menu->encounterChartPage = 0;
        Sound_PlayEffect(SEQ_SE_DP_SELECT78_sseq);
        StartMenu_DrawEncounterChart(fieldTask);
        return;
    }

    WildEncounters encounters;
    MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);
"""
    redraw_new = """    if (redraw) {
        if (menu->encounterChartArea < MERCURY_ENCOUNTER_CHART_STANDARD_AREAS) {
            WildEncounters encounters;
            MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);
            menu->encounterChartMethod = StartMenu_EncounterFirstMethod(&encounters);
        } else {
            menu->encounterChartMethod = 0;
        }

        menu->encounterChartPage = 0;
        Sound_PlayEffect(SEQ_SE_DP_SELECT78_sseq);
        StartMenu_DrawEncounterChart(fieldTask);
        return;
    }

    if (menu->encounterChartArea == MERCURY_ENCOUNTER_CHART_HONEY_AREA) {
        if (JOY_NEW(PAD_KEY_LEFT)) {
            menu->encounterChartMethod = (menu->encounterChartMethod + MERCURY_HONEY_TIER_COUNT - 1) % MERCURY_HONEY_TIER_COUNT;
            menu->encounterChartPage = 0;
            redraw = TRUE;
        } else if (JOY_NEW(PAD_KEY_RIGHT)) {
            menu->encounterChartMethod = (menu->encounterChartMethod + 1) % MERCURY_HONEY_TIER_COUNT;
            menu->encounterChartPage = 0;
            redraw = TRUE;
        } else if (JOY_NEW(PAD_BUTTON_A)) {
            MercuryEncounterChartDisplayRow rows[MAX_GRASS_ENCOUNTERS];
            int rowCount = StartMenu_EncounterBuildHoneyRows(menu->encounterChartMethod, rows);
            int pages = (rowCount + 3) / 4;
            if (pages < 1) {
                pages = 1;
            }
            if (pages > 1) {
                menu->encounterChartPage = (menu->encounterChartPage + 1) % pages;
                redraw = TRUE;
            }
        }

        if (redraw) {
            Sound_PlayEffect(SEQ_SE_DP_SELECT78_sseq);
            StartMenu_DrawEncounterChart(fieldTask);
        }
        return;
    }

    if (menu->encounterChartArea == MERCURY_ENCOUNTER_CHART_MARSH_INFO_AREA) {
        return;
    }

    WildEncounters encounters;
    MercuryEncounterChart_LoadArea(menu->encounterChartArea, &encounters);
"""
    replace_once(path, redraw_anchor, redraw_new, "MR06C special-page input")


def validate(root: Path, manifest: dict[str, Any]) -> dict[str, int]:
    areas = manifest.get("areas")
    if not isinstance(areas, dict):
        raise SystemExit("MR06C manifest areas missing")

    honey = areas.get(HONEY)
    lookout = areas.get(LOOKOUT)
    if not isinstance(honey, dict) or not isinstance(lookout, dict):
        raise SystemExit("MR06C special resources missing")

    honey_species = []
    for tier in ("common", "uncommon", "rare"):
        values = honey.get(tier)
        if not isinstance(values, list) or len(values) != 6:
            raise SystemExit(f"MR06C Honey {tier} must contain six slots")
        honey_species.extend(values)

    if len(set(honey_species)) != 18:
        raise SystemExit("MR06C expected 18 unique premium Honey Tree species")
    if any("BURMY" in species for species in honey_species):
        raise SystemExit("MR06C Burmy regression in Honey Tree pool")

    source = (root / "src/start_menu.c").read_text()
    for token in (
        "MERCURY_ENCOUNTER_CHART_TOTAL_AREAS 160",
        "MERCURY_ENCOUNTER_CHART_HONEY_AREA 158",
        "MERCURY_ENCOUNTER_CHART_MARSH_INFO_AREA 159",
        "NARC_INDEX_ARC__ENCDATA_EX",
        "StartMenu_EncounterBuildHoneyRows",
        "sMercuryHoneyTierOdds",
        "sMercuryHoneySlotOdds",
    ):
        if token not in source:
            raise SystemExit(f"MR06C source missing {token}")

    bank = load_json(root / "res/text/start_menu.json")
    ids = {row.get("id") for row in bank.get("messages", [])}
    for msg_id, _ in MESSAGES:
        if msg_id not in ids:
            raise SystemExit(f"MR06C message missing {msg_id}")

    area_ids = [
        value for value in ids
        if isinstance(value, str) and value.startswith("StartMenu_Text_EncounterArea_")
    ]
    if len(area_ids) != 160:
        raise SystemExit(f"MR06C expected 160 area labels, found {len(area_ids)}")

    return {
        "honey_unique": len(set(honey_species)),
        "marsh_before": len(lookout.get("before_national_dex", [])),
        "marsh_after": len(lookout.get("after_national_dex", [])),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr06c-encounter-chart-special-pages.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    manifest = load_json(args.manifest)

    patch_text(root)
    patch_source(root)
    info = validate(root, manifest)

    report = {
        "gate": "MERCURY_MR06C_ENCOUNTER_CHART_SPECIAL_PAGES",
        "status": "PASS",
        "player_facing_area_count": 160,
        "standard_area_count": 158,
        "special_page_count": 2,
        "honey_tree_page": True,
        "great_marsh_info_page": True,
        "honey_reads_live_encdata_narc": True,
        "honey_tree_unique_species": info["honey_unique"],
        "honey_tree_levels": [5, 15],
        "honey_tier_distribution_percent": [70, 20, 10],
        "honey_slot_distribution_percent": [40, 20, 20, 10, 5, 5],
        "honey_instant_rule_shown": True,
        "great_marsh_daily_rng_gate_shown_as_disabled": True,
        "great_marsh_binoculars_shown_as_informational": True,
        "great_marsh_lookout_entries_before_natdex": info["marsh_before"],
        "great_marsh_lookout_entries_after_natdex": info["marsh_after"],
        "duplicate_encounter_database_created": False,
        "mr06b_standard_browser_retained": True,
    }

    if info["marsh_before"] != 32 or info["marsh_after"] != 32:
        raise SystemExit("MR06C Great Marsh lookout registry shape changed")

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
