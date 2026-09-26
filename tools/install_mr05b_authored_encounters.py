#!/usr/bin/env python3
"""MR05B authored Mercury encounter import.

Ports recovered Mercury Redux encounter content from the legacy Sinnoh-GBA
runtime snapshot into the real Platinum encounter JSONs.

This pass intentionally uses Platinum's native encounter structures as the
baseline representation:
- Morning is the 12-slot base grass table.
- Native Day/Night replacement slots are populated from recovered Mercury
  Day/Night tables.
- Surf is copied exactly when the recovered record has five water slots.
- Fishing preserves the recovered 10-slot species/level set across Platinum's
  three five-slot rod tables using deterministic duplication for the two- and
  three-slot legacy rods.

A follow-up MR05B runtime selector restores all 12 authored land slots for all
four Mercury periods. The recovered source remains authoritative.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TOD_MAP = {
    "gTwinleafTown": "encounters_twinleaf_town",
    "gRoute201": "encounters_route_201",
    "gRoute202": "encounters_route_202",
    "gLakeVerity": "encounters_lake_verity",
    "gRoute203": "encounters_route_203",
    "gRoute204South": "encounters_route_204_south",
    "gRoute204North": "encounters_route_204_north",
    "gValleyWindworksApproach": "encounters_valley_windworks_outside",
    "gRoute205South": "encounters_route_205_south",
    "gEternaForest": "encounters_eterna_forest",
    "gRoute206": "encounters_route_206",
    "gRoute207": "encounters_route_207",
    "gRoute208Shared": "encounters_route_208",
    "gRoute209": "encounters_route_209",
    "gRoute210SouthShared": "encounters_route_210_south",
    "gRoute212North": "encounters_route_212_north",
    "gRoute212South": "encounters_route_212_south",
    "gTrophyGarden": "encounters_trophy_garden",
    "gRoute213": "encounters_route_213",
    "gValorLakefront": "encounters_valor_lakefront",
    "gRoute214": "encounters_route_214",
    "gRoute215": "encounters_route_215",
    "gGreatMarshArea1": "encounters_great_marsh_1",
    "gGreatMarshArea2": "encounters_great_marsh_2",
    "gGreatMarshArea3": "encounters_great_marsh_3",
    "gGreatMarshArea4": "encounters_great_marsh_4",
    "gGreatMarshArea5": "encounters_great_marsh_5",
    "gGreatMarshArea6": "encounters_great_marsh_6",
}

STATIC_MAP = {
    "gOreburghGate": "encounters_oreburgh_gate_1f",
    "gOreburghMine_1": "encounters_oreburgh_mine_b1f",
    "gOreburghMine_3": "encounters_oreburgh_mine_b2f",
    "gMtCoronetFirstCrossing": "encounters_mt_coronet_1f_south",
    "gLostTower_1F": "encounters_route_209_lost_tower_1f",
    "gLostTower_2F": "encounters_route_209_lost_tower_2f",
    "gLostTower_3F": "encounters_route_209_lost_tower_3f",
    "gLostTower_4F": "encounters_route_209_lost_tower_4f",
    "gRuinManiacTunnel": "encounters_maniac_tunnel",
}

ADDITIVE_MAPS = {
    "gVerityLakefront": "MAP_HEADER_VERITY_LAKEFRONT",
    "gSandgemTown": "MAP_HEADER_SANDGEM_TOWN",
    "gFloaromaMeadow": "MAP_HEADER_FLOAROMA_MEADOW",
}

SPECIES_ALIASES = {
    # DS form plumbing is handled separately from the canonical 1025-species
    # registry. These aliases keep the encounter port compilable until the
    # custom/form registry is installed.
    "SPECIES_SHELLOS_WEST": "SPECIES_SHELLOS",
    "SPECIES_SHELLOS_EAST": "SPECIES_SHELLOS",
    "SPECIES_GASTRODON_WEST": "SPECIES_GASTRODON",
    "SPECIES_GASTRODON_EAST": "SPECIES_GASTRODON",
    "SPECIES_DEERLING_SPRING": "SPECIES_DEERLING",
    "SPECIES_DEERLING_SUMMER": "SPECIES_DEERLING",
    "SPECIES_DEERLING_AUTUMN": "SPECIES_DEERLING",
    "SPECIES_DEERLING_WINTER": "SPECIES_DEERLING",
    "SPECIES_ABRA_REDUX": "SPECIES_ABRA",
    "SPECIES_MACHOP_REDUX": "SPECIES_MACHOP",
    "SPECIES_LARVITAR_REDUX": "SPECIES_LARVITAR",
    "SPECIES_DARUMAKA_REDUX": "SPECIES_DARUMAKA",
    "SPECIES_MARBEEP": "SPECIES_MAREEP",
    "SPECIES_BASCULIN_RED_STRIPED": "SPECIES_BASCULIN",
    "SPECIES_DARUMAKA_GALAR": "SPECIES_DARUMAKA",
    "SPECIES_EISCUE_ICE": "SPECIES_EISCUE",
    "SPECIES_FARFETCHD_GALAR": "SPECIES_FARFETCHD",
    "SPECIES_GRIMER_ALOLA": "SPECIES_GRIMER",
    "SPECIES_GROWLITHE_HISUI": "SPECIES_GROWLITHE",
    "SPECIES_LILLIGANT_HISUI": "SPECIES_LILLIGANT",
    "SPECIES_MEOWTH_GALAR": "SPECIES_MEOWTH",
    "SPECIES_ORICORIO_PAU": "SPECIES_ORICORIO",
    "SPECIES_SANDSHREW_ALOLA": "SPECIES_SANDSHREW",
    "SPECIES_SLOWPOKE_GALAR": "SPECIES_SLOWPOKE",
    "SPECIES_SNEASEL_HISUI": "SPECIES_SNEASEL",
    "SPECIES_STUNFISK_GALAR": "SPECIES_STUNFISK",
    "SPECIES_VOLTORB_HISUI": "SPECIES_VOLTORB",
    "SPECIES_VULPIX_ALOLA": "SPECIES_VULPIX",
    "SPECIES_WOOPER_PALDEA": "SPECIES_WOOPER",
}

OLD_ROD_EXPAND = (0, 1, 0, 0, 1)
GOOD_ROD_EXPAND = (2, 3, 4, 2, 4)
SUPER_ROD_INDEXES = (5, 6, 7, 8, 9)

MAP_HEADER_BY_AREA = {
    "encounters_route_201": "MAP_HEADER_ROUTE_201",
    "encounters_route_202": "MAP_HEADER_ROUTE_202",
    "encounters_route_203": "MAP_HEADER_ROUTE_203",
    "encounters_route_204_south": "MAP_HEADER_ROUTE_204_SOUTH",
    "encounters_route_204_north": "MAP_HEADER_ROUTE_204_NORTH",
    "encounters_route_205_south": "MAP_HEADER_ROUTE_205_SOUTH",
    "encounters_route_205_north": "MAP_HEADER_ROUTE_205_NORTH",
    "encounters_route_206": "MAP_HEADER_ROUTE_206",
    "encounters_route_207": "MAP_HEADER_ROUTE_207",
    "encounters_route_208": "MAP_HEADER_ROUTE_208",
    "encounters_route_209": "MAP_HEADER_ROUTE_209",
    "encounters_route_210_south": "MAP_HEADER_ROUTE_210_SOUTH",
    "encounters_route_210_north": "MAP_HEADER_ROUTE_210_NORTH",
    "encounters_route_211_west": "MAP_HEADER_ROUTE_211_WEST",
    "encounters_route_211_east": "MAP_HEADER_ROUTE_211_EAST",
    "encounters_route_212_north": "MAP_HEADER_ROUTE_212_NORTH",
    "encounters_route_212_south": "MAP_HEADER_ROUTE_212_SOUTH",
    "encounters_route_213": "MAP_HEADER_ROUTE_213",
    "encounters_route_214": "MAP_HEADER_ROUTE_214",
    "encounters_route_215": "MAP_HEADER_ROUTE_215",
    "encounters_route_216": "MAP_HEADER_ROUTE_216",
    "encounters_route_217": "MAP_HEADER_ROUTE_217",
    "encounters_route_218": "MAP_HEADER_ROUTE_218",
    "encounters_route_219": "MAP_HEADER_ROUTE_219",
    "encounters_route_220": "MAP_HEADER_ROUTE_220",
    "encounters_route_221": "MAP_HEADER_ROUTE_221",
    "encounters_route_222": "MAP_HEADER_ROUTE_222",
    "encounters_route_223": "MAP_HEADER_ROUTE_223",
    "encounters_route_224": "MAP_HEADER_ROUTE_224",
    "encounters_great_marsh_1": "MAP_HEADER_GREAT_MARSH_1",
    "encounters_great_marsh_2": "MAP_HEADER_GREAT_MARSH_2",
    "encounters_great_marsh_3": "MAP_HEADER_GREAT_MARSH_3",
    "encounters_great_marsh_4": "MAP_HEADER_GREAT_MARSH_4",
    "encounters_great_marsh_5": "MAP_HEADER_GREAT_MARSH_5",
    "encounters_great_marsh_6": "MAP_HEADER_GREAT_MARSH_6",
}

TOD_PERIODS = ("Morning", "Day", "Evening", "Night")



def species(token: str) -> str:
    if token.startswith("SPECIES_UNOWN_") and token != "SPECIES_UNOWN":
        return "SPECIES_UNOWN"
    return SPECIES_ALIASES.get(token, token)


def fixed_level(mon: dict[str, Any]) -> int:
    lo = int(mon["min_level"])
    hi = int(mon["max_level"])
    return (lo + hi + 1) // 2


def land_slot(mon: dict[str, Any]) -> dict[str, Any]:
    return {"level": fixed_level(mon), "species": species(mon["species"])}


def water_slot(mon: dict[str, Any]) -> dict[str, Any]:
    return {
        "level_max": int(mon["max_level"]),
        "level_min": int(mon["min_level"]),
        "species": species(mon["species"]),
    }


def copy_water(dst: dict[str, Any], rec: dict[str, Any]) -> None:
    water = rec.get("water_mons")
    if not water:
        return
    mons = water.get("mons", [])
    if len(mons) != 5:
        raise SystemExit(f"{rec['base_label']}: expected 5 Surf slots, found {len(mons)}")
    dst["surf_rate"] = int(water.get("encounter_rate", dst.get("surf_rate", 0)))
    dst["surf_encounters"] = [water_slot(mon) for mon in mons]


def copy_fishing(dst: dict[str, Any], rec: dict[str, Any]) -> None:
    fishing = rec.get("fishing_mons")
    if not fishing:
        return
    mons = fishing.get("mons", [])
    if len(mons) != 10:
        raise SystemExit(f"{rec['base_label']}: expected 10 legacy fishing slots, found {len(mons)}")

    dst["old_rod_encounters"] = [water_slot(mons[i]) for i in OLD_ROD_EXPAND]
    dst["good_rod_encounters"] = [water_slot(mons[i]) for i in GOOD_ROD_EXPAND]
    dst["super_rod_encounters"] = [water_slot(mons[i]) for i in SUPER_ROD_INDEXES]

    rate = int(fishing.get("encounter_rate", 0))
    if rate:
        dst["old_rod_rate"] = rate
        dst["good_rod_rate"] = rate
        dst["super_rod_rate"] = rate


def records_by_label(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {rec["base_label"]: rec for rec in snapshot["records"]}


def update_tod_area(enc_dir: Path, stem: str, out_stem: str, records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    periods = {}
    for period in ("Morning", "Day", "Evening", "Night"):
        label = f"{stem}_{period}"
        if label not in records:
            raise SystemExit(f"Missing recovered Mercury record {label}")
        periods[period] = records[label]

    path = enc_dir / f"{out_stem}.json"
    if not path.exists():
        raise SystemExit(f"Missing Platinum encounter file {path}")

    before = json.loads(path.read_text())
    after = json.loads(path.read_text())

    morning_land = periods["Morning"].get("land_mons")
    if morning_land:
        mons = morning_land["mons"]
        if len(mons) != 12:
            raise SystemExit(f"{stem}: Morning must have 12 land slots")
        after["land_rate"] = int(morning_land["encounter_rate"])
        after["land_encounters"] = [land_slot(mon) for mon in mons]

        day_mons = periods["Day"]["land_mons"]["mons"]
        night_mons = periods["Night"]["land_mons"]["mons"]
        after["day"] = [species(day_mons[2]["species"]), species(day_mons[3]["species"])]
        after["night"] = [species(night_mons[2]["species"]), species(night_mons[3]["species"])]

        # Disable vanilla daily/cartridge replacement species from overriding
        # authored Mercury ecology. Dedicated Mercury Radar comes later.
        after["swarms"] = [after["land_encounters"][0]["species"], after["land_encounters"][1]["species"]]
        after["radar"] = [after["land_encounters"][8]["species"], after["land_encounters"][9]["species"], after["land_encounters"][10]["species"], after["land_encounters"][11]["species"]]
        for key in ("ruby", "sapphire", "emerald", "firered", "leafgreen"):
            after[key] = [after["land_encounters"][8]["species"], after["land_encounters"][9]["species"]]

    copy_water(after, periods["Day"])
    copy_fishing(after, periods["Day"])

    path.write_text(json.dumps(after, indent=4, ensure_ascii=False) + "\n")
    return {
        "area": out_stem,
        "source": stem,
        "changed": before != after,
        "morning_species": [x["species"] for x in after.get("land_encounters", [])],
    }


def update_static_area(enc_dir: Path, label: str, out_stem: str, records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rec = records.get(label)
    if rec is None:
        raise SystemExit(f"Missing recovered Mercury record {label}")
    path = enc_dir / f"{out_stem}.json"
    if not path.exists():
        raise SystemExit(f"Missing Platinum encounter file {path}")
    before = json.loads(path.read_text())
    after = json.loads(path.read_text())

    land = rec.get("land_mons")
    if land:
        mons = land["mons"]
        if len(mons) != 12:
            raise SystemExit(f"{label}: expected 12 land slots")
        after["land_rate"] = int(land["encounter_rate"])
        after["land_encounters"] = [land_slot(mon) for mon in mons]
        after["day"] = [after["land_encounters"][2]["species"], after["land_encounters"][3]["species"]]
        after["night"] = list(after["day"])

    copy_water(after, rec)
    copy_fishing(after, rec)
    path.write_text(json.dumps(after, indent=4, ensure_ascii=False) + "\n")
    return {"area": out_stem, "source": label, "changed": before != after}



def c_ident(area: str) -> str:
    return "".join(part.capitalize() for part in area.removeprefix("encounters_").split("_"))


def build_full_tod_runtime_block(route_specs: dict[str, Any]) -> tuple[str, int]:
    arrays: list[str] = []
    table_cases: list[str] = []
    weight_cases: list[str] = []
    installed = 0

    routes = route_specs.get("routes", {})
    if not isinstance(routes, dict):
        raise SystemExit("MR05B route specs missing routes object")

    default_weights = (20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1)

    for area, spec in routes.items():
        land = spec.get("land") or {}
        if not land:
            continue

        if area not in MAP_HEADER_BY_AREA:
            raise SystemExit(f"MR05B missing map-header mapping for {area}")

        for period in TOD_PERIODS:
            slots = land.get(period)
            if not isinstance(slots, list) or len(slots) != 12:
                raise SystemExit(f"{area}/{period}: expected 12 authored land slots")

        ident = c_ident(area)
        for period in TOD_PERIODS:
            slots = land[period]
            weights = [
                int(slot.get("weight", default_weights[index]))
                for index, slot in enumerate(slots)
            ]
            if any(weight <= 0 for weight in weights):
                raise SystemExit(f"{area}/{period}: all authored weights must be positive")
            if sum(weights) != 100:
                raise SystemExit(
                    f"{area}/{period}: authored weights must total 100, found {sum(weights)}"
                )

            arrays.append(
                f"static const EncounterSlot sMercury{ident}{period}[MAX_GRASS_ENCOUNTERS] = {{"
            )
            for slot in slots:
                arrays.append(
                    "    { "
                    + species(slot["species"])
                    + f", {int(slot['max_level'])}, {int(slot['min_level'])} "
                    + "},"
                )
            arrays.append("};")
            arrays.append(
                f"static const u8 sMercury{ident}{period}Weights[MAX_GRASS_ENCOUNTERS] = {{ "
                + ", ".join(str(weight) for weight in weights)
                + " };"
            )
            arrays.append("")

        table_cases.extend(
            [
                f"    case {MAP_HEADER_BY_AREA[area]}:",
                "        switch (timeOfDay) {",
                "        case TIMEOFDAY_MORNING:",
                f"            return sMercury{ident}Morning;",
                "        case TIMEOFDAY_DAY:",
                f"            return sMercury{ident}Day;",
                "        case TIMEOFDAY_TWILIGHT:",
                f"            return sMercury{ident}Evening;",
                "        case TIMEOFDAY_NIGHT:",
                "        case TIMEOFDAY_LATE_NIGHT:",
                "        default:",
                f"            return sMercury{ident}Night;",
                "        }",
            ]
        )
        weight_cases.extend(
            [
                f"    case {MAP_HEADER_BY_AREA[area]}:",
                "        switch (timeOfDay) {",
                "        case TIMEOFDAY_MORNING:",
                f"            return sMercury{ident}MorningWeights;",
                "        case TIMEOFDAY_DAY:",
                f"            return sMercury{ident}DayWeights;",
                "        case TIMEOFDAY_TWILIGHT:",
                f"            return sMercury{ident}EveningWeights;",
                "        case TIMEOFDAY_NIGHT:",
                "        case TIMEOFDAY_LATE_NIGHT:",
                "        default:",
                f"            return sMercury{ident}NightWeights;",
                "        }",
            ]
        )
        installed += 1

    block = arrays + [
        "/* MERCURY_MR05B_AUTHORED_TOD_BEGIN */",
        "static const EncounterSlot *Mercury_GetAuthoredLandTable(int mapHeaderID)",
        "{",
        "    int timeOfDay = GetTimeOfDay();",
        "",
        "    switch (mapHeaderID) {",
    ] + table_cases + [
        "    default:",
        "        return NULL;",
        "    }",
        "}",
        "",
        "static const u8 *Mercury_GetAuthoredLandWeights(int mapHeaderID)",
        "{",
        "    int timeOfDay = GetTimeOfDay();",
        "",
        "    switch (mapHeaderID) {",
    ] + weight_cases + [
        "    default:",
        "        return NULL;",
        "    }",
        "}",
        "",
        "static u8 Mercury_GetWeightedLandSlot(int mapHeaderID)",
        "{",
        "    const u8 *weights = Mercury_GetAuthoredLandWeights(mapHeaderID);",
        "    u8 roll;",
        "    u16 cumulative = 0;",
        "",
        "    if (weights == NULL) {",
        "        return MAX_GRASS_ENCOUNTERS;",
        "    }",
        "",
        "    roll = LCRNG_RandMod(100);",
        "    for (int i = 0; i < MAX_GRASS_ENCOUNTERS; i++) {",
        "        cumulative += weights[i];",
        "        if (roll < cumulative) {",
        "            return i;",
        "        }",
        "    }",
        "",
        "    return MAX_GRASS_ENCOUNTERS - 1;",
        "}",
        "",
        "static BOOL Mercury_ApplyAuthoredLandTable(int mapHeaderID, EncounterSlot *encounterTable)",
        "{",
        "    const EncounterSlot *source = Mercury_GetAuthoredLandTable(mapHeaderID);",
        "",
        "    if (source == NULL) {",
        "        return FALSE;",
        "    }",
        "",
        "    memcpy(encounterTable, source, sizeof(EncounterSlot) * MAX_GRASS_ENCOUNTERS);",
        "    return TRUE;",
        "}",
        "/* MERCURY_MR05B_AUTHORED_TOD_END */",
        "",
    ]
    return "\n".join(block), installed


def patch_full_tod_runtime(root: Path, route_specs: dict[str, Any]) -> int:
    path = root / "src/overlay006/wild_encounters.c"
    text = path.read_text()

    if "MERCURY_MR05B_AUTHORED_TOD_BEGIN" in text:
        raise SystemExit("MR05B full TOD runtime selector already installed")

    include_anchor = '#include "generated/items.h"\n'
    if include_anchor not in text:
        raise SystemExit("MR05B map-header include anchor missing")
    text = text.replace(
        include_anchor,
        include_anchor + '#include "generated/map_headers.h"\n',
        1,
    )

    struct_anchor = """typedef struct EncounterSlot {
    int species;
    u16 maxLevel;
    u16 minLevel;
} EncounterSlot;
"""
    if text.count(struct_anchor) != 1:
        raise SystemExit(
            f"MR05B EncounterSlot anchor mismatch: {text.count(struct_anchor)}"
        )

    field_params_anchor = "    u8 unownTableID;\n} WildEncounters_FieldParams;\n"
    if text.count(field_params_anchor) != 1:
        raise SystemExit(
            f"MR05B encounter field params anchor mismatch: {text.count(field_params_anchor)}"
        )
    text = text.replace(
        field_params_anchor,
        "    u8 unownTableID;\n    int mapHeaderID;\n} WildEncounters_FieldParams;\n",
        1,
    )

    runtime_block, installed = build_full_tod_runtime_block(route_specs)
    text = text.replace(
        struct_anchor,
        struct_anchor + "\n" + runtime_block + "\n",
        1,
    )

    old_replace = """        BOOL nationalDexObtained = Pokedex_IsNationalDexObtained(SaveData_GetPokedex(FieldSystem_GetSaveData(fieldSystem)));

        WildEncounters_ReplaceTimedEncounters(encounterData, &encounterTable[2].species, &encounterTable[3].species);
        WildEncounters_ReplaceSwarmEncounters(fieldSystem, encounterData, &encounterTable[0].species, &encounterTable[1].species);
        WildEncounters_ReplaceTrophyGardenEncounters(fieldSystem, nationalDexObtained, &encounterTable[6].species, &encounterTable[7].species);
        WildEncounters_ReplaceDualSlotEncounters(encounterData, nationalDexObtained, &encounterTable[8].species, &encounterTable[9].species);
"""
    new_replace = """        BOOL nationalDexObtained = Pokedex_IsNationalDexObtained(SaveData_GetPokedex(FieldSystem_GetSaveData(fieldSystem)));
        BOOL mercuryAuthoredTable = Mercury_ApplyAuthoredLandTable(fieldSystem->location->mapHeaderID, encounterTable);

        if (mercuryAuthoredTable == FALSE) {
            WildEncounters_ReplaceTimedEncounters(encounterData, &encounterTable[2].species, &encounterTable[3].species);
            WildEncounters_ReplaceSwarmEncounters(fieldSystem, encounterData, &encounterTable[0].species, &encounterTable[1].species);
            WildEncounters_ReplaceTrophyGardenEncounters(fieldSystem, nationalDexObtained, &encounterTable[6].species, &encounterTable[7].species);
            WildEncounters_ReplaceDualSlotEncounters(encounterData, nationalDexObtained, &encounterTable[8].species, &encounterTable[9].species);
        }
"""
    if text.count(old_replace) != 1:
        raise SystemExit(
            f"MR05B wild replacement anchor mismatch: {text.count(old_replace)}"
        )
    text = text.replace(old_replace, new_replace, 1)

    ground_sig = "static u8 GetGroundEncounterSlot(void)\n{\n"
    if text.count(ground_sig) != 1:
        raise SystemExit(
            f"MR05B ground encounter selector anchor mismatch: {text.count(ground_sig)}"
        )
    text = text.replace(
        ground_sig,
        "static u8 GetGroundEncounterSlot(const WildEncounters_FieldParams *encounterFieldParams)\n"
        "{\n"
        "    u8 mercurySlot = Mercury_GetWeightedLandSlot(encounterFieldParams->mapHeaderID);\n"
        "\n"
        "    if (mercurySlot < MAX_GRASS_ENCOUNTERS) {\n"
        "        return mercurySlot;\n"
        "    }\n"
        "\n",
        1,
    )

    ground_call = "GetGroundEncounterSlot();"
    if text.count(ground_call) != 2:
        raise SystemExit(
            f"MR05B ground encounter call count mismatch: {text.count(ground_call)}"
        )
    text = text.replace(
        ground_call,
        "GetGroundEncounterSlot(encounterFieldParams);",
    )

    old_level = "        level = encounterTable[encounterSlot].maxLevel;\n"
    if text.count(old_level) != 1:
        raise SystemExit(
            f"MR05B grass level anchor mismatch: {text.count(old_level)}"
        )
    text = text.replace(
        old_level,
        "        level = GetWildMonLevel(&encounterTable[encounterSlot], encounterFieldParams);\n",
        1,
    )

    init_anchor = "    encounterFieldParams->trainerID = TrainerInfo_ID(SaveData_GetTrainerInfo(fieldSystem->saveData));\n"
    if text.count(init_anchor) != 1:
        raise SystemExit(
            f"MR05B encounter field init anchor mismatch: {text.count(init_anchor)}"
        )
    text = text.replace(
        init_anchor,
        "    encounterFieldParams->mapHeaderID = fieldSystem->location->mapHeaderID;\n"
        + init_anchor,
        1,
    )

    path.write_text(text)
    return installed


RUNTIME_MAP_HEADERS = {
    "gTwinleafTown": ["MAP_HEADER_TWINLEAF_TOWN"],
    "gRoute201": ["MAP_HEADER_ROUTE_201"],
    "gRoute202": ["MAP_HEADER_ROUTE_202"],
    "gLakeVerity": ["MAP_HEADER_LAKE_VERITY", "MAP_HEADER_LAKE_VERITY_LOW_WATER"],
    "gRoute203": ["MAP_HEADER_ROUTE_203"],
    "gRoute204South": ["MAP_HEADER_ROUTE_204_SOUTH"],
    "gRoute204North": ["MAP_HEADER_ROUTE_204_NORTH"],
    "gValleyWindworksApproach": ["MAP_HEADER_VALLEY_WINDWORKS_OUTSIDE"],
    "gRoute205South": ["MAP_HEADER_ROUTE_205_SOUTH"],
    "gEternaForest": ["MAP_HEADER_ETERNA_FOREST"],
    "gRoute206": ["MAP_HEADER_ROUTE_206"],
    "gRoute207": ["MAP_HEADER_ROUTE_207"],
    "gRoute208Shared": ["MAP_HEADER_ROUTE_208"],
    "gRoute209": ["MAP_HEADER_ROUTE_209"],
    "gRoute210SouthShared": ["MAP_HEADER_ROUTE_210_SOUTH"],
    "gRoute212North": ["MAP_HEADER_ROUTE_212_NORTH"],
    "gRoute212South": ["MAP_HEADER_ROUTE_212_SOUTH"],
    "gTrophyGarden": ["MAP_HEADER_TROPHY_GARDEN"],
    "gRoute213": ["MAP_HEADER_ROUTE_213"],
    "gValorLakefront": ["MAP_HEADER_VALOR_LAKEFRONT"],
    "gRoute214": ["MAP_HEADER_ROUTE_214"],
    "gRoute215": ["MAP_HEADER_ROUTE_215"],
    "gGreatMarshArea1": ["MAP_HEADER_GREAT_MARSH_1"],
    "gGreatMarshArea2": ["MAP_HEADER_GREAT_MARSH_2"],
    "gGreatMarshArea3": ["MAP_HEADER_GREAT_MARSH_3"],
    "gGreatMarshArea4": ["MAP_HEADER_GREAT_MARSH_4"],
    "gGreatMarshArea5": ["MAP_HEADER_GREAT_MARSH_5"],
    "gGreatMarshArea6": ["MAP_HEADER_GREAT_MARSH_6"],
    "gOreburghGate": ["MAP_HEADER_OREBURGH_GATE_1F"],
    "gOreburghMine_1": ["MAP_HEADER_OREBURGH_MINE_B1F"],
    "gOreburghMine_3": ["MAP_HEADER_OREBURGH_MINE_B2F"],
    "gMtCoronetFirstCrossing": ["MAP_HEADER_MT_CORONET_1F_SOUTH"],
    "gLostTower_1F": ["MAP_HEADER_ROUTE_209_LOST_TOWER_1F"],
    "gLostTower_2F": ["MAP_HEADER_ROUTE_209_LOST_TOWER_2F"],
    "gLostTower_3F": ["MAP_HEADER_ROUTE_209_LOST_TOWER_3F"],
    "gLostTower_4F": ["MAP_HEADER_ROUTE_209_LOST_TOWER_4F"],
    "gRuinManiacTunnel": [
        "MAP_HEADER_RUIN_MANIAC_CAVE_SHORT",
        "MAP_HEADER_RUIN_MANIAC_CAVE_LONG",
        "MAP_HEADER_MANIAC_TUNNEL",
    ],
}


def runtime_period_records(stem: str, records: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    periods = {}
    for period in ("Morning", "Day", "Evening", "Night"):
        row = records.get(f"{stem}_{period}")
        if row is not None and row.get("land_mons"):
            periods[period] = row

    if periods:
        if len(periods) != 4:
            raise SystemExit(f"{stem}: incomplete four-period runtime source")
        return periods

    static = records.get(stem)
    if static is None or not static.get("land_mons"):
        raise SystemExit(f"{stem}: missing authored land source")
    return {period: static for period in ("Morning", "Day", "Evening", "Night")}


def write_runtime_header(root: Path, records: dict[str, dict[str, Any]]) -> int:
    profiles = []
    for stem, headers in RUNTIME_MAP_HEADERS.items():
        period_rows = runtime_period_records(stem, records)
        period_slots = {}
        for period, row in period_rows.items():
            mons = row["land_mons"]["mons"]
            if len(mons) != 12:
                raise SystemExit(f"{stem} {period}: expected 12 land slots")
            period_slots[period] = [
                {
                    "species": species(mon["species"]),
                    "min_level": int(mon["min_level"]),
                    "max_level": int(mon["max_level"]),
                }
                for mon in mons
            ]
        for header in headers:
            profiles.append((header, stem, period_slots))

    out = root / "include/generated/mercury_authored_encounters.h"
    lines = [
        "#ifndef POKEPLATINUM_GENERATED_MERCURY_AUTHORED_ENCOUNTERS_H",
        "#define POKEPLATINUM_GENERATED_MERCURY_AUTHORED_ENCOUNTERS_H",
        "",
        '#include "generated/map_headers.h"',
        "",
        "typedef struct MercuryEncounterSourceSlot {",
        "    u16 species;",
        "    u8 minLevel;",
        "    u8 maxLevel;",
        "} MercuryEncounterSourceSlot;",
        "",
    ]

    for i, (_header, stem, period_slots) in enumerate(profiles):
        lines.append(
            f"static const MercuryEncounterSourceSlot sMercuryLandProfile{i}[4][MAX_GRASS_ENCOUNTERS] = {{"
        )
        for pidx, period in enumerate(("Morning", "Day", "Evening", "Night")):
            lines.append(f"    [{pidx}] = {{ // {period}: {stem}")
            for slot in period_slots[period]:
                lines.append(
                    f"        {{ {slot['species']}, {slot['min_level']}, {slot['max_level']} }},"
                )
            lines.append("    },")
        lines += ["};", ""]

    lines += [
        "static u8 MercuryEncounters_GetAuthoredPeriod(void)",
        "{",
        "    switch (GetTimeOfDay()) {",
        "    case TIMEOFDAY_MORNING:",
        "        return 0;",
        "    case TIMEOFDAY_DAY:",
        "        return 1;",
        "    case TIMEOFDAY_TWILIGHT:",
        "        return 2;",
        "    case TIMEOFDAY_NIGHT:",
        "    case TIMEOFDAY_LATE_NIGHT:",
        "    default:",
        "        return 3;",
        "    }",
        "}",
        "",
        "static BOOL MercuryEncounters_ApplyAuthoredLand(",
        "    const enum MapHeaderID mapHeaderID, EncounterSlot *encounterTable)",
        "{",
        "    const MercuryEncounterSourceSlot (*profile)[MAX_GRASS_ENCOUNTERS] = NULL;",
        "    switch (mapHeaderID) {",
    ]
    for i, (header, _stem, _period_slots) in enumerate(profiles):
        lines += [
            f"    case {header}:",
            f"        profile = sMercuryLandProfile{i};",
            "        break;",
        ]
    lines += [
        "    default:",
        "        return FALSE;",
        "    }",
        "",
        "    const u8 period = MercuryEncounters_GetAuthoredPeriod();",
        "    for (u8 i = 0; i < MAX_GRASS_ENCOUNTERS; i++) {",
        "        encounterTable[i].species = profile[period][i].species;",
        "        encounterTable[i].minLevel = profile[period][i].minLevel;",
        "        encounterTable[i].maxLevel = profile[period][i].maxLevel;",
        "    }",
        "    return TRUE;",
        "}",
        "",
        "#endif",
        "",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    return len(profiles)


def patch_runtime_selector(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"
    text = path.read_text()

    typedef = """typedef struct EncounterSlot {
    int species;
    u16 maxLevel;
    u16 minLevel;
} EncounterSlot;
"""
    include = '\n#include "generated/mercury_authored_encounters.h"\n'
    if include.strip() not in text:
        if text.count(typedef) != 1:
            raise SystemExit("MR05B runtime selector: EncounterSlot typedef anchor mismatch")
        text = text.replace(typedef, typedef + include, 1)

    old = """        WildEncounters_ReplaceTimedEncounters(encounterData, &encounterTable[2].species, &encounterTable[3].species);
        WildEncounters_ReplaceSwarmEncounters(fieldSystem, encounterData, &encounterTable[0].species, &encounterTable[1].species);
        WildEncounters_ReplaceTrophyGardenEncounters(fieldSystem, nationalDexObtained, &encounterTable[6].species, &encounterTable[7].species);
        WildEncounters_ReplaceDualSlotEncounters(encounterData, nationalDexObtained, &encounterTable[8].species, &encounterTable[9].species);

        if (!withPartner) {
            WildEncounters_ReplaceGreatMarshDailyEncounters(fieldSystem, safariGameActive, nationalDexObtained, encounterTable);
"""
    new = """        BOOL mercuryAuthoredLand = MercuryEncounters_ApplyAuthoredLand(
            fieldSystem->location->mapHeaderID,
            encounterTable);

        if (mercuryAuthoredLand == FALSE) {
            WildEncounters_ReplaceTimedEncounters(encounterData, &encounterTable[2].species, &encounterTable[3].species);
            WildEncounters_ReplaceSwarmEncounters(fieldSystem, encounterData, &encounterTable[0].species, &encounterTable[1].species);
            WildEncounters_ReplaceTrophyGardenEncounters(fieldSystem, nationalDexObtained, &encounterTable[6].species, &encounterTable[7].species);
            WildEncounters_ReplaceDualSlotEncounters(encounterData, nationalDexObtained, &encounterTable[8].species, &encounterTable[9].species);
        }

        if (!withPartner) {
            if (mercuryAuthoredLand == FALSE) {
                WildEncounters_ReplaceGreatMarshDailyEncounters(fieldSystem, safariGameActive, nationalDexObtained, encounterTable);
            }
"""
    if "MercuryEncounters_ApplyAuthoredLand" not in text[text.find("if (encounterType == ENCOUNTER_TYPE_GRASS"):]:
        if text.count(old) != 1:
            raise SystemExit("MR05B runtime selector: vanilla replacement anchor mismatch")
        text = text.replace(old, new, 1)

    path.write_text(text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("runtime_snapshot", type=Path)
    ap.add_argument("--route-specs", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr05b-authored-encounters.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    enc_dir = root / "res/field/encounters"
    snapshot = json.loads(args.runtime_snapshot.read_text())
    records = records_by_label(snapshot)

    results = []
    for stem, out_stem in TOD_MAP.items():
        results.append(update_tod_area(enc_dir, stem, out_stem, records))
    for label, out_stem in STATIC_MAP.items():
        results.append(update_static_area(enc_dir, label, out_stem, records))

    route_specs = json.loads(args.route_specs.read_text())
    full_tod_area_count = patch_full_tod_runtime(root, route_specs)

    runtime_profile_count = write_runtime_header(root, records)
    patch_runtime_selector(root)

    changed = [r["area"] for r in results if r["changed"]]
    report = {
        "gate": "MERCURY_MR05B_AUTHORED_ENCOUNTERS",
        "status": "PASS",
        "source_record_count": int(snapshot.get("record_count", len(snapshot["records"]))),
        "ported_area_count": len(results),
        "changed_area_count": len(changed),
        "changed_areas": changed,
        "additive_maps_pending_in_next_pass": ADDITIVE_MAPS,
        "full_four_period_runtime_selector_pending": False,
        "full_four_period_runtime_area_count": full_tod_area_count,
        "water_only_authored_routes": [
            "encounters_route_219",
            "encounters_route_220",
            "encounters_route_223",
        ],
        "regional_honey_tree_runtime_pending": True,
        "species_aliases_used": SPECIES_ALIASES,
    }
    if not changed:
        raise SystemExit("MR05B authored encounter import changed zero areas")
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
